from math import isclose

import pytest

from datethyme.constants import Unit
from datethyme.exceptions import TemporalLogicError


class TestUnit:

    def test_as_dhms(self) -> None:
        NUM_A = 1.234567
        NUM_B = 99.99999
        NUM_C = 1436845

        assert Unit.DAY.as_dhms(NUM_A) == (1, 5, 37, 46.589)
        assert Unit.HOUR.as_dhms(NUM_A) == (0, 1, 14, 4.441)
        assert Unit.MINUTE.as_dhms(NUM_A) == (0, 0, 1, 14.074)
        assert Unit.SECOND.as_dhms(NUM_A) == (0, 0, 0, 1.235)

        assert Unit.DAY.as_dhms(NUM_B) == (99, 23, 59, 59.136)
        assert Unit.HOUR.as_dhms(NUM_B) == (4, 3, 59, 59.964)
        assert Unit.MINUTE.as_dhms(NUM_B) == (0, 1, 39, 59.999)
        assert Unit.SECOND.as_dhms(NUM_B) == (0, 0, 1, 40.0)

        assert Unit.DAY.as_dhms(NUM_C) == (1436845, 0, 0, 0.0)
        assert Unit.HOUR.as_dhms(NUM_C) == (59868, 13, 0, 0.0)
        assert Unit.MINUTE.as_dhms(NUM_C) == (997, 19, 25, 0.0)
        assert Unit.SECOND.as_dhms(NUM_C) == (16, 15, 7, 25.0)

    def test_n_in(self) -> None:
        assert Unit.DAY.n_in(Unit.DAY) == 1
        assert Unit.HOUR.n_in(Unit.DAY) == 24
        assert Unit.MINUTE.n_in(Unit.DAY) == 1440
        assert Unit.SECOND.n_in(Unit.DAY) == 86400

        assert Unit.HOUR.n_in(Unit.HOUR) == 1
        assert Unit.MINUTE.n_in(Unit.HOUR) == 60
        assert Unit.SECOND.n_in(Unit.HOUR) == 3600
    
        assert Unit.MINUTE.n_in(Unit.MINUTE) == 1
        assert Unit.SECOND.n_in(Unit.MINUTE) == 60

        assert Unit.SECOND.n_in(Unit.SECOND) == 1

    def test_has_n(self) -> None:
        assert Unit.DAY.has_n(Unit.DAY) == 1
        assert Unit.DAY.has_n(Unit.HOUR) == 24
        assert Unit.DAY.has_n(Unit.MINUTE) == 1440
        assert Unit.DAY.has_n(Unit.SECOND) == 86400

        assert Unit.HOUR.has_n(Unit.HOUR) == 1
        assert Unit.HOUR.has_n(Unit.MINUTE) == 60
        assert Unit.HOUR.has_n(Unit.SECOND) == 3600
    
        assert Unit.MINUTE.has_n(Unit.MINUTE) == 1
        assert Unit.MINUTE.has_n(Unit.SECOND) == 60

        assert Unit.SECOND.has_n(Unit.SECOND) == 1

    def test_wrt_superunit(self) -> None:
        assert Unit.HOUR.wrt_superunit(345) == (14, 9)
        assert Unit.MINUTE.wrt_superunit(345) == (5, 45)
        assert Unit.SECOND.wrt_superunit(345) == (5, 45)

        assert Unit.SECOND.wrt_superunit(65.5) == (1, 5.5)
        assert Unit.MINUTE.wrt_superunit(65.5) == (1, 5.5)
        assert Unit.HOUR.wrt_superunit(65.5) == (2, 17.5)

    def test_wrt_subunit(self) -> None:
        assert Unit.DAY.wrt_subunit(345) == 8280
        assert Unit.HOUR.wrt_subunit(345) == 20700
        assert Unit.MINUTE.wrt_subunit(345) == 20700

        assert Unit.DAY.wrt_subunit(1.5) == 36.0
        assert Unit.HOUR.wrt_subunit(1.5) == 90.0
        assert Unit.MINUTE.wrt_subunit(1.5) == 90.0

    def test_int_properties(self) -> None:
        assert Unit.DAY.hours_int == 24
        assert Unit.DAY.minutes_int == 1440

        assert Unit.HOUR.hours_int == 1
        assert Unit.HOUR.minutes_int == 60

        assert Unit.MINUTE.minutes_int == 1

    def test_int_properties_errors(self) -> None:
        with pytest.raises(TemporalLogicError):
            _ = Unit.SECOND.minutes_int

        with pytest.raises(TemporalLogicError):
            _ = Unit.SECOND.hours_int

        with pytest.raises(TemporalLogicError):
            _ = Unit.MINUTE.hours_int

    def test_float_properties(self) -> None:
        assert Unit.DAY.days == 1.0
        assert Unit.DAY.hours == 24.0
        assert Unit.DAY.minutes == 1440.0
        assert Unit.DAY.seconds == 86400.0

        assert isclose(Unit.HOUR.days, 1 / 24, abs_tol=1e-8)
        assert Unit.HOUR.hours == 1.0
        assert Unit.HOUR.minutes == 60.0
        assert Unit.HOUR.seconds == 3600.0

        assert isclose(Unit.MINUTE.days, 1 / 1440, abs_tol=1e-8)
        assert isclose(Unit.MINUTE.hours, 1 / 60, abs_tol=1e-8)
        assert Unit.MINUTE.minutes == 1.0
        assert Unit.MINUTE.seconds == 60.0

        assert isclose(Unit.SECOND.days, 1 / 86400, abs_tol=1e-8)
        assert isclose(Unit.SECOND.hours, 1 / 3600, abs_tol=1e-8)
        assert isclose(Unit.SECOND.minutes, 1 / 60, abs_tol=1e-8)
        assert Unit.SECOND.seconds == 1.0

    def test_roundtrip_to_milliseconds(self) -> None:
        def is_close_enough(f: float) -> bool:
            return isclose(f, 1.0, abs_tol=0.00001)
        
        assert is_close_enough(Unit.SECOND.days * Unit.DAY.seconds)
        assert is_close_enough(Unit.MINUTE.days * Unit.DAY.minutes)
        assert is_close_enough(Unit.SECOND.hours * Unit.HOUR.seconds)
        assert is_close_enough(Unit.MINUTE.hours * Unit.HOUR.minutes)
        assert is_close_enough(Unit.SECOND.minutes * Unit.MINUTE.seconds)
