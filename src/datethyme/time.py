from datetime import datetime
from typing import Any, Self

import deal
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator


class TimeValidationError(TypeError):
    @classmethod
    def from_value(cls, value: str | dict | list | tuple) -> Self:
        return cls(f"Invalid value for conversion to Time: `{value}` ({value.__class__.__name__}).")


class Time(BaseModel):
    """Bespoke immutable date class designed to simplify working with times,
    in particular input parsing, time calculations, and ranges."""

    model_config = ConfigDict(frozen=True)

    hour: int
    minute: int = Field(default=0)
    second: float = Field(default=0.0)
    isblank: bool = Field(default=False)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(TimeValidationError)
    def validate_time(cls, raw_time: str | dict | list | tuple) -> dict[str, str | int | float]:
        if not raw_time:
            raise TimeValidationError.from_value(raw_time)
        outdict = {}
        if isinstance(raw_time, dict):
            outdict = raw_time
        if isinstance(raw_time, str):
            substrings = raw_time.split(":") if raw_time else []
            if 0 < len(substrings) < 4:
                outdict = dict(zip(("hour", "minute", "second"), map(float, substrings)))
        if isinstance(raw_time, list | tuple) and (0 < len(raw_time) < 4):
            outdict = dict(zip(("hour", "minute", "second"), raw_time))

        if (tuple(outdict.values()) == (-1, -1, -1.0)) or all(
            (
                outdict,
                0 <= outdict["hour"] <= 24,
                0 <= outdict.get("minute", 0) <= 60,
                0.0 <= outdict.get("second", 0.0) <= 60.0,
            )
        ):
            return outdict

        raise TimeValidationError.from_value(raw_time)

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

    @deal.pure
    def __bool__(self):
        return not self.isblank

    @classmethod
    def parse(cls, time_string: str) -> Self:
        return cls.model_validate(time_string)

    @classmethod
    def if_valid(cls, time_string: str) -> Self | "NoneTime":
        """
        Parse a string and return an instance of Time if possible; otherwise None.
        """
        try:
            return cls.model_validate(time_string)
        except Exception:
            return cls.none()

    @classmethod
    @deal.has("time")
    def now(cls) -> "Time":
        time_now = datetime.now()
        return cls(hour=time_now.hour, minute=time_now.minute)

    @classmethod
    @deal.pure
    def from_minutes(cls, mins: int) -> "Time":
        hour, minute = divmod(mins, 60)
        return cls(hour=hour, minute=minute)

    @staticmethod
    @deal.pure
    def none() -> "NoneTime":
        return NONETIME

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


class NoneTime(Time):
    """Empty time for cases where this may be superior to using None."""

    hour: int = Field(default=-1, frozen=True)
    minute: int = Field(default=-1, frozen=True)
    second: float = Field(default=-1.0, frozen=True)
    isblank: bool = Field(default=True, frozen=True)

    @deal.pure
    def __init__(self) -> None:
        super().__init__(hour=-1, minute=-1, second=-1.0)

    @deal.pure
    def __str__(self) -> str:
        return self.__class__.__name__

    @deal.pure
    def __repr__(self) -> str:
        return self.__str__()

    @deal.pure
    def __add__(self, _: Any) -> Self:
        return self

    @deal.pure
    def __sub__(self, _: Any) -> Self:
        return self

    @deal.pure
    def __bool__(self) -> bool:
        return False

    @deal.pure
    def __eq__(self, __other: Any) -> bool:
        return isinstance(__other, NoneTime)

    @deal.pure
    def __lt__(self, __other: Any) -> bool:
        return False

    @deal.pure
    def __gt__(self, __other: Any) -> bool:
        return False

    @deal.pure
    def __le__(self, __other: Any) -> bool:
        return False

    @deal.pure
    def __ge__(self, __other: Any) -> bool:
        return False


NONETIME = NoneTime()
