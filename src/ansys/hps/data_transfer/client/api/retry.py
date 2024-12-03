# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import traceback

import backoff
import httpx

from ..exceptions import HPSError, NotReadyError, TimeoutError

log = logging.getLogger(__name__)


def _on_backoff(details, exc_info=True):
    try:
        msg = "Backing off {wait:0.1f} seconds after {tries} tries: {exception}".format(**details)
        log.info(msg)
        if exc_info:
            try:
                ex_str = "\n".join(traceback.format_exception(details["exception"]))
                log.debug(f"Backoff caused by:\n{ex_str}")
            except:
                pass
    except Exception as ex:
        log.warning(f"Failed to log in backoff handler: {ex}")


def _giveup(e):
    if isinstance(e, httpx.ConnectError):
        return False
    elif isinstance(e, TimeoutError):
        return True
    elif isinstance(e, NotReadyError):
        return False
    elif isinstance(e, HPSError) and e.give_up:
        return True
    elif isinstance(e, TypeError):
        return True

    return False


def retry(
    max_tries=20,
    max_time=60,
    raise_on_giveup=True,
    jitter=backoff.full_jitter,
):
    return backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=max_tries,
        max_time=max_time,
        jitter=jitter,
        raise_on_giveup=raise_on_giveup,
        on_backoff=_on_backoff,
        logger=None,
        giveup=_giveup,
    )
