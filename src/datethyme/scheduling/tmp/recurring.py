from __future__ import annotations

from adiumentum.pydantic import BaseList
from datethyme import Date
from pydantic import BaseModel, Field


class RecurringTask(BaseModel):
    id: str
    name: str
    frequency: int
    last: Date
    contexts: set[str] = Field(default_factory=set)
    routines: set[str] = Field(default_factory=set)
    description: str = Field(default="")
    duration: int | tuple[int, int, int] | tuple[int, int, int, int] = Field(
        default=(10, 30, 40, 60)
    )

    def _duration_by_index(self, idx: int) -> int:
        if isinstance(self.duration, int):
            return self.duration
        return self.duration[idx]

    @property
    def duration_repr(self) -> str:
        if isinstance(self.duration, int):
            return str(self.duration)
        return f"{self.minTime}..{self.normalTime}(*{self.idealTime})..{self.maxTime}"

    @property
    def normalTime(self) -> int:
        return self._duration_by_index(1)

    @property
    def minTime(self) -> int:
        return self._duration_by_index(0)

    @property
    def maxTime(self) -> int:
        return self._duration_by_index(-1)

    @property
    def idealTime(self) -> int:
        return self._duration_by_index(-2)

    @property
    def due_date(self) -> Date:
        return self.last + self.frequency

    def is_due(self, date: Date = Date.today()) -> bool:
        return (date - self.last) > self.frequency

    def __str__(self) -> str:
        return (
            f"DUE: {self.due_date}  |  {self.name:<20} |{self.frequency:>2}"
            f"|  last done: {self.last}  |  {self.duration_repr}"
        )


class RecurringTasks(BaseList[RecurringTask]):
    def get_due(self, date: Date | None = None) -> RecurringTasks:
        date = date or Date.today()

        def is_due_(task: RecurringTask) -> bool:
            return task.is_due(date)

        return self.__class__.model_validate(filter(is_due_, self))

    def get_not_due(self, date: Date | None = None) -> RecurringTasks:
        date = date or Date.today()

        def not_due(task: RecurringTask) -> bool:
            return not task.is_due(date)

        return self.__class__.model_validate(filter(not_due, self))

    def by_context(self, ctx: str) -> RecurringTasks:
        return self.__class__.model_validate(filter(lambda x: ctx in x.contexts, self))

    def by_routine(self, routine: str) -> RecurringTasks:
        return self.__class__.model_validate(filter(lambda x: routine in x.routines, self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}\n  {'\n  '.join(sorted(map(str, self)))}"
