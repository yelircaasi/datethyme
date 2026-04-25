from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Literal, Protocol, Self, TypeVar, runtime_checkable

from pydantic import NonNegativeInt

TimeUnit = TypeVar("TimeUnit", bound=Literal["day", "hour", "minute", "second"])


class IntervalType(Protocol):
    start: TimeProtocol
    end: TimeProtocol


@runtime_checkable
class DeltaProtocol(Protocol):
    hours: float
    minutes: float
    seconds: float


@runtime_checkable
class DateProtocol(Protocol):
    year: NonNegativeInt
    month: NonNegativeInt
    day: NonNegativeInt

    def __eq__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __le__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...


@runtime_checkable
class TimeProtocol(Protocol):
    hour: int
    minute: int
    second: float

    def __bool__(self) -> bool: ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

    @classmethod
    def parse(cls, raw: str) -> Self: ...

    def to(self, __other) -> SpanProtocol: ...
    def span(self, __other) -> SpanProtocol: ...

    @property
    def ordinal(self) -> float: ...

    @classmethod
    def from_ordinal(cls, ordinal: float) -> Self: ...

    def minutes_to(self, other) -> float: ...

    def minutes_from(self, other) -> float: ...

    def add_minutes(self, n: int | float) -> Self: ...

    def round_hours(self, places: int = 0) -> Self: ...

    def round_minutes(self, places: int = 0) -> Self: ...

    def round_seconds(self, places: int = 0) -> Self: ...


@runtime_checkable
class SpanProtocol[T: TimeProtocol](Protocol):
    @property
    def start(self) -> T: ...
    @property
    def end(self) -> T: ...
    @property
    def minutes(self) -> float: ...
    @property
    def midpoint(self) -> T: ...

    def __init__(self, start: T, end: T) -> None: ...
    def __bool__(self) -> bool: ...
    def snap_start_to(self, new_start: T) -> SpanProtocol[T]: ...
    def snap_end_to(self, new_end: T) -> SpanProtocol[T]: ...
    def shift_start_rigid(self, new_start: T) -> SpanProtocol[T]: ...
    def shift_end_rigid(self, new_end: T) -> SpanProtocol[T]: ...
    def split(self, cut_point: T) -> tuple[SpanProtocol[T], SpanProtocol[T]]: ...
    def interior_point(self, alpha: float) -> T: ...
    def contains(self, other) -> bool: ...
    def round_hours(self, round_to: int) -> SpanProtocol[T]: ...
    def round_minutes(self, round_to: int) -> SpanProtocol[T]: ...
    def round_seconds(self, round_to: float) -> SpanProtocol[T]: ...

    def forward_affine_transform(
        self,
        *,
        scale_factor: float,
        new_start: T | None = None,
        min_minutes: int | float = 5,
    ) -> SpanProtocol[T]: ...

    def backward_affine_transform(
        self,
        *,
        scale_factor: float,
        new_end: T | None = None,
        min_minutes: int | float = 5,
    ) -> SpanProtocol[T]: ...


class PartitionProtocol: ...


# @runtime_checkable
class EntryProtocol[D: DateProtocol](Protocol):
    # name: str
    # priority: float
    # min_time: NonNegativeInt
    # normal_time: NonNegativeInt
    # ideal_time: NonNegativeInt
    # max_time: NonNegativeInt
    # contexts: set[str]
    # dependencies: set[str]

    @property
    def name(self) -> str: ...

    @property
    def priority(self) -> float: ...

    @property
    def min_time(self) -> int: ...

    @property
    def normal_time(self) -> int: ...

    @property
    def ideal_time(self) -> int: ...

    @property
    def max_time(self) -> int: ...

    @property
    def contexts(self) -> set[str | None]: ...

    @property
    def dependencies(self) -> set[str]: ...

    @property
    def due_date(self) -> D | None: ...

    @property
    def earliest_date(self) -> D | None: ...


def make_entry_adapter[T: object, D: DateProtocol](  # noqa: C901 (too complex)
    *,
    get_name: Callable[[T], str],
    get_priority: Callable[[T], float],
    get_min_time: Callable[[T], NonNegativeInt],
    get_normal_time: Callable[[T], NonNegativeInt],
    get_ideal_time: Callable[[T], NonNegativeInt],
    get_max_time: Callable[[T], NonNegativeInt],
    get_contexts: Callable[[T], set[str | None]],
    get_dependencies: Callable[[T], set[str]],
    get_due_date: Callable[[T], D | None],
    get_earliest_date: Callable[[T], D | None],
) -> type[EntryProtocol]:
    class EntryAdapter(EntryProtocol):
        def __init__(
            self,
            entry: T,
        ) -> None:
            self.entry = entry

        @property
        def name(self) -> str:
            return get_name(self.entry)

        @property
        def priority(self) -> float:
            return get_priority(self.entry)

        @property
        def min_time(self) -> int:
            return get_min_time(self.entry)

        @property
        def normal_time(self) -> int:
            return get_normal_time(self.entry)

        @property
        def ideal_time(self) -> int:
            return get_ideal_time(self.entry)

        @property
        def max_time(self) -> int:
            return get_max_time(self.entry)

        @property
        def contexts(self) -> set[str | None]:
            return get_contexts(self.entry)

        @property
        def dependencies(self) -> set[str]:
            return get_dependencies(self.entry)

        @property
        def due_date(self) -> D | None:
            return get_due_date(self.entry)

        @property
        def earliest_date(self) -> D | None:
            return get_earliest_date(self.entry)

    return EntryAdapter


class EntriesProtocol(Protocol): ...


def make_entries_adapter[T: Iterable[EntryProtocol]](
    # TODO
) -> type[EntriesProtocol]:
    class EntriesAdapter: ...

    return EntriesAdapter
