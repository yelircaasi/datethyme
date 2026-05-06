from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class DataType(StrEnum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"


class BaseData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    datatype: DataType = Field(alias="type")
    label: str


class TextData(BaseData):
    datatype: Literal[DataType.TEXT] = Field(alias="type")
    value: str
    max_length: int | None = None


class NumberData(BaseData):
    datatype: Literal[DataType.NUMBER] = Field(alias="type")
    value: float
    unit: str | None = None


class BooleanData(BaseData):
    datatype: Literal[DataType.BOOLEAN] = Field(alias="type")
    value: bool


type AnyData = Annotated[
    TextData | NumberData | BooleanData,
    Field(discriminator="datatype"),
]


class Payload(BaseModel):
    """Wrapper model that holds a list of heterogensous types."""

    items: list[AnyData]


if __name__ == "__main__":
    payload = Payload.model_validate({
        "items": [
            {"type": "text", "label": "Name", "value": "Alice"},
            {"type": "number", "label": "Score", "value": 42.5},
        ]
    })

    item = payload.items[0]
    print(item.datatype)
    print(item.model_dump(by_alias=True))

    payload.model_dump()
