import httpx

from ansys.rep.data.transfer.client.binary import Binary
from ansys.rep.data.transfer.client.exceptions import async_raise_for_status, raise_for_status


class ClientBase:
    def __init__(
        self, dts_url: str, dtsc_url: str, run_client_binary: bool = False, verify: bool = True
    ):
        if run_client_binary:
            self.binary = Binary(dts_url, dtsc_url)

        self.dtsc_api_url = dtsc_url + "/api/v1"

    def __enter__(self):
        if self.binary:
            self.binary.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.binary:
            self.binary.stop()

class AsyncClient(ClientBase):
    def __init__(
        self, dts_url: str, dtsc_url: str, run_client_binary: bool = False, verify: bool = True
    ):
        super().__init__(dts_url, dtsc_url, run_client_binary, verify)
        self.session = httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=5, verify=verify),
                base_url=self.dtsc_api_url,
                verify=verify,
                follow_redirects=True,
                event_hooks={"response": [async_raise_for_status]},
        )

class Client(ClientBase):
    def __init__(
        self, dts_url: str, dtsc_url: str, run_client_binary: bool = False, verify: bool = True
    ):
        super().__init__(dts_url, dtsc_url, run_client_binary, verify)
        self.session = httpx.Client(
                transport=httpx.HTTPTransport(retries=5, verify=verify),
                base_url=self.dtsc_api_url,
                verify=verify,
                follow_redirects=True,
                event_hooks={"response": [raise_for_status]},
        )