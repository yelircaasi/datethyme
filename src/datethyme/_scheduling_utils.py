from collections.abc import Callable, Iterable
from functools import partial
from typing import TypeVar, cast

from .protocols import SpanProtocol, TimeProtocol  # type: ignore

T = TypeVar("T", bound=TimeProtocol)


Span = TypeVar("Span", bound=SpanProtocol)
PairCallback = Callable[[Span, Span], tuple[Span, Span]]


def snap_forward(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end >= second.start:
        return first, second
    return cast(Span, first.snap_end_to(second.start)), second


def snap_back(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end >= second.start:
        return first, second
    return first, cast(Span, second.snap_start_to(first.end))


def snap_between(span: Span, earliest: T | None, latest: T | None) -> Span:
    earliest_none = earliest is None
    latest_none = latest is None
    if earliest_none and latest_none:
        return span
    elif earliest_none:
        return cast(Span, span.snap_end_to(latest))
    elif latest_none:
        return cast(Span, span.snap_start_to(earliest))
    else:
        return cast(Span, span.snap_start_to(earliest).snap_end_to(latest))


def earliest_start[T: TimeProtocol](seq: Iterable[SpanProtocol[T]]) -> T:
    return min([t.start for t in seq])


def latest_end[T: TimeProtocol](seq: Iterable[SpanProtocol[T]]) -> T:
    return max([t.end for t in seq])


def most_central_span[Span: SpanProtocol](seq: Iterable[Span]) -> Span:
    def get_midpoint(start: TimeProtocol, end: TimeProtocol) -> TimeProtocol:
        return start.__class__.from_ordinal((start.ordinal + end.ordinal) / 2)

    start: TimeProtocol = earliest_start(seq)
    end: TimeProtocol = latest_end(seq)
    midpoint: TimeProtocol = get_midpoint(start, end)

    def get_midpoint_distance(spn: Span) -> int:
        return int(abs(midpoint.minutes_to(spn.midpoint)))

    return min(seq, key=get_midpoint_distance)


def get_relative_lengths[Span: SpanProtocol](seq: Iterable[Span]) -> list[float]:
    lengths = [t.minutes for t in seq]
    total = sum(lengths)
    return [x / total for x in lengths]


def get_total_length[Span: SpanProtocol](seq: Iterable[Span]) -> float:
    lengths = [t.minutes for t in seq]
    return sum(lengths)


def stack_forward[Span: SpanProtocol](seq: Iterable[Span], anchor=None) -> list[Span]:
    spans: list[Span] = []
    anchor = anchor or earliest_start(seq)
    _current: TimeProtocol = anchor or earliest_start(seq)
    for span in seq:
        spans.append(shifted := cast(Span, span.shift_start_rigid(_current)))
        _current = shifted.end

    return spans


def stack_backward[Span: SpanProtocol](seq: Iterable[Span], anchor=None) -> list[Span]:
    spans: list[Span] = []
    anchor = anchor or latest_end(seq)
    _current: TimeProtocol = anchor or earliest_start(seq)
    for span in seq:
        spans.insert(0, shifted := cast(Span, span.shift_end_rigid(_current)))
        _current = shifted.start

    return spans


def stack_from_middle[Span: SpanProtocol](seq: Iterable[Span], anchor=None) -> list[Span]:
    spans: list[Span] = []
    central = most_central_span(seq := list(seq))
    idx = seq.index(central)
    before, after = seq[:idx], seq[idx + 1 :]
    spans = [
        *stack_backward(before, anchor=central.start),
        central,
        *stack_forward(after, anchor=central.end),
    ]
    return spans


def apply_pairwise[Span: SpanProtocol](
    pair_callback: PairCallback[Span],
    seq: Iterable[Span],
) -> list[Span]:
    if not seq:
        return []
    if len(seq := list(seq)) == 1:
        return seq

    spans: list[Span] = []

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


def split_overlap_equal(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end <= second.start:
        return first, second
    new_border = first.__class__(second.start, first.end).midpoint

    return (
        cast(Span, first.snap_end_to(new_border)),
        cast(Span, second.snap_start_to(new_border)),
    )


def split_overlap_proportional(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end <= second.start:
        return first, second

    overlap = first.__class__(start=second.start, end=first.end)
    length_first, length_second = first.minutes, second.minutes
    first_proportion = length_first / (length_first + length_second)
    new_border = overlap.interior_point(first_proportion)

    return cast(Span, first.snap_end_to(new_border)), cast(Span, second.snap_start_to(new_border))


def split_overlap_inverse_proportional(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end <= second.start:
        return first, second

    overlap = first.__class__(second.start, first.end)
    length_first, length_second = first.minutes, second.minutes
    first_rel_share = length_second / (length_first + length_second)
    new_border = overlap.interior_point(first_rel_share)

    return cast(Span, first.snap_end_to(new_border)), cast(Span, second.snap_start_to(new_border))


def split_gap_equal(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end >= second.start:
        return first, second
    gap = first.__class__(first.end, second.start)

    return (
        cast(Span, first.snap_end_to(new_border := gap.midpoint)),
        cast(Span, second.snap_start_to(new_border)),
    )


def split_gap_proportional(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end >= second.start:
        return first, second
    gap = first.__class__(start=first.end, end=second.start)
    length_first, length_second = first.minutes, second.minutes
    first_proportion = length_first / (length_first + length_second)
    new_border = gap.interior_point(first_proportion)

    new_first = cast(Span, first.snap_end_to(new_border))
    new_second = cast(Span, second.snap_start_to(new_border))
    return new_first, new_second


def split_gap_inverse_proportional(first: Span, second: Span) -> tuple[Span, Span]:
    if first.end >= second.start:
        return first, second
    gap = first.__class__(first.end, second.start)
    length_first, length_second = first.minutes, second.minutes
    first_rel_share = length_second / (length_first + length_second)
    new_border = gap.interior_point(first_rel_share)

    new_first = cast(Span, first.snap_end_to(new_border))
    new_second = cast(Span, second.snap_start_to(new_border))
    return new_first, new_second


def truncate[Span: SpanProtocol](
    seq: Iterable[Span], earliest: TimeProtocol, latest: TimeProtocol
) -> tuple[list[Span], list[Span], list[Span]]:
    before: list[Span] = []
    kept: list[Span] = []
    after: list[Span] = []
    for span in seq:
        if span.end <= earliest:
            before.append(span)
        elif span.contains(earliest):
            outside, inside = span.split(earliest)
            before.append(cast(Span, outside))
            kept.append(cast(Span, inside))
        elif earliest <= span <= latest:
            kept.append(span)
        elif span.contains(latest):
            inside, outside = span.split(latest)
            kept.append(cast(Span, inside))
            after.append(cast(Span, outside))
        elif span.start >= latest:
            after.append(span)
        else:
            raise ValueError

    return before, kept, after


def truncate_nodiscard[Span: SpanProtocol](
    seq: Iterable[Span], earliest: TimeProtocol, latest: TimeProtocol
) -> list[Span] | None:
    """
    Truncate a sequence, but return None if truncation causes the
        loss of one or more entire (as opposed to only partial)
        AbstractSpans.
    """
    if min(seq, key=lambda s: s.end) <= earliest:
        return None
    if max(seq, key=lambda s: s.start) >= latest:
        return None
    truncator = cast(
        Callable[[Span], Span],
        partial(snap_between, earliest=earliest, latest=latest),
    )
    truncated: Iterable[Span] = map(truncator, seq)
    return list(filter(bool, truncated))
