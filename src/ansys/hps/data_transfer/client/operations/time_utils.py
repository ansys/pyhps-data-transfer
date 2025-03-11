# Copyright (C) 2023 - 2024 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.

import logging
from random import uniform
import time

log = logging.getLogger(__name__)


def duration_string(start_time):
    # return str(datetime.timedelta(seconds = time.time() - start_time))

    seconds = time.time() - start_time
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    result = ""
    if hours:
        result += "%sh " % int(hours)
    if minutes:
        result += "%smin " % int(minutes)
    result += "%.3fsec" % seconds
    return result


class TimeMe(object):
    completion_only = True
    silent = False

    def __init__(self, title):
        self.start_time = None
        self.title = title

    def __enter__(self):
        if self.silent:
            return
        if not self.completion_only:
            log.debug("%s ... " % self.title)
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        if not self.silent:
            log.debug("%s took %s" % (self.title, duration_string(self.start_time)))


def _exponential_backoff(attempts, max_backoff: int, min_backoff: int) -> None:
    return uniform(min_backoff, min(max_backoff, min_backoff * (2**attempts)))


def exponential_backoff(attempts, max_backoff: int, min_backoff: int = 0.1, sleep: bool = True) -> None:
    sleep_secs = _exponential_backoff(attempts, max_backoff, min_backoff)
    if sleep:
        time.sleep(sleep_secs)
    return sleep_secs
