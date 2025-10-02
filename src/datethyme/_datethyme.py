"""
TODO: add x_to_next and x_from_last methods for all time-related objects

add add_x and maybe also subtract_x for time increments

make Date.start -> DateTime [00:00] and Date.end -> DateTime [24:00]

add next_second, last_second, next_minute, ... to time classes

add representation as 12-hour time and .format(...) for DateTime and Time analogous to Date.format()
"""

import datetime as DATETIME
import re
from collections.abc import Iterator
from functools import singledispatchmethod
from math import floor
from typing import Any, Self, Union

import deal
from multipledispatch import dispatch
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_serializer,
    model_validator,
)

from ._abcs import (
    AbstractDate,
    AbstractRange,
    AbstractSpan,
    AbstractTime,
    OptionalDate,
)
from ._null import NONE_DATE, NONE_TIME, NoneDate, NoneTime
from .exceptions import (
    DateTimeValidationError,
    DateValidationError,
    TimeValidationError,
)
from .utils import (
    DATE_TIME_REGEX,
    WeekdayLiteral,
    transfer_case,
    validate_date,
    validate_time,
)

FROZEN = True

# --- ELEMENTARY TYPES ---------------------------------------------------------------------------


class Date(OptionalDate, BaseModel):
    """Bespoke immutable date class designed to simplify working with dates,
    in particular input parsing, date calculations, and ranges.
    """

    model_config = ConfigDict(frozen=True)

    year: int = Field(ge=1, le=1000000, frozen=True)
    month: int = Field(ge=1, le=12, frozen=True)
    day: int = Field(ge=1, le=31, frozen=True)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(DateValidationError)
    def validate_raw_date(cls, raw_date: str | dict | list | tuple) -> dict[str, str | int | float]:
        return validate_date(raw_date)

    @model_serializer
    @deal.has()
    @deal.raises(ValidationError)
    def serialize_date(self) -> str:
        return str(self)

    @property
    def datetime(self) -> "DateTime":
        return DateTime.from_pair(self, Time.none())

    @property
    # @deal.pure
    def stdlib(self) -> DATETIME.date:
        return DATETIME.date(self.year, self.month, self.day)

    @property
    @deal.pure
    def ordinal(self) -> int:
        return self.stdlib.toordinal()

    @property
    @deal.pure
    def weekday_ordinal(self) -> int:
        return self.stdlib.weekday()

    @property
    @deal.pure
    def weekday(self) -> WeekdayLiteral:
        weekday_dict: dict[int, WeekdayLiteral] = {
            0: "mon",
            1: "tue",
            2: "wed",
            3: "thu",
            4: "fri",
            5: "sat",
            6: "sun",
        }
        return weekday_dict[self.weekday_ordinal]

    @property
    @deal.has()
    def prose(self) -> str:
        """Prose English date string of the form `Wednesday, March 17th 2025`."""
        return self.format("{Weekday}, {Month} {ordinal}, {year}")

    @property
    def start(self) -> "DateTime":
        return DateTime.from_pair(self, Time(hour=0))

    @property
    def end(self) -> "DateTime":
        return DateTime.from_pair(self, Time(hour=24))

    @property
    def span(self) -> "DateTimeSpan":
        return self.start >> self.end

    def __and__(self, time: AbstractTime) -> "DateTime":
        if isinstance(time, Time):
            return DateTime(
                year=self.year,
                month=self.month,
                day=self.day,
                hour=time.hour,
                minute=time.minute,
                second=time.second,
            )
        return DateTime(year=self.year, month=self.month, day=self.day)

    @deal.pure
    def __str__(self) -> str:
        return f"{self.year}-{self.month:0>2}-{self.day:0>2}"

    @deal.pure
    def __repr__(self) -> str:
        return f"Date({self.__str__()})"

    @deal.pure
    def __bool__(self) -> bool:
        return True

    @deal.has()
    def __add__(self, days: int) -> "Date":
        """Create a new date `days` later than `self`."""
        d = DATETIME.date.fromordinal(self.ordinal + int(days))
        return Date(year=d.year, month=d.month, day=d.day)

    # @dispatch()
    # def __sub__(self, subtrahend):
    #     raise ValueError(f"Invalid type for argument 'subtrahend' to
    # method '__sub__' of 'Date': {type(subtrahend)}")

    @dispatch(int)
    def __sub__(self, subtrahend: int) -> "Date":
        return Date.from_ordinal(self.ordinal - int(subtrahend))

    @dispatch(OptionalDate)
    def __sub__(self, subtrahend: "Date") -> int:  # type: ignore
        if not subtrahend:
            raise TypeError("Date or int required for method __sub__ of Date.")
        return self.ordinal - subtrahend.ordinal

    @deal.pure
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DATETIME.date | Date):
            return False
        return (self.year, self.month, self.day) == (
            other.year,
            other.month,
            other.day,
        )

    @deal.pure
    def __lt__(self, other: Any) -> bool:
        if isinstance(other, NoneDate):
            return False
        return self.__int__() < int(other)

    @deal.pure
    def __gt__(self, other: Any) -> bool:
        if isinstance(other, NoneDate):
            return False
        return self.__int__() > int(other)

    @deal.pure
    def __le__(self, other: Any) -> bool:
        if isinstance(other, NoneDate):
            return False
        return self.__int__() <= int(other)

    @deal.pure
    def __ge__(self, other: Any) -> bool:
        if isinstance(other, NoneDate):
            return False
        return self.__int__() >= int(other)

    @deal.pure
    def __int__(self) -> int:
        return self.ordinal

    @deal.pure
    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))

    @deal.pure
    def __pow__(self, other: "Date") -> "DateRange":
        return DateRange(start=self, stop=other, step=1, inclusive=False)

    @classmethod
    def parse(cls, date_string: str) -> Self:
        """Alias for `model_validate`, but expects a string."""
        return cls.model_validate(date_string)

    @classmethod
    def if_valid(cls, date_string: str) -> Self | "NoneDate":
        """Parse a string and return an instance of Date if possible; otherwise None."""
        try:
            return cls.model_validate(date_string)
        except Exception:
            return cls.none()

    @classmethod
    @deal.has("time")
    def today(cls) -> "Date":
        """Return todays date, using datetime.date.today() from the Python standard library."""
        d = DATETIME.date.today()
        return cls(year=d.year, month=d.month, day=d.day)

    @classmethod
    @deal.pure
    def from_ordinal(cls, ord: int) -> "Date":
        d = DATETIME.date.fromordinal(ord)
        return cls(year=d.year, month=d.month, day=d.day)

    @classmethod
    @deal.has("time")
    def tomorrow(cls) -> "Date":
        return cls.today() + 1

    @deal.has()
    def format(self, template: str) -> str:  # TODO
        """Returns a the date written out in long form."""

        def get_string(placeholder: str) -> str:
            normalized = placeholder.lower()
            match normalized:
                case "weekday":
                    return {
                        0: "Monday",
                        1: "Tuesday",
                        2: "Wednesday",
                        3: "Thursday",
                        4: "Friday",
                        5: "Saturday",
                        6: "Sunday",
                    }[self.weekday_ordinal]
                case "weekday3":
                    return {
                        0: "Mon",
                        1: "Tue",
                        2: "Wed",
                        3: "Thu",
                        4: "Fri",
                        5: "Sat",
                        6: "Sun",
                    }[self.weekday_ordinal]
                case "month":
                    return {
                        1: "January",
                        2: "February",
                        3: "March",
                        4: "April",
                        5: "May",
                        6: "June",
                        7: "July",
                        8: "August",
                        9: "September",
                        10: "October",
                        11: "November",
                        12: "December",
                    }[self.month]
                case "month3":
                    return {
                        1: "Jan",
                        2: "Feb",
                        3: "Mar",
                        4: "Apr",
                        5: "May",
                        6: "Jun",
                        7: "Jul",
                        8: "Aug",
                        9: "Sep",
                        10: "Oct",
                        11: "Nov",
                        12: "Dec",
                    }[self.month]
                case "ordinal":
                    ending = {
                        1: "st",
                        2: "nd",
                        3: "rd",
                        21: "st",
                        22: "nd",
                        23: "rd",
                        31: "st",
                    }.get(self.day, "th")
                    return f"{self.day}{ending}"
                case "year":
                    return str(self.year)
                case "day":
                    return str(self.day)
                case _:
                    raise ValueError(f"Invalid placeholder in template: {placeholder}")

        placeholders = re.findall(r"(?<=\{)[A-Za-z]+3?(?=\})", template)
        return template.format(**{p: transfer_case(p, get_string(p)) for p in placeholders})

    @deal.has()
    def range(self, end: Union["Date", int], inclusive: bool = False) -> list["Date"]:
        """Returns a list of consecutive days, default non-inclusive as is standard in Python.
        Supports reverse-order ranges."""
        inclusive = inclusive and (self != end != 0)

        date1 = self.model_copy()
        if isinstance(end, int):
            date2 = date1 + end
        else:
            date2 = end

        reverse: bool = False

        if date1 > date2:
            date1, date2 = date2, date1
            reverse = True

        if not inclusive:
            if not reverse:
                date2 -= 1
            else:
                date1 += 1

        date_i = date1
        dates = [date_i]

        while date_i < date2:
            dates.append(date_i := date_i + 1)

        if reverse:
            dates.reverse()

        return dates
    
    @deal.pure
    def days_to(self, date2: "Date") -> int:
        return date2.ordinal - self.ordinal
    
    @staticmethod
    @deal.pure
    def none() -> "NoneDate":
        return NONE_DATE


class Time(AbstractTime, BaseModel):
    """Bespoke immutable date class designed to simplify working with times,
    in particular input parsing, time calculations, and ranges.
    """

    model_config = ConfigDict(frozen=FROZEN)

    hour: int = Field(frozen=FROZEN)
    minute: int = Field(default=0, frozen=FROZEN)
    second: float = Field(default=0.0, frozen=FROZEN)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(TimeValidationError)
    def validate_time(cls, raw_time: str | dict | list | tuple) -> dict[str, str | int | float]:
        return validate_time(raw_time)

    @model_serializer
    @deal.pure
    def serialize_time(self) -> str:
        return str(self)

    @property
    def seconds(self) -> float:
        return self._seconds

    @property
    def full_hours(self) -> int:
        return int(self.to_hours // 3600)

    @property
    def full_minutes(self) -> int:
        return floor(self.to_minutes())

    @property
    def full_seconds(self) -> int:
        return floor(self.to_seconds())
    
    @property
    def decimal_places(self) -> int:
        return 10

    def __and__(self, date: "Date") -> "DateTime":
        return DateTime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
        )

    def __rshift__(self, other: "Time") -> "TimeSpan":
        return TimeSpan(start=self, end=other)

    @deal.pure
    def __str__(self) -> str:
        if self.second:
            return f"{self.hour:0>2}:{self.minute:0>2}:{self.second:06.3f}"
        return f"{self.hour:0>2}:{self.minute:0>2}"

    @deal.pure
    def __repr__(self) -> str:
        return f"Time({self.__str__()})"

    @deal.pure
    def __bool__(self):
        return True

    @dispatch((int, float))
    def __add__(self, mins: int | float) -> "Time":
        return Time.from_minutes(min(1440, max(0, self.to_minutes() + mins)))

    @dispatch(AbstractTime)
    def __sub__(self, subtrahend: "Time") -> "TimeDelta":
        if not isinstance(subtrahend, Time):
            raise TypeError
        return TimeDelta(self.to_seconds() - subtrahend.to_seconds())

    @dispatch((int, float))
    def __sub__(self, mins: int | float) -> "Time":
        return Time.from_minutes(min(1440, max(0, self.to_minutes() - mins)))

    @deal.pure
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NoneTime):
            return False
        if isinstance(other, Time):
            return (
                self.to_seconds(places=self.decimal_accuracy) == 
                other.to_seconds(places=self.decimal_accuracy)
            )
        return False

    @deal.has()
    def __lt__(self, other: "Time") -> bool:  # type: ignore
        if isinstance(other, NoneTime):
            return False
        return self.to_minutes() < other.to_minutes()

    @deal.has()
    def __gt__(self, other: "Time") -> bool:  # type: ignore
        if isinstance(other, NoneTime):
            return False
        return self.to_minutes() > other.to_minutes()

    @deal.has()
    def __le__(self, other: "Time") -> bool:  # type: ignore
        if isinstance(other, NoneTime):
            return False
        return self.to_minutes() <= other.to_minutes()

    @deal.has()
    def __ge__(self, other: "Time") -> bool:  # type: ignore
        if isinstance(other, NoneTime):
            return False
        return self.to_minutes() >= other.to_minutes()

    @deal.pure
    def __hash__(self) -> int:
        return hash((self.hour, self.minute))

    @classmethod
    def parse(cls, time_string: str) -> Self:
        return cls.model_validate(time_string)

    @classmethod
    def if_valid(cls, time_string: str) -> Self | "NoneTime":
        """Parse a string and return an instance of Time if possible; otherwise None."""
        try:
            return cls.model_validate(time_string)
        except Exception:
            return cls.none()

    @classmethod
    @deal.has("time")
    def now(cls) -> "Time":
        time_now = DATETIME.datetime.now()
        return cls(hour=time_now.hour, minute=time_now.minute)
    
    @classmethod
    @deal.has()
    def from_hours(cls, hours: int | float, places: int | None = None) -> "Time":
        hours, minutes = divmod(hours, 1.0)
        minutes, seconds = divmod(minutes * 60.0, 1.0)
        seconds *= 60.0
        return cls(
            hour=int(hours),
            minute=int(minutes),
            second=round(seconds, places) if places else seconds,
        )

    @classmethod
    @deal.has()
    def from_minutes(cls, minutes: int | float, places: int | None = None) -> "Time":
        hours, minutes = divmod(minutes, 60.0)
        minutes, seconds = divmod(minutes, 1.0)
        seconds *= 60.0
        return cls(
            hour=int(hours),
            minute=int(minutes),
            second=round(seconds, places) if places else seconds,
        )
    
    @classmethod
    @deal.has()
    def from_seconds(cls, seconds: int | float, places: int | None = None) -> "Time":
        hours, seconds = divmod(seconds, 1440.0)
        minutes, seconds = divmod(seconds, 60.0)
        return cls(
            hour=int(hours),
            minute=int(minutes),
            second=round(seconds, places) if places else seconds,
        )

    @classmethod
    @deal.pure
    def start(cls) -> "Time":
        return cls(hour=0)

    @classmethod
    @deal.pure
    def end(cls) -> "Time":
        return cls(hour=24)

    def round_hours(self, round_to: int | float = 1, round_down: bool = False) -> "Time":
        raw_hours = self.to_hours()
        return self.__class__.from_hours(self._round_to(raw_hours, round_to, round_down))
    
    def round_minutes(self, round_to: int | float = 1, round_down: bool = False) -> "Time":
        raw_minutes = self.to_minutes()
        return self.__class__.from_minutes(self._round_to(raw_minutes, round_to, round_down))
    
    def round_seconds(self, round_to: int | float = 1, round_down: bool = False) -> "Time":
        raw_seconds = self.to_seconds()
        return self.__class__.from_seconds(self._round_to(raw_seconds, round_to, round_down))
    
    def floor_hours(self, increment: int | float = 1) -> "Time":
        new_hours = self._floor(self.to_hours(), increment)
        return self.__class__.from_hours(new_hours)
    
    def floor_minutes(self, increment: int | float = 1) -> "Time":
        new_minutes = self._floor(self.to_minutes(), increment)
        return self.__class__.from_minutes(new_minutes)
    
    def floor_seconds(self, increment: int | float = 1) -> "Time":
        new_seconds = self._floor(self.to_seconds(), increment)
        return self.__class__.from_seconds(new_seconds)
    
    def ceiling_hours(self, increment: int | float = 1) -> "Time":
        new_hours = self._ceiling(self.to_hours(), increment)
        return self.__class__.from_hours(new_hours)
    
    def ceiling_minutes(self, increment: int | float = 1) -> "Time":
        new_minutes = self._ceiling(self.to_minutes(), increment)
        return self.__class__.from_minutes(new_minutes)
    
    def ceiling_seconds(self, increment: int | float = 1) -> "Time":
        new_seconds = self._ceiling(self.to_seconds(), increment)
        return self.__class__.from_seconds(new_seconds)
    
    @deal.pure
    def to_hours(self, places: int | None = None) -> float:
        raw =  self.hour + self.minute / 60 + self.second / 3600
        return round(raw, places or 1)

    @deal.pure
    def to_minutes(self, places: int | None = None) -> float:
        raw =  60.0 * self.hour + self.minute + self.second / 60.0
        return round(raw, places or 1)

    @deal.pure
    def to_seconds(self, places: int | None = None) -> float:
        raw = 3600.0 * self.hour + 60.0 * self.minute + self.second
        return round(raw, places or 1)

    @deal.pure
    def minutes_to(self, time2: "Time") -> float:
        t2, t1 = time2.to_minutes(), self.to_minutes()
        return t2 - t1

    @deal.pure
    def minutes_from(self, time2: "Time") -> float:
        t2, t1 = self.to_minutes(), time2.to_minutes()
        return t2 - t1

    @deal.pure
    def minutes_to_next(self, time2: "Time") -> float:
        if time2 >= self:
            return self.minutes_to(time2)
        else:
            return self.minutes_to(self.day_end) + self.day_start.minutes_to(time2)

    @deal.pure
    def minutes_from_last(self, time2: "Time") -> float:
        if time2 <= self:
            return time2.minutes_to(self)
        else:
            return time2.minutes_to(self.day_end) + self.day_start.minutes_to(self)

    @deal.pure
    def seconds_to(self, time2: "Time") -> float:
        t2, t1 = time2.to_minutes(), self.to_minutes()
        return t2 - t1

    @deal.pure
    def seconds_from(self, time2: "Time") -> float:
        t2, t1 = self.to_minutes(), time2.to_minutes()
        return t2 - t1

    @deal.pure
    def seconds_to_next(self, time2: "Time") -> float:
        if time2 >= self:
            return self.minutes_to(time2)
        else:
            return self.minutes_to(self.day_end) + self.day_start.minutes_to(time2)

    @deal.pure
    def seconds_from_last(self, time2: "Time") -> float:
        if time2 <= self:
            return time2.minutes_to(self)
        else:
            return time2.minutes_to(self.day_end) + self.day_start.minutes_to(self)

    @deal.pure
    def hours_to(self, time2: "Time") -> float:
        t2, t1 = time2.to_hours(), self.to_hours()
        return t2 - t1

    @deal.pure
    def hours_from(self, time2: "Time") -> float:
        t2, t1 = self.to_hours(), time2.to_hours()
        return t2 - t1

    @deal.pure
    def hours_to_next(self, time2: "Time") -> float:
        if time2 >= self:
            return self.hours_to(time2)
        else:
            return self.hours_to(self.day_end) + self.day_start.hours_to(time2)

    @deal.pure
    def hours_from_last(self, time2: "Time") -> float:
        if time2 <= self:
            return time2.hours_to(self)
        else:
            return time2.hours_to(self.day_end) + self.day_start.hours_to(self)

    def add_hours_wraparound(self, n: int | float) -> tuple["Time", int]:
        days, hours = divmod(self.to_hours() + n, 24)
        return (self.from_hours(hours), days)

    def add_minutes_wraparound(self, n: int | float) -> tuple["Time", int]:
        days, minutes = divmod(self.to_minutes() + n, 1440)
        return (self.from_minutes(minutes), days)

    def add_seconds_wraparound(self, n: int | float) -> tuple["Time", int]:
        days, seconds = divmod(self.to_seconds() + n, 86400)
        return (self.from_seconds(seconds), days)

    def add_hours_bounded(self, n: int | float) -> "Time":
        if (total := self.to_hours() + n) > 24:
            return self.day_end
        if total < 0:
            return self.day_start

        return self.from_hours(total)

    def add_minutes_bounded(self, n: int | float) -> "Time":
        if (total := self.to_minutes() + n) > 1440:
            return self.day_end
        if total < 0:
            return self.day_start

        return self.from_minutes(total)

    def add_seconds_bounded(self, n: int | float) -> "Time":
        if (total := self.to_seconds() + n) > 86400:
            return self.day_end
        if total < 0:
            return self.day_start

        return self.from_seconds(total)
    
    @staticmethod
    @deal.pure
    def none() -> "NoneTime":
        return NONE_TIME

    @staticmethod
    def _round_to(self, raw_units: float, round_to: int | float, round_down: bool) -> float:
        epsilon = 0.1 * round_to * (0.5 - int(round_down))
        remainder = raw_units % round_to
        coda = round_to * round(remainder / round_to + epsilon)
        return raw_units + coda
    
    @staticmethod
    def _floor(self, raw_units: float, increment: int | float) -> float:
        return raw_units - (raw_units % increment)
    
    @staticmethod
    def _ceiling(self, raw_units: float, increment: int | float) -> float:
        remainder = raw_units % increment
        return raw_units - remainder + (increment * bool(remainder))


class TimeDelta:
    def __init__(self, seconds: float | int):
        self._seconds = seconds

    @property
    def days(self) -> float:
        return self._seconds / 86400.0

    @property
    def hours(self) -> float:
        return self._seconds / 3600.0

    @property
    def minutes(self) -> float:
        return self._seconds / 60.0

    @classmethod
    def from_days(cls, days: int | float) -> Self:
        return cls(days * 86400)

    @classmethod
    def from_days(cls, hours: int | float) -> Self:
        return cls(hours * 3600)

    @classmethod
    def from_days(cls, minutes: int | float) -> Self:
        return cls(minutes * 60)

    @classmethod
    def from_seconds(cls, seconds: int | float) -> Self:
        return cls(seconds)


class DateTime(BaseModel, AbstractTime, AbstractDate):
    """
    .
    """

    model_config = ConfigDict(frozen=FROZEN)

    year: int = Field(ge=1, le=1000000, frozen=FROZEN)
    month: int = Field(ge=1, le=12, frozen=FROZEN)
    day: int = Field(ge=1, le=31, frozen=FROZEN)
    hour: int = Field(default=0)
    minute: int = Field(default=0)
    second: float = Field(default=0.0)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(DateTimeValidationError, DateValidationError, TimeValidationError)
    def validate_datetime(
        cls, raw_datetime: str | dict | list | tuple
    ) -> dict[str, str | int | float]:
        if isinstance(raw_datetime, dict):
            return validate_date(raw_datetime) | validate_time(raw_datetime)

        if isinstance(raw_datetime, str):
            results = re.search(DATE_TIME_REGEX, raw_datetime)
            if results:
                raw_date, raw_time = results.groups()
                return validate_date(raw_date) | validate_time(raw_time)

        if isinstance(raw_datetime, list | tuple):
            return validate_date(raw_datetime[:3]) | validate_time(list(raw_datetime[3:]) or [0])

        raise DateTimeValidationError.from_value(raw_datetime)

    @property
    def date(self) -> Date:
        return Date(year=self.year, month=self.month, day=self.day)

    @property
    def time(self) -> Time:
        return Time(hour=self.hour, minute=self.minute, second=self.second)

    def __repr__(self) -> str:
        return f"DateTime({self.__str__()})"

    def __str__(self) -> str:
        def show_seconds() -> str:
            return f":{self.second:0>6.3f}" if self.second else ""

        return (
            f"{self.year}"
            f"-{self.month:0>2}"
            f"-{self.day:0>2}"
            f"_{self.hour:0>2}"
            f":{self.minute:0>2}{show_seconds()}"
        )

    @deal.has()
    def __lt__(self, other: "DateTime") -> bool:  # type: ignore
        return (self.date < other.date) and (self.time < other.time)

    @deal.has()
    def __gt__(self, other: "DateTime") -> bool:  # type: ignore
        return (self.date > other.date) and (self.time > other.time)

    @deal.has()
    def __le__(self, other: "DateTime") -> bool:  # type: ignore
        return (self.date <= other.date) and (self.time <= other.time)

    @deal.has()
    def __ge__(self, other: "DateTime") -> bool:  # type: ignore
        return (self.date >= other.date) and (self.time >= other.time)

    @deal.has()
    def __rshift__(self, other: "DateTime") -> "DateTimeSpan":  # type: ignore
        return DateTimeSpan(start=self, end=other)

    @classmethod
    def parse(cls, raw: str) -> Self:
        return cls.model_validate(raw)

    @classmethod
    def from_pair(cls, d: Date, t: Time) -> Self:
        return cls(
            year=d.year,
            month=d.month,
            day=d.day,
            hour=t.hour or 0,
            minute=t.minute or 0,
            second=t.second or 0.0,
        )

    def add_days(self, n: int) -> "DateTime":
        return (self.date + n) & self.time

    def add_hours(self, n: int | float) -> "DateTime":
        time, wraps = self.time.add_hours_wraparound(n)
        return (self.date + wraps) & time

    def add_minutes(self, n: int | float) -> "DateTime":
        time, wraps = self.time.add_minutes_wraparound(n)
        return (self.date + wraps) & time

    def add_seconds(self, n: int | float) -> "DateTime":
        time, wraps = self.time.add_seconds_wraparound(n)
        return (self.date + wraps) & time
    
    @deal.pure
    def minutes_to(self, datetime2: "Time") -> float:
        t2, t1 = datetime2.to_minutes(), self.to_minutes()
        return t2 - t1

    @deal.pure
    def minutes_from(self, datetime2: "Time") -> float:
        t2, t1 = self.to_minutes(), datetime2.to_minutes()
        return t2 - t1

    @deal.pure
    def minutes_to_next(self, time2: "Time") -> float:
        if time2 >= self:
            return self.minutes_to(time2)
        else:
            return 1440 - self.minutes_from(time2)

    @deal.pure
    def minutes_from_last(self, time2: "Time") -> float:
        if time2 <= self:
            return time2.minutes_to(self)
        else:
            return 1440 - self.minutes_to(time2)

    @deal.pure
    def seconds_to(self, datetime2: "Time") -> float:
        t2, t1 = datetime2.to_minutes(), self.to_minutes()
        return t2 - t1

    @deal.pure
    def seconds_from(self, datetime2: "Time") -> float:
        t2, t1 = self.to_minutes(), datetime2.to_minutes()
        return t2 - t1

    @deal.pure
    def seconds_to_next(self, time2: "Time") -> float:
        if time2 >= self:
            return self.minutes_to(time2)
        else:
            return self.minutes_to(self.day_end) + self.day_start.minutes_to(time2)

    @deal.pure
    def seconds_from_last(self, time2: "Time") -> float:
        if time2 <= self:
            return time2.minutes_to(self)
        else:
            return time2.minutes_to(self.day_end) + self.day_start.minutes_to(self)

    @deal.pure
    def hours_to(self, datetime2: "Time") -> float:
        t2, t1 = datetime2.to_hours(), self.to_hours()
        return t2 - t1

    @deal.pure
    def hours_from(self, datetime2: "Time") -> float:
        t2, t1 = self.to_hours(), datetime2.to_hours()
        return t2 - t1

    @deal.pure
    def hours_to_next(self, time2: "Time") -> float:
        if time2 >= self:
            return self.hours_to(time2)
        else:
            return self.hours_to(self.day_end) + self.day_start.hours_to(time2)

    @deal.pure
    def hours_from_last(self, time2: "Time") -> float:
        if time2 <= self:
            return time2.hours_to(self)
        else:
            return time2.hours_to(self.day_end) + self.day_start.hours_to(self)


# --- SPAN TYPES ---------------------------------------------------------------------------------


class TimeSpan(AbstractSpan[Time]):
    def __init__(self, start: Time, end: Time, name: str | None = None):
        self.start = start
        self.end = end
        self._name = name

    @property
    def name(self) -> str:
        return self._name or f"TimeSpan[id{id(self)}]"

    @property
    def id(self) -> str:
        return self.name

    @property
    def days(self) -> float:
        return self.minutes / 1440

    @property
    def hours(self) -> float:
        return self.minutes / 60

    @property
    def minutes(self) -> float:
        return self.end.to_minutes() - self.start.to_minutes()

    @property
    def seconds(self) -> float:
        return self.end.to_seconds() - self.start.to_seconds()

    def overlap(
        self, other: "TimeSpan", strict: bool = False
    ) -> Union["TimeSpan", None]:
        raise NotImplementedError
    
    def gap(
        self, other: "TimeSpan", strict: bool = False
    ) -> Union["TimeSpan", None]:  # alias end_to_start
        if self.start > other.end:
            return TimeSpan(other.end, self.start)
        if other.start > self.end:
            return TimeSpan(other.end, self.start)
        return None

    def hull(
        self, other: "TimeSpan", strict: bool = False
    ) -> "TimeSpan":  # alias outer, union, cover
        return TimeSpan(min(self.start, other.start), max(self.end, other.end))

    def intersection(
        self, other: "TimeSpan", strict: bool = False
    ) -> Union["TimeSpan", None]:  # alias inner
        first, second = sorted((self, other), key=lambda d: d.start)
        if first.start <= second.start < first.end:
            return TimeSpan(second.start, min((first.end, second.end)))
        return None

    def affine_transform(
        self,
        scale_factor: float,
        new_start: Time | None = None,
        new_end: Time | None = None,
        min_minutes: int | float = 5,
    ) -> "TimeSpan":
        raise NotImplementedError

    def interior_point(self, alpha: float) -> Time:
        raise NotImplementedError

    def contains(self, other) -> bool:
        raise NotImplementedError

    def gap(self, other: Time, strict: bool = False) -> "TimeSpan":
        raise NotImplementedError

    def snap_start_to(self, new_start: Time) -> "TimeSpan":
        raise NotImplementedError

    def split(self, point: Time) -> tuple["TimeSpan", "TimeSpan"]:
        raise NotImplementedError

    def snap_end_to(self, new_end: Time) -> "TimeSpan":
        raise NotImplementedError

    def shift_start_rigid(self, new_start: Time) -> "TimeSpan":
        raise NotImplementedError

    def shift_end_rigid(self, new_end: Time) -> "TimeSpan":
        raise NotImplementedError

    def interior_point(self, alpha: float) -> Time:
        raise NotImplementedError
    
    def subdivide(self, ): # -> "TimePartition":
        ...


class DateTimeSpan(AbstractSpan[DateTime]):
    def __init__(self, start: DateTime, end: DateTime, name: str | None = None):
        self.start = start
        self.end = end
        self.name = name

    @property
    def days(self) -> float:
        return 99999

    @property
    def hours(self) -> float:
        return 99999

    @property
    def minutes(self) -> float:
        return 99999

    @property
    def seconds(self) -> float:
        return 99999

    def __add__(self, other: Date | Time | DateTime) -> "DateTimeSpan":
        return self  # TODO

    @classmethod
    def from_dates(cls, start: Date, end: Date) -> Self:
        return cls(start=start.datetime, end=end.datetime)

    def gap(self, other: "DateTimeSpan", strict: bool = False) -> Union["DateTimeSpan", None]:
        # alias end_to_start
        if self.start > other.end:
            return DateTimeSpan(other.end, self.start)
        if other.start > self.end:
            return DateTimeSpan(other.end, self.start)
        return None
    
    def overlap(self, other: "DateTimeSpan", strict: bool = False) -> Union["DateTimeSpan", None]:
        raise NotImplementedError

    def hull(self, other: "DateTimeSpan", strict: bool = False) -> "DateTimeSpan":
        # alias outer, union, cover
        return DateTimeSpan(min(self.start, other.start), max(self.end, other.end))

    def intersection(
        self, other: "DateTimeSpan", strict: bool = False
    ) -> Union["DateTimeSpan", None]:
        # alias inner
        if self.start > other.end:
            return DateTimeSpan(other.end, self.start)
        if other.start > self.end:
            return DateTimeSpan(other.end, self.start)
        return None

    def affine_transform(
        self,
        scale_factor: float,
        new_start: DateTime | None = None,
        new_end: DateTime | None = None,
        min_minutes: int | float = 5,
    ) -> "DateTimeSpan":
        raise NotImplementedError

    def contains(self, other) -> bool:
        raise NotImplementedError

    def gap(self, other: DateTime, strict: bool = False) -> "DateTimeSpan":
        raise NotImplementedError

    def snap_start_to(self, new_start: DateTime) -> "DateTimeSpan":
        raise NotImplementedError

    def split(self, point: DateTime) -> tuple["DateTimeSpan", "DateTimeSpan"]:
        raise NotImplementedError

    def snap_end_to(self, new_end: DateTime) -> "DateTimeSpan":
        raise NotImplementedError

    def shift_start_rigid(self, new_start: DateTime) -> "DateTimeSpan":
        raise NotImplementedError

    def shift_end_rigid(self, new_end: DateTime) -> "DateTimeSpan":
        raise NotImplementedError

    def interior_point(self, alpha: float) -> DateTime:
        raise NotImplementedError
    
    def subdivide(self, ): # -> "DateTimePartition":
        ...


# --- RANGE TYPES --------------------------------------------------------------------------------


class DateRange(AbstractRange[Date]):
    def __init__(self, start: Date, stop: Date, step: int = 1, inclusive: bool = False):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def last(self) -> Date:
        limit = self.stop - int(not self.inclusive)
        last_index = self.start.days_to(limit)
        return limit - (last_index % self.step)

    @property
    def with_end(self) -> Self:
        self.inclusive = True
        return self

    @property
    def without_end(self) -> Self:
        self.inclusive = False
        return self

    @property
    def days(self) -> int:
        return 1 + int(self.stop) - int(self.start)

    @property
    def hours(self) -> float:
        return 24 * len(self)

    @property
    def minutes(self) -> float:
        return 24 * 60 * len(self)

    @property
    def seconds(self) -> float:
        return 24 * 60 * 60 * len(self)

    @dispatch(int)
    def __getitem__(self, idx: int) -> Date:
        if idx < 0:
            idx += len(self)
        d = self.start + idx * self.step
        if d in self:
            return d
        raise ValueError(f"Index out of range for {self:r!}")

    @dispatch(slice)
    def __getitem__(self, sli: slice):
        start, stop, step = slice.indices(len(self))
        return DateRange(
            self.start + start * self.step,
            self.start + stop * self.step,
            self.step * step,
        )

    def __len__(self):
        if self.step > 0:
            return max(0, (self.stop - self.start + self.step - 1) // self.step)
        elif self.step < 0:
            return max(0, (self.start - self.stop - self.step - 1) // -self.step)
        return 0

    def __contains__(self, d: Date):
        if not isinstance(d, Date):
            return False
        return (self.start <= d < self.stop) and ((self.start.days_to(d) % self.step) == 0)

    def __hash__(self) -> int:
        return hash((hash(self.start), hash(self.stop), self.step, self.inclusive))

    def __reversed__(self) -> "DateRange":
        start = self.last
        end = self.start - 1
        return DateRange(start, end, step=self.step, inclusive=False)

    def __iter__(self):
        current = self.start
        while ((self.step > 0) and (current < self.stop)) or (
            (self.step < 0) and (current > self.stop)
        ):
            yield current
            current += self.step

    def __repr__(self):
        return f"DateRange({self.start}, {self.stop}, step={self.step})"

    def count(self, d: Date) -> int:
        return int(d in self)

    def index(self, d: Date) -> int:
        if d not in self:
            raise ValueError(f"{d} is not in {self!r}")
        return len(DateRange(self.start, d, step=self.step, inclusive=False))

    def overlap(self, other: "DateRange", strict: bool = False) -> Union["DateRange", None]:
        raise NotImplementedError

    def gap(self, other: "DateRange", strict: bool = False) -> Union["DateRange", None]:
        # alias end_to_start
        if self.start > other.stop:
            return DateRange(other.stop, self.start)
        if other.start > self.stop:
            return DateRange(other.stop, self.start)
        return None

    def hull(self, other: "DateRange", strict: bool = False) -> "DateRange":
        return DateRange(
            min((self.start, other.start)),
            max((self.stop, other.stop)),
        )

    def intersection(self, other: "DateRange", strict: bool = False) -> Union["DateRange", None]:
        first, second = sorted((self, other), key=lambda d: d.start)
        if first.start <= second.start < first.stop:
            return DateRange(second.start, min((first.stop, second.stop)))
        return None

    def _increment(self) -> None:
        self._current += 1


class DayRangeDated(AbstractRange[DateTime]):
    """ """

    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    @property
    def last(self) -> DateTime:
        return self.stop  # TODO

    def __contains__(self, other: DateTime) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    def __getitem__(self, idx: int) -> DateTime:
        return self.start  # TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999  # TODO

    def index(self, item: DateTime) -> int:
        return 999  # TODO

    def _increment(self) -> None:
        self._current = self._current.add_days(1)


class HourRange(AbstractRange[Time]):
    """
    Sequence of hours, behaving roughly analogously to the built-in range object.

    Example: ```
    time0 = Time.parse("05:00")
    time0 = Time.parse("14:00")
    hours: TimeHourRange = time0 ** time1
    ```
    """

    def __init__(
        self,
        start: Time,
        stop: Time,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = start

    @property
    def last(self) -> Time:
        return self.stop  # TODO

    def __contains__(self, other: Time) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    def __getitem__(self, idx: int) -> Time:
        return self.start  # TODO

    def __reversed__(self) -> Self:
        return self

    def index(self, item: Time) -> int:
        return 999  # TODO

    def _increment(self) -> None:
        self._current = self._current.add_hours(1)


class HourRangeDated(AbstractRange[DateTime]):
    """ """

    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    @property
    def last(self) -> DateTime:
        return self.stop  # TODO

    def __contains__(self, other: DateTime) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    def __getitem__(self, idx: int) -> DateTime:
        return self.start  # TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999  # TODO

    def index(self, item: DateTime) -> int:
        return 999  # TODO

    def _increment(self) -> None:
        self._current = self._current.add_hours(1)


class MinuteRange(AbstractRange[Time]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def last(self) -> Time:
        return self.stop  # TODO

    def __contains__(self, other: Time) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    def __getitem__(self, idx: int) -> Time:
        return self.start  # TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return 999  # TODO

    def index(self, item: Time) -> int:
        return 999  # TODO

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)


class MinuteRangeDated(AbstractRange[DateTime]):
    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    @property
    def last(self) -> DateTime:
        return self.stop  # TODO

    def __contains__(self, other: DateTime) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @dispatch(int)
    def __getitem__(self, idx: int) -> DateTime:
        if not isinstance(idx, int):
            return TypeError(f"list indices must be integers or slices, not {type(idx)}")

        _len = self.__len__()
        if not (-_len <= idx < _len):
            raise IndexError(f"{self.__class__.__name__} index out of range")

        return self.start.add_seconds(idx * self.step)

    @dispatch(slice)
    def __getitem__(self, slc: slice, inclusive: bool = True):  # -> "MinuteRangeDated":
        """
        Attention! The step in the slice, if provided, is with respect to the
          pre-existing step in `self`. This is accordance with the behavior of
          Python's built-in range().
        """
        return MinuteRangeDated(
            start=self[slc.start],
            stop=self[slc.stop - int(inclusive)],
            step=self.step * slc.step,
        )

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999  # TODO

    def index(self, item: DateTime) -> int:
        return 999  # TODO

    def _increment(self) -> None:
        self._current = self._current.add_minutes(self.step)


class SecondRange(AbstractRange[Time]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def last(self) -> Time:
        return self.stop  # TODO

    def __contains__(self, other: Time) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    def __getitem__(self, idx: int) -> Time:
        return self.start  # TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return 999  # TODO

    def index(self, item: Time) -> int:
        return 999  # TODO

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)


class SecondRangeDated(AbstractRange[DateTime]):
    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def last(self) -> DateTime:
        rem = self._rem
        if rem == 0:
            return self.stop.add_seconds(-(not self.inclusive))
        return self.stop.add_seconds(-rem)

    def __contains__(self, other: DateTime) -> bool:
        return (
            (self.start < other)
            and (self._limit > other)
            and (self.start.seconds_to(other) % self.step == 0)
        )

    def __len__(self) -> int:
        return round(self.start.seconds_to(self.last) % self.step) + 1

    @dispatch(int)
    def __getitem__(self, idx: int) -> DateTime:
        if not isinstance(idx, int):
            return TypeError(f"list indices must be integers or slices, not {type(idx)}")

        _len = self.__len__()
        if not (-_len <= idx < _len):
            raise IndexError(f"{self.__class__.__name__} index out of range")

        return self.start.add_seconds(idx * self.step)

    @dispatch(slice)
    def __getitem__(self, slc: slice, inclusive: bool = True):  # -> "SecondRangeDated":
        """
        Attention! The step in the slice, if provided, is with respect to the
          pre-existing step in `self`. This is accordance with the behavior of
          Python's built-in range().
        """
        return SecondRangeDated(
            start=self[slc.start],
            stop=self[slc.stop - int(inclusive)],
            step=self.step * slc.step,
        )

    def __iter__(self) -> Iterator[DateTime]:
        return iter(self)

    def __reversed__(self):
        return super().__reversed__()  # TODO

    def index(self, item: DateTime) -> int:
        if not self.__contains__(item):
            raise ValueError(f"{item} is not in range {self.__repr__()}")
        return round((item - self.start) % self.step, 10)

    @property
    def _limit(self) -> DateTime:
        return self.stop.add_seconds(self._rem * (int(self.inclusive) - 0.5))

    @property
    def _rem(self) -> float:
        return round(self.start.seconds_to(self.stop) % self.step, 10)

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)


class TimePartition:
    """
    A contiguous sequence of DateSpan objects, useful for scheduling.
    """

    def __init__(self):
        pass

