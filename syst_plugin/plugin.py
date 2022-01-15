import pytest


@pytest.fixture
def process():
    print("    >>>> We call a process")
    yield 42
    print("    <<<< We kill a process")

