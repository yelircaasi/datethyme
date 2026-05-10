from __future__ import annotations

from typing import Annotated

from adiumentum.pydantic import BaseDict
from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer

from ...core import Date


class Entry(BaseModel):
    name: str
    normal_time: int = Field(default=30)
    projects: set[str] | None = Field(default_factory=set)
    priority: float = Field(default=0.5)
    contexts: set[str | None] = Field(default_factory=set)
    dependencies: set[str] | None = Field(default=None)
    min_time_explicit: int | None = Field(default=None)
    ideal_time_explicit: int | None = Field(default=None)
    max_time_explicit: int | None = Field(default=None)
    due_date: Date | None = Field(default=None)
    earliest_date: Date | None = Field(default=None)

    @property
    def min_time(self) -> int:
        return min(
            self.normal_time,
            self.min_time_explicit or self.normal_time,
            self.ideal_time_explicit or self.normal_time,
        )

    @property
    def ideal_time(self) -> int:
        return self.ideal_time_explicit or self.normal_time

    @property
    def max_time(self) -> int:
        return max(
            self.normal_time,
            self.max_time_explicit or self.normal_time,
            self.ideal_time_explicit or self.normal_time,
        )

    def __repr__(self) -> str:
        return (
            f"ScheduleItem[{self.name}]({self.min_time} ≤ {self.normal_time}"
            f" ≤ {self.max_time}, ideal_time={self.ideal_time})"
        )

    def __str__(self) -> str:
        return repr(self)

    def rescaled(self, scale_factor: float) -> Entry:
        def rescale(maybe_num: int | None) -> int | None:
            if maybe_num is None:
                return maybe_num
            return round(scale_factor * maybe_num)

        return Entry(
            name=self.name,
            normal_time=round(self.normal_time * scale_factor),
            projects=self.projects,
            min_time_explicit=rescale(self.min_time_explicit),
            ideal_time_explicit=rescale(self.ideal_time_explicit),
            max_time_explicit=rescale(self.max_time_explicit),
            priority=self.priority,
        )


class Entries(BaseDict[str, Entry]):
    """Container type for a sequence of entries."""

    # @model_validator(mode="after")
    # def verify_unique_ids(self) -> Self:
    #     if not len(set(self)) == len(self):
    #         raise ValueError("Item names must be unique.")
    #     return self

    @property
    def normal_time(self) -> float:
        return sum(map(lambda it: it.normal_time, self.values()))

    @property
    def min_time(self) -> float:
        return sum(map(lambda it: it.min_time, self.values()))

    @property
    def ideal_time(self) -> float:
        return sum(map(lambda it: it.ideal_time, self.values()))

    @property
    def max_time(self) -> float:
        return sum(map(lambda it: it.max_time, self.values()))

    def __repr__(self) -> str:
        return f"Entries(\n    {'\n    '.join(map(repr, self.values()))}\n)"

    def __str__(self) -> str:
        return f"Entries(\n    {'\n    '.join(map(repr, self.values()))}\n)"


def _entries_deserialize(v: list[dict]) -> Entries:
    if isinstance(v, Entries):
        return v
    if isinstance(v, dict):
        return Entries.model_validate(v)
    names = [e["name"] for e in v]
    if len(names) != len(set(names)):
        raise ValueError("Entry names must be unique.")
    return Entries({e["name"]: e for e in v})


def _entries_serialize(v: Entries) -> list[Entry]:
    return list(v.values())


SerializedEntries = Annotated[
    Entries,
    BeforeValidator(_entries_deserialize),
    PlainSerializer(_entries_serialize, return_type=list[Entry]),
]
