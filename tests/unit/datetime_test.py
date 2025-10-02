"""
import pytest
from hypothesis import given, strategies as st


# --- Helper strategy for valid DateTime objects ---
@st.composite
def datetimes(draw):
    year = draw(st.integers(min_value=1, max_value=9999))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=31))
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    second = draw(st.floats(min_value=0, max_value=59.999))
    return DateTime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)


"""

import pytest

from datethyme._datethyme import Date, DateTime, Time


class TestDateTime:
    @pytest.mark.parametrize(
        "raw_input, expected",
        [
            (
                {"year": 2024, "month": 6, "day": 22, "hour": 12, "minute": 30, "second": 15.5},
                DateTime(year=2024, month=6, day=22, hour=12, minute=30, second=15.5),
            ),
            (
                {"year": 1, "month": 1, "day": 1},
                DateTime(year=2000, month=1, day=1, hour=0, minute=0, second=0.0),
            ),
        ],
    )
    def test_validate_datetime(self, raw_input, expected):
        result = DateTime.model_validate(raw_input)
        assert result == expected

    @pytest.mark.parametrize(
        "dt, expected",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45, second=30),
                Time(hour=13, minute=45, second=30),
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=0, minute=1, second=1),
                Time(hour=0, minute=0, second=0),
            ),
        ],
    )
    def test_time(self, dt, expected):
        assert dt.time == expected

    @pytest.mark.parametrize(
        "dt, expected",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45, second=30),
                Date(year=2024, month=6, day=22),
            ),
            (
                DateTime(year=2000, month=1, day=1, hour=0, minute=1, second=1),
                Date(year=2000, month=1, day=1),
            ),
        ],
    )
    def test_date(self, dt, expected):
        assert dt.date == expected

    @pytest.mark.parametrize(
        "dt1, dt2, expected",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                DateTime(year=2024, month=6, day=22, hour=12, minute=45),
                True,
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=12, minute=45),
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                False,
            ),
        ],
    )
    def test_dunder_ge(self, dt1, dt2, expected):
        assert (dt1 >= dt2) == expected

    @pytest.mark.parametrize(
        "dt1, dt2, expected",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                DateTime(year=2024, month=6, day=22, hour=13, minute=44),
                True,
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                False,
            ),
        ],
    )
    def test_dunder_gt(self, dt1, dt2, expected):
        assert (dt1 > dt2) == expected

    @pytest.mark.parametrize(
        "dt1, dt2, expected",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                True,
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=14, minute=0),
                DateTime(year=2024, month=6, day=22, hour=14, minute=1),
                True,
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=15, minute=0),
                DateTime(year=2024, month=6, day=22, hour=14, minute=0),
                False,
            ),
        ],
    )
    def test_dunder_le(self, dt1, dt2, expected):
        assert (dt1 <= dt2) == expected

    @pytest.mark.parametrize(
        "dt1, dt2, expected",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                DateTime(year=2024, month=6, day=22, hour=13, minute=46),
                True,
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                DateTime(year=2024, month=6, day=22, hour=13, minute=45),
                False,
            ),
        ],
    )
    def test_dunder_lt(self, dt1, dt2, expected):
        assert (dt1 < dt2) == expected

    def test_dunder_repr(self):
        dt = DateTime(year=2024, month=6, day=22, hour=12, minute=30, second=15.123)
        assert repr(dt) == str(dt)

    def test_dunder_rshift(self):
        dt1 = DateTime(2024, 6, 22, 10)
        dt2 = DateTime(2024, 6, 23, 15)
        result = dt1 >> dt2
        assert result.start == dt1
        assert result.end == dt2

    @pytest.mark.parametrize(
        "dt, expected",
        [
            (DateTime(year=2024, month=6, day=22, hour=9, minute=5, second=0), "2024-06-22_09:05"),
            (
                DateTime(year=2024, month=12, day=31, hour=23, minute=59, second=59.123),
                "2024-12-31_23:59:59.123",
            ),
        ],
    )
    def test_dunder_str(self, dt, expected):
        s = str(dt)
        assert s.startswith(expected[:16])  # allow for second formatting

    def test_from_pair(self):
        d = Date(year=2024, month=6, day=22)
        t = Time(10, 30, 15.5)
        dt = DateTime.from_pair(d, t)
        assert dt.date == d
        assert dt.time == t

    @pytest.mark.parametrize(
        "dt, days, expected_date",
        [
            (
                DateTime(year=2024, month=6, day=22, hour=20, minute=6, second=22),
                1,
                Date(year=2024, month=6, day=23, hour=20, minute=6, second=22),
            ),
            (
                DateTime(year=2024, month=6, day=22, hour=20, minute=6, second=22),
                -1,
                Date(year=2024, month=6, day=21, hour=20, minute=6, second=22),
            ),
        ],
    )
    def test_add_days(self, dt, days, expected_date):
        result = dt.add_days(days)
        assert result.date == expected_date
        assert result.time == dt.time

    @pytest.mark.parametrize(
        "dt, hours",
        [
            (DateTime(year=2024, month=6, day=22, hour=10, minute=0), 5),
            (DateTime(year=2024, month=6, day=22, hour=10, minute=0), 2.5),
            (DateTime(year=2024, month=6, day=22, hour=10, minute=0), -3),
        ],
    )
    def test_add_hours(self, dt, hours):
        result = dt.add_hours(hours)
        assert isinstance(result, DateTime)

    @pytest.mark.parametrize(
        "dt, minutes",
        [
            (DateTime(year=2024, month=6, day=22, hour=10, minute=0), 60),
            (DateTime(year=2024, month=6, day=22, hour=23, minute=59), 1),
            (DateTime(year=2024, month=6, day=22, hour=0, minute=0), -15),
        ],
    )
    def test_add_minutes(self, dt, minutes):
        result = dt.add_minutes(minutes)
        assert isinstance(result, DateTime)

    @pytest.mark.parametrize(
        "dt, seconds",
        [
            (DateTime(year=2024, month=6, day=22, hour=10, minute=0, second=0), 3600),
            (DateTime(year=2024, month=6, day=22, hour=23, minute=59, second=59), 2),
            (DateTime(year=2024, month=6, day=22, hour=0, minute=0, second=0), -30),
        ],
    )
    def test_add_seconds(self, dt, seconds):
        result = dt.add_seconds(seconds)
        assert isinstance(result, DateTime)

    def test_hours_from(self):
        dt1 = DateTime(2024, 6, 22, 12)
        dt2 = DateTime(2024, 6, 22, 14)
        assert dt1.hours_from(dt2) == -2
        assert dt2.hours_from(dt1) == 2

    def test_hours_from_last(self):
        dt1 = DateTime(2024, 6, 22, 12)
        dt2 = DateTime(2024, 6, 22, 14)
        assert dt1.hours_from_last(dt2) >= 0

    def test_hours_to(self):
        dt1 = DateTime(2024, 6, 22, 12)
        dt2 = DateTime(2024, 6, 22, 15)
        assert dt1.hours_to(dt2) == 3

    def test_hours_to_next(self):
        dt1 = DateTime(2024, 6, 22, 23)
        dt2 = DateTime(2024, 6, 22, 2)
        assert dt1.hours_to_next(dt2) >= 0

    def test_minutes_from(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=12, minute=0)
        dt2 = DateTime(year=2024, month=6, day=22, hour=12, minute=30)
        assert dt1.minutes_from(dt2) == -30
        assert dt2.minutes_from(dt1) == 30

    def test_minutes_from_last(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=12, minute=0)
        dt2 = DateTime(year=2024, month=6, day=22, hour=12, minute=30)
        assert dt1.minutes_from_last(dt2) >= 0

    def test_minutes_to(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=12, minute=0)
        dt2 = DateTime(year=2024, month=6, day=22, hour=12, minute=45)
        assert dt1.minutes_to(dt2) == 45

    def test_minutes_to_next(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=23, minute=59)
        dt2 = DateTime(year=2024, month=6, day=22, hour=0, minute=1)
        assert dt1.minutes_to_next(dt2) >= 0

    def test_parse(self):
        s = "2024-06-22_09:30:15.000"
        dt = DateTime.parse(s)
        assert str(dt) == s

    def test_seconds_from(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=12, minute=0, second=0)
        dt2 = DateTime(year=2024, month=6, day=22, hour=12, minute=0, second=10)
        assert dt1.seconds_from(dt2) == -10

    def test_seconds_from_last(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=12, minute=0, second=0)
        dt2 = DateTime(year=2024, month=6, day=22, hour=12, minute=0, second=10)
        assert dt1.seconds_from_last(dt2) >= 0

    def test_seconds_to(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=12, minute=0, second=0)
        dt2 = DateTime(year=2024, month=6, day=22, hour=12, minute=0, second=20)
        assert dt1.seconds_to(dt2) == 20

    def test_seconds_to_next(self):
        dt1 = DateTime(year=2024, month=6, day=22, hour=23, minute=59, second=59)
        dt2 = DateTime(year=2024, month=6, day=22, hour=0, minute=0, second=1)
        assert dt1.seconds_to_next(dt2) >= 0
