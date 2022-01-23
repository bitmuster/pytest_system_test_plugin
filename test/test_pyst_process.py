import pytest
from syst_plugin.pyst_process import PystProcess


def test_init():
    # TODO With mypy in place this should not pass
    pystp = PystProcess(22, __file__)
    assert pystp.get_command() == 22


def test_get_set_command():
    pystp = PystProcess(33, __file__)
    assert pystp.get_command() == 33
    pystp.set_command(77)
    assert pystp.get_command() == 77


def test_kill_on_not_existing():
    pystp = PystProcess(["notexist"], __file__)
    with pytest.raises(SystemError):
        pystp.run_bg()
    assert pystp.kill() is None


def test_set_name():
    pystp = PystProcess(["theone"], __file__)
    pystp.set_name("one")
    assert pystp.get_name() == "one"


def test_echo():
    pystp = PystProcess(["echo", "hello", "world"], __file__)
    pystp.run()
    assert pystp.get_stdout() == "hello world"
    assert pystp.get_returncode() == 0


def test_true():
    pystp = PystProcess("true", __file__)
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_returncode() == 0


def test_true_not_started():
    pystp = PystProcess("true", __file__)
    with pytest.raises(SystemError):
        pystp.get_stdout()
    with pytest.raises(SystemError):
        pystp.get_stderr()
    with pytest.raises(SystemError):
        pystp.get_stderr()
    with pytest.raises(SystemError):
        pystp.get_returncode()


def test_true_with_name():
    pystp = PystProcess("true", __file__, name="Bob_")
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_returncode() == 0
    assert pystp.outfile.endswith("Bob_stdout.out")
    assert pystp.errfile.endswith("Bob_stderr.out")


def test_false():
    pystp = PystProcess("false", __file__)
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_stderr() == ""
    assert pystp.get_returncode() == 1


def test_stderr():
    exp = "ls: cannot access 'notthere': No such file or directory"
    pystp = PystProcess(["ls", "notthere"], __file__)
    pystp.run()
    assert pystp.get_stdout() == ""
    assert pystp.get_stderr() == exp
    assert pystp.get_returncode() == 2


def test_stderr_file():
    exp = "ls: cannot access 'notthere': No such file or directory"
    pystp = PystProcess(["ls", "notthere"], __file__)
    pystp.run()
    assert pystp.get_stderr() == exp


def test_stdout_file():
    exp = "hello nice ball"
    pystp = PystProcess(["echo", "hello", "nice", "ball"], __file__)
    pystp.run()
    assert pystp.get_stdout() == exp


def test_run(mocker):
    runmock = mocker.MagicMock()
    runmock.stdout = b"whatever"
    runmock.stderr = b"nope"
    mock = mocker.patch("subprocess.run", return_value=runmock)
    mocker.patch("__main__.open", mocker.mock_open(read_data="stuff"))
    pystp = PystProcess("false", __file__)

    pystp.run()

    mock.assert_called_once_with(
        "false", stdout=mocker.ANY, stderr=mocker.ANY, check=False
    )


def test_run_bg_parent(mocker):
    fmock = mocker.patch("os.fork", return_value=44)
    emock = mocker.patch("os.execve")
    pystp = PystProcess("/usr/bin/false", __file__)
    pystp.run_bg()
    fmock.assert_called_once_with()
    emock.assert_not_called()


def test_run_bg_child(mocker):
    fmock = mocker.patch("os.fork", return_value=0)
    emock = mocker.patch("os.execve")
    mocker.patch("os.dup2")
    mocker.patch("os.open")
    mocker.patch("os.setpgrp")

    pystp = PystProcess("/usr/bin/false", __file__)

    pystp.run_bg()

    fmock.assert_called_once_with()
    emock.assert_called_once_with("/", "/usr/bin/false", {})


def test_run_bg_child_wrong_args(mocker):
    fmock = mocker.patch("os.fork")
    emock = mocker.patch("os.execve")
    pystp = PystProcess(42, __file__)

    with pytest.raises(SystemError):
        pystp.run_bg()

    fmock.assert_not_called()
    emock.assert_not_called()


def test_run_bg_child_wrong_args_b(mocker):
    fmock = mocker.patch("os.fork")
    emock = mocker.patch("os.execve")
    pystp = PystProcess([42, 42], __file__)

    with pytest.raises(SystemError):
        pystp.run_bg()

    fmock.assert_not_called()
    emock.assert_not_called()
