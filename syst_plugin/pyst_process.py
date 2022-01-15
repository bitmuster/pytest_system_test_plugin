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

    def get_returncode(self):
        return self.proc.returncode

    def run(self):
        print(f"    Process: run: {self.config}")
        self.proc = subprocess.run(self.config,
                stdout=subprocess.PIPE)
        return self.proc.returncode

    def terminate(self):
        print(f"    Process: terminate: {self.config}")
