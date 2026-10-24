"""Load the extensionless tools from ~/.local/bin as modules."""

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parents[1] / "bin"


def load(name):
    loader = SourceFileLoader(name, str(BIN / name))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def narrate():
    return load("narrate")


@pytest.fixture(scope="session")
def scan2pdf():
    return load("scan2pdf")


@pytest.fixture(scope="session")
def xzarchive():
    return load("xzarchive")


@pytest.fixture(scope="session")
def dbdump():
    return load("dbdump")


@pytest.fixture(scope="session")
def dotcheck():
    return load("dotcheck")


@pytest.fixture(scope="session")
def subs():
    return load("subs")
