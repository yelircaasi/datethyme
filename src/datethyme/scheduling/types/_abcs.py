from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from functools import lru_cache
from itertools import pairwise
from typing import Literal, Self

from ...core import TimeSpan
from ...protocols import (
    DeltaProtocol,
    EntryProtocol,
    PartitionProtocol,
    SpanProtocol,
    TimeProtocol,
)
from ...utils import assert_xor
from ..algorithms import (
    is_contiguous,
    stack_forward,
)


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
        raise NotImplementedError

    @property
    def named_spans(self) -> tuple[tuple[str, SpanProtocol[T]], ...]:
        return tuple(zip(self.names, self._spans))

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(map(lambda sp: sp.name, self.spans))

    @property
    def span(self) -> SpanProtocol[T]:
        return self.start.to(self.end)  # TODO # type: ignore

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
        spans: dict[T, str] | Iterable[T],
        start: T,
    ) -> Self:
        raise NotImplementedError

    @classmethod
    def from_ends(
        cls,
        spans: dict[T, str] | Iterable[T],
        start: T,
    ) -> Self:
        raise NotImplementedError

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
    def from_durations(
        cls,
        *,
        durations: Iterable[int | float],
        start: T | None,
        end: T | None,
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
        start: T | None,
        end: T | None,
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
        start: T,
        end: T,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        raise NotImplementedError

    def partition_element(
        self,
        element_id: str,
        other: PartitionProtocol[T] | Iterable[EntryProtocol],
        min_length: int = 1,
        max_length: int | None = None,
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
        start: T,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        raise NotImplementedError

    @classmethod
    def from_minutes_and_end(
        cls,
        end: T,
        minutes: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        raise NotImplementedError

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

    def shift_end_rigid(self, new_end: T) -> PartitionProtocol[T]:
        raise NotImplementedError

    def shift_start_rigid(self, new_start: T) -> PartitionProtocol[T]:
        raise NotImplementedError

    def snap_end_to(self, new_end: T) -> PartitionProtocol[T]:
        raise NotImplementedError

    def snap_start_to(self, new_start: T) -> PartitionProtocol[T]:
        raise NotImplementedError

    def split(self, cut_point: T) -> tuple[PartitionProtocol[T], PartitionProtocol[T]]:
        raise NotImplementedError

    def span_containing(self, point: T) -> SpanProtocol[T] | None:
        for span in self._spans:
            if span.contains(point):
                return span
        return None

    def insert(
        self,
        span_start: T | int,
        new_span: SpanProtocol[T],
        mode: Literal["SQUEEZE", "PUSH_BACK", "PUSH_FORWARD"],
        split_incumbent: bool = True,
    ) -> PartitionProtocol[T]:
        raise NotImplementedError

    def index_from_name(self, name: str) -> int | None:
        raise NotImplementedError

    def index_from_T(self, point: T) -> int | None:
        raise NotImplementedError

    def forward_affine_transform(  # TODO
        self,
        scale_factor: float,
        new_start: T | None = None,
        min_minutes: int | float = 5,
    ) -> Self:
        new_length = scale_factor * self.minutes
        new_start = new_start or self.start
        result = self.__class__(new_start, new_start.add_minutes(new_length))  # type: ignore

        if result.minutes < min_minutes:
            raise ValueError
        return result

    def backward_affine_transform(  # TODO
        self,
        scale_factor: float,
        new_end: T | None = None,
        min_minutes: int | float = 5,
    ) -> Self:
        new_length = scale_factor * self.minutes
        new_end = new_end or self.start
        result = self.__class__(new_end.add_minutes(-new_length), new_end)  # type: ignore

        if result.minutes < min_minutes:
            raise ValueError
        return result

    def reordered(self, orderer: Callable[[SpanProtocol[T]], int | float | str | T]) -> Self:
        reordered = sorted(self.spans, key=orderer)
        return self.__class__.from_partition(stack_forward(reordered))  # type: ignore

    # FROM TimePartition -------------------------------------------------

    @property
    @abstractmethod
    def passes_day_boundary(self) -> bool: ...

    @classmethod
    def eclipse_forward(cls, spans: Iterable[SpanProtocol[T]]) -> Self:
        raise NotImplementedError

    @classmethod
    def eclipse_backward(cls, spans: Iterable[SpanProtocol[T]]) -> Self:
        raise NotImplementedError

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
            "TimePartition(\n    "
            f"{'\n    '.join(map(format_span, self.spans))}"  # TODO # type: ignore
            f"\n    {self.end} - <END>\n)"
        )

    # def repr_indented(self, span: PartitionProtocol[T], indent: int) -> str:
    #     prefix = indent * " "
    #     if isinstance(span, PartitionProtocol[T]):

    #     return ("\n" + (" " * indent)).join(map(partial(self.format_span, indent=indent), span))

    @staticmethod
    @abstractmethod
    def format_span(span: SpanProtocol[T] | PartitionProtocol[T], indent: int = 0) -> str: ...
