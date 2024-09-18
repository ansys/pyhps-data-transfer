import logging

import httpx

from ansys.hps.data_transfer.client.api.retry import retry
from ansys.hps.data_transfer.client.exceptions import HPSError, NotReadyError, TimeoutError, raise_for_status

log = logging.getLogger(__name__)


class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value


def test_retry_not_ready(client, storage_path):
    count = Counter()

    @retry(max_time=1, max_tries=2, raise_on_giveup=False)
    def test_func(count):
        count.increment()
        raise NotReadyError("Not ready")

    test_func(count)

    assert count.value > 0


def test_retry_timeout_error(client, storage_path):
    count = Counter()

    @retry(max_time=1, max_tries=20, raise_on_giveup=False)
    def test_func(count):
        count.increment()
        raise TimeoutError("Timeout")

    test_func(count)

    # Should give up immediately
    assert count.value == 1


def test_retry_hpserror_giveup(client, storage_path):
    count = Counter()

    @retry(max_time=1, max_tries=20, raise_on_giveup=False)
    def test_func(count):
        count.increment()
        raise HPSError("HPSError", give_up=True)

    test_func(count)

    # Should give up immediately
    assert count.value == 1


def test_give_up_status(client, storage_path):
    count = Counter()

    @retry(max_time=1, max_tries=20, raise_on_giveup=False)
    def test_func(count, code):
        resp = httpx.Response(status_code=code, request=httpx.Request("GET", "http://localhost"))
        raise_for_status(resp)
        count.increment()

    give_up_on = [401, 403]
    codes = give_up_on + [200, 202]
    for code in codes:
        test_func(count, code)

    # Should give up immediately
    assert count.value == len(give_up_on)
