from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from itertools import pairwise
from pathlib import Path
from typing import Literal, Self, overload

from adiumentum.pydantic import BaseDict, BaseModelRW
from pydantic import Field, model_validator

from ..._abcs import TimeProtocol
from ...constants import AddResult
from ...core import Date, Time, TimeSpan
from ...exceptions import TemporalLogicError
from ...protocols import (
    EntriesProtocol,
    EntryProtocol,
    PartitionProtocol,
    ResultTriple,
    SpanProtocol,
    TimeBlockProtocol,
)
from ..utils import is_partitioned
from .entries import Entries, SerializedEntries
from .log import SchedulingLog
from .new_abstract_block import AbstractBlock

DEFAULT_DATE = Date.parse("2000-01-01")


# class ScheduledEntry[T: TimeProtocol](BaseModel):
#     """Like CalendarPartition, except that start time may be after 00:00
#     and end time may be before 24:00.
#     """

#     _start: T
#     _end: T
#     _subentries: list[DurationProtocol]  # list[EntryProtocol | ScheduledEntries | TimeSlot]
#     _name: str | None = None

#     @property
#     def name(self) -> str:
#         return self._name or f"TimeSpan[id{str(hash(self))[:16]}]"

#     @property
#     def start(self) -> T:
#         return self._start

#     @model_validator(mode="wrap")
#     @classmethod
#     def assert_partitioned(cls, data: object, handler: ModelWrapValidatorHandler[Self]) -> Self:
#         # need
#         prevalidated = handler(data)
#         members: list[DurationProtocol] = prevalidated._subentries
#         if not is_partitioned(members):
#             msg = f"Data is not a correct partition:\n{data}"
#             raise ValidationError(msg)
#         return prevalidated

#     @property
#     def minutes(self) -> NonNegativeInt:
#         self.assert_validity()
#         return round(self._start.minutes_to(self._end))

#     def assert_validity(self) -> None: ...


class FixedBlock[T: TimeProtocol](AbstractBlock[T]):
    # _start: T
    # _end: T
    # _name: str | None = None
    # subentries: list[SpanProtocol[T]] = []

    start: T
    end: T
    name: str | None = None
    contexts: set[str] = Field(default_factory=set)
    subentries: list[SpanProtocol[T]] = Field(default_factory=list)

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining


class FlexBlock[T: TimeProtocol](AbstractBlock[T]):
    # _start: T
    # _end: T
    # _name: str | None = None
    # subentries: list[SpanProtocol[T]] = []

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining


class EmptyBlock[T: TimeProtocol](AbstractBlock[T]):
    # _start: T
    # _end: T
    # _name: str | None = None

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining


class DayPartition(BaseModelRW):
    """Special case of [Date]TimePartition beginning at 00:00 and ending at 24:00 on the same day.

    Consideration: distinguish between "not added because of conflict" (for add_fixed)
        and "not added because of no room" (presumably only for add_flex)? -> AddResult enum

    """

    fixed: list[FixedBlock[Time]]
    flex: list[FlexBlock[Time]] = Field(default_factory=list)
    gaps: list[EmptyBlock[Time]] = Field(default_factory=list)

    @model_validator(mode="after")
    def infer_gaps(self) -> Self:
        """TODO: add fixed entries to entries lookup?"""
        blocks = self._blocks
        first = Time(hour=0).span(Time(hour=0))
        last = Time(hour=24).span(Time(hour=24))

        for a, b in pairwise([first, *blocks, last]):
            if a.end < b.start:
                self.gaps.append(EmptyBlock(start=a.end, end=b.start))

        self.gaps.sort(key=lambda x: x.start)
        self.assert_validity()
        return self

    def plain_display(self) -> str:
        return "\n  ".join(map(repr, self.blocks))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n  {self.plain_display()}"

    @property
    def start(self) -> Time:
        return self.blocks[0].start

    @property
    def end(self) -> Time:
        return max(x.end for x in self.blocks)

    # def __init__(self, fixed: Iterable[FixedBlock[T]]) -> None:
    #     self._fixed: list[FixedBlock[T]] = list(fixed)
    #     self._flex: list[FlexBlock[T]] = []
    #     self._gaps: list[EmptyBlock[T]] = []
    #     self.end: T

    def assert_partitioned(self) -> None:
        if not is_partitioned(self.blocks):
            raise TemporalLogicError

    def add_fixed(self, entry: EntryProtocol, earliest: Time, latest: Time) -> ResultTriple[Self]:
        """Cases:

        - fits in gap
            -> return (AddResult.ADDED,          [],                    self)
        - fits in gap with stretching or squeezing
            -> return (AddResult.ADDED_MUTATED,  [],                    self)
        - conflict with fixed
            -> return (AddResult.NOT_ADDED,      [Entry],               self)
        - displaces incumbent flex entries
            -> return (AddResult.DISPLACE,       [<displaced entries>], Self)

        """
        success = AddResult.ADDED
        popped: list[EntryProtocol] = []
        return success, self, popped

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        """Cases:

        - fits in gap
            -> return (AddResult.ADDED,          [],                    self)
        - fits in gap with stretching or squeezing
            -> return (AddResult.ADDED_MUTATED,  [],                    self)
        - does not fit in any suitable gap
            -> return (AddResult.NOT_ADDED,      [Entry],               self)
        - displaces incumbent flex entries (via priority)
            -> return (AddResult.DISPLACE,       [<displaced entries>], Self)

        """
        result = AddResult.NOT_ADDED
        popped: list[EntryProtocol] = []
        return result, self, popped

    def assert_validity(self) -> None: ...

    @property
    def _blocks(self) -> list[EmptyBlock[Time] | FlexBlock[Time] | FixedBlock[Time]]:
        all_blocks: Sequence[FixedBlock[Time] | FlexBlock[Time] | EmptyBlock[Time]] = (
            self.fixed + self.flex + self.gaps
        )
        return sorted(all_blocks, key=lambda x: (x.start, x.end))

    @property
    def blocks(self) -> list[EmptyBlock[Time] | FlexBlock[Time] | FixedBlock[Time]]:
        self.assert_validity()
        return self._blocks

    def __contains__(self, obj: object) -> bool:
        if type(obj) is type(self.start):
            return self.start <= obj <= self.end
        if isinstance(obj, str):
            return any(block.name == obj for block in self.blocks)
        raise TypeError

    @classmethod
    def from_spans(
        cls, spans: dict[SpanProtocol[Time], str] | Iterable[SpanProtocol[Time]], end: Time
    ) -> Self:
        return cls(fixed=[])
        # should be: return cls((FixedBlock(span.start, span.end) for span in spans))
        # needs FixedBlock to implement all required methods

    @classmethod
    def from_starts(cls, starts: dict[Time, str] | Iterable[Time], end: Time) -> Self:
        names_ = tuple(starts.values()) if isinstance(starts, dict) else None
        starts = tuple(starts)

        names = names_[:-1] if names_ else [None] * (len(starts) - 1)
        other_spans = []
        for i, (start_, end_) in enumerate(pairwise(starts)):
            block = FixedBlock(start=start_, end=end_, name=names[i], subentries=[])
            other_spans.append(block)

        other_spans.append(FixedBlock(start=starts[0], end=end, name=names[-1], subentries=[]))

        return cls(fixed=other_spans)

    @overload
    def __getitem__(self, idx: str) -> TimeBlockProtocol | None: ...  # by ID
    @overload
    def __getitem__(self, idx: Time) -> TimeBlockProtocol | None: ...  # by point time
    @overload
    def __getitem__(self, idx: TimeSpan) -> list[TimeBlockProtocol]: ...  # by time span
    def __getitem__(self, idx) -> TimeBlockProtocol | list[TimeBlockProtocol] | None:  # type: ignore
        if isinstance(idx, str):
            for block in self.blocks:
                if block.name == idx:
                    return block
            raise IndexError
        raise ValueError

    @staticmethod
    def format_span(span: SpanProtocol[Time] | PartitionProtocol[Time], indent: int = 0) -> str:
        prefix = indent * " "
        if isinstance(span, SpanProtocol):
            return f"{prefix}{span.start} - {id(span)}"
        elif isinstance(span, PartitionProtocol):
            return repr(span).replace("\n", "\n" + prefix)
        raise ValueError

    @property
    def passes_day_boundary(self) -> bool:
        return False
    
    def get_all_names(self) -> tuple[str, ...]:
        raise NotImplementedError


class CalendarDay(BaseModelRW):  # PartitionProtocol[Time]):
    # class Config():
    #     arbitrary_types_allowed=True

    schedule: DayPartition  # validate that start is 00:00 and end is 24:00
    entries: SerializedEntries

    def plain_display(self) -> str:
        return f"{self.schedule.plain_display()}\n\n  Entries: {', '.join(self.entries)}\n\n"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n  {self.plain_display()}"

    def assert_validity(self) -> None:
        schedule_names = set(self.schedule.get_all_names())
        entry_names = set(self.entries.keys())

        if not schedule_names == entry_names:
            msg = f"Scheduled names do not match entry names:\n  {schedule_names=}\n  {entry_names=}"
            raise TemporalLogicError(msg)

    # @field_validator("entries", mode="before")
    # @classmethod
    # def ensure_entries(cls, raw: Iterable) -> Entries:
    #     entry_tuple = (Entry.model_validate(e) for e in raw)
    #     return Entries({e.name: e for e in entry_tuple})

    # @field_serializer("entries")
    # def export_list(self, raw: dict) -> list[dict[str, object]]:
    #     return list(raw.values())

    # @classmethod
    # def from_dict(cls, raw: dict[str, list[object]]) -> Self:
    #     return cls.model_validate(raw)


class Routines:
    @classmethod
    def read_json_file(
        cls,
        path: Path,
    ) -> Self:
        return cls()


class Recurring:
    @classmethod
    def read_json_file(
        cls,
        path: Path,
    ) -> Self:
        return cls()


class ContextHierarchy:
    @classmethod
    def read_json_file(
        cls,
        path: Path,
    ) -> Self:
        return cls()


class Calendar(BaseDict[Date, CalendarDay]):
    @classmethod
    def read_restricted(
        cls,
        calendar: Path,
        start: Date | None = None,
        end: Date | None = None,
        ndays: int = 30,
    ) -> Self:
        raw = json.loads((calendar).read_text())
        return cls.model_validate({k: CalendarDay.model_validate(v) for k, v in raw.items()})

    def __str__(self) -> str:
        return "\n".join((f"{k!s}\n  {v.plain_display()}" for k, v in self.items()))

    def __repr__(self) -> str:
        return self.__str__()

    @model_validator(mode="before")
    @classmethod
    def ensure_validation(cls, value: dict[str, object]) -> dict[Date, CalendarDay]:
        return {Date.model_validate(k): CalendarDay.model_validate(v) for k, v in value.items()}

    def create_schedule(
        self,
        *,
        recurring: Recurring,
        routines: Routines,
        entries: EntriesProtocol,
        context_hierarchy: ContextHierarchy,
    ) -> tuple[
        Calendar,
        Entries,
        list[SchedulingLog],
    ]:
        logs: list[SchedulingLog] = []

        routines_logs = self.allocate_routines(routines)
        logs.append(routines_logs)

        recurring_log = self.allocate_recurring(recurring)
        logs.append(recurring_log)
        # interactive resolution of conflicts? simply return Conflicts object?

        remaining, log = self.allocate_entries(
            entries,
            context_hierarchy=context_hierarchy,
        )
        logs.append(log)

        return self, remaining, logs

    def allocate_routines(self, routines: Routines) -> SchedulingLog:
        log = SchedulingLog()
        return log

    def allocate_entries(
        self,
        entries: EntriesProtocol | Iterable[EntryProtocol],
        *,
        context_hierarchy: ContextHierarchy,
    ) -> tuple[Entries, SchedulingLog]:
        remaining = Entries([])
        log = SchedulingLog()
        return remaining, log

    def allocate_recurring(self, recurring: Recurring) -> SchedulingLog:
        log = SchedulingLog()
        return log

    def export_latex(
        self, style: Literal["compact"] | Literal["verbose"] | Literal["default"] = "default"
    ) -> str:
        return "PLACEHOLDER"
