from operator import attrgetter

from datethyme import Time
from datethyme.scheduling.types import DateTimePartition, Entries, Entry

agenda = DateTimePartition.from_starts(
    # start_name="sleep",
    spans={
        Time.parse("05:30"): "morning routine",
        Time.parse("06:30"): "gym",
        Time.parse("07:15"): "work (morning)",
        Time.parse("12:00"): "lunch",
        Time.parse("13:00"): "work (afternoon)",
        Time.parse("16:15"): "chores",
        Time.parse("17:30"): "dinner",
        Time.parse("18:30"): "programming",
        Time.parse("20:30"): "evening routine",
        Time.parse("22:30"): "sleep",
    },
    end=Time.parse("24:00"),
)

morning_routine = Entries((
    Entry("wake up", 1),
    Entry("get dressed", 5),
    Entry("workout", 10),
    Entry("shower", 15),
))

evening_routine = Entries((
    Entry("clean up", 5),
    Entry("walk", 10),
    Entry("change clothes", 1),
    Entry("reading", 30, ideal_time=60),
))

chore_backlog = Entries((
    Entry("a", 5),
    Entry("b", 10, ideal_time=20),
    Entry("c", 15, min_time=10),
    Entry("d", 30),
))

agenda = agenda.partition_element(
    "morning routine",
    morning_routine,
    min_length=1,
    max_length=20,
).partition_element(
    "evening routine",
    evening_routine,
    min_length=5,
    max_length=60,
)

agenda, leftover_chores = agenda.pack_from(  # type: ignore TODO
    "chores",
    chore_backlog,
    prefer_compress=False,
    min_callback=attrgetter("default"),
    max_callback=attrgetter("maximum"),
)

print(agenda)
print(leftover_chores)
