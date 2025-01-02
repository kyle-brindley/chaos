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
):
    """Calculate a range of states"""
    stop_iterations = [max_iteration for initial_state in initial_states]
    state = [[0] * max_iteration for initial_state in initial_states]

    for row, initial_state in enumerate(initial_states):
        state[row][0] = initial_state
        for iteration in range(1, max_iteration):
            previous_iteration = iteration - 1
            state[row][iteration] = logistic(state[row][previous_iteration], parameter)
            if state[row][iteration] < 0.0 or math.isclose(
                state[row][iteration],
                state[row][previous_iteration],
                rel_tol=relative_tolerance,
            ):
                stop_iterations[row] = iteration
                break

    return state, stop_iterations


def get_parser():
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
        help="The maximum number of iterations to compute",
    )
    parser.add_argument(
        "-t",
        "--relative-tolerance",
        type=float,
        default=DEFAULT_RELATIVE_TOLERANCE,
        help="The relative tolerance used to compare floats",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    max_iteration = args.max_iteration
    stop_iteration = max_iteration
    parameter = args.parameter
    initial_states = args.initial
    relative_tolerance = args.relative_tolerance

    state, stop_iterations = calculate_states(
        initial_states,
        parameter,
        relative_tolerance=relative_tolerance,
        max_iteration=max_iteration,
    )

    for row, stop_iteration in enumerate(stop_iterations):
        matplotlib.pyplot.plot(
            state[row][: stop_iteration + 1], label=f"$x_{0}$: {state[row][0]}"
        )

    matplotlib.pyplot.title(
        r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$: r = "
        + f"{parameter}"
    )
    matplotlib.pyplot.legend(loc="lower right")
    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
