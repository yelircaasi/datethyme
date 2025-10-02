import pytest

from datethyme import (
    DateTime,
    DayRangeDated,
)


class TestDayRangeDated:
    dr = DayRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0),
        stop=DateTime(year=2025, month=6, day=23, hour=10, minute=30, second=0),
    )
    dr_inclusive = DayRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0),
        stop=DateTime(year=2025, month=6, day=23, hour=10, minute=30, second=0),
        inclusive=True,
    )

    def test_last(self):
        assert self.dr.last == DateTime(year=2025, month=6, day=22, hour=10, minute=30, second=0)
        assert self.dr_inclusive.last == DateTime(
            year=2025, month=6, day=23, hour=10, minute=30, second=0
        )

    def test_dunder_contains(self):
        assert DateTime(year=2025, month=6, day=17, hour=10, minute=30, second=0) in self.dr
        assert DateTime(year=2025, month=6, day=23, hour=10, minute=30, second=0) not in self.dr
        assert DateTime(year=2025, month=6, day=24, hour=10, minute=30, second=0) not in self.dr
        assert (
            dt615 := DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0)
        ) not in DayRangeDated(
            start=DateTime(year=2025, month=6, day=10, hour=10, minute=30, second=0),
            stop=dt615,
        )

    def test_dunder_getitem(self):
        assert self.dr[1] == DateTime(year=2025, month=6, day=16, hour=10, minute=30, second=0)
        assert self.dr[1:4] == DayRangeDated(
            DateTime(year=2025, month=6, day=16, hour=10, minute=30, second=0),
            DateTime(year=2025, month=6, day=19, hour=10, minute=30, second=0),
        )

    def test_dunder_init(self):
        with pytest.raises(
            ValueError,
            match="Set allow_wraparound=True to allow DayRangeDated to pass a month boundary.",
        ):
            DayRangeDated(
                DateTime(year=2025, month=6, day=28, hour=10, minute=30, second=0),
                DateTime(year=2025, month=7, day=5, hour=10, minute=30, second=0),
            )

        dr_wrap = DayRangeDated(
            DateTime(year=2025, month=6, day=28, hour=10, minute=30, second=0),
            DateTime(year=2025, month=7, day=5, hour=10, minute=30, second=0),
            allow_wraparound=True,
        )
        assert len(dr_wrap) == 7

    def test_dunder_len(self):
        assert len(self.dr) == 8
        assert len(self.dr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_count(self):
        assert (
            self.dr.count(DateTime(year=2025, month=6, day=17, hour=10, minute=30, second=0)) == 1
        )
        assert (
            self.dr.count(DateTime(year=2025, month=6, day=25, hour=10, minute=30, second=0)) == 0
        )

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.dr.index[50]

    def test__increment(self):
        curr = self.dr._current
        self.dr._increment
        assert self.dr._current == (curr.add_days(1))

    def test__restart(): ...

    def test_dunder_eq(): ...

    def test_dunder_hash(): ...

    def test_dunder_iter(): ...

    def test_dunder_next(): ...

    def test_filtered(): ...
