from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, Protocol, Self, TypeVar, overload, runtime_checkable

from pydantic import NonNegativeInt

TimeUnit = TypeVar("TimeUnit", bound=Literal["day", "hour", "minute", "second"])


@runtime_checkable
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
class AtomProtocol(Protocol):
    def __bool__(self) -> bool: ...
    def __eq__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_minutes(self) -> float: ...
    def to_seconds(self) -> float: ...
    @classmethod
    def from_seconds(cls, n: float | int, places: int | None = 10) -> Self: ...
    # @overload
    def range(
        self,
        # stop: Self | int,
        # *,
        # unit: Unit,
        # step: int = 1,
        # inclusive: bool = False,
        *args,
        **kwargs,
    ) -> RangeProtocol[Self]: ...

    # @overload
    # def range(
    #     self,
    #     stop: Self | int,
    #     *,
    #     step: int = 1,
    #     inclusive: bool = False,
    # ) -> RangeProtocol[Self]: ...


@runtime_checkable
class TimeProtocol(AtomProtocol, Protocol):
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

    def round_hours(self, round_to: int | float = 1, round_down: bool = False) -> Self: ...

    def round_minutes(self, round_to: int | float = 1, round_down: bool = False) -> Self: ...

    def round_seconds(self, round_to: int | float = 1, round_down: bool = False) -> Self: ...


@runtime_checkable
class RangeProtocol[T: AtomProtocol](Protocol):
    start: T
    stop: T
    step: int
    inclusive: bool

    @property
    def seconds_per_step(self) -> int: ...

    @overload
    def __getitem__(self, idx: int) -> T: ...
    @overload
    def __getitem__(self, idx: slice) -> RangeProtocol[T]: ...


@runtime_checkable
class DurationProtocol(Protocol):
    start: TimeProtocol
    end: TimeProtocol


@runtime_checkable
class SpanProtocol[T: TimeProtocol](DurationProtocol, Protocol):
    @property
    def name(self) -> str: ...
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
    def round_hours(
        self, round_to: int | float = 1, round_down: bool = False
    ) -> SpanProtocol[T]: ...
    def round_minutes(
        self, round_to: int | float = 1, round_down: bool = False
    ) -> SpanProtocol[T]: ...
    def round_seconds(
        self, round_to: int | float = 1, round_down: bool = False
    ) -> SpanProtocol[T]: ...

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


@runtime_checkable
class PartitionProtocol[Atom](SpanProtocol, Protocol):
    start: Atom
    end: Atom

    @classmethod
    def from_starts(
        cls,
        spans: dict[Atom, str] | Iterable[Atom],
        end: Atom,
    ) -> Self: ...

    @classmethod
    def from_ends(
        cls,
        spans: dict[Atom, str] | Iterable[Atom],
        start: Atom,
    ) -> Self: ...

    def partition_element(
        self,
        element_id: str,
        other: PartitionProtocol[Atom] | Iterable[EntryProtocol],
        min_length: int = 1,
        max_length: int | None = None,
    ) -> Self: ...


@runtime_checkable
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
    def projects(self) -> set[str]: ...

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

class TimeBlockProtocol(PartitionProtocol, Protocol):
    ...

class EntriesProtocol(Protocol): ...
