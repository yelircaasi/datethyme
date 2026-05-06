from math import isclose


class HelperMixin:
    @staticmethod
    def assert_almost_equal(a: float | int, b: float | int) -> None:
        assert isclose(a, b)
