import pytest

def test_process_run(process):
    assert process.run() == 0

def test_process_set_config(process):
    process.set_config(33)
    assert process.get_config() == 33

def test_process_get_config(process):
    assert process.get_config() == "true"

def test_process_terminate(process):
    assert process.terminate() == None


