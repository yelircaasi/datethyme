from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from typing import Literal, TypeVar

from .protocols import AtomProtocol, PartitionProtocol, SpanProtocol, TimeProtocol
from .utils import compute_index

TimeUnit = TypeVar("TimeUnit", bound=Literal["day", "hour", "minute", "second"])


class AbstractRange[Atom: AtomProtocol](ABC):
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
    def __getitem__(self, idx) -> Atom: ...

    def __iter__(self) -> Iterator[Atom]:
        self._restart()
        return self

    def __next__(self) -> Atom:
        if self._current < self.stop:  # pyright: ignore
            self._increment()
            return self._current
        else:
            raise StopIteration

    def __eq__(self, other) -> bool:
        return all((
            self.start == other.start,
            self.stop == other.stop,
            self.step == other.step,
            self.inclusive == other.inclusive,
        ))

    def __hash__(self) -> int:
        return hash((hash(self.start), hash(self.stop), self.step, self.inclusive))

    def index(self, item: Atom) -> int:
        if item not in self:
            raise ValueError(f"{item} is not in {self!r}")
        return len(self.__class__(self.start, item, step=self.step, inclusive=False))

    def index_ALTERNATIVE(self, item: Atom, tolerance: float = 1e-8) -> int:
        """TODO: Determine superior indexing approach."""
        return compute_index(
            start=round(item.to_seconds()),
            current=round(self.start.to_seconds()),
            step=self.step,
            tolerance=tolerance,
        )

    def count(self, item: Atom) -> int:
        return int(item in self)

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


class AbstractSpan[Atom: TimeProtocol](ABC, SpanProtocol):
    @property
    @abstractmethod
    def start(self) -> Atom: ...

    @property
    @abstractmethod
    def end(self) -> Atom: ...

    def midpoint(self) -> Atom:
        return self.interior_point(0.5)

    @abstractmethod
    def __init__(self, start: Atom, end: Atom) -> None: ...

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    @property
    def name(self) -> str:
        return "TODO"

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
    def span(self) -> AbstractSpan[Atom]:
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
    def round_hours(self, round_to: int) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def round_minutes(self, round_to: int) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def round_seconds(self, round_to: float) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def intersection(self, other, strict: bool = False) -> AbstractSpan[Atom] | None: ...

    # alias inner

    @abstractmethod
    def hull(self, other, strict: bool = False) -> AbstractSpan[Atom]: ...

    # alias outer, union, cover

    # def union(self, other, strict: bool = False): ...

    @abstractmethod
    def gap(self, other, strict: bool = False) -> AbstractSpan[Atom] | None: ...

    # alias end_to_start

    @abstractmethod
    def overlap(self, other, strict: bool = False) -> AbstractSpan[Atom] | None: ...

    # alias end_to_start

    @abstractmethod
    def snap_start_to(self, new_start: Atom) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def split(self, cut_point: Atom) -> tuple[AbstractSpan[Atom], AbstractSpan[Atom]]: ...

    @abstractmethod
    def snap_end_to(self, new_end: Atom) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def shift_start_rigid(self, new_start: Atom) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def shift_end_rigid(self, new_end: Atom) -> AbstractSpan[Atom]: ...

    @abstractmethod
    def interior_point(self, alpha: float) -> Atom: ...

    @abstractmethod  # use dispatch: str | AbstractSpan | AbstractTime
    def contains(self, other, include_start: bool = True, include_end: bool = False) -> bool: ...

    # @abstractmethod
    # @dispatch(str)
    # def contains(
    #     self, other: Atom, include_start: bool = True, include_end: bool = False) -> bool: ...

    @abstractmethod
    def forward_affine_transform(
        self,
        *,
        scale_factor: float,
        new_start: Atom | None = None,
        min_minutes: int | float = 5,
    ) -> AbstractSpan[Atom]:
        raise NotImplementedError
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

    @abstractmethod
    def backward_affine_transform(
        self,
        *,
        scale_factor: float,
        new_end: Atom | None = None,
        min_minutes: int | float = 5,
    ) -> AbstractSpan[Atom]:
        raise NotImplementedError


class AbstractPartition[T: TimeProtocol](PartitionProtocol, ABC):
    def __init__(
        self,
        spans: Iterable[SpanProtocol[T]],
        names: Iterable[str | None] | None = None,
    ) -> None: ...
