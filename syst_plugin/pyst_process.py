""" Implementation of the process class for the pyst plugin
"""

import logging
import os
import os.path
import signal
import subprocess
import time


# logging.basicConfig(level=logging.DEBUG)


class PystProcess:
    def __init__(self, config):
        self.config = config
        self.child = None
        logging.debug("    A new process: %s", self.config)

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
        logging.debug("    Process: run: %s", self.config)
        self.proc = subprocess.run(
            self.config, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout = os.path.join(os.path.dirname(__file__), "stdout.out")
        with open(stdout, "bw") as outfile:
            outfile.write(self.proc.stdout)

        stderr = os.path.join(os.path.dirname(__file__), "stderr.out")
        with open(stderr, "bw") as outfile:
            outfile.write(self.proc.stderr)

        return self.proc.returncode

    def run_bg(self):
        self.outfile = os.path.abspath("./out/stdout.out")
        self.errfile = os.path.abspath("./out/stderr.out")
        # self.cmd = ["/usr/bin/ls", "/usr/bin/false", "/usr/bin/ls", "-lah", "whatever"]
        # self.cmd = ['/usr/bin/bash', '-c', '/usr/bin/sleep 1 ; false']
        self.cmd = self.config
        self.newenv = {}
        self.child = os.fork()
        if self.child == 0:
            logging.info("Im the child")
            flags = os.O_CREAT | os.O_TRUNC | os.O_WRONLY
            out = os.open(self.outfile, flags)
            err = os.open(self.errfile, flags)
            os.dup2(out, 1)  # Duplicate stdout to the the descriptor
            os.dup2(err, 2)  # Duplicate stderr the descriptor
            os.setpgrp()
            logging.info("Im the child, one line before execve")
            os.execve(self.cmd[0], self.cmd, self.newenv)
        else:
            logging.info("Im the parent, there is a new child %s", self.child)

    def get_status(self, poll=1):

        for _ in range(poll*10):
            pid, status = os.waitpid(self.child, os.WNOHANG)
            # print(pid,status)
            if (pid, status) == (0, 0):
                logging.debug("No status available for child %s", self.child)
            else:
                if os.WIFEXITED(status):
                    exitstatus = os.WEXITSTATUS(status)
                    logging.info("Exit status of background process %s", exitstatus)
                    return exitstatus
            time.sleep(0.1)

        return None

    def kill(self):
        logging.debug("    Process: terminate: %s", self.config)
        if self.child is None:
            logging.warn("Chiild was never called, won't kill it")
        else:
            os.kill(self.child, signal.SIGKILL)
