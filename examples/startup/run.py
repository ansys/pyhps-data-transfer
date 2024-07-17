import json
import logging
import time

from ansys.hps.dt_client.data_transfer import Client, DataTransferApi
from ansys.hps.dt_client.data_transfer.authenticate import authenticate

log = logging.getLogger(__name__)

hps_url = "https://localhost:8443/hps"
dt_url = f"{hps_url}/dt/api/v1"
auth_url = f"{hps_url}/auth/realms/rep"

if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="%(levelname)8s > %(message)s", level=logging.DEBUG)

    user_token = authenticate(username="repuser", password="repuser", verify=False, url=auth_url)
    user_token = user_token.get("access_token", None)
    assert user_token is not None

    client = Client()
    client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=user_token,
    )

    client.binary_config.debug = True
    client.start()
    api = DataTransferApi(client)
    s = api.status(wait=True)
    log.info("Status: %s" % s)

    log.info("Available storage:")
    for d in api.storages():
        log.info(f"- {json.dumps(d, indent=4)}")

    time.sleep(2)

    client.stop()
