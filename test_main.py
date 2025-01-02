import pytest

import main


@pytest.mark.parametrize(
    "x_current, r, x_next_expected",
    [
        (0., 0., 0.),
        (0., 1., 0.),
        (0., 10., 0.),
        (0., -1., 0.),
        (0., -10., 0.),
        (1., 0., 0.),
        (10., 0., 0.),
        (-1., 0., 0.),
        (-10., 0., 0.),
        (1., 1., 0.),
        (1., -1., 0.),
        (-1., 1., -2.),
        (-1., -1., 2.),
        (0.5, 1., 0.25),
        (0.5, 0.5, 0.125),
        (0.5, -1., -0.25),
        (0.5, -0.5, -0.125),
    ],
)
def test_logistic(x_current, r, x_next_expected):
    assert main.logistic(x_current, r) == x_next_expected
