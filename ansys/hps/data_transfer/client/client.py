import asyncio
import logging
import os
import platform
import shutil
import time
import traceback

import backoff
import filelock
import httpx
import requests
import urllib3

from .binary import Binary, BinaryConfig
from .exceptions import BinaryError, async_raise_for_status, raise_for_status

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
    class Meta:
        is_async = False

    def __init__(
        self, bin_config: BinaryConfig = BinaryConfig(), download_dir: str = "dt_download", clean=False, clean_dev=True
    ):
        self._bin_config = bin_config
        self._download_dir = download_dir
        self._clean = clean
        self._session = None
        self._clean_dev = clean_dev
        self.binary = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_session"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._session = None

    @property
    def binary_config(self):
        return self._bin_config

    @property
    def base_api_url(self):
        return self._bin_config.url

    @property
    def session(self):
        if self._session is None:
            self._session = self._create_session(self.base_api_url, sync=not self.Meta.is_async)
        return self._session

    @property
    def is_started(self):
        return self.binary is not None and self.binary.is_started

    def start(self):
        if self.binary is not None:
            return

        if self._clean and os.path.exists(self._download_dir):
            try:
                shutil.rmtree(self._download_dir)
            except:
                pass

        self._prepare_platform_binary()

        self.binary = Binary(config=self._bin_config)
        self.binary.start()

        # self._session = self._create_session(self.base_api_url)

    def stop(self, wait=5.0):
        if self.binary is None:
            return
        self.binary.stop(wait=wait)
        self.binary = None
        self._session = None

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
        if plat == "win":
            match platform.uname().machine:
                case "AMD64":
                    arch = "x64"
        else:
            match os.uname().machine:
                case "x86_64":
                    arch = "x64"
                case "aarch64":
                    arch = "arm64"
                case "arm64":
                    arch = "arm64"

        if not arch:
            raise BinaryError(f"Unsupported architecture: {os.uname().machine}")

        return f"{plat}-{arch}"

    def _check_binary(self, build_info):
        log.debug(f"Server version: {build_info}")
        version_hash = build_info["version_hash"]
        branch = build_info["branch"]

        # Figure out binary download path
        bin_ext = ".exe" if platform.system() == "Windows" else ""
        bin_dir = os.path.join(self._download_dir, "worker")
        bin_path = os.path.join(bin_dir, f"hpsdata-{version_hash}{bin_ext}")

        # Check if we need to download the binary
        reason = None
        if self._bin_config.path is not None and not os.path.exists(self._bin_config.path):
            reason = "binary not found"
        elif not os.path.exists(bin_path):
            reason = "binary version not found"
        elif self._clean_dev and branch == "dev":
            reason = "dev branch"

        # Use downloaded binary if nothing else was specified
        if self._bin_config.path is None and os.path.exists(bin_path):
            self._bin_config.path = bin_path

        return reason, bin_path

    def _prepare_platform_binary(self):
        # Get service build info
        dt_url = self._bin_config.data_transfer_url
        session = self._create_session(dt_url, sync=True)
        resp = session.get("/")
        if resp.status_code != 200:
            raise BinaryError(f"Failed to download binary: {resp.text}")

        d = resp.json()

        reason, bin_path = self._check_binary(d["build_info"])

        lock_name = f"{os.path.splitext(os.path.basename(bin_path))[0]}.lock"
        lock_path = os.path.join(os.path.dirname(bin_path), lock_name)
        lock = filelock.SoftFileLock(lock_path, timeout=60)

        if reason is None:
            log.debug(f"Using existing binary: {self._bin_config.path}")
            return

        try:
            log.warning("##### TEST MARKER")
            with lock:
                bin_dir = os.path.dirname(bin_path)
                bin_ext = os.path.splitext(bin_path)[1]
                if not os.path.exists(bin_dir):
                    try:
                        os.makedirs(bin_dir)
                    except:
                        pass

                platform_str = self._platform()
                log.debug(
                    f"Downloading binary for platform '{platform_str}' from {dt_url} to {bin_path}, reason: {reason}"
                )
                url = f"/binaries/worker/{platform_str}/hpsdata{bin_ext}"
                try:
                    resp = requests.get(f"{dt_url}{url}", verify=False)
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
        except filelock.Timeout:
            raise BinaryError(f"Failed to acquire lock for binary download: {lock_path}")
        except Exception as ex:
            if self._bin_config.debug:
                log.debug(traceback.format_exc())
            raise

    def _create_session(self, url: str, *, sync: bool = True):
        verify = not self._bin_config.insecure
        log.debug("Creating session for %s with verify=%s", url, verify)

        if sync:
            session = httpx.Client(
                # transport=httpx.HTTPTransport(retries=5, verify=verify),
                event_hooks={"response": [raise_for_status]},
                verify=verify,
            )
        else:
            session = httpx.AsyncClient(
                # transport=httpx.AsyncHTTPTransport(retries=5, verify=verify),
                event_hooks={"response": [async_raise_for_status]},
                verify=verify,
            )
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
    class Meta(ClientBase.Meta):
        is_async = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start(self):
        super().start()
        self._session = self._create_session(self.base_api_url, sync=False)

    async def stop(self, wait=5.0):
        if self._session is not None:
            try:
                await self._session.post(self.base_api_url + "/shutdown")
                await asyncio.sleep(0.1)
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
                await asyncio.sleep(backoff.full_jitter(sleep))


class Client(ClientBase):
    class Meta(ClientBase.Meta):
        is_async = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def stop(self, wait=5.0):
        if self._session is not None:
            try:
                self._session.post(self.base_api_url + "/shutdown")
            except:
                pass
        super().stop(wait=wait)

    def wait(self, timeout: float = 60.0, sleep=0.5):
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = self._session.get(self.base_api_url)
                if resp.status_code != 200:
                    log.debug("Waiting for worker to start")
                else:
                    return
            except Exception as ex:
                if self._bin_config.debug:
                    log.debug(f"Error waiting for worker to start: {ex}")
            finally:
                time.sleep(backoff.full_jitter(sleep))
