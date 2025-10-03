import pytest

from datethyme import DateTime, DateTimeSpan, Time, TimeSpan
from datethyme._scheduling_utils import (
    apply_pairwise,
    earliest_start,
    get_relative_lengths,
    get_total_length,
    latest_end,
    most_central_span,
    snap_back,
    snap_between,
    snap_forward,
    split_gap_equal,
    split_gap_inverse_proportional,
    split_gap_proportional,
    split_overlap_equal,
    split_overlap_inverse_proportional,
    split_overlap_proportional,
    stack_backward,
    stack_forward,
    stack_from_middle,
    truncate,
    truncate_nodiscard,
)


@pytest.mark.parametrize(
    "callback, original, modified",
    [
        (
            snap_forward,
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
        ),
        (
            lambda x: x,
            unchanged := [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            unchanged,
        ),
    ],
)
def test_apply_pairwise(callback, original, modified):
    assert apply_pairwise(callback, original) == modified


@pytest.mark.parametrize(
    "original, earliest",
    [
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            Time(hour=25, minute=61, second=61),
        ),
        (
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            DateTime(hour=25, minute=61, second=61),
        ),
    ],
)
def test_earliest_start(original, earliest):
    assert earliest_start(original) == earliest


@pytest.mark.parametrize(
    "original, rel_lengths",
    [
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            [0.2, 0.3, 0.1, 0.5],
        ),
        (
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            [0.2, 0.3, 0.1, 0.5],
        ),
    ],
)
def test_get_relative_lengths(original, rel_lengths):
    assert get_relative_lengths(original) == rel_lengths


@pytest.mark.parametrize(
    "original, length",
    [
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            999,
        ),
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            999,
        ),
        (
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            999,
        ),
        (
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            999,
        ),
    ],
)
def test_get_total_length(original, length):
    assert get_total_length(original) == length


@pytest.mark.parametrize(
    "original, latest",
    [
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            Time(hour=25, minute=61, second=61),
        ),
        (
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            DateTime(hour=25, minute=61, second=61),
        ),
    ],
)
def test_latest_end(original, latest):
    assert latest_end(original) == latest


@pytest.mark.parametrize(
    "sequence, central_span",
    [
        (...),
        (...),
    ],
)
def test_most_central_span(sequence, central_span):
    assert most_central_span(sequence) == central_span


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_snap_back(original, modified):
    assert snap_back(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_snap_between(original, modified):
    assert snap_between(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_snap_forward(original, modified):
    assert snap_forward(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_split_gap_equal(original, modified):
    assert split_gap_equal(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_split_gap_inverse_proportional(original, modified):
    assert split_gap_inverse_proportional(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_split_gap_proportional(original, modified):
    assert split_gap_proportional(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_split_overlap_equal(original, modified):
    assert split_overlap_equal(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_split_overlap_inverse_proportional(original, modified):
    assert split_overlap_inverse_proportional(*original) == modified


@pytest.mark.parametrize(
    "original, modified",
    [
        (
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
        (
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
            (
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ),
        ),
    ],
)
def test_split_overlap_proportional(original, modified):
    assert split_overlap_proportional(*original) == modified


@pytest.mark.parametrize(
    "original, stacked",
    [
        (
            [
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
            ],
            [
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
            ],
        ),
        (
            [
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
            ],
            [
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
            ],
        ),
    ],
)
def test_stack_backward(original, stacked):
    assert stack_backward(original) == stacked


@pytest.mark.parametrize(
    "original, stacked",
    [
        (
            [
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
            ],
            [
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
            ],
        ),
        (
            [
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
            ],
            [
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
            ],
        ),
    ],
)
def test_stack_forward(original, stacked):
    assert stack_forward(original) == stacked


@pytest.mark.parametrize(
    "original, stacked",
    [
        (
            [
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
            ],
            [
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
                Time(hour=25, minute=61, second=61),
            ],
        ),
        (
            [
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
            ],
            [
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
                DateTime(hour=25, minute=61, second=61),
            ],
        ),
    ],
)
def test_stack_from_middle(original, stacked):
    assert stack_from_middle(original) == stacked


@pytest.mark.parametrize(
    "original, earliest, latest, before_inside_after",
    [
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            Time(hour=25, minute=61, second=61),
            Time(hour=25, minute=61, second=61),
            (
                [],
                [],
                [],
            ),
        ),
        (
            [
                DateTimeSpan(
                    start=DateTime(hour=25, minute=61, second=61),
                    end=DateTime(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=DateTime(hour=25, minute=61, second=61),
                    end=DateTime(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=DateTime(hour=25, minute=61, second=61),
                    end=DateTime(hour=25, minute=61, second=61),
                ),
            ],
            Time(hour=25, minute=61, second=61),
            Time(hour=25, minute=61, second=61),
            (
                [],
                [],
                [],
            ),
        ),
    ],
)
def test_truncate(original, earliest, latest, before_inside_after):
    assert truncate(original, earliest=earliest, latest=latest) == before_inside_after


@pytest.mark.parametrize(
    "original, earliest, latest, truncated",
    [
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            Time(hour=25, minute=61, second=61),
            Time(hour=25, minute=61, second=61),
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
        ),
        (
            [
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                TimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
            Time(hour=25, minute=61, second=61),
            Time(hour=25, minute=61, second=61),
            [
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
                DateTimeSpan(
                    start=Time(hour=25, minute=61, second=61),
                    end=Time(hour=25, minute=61, second=61),
                ),
            ],
        ),
    ],
)
def test_truncate_nodiscard(original, earliest, latest, truncated):
    assert truncate_nodiscard(original, earliest=earliest, latest=latest) == truncated
