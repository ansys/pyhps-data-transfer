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
