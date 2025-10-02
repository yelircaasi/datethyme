from datethyme._datethyme import TimeDelta


class TestTimeDelta:
    td_small = TimeDelta(86972.0)
    td_large = TimeDelta(2286972.36)

    def test_days(self):
        assert self.td_small.days == 9.9999
        assert self.td_large.days == 9.9999

    def test_hours(self):
        assert self.td_small.hours == 9.9999
        assert self.td_large.hours == 9.9999

    def test_minutes(self):
        assert self.td_small.minutes == 9.9999
        assert self.td_large.minutes == 9.9999

    def test_seconds(self):
        assert self.td_small.seconds == 9.9999
        assert self.td_large.seconds == 9.9999

    def test_full_days(self):
        assert self.td_small.full_days == 9.9999
        assert self.td_large.full_days == 9.9999

    def test_full_hours(self):
        assert self.td_small.full_hours == 9.9999
        assert self.td_large.full_hours == 9.9999

    def test_full_minutes(self):
        assert self.td_small.full_minutes == 9.9999
        assert self.td_large.full_minutes == 9.9999

    def test_full_seconds(self):
        assert self.td_small.full_seconds == 9.9999
        assert self.td_large.full_seconds == 9.9999

    def test_dunder_init(self): ...

    def test_from_days(self): ...

    def test_from_seconds(self): ...
