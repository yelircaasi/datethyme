import pytest

from datethyme import (
    DateTime,
    SecondRangeDated,
)


class TestSecondRangeDated:
    sr = SecondRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=15),
        stop=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=23),
    )
    sr_inclusive = SecondRangeDated(
        start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=15),
        stop=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=23),
        inclusive=True,
    )

    def test_last(self):
        assert self.sr.last == DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=22)
        assert self.sr_inclusive.last == DateTime(
            year=2025, month=6, day=15, hour=10, minute=30, second=23
        )

    def test_dunder_contains(self):
        assert DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=17) in self.sr
        assert DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=23) not in self.sr
        assert DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=24) not in self.sr
        assert (
            dt1015 := DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=15)
        ) not in SecondRangeDated(
            start=DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=10),
            stop=dt1015,
        )

    def test_dunder_getitem(self):
        assert self.sr[1] == DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=16)
        assert self.sr[1:4] == SecondRangeDated(
            DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=16),
            DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=19),
        )

    def test_dunder_init(self):
        with pytest.raises(
            ValueError,
            match="Set allow_wraparound=True to allow SecondRangeDated to pass a minute boundary.",
        ):
            SecondRangeDated(
                DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=45),
                DateTime(year=2025, month=6, day=15, hour=10, minute=31, second=15),
            )

        sr_wrap = SecondRangeDated(
            DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=45),
            DateTime(year=2025, month=6, day=15, hour=10, minute=31, second=15),
            allow_wraparound=True,
        )
        assert len(sr_wrap) == 30

    def test_dunder_iter(self):
        seconds = list(self.sr)
        assert len(seconds) == 8
        assert seconds[0] == DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=15)
        assert seconds[-1] == DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=22)

    def test_dunder_len(self):
        assert len(self.sr) == 8
        assert len(self.sr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.sr.index[50]

    def test__increment(self):
        curr = self.sr._current
        self.sr._increment
        assert self.sr._current == (curr.add_seconds(1))

    def test__limit(self):
        # Assuming _limit tests some boundary or constraint functionality
        assert self.sr._limit() == DateTime(
            year=2025, month=6, day=15, hour=10, minute=30, second=22
        )

    def test__rem(self):
        # Assuming _rem tests remainder functionality or modulo operations
        dt = DateTime(year=2025, month=6, day=15, hour=10, minute=30, second=20)
        assert self.sr._rem(dt) == 5  # 5 seconds from start

    def test__restart(): ...

    def test_dunder_eq(): ...

    def test_dunder_hash(): ...

    def test_dunder_iter(): ...

    def test_dunder_next(): ...

    def test_filtered(): ...
