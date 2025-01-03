import typing
import pathlib
import argparse

import numpy
import xarray
import matplotlib.pyplot


DESCRIPTION = """Calculate and plot the logistic function:
`x_{next} = r * x_{current} * (1 - x_{current})`"
"""
DEFAULT_MAX_ITERATION = 100
DEFAULT_RELATIVE_TOLERANCE = 1e-4
DEFAULT_MAX_PERIOD = 12


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        nargs="+",
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


def logistic(x: float, r: float) -> float:
    r"""Return the next value in the logistic function give the current value

    .. math

       x_{next} = r x_{current} \left ( 1 - x_{current} \right )

    :param x: The current :math:`x_{current}` value of the logistic function
    :param r: The parameter :math:`r` value of the logistic function
    """
    return r * x * (1 - x)


def calculate_states(
    initial_states: list[float],
    parameters: list[float],
    max_period: int = DEFAULT_MAX_PERIOD,
    max_iteration: float = DEFAULT_MAX_ITERATION,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
) -> tuple[numpy.ndarray, list]:
    """Calculate a range of logistic function results from initial states

    Returns an array of logistic function evaluations from initial state(s) and
    the logistic function parameter(s). Exits the calculation early if the
    function state stabilizes, leaving NaN where calculation was discontinued.

    Implemented "stable" exit conditions:

    * Calculation returns a negative number
    * Calculation returns the same number as input within the relative tolerance

    :param initial_states: list of initial states :math:`x_{0}`
    :param parameters: list of logistic function parameters :math:`r`
    :param relative_tolerance: the relative tolerance on float equality
        comparisons
    :param max_iteration: the maximum number of iterations to compute

    :returns: an array of evaluated logistic function results from the initial
        states and logistic function parameters
    """
    states = numpy.full(
        (len(parameters), len(initial_states), max_iteration),
        numpy.nan,
    )
    states[:, :, 0] = initial_states
    parameter_periods = [None] * len(parameters)

    for depth, parameter in enumerate(parameters):
        for iteration in range(1, max_iteration):
            previous_iteration = iteration - 1
            states[depth, :, iteration] = logistic(
                states[depth, :, previous_iteration], parameter
            )
            periods = [
                stable_period(
                    states[depth, row, :iteration],
                    max_period=max_period,
                    relative_tolerance=relative_tolerance,
                )
                for row in range(len(initial_states))
            ]
            period = periods[0] if numpy.all(periods) else None
            if numpy.any(states[depth, :, iteration] < 0.0) or period is not None:
                parameter_periods[depth] = period
                break

    data = xarray.Dataset(
        data_vars={
            "value": (["r", "x_0", "iteration"], states),
            "period": (["r"], parameter_periods),
        },
        coords={
            "r": parameters,
            "x_0": initial_states,
            "iteration": range(max_iteration),
        }
    )

    return states, parameter_periods


def plot_states(
    states: numpy.ndarray,
    parameters: list[float],
    periods: typing.Optional[list[float]] = None,
    output: typing.Optional[pathlib.Path] = None,
) -> None:
    """Plot the logistic function results from :meth:`calculate_states`

    :param states: Array of logistic function calculations with dimensions
        [curve, iteration]
    :param parameters: vector of logistic function parameters :math:`r`
    :param filepath: save to file instead of raising a plot window
    """
    for depth, (parameter, period) in enumerate(zip(parameters, periods)):
        for curve in states[depth]:
            matplotlib.pyplot.plot(
                curve,
                label=f"$r$: {parameter}; $x_{0}$: {curve[0]}; $period$: {period}",
            )

    matplotlib.pyplot.title(
        r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$"
    )
    matplotlib.pyplot.legend(loc="lower right")
    if output is not None:
        matplotlib.pyplot.savefig(output)
    else:
        matplotlib.pyplot.show()


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    initial_states = args.initial
    parameters = args.parameter
    output = args.output
    max_period = args.max_period
    max_iteration = args.max_iteration
    relative_tolerance = args.relative_tolerance

    states, periods = calculate_states(
        initial_states,
        parameters,
        max_period=max_period,
        max_iteration=max_iteration,
        relative_tolerance=relative_tolerance,
    )

    plot_states(
        states,
        parameters,
        periods=periods,
        output=output,
    )


if __name__ == "__main__":
    main()
