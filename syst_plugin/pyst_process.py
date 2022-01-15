
class PystProcess():

    def __init__(self, config):
        self.config = config
        print(f"    A new process: {self.config}")

    def set_config(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def run(self):
        print(f"    Process: run: {self.config}")
        return self.config

    def terminate(self):
        print(f"    Process: terminate: {self.config}")
