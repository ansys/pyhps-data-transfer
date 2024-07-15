import httpx
import urllib3

from .binary import Binary, BinaryConfig
from .exceptions import async_raise_for_status, raise_for_status

urllib3.disable_warnings()


class ClientBase:
    def __init__(
        self,
        bin_config: BinaryConfig = BinaryConfig(),
    ):
        self._bin_config = bin_config
        self.binary = None

    @property
    def binary_config(self):
        return self._bin_config

    def start(self, wait: float = None, sleep: float = 0.5):
        if self.binary is not None:
            return

        self.binary = Binary(config=self._bin_config)
        self.binary.start(wait=wait, sleep=sleep)
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
