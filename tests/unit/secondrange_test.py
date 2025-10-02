import pytest

from datethyme import SecondRange, Time


class TestSecondRange:
    sr = SecondRange(
        start=Time(hour=5, minute=30, second=15), stop=Time(hour=5, minute=30, second=23)
    )
    sr_inclusive = SecondRange(
        start=Time(hour=5, minute=30, second=15),
        stop=Time(hour=5, minute=30, second=23),
        inclusive=True,
    )

    def test__increment(self):
        curr = self.sr._current
        self.sr._increment
        assert self.sr._current == (curr.add_seconds(1))

    def test_count(self):
        # Assuming count method counts occurrences of a specific time
        assert self.sr.count(Time(hour=5, minute=30, second=17)) == 1
        assert self.sr.count(Time(hour=5, minute=30, second=25)) == 0

    def test_dunder_contains(self):
        assert Time(hour=5, minute=30, second=17) in self.sr
        assert Time(hour=5, minute=30, second=23) not in self.sr
        assert Time(hour=5, minute=30, second=24) not in self.sr
        assert (time515 := Time(hour=5, minute=30, second=15)) not in SecondRange(
            start=Time(hour=5, minute=30, second=10),
            stop=time515,
        )

    def test_dunder_getitem(self):
        assert self.sr[1] == Time(hour=5, minute=30, second=16)
        assert self.sr[1:4] == SecondRange(
            Time(hour=5, minute=30, second=16), Time(hour=5, minute=30, second=19)
        )

    def test_dunder_init(self):
        with pytest.raises(
            ValueError,
            match="Set allow_wraparound=True to allow SecondRange to pass a minute boundary.",
        ):
            SecondRange(Time(hour=5, minute=30, second=45), Time(hour=5, minute=31, second=15))

        sr_wrap = SecondRange(
            Time(hour=5, minute=30, second=45),
            Time(hour=5, minute=31, second=15),
            allow_wraparound=True,
        )
        assert len(sr_wrap) == 30

    def test_dunder_len(self):
        assert len(self.sr) == 8
        assert len(self.sr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.sr.index[50]

    def test_last(self):
        assert self.sr.last == Time(hour=5, minute=30, second=22)
        assert self.sr_inclusive.last == Time(hour=5, minute=30, second=23)

    def test__restart(): ...

    def test_dunder_eq(): ...

    def test_dunder_hash(): ...

    def test_dunder_iter(): ...

    def test_dunder_next(): ...

    def test_filtered(): ...
