import time
import pytest

WAITSTATUS = 0.1


def test_process_run(process):
    assert process.run() == 0


def test_process_set_command(process):
    process.set_command(33)
    assert process.get_command() == 33


def test_process_get_command(process):
    assert process.get_command() == "true"


def test_process_kill(process):
    process.set_command("read")
    with pytest.raises(SystemError):
        process.run_bg()
    assert process.kill() is None


def test_echo_hello(process):
    process.set_command(["echo", "hello", "world"])
    process.run()
    time.sleep(WAITSTATUS)
    assert process.get_stdout() == "hello world"
    assert process.get_returncode() == 0


def test_run_background_echo_hello(process):
    process.set_command(["/usr/bin/sh", "-c", "/usr/bin/sleep 0.1"])
    process.run_bg()
    time.sleep(WAITSTATUS * 2)
    assert process.get_status() == 0


def test_run_background_echo_hello_fail(process):
    process.set_command(["/usr/bin/sh", "-c", "/usr/bin/sleep 0.1 ; false"])
    process.run_bg()
    time.sleep(WAITSTATUS * 2)
    assert process.get_status() == 1


def test_run_background_status_poll_fails(process):
    process.set_command(["/usr/bin/sleep", "3"])
    process.run_bg()
    assert process.get_status() == "Running"


def test_run_background_status_poll(process):
    process.set_command(["/usr/bin/sleep", "0.1"])
    process.run_bg()
    time.sleep(WAITSTATUS * 2)
    assert process.get_status(poll=1) == 0


# Factory tests


def test_proc_factory_int(process_factory):
    # TODO With mypy in place this should not pass
    process_factory(88)


def test_proc_factory(process_factory):
    proc1 = process_factory(["/usr/bin/sleep", "100"])
    proc2 = process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()
    proc2.run_bg()
    time.sleep(0.1)
    proc1.kill()
    proc2.kill()


def test_proc_factory_with_prefix(process_factory):
    proc1 = process_factory(["/usr/bin/sleep", "100"], name="hundred")
    proc2 = process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()
    proc2.run_bg()


def test_proc_factory_autokill(process_factory):
    proc1 = process_factory(["/usr/bin/sleep", "100"])
    proc2 = process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()
    proc2.run_bg()


def test_proc_factory_one_not_called(process_factory):
    # Test will pass and we will see a warning in pytest
    # TODO: can we run an assertion on that?
    proc1 = process_factory(["/usr/bin/sleep", "100"])
    process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()


def test_proc_factory_has_exited_with_error(process_factory):
    # args = ["/usr/bin/sh", "-c", "/usr/bin/sleep 0.1 ; false"]
    args = ["/usr/bin/false"]
    proc1 = process_factory(args)
    proc1.run_bg()
    time.sleep(WAITSTATUS)
    assert proc1.get_status(5) == 1
    assert proc1.get_returncode() == 1
    time.sleep(1)


def test_proc_factory_was_never_started(process_factory):
    # Will happen when we call without the full path or invalid arguents.
    # E.g. if os.fork failed for that process.
    # In this case we will see the last complaints in stderr of the process
    # since we fist fork and then exeve
    args = ["idonotexist"]
    proc1 = process_factory(args)

    with pytest.raises(SystemError):
        proc1.run_bg()

    assert proc1.get_status(5) is None

    with pytest.raises(SystemError):
        proc1.get_returncode()


def test_grep_stdout_fg(process):
    process.set_command(["echo", "hello", "world"])
    process.run()
    assert process.get_stdout() == "hello world"
    assert process.get_returncode() == 0


def test_grep_stdout_bg(process):
    process.set_command(["/usr/bin/echo", "hello", "worldpeace"])
    process.run_bg()
    # time.sleep(0.1)
    time.sleep(WAITSTATUS)
    assert process.get_status() == 0
    assert process.background is True
    assert process.get_stdout() == "hello worldpeace"
    assert process.get_returncode() == 0


def test_grep_stderr_bg(process):
    # process.set_command(["/bin/sh", "-c", "echo not found", ">&2"])
    process.set_command(["/usr/bin/ls", "notthere"])
    process.run_bg()
    # time.sleep(0.1)
    time.sleep(WAITSTATUS)
    assert process.get_status() == 2
    assert process.background is True
    assert (
        process.get_stderr()
        == "/usr/bin/ls: cannot access 'notthere': No such file or directory"
    )
    assert process.get_returncode() == 2
