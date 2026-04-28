from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from functools import lru_cache
from typing import NamedTuple, cast, overload


class AddResult(Enum):
    ADDED = auto()
    DISPLACE = auto()
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
    """TODO: Rewrite using dataclass mixin?"""

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
        return round(self.value / 60, 10)

    @property
    @lru_cache
    def hours(self) -> float:
        return round(self.value / 3600, 10)

    @property
    @lru_cache
    def days(self) -> float:
        return round(self.value * 86400, 10)

    @property
    @lru_cache
    def minutes_int(self) -> int:
        minutes = self.minutes
        if minutes == round(minutes):
            return int(minutes)
        raise ValueError

    @property
    @lru_cache
    def hours_int(self) -> int:
        hours = self.hours
        if hours == round(hours):
            return int(hours)
        raise ValueError

    @overload
    def divmod(self, dividend: float, by: Unit) -> tuple[int, float]: ...
    @overload
    def divmod(self, dividend: int, by: Unit) -> tuple[int, int]: ...
    def divmod(self, dividend: int | float, by: Unit) -> tuple[int, int | float]:
        x_per_self: int = self._n_per_self(by)
        q, r = divmod(dividend, x_per_self)
        remainder = int(r) if isinstance(dividend, int) else float(r)
        return int(q), remainder

    def divmod_hours[T: int | float](self, dividend: T) -> tuple[int, T]:
        q, r = self.divmod(dividend, by=Unit.HOUR)
        return q, cast(T, r)

    def divmod_minutes[T: int | float](self, dividend: T) -> tuple[int, T]:
        q, r = self.divmod(dividend, by=Unit.MINUTE)
        return q, cast(T, r)

    def divmod_seconds[T: int | float](self, dividend: T) -> tuple[int, T]:
        q, r = self.divmod(dividend, by=Unit.SECOND)
        return q, cast(T, r)

    def _n_per_self(self, other: Unit) -> int:
        match other:
            case Unit.HOUR:
                return self.hours_int
            case Unit.MINUTE:
                return self.minutes_int
            case Unit.SECOND:
                return self.value
            case _:
                raise ValueError

    def cascade(self, value: int | float) -> tuple[int, int, int, float]:
        """Perform cascading modular division at each of our four time resolutions of interest."""
        days, hours, minutes = 0, 0, 0
        seconds = float(self.seconds * value)
        minutes, seconds = Unit.MINUTE.divmod_seconds(value)
        hours, minutes = Unit.HOUR.divmod_minutes(minutes)
        days, hours = Unit.DAY.divmod_hours(hours)
        return (days, hours, minutes, float(seconds))
