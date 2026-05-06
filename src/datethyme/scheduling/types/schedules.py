from __future__ import annotations

from collections import UserDict
from collections.abc import Iterable, Sequence
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
from .entries import Entries, Entry

DEFAULT_DATE = Date.parse("2000-01-01")


class ScheduledEntry[T: TimeProtocol](BaseModel):
    """Like CalendarPartition, except that start time may be after 00:00
    and end time may be before 24:00.
    """

    _start: T
    _end: T
    _subentries: list[DurationProtocol]  # list[EntryProtocol | ScheduledEntries | TimeSlot]

    @property
    def name(self) -> str:
        raise NotImplementedError

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


class FixedBlock[T: TimeProtocol](TimeBlockProtocol[T], ScheduledEntry):
    start: T
    end: T

    def add_flex(self, entry: SpanProtocol) -> ResultTriple[T]:
        raise NotImplementedError

    def add_fixed(self, entry: SpanProtocol, earliest: T, latest: T) -> ResultTriple[T]:
        raise NotImplementedError


class FlexBlock[T: TimeProtocol](TimeBlockProtocol[T], ScheduledEntry):
    start: T
    end: T

    def add_flex(self, entry: SpanProtocol) -> ResultTriple[T]:
        raise NotImplementedError

    def add_fixed(self, entry: SpanProtocol, earliest: T, latest: T) -> ResultTriple[T]:
        raise NotImplementedError


class EmptyBlock[T: TimeProtocol](TimeBlockProtocol[T]):
    start: T
    end: T

    def add_flex(self, entry: SpanProtocol) -> ResultTriple[T]:
        raise NotImplementedError

    def add_fixed(self, entry: SpanProtocol, earliest: T, latest: T) -> ResultTriple[T]:
        raise NotImplementedError


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
        return success, popped, self

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
        success = AddResult.ADDED
        popped: list[EntryProtocol] = []
        raise NotImplementedError
        return success, popped, self

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
        raise NotImplementedError

    @classmethod
    def from_spans(
        cls, spans: dict[T | SpanProtocol[T], str] | Iterable[T | SpanProtocol[T]], end: T
    ) -> Self:
        raise NotImplementedError

    @classmethod
    def from_starts(cls, starts: dict[T, str] | Iterable[T], end: T) -> Self:
        raise NotImplementedError

    def partition_element(
        self,
        element_name: str | int,
        subelements: PartitionProtocol[T] | Iterable[SpanProtocol[T] | EntryProtocol],
        min_length: int = 1,
        max_length: int | None = None,
    ) -> Self:
        raise NotImplementedError

    @overload
    def __getitem__(self, idx: str) -> Entry | None: ...  # by ID
    @overload
    def __getitem__(self, idx: Time) -> Entry | None: ...  # by point time
    @overload
    def __getitem__(self, idx: TimeSpan) -> list[Entry]: ...  # by time span
    def __getitem__(self, idx) -> Entry | list[Entry] | None:
        raise NotImplementedError


class CalendarDay:
    schedule: DayPartition  # validate that start is 00:00 and end is 24:00
    entries: Entries


class Calendar(UserDict[Date, CalendarDay]): ...
