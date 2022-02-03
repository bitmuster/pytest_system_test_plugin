from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytest_system_test_plugin",
    version="0.0.2",
    packages=["syst_plugin"],
    author="Michael Abel",
    author_email="python@bitmuster.org",
    description="Pyst - Pytest System-Test Plugin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/bitmuster/pytest_system_test_plugin",
    project_urls={
        "GitLab": "https://gitlab.com/bitmuster/pytest_system_test_plugin",
        "GitHub": "https://github.com/bitmuster/pytest_system_test_plugin",
        "Examples": "https://github.com/abelikt/pytest_system_test_plugin_test"
    },
    entry_points={"pytest11": ["pytest_system_test_plugin = syst_plugin.plugin"]},
    classifiers=["Framework :: Pytest"],
)
