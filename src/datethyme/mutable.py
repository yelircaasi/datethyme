from pydantic import ConfigDict, Field

from ._datethyme import Date as _Date
from ._datethyme import Time as _Time

FROZEN = False


"""
from ._datethyme import class_factory


(
    Time,
    Date,
    ...
) = class_factory(frozen=FROZEN)
"""


class Time(_Time):
    model_config = ConfigDict(frozen=FROZEN)

    hour: int = Field(frozen=FROZEN)
    minute: int = Field(default=0, frozen=FROZEN)
    second: float = Field(default=0.0, frozen=FROZEN)


class Date(_Date):
    model_config = ConfigDict(frozen=FROZEN)

    year: int = Field(ge=1, le=1000000, frozen=FROZEN)
    month: int = Field(ge=1, le=12, frozen=FROZEN)
    day: int = Field(ge=1, le=31, frozen=FROZEN)


__all__ = [
    "Date",
    "Time",
]
