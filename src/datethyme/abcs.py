from abc import ABC


class OptionalDate(ABC):
    year: int | None
    month: int | None
    day: float | None


class OptionalTime(ABC):
    hour: int | None
    minute: int | None
    second: float | None


class OptionalDateTime(ABC):
    year: int | None
    month: int | None
    day: int | None
    hour: int | None
    minute: int | None
    second: float | None
