from datethyme._datethyme import DateTime
from datethyme._null import NONE_DATETIME, NoneDateTime


class TestNoneDateTime:
    ndt = NONE_DATETIME
    dt = DateTime.parse("2012-12-31__20:30")

    def test_dunder_init(self):
        assert NoneDateTime() == self.ndt

    def test_dunder_add(self):
        assert (self.ndt + self.dt) == self.ndt

    def test_dunder_bool(self):
        assert not self.ndt
        assert not bool(self.ndt)

    def test_dunder_eq(self):
        assert self.ndt == self.ndt
        assert self.ndt != self.dt

    def test_dunder_ge(self):
        assert not (self.ndt >= self.dt)

    def test_dunder_gt(self):
        assert not (self.ndt > self.dt)

    def test_dunder_le(self):
        assert not (self.ndt <= self.dt)

    def test_dunder_lt(self):
        assert not (self.ndt < self.dt)

    def test_dunder_repr(self):
        assert repr(self.ndt) == "NoneDate"

    def test_dunder_str(self):
        assert str(self.ndt) == "NoneDate"

    def test_dunder_sub(self):
        assert (self.ndt - self.dt) is None
        assert (self.ndt - 33) == self.ndt
