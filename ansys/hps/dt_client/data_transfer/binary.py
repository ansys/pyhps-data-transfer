import json
import logging
import os
import stat
import subprocess

log = logging.getLogger(__name__)


class Binary:
    def __init__(
        self, binary_path: str, data_transfer_url: str, external_url: str = None, token: str = None, port: int = 1091
    ):
        if not binary_path or not os.path.exists(binary_path):
            # TODO - retrieve the binary?
            raise os.error("Binary not found.")

        # Mark binary as executable
        if not os.access(binary_path, os.X_OK):
            st = os.stat(binary_path)
            os.chmod(binary_path, st.st_mode | stat.S_IEXEC)

        # Rather pass token via env
        self.args = [
            binary_path,
            "--dt-url",
            data_transfer_url,
            "--docs",
            "--insecure",
            "-v",
            "3",
            "-d",
            "--port",
            str(port),
            "--log-types",
            "console",
        ]

        # TODO: use shell=True on subprocess calls
        if external_url is None:
            args = " ".join(self.args)
            resp = subprocess.run(f"{args} config show", capture_output=True, text=True, shell=True)
            config = json.loads(resp.stdout)
            external_url = config.get("external_url", None)

        self.external_url = external_url

        self.args.extend(
            [
                "--external-url",
                external_url,
            ]
        )

        if token is not None:
            self.args.extend(
                [
                    "-t",
                    f"Bearer {token}",
                ]
            )

        self.process = None

    def start(self):
        args = " ".join(self.args)
        self.process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.process.kill()

    def args_str(self):
        return " ".join(self.args)
