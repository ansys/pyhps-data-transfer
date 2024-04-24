from openapi_client import ApiClient, Configuration

from ansys.rep.data.transfer.client.binary import Binary


class Client(ApiClient):
    def __init__(
        self,
        dts_url: str,
        dtsc_url: str,
        run_client_binary: bool = False,
    ):
        config = Configuration.get_default()
        config.host = dtsc_url + "/api/v1"
        super().__init__(configuration=config)
        if run_client_binary:
            self.binary = Binary(dts_url, dtsc_url)

    def __enter__(self):
        super().__enter__()
        if self.binary:
            self.binary.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        if self.binary:
            self.binary.stop()
