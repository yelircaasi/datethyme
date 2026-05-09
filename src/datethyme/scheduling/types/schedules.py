from __future__ import annotations

from collections import UserDict
from collections.abc import Iterable, Sequence
from itertools import pairwise
from typing import Self, overload

from pydantic import (
    BaseModel,
    ModelWrapValidatorHandler,
    NonNegativeInt,
    ValidationError,
    model_validator,
)

from ..._abcs import TimeProtocol
from ...constants import AddResult
from ...core import Date, Time, TimeSpan
from ...protocols import (
    DurationProtocol,
    EntryProtocol,
    PartitionProtocol,
    ResultTriple,
    SpanProtocol,
    TimeBlockProtocol,
)
from ..utils import is_partitioned
from .entries import Entries

DEFAULT_DATE = Date.parse("2000-01-01")


class ScheduledEntry[T: TimeProtocol](BaseModel):
    """Like CalendarPartition, except that start time may be after 00:00
    and end time may be before 24:00.
    """

    _start: T
    _end: T
    _subentries: list[DurationProtocol]  # list[EntryProtocol | ScheduledEntries | TimeSlot]
    _name: str | None = None

    @property
    def name(self) -> str:
        return self._name or f"TimeSpan[id{str(hash(self))[:16]}]"

    @property
    def start(self) -> T:
        return self._start

    @model_validator(mode="wrap")
    @classmethod
    def assert_partitioned(cls, data: object, handler: ModelWrapValidatorHandler[Self]) -> Self:
        # need
        prevalidated = handler(data)
        members: list[DurationProtocol] = prevalidated._subentries
        if not is_partitioned(members):
            msg = f"Data is not a correct partition:\n{data}"
            raise ValidationError(msg)
        return prevalidated

    @property
    def minutes(self) -> NonNegativeInt:
        self.assert_validity()
        return round(self._start.minutes_to(self._end))

    def assert_validity(self) -> None: ...


class FixedBlock[T: TimeProtocol](TimeBlockProtocol[T], ScheduledEntry, TimeSpan):
    _start: T
    _end: T
    _name: str | None = None

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining


class FlexBlock[T: TimeProtocol](TimeBlockProtocol[T], ScheduledEntry, TimeSpan):
    _start: T
    _end: T
    _name: str | None = None

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining


class EmptyBlock[T: TimeProtocol](TimeBlockProtocol[T], TimeSpan):
    _start: T
    _end: T
    _name: str | None = None

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        result = AddResult.NOT_ADDED
        remaining: list[EntryProtocol] = [entry]
        return result, self, remaining


class DayPartition[T: TimeProtocol](PartitionProtocol[T]):
    """Special case of [Date]TimePartition beginning at 00:00 and ending at 24:00 on the same day.

    Consideration: distinguish between "not added because of conflict" (for add_fixed)
        and "not added because of no room" (presumably only for add_flex)? -> AddResult enum
    """

    def __init__(self, fixed: Iterable[FixedBlock[T]]) -> None:
        self._fixed: list[FixedBlock[T]] = list(fixed)
        self._flex: list[FlexBlock[T]] = []
        self._gaps: list[EmptyBlock[T]] = []
        self.end: T

    def assert_partitioned(self) -> None: ...

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
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

    _blocks: list[TimeBlockProtocol]

    def assert_validity(self) -> None: ...

    @property
    def blocks(self) -> list[TimeBlockProtocol[T]]:
        self.assert_validity()
        all_blocks: Sequence[FixedBlock[T] | FlexBlock[T] | EmptyBlock[T]] = (
            self._fixed + self._fixed + self._fixed
        )
        return sorted(all_blocks, key=lambda x: (x.start, x.end))

    def __contains__(self, obj: object) -> bool:
        if type(obj) is type(self.start):
            return self.start <= obj <= self.end
        if isinstance(obj, str):
            return any(block.name == obj for block in self.blocks)
        raise TypeError

    @classmethod
    def from_spans(
        cls, spans: dict[SpanProtocol[T], str] | Iterable[SpanProtocol[T]], end: T
    ) -> Self:
        return cls(fixed=[])
        # should be: return cls((FixedBlock(span.start, span.end) for span in spans))
        # needs FixedBlock to implement all required methods

    @classmethod
    def from_starts(cls, starts: dict[T, str] | Iterable[T], end: T) -> Self:
        names_ = tuple(starts.values()) if isinstance(starts, dict) else None
        starts = tuple(starts)

        names = names_[:-1] if names_ else [None] * (len(starts) - 1)
        other_spans = []
        for i, (start_, end_) in enumerate(pairwise(starts)):
            block = FixedBlock(_start=start_, _end=end_, _name=names[i], _subentries=[])
            other_spans.append(block)

        other_spans.append(FixedBlock(_start=starts[0], _end=end, _name=names[-1], _subentries=[]))

        return cls(fixed=other_spans)

    @overload
    def __getitem__(self, idx: str) -> TimeBlockProtocol | None: ...  # by ID
    @overload
    def __getitem__(self, idx: Time) -> TimeBlockProtocol | None: ...  # by point time
    @overload
    def __getitem__(self, idx: TimeSpan) -> list[TimeBlockProtocol]: ...  # by time span
    def __getitem__(self, idx) -> TimeBlockProtocol | list[TimeBlockProtocol] | None:
        if isinstance(idx, str):
            for block in self.blocks:
                if block.name == idx:
                    return block
            raise IndexError
        raise ValueError


class CalendarDay:
    schedule: DayPartition  # validate that start is 00:00 and end is 24:00
    entries: Entries


class Calendar(UserDict[Date, CalendarDay]): ...
