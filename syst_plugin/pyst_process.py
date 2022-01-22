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
    """Class to manage Pytest system-test processes

    TODO: Handle stdin
    TODO: Possibiltiy to run in subshells
    """

    def __init__(self, command, logpath, testname="unnamed_test_", name="no_name_"):
        self.child = None
        self.returncode = None
        self.background = None
        self.proc = None
        self.command = command

        self.testname = testname
        self.logpath = logpath
        self.name = name

        self.testdir = os.path.join(os.path.dirname(self.logpath), "out", self.testname)
        self.newenv = {}

        logging.debug("    A new process: %s", self.command)
        # logging.info("Path %s", self.scriptpath)
        self.outfile = os.path.join(self.testdir, self.name + "stdout.out")
        self.errfile = os.path.join(self.testdir, self.name + "stderr.out")

    def set_name(self, name):
        """Set the name of the process
        Will be used to distinguish stdout and sterr.
        """
        self.name = name

    def get_name(self):
        """Get name of process.
        Will be used to distinguish stdout and sterr.
        """
        return self.name

    def set_command(self, command):
        """Set the arguments of the process.
        TODO: Do we have a better method to pass arguments without the factory?
        """
        self.command = command

    def get_command(self):
        """Get command that will be executed"""
        return self.command

    def get_stdout(self):
        """Get standard output of process"""
        if self.background:
            assert os.path.exists(self.outfile)
            with open(self.outfile, encoding="utf-8") as out:
                content = out.read()
                return content.strip()
        else:
            return self.proc.stdout.decode(encoding="utf-8").strip()

    def get_stderr(self):
        """Get standard error of process"""
        if self.background:
            assert os.path.exists(self.errfile)
            with open(self.errfile, encoding="utf-8") as err:
                content = err.read()
                return content.strip()
        else:
            return self.proc.stderr.decode(encoding="utf-8").strip()

    def get_returncode(self):
        """Get returncode"""
        return self.returncode

    def run(self):
        """Run process in the foreground"""
        logging.debug("    Process: run: %s", self.command)
        # try:
        self.proc = subprocess.run(
            self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
        )
        # except subprocess.CalledProcessError as ex:
        #    pass

        try:
            os.makedirs(self.testdir)
        except FileExistsError:
            pass

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
        if not os.path.exists(self.command[0]):
            raise SystemError("Programm is not exiting: ", self.command[0])
        try:
            os.makedirs(self.testdir)
        except FileExistsError:
            pass

        # really make sure all folders are there. If we fork and find out,
        # we have N forked pytests running
        assert os.path.exists(os.path.dirname(self.outfile))
        assert os.path.exists(os.path.dirname(self.errfile))
        assert os.access(os.path.dirname(self.outfile), os.W_OK)
        assert os.access(os.path.dirname(self.errfile), os.W_OK)

        # self.cmd = ["/usr/bin/ls", "/usr/bin/false", "/usr/bin/ls", "-lah", "whatever"]
        # self.cmd = ['/usr/bin/bash', '-c', '/usr/bin/sleep 1 ; false']

        self.child = os.fork()
        if self.child == 0:
            flags = os.O_CREAT | os.O_TRUNC | os.O_WRONLY
            out = os.open(self.outfile, flags)
            err = os.open(self.errfile, flags)
            os.dup2(out, 1)  # Duplicate stdout to the the descriptor
            os.dup2(err, 2)  # Duplicate stderr the descriptor
            os.setpgrp()

            # Disabled, will make grepping stdout more complicated
            # logging.debug("Im the child, one line before execve")

            try:
                os.execve(self.command[0], self.command, self.newenv)
            except OSError as exception:
                logging.error("Caught excepton on execve: %s", exception)
                # raise exception
                logging.error("Will die now")
                os.abort()
        else:
            logging.info("Child pid is : %s", self.child)

    def get_status(self, poll=1):
        """Returns the returncode of the process and polls if it hasn't yet
        finished.
        Returns "Running" if the process is still running.
        Returns "NotExisting" if the process does not exist anyore.
        """
        if self.child is None:
            return None

        status = None
        for _ in range(poll * 10):
            try:
                pid, status = os.waitpid(self.child, os.WNOHANG)
            except ChildProcessError:
                logging.warning("Process %i is not existing", self.child)
                self.child = None
                return "NotExisting"
            # print(pid,status)
            if (pid, status) == (0, 0):
                logging.debug(
                    "No status available for child %s probably still running",
                    self.child,
                )
                status = "Running"
            else:
                if os.WIFEXITED(status):
                    exitstatus = os.WEXITSTATUS(status)
                    logging.info("Exit status of background process %s", exitstatus)
                    self.returncode = exitstatus
                    return exitstatus
            time.sleep(0.1)

        return status

    def kill(self):
        """Kill the child process"""
        logging.debug("    Process: terminate: %s", self.command)
        if self.child == 0:
            logging.error("Somebody tried to kill the parent process")
        elif self.child is None:
            logging.warning("Child was never called, won't kill it")
        elif self.returncode is not None:
            logging.warning(
                "Child %s has already quit with %s, won't kill it",
                self.child,
                self.returncode,
            )
        else:
            print("Ret", self.returncode)
            os.kill(self.child, signal.SIGKILL)
