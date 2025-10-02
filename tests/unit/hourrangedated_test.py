import pytest

from datethyme import (
    DateTime,
    HourRangeDated,
)


class TestHourRangeDated:
    hr = HourRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0),
        stop=DateTime(year=2025, month=6, day=15, hour=18, minute=30, second=0),
    )
    hr_inclusive = HourRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0),
        stop=DateTime(year=2025, month=6, day=15, hour=18, minute=30, second=0),
        inclusive=True,
    )

    def test_last(self):
        assert self.hr.last == DateTime(year=2025, month=6, day=15, hour=17, minute=30, second=0)
        assert self.hr_inclusive.last == DateTime(
            year=2025, month=6, day=15, hour=18, minute=30, second=0
        )

    def test_dunder_contains(self):
        assert DateTime(year=2025, month=6, day=15, hour=12, minute=30, second=0) in self.hr
        assert DateTime(year=2025, month=6, day=15, hour=18, minute=30, second=0) not in self.hr
        assert DateTime(year=2025, month=6, day=15, hour=19, minute=30, second=0) not in self.hr
        assert (
            dt1030 := DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0)
        ) not in HourRangeDated(
            start=DateTime(year=2025, month=6, day=15, hour=8, minute=30, second=0),
            stop=dt1030,
        )

    def test_dunder_getitem(self):
        assert self.hr[1] == DateTime(year=2025, month=6, day=15, hour=11, minute=30, second=0)
        assert self.hr[1:4] == HourRangeDated(
            DateTime(year=2025, month=6, day=15, hour=11, minute=30, second=0),
            DateTime(year=2025, month=6, day=15, hour=14, minute=30, second=0),
        )

    def test_dunder_init(self):
        with pytest.raises(
            ValueError,
            match="Set allow_wraparound=True to allow HourRangeDated to pass a day boundary.",
        ):
            HourRangeDated(
                DateTime(year=2025, month=6, day=15, hour=23, minute=30, second=0),
                DateTime(year=2025, month=6, day=16, hour=2, minute=30, second=0),
            )

        hr_wrap = HourRangeDated(
            DateTime(year=2025, month=6, day=15, hour=23, minute=30, second=0),
            DateTime(year=2025, month=6, day=16, hour=2, minute=30, second=0),
            allow_wraparound=True,
        )
        assert len(hr_wrap) == 3

    def test_dunder_len(self):
        assert len(self.hr) == 8
        assert len(self.hr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_count(self):
        assert (
            self.hr.count(DateTime(year=2025, month=6, day=15, hour=12, minute=30, second=0)) == 1
        )
        assert (
            self.hr.count(DateTime(year=2025, month=6, day=15, hour=20, minute=30, second=0)) == 0
        )

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.hr.index[50]

    def test__increment(self):
        curr = self.hr._current
        self.hr._increment
        assert self.hr._current == (curr.add_hours(1))

    def test__restart(): ...

    def test_dunder_eq(): ...

    def test_dunder_hash(): ...

    def test_dunder_iter(): ...

    def test_dunder_next(): ...

    def test_filtered(): ...
