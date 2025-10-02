from datethyme._datethyme import Time
from datethyme._null import NONE_TIME, NoneTime


class TestNoneTime:
    nt = NONE_TIME
    time2030 = Time.parse("20:30")

    def test_dunder_init(self):
        assert NoneTime() == self.nt

    def test_dunder_add(self):
        assert (self.nt + self.time2030) == self.nt

    def test_dunder_bool(self):
        assert not self.nt
        assert not bool(self.nt)

    def test_dunder_eq(self):
        assert self.nt == self.nt
        assert self.nt != self.time2030

    def test_dunder_ge(self):
        assert not (self.nt >= self.time2030)

    def test_dunder_gt(self):
        assert not (self.nt > self.time2030)

    def test_dunder_le(self):
        assert not (self.nt <= self.time2030)

    def test_dunder_lt(self):
        assert not (self.nt < self.time2030)

    def test_dunder_repr(self):
        assert repr(self.nt) == "NoneDate"

    def test_dunder_str(self):
        assert str(self.nt) == "NoneDate"

    def test_dunder_sub(self):
        assert (self.nt - self.time2030) is None
        assert (self.nt - 33) == self.nt
