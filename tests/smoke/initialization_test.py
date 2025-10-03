from datethyme import (
    # DATE_REGEX,
    # DATE_REGEX_STRICT,
    # DATE_TIME_REGEX,
    Date,
    DateRange,
    DateTime,
    DateTimePartition,
    DateTimeSpan,
    # DateTimeValidationError,
    # DateValidationError,
    DayRangeDated,
    HourRange,
    HourRangeDated,
    MinuteRange,
    MinuteRangeDated,
    # NONE_DATE,
    # NONE_DATETIME,
    # NONE_TIME,
    NoneDate,
    NoneDateTime,
    NoneTime,
    # OptionalDate,
    # OptionalDateTime,
    # OptionalTime,
    SecondRange,
    SecondRangeDated,
    Time,
    TimeDelta,
    TimePartition,
    TimeSpan,
    # TimeValidationError,
    # utils,
)

nonedate = NoneDate()
nonedatetime = NoneDateTime()
nonetime = NoneTime()

timedelta = TimeDelta(533.5)

date = Date(year=2050, month=12, day=3)
time = Time(hour=15, minute=15, second=30)
datetime = DateTime(year=2050, month=12, day=3, hour=15, minute=15, second=30)

daterange = DateRange(start=date, stop=date + 30)
hourrange = HourRange(start=time, stop=time.add_hours_bounded(5))
minuterange = MinuteRange(start=time, stop=time.add_hours_bounded(2))
secondrange = SecondRange(start=time, stop=time.add_hours_bounded(0.5))

dayrangedated = DayRangeDated(start=datetime, stop=datetime.add_days(3))
hourrangedated = HourRangeDated(start=datetime, stop=datetime.add_days(3))
minuterangedated = MinuteRangeDated(start=datetime, stop=datetime.add_days(3))
secondrangedated = SecondRangeDated(start=datetime, stop=datetime.add_days(3))

timespan = TimeSpan(start=time, end=time.add_hours_bounded(2))
datetimespan = DateTimeSpan(start=datetime, end=datetime.add_hours(2))

timepartition = TimePartition(
    (
        TimeSpan(start=time, end=time.add_hours_bounded(2)),
        TimeSpan(start=time.add_hours_bounded(2), end=time.add_hours_bounded(4)),
        TimeSpan(start=time.add_hours_bounded(4), end=time.add_hours_bounded(6)),
        TimeSpan(start=time.add_hours_bounded(6), end=time.add_hours_bounded(8)),
    )
)
datetimepartition = DateTimePartition(
    (
        DateTimeSpan(start=datetime, end=datetime.add_hours(2)),
        DateTimeSpan(start=datetime.add_hours(2), end=datetime.add_hours(4)),
        DateTimeSpan(start=datetime.add_hours(4), end=datetime.add_hours(6)),
        DateTimeSpan(start=datetime.add_hours(6), end=datetime.add_hours(8)),
    )
)


def test_basic_initialization():
    assert isinstance(date, Date)
    assert isinstance(daterange, DateRange)
    assert isinstance(datetime, DateTime)
    assert isinstance(datetimepartition, DateTimePartition)
    assert isinstance(datetimespan, DateTimeSpan)
    assert isinstance(dayrangedated, DayRangeDated)
    assert isinstance(hourrange, HourRange)
    assert isinstance(hourrangedated, HourRangeDated)
    assert isinstance(minuterange, MinuteRange)
    assert isinstance(minuterangedated, MinuteRangeDated)
    assert isinstance(nonedate, NoneDate)
    assert isinstance(nonedatetime, NoneDateTime)
    assert isinstance(nonetime, NoneTime)
    assert isinstance(secondrange, SecondRange)
    assert isinstance(secondrangedated, SecondRangeDated)
    assert isinstance(time, Time)
    assert isinstance(timedelta, TimeDelta)
    assert isinstance(timepartition, TimePartition)
    assert isinstance(timespan, TimeSpan)
