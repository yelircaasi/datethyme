from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from functools import lru_cache
from typing import NamedTuple, overload


class AddResult(Enum):
    ADDED = auto()
    ADDED_MODIFIED = auto()
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
    def wrt(self, larger_unit: Unit, n: int) -> tuple[int, int]: ...
    @overload
    def wrt(self, larger_unit: Unit, n: float) -> tuple[int, float]: ...
    def wrt(self, larger_unit: Unit, n: int | float) -> tuple[int, int | float]:
        self_per_larger: int = larger_unit._n_per_self(self)
        q, r = divmod(n, self_per_larger)
        remainder = int(r) if isinstance(n, int) else float(r)
        return int(q), remainder

    def _n_per_self(self, other: Unit) -> int:
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

    def cascade(self, value: int | float) -> tuple[int, int, int, float]:
        """Perform cascading modular division at each of our four time resolutions of interest."""
        days, hours, minutes = 0, 0, 0
        seconds = float(self.seconds * value)
        minutes, seconds = Unit.SECOND.wrt(Unit.MINUTE, value)
        hours, minutes = Unit.MINUTE.wrt(Unit.HOUR, minutes)
        days, hours = Unit.HOUR.wrt(Unit.DAY, hours)
        return (days, hours, minutes, float(seconds))

    def as_dhms(self, value: int | float) -> tuple[int, int, int, float]:
        return self.cascade(value)
