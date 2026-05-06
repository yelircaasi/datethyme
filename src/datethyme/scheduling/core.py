from collections.abc import Iterable

from ..constants import Recipe
from ..protocols import EntryProtocol
from .types import Calendar


def schedule_entries(
    entries: Iterable[EntryProtocol], preexisting: Calendar | None, recipe: Recipe
) -> Calendar:
    raise NotImplementedError
    return Calendar()


def lint_calendar(cal: Calendar) -> None:
    raise NotImplementedError
