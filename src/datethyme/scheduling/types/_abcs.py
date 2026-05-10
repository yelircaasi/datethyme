from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from functools import lru_cache
from itertools import pairwise
from typing import Self

from ..._abcs import AbstractSpan
from ...constants import Unit
from ...exceptions import TemporalLogicError
from ...protocols import (
    DeltaProtocol,
    EntryProtocol,
    PartitionProtocol,
    ResultTriple,
    SpanProtocol,
    TimeProtocol,
)
from ...utils import assert_xor
from ..algorithms import (
    is_contiguous,
    stack_forward,
)
from ..utils import is_partitioned


class AbstractPartition[T: TimeProtocol](PartitionProtocol, ABC):
    def __init__(
        self,
        spans: Iterable[SpanProtocol[T]],
        names: Iterable[str | None] | None = None,
    ) -> None:
        if not is_contiguous(spans):
            raise ValueError

        self._spans = list(spans)
        self._names = list(names) if names else names

        if names and not (len(self.spans) == len(self.names)):
            raise ValueError

    def __getitem__(self, idx: str) -> SpanProtocol[T]:
        for span in self._spans:
            if span.name == idx:
                return span
        raise IndexError

    @property
    @lru_cache
    def stable_random_id(self) -> str:
        return str(hash(self))[:8]

    @property
    @lru_cache
    def name(self) -> str:
        return f"Partition{self.stable_random_id}[{self.start!s}-{self.end!s})]"

    @staticmethod
    def is_contiguous(seq: Iterable[SpanProtocol]) -> bool:
        return is_contiguous(seq)

    @property
    def named_spans(self) -> tuple[tuple[str, SpanProtocol[T]], ...]:
        return tuple(zip(self.names, self._spans))

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(map(lambda sp: sp.name, self.spans))

    @property
    def span(self) -> SpanProtocol[T]:
        return self.start.to(self.end)

    @property
    def midpoint(self) -> T:
        return self.span.midpoint

    @property
    def spans(self) -> tuple[SpanProtocol[T], ...]:
        return tuple(self._spans)

    @property
    def start(self) -> T:
        return min(self.starts)

    @property
    def end(self) -> T:
        return max(self.ends)

    @property
    def starts(self) -> tuple[T, ...]:
        return tuple(map(lambda s: s.start, self.spans))

    @property
    def ends(self) -> tuple[T, ...]:
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
        return self.end > self.start

    def __contains__(self, other: object) -> bool:
        return self.contains(other)

    # @classmethod
    # def from_sequence(
    #     cls,
    #     seq: Iterable[SpanProtocol[T]],
    #     mode,
    #     round_to: int = 0,
    # ) -> Self:
    #     meth = {}[mode]
    #     return cls(meth(seq))

    @classmethod
    def from_starts(
        cls,
        starts: dict[T, str] | Iterable[T],
        end: T,
    ) -> Self:
        names = tuple(starts.values()) if isinstance(starts, dict) else None
        starts = tuple(starts)
        last_span = starts[0].span(end)
        span_class: type[SpanProtocol[T]] = last_span.__class__

        def make_span(tup: tuple[T, T]) -> SpanProtocol[T]:
            return span_class(start=tup[0], end=tup[1])

        other_spans = map(make_span, pairwise(starts))
        return cls(spans=(*other_spans, last_span), names=names)

    @classmethod
    def from_ends(
        cls,
        ends: dict[T, str] | Iterable[T],
        start: T,
    ) -> Self:
        names = tuple(ends.values()) if isinstance(ends, dict) else None
        ends = tuple(ends)
        first_span = start.span(ends[0])
        span_class: type[SpanProtocol[T]] = first_span.__class__

        def make_span(tup: tuple[T, T]) -> SpanProtocol[T]:
            return span_class(start=tup[0], end=tup[1])

        other_spans = map(make_span, pairwise(ends))
        return cls(spans=(first_span, *other_spans), names=names)

    @classmethod
    def from_pipeline(
        cls,
        segments: Iterable[SpanProtocol[T]],
        pipeline: Iterable[Callable[[Iterable[SpanProtocol[T]]], Iterable[SpanProtocol[T]]]],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        for step in pipeline:
            segments = step(segments)
        return cls.from_partition(segments, names=names)

    @classmethod
    def from_boundaries(
        cls,
        times: Iterable[T],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        names = names or (None,) * (len(times := tuple(times)) - 1)
        spans = (a.span(b) for (a, b), name in zip(pairwise(times), names))
        return cls(spans=spans, names=names)

    @classmethod
    def from_partition(
        cls,
        segments: Iterable[SpanProtocol[T]],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        return cls(spans=segments, names=names)

    @classmethod
    def from_minutes(
        cls,
        *,
        minute_durations: Iterable[int | float],
        start: T | None = None,
        end: T | None = None,
        names: Iterable[str | None] | None = None,
    ) -> Self:
        anchor_start = assert_xor(start, end)
        if not anchor_start:
            total = sum(minute_durations)
            assert end
            start = end.add_minutes(-total)
        spans = []
        assert start
        current: T = start
        for duration in minute_durations:
            spans.append(current.span(current.add_minutes(duration)))
        return cls(spans)

    @classmethod
    def from_deltas(
        cls,
        *,
        deltas: Iterable[DeltaProtocol],
        start: T | None,
        end: T | None,
        names: Iterable[str | None] | None = None,
    ) -> Self:
        minute_durations = [x.minutes for x in deltas]
        return cls.from_minutes(
            minute_durations=minute_durations,
            start=start,
            end=end,
            names=names,
        )

    @classmethod
    def from_relative_lengths(
        cls,
        start: T,
        end: T,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        total_weight = sum(segments)
        total_minutes = start.minutes_to(end)
        minute_durations = [seg * total_minutes / total_weight for seg in segments]
        return cls.from_minutes(
            minute_durations=minute_durations,
            start=start,
            end=end,
            names=names,
        )

    def partition_element(
        self,
        element_id: str,
        subelements: PartitionProtocol[T] | Iterable[SpanProtocol[T] | EntryProtocol],
        min_length: int = 1,
        max_length: int | None = None,
    ) -> Self:
        element = self[element_id]
        print(element)
        if isinstance(subelements, PartitionProtocol):
            ...
        elif isinstance(subelements, EntryProtocol):
            ...
        return self

    def round_hours(self, round_to: int | float = 1, round_down: bool = False) -> Self:
        return self.__class__(
            spans=tuple(span.round_hours(round_to) for span in self.spans),
            names=tuple(span.name for span in self.spans),
        )

    def round_minutes(self, round_to: int | float = 1, round_down: bool = False) -> Self:
        return self.__class__(spans=tuple(span.round_minutes(round_to) for span in self.spans))

    def round_seconds(self, round_to: int | float = 1, round_down: bool = False) -> Self:
        return self.__class__(span.round_seconds(round_to) for span in self.spans)

    def contains(
        self,
        other,
        include_start: bool = True,
        include_end: bool = False,
    ) -> bool:
        ...
        return self.span.contains(
            other.span,
            include_start=include_start,
            include_end=include_end,
        )

    def gap(self, other, strict: bool = False) -> SpanProtocol[T] | None: ...

    def hull(self, other, strict: bool = False) -> SpanProtocol[T]:
        return self.span.hull(other)

    def interior_point(self, alpha: float) -> T:
        return self.span.interior_point(alpha)

    def intersection(self, other, strict: bool = False) -> PartitionProtocol[T] | None:
        ...
        # return self.span.intersection(other)

    def overlap(self, other, strict: bool = False) -> PartitionProtocol[T] | None: ...

    def shift_end_rigid(self, new_end: T) -> Self:
        new_spans = []
        shift = self.end.seconds_to(new_end)
        for span in self._spans:
            new_span = span.__class__(  # could implement .shift_seconds()
                start=span.start.add_seconds(shift),
                end=span.end.add_seconds(shift),
            )
            new_spans.append(new_span)
        return self

    def shift_seconds(self, n: int | float) -> Self:
        new_spans = []
        for span in self._spans:
            new_span = span.__class__(  # could implement .shift_seconds()
                start=span.start.add_seconds(n),
                end=span.end.add_seconds(n),
            )
            new_spans.append(new_span)
        self._spans = new_spans
        return self

    def shift_start_rigid(self, new_start: T) -> Self:
        shift = self.end.seconds_to(new_start)
        return self.shift_seconds(shift)

    def snap_end_to(self, new_end: T) -> Self:
        self._end = new_end
        return self

    def snap_start_to(self, new_start: T) -> Self:
        # may be better to add checks
        self._start = new_start
        return self

    def split(self, cut_point: T) -> tuple[PartitionProtocol[T], PartitionProtocol[T]]:
        if not self.start <= cut_point <= self.end:
            raise TemporalLogicError
        first = []
        second = []
        trouble = []
        for span in self.spans:
            if span.end <= cut_point:
                first.append(span)
            elif span.start <= cut_point:
                second.append(span)
            else:
                trouble.append(span)
        if trouble:
            if len(trouble) > 1:
                raise TemporalLogicError
            span_to_cut = trouble[0]
            first.append(span_to_cut.start.span(cut_point))
            second.insert(0, cut_point.span(span_to_cut.end))

        return self.__class__(first), self.__class__(second)

    def span_containing(self, point: T) -> SpanProtocol[T] | None:
        for span in self._spans:
            if span.contains(point):
                return span
        return None

    # def insert(
    #     self,
    #     span_start: T | int,
    #     new_span: SpanProtocol[T],
    #     mode: Literal["SQUEEZE", "PUSH_BACK", "PUSH_FORWARD"],
    #     split_incumbent: bool = True,
    # ) -> PartitionProtocol[T]:

    def index_from_name(self, name: str) -> int | None:
        for i, span in enumerate(self.spans):
            if span.name == name:
                return i
        return None

    def index_from_time(self, point: T) -> int | None:
        for i, span in enumerate(self.spans):
            if span.start <= point < span.end:
                return i
        return None

    def forward_affine_transform(
        self,
        scale_factor: float,
        new_start: T | None = None,
        min_minutes: int | float = 5,
    ) -> Self:
        new_spans = []
        current = new_start or self.start
        for span in self._spans:
            new_span = span.forward_affine_transform(
                scale_factor=scale_factor,
                new_start=current,
                min_minutes=min_minutes,
            )
            new_spans.append(new_span)
            current = new_span.end
        self._spans = new_spans

        if self.minutes < min_minutes:
            raise ValueError

        return self

    def backward_affine_transform(
        self,
        scale_factor: float,
        new_end: T | None = None,
        min_minutes: int | float = 5,
    ) -> Self:
        new_spans = []
        current = new_end or self.start
        for span in self._spans[::-1]:
            new_span = span.forward_affine_transform(
                scale_factor=scale_factor,
                new_start=current,
                min_minutes=min_minutes,
            )
            new_spans.append(new_span)
            current = new_span.end
        self._spans = new_spans

        if self.minutes < min_minutes:
            raise ValueError

        return self

    def reordered(self, orderer: Callable[[SpanProtocol[T]], int | float | str | T]) -> Self:
        reordered = sorted(self.spans, key=orderer)
        return self.__class__.from_partition(stack_forward(reordered))

    # FROM TimePartition -------------------------------------------------

    @property
    @abstractmethod
    def passes_day_boundary(self) -> bool: ...

    # DEV ONLY -----------------------------------------------------------------------------------
    # class PartitionProtocol[T]():

    # spans: Iterable[SpanProtocol[T]]
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

    def iter_nested(self) -> Iterator[tuple[int, SpanProtocol[T]]]:
        denested = []
        for span in self._spans:
            if isinstance(span, AbstractPartition):
                denested.extend(list(span.iter_nested()))
            else:
                denested.append(span)
        return iter(denested)

    def __str__(self) -> str:
        return "PLACEHOLDER"  # {self}"

    def __repr__(self) -> str:
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

        def format_span(span: SpanProtocol):
            return f"{span.start} - {span.name}"

        return (
            "TimePartition(\n    "
            f"{'\n    '.join(map(format_span, self.spans))}"
            f"\n    {self.end} - <END>\n)"
        )

    # def repr_indented(self, span: PartitionProtocol[T], indent: int) -> str:
    #     prefix = indent * " "
    #     if isinstance(span, PartitionProtocol[T]):

    #     return ("\n" + (" " * indent)).join(map(partial(self.format_span, indent=indent), span))

    @staticmethod
    def format_span(span: SpanProtocol[T] | PartitionProtocol[T], indent: int = 0) -> str:
        prefix = indent * " "
        if isinstance(span, SpanProtocol):
            return f"{prefix}{span.start} - {id(span)}"
        elif isinstance(span, PartitionProtocol):
            return repr(span).replace("\n", "\n" + prefix)
        raise ValueError


class AbstractBlock[T: TimeProtocol](AbstractSpan, ABC):
    def __init__(
        self,
        start: T,
        end: T,
        name: str | None = None,
        subentries: list[SpanProtocol[T]] | None = None,
    ) -> None:
        self._start = start
        self._end = end
        self._name = name
        self._subentries = subentries or []
        self.assert_partitioned()

    @property
    def name(self) -> str:
        return self._name or f"TimeSpan[id{str(hash(self))[:16]}]"

    @property
    def start(self) -> T:
        return self._start

    @property
    def end(self) -> T:
        return self._end

    def assert_partitioned(self) -> None:
        if not is_partitioned(self._subentries):
            msg = f"Data is not a correct partition:\n{self._subentries}"
            raise TemporalLogicError(msg)

    @property
    def seconds(self) -> float:
        self.assert_validity()
        return round(self._start.minutes_to(self._end) * Unit.MINUTE.seconds)

    @property
    def minutes(self) -> float:
        self.assert_validity()
        return round(self._start.minutes_to(self._end))

    @property
    def hours(self) -> float:
        self.assert_validity()
        return round(self._start.minutes_to(self._end) / Unit.HOUR.minutes)

    @property
    def days(self) -> float:
        self.assert_validity()
        return round(self._start.minutes_to(self._end) / Unit.DAY.minutes)

    def assert_validity(self) -> None: ...

    @abstractmethod
    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]: ...

    @abstractmethod
    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]: ...
