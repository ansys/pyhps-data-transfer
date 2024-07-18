import logging
import traceback

import backoff

log = logging.getLogger(__name__)


def _on_backoff(details, exc_info=False):
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


def retry():
    return backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=60,
        jitter=backoff.full_jitter,
        raise_on_giveup=True,
        on_backoff=_on_backoff,
        logger=None,
    )
