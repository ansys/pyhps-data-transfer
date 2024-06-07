import json
import os
import stat
import subprocess


class Binary:
    def __init__(self, binary_path: str, data_transfer_url: str, external_url: str = None, token: str = None):
        if not binary_path or not os.path.exists(binary_path):
            # TODO - retrieve the binary?
            raise os.error("Binary not found.")

        # Mark binary as executable
        if not os.access(binary_path, os.X_OK):
            st = os.stat(binary_path)
            os.chmod(binary_path, st.st_mode | stat.S_IEXEC)

        self.args = [
            binary_path,
            "--dt-url",
            data_transfer_url,
            "--docs",
            "--insecure",
        ]

        if external_url is None:
            resp = subprocess.run(self.args + ["config", "show"], capture_output=True, text=True)
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
        self.process = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.process.kill()
