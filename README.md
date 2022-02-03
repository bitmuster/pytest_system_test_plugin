
# Pyst - Pytest System-Test Plugin

Note: This plugin is the state experimental / techdemo !

This plugin should ease system-testing with Pytest.
To achieve this it provides a simple interface to
manage processes in the operating system like starting them,
running background processes and evaluating the output.

This is especially useful to prepare the system for a test
(e.g. start background prcesses, databases, servers, ...) and then
run the programm under test in a blackbox-manner.

Features should be (intended, partly unfinished):

* DONE: Starting, stopping and managing processes in the OS
* DONE: Pysys like interface to run systemtests
    * Especially startProcess and assertGrep
* DONE: Logs all outputs to files and can later on run assertions on that outputs
* Should work:
    * DONE: Start and stop processes with and without sudo
    * Prepare configuration files for executables
* DONE: Simple user fixtures
* Provides envioronment fixtures / group fixtures / environments (terminology
    depends on the framework you are used to).
* Multistage environments fixtures
    * Supports you to write your own fixures


So far, this will only un on unix-like systems.

## Prepare

    python3 -m venv env-plugin
    source env-plugin/bin/activate
    pip install pytest
    pip install pytest-mock
    pip install restapi_echo_server
    or
    pip install -r requirements.txt

## Usage

Have a look at [tests/test_use_cases.py](tests/test_use_cases.py) it
contains some exemplary use-cases.
We use an echo-server and curl to be near to real use cases. More will be added
soon.


## Example


Some other use cases are here https://github.com/abelikt/pytest_system_test_plugin_test

    import re
    import pytest

    def test_use_rolldice(process_factory):
        """This test installs a package via the package management, uses
        it and removes it again.
        """

        # make sure it is not installed
        call = process_factory(["whereis", "rolldice"])
        call.run()
        assert call.get_stdout() == "rolldice:"
        assert call.returncode == 0

        # Install package
        install = process_factory(["sudo", "apt-get", "install", "-y", "-q", "rolldice"])
        install.run()
        assert install.returncode == 0

        # Call and check output against a regex
        call = process_factory(["rolldice", "6"])
        call.run()
        print(call.get_stdout())
        print(call.get_stderr())

        # match a single digit
        assert re.match(r"^\d$", call.get_stdout()) is not None
        assert call.returncode == 0

        # deinstall it
        deinstall = process_factory(["sudo", "apt-get", "remove", "-y", "-q", "rolldice"])
        deinstall.run()
        assert install.returncode == 0

## Test

    pip install .; python -m pytest -s --log-cli-level=INFO
    tox
    tox -e {lint, linttest}

### Measure test execution

    pip install .; python -m pytest -s --log-cli-level=INFO --junitxml=junit.xml
    xmllint junit.xml --format > junitf.xml


## Links

This repo:

* https://gitlab.com/bitmuster/pytest_system_test_plugin
* https://github.com/bitmuster/pytest_system_test_plugin

Some exemplary tests:

* https://github.com/abelikt/pytest_system_test_plugin_test

Pytest test-framework:

* https://docs.pytest.org

PySys test-framework:

* https://pysys-test.github.io/pysys-test

Similar plugins:

* https://github.com/pysys-test/pysys-test
* https://github.com/CS-SI/pytest-executable



