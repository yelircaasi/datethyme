from collections import defaultdict
from operator import attrgetter
from datethyme import Date, DateTimePartition, DeltaSequence, TimePartition, Time
from datethyme._scheduling import Item, ItemSequence

agenda: DateTimePartition = Date.parse("2025-10-10").partition(
    start_name="sleep",
    events={
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
)

morning_routine = ItemSequence((
    Item("wake up", 1),
    Item("get dressed", 5),
    Item("workout", 10),
    Item("shower", 15),
))

evening_routine = ItemSequence((
    Item("clean up", 5),
    Item("walk", 10),
    Item("change clothes", 1),
    Item("reading", 30, ideal=60),
))

chore_backlog = ItemSequence((
    Item("a", 5),
    Item("b", 10, ideal=20),
    Item("c", 15, minimum=10),
    Item("d", 30),
))

agenda = agenda.partition_element(
    "morning routine",
    morning_routine,
    item_min=1,
    item_max=20,
).partition_element(
    "evening routine",
    evening_routine,
    item_min=5,
    item_max=60,
)

agenda, leftover_chores = agenda.pack_from(
    "chores",
    chore_backlog,
    prefer_compress=False,
    min_callback=attrgetter("default"),
    max_callback=attrgetter("maximum"),
)

print(agenda)
print(leftover_chores)
