
# Pyst - Pytest System-Test Plugin

Note: This plugin is the state experimental / techdemo !

This plugin should ease system-testing with Pytest.
To achieve this it provides a simple interface to
manage processes in the operating system like starting them,
running background processes and evaluating the output.

This is especially useful to prepare the system
(e.g. start background prcesses, databases, servers, ...) and then
run the programm under test in a blackbox-manner.

Features should be (intended, unfinished):

* Starting, stopping and managing processes in the OS
* Pysys like interface to run systemtests
    * Especially startProcess and assertGrep
* Logs all outputs to files and can later on run assertions on that outputs
* Should work:
    * Start and stop processes with and without sudo
    * Prepare configuration files for executables
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

Have a look at tests/test_use_cases.py it contains some exemplary use-cases.
We use an echo-server and curl to be near to real use cases. More will be added
soon.

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

Pytest test-framework:

* https://docs.pytest.org

PySys test-framework:

* https://pysys-test.github.io/pysys-test

Similar plugins:

* https://github.com/pysys-test/pysys-test
* https://github.com/CS-SI/pytest-executable



