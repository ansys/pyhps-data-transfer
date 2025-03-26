# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module provides the Python client to the HPS data transfer APIs."""

import asyncio
import atexit
import logging
import os
import platform
import shutil
import stat
import threading
import time
import traceback

import backoff
import filelock
import httpx
import psutil
import urllib3

from ansys.hps.data_transfer.client.binary import Binary, BinaryConfig
from ansys.hps.data_transfer.client.exceptions import BinaryError, async_raise_for_status, raise_for_status

from .token import prepare_token

urllib3.disable_warnings()

for n in ["httpx", "httpcore", "requests", "urllib3"]:
    logger = logging.getLogger(n)
    logger.setLevel(logging.CRITICAL)

log = logging.getLogger(__name__)


def bin_in_use(bin_path):
    """Check if a binary is in use."""
    for proc in psutil.process_iter():
        try:
            cmd = proc.cmdline()
            for c in cmd:
                if bin_path in c:
                    return True
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            pass
        except Exception as err:
            log.debug(f"Error checking process: {err}")
    return False


class MonitorState:
    """Monitor and track state of worker binary."""

    def __init__(self):
        self.reset()
        self._sleep_not_started = 2
        self._sleep_while_running = 5

    @property
    def sleep_for(self):
        return self._sleep_while_running if self._was_ready else self._sleep_not_started

    def reset(self):
        self._ok_reported = False
        self._was_ready = False
        self._failed = False
        self._last_exc = None

    def mark_ready(self, ready):
        """Mark worker as ready or not ready."""
        self._was_ready = True
        msg = f"Worker is running, reporting {'' if ready else 'not '}ready"
        if ready:
            if not self._ok_reported:
                log.info(msg)
                self._ok_reported = True
        else:
            self._ok_reported = False
            log.warning(msg)

    def mark_failed(self, exc=None, binary=None):
        """Mark worker as failed."""
        exc_str = "" if exc is None else f": {exc}"
        if binary:
            bin_str = f", binary is {'' if binary.is_started else 'not '}running"
        else:
            bin_str = ""
        log.warning(f"Worker failure detected{exc_str}{bin_str}")

        self._ok_reported = False
        self._failed = True
        self._last_exc = exc

    def report(self, binary):
        """Report worker status."""
        if self._failed and self._was_ready:
            descr = "running" if binary.is_started else "not running"
            if self._last_exc is not None:
                descr += f", last exception: {self._last_exc}"
            log.warning(f"Worker failure detected, binary is {descr}")


class ClientBase:
    """Provide the Python client to the HPS data transfer APIs.

    This class uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.

    Parameters
    ----------
    bin_config: BinaryConfig
        BinaryConfig object, Default is None
    download_dir: str
        download dir path. Default is None
    clean: bool
        If True, cleans download_dir path. Default is False.
    clean_dev: bool
        If True, downloads binary from dev branch. Default is True.
    check_in_use: bool
        If True, checks if binary is in use and skips downloading new binary. Default is True.
    timeout: float
        Default is 60.0
    retries: int
        Default is 10

    Examples:
    --------
    Create a client object and connect to HPS data transfer with a access_token.

    >>> from ansys.hps.data_transfer.client import Client
    >>> token = authenticate(username=username, password=password, verify=False, url=auth_url)
    >>> token = token.get("access_token", None)
    >>> client = Client(clean=True)
    >>> client.binary_config.update(
            verbosity=3,
            debug=False,
            insecure=True,
            token=token,
            data_transfer_url=dt_url,
        )
    >>> client.start()

    """

    class Meta:
        is_async = False

    def __init__(
        self,
        bin_config: BinaryConfig = None,
        download_dir: str = "dt_download",
        clean=False,
        clean_dev=True,
        check_in_use=True,
        timeout=60.0,
        retries=10,
    ):
        self._bin_config = bin_config or BinaryConfig()
        self._download_dir = download_dir
        self._clean = clean
        self._clean_dev = clean_dev
        self._check_in_use = check_in_use
        self._timeout = timeout
        self.retries = retries

        self._session = None
        self.binary = None

        self._monitor_stop = None
        self._monitor_state = MonitorState()

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_session"]
        del state["_monitor_stop"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._session = None
        self._monitor_stop = None

    @property
    def binary_config(self):
        """Return binary config."""
        return self._bin_config

    @property
    def base_api_url(self):
        """Return api url from config."""
        return self._bin_config.url

    @property
    def session(self):
        """Return a session object. Creates a new one if one is not already created."""
        if self._session is None:
            self._session = self._create_session(self.base_api_url, sync=not self.Meta.is_async)
        return self._session

    @property
    def is_started(self):
        """Return True if binary is up and running."""
        return self.binary is not None and self.binary.is_started

    @property
    def timeout(self):
        """Return the timeout for the session."""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Set the timeout for the session."""
        self._timeout = value

    @property
    def retries(self):
        """Return the number of retries."""
        return self._retries

    @retries.setter
    def retries(self, value):
        """Set the number of retries."""
        self._retries = value

    def start(self):
        """Start client session using binary config credentials."""
        if self.binary is not None:
            return

        if self._clean and os.path.exists(self._download_dir):
            try:
                shutil.rmtree(self._download_dir)
            except:
                pass

        self._monitor_stop = threading.Event()
        self._monitor_state.reset()
        self._prepare_platform_binary()

        self._bin_config._on_port_changed = self._on_port_changed
        self._bin_config._on_process_died = self._on_process_died

        self.binary = Binary(config=self._bin_config)
        self.binary.start()

        # self._session = self._create_session(self.base_api_url)

    def stop(self, wait=5.0):
        """Stop client session."""
        if self.binary is None:
            return
        self._monitor_stop.set()
        self.binary.stop(wait=wait)
        self.binary = None
        self._session = None
        self._bin_config._on_port_changed = None

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

    def _prepare_bin_path(self, build_info):
        log.debug(f"Server version: {build_info}")
        version_hash = build_info["version_hash"]
        branch = build_info["branch"]

        # Figure out binary download path
        bin_ext = ".exe" if platform.system() == "Windows" else ""
        bin_dir = os.path.join(self._download_dir, "worker")
        bin_path = os.path.join(bin_dir, f"hpsdata-{version_hash}{bin_ext}")
        return bin_path

    def _check_binary(self, build_info, bin_path):
        """Check if there is a need to download the binary."""
        branch = build_info["branch"]

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

        bin_path = self._prepare_bin_path(d["build_info"])
        lock_name = f"{os.path.splitext(os.path.basename(bin_path))[0]}.lock"
        lock_dir = os.path.dirname(bin_path)
        if not os.path.exists(lock_dir):
            try:
                os.makedirs(lock_dir)
            except Exception as ex:
                log.debug(f"Failed to create lock dir: {ex}")
        lock_path = os.path.join(lock_dir, lock_name)
        lock = filelock.SoftFileLock(lock_path, timeout=60)

        try:
            with lock:
                reason, bin_path = self._check_binary(d["build_info"], bin_path)
                bin_path = os.path.abspath(bin_path)

                if self._check_in_use and bin_in_use(bin_path):
                    log.info(f"Skipping download, binary in use: {bin_path}")
                    return

                if reason is None:
                    log.debug(f"Using existing binary: {self._bin_config.path}")
                    return

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
                    with open(bin_path, "wb") as f, session.stream("GET", url) as resp:
                        resp.read()
                        if resp.status_code != 200:
                            raise BinaryError(f"Failed to download binary: {resp.text}")
                        for chunk in resp.iter_bytes():
                            f.write(chunk)
                    self._bin_config.path = bin_path
                except Exception as ex:
                    if self._bin_config.debug:
                        log.debug(traceback.format_exc())
                    log.error(f"Failed to download binary: {ex}")
                    os.remove(bin_path)

                st = os.stat(bin_path)
                log.debug(f"Marking binary as executable: {bin_path}")
                os.chmod(bin_path, st.st_mode | stat.S_IEXEC)
                if self._bin_config.debug:
                    log.debug(f"Binary mode: {stat.filemode(os.stat(bin_path).st_mode)}")
        except filelock.Timeout:
            raise BinaryError(f"Failed to acquire lock for binary download: {lock_path}")

    def _create_session(self, url: str, *, sync: bool = True):
        verify = not self._bin_config.insecure
        log.debug("Creating session for %s with verify=%s", url, verify)

        args = {
            "timeout": httpx.Timeout(self._timeout),
        }

        if sync:
            session = httpx.Client(
                transport=httpx.HTTPTransport(retries=self._retries, verify=verify),
                event_hooks={"response": [raise_for_status]},
                **args,
            )
        else:
            session = httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=self._retries, verify=verify),
                event_hooks={"response": [async_raise_for_status]},
                **args,
            )
        session.base_url = url
        session.verify = verify
        session.follow_redirects = True

        if self._bin_config.token is not None:
            session.headers["Authorization"] = prepare_token(self._bin_config.token)

        return session

    def _on_port_changed(self, port):
        log.debug(f"Port changed to {port}")
        self._session = None

    def _on_process_died(self, ret_code):
        self._monitor_state.reset()


class AsyncClient(ClientBase):
    """An async interface to the Python client to the HPS data transfer APIs."""

    class Meta(ClientBase.Meta):
        is_async = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bin_config._on_token_update = self._update_token

    async def start(self):
        """Start async binary worker."""
        super().start()
        asyncio.create_task(self._monitor())

    async def stop(self, wait=5.0):
        """Stop async binary worker."""
        if self._session is not None:
            try:
                await self._session.post(self.base_api_url + "/shutdown")
                await asyncio.sleep(0.1)
            except:
                pass
        super().stop(wait=wait)
        # asyncio_atexit.register(self.stop)

    async def wait(self, timeout: float = 60.0, sleep=0.5):
        """Wait on async binary worker."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                if self._session is not None:
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

    def _update_token(self):
        loop = asyncio.get_running_loop()
        if self._session is None:
            return
        log.debug("Updating auth token, ends in %s", self._bin_config.token[-10:])
        try:
            self._session.headers["Authorization"] = prepare_token(self._bin_config.token)
            # Make sure the token gets intercepted by the worker
            loop.run_until_complete(self.session.get("/"))
        except Exception as e:
            log.debug(f"Error updating token: {e}")

    async def _monitor(self):
        while not self._monitor_stop.is_set():
            await asyncio.sleep(self._monitor_state.sleep_for)

            if self._session is None or self.binary is None:
                continue
            try:
                resp = await self._session.get(self.base_api_url)

                if resp.status_code == 200:
                    ready = resp.json().get("ready", False)
                    self._monitor_state.mark_ready(ready)
                    continue
            except Exception as ex:
                if self.binary_config.debug:
                    log.debug("URL: %s", self.base_api_url)
                    log.debug(traceback.format_exc())
                self._monitor_state.mark_failed(exc=ex, binary=self.binary)
                continue

            self._monitor_state.report(self.binary)
        log.debug("Worker status monitor stopped")


class Client(ClientBase):
    """Provide the Python client to the HPS data transfer APIs.
    This class uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.
    """

    class Meta(ClientBase.Meta):
        is_async = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bin_config._on_token_update = self._update_token
        self._monitor_thread = None

    def __getstate__(self):
        state = super().__getstate__()
        del state["_monitor_thread"]
        return state

    def __setstate__(self, state):
        super().__setstate__(state)
        self.__dict__.update(state)
        self._monitor_thread = None

    def start(self):
        """Start client session using binary config credentials."""
        super().start()
        atexit.register(self.stop)
        self._monitor_thread = threading.Thread(
            target=self._monitor, args=(), daemon=True, name="worker_status_monitor"
        )
        self._monitor_thread.start()

    def stop(self, wait=5.0):
        """Stop client session."""
        if self._session is not None:
            try:
                self._session.post(self.base_api_url + "/shutdown")
            except:
                pass
        super().stop(wait=wait)

    def wait(self, timeout: float = 60.0, sleep=0.5):
        """Wait on worker binary to start."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                if self._session is not None:
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

    def _update_token(self):
        if self._session is None:
            return
        log.debug("Updating auth token, ends in %s", self._bin_config.token[-10:])
        try:
            self._session.headers["Authorization"] = prepare_token(self._bin_config.token)
            # Make sure the token gets intercepted by the worker
            resp = self.session.get("/")
        except Exception as e:
            log.debug(f"Error updating token: {e}")

    def _monitor(self):
        while not self._monitor_stop.is_set():
            time.sleep(self._monitor_state.sleep_for)

            if self._session is None or self.binary is None:
                continue
            try:
                resp = self._session.get(self.base_api_url)

                if resp.status_code == 200:
                    ready = resp.json().get("ready", False)
                    self._monitor_state.mark_ready(ready)
                    continue
            except Exception as ex:
                if self.binary_config.debug:
                    log.debug("URL: %s", self.base_api_url)
                    log.debug(traceback.format_exc())
                self._monitor_state.mark_failed(exc=ex, binary=self.binary)
                continue

            self._monitor_state.report(self.binary)
        log.debug("Worker status monitor stopped")
