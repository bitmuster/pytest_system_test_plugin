import pytest
from .pyst_process import PystProcess

@pytest.fixture
def process():
    print("    >>>> We call a process")
    # So far, until we have nice mechanics to mithify this we only run true
    yield PystProcess("true")
    print("    <<<< We kill a process")

