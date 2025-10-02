import pytest

from datethyme import (
    DateTime,
    MinuteRangeDated,
)


class TestMinuteRangeDated:
    mr = MinuteRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0),
        stop=DateTime(year=2025, month=6, day=15, hour=10, minute=38, second=0),
    )
    mr_inclusive = MinuteRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0),
        stop=DateTime(year=2025, month=6, day=15, hour=10, minute=38, second=0),
        inclusive=True,
    )

    def test_last(self):
        assert self.mr.last == DateTime(year=2025, month=6, day=15, hour=10, minute=37, second=0)
        assert self.mr_inclusive.last == DateTime(
            year=2025, month=6, day=15, hour=10, minute=38, second=0
        )

    def test_dunder_contains(self):
        assert DateTime(year=2025, month=6, day=15, hour=10, minute=32, second=0) in self.mr
        assert DateTime(year=2025, month=6, day=15, hour=10, minute=38, second=0) not in self.mr
        assert DateTime(year=2025, month=6, day=15, hour=10, minute=39, second=0) not in self.mr
        assert (
            dt1030 := DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=0)
        ) not in MinuteRangeDated(
            start=DateTime(year=2025, month=6, day=15, hour=10, minute=25, second=0),
            stop=dt1030,
        )

    def test_dunder_getitem(self):
        assert self.mr[1] == DateTime(year=2025, month=6, day=15, hour=10, minute=31, second=0)
        assert self.mr[1:4] == MinuteRangeDated(
            DateTime(year=2025, month=6, day=15, hour=10, minute=31, second=0),
            DateTime(year=2025, month=6, day=15, hour=10, minute=34, second=0),
        )

    def test_dunder_init(self):
        with pytest.raises(
            ValueError,
            match="Set allow_wraparound=True to allow MinuteRangeDated to pass an hour boundary.",
        ):
            MinuteRangeDated(
                DateTime(year=2025, month=6, day=15, hour=10, minute=45, second=0),
                DateTime(year=2025, month=6, day=15, hour=11, minute=15, second=0),
            )

        mr_wrap = MinuteRangeDated(
            DateTime(year=2025, month=6, day=15, hour=10, minute=45, second=0),
            DateTime(year=2025, month=6, day=15, hour=11, minute=15, second=0),
            allow_wraparound=True,
        )
        assert len(mr_wrap) == 30

    def test_dunder_len(self):
        assert len(self.mr) == 8
        assert len(self.mr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_count(self):
        assert (
            self.mr.count(DateTime(year=2025, month=6, day=15, hour=10, minute=32, second=0)) == 1
        )
        assert (
            self.mr.count(DateTime(year=2025, month=6, day=15, hour=10, minute=40, second=0)) == 0
        )

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.mr.index[50]

    def test__increment(self):
        curr = self.mr._current
        self.mr._increment
        assert self.mr._current == (curr.add_minutes(1))

    def test__restart(): ...

    def test_dunder_eq(): ...

    def test_dunder_hash(): ...

    def test_dunder_iter(): ...

    def test_dunder_next(): ...

    def test_filtered(): ...
