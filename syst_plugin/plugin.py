import pytest
from .pyst_process import PystProcess

@pytest.fixture
def process():
    print("    >>>> We call a process")
    yield PystProcess(42)
    print("    <<<< We kill a process")

