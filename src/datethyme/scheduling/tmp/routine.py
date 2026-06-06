from __future__ import annotations

from pathlib import Path
from typing import Self

from adiumentum.fp import lmap
from adiumentum.io import read_json, write_json
from pydantic import BaseModel, Field


class RoutineItem(BaseModel):
    name: str
    description: str | None
    minTime: int
    idealTime: int
    normalTime: int
    maxTime: int
    narrowable: bool = Field(default=False)

    @property
    def text(self) -> str:
        return self.description or self.name


class Routine(BaseModel):
    name: str
    elements: list[RoutineItem]
    narrowable: bool = Field(default=True)
    # TODO: use me to add other more specific tasks (i.e. cleaning <- mopping)

    @property
    def normalTime(self) -> int:
        return sum(x.normalTime for x in self.elements)

    @property
    def minTime(self) -> int:
        return sum(x.minTime for x in self.elements)

    @property
    def idealTime(self) -> int:
        return sum(x.idealTime for x in self.elements)

    @property
    def maxTime(self) -> int:
        return sum(x.maxTime for x in self.elements)


class Routines(dict[str, Routine]):
    # @model_validator(mode="before")
    # @classmethod
    # def _(cls, value: object) -> dict[str, object]:
    #     if not isinstance(value, list):
    #         raise ValueError
    #     return {x["name"]: x for x in value}

    # @model_serializer
    # def _(self) -> list[object]:
    #     return list(self.values())

    @classmethod
    def read_json_file(cls, p: Path) -> Self:
        raw: dict[str, object] = read_json(p)  # type: ignore
        return cls({e.name: e for e in map(Routine.model_validate, raw)})

    def write_json_file(self, p: Path) -> Path:
        dumped = lmap(lambda x: x.model_dump(mode="json"), self.values())
        write_json(dumped, p)  # type: ignore
        return p
