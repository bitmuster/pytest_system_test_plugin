""" Implementation of the process class for the pyst plugin
"""

import logging
import os
import os.path
import signal
import subprocess
import time
from typing import Union, List

# logging.basicConfig(level=logging.DEBUG)


class PystProcess:
    """Class to manage Pytest system-test processes

    TODO: Handle stdin
    TODO: Possibiltiy to run in subshells
    """

    def __init__(
        self,
        command: Union[List[str], str],
        logpath: str,
        testname: str = "unnamed_test_",
        name: str = "no_name_",
    ):
        self.child: Union[int, None] = None
        self.returncode: Union[int, None] = None
        self.background: Union[bool, None] = None
        self.proc: Union[subprocess.CompletedProcess, None] = None
        self.command: Union[List[str], str] = command

        self.testname = testname
        self.logpath = logpath
        self.name = name

        self.testdir = os.path.join(os.path.dirname(self.logpath), "out", self.testname)
        self.newenv: dict = {}

        logging.debug("    A new process: %s", self.command)
        # logging.info("Path %s", self.scriptpath)
        self.outfile = os.path.join(self.testdir, self.name + "stdout.out")
        self.errfile = os.path.join(self.testdir, self.name + "stderr.out")

    def set_name(self, name: str) -> None:
        """Set the name of the process
        Will be used to distinguish stdout and sterr.

        Args:
            name
        """
        self.name = name
        self.outfile = os.path.join(self.testdir, self.name + "stdout.out")
        self.errfile = os.path.join(self.testdir, self.name + "stderr.out")

    def get_name(self) -> str:
        """Get name of process.
        Will be used to distinguish stdout and sterr.

        Returns:
            name
        """
        return self.name

    def set_command(self, command):
        """Set the arguments of the process.
        TODO: Do we have a better method to pass arguments without the factory?
        """
        self.command = command

    def get_command(self) -> Union[str, list]:
        """Get command that will be executed

        Returns:
            command either as string or list of strings
        """
        return self.command

    def get_stdout(self) -> str:
        """Get standard output of process

        Returns:
            stdout
        """
        if self.background:
            assert os.path.exists(self.outfile)
            with open(self.outfile, encoding="utf-8") as out:
                content = out.read()
                return content.strip()
        else:
            if self.proc:
                return self.proc.stdout.decode(encoding="utf-8").strip()
            raise SystemError("Process is None")

    def get_stderr(self) -> str:
        """Get standard error of process

        Returns:
            stderr
        """
        if self.background:
            assert os.path.exists(self.errfile)
            with open(self.errfile, encoding="utf-8") as err:
                content = err.read()
                return content.strip()
        else:
            if self.proc:
                return self.proc.stderr.decode(encoding="utf-8").strip()
            raise SystemError("Process is None")

    def get_returncode(self) -> int:
        """Get returncode

        Returns:
            returncode of last process run or None
        """
        if self.returncode is not None:
            return self.returncode
        raise SystemError("Returncode is None")

    def run(self) -> int:
        """Run process in the foreground with subprocess.run

        Returns:
            returncode of new process
        """
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

    def run_bg(self) -> None:
        """Run process in the background
        TODO: Maybe merge with run()
        Note: Unlike run we need the full path of the binary here
        """

        self.background = True

        if (not isinstance(self.command, list)) and (not isinstance(self.command, str)):
            raise SystemError("Please supply a list of strings as command")

        if not isinstance(self.command[0], str):
            raise SystemError("Please supply a list of strings as command")

        if not all(map(lambda x: isinstance(x, str), self.command)):
            raise SystemError("Please supply a list of strings as command")

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

        # self.cmd = ["/usr/bin/ls", "/usr/bin/false", "/usr/bin/ls", "-lah", "wever"]
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
                os.execve(self.command[0], self.command, self.newenv)  # type: ignore
            except OSError as exception:
                logging.error("Caught excepton on execve: %s", exception)
                # raise exception
                logging.error("Will die now")
                os.abort()
        else:
            logging.info("Child pid is : %s", self.child)

    def get_status(self, poll: int = 1) -> Union[int, None, str]:
        """Returns the returncode of the process and polls if it hasn't yet
        finished.
        Returns "Running" if the process is still running.
        Returns "NotExisting" if the process does not exist anyore.
        """
        if self.child is None:
            return None

        status: Union[int, None, str] = None
        for _ in range(poll * 10):
            try:
                pid, status = os.waitpid(self.child, os.WNOHANG)
            except ChildProcessError:
                logging.debug("Process %i is not existing", self.child)
                return "NotExisting"
            # print(pid,status)
            if (pid, status) == (0, 0):
                logging.debug(
                    "No status available for child %s probably still running",
                    self.child,
                )
                status = "Running"
                return status

            if os.WIFEXITED(status):
                exitstatus = os.WEXITSTATUS(status)
                logging.debug("Exit status of background process %s", exitstatus)
                self.returncode = exitstatus
                return exitstatus

            time.sleep(0.1)

        return status

    def kill(self) -> None:
        """Kill the child process"""
        logging.debug("    Process: terminate: %s", self.command)
        if self.child == 0:
            logging.error("Somebody tried to kill the parent process")
        elif self.child is None:
            logging.debug("Child was never called, won't kill it")
        elif self.returncode is not None:
            logging.debug(
                "Child %s has already quit with %s, won't kill it",
                self.child,
                self.returncode,
            )
        else:
            logging.debug("Will kill %s with exit code %s", self.child, self.returncode)
            try:
                os.kill(self.child, signal.SIGKILL)
            except ProcessLookupError:
                logging.info(
                    "Process %s with pid %i already dead", self.name, self.child
                )
