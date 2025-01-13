import datetime
import re

import pytest

from datethyme import Date, DateValidationError, NoneDate


class TestDate:
    date = Date(year=2025, month=4, day=25)
    nonedate = Date.none()

    def test_parse(self):
        assert self.date == Date.parse("2025-04-25") == Date.parse("2025-4-25")

    def test_representation(self):
        assert self.date.model_dump() == "2025-04-25"
        assert repr(self.date) == "Date(2025-04-25)"

    def test_validation(self):
        assert (
            self.date
            == Date.model_validate((2025, 4, 25))
            == Date.model_validate([2025, 4, 25])
            == Date.model_validate(self.date)
            == Date.model_validate("2025-04-25")
            == Date.model_validate("2025-4-25")
        )

    def test_if_valid(self):
        assert Date.if_valid("") == self.nonedate
        assert Date.if_valid("nonsense") == self.nonedate
        assert Date.if_valid(None) == self.nonedate
        assert Date.if_valid((1, 2, 3)) == self.nonedate
        assert Date.if_valid("2025-04-25") == self.date
        assert Date.if_valid("2025-4-25") == self.date

    def test_days_to(self):
        d = Date(year=2025, month=4, day=25)
        assert d.days_to(Date(year=2026, month=1, day=15)) == 265

        assert d.stdlib == datetime.date(2025, 4, 25)
        assert d.weekday == "fri"
        assert d.pretty() == "Friday, April 25th, 2025"

    def test_formatting(self):
        assert Date(year=2025, month=4, day=3).pretty() == "Thursday, April 3rd, 2025"
        assert Date(year=2027, month=10, day=4).pretty() == "Monday, October 4th, 2027"
        assert Date(year=2019, month=6, day=21).pretty() == "Friday, June 21st, 2019"

    def test_today_and_tomorrow(self):
        today = Date.today()
        tomorrow = Date.tomorrow()

        today_stdlib = datetime.date.today()
        assert today == Date(year=today_stdlib.year, month=today_stdlib.month, day=today_stdlib.day)
        assert tomorrow == Date(
            year=today_stdlib.year, month=today_stdlib.month, day=today_stdlib.day + 1
        )

    def test_range(self):
        range_normal = Date(year=2025, month=12, day=30).range(Date(year=2026, month=1, day=4))
        range_int = Date(year=2025, month=12, day=30).range(5)
        range_int_noninclusive = Date(year=2025, month=12, day=30).range(6, inclusive=False)
        range_noninclusive = Date(year=2025, month=12, day=30).range(
            Date(year=2026, month=1, day=5), inclusive=False
        )
        range_reverse = Date(year=2026, month=1, day=4).range(Date(year=2025, month=12, day=30))
        range_reverse_noninclusive = Date(year=2026, month=1, day=4).range(
            Date(year=2025, month=12, day=29), inclusive=False
        )
        range_expected = [
            Date(year=2025, month=12, day=30),
            Date(year=2025, month=12, day=31),
            Date(year=2026, month=1, day=1),
            Date(year=2026, month=1, day=2),
            Date(year=2026, month=1, day=3),
            Date(year=2026, month=1, day=4),
        ]

        assert range_normal == range_expected
        assert range_int == range_expected
        assert range_int_noninclusive == range_expected
        assert range_noninclusive == range_expected
        assert range_reverse == range_reverse_noninclusive == list(reversed(range_expected))

    def test_date_comparison(self):
        assert Date(year=2020, month=12, day=30) > Date(year=2020, month=12, day=29)
        assert Date(year=2021, month=12, day=30) > Date(year=2020, month=12, day=29)
        assert Date(year=2020, month=12, day=30) > Date(year=2020, month=11, day=30)

        assert Date(year=2020, month=12, day=29) < Date(year=2020, month=12, day=30)
        assert Date(year=2020, month=12, day=30) < Date(year=2021, month=12, day=30)
        assert Date(year=2020, month=11, day=30) < Date(year=2020, month=12, day=30)

        assert Date(year=2020, month=12, day=30) >= Date(year=2020, month=12, day=30)
        assert Date(year=2020, month=12, day=30) >= Date(year=2019, month=12, day=30)
        assert Date(year=2020, month=12, day=30) >= Date(year=2020, month=12, day=29)
        assert Date(year=2020, month=12, day=30) >= Date(year=2020, month=11, day=30)

        assert Date(year=2020, month=12, day=30) <= Date(year=2020, month=12, day=30)
        assert Date(year=2020, month=12, day=30) <= Date(year=2021, month=12, day=30)
        assert Date(year=2020, month=12, day=30) <= Date(year=2021, month=1, day=1)
        assert Date(year=2020, month=11, day=30) <= Date(year=2020, month=12, day=30)
        assert Date(year=2020, month=12, day=30) <= Date(year=2020, month=12, day=31)

        assert Date(year=2020, month=12, day=30) == Date(year=2020, month=12, day=30)
        assert not (Date(year=2020, month=12, day=30) == Date(year=2021, month=12, day=30))
        assert not (Date(year=2020, month=12, day=30) == Date(year=2020, month=1, day=30))
        assert not (Date(year=2020, month=12, day=30) == Date(year=2020, month=12, day=2))

    def test_date_validation(self):
        assert Date.model_validate(Date(year=2020, month=12, day=20)) == Date(
            year=2020, month=12, day=20
        )

        with pytest.raises(
            DateValidationError,
            match=re.compile(r"Invalid value for conversion to Date: `2025-13` \(str\)."),
        ):
            Date.model_validate("2025-13")

        with pytest.raises(
            DateValidationError,
            match=re.compile(r"Invalid value for conversion to Date: `2025-13-05` \(str\)."),
        ):
            Date.model_validate("2025-13-05")

        with pytest.raises(
            DateValidationError,
            match=re.compile(r"Invalid value for conversion to Date: `2025-05-32` \(str\)."),
        ):
            Date.model_validate("2025-05-32")

        with pytest.raises(
            DateValidationError,
            match=re.compile(r"Invalid value for conversion to Date: `2025-13` \(str\)."),
        ):
            Date.model_validate("2025-13")

        with pytest.raises(
            TypeError,
            match=re.compile(
                r"BaseModel.model_validate\(\) takes 2 positional arguments but 4 were given"
            ),
        ):
            Date.model_validate(2020, 12, 20)

        with pytest.raises(
            DateValidationError,
            match=re.compile(r"Invalid value for conversion to Date: `None` \(NoneType\)."),
        ):
            Date.model_validate(None)

    def test_hashing(self):
        d = Date(year=2025, month=4, day=25)
        assert hash(d) == hash(Date(year=2025, month=4, day=25))


class TestNoneDate:
    nonedate = Date.none()
    date = Date(year=2025, month=4, day=25)

    def test_validation(self):
        _ = Date.none()

    def test_typing(self):
        nd = Date.none()
        d = Date(year=2025, month=4, day=25)

        assert isinstance(nd, NoneDate)
        assert not nd

        assert not (nd < d)
        assert not (nd > d)
        assert not (nd <= d)
        assert not (nd >= d)
        assert not (nd == d)

        assert not (nd < nd)
        assert not (nd > nd)
        assert not (nd <= nd)
        assert not (nd >= nd)
        assert nd == nd

        assert not nd.__lt__(d)
        assert not nd.__gt__(d)
        assert not nd.__le__(d)
        assert not nd.__ge__(d)
        assert not nd.__eq__(d)

        assert not (d < nd)
        assert not (d > nd)
        assert not (d <= nd)
        assert not (d >= nd)
        assert not (d == nd)

        assert not d.__lt__(nd)
        assert not d.__gt__(nd)
        assert not d.__le__(nd)
        assert not d.__ge__(nd)
        assert not d.__eq__(nd)

    def test_string_and_repr(self):
        nd = Date.none()
        assert str(nd) == repr(nd) == "NoneDate"

    def test_arithmetic(self):
        assert (self.nonedate + 42) == self.nonedate
        assert (self.nonedate - 42) == self.nonedate
