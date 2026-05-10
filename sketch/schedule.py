from operator import attrgetter
from pathlib import Path

from datethyme import Date
from datethyme.scheduling import (
    Calendar,
    SchedulingLog,
    make_entry_adapter,
    # Entry,
)

# from consilium.notes import (
#     Notes,
#     get_next_tasks,  # type: ignore
#     get_note_paths,  # type: ignore
# )
from datethyme.scheduling.types.schedules import (  # type: ignore
    ContextHierarchy,
    Recurring,
    Routines,
    # get_planning_paths,
)

# npaths = get_note_paths()
# ppaths = get_planning_paths()

# tasks: Notes = get_next_tasks(n=200)

# =================== SIMPLIFIED FROM consilium.notes to retain interface ==++=


class PPaths:
    calendar: Path = Path("/home/isaac/repos/datethyme-1/sketch/calendar/calendar.json")
    output: Path = Path("/home/isaac/repos/datethyme-1/sketch/output.tex")
    routines: Path = Path("/home/isaac/repos/datethyme-1/sketch/routines.json")
    recurring: Path = Path("/home/isaac/repos/datethyme-1/sketch/recurring.json")
    context_hierarchy: Path = Path("/home/isaac/repos/datethyme-1/sketch/context-hierarchy.json")


ppaths = PPaths()

# class NPaths:


# =============================================================================


logs: list[SchedulingLog] = []
Entry = make_entry_adapter(
    get_name=attrgetter("id"),
    get_projects=attrgetter("projects"),
    get_priority=attrgetter("task.priority"),
    get_min_time=attrgetter("task.minTime"),
    get_normal_time=attrgetter("task.normalTime"),
    get_ideal_time=attrgetter("task.idealTime"),
    get_max_time=attrgetter("task.maxTime"),
    get_contexts=attrgetter("task.contexts"),
    get_dependencies=attrgetter("task.dependencies"),
    get_due_date=attrgetter("task.dateDue"),
    get_earliest_date=attrgetter("task.dateEarliest"),
)
candidate_entries = []  # list(map(Entry, tasks.values()))


calendar = Calendar.read_json_file(ppaths.calendar, start=Date.today(), ndays=30)
routines = Routines.read_json_file(ppaths.routines)
recurring = Recurring.read_json_file(ppaths.recurring)
context_hierarchy = ContextHierarchy.read_json_file(ppaths.context_hierarchy)


calendar, remaining_entries, logs = calendar.create_schedule(
    recurring=recurring,
    routines=routines,
    entries=candidate_entries,
    context_hierarchy=context_hierarchy,
)


latex_calendar: str = calendar.export_latex(style="compact")
ppaths.output.write_text(latex_calendar)
