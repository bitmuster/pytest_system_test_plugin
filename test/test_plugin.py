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


def test_echo_hello(process):
    process.set_config(["echo", "hello", "world"])
    process.run()
    assert process.get_stdout() == "hello world"
    assert process.get_returncode() == 0


def test_run_background_echo_hello(process):
    process.set_config(["/usr/bin/sh", "-c", "/usr/bin/sleep 1"])
    process.run_bg()
    assert process.get_status() == 0


def test_run_background_echo_hello_fail(process):
    process.set_config(["/usr/bin/sh", "-c", "/usr/bin/sleep 1 ; false"])
    process.run_bg()
    assert process.get_status() == 1


def test_run_background_status_poll_fails(process):
    process.set_config(["/usr/bin/sleep", "3"])
    process.run_bg()
    assert process.get_status() == None


def test_run_background_status_poll(process):
    process.set_config(["/usr/bin/sleep", "3"])
    process.run_bg()
    assert process.get_status(poll=4) == 0
