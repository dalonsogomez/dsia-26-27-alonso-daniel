import pytest

from calculator import add, clamp, divide


def test_add():
    assert add(2, 3) == 5


def test_divide():
    assert divide(10, 4) == 2.5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


@pytest.mark.parametrize(
    ("value", "low", "high", "expected"),
    [
        (5, 0, 10, 5),
        (-1, 0, 10, 0),
        (99, 0, 10, 10),
    ],
)
def test_clamp(value, low, high, expected):
    assert clamp(value, low, high) == expected


def test_clamp_invalid_bounds():
    with pytest.raises(ValueError):
        clamp(1, 10, 0)
