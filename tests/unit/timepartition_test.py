import pytest

from datethyme import TimePartition, TimeSpan, Time

REPLACE_ME = 99

PARTITION_3H = TimePartition(...)
PARTITION_5H = TimePartition(...)
PARTITION_DAY = TimePartition(...)
PARTITION_NESTED = TimePartition(...)
PARTITION_DOUBLE_NESTED = TimePartition(...)

SEQ_GAPS = (
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
)
SEQ_OVERLAPS = (
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
)
SEQ_GAPS_OVERLAPS = (
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
)
SEQ_CONTIGUOUS = (
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
)
SEQ_UNORDERED = (
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
    TimeSpan(
        start=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
        end=Time(hour=REPLACE_ME, minute=REPLACE_ME, second=REPLACE_ME),
    ),
)


class TestTimePartition:
    def test_dunder_init(self): ...

    def test_dunder_init_error(self):
        with pytest.raises(...):
            ...

    @pytest.mark.parametrize(
        "partition, midpoint",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_midpoint(self, partition, midpoint):
        assert partition.midpoint == midpoint

    @pytest.mark.parametrize(
        "partition, start_time",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_start(self, partition, start_time):
        assert partition.start == start_time

    @pytest.mark.parametrize(
        "partition, start_times",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_starts(self, partition, start_times):
        assert partition.starts == start_times

    @pytest.mark.parametrize(
        "partition, end",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_end(self, partition, end):
        assert partition.end == end

    @pytest.mark.parametrize(
        "partition, ends",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_ends(self, partition, ends):
        assert partition.ends == ends

    @pytest.mark.parametrize(
        "partition, days",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_days(self, partition, days):
        assert partition.days == days

    @pytest.mark.parametrize(
        "partition, hours",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_hours(self, partition, hours):
        assert partition.hours == hours

    @pytest.mark.parametrize(
        "partition, minutes",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_minutes(self, partition, minutes):
        assert partition.minutes == minutes

    @pytest.mark.parametrize(
        "partition, seconds",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_seconds(self, partition, seconds):
        assert partition.seconds == seconds

    @pytest.mark.parametrize(
        "sequence, pipeline, expected",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_from_pipeline(self, sequence, pipeline, expected):
        assert TimePartition.from_pipeline(sequence, pipeline) == expected

    @pytest.mark.parametrize(
        "sequence, expected",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_from_partition(self, sequence, expected):
        assert TimePartition.from_partition(sequence) == expected

    @pytest.mark.parametrize(
        "lengths, start, end, expected",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_from_relative_lengths(self, lengths, start, end, expected):
        partition = TimePartition.from_relative_lengths(lengths, start=start, end=end)
        assert partition == expected

    @pytest.mark.parametrize(
        "durations, start, end, names, expected",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_from_durations(self, durations, start, end, names, expected):
        partition = TimePartition.from_durations(
            durations, durations, start=start, end=end, names=names
        )
        assert partition == expected

    @pytest.mark.parametrize(
        "minutes, start, names, expected",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_from_minutes_and_start(self, minutes, start, names, expected):
        partition = TimePartition.from_minutes_and_end(minutes=minutes, start=start, names=names)
        assert partition == expected

    @pytest.mark.parametrize(
        "minutes, end, names, expected",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_from_minutes_and_end(self, minutes, end, names, expected):
        partition = TimePartition.from_minutes_and_end(minutes=minutes, end=end, names=names)
        assert partition == expected

    @pytest.mark.parametrize(
        "partition, is_true",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_dunder_bool(self, partition, is_true):
        assert bool(partition) == is_true

    @pytest.mark.parametrize(
        "partition, maybe_contained, is_contained",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_dunder_contains(self, partition, maybe_contained, is_contained):
        assert (maybe_contained in partition) == is_contained

    @pytest.mark.parametrize(
        "partition, other, are_equal",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_dunder_eq(self, partition, other, are_equal):
        assert (partition == other) == are_equal

    @pytest.mark.parametrize(
        "original, scale_factor, new_start, new_end, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_affine_transform(self, original, scale_factor, new_start, new_end, transformed):
        result = original.affine_transform(
            scale_factor,
            new_start=new_start,
            new_end=new_end,
        )
        assert result == transformed

    def test_affine_transform_errors(self):
        with pytest.raises(...):
            ...

    @pytest.mark.parametrize(
        "partition, maybe_contained, is_contained",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_contains(self, partition, maybe_contained, is_contained):
        assert partition.contains(maybe_contained) == is_contained

    @pytest.mark.parametrize(
        "partition, other, gap",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_gap(self, partition, other, gap):
        assert partition.gap(other) == gap

    @pytest.mark.parametrize(
        "partition, other, overlap",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_overlap(self, partition, other, overlap):
        assert partition.overlap(other) == overlap

    @pytest.mark.parametrize(
        "partition_a, partition_b, expected_hull",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_hull(self, partition_a, partition_b, expected_hull):
        hull_forward = partition_a.hull(partition_b)
        hull_reverse = partition_b.hull(partition_a)
        assert hull_forward == hull_reverse == expected_hull

    @pytest.mark.parametrize(
        "partition_a, partition_b, expected_intersection",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_intersection(self, partition_a, partition_b, expected_intersection):
        int_forward = partition_a.intersection(partition_b)
        int_reverse = partition_b.hull(partition_a)
        assert int_forward == int_reverse == expected_intersection

    @pytest.mark.parametrize(
        "partition, alpha, point",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_interior_point(self, partition, alpha, point):
        assert partition.interior_point(alpha) == point

    @pytest.mark.parametrize(
        "partition, does_pass",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_passes_day_boundary(self, partition, does_pass):
        assert partition.passes_day_boundary == does_pass

    # STATIC ------------------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "sequence, transformed",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_eclipse_backward(self, sequence, transformed):
        assert TimePartition.eclipse_backward(sequence) == transformed

    @pytest.mark.parametrize(
        "sequence, transformed",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_eclipse_forward(self, sequence, transformed):
        assert TimePartition.eclipse_forward(sequence) == transformed

    @pytest.mark.parametrize(
        "original, reorderer, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_reordered(self, original, reorderer, transformed):
        assert original.reordered(reorderer) == transformed

    @pytest.mark.parametrize(
        "original, mode, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_resolve_gaps(self, original, mode, transformed):
        assert TimePartition.resolve_gaps(original, mode=mode) == transformed

    @pytest.mark.parametrize(
        "original, mode, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_resolve_overlaps(self, original, mode, transformed):
        assert TimePartition.resolve_overlaps(original, mode=mode) == transformed

    @pytest.mark.parametrize(
        "original, new_end, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_shift_start_rigid(self, original, new_end, transformed):
        assert original.shift_start_rigid(new_end=new_end) == transformed

    @pytest.mark.parametrize(
        "original, new_start, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_shift_start_rigid(self, original, new_start, transformed):
        assert original.shift_start_rigid(new_start=new_start) == transformed

    @pytest.mark.parametrize(
        "original, new_end, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_snap_end_to(self, original, new_end, transformed):
        assert original.snap_end_to(new_end=new_end) == transformed

    @pytest.mark.parametrize(
        "original, new_start, transformed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_snap_start_to(self, original, new_start, transformed):
        assert original.snap_start_to(new_start=new_start) == transformed

    @pytest.mark.parametrize(
        "partition, spans",
        [
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_spans(self, partition, spans):
        assert partition.spans == spans

    @pytest.mark.parametrize(
        "original, point, first, second",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_split(self, original, point, first, second):
        assert original.split(point) == (first, second)

    @pytest.mark.parametrize(
        "original, earliest, latest, gap_resolver, overlap_resolver, min_minutes, squeezed",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_squeeze(
        self,
        original,
        earliest,
        latest,
        gap_resolver,
        overlap_resolver,
        min_minutes,
        squeezed,
    ):
        transformed = TimePartition.squeeze(
            original,
            earliest=earliest,
            latest=latest,
            gap_resolver=gap_resolver,
            overlap_resolver=overlap_resolver,
            min_minutes=min_minutes,
        )
        assert transformed == squeezed

    @pytest.mark.parametrize(
        "original, earliest, latest, gap_resolver, overlap_resolver, min_minutes, squeezed, rollover",
        [
            (
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
            ),
            (
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
            ),
            (
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
            ),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_squeeze_with_rollover(
        self,
        original,
        earliest,
        latest,
        gap_resolver,
        overlap_resolver,
        min_minutes,
        squeezed,
    ):
        transformed = TimePartition.squeeze_with_rollover(
            original,
            earliest=earliest,
            latest=latest,
            gap_resolver=gap_resolver,
            overlap_resolver=overlap_resolver,
            min_minutes=min_minutes,
        )
        assert transformed == squeezed

    @pytest.mark.parametrize(
        (
            "original, earliest, latest, gap_resolver, overlap_resolver, "
            "min_minutes, squeezed, rollforward"
        ),
        [
            (
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
            ),
            (
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
            ),
            (
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
                REPLACE_ME,
            ),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_squeeze_with_rollforward(
        self,
        original,
        earliest,
        latest,
        gap_resolver,
        overlap_resolver,
        min_minutes,
        squeezed,
    ):
        transformed = TimePartition.squeeze_with_rollforward(
            original,
            earliest=earliest,
            latest=latest,
            gap_resolver=gap_resolver,
            overlap_resolver=overlap_resolver,
            min_minutes=min_minutes,
        )
        assert transformed == squeezed

    @pytest.mark.parametrize(
        "original, mode, anchor, stacked",
        [
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
            (REPLACE_ME, REPLACE_ME, REPLACE_ME, REPLACE_ME),
        ],
        ids=["REPLACE_ME", "REPLACE_ME", "REPLACE_ME"],
    )
    def test_stack(self, original, mode, anchor, stacked):
        transformed = TimePartition.stack(original, mode=mode, anchor=anchor)
        assert transformed == stacked

    def test_is_contiguous(self):
        assert TimePartition.is_contiguous(SEQ_CONTIGUOUS)
        assert TimePartition.is_contiguous(TimePartition.stack(SEQ_GAPS, mode="FORWARD"))
        assert not TimePartition.is_contiguous(SEQ_GAPS)
        assert not TimePartition.is_contiguous(SEQ_OVERLAPS)
        assert not TimePartition.is_contiguous(SEQ_GAPS_OVERLAPS)
        assert not TimePartition.is_contiguous(SEQ_UNORDERED)

    def test_daterange(): ...

    def test_dunder_repr(): ...

    def test_dunder_str(): ...

    def test_format_span(): ...

    def test_from_boundaries(): ...

    def test_from_datetimes(): ...

    def test_from_deltas(): ...

    def test_from_times(): ...

    def test_index_from_name(): ...

    def test_index_from_time(): ...

    def test_insert(): ...

    def test_names(): ...

    def test_round_hours(): ...

    def test_round_minutes(): ...

    def test_round_seconds(): ...

    def test_shift_end_rigid(): ...

    def test_span(): ...

    def test_span_containing(): ...

