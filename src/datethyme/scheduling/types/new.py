from __future__ import annotations

from collections.abc import Iterator, Mapping
from enum import StrEnum, auto
from pathlib import Path
from typing import Self

from adiumentum.fp import lmap, tfilter

# from adiumentum.num import round5
from adiumentum.pydantic import BaseDict
from loguru import logger
from pydantic import BaseModel, Field, model_validator

from datethyme import Date, Time

from .context import ContextValidator, make_context_validator
from .elementary_types import DurationType, IDType, NoteProtocol, NotesProtocol
from .recurring import RecurringTask, RecurringTasks
from .routine import Routine, RoutineItem, Routines
from .utils import (
    DAY_START,
    SpanMixin,
    adjust_blocks,
    last_end,
    parse_calendar,
    rescale,
    sum_time,
)

# from consilium.notes.types.core import IDType, Note, Notes  # TODO: get adapters polished


class NoteAdapter(BaseModel):
    id: str = Field(frozen=True)
    scheduling_contexts: frozenset[str] = Field(frozen=True)
    text: str = Field(frozen=True)
    link: str = Field(frozen=True)
    normalTime: int = Field(frozen=True)
    idealTime: int = Field(frozen=True)
    minTime: int = Field(frozen=True)
    maxTime: int = Field(frozen=True)
    priority: float = Field(frozen=True)

    scheduled: bool = Field(default=False)

    def duration(self, duration_type: DurationType) -> int:
        match duration_type:
            case DurationType.IDEAL:
                return self.idealTime
            case DurationType.NORMAL:
                return self.normalTime
            case DurationType.MIN:
                return self.minTime
            case DurationType.MAX:
                return self.maxTime
            case _:
                raise ValueError

    @property
    def display_text(self) -> str:
        if not self.text or self.link:
            return "<empty>"
        if not self.text:
            return self.link
        if not self.link:
            return self.text
        return f"{self.text} (-> {self.link})"

    @classmethod
    def from_note(cls, note: NoteProtocol) -> Self:
        return cls(
            id=note.id,
            text=note.text,
            link=note.link,
            scheduling_contexts=frozenset(note.scheduling_contexts),
            normalTime=note.normalTime,
            idealTime=note.idealTime,
            minTime=note.minTime,
            maxTime=note.maxTime,
            priority=note.priority,
        )


class NotesAdapter(BaseModel):
    notes: dict[str, NoteAdapter]

    def __iter__(self) -> Iterator[NoteAdapter]:
        return iter(self.notes.values())

    @classmethod
    def from_notes(cls, notes: Mapping[str, NoteProtocol] | list[NoteProtocol]) -> Self:
        if isinstance(notes, dict):
            return cls(notes={k: NoteAdapter.from_note(v) for k, v in notes.items()})
        elif isinstance(notes, list):
            return cls(notes={note.id: NoteAdapter.from_note(note) for note in notes})
        raise ValueError


PLANNED = set()


class Origin(StrEnum):
    MANUAL = auto()
    ROUTINE = auto()
    RECURRING = auto()
    NOTE = auto()
    GAP = auto()
    NA = auto()


class SubBlock(SpanMixin, BaseModel):
    id: str = Field(default="")
    start: Time
    end: Time
    text: str = Field(default="<empty>")
    contexts: str | None = Field(default=None)
    task: NoteAdapter | RoutineItem | RecurringTask | None = Field(default=None)
    origin: Origin = Field(default=Origin.NA)
    # context_validator: ContextValidator = Field(default=trivial_validator)
    context_mapping: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _(self) -> Self:
        if not self.id:
            self.id = f"{self.start}--{self.end}"
        return self

    @property
    def context_validator(self) -> ContextValidator:
        validator = make_context_validator(self.contexts or "_any", self.context_mapping)
        return validator

    @classmethod
    def from_routine_item(cls, element: RoutineItem) -> Self:
        return cls(
            id=element.name,
            text=element.name,
            start=DAY_START,
            end=DAY_START,
            task=element,
            origin=Origin.ROUTINE,
        )

    @classmethod
    def from_routine(cls, name: str, routine: Routine, start: Time, end: Time) -> list[Self]:
        return lmap(cls.from_routine_item, routine.elements)

    @classmethod
    def from_recurring_task(cls, task: RecurringTask, start: Time, end: Time) -> Self:
        return cls(
            id=task.id,
            text=task.name,
            start=start,
            end=end,
            task=task,
            origin=Origin.RECURRING,
        )

    @classmethod
    def from_note(cls, note: NoteAdapter, start: Time, end: Time) -> Self:
        # note = NoteAdapter.from_note(note_orig)
        return cls(
            id=note.id,
            text=note.display_text,
            start=start,
            end=end,
            origin=Origin.NOTE,
        )

    @property
    def size(self) -> int:
        return int(self.start.minutes_to(self.end))

    @property
    def repr_contexts(self) -> str:
        if not self.contexts:
            return ""
        return f" [{self.contexts}]"

    @property
    def minTime(self) -> int:
        return self.task.minTime if self.task else 15

    @property
    def normalTime(self) -> int:
        return self.task.normalTime if self.task else 15

    @property
    def idealTime(self) -> int:
        return self.task.idealTime if self.task else 15

    @property
    def maxTime(self) -> int:
        return self.task.maxTime if self.task else 15

    def __str__(self) -> str:
        naive = f"    | {self.start} - {self.end} {self.text}"  # {self.origin.value.upper()}
        return f"{naive:<40}{self.repr_contexts}"


class Block(SubBlock):
    # start: Time
    # end: Time | None
    # title: str
    # contexts: tuple[str, ...]
    children: list[SubBlock] = Field(default_factory=list)
    registry: dict[str, Routine | RecurringTask | NoteAdapter] = Field(default_factory=dict)

    @classmethod
    def initial(cls, end: Time) -> Self:
        return cls(start=Time(hour=0), end=end, origin=Origin.GAP)

    @classmethod
    def final(cls, start: Time) -> Self:
        return cls(start=start, end=Time(hour=24), origin=Origin.GAP)

    def __str__(self) -> str:
        def make_toplevel() -> str:
            naive = f"  {self.start} - {self.end} {self.text}"
            return f"{naive:<40}{self.repr_contexts}"

        segments = tfilter((
            make_toplevel(),
            "\n".join(map(str, self.children)),
        ))
        return "\n".join(segments)

    # @property
    # def max_available(self) -> int:
    #     if not self.children:
    #         return self.size
    #     return self.size - self.minTime

    # @property
    # def normal_available(self) -> int:
    #     if not self.children:
    #         return self.size
    #     return self.size - self.normalTime

    # @property
    # def ideal_available(self) -> int:
    #     if not self.children:
    #         return self.size
    #     return self.size - self.idealTime

    # @property
    # def min_available(self) -> int:
    #     if not self.children:
    #         return self.size
    #     return self.size - self.maxTime

    def available(self, duration_type: DurationType) -> int:
        if not self.children:
            return self.size
        print("available:", self.size - self.duration(duration_type))
        return self.size - self.duration(duration_type)

    def duration(self, duration_type: DurationType) -> int:
        match duration_type:
            case DurationType.IDEAL | DurationType.NORMAL | DurationType.MIN | DurationType.MAX:
                return sum_time(duration_type, self.registry.values(), fallback=self.size)
            case _:
                raise ValueError

    @property
    def minTime(self) -> int:
        return sum_time(DurationType.MIN, self.registry.values(), fallback=self.size)

    @property
    def normalTime(self) -> int:
        return sum_time(DurationType.NORMAL, self.registry.values(), fallback=self.size)

    @property
    def idealTime(self) -> int:
        return sum_time(DurationType.IDEAL, self.registry.values(), fallback=self.size)

    @property
    def maxTime(self) -> int:
        return sum_time(DurationType.MAX, self.registry.values(), fallback=self.size)

    def add_routines(self, routines: Routines) -> tuple[str, ...]:
        added: list[str] = []
        for name, routine in routines.items():
            if self.context_validator({name}):
                # logger.info(f"Routine context resolved: {name}")
                self._add_routine_items(routine=routine)
                added.append(name)
                self.contexts = "_locked"
                return tuple(added)
        return tuple()

    def add_recurring_tasks(self, *, date: Date, recurring_due: RecurringTasks) -> RecurringTasks:
        for task in recurring_due.get_due():
            if self.context_validator(task.contexts):
                # logger.info(f"Task context resolved: {task.id}")
                if task.minTime <= (av := self.available(DurationType.NORMAL)):
                    self._add_recurring_task(task)
                    # logger.info("Should have added task.")
                    task.last = date
                if av < 10:
                    # logger.info(f"Block full: {date}->{self.start}")
                    return recurring_due
        return recurring_due

    def add_notes(
        self,
        notes_orig: NotesProtocol,
        scheduled: set[IDType],
        when_loose: DurationType = DurationType.IDEAL,
        at_margin: DurationType = DurationType.NORMAL,
    ) -> set[IDType]:
        print(scheduled)
        notes = NotesAdapter.from_notes(notes_orig)
        for note in notes:
            if (note.id in scheduled) or (note.id in self.registry):
                print("already_contained")
                continue
            elif self.context_validator(note.scheduling_contexts):
                logger.info(f"Task context resolved: {note.id} {note.scheduling_contexts}")
                print(note.duration(at_margin), self.available(when_loose), len(self.registry))

                if note.duration(at_margin) <= (av := self.available(when_loose)):
                    print(av)
                    self._add_note(note)
                    scheduled.add(note.id)
                    logger.info("Should have added note.")
                if av < 10:
                    logger.info(f"Block full: {self.start}, {self.id}")
                    break
                    # self.children = rescale(self.start, self.end, self.children)
                    # return scheduled
        self.children = rescale(self.start, self.end, self.children)
        return scheduled
        # for note in notes.without(scheduled).values():

        #     if ctxs := resolve_contexts(
        #         self.contexts, note.projects | note.contexts, none_means_any=True
        #     ):
        #         logger.info(f"Task context resolved: {note.id} {ctxs}")
        #         if (note.id in scheduled) or (note.id in self.registry):
        #             print("yes", note.id)
        #             continue
        #         elif note.normalTime <= (av := self.ideal_available):
        #             print("no", note.id)
        #             self._add_note(note)
        #             scheduled.add(note.id)

        #             logger.info("Should have added note.")
        #             if av < 10:
        #                 logger.info(f"Block full: {self.start}, {self.id}")
        #                 self.children = rescale(self.start, self.end, self.children)
        #                 return scheduled
        #         else:
        #             pass
        # self.children = rescale(self.start, self.end, self.children)
        # return scheduled

    def rescale(self) -> Self:
        self.children = rescale(self.start, self.end, self.children)
        return self

    def _add_routine_items(self, routine: Routine) -> None:
        start = last_end(self.children, self.start)
        name = routine.name
        new_subblocks = SubBlock.from_routine(name, routine, start=start, end=self.end)
        n = len(new_subblocks)
        if not routine.minTime <= self.available(DurationType.MAX):
            raise ValueError(f"{routine.minTime} > {self.available(DurationType.MAX)}")
        # print(self.children, n)
        self.children = adjust_blocks(self.start, self.end, [*self.children, *new_subblocks])
        if not len(self.children) == n:
            # print(len(self.children))
            raise ValueError("======")
        self.registry.update({name: routine})

    def _add_recurring_task(self, recurring: RecurringTask) -> None:
        start = last_end(self.children, self.start)
        new_subblock = SubBlock.from_recurring_task(recurring, start=start, end=self.end)
        # print([*(self.children or []), new_subblock])
        self.children = adjust_blocks(self.start, self.end, [*(self.children or []), new_subblock])
        self.registry.update({recurring.name: recurring})

    def _add_note(self, note: NoteAdapter) -> None:
        start = last_end(self.children, self.start)
        new_subblock = SubBlock.from_note(note, start=start, end=start + note.idealTime)
        self.children = adjust_blocks(self.start, self.end, [*(self.children or []), new_subblock])
        self.registry.update({note.id: note})


class Day(BaseModel):
    blocks: list[Block]
    text: str = Field(default="")

    def __str__(self) -> str:
        return f"{self.text}\n{'\n'.join(map(str, self.blocks))}"

    def add_routines(self, routines: Routines) -> set[str]:
        """TODO"""
        scheduled: set[str] = set()
        for block in self.blocks:
            scheduled.update(block.add_routines(routines))
        return scheduled

    def add_recurring(self, date: Date, recurring_due: RecurringTasks) -> RecurringTasks:
        for block in self.blocks:
            recurring_due = block.add_recurring_tasks(date=date, recurring_due=recurring_due)
        return recurring_due

    def add_notes(
        self,
        notes: NotesProtocol,
        scheduled: set[IDType],
        when_loose: DurationType = DurationType.IDEAL,
        at_margin: DurationType = DurationType.NORMAL,
    ) -> set[IDType]:
        for block in self.blocks:
            scheduled.update(
                block.add_notes(notes, scheduled, when_loose=when_loose, at_margin=at_margin)
            )
        return scheduled

    def add_gaps(self) -> None:
        # return
        day_end = Time(hour=24)
        new_blocks: list[Block] = []
        self.blocks.sort(key=lambda b: b.start)
        current = Time(hour=0)
        # if (first := self.blocks[0].start) > day_start:
        #     new_blocks.append(Block.initial(first))
        for block in self.blocks:
            if block.start > current:
                gap_filler = Block(start=current, end=block.start, origin=Origin.GAP)
                new_blocks.append(gap_filler)
            new_blocks.append(block)
            current = block.end
        if self.blocks and (last := self.blocks[-1].end) > day_end:
            new_blocks.append(Block.final(last))

        self.blocks = new_blocks


class DefaultSchedules(BaseDict[str, Day]):
    def get_schedule(self, key: str, day_classes: dict[str, str] | None = None) -> Day:
        key = key.lower()[:3]
        if key in self:
            return self[key]

        day_classes = {
            "mon": "workday",
            "tue": "workday",
            "wed": "workday",
            "thu": "workday",
            "fri": "workday",
            "sat": "weekend",
            "sun": "weekend",
        } | (day_classes or {})

        if key in day_classes:
            translated_key = day_classes[key]
            if translated_key in self:
                # logger.info(f"Using default schedule: {translated_key}")
                return Day.model_validate_json(self[translated_key].model_dump_json())
        raise ValueError(f"Key not found in DefaultSchedules: {key}.")


class BlockCalendar(BaseDict[Date, Day]):
    def __str__(self) -> str:
        return (
            "\n\n".join(
                (f"{'=' * 50} {date} {date.weekday.title()} {day}" for date, day in self.items())
            )
            + "\n"
        )

    @classmethod
    def model_validate_plain(cls, txt: str) -> Self:
        raw = parse_calendar(txt)
        # for k, v in raw.items():
        #     print(k)
        #     for k_, v_ in v.items():
        #         print(k_, v_)
        return cls.model_validate(raw)

    @classmethod
    def read_txt_file(cls, p: Path) -> Self:
        return cls.model_validate_plain(p.read_text())

    def write_txt_file(self, p: Path) -> Path:
        p.write_text(str(self))
        return p

    def fill_with_defaults(
        self,
        defaults: DefaultSchedules,
        start: Date | int | None,
        end: Date | int = 30,
    ) -> Self:
        start = start if isinstance(start, Date) else (Date.today() + (start or 0))
        end = end if isinstance(end, Date) else (start + end)
        for date in start.range(end, inclusive=True):
            if date not in self:
                self.update({date: defaults.get_schedule(date.weekday)})
                # logger.info(f"updated {date} with default")
            if not self[date].blocks:
                raise ValueError("NO BLOCKS FOUND")

        return self

    def fill_gaps(self) -> Self:
        for date in self:
            if not self[date].blocks:
                raise ValueError("NO BLOCKS FOUND")
            self[date].add_gaps()

            if not self[date].blocks:
                raise ValueError(f"{date}: NO BLOCKS FOUND AFTER")
        return self

    def fill_schedule(
        self,
        routines: Routines,
        recurring: RecurringTasks,
        notes: NotesProtocol,
        when_loose: DurationType = DurationType.IDEAL,
        at_margin: DurationType = DurationType.NORMAL,
    ) -> tuple[Self, RecurringTasks, set[IDType]]:
        note_ids: set[IDType] = set()
        # return self, recurring, note_ids

        for date in self:
            print("=========", date, "=========")
            _ = self[date].add_routines(routines)
            recurring = self[date].add_recurring(date, recurring)
            self[date].add_notes(notes, note_ids, when_loose=when_loose, at_margin=at_margin)

        return self, recurring, note_ids
