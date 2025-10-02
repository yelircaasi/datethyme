from typing import Self


class TimeValidationError(TypeError):
    @classmethod
    def from_value(cls, value: str | dict | list | tuple) -> Self:
        return cls(f"Invalid value for conversion to Time: `{value}` ({value.__class__.__name__}).")


class DateValidationError(TypeError):
    @classmethod
    def from_value(cls, value: str | dict | list | tuple) -> Self:
        return cls(f"Invalid value for conversion to Date: `{value}` ({value.__class__.__name__}).")


class DateTimeValidationError(TypeError):
    @classmethod
    def from_value(cls, value: str | dict | list | tuple) -> Self:
        return cls(f"Invalid value for conversion to Date: `{value}` ({value.__class__.__name__}).")
