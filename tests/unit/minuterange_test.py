import pytest

from datethyme import MinuteRange, Time


class TestMinuteRange:
    mr = MinuteRange(start=Time(hour=5, minute=30), stop=Time(hour=5, minute=38))
    mr_inclusive = MinuteRange(
        start=Time(hour=5, minute=30),
        stop=Time(hour=5, minute=38),
        inclusive=True,
    )

    def test_count(self): ...

    def test_dunder_init(self):
        with pytest.raises(
            ValueError,
            match="Set allow_wraparound=True to allow MinuteRange to pass an hour boundary.",
        ):
            MinuteRange(Time(hour=5, minute=45), Time(hour=6, minute=15))

        mr_wrap = MinuteRange(
            Time(hour=5, minute=45),
            Time(hour=6, minute=15),
            allow_wraparound=True,
        )
        assert len(mr_wrap) == 30

    def test_dunder_contains(self):
        assert Time(hour=5, minute=32) in self.mr
        assert Time(hour=5, minute=38) not in self.mr
        assert Time(hour=5, minute=39) not in self.mr
        assert (time530 := Time(hour=5, minute=30)) not in MinuteRange(
            start=Time(hour=5, minute=25),
            stop=time530,
        )

    def test_dunder_getitem(self):
        assert self.mr[1] == Time(hour=5, minute=31)
        assert self.mr[1:4] == MinuteRange(Time(hour=5, minute=31), Time(hour=5, minute=34))

    def test_dunder_len(self):
        assert len(self.mr) == 8
        assert len(self.mr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.mr.index[50]

    def test_last(self):
        assert self.mr.last == Time(hour=5, minute=37)
        assert self.mr_inclusive.last == Time(hour=5, minute=38)

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
