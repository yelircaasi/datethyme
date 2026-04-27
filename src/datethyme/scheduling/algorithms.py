"""
Note the following type aliases used for readability in this file:

```python
type SpanPair[TP: TimeProtocol] = tuple[SpanProtocol[TP], SpanProtocol[TP]]

type SpanTuple[TP: TimeProtocol] = tuple[SpanProtocol[TP], ...]

type SpanList[TP: TimeProtocol] = list[SpanProtocol[TP]]

type SpanIterable[TP: TimeProtocol] = Iterable[SpanProtocol[TP]]

type PairCallback[TP: TimeProtocol] = Callable[
    [SpanProtocol[TP], SpanProtocol[TP]],
    SpanPair[TP],
]
```
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial
from itertools import pairwise
from typing import Literal, TypeVar, cast, overload

from ..protocols import SpanProtocol, TimeProtocol

T = TypeVar("T", bound=TimeProtocol)
type SpanPair[TP: TimeProtocol] = tuple[SpanProtocol[TP], SpanProtocol[TP]]
type SpanTuple[TP: TimeProtocol] = tuple[SpanProtocol[TP], ...]
type SpanList[TP: TimeProtocol] = list[SpanProtocol[TP]]
type SpanIterable[TP: TimeProtocol] = Iterable[SpanProtocol[TP]]
type PairCallback[TP: TimeProtocol] = Callable[
    [SpanProtocol[TP], SpanProtocol[TP]],
    SpanPair[TP],
]
"""Transform one pair of spans into another pair of the same type."""


def snap_forward(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end >= second.start:
        return first, second
    return first.snap_end_to(second.start), second


def snap_back(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end >= second.start:
        return first, second
    return first, second.snap_start_to(first.end)


def snap_between(span: SpanProtocol[T], earliest: T | None, latest: T | None) -> SpanProtocol[T]:
    """Please write me!"""

    earliest_none = earliest is None
    latest_none = latest is None
    if earliest_none and latest_none:
        return span
    elif latest and earliest_none:
        return span.snap_end_to(latest)
    elif earliest and latest_none:
        return span.snap_start_to(earliest)
    elif earliest and latest:
        return span.snap_start_to(earliest).snap_end_to(latest)
    raise ValueError


def earliest_start[T: TimeProtocol](seq: SpanIterable[T] | Iterable[T]) -> T:
    """Please write me!"""

    if all(map(lambda inst: isinstance(inst, TimeProtocol), seq)):
        return min(cast(Iterable[T], seq))
    return min([t.start for t in cast(SpanIterable[T], seq)])


def latest_end[T: TimeProtocol](seq: Iterable[T] | SpanIterable[T]) -> T:
    """Please write me!"""

    if all(map(lambda inst: isinstance(inst, TimeProtocol), seq)):
        return max(cast(Iterable, seq))
    return max([t.end for t in cast(SpanIterable, seq)])


@overload
def most_central[T: TimeProtocol](seq: Iterable[T]) -> T: ...
@overload
def most_central[T: TimeProtocol](seq: SpanIterable[T]) -> SpanProtocol[T]: ...
def most_central[T: TimeProtocol](seq: Iterable[T] | SpanIterable[T]) -> T | SpanProtocol[T]:
    """Please write me!"""

    def get_midpoint(start: TimeProtocol, end: TimeProtocol) -> TimeProtocol:
        return start.__class__.from_ordinal((start.ordinal + end.ordinal) / 2)

    start: TimeProtocol = earliest_start(seq)
    end: TimeProtocol = latest_end(seq)
    get_midpoint(start, end)

    def get_midpoint_distance(item: T | SpanProtocol) -> int:
        if isinstance(item, SpanProtocol):
            midpoint = item.midpoint
        return int(abs(midpoint.minutes_to(midpoint)))

    return min(seq, key=get_midpoint_distance)


def get_relative_lengths[T: TimeProtocol](seq: SpanIterable[T]) -> list[float]:
    """Please write me!"""

    lengths = [t.minutes for t in seq]
    total = sum(lengths)
    return [x / total for x in lengths]


def get_total_length[T: TimeProtocol](seq: SpanIterable[T]) -> float:
    """Please write me!"""

    lengths = [t.minutes for t in seq]
    return sum(lengths)


def stack_forward(seq: SpanIterable[T], anchor: T | None = None) -> SpanList[T]:
    """Please write me!"""

    spans: SpanList[T] = []
    anchor = anchor or earliest_start(seq)
    current: T = anchor or earliest_start(seq)
    for span in seq:
        spans.append(shifted := span.shift_start_rigid(current))
        current = shifted.end

    return spans


def stack_backward(seq: SpanIterable[T], anchor: T | None = None) -> SpanList[T]:
    """Please write me!"""

    spans: SpanList[T] = []
    anchor = anchor or latest_end(seq)
    current: T = anchor or earliest_start(seq)
    for span in seq:
        spans.insert(0, shifted := span.shift_end_rigid(current))
        current = shifted.start

    return spans


def stack_from_middle(seq: SpanIterable[T], anchor: T | None = None) -> SpanList[T]:
    """Please write me!"""

    spans: SpanList[T] = []
    central = most_central(seq := list(seq))
    idx = seq.index(central)
    before, after = seq[:idx], seq[idx + 1 :]
    spans = [
        *stack_backward(before, anchor=central.start),
        central,
        *stack_forward(after, anchor=central.end),
    ]
    return spans


def apply_pairwise[T: TimeProtocol](
    pair_callback: PairCallback,
    seq: SpanIterable[T],
) -> SpanList[T]:
    """Please write me!"""

    if not seq:
        return []
    if len(seq := list(seq)) == 1:
        return seq

    spans: SpanList[T] = []

    if not (remaining := seq[1:]):
        raise ValueError("Cannot call `apply_pairwise` on a sequence of length 1.")
    span_a, span_b = seq[0], seq[1]
    new_b = span_b

    for span_b in remaining:
        new_a, new_b = pair_callback(span_a, span_b)
        spans.append(new_a)
        span_a = new_b
    spans.append(new_b)

    return spans


def split_overlap_equal(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end <= second.start:
        return first, second
    new_border = first.__class__(second.start, first.end).midpoint

    return (
        first.snap_end_to(new_border),
        second.snap_start_to(new_border),
    )


def split_overlap_proportional(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end <= second.start:
        return first, second

    overlap = first.__class__(start=second.start, end=first.end)
    length_first, length_second = first.minutes, second.minutes
    first_proportion = length_first / (length_first + length_second)
    new_border = overlap.interior_point(first_proportion)

    return first.snap_end_to(new_border), second.snap_start_to(new_border)


def split_overlap_inverse_proportional(
    first: SpanProtocol[T], second: SpanProtocol[T]
) -> SpanPair[T]:
    """Please write me!"""

    if first.end <= second.start:
        return first, second

    overlap = first.__class__(second.start, first.end)
    length_first, length_second = first.minutes, second.minutes
    first_rel_share = length_second / (length_first + length_second)
    new_border = overlap.interior_point(first_rel_share)

    return first.snap_end_to(new_border), second.snap_start_to(new_border)


def split_gap_equal(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end >= second.start:
        return first, second
    gap = first.__class__(first.end, second.start)

    return (
        first.snap_end_to(new_border := gap.midpoint),
        second.snap_start_to(new_border),
    )


def split_gap_proportional(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end >= second.start:
        return first, second
    gap = first.__class__(start=first.end, end=second.start)
    length_first, length_second = first.minutes, second.minutes
    first_proportion = length_first / (length_first + length_second)
    new_border = gap.interior_point(first_proportion)

    new_first = first.snap_end_to(new_border)
    new_second = second.snap_start_to(new_border)
    return new_first, new_second


def split_gap_inverse_proportional(first: SpanProtocol[T], second: SpanProtocol[T]) -> SpanPair[T]:
    """Please write me!"""

    if first.end >= second.start:
        return first, second
    gap = first.__class__(first.end, second.start)
    length_first, length_second = first.minutes, second.minutes
    first_rel_share = length_second / (length_first + length_second)
    new_border = gap.interior_point(first_rel_share)

    new_first = first.snap_end_to(new_border)
    new_second = second.snap_start_to(new_border)
    return new_first, new_second


def truncate(
    seq: SpanIterable[T], earliest: T, latest: T
) -> tuple[SpanList[T], SpanList[T], SpanList[T]]:
    """Please write me!"""

    before: SpanList[T] = []
    kept: SpanList[T] = []
    after: SpanList[T] = []
    for span in seq:
        if span.end <= earliest:
            before.append(span)
        elif span.contains(earliest):
            outside, inside = span.split(earliest)
            before.append(outside)
            kept.append(inside)
        elif earliest <= span <= latest:
            kept.append(span)
        elif span.contains(latest):
            inside, outside = span.split(latest)
            kept.append(inside)
            after.append(outside)
        elif span.start >= latest:
            after.append(span)
        else:
            raise ValueError

    return before, kept, after


def truncate_nodiscard[T: TimeProtocol](
    seq: SpanIterable[T], earliest: TimeProtocol, latest: TimeProtocol
) -> SpanList[T] | None:
    """Please write me!"""

    """
    Truncate a sequence, but return None if truncation causes the
        loss of one or more entire (as opposed to only partial) spans.
    """
    if min(seq, key=lambda s: s.end) <= earliest:
        return None
    if max(seq, key=lambda s: s.start) >= latest:
        return None
    truncator = cast(
        Callable[[SpanProtocol[T]], SpanProtocol[T]],
        partial(snap_between, earliest=earliest, latest=latest),
    )
    truncated: SpanIterable[T] = map(truncator, seq)
    return list(filter(bool, truncated))


def eclipse_forward[T: TimeProtocol](
    seq: SpanIterable[T],
) -> tuple[
    SpanTuple[T],
    SpanTuple[T],
]:
    """Please write me!"""

    if not seq:
        return tuple(), tuple()

    spans: SpanList[T] = [(seq := list(seq))[0]]
    rejects: SpanList[T] = []
    current = seq[0].end

    for span in seq[1:]:
        rejected_span, kept_span = span.split(max(current, span.start))
        if kept_span:
            spans.append(kept_span)
        if rejected_span:
            rejects.append(rejected_span)
        current = max(current, kept_span.end)

    return tuple(spans), tuple(rejects)


def eclipse_backward[T: TimeProtocol](
    seq: SpanIterable[T],
) -> tuple[SpanTuple[T], SpanTuple[T]]:
    """Please write me!"""

    if not seq:
        return tuple(), tuple()

    spans: SpanList[T] = [(seq := list(seq))[-1]]
    rejects: SpanList[T] = []
    current = seq[0].end

    for span in seq[-2::-1]:
        kept_span, rejected_span = span.split(min(current, span.end))
        if kept_span:
            spans.append(kept_span)
        if rejected_span:
            rejects.append(rejected_span)
        current = min(current, kept_span.end)

    return tuple(spans), tuple(rejects)


def resolve_overlaps[T: TimeProtocol](
    seq: SpanIterable[T],
    mode: Literal["EQUAL", "PROPORTIONAL", "INVERSE"],
) -> SpanTuple[T]:
    """Please write me!"""

    if mode == "EQUAL":
        return tuple(apply_pairwise(split_overlap_equal, seq))
    elif mode == "PROPORTIONAL":
        return tuple(apply_pairwise(split_overlap_proportional, seq))
    elif mode == "INVERSE":
        return tuple(apply_pairwise(split_overlap_inverse_proportional, seq))
    else:
        raise ValueError(f"Invalid mode for method 'resolve_overlaps': '{mode}'")


def resolve_gaps[T: TimeProtocol](
    seq: SpanIterable[T],
    mode=Literal["EQUAL", "PROPORTIONAL", "INVERSE", "SNAP_FORWARD", "SNAP_BACK"],
) -> SpanTuple[T]:
    """Please write me!"""

    if mode == "EQUAL":
        return tuple(apply_pairwise(split_gap_equal, seq))
    if mode == "PROPORTIONAL":
        return tuple(apply_pairwise(split_gap_proportional, seq))
    if mode == "INVERSE":
        return tuple(apply_pairwise(split_gap_inverse_proportional, seq))
    if mode == "SNAP_FORWARD":
        return tuple(apply_pairwise(snap_forward, seq))
    if mode == "SNAP_BACK":
        return tuple(apply_pairwise(snap_back, seq))
    raise ValueError(f"Invalid mode for method 'resolve_gaps': '{mode}'")


def squeeze(
    seq: SpanIterable[T],
    *,
    mode: Literal["PROPORTIONAL", "EQUAL"],
    earliest: T | None = None,
    latest: T | None = None,
    min_minutes: int | float = 5,
    gap_resolver: Callable[[SpanProtocol[T]], SpanProtocol[T]] | None = None,
    overlap_resolver: Callable[[SpanProtocol[T]], SpanProtocol[T]] | None = None,
) -> SpanTuple[T]:
    """Squeeze all elements of `seq` to fit between `earliest` and `latest`."""
    spans: SpanList[T] = []
    # earliest: Atom = earliest or earliest_start(seq)
    # latest: Atom = latest or latest_end(seq)
    if mode == "PROPORTIONAL":
        relative_lengths = get_relative_lengths(seq)
    elif mode == "EQUAL":
        seq = list(seq)
        relative_lengths = [x / len(seq) for x in range(len(seq))]
    else:
        raise ValueError(f"Invalid mode for method 'squeeze': '{mode}'")

    earliest_: T = earliest or earliest_start(seq)
    latest_: T = latest or latest_end(seq)
    new_total: float = earliest_.minutes_to(latest_)
    current = earliest_
    squeezed: SpanProtocol[T]
    for span, rel_length in zip(seq, relative_lengths):
        spans.append(
            squeezed := span.forward_affine_transform(
                scale_factor=rel_length * new_total,
                new_start=current,
                min_minutes=min_minutes,
            )
        )
        current = squeezed.end
    return tuple(spans)


def squeeze_with_rollover(
    seq: SpanIterable[T],
    *,
    mode: Literal["PROPORTIONAL", "EQUAL"],
    earliest: T | None = None,
    latest: T | None = None,
    min_minutes: int | float = 5,
    gap_resolver: Callable[[SpanProtocol[T]], SpanProtocol[T]] | None = None,
    overlap_resolver: Callable[[SpanProtocol[T]], SpanProtocol[T]] | None = None,
) -> tuple[SpanTuple[T], SpanTuple[T]]:
    """Please write me!"""

    seq = list(seq)
    keep_n = (
        int(len(seq) // min_minutes)
        if earliest and latest and (len(seq) * min_minutes) > earliest.minutes_to(latest)
        else len(seq)
    )
    return (
        squeeze(seq[:keep_n], mode=mode, earliest=earliest, latest=latest, min_minutes=min_minutes),
        tuple(seq[keep_n:]),
    )


def stack[T: TimeProtocol](
    seq: SpanIterable[T],
    mode: Literal["FORWARD", "OUTWARD", "BACKWARD"],
    anchor=None,
) -> SpanTuple[T]:
    """Please write me!"""

    lookup: dict[
        Literal["FORWARD", "OUTWARD", "BACKWARD"],
        Callable[[SpanIterable[T], T | None], SpanIterable[T]],
    ] = {
        "FORWARD": stack_forward,
        "OUTWARD": stack_from_middle,
        "BACKWARD": stack_backward,
    }
    func = lookup.get(mode)
    if not func:
        raise ValueError(f"Invalid mode for method 'stack': '{mode}'")
    return tuple(func(seq, anchor))


def is_contiguous[T: TimeProtocol](seq: SpanIterable[T]) -> bool:
    """Please write me!"""

    return all(map(lambda pair: pair[0].end == pair[1].start, pairwise(seq)))
