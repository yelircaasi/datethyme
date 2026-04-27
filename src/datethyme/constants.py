from enum import Enum
from functools import lru_cache


class Unit(Enum):
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
