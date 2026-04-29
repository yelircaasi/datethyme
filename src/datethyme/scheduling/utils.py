from collections.abc import Iterable
from itertools import pairwise

from ..protocols import DurationProtocol


def is_partitioned(spans: Iterable[DurationProtocol]) -> bool:
    sorted_spans: list[DurationProtocol] = sorted(spans, key=lambda s: s.start)
    for first, second in pairwise(sorted_spans):
        if not first.end == second.start:
            return False
    return True
