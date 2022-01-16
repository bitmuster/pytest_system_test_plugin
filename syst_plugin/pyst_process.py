import os
import os.path
import time
import subprocess

debug = False

class PystProcess():

    def __init__(self, config):
        self.config = config
        if debug:
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
        if debug:
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

    def run_bg(self):
        self.outfile = os.path.abspath('./out/stdout.out')
        self.errfile = os.path.abspath('./out/stderr.out')
        #self.cmd = ["/usr/bin/ls", "/usr/bin/false", "/usr/bin/ls", "-lah", "whatever"]
        #self.cmd = ['/usr/bin/bash', '-c', '/usr/bin/sleep 1 ; false']
        self.cmd = self.config
        self.newenv = {}
        self.child = os.fork()
        if self.child == 0:
            print("Im the child")
            flags = os.O_CREAT | os.O_TRUNC | os.O_WRONLY
            out = os.open(self.outfile, flags)
            err = os.open(self.errfile, flags)
            os.dup2(out, 1) # Duplicate stdout to the the descriptor
            os.dup2(err, 2) # Duplicate stderr the descriptor
            os.setpgrp()
            print("Im the child, one line before execve")
            os.execve(self.cmd[0], self.cmd, self.newenv)
        else:
            print(f"Im the parent, there is a new child {self.child}")

    def get_status(self):

        for i in range(20):
            pid,status = os.waitpid(self.child, os.WNOHANG)
            #print(pid,status)
            if (pid,status) == (0,0):
                if debug:
                    print(f"No status available for child {self.child}")
            else:
                if os.WIFEXITED(status):
                    exitstatus = os.WEXITSTATUS(status)
                    print("Exit status of background process", exitstatus)
                    return exitstatus
            time.sleep(0.2)

        return status

    def terminate(self):
        if debug:
            print(f"    Process: terminate: {self.config}")
