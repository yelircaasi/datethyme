import datetime
import re

import pytest

from datethyme import NoneTime, Time, TimeValidationError


class TestTime:
    time = Time(hour=5, minute=36)
    nonetime = Time.none()

    def test_parse(self):
        assert (
            self.time
            == Time.parse("5:36")
            == Time.parse("05:36")
            == Time.parse("5:36:00")
            == Time.parse("5:36:00.000")
        )

    def test_representation(self):
        t = Time(hour=5, minute=36)
        assert (
            Time(hour=5, minute=36)
            == Time.model_validate("5:36")
            == Time.model_validate("05:36")
            == Time.model_validate("05:36:00")
            == Time.model_validate("05:36:00.000")
            == Time.model_validate(t)
        )

    def test_validation(self):
        t = Time(hour=5, minute=36)

        assert t
        assert (t + 102) == Time(hour=7, minute=18)
        assert (t - 123) == Time(hour=3, minute=33)
        assert Time.from_minutes(666) == Time(hour=11, minute=6)

        assert (
            Time(hour=5)
            == Time.model_validate((5, 0))
            == Time.model_validate((5,))
            == Time.model_validate([5, 0])
            == Time.model_validate([5])
            == Time(hour=5, minute=0)
            == Time.model_validate("5:00")
            == Time.model_validate("05:00")
            == Time.model_validate("05:00:00")
        )

        assert Time.model_validate("12")

    def test_hash(self):
        t = Time(hour=5, minute=36)
        assert hash(t) == hash(Time(hour=5, minute=36))

    def test_dump(self):
        t = Time(hour=5, minute=36)
        assert t.model_dump() == "05:36" == str(t) == t.model_dump()

    def test_repr(self):
        t = Time(hour=5, minute=36)
        assert repr(t) == "Time(05:36)"

        assert repr(Time.model_validate("6:03:49")) == "Time(06:03:49.000)"
        assert repr(Time.model_validate("23:00:05.112003")) == "Time(23:00:05.112)"

    def test_if_valid(self):
        assert Time.if_valid("") == self.nonetime
        assert Time.if_valid("nonsense") == self.nonetime
        assert Time.if_valid(None) == self.nonetime
        assert Time.if_valid((1, 2, 72)) == self.nonetime
        assert Time.if_valid("5:36") == self.time
        assert Time.if_valid("05:36") == self.time

    def test_timespans(self):
        t = Time(hour=5, minute=36)
        assert t.minutes_to(Time(hour=23, minute=56)) == 1100
        assert t.minutes_from(Time(hour=3, minute=23)) == 133

    def test_validation_error(self):
        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Time: `\[\]` \(list\)\."),
        ):
            Time.model_validate([])

        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Time: `\(1, 2, 72\)` \(tuple\)\."),
        ):
            Time.model_validate((1, 2, 72))

        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Time: `None` \(NoneType\)\."),
        ):
            Time.model_validate(None)

    def test_comparisons(self):
        assert Time(hour=13, minute=47) > Time(hour=13, minute=46)
        assert Time(hour=13, minute=47) > Time(hour=12, minute=47)
        assert Time(hour=13, minute=47) > Time(hour=5, minute=7)
        assert Time(hour=13, minute=47) > Time(hour=0, minute=0)

        assert Time(hour=13, minute=47) < Time(hour=13, minute=48)
        assert Time(hour=13, minute=47) < Time(hour=14, minute=47)
        assert Time(hour=13, minute=47) < Time(hour=17, minute=12)
        assert Time(hour=13, minute=47) < Time(hour=24, minute=0)

        assert Time(hour=13, minute=47) >= Time(hour=13, minute=47)
        assert Time(hour=13, minute=47) >= Time(hour=13, minute=46)
        assert Time(hour=13, minute=47) >= Time(hour=12, minute=47)
        assert Time(hour=13, minute=47) >= Time(hour=5, minute=7)
        assert Time(hour=13, minute=47) >= Time(hour=0)

        assert Time(hour=13, minute=47) <= Time(hour=13, minute=47)
        assert Time(hour=13, minute=47) <= Time(hour=13, minute=48)
        assert Time(hour=13, minute=47) <= Time(hour=14, minute=47)
        assert Time(hour=13, minute=47) <= Time(hour=17, minute=12)
        assert Time(hour=13, minute=47) <= Time(hour=24)

        assert Time(hour=13, minute=47) == Time(hour=13, minute=47)
        assert not (Time(hour=13, minute=47) == Time(hour=13, minute=48))
        assert not (Time(hour=13, minute=47) == Time(hour=9, minute=47))
        assert not (Time(hour=13, minute=47) == Time(hour=12, minute=50))
        assert not (Time(hour=13, minute=47) == "")

    def test_now(self):
        now = Time.now()
        now_stdlib = datetime.datetime.now()
        assert abs(now.hour - now_stdlib.hour) <= 1
        assert abs(now.minute - now_stdlib.minute) <= 1


class TestNoneTime:
    nonetime = Time.none()
    time = Time(hour=5, minute=36)

    def test_none(self):
        nt = Time.none()
        t = Time(hour=5, minute=36)

        assert isinstance(nt, NoneTime)

        assert not nt
        assert (nt + Time(hour=5, minute=5)) == nt
        assert (nt - Time(hour=5, minute=5)) == nt
        assert (nt + 5) == nt
        assert (nt - 5) == nt

        assert not (nt < t)
        assert not (nt > t)
        assert not (nt <= t)
        assert not (nt >= t)
        assert not (nt == t)

        assert not (nt < nt)
        assert not (nt > nt)
        assert not (nt <= nt)
        assert not (nt >= nt)
        assert nt == nt

        assert not nt.__lt__(t)
        assert not nt.__gt__(t)
        assert not nt.__le__(t)
        assert not nt.__ge__(t)
        assert not nt.__eq__(t)

        assert not (t < nt)
        assert not (t > nt)
        assert not (t <= nt)
        assert not (t >= nt)
        assert not (t == nt)

        assert not t.__lt__(nt)
        assert not t.__gt__(nt)
        assert not t.__le__(nt)
        assert not t.__ge__(nt)
        assert not t.__eq__(nt)

        assert str(nt) == repr(nt) == "NoneTime"

    def test_arithmetic(self):
        assert (self.nonetime + 42) == self.nonetime
        assert (self.nonetime - 42) == self.nonetime
