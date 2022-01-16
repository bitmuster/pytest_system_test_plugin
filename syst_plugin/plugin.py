""" Pysst: A Pytest System-Test Plugin
"""

import logging
import pytest
from .pyst_process import PystProcess

# logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def process(request):
    """process base fixture"""
    logging.debug("    >>>> We call a process")
    # So far, until we have nice mechanics to modify this we only run true
    yield PystProcess("true", testname=request.node.name)
    logging.debug("    <<<< We kill a process")


@pytest.fixture
def process_factory(request):
    """process base fixture factory"""

    processes = []

    def _make_process(cmd):
        logging.debug("    >>>>>>>> We generate a process")
        proc = PystProcess(cmd, testname=request.node.name)
        processes.append(proc)
        return proc

    yield _make_process

    logging.debug("    <<<<<<<< We kill a generated process")

    for proc in processes:
        logging.info("Killing process %s", proc.child)
        proc.kill()
