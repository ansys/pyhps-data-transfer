import os
import sys

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
        port: int = 1091,
    ):
        if binary_path is None:
            bin_ext = ".exe" if sys.platform == "win32" else ""
            binary_path = os.path.join("bin", f"hpsdata{bin_ext}")

        if run_client_binary:
            self.binary = Binary(binary_path, data_transfer_url, external_url, token, port=port)
            external_url = self.binary.external_url
            self.base_api_url = external_url + "/api/v1"
        else:
            self.binary = None
            # self.base_api_url = data_transfer_url
            self.base_api_url = external_url or f"http://localhost:1091/api/v1"

    def start(self):
        if not self.binary:
            return
        self.binary.start()

    def stop(self):
        if self.binary:
            self.binary.stop()

    def __enter__(self):
        # if self.binary:
        #     self.binary.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        # if self.binary:
        #     self.binary.stop()


class AsyncClient(ClientBase):
    def __init__(
        self,
        data_transfer_url: str,
        external_url: str = None,
        run_client_binary: bool = False,
        binary_path: str = None,
        verify: bool = True,
        token: str = None,
        port: int = 1091,
    ):
        super().__init__(data_transfer_url, external_url, run_client_binary, binary_path, verify, token, port)
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
        port: int = 1091,
    ):
        super().__init__(data_transfer_url, external_url, run_client_binary, binary_path, verify, token, port)
        self.session = httpx.Client(
            transport=httpx.HTTPTransport(retries=5, verify=verify),
            base_url=self.base_api_url,
            verify=verify,
            follow_redirects=True,
            event_hooks={"response": [raise_for_status]},
        )
        if token is not None:
            self.session.headers.setdefault("Authorization", f"Bearer {token}")
