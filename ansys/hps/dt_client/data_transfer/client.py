import httpx

from .binary import Binary
from .exceptions import async_raise_for_status, raise_for_status


class ClientBase:
    def __init__(
        self,
        data_transfer_url: str,
        external_url: str = None,
        run_client_binary: bool = False,
        binary_path: str = None,
        verify: bool = True,
        token: str = None,
    ):
        if run_client_binary:
            self.binary = Binary(binary_path, data_transfer_url, external_url, token)
            external_url = self.binary.external_url
            self.base_api_url = external_url + "/api/v1"
        else:
            self.base_api_url = data_transfer_url

    def __enter__(self):
        if self.binary:
            self.binary.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.binary:
            self.binary.stop()


class AsyncClient(ClientBase):
    def __init__(
        self,
        data_transfer_url: str,
        external_url: str = None,
        run_client_binary: bool = False,
        binary_path: str = None,
        verify: bool = True,
        token: str = None,
    ):
        super().__init__(data_transfer_url, external_url, run_client_binary, binary_path, verify, token)
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
    def __init__(
        self,
        data_transfer_url: str,
        external_url: str = None,
        run_client_binary: bool = False,
        binary_path: str = None,
        verify: bool = True,
        token: str = None,
    ):
        super().__init__(data_transfer_url, external_url, run_client_binary, binary_path, verify, token)
        self.session = httpx.Client(
            transport=httpx.HTTPTransport(retries=5, verify=verify),
            base_url=self.base_api_url,
            verify=verify,
            follow_redirects=True,
            event_hooks={"response": [raise_for_status]},
        )
        if token is not None:
            self.session.headers.setdefault("Authorization", f"Bearer {token}")
