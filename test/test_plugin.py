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
    assert process.get_status() is None


def test_run_background_status_poll(process):
    process.set_config(["/usr/bin/sleep", "0.1"])
    process.run_bg()
    assert process.get_status(poll=1) == 0


def test_use_case_echo(process):
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
    process.run_bg()
    time.sleep(1)
    process.kill()


def test_use_case_echo_and_curl(process):
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
    process.run_bg()

    "curl -X POST http://localhost:8080 -d hello_my_plugins"

    time.sleep(1)
    process.kill()


