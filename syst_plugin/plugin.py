""" Pysst: A Pytest System-Test Plugin
"""

import logging
import secrets

import pytest
from . import PystProcess

# logging.basicConfig(level=logging.DEBUG)

# TODO: Automatically delete output folders


@pytest.fixture(scope="function")
def process(request):
    """process base fixture
    Issue: When used multiple time in one test it will return cached results !!!
    """
    logging.debug("    >>>> We call a process")
    # So far, until we have nice mechanics to modify this we only run true
    yield PystProcess(
        command="true", logpath=request.fspath, testname=request.node.name
    )
    logging.debug("    <<<< We kill a process")


@pytest.fixture(scope="function")
def process_factory(request):
    """process base fixture factory"""

    processes = []

    def _make_process(cmd, name=None):
        if not name:
            name = secrets.token_hex(2) + "_"
        logging.debug("    >>>>>>>> We generate a process with name %s", name)
        proc = PystProcess(
            command=cmd, logpath=request.fspath, testname=request.node.name, name=name
        )
        processes.append(proc)
        return proc

    yield _make_process

    logging.debug("    <<<<<<<< We kill a generated process")

    # TODO: Do we kill processes in the right order?
    # TODO: Wo we kill them right?
    for proc in processes:
        logging.info("Killing process %s with pid %s", proc.name, proc.child)
        proc.kill()


@pytest.fixture(scope="module")
def process_factory_module(request):
    """process base fixture factory
    TODO: Avoid duplication of code
    TODO: Test this with pytester
    """

    processes = []

    def _make_process(cmd, name=None):
        if not name:
            name = secrets.token_hex(2) + "_"
        logging.info(
            "    >>>>>>>> We generate a module scope process with name %s", name
        )
        proc = PystProcess(
            command=cmd, logpath=request.fspath, testname=request.node.name, name=name
        )
        processes.append(proc)
        return proc

    yield _make_process

    # TODO: Do we kill processes in the right order?
    # TODO: Wo we kill them right?
    for proc in processes:
        logging.info("    <<<<<<<< We kill a module scope generated process")
        logging.info("Killing process %s", proc.child)
        proc.kill()


@pytest.fixture(scope="session")
def process_factory_session(request):
    """process base fixture factory
    TODO: Avoid duplication of code
    TODO: Test this with pytester
    """
    processes = []

    def _make_process(cmd, name=None):
        if not name:
            name = secrets.token_hex(2) + "_"
        logging.info(
            "    >>>>>>>> We generate a session scope process with name %s", name
        )
        proc = PystProcess(
            command=cmd, logpath="session_", testname=request.node.name, name=name
        )
        processes.append(proc)
        return proc

    yield _make_process

    # TODO: Do we kill processes in the right order?
    # TODO: Wo we kill them right?
    for proc in processes:
        logging.info("    <<<<<<<< We kill a session scope generated process")
        logging.info("Killing process %s", proc.child)
        proc.kill()
