import pytest

from datethyme.exceptions import (
    DateValidationError,
    TimeValidationError,
)
from datethyme.utils import (
    assert_xor,
    transfer_case,
    truthy_falsy,
    validate_date,
    validate_time,
)


@pytest.mark.parametrize(
    "reference,candidate,expected",
    [
        ("Hello", "world", "World"),
        ("hello", "WORLD", "world"),
        ("HELLO", "world", "WORLD"),
        ("Mixed", "case", "Case"),
        ("plain", "text", "text"),
    ],
)
def test_transfer_case(reference: str, candidate: str, expected: str) -> None:
    assert transfer_case(reference, candidate) == expected


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
        validate_time(None)  # type: ignore

    with pytest.raises(TimeValidationError):
        validate_time("12:12:12:12:12")


def test_truthy_falsy():
    assert truthy_falsy("s", "") == (True, ("s", ""))
    assert truthy_falsy(True, False) == (True, (True, False))
    assert truthy_falsy(False, True) == (False, (True, False))
    assert truthy_falsy("", "some string") == (False, ("some string", ""))

    class SomeClass:
        def __eq__(self, value: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 123

    INSTANCE = SomeClass()

    assert truthy_falsy(None, INSTANCE) == (False, (INSTANCE, None))

    for a, b in [
        (True, True),
        (False, False),
        (None, None),
        ("string", "other string"),
        (INSTANCE, INSTANCE),
    ]:
        with pytest.raises(ValueError):
            truthy_falsy(a, b)
        with pytest.raises(ValueError):
            assert_xor(a, b)
