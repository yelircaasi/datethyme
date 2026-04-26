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

from datethyme import DateTime, DateTimeSpan

DTS_24_622 = DateTime(year=2024, month=6, day=22, hour=10, minute=0)
DTS_24_623 = DateTime(year=2024, month=6, day=23, hour=15, minute=0)
DTS_24_812 = DateTime(year=2024, month=6, day=23, hour=15, minute=0)
DTS_25_112 = DateTime(year=2025, month=1, day=12, hour=7, minute=3)

PLACEHOLDER = DateTime(year=2024, month=6, day=22, hour=10, minute=0)


class TestDateTimeSpan:
    dts_a = DateTimeSpan(DTS_24_622, DTS_24_623)
    dts_b = DateTimeSpan(DTS_24_622, DTS_24_623)
    dts_c = DateTimeSpan(DTS_24_622, DTS_24_623)
    dts_d = DateTimeSpan(DTS_24_622, DTS_24_623)

    span_ab = DateTimeSpan(DTS_24_622, DTS_24_623)
    span_ac = DateTimeSpan(DTS_24_622, DTS_24_812)
    span_ad = DateTimeSpan(DTS_24_622, DTS_25_112)
    span_bc = DateTimeSpan(DTS_24_623, DTS_24_812)
    span_bd = DateTimeSpan(DTS_24_623, DTS_25_112)
    span_cd = DateTimeSpan(DTS_24_812, DTS_25_112)

    def test_dunder_init(self):
        assert self.span_ab.start == self.dts_a
        assert self.span_ab.end == self.dts_b
        assert self.span_ac.start == self.dts_a
        assert self.span_ac.end == self.dts_c

    def test_days_alt(self) -> None:
        span = DateTimeSpan(PLACEHOLDER, PLACEHOLDER)
        assert span.days == 99999

    def test_days(self): ...

    def test_dunder_add(self): ...

    def test_from_dates(self): ...

    def test_hours(self): ...

    def test_minutes(self): ...

    def test_seconds(self): ...

    def test_hull(self) -> None:
        hull = self.dts_a.hull(self.dts_b)
        assert hull.start == self.dts_a.start
        assert hull.end == self.dts_b

    def test_intersection(self):
        inter = self.dts_a.intersection(self.dts_b)
        assert inter is not None
        assert inter.start == PLACEHOLDER
        assert inter.end == PLACEHOLDER

    def test_intersection_none(self):
        inter = self.dts_a.intersection(self.dts_b)
        assert inter is None

    def test_gap(self):
        gap = self.dts_a.gap(self.dts_b)
        assert gap is not None
        assert gap.start == DateTime.ymdhms(2024, 6, 22, 12)
        assert gap.end == DateTime.ymdhms(2024, 6, 22, 13)

    def test_gap_none(self):
        assert self.span_ab.gap(self.span_ab) is None
        assert self.span_ab.gap(self.span_cd) == self.span_bc

    def test_affine_transform(self):
        expected_ab = PLACEHOLDER
        assert self.span_ab.forward_affine_transform(1.3, new_start=PLACEHOLDER) == expected_ab

        expected_ac = PLACEHOLDER
        assert self.span_ac.forward_affine_transform(0.25, new_start=PLACEHOLDER) == expected_ac

        expected_ac_constrained = PLACEHOLDER
        assert (
            self.span_ac.forward_affine_transform(0.25, new_start=PLACEHOLDER, min_minutes=999)
            == expected_ac_constrained
        )

        expected_ad = DateTimeSpan(PLACEHOLDER, PLACEHOLDER)
        assert (
            self.span_ac.forward_affine_transform(1.3, new_start=PLACEHOLDER, min_minutes=999)
            == expected_ad
        )

    def test_contains(self):
        assert self.span_ac.contains(self.dts_b)
        assert not self.span_ac.contains(self.dts_d)

    def test_interior_point(self):
        assert self.span_ab.interior_point(0.77) == PLACEHOLDER

    def test_shift_end_rigid(self):
        assert self.span_ab.shift_end_rigid(PLACEHOLDER) == self.span_ac

    def test_shift_start_rigid(self):
        assert self.span_ab.shift_start_rigid(PLACEHOLDER) == PLACEHOLDER

    def test_snap_start_to(self):
        assert self.span_bc.snap_start_to(PLACEHOLDER) == PLACEHOLDER

    def test_snap_end_to(self):
        assert self.span_bc.snap_end_to(PLACEHOLDER) == PLACEHOLDER

    def test_split(self):
        assert self.span_ac.split(PLACEHOLDER) == (self.span_ab, self.span_bc)

    def test_dunder_bool(self): ...

    def test_dunder_contains(self): ...

    def test_dunder_eq(self): ...

    def test_midpoint(self): ...

    def test_overlap(self): ...

    def test_span(self): ...

    def test_subdivide(self): ...
