from __future__ import annotations

from collections.abc import Callable, Iterable

from pydantic import NonNegativeInt

from ...protocols import DateProtocol, EntriesProtocol, EntryProtocol


def make_entry_adapter[T: object, D: DateProtocol](  # noqa: C901 (too complex)
    *,
    get_name: Callable[[T], str],
    get_projects: Callable[[T], set[str]],
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
        def projects(self) -> set[str]:
            return get_projects(self.entry)

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


def make_entries_adapter[T: Iterable[EntryProtocol]](
    # TODO
) -> type[EntriesProtocol]:
    class EntriesAdapter: ...

    return EntriesAdapter
