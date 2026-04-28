from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ModelWrapValidatorHandler,
    NonNegativeInt,
    model_validator,
)

from ..._abcs import TimeProtocol
from ...constants import AddResult
from ...core import Date, Time
from ...protocols import EntryProtocol, PartitionProtocol, SpanProtocol
from .entries import Entries, Entry
from .slots import TimeSlot

type ResultTriple[T] = tuple[AddResult, list[EntryProtocol], T]
DEFAULT_DATE = Date.parse("2000-01-01")


class ScheduledEntries(BaseModel, EntryProtocol):
    """Like CalendarPartition, except that start time may be after 00:00
    and end time may be before 24:00.
    """

    name: str
    _start: Time
    _end: Time
    _subpartition: list[EntryProtocol | ScheduledEntries | TimeSlot]

    @property
    def start(self) -> Time:
        return self._start

    @model_validator(mode="wrap")
    @classmethod
    def assert_partitioned(cls, data: object, handler: ModelWrapValidatorHandler[Self]) -> Self:
        return handler(data)

    @property
    def minutes(self) -> NonNegativeInt:
        self.assert_validity()
        return round(self._start.minutes_to(self._end))

    def assert_validity(self) -> None: ...


class FixedBlock[T: TimeProtocol](PartitionProtocol[T]): ...


class FlexBlock[T: TimeProtocol](PartitionProtocol[T]): ...


class EmptyBlock[T: TimeProtocol](PartitionProtocol[T]): ...


class ChunkedDay[T: TimeProtocol](PartitionProtocol):
    def __init__(self, fixed: Iterable[FixedBlock]) -> None:
        self._fixed = list(fixed)
        self._flex: list[FlexBlock] = []
        self._gaps: list[EmptyBlock] = []

    def assert_partitioned(self) -> None: ...

    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]:
        """Cases:

        - fits in gap
            -> return (AddResult.ADDED,     [],                    self)
        - fits in gap with stretching or squeezing
            -> return (AddResult.ADDED,     [],                    self)
        - conflict with fixed
            -> return (AddResult.NOT_ADDED, [Entry],               self)
        - displaces incumbent flex entries
            -> return (AddResult.DISPLACE,  [<displaced entries>], Self)

        """
        success = AddResult.ADDED
        popped: list[EntryProtocol] = []
        return success, popped, self

    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]:
        """Cases:

        - fits in gap
            -> return (AddResult.ADDED,     [],                    self)
        - fits in gap with stretching or squeezing
            -> return (AddResult.ADDED,     [],                    self)
        - conflict with fixed
            -> return (AddResult.NOT_ADDED, [Entry],               self)
        - displaces incumbent flex entries
            -> return (AddResult.DISPLACE,  [<displaced entries>], Self)

        """
        success = AddResult.ADDED
        popped: list[EntryProtocol] = []
        return success, popped, self


class DayPartition[T: TimeProtocol](BaseModel):
    """Special case of DateTimePartition beginning at 00:00 and ending at 24:00 on the same day."""

    _blocks: list[ScheduledEntries]

    def assert_validity(self) -> None: ...

    @property
    def blocks(self) -> list[ScheduledEntries]:
        self.assert_validity()
        return self._blocks

    def __contains__(self, obj: object) -> bool:
        return False  # TODO

    @classmethod
    def from_spans(cls, spans: dict[SpanProtocol, str] | Iterable[SpanProtocol]) -> Self:
        raise NotImplementedError

    @classmethod
    def from_starts(cls, starts: dict[T, str] | Iterable[T]) -> Self:
        raise NotImplementedError

    def partition_element(
        self,
        element_name: str | int,
        subelements: Iterable[SpanProtocol | Entry],
        min_length: int = 1,
        max_length: int | None = None,
    ) -> Self:
        raise NotImplementedError


class CalendarDay:
    schedule: DayPartition  # validate that start is 00:00 and end is 24:00
    entries: Entries


class Calendar: ...


class Strategy(StrEnum): ...


# TODO: how to add identity, i.e. 'is' operator?
