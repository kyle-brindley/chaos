from unittest.mock import patch

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
