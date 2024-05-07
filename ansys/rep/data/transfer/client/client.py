from ansys.rep.data.transfer.client.exceptions import raise_for_status

from ansys.rep.data.transfer.client.binary import Binary

import httpx

class Client():
    def __init__(
        self,
        dts_url: str,
        dtsc_url: str,
        run_client_binary: bool = False,
        verify: bool = True,
        sync: bool = True
    ):
        if run_client_binary:
            self.binary = Binary(dts_url, dtsc_url)
        
        dtsc_api_url = dtsc_url + "/api/v1"

        if sync:
            self.session = httpx.Client(
                transport=httpx.HTTPTransport(retries=5, verify=verify),
                base_url=dtsc_api_url,
                verify=verify,
                follow_redirects=True,
                event_hooks={"response": [raise_for_status]},
            )
        else:
            self.session = httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=5, verify=verify),
                base_url=dtsc_api_url,
                verify=verify,
                follow_redirects=True,
                event_hooks={"response": [raise_for_status]},
            )

    def __enter__(self):
        if self.binary:
            self.binary.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.binary:
            self.binary.stop()
