from operator import attrgetter

from datethyme import (
    DateRange,
    DateTimeSpan,
    HourRange,
    HourRangeDated,
    MinuteRange,
    MinuteRangeDated,
    SecondRange,
    SecondRangeDated,
    TimeSpan,
)
from datethyme.core import DateTimeRange, TimeRange
from datethyme.protocols import (
    EntryProtocol,
    PartitionProtocol,
    RangeProtocol,
    SpanProtocol,
    TimeBlockProtocol,
)
from datethyme.scheduling import DateTimePartition, TimePartition, make_entry_adapter
from datethyme.scheduling.types import (
    Calendar,
    CalendarDay,
    DayPartition,
    EmptyBlock,
    FixedBlock,
    FlexBlock,
    ScheduledEntry,
)


def test_entryprotocol_conformity() -> None:
    assert isinstance(ScheduledEntry, EntryProtocol)

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


def test_rangeprotocol_conformity() -> None:
    assert isinstance(DateRange, RangeProtocol)
    assert isinstance(TimeRange, RangeProtocol)
    assert isinstance(DateTimeRange, RangeProtocol)
    assert isinstance(SecondRange, RangeProtocol)
    assert isinstance(MinuteRange, RangeProtocol)
    assert isinstance(HourRange, RangeProtocol)
    assert isinstance(SecondRangeDated, RangeProtocol)
    assert isinstance(MinuteRangeDated, RangeProtocol)
    assert isinstance(HourRangeDated, RangeProtocol)


def test_spanprotocol_conformity() -> None:
    assert isinstance(TimeSpan, SpanProtocol)
    assert isinstance(DateTimeSpan, SpanProtocol)
    assert isinstance(FixedBlock, SpanProtocol)
    assert isinstance(FlexBlock, SpanProtocol)
    assert isinstance(EmptyBlock, SpanProtocol)


def test_timeblockprotocol_conformity() -> None:
    assert isinstance(FixedBlock, TimeBlockProtocol)
    assert isinstance(FlexBlock, TimeBlockProtocol)
    assert isinstance(EmptyBlock, TimeBlockProtocol)


def test_partitionprotocol_conformity() -> None:
    assert isinstance(TimePartition, PartitionProtocol)
    assert isinstance(DateTimePartition, PartitionProtocol)
    assert isinstance(DayPartition, PartitionProtocol)
    assert isinstance(CalendarDay, PartitionProtocol)
    assert isinstance(Calendar, PartitionProtocol)
