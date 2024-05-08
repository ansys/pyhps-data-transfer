import os
import platform
import stat
import subprocess


class Binary:
    def __init__(self, dts_url: str, dtsc_url: str):
        if platform.system() == "Windows":
            binary_filename = "hpsdata.exe"
        else:
            binary_filename = "hpsdata"

        binary_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", binary_filename)

        # Mark binary as executable
        if not os.access(binary_file_path, os.X_OK):
            st = os.stat(binary_file_path)
            os.chmod(binary_file_path, st.st_mode | stat.S_IEXEC)

        self.args = [
            binary_file_path,
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
