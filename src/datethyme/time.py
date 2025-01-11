from datetime import datetime
from typing import Any, Self

import deal
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator


class TimeValidationError(TypeError):
    pass


class Time(BaseModel):
    """Bespoke time class designed to simplify the nebokrai codebase."""

    model_config = ConfigDict(frozen=True)

    hour: int
    minute: int = Field(default=0)
    second: float = Field(default=0.0)
    isblank: bool = Field(default=False)

    @model_validator(mode="before")
    @classmethod
    @deal.has()
    @deal.raises(TimeValidationError)
    def validate_date(cls, raw_time: str | dict | list | tuple) -> dict[str, str | int]:
        if isinstance(raw_time, dict):
            return raw_time
        if isinstance(raw_time, str):
            substrings = raw_time.split(":")
            if len(substrings) == 2:
                return dict(zip(("hour", "minute"), map(int, substrings)))
            if len(substrings) == 3:
                return dict(zip(("hour", "minute", "second"), map(float, substrings)))
            # raise TimeValidationError(
            #         "Argument to Time.model_validate must have exactly one or two colons."
            #         " Given: '{raw_time}'."
            #     )

        if isinstance(raw_time, list | tuple):
            if 0 < len(raw_time) < 3:
                # raise TimeValidationError(f"Wrong number of arguments (expected 2): '{raw_time}'.")
                hour = int(raw_time[0])
                minute = int(raw_time[1]) if (len(raw_time) == 2) else 0
                return {"hour": hour, "minute": minute}

        raise TimeValidationError(f"Invalid value for conversion to Date: '{raw_time}'.")

    @model_serializer
    @deal.pure
    def serialize_date(self) -> str:
        return str(self)

    @deal.pure
    def __str__(self) -> str:
        if self.second:
            return f"{self.hour:0>2}:{self.minute:0>2}:{self.second:.3f}"
        return f"{self.hour:0>2}:{self.minute:0>2}"

    @deal.pure
    def __repr__(self) -> str:
        return f"Time({self.__str__()})"

    @deal.pure
    def __add__(self, mins: int) -> "Time":
        return Time.fromminutes(min(1440, max(0, self.tominutes() + mins)))

    @deal.pure
    def __sub__(self, mins: int) -> "Time":
        return Time.fromminutes(min(1440, max(0, self.tominutes() - mins)))

    @deal.pure
    def __eq__(self, __other: Any) -> bool:
        if isinstance(__other, NoneTime):
            return False
        if isinstance(__other, Time):
            return self.tominutes() == __other.tominutes()
        return False

    @deal.has()
    def __lt__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.tominutes() < __other.tominutes()

    @deal.has()
    def __gt__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.tominutes() > __other.tominutes()

    @deal.has()
    def __le__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.tominutes() <= __other.tominutes()

    @deal.has()
    def __ge__(self, __other: "Time") -> bool:  # type: ignore
        if isinstance(__other, NoneTime):
            return False
        return self.tominutes() >= __other.tominutes()

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
    @deal.has("time")
    def now(cls) -> "Time":
        time_now = datetime.now()
        return cls(hour=time_now.hour, minute=time_now.minute)

    @classmethod
    @deal.pure
    def fromminutes(cls, mins: int) -> "Time":
        hour, minute = divmod(mins, 60)
        return cls(hour=hour, minute=minute)

    @staticmethod
    @deal.pure
    def nonetime() -> "NoneTime":
        return NONETIME

    @deal.pure
    def tominutes(self) -> int:
        return 60 * self.hour + self.minute

    @deal.pure
    def timeto(self, time2: "Time") -> int:
        t2, t1 = time2.tominutes(), self.tominutes()
        return t2 - t1

    @deal.pure
    def timefrom(self, time2: "Time") -> int:
        t2, t1 = self.tominutes(), time2.tominutes()
        return t2 - t1


class NoneTime(Time):
    """Empty time for cases where this may be superior to using None."""

    hour: int = Field(default=-1, frozen=True)
    minute: int = Field(default=-1, frozen=True)
    isblank: bool = Field(default=True, frozen=True)

    @deal.pure
    def __str__(self) -> str:
        return "NoneTime"

    @deal.pure
    def __repr__(self) -> str:
        return self.__str__()

    @deal.pure
    def __add__(self, _: Any) -> "NoneTime":
        return NoneTime()

    @deal.pure
    def __sub__(self, _: Any) -> "NoneTime":
        return NoneTime()

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
