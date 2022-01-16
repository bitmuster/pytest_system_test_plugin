import pytest
from .pyst_process import PystProcess

debug = False


@pytest.fixture
def process():
    if debug:
        print("    >>>> We call a process")
    # So far, until we have nice mechanics to mithify this we only run true
    yield PystProcess("true")
    if debug:
        print("    <<<< We kill a process")
