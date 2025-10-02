from datethyme import NONE_DATE, Date
from datethyme._null import NoneDate


class TestNoneDate:
    nd = NONE_DATE
    xmas = Date.parse("2031-12-31")

    def test_dunder_init(self):
        assert NoneDate() == self.nd

    def test_dunder_add(self):
        assert (self.nd + self.xmas) == self.nd

    def test_dunder_bool(self):
        assert not self.nd
        assert not bool(self.nd)

    def test_dunder_eq(self):
        assert self.nd == self.nd
        assert self.nd != self.xmas

    def test_dunder_ge(self):
        assert not (self.nd >= self.xmas)

    def test_dunder_gt(self):
        assert not (self.nd > self.xmas)

    def test_dunder_le(self):
        assert not (self.nd <= self.xmas)

    def test_dunder_lt(self):
        assert not (self.nd < self.xmas)

    def test_dunder_repr(self):
        assert repr(self.nd) == "NoneDate"

    def test_dunder_str(self):
        assert str(self.nd) == "NoneDate"

    def test_dunder_sub(self):
        assert (self.nd - self.xmas) is None
        assert (self.nd - 33) == self.nd
