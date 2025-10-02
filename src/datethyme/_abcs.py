from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from itertools import pairwise
from typing import Generic, Literal, Protocol, Self, TypeVar, cast

from multipledispatch import dispatch

from ._scheduling_utils import (
    _Atomic,
    _SpanLike,
    _TimeLike,
    apply_pairwise,
    earliest_start,
    get_relative_lengths,
    latest_end,
    snap_back,
    snap_forward,
    split_gap_equal,
    split_gap_inverse_proportional,
    split_gap_proportional,
    split_overlap_equal,
    split_overlap_inverse_proportional,
    split_overlap_proportional,
    stack_backward,
    stack_forward,
    stack_from_middle,
)
from .utils import (
    assert_xor,
)

TimeUnit = TypeVar("TimeUnit", bound=Literal["day", "hour", "minute", "second"])


class OptionalDate(ABC):
    year: int | None
    month: int | None
    day: float | None

    @abstractmethod
    def __lt__(self, other) -> bool: ...


class OptionalTime(ABC):
    hour: int | None
    minute: int | None
    second: float | None

    @abstractmethod
    def __lt__(self, other) -> bool: ...


class OptionalDateTime(ABC):
    year: int | None
    month: int | None
    day: int | None
    hour: int | None
    minute: int | None
    second: float | None

    @abstractmethod
    def __lt__(self, other) -> bool: ...


Atom = TypeVar("Atom", bound=_Atomic)
TT = TypeVar("TT", bound=_TimeLike)
PairCallback = Callable[
    [tuple["AbstractSpan", "AbstractSpan"]], tuple["AbstractSpan", "AbstractSpan"]
]


class AbstractTime(ABC):
    """
    Defines the common interface that both Time and DateTime are required to implement.
    """
    hour: int
    minute: int
    second: float


class AbstractDate(ABC):
    year: int
    month: int
    day: float


class AbstractRange(ABC, Generic[Atom]):
    start: Atom
    stop: Atom
    step: int
    inclusive: bool
    _current: Atom

    @abstractmethod
    def __init__(self, start: Atom, stop: Atom, step: int = 1, inclusive: bool = True) -> None: ...

    @property
    @abstractmethod
    def last(self) -> Atom: ...

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __contains__(self, item: Atom) -> bool: ...

    @abstractmethod
    def __reversed__(self) -> Iterable[Atom]: ...

    @abstractmethod
    def __getitem__(self, idx): ...

    def __iter__(self) -> Iterator[Atom]:
        self._restart()
        return self

    def __next__(self) -> Atom:
        if self._current < self.stop:
            self._increment()
            return self._current
        else:
            raise StopIteration

    def __eq__(self, other) -> bool:
        return all(
            (
                self.start == other.start,
                self.stop == other.stop,
                self.step == other.step,
                self.inclusive == other.inclusive,
            )
        )

    def __hash__(self) -> int:
        return hash((hash(self.start), hash(self.stop), self.step, self.inclusive))

    @abstractmethod
    def index(self, item: Atom) -> int: ...

    def filtered(self, predicate: Callable[[Atom], bool]) -> Iterator[Atom]:
        """
        Generic filtered iterator.
        """
        for atom in self:
            if predicate(atom):
                yield atom

    @abstractmethod
    def _increment(self) -> None: ...

    def _restart(self) -> None:
        self._current = self.start

    # @property
    # @abstractmethod
    # def string_list(self) -> list[str]: ...


class AbstractSpan(_SpanLike, ABC, Generic[Atom]):
    start: Atom
    end: Atom

    @abstractmethod
    def __init__(self, start: Atom, end: Atom): ...

    @property
    @abstractmethod
    def days(self) -> float: ...

    @property
    @abstractmethod
    def hours(self) -> float: ...

    @property
    @abstractmethod
    def minutes(self) -> float: ...

    @property
    @abstractmethod
    def seconds(self) -> float: ...

    @property
    def span(self) -> "AbstractSpan[TT]":
        return self

    def __eq__(self, other) -> bool:
        if isinstance(other, AbstractSpan):
            return (self.start == other.start) and (self.end == other.end)
        return False

    def __contains__(self, other) -> bool:
        return self.contains(other)

    def __bool__(self) -> bool:
        return self.end > self.start

    @abstractmethod
    def intersection(self, other, strict: bool = False): ...  # alias inner

    @abstractmethod
    def hull(self, other: Atom, strict: bool = False): ...  # alias outer, union, cover

    # def union(self, other, strict: bool = False): ...

    @abstractmethod
    def gap(self, other, strict: bool = False) -> "AbstractSpan[Atom]": ...  # alias end_to_start

    @abstractmethod
    def overlap(
        self, other, strict: bool = False
    ) -> "AbstractSpan[Atom]": ...  # alias end_to_start

    @abstractmethod
    def snap_start_to(self, new_start: Atom) -> "AbstractSpan[Atom]": ...

    @abstractmethod
    def split(self, point: Atom) -> tuple["AbstractSpan[Atom]", "AbstractSpan[Atom]"]: ...

    @abstractmethod
    def snap_end_to(self, new_end: Atom) -> "AbstractSpan[Atom]": ...

    @abstractmethod
    def shift_start_rigid(self, new_start: Atom) -> "AbstractSpan[Atom]": ...

    @abstractmethod
    def shift_end_rigid(self, new_end: Atom) -> "AbstractSpan[Atom]": ...

    @abstractmethod
    def interior_point(self, alpha: float) -> Atom: ...

    @abstractmethod  # use dispatch: str | AbstractSpan | AbstractTime
    def contains(self, other, include_start: bool = True, include_end: bool = False) -> bool: ...

    # @abstractmethod
    # @dispatch(str)
    # def contains(self, other: Atom, include_start: bool = True, include_end: bool = False) -> bool: ...

    @abstractmethod
    def affine_transform(
        self,
        scale_factor: float,
        new_start: Atom | None = None,
        new_end: Atom | None = None,
        min_minutes: int | float = 5,
    ) -> "AbstractSpan[Atom]":
        ...
        # new_length = scale_factor * self.minutes
        # if new_start and not new_end:
        #     result = self.__class__(new_start, new_start.add_minutes(new_length))
        # elif new_end and not new_start:
        #     result = self.__class__(new_end.add_minutes(new_length), new_end)
        # else:
        #     raise ValueError

        # if result.minutes < min_minutes:
        #     raise ValueError
        # return result

    def midpoint(self) -> Atom:
        return self.interior_point(0.5)


class DeltaProtocol(Protocol):
    hours: float
    minutes: float
    seconds: float


class AbstractPartition(AbstractSpan, Generic[TT]):
    """
    TODO: add nesting_mode to determine how nested time partitions are resized under different operations
    """

    def __init__(self, spans: Iterable[AbstractSpan[TT]], names: Iterable[str] | None = None):
        if not self.is_contiguous(spans):
            raise ValueError
        self._spans = spans
        self._names = tuple(names) if names else names

    property
    def names(self) -> tuple[str, ...]:
        return tuple(map(self.name, self.spans))

    @property
    def span(self) -> "AbstractSpan[TT]":
        return self.start >> self.end

    @property
    def spans(self) -> tuple[AbstractSpan[TT]]:
        return tuple(self._spans)

    @property
    def start(self) -> TT:
        return min(self.starts)

    @property
    def end(self) -> TT:
        return max(self.ends)

    @property
    def starts(self) -> tuple[TT, ...]:
        return tuple(map(lambda s: s.start, self.spans))

    @property
    def ends(self) -> tuple[TT, ...]:
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
    
    def __contains__(self, other) -> bool:
        return self.contains(other)

    # @classmethod
    # def from_sequence(
    #     cls,
    #     seq: Iterable[AbstractSpan],
    #     mode,
    #     round_to: int = 0,
    # ) -> Self:
    #     meth = {}[mode]
    #     return cls(meth(seq))

    @classmethod
    def from_pipeline(
        cls,
        segments: Iterable[AbstractSpan[TT]],
        pipeline: Callable[[Iterable[AbstractSpan[TT]]], tuple[AbstractSpan[TT]]],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        for step in pipeline:
            segments = step(segments)
        return cls.from_partition(segments, names=names)

    @classmethod
    def from_boundaries(
        cls,
        times: Iterable[TT],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        names = names or (None,) * (len(times := tuple(times)) - 1)
        spans = (a.span(b, name=name) for (a, b), name in zip(pairwise(times), names))
        return cls(spans=spans, names=names)

    @classmethod
    def from_partition(
        cls,
        segments: Iterable[AbstractSpan[TT]],
        names: Iterable[str | None] | None = None,
    ) -> Self:
        return cls(spans=segments, names=names)

    @classmethod
    def from_durations(
        cls,
        *,
        durations: Iterable[int | float],
        start: TT | None,
        end: TT | None,
        names: Iterable[str | None] | None = None,
    ) -> Self:
        anchor_start = assert_xor(start, end)
        if anchor_start:
            ...
        else:
            ...

    @classmethod
    def from_deltas(
        cls,
        *,
        durations: Iterable[DeltaProtocol],
        start: TT | None,
        end: TT | None,
        names: Iterable[str | None] | None = None,
    ) -> Self:
        anchor_start = assert_xor(start, end)
        if anchor_start:
            ...
        else:
            ...

    @classmethod
    def from_relative_lengths(
        cls,
        start: TT,
        end: TT,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self: ...

    @classmethod
    def from_minutes_and_start(
        cls,
        start: TT,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self: ...

    @classmethod
    def from_minutes_and_end(
        cls,
        end: TT,
        segments: Iterable[float],
        names: Iterable[str | None] | None = None,
    ) -> Self: ...

    @classmethod
    def from_pipeline(
        cls,
        segments: Iterable[float],
        pipeline: Iterable[Callable[[AbstractSpan[TT]], AbstractSpan[TT]]],
        names: Iterable[str | None] | None = None,
    ) -> Self: ...

    def contains(self, other: AbstractSpan[TT] | TT) -> float:
        return self.span.contains(other)

    def gap(self, other: AbstractSpan[TT]) -> float:
        return self.span.days

    def hull(self, other: AbstractSpan[TT]) -> float:
        return self.span.hull(other)

    def interior_point(self, alpha: float) -> TT:
        return self.span.interior_point(alpha)

    def intersection(self, other: AbstractSpan[TT]) -> float:
        return self.span.intersection(other)

    def overlap(self, other: AbstractSpan[TT]) -> "AbstractPartition[TT]":
        ...

    def shift_end_rigid(self) -> "AbstractPartition[TT]":
        ...

    def shift_start_rigid(self) -> "AbstractPartition[TT]":
        ...

    def snap_end_to(self) -> "AbstractPartition[TT]":
        ...

    def snap_start_to(self) -> "AbstractPartition[TT]":
        ...

    def split(self) -> "tuple[AbstractPartition[TT], AbstractPartition[TT]]":
        ...

    def span_containing(self, point: TT) -> AbstractSpan[TT] | None:
        for span in self:
            if span.contains(point):
                return span
        return None
    
    def insert(
        self,
        span_start: TT | int,
        new_span: AbstractSpan[TT],
        mode: Literal["SQUEEZE", "PUSH_BACK", "PUSH_FORWARD"],
        split_incumbent: bool = True,
    ) -> "AbstractPartition[TT]":
        ...

    def index_from_name(self, name: str) -> int | None:
        ...

    def index_from_time(self, point: TT) -> int | None:
        ...

    def affine_transform(
        self,
        scale_factor: float,
        new_start: TT | None = None,
        new_end: TT | None = None,
        min_minutes: int | float = 5,
    ) -> AbstractSpan[TT]:
        new_length = scale_factor * self.minutes
        if new_start and not new_end:
            result = self.__class__(new_start, new_start.add_minutes(new_length))
        elif new_end and not new_start:
            result = self.__class__(new_end.add_minutes(new_length), new_end)
        else:
            raise ValueError

        if result.minutes < min_minutes:
            raise ValueError
        return result

    def reordered(
        self, orderer: Callable[[AbstractSpan[TT]], int | float | str | TT]
    ) -> "AbstractPartition[TT]":
        reordered = sorted(self.spans, key=orderer)
        return self.__class__.from_partition(stack_forward(reordered))

    def round_hours(self, round_to: int) -> "AbstractPartition[TT]":
        return self.__class__((span.round_hours(round_to) for span in self.spans))

    def round_minutes(self, round_to: int) -> "AbstractPartition[TT]":
        return self.__class__((span.round_minutes(round_to) for span in self.spans))

    def round_seconds(self, round_to: float) -> "AbstractPartition[TT]":
        return self.__class__((span.round_seconds(round_to) for span in self.spans))

    @staticmethod
    def eclipse_forward(
        seq: Iterable[AbstractSpan[TT]],
    ) -> tuple[tuple[AbstractSpan[TT], ...], tuple[AbstractSpan[TT], ...]]:
        if not seq:
            return tuple(), tuple()

        spans: list[AbstractSpan[TT]] = [(seq := list(seq))[0]]
        rejects: list[AbstractSpan] = []
        _current = seq[0].end

        for span in seq[1:]:
            rejected_span, kept_span = span.split(max(_current, span.start))
            if kept_span:
                spans.append(kept_span)
            if rejected_span:
                rejects.append(rejected_span)
            _current = max(_current, kept_span.end)

        return tuple(spans), tuple(rejects)

    @staticmethod
    def eclipse_backward(
        seq: Iterable[AbstractSpan[TT]],
    ) -> tuple[tuple[AbstractSpan[TT], ...], tuple[AbstractSpan[TT], ...]]:
        if not seq:
            return tuple(), tuple()

        spans: list[AbstractSpan] = [(seq := list(seq))[-1]]
        rejects: list[AbstractSpan] = []
        _current = seq[0].end

        for span in seq[-2::-1]:
            kept_span, rejected_span = span.split(min(_current, span.end))
            if kept_span:
                spans.append(kept_span)
            if rejected_span:
                rejects.append(rejected_span)
            _current = min(_current, kept_span.end)

        return tuple(spans), tuple(rejects)

    @staticmethod
    def resolve_overlaps(
        seq: Iterable[AbstractSpan[TT]],
        mode: Literal["EQUAL", "PROPORTIONAL", "INVERSE"],
    ) -> tuple[AbstractSpan[TT], ...]:
        if mode == "EQUAL":
            return tuple(apply_pairwise(split_overlap_equal, seq))
        elif mode == "PROPORTIONAL":
            return tuple(apply_pairwise(split_overlap_proportional, seq))
        elif mode == "INVERSE":
            return tuple(apply_pairwise(split_overlap_inverse_proportional, seq))
        else:
            raise ValueError(f"Invalid mode for method 'resolve_overlaps': '{mode}'")

    @staticmethod
    def resolve_gaps(
        seq: Iterable[AbstractSpan[TT]],
        mode=Literal["EQUAL", "PROPORTIONAL", "INVERSE", "SNAP_FORWARD", "SNAP_BACK"],
    ) -> tuple[AbstractSpan[TT]]:
        if mode == "EQUAL":
            return tuple(apply_pairwise(split_gap_equal, seq))
        if mode == "PROPORTIONAL":
            return tuple(apply_pairwise(split_gap_proportional, seq))
        if mode == "INVERSE":
            return tuple(apply_pairwise(split_gap_inverse_proportional, seq))
        if mode == "SNAP_FORWARD":
            return tuple(apply_pairwise(snap_forward, seq))
        if mode == "SNAP_BACK":
            return tuple(apply_pairwise(snap_back, seq))
        raise ValueError(f"Invalid mode for method 'resolve_gaps': '{mode}'")

    @staticmethod
    def squeeze(
        seq: Iterable[AbstractSpan],
        mode: Literal["PROPORTIONAL", "EQUAL"],
        earliest: TT | None = None,
        latest: TT | None = None,
        min_minutes: int | float = 5,
    ) -> tuple[AbstractSpan[TT], ...]:
        spans: list[AbstractSpan[TT]] = []
        earliest: TT = earliest or earliest_start(seq)
        latest: TT = latest or latest_end(seq)
        if mode == "PROPORTIONAL":
            relative_lengths = get_relative_lengths(seq)
        elif mode == "EQUAL":
            seq = list(seq)
            relative_lengths = [x / len(seq) for x in range(len(seq))]
        else:
            raise ValueError(f"Invalid mode for method 'squeeze': '{mode}'")

        earliest: TT = earliest or earliest_start(seq)
        latest: TT = latest or latest_end(seq)
        new_total: float = cast(TT, earliest).minutes_to(latest)
        _current = earliest
        for span, rel_length in zip(seq, relative_lengths):
            spans.append(
                squeezed := span.affine_transform(
                    scale_factor=rel_length * new_total,
                    new_start=_current,
                    min_minutes=min_minutes,
                )
            )
            _current = squeezed.end
        return tuple(spans)

    @staticmethod
    def squeeze_with_rollover(
        seq: Iterable[AbstractSpan[TT]],
        mode=Literal["PROPORTIONAL", "EQUAL"],
        earliest: TT | None = None,
        latest: TT | None = None,
        min_minutes: int | float = 5,
    ) -> tuple[tuple[AbstractSpan[TT], ...], tuple[AbstractSpan[TT], ...]]:
        seq = list(seq)
        keep_n = (
            int(len(seq) // min_minutes)
            if earliest and latest and (len(seq) * min_minutes) > earliest.minutes_to(latest)
            else len(seq)
        )
        return (
            AbstractPartition.squeeze(
                seq[:keep_n], mode=mode, earliest=earliest, latest=latest, min_minutes=min_minutes
            ),
            tuple(seq[keep_n:]),
        )

    @staticmethod
    def stack(
        seq: Iterable[AbstractSpan[TT]], mode=Literal["FORWARD", "OUTWARD", "BACKWARD"], anchor=None
    ) -> tuple[AbstractSpan[TT], ...]:
        func = {
            "FORWARD": stack_forward,
            "OUTWARD": stack_from_middle,
            "BACKWARD": stack_backward,
        }.get(mode)
        if not func:
            raise ValueError(f"Invalid mode for method 'stack': '{mode}'")
        return tuple(func(seq, anchor))

    @staticmethod
    def is_contiguous(seq: AbstractSpan[TT]) -> bool:
        return all(map(lambda pair: pair[0].end == pair[1].start, pairwise(seq)))

    # TO ADD ---------------------------------------------------------------------------------------

    # FROM ABC -------------------------------------------------

    
