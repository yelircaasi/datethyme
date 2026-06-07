from __future__ import annotations

import itertools
import re
from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Protocol, TypedDict

from adiumentum.fp import lmap
from loguru import logger

# from adiumentum.num import round5
# from adiumentum.num import round5
from datethyme import Date, Time, TimeSpan

from .new import DurationType

DATE_RE = re.compile(r"^[=\s]*(?P<date>\d{4}-\d{1,2}-\d{1,2})(?:\s+(?P<text>.*)\s*)?$")
EVENT_RE = re.compile(
    r"""
    ^\s+
    (?P<start>\d{1,2}:\d{2})
    \s*-\s*
    (?:
        (?P<end>\d{1,2}:\d{2})
        \s+
    )?
    (?P<title>.*?)
    \s*
    (?P<contexts>\[[^\]]*\])?
    \s*$
    """,
    re.VERBOSE,
)
NESTED_RE = re.compile(
    r"""
    ^\s*
    (?P<pipe>\|+)
    \s*
    (?P<start>\d{1,2}:\d{2})
    \s*-\s*
    (?:
        (?P<end>\d{1,2}:\d{2})
        \s+
    )?
    (?P<text>.*?)
    \s*
    (?P<contexts>\[[^\]]*\])?
    \s*$
    """,
    re.VERBOSE,
)


def _parse_contexts(raw: str | None) -> list[str]:
    if not raw:
        return []

    inner = raw[1:-1].strip()
    if not inner:
        return []

    return [x.strip() for x in inner.split(",") if x.strip()]


class DayDict(TypedDict):
    blocks: list[dict[str, Any]]
    text: str


def parse_calendar(text: str) -> dict[Date, DayDict]:
    result: dict[Date, DayDict] = {}

    current_date: Date | None = None
    current_event: dict[str, Any] | None = None

    # stack[level] = most recent node at that nesting level
    stack: list[dict[str, Any]] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            continue

        # Date line
        m = DATE_RE.match(line)
        if m:
            current_date = Date.parse(m.group("date"))
            result[current_date] = {"blocks": [], "text": m.group("text") or ""}
            current_event = None
            stack.clear()
            continue

        if current_date is None:
            raise ValueError(f"Content before first date: {line!r}")

        # Top-level event
        m = EVENT_RE.match(line)
        if m:
            event = {
                "start": Time.parse(m.group("start")),
                "end": (Time.parse(m.group("end")) if m.group("end") else None),
                "text": m.group("title").strip(),
                "contexts": _parse_contexts(m.group("contexts")),
                "children": [],
            }

            result[current_date]["blocks"].append(event)
            current_event = event
            stack.clear()
            continue

        # Nested star block
        m = NESTED_RE.match(line)
        if m:
            if current_event is None:
                raise ValueError(f"Nested block without parent event: {line!r}")

            node = {
                "start": m.group("start"),
                "end": Time.parse(m.group("end")) if m.group("end") else None,
                "text": m.group("text").strip(),
                "contexts": _parse_contexts(m.group("contexts")),
                "children": [],
            }

            parent = current_event

            parent["children"].append(node)

            stack.append(node)

            continue

        raise ValueError(f"Cannot parse line: {line!r}")

    return result


class SpanMixin:
    """Delegates AbstractSpan methods to a lazily-constructed TimeSpan."""

    start: Time
    end: Time | None

    def _span(self) -> TimeSpan:
        if self.end is None:
            raise ValueError("Cannot use span operations without an end time")
        return TimeSpan(self.start, self.end)

    # Delegate everything you actually use from AbstractSpan:
    def midpoint(self) -> Time:
        return self._span().midpoint()

    def contains(self, other, **kwargs) -> bool:
        return self._span().contains(other, **kwargs)

    def intersection(self, other, **kwargs):
        return self._span().intersection(other, **kwargs)

    def hull(self, other, **kwargs):
        return self._span().hull(other, **kwargs)

    def overlap(self, other, **kwargs):
        return self._span().overlap(other, **kwargs)

    def __contains__(self, other) -> bool:
        return self._span().__contains__(other)

    def __bool__(self) -> bool:
        return self.end is not None and self.end > self.start

    # ... add others as needed


class HasStartEnd(Protocol):
    start: Time
    end: Time


def last_end(spans: Iterable[HasStartEnd], fallback: Time) -> Time:
    if not spans:
        return fallback
    return max(x.end for x in spans)


def first_start(spans: Iterable[HasStartEnd], fallback: Time) -> Time:
    if not spans:
        return fallback
    return min(x.start for x in spans)


DAY_START = Time(hour=0)


class HasDuration(Protocol):
    @property
    def minTime(self) -> int: ...
    @property
    def normalTime(self) -> int: ...
    @property
    def idealTime(self) -> int: ...
    @property
    def maxTime(self) -> int: ...


def sum_time(duration_type: DurationType, seq: Iterable[HasDuration], fallback: int = 0) -> int:
    if fallback and not seq:
        return fallback
    attr = f"{duration_type!s}Time"
    print(attr)
    getter = attrgetter(attr)
    return sum(map(getter, seq))


def negotiate_length(start: Time, end: Time, seq: Iterable[HasDuration]) -> list[tuple[Time, Time]]:
    seq = tuple(seq)
    length = start.minutes_to(end)

    min_total = sum_time(DurationType.MIN, seq)
    max_total = sum_time(DurationType.MAX, seq)

    # Clamp target to what the sequence can physically achieve
    target = min(max(length, min_total), max_total)

    def clamp(val: float, block: HasDuration) -> int:
        return min(max(round(val), block.minTime), block.maxTime)

    # Weight each block by its ideal↔normal gap — blocks with more
    # slack between the two absorb proportionally more of the adjustment
    weights = [abs(b.idealTime - b.normalTime) for b in seq]
    total_weight = sum(weights) or len(seq)  # fallback: uniform
    if not any(weights):
        weights = [1] * len(seq)

    durations: list[float] = [float(b.idealTime) for b in seq]

    for _ in range(100):
        deficit = target - sum(durations)
        if deficit == 0:
            break
        durations = [
            clamp(d + deficit * (w / total_weight), b) for d, w, b in zip(durations, weights, seq)
        ]

    current = start
    time_pairs: list[tuple[Time, Time]] = []
    for d in durations:
        old = current
        current += round(d)
        time_pairs.append((old, current))

    return time_pairs


class BlockProtocol(Protocol):
    start: Time
    end: Time

    @property
    def size(self) -> int: ...

    @property
    def minTime(self) -> int: ...

    @property
    def normalTime(self) -> int: ...

    @property
    def idealTime(self) -> int: ...

    @property
    def maxTime(self) -> int: ...

    task: Any


def adjust_blocks_OLD[T: BlockProtocol](
    start: Time,
    end: Time,
    blocks: list[T],
    duration_type: DurationType = DurationType.NORMAL,
) -> list[T]:
    _getter = attrgetter(f"{duration_type}Time")

    def getter(sb: T) -> int:
        # if sb.task:
        #     return _getter(sb.task)
        return sb.size

    stretched: list[T] = []
    size_minutes = round(start.minutes_to(end))
    total = sum_time(DurationType.NORMAL, blocks, fallback=size_minutes)
    ratio: float = size_minutes / total
    logger.info(f"{size_minutes=}, {total=}, {ratio=}")

    def adjust_size(blck: T) -> int:
        return round(getter(blck) * ratio)

    blocks.sort(key=lambda x: x.start)
    new_lengths = lmap(adjust_size, blocks)
    logger.info(str(new_lengths))
    current: Time = start.model_copy()
    for length, block in zip(new_lengths, blocks):
        block.start = current
        current = current.add_minutes_bounded(length)
        block.end = current
        stretched.append(block)
    return stretched


def adjust_blocks[T: BlockProtocol](
    start: Time, end: Time, blocks: list[T], duration_type: DurationType = DurationType.NORMAL
) -> list[T]:
    blocks = sorted(blocks, key=lambda x: x.start)

    # adapters so that negotiate_length can see each block's
    #     time budget, pulling from the attached task if present, else the
    #     block's own size for all four fields
    class _Adapter:
        def __init__(self, block: T) -> None:
            if block.task:
                self.minTime = block.task.minTime
                self.normalTime = block.task.normalTime
                self.idealTime = block.task.idealTime
                self.maxTime = block.task.maxTime
            else:
                self.minTime = block.size
                self.normalTime = block.size
                self.idealTime = block.size
                self.maxTime = block.size

    adapters = [_Adapter(b) for b in blocks]
    time_pairs = negotiate_length(start, end, adapters)

    stretched: list[T] = []
    for block, (new_start, new_end) in zip(blocks, time_pairs):
        # print(block.id, new_start, new_end)
        block.start = new_start
        block.end = new_end
        stretched.append(block)

    actual_end = stretched[-1].end
    remainder = round(actual_end.minutes_to(end))  # +ve: short, -ve: overshot

    if remainder != 0:
        direction = 1 if remainder > 0 else -1

        def slack(i: int) -> int:
            block = stretched[i]
            duration = round(block.start.minutes_to(block.end))
            if direction > 0:
                return adapters[i].maxTime - duration
            else:
                return duration - adapters[i].minTime

        # important correction: only consider blocks that actually have room to absorb a nudge
        candidates = sorted(
            [i for i in range(len(stretched)) if slack(i) > 0],
            key=slack,
            reverse=True,
        )

        if candidates:
            for i in itertools.islice(itertools.cycle(candidates), abs(remainder)):
                # re-check slack at the time of application;
                # a previous iteration may have exhausted this block's headroom
                if slack(i) <= 0:
                    continue
                stretched[i].end = stretched[i].end.add_minutes_bounded(direction)
                for j in range(i + 1, len(stretched)):
                    stretched[j].start = stretched[j].start.add_minutes_bounded(direction)
                    stretched[j].end = stretched[j].end.add_minutes_bounded(direction)

    return stretched


def rescale[T: BlockProtocol](start: Time, end: Time, blocks: list[T]) -> list[T]:
    current: Time = start
    block_size = sum(map(lambda b: b.size, blocks))
    if not block_size:
        return blocks
    factor = start.minutes_to(end) / block_size
    for block in blocks:
        old_size = block.size
        block.start = current.model_copy()
        current += round(factor * old_size)
        block.end = current.model_copy()
    if abs(block.end.minutes_to(end)) < 6:
        block.end = end
        # raise ValueError(f"{end} != {block.end}")
    return blocks
