import math
import argparse

import matplotlib.pyplot


DESCRIPTION = """Calculate and plot the logistic function:
`x_{next} = r * x_{current} * (1 - x_{current})`"
"""
DEFAULT_MAX_ITERATION = 100
DEFAULT_RELATIVE_TOLERANCE = 1e-4


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
    parameter: float,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
    max_iteration: float = DEFAULT_MAX_ITERATION,
) -> list[list[float]]:
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
        states and logistic function parameter
    """
    states = [[math.nan] * max_iteration for initial_state in initial_states]

    for row, initial_state in enumerate(initial_states):
        states[row][0] = initial_state
        for iteration in range(1, max_iteration):
            previous_iteration = iteration - 1
            states[row][iteration] = logistic(states[row][previous_iteration], parameter)
            if (
                # fmt: off
                states[row][iteration] < 0.0
                or math.isclose(
                    states[row][iteration],
                    states[row][previous_iteration],
                    rel_tol=relative_tolerance,
                )
                # fmt: on
            ):
                break

    return states


def plot_states(states: list[list[float]], parameter: float) -> None:
    """Plot the logistic function results from :meth:`calculate_states`

    :param states: Array of logistic function calculations with dimensions
        [curve, iteration]
    :param parameter: logistic function parameter :math:`r`
    """
    for curve in states:
        matplotlib.pyplot.plot(curve, label=f"$x_{0}$: {curve[0]}")

    matplotlib.pyplot.title(
        r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$: r = "
        + f"{parameter}"
    )
    matplotlib.pyplot.legend(loc="lower right")
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
        "-m",
        "--max-iteration",
        type=int,
        default=DEFAULT_MAX_ITERATION,
        help="The relative tolerance on float equality comparisons",
    )
    parser.add_argument(
        "-t",
        "--relative-tolerance",
        type=float,
        default=DEFAULT_RELATIVE_TOLERANCE,
        help="The relative tolerance used to compare floats",
    )
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    max_iteration = args.max_iteration
    parameter = args.parameter
    initial_states = args.initial
    relative_tolerance = args.relative_tolerance

    states = calculate_states(
        initial_states,
        parameter,
        relative_tolerance=relative_tolerance,
        max_iteration=max_iteration,
    )

    plot_states(states, parameter)


if __name__ == "__main__":
    main()
