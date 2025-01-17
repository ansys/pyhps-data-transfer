import logging
import os

import backoff
import httpx

from ..exceptions import HPSError, NotReadyError, TimeoutError

log = logging.getLogger(__name__)

max_tries_env_name = "ANSYS_DT_CLIENT_RETRY_MAX_TIME"
max_time_env_name = "ANSYS_DT_CLIENT_RETRY_MAX_TRIES"


def _on_backoff(details, exc_info=True, traceback=False):
    try:
        msg = "Backing off {wait:0.1f} seconds after {tries} tries: {exception}".format(**details)
        log.info(msg)
        if exc_info:
            try:
                if traceback:
                    ex_str = "\n".join(traceback.format_exception(details["exception"]))
                else:
                    ex_str = str(details["exception"]).strip()
                log.debug(f"Backoff caused by: {ex_str}")
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


def _lookup_max_time():
    v = os.getenv(max_time_env_name)
    if v is not None:
        return v
    return 300


def _lookup_max_tries():
    v = os.getenv(max_tries_env_name)
    if v is not None:
        return v
    return 40


def retry(
    max_tries=_lookup_max_tries,
    max_time=_lookup_max_time,
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
