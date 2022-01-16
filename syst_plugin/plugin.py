""" Pysst: A Pytest System-Test Plugin
"""

import logging
import pytest
from .pyst_process import PystProcess

# logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def process():
    """process base fixture"""
    logging.debug("    >>>> We call a process")
    # So far, until we have nice mechanics to mithify this we only run true
    yield PystProcess("true")
    logging.debug("    <<<< We kill a process")
