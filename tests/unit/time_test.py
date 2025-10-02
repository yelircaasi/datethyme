import pytest

from datethyme import Time
from datethyme._datethyme import Date, TimeDelta
from datethyme._null import NONE_TIME, NoneTime
from datethyme.exceptions import TimeValidationError


class TestTime:
    def test_validate_time(self):
        with pytest.raises(TimeValidationError):
            Time.validate_time("25:00")
        with pytest.raises(TimeValidationError):
            Time.validate_time("12:60")
        
        assert Time.validate_time("14:30") == {"hour": 14, "minute": 30, "second": 0.0}
        assert Time.validate_time("09:15:30") == {"hour": 9, "minute": 15, "second": 30.0}
        assert Time.validate_time({"hour": 10, "minute": 45}) == {"hour": 10, "minute": 45, "second": 0.0}
        assert Time.validate_time([8, 30]) == {"hour": 8, "minute": 30, "second": 0.0}
        assert Time.validate_time((12, 15, 45)) == {"hour": 12, "minute": 15, "second": 45.0}
    
    def test_start(self):
        start_time = Time.start()
        assert start_time.hour == 0
        assert start_time.minute == 0

    def test_end(self):
        end_time = Time.end()
        assert end_time.hour == 24
        assert end_time.minute == 0

    def test_parse(self):
        time = Time.parse("14:30")
        assert time.hour == 14
        assert time.minute == 30
        assert time.second == 0.0
        
        time_with_seconds = Time.parse("09:15:30.500")
        assert time_with_seconds.hour == 9
        assert time_with_seconds.minute == 15
        assert time_with_seconds.second == 30.5

    @pytest.mark.parametrize("hours, expected", [
        (1.5, Time(hour=1, minute=30, second=0)),
        (0.025, Time(hour=0, minute=1, second=30)),
        (0.0, Time(hour=0, minute=0, second=0)),
        (1.7583333333333333, Time(hour=1, minute=0, second=45.5)),
    ])
    def test_from_hours(hours, expected):
        assert Time.from_hours(hours) == expected

    @pytest.mark.parametrize("minutes, expected_hour, expected_minute, expected_second", [
        (90, 1, 30, 0.0),
        (125.5, 2, 5, 30.0),
        (0, 0, 0, 0.0),
        (1440, 24, 0, 0.0),
    ])
    def test_from_minutes(self, minutes, expected_hour, expected_minute, expected_second):
        time = Time.from_minutes(minutes)
        assert time.hour == expected_hour
        assert time.minute == expected_minute
        assert time.second == expected_second

    @pytest.mark.parametrize("seconds, expected", [
        (5400.0, Time(hour=1, minute=30, second=0)),
        (90.0, Time(hour=0, minute=1, second=30)),
        (0.0, Time(hour=0, minute=0, second=0)),
        (3645.5, Time(hour=1, minute=0, second=45.5)),
    ])
    def test_from_seconds(seconds, expected):
        assert Time.from_seconds(seconds) == expected

    def test_none(self):
        none_time = Time.none()
        assert isinstance(none_time, NoneTime)
        assert none_time == NONE_TIME

    def test_now(self):
        current_time = Time.now()
        assert isinstance(current_time, Time)
        assert 0 <= current_time.hour <= 23
        assert 0 <= current_time.minute <= 59

    @pytest.mark.parametrize("time,minutes_to_add,expected", [
        (Time(hour=10, minute=30), 30, Time(hour=11, minute=0)),
        (Time(hour=10, minute=30), 90, Time(hour=12, minute=0)),
        (Time(hour=23, minute=30), 60, Time(hour=24, minute=0)),
        (Time(hour=10, minute=30), -30, Time(hour=10, minute=0)),
    ], ids=["normal_30", "normal_90", "clamped", "negative"])
    def test_dunder_add(self, time, minutes_to_add, expected):
        result = time + minutes_to_add
        assert result == expected

    def test_dunder_and(self):
        time = Time(hour=14, minute=30)
        date = Date(year=2025, month=6, day=15)
        datetime = time & date
        assert datetime.year == 2025
        assert datetime.month == 6
        assert datetime.day == 15
        assert datetime.hour == 14
        assert datetime.minute == 30

    def test_dunder_bool(self):
        assert bool(Time(hour=0, minute=0)) is True
        assert bool(Time(hour=12, minute=30)) is True
        assert bool(Time(hour=23, minute=59)) is True

    @pytest.mark.parametrize("time_a,time_b,expected", [
        (Time(hour=10, minute=30), Time(hour=10, minute=30), True),
        (Time(hour=10, minute=30), Time(hour=10, minute=31), False),
        (Time(hour=10, minute=30), NoneTime(), False),
        (Time(hour=10, minute=30), "not a time", False),
    ])
    def test_dunder_eq(self, time_a, time_b, expected):
        assert (time_a == time_b) is expected

    @pytest.mark.parametrize("time_a,time_b,expected", [
        (Time(hour=10, minute=30), Time(hour=10, minute=30), True),
        (Time(hour=10, minute=31), Time(hour=10, minute=30), True),
        (Time(hour=10, minute=29), Time(hour=10, minute=30), False),
        (Time(hour=10, minute=30), NoneTime(), False),
    ])
    def test_dunder_ge(self, time_a, time_b, expected):
        assert (time_a >= time_b) is expected

    @pytest.mark.parametrize("time_a,time_b,expected", [
        (Time(hour=10, minute=31), Time(hour=10, minute=30), True),
        (Time(hour=10, minute=30), Time(hour=10, minute=30), False),
        (Time(hour=10, minute=29), Time(hour=10, minute=30), False),
        (Time(hour=10, minute=30), NoneTime(), False),
    ])
    def test_dunder_gt(self, time_a, time_b, expected):
        assert (time_a > time_b) is expected

    def test_dunder_hash(self):
        time_a = Time(hour=10, minute=30)
        time_b = Time(hour=10, minute=30)
        time3 = Time(hour=10, minute=31)
        
        assert hash(time_a) == hash(time_b)
        assert hash(time_a) != hash(time3)

    @pytest.mark.parametrize("time_a,time_b,expected", [
        (Time(hour=10, minute=30), Time(hour=10, minute=30), True),
        (Time(hour=10, minute=30), Time(hour=10, minute=31), True),
        (Time(hour=10, minute=31), Time(hour=10, minute=30), False),
        (Time(hour=10, minute=30), NoneTime(), False),
    ])
    def test_dunder_le(self, time_a, time_b, expected):
        assert (time_a <= time_b) is expected

    @pytest.mark.parametrize("time_a,time_b,expected", [
        (Time(hour=10, minute=29), Time(hour=10, minute=30), True),
        (Time(hour=10, minute=30), Time(hour=10, minute=30), False),
        (Time(hour=10, minute=31), Time(hour=10, minute=30), False),
        (Time(hour=10, minute=30), NoneTime(), False),
    ])
    def test_dunder_lt(self, time_a, time_b, expected):
        assert (time_a < time_b) is expected

    @pytest.mark.parametrize("time,expected", [
        (Time(hour=10, minute=30), "Time(10:30)"),
        (Time(hour=9, minute=5), "Time(09:05)"),
        (Time(hour=14, minute=30, second=45.5), "Time(14:30:45.500)"),
    ])
    def test_dunder_repr(self, time, expected):
        assert repr(time) == expected

    def test_dunder_rshift(self):
        start_time = Time(hour=9, minute=0)
        end_time = Time(hour=17, minute=0)
        timespan = start_time >> end_time
        assert timespan.start == start_time
        assert timespan.end == end_time

    @pytest.mark.parametrize("time,expected", [
        (Time(hour=10, minute=30), "10:30"),
        (Time(hour=9, minute=5), "09:05"),
        (Time(hour=14, minute=30, second=45.5), "14:30:45.500"),
        (Time(hour=0, minute=0, second=0), "00:00"),
    ])
    def test_dunder_str(self, time, expected):
        assert str(time) == expected

    def test_dunder_sub(self):
        time_a = Time(hour=10, minute=30)
        time_b = Time(hour=9, minute=0)
        delta = time_a - time_b
        assert isinstance(delta, TimeDelta)
        assert delta.seconds == 90 * 60  # 90 minutes in seconds
        
        time = Time(hour=10, minute=30)
        result = time - 30
        assert result == Time(hour=10, minute=0)

    @pytest.mark.parametrize("time, hours, expected", [
        (Time(hour=10, minute=30), 2, Time(hour=12, minute=30)),
        (Time(hour=22, minute=0), 5, Time(hour=24, minute=0)),
        (Time(hour=2, minute=0), -5, Time(hour=0, minute=0)),
    ], ids=["", "", "clamped_end", "clamped_start"])
    def test_add_hours_bounded(self, time, hours, expected):
        result = time.add_hours_bounded(hours)
        assert result == expected

    @pytest.mark.parametrize("time, hours, expected_time, expected_days", [
        (Time(hour=10, minute=30), 2, Time(hour=12, minute=30), 0),
        (Time(hour=22, minute=0), 5, Time(hour=3, minute=0), 1),
        (Time(hour=2, minute=0), -5, Time(hour=21, minute=0), -1),
    ])
    def test_add_hours_wraparound(self, time, hours, expected_time, expected_days):
        result_time, days = time.add_hours_wraparound(hours)
        assert result_time == expected_time
        assert days == expected_days

    @pytest.mark.parametrize("time, minutes, expected", [
        (Time(hour=10, minute=30), 30, Time(hour=11, minute=0)),
        (Time(hour=23, minute=30), 60, Time(hour=24, minute=0)),
        (Time(hour=1, minute=0), -90, Time(hour=0, minute=0)),
    ], ids=["", "clamped_end", "clamped_start"])
    def test_add_minutes_bounded(self, time, minutes, expected):
        result = time.add_minutes_bounded(minutes)
        assert result == expected

    @pytest.mark.parametrize("time, minutes, expected_time, expected_days", [
        (Time(hour=10, minute=30), 30, Time(hour=11, minute=0), 0),
        (Time(hour=23, minute=30), 60, Time(hour=0, minute=30), 1),
        (Time(hour=1, minute=0), -90, Time(hour=22, minute=30), -1),
    ])
    def test_add_minutes_wraparound(self, time, minutes, expected_time, expected_days):
        result_time, days = time.add_minutes_wraparound(minutes)
        assert result_time == expected_time
        assert days == expected_days

    @pytest.mark.parametrize("time, seconds, expected", [
        (Time(hour=10, minute=30, second=0), 30, Time(hour=10, minute=30, second=30)),
        (Time(hour=23, minute=59, second=30), 60, Time(hour=24, minute=0, second=0)),
        (Time(hour=0, minute=1, second=0), -90, Time(hour=0, minute=0, second=0)),
    ], ids=["", "clamped_end", "clamped_start"])
    def test_add_seconds_bounded(self, time, seconds, expected):
        result = time.add_seconds_bounded(seconds)
        assert result == expected

    @pytest.mark.parametrize("time, seconds, expected_time, expected_days", [
        (Time(hour=10, minute=30, second=0), 30, Time(hour=10, minute=30, second=30), 0),
        (Time(hour=23, minute=59, second=30), 60, Time(hour=0, minute=0, second=30), 1),
        (Time(hour=0, minute=1, second=0), -90, Time(hour=23, minute=59, second=30), -1),
    ])
    def test_add_seconds_wraparound(self, time, seconds, expected_time, expected_days):
        result_time, days = time.add_seconds_wraparound(seconds)
        assert result_time == expected_time
        assert days == expected_days

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=12, minute=0), Time(hour=10, minute=0), 2.0),
        (Time(hour=10, minute=30), Time(hour=9, minute=0), 1.5),
        (Time(hour=8, minute=0), Time(hour=10, minute=0), -2.0),
    ])
    def test_hours_from(self, time_a, time_b, expected):
        result = time_a.hours_from(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 2.0),
        (Time(hour=10, minute=0), Time(hour=8, minute=0), 14.0),
    ])
    def test_hours_from_last(self, time_a, time_b, expected):
        result = time_a.hours_from_last(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a,time_b,expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 2.0),
        (Time(hour=9, minute=0), Time(hour=10, minute=30), 1.5),
        (Time(hour=10, minute=0), Time(hour=8, minute=0), -2.0),
    ])
    def test_hours_to(self, time_a, time_b, expected):
        result = time_a.hours_to(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 2.0),
        (Time(hour=12, minute=0), Time(hour=8, minute=0), 20.0),
    ])
    def test_hours_to_next(self, time_a, time_b, expected):
        result = time_a.hours_to_next(time_b)
        assert result == expected

    def test_if_valid(self):
        valid_time = Time.if_valid("14:30")
        assert isinstance(valid_time, Time)
        assert valid_time.hour == 14
        assert valid_time.minute == 30
        
        invalid_time = Time.if_valid("25:70")
        assert isinstance(invalid_time, NoneTime)

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=12, minute=0), Time(hour=10, minute=0), 120.0),
        (Time(hour=10, minute=30), Time(hour=9, minute=0), 90.0),
        (Time(hour=8, minute=0), Time(hour=10, minute=0), -120.0),
    ])
    def test_minutes_from(self, time_a, time_b, expected):
        result = time_a.minutes_from(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 120.0),
        (Time(hour=10, minute=0), Time(hour=8, minute=0), 840.0),
    ])
    def test_minutes_from_last(self, time_a, time_b, expected):
        result = time_a.minutes_from_last(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 120.0),
        (Time(hour=9, minute=0), Time(hour=10, minute=30), 90.0),
        (Time(hour=10, minute=0), Time(hour=8, minute=0), -120.0),
    ])
    def test_minutes_to(self, time_a, time_b, expected):
        result = time_a.minutes_to(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 120.0),
        (Time(hour=12, minute=0), Time(hour=8, minute=0), 1200.0),
    ])
    def test_minutes_to_next(self, time_a, time_b, expected):
        result = time_a.minutes_to_next(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=12, minute=0), Time(hour=10, minute=0), 120.0),
        (Time(hour=10, minute=30), Time(hour=9, minute=0), 90.0),
        (Time(hour=8, minute=0), Time(hour=10, minute=0), -120.0),
    ])
    def test_seconds_from(self, time_a, time_b, expected):
        result = time_a.seconds_from(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 120.0),
        (Time(hour=10, minute=0), Time(hour=8, minute=0), 840.0),
    ])
    def test_seconds_from_last(self, time_a, time_b, expected):
        result = time_a.seconds_from_last(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 120.0),
        (Time(hour=9, minute=0), Time(hour=10, minute=30), 90.0),
        (Time(hour=10, minute=0), Time(hour=8, minute=0), -120.0),
    ])
    def test_seconds_to(self, time_a, time_b, expected):
        result = time_a.seconds_to(time_b)
        assert result == expected

    @pytest.mark.parametrize("time_a, time_b, expected", [
        (Time(hour=10, minute=0), Time(hour=12, minute=0), 120.0),
        (Time(hour=12, minute=0), Time(hour=8, minute=0), 1200.0),
    ])
    def test_seconds_to_next(self, time_a, time_b, expected):
        result = time_a.seconds_to_next(time_b)
        assert result == expected

    @pytest.mark.parametrize("time, expected", [
        (Time(hour=10, minute=30), "10:30"),
        (Time(hour=14, minute=30, second=45.5), "14:30:45.500"),
    ])
    def test_serialize_time(self, time, expected):
        result = time.serialize_time()
        assert result == expected

    def test_to_hours(): ...

    @pytest.mark.parametrize("time, expected", [
        (Time(hour=1, minute=30), 90.0),
        (Time(hour=10, minute=0), 600.0),
        (Time(hour=0, minute=0), 0.0),
        (Time(hour=12, minute=15), 735.0),
    ])
    def test_to_minutes(self, time, expected):
        result = time.to_minutes()
        assert result == expected

    @pytest.mark.parametrize("time, expected", [
        (Time(hour=1, minute=30, second=0), 5400.0),
        (Time(hour=0, minute=1, second=30), 90.0),
        (Time(hour=0, minute=0, second=0), 0.0),
        (Time(hour=1, minute=0, second=45.5), 3645.5),
    ])
    def test_to_seconds(self, time, expected):
        result = time.to_seconds()
        assert result == expected
