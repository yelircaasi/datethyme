"""
# with pytest.raises(ValueError) as exc_info: TODO
#     process_string(42)
# assert str(exc_info.value) == expected_message
"""

import pytest

from datethyme import HourRange, Time


class TestHourRange:
    hr = HourRange(start=Time(hour=5, minute=30), stop=Time(hour=13, minute=30))
    hr_inclusive = HourRange(
        start=Time(hour=5, minute=30),
        stop=Time(hour=13, minute=30),
        inclusive=True,
    )

    def test_dunder_contains(self):
        assert Time(hour=7, minute=30) in self.hr
        assert Time(hour=13, minute=30) not in self.hr
        assert Time(hour=9, minute=31) not in self.hr
        assert (time445 := Time(hour=4, minute=45)) not in HourRange(
            start=Time(hour=1, minute=45),
            stop=time445,
        )

    def test_dunder_getitem(self):
        assert self.hr[1] == Time(hour=6, minute=30)
        assert self.hr[1:4] == HourRange(Time(hour=6, minute=30), Time(hour=9, minute=30))

    def test_dunder_init(self):
        with pytest.raises(
            ValueError, match="Set allow_wraparound=True to allow HourRange to pass a day boundary."
        ):
            HourRange(Time(hour=23, minute=12), Time(hour=4, minute=23))

        hr_wrap = HourRange(
            Time(hour=23, minute=12),
            Time(hour=4, minute=23),
            allow_wraparound=True,
        )
        assert len(hr_wrap) == 2

    def test_dunder_len(self):
        assert len(self.hr) == 8
        assert len(self.hr_inclusive) == 9

    def test_dunder_reversed(
        self,
    ): ...  # TODO: remove __reversed__? in any case, not the highest priority

    def test_index(self):
        with pytest.raises(ValueError, match="..."):
            self.hr.index[50]

    def test_last(self):
        assert self.hr.last == Time(hour=12, minute=30)
        assert self.hr_inclusive.last == Time(hour=13, minute=30)

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
