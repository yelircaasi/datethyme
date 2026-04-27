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
from ...core import Date, Time
from ...protocols import EntryProtocol, SpanProtocol
from .entries import Entries, Entry
from .slots import TimeSlot

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
