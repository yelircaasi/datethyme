from collections.abc import Iterable
from itertools import pairwise
from typing import Self, TypeVar, Union

from ._datethyme import AbstractPartition, AbstractSpan, Date, DateRange, DateTime, DateTimeSpan, Time, TimeSpan

# ==============================================================================================================







# ==============================================================================================================

NestedSpan = Union[TimeSpan, "TimePartition"]

S = TypeVar("S")
T = TypeVar("T", bound=Time | DateTime | Date)


class TimePartition(AbstractPartition[Time]):
    """
    A contiguous sequence of TimeSpan objects or TimePartition objects (recursive),
      useful for scheduling.

    intuitively:
        resolve_overlaps(seq, mode=EQUAL|PROPORTIONAL|INVERSE|ECLIPSE|SHIFT)
        resolve_gaps(seq, mode=EQUAL|PROPORTIONAL|INVERSE|SNAP_FORWARD|SNAP_BACK|SHIFT_FORWARD|
          SHIFT_BACK)
        squeeze(seq, mode=PROPORTIONAL|EQUAL, earliest=None, latest=None)
        stack(seq, mode=forward|middle|backward, anchor=None)
        truncate(seq, earliest: Time, latest: Time)

        truncate_preserve -> return (before, truncated, after)

    both can be procrustean or not

    """

    @property
    def passes_day_boundary(self) -> bool: ...

    def __str__(self):
        return "[TODO] "  # {repr(self)}"

    def __repr__(self):
        for level, event in self.iter_nested():
            indent = " " * level
            print(f"{indent:<12} {event.start} — {event.name.title()}")

        def format_span(span: TimeSpan):
            return f"{span.start} - {span.name}"

        return f"TimePartition(\n    {'\n    '.join(map(format_span, self.spans))}\n    {self.end} - <END>\n)"

    @classmethod
    def from_times(cls, times: Iterable[Time], names: Iterable[str] | None = None):
        n_spans = len(times := tuple(times)) - 1
        if names is None:
            names = (None,) * n_spans
        if not len(names := tuple(names)) == n_spans:
            return ValueError
        return cls.__init__(
            spans=(
                TimeSpan(start=a, end=b, name=name) for (a, b), name in zip(pairwise(times), names)
            )
        )


# DEV ONLY ------------------------------------------------------------------------------------------------
# class DateTimePartition():
class DateTimePartition(AbstractPartition[DateTime]):
    # spans: Iterable[AbstractSpan[DateTime]]
    # def __init__(self, spans, names: Iterable[str] | None = None):
    #     self._spans = tuple(spans)
    #     self._names = tuple(names) if names else names

    # @property
    # def ends(self):
    #     return tuple(map(lambda t: t.end, self.spans))

    # @property
    # def end(self):
    #     return max(self.ends)
    # --------------------------------------------------------------------------------------------------------
    @classmethod
    def from_datetimes(cls, times: Iterable[DateTime], names: Iterable[str] | None = None) -> Self:
        n_spans = len(times := tuple(times)) - 1
        if names is None:
            names = (None,) * n_spans
        if not len(names := tuple(names)) == n_spans:
            return ValueError
        return cls(
            spans=(
                DateTimeSpan(start=a, end=b, name=name)
                for (a, b), name in zip(pairwise(times), names)
            )
        )

    @property
    def spans(self) -> tuple[DateTimeSpan]:
        return self._spans

    @property
    def passes_day_boundary(self) -> bool: ...

    @property
    def daterange(self) -> DateRange:
        return DateRange(
            start=self.start.date,
            stop=self.end.date,
        )

    def __str__(self):
        return "TODO: "  # {self}"

    def __repr__(self):
        # change _spans to spans later
        return f"TimePartition(\n    {'\n    '.join(map(self.format_span, self._spans))}\n    {self.end} - <END>\n)"

    # def repr_indented(self, span: AbstractPartition[DateTime], indent: int) -> str:
    #     prefix = indent * " "
    #     if isinstance(span, DateTimePartition):

    #     return ("\n" + (" " * indent)).join(map(partial(self.format_span, indent=indent), span))

    def format_span(self, span: DateTimeSpan | AbstractPartition[DateTime], indent: int = 0):
        prefix = indent * " "
        if isinstance(span, DateTimeSpan):
            return f"{prefix}{span.start} - {span.name}"
        elif isinstance(span, DateTimePartition):
            return repr(DateTimePartition).replace("\n", "\n" + prefix)
        raise ValueError


# dt0 = DateTime(year=2025, month=6, day=15, hour=16)
# dt1 = DateTime(year=2025, month=6, day=15, hour=17, minute=30)
# dt2 = DateTime(year=2025, month=6, day=15, hour=18, minute=45)
# dt3 = DateTime(year=2025, month=6, day=15, hour=19, minute=0)
# dt4 = DateTime(year=2025, month=6, day=15, hour=20, minute=15)
# dtp = DateTimePartition.from_datetimes((dt0, dt1, dt2, dt3, dt4))

# print(dtp)
# print(str(dtp))
# print(repr(dtp))


class SpanContainer[T]:
    def __init__(self, start: T, end: T, subpartition: Iterable[AbstractSpan[T]]) -> None:
        self.start: T = start
        self.end: T = end
        self.subpartition: tuple[AbstractSpan[T], ...] = tuple(subpartition)


class DatePartition: ...


class Item:
    def __init__(
        self,
        name: str,
        default: int | float,
        *,
        minimum: int | float | None = None,
        ideal: int | float | None = None,
        maximum: int | float | None = None,
    ):
        self.name = name
        self.default = default
        self.ideal = ideal or self.default
        self.minimum = min(default, minimum or default, self.ideal)
        self.maximum = max(default, maximum or default, self.ideal)

    def __repr__(self) -> str:
        return f"Item({self.minimum} ≤ {self.default} ≤ {self.maximum}, ideal={self.ideal})"

    def __str__(self) -> str:
        return f"Item({self.minimum} ≤ {self.default} ≤ {self.maximum}, ideal={self.ideal})"

    def rescaled(self, scale_factor: float) -> "Item":
        return Item(
            self.name,
            self.default * scale_factor,
            minimum=self.minimum * scale_factor,
            ideal=self.ideal * scale_factor,
            maximum=self.maximum * scale_factor,
        )


class ItemSequence(list[Item]):
    """ """

    def __init__(self, items: Iterable[Item]):
        items = list(items)
        if not len(set(items)) == len(items):
            raise ValueError("Item names must be unique.")
        super().__init__(items)

    @property
    def default(self) -> float:
        return sum(map(lambda it: it.default, self))

    @property
    def minimum(self) -> float:
        return sum(map(lambda it: it.minimum, self))

    @property
    def ideal(self) -> float:
        return sum(map(lambda it: it.ideal, self))

    @property
    def maximum(self) -> float:
        return sum(map(lambda it: it.maximum, self))

    def __repr__(self) -> str:
        return f"ItemSequence(\n    {'\n    '.join(map(repr, self))}\n)"

    def __str__(self) -> str:
        return f"ItemSequence(\n    {'\n    '.join(map(repr, self))}\n)"


# migrate Entry from consilium?
