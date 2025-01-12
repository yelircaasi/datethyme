import re
from datetime import date
from typing import Any, Literal, Self, Union

import deal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_serializer,
    model_validator,
)

DATE_REGEX: re.Pattern = re.compile(r"^([12]\d\d\d)-(0?\d|1[012])-(0?\d|[12]\d|3[01])$")
DATE_REGEX_STRICT: re.Pattern = re.compile(r"^([12]\d\d\d)-(0\d|1[012]|)-(0\d|[12]\d|3[01])$")
WeekdayLiteral = Literal[
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
]


class DateValidationError(TypeError):
    pass


class Date(BaseModel):
    """
    Bespoke immutable date class designed to simplify working with dates,
        in particular input parsing, date calculations, and ranges.
    """

    model_config = ConfigDict(frozen=True)

    year: int = Field(ge=1970, le=2100, frozen=True)
    month: int = Field(ge=1, le=12, frozen=True)
    day: int = Field(ge=1, le=31, frozen=True)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(DateValidationError, AssertionError, TypeError)
    def validate_date(cls, raw_date: str | dict | list | tuple) -> dict[str, str | int]:
        MAX_DAYS = {
            1: 31,
            2: 29,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 31,
            10: 31,
            11: 30,
            12: 31,
        }
        if isinstance(raw_date, dict):
            outdict = raw_date
        elif isinstance(raw_date, str):
            result = re.search(DATE_REGEX, raw_date.strip())
            if result:
                year, month, day = map(int, result.groups())
                outdict = {"year": year, "month": month, "day": day}
            else:
                raise DateValidationError(f"Invalid string for conversion to Date: '{raw_date}'.")
        elif isinstance(raw_date, list | tuple):
            assert len(raw_date) == 3, "Wrong number of arguments to Date (expected 3): {raw_date}"
            outdict = dict(zip(("year", "month", "day"), map(int, raw_date)))
        else:
            raise DateValidationError(f"Invalid value for conversion to Date: '{raw_date}'.")
        if not (outdict["month"] in MAX_DAYS) and (0 < outdict["day"] <= MAX_DAYS[outdict["month"]]):
            raise DateValidationError(f"Invalid month or number of days for month: {outdict}")
        return outdict

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

    @deal.has()
    def __add__(self, days: int) -> "Date":
        d = date.fromordinal(self.ordinal + int(days))
        return Date(year=d.year, month=d.month, day=d.day)

    @deal.has()
    def __sub__(self, days: int) -> "Date":
        return Date.from_ordinal(self.ordinal - int(days))

    @deal.pure
    def __eq__(self, __other: object) -> bool:
        if not isinstance(__other, date | Date):
            return False
        return (self.year, self.month, self.day) == (
            __other.year,
            __other.month,
            __other.day,
        )

    @deal.pure
    def __lt__(self, __other: Any) -> bool:
        if isinstance(__other, NoneDate):
            # print("nonedate")
            return False
        return self.__int__() < int(__other)

    @deal.pure
    def __gt__(self, __other: Any) -> bool:
        if isinstance(__other, NoneDate):
            return False
        return self.__int__() > int(__other)

    @deal.pure
    def __le__(self, __other: Any) -> bool:
        if isinstance(__other, NoneDate):
            return False
        return self.__int__() <= int(__other)

    @deal.pure
    def __ge__(self, __other: Any) -> bool:
        if isinstance(__other, NoneDate):
            return False
        return self.__int__() >= int(__other)

    @deal.pure
    def __int__(self) -> int:
        return self.ordinal

    @deal.pure
    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))

    @property
    # @deal.pure
    def _date(self) -> date:
        return date(self.year, self.month, self.day)

    @property
    @deal.pure
    def ordinal(self) -> int:
        return self._date.toordinal()

    @property
    @deal.pure
    def weekday_ordinal(self) -> int:
        return self._date.weekday()

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

    @classmethod
    def parse(cls, date_string: str) -> Self:
        return cls.model_validate(date_string)
    
    @classmethod
    def if_valid(cls, date_string: str) -> Self | None:
        """
        Parse a string and return an instance of Date if possible; otherwise None.
        """
        try:
            return cls.model_validate(date_string)
        except DateValidationError:
            return None
        finally:
            return None

    @classmethod
    @deal.has("time")
    def today(cls) -> "Date":
        d = date.today()
        return cls(year=d.year, month=d.month, day=d.day)
    
    @classmethod
    @deal.pure
    def from_ordinal(cls, ord: int) -> "Date":
        d = date.fromordinal(ord)
        return cls(year=d.year, month=d.month, day=d.day)

    @classmethod
    @deal.has("time")
    def tomorrow(cls) -> "Date":
        return cls.today() + 1

    @staticmethod
    @deal.pure
    def nonedate() -> "NoneDate":
        return NoneDate()

    @deal.pure
    def days_to(self, date2: "Date") -> int:
        return date2.ordinal - self.ordinal

    @deal.pure
    def pretty(self) -> str:
        """Returns a the date written out in long form."""
        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        months = {
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
        }
        ordinal_endings = {
            1: "st",
            2: "nd",
            3: "rd",
            21: "st",
            22: "nd",
            23: "rd",
            31: "st",
        }
        ending = ordinal_endings.get(self.day, "th")
        return f"{days[self.weekday_ordinal]}, {months[self.month]} {self.day}{ending}, {self.year}"

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


class NoneDate(Date):
    """Empty date for cases where this may be superior to using None."""

    @deal.pure
    def __init__(self) -> None:
        super().__init__(year=1970, month=1, day=1)

    @deal.pure
    def __str__(self) -> str:
        return "NoneDate"

    @deal.pure
    def __repr__(self) -> str:
        return self.__str__()

    @deal.pure
    def __bool__(self) -> bool:
        return False

    @deal.pure
    def __eq__(self, __other: object) -> bool:
        return isinstance(__other, NoneDate)

    @deal.pure
    def __lt__(self, __other: object) -> bool:
        return False

    @deal.pure
    def __gt__(self, __other: object) -> bool:
        return False

    @deal.pure
    def __le__(self, __other: object) -> bool:
        return False

    @deal.pure
    def __ge__(self, __other: object) -> bool:
        return False
