import datetime as stdlib_datetime

import pytest

from datethyme import NONE_DATE, Date, DateRange, DateTime, Time
from datethyme._datethyme import DateTimeSpan


class TestDate:
    cinco_de_mayo = Date(year=2025, month=5, day=5)
    st_pat = Date(year=2027, month=3, day=17)
    time1613 = Time(hour=16, minute=13)

    def test_validate_raw_date(self):
        assert self.st_pat == Date.model_validate("2027-03-17")
        assert self.st_pat == Date.model_validate((2027, 3, 17))
        assert self.st_pat == Date.model_validate([2027, 3, 17])
        assert self.st_pat == Date.model_validate(
            {
                "year": 2027,
                "month": 3,
                "day": 17,
            }
        )

    def test_serialize_date(self): ...

    def test_datetime(self):
        assert self.cinco_de_mayo.datetime == DateTime(
            year=2025,
            month=5,
            day=5,
            hour=0,
            minute=0,
        )

    def test_model_dump(self):
        assert str(self.st_pat) == self.st_pat.model_dump()

    def test_span(self):
        assert self.st_pat.span == DateTimeSpan(
            start=self.st_pat.start,
            end=self.st_pat.end,
        )

    def test_start(self):
        assert self.st_pat.start == DateTime(
            year=2027,
            month=3,
            day=17,
            hour=0,
            minute=0,
        )
        assert self.cinco_de_mayo.start == DateTime(
            year=2025,
            month=5,
            day=5,
            hour=0,
            minute=0,
        )

    def test_stdlib(self):
        assert self.st_pat.stdlib == stdlib_datetime.date(year=2027, month=3, day=17)
        assert self.cinco_de_mayo.stdlib == stdlib_datetime.date(year=2025, month=5, day=5)

    def test_weekday(self):
        assert self.cinco_de_mayo.weekday == "mon"
        assert self.st_pat.weekday == "wed"

    def test_weekday_ordinal(self):
        assert self.cinco_de_mayo.weekday_ordinal == 0
        assert self.st_pat.weekday_ordinal == 2

    def test_ordinal(self):
        assert self.st_pat.ordinal == 740057
        assert self.cinco_de_mayo.ordinal == 739376

    def test_prose(self):
        assert self.st_pat.prose == "Wednesday, March 17th, 2027"
        assert self.cinco_de_mayo.prose == "Monday, May 5th, 2025"

    def test_end(self):
        assert self.st_pat.start == DateTime(
            year=2027,
            month=3,
            day=17,
            hour=0,
            minute=0,
        )
        assert self.cinco_de_mayo.end == DateTime(
            year=2025,
            month=5,
            day=5,
            hour=24,
            minute=0,
        )

    def test_parse(self):
        assert self.cinco_de_mayo == Date.parse("2025-05-05")
        assert self.cinco_de_mayo == Date.parse("2025-5-5")
        assert self.cinco_de_mayo == Date.parse("2025-05-5")
        assert self.cinco_de_mayo == Date.parse("2025-5-05")

    def test_from_ordinal(self):
        assert self.st_pat == Date.from_ordinal(740057)
        assert self.st_pat == Date.from_ordinal(self.st_pat.ordinal)

    def test_today(self):
        assert Date.today().stdlib == stdlib_datetime.date.today()

    def test_tomorrow(self):
        assert Date.today() == (Date.tomorrow() - 1)

    def test_dunder_add(self):
        assert (self.st_pat + 23) == Date.parse("2027-04-09")

    def test_dunder_sub(self):
        assert (self.st_pat - 23) == Date.parse("2027-02-22")
        assert (Date.parse("2027-02-22") - self.st_pat) == -23
        assert (self.st_pat - Date.parse("2027-02-22")) == 23

        assert self.st_pat - self.cinco_de_mayo == 681
        assert self.cinco_de_mayo - self.st_pat == -681

        assert (self.st_pat - 5) == Date.parse("2027-03-12")
        assert (self.cinco_de_mayo - 20) == Date.parse("2025-04-15")

    def test_dunder_and(self):
        assert (self.cinco_de_mayo & self.time1613) == DateTime(
            year=2025,
            month=5,
            day=5,
            hour=16,
            minute=13,
        )

    def test_dunder_bool(self):
        assert self.cinco_de_mayo
        assert self.st_pat
        assert bool(self.cinco_de_mayo)
        assert bool(self.st_pat)

    def test_dunder_eq(self):
        assert self.st_pat == Date.parse("2027-03-17")
        assert self.st_pat != Date.parse("2026-03-17")
        assert self.st_pat != Date.parse("2027-06-17")
        assert self.st_pat != Date.parse("2027-03-18")

    def test_dunder_ge(self):
        assert self.st_pat >= Date.parse("2027-03-17")
        assert self.st_pat >= Date.parse("2026-03-16")
        assert self.st_pat >= Date.parse("2026-02-16")
        assert self.st_pat >= Date.parse("2020-03-17")
        assert not (self.st_pat >= Date.parse("2028-02-16"))
        assert not (self.st_pat >= Date.parse("2027-03-18"))
        assert not (self.st_pat >= Date.parse("2027-04-16"))

    def test_dunder_gt(self):
        assert not (self.st_pat > Date.parse("2027-03-17"))
        assert self.st_pat > Date.parse("2026-03-16")
        assert self.st_pat > Date.parse("2026-02-16")
        assert self.st_pat > Date.parse("2020-03-17")
        assert not (self.st_pat > Date.parse("2028-02-16"))
        assert not (self.st_pat > Date.parse("2027-03-18"))
        assert not (self.st_pat > Date.parse("2027-04-16"))

    def test_dunder_hash(self):
        assert hash(self.st_pat) == 2660316880087496949
        assert hash(self.cinco_de_mayo) == 6492698278428822127

    def test_dunder_int(self):
        assert int(self.st_pat) == 740057
        assert int(self.cinco_de_mayo) == 739376

    def test_dunder_le(self):
        assert self.st_pat <= Date.parse("2027-03-17")
        assert self.st_pat <= Date.parse("2028-02-16")
        assert self.st_pat <= Date.parse("2027-03-18")
        assert self.st_pat <= Date.parse("2027-04-16")
        assert not (self.st_pat <= Date.parse("2027-03-16"))
        assert not (self.st_pat <= Date.parse("2027-02-20"))
        assert not (self.st_pat <= Date.parse("2026-09-30"))

    def test_dunder_lt(self):
        assert not (self.st_pat < Date.parse("2027-03-17"))
        assert self.st_pat < Date.parse("2028-02-16")
        assert self.st_pat < Date.parse("2027-03-18")
        assert self.st_pat < Date.parse("2027-04-16")
        assert not (self.st_pat < Date.parse("2027-03-16"))
        assert not (self.st_pat < Date.parse("2027-02-20"))
        assert not (self.st_pat < Date.parse("2026-09-30"))

    def test_dunder_pow(self):
        assert (self.cinco_de_mayo**self.st_pat) == DateRange(
            start=self.cinco_de_mayo, stop=self.st_pat
        )

    def test_dunder_repr(self):
        assert repr(self.st_pat) == "Date(2027-03-17)"
        assert repr(self.cinco_de_mayo) == "Date(2025-05-05)"

    def test_dunder_str(self):
        assert str(self.st_pat) == "2027-03-17"
        assert str(self.cinco_de_mayo) == "2025-05-05"

    def test_days_to(self):
        assert self.cinco_de_mayo.days_to(self.st_pat) == 681
        assert self.st_pat.days_to(self.cinco_de_mayo) == -681
        assert self.st_pat.days_to(self.st_pat) == 0
        assert self.st_pat.days_to(self.st_pat + 20) == 20

    @pytest.mark.parametrize(
        "template, formatted",
        [
            ("{weekday3}", "wed"),
            ("{Weekday}, {Month} {ordinal}, {year}", "Wednesday, March 17th, 2027"),
            ("{day} {month3} {year}", "17 mar 2027"),
            ("{WEEKDAY3} {day} {MONTH3} {year}", "WED 17 MAR 2027"),
            ("{ORDINAL} {MONTH} {year}", "17TH MARCH 2027"),
            ("{month3} {year}", "mar 2027"),
        ],
    )
    def test_format(self, template, formatted):
        assert self.st_pat.format(template) == formatted

    def test_if_valid(self):
        assert Date.if_valid("invalid string") is NONE_DATE
        assert Date.if_valid("2027-03-17") == self.st_pat

    def test_none(self):
        assert Date.none() == NONE_DATE

    def test_range(self):
        may5th = Date(year=2025, month=5, day=5)
        may6th = Date(year=2025, month=5, day=6)
        may7th = Date(year=2025, month=5, day=7)
        may8th = Date(year=2025, month=5, day=8)
        may9th = Date(year=2025, month=5, day=9)
        may10th = Date(year=2025, month=5, day=10)

        dr = [
            may5th,
            may6th,
            may7th,
            may8th,
            may9th,
        ]
        dr_inclusive = [
            may5th,
            may6th,
            may7th,
            may8th,
            may9th,
            may10th,
        ]
        dr_reversed = [
            may10th,
            may9th,
            may8th,
            may7th,
            may6th,
        ]
        dr_reversed_inclusive = [
            may10th,
            may9th,
            may8th,
            may7th,
            may6th,
            may5th,
        ]

        assert list(self.cinco_de_mayo.range(may10th)) == dr
        assert list(self.cinco_de_mayo.range(may10th, inclusive=True)) == dr_inclusive
        assert list(may10th.range(self.cinco_de_mayo)) == dr_reversed
        assert list(may10th.range(self.cinco_de_mayo, inclusive=True)) == dr_reversed_inclusive

    def test_affine_transform(self): ...
    def test_contains(self): ...
    def test_interior_point(self): ...
    def test_shift_end_rigid(self): ...
    def test_shift_start_rigid(self): ...
    def test_snap_end_to(self): ...
    def test_snap_start_to(self): ...
    def test_split(self): ...
