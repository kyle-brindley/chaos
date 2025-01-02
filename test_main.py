from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import numpy
import pytest

import main


@pytest.mark.parametrize(
    "x_current, r, x_next_expected",
    [
        (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 10.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, -10.0, 0.0),
        (1.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (-1.0, 0.0, 0.0),
        (-10.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (1.0, -1.0, 0.0),
        (-1.0, 1.0, -2.0),
        (-1.0, -1.0, 2.0),
        (0.5, 1.0, 0.25),
        (0.5, 0.5, 0.125),
        (0.5, -1.0, -0.25),
        (0.5, -0.5, -0.125),
    ],
)
def test_logistic(x_current, r, x_next_expected):
    assert main.logistic(x_current, r) == x_next_expected



@pytest.mark.parametrize(
    "curve, period, expected_first_period, expected_second_period, outcome",
    [
        (numpy.array([0., 0.]), 1, numpy.array([0.0]), numpy.array([0.0]), does_not_raise()),
        (numpy.array([0., 0.]), 2, None, None, pytest.raises(ValueError)),
        (numpy.array([0., 0., 0.]), 2, None, None, pytest.raises(ValueError)),
        (numpy.array([0., 0., 0., 0.]), 1, numpy.array([0.0]), numpy.array([0.0]), does_not_raise()),
        (numpy.array([0., 0., 1., 1.]), 1, numpy.array([1.0]), numpy.array([1.0]), does_not_raise()),
        (numpy.array([0., 1., 0., 1.]), 1, numpy.array([1.0]), numpy.array([0.0]), does_not_raise()),
        (numpy.array([0., 0., 0., 0.]), 2, numpy.array([0.0, 0.0]), numpy.array([0.0, 0.0]), does_not_raise()),
        (numpy.array([0., 1., 0., 1.]), 2, numpy.array([0.0, 1.0]), numpy.array([0.0, 1.0]), does_not_raise()),
        (numpy.array([0., 0., 0., 0., 0.]), 3, None, None, pytest.raises(ValueError)),
        (numpy.array([0., 0., 0., 0., 0., 0.]), 2, numpy.array([0.0, 0.0]), numpy.array([0.0, 0.0]), does_not_raise()),
        (numpy.array([0., 0., 1., 2., 1., 2.]), 2, numpy.array([1.0, 2.0]), numpy.array([1.0, 2.0]), does_not_raise()),
        (numpy.array([0., 1., 2., 0., 1., 2.]), 2, numpy.array([1.0, 2.0]), numpy.array([2.0, 0.0]), does_not_raise()),
        (numpy.array([0., 0., 0., 0., 0., 0.]), 3, numpy.array([0.0, 0.0, 0.0]), numpy.array([0.0, 0.0, 0.0]), does_not_raise()),
        (numpy.array([0., 1., 2., 0., 1., 2.]), 3, numpy.array([0.0, 1.0, 2.0]), numpy.array([0.0, 1.0, 2.0]), does_not_raise()),
    ],
)
def test_return_periods(
    curve, period, expected_first_period, expected_second_period, outcome
):
    with outcome:
        try:
            first_period, second_period = main.return_periods(curve, period=period)
            assert first_period.shape == second_period.shape
            assert numpy.allclose(first_period, expected_first_period)
            assert numpy.allclose(second_period, expected_second_period)
        finally:
            pass


@pytest.mark.parametrize(
    "curve, period, expected",
    [
        (numpy.array([0., 0.]), 1, True),
        (numpy.array([0., 0.]), 2, False),
        (numpy.array([0., 0., 0.]), 2, False),
        (numpy.array([0., 0., 0., 0.]), 1, True),
        (numpy.array([0., 0., 1., 1.]), 1, True),
        (numpy.array([0., 1., 0., 1.]), 1, False),
        (numpy.array([0., 0., 0., 0.]), 2, True),
        (numpy.array([0., 1., 0., 1.]), 2, True),
        (numpy.array([0., 0., 0., 0., 0.]), 3, False),
        (numpy.array([0., 0., 0., 0., 0., 0.]), 2, True),
        (numpy.array([0., 0., 1., 2., 1., 2.]), 2, True),
        (numpy.array([0., 1., 2., 0., 1., 2.]), 2, False),
        (numpy.array([0., 0., 0., 0., 0., 0.]), 3, True),
        (numpy.array([0., 1., 2., 0., 1., 2.]), 3, True),
    ],
)
def test_is_period_stable(curve, period, expected):
    assert main.is_period_stable(curve, period) == expected


def test_plot_states():
    # No output should raise plot window
    with (
        patch("matplotlib.pyplot.savefig") as mock_save_fig,
        patch("matplotlib.pyplot.show") as mock_show,
    ):
        main.plot_states([[1.0]], 1.0, output=None)
        mock_save_fig.assert_not_called()
        mock_show.assert_called_once()

    # Output should save the figure without plot window
    with (
        patch("matplotlib.pyplot.savefig") as mock_save_fig,
        patch("matplotlib.pyplot.show") as mock_show,
    ):
        main.plot_states([[1.0]], 1.0, output="dummy.png")
        mock_save_fig.assert_called_once()
        mock_show.assert_not_called()
