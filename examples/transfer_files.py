"""
Basic script to transfer files to remote backends and back using new data transfer service.

Example usage:

    python examples\transfer_files.py --local-path=examples\basic\files\* --remote-path=hello --debug
    python examples\transfer_files.py --local-path=D:\ANSYSDev\models\rolls-royce-large-engine\d3* --debug

"""

import filecmp
import glob
import logging
import os
from pathlib import Path
from time import perf_counter
from typing import Optional

from humanfriendly import format_size
import typer
from typing_extensions import Annotated

from ansys.hps.data_transfer.client import Client, DataTransferApi
from ansys.hps.data_transfer.client.authenticate import authenticate
from ansys.hps.data_transfer.client.models.msg import SrcDst, StoragePath

log = logging.getLogger(__name__)


def transfer_files(api: DataTransferApi, local_path: str, remote_path: Optional[str] = None):
    if not remote_path:
        remote_path = Path(local_path).parent.name
    local_dir = os.path.dirname(local_path)

    log.info(10 * "=")
    log.info(f"Transfer files: {local_path} to {remote_path}")

    log.info("== Removing remote directory if it exists ...")
    op = api.rmdir([StoragePath(path=remote_path)])
    op = api.wait_for([op.id])
    log.debug(f"Operation {op[0].state}")

    log.info("== Create remote directory ...")
    mkdir_op = api.mkdir([StoragePath(path=remote_path)])
    api.wait_for([mkdir_op.id])
    log.info(f"Directory {remote_path} created")

    local_files = [f for f in glob.glob(local_path, recursive=True)]
    log.info(f"== Uploading {len(local_files)} files ...")
    log.debug(f"Local files: {local_files}")

    copy_args = [
        SrcDst(
            src=StoragePath(path=f, remote="local"),
            dst=StoragePath(path=f"{remote_path}/{os.path.basename(f)}", remote="any"),
        )
        for f in local_files
    ]
    t0 = perf_counter()
    op = api.copy(copy_args)
    op = api.wait_for([op.id])
    t1 = perf_counter()
    log.debug(f"Operation {op[0].state}")

    log.info(f"== Query files and metadata in {remote_path} ...")
    op = api.list([StoragePath(path=remote_path)])
    op = api.wait_for([op.id])
    log.debug(f"Operation {op[0].state}")
    log.debug(f"Files in {remote_path}: {op[0].result}")
    fnames = op[0].result[f"any:{remote_path}"]

    op = api.get_metadata([StoragePath(path=f"{remote_path}/{fname}") for fname in fnames])
    op = api.wait_for(op.id)
    log.debug(f"Operation {op[0].state}")
    log.debug(f"Metadata for {remote_path}: {op[0].result}")

    log.info("== List of uploaded files:")
    total_size = 0
    for fname in fnames:
        size = op[0].result[f"{remote_path}/{fname}"].get("size", 0)
        total_size += size
        checksum = op[0].result[f"{remote_path}/{fname}"].get("checksum")
        log.info(f"- name={fname} size={format_size(size)} checksum={checksum if checksum else 'n/a'}")

    log.info("== Upload performance:")
    log.info(f"- Total time: {t1-t0:.5f} s")
    log.info(f"- Total size: {format_size(total_size)}")
    log.info(f"- Throughput: {format_size(total_size / (t1 - t0) )}/s")

    log.info("== Downloading files again")
    copy_args = [
        SrcDst(
            src=StoragePath(path=f"{remote_path}/{fname}", remote="any"),
            dst=StoragePath(path=f"{local_dir}_downloaded/{fname}", remote="local"),
        )
        for fname in fnames
    ]
    t0 = perf_counter()
    op = api.copy(copy_args)
    op = api.wait_for([op.id])
    t1 = perf_counter()
    log.debug(f"Operation {op[0].state}")

    log.info("== Download performance:")
    log.info(f"- Total time: {t1-t0:.5f} s")
    log.info(f"- Total size: {format_size(total_size)}")
    log.info(f"- Throughput: {format_size(total_size / (t1 - t0) )}/s")

    log.info("== Comparing files ...")
    for fname in fnames:
        success = filecmp.cmp(f"{local_dir}/{fname}", f"{local_dir}_downloaded/{fname}", shallow=True)
        log.info(f"- {fname}: {'Success' if success else 'Failed'}")


def main(
    local_path: Annotated[str, typer.Option(help="Path to the files or directory to transfer. Supports wildcards")],
    remote_path: Annotated[str, typer.Option(help="Optional path to the remote directory to transfer files to")] = None,
    debug: Annotated[bool, typer.Option(help="Enable debug logging")] = False,
    url: Annotated[str, typer.Option(help="HPS URL to connect to")] = "https://localhost:8443/hps",
    username: Annotated[str, typer.Option(help="Username to authenticate with")] = "repadmin",
    password: Annotated[
        str, typer.Option(prompt=True, hide_input=True, help="Password to authenticate with")
    ] = "repadmin",
):
    logging.basicConfig(
        format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG if debug else logging.INFO
    )

    dt_url = f"{url}/dt/api/v1"
    auth_url = f"{url}/auth/realms/rep"

    token = authenticate(username=username, password=password, verify=False, url=auth_url)
    token = token.get("access_token", None)
    assert token is not None

    log.info("Connecting to the data transfer service client..")
    client = Client(clean=True)

    client.binary_config.update(
        verbosity=3,
        debug=False,
        insecure=True,
        token=token,
        data_transfer_url=dt_url,
    )
    client.start()

    api = DataTransferApi(client)
    api.status(wait=True)
    storage_names = [f"{s['name']}({s['type']})" for s in api.storages()]
    log.info(f"Available storages: {storage_names}")

    transfer_files(api=api, local_path=local_path, remote_path=remote_path)

    client.stop()


if __name__ == "__main__":
    typer.run(main)
