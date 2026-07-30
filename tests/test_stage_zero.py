"""Standard-library tests for project metadata and CLI options."""

import unittest

from haqicat import __version__
from haqicat.app import build_parser


class StageZeroTests(unittest.TestCase):
    def test_version_is_defined(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_smoke_test_option_is_available(self) -> None:
        arguments = build_parser().parse_args(["--smoke-test"])
        self.assertTrue(arguments.smoke_test)


if __name__ == "__main__":
    unittest.main()
