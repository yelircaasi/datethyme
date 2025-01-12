import datetime
import re
import pytest
from pydantic import ValidationError

from datethyme import Time, NoneTime, TimeValidationError


class TestTime:
    def test_validation(self):
        t = Time(hour=5, minute=36)

        assert t

        assert (t + 102) == Time(hour=7, minute=18)
        assert (t - 123) == Time(hour=3, minute=33)
        assert Time.from_minutes(666) == Time(hour=11, minute=6)

        assert (
            Time(hour=5, minute=36)
            == Time.model_validate("5:36")
            == Time.model_validate("05:36")
            == Time.model_validate("05:36:00")
            == Time.model_validate("05:36:00.000")
            == Time.model_validate(t)
        )

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

    def test_hash(self):
        t = Time(hour=5, minute=36)
        assert hash(t) == hash(Time(hour=5, minute=36))

    def test_dump(self):
        t = Time(hour=5, minute=36)
        assert t.model_dump() == "05:36" == str(t) == t.model_dump()

    def test_repr(self):
        t = Time(hour=5, minute=36)
        assert repr(t) == "Time(05:36)"

    def test_timespans(self):
        t = Time(hour=5, minute=36)
        assert t.minutes_to(Time(hour=23, minute=56)) == 1100
        assert t.minutes_from(Time(hour=3, minute=23)) == 133

    def test_validation_error(self):

        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Date: '12'\."),
        ):
            _d = Time.model_validate("12")

        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Date: '\[\]'\."),
        ):
            _d = Time.model_validate([])

        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Date: '\(1, 2, 3\)'\."),
        ):
            _d = Time.model_validate((1, 2, 3))

        with pytest.raises(
            TimeValidationError,
            match=re.compile(r"Invalid value for conversion to Date: 'None'\."),
        ):
            _d = Time.model_validate(None)

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
    def test_nonetime(self):
        nt = Time.nonetime()
        # nt2 = Time.model_validate("None")
        # nt3 = Time.model_validate("null")
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
