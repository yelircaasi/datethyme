from datethyme import DateTime
from datethyme._datethyme import (
    DateTimeHourRange,
    DateTimeMinuteRange,
    DateTimeSecondRange,
)


class TestDateTimeDayRange:
    range_a = DateTimeHourRange(
        DateTime.parse("2025-03-03_05:30:15"), DateTime.parse("2025-6-6_14:17")
    )

    def test_creation(self) -> None: ...


class TestDateTimeHourRange:
    range_a = DateTimeHourRange(
        DateTime.parse("2025-03-03_05:30:15"),
        DateTime.parse("2025-6-6_14:17"),
    )

    def test_creation(self) -> None: ...


class TestDateTimeMinuteRange:
    range_a = DateTimeMinuteRange(
        DateTime.parse("2025-03-03_05:30:15"),
        DateTime.parse("2025-6-6_14:17"),
    )

    def test_creation(self) -> None: ...


class TestDateTimeSecondRange:
    range_a = DateTimeSecondRange(
        DateTime.parse("2025-03-03_05:30:15"),
        DateTime.parse("2025-6-6_14:17"),
    )

    def test_creation(self) -> None: ...
