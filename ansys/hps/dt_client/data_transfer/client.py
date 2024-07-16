import asyncio
import logging
import os
import platform
import time

import backoff
import httpx
import urllib3

from .binary import Binary, BinaryConfig
from .exceptions import BinaryError

urllib3.disable_warnings()

httpx_log = logging.getLogger("httpx")
httpx_log.setLevel(logging.CRITICAL)

httpcore_log = logging.getLogger("httpcore")
httpcore_log.setLevel(logging.CRITICAL)

for n in ["httpx", "httpcore", "requests", "urllib3"]:
    log = logging.getLogger(n)
    log.setLevel(logging.CRITICAL)

log = logging.getLogger(__name__)


class ClientBase:
    def __init__(self, bin_config: BinaryConfig = BinaryConfig(), download_dir: str = "dt_download"):
        self._bin_config = bin_config
        self._download_dir = download_dir
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

        download_bin = self._bin_config.path is None or not os.path.exists(self._bin_config.path)
        if download_bin:
            self._prepare_platform_binary()

        self.binary = Binary(config=self._bin_config)
        self.binary.start()
        self.base_api_url = self.binary.external_url + "/api/v1"

    def stop(self, wait=5.0):
        if self.binary is None:
            return
        self.binary.stop(wait=wait)
        self.binary = None

    def _platform(self):
        plat = ""
        match platform.system():
            case "Windows":
                plat = "win"
            case "Linux":
                plat = "lin"
            case "Darwin":
                plat = "darwin"

        if not plat:
            raise BinaryError(f"Unsupported platform: {platform.system()}")

        arch = ""
        match os.uname().machine:
            case "x86_64":
                arch = "x64"
            case "aarch64":
                arch = "arm64"
            case "arm64":
                arch = "arm64"

        if not arch:
            raise BinaryError(f"Unsupported architecture: {os.uname().machine}")

        return plat + arch

    def _prepare_platform_binary(self):
        dt_url = self._bin_config.data_transfer_url
        session = self._create_session(dt_url)
        resp = session.get("/")
        if resp.status_code != 200:
            raise BinaryError(f"Failed to download binary: {resp.text}")
        d = resp.json()
        log.debug(f"Server version: {d['build_info']}")
        version_hash = d["build_info"]["version_hash"]

        bin_ext = ".exe" if platform.system() == "Windows" else ""
        bin_dir = os.path.join(self._download_dir, "worker")
        if not os.path.exists(bin_dir):
            try:
                os.makedirs(bin_dir)
            except:
                pass

        bin_path = os.path.join(bin_dir, f"hpsdata-{version_hash}{bin_ext}")
        if os.path.exists(bin_path):
            log.debug(f"Using existing binary: {bin_path}")
            return bin_path

        platform_str = self._platform()
        log.debug(f"Downloading binary for platform '{platform_str}' from {dt_url}")
        url = f"/binaries/client/{platform_str}/hpsdata"
        try:
            with open(bin_path, "wb") as f, session.stream("GET", url) as resp:
                resp.read()
                if resp.status_code != 200:
                    raise BinaryError(f"Failed to download binary: {resp.text}")
                for chunk in resp.iter_bytes():
                    f.write(chunk)
            self._bin_config.path = bin_path
        except Exception as ex:
            log.error(f"Failed to download binary: {ex}")
            os.remove(bin_path)

    def _create_session_obj(self, url, verify):
        raise NotImplementedError

    def _create_session(self, url):
        verify = not self._bin_config.insecure

        session = self._create_session_obj(url, verify)
        session.base_url = url
        session.verify = verify
        session.follow_redirects = True

        if self._bin_config.token is not None:
            t = self._bin_config.token
            if not t.startswith("Bearer "):
                t = f"Bearer {t}"
            session.headers.setdefault("Authorization", t)

        return session


class AsyncClient(ClientBase):
    def __init__(self):
        super().__init__()

    async def start(self, verify: bool = True, token: str = None):
        super().start(verify=verify)
        self.session = self._create_session(self.base_api_url)
        if token is not None:
            self.session.headers.setdefault("Authorization", f"Bearer {token}")

    async def stop(self, wait=5.0):
        if self.session is not None:
            try:
                await self.session.post(self.base_api_url + "/shutdown")
                asyncio.sleep(0.1)
            except:
                pass
        super().stop(wait=wait)

    async def wait(self, timeout: float = 60.0, sleep=0.5):
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = await self.session.get(self.base_api_url)
                if resp.status_code != 200:
                    log.debug("Waiting for worker to start")
                else:
                    return
            except Exception as ex:
                if self._bin_config.debug:
                    log.debug(f"Error waiting for worker to start: {ex}")
            finally:
                asyncio.sleep(backoff.full_jitter(sleep))

    def _create_session_obj(self, url, verify):
        return httpx.AsyncClient(
            transport=httpx.AsyncHTTPTransport(retries=5, verify=verify),
            # event_hooks={"response": [async_raise_for_status]},
        )


class Client(ClientBase):
    def __init__(self):
        super().__init__()

    def start(self, verify: bool = True, token: str = None):
        super().start()
        self.session = self._create_session(self.base_api_url)

    def stop(self, wait=5.0):
        if self.session is not None:
            try:
                self.session.post(self.base_api_url + "/shutdown")
            except:
                pass
        super().stop(wait=wait)

    def wait(self, timeout: float = 60.0, sleep=0.5):
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = self.session.get(self.base_api_url)
                if resp.status_code != 200:
                    log.debug("Waiting for worker to start")
                else:
                    return
            except Exception as ex:
                if self._bin_config.debug:
                    log.debug(f"Error waiting for worker to start: {ex}")
            finally:
                time.sleep(backoff.full_jitter(sleep))

    def _create_session_obj(self, url, verify):
        return httpx.Client(
            transport=httpx.HTTPTransport(retries=5, verify=verify),
            # event_hooks={"response": [raise_for_status]},
        )
