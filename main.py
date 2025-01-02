import math
import typing
import pathlib
import argparse

import numpy
import matplotlib.pyplot


DESCRIPTION = """Calculate and plot the logistic function:
`x_{next} = r * x_{current} * (1 - x_{current})`"
"""
DEFAULT_MAX_ITERATION = 100
DEFAULT_RELATIVE_TOLERANCE = 1e-4
DEFAULT_MAX_PERIOD = 12


def logistic(x: float, r: float) -> float:
    r"""Return the next value in the logistic function give the current value

    .. math

       x_{next} = r x_{current} \left ( 1 - x_{current} \right )

    :param x: The current :math:`x_{current}` value of the logistic function
    :param r: The parameter :math:`r` value of the logistic function
    """
    return r * x * (1 - x)


def return_periods(
    curve: numpy.ndarray,
    period: int = 1,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """Return last two periods from curve

    Period indicates number of values in a series, e.g. period 1 returns the
    last two values [2] and [3] of [1, 2, 3] and period 5 means two series of
    length 5 [2-6], and [7-11] from [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].

    :param curve: numpy vector of values to evaluate for period stability
    :param period: number of repeated values

    :returns: two numpy vectors of lengths equal to the period
    """
    if len(curve) < 2 * period:
        raise ValueError(f"Curve does not have enough points for period {period}")
    first_period_start = -period
    second_period_start = first_period_start - period
    second_period_end = first_period_start
    first_period = curve[first_period_start:]
    second_period = curve[second_period_start:second_period_end]
    return first_period, second_period


def is_period_stable(
    curve: numpy.ndarray,
    period: int = 1,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
) -> bool:
    """Return boolean for period stability

    Period indicates number of repeating values that are equal, e.g. period 1
    means two values in a row are equal [1, 1] and period 5 means two series of
    length 5 are equal [1, 2, 3, 4, 5, 1, 2, 3, 4, 5].

    :param curve: numpy vector of values to evaluate for period stability
    :param period: number of repeated values
    :param relative_tolerance: the relative tolerance on float equality
        comparisons

    :returns: boolean indicating that the curve ends in a period
    """
    try:
        first_period, second_period = return_periods(curve, period=period)
    except ValueError as err:
        return False
    return numpy.allclose(
        first_period,
        second_period,
        rtol=relative_tolerance,
    )


def stable_period(
    curve: numpy.ndarray,
    max_period: int = DEFAULT_MAX_PERIOD,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
) -> int:
    """Return the stable period or None

    :param curve: numpy vector of values to evaluate for period stability
    :param max_period: maximum number of repeated values to search for
    :param relative_tolerance: the relative tolerance on float equality
        comparisons

    :returns: the stable period for the curve
    """
    for period in range(1, max_period + 1):
        if is_period_stable(
            curve, period=period, relative_tolerance=relative_tolerance
        ):
            return period
    else:
        return None


def calculate_states(
    initial_states: list[float],
    parameter: float,
    max_period: int = DEFAULT_MAX_PERIOD,
    max_iteration: float = DEFAULT_MAX_ITERATION,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
) -> tuple[numpy.ndarray, list]:
    """Calculate a range of logistic function results from initial states

    Returns an array of logistic function evaluations from initial states and
    the logistic function parameter. Exits the calculation early if the function
    state stabilizes, leaving NaN where calculation was discontinued.

    Implemented "stable" exit conditions:

    * Calculation returns a negative number
    * Calculation returns the same number as input within the relative tolerance

    :param initial_states: list of initial states :math:`x_{0}`
    :param parameter: logistic function parameter :math:`r`
    :param relative_tolerance: the relative tolerance on float equality
        comparisons
    :param max_iteration: the maximum number of iterations to compute

    :returns: an array of evaluated logistic function results from the initial
        states and logistic function parameter and a list of the associated
        periods
    """
    states = numpy.full(
        (len(initial_states), max_iteration),
        numpy.nan,
    )
    periods = numpy.full((len(initial_states),), None)

    for row, initial_state in enumerate(initial_states):
        states[row][0] = initial_state
        for iteration in range(1, max_iteration):
            previous_iteration = iteration - 1
            states[row][iteration] = logistic(
                states[row][previous_iteration], parameter
            )
            periods[row] = stable_period(
                states[row][:iteration],
                max_period=max_period,
                relative_tolerance=relative_tolerance,
            )
            if states[row][iteration] < 0.0 or periods[row] is not None:
                break

    period = periods[0] if numpy.all(periods == periods[0]) else None

    return states, period


def plot_states(
    states: numpy.ndarray,
    parameter: float,
    period: typing.Optional[int] = None,
    output: typing.Optional[pathlib.Path] = None,
) -> None:
    """Plot the logistic function results from :meth:`calculate_states`

    :param states: Array of logistic function calculations with dimensions
        [curve, iteration]
    :param parameter: logistic function parameter :math:`r`
    :param filepath: save to file instead of raising a plot window
    """
    for curve in states:
        matplotlib.pyplot.plot(curve, label=f"$x_{0}$: {curve[0]}")

    matplotlib.pyplot.title(
        r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$: r = "
        + f"{parameter}, period = {period}"
    )
    matplotlib.pyplot.legend(loc="lower right")
    if output is not None:
        matplotlib.pyplot.savefig(output)
    else:
        matplotlib.pyplot.show()


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--initial",
        nargs="+",
        type=float,
        required=True,
        help="The initial state: `x_{0}`",
    )
    parser.add_argument(
        "--parameter",
        type=float,
        required=True,
        help="The logistic function parameter: `r`)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=None,
        help="The output plot absolute or relative path",
    )
    parser.add_argument(
        "-n",
        "--max-period",
        type=int,
        default=DEFAULT_MAX_PERIOD,
        help="The maximum number of periods to search for",
    )
    parser.add_argument(
        "-m",
        "--max-iteration",
        type=int,
        default=DEFAULT_MAX_ITERATION,
        help="The maximum number of iterations to calculate",
    )
    parser.add_argument(
        "-t",
        "--relative-tolerance",
        type=float,
        default=DEFAULT_RELATIVE_TOLERANCE,
        help="The relative tolerance on float equality comparisons",
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    initial_states = args.initial
    parameter = args.parameter
    output = args.output
    max_period = args.max_period
    max_iteration = args.max_iteration
    relative_tolerance = args.relative_tolerance

    states, period = calculate_states(
        initial_states,
        parameter,
        max_period=max_period,
        max_iteration=max_iteration,
        relative_tolerance=relative_tolerance,
    )

    plot_states(
        states,
        parameter,
        period=period,
        output=output,
    )


if __name__ == "__main__":
    main()
