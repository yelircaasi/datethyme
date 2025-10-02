"""Coming soon"""

from typing import Any, Self

import deal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from ._abcs import (
    AbstractSpan,
    OptionalDate,
    OptionalTime,
)


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


class NoneTime(OptionalTime, BaseModel):
    """Empty time for cases where this may be superior to using None."""

    model_config = ConfigDict(frozen=True)

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


class NoneDateTime(BaseModel, OptionalDate):
    """Empty datetime for cases where this may be superior to using None."""

    model_config = ConfigDict(frozen=True)

    year: None = Field(default=None, frozen=True)
    month: None = Field(default=None, frozen=True)
    day: None = Field(default=None, frozen=True)
    hour: None = Field(default=None, frozen=True)
    minute: None = Field(default=None, frozen=True)
    second: None = Field(default=None, frozen=True)

    @deal.pure
    def __bool__(self) -> bool:
        """Always has a boolean value of False."""
        return False

    @deal.pure
    def __eq__(self, __other: Any) -> bool:
        """
        False in all cases except when comparing with another instance of NoneDateTime
            (including self).
        """
        return isinstance(__other, NoneDateTime)

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


NONE_DATE = NoneDate()
NONE_TIME = NoneTime()
NONE_DATETIME = NoneDateTime()


class NoneSpan(AbstractSpan):
    """
    A trivial time span that is falsy in Boolean contexts,
        but which maintains interoperability with other span types.
    """
