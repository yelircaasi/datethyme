import pytest

from datethyme import Time, TimeSpan
from datethyme.utils import (
    snap_back,
    transfer_case,
    validate_date,
    validate_time,
)


class DateValidationError(ValueError):  # TODO
    @classmethod
    def from_value(cls, val):
        return cls(f"Invalid date: {val}")


class TimeValidationError(ValueError):  # TODO
    @classmethod
    def from_value(cls, val):
        return cls(f"Invalid time: {val}")


def test_transfer_case():
    assert transfer_case("Hello", "world") == "World"
    assert transfer_case("hello", "WORLD") == "world"
    assert transfer_case("HELLO", "world") == "WORLD"
    assert transfer_case("Mixed", "case") == "Case"
    assert transfer_case("plain", "text") == "text"


def test_validate_date():
    assert validate_date("2024-06-22") == {"year": 2024, "month": 6, "day": 22}
    assert validate_date(["2024", "6", "22"]) == {"year": 2024, "month": 6, "day": 22}
    assert validate_date({"year": 2024, "month": 6, "day": 22}) == {
        "year": 2024,
        "month": 6,
        "day": 22,
    }

    assert validate_date({"year": 0, "month": 0, "day": 0}) == {"year": 0, "month": 0, "day": 0}

    with pytest.raises(DateValidationError):
        validate_date("not-a-date")

    with pytest.raises(DateValidationError):
        validate_date(["2024", "13", "01"])

    with pytest.raises(DateValidationError):
        validate_date({"year": 2024, "month": 2, "day": 30})


def test_validate_time():
    # valid times
    assert validate_time("12:30:45") == {"hour": 12.0, "minute": 30.0, "second": 45.0}
    assert validate_time("12:30") == {"hour": 12.0, "minute": 30.0}
    assert validate_time(["12", "30", "45"]) == {"hour": "12", "minute": "30", "second": "45"}
    assert validate_time({"hour": 12, "minute": 30, "second": 45}) == {
        "hour": 12,
        "minute": 30,
        "second": 45,
    }
    assert validate_time({"hour": -1, "minute": -1, "second": -1.0}) == {
        "hour": -1,
        "minute": -1,
        "second": -1.0,
    }

    with pytest.raises(TimeValidationError):
        validate_time("")

    with pytest.raises(TimeValidationError):
        validate_time("25:00:00")

    with pytest.raises(TimeValidationError):
        validate_time("12:61:00")

    with pytest.raises(TimeValidationError):
        validate_time("12:30:61.0")

    with pytest.raises(TimeValidationError):
        validate_time(["12", "30", "45", "extra"])

    with pytest.raises(TimeValidationError):
        validate_time(None)


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_snap_back(original, times, modified):
    assert snap_back(*original) == modified


def test_assert_xor(): ...
