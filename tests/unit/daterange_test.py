import pytest

from datethyme import Date, DateRange

DATE_A = Date.parse("2025-07-24")
DATE_B = Date.parse("2025-07-29")

PLACEHOLDER = DATE_A


class TestDateRange:
    date_a = DATE_A
    date_b = DATE_B

    def test_with_end(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.with_end().inclusive is True

    def test_without_end(self) -> None:
        dr = DateRange(self.date_a, self.date_b, inclusive=True)
        assert dr.without_end().inclusive is False

    def test_days(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.days == 1 + int(dr.stop) - int(dr.start)

    def test_hours(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.hours == 24 * len(dr)

    def test_minutes(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.minutes == 24 * 60 * len(dr)

    def test_seconds(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.seconds == 24 * 60 * 60 * len(dr)

    def test_dunder_contains(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert self.date_a + 1 in dr
        assert self.date_b not in dr

    def test_dunder_getitem(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr[0] == self.date_a  # pyright: ignore
        assert dr[1] == self.date_a + 1  # pyright: ignore
        assert dr[-1] == self.date_a + 3  # pyright: ignore
        with pytest.raises(IndexError):
            _ = dr[10]  # pyright: ignore

    def test_dunder_hash(self):
        dr = DateRange(self.date_a, self.date_b)
        assert isinstance(hash(dr), int)

    def test_dunder_init(self):
        dr = DateRange(self.date_a, self.date_b, step=1, inclusive=False)
        assert dr.start == self.date_a
        assert dr.stop == self.date_b

    def test_dunder_iter(self):
        dr = DateRange(self.date_a, self.date_a + 3)
        lst = list(dr)
        assert lst == [self.date_a, self.date_a + 1, self.date_a + 2]

    def test_dunder_len(self):
        dr = DateRange(self.date_a, self.date_b, step=1)
        assert len(dr) == 4
        dr2 = DateRange(self.date_b, self.date_a, step=-1)
        assert len(dr2) == 4

    def test_dunder_repr(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert repr(dr) == "DateRange(self.date_a, self.date_b, step=1)"

    def test_dunder_reversed(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        rev = reversed(dr)
        assert isinstance(rev, DateRange)
        assert rev.start == dr.last

    def test_gap(self) -> None:
        dr1 = DateRange(self.date_a, self.date_b)
        dr2 = DateRange(PLACEHOLDER, PLACEHOLDER)
        gap = dr1.gap(dr2)
        assert gap.start == self.date_b  # type: ignore
        assert gap.stop == PLACEHOLDER  # type: ignore

        overlap = dr1.gap(DateRange(self.date_a + 3, Date(6)))
        assert overlap is None

    def test_hull(self) -> None:
        dr1 = DateRange(self.date_a, self.date_b)
        dr2 = DateRange(self.date_a + 3, self.date_a + 10)
        hull = dr1.hull(dr2)
        assert hull.start == self.date_a
        assert hull.stop == self.date_a + 10

    def test_index_alt(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.index(self.date_a + 2) == 2
        with pytest.raises(ValueError):
            dr.index(PLACEHOLDER)

    def test_intersection_alt(self) -> None:
        dr1 = DateRange(self.date_a, self.date_b)
        dr2 = DateRange(self.date_a + 2, Date(7))
        inter = dr1.intersection(dr2)
        assert inter.start == self.date_a + 2  # type: ignore
        assert inter.stop == self.date_b  # type: ignore

        dr3 = DateRange(PLACEHOLDER, PLACEHOLDER)
        inter_none = dr1.intersection(dr3)
        assert inter_none is None

    def test_last_alt(self) -> None:
        dr = DateRange(self.date_a, self.date_b, step=1)
        assert dr.last == self.date_a + 3

    def test_count_alt(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.count(self.date_a + 1) == 1
        assert dr.count(PLACEHOLDER) == 0

    def test__increment(self):
        dr = DateRange(self.date_a, self.date_b)
        dr._current = PLACEHOLDER
        dr._increment()
        assert dr._current == 1

    @pytest.mark.parametrize(
        "start, stop, step, expected_len",
        [
            (date_a, date_b, 1, 4),
            (date_b, date_a, -1, 4),
            (date_a, date_a, 1, 0),
        ],
    )
    def test_len(self, start, stop, step, expected_len):
        dr = DateRange(start, stop, step=step)
        assert len(dr) == expected_len

    @pytest.mark.parametrize(
        "start, stop, step, expected",
        [
            (date_a, date_b, 1, [date_a, date_a + 1, date_a + 2, date_a + 3]),
            (date_b, date_a, -1, [date_b, date_a + 3, date_a + 2, date_a + 1]),
            (date_a, date_a, 1, []),
        ],
    )
    def test_iter(self, start, stop, step, expected):
        dr = DateRange(start, stop, step=step)
        assert list(dr) == expected

    @pytest.mark.parametrize(
        "dr, member, expected",
        [
            (DateRange(date_a, date_b), date_a + 2, True),
            (DateRange(date_a, date_b), date_b, False),
        ],
    )
    def test_contains(self, dr, member, expected):
        assert (member in dr) == expected

    @pytest.mark.parametrize(
        "index, expected",
        [
            (0, date_a),
            (1, date_a + 1),
            (2, date_a + 2),
            (3, date_a + 3),
            (-1, date_a + 3),
        ],
    )
    def test_getitem(self, index, expected):
        dr = DateRange(self.date_a, self.date_b)
        assert dr[index] == expected

    @pytest.mark.parametrize("index", [-5, 4, 10])
    def test_getitem_out_of_range(self, index):
        dr = DateRange(self.date_a, self.date_b)
        with pytest.raises(IndexError):
            _ = dr[index]

    def test_repr(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert repr(dr) == "DateRange(self.date_a, self.date_b, step=1)"

    def test_hash(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert isinstance(hash(dr), int)

    def test_with_end_and_without_end(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.with_end().inclusive is True
        assert dr.without_end().inclusive is False

    def test_last(self) -> None:
        dr = DateRange(self.date_a, self.date_b, step=1)
        assert dr.last == self.date_a + 3

    @pytest.mark.parametrize(
        "method, expected",
        [
            ("days", ...),
            ("hours", 24 * len(DateRange(date_a, date_b))),
            ("minutes", 24 * 60 * len(DateRange(date_a, date_b))),
            ("seconds", 24 * 60 * 60 * len(DateRange(date_a, date_b))),
        ],
    )
    def test_duration_properties(self, method, expected):
        dr = DateRange(self.date_a, self.date_b)
        assert getattr(dr, method) == expected

    def test_reversed(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        rev = reversed(dr)
        assert rev.start == dr.last  # type: ignore
        assert rev.stop == dr.start - 1  # type: ignore

    def test_count(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.count(self.date_a + 2) == 1
        assert dr.count(PLACEHOLDER) == 0

    def test_index(self) -> None:
        dr = DateRange(self.date_a, self.date_b)
        assert dr.index(self.date_a + 2) == 2
        with pytest.raises(ValueError):
            dr.index(PLACEHOLDER)

    def test_gap_and_hull(self) -> None:
        dr1 = DateRange(self.date_a, self.date_b)
        dr2 = DateRange(PLACEHOLDER, PLACEHOLDER)
        gap = dr1.gap(dr2)
        assert gap.start == self.date_b  # type: ignore
        assert gap.stop == PLACEHOLDER  # type: ignore

        overlap = dr1.gap(DateRange(self.date_a + 3, PLACEHOLDER))
        assert overlap is None

        hull = dr1.hull(DateRange(self.date_a + 3, PLACEHOLDER))
        assert hull.start == self.date_a
        assert hull.stop == PLACEHOLDER

    def test_intersection(self) -> None:
        dr1 = DateRange(self.date_a, self.date_b)
        dr2 = DateRange(self.date_a + 2, PLACEHOLDER)
        inter = dr1.intersection(dr2)
        assert inter.start == self.date_a + 2  # type: ignore
        assert inter.stop == self.date_b  # type: ignore

        dr3 = DateRange(PLACEHOLDER, PLACEHOLDER)
        assert dr1.intersection(dr3) is None

    def test__restart(self): ...

    def test_dunder_eq(self): ...

    def test_dunder_next(self): ...

    def test_filtered(self): ...

    def test_overlap(self): ...
