import pytest

from datethyme import Time, TimeSpan

TS_24_622 = Time(hour=10, minute=0)
TS_24_623 = Time(hour=15, minute=0)
TS_24_812 = Time(hour=15, minute=0)
TS_25_112 = Time(hour=7, minute=3)

PLACEHOLDER_TIME = Time(hour=10, minute=0)


class TestTimeSpan:
    time_a = TS_24_622
    time_b = TS_24_623
    time_c = TS_24_812
    time_d = TS_25_112

    span_ab = TimeSpan(TS_24_622, TS_24_623)
    span_ac = TimeSpan(TS_24_622, TS_24_812)
    span_ad = TimeSpan(TS_24_622, TS_25_112)
    span_bc = TimeSpan(TS_24_623, TS_24_812)
    span_bd = TimeSpan(TS_24_623, TS_25_112)
    span_cd = TimeSpan(TS_24_812, TS_25_112)

    def test_dunder_init(self): ...

    @pytest.mark.parametrize(
        "start, end, expected_minutes",
        [
            (Time(hour=10, minute=0), Time(hour=11, minute=0), 60),
            (Time(hour=0, minute=0), Time(hour=0, minute=0), 0),
        ],
    )
    def test_minutes(self, start, end, expected_minutes):
        span = TimeSpan(start, end)
        assert span.minutes == expected_minutes

    @pytest.mark.parametrize(
        "start, end, expected_seconds",
        [
            (Time(hour=10, minute=0, second=0), Time(hour=11, minute=0, second=0), 3600),
            (Time(hour=10, minute=0, second=0), Time(hour=10, minute=0, second=30), 30),
        ],
    )
    def test_seconds(self, start, end, expected_seconds):
        span = TimeSpan(start, end)
        assert span.seconds == expected_seconds

    @pytest.mark.parametrize(
        "start, end, expected_hours",
        [
            (Time(hour=10, minute=0), Time(hour=11, minute=0), 1),
            (Time(hour=10, minute=0), Time(hour=10, minute=30), 0.5),
        ],
    )
    def test_hours(self, start, end, expected_hours) -> None:
        span = TimeSpan(start, end)
        assert span.hours == expected_hours

    @pytest.mark.parametrize(
        "start, end, expected_days",
        [
            (Time(hour=0, minute=0), Time(hour=12, minute=0), 0.5),
            (Time(hour=0, minute=0), Time(hour=0, minute=0), 0),
        ],
    )
    def test_days(self, start, end, expected_days) -> None:
        span = TimeSpan(start, end)
        assert span.days == expected_days

    def test_name_and_id(self) -> None:
        span = TimeSpan(Time(hour=10, minute=0), Time(hour=11, minute=0), name="TestSpan")
        assert span.name == "TestSpan"
        assert span.id == "TestSpan"

    def test_hull(self) -> None:
        hull = self.span_ac.hull(self.span_bd)
        assert hull.start == self.time_a
        assert hull.end == Time(hour=12, minute=0)

    def test_intersection(self) -> None:
        a = TimeSpan(Time(hour=10, minute=0), Time(hour=11, minute=0))
        b = TimeSpan(Time(hour=10, minute=30), Time(hour=12, minute=0))
        inter = a.intersection(b)
        assert inter is not None
        assert inter.start == Time(hour=10, minute=30)
        assert inter.end == Time(hour=11, minute=0)

    def test_intersection_none(self) -> None:
        a = TimeSpan(Time(hour=10, minute=0), Time(hour=11, minute=0))
        b = TimeSpan(Time(hour=12, minute=0), Time(hour=13, minute=0))
        inter = a.intersection(b)
        assert inter is None

    def test_gap(self) -> None:
        a = TimeSpan(Time(hour=10, minute=0), Time(hour=11, minute=0))
        b = TimeSpan(Time(hour=12, minute=0), Time(hour=13, minute=0))
        gap = a.gap(b)
        assert gap is not None
        assert gap.start == Time(hour=11, minute=0)
        assert gap.end == Time(hour=12, minute=0)

    def test_gap_none(self) -> None:
        a = TimeSpan(Time(hour=10, minute=0), Time(hour=11, minute=0))
        b = TimeSpan(Time(hour=10, minute=30), Time(hour=12, minute=0))
        gap = a.gap(b)
        assert gap is None

    def test_affine_transform(self) -> None:
        expected_ab = TimeSpan(PLACEHOLDER_TIME, PLACEHOLDER_TIME)
        transform_ab = self.span_ab.forward_affine_transform(1.3, new_start=PLACEHOLDER_TIME)
        assert transform_ab == expected_ab

        expected_ac = TimeSpan(PLACEHOLDER_TIME, PLACEHOLDER_TIME)
        transform_ac = self.span_ac.forward_affine_transform(0.25, new_start=PLACEHOLDER_TIME)
        assert transform_ac == expected_ac

        expected_ac_constrained = TimeSpan(PLACEHOLDER_TIME, PLACEHOLDER_TIME)
        transform_ac_constrained = self.span_ac.forward_affine_transform(
            0.25,
            new_start=PLACEHOLDER_TIME,
            min_minutes=999,
        )
        assert transform_ac_constrained == expected_ac_constrained

        expected_ad = TimeSpan(PLACEHOLDER_TIME, PLACEHOLDER_TIME)
        transformed_ad = self.span_ac.forward_affine_transform(
            1.3,
            new_start=PLACEHOLDER_TIME,
            min_minutes=999,
        )
        assert transformed_ad == expected_ad

    def test_contains(self) -> None:
        assert self.span_ac.contains(self.time_b)
        assert not self.span_ac.contains(self.time_d)

    def test_interior_point(self) -> None:
        assert self.span_ab.interior_point(0.77) == PLACEHOLDER_TIME

    def test_shift_end_rigid(self) -> None:
        assert self.span_ab.shift_end_rigid(self.time_c) == self.span_ac

    def test_shift_start_rigid(self) -> None:
        assert self.span_ab.shift_start_rigid(self.time_c) == TimeSpan(
            PLACEHOLDER_TIME, PLACEHOLDER_TIME
        )

    def test_snap_start_to(self) -> None:
        assert self.span_bc.snap_start_to(PLACEHOLDER_TIME) == TimeSpan(
            PLACEHOLDER_TIME, PLACEHOLDER_TIME
        )

    def test_snap_end_to(self) -> None:
        assert self.span_bc.snap_end_to(PLACEHOLDER_TIME) == TimeSpan(
            PLACEHOLDER_TIME, PLACEHOLDER_TIME
        )

    def test_split(self) -> None:
        assert self.span_ac.split(self.time_b) == (self.span_ab, self.span_bc)

    def test_id(self): ...

    def test_name(self): ...

    def test_dunder_bool(self): ...

    def test_dunder_contains(self): ...

    def test_dunder_eq(self): ...

    def test_midpoint(self): ...

    def test_overlap(self): ...

    def test_span(self): ...

    def test_subdivide(self): ...
