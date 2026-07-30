"""Tests for the stage-one desktop-pet window."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QApplication

from haqicat.window import PetWindow


class PetWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = PetWindow()

    def tearDown(self) -> None:
        self.window.close()

    def test_window_has_desktop_pet_flags(self) -> None:
        flags = self.window.windowFlags()
        self.assertTrue(flags & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(flags & Qt.WindowType.WindowStaysOnTopHint)
        self.assertTrue(flags & Qt.WindowType.Tool)
        self.assertTrue(
            self.window.testAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground
            )
        )

    def test_clamp_to_bounds_limits_all_edges(self) -> None:
        bounds = QRect(100, 50, 800, 600)
        size = QSize(240, 220)

        self.assertEqual(
            PetWindow.clamp_to_bounds(QPoint(-500, -500), bounds, size),
            QPoint(100, 50),
        )
        self.assertEqual(
            PetWindow.clamp_to_bounds(QPoint(5000, 5000), bounds, size),
            QPoint(660, 430),
        )
        self.assertEqual(
            PetWindow.clamp_to_bounds(QPoint(300, 250), bounds, size),
            QPoint(300, 250),
        )


if __name__ == "__main__":
    unittest.main()

