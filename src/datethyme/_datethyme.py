"""Coming soon"""

import datetime as DATETIME
import re
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
    AbstractRange,
    AbstractSpan,
    OptionalDate,
    OptionalDateTime,
    OptionalTime,
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

# --- ELEMENTARY TYPES ---------------------------------------------------------------------------


class Date(OptionalDate, BaseModel):
    @property
    def datetime(self) -> "DateTime":
        return DateTime.from_pair(self, Time.none())

    def __and__(self, time: OptionalTime) -> "DateTime":
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

    def __pow__(self, other: "Date") -> "DateRange":
        return DateRange(start=self, stop=other)

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
    def validate_date(cls, raw_date: str | dict | list | tuple) -> dict[str, str | int | float]:
        return validate_date(raw_date)

    @model_serializer
    @deal.has()
    @deal.raises(ValidationError)
    def serialize_date(self) -> str:
        return str(self)

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

    # @singledispatch
    # def __sub__(self, subtrahend):
    #     raise ValueError(f"Invalid type for argument 'subtrahend' to method '__sub__'
    #     of 'Date': {type(subtrahend)}")

    @dispatch(int)
    def __sub__(self, subtrahend: int) -> "Date":
        return Date.from_ordinal(self.ordinal - int(subtrahend))

    @dispatch(OptionalDate)
    def __sub__(self, subtrahend: "Date") -> int:  # type: ignore
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
        return self.start**self.end

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

    @staticmethod
    @deal.pure
    def none() -> "NoneDate":
        return NONE_DATE

    @deal.pure
    def days_to(self, date2: "Date") -> int:
        return date2.ordinal - self.ordinal

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
                case "day":
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
                case "mon":
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
                case _:
                    raise ValueError(f"Invalid placeholder in template: {placeholder}")

        placeholders = re.findall(r"(?<=\{)[A-Za-z]+(?=\})", template)
        return template.format(**{p: transfer_case(p, get_string(p)) for p in placeholders})

    @deal.has()
    def range(self, end: Union["Date", int], inclusive: bool = True) -> list["Date"]:
        """Returns a list of consecutive days, default inclusive. Supports reverse-order ranges."""
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


class Time(OptionalTime, BaseModel):
    def __and__(self, date: "Date") -> "DateTime":
        return DateTime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
        )

    def __pow__(self, other: "Time") -> "TimeSpan":
        return TimeSpan(start=self, end=other)

    """Bespoke immutable date class designed to simplify working with times,
    in particular input parsing, time calculations, and ranges.
    """

    model_config = ConfigDict(frozen=True)

    hour: int
    minute: int = Field(default=0)
    second: float = Field(default=0.0)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(TimeValidationError)
    def validate_time(cls, raw_time: str | dict | list | tuple) -> dict[str, str | int | float]:
        return validate_time(raw_time)

    @model_serializer
    @deal.pure
    def serialize_date(self) -> str:
        return str(self)

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

    @dispatch(OptionalTime)
    def __sub__(self, subtrahend: "Time") -> "TimeDelta":
        return TimeDelta(self.to_seconds() - subtrahend.to_seconds())

    @dispatch((int, float))
    def __sub__(self, mins: int | float) -> "Time":  # type: ignore
        return Time.from_minutes(min(1440, max(0, self.to_minutes() - mins)))

    @deal.pure
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NoneTime):
            return False
        if isinstance(other, Time):
            return self.to_minutes() == other.to_minutes()
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
    @deal.pure
    def from_minutes(cls, mins: int | float) -> "Time":
        hour, minute = divmod(mins, 60.0)
        minute, second = divmod(minute, 1.0)
        return cls(hour=int(hour), minute=int(minute), second=60.0 * second)

    @staticmethod
    @deal.pure
    def none() -> "NoneTime":
        return NONE_TIME

    @deal.pure
    def to_minutes(self) -> float:
        return 60 * self.hour + self.minute

    @deal.pure
    def to_seconds(self) -> float:
        return 3600 * self.hour + 60 * self.minute + self.second

    @deal.pure
    def minutes_to(self, time2: "Time") -> float:
        t2, t1 = time2.to_minutes(), self.to_minutes()
        return t2 - t1

    @deal.pure
    def minutes_from(self, time2: "Time") -> float:
        t2, t1 = self.to_minutes(), time2.to_minutes()
        return t2 - t1

    def add_hours_wraparound(self, n: int | float) -> tuple["Time", int]:
        return (self, 999)  # TODO

    def add_minutes_wraparound(self, n: int | float) -> tuple["Time", int]:
        return (self, 999)  # TODO

    def add_seconds_wraparound(self, n: int | float) -> tuple["Time", int]:
        return (self, 999)  # TODO

    def add_hours(self, n: int | float) -> "Time":
        return self  # TODO

    def add_minutes(self, n: int | float) -> "Time":
        return self  # TODO

    def add_seconds(self, n: int | float) -> "Time":
        return self  # TODO


class TimeDelta:
    def __init__(self, seconds: float):
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

    @property
    def seconds(self) -> float:
        return self._seconds

    @property
    def full_days(self) -> int:
        return int(self._seconds // 86400)

    @property
    def full_hours(self) -> int:
        return int(self._seconds // 3600)

    @property
    def full_minutes(self) -> int:
        return int(self._seconds // 60)

    @property
    def full_seconds(self) -> int:
        return int(floor(self._seconds))


class DateTime(BaseModel, OptionalDateTime):
    def __pow__(self, other: "DateTime") -> "DateTimeSpan":
        return DateTimeSpan(start=self, end=other)

    """
    .
    """
    model_config = ConfigDict(frozen=True)

    year: int = Field(ge=1, le=1000000, frozen=True)
    month: int = Field(ge=1, le=12, frozen=True)
    day: int = Field(ge=1, le=31, frozen=True)
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

    @classmethod
    def parse(cls, raw: str) -> Self:
        return cls.model_validate(raw)

    def __repr__(self) -> str:
        return self.__str__()

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

    @property
    def date(self) -> Date:
        return Date(year=self.year, month=self.month, day=self.day)

    @property
    def time(self) -> Time:
        return Time(hour=self.hour, minute=self.minute, second=self.second)

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

    @classmethod
    def from_pair(cls, d: Date, t: OptionalTime) -> Self:
        return cls(
            year=d.year,
            month=d.month,
            day=d.day,
            hour=t.hour or 0,
            minute=t.minute or 0,
            second=t.second or 0.0,
        )

    def add_days(self, n: int) -> "DateTime":
        time, wraps = self.time.add_hours_wraparound(n * 24)
        return (self.date + wraps) & time

    def add_hours(self, n: int | float) -> "DateTime":
        time, wraps = self.time.add_hours_wraparound(n)
        return (self.date + wraps) & time

    def add_minutes(self, n: int | float) -> "DateTime":
        time, wraps = self.time.add_minutes_wraparound(n)
        return (self.date + wraps) & time

    def add_seconds(self, n: int | float) -> "DateTime":
        time, wraps = self.time.add_seconds_wraparound(n)
        return (self.date + wraps) & time


# --- SPAN TYPES ---------------------------------------------------------------------------------


class DateSpan(AbstractSpan[Date]):
    def __init__(self, start: Date, end: Date):
        self.start = start
        self.end = end

    def hull(self, other: "DateSpan", strict: bool = False) -> "DateSpan":
        # alias outer, union, cover
        return DateSpan(min(self.start, other.start), max(self.end, other.end))

    def intersection(self, other: "DateSpan", strict: bool = False) -> Union["DateSpan", None]:
        # alias inner
        first, second = sorted((self, other), key=lambda d: d.start)
        if first.start <= second.start < first.end:
            return DateSpan(second.start, min((first.end, second.end)))
        return None

    @property
    def days(self) -> float:
        return int(self.end) - int(self.start)

    @property
    def hours(self) -> float:
        return 60 * self.days

    @property
    def minutes(self) -> float:
        return 24 * 60 * self.days

    @property
    def seconds(self) -> float:
        return 24 * 60 * 60 * self.days

    def gap(
        self, other: "DateSpan", strict: bool = False
    ) -> Union["DateSpan", None]:  # alias end_to_start
        if self.start > other.end:
            return DateSpan(other.end, self.start)
        if other.start > self.end:
            return DateSpan(other.end, self.start)
        return None

    def start_to_start(self, other: "DateSpan", strict: bool = False) -> "DateSpan":
        return DateSpan(self.start, other.start)

    def end_to_end(self, other: "DateSpan", strict: bool = False) -> "DateSpan":
        return DateSpan(self.end, other.end)


class TimeSpan(AbstractSpan[Time]):
    def __init__(self, start: Time, end: Time):
        self.start = start
        self.end = end

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

    def end_to_end(self, other: "TimeSpan", strict: bool = False) -> "TimeSpan":
        return TimeSpan(self.end, other.end)

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

    def start_to_start(self, other: "TimeSpan", strict: bool = False) -> "TimeSpan":
        return TimeSpan(self.start, other.start)


class DateTimeSpan(AbstractSpan[DateTime]):
    def __init__(self, start: DateTime, end: DateTime):
        self.start = start
        self.end = end

    def gap(self, other: "DateTimeSpan", strict: bool = False) -> Union["DateTimeSpan", None]:
        # alias end_to_start
        if self.start > other.end:
            return DateTimeSpan(other.end, self.start)
        if other.start > self.end:
            return DateTimeSpan(other.end, self.start)
        return None

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

    def start_to_start(self, other: "DateTimeSpan", strict: bool = False) -> "DateTimeSpan":
        return DateTimeSpan(self.start, other.start)

    def end_to_end(self, other: "DateTimeSpan", strict: bool = False) -> "DateTimeSpan":
        return DateTimeSpan(self.end, other.end)

    def __add__(self, other: Date | Time | DateTime) -> "DateTimeSpan":
        return self  # TODO

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

    @classmethod
    def from_dates(cls, start: Date, end: Date) -> Self:
        return cls(start=start.datetime, end=end.datetime)

    # def hull(self, other: Date | Time | DateTime) -> "DateTimeSpan": ...

    # def overlap(self, other: Date | Time | DateTime | DateRange | ) -> "DateTimeSpan": ...

    # def gap(self, other: Date | Time | DateTime | DateRange | ) -> "DateTimeSpan": ...


# --- RANGE TYPES --------------------------------------------------------------------------------


class DateRange(AbstractRange[Date]):
    # def __init__(self, start: Date, end: Date, inclusive: bool = True) -> None:
    #     self.start = start
    #     self.end = end
    #     self.inclusive = inclusive

    def __init__(self, start: Date, stop: Date, step: int = 1, inclusive: bool = False):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    # def __getitem__(self, idx: int) -> Date: TODO
    #     d = self.start + idx * self.step
    #     if d in self:
    #         return d
    #     raise ValueError(f"Index out of range for {self:r!}")

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            return DateRange(
                self.start + start * self.step,
                self.start + stop * self.step,
                self.step * step,
            )
        else:
            if index < 0:
                index += len(self)
            if index < 0 or index >= len(self):
                raise IndexError("DateRange index out of range.")
            return self.start + index * self.step

    def _increment(self) -> None:
        self._current += 1

    # def __len__(self) -> int:
    #     return int(self.end) - int(self.start)

    def __len__(self):
        if self.step > 0:
            return max(0, (self.stop - self.start + self.step - 1) // self.step)
        elif self.step < 0:
            return max(0, (self.start - self.stop - self.step - 1) // -self.step)
        return 0

    def __contains__(self, d: Date):
        if not isinstance(d, Date):
            # raise TypeError("DateRange.__contains__ only accepts arguments of type 'Date'.")
            return False
        return (self.start <= d < self.stop) and ((self.start.days_to(d) % self.step) == 0)

    def __hash__(self) -> int:
        return hash((hash(self.start), hash(self.stop), self.step, self.inclusive))

    @property
    def last(self) -> Date:
        limit = self.stop - int(not self.inclusive)
        last_index = self.start.days_to(limit)
        return limit - (last_index % self.step)

    def __reversed__(self) -> "DateRange":
        start = self.last
        end = self.start - 1
        return DateRange(start, end, step=self.step, inclusive=False)

    def count(self, d: Date) -> int:
        return int(d in self)

    def index(self, d: Date) -> int:
        if d not in self:
            raise ValueError(f"{d} is not in {self!r}")
        return len(DateRange(self.start, d, step=self.step, inclusive=False))

    @property
    def with_end(self) -> Self:
        self.inclusive = True
        return self

    @property
    def without_end(self) -> Self:
        self.inclusive = False
        return self

    @property
    def days(self) -> float:
        return len(self)

    @property
    def hours(self) -> float:
        return 24 * len(self)

    @property
    def minutes(self) -> float:
        return 24 * 60 * len(self)

    @property
    def seconds(self) -> float:
        return 24 * 60 * 60 * len(self)

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

    def start_to_start(self, other: "DateRange", strict: bool = False) -> "DateRange":
        return DateRange(self.start, other.start)

    def end_to_end(self, other: "DateRange", strict: bool = False) -> "DateRange":
        return DateRange(self.stop, other.stop)

    def __iter__(self):
        current = self.start
        while ((self.step > 0) and (current < self.stop)) or (
            (self.step < 0) and (current > self.stop)
        ):
            yield current
            current += self.step

    def __repr__(self):
        return f"DateRange({self.start}, {self.stop}, step={self.step})"


# class TimeRangeHours:
#     """
#     Lazy generator for discrete time sequences, supporting any unit
#         (hour, minute, second, millisecond) and integer step size.
#         Supports backward ranges.

#     """
#     start = ...
#     end = ...
#     unit: Literal["hour", "minute", "second", "millisecond"] = "minute"
#     step = 1
# TimeEntity = TypeVar("TimeEntity", bound=Time | DateTime)


# class HourRange(AbstractRange, Generic[TimeEntity]): ...


# class MinuteRange(AbstractRange, Generic[TimeEntity]): ...


# class SecondRange(AbstractRange, Generic[TimeEntity]): ...


class DateTimeDayRange(AbstractRange[DateTime]):
    """ """

    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    def __contains__(self, other: DateTime) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> DateTime:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999 #TODO

    def index(self, item: DateTime) -> int:
        return 999 #TODO

    @property
    def last(self) -> DateTime:
        return self.stop #TODO

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

    def __init__(self, start: Time, stop: Time, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    def __contains__(self, other: Time) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> Time:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return 999 #TODO

    def index(self, item: Time) -> int:
        return 999 #TODO

    @property
    def last(self) -> Time:
        return self.stop #TODO

    def _increment(self) -> None:
        self._current = self._current.add_hours(1)


class DateTimeHourRange(AbstractRange[DateTime]):
    """ """

    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    def __contains__(self, other: DateTime) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> DateTime:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999 #TODO

    def index(self, item: DateTime) -> int:
        return 999 #TODO

    @property
    def last(self) -> DateTime:
        return self.stop #TODO

    def _increment(self) -> None:
        self._current = self._current.add_hours(1)


class MinuteRange(AbstractRange[Time]):
    def __init__(self, start: Time, stop: Time, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    def __contains__(self, other: Time) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> Time:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return 999 #TODO

    def index(self, item: Time) -> int:
        return 999 #TODO

    @property
    def last(self) -> Time:
        return self.stop #TODO

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)


class DateTimeMinuteRange(AbstractRange[DateTime]):
    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    def __contains__(self, other: DateTime) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> DateTime:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999 #TODO

    def index(self, item: DateTime) -> int:
        return 999 #TODO

    @property
    def last(self) -> DateTime:
        return self.stop #TODO

    def _increment(self) -> None:
        self._current = self._current.add_minutes(self.step)


class SecondRange(AbstractRange[Time]):
    def __init__(self, start: Time, stop: Time, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    def __contains__(self, other: Time) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> Time:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return 999 #TODO

    def index(self, item: Time) -> int:
        return 999 #TODO

    @property
    def last(self) -> Time:
        return self.stop #TODO

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)


class DateTimeSecondRange(AbstractRange[DateTime]):
    def __init__(self, start: DateTime, stop: DateTime, step: int = 1, inclusive: bool = True):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    def __contains__(self, other: DateTime) -> bool:
        return False #TODO

    def __len__(self) -> int:
        return 999 #TODO

    def __getitem__(self, idx: int) -> DateTime:
        return self.start #TODO

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return 999 #TODO

    def index(self, item: DateTime) -> int:
        return 999 #TODO

    @property
    def last(self) -> DateTime:
        return self.stop #TODO

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)
