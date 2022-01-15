
import pytest
from syst_plugin.pyst_process import PystProcess


def test_init():
    pystp = PystProcess(22)
    assert pystp.get_config() == 22

def test_get_set_config():
    pystp = PystProcess(33)
    assert pystp.get_config() == 33
    pystp.set_config(77)
    assert pystp.get_config() == 77

def test_terminate():
    pystp = PystProcess(22)
    assert pystp.run() == 22
    assert pystp.terminate() == None

