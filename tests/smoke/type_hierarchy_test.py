from operator import attrgetter

from datethyme import (
    Date,
    DateRange,
    DateTime,
    DateTimeSpan,
    HourRange,
    HourRangeDated,
    MinuteRange,
    MinuteRangeDated,
    SecondRange,
    SecondRangeDated,
    Time,
    TimeSpan,
)
from datethyme.constants import Unit
from datethyme.core import DateTimeRange, TimeRange
from datethyme.protocols import (
    AtomProtocol,
    EntryProtocol,
    PartitionProtocol,
    RangeProtocol,
    SpanProtocol,
    TimeBlockProtocol,
    TimeProtocol,
)
from datethyme.scheduling import DateTimePartition, Entries, TimePartition, make_entry_adapter
from datethyme.scheduling.types import (
    Calendar,
    CalendarDay,
    DayPartition,
    EmptyBlock,
    Entry,
    FixedBlock,
    FlexBlock,
)


def test_entryprotocol_conformity() -> None:
    assert isinstance(Entry, EntryProtocol)

    class ForeignEntry: ...

    EntryType = make_entry_adapter(
        get_name=attrgetter("PLACEHOLDER"),
        get_projects=attrgetter("PLACEHOLDER"),
        get_priority=attrgetter("PLACEHOLDER"),
        get_min_time=attrgetter("PLACEHOLDER"),
        get_normal_time=attrgetter("PLACEHOLDER"),
        get_ideal_time=attrgetter("PLACEHOLDER"),
        get_max_time=attrgetter("PLACEHOLDER"),
        get_contexts=attrgetter("PLACEHOLDER"),
        get_dependencies=attrgetter("PLACEHOLDER"),
        get_due_date=attrgetter("PLACEHOLDER"),
        get_earliest_date=attrgetter("PLACEHOLDER"),
    )
    foreign = ForeignEntry()
    assert isinstance(EntryType(foreign), EntryProtocol)


class TestProtocols:
    date = Date(year=2025, month=10, day=30)
    time = Time(hour=12, minute=30)
    datetime = DateTime(year=2025, month=10, day=30, hour=12, minute=30)
    daterange = DateRange(Date(year=2025, month=10, day=30), Date(year=2025, month=11, day=15))
    timerange = TimeRange(
        Time(hour=12, minute=30),
        Time(hour=15, minute=30),
        unit=Unit.HOUR,
    )
    datetimerange = DateTimeRange(
        DateTime(year=2025, month=10, day=30, hour=12, minute=30),
        DateTime(year=2025, month=11, day=20, hour=12, minute=30),
        unit=Unit.HOUR,
    )
    secondrange = SecondRange(
        Time(hour=12, minute=30),
        Time(hour=15, minute=30),
    )
    minuterange = MinuteRange(
        Time(hour=12, minute=30),
        Time(hour=15, minute=30),
    )
    hourrange = HourRange(
        Time(hour=12, minute=30),
        Time(hour=15, minute=30),
    )
    secondrangedated = SecondRangeDated(
        DateTime(year=2025, month=10, day=30, hour=12, minute=30),
        DateTime(year=2025, month=11, day=20, hour=12, minute=30),
    )
    minuterangedated = MinuteRangeDated(
        DateTime(year=2025, month=10, day=30, hour=12, minute=30),
        DateTime(year=2025, month=11, day=20, hour=12, minute=30),
    )
    hourrangedated = HourRangeDated(
        DateTime(year=2025, month=10, day=30, hour=12, minute=30),
        DateTime(year=2025, month=11, day=20, hour=12, minute=30),
    )
    timespan = TimeSpan(
        Time(hour=12, minute=30),
        Time(hour=15, minute=30),
    )
    datetimespan = DateTimeSpan(
        DateTime(year=2025, month=10, day=30, hour=12, minute=30),
        DateTime(year=2025, month=11, day=20, hour=12, minute=30),
    )
    fixedblock = FixedBlock(
        start=Time(hour=12, minute=30),
        end=Time(hour=15, minute=30),
    )
    flexblock = FlexBlock(
        start=Time(hour=12, minute=30),
        end=Time(hour=15, minute=30),
    )
    emptyblock = EmptyBlock(
        start=Time(hour=12, minute=30),
        end=Time(hour=15, minute=30),
    )
    timepartition = TimePartition(spans=[])
    datetimepartition = DateTimePartition(spans=[])
    daypartition = DayPartition(fixed=[])
    calendarday = CalendarDay(schedule=DayPartition(fixed=[]), entries=Entries([]))
    calendar = Calendar()

    def test_atomprotocol_conformity(self) -> None:
        assert isinstance(self.date, AtomProtocol)
        assert isinstance(self.time, AtomProtocol)
        assert isinstance(self.datetime, AtomProtocol)

    def test_timeprotocol_conformity(self) -> None:
        assert isinstance(self.time, TimeProtocol)
        assert isinstance(self.datetime, TimeProtocol)

    def test_rangeprotocol_conformity(self) -> None:
        assert isinstance(self.daterange, RangeProtocol)
        assert isinstance(self.timerange, RangeProtocol)
        assert isinstance(self.datetimerange, RangeProtocol)
        assert isinstance(self.secondrange, RangeProtocol)
        assert isinstance(self.minuterange, RangeProtocol)
        assert isinstance(self.hourrange, RangeProtocol)
        assert isinstance(self.secondrangedated, RangeProtocol)
        assert isinstance(self.minuterangedated, RangeProtocol)
        assert isinstance(self.hourrangedated, RangeProtocol)

    def test_spanprotocol_conformity(self) -> None:
        assert isinstance(self.timespan, SpanProtocol)
        assert isinstance(self.datetimespan, SpanProtocol)
        assert isinstance(self.fixedblock, SpanProtocol)
        assert isinstance(self.flexblock, SpanProtocol)
        assert isinstance(self.emptyblock, SpanProtocol)

    def test_timeblockprotocol_conformity(self) -> None:
        assert isinstance(self.fixedblock, TimeBlockProtocol)
        assert isinstance(self.flexblock, TimeBlockProtocol)
        assert isinstance(self.emptyblock, TimeBlockProtocol)

    def test_partitionprotocol_conformity(self) -> None:
        assert isinstance(self.timepartition, PartitionProtocol)
        assert isinstance(self.datetimepartition, PartitionProtocol)
        assert isinstance(self.daypartition, PartitionProtocol)
        # assert isinstance(self.calendarday, PartitionProtocol)
        # assert isinstance(self.calendar, PartitionProtocol)
