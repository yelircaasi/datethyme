"""Coming soon"""

import datetime
import re
from typing import Any, Self, Union

import deal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_serializer,
    model_validator,
)

from .abcs import (
    OptionalDate,
    OptionalDateTime,
    OptionalTime,
)
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


class Time(OptionalTime, BaseModel):
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

    def __and__(self, date: "Date") -> "DateTime":
        return DateTime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
        )

    def __or__(self, date: "Date") -> "DateTime":
        return self.__and__(date)

    @deal.pure
    @deal.pure
    def __add__(self, mins: int) -> "Time":
        return Time.from_minutes(min(1440, max(0, self.to_minutes() + mins)))

    @deal.pure
    def __sub__(self, mins: int) -> "Time":
        return Time.from_minutes(min(1440, max(0, self.to_minutes() - mins)))

    @deal.pure
    def __eq__(self, __other: Any) -> bool:
        if isinstance(__other, NoneTime):
            return False
        if isinstance(__other, Time):
            return self.to_minutes() == __other.to_minutes()
        return False

    @deal.has()
    def __lt__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.to_minutes() < __other.to_minutes()

    @deal.has()
    def __gt__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.to_minutes() > __other.to_minutes()

    @deal.has()
    def __le__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.to_minutes() <= __other.to_minutes()

    @deal.has()
    def __ge__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.to_minutes() >= __other.to_minutes()

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
        time_now = datetime.datetime.now()
        return cls(hour=time_now.hour, minute=time_now.minute)

    @classmethod
    @deal.pure
    def from_minutes(cls, mins: int) -> "Time":
        hour, minute = divmod(mins, 60)
        return cls(hour=hour, minute=minute)

    @staticmethod
    @deal.pure
    def none() -> "NoneTime":
        return OPTIONAL_TIME

    @deal.pure
    def to_minutes(self) -> int:
        return 60 * self.hour + self.minute

    @deal.pure
    def minutes_to(self, time2: "Time") -> int:
        t2, t1 = time2.to_minutes(), self.to_minutes()
        return t2 - t1

    @deal.pure
    def minutes_from(self, time2: "Time") -> int:
        t2, t1 = self.to_minutes(), time2.to_minutes()
        return t2 - t1


class NoneTime(OptionalTime, BaseModel):
    """Empty time for cases where this may be superior to using None."""

    hour: None = Field(default=None, frozen=True)
    minute: None = Field(default=None, frozen=True)
    second: None = Field(default=None, frozen=True)

    @deal.pure
    def __init__(self) -> None:
        """Sets the attributes `hour`, `minute`, and `second` each to `None`."""
        super().__init__()

    @deal.pure
    def __str__(self) -> str:
        """String conversion returns `NoneTime`: str(nt) == "NoneTime"."""
        return self.__class__.__name__

    @deal.pure
    def __repr__(self) -> str:
        """Displayed as `NoneTime`: repr(nt) == "NoneTime"."""
        return self.__str__()

    @deal.pure
    def __add__(self, _: Any) -> Self:
        """Idempotent under addition, e.g. nt - 42 == nt"""
        return self

    @deal.pure
    def __sub__(self, _: Any) -> Self:
        """Idempotent under subtraction, e.g. nt - 42 == nt"""
        return self

    @deal.pure
    def __bool__(self) -> bool:
        """Always has a boolean value of False."""
        return False

    @deal.pure
    def __eq__(self, __other: Any) -> bool:
        """
        False in all cases except when comparing with another instance of NoneTime
            (including self).
        """
        return isinstance(__other, NoneTime)

    @deal.pure
    def __lt__(self, __other: Any) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __gt__(self, __other: Any) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __le__(self, __other: Any) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __ge__(self, __other: Any) -> bool:
        """False in all cases."""
        return False


OPTIONAL_TIME = NoneTime()


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

    def __or__(self, time: OptionalTime) -> "DateTime":
        return self.__and__(time)

    @deal.has()
    def __add__(self, days: int) -> "Date":
        """Create a new date `days` later than `self`."""
        d = datetime.date.fromordinal(self.ordinal + int(days))
        return Date(year=d.year, month=d.month, day=d.day)

    @deal.has()
    def __sub__(self, days: int) -> "Date":
        return Date.from_ordinal(self.ordinal - int(days))

    @deal.pure
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, datetime.date | Date):
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
    def stdlib(self) -> datetime.date:
        return datetime.date(self.year, self.month, self.day)

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
        d = datetime.date.today()
        return cls(year=d.year, month=d.month, day=d.day)

    @classmethod
    @deal.pure
    def from_ordinal(cls, ord: int) -> "Date":
        d = datetime.date.fromordinal(ord)
        return cls(year=d.year, month=d.month, day=d.day)

    @classmethod
    @deal.has("time")
    def tomorrow(cls) -> "Date":
        return cls.today() + 1

    @staticmethod
    @deal.pure
    def none() -> "NoneDate":
        return OPTIONAL_DATE

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


class NoneDate(OptionalDate, BaseModel):
    """Empty date for cases where this may be superior to using None."""

    model_config = ConfigDict(frozen=True)

    year: None = Field(default=None, frozen=True)
    month: None = Field(default=None, frozen=True)
    day: None = Field(default=None, frozen=True)

    @deal.pure
    def __init__(self) -> None:
        super().__init__()

    @deal.pure
    def __str__(self) -> str:
        return self.__class__.__name__

    @deal.pure
    def __repr__(self) -> str:
        return self.__str__()

    @deal.pure
    def __add__(self, _: Any) -> Self:
        """Simply returns itself: nt + 42 == nt"""
        return self

    @deal.pure
    def __sub__(self, _: Any) -> Self:
        """Simply returns itself: nt - 42 == nt"""
        return self

    @deal.pure
    def __bool__(self) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __eq__(self, other: object) -> bool:
        """NoneDate is only equal to instances of NoneDate."""
        return isinstance(other, NoneDate)

    @deal.pure
    def __lt__(self, other: object) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __gt__(self, other: object) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __le__(self, other: object) -> bool:
        """False in all cases."""
        return False

    @deal.pure
    def __ge__(self, other: object) -> bool:
        """False in all cases."""
        return False


OPTIONAL_DATE = NoneDate()


class DateTime(BaseModel, OptionalDateTime):
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

    @property
    def date(self) -> Date:
        return Date(year=self.year, month=self.month, day=self.day)

    @property
    def time(self) -> Time:
        return Time(hour=self.hour, minute=self.minute, second=self.second)

    @classmethod
    def from_pair(cls, d: Date, t: Time) -> Self:
        return cls(
            year=d.year,
            month=d.month,
            day=d.day,
            hour=t.hour,
            minute=t.minute,
            second=t.second,
        )


class NoneDateTime(BaseModel, OptionalDate):
    """Empty datetime for cases where this may be superior to using None."""
