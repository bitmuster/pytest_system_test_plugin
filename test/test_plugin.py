import logging
import os
import os.path
import time
import pytest


def test_process_run(process):
    assert process.run() == 0


def test_process_set_config(process):
    process.set_config(33)
    assert process.get_config() == 33


def test_process_get_config(process):
    assert process.get_config() == "true"


def test_process_kill(process):
    process.set_config("read")
    with pytest.raises(SystemError):
        process.run_bg()
    assert process.kill() is None


def test_echo_hello(process):
    process.set_config(["echo", "hello", "world"])
    process.run()
    assert process.get_stdout() == "hello world"
    assert process.get_returncode() == 0


def test_run_background_echo_hello(process):
    process.set_config(["/usr/bin/sh", "-c", "/usr/bin/sleep 0.1"])
    process.run_bg()
    assert process.get_status() == 0


def test_run_background_echo_hello_fail(process):
    process.set_config(["/usr/bin/sh", "-c", "/usr/bin/sleep 0.1 ; false"])
    process.run_bg()
    assert process.get_status() == 1


def test_run_background_status_poll_fails(process):
    process.set_config(["/usr/bin/sleep", "3"])
    process.run_bg()
    assert process.get_status() is "Running"


def test_run_background_status_poll(process):
    process.set_config(["/usr/bin/sleep", "0.1"])
    process.run_bg()
    assert process.get_status(poll=1) == 0


@pytest.fixture
def echoserver(process):
    """
    Custom fixture
    """
    # TODO: Find bette way of getting an interpreter in the current env
    interpreter = os.path.abspath("./env-plugin/bin/python")
    process.set_config(
        [
            interpreter,
            "-m",
            "restapi_echo_server",
            "--host",
            "0.0.0.0",
            "--port",
            "8080",
        ]
    )
    yield process
    logging.info("Killing echoserver")
    process.kill()

@pytest.fixture
def asserts_echoserver():
    yield
    logging.info("Asserts Echoserver")

@pytest.fixture
def cleanup_echoserver():
    yield
    logging.info("Cleanup Echoserver")

def test_use_case_echo(echoserver):
    echoserver.run_bg()
    time.sleep(1)
    echoserver.kill()
    assert echoserver.get_status() == "NotExisting"

def test_use_case_echo_with_additional_cleanup(echoserver, asserts_echoserver, cleanup_echoserver):
    # Does not work right
    echoserver.run_bg()
    time.sleep(0.1)

def test_proc_factory(process_factory):
    proc1 = process_factory(["/usr/bin/sleep", "100"])
    proc2 = process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()
    proc2.run_bg()
    time.sleep(0.1)
    proc1.kill()
    proc2.kill()


def test_proc_factory_autokill(process_factory):
    proc1 = process_factory(["/usr/bin/sleep", "100"])
    proc2 = process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()
    proc2.run_bg()


def test_proc_factory_one_not_called(process_factory):
    # Test will pass and we will see a warning in pytest
    # TODO: can we run an assertion on that?
    proc1 = process_factory(["/usr/bin/sleep", "100"])
    proc2 = process_factory(["/usr/bin/sleep", "101"])
    proc1.run_bg()


def test_proc_factory_has_exited_with_error(process_factory):
    # args = ["/usr/bin/sh", "-c", "/usr/bin/sleep 0.1 ; false"]
    args = ["/usr/bin/false"]
    proc1 = process_factory(args)
    proc1.run_bg()
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
    assert proc1.get_status(5) == None
    assert proc1.get_returncode() == None


def test_use_case_echo_and_curl(process_factory, process):
    # TODO: Find bette way of getting an interpreter in the current env
    interpreter = os.path.abspath("./env-plugin/bin/python")
    server = process_factory(
        [
            interpreter,
            "-m",
            "restapi_echo_server",
            "--host",
            "0.0.0.0",
            "--port",
            "8080",
        ]
    )
    server.run_bg()
    # give the server 100ms to start in the background
    time.sleep(0.1)
    process.set_config(
        "/usr/bin/curl -X POST http://localhost:8080 -d hello_my_plugins".split()
    )
    assert process.run() == 0


def test_use_case_echo_and_curl_from_factory(process_factory, process):
    # TODO: Find bette way of getting an interpreter in the current env
    interpreter = os.path.abspath("./env-plugin/bin/python")
    server = process_factory(
        [
            interpreter,
            "-m",
            "restapi_echo_server",
            "--host",
            "0.0.0.0",
            "--port",
            "8080",
        ]
    )
    server.run_bg()
    assert server.get_status() == "Running" # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        "/usr/bin/curl -X POST http://localhost:8080 -d hello_my_plugins".split()
    )
    client.run_bg()


def test_grep_stdout_fg(process):
    process.set_config(["echo", "hello", "world"])
    process.run()
    assert process.get_stdout() == "hello world"
    assert process.get_returncode() == 0


def test_grep_stdout_bg(process):
    process.set_config(["/usr/bin/echo", "hello", "worldpeace"])
    process.run_bg()
    # time.sleep(0.1)
    assert process.get_status() == 0
    assert process.background is True
    assert process.get_stdout() == "hello worldpeace"
    assert process.get_returncode() == 0


def test_grep_stderr_bg(process):
    # process.set_config(["/bin/sh", "-c", "echo not found", ">&2"])
    process.set_config(["/usr/bin/ls", "notthere"])
    process.run_bg()
    # time.sleep(0.1)
    assert process.get_status() == 2
    assert process.background is True
    assert (
        process.get_stderr()
        == "/usr/bin/ls: cannot access 'notthere': No such file or directory"
    )
    assert process.get_returncode() == 2
