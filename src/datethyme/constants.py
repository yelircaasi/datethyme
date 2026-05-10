from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from functools import lru_cache
from typing import NamedTuple, overload

from .exceptions import TemporalLogicError

_DEFAULT_PLACES = 9


class AddResult(Enum):
    ADDED = auto()
    ADDED_MODIFIED = auto()
    DISPLACED = auto()
    NOT_ADDED = auto()


@dataclass
class _RecipeMixin:
    stretch: Stretch
    squeeze: Squeeze


class Snap(NamedTuple):
    within: int = 10


class Squeeze(StrEnum):
    """Options for resolving overlaps between timespans."""

    SHIFT_FORWARD = auto()
    SHIFT_BACKWARD = auto()
    EQUAL = auto()
    PROPORTIONAL = auto()
    RELATIVE_SHARE = auto()
    # share = len_overlap / len_span -> portion_a = len_overlap * share_a / (ashare_a + share_b)


class Stretch(StrEnum):
    """Options for resolving gaps between timespans."""

    PROPORTIONAL = auto()
    INVERSE = auto()
    EQUAL = auto()
    SHIFT_FORWARD = auto()
    SHIFT_BACKWARD = auto()
    KEEP = auto()
    FIRST_ECLIPSES = auto()
    SECOND_ECLIPSES = auto()


class Recipe(_RecipeMixin, Enum):
    """Complete configuration for a timespan algorithm."""

    DEFAULT = Stretch.EQUAL, Squeeze.RELATIVE_SHARE
    EQUAL = Stretch.EQUAL, Squeeze.EQUAL
    FORWARD = Stretch.SHIFT_FORWARD, Squeeze.SHIFT_FORWARD
    BACKWARD = Stretch.SHIFT_BACKWARD, Squeeze.SHIFT_BACKWARD


# class Shift(Enum):
#     """Options for rigid timespan movement."""
#     FORWARD = auto()
#     BACKWARD = auto()
#     OUTWARD = auto()


class Unit(Enum):
    """"""

    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400

    @property
    @lru_cache
    def seconds(self) -> int:
        return self.value

    @property
    @lru_cache
    def minutes(self) -> float:
        return round(self.value / 60, _DEFAULT_PLACES)

    @property
    @lru_cache
    def hours(self) -> float:
        return round(self.value / 3600, _DEFAULT_PLACES)

    @property
    @lru_cache
    def days(self) -> float:
        return round(self.value / 86400, _DEFAULT_PLACES)

    @property
    @lru_cache
    def minutes_int(self) -> int:
        minutes = self.minutes
        if minutes == round(minutes):
            return int(minutes)
        raise TemporalLogicError(f"Cannot get property `minutes_int` from {self!s}")

    @property
    @lru_cache
    def hours_int(self) -> int:
        hours = self.hours
        if hours == round(hours):
            return int(hours)
        raise TemporalLogicError(f"Cannot get property `hours_int` from {self!s}")

    @property
    def superunit(self) -> Unit:
        if self is Unit.DAY:
            raise TemporalLogicError("Unit.DAY is the largest supported time unit.")
        return {Unit.SECOND: Unit.MINUTE, Unit.MINUTE: Unit.HOUR, Unit.HOUR: Unit.DAY}[self]

    @property
    def subunit(self) -> Unit:
        if self is Unit.SECOND:
            raise TemporalLogicError("Unit.SECOND is the smallest supported time unit.")
        return {
            Unit.DAY: Unit.HOUR,
            Unit.HOUR: Unit.MINUTE,
            Unit.MINUTE: Unit.SECOND,
        }[self]

    @overload
    def wrt_subunit(self, n: int) -> int: ...
    @overload
    def wrt_subunit(self, n: float) -> float: ...
    def wrt_subunit(self, n: int | float) -> int | float:
        sub_per_self: int = self.subunit.n_in(self)
        raw = n * sub_per_self
        return int(raw) if isinstance(n, int) else float(raw)

    @overload
    def wrt_superunit(self, n: int) -> tuple[int, int]: ...
    @overload
    def wrt_superunit(self, n: float) -> tuple[int, float]: ...
    def wrt_superunit(self, n: int | float) -> tuple[int, int | float]:
        self_per_super: int = self.superunit.has_n(self)
        q, r = divmod(n, self_per_super)
        remainder = int(r) if isinstance(n, int) else float(r)
        return int(q), remainder

    def n_in(self, other: Unit) -> int:
        return other.has_n(self)

    def has_n(self, other: Unit) -> int:
        if self is Unit.DAY and other is Unit.DAY:
            return 1
        match other:
            case Unit.HOUR:
                return self.hours_int
            case Unit.MINUTE:
                return self.minutes_int
            case Unit.SECOND:
                return self.value
            case _:
                raise ValueError

    def cascade(self, value: int | float, round_to: int = 3) -> tuple[int, int, int, float]:
        """Perform cascading modular division at each of our four time resolutions of interest."""
        days, hours, minutes = 0, 0, 0
        raw_seconds = float(self.seconds * value)
        minutes, seconds = Unit.SECOND.wrt_superunit(raw_seconds)
        hours, minutes = Unit.MINUTE.wrt_superunit(minutes)
        days, hours = Unit.HOUR.wrt_superunit(hours)
        return (days, hours, minutes, round(float(seconds), round_to))

    def as_dhms(self, value: int | float, round_to: int = 3) -> tuple[int, int, int, float]:
        return self.cascade(value, round_to=round_to)
