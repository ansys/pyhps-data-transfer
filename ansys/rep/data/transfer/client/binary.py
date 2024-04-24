import os
import platform
import subprocess


class Binary:
    def __init__(self, dts_url: str, dtsc_url: str):
        if platform.system() == "Windows":
            binary_filename = "hpsdata.exe"
        else:
            binary_filename = "hpsdata"
        self.args = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", binary_filename),
            "--dt-url",
            dts_url,
            "--external-url",
            dtsc_url,
            "--docs",
            "--insecure",
        ]
        self.process = None

    def start(self):
        self.process = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.process.kill()
