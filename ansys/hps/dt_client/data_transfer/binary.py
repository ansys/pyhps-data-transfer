import json
import logging
import os
import socket
import stat
import subprocess
import sys
import threading
import time

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
        external_url: str = None,
        token: str = None,
        port: int = None,
        verbosity: int = 1,
        insecure: bool = False,
        debug: bool = False,
        docs: bool = False,
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
        self.port = port
        self.token = token
        self.external_url = external_url
        self.insecure = insecure
        self.docs = docs

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Unknown attribute {key}")


class Binary:
    def __init__(
        self,
        config: BinaryConfig = BinaryConfig(),
    ):
        self._config = config

        self._base_args = []
        self._args = []
        self._stop = threading.Event()
        self._process = None

    @property
    def external_url(self):
        return self._config.external_url

    @property
    def config(self):
        return self._config

    def start(self, wait: float = None, sleep: float = 0.5):
        if self._process is not None and self._process.returncode is None:
            raise BinaryError("Worker already started.")

        self._stop.clear()

        # Retrieve an open port
        if self._config.port is None:
            self._config.port = self._get_open_port()

        bin_path = self._config.path
        if not bin_path or not os.path.exists(bin_path):
            # TODO - retrieve the binary?
            raise BinaryError(f"Binary not found: {bin_path}")

        # Mark binary as executable
        if not os.access(bin_path, os.X_OK):
            st = os.stat(bin_path)
            os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

        self._base_args = [
            bin_path,
            "--log-types",
            "console",
        ]

        if self._config.external_url is None:
            self._fill_external_url()

        self._build_args()

        self._process = None

        if self._config.debug:
            log.info(f"Starting worker: {self._args}")

        # if False:
        t = threading.Thread(target=self._monitor, args=())
        t.daemon = True
        t.start()

        if self._config.capture_log:
            t = threading.Thread(target=self._log_output, args=())
            t.daemon = True
            t.start()

        if wait is not None:
            start = time.time()
            while time.time() - start < wait:
                log.warn("not implemented")
                time.sleep(sleep)

    def stop(self):
        if self._process is None:
            return
        self._stop.set()
        # TODO use /shutdown endpoint
        self.process.kill()

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
                args = " ".join(self._args)
                self._process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            ret_code = self._process.poll()
            if ret_code is not None:
                log.warn(f"Worker exited with code {ret_code}, restarting ...")
                self._process = None
                time.sleep(1.0)
                continue

            time.sleep(self._config.monitor_interval)

    def _get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    def _build_args(self):
        self._args = list(self._base_args)
        self._args.extend(
            [
                "--dt-url",
                self._config.data_transfer_url,
                "--port",
                str(self._config.port),
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

        if self._config.docs:
            self._args.append("--docs")

        if self._config.insecure:
            self._args.append("--insecure")

        if self._config.debug:
            self._args.append("--debug")

        if self._config.external_url is not None:
            self._args.extend(
                [
                    "--external-url",
                    self._config.external_url,
                ]
            )

        if self._config.token is not None:
            self._args.extend(
                [
                    "-t",
                    f"Bearer {self._config.token}",
                ]
            )

    def _fill_external_url(self):
        args = " ".join(self._base_args)
        resp = subprocess.run(f"{args} config show", capture_output=True, text=True, shell=True)
        loaded = json.loads(resp.stdout)
        self._config.external_url = loaded.get("external_url", None)
