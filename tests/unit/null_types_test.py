from datethyme import Date, DateTime, Time
from datethyme.null import NONE_DATE, NONE_DATETIME, NONE_TIME, NoneDate, NoneDateTime, NoneTime


class TestNoneDate:
    nd = NONE_DATE
    xmas = Date.parse("2031-12-31")

    def test_dunder_init(self) -> None:
        assert NoneDate() == self.nd

    def test_hash(self) -> None:
        assert isinstance(hash(NONE_DATE), int)

    def test_dunder_add(self) -> None:
        assert (self.nd + self.xmas) == self.nd

    def test_dunder_bool(self) -> None:
        assert not self.nd
        assert not bool(self.nd)

    def test_dunder_eq(self) -> None:
        assert self.nd == self.nd
        assert self.nd != self.xmas

    def test_dunder_ge(self) -> None:
        assert not (self.nd >= self.xmas)

    def test_dunder_gt(self) -> None:
        assert not (self.nd > self.xmas)

    def test_dunder_le(self) -> None:
        assert not (self.nd <= self.xmas)

    def test_dunder_lt(self) -> None:
        assert not (self.nd < self.xmas)

    def test_dunder_repr(self) -> None:
        assert repr(self.nd) == "NoneDate"

    def test_dunder_str(self) -> None:
        assert str(self.nd) == "NoneDate"

    def test_dunder_sub(self) -> None:
        assert (self.nd - self.xmas) is None
        assert (self.nd - 33) == self.nd


class TestNoneTime:
    nt = NONE_TIME
    time2030 = Time.parse("20:30")

    def test_dunder_init(self) -> None:
        assert NoneTime() == self.nt

    def test_hash(self) -> None:
        assert isinstance(hash(NONE_TIME), int)

    def test_dunder_add(self) -> None:
        assert (self.nt + self.time2030) == self.nt

    def test_dunder_bool(self) -> None:
        assert not self.nt
        assert not bool(self.nt)

    def test_dunder_eq(self) -> None:
        assert self.nt == self.nt
        assert self.nt != self.time2030

    def test_dunder_ge(self) -> None:
        assert not (self.nt >= self.time2030)

    def test_dunder_gt(self) -> None:
        assert not (self.nt > self.time2030)

    def test_dunder_le(self) -> None:
        assert not (self.nt <= self.time2030)

    def test_dunder_lt(self) -> None:
        assert not (self.nt < self.time2030)

    def test_dunder_repr(self) -> None:
        assert repr(self.nt) == "NoneDate"

    def test_dunder_str(self) -> None:
        assert str(self.nt) == "NoneDate"

    def test_dunder_sub(self) -> None:
        assert (self.nt - self.time2030) is None
        assert (self.nt - 33) == self.nt


class TestNoneDateTime:
    ndt = NONE_DATETIME
    dt = DateTime.parse("2012-12-31__20:30")

    def test_dunder_init(self) -> None:
        assert NoneDateTime() == self.ndt

    def test_hash(self) -> None:
        assert isinstance(hash(NONE_DATETIME), int)

    def test_dunder_add(self) -> None:
        assert (self.ndt + self.dt) == self.ndt

    def test_dunder_bool(self) -> None:
        assert not self.ndt
        assert not bool(self.ndt)

    def test_dunder_eq(self) -> None:
        assert self.ndt == self.ndt
        assert self.ndt != self.dt

    def test_dunder_ge(self) -> None:
        assert not (self.ndt >= self.dt)

    def test_dunder_gt(self) -> None:
        assert not (self.ndt > self.dt)

    def test_dunder_le(self) -> None:
        assert not (self.ndt <= self.dt)

    def test_dunder_lt(self) -> None:
        assert not (self.ndt < self.dt)

    def test_dunder_repr(self) -> None:
        assert repr(self.ndt) == "NoneDate"

    def test_dunder_str(self) -> None:
        assert str(self.ndt) == "NoneDate"

    def test_dunder_sub(self) -> None:
        assert (self.ndt - self.dt) is None
        assert (self.ndt - 33) == self.ndt
