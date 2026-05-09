from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from functools import lru_cache
from operator import le, lt
from typing import Literal, Self, TypeVar, overload

from .exceptions import TemporalLogicError

from .constants import Unit
from .protocols import AtomProtocol, RangeProtocol, SpanProtocol, TimeProtocol
from .utils import compute_index, get_end, get_start

TimeUnit = TypeVar("TimeUnit", bound=Literal["day", "hour", "minute", "second"])


class AbstractRange[Atom: AtomProtocol](ABC, RangeProtocol):
    start: Atom
    stop: Atom
    step: int
    inclusive: bool
    _current: Atom

    @property
    @abstractmethod
    def seconds_per_step(self) -> int: ...

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
    @overload
    def __getitem__(self, idx: int) -> Atom: ...
    @abstractmethod
    @overload
    def __getitem__(self, idx: slice) -> RangeProtocol[Atom]: ...
    @abstractmethod
    def __getitem__(self, idx) -> Atom | RangeProtocol[Atom]: ...

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
        """Is this the superior indexing approach?"""
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

    @property
    @abstractmethod
    def limit(self) -> Atom: ...

    @property
    @abstractmethod
    def remaining(self) -> float: ...

    # @property
    # @abstractmethod
    # def string_list(self) -> list[str]: ...


class AbstractSpan[Atom: TimeProtocol](ABC, SpanProtocol):
    @property
    @lru_cache
    def stable_random_id(self) -> str:
        return str(hash(self))[:8]

    @property
    @lru_cache
    def name(self) -> str:
        return f"Span{self.stable_random_id}[{self.start!s}-{self.end!s})]"

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

    def round_hours(
        self, round_to: int | float = 0, round_down: bool = False
    ) -> AbstractSpan[Atom]:
        self._start = self._start.round_hours(round_to=round_to, round_down=round_down)
        self._end = self._end.round_hours(round_to=round_to, round_down=round_down)
        return self

    def round_minutes(
        self, round_to: int | float = 0, round_down: bool = False
    ) -> AbstractSpan[Atom]:
        self._start = self._start.round_minutes(round_to=round_to, round_down=round_down)
        self._end = self._end.round_minutes(round_to=round_to, round_down=round_down)
        return self

    def round_seconds(
        self, round_to: float = 0, round_down: bool = False
    ) -> AbstractSpan[Atom]:
        self._start = self._start.round_seconds(round_to=round_to, round_down=round_down)
        self._end = self._end.round_seconds(round_to=round_to, round_down=round_down)
        return self

    def intersection(self, other, strict: bool = False) -> Self | None:
        if self.start > other.end:
            return self.__class__(other.end, self.start)
        if other.start > self.end:
            return self.__class__(other.end, self.start)
        return None

    # alias inner

    def hull(self, other, strict: bool = False) -> Self:
        return self.__class__(min(self.start, other.start), max(self.end, other.end))

    # alias outer, union, cover

    # def union(self, other, strict: bool = False): ...

    def gap(self, other, strict: bool = False) -> Self | None:
        start: Atom = get_start(other)
        end: Atom = get_end(other)
        if self.start > end:
            return self.__class__(end, self.start)
        if start > self.end:
            return self.__class__(self.end, start)
        if strict:
            raise TemporalLogicError
        return None

    # alias end_to_start

    def overlap(self, other: AbstractSpan[Atom], strict: bool = False) -> Self | None:
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        if (end < start):
            if strict:
                raise TemporalLogicError
            return None
        return self.__class__(start=start, end=end)

    # alias end_to_start

    def snap_start_to(self, new_start: Atom) -> AbstractSpan[Atom]:
        if new_start < self.start:
            self._start = new_start
            return self
        raise ValueError

    def split(self, cut_point: Atom) -> tuple[AbstractSpan[Atom], AbstractSpan[Atom]]:
        if not self.start <= cut_point <= self.end:
            raise ValueError
        return self.__class__(self.start, cut_point), self.__class__(cut_point, self.end)

    def snap_end_to(self, new_end: Atom) -> AbstractSpan[Atom]:
        if new_end > self.start:
            self._end = new_end
            return self
        raise ValueError

    def shift_start_rigid(self, new_start: Atom) -> AbstractSpan[Atom]:
        shift = self.start.seconds_to(new_start)
        self._start = new_start
        self._end = self.end.add_seconds(shift)
        return self

    def shift_end_rigid(self, new_end: Atom) -> AbstractSpan[Atom]:
        shift = self.end.seconds_to(new_end)
        self._end = new_end
        self._start = self.start.add_seconds(shift)
        return self

    def interior_point(self, alpha: float, round_seconds_to: int = 3) -> Atom:
        seconds_from_start = round(alpha * self.seconds, round_seconds_to)
        return self.start.add_seconds(seconds_from_start)

    def contains(self, other: SpanProtocol[Atom] | TimeProtocol, include_start: bool = True, include_end: bool = False) -> bool:
        op_a = le if include_start else lt
        op_b = le if include_start else lt
        if isinstance(other, SpanProtocol):
            return op_a(self.start, other.start) and op_b(other.end, self.end)
        if isinstance(other, TimeProtocol):
            return op_a(self.start, other) and op_b(other, self.end)
        raise TypeError

    def forward_affine_transform(
        self,
        *,
        scale_factor: float,
        new_start: Atom | None = None,
        min_minutes: int | float = 5,
    ) -> AbstractSpan[Atom]:
        self._start = new_start or self.start
        self._end = self._start.add_minutes(max(min_minutes, scale_factor * self.minutes))
        return self

    def backward_affine_transform(
        self,
        *,
        scale_factor: float,
        new_end: Atom | None = None,
        min_minutes: int | float = 5,
    ) -> AbstractSpan[Atom]:
        self._end = new_end or self._end
        self._start = self._end.add_minutes(-max(min_minutes, scale_factor * self.minutes))
        return self


class AbstractTimeRange[T: TimeProtocol, U: Unit](AbstractRange[T]):
    unit: U

    @property
    def seconds_per_step(self) -> int:
        return self.unit.seconds

    @abstractmethod
    def __init__(
        self, start: T, stop: T, *, unit: U, step: int = 1, inclusive: bool = True
    ) -> None: ...

    def _divmod_seconds(self) -> tuple[int, float]:
        total_seconds = self.start.seconds_to(self.stop)
        steps, rem = divmod(total_seconds, self.seconds_per_step)
        return int(steps), rem

    @property
    def last(self) -> T:
        remainder_seconds = self._divmod_seconds()[1]
        return self.stop.add_seconds(-remainder_seconds)

    def __len__(self) -> int:
        return self._divmod_seconds()[0]

    def __contains__(self, item: T) -> bool:
        return True

    def __reversed__(self) -> Iterable[T]:
        return self.__class__(self.last, self.start.add_seconds(-1e-3), unit=self.unit)

    @overload
    def __getitem__(self, idx: int) -> T: ...
    @overload
    def __getitem__(self, idx: slice) -> RangeProtocol[T]: ...
    def __getitem__(self, idx) -> T | RangeProtocol[T]:
        if isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            return self.__class__(
                self.start.add_seconds(start * step * self.seconds_per_step),
                self.start.add_seconds(stop * step * self.seconds_per_step),
                unit=self.unit,
                step=self.step * step,
            )
        if idx < 0:
            idx += len(self)
        d = self.start + idx * self.step
        if d in self:
            return d
        raise ValueError(f"Index out of range for {self:r!}")

    def _increment(self) -> None:
        self._current.add_seconds(self.seconds_per_step)

    @property
    def limit(self) -> T:
        return self.last.add_seconds(self.seconds_per_step)

    @property
    def remaining(self) -> float:
        return round(self._current.seconds_to(self.last) / self.seconds_per_step)
