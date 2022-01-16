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
        self.returncode = None
        self.background = None
        logging.debug("    A new process: %s", self.config)

        self.outfile = os.path.join(os.path.dirname(__file__), "out/stdout.out")
        self.errfile = os.path.join(os.path.dirname(__file__), "out/stderr.out")

    def set_config(self, config):
        """Set the arguments of the process.
        TODO: Do we have a better method to pass arguments without the factory?
        """
        self.config = config

    def get_config(self):
        return self.config

    def get_stdout(self):
        if self.background:
            assert os.path.exists(self.outfile)
            with open(self.outfile, encoding="utf-8") as out:
                content = out.read()
                return content.strip()
        else:
            return self.proc.stdout.decode(encoding="utf-8").strip()

    def get_stderr(self):
        if self.background:
            assert os.path.exists(self.errfile)
            with open(self.errfile, encoding="utf-8") as err:
                content = err.read()
                return content.strip()
        else:
            return self.proc.stderr.decode(encoding="utf-8").strip()

    def get_returncode(self):
        return self.returncode

    def run(self):
        """Run process in the foreground
        """
        logging.debug("    Process: run: %s", self.config)
        self.proc = subprocess.run(
            self.config, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        with open(self.outfile, "bw") as out:
            out.write(self.proc.stdout)

        with open(self.errfile, "bw") as out:
            out.write(self.proc.stderr)

        self.returncode = self.proc.returncode
        return self.proc.returncode

    def run_bg(self):
        """Run process in the background
        TODO: Maybe merge with run()
        Note: Unlike run we need the full path of the binary here
        """
        self.background = True
        if not os.path.exists(self.config[0]):
            raise SystemError("Programm %s is not exiting", self.config[0])

        try:
            os.mkdir( os.path.join(os.path.dirname(__file__), "out"))
        except FileExistsError:
            pass

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

            # Disabled, will make grepping more complicated
            # logging.debug("Im the child, one line before execve")

            try:
                os.execve(self.cmd[0], self.cmd, self.newenv)
            except Exception as exception:
                logging.error("Caught excepton on execve: %s", exception)
                #raise exception
                logging.error("Will die now")
                os.abort()
        else:
            logging.info("Im the parent, there is a new child %s", self.child)

    def get_status(self, poll=1):
        """Returns the returncode of the process and polls if it hasn't yet
        finished.
        Will return None if the process is still running.
        """
        if self.child is None:
            return None

        for _ in range(poll*10):
            try:
                pid, status = os.waitpid(self.child, os.WNOHANG)
            except ChildProcessError:
                logging.warning("Process %i is not existing", self.child)
                self.child = None
                return None
            # print(pid,status)
            if (pid, status) == (0, 0):
                logging.debug("No status available for child %s", self.child)
            else:
                if os.WIFEXITED(status):
                    exitstatus = os.WEXITSTATUS(status)
                    logging.info("Exit status of background process %s", exitstatus)
                    self.returncode = exitstatus
                    return exitstatus
            time.sleep(0.1)

        return None

    def kill(self):
        logging.debug("    Process: terminate: %s", self.config)
        if self.child == 0:
            logging.error("Somebody tried to kill the parent process")
        elif self.child is None:
            logging.warning("Child was never called, won't kill it")
        elif self.returncode != None:
            logging.warning("Chiild has already quit with %s, won't kill it",
                    self.returncode)
        else:
            print("Ret", self.returncode)
            os.kill(self.child, signal.SIGKILL)
