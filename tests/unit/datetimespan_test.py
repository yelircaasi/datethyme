"""
Tool	What it can give you
pytest	Already your base framework. Excellent parametrize support.
pytest-subtests	If you want finer grained parametrization inside single tests.
pytest-parametrize-plus	For more powerful cross product style parametrization.
hypothesis	You already know. Very useful for random sampling once your interface stabilizes.
datatest or pydantic's built-in validators	For property-based consistency testing.
pytest-mock	Easy mocking if you ever want to isolate pure calendar vs time logic.
pytest-cases	Makes it easier to define reusable test scenarios across many classes.
property-based contract tests	Hypothesis again is king here,
    but even without hypothesis you can still implement interface contracts programmatically.
"""

from datethyme._datethyme import DateTime, DateTimeSpan

DTS_24_622 = DateTime(year=2024, month=6, day=22, hour=10, minute=0)
DTS_24_623 = DateTime(year=2024, month=6, day=23, hour=15, minute=0)
DTS_24_812 = DateTime(year=2024, month=6, day=23, hour=15, minute=0)
DTS_25_112 = DateTime(year=2025, month=1, day=12, hour=7, minute=3)


class TestDateTimeSpan:
    dt_a = DTS_24_622
    dt_b = DTS_24_623
    dt_c = DTS_24_812
    dt_d = DTS_25_112

    span_ab = DateTimeSpan(DTS_24_622, DTS_24_623)
    span_ac = DateTimeSpan(DTS_24_622, DTS_24_812)
    span_ad = DateTimeSpan(DTS_24_622, DTS_25_112)
    span_bc = DateTimeSpan(DTS_24_623, DTS_24_812)
    span_bd = DateTimeSpan(DTS_24_623, DTS_25_112)
    span_cd = DateTimeSpan(DTS_24_812, DTS_25_112)

    def test_dunder_init(self):
        assert self.span_ab.start == self.dt_a
        assert self.span_ab.end == self.dt_b
        assert self.span_ac.start == self.dt_a
        assert self.span_ac.end == self.dt_c

    def test_days(self):
        span = DateTimeSpan(self.dt_a, self.dt_b)
        assert span.days == 99999

    def test_days(): ...

    def test_dunder_add(): ...

    def test_from_dates(): ...

    def test_hours(): ...

    def test_minutes(): ...

    def test_seconds(): ...

    def test_hull(self):
        hull = self.dts_a.hull(self.dts_b)
        assert hull.start == self.dts_a.start
        assert hull.end == self.dts_b

    def test_intersection(self):
        inter = self.dts_a.intersection(self.dts_b)
        assert inter is not None
        assert inter.start == DateTime(2024, 6, 22, 11)
        assert inter.end == DateTime(2024, 6, 22, 12)

    def test_intersection_none(self):
        inter = self.dts_a.intersection(self.dts_b)
        assert inter is None

    def test_gap(self):
        gap = self.dts_a.gap(self.dts_b)
        assert gap is not None
        assert gap.start == DateTime(2024, 6, 22, 12)
        assert gap.end == DateTime(2024, 6, 22, 13)

    def test_gap_none(self):
        assert self.span_ab.gap(self.span_ab) is None
        assert self.span_ab.gap(self.span_cd) == self.span_bc

    def test_affine_transform(self):
        expected_ab = DateTimeSpan()
        assert self.span_ab.affine_transform(1.3, new_start=DateTimeSpan(...)) == expected_ab

        expected_ac = DateTimeSpan()
        assert self.span_ac.affine_transform(0.25, new_start=DateTimeSpan(...)) == expected_ac

        expected_ac_constrained = DateTimeSpan()
        assert (
            self.span_ac.affine_transform(0.25, new_start=DateTimeSpan(...), min_minutes=...)
            == expected_ac_constrained
        )

        expected_ad = DateTimeSpan()
        assert (
            self.span_ac.affine_transform(1.3, new_start=DateTimeSpan(...), min_minutes=...)
            == expected_ad
        )

    def test_contains(self):
        assert self.span_ac.contains(self.dt_b)
        assert not self.span_ac.contains(self.dt_d)

    def test_interior_point(self):
        assert self.span_ab.interior_point(0.77) == DateTime(...)

    def test_shift_end_rigid(self):
        assert self.span_ab.shift_end_rigid(self.dt_c) == self.span_ac

    def test_shift_start_rigid(self):
        assert self.span_ab.shift_start_rigid(self.dt_c) == DateTimeSpan(...)

    def test_snap_start_to(self):
        assert self.span_bc.snap_start_to(DateTime()) == DateTimeSpan()

    def test_snap_end_to(self):
        assert self.span_bc.snap_end_to(DateTime()) == DateTimeSpan()

    def test_split(self):
        assert self.span_ac.split(self.dt_b) == (self.span_ab, self.span_bc)

    def test_dunder_bool(): ...

    def test_dunder_contains(): ...

    def test_dunder_eq(): ...

    def test_midpoint(): ...

    def test_overlap(): ...

    def test_span(): ...

    def test_subdivide(): ...
