import logging
import os
import stat
import subprocess
import sys
import threading
import time

import portend

from .exceptions import BinaryError

log = logging.getLogger(__name__)


class BinaryConfig:
    def __init__(
        self,
        # Required
        data_transfer_url: str = "https://localhost:8443/hps/dt/api/v1",
        # Process related settings
        log: bool = True,
        monitor_interval: float = 0.5,
        path: str = None,
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
        self.capture_log = log
        self.monitor_interval = monitor_interval
        if path is None:
            bin_ext = ".exe" if sys.platform == "win32" else ""
            self.path = os.path.join(os.getcwd(), "bin", f"hpsdata{bin_ext}")
        else:
            self.path = path

        # Worker config settings
        self.debug = debug
        self.data_transfer_url = data_transfer_url
        self.verbosity = verbosity
        self.host = host
        self._selected_port = port
        self._detected_port = None
        self.token = token
        self.insecure = insecure

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Unknown attribute {key}")

    @property
    def port(self):
        return self._selected_port or self._detected_port

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/api/v1"


class Binary:
    def __init__(
        self,
        config: BinaryConfig = BinaryConfig(),
    ):
        self._config = config

        self._base_args = []
        self._args = []
        self._stop = threading.Event()
        self._prepared = threading.Event()
        self._process = None

    @property
    def config(self):
        return self._config

    def start(self):
        if self._process is not None and self._process.returncode is None:
            raise BinaryError("Worker already started.")

        self._stop.clear()

        bin_path = self._config.path
        if not bin_path or not os.path.exists(bin_path):
            raise BinaryError(f"Binary not found: {bin_path}")

        # Mark binary as executable
        if not os.access(bin_path, os.X_OK):
            st = os.stat(bin_path)
            os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

        self._process = None

        # if False:
        t = threading.Thread(target=self._monitor, args=())
        t.daemon = True
        t.start()

        if self._config.capture_log:
            t = threading.Thread(target=self._log_output, args=())
            t.daemon = True
            t.start()

        if not self._prepared.wait(timeout=5.0):
            log.warning("Worker did not prepare in time.")

    def stop(self, wait=5.0):
        if self._process is None:
            return
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

    def args_str(self):
        return " ".join(self._args)

    def _log_output(self):
        while not self._stop.is_set():
            if self._process is None:
                time.sleep(1)
                continue
            try:
                line = self._process.stdout.readline()
                if not line:
                    break
                line = line.decode().strip()
                log.info("Worker: %s" % line)
            except Exception as e:
                if self._config.debug:
                    log.debug(f"Error reading worker output: {e}")
                time.sleep(1)

    def _monitor(self):
        while not self._stop.is_set():
            if self._process is None:
                self._prepare()
                args = " ".join(self._args)
                if self._config.debug:
                    s = args.replace(self._config.token, "***")
                    log.debug(f"Starting worker: {s}")
                self._process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                ret_code = self._process.poll()
                if ret_code is not None:
                    log.warning(f"Worker exited with code {ret_code}, restarting ...")
                    self._process = None
                    time.sleep(1.0)
                    continue

            time.sleep(self._config.monitor_interval)

    def _prepare(self):
        if self._config._selected_port is None:
            self._config._detected_port = self._get_open_port()

        self._build_base_args()

        self._build_args()
        self._prepared.set()

    def _get_open_port(self):
        port = portend.find_available_local_port()
        return port

    def _build_base_args(self):
        self._base_args = [
            self._config.path,
            "--log-types",
            "console",
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
                    f'"Bearer {self._config.token}"',
                ]
            )
