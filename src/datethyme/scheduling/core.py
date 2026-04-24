from collections.abc import Iterable

from ..protocols import EntryProtocol
from .types import Calendar, Strategy


def schedule_entries(
    entries: Iterable[EntryProtocol], preexisting: Calendar | None, strategy: Strategy
) -> Calendar:
    return Calendar()  # TODO


def lint_calendar(cal: Calendar) -> None: ...
