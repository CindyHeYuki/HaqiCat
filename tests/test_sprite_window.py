"""Tests for the sprite-driven desktop-pet window."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from haqicat.sprite_window import SpritePetWindow


class SpritePetWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = SpritePetWindow()

    def tearDown(self) -> None:
        self.window.close()

    def test_all_required_sprites_load(self) -> None:
        diagnostics = self.window.diagnostic_state()
        self.assertTrue(diagnostics["sprites_loaded"])
        self.assertEqual(
            set(self.window.sprite_paths),
            {
                "idle",
                "hiss",
                "sleep",
                "drag",
                "crawl_left",
                "crawl_right",
                "observe_left",
                "observe_right",
                "rise_left",
                "rise_right",
            },
        )

    def test_sleep_stops_idle_timer_and_idle_restarts_it(self) -> None:
        self.window.set_state("sleep")
        self.assertEqual(self.window.state, "sleep")
        self.assertFalse(self.window._idle_timer.isActive())

        self.window.set_state("idle")
        self.assertEqual(self.window.state, "idle")
        self.assertTrue(self.window._idle_timer.isActive())

    def test_idle_animation_is_low_frequency(self) -> None:
        self.assertGreaterEqual(
            self.window.diagnostic_state()["idle_interval_ms"],
            500,
        )


if __name__ == "__main__":
    unittest.main()

