import matplotlib.pyplot


def logistic(x: float, r: float):
    r"""Return the next value in the logistic function give the current value

    .. math

       x_{next} = r x_{current} \left ( 1 - x_{current} \right )

    :param x: The current :math:`x_{current}` value of the logistic function
    :param r: The parameter :math:`r` value of the logistic function
    """
    return r * x * (1 - x)


def main():
    max_iteration = 100
    parameter = 1.0
    initial_state = 0.5

    state = [0] * max_iteration
    state[0] = initial_state
    for iteration in range(1, max_iteration):
        state[iteration] = logistic(state[iteration - 1], parameter)

    matplotlib.pyplot.plot(state)
    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
