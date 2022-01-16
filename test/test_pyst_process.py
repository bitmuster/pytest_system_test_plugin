import os
import os.path
import time
import pytest
from syst_plugin.pyst_process import PystProcess


def test_init():
    pystp = PystProcess(22)
    assert pystp.get_command() == 22


def test_get_set_command():
    pystp = PystProcess(33)
    assert pystp.get_command() == 33
    pystp.set_command(77)
    assert pystp.get_command() == 77


def test_kill_on_not_existing():
    pystp = PystProcess(["notexist"])
    with pytest.raises(SystemError):
        pystp.run_bg()
    assert pystp.kill() is None


def test_set_name():
    pystp = PystProcess(["theone"])
    pystp.set_name("one")
    assert pystp.get_name() == "one"


def test_echo():
    pystp = PystProcess(["echo", "hello", "world"])
    pystp.run()
    assert pystp.get_stdout() == "hello world"
    assert pystp.get_returncode() == 0


def test_true():
    pystp = PystProcess("true")
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_returncode() == 0


def test_true_with_name():
    pystp = PystProcess("true", name="Bob_")
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_returncode() == 0
    assert pystp.outfile.endswith("Bob_stdout.out")
    assert pystp.errfile.endswith("Bob_stderr.out")


def test_false():
    pystp = PystProcess("false")
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_stderr() == ""
    assert pystp.get_returncode() == 1


def test_stderr():
    pystp = PystProcess(["ls", "notthere"])
    pystp.run()
    assert pystp.get_stdout() == ""
    assert (
        pystp.get_stderr() == "ls: cannot access 'notthere': No such file or directory"
    )
    assert pystp.get_returncode() == 2


def test_stderr_file():
    exp = "ls: cannot access 'notthere': No such file or directory"
    pystp = PystProcess(["ls", "notthere"])
    pystp.run()
    # content = os.path.abspath(
    #    os.path.join(os.path.dirname(__file__), "../syst_plugin/out/stderr.out")
    # )
    # print(content)
    # with open(content, encoding="utf-8") as out:
    #    assert out.read().strip() == exp
    assert pystp.get_stderr() == exp


def test_stdout_file():
    exp = "hello nice ball"
    pystp = PystProcess(["echo", "hello", "nice", "ball"])
    pystp.run()
    # content = os.path.abspath(
    #    os.path.join(os.path.dirname(__file__), "../syst_plugin/out/stdout.out")
    # )
    # with open(content, encoding="utf-8") as out:
    #    assert out.read().strip() == exp
    assert pystp.get_stdout() == exp
