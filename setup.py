from setuptools import setup

setup(
    name="pytest_system_test_plugin",
    version="0.0.1",
    packages=["syst_plugin"],
    entry_points={"pytest11": ["pytest_system_test_plugin = syst_plugin.plugin"]},
    classifiers=["Framework :: Pytest"],
)
