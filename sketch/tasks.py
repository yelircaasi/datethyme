
from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel, Field
from adiumentum.pydantic import BaseList
from datethyme import Date




class RecurringTask(BaseModel):
    id: str
    name: str
    frequency: int
    last: Date
    contexts: set[str] = Field(default_factory=set)
    routines: set[str] = Field(default_factory=set)
    description: str = Field(default="")
    
    @property
    def due_date(self) -> Date:
        return self.last + self.frequency

    def is_due(self, date: Date = Date.today()) -> bool:
        return (date - self.last) > self.frequency 
    
    def __str__(self) -> str:
        return f"DUE: {self.due_date}  |  {self.name:<20} [{self.frequency:>2}]  last done on: {self.last}"



class RecurringTasks(BaseList[RecurringTask]):
    def get_due(self, date: Date | None = None) -> RecurringTasks:
        date = date or Date.today()

        def is_due_(task: RecurringTask) -> bool:
            return task.is_due(date)            

        return self.__class__(filter(is_due_, self))
    
    def by_context(self, ctx: str) -> RecurringTasks:
        return self.__class__(filter(lambda x: ctx in x.contexts, self))

    def by_routine(self, routine: str) -> RecurringTasks:
        return self.__class__(filter(lambda x: routine in x.routines, self))
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}\n  {'\n  '.join(sorted(map(str, self)))}"


t = """

"""

recurring_tasks_path = Path("/home/isaac/repos/datethyme-1/sketch/recurring.json")

rectasks = RecurringTasks.read_json_file(recurring_tasks_path)
due = rectasks.get_due()

print(due)

# TODO: use terminal menu library from old consilium-notes / apiarium