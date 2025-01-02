import pytest

import main


@pytest.mark.parametrize(
    "x_current, r, x_next_expected",
    [
        (0., 1., 0.)
    ],
)
def test_logistic(x_current, r, x_next_expected):
    assert main.logistic(x_current, r) == x_next_expected
