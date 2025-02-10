# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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

import json
import logging
import os
import stat
import subprocess
import threading
import time

import portend

from .exceptions import BinaryError
from .token import prepare_token

log = logging.getLogger(__name__)

level_map = {
    "trace": logging.DEBUG,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
    "panic": logging.CRITICAL,
}


class PrepareSubprocess:
    def __enter__(self):
        self._orig_use_vfork = subprocess._USE_VFORK
        self._orig_use_pspawn = subprocess._USE_POSIX_SPAWN
        subprocess._USE_VFORK = False
        subprocess._USE_POSIX_SPAWN = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        subprocess._USE_VFORK = self._orig_use_vfork
        subprocess._USE_POSIX_SPAWN = self._orig_use_pspawn


class BinaryConfig:
    """
    Class to configure worker binary connection to HPS data transfer client

    Parameters
    ----------
    data_transfer_url: str
        data transfer url. Default is https://localhost:8443/hps/dt/api/v1
    log: bool
        Process related setting to enable logging. Default is True
    log_to_file: bool
        To enable logging to a file. Default is False
    monitor_interval: float
        duration for waiting before the next monitor check on the binary. Default is 0.5
    token: str
        A worker config setting of access token credential.
    host: str
        Host IP to talk to data tarsnfer service. Default is 127.0.0.1
    port: int
        Host port to talk to data tarsnfer service
    verbosity: int
        Default is 1
    insecure: bool
        Default is False
    debug: bool
        Default is False
    """

    def __init__(
        self,
        # Required
        data_transfer_url: str = "https://localhost:8443/hps/dt/api/v1",
        # Process related settings
        log: bool = True,
        log_to_file: bool = False,
        monitor_interval: float = 0.5,
        # TODO: Remove path? not used anywhere
        path=None,
        # Worker config settings
        token: str = None,
        host: str = "127.0.0.1",
        port: int = None,
        verbosity: int = 1,
        insecure: bool = False,
        debug: bool = False,
    ):
        self.data_transfer_url = data_transfer_url

        # Process related settings
        self.log = log
        self.log_to_file = log_to_file
        self.monitor_interval = monitor_interval
        self.path = path

        # Worker config settings
        self.debug = debug
        self.data_transfer_url = data_transfer_url
        self.verbosity = verbosity
        self.host = host
        self._selected_port = port
        self._detected_port = None
        self._token = token
        self.insecure = insecure

        self._on_token_update = None
        self._on_process_died = None
        self._on_port_changed = None

    # TODO: Should this begin with underscore?
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Unknown attribute {key}")

    @property
    def port(self):
        return self._selected_port or self._detected_port

    @port.setter
    def port(self, value):
        self._selected_port = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        if self.debug:
            log.debug(
                f"Setting token to ...{value[-10:]}, old token: {f'...{self._token[-10:]}' if self._token else 'none'}"
            )
        self._token = value
        if self._on_token_update is not None:
            self._on_token_update()

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/api/v1"


class Binary:
    """
    Class to start, stop and monitor worker binary.

    Parameters
    ----------
    config: BinaryConfig
        BinaryConfig object.
    """

    def __init__(
        self,
        config: BinaryConfig = BinaryConfig(),
    ):
        self._config = config

        self._base_args = []
        self._args = []
        self._stop = None
        self._prepared = None
        self._process = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_stop"]
        del state["_prepared"]
        del state["_process"]
        return state

    @property
    def config(self):
        """
        Method to return config
        """
        return self._config

    @property
    def is_started(self):
        """
        Method to check if binary has started. Returns true if binary is up and running.
        """
        try:
            return self._process is not None and self._process.returncode is None
        except Exception:
            return False

    def start(self):
        """
        Method to start the worker binary.
        Looks for binary in a set path, marks the binary as an executable and then start the executable
        """
        if self._process is not None and self._process.returncode is None:
            raise BinaryError("Worker already started.")

        log.debug("Starting worker ...")

        self._stop = threading.Event()
        self._prepared = threading.Event()

        bin_path = self._config.path
        if not bin_path or not os.path.exists(bin_path):
            raise BinaryError(f"Binary not found: {bin_path}")

        # Mark binary as executable
        if not os.access(bin_path, os.X_OK):
            log.debug(f"Marking binary as executable: {bin_path}")
            st = os.stat(bin_path)
            os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

        self._process = None

        # if False:
        t = threading.Thread(target=self._monitor, args=(), name="worker_monitor")
        t.daemon = True
        t.start()

        if self._config.log:
            t = threading.Thread(target=self._log_output, args=(), name="worker_log_output")
            t.daemon = True
            t.start()

        if not self._prepared.wait(timeout=5.0):
            log.warning("Worker did not prepare in time.")

    def stop(self, wait=5.0):
        """
        Stop worker binary
        """
        if self._process is None:
            return

        log.debug("Stopping worker ...")
        self._stop.set()
        self._prepared.clear()

        start = time.time()
        while True:
            if self._process.poll() is not None:
                break
            if time.time() - start > wait:
                log.warning("Worker did not stop in time, killing ...")
                self._process.kill()
                break
            time.sleep(wait * 0.1)

    # TODO: This method is not used anywhere. remove it?
    def args_str(self):
        return " ".join(self._args)

    def _log_output(self):
        while not self._stop.is_set():
            if self._process is None or self._process.stdout is None:
                time.sleep(1)
                continue
            try:
                line = self._process.stdout.readline()
                if not line:
                    break
                line = line.decode(errors="strip").strip()
                # log.info("Worker: %s" % line)
                self._log_line(line)
            except json.decoder.JSONDecodeError:
                pass
            except Exception as e:
                if self._config.debug:
                    log.debug(f"Error reading worker output: {e}")
                time.sleep(1)
        log.debug("Worker log output stopped")

    def _log_line(self, line):
        d = json.loads(line)
        # log.warning(f"Worker: {d}")

        level = d.pop("level", "info")
        d.pop("time", None)
        if not self._config.debug:
            d.pop("caller", None)
            d.pop("mode", None)
        msg = d.pop("message", None)

        if msg is None:
            return

        msg = msg.capitalize()
        level_no = level_map.get(level, logging.INFO)
        other = ""
        for k, v in d.items():
            if isinstance(v, str) and " " in v:
                v = f'"{v}"'
            other += f"{k}={v} "
        other = other.strip()
        if other:
            msg += f" {other}"
        msg = msg.encode("ascii", errors="ignore").decode().strip()
        log.log(level_no, f"{msg}")

    def _monitor(self):
        while not self._stop.is_set():
            if self._process is None:
                self._prepare()
                args = " ".join(self._args)

                redacted = f"{args}"
                if self._config.token is not None:
                    redacted = args.replace(self._config.token, "***")
                log.debug(f"Starting worker: {redacted}")

                with PrepareSubprocess():
                    self._process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                ret_code = self._process.poll()
                if ret_code is not None and ret_code != 0:
                    log.warning(f"Worker exited with code {ret_code}, restarting ...")
                    self._process = None
                    self._prepared.clear()
                    if self.config._on_process_died is not None:
                        self.config._on_process_died(ret_code)
                    time.sleep(1.0)
                    continue
                # elif self._config.debug:
                #     log.debug(f"Worker running ...")

            time.sleep(self._config.monitor_interval)
        log.debug("Worker monitor stopped")

    def _prepare(self):
        if self._config._selected_port is None:
            self._config._detected_port = self._get_open_port()
            if self._config._on_port_changed is not None:
                self._config._on_port_changed(self._config._detected_port)

        self._build_base_args()

        self._build_args()
        self._prepared.set()

    def _get_open_port(self):
        port = portend.find_available_local_port()
        return port

    def _build_base_args(self):
        log_types = ["diode"]
        if self._config.log_to_file:
            log_types.append("file")

        self._base_args = [
            self._config.path,
            "--log-types",
            ",".join(log_types),
            "--host",
            self._config.host,
            "--port",
            str(self._config.port),
        ]

    def _build_args(self):
        self._args = list(self._base_args)
        self._args.extend(
            [
                "--dt-url",
                self._config.data_transfer_url,
                "--log-types",
                "console",
            ]
        )

        self._args.extend(
            [
                "-v",
                str(self._config.verbosity),
            ]
        )

        if self._config.insecure:
            self._args.append("--insecure")

        if self._config.debug:
            self._args.append("--debug")

        if self._config.token is not None:
            self._args.extend(
                [
                    "-t",
                    f'"{prepare_token(self._config.token)}"',
                ]
            )
