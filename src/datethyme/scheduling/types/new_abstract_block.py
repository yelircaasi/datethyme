from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from ...constants import Unit
from ...exceptions import TemporalLogicError
from ...protocols import ResultTriple, TimeProtocol
from ...utils import SpanProtocol
from .. import EntryProtocol
from ..utils import is_partitioned


class AbstractBlock[T: TimeProtocol](BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    start: T
    end: T
    name: str | None = None
    subentries: list[SpanProtocol[T]] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_partitioned(self) -> Self:
        self.assert_partitioned()
        return self

    @computed_field
    @property
    def display_name(self) -> str:
        return self.name or f"TimeSpan[id{str(hash(self))[:16]}]"

    def assert_partitioned(self) -> None:
        if not is_partitioned(self.subentries):
            msg = f"Data is not a correct partition:\n{self.subentries}"
            raise TemporalLogicError(msg)

    @property
    def seconds(self) -> float:
        self.assert_validity()
        return round(self.start.minutes_to(self.end) * Unit.MINUTE.seconds)

    @property
    def minutes(self) -> float:
        self.assert_validity()
        return round(self.start.minutes_to(self.end))

    @property
    def hours(self) -> float:
        self.assert_validity()
        return round(self.start.minutes_to(self.end) / Unit.HOUR.minutes)

    @property
    def days(self) -> float:
        self.assert_validity()
        return round(self.start.minutes_to(self.end) / Unit.DAY.minutes)

    def assert_validity(self) -> None: ...

    @abstractmethod
    def add_flex(self, entry: EntryProtocol) -> ResultTriple[Self]: ...

    @abstractmethod
    def add_fixed(self, entry: EntryProtocol, earliest: T, latest: T) -> ResultTriple[Self]: ...
