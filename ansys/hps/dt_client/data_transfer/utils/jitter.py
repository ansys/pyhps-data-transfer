from random import randint


def get_expo_backoff(base: int, attempts: int = 1, cap: int = 100_000_000, jitter: bool = True):
    """
    Returns a backoff value https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    :param base: The time to sleep in the first attempt.
    :param attempts: The number of attempts that have already been made.
    :param cap: The maximum value that can be returned.
    :param jitter: Whether or not to apply jitter to the returned value.
    """
    # Full jitter formula
    # https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    if jitter:
        return randint(base, min(cap, base * 2 ** (attempts - 1)))
    else:
        return min(cap, base * 2 ** (attempts - 1))
