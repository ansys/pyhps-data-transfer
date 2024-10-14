from random import uniform


def get_expo_backoff(
    base: float, attempts: int = 1, cap: float = 100_000_000, attempts_cap: int = 100_000_000, jitter: bool = True
):
    """
    Returns a backoff value https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    :param base: The time to sleep in the first attempt.
    :param attempts: The number of attempts that have already been made.
    :param cap: The maximum value that can be returned.
    :param jitter: Whether or not to apply jitter to the returned value.
    """
    # Full jitter formula
    # https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    attempts = min(attempts, attempts_cap)
    if jitter:
        try:
            return uniform(base, min(cap, base * 2 ** (attempts - 1)))
        except OverflowError:
            return cap
    else:
        return min(cap, base * 2 ** (attempts - 1))
