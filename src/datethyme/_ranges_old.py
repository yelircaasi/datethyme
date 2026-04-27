from __future__ import annotations

from collections.abc import Iterator
from typing import Self, overload

from multipledispatch import dispatch

from ._abcs import AbstractRange
from .constants import Unit
from .core import DateTime, Time
from .utils import index_getter


class HourRange(AbstractRange[Time]):
    """
    Sequence of hours, behaving roughly analogously to the built-in range object.

    Example: ```
    time0 = Time.parse("05:00")
    time0 = Time.parse("14:00")
    hours: TimeHourRange = time0 ** time1
    ```
    """

    def __init__(
        self,
        start: Time,
        stop: Time,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = start

    @property
    def last(self) -> Time:
        return self.stop  # TODO

    @property
    def seconds_per_step(self) -> int:
        return self.step * Unit.HOUR.seconds

    def __contains__(self, other: Time) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @overload
    def __getitem__(self, idx: int) -> Time: ...
    @overload
    def __getitem__(self, idx: slice) -> HourRange: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __reversed__(self) -> Self:
        return self

    def _increment(self) -> None:
        self._current, _ = self._current.add_hours_wraparound(1)

    def _increment_bounded(self) -> None:
        self._current = self._current.add_hours_bounded(1)


class HourRangeDated(AbstractRange[DateTime]):
    """ """

    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    @property
    def last(self) -> DateTime:
        return self.stop  # TODO

    @property
    def seconds_per_step(self) -> int:
        return self.step * Unit.HOUR.seconds

    def __contains__(self, other: DateTime) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @overload
    def __getitem__(self, idx: int) -> DateTime: ...
    @overload
    def __getitem__(self, idx: slice) -> HourRangeDated: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __reversed__(self) -> Self:
        return self

    def _increment(self) -> None:
        self._current = self._current.add_hours(1)


class MinuteRange(AbstractRange[Time]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def last(self) -> Time:
        return self.stop  # TODO

    @property
    def seconds_per_step(self) -> int:
        return self.step * 60

    def __contains__(self, other: Time) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @overload
    def __getitem__(self, idx: int) -> Time: ...
    @overload
    def __getitem__(self, idx: slice) -> MinuteRange: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return int(item in self)

    def _increment(self) -> None:
        self._current, _ = self._current.add_minutes_wraparound(self.step)

    def _increment_bounded(self) -> None:
        self._current = self._current.add_minutes_bounded(self.step)


class MinuteRangeDated(AbstractRange[DateTime]):
    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    @property
    def last(self) -> DateTime:
        return self.stop  # TODO

    @property
    def seconds_per_step(self) -> int:
        return self.step * 60

    def __contains__(self, other: DateTime) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @dispatch(int)
    def OLD__getitem__(self, idx: int) -> DateTime:  # pyright: ignore
        if not isinstance(idx, int):
            return TypeError(f"list indices must be integers or slices, not {type(idx)}")

        length = len(self)
        if not (-length <= idx < length):
            raise IndexError(f"{self.__class__.__name__} index out of range")

        return self.start.add_seconds(idx * self.step)

    @dispatch(slice)
    def OLD__getitem__(self, slc: slice, inclusive: bool = True) -> MinuteRangeDated:
        """
        Attention! The step in the slice, if provided, is with respect to the
          pre-existing step in `self`. This is accordance with the behavior of
          Python's built-in range().
        """
        start, stop, _step = slc.indices(len(self))
        return MinuteRangeDated(
            start=self[start],  # pyright: ignore
            stop=self[stop - int(inclusive)],  # pyright: ignore
            step=self.step * slc.step,
        )

    @overload
    def __getitem__(self, idx: int) -> DateTime: ...
    @overload
    def __getitem__(self, idx: slice) -> MinuteRangeDated: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return int(item in self)

    def _increment(self) -> None:
        self._current = self._current.add_minutes(self.step)


class SecondRange(AbstractRange[Time]):
    def __init__(
        self,
        start: Time,
        stop: Time,
        step: int = 1,
        inclusive: bool = False,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def seconds_per_step(self) -> int:
        return self.step

    @property
    def last(self) -> Time:
        return self.stop  # TODO

    def __contains__(self, other: Time) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @overload
    def __getitem__(self, idx: int) -> Time: ...
    @overload
    def __getitem__(self, idx: slice) -> SecondRange: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __reversed__(self) -> Self:
        return self

    def count(self, item: Time) -> int:
        return int(item in self)

    def _increment(self) -> None:
        self._current, _ = self._current.add_seconds_wraparound(self.step)  # TODO

    def _increment_bounded(self) -> None:
        self._current = self._current.add_seconds_bounded(1)


class SecondRangeDated(AbstractRange[DateTime]):
    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive

    @property
    def last(self) -> DateTime:
        rem = self._rem
        if rem == 0:
            return self.stop.add_seconds(-(not self.inclusive))
        return self.stop.add_seconds(-rem)

    @property
    def seconds_per_step(self) -> int:
        return self.step

    def __contains__(self, other: DateTime) -> bool:
        return (
            (self.start < other)
            and (self._limit > other)
            and (self.start.seconds_to(other) % self.step == 0)
        )

    def __len__(self) -> int:
        return round(self.start.seconds_to(self.last) % self.step) + 1

    @dispatch(int)
    def OLD__getitem__(self, idx: int) -> DateTime:  # pyright: ignore
        if not isinstance(idx, int):
            return TypeError(f"list indices must be integers or slices, not {type(idx)}")

        length = len(self)
        if not (-length <= idx < length):
            raise IndexError(f"{self.__class__.__name__} index out of range")

        return self.start.add_seconds(idx * self.step)

    @dispatch(slice)
    def OLD__getitem__(
        self, slc: slice, inclusive: bool = True, allow_wraparound: bool = True
    ) -> SecondRangeDated:  # pyright: ignore
        """
        Attention! The step in the slice, if provided, is with respect to the
          pre-existing step in `self`. This is accordance with the behavior of
          Python's built-in range().
        """
        start, stop, _step = slc.indices(len(self))
        return SecondRangeDated(
            start=self[start],  # pyright: ignore
            stop=self[stop - int(inclusive)],  # pyright: ignore
            step=self.step * slc.step,
        )

    @overload
    def __getitem__(self, idx: int) -> DateTime: ...
    @overload
    def __getitem__(self, idx: slice) -> SecondRangeDated: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __iter__(self) -> Iterator[DateTime]:
        return iter(self)

    def __reversed__(self) -> SecondRangeDated:
        raise NotImplementedError  # TODO

    @property
    def _limit(self) -> DateTime:
        return self.stop.add_seconds(self._rem * (int(self.inclusive) - 0.5))

    @property
    def _rem(self) -> float:
        return round(self.start.seconds_to(self.stop) % self.step, 10)

    def _increment(self) -> None:
        self._current = self._current.add_seconds(self.step)


class DayRangeDated(AbstractRange[DateTime]):
    """ """

    def __init__(
        self,
        start: DateTime,
        stop: DateTime,
        step: int = 1,
        inclusive: bool = True,
        allow_wraparound: bool = True,
    ):
        self.start = start
        self.stop = stop
        self.step = step
        self.inclusive = inclusive
        self._current = self.start

    @property
    def last(self) -> DateTime:
        return self.stop  # TODO

    @property
    def seconds_per_step(self) -> int:
        return self.step * Unit.DAY.seconds

    def __contains__(self, other: DateTime) -> bool:
        return False  # TODO

    def __len__(self) -> int:
        return 999  # TODO

    @overload
    def __getitem__(self, idx: int) -> DateTime: ...
    @overload
    def __getitem__(self, idx: slice) -> DayRangeDated: ...
    def __getitem__(self, idx: int | slice) -> object:
        return index_getter(self, idx)

    def __reversed__(self) -> Self:
        return self

    def count(self, item: DateTime) -> int:
        return int(item in self)

    def _increment(self) -> None:
        self._current = self._current.add_days(1)
