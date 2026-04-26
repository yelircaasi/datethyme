from datethyme import (
    DateTime,
    HourRangeDated,
    MinuteRangeDated,
    SecondRangeDated,
)


class TestDateTimeDayRange:
    range_a = HourRangeDated(
        DateTime.parse("2025-03-03_05:30:15"), DateTime.parse("2025-6-6_14:17")
    )

    def test_creation(self) -> None: ...


class TestHourRangeDated:
    range_a = HourRangeDated(
        DateTime.parse("2025-03-03_05:30:15"),
        DateTime.parse("2025-6-6_14:17"),
    )

    def test_creation(self) -> None: ...


class TestMinuteRangeDated:
    range_a = MinuteRangeDated(
        DateTime.parse("2025-03-03_05:30:15"),
        DateTime.parse("2025-6-6_14:17"),
    )

    def test_creation(self) -> None: ...


class TestSecondRangeDated:
    range_a = SecondRangeDated(
        DateTime.parse("2025-03-03_05:30:15"),
        DateTime.parse("2025-6-6_14:17"),
    )

    def test_creation(self) -> None: ...
