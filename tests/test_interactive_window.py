"""Tests for motion timing and direct pet interactions."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from haqicat.interactive_window import InteractivePetWindow


class InteractivePetWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = InteractivePetWindow()

    def tearDown(self) -> None:
        self.window.close()

    def test_motion_timer_uses_bounded_low_frame_rate(self) -> None:
        interval = self.window.diagnostic_state()["motion_interval_ms"]
        self.assertGreaterEqual(interval, 60)
        self.assertLessEqual(interval, 250)

    def test_drag_pose_anchors_below_cursor_and_restores(self) -> None:
        self.window._begin_drag_pose()
        self.assertTrue(self.window.diagnostic_state()["drag_pose_active"])
        self.assertEqual(
            self.window._drag_offset.x(),
            self.window.width() // 2,
        )
        self.assertEqual(self.window._drag_offset.y(), self.window.DRAG_LIFT_Y_PX)
        self.window._end_drag_pose()
        self.assertFalse(self.window.diagnostic_state()["drag_pose_active"])

    def test_single_click_handler_hisses(self) -> None:
        self.window._handle_single_click()
        self.assertEqual(self.window.state, "hiss")

    def test_sleep_toggle_changes_state_and_frame_rate(self) -> None:
        self.window.toggle_sleep()
        self.assertEqual(self.window.state, "sleep")
        self.assertEqual(
            self.window.diagnostic_state()["motion_interval_ms"],
            self.window.SLEEP_FRAME_INTERVAL_MS,
        )

        self.window.toggle_sleep()
        self.assertEqual(self.window.state, "idle")
        self.assertEqual(
            self.window.diagnostic_state()["motion_interval_ms"],
            self.window.ACTIVE_FRAME_INTERVAL_MS,
        )


if __name__ == "__main__":
    unittest.main()
