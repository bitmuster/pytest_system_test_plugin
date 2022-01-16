
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
    * Prepare configuration files
* Provides envioronment fixtures
* Multistage environments fixtures
    * Supports you to write your own fixures


## Prepare

    python3 -m venv env-plugin
    source env-plugin/bin/activate
    pip install pytest


## Usage


## Test

    pip install .; python -m pytest -s
    tox
    tox -e {lint, linttest}



## Links

* https://docs.pytest.org
* https://github.com/pysys-test/pysys-test
* https://github.com/CS-SI/pytest-executable



