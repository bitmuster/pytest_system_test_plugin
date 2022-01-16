import logging
import os
import time
import pytest

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
    # If this fails, there is maybe still one running
    assert echoserver.get_status() == "NotExisting"


def test_use_case_echo_with_additional_cleanup(
    echoserver, asserts_echoserver, cleanup_echoserver
):
    # Does not work right
    echoserver.run_bg()
    time.sleep(0.1)


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


def test_use_case_echo_and_curl_from_factory(process_factory):
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
        ], "server_"
    )
    server.run_bg()
    assert server.get_status() == "Running"  # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        "/usr/bin/curl -X POST http://localhost:8080 -d hello_my_plugins".split(),
        "client_"
    )
    client.run_bg()
    assert client.get_status() == 0
    server.kill()
    assert server.get_status() == "NotExisting"
    assert server.get_stdout() == "" # For weird reasons the echoserver logs to stderr
    assert "hello_my_plugins" in server.get_stderr()

def test_use_case_echoserver_fixture_and_curl(process_factory, echoserver):
    echoserver.run_bg()
    assert echoserver.get_status() == "Running"  # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        "/usr/bin/curl -X POST http://localhost:8080 -d hello_my_plugins".split(),
        "client_"
    )
    client.run_bg()
    assert client.get_status() == 0
    echoserver.kill()
    assert echoserver.get_status() == "NotExisting"
    assert echoserver.get_stdout() == "" # For weird reasons the echoserver logs to stderr
    assert "hello_my_plugins" in echoserver.get_stderr()
