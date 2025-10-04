from abc import abstractmethod
from collections.abc import Callable, Iterable, Iterator
from itertools import pairwise
from typing import Literal, Self, TypeVar, Union

from ._datethyme import Date, DateRange, DateTime, DateTimeSpan, Time, TimeSpan
from ._scheduling_utils import (
    is_contiguous,
    stack_forward,
)
from .protocols import DeltaProtocol, PartitionProtocol  # pyright: ignore
from .utils import (
    assert_xor,
)

NestedSpan = Union[TimeSpan, "TimePartition"]

S = TypeVar("S")
T = TypeVar("T", bound=Time | DateTime | Date)
DEFAULT_DATE = Date.parse("2000-01-01")


class DateTimePartition(PartitionProtocol):
    # type DateTimeSpan = DateTimeSpan
    """
    TODO: add nesting_mode to determine how nested time partitions are
    resized under different operations
    """

    def __init__(
        self,
        spans: Iterable[DateTimeSpan],
        names: Iterable[str | None] | None = None,
    ):
        if not is_contiguous(spans):
            raise ValueError
        self._spans = spans
        self._names = tuple(names) if names else names

    @property
    def named_spans(self) -> tuple[tuple[str, DateTimeSpan], ...]:
        return tuple(zip(self.names, self._spans))

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(map(lambda sp: sp.name, self.spans))

    @property
    def span(self) -> "DateTimeSpan":
        return self.start.to(self.end)  # pyright: ignore

    @property
    def spans(self) -> tuple[DateTimeSpan, ...]:
        return tuple(self._spans)

    @property
    def start(self) -> DateTime:
        return min(self.starts)

    @property
    def end(self) -> DateTime:
        return max(self.ends)

    @property
    def starts(self) -> tuple[DateTime, ...]:
        return tuple(map(lambda s: s.start, self.spans))

    @property
    def ends(self) -> tuple[DateTime, ...]:
        return tuple(map(lambda t: t.end, self.spans))

    @property
    def days(self) -> float:
        return self.span.days

    @property
    def hours(self) -> float:
        return self.span.hours

    @property
    def minutes(self) -> float:
        return self.span.minutes

    @property
    def seconds(self) -> float:
        return self.span.seconds

    def __bool__(self) -> bool:
        return self.end > self.start  # pyright: ignore

    def __contains__(self, other) -> bool:
        return self.contains(other)

    # @classmethod
    # def from_sequence(
    #     cls,
    #     seq: Iterable[DateTimeSpan],
    #     mode,
    #     round_to: int = 0,
    # ) -> Self:
    #     meth = {}[mode]
    #     return cls(meth(seq))

    @classmethod
    def from_pipeline(
        cls,
        segments: Iterable[DateTimeSpan],
        pipeline: Iterable[Callable[[Iterable[DateTimeSpan]], Iterable[DateTimeSpan]]],
        # Callable[[Iterable[DateTimeSpan]], tuple[DateTimeSpan]],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        for step in pipeline:
            segments = step(segments)
        return cls.from_partition(segments, names=names)

    @classmethod
    def from_boundaries(
        cls,
        times: Iterable[DateTime],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        names = names or (None,) * (len(times := tuple(times)) - 1)
        spans = (a.span(b, name=name) for (a, b), name in zip(pairwise(times), names))  # pyright: ignore
        return cls(spans=spans, names=names)  # pyright: ignore

    @classmethod
    def from_partition(
        cls,
        segments: Iterable[DateTimeSpan],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        return cls(spans=segments, names=names)

    @classmethod
    def from_durations(
        cls,
        *,
        durations: Iterable[int | float],
        start: DateTime | None,
        end: DateTime | None,
        names: Iterable[str | None] | None = None,
    ) -> Self:
        anchor_start = assert_xor(start, end)
        if anchor_start:
            raise NotImplementedError
        else:
            raise NotImplementedError

    @classmethod
    def from_deltas(
        cls,
        *,
        durations: Iterable[DeltaProtocol],
        start: DateTime | None,
        end: DateTime | None,
        names: Iterable[str | None] | None = None,
    ) -> Self:
        anchor_start = assert_xor(start, end)
        if anchor_start:
            raise NotImplementedError
        else:
            raise NotImplementedError

    @classmethod
    def from_relative_lengths(
        cls,
        start: DateTime,
        end: DateTime,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        raise NotImplementedError

    def round_hours(self, round_to: int) -> Self:
        return self.__class__(
            spans=tuple(span.round_hours(round_to) for span in self.spans),
            names=tuple(span.name for span in self.spans),
        )

    def round_minutes(self, round_to: int) -> Self:
        return self.__class__(spans=tuple(span.round_minutes(round_to) for span in self.spans))

    def round_seconds(self, round_to: float) -> Self:
        return self.__class__(span.round_seconds(round_to) for span in self.spans)

    @classmethod
    def from_minutes_and_start(
        cls,
        start: DateTime,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        raise NotImplementedError

    @classmethod
    def from_minutes_and_end(
        cls,
        end: DateTime,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        other,
        include_start: bool = True,
        include_end: bool = False,
    ) -> bool:
        ...
        # return self.span.contains(other)

    def gap(self, other, strict: bool = False) -> "DateTimeSpan | None": ...

    def hull(self, other, strict: bool = False) -> "DateTimeSpan":
        return self.span.hull(other)

    def interior_point(self, alpha: float) -> DateTime:
        return self.span.interior_point(alpha)

    def intersection(self, other, strict: bool = False) -> "DateTimePartition | None":
        ...
        # return self.span.intersection(other)

    def overlap(self, other, strict: bool = False) -> "DateTimePartition | None": ...

    def shift_end_rigid(self, new_end: DateTime) -> "DateTimePartition":
        raise NotImplementedError

    def shift_start_rigid(self, new_start: DateTime) -> "DateTimePartition":
        raise NotImplementedError

    def snap_end_to(self, new_end: DateTime) -> "DateTimePartition":
        raise NotImplementedError

    def snap_start_to(self, new_start: DateTime) -> "DateTimePartition":
        raise NotImplementedError

    def split(self, cut_point: DateTime) -> "tuple[DateTimePartition, DateTimePartition]":
        raise NotImplementedError

    def span_containing(self, point: DateTime) -> DateTimeSpan | None:
        for span in self._spans:
            if span.contains(point):
                return span
        return None

    def insert(
        self,
        span_start: DateTime | int,
        new_span: DateTimeSpan,
        mode: Literal["SQUEEZE", "PUSH_BACK", "PUSH_FORWARD"],
        split_incumbent: bool = True,
    ) -> "DateTimePartition":
        raise NotImplementedError

    def index_from_name(self, name: str) -> int | None:
        raise NotImplementedError

    def index_from_time(self, point: DateTime) -> int | None:
        raise NotImplementedError

    def affine_transform(  # TODO
        self,
        scale_factor: float,
        new_start: DateTime | None = None,
        new_end: DateTime | None = None,
        min_minutes: int | float = 5,
    ) -> Self:
        new_length = scale_factor * self.minutes
        if new_start and not new_end:
            result = self.__class__(new_start, new_start.add_minutes(new_length))  # type: ignore
        elif new_end and not new_start:
            result = self.__class__(new_end.add_minutes(new_length), new_end)  # type: ignore
        else:
            raise ValueError

        if result.minutes < min_minutes:
            raise ValueError
        return result

    def reordered(self, orderer: Callable[[DateTimeSpan], int | float | str | DateTime]) -> Self:
        reordered = sorted(self.spans, key=orderer)
        return self.__class__.from_partition(stack_forward(reordered))

    # FROM TimePartition -------------------------------------------------

    @property
    def passes_day_boundary(self) -> bool: ...

    @classmethod
    def from_times(
        cls, times: Iterable[Time], names: Iterable[str | None] | None = None
    ) -> "DateTimePartition":
        n_spans = len(times := tuple(times)) - 1
        if names is None:
            names = (None,) * n_spans
        if not len(names := tuple(names)) == n_spans:
            raise ValueError
        return DateTimePartition(
            spans=(
                TimeSpan(start=a, end=b, name=name) for (a, b), name in zip(pairwise(times), names)
            )
        )

    # DEV ONLY -----------------------------------------------------------------------------------
    # class DateTimePartition():

    # spans: Iterable[DateTimeSpan]
    # def __init__(self, spans, names: Iterable[str] | None = None):
    #     self._spans = tuple(spans)
    #     self._names = tuple(names) if names else names

    # @property
    # def ends(self):
    #     return tuple(map(lambda t: t.end, self.spans))

    # @property
    # def end(self):
    #     return max(self.ends)
    # --------------------------------------------------------------------------------------------
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

    def iter_nested(self) -> Iterator[tuple[int, DateTimeSpan]]:
        raise NotImplementedError

    def __str__(self):
        return "TODO: "  # {self}"

    def __repr__(self):
        # change _spans to spans later
        return (
            f"TimePartition(\n    "
            f"{'\n    '.join(map(self.format_span, self.spans))}"
            f"\n    {self.end} - <END>\n)"
        )

    def ALT__repr__(self):
        for level, event in self.iter_nested():
            indent = " " * level
            print(f"{indent:<12} {event.start} — {event.name.title()}")

        def format_span(span: TimeSpan):
            return f"{span.start} - {span.name}"

        return (
            f"TimePartition(\n    {'\n    '.join(map(format_span, self.spans))}"
            f"\n    {self.end} - <END>\n)"
        )

    # def repr_indented(self, span: DateTimePartition, indent: int) -> str:
    #     prefix = indent * " "
    #     if isinstance(span, DateTimePartition):

    #     return ("\n" + (" " * indent)).join(map(partial(self.format_span, indent=indent), span))

    def format_span(self, span: "DateTimeSpan | DateTimePartition", indent: int = 0):
        prefix = indent * " "
        if isinstance(span, DateTimeSpan):
            return f"{prefix}{span.start} - {span.name}"
        elif isinstance(span, DateTimePartition):
            return repr(DateTimePartition).replace("\n", "\n" + prefix)
        raise ValueError


# ================================================================================================


class TimePartition(PartitionProtocol):
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


class ScheduleItem:
    def __init__(
        self,
        name: str,
        default: int | float,
        *,
        minimum: int | float | None = None,
        ideal: int | float | None = None,
        maximum: int | float | None = None,
    ):
        self.name = name
        self.default = default
        self.ideal = ideal or self.default
        self.minimum = min(default, minimum or default, self.ideal)
        self.maximum = max(default, maximum or default, self.ideal)

    def __repr__(self) -> str:
        return f"ScheduleItem({self.minimum} ≤ {self.default} ≤ {self.maximum}, ideal={self.ideal})"

    def __str__(self) -> str:
        return f"ScheduleItem({self.minimum} ≤ {self.default} ≤ {self.maximum}, ideal={self.ideal})"

    def rescaled(self, scale_factor: float) -> "ScheduleItem":
        return ScheduleItem(
            self.name,
            self.default * scale_factor,
            minimum=self.minimum * scale_factor,
            ideal=self.ideal * scale_factor,
            maximum=self.maximum * scale_factor,
        )


class ScheduleItems(list[ScheduleItem]):
    """ """

    def __init__(self, items: Iterable[ScheduleItem]):
        items = list(items)
        if not len(set(items)) == len(items):
            raise ValueError("Item names must be unique.")
        super().__init__(items)

    @property
    def default(self) -> float:
        return sum(map(lambda it: it.default, self))

    @property
    def minimum(self) -> float:
        return sum(map(lambda it: it.minimum, self))

    @property
    def ideal(self) -> float:
        return sum(map(lambda it: it.ideal, self))

    @property
    def maximum(self) -> float:
        return sum(map(lambda it: it.maximum, self))

    def __repr__(self) -> str:
        return f"ItemSequence(\n    {'\n    '.join(map(repr, self))}\n)"

    def __str__(self) -> str:
        return f"ItemSequence(\n    {'\n    '.join(map(repr, self))}\n)"


# migrate Entry from consilium?
