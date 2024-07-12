import json
import logging
import os
import socket
import stat
import subprocess
import threading
import time

log = logging.getLogger(__name__)


class Binary:
    def __init__(
        self,
        # Required
        binary_path: str,
        data_transfer_url: str,
        # Process related settings
        log: bool = True,
        monitor_interval: float = 0.5,
        # Worker config settings
        external_url: str = None,
        token: str = None,
        port: int = None,
        verbosity: int = 1,
        insecure: bool = False,
        debug: bool = False,
        docs: bool = False,
    ):
        # Process related settings
        self._base_args = []
        self._args = []
        self._binary_path = binary_path
        self._capture_log = log
        self._monitor_interval = monitor_interval
        self._stop = threading.Event()

        # Worker config settings
        self._debug = debug
        self._data_transfer_url = data_transfer_url
        self._verbosity = verbosity
        self._port = port
        self._token = token
        self._external_url = external_url
        self._insecure = insecure
        self._docs = docs

    def start(self):
        if self._process is not None and self._process.returncode is None:
            raise RuntimeError("Worker already started.")

        self._stop.clear()

        # Retrieve an open port
        if self._port is None:
            self._port = self._get_open_port()

        if not self._binary_path or not os.path.exists(self._binary_path):
            # TODO - retrieve the binary?
            raise os.error("Binary not found.")

        # Mark binary as executable
        if not os.access(self._binary_path, os.X_OK):
            st = os.stat(self._binary_path)
            os.chmod(self._binary_path, st.st_mode | stat.S_IEXEC)

        self._base_args = [
            self._binary_path,
            "--log-types",
            "console",
        ]

        if self._external_url is None:
            args = " ".join(self._base_args)
            resp = subprocess.run(f"{args} config show", capture_output=True, text=True, shell=True)
            config = json.loads(resp.stdout)
            self._external_url = config.get("external_url", None)

        self._build_args()

        self._process = None

        if self._debug:
            log.info(f"Starting worker: {args}")

        # if False:
        t = threading.Thread(target=self._monitor, args=())
        t.daemon = True
        t.start()

        if self._capture_log:
            t = threading.Thread(target=self._log_output, args=())
            t.daemon = True
            t.start()

    def stop(self):
        if self._process is None:
            return
        self._stop.set()
        # TODO use /shutdown endpoint
        self.process.kill()

    def args_str(self):
        return " ".join(self.args)

    def _log_output(self):
        while not self._stop.is_set():
            line = self._process.stdout.readline()
            if not line:
                break
            line = line.decode().strip()
            log.info("Worker: %s" % line)

    def _monitor(self):
        while not self._stop.is_set():
            if self._process is None:
                args = " ".join(self._args)
                self._process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            ret_code = self._process.poll()
            if ret_code is not None:
                log.warn(f"Worker exited with code {ret_code}, restarting ...")
                self._process = None

            time.sleep(self._monitor_interval)

    def _get_open_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    def _build_args(self):
        self.args = list(self._base_args)
        self.args.extend(
            [
                "--dt-url",
                self._data_transfer_url,
                "--port",
                str(self._port),
                "--log-types",
                "console",
            ]
        )

        self.args.extend(
            [
                "-v",
                str(self._verbosity),
            ]
        )

        if self._docs:
            self.args.append("--docs")

        if self._insecure:
            self.args.append("--insecure")

        if self._debug:
            self.args.append("--debug")

        if self._external_url is not None:
            self.args.extend(
                [
                    "--external-url",
                    self._external_url,
                ]
            )

        if self._token is not None:
            self.args.extend(
                [
                    "-t",
                    f"Bearer {self._token}",
                ]
            )
