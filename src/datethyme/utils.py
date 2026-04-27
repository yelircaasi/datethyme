from __future__ import annotations

import re
from collections.abc import Callable
from operator import le, lt
from typing import Literal, overload

import deal

from .exceptions import DateValidationError, TimeValidationError
from .protocols import AtomProtocol, RangeProtocol, SpanProtocol, TimeProtocol


def assert_xor(a: bool | object | str | None, b: bool | object | str | None) -> bool:
    if not (bool(a) ^ bool(b)):
        raise ValueError
    if a:
        return True
    return False


def transfer_case(reference: str, candidate: str) -> str:
    if reference.istitle():
        return candidate.title()
    if reference.islower():
        return candidate.lower()
    if reference.isupper():
        return candidate.upper()
    return candidate


DATE_REGEX: re.Pattern = re.compile(r"^([12]\d\d\d)-(0?\d|1[012])-(0?\d|[12]\d|3[01])$")
DATE_REGEX_STRICT: re.Pattern = re.compile(r"^([12]\d\d\d)-(0\d|1[012]|)-(0\d|[12]\d|3[01])$")
DATE_TIME_REGEX: re.Pattern = re.compile(r"^([12]\d\d\d-\d\d?-\d\d?)[^0-9]{1,4}([0-9:\.]+)$")

WeekdayLiteral = Literal[
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
]


@deal.has()
@deal.raises(DateValidationError)
def validate_date(raw_date: str | dict | list | tuple) -> dict[str, str | int | float]:
    MAX_DAYS = {
        1: 31,
        2: 29,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 31,
        10: 31,
        11: 30,
        12: 31,
    }
    outdict: dict[str, str | int | float] = {}
    if isinstance(raw_date, dict):
        outdict = raw_date
    elif isinstance(raw_date, str) and (result := re.search(DATE_REGEX, raw_date.strip())):
        year, month, day = map(int, result.groups())
        outdict = {"year": year, "month": month, "day": day}
    elif isinstance(raw_date, list | tuple) and len(raw_date) == 3:
        outdict = dict(zip(("year", "month", "day"), map(int, raw_date)))
    else:
        raise DateValidationError.from_value(raw_date)

    if tuple(outdict.values()) == (0, 0, 0):
        return outdict
    if (
        outdict
        and (outdict["month"] in MAX_DAYS)
        and (0 < outdict["day"] <= MAX_DAYS[outdict["month"]])  # type: ignore
        and all((outdict["year"] > 1970, outdict["month"] > 0, outdict["day"] > 0))  # type: ignore
    ):
        return outdict

    raise DateValidationError.from_value(raw_date)


@deal.has()
@deal.raises(TimeValidationError)
def validate_time(raw_time: str | dict | list | tuple) -> dict[str, str | int | float]:
    if not raw_time:
        raise TimeValidationError.from_value(raw_time)
    outdict: dict[str, str | int | float] = {}
    if isinstance(raw_time, dict):
        outdict = raw_time
    if isinstance(raw_time, str):
        substrings = raw_time.split(":") if raw_time else []
        if 0 < len(substrings) < 4:
            outdict = dict(zip(("hour", "minute", "second"), map(float, substrings)))
    if isinstance(raw_time, list | tuple) and (0 < len(raw_time) < 4):
        outdict = dict(zip(("hour", "minute", "second"), raw_time))

    if (tuple(outdict.values()) == (-1, -1, -1.0)) or all((
        outdict,
        0 <= outdict["hour"] <= 24,  # type: ignore
        0 <= outdict.get("minute", 0) <= 60,  # type: ignore
        0.0 <= outdict.get("second", 0.0) <= 60.0,  # type: ignore
    )):
        return outdict

    raise TimeValidationError.from_value(raw_time)


def compute_index(*, start: int, current: int, step: int, tolerance: float = 1e-8) -> int:
    raw_float_offset: float = (current - start) / step
    index_ = int(raw_float_offset)
    if abs(index_ - raw_float_offset) > tolerance:
        raise IndexError
    return index_


def get_start[Atom: TimeProtocol](obj: Atom | SpanProtocol[Atom]) -> Atom:
    if isinstance(obj, TimeProtocol):
        return obj
    return obj.start


def get_end[Atom: TimeProtocol](obj: Atom | SpanProtocol[Atom]) -> Atom:
    if isinstance(obj, TimeProtocol):
        return obj
    return obj.end


def _get_from_range_index[T: AtomProtocol](
    range_: RangeProtocol,
    idx: int,
    *,
    seconds_per_step: int,
    serializer: Callable[[T], int | float],
    deserializer: Callable[[int | float], T],
) -> T:
    step = range_.step * seconds_per_step
    candidate = deserializer(serializer(range_.start) + idx * step)
    op = le if range_.inclusive else lt
    if op(candidate, range_.stop):
        return candidate
    raise ValueError(f"Index {idx} out of bounds.")


type TimeSerializer[T] = Callable[[T], int | float]
type TimeDeserializer[T] = Callable[[int | float], T]


@overload
def index_getter[T: AtomProtocol](
    range_: RangeProtocol[T],
    slice_or_index: int,
) -> T: ...
@overload
def index_getter[T: AtomProtocol](
    range_: RangeProtocol[T],
    slice_or_index: slice,
) -> RangeProtocol[T]: ...
def index_getter[T: AtomProtocol](
    range_: RangeProtocol[T],
    slice_or_index: int | slice,
) -> T | RangeProtocol[T]:
    seconds_per_step = range_.seconds_per_step
    serializer = range_.start.__class__.to_seconds
    deserializer = range_.start.__class__.from_seconds
    if isinstance(slice_or_index, int):
        step = range_.step * seconds_per_step
        candidate = deserializer(serializer(range_.start) + slice_or_index * step)
        op = le if range_.inclusive else lt
        if op(candidate, range_.stop):
            return candidate
        raise ValueError(f"Index {slice_or_index} out of bounds.")

    elif isinstance(slice_or_index, slice):
        new_start: T = range_[slice_or_index.start]
        new_stop: T = range_[slice_or_index.stop]
        new_step: int = (range_.step or 1) * (slice_or_index.step or 1)

        return new_start.range(new_stop, step=new_step, inclusive=range_.inclusive)

    raise TypeError
