from typing import Literal

from .constants import Unit
from .core import DateTime, DateTimeRange, Time, TimeRange


class DayRangeDated(DateTimeRange[Literal[Unit.DAY]]):
    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.DAY
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound


class HourRange(TimeRange[Literal[Unit.HOUR]]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.HOUR
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound


class HourRangeDated(DateTimeRange[Literal[Unit.HOUR]]):
    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.HOUR
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound


class MinuteRange(TimeRange[Literal[Unit.MINUTE]]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.MINUTE
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound


class MinuteRangeDated(DateTimeRange[Literal[Unit.MINUTE]]):
    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.MINUTE
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound


class SecondRange(TimeRange[Literal[Unit.SECOND]]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.SECOND
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound


class SecondRangeDated(DateTimeRange[Literal[Unit.SECOND]]):
    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        *,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ) -> None:
        self.unit = Unit.SECOND
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self.allow_wraparound = allow_wraparound
