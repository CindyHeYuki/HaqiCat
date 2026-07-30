"""Tests for the stage-zero project scaffold."""

from haqicat import __version__
from haqicat.__main__ import main


def test_version_is_defined() -> None:
    assert __version__ == "0.1.0"


def test_scaffold_entry_point_runs() -> None:
    assert main() == 0

