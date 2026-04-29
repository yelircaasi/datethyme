from __future__ import annotations

from collections.abc import Iterable
from itertools import pairwise
from typing import Self, Union

from ...core import Date, DateRange, DateTime, DateTimeSpan, Time, TimeSpan
from ...protocols import (
    EntryProtocol,
    PartitionProtocol,
)
from ._abcs import AbstractPartition

NestedSpan = Union[TimeSpan, "TimePartition"]

DEFAULT_DATE = Date.parse("2000-01-01")


class DateTimePartition(AbstractPartition[DateTime]):
    # type DateTimeSpan = DateTimeSpan
    """
    TODO: add nesting_mode to determine how nested time partitions are
    resized under different operations
    """

    @property
    def passes_day_boundary(self) -> bool:
        return self.start.date < self.end.date

    @classmethod
    def from_datetimes(
        cls, times: Iterable[DateTime], names: Iterable[str | None] | None = None
    ) -> Self:
        n_spans = len(times := tuple(times)) - 1
        if names is None:
            names = (None,) * n_spans
        if not len(names := tuple(names)) == n_spans:
            raise ValueError
        return cls(
            spans=(
                DateTimeSpan(start=a, end=b, name=name)
                for (a, b), name in zip(pairwise(times), names)
            )
        )

    @property
    def daterange(self) -> DateRange:
        return DateRange(
            start=self.start.date,
            stop=self.end.date,
        )

    @staticmethod
    def format_span(span: DateTimeSpan | DateTimePartition, indent: int = 0):
        prefix = indent * " "
        if isinstance(span, DateTimeSpan):
            return f"{prefix}{span.start} - {id(span)}"
        elif isinstance(span, DateTimePartition):
            return repr(DateTimePartition).replace("\n", "\n" + prefix)
        raise ValueError


# ================================================================================================


class TimePartition(AbstractPartition[Time]):
    """
    A contiguous sequence of TimeSpan objects or TimePartition objects (recursive),
      useful for scheduling.

    intuitively:
        resolve_overlaps(seq, mode=EQUAL|PROPORTIONAL|INVERSE|ECLIPSE|SHIFT)
        resolve_gaps(seq, mode=EQUAL|PROPORTIONAL|INVERSE|SNAP_FORWARD|SNAP_BACK|SHIFT_FORWARD|
          SHIFT_BACK)
        squeeze(seq, mode=PROPORTIONAL|EQUAL, earliest=None, latest=None)
        stack(seq, mode=forward|middle|backward, anchor=None)
        truncate(seq, earliest: Time, latest: Time)

        truncate_preserve -> return (before, truncated, after)

    both can be procrustean or not

    """

    @classmethod
    def from_starts(cls, spans: dict[TimeSpan, str] | Iterable, end: Time) -> Self:
        raise NotImplementedError

    @classmethod
    def from_ends(cls, spans: dict[TimeSpan, str] | Iterable, start: Time) -> Self:
        raise NotImplementedError

    def partition_element(
        self,
        element_id: str,
        other: PartitionProtocol | Iterable[EntryProtocol],
        min_length: int = 1,
        max_length: int | None = None,
    ) -> Self:
        raise NotImplementedError

    @classmethod
    def from_times(
        cls, times: Iterable[Time], names: Iterable[str | None] | None = None
    ) -> PartitionProtocol[Time]:
        n_spans = len(times := tuple(times)) - 1
        if names is None:
            names = (None,) * n_spans
        if not len(names := tuple(names)) == n_spans:
            raise ValueError
        return cls(
            spans=(
                TimeSpan(start=a, end=b, name=name)  # TODO # type: ignore
                for (a, b), name in zip(pairwise(times), names)
            )
        )

    @staticmethod
    def format_span(span: TimeSpan | TimePartition, indent: int = 0):
        prefix = indent * " "
        if isinstance(span, TimeSpan):
            return f"{prefix}{span.start} - {id(span)}"
        elif isinstance(span, TimePartition):
            return repr(TimePartition).replace("\n", "\n" + prefix)
        raise ValueError

    @property
    def passes_day_boundary(self) -> bool:
        return self.start > self.end


# dt0 = DateTime(year=2025, month=6, day=15, hour=16)
# dt1 = DateTime(year=2025, month=6, day=15, hour=17, minute=30)
# dt2 = DateTime(year=2025, month=6, day=15, hour=18, minute=45)
# dt3 = DateTime(year=2025, month=6, day=15, hour=19, minute=0)
# dt4 = DateTime(year=2025, month=6, day=15, hour=20, minute=15)
# dtp = DateTimePartition.from_datetimes((dt0, dt1, dt2, dt3, dt4))

# print(dtp)
# print(str(dtp))
# print(repr(dtp))


# class SpanContainer[T]:
#     def __init__(self, start: T, end: T, subpartition: Iterable[SpanProtocol[T]]) -> None:
#         self.start: T = start
#         self.end: T = end
#         self.subpartition: tuple[SpanProtocol[T], ...] = tuple(subpartition)


class DatePartition: ...
