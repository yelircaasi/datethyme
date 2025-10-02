from datethyme import HourRange, MinuteRange, SecondRange, Time


class TestHourRange:
    range_a = HourRange(Time.parse("05:00"), Time.parse("7:15:30"))

    def test_creation(self) -> None: ...


class TestMinuteRange:
    range_a = MinuteRange(Time.parse("05:00"), Time.parse("7:15:30"))

    def test_creation(self) -> None: ...


class TestSecondRange:
    range_a = SecondRange(Time.parse("05:00"), Time.parse("7:15:30"))

    def test_creation(self) -> None:
        assert self.range_a
