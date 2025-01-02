import math
import argparse

import matplotlib.pyplot


DESCRIPTION = """Calculate and plot the logistic function:
`x_{next} = r * x_{current} * (1 - x_{current})`"
"""
DEFAULT_MAX_ITERATION = 10000


def logistic(x: float, r: float):
    r"""Return the next value in the logistic function give the current value

    .. math

       x_{next} = r x_{current} \left ( 1 - x_{current} \right )

    :param x: The current :math:`x_{current}` value of the logistic function
    :param r: The parameter :math:`r` value of the logistic function
    """
    return r * x * (1 - x)


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
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    max_iteration = args.max_iteration
    stop_iteration = max_iteration
    parameter = args.parameter
    initial_states = args.initial

    for initial_state in initial_states:
        state = [0] * max_iteration
        state[0] = initial_state
        for iteration in range(1, max_iteration):
            previous_iteration = iteration - 1
            state[iteration] = logistic(state[previous_iteration], parameter)
            if state[iteration] < 0.0 or math.isclose(
                state[iteration], state[previous_iteration]
            ):
                stop_iteration = iteration
                break

        matplotlib.pyplot.plot(state[:stop_iteration + 1], label=f"$x_{0}$: {initial_state}")

    matplotlib.pyplot.title(r"$x_{next} = r x_{current} \left ( 1 - x_{current} \right )$: r = " + f"{parameter}")
    matplotlib.pyplot.legend(loc="lower right")
    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
