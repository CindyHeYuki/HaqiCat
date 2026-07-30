"""Standard-library tests for the stage-zero project scaffold."""

import unittest

from haqicat import __version__
from haqicat.__main__ import main


class StageZeroTests(unittest.TestCase):
    def test_version_is_defined(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_scaffold_entry_point_runs(self) -> None:
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
