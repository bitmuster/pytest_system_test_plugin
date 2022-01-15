import os
import os.path
import subprocess

class PystProcess():

    def __init__(self, config):
        self.config = config
        print(f"    A new process: {self.config}")

    def set_config(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def get_stdout(self):
        return self.proc.stdout.decode(encoding="utf-8").strip()

    def get_stderr(self):
        return self.proc.stderr.decode(encoding="utf-8").strip()

    def get_returncode(self):
        return self.proc.returncode

    def run(self):
        print(f"    Process: run: {self.config}")
        self.proc = subprocess.run(self.config,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        stdout = os.path.join( os.path.dirname(__file__), "stdout.out")
        with open(stdout, "bw") as outfile:
            outfile.write(self.proc.stdout)

        stderr = os.path.join( os.path.dirname(__file__), "stderr.out")
        with open(stderr, "bw") as outfile:
            outfile.write(self.proc.stderr)

        return self.proc.returncode

    def terminate(self):
        print(f"    Process: terminate: {self.config}")
