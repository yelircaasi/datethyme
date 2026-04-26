from __future__ import annotations

from collections import UserList
from collections.abc import Iterable

from ...core import Date
from ...protocols import EntryProtocol


class Entry(EntryProtocol):
    def __init__(
        self,
        name: str,
        normal_time: int,
        *,
        projects: set[str] | None = None,
        priority: float | None = None,
        contexts: set[str | None] | None = None,
        dependencies: set[str] | None = None,
        min_time: int | None = None,
        ideal_time: int | None = None,
        max_time: int | None = None,
    ):
        self._name = name
        self._projects = projects
        self._priority = priority
        self._contexts = contexts
        self._normal_time = normal_time
        self._ideal_time = ideal_time
        self._min_time = min_time
        self._max_time = max_time
        self._dependencies = dependencies

    @property
    def name(self) -> str:
        return self._name

    @property
    def projects(self) -> set[str]:
        return self._projects or set()

    @property
    def priority(self) -> float:
        return self._priority or 0.5

    @property
    def min_time(self) -> int:
        return min(
            self._normal_time,
            self._min_time or self._normal_time,
            self._ideal_time or self._normal_time,
        )

    @property
    def normal_time(self) -> int:
        return self._normal_time

    @property
    def ideal_time(self) -> int:
        return self._ideal_time or self._normal_time

    @property
    def max_time(self) -> int:
        return max(
            self._normal_time,
            self._max_time or self._normal_time,
            self._ideal_time or self._normal_time,
        )

    @property
    def contexts(self) -> set[str | None]:
        return self._contexts or set()

    @property
    def dependencies(self) -> set[str]:
        return self._dependencies or set()

    @property
    def due_date(self) -> Date | None:
        raise NotImplementedError

    @property
    def earliest_date(self) -> Date | None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            f"ScheduleItem({self.min_time} ≤ {self.normal_time}"
            f" ≤ {self.max_time}, ideal_time={self.ideal_time})"
        )

    def __str__(self) -> str:
        return repr(self)

    def rescaled(self, scale_factor: float) -> Entry:
        def rescale(maybe_num: int | None) -> int | None:
            if maybe_num is None:
                return maybe_num
            return round(scale_factor * maybe_num)

        return Entry(
            self.name,
            round(self._normal_time * scale_factor),
            projects=self.projects,
            min_time=rescale(self._min_time),
            ideal_time=rescale(self._ideal_time),
            max_time=rescale(self._min_time),
            priority=self._priority,
        )


class Entries[T](UserList[Entry]):
    """Container type for a sequence of entries."""

    def __init__(self, items: Iterable[Entry]) -> None:
        items = list(items)
        if not len(set(items)) == len(items):
            raise ValueError("Item names must be unique.")
        super().__init__(items)

    @property
    def normal_time(self) -> float:
        return sum(map(lambda it: it.normal_time, self))

    @property
    def min_time(self) -> float:
        return sum(map(lambda it: it.min_time, self))

    @property
    def ideal_time(self) -> float:
        return sum(map(lambda it: it.ideal_time, self))

    @property
    def max_time(self) -> float:
        return sum(map(lambda it: it.max_time, self))

    def __repr__(self) -> str:
        return f"Entries(\n    {'\n    '.join(map(repr, self))}\n)"

    def __str__(self) -> str:
        return f"Entries(\n    {'\n    '.join(map(repr, self))}\n)"
