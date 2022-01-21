import logging
import os
import time
import pytest

CURL = "/usr/bin/curl -X POST http://localhost:{} -d hello_my_plugins"


@pytest.fixture
def echoserver(process_factory):
    """
    Custom fixture starts an echoserver on port 8090
    """
    # TODO: Find better way of getting an interpreter in the current env
    interpreter = os.path.abspath("./env-plugin/bin/python")
    process = process_factory(
        [
            interpreter,
            "-m",
            "restapi_echo_server",
            "--host",
            "0.0.0.0",
            "--port",
            "8090",
        ],
    )
    process.set_name("ecoserver")
    yield process
    logging.info("Killing echoserver")
    process.kill()


@pytest.fixture
def echoserver_2(process_factory):
    """
    Custom fixture starts an echoserver on port 8092
    """
    # TODO: Find better way of getting an interpreter in the current env
    interpreter = os.path.abspath("./env-plugin/bin/python")
    process = process_factory(
        [
            interpreter,
            "-m",
            "restapi_echo_server",
            "--host",
            "0.0.0.0",
            "--port",
            "8092",
        ],
    )
    process.set_name("ecoserver_2")
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
    process.set_command(
        CURL.format(8080).split(),
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
        ],
        "server_",
    )
    server.run_bg()
    assert server.get_status() == "Running"  # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        CURL.format(8080).split(),
        "client_",
    )
    client.run_bg()
    assert client.get_status() == 0
    server.kill()
    assert server.get_status() == "NotExisting"

    # For weird reasons the echoserver logs to stderr
    assert server.get_stdout() == ""
    assert "hello_my_plugins" in server.get_stderr()


def test_use_case_echoserver_fixture_and_curl(process_factory, echoserver):
    echoserver.run_bg()
    assert echoserver.get_status() == "Running"  # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        CURL.format(8090).split(),
        "client_",
    )
    client.run_bg()
    assert client.get_status() == 0
    echoserver.kill()
    assert echoserver.get_status() == "NotExisting"
    assert (
        echoserver.get_stdout() == ""
    )  # For weird reasons the echoserver logs to stderr
    assert "hello_my_plugins" in echoserver.get_stderr()


def test_use_case_echoserver_1_and_2(process_factory, echoserver, echoserver_2):

    echoserver_1 = echoserver

    echoserver_1.run_bg()
    echoserver_2.run_bg()

    assert echoserver_1.get_status() == "Running"
    assert echoserver_2.get_status() == "Running"

    time.sleep(0.1)

    client_a = process_factory(
        CURL.format(8090).split(),
        "client_a_",
    )

    client_b = process_factory(
        CURL.format(8092).split(),
        "client_b_",
    )

    client_a.run_bg()
    client_b.run_bg()

    assert client_a.get_status() == 0
    assert client_b.get_status() == 0

    echoserver_1.kill()
    echoserver_2.kill()

    assert echoserver_1.get_status() == "NotExisting"
    assert echoserver_2.get_status() == "NotExisting"

    assert "hello_my_plugins" in echoserver_1.get_stderr()
    assert "hello_my_plugins" in echoserver_2.get_stderr()