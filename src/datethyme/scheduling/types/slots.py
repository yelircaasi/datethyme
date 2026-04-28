from __future__ import annotations

from typing import Literal, Self, final

from ..._abcs import TimeProtocol
from ...core import Date, DateTime, DateTimeSpan, Time, TimeSpan

DEFAULT_DATE = Date.parse("2000-01-01")


type Context = str


class _SentinelContext: ...


SENTINEL = _SentinelContext()
type ReceivingContext = Context | _SentinelContext
type ReceivingSet = set[ReceivingContext] | frozenset[ReceivingContext]


class TimeSlotMixin[T: TimeProtocol]:
    def __init__(
        self,
        start: T,
        end: T,
        require_all: ReceivingSet | None = None,
        require_any: ReceivingSet | None = None,
        require_none: ReceivingSet | None = None,
    ) -> None:
        self._start = start
        self._end = end
        self._require_all: ReceivingSet = require_all or set()
        self._require_any: ReceivingSet = require_any or set()
        self._require_none: ReceivingSet = require_none or set()

    @final
    @classmethod
    def locked(cls, start: T, end: T) -> Self:
        return cls(start, end, require_all=frozenset({SENTINEL}))

    @final
    @classmethod
    def locked_open(cls, start: T, end: T) -> Self:
        return cls(
            start,
            end,
            require_all=frozenset(),
            require_any=frozenset(),
            require_none=frozenset(),
        )

    @property
    def start(self) -> T:
        return self._start

    @property
    def end(self) -> T:
        return self._end

    def can_receive(self, context: Context | set[Context]) -> bool:
        contexts = {context} if isinstance(context, str) else context
        if None in contexts:
            msg = (
                "None is a special sentinel value and con only appear as a slot context, "
                "not as an entry context."
            )
            raise ValueError(msg)
        all_condition = self._require_all.issubset(context)
        any_condition = bool((not self._require_any) or self._require_any.intersection(context))
        none_condition = not self._require_none.intersection(context)
        return all_condition and any_condition and none_condition

    def add_requirement(self, type_: Literal["all", "any", "none"], context: Context) -> Self:
        attrname = f"_require_{type_}"
        new_set = self._add_to_set(getattr(self, attrname), context)
        setattr(self, attrname, new_set)
        return self

    def remove_requirement(
        self, type_: Literal["all", "any", "none"], context: ReceivingContext
    ) -> Self:
        attrname = f"_require_{type_}"
        new_set = self._remove_from_set(getattr(self, attrname), context)
        setattr(self, attrname, new_set)
        return self

    @staticmethod
    def _remove_from_set(set_: ReceivingSet, context: ReceivingContext) -> ReceivingSet:
        if isinstance(set_, set):
            return set_ - {context}
        else:
            raise TypeError("Set is frozen and cannot be modified.")

    @staticmethod
    def _add_to_set(set_: ReceivingSet, context: ReceivingContext) -> ReceivingSet:
        if isinstance(set_, set):
            return set_ | {context}
        else:
            raise TypeError("Set is frozen and cannot be modified.")


class TimeSlot(TimeSlotMixin[Time], TimeSpan): ...


class DateTimeSlot(TimeSlotMixin[DateTime], DateTimeSpan): ...
