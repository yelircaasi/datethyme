from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Generic, Literal, Protocol, TypeVar

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


PointType = OptionalDate | OptionalTime | OptionalDateTime
T = TypeVar("T", bound=PointType)


class IntervalType(Protocol):
    start: PointType
    end: PointType


class AbstractSpan(ABC, Generic[T]):
    start: T
    end: T

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

    @abstractmethod
    def hull(self, other, strict: bool = False): ...  # alias outer, union, cover

    @abstractmethod
    def intersection(self, other, strict: bool = False): ...  # alias inner

    @abstractmethod
    def gap(self, other, strict: bool = False): ...  # alias end_to_start

    @abstractmethod
    def start_to_start(self, other): ...

    @abstractmethod
    def end_to_end(self, other): ...


class AbstractRange(ABC, Generic[T]):
    start: T
    stop: T
    step: int
    inclusive: bool
    _current: T

    def __iter__(self) -> Iterator[T]:
        self._restart()
        return self

    def _restart(self) -> None:
        self._current = self.start

    @abstractmethod
    def __init__(self, start: T, stop: T, step: int = 1, inclusive: bool = True) -> None: ...

    @abstractmethod
    def __len__(self) -> int: ...

    def __next__(self) -> T:
        if self._current < self.stop:
            self._increment()
            return self._current
        else:
            raise StopIteration

    # @property
    # def start(self) -> int: ...
    # @property
    # def stop(self) -> int: ...
    # @property
    # def step(self) -> int: ...
    # @overload
    # def __new__(cls, stop: SupportsIndex, /) -> Self: ...
    # @overload
    # def __new__(cls, start: SupportsIndex, stop: SupportsIndex,
    #     step: SupportsIndex = ..., /) -> Self: ...

    @abstractmethod
    def count(self, item: T) -> int: ...

    @abstractmethod
    def index(self, item: T) -> int: ...

    @abstractmethod
    def _increment(self) -> None: ...

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
    def __contains__(self, item: T) -> bool: ...

    @abstractmethod
    def __getitem__(self, idx: int) -> T: ...

    # @overload
    # def __getitem__(self, key: slice, /) -> range: ...

    @abstractmethod
    def __reversed__(self) -> Iterable[T]: ...

    @property
    @abstractmethod
    def last(self) -> T: ...

    # @property
    # @abstractmethod
    # def string_list(self) -> list[str]: ...
