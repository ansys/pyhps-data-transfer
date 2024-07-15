import logging
import time

import backoff
import httpx
import urllib3

from .binary import Binary, BinaryConfig
from .exceptions import async_raise_for_status, raise_for_status

urllib3.disable_warnings()

httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.CRITICAL)

httpcore_log = logging.getLogger("httpcore")
httpcore_log.setLevel(logging.CRITICAL)

log = logging.getLogger(__name__)


class ClientBase:
    def __init__(
        self,
        bin_config: BinaryConfig = BinaryConfig(),
    ):
        self._bin_config = bin_config
        self.binary = None
        self.base_api_url = None

        if bin_config.external_url is not None:
            self.base_api_url = bin_config.external_url + "/api/v1"

    @property
    def binary_config(self):
        return self._bin_config

    def start(self):
        if self.binary is not None:
            return

        self.binary = Binary(config=self._bin_config)
        self.binary.start()
        self.base_api_url = self.binary.external_url + "/api/v1"

    def stop(self):
        if self.binary is None:
            return
        self.binary.stop()
        self.binary = None


class AsyncClient(ClientBase):
    def __init__(self):
        super().__init__()

    def start(self, verify: bool = True, token: str = None, **kwargs):
        super().start(**kwargs)
        self.session = httpx.AsyncClient(
            transport=httpx.AsyncHTTPTransport(retries=5, verify=verify),
            base_url=self.base_api_url,
            verify=verify,
            follow_redirects=True,
            event_hooks={"response": [async_raise_for_status]},
        )
        if token is not None:
            self.session.headers.setdefault("Authorization", f"Bearer {token}")


class Client(ClientBase):
    def __init__(self):
        super().__init__()

    def start(self, verify: bool = True, token: str = None, **kwargs):
        super().start(**kwargs)
        self.session = httpx.Client(
            transport=httpx.HTTPTransport(retries=5, verify=verify),
            base_url=self.base_api_url,
            verify=verify,
            follow_redirects=True,
            event_hooks={"response": [raise_for_status]},
        )
        if token is not None:
            self.session.headers.setdefault("Authorization", f"Bearer {token}")

    def wait(self, timeout: float = 60.0, sleep=0.5):
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = httpx.get(self.base_api_url)
                if resp.status_code != 200:
                    log.debug("Waiting for worker to start")
                else:
                    return
            except Exception as ex:
                if self._bin_config.debug:
                    log.debug(f"Error waiting for worker to start: {ex}")
            finally:
                time.sleep(backoff.full_jitter(sleep))
