from __future__ import annotations

from ..._abcs import TimeProtocol
from ...core import Date, DateTime, DateTimeSpan, Time, TimeSpan

DEFAULT_DATE = Date.parse("2000-01-01")


type Context = str


class TimeSlotMixin[T: TimeProtocol]:
    def __init__(
        self,
        start: T,
        end: T,
        require_all: set[Context] | None = None,
        require_any: set[Context] | None = None,
        require_none: set[Context] | None = None,
    ) -> None:
        self._start = start
        self._end = end
        self.require_all: set[Context] = require_all or set()
        self.require_any: set[Context] = require_any or set()
        self.require_none: set[Context] = require_none or set()

    def is_valid(self, context: Context | set[Context]) -> bool:
        context = {context} if isinstance(context, str) else context
        all_condition = self.require_all.issubset(context)
        any_condition = bool((not self.require_any) or self.require_any.intersection(context))
        none_condition = not self.require_none.intersection(context)
        return all_condition and any_condition and none_condition


class TimeSlot(TimeSlotMixin[Time], TimeSpan): ...


class DateTimeSlot(TimeSlotMixin[DateTime], DateTimeSpan): ...
