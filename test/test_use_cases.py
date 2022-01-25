import logging
import os
import time
import pytest

CURL = "/usr/bin/curl -X POST http://localhost:{} -d hello_my_plugins"
WAITSTATUS = 0.1


def get_factory_args(port):

    # TODO: Find better way of getting an interpreter in the current env
    interpreter = os.path.abspath("./env-plugin/bin/python")

    args = [
        interpreter,
        "-m",
        "restapi_echo_server",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
    ]
    return args


@pytest.fixture(name="echoserver")
def fixture_echoserver(process_factory):
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
    process.set_name("echoserver_")
    yield process
    logging.info("Killing echoserver")
    process.kill()


@pytest.fixture(name="echoserver_2")
def fixture_echoserver_2(process_factory):
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
    process.set_name("ecoserver_2_")
    yield process
    logging.info("Killing echoserver")
    process.kill()


@pytest.fixture(name="asserts_echoserver")
def fixture_asserts_echoserver():
    yield
    logging.info("Asserts Echoserver")


@pytest.fixture(name="cleanup_echoserver")
def fixture_cleanup_echoserver():
    yield
    logging.info("Cleanup Echoserver")


def test_use_case_echo(echoserver):
    echoserver.run_bg()
    time.sleep(1)
    echoserver.kill()
    time.sleep(WAITSTATUS)
    # If this fails, there is maybe still one running
    assert echoserver.get_status() == "NotExisting"


def test_use_case_echo_with_additional_cleanup(
    echoserver, asserts_echoserver, cleanup_echoserver
):
    _ = asserts_echoserver  # for now just use them otherwise pylint will complain
    _ = cleanup_echoserver

    # Does not work right
    echoserver.run_bg()
    time.sleep(0.1)


def test_use_case_echo_and_curl(process_factory, process):
    # TODO: Find better way of getting an interpreter in the current env
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
    # TODO: Find better way of getting an interpreter in the current env
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
    time.sleep(WAITSTATUS)
    assert server.get_status() == "Running"  # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        CURL.format(8080).split(),
        "client_",
    )
    client.run_bg()
    time.sleep(WAITSTATUS)
    assert client.get_status() == 0
    server.kill()
    time.sleep(WAITSTATUS)
    assert server.get_status() == "NotExisting"

    # For weird reasons the echoserver logs to stderr
    assert server.get_stdout() == ""
    assert "hello_my_plugins" in server.get_stderr()


def test_use_case_echoserver_fixture_and_curl(process_factory, echoserver):
    echoserver.run_bg()
    time.sleep(WAITSTATUS)  # give the server some time to start
    assert echoserver.get_status() == "Running"  # make sure it still runs
    # give the server 100ms to start in the background
    time.sleep(0.1)
    client = process_factory(
        CURL.format(8090).split(),
        "client_",
    )
    client.run_bg()
    time.sleep(WAITSTATUS)
    assert client.get_status() == 0
    echoserver.kill()
    time.sleep(WAITSTATUS)
    assert echoserver.get_status() == "NotExisting"
    assert (
        echoserver.get_stdout() == ""
    )  # For weird reasons the echoserver logs to stderr
    assert "hello_my_plugins" in echoserver.get_stderr()


def test_use_case_echoserver_1_and_2(process_factory, echoserver, echoserver_2):

    echoserver_1 = echoserver

    echoserver_1.run_bg()
    echoserver_2.run_bg()
    time.sleep(0.1)
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
    time.sleep(0.1)
    assert client_a.get_status() == 0
    assert client_b.get_status() == 0

    echoserver_1.kill()
    echoserver_2.kill()
    time.sleep(0.1)
    assert echoserver_1.get_status() == "NotExisting"
    assert echoserver_2.get_status() == "NotExisting"

    assert "hello_my_plugins" in echoserver_1.get_stderr()
    assert "hello_my_plugins" in echoserver_2.get_stderr()


def test_use_case_echo_and_curl_from_factory_n(process_factory):

    amount = 10
    servers = []
    clients = []

    for i in range(amount):
        server = process_factory(get_factory_args(8080 + i), f"server_{i}_")
        server.run_bg()
        servers.append(server)

    time.sleep(0.1)

    logging.info("Polling server status")
    for server in servers:
        status = server.get_status()
        if status != "Running":
            logging.error("Something went wrong here is stdout")
            logging.error(server.get_stdout())
            logging.error("Something went wrong here is stderr")
            logging.error(server.get_stderr())
            assert status == "Running"

    time.sleep(0.5)
    logging.info("Starting clients")

    for i in range(amount):
        client = process_factory(
            CURL.format(8080 + i).split(),
            f"client_{i}_",
        )
        client.run_bg()

    time.sleep(0.5)
    logging.info("Polling clients")

    # We expect, that all clients exited with zero
    for client in clients:
        assert client.get_status() == 0
        clients.append(client)

    for server in servers:
        server.kill()

    time.sleep(0.1)

    for server in servers:
        assert server.get_status() == "NotExisting"

    for server in servers:
        # For weird reasons the echoserver logs to stderr
        assert server.get_stdout() == ""
        assert "hello_my_plugins" in server.get_stderr()

    for client in clients:
        assert "method" in client.get_stdout()
        assert "Total" in client.get_stderr()
