import typing
import pathlib
import argparse
import itertools

import numpy
import xarray
import matplotlib.pyplot

from chaos import __version__


DESCRIPTION = """Calculate and plot the logistic function:
`x_{next} = r * x_{current} * (1 - x_{current})`"
"""
DEFAULT_MAX_ITERATION = 1000
DEFAULT_RELATIVE_TOLERANCE = 1e-6
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
    # TODO: Add a CLI option to specify a continuous range of parameters
    parser.add_argument(
        "--parameter",
        nargs="+",
        type=float,
        required=True,
        help="The logistic function parameter: `r`)",
    )
    parser.add_argument(
        "--parameter-arange",
        nargs=3,
        type=float,
        action="append",
        help="Specify range of parameters [start, stop, step]",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=None,
        help="Save the calculations to a HDF5 file",
    )
    parser.add_argument(
        "--plot-curves",
        nargs="?",
        type=pathlib.Path,
        default=False,
        const=None,
        help="Use as a flag to open the plot window or provide a file path",
    )
    parser.add_argument(
        "--plot-bifurcation",
        nargs="?",
        type=pathlib.Path,
        default=False,
        const=None,
        help="Use as a flag to open the plot window or provide a file path",
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
    # TODO: add an option to force computation to the full max iterations
    parser.add_argument(
        "-t",
        "--relative-tolerance",
        type=float,
        default=DEFAULT_RELATIVE_TOLERANCE,
        help="The relative tolerance on float equality comparisons",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=__version__,
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


def calculate_curves(
    initial_states: list[float],
    parameters: typing.Iterable[float],
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
    * Calculation returns the same number as input within relative tolerance
    * Two repeated series of up to length ``max_period`` exist

    :param initial_states: list of initial states :math:`x_{0}`
    :param parameters: list of logistic function parameters :math:`r`
    :param max_period: the maximum period to search for in the curve
    :param max_iteration: the maximum number of iterations to compute
    :param relative_tolerance: the relative tolerance on float equality
        comparisons

    :returns: an array of evaluated logistic function results from the initial
        states and logistic function parameters
    """
    states = numpy.full(
        (len(parameters), len(initial_states), max_iteration),
        numpy.nan,
    )
    states[:, :, 0] = initial_states
    parameter_periods = [None] * len(parameters)

    # TODO: Build the xarray dataset first, then operate on its contents
    # Counter option: Cython-ize the function calculations. I think this is
    # possible as a numpy array, but maybe not as an xarray dataset.
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
            # TODO: add an option to force computation to the full max
            # iterations
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
        },
    )

    return data


def matplotlib_output(
    title: str,
    output: typing.Optional[pathlib.Path] = None,
) -> None:
    """Attach matplotlib meta and plot or save figure

    :param title: Title of matplotlib plot
    :param output: save to file instead of raising a plot window
    """
    matplotlib.pyplot.title(title)
    if output is not None:
        matplotlib.pyplot.savefig(output)
    else:
        matplotlib.pyplot.show()


def plot_curves(
    data: xarray.Dataset,
    output: typing.Optional[pathlib.Path] = None,
) -> None:
    """Plot the logistic function results from :meth:`calculate_curves`

    :param data: XArray Dataset of logistic function calculations
    :param output: save to file instead of raising a plot window
    """
    line_styles = itertools.cycle(["-", "--", "-.", ":"])
    labels = [
        f"$r$={point['r'].item()}, $period$={point.item()}" for point in data["period"]
    ]
    for initial_state in data["x_0"]:
        lines = matplotlib.pyplot.gca().set_prop_cycle(None)
        xarray.plot.line(
            data["value"].sel({"x_0": initial_state}),
            x="iteration",
            hue="r",
            linestyle=next(line_styles),
        )
        matplotlib.pyplot.legend(
            handles=lines,
            labels=labels,
            loc="lower right",
        )

    title = r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$"
    matplotlib_output(title, output=output)


def plot_bifurcation(
    data: xarray.Dataset,
    output: typing.Optional[pathlib.Path] = None,
) -> None:
    """Plot the bifurcation periods of function calculations

    :param data: XArray Dataset of logistic function calculations
    :param output: save to file instead of raising a plot window
    """
    # NOTE: assumes that initial states result in the same period
    initial_state = data["x_0"][0]

    # TODO: Move bifurcation calculation to dedicated function
    bifurcation_data = list()
    for point in data["period"]:
        period = point.item()
        parameter = point["r"].item()
        series = data["value"].sel({"r": parameter, "x_0": initial_state}).to_pandas()
        vector = series[series.first_valid_index() : series.last_valid_index()]
        if period is not None:
            bifurcation_data.append(vector[-period:])
        else:
            bifurcation_data.append(vector)

    for period, bifurcation in zip(data["r"].values, bifurcation_data):
        matplotlib.pyplot.scatter(
            x=[period] * len(bifurcation), y=bifurcation, marker=".", color="b"
        )

    title = r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$"
    matplotlib_output(title, output=output)


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    initial_states = args.initial
    max_period = args.max_period
    max_iteration = args.max_iteration
    relative_tolerance = args.relative_tolerance

    parameters = numpy.array(args.parameter)
    if args.parameter_arange is not None:
        for arange_args in args.parameter_arange:
            parameters = numpy.concatenate((parameters, numpy.arange(*arange_args)))
    parameters = numpy.unique(parameters)

    data = calculate_curves(
        initial_states,
        parameters,
        max_period=max_period,
        max_iteration=max_iteration,
        relative_tolerance=relative_tolerance,
    )

    if args.plot_curves is not False:
        plot_curves(data, output=args.plot_curves)
    if args.plot_bifurcation is not False:
        plot_bifurcation(data, output=args.plot_bifurcation)

    if args.output:
        data.to_netcdf(args.output, engine="h5netcdf")


if __name__ == "__main__":
    main()
