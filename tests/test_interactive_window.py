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
        self.assertTrue(self.window.diagnostic_state()["landing_active"])
        self.assertTrue(self.window._landing_timer.isActive())
        self.assertEqual(self.window.state, "idle")
        self.window._finish_landing_animation()
        self.assertFalse(self.window.diagnostic_state()["landing_active"])
        self.assertFalse(self.window._landing_timer.isActive())

    def test_walk_moves_then_stops_to_observe(self) -> None:
        screen = self.window.screen()
        self.assertIsNotNone(screen)
        bounds = screen.availableGeometry()
        self.window.move(bounds.left() + 50, bounds.top() + 50)
        start_x = self.window.x()

        self.window._start_walk(direction=1, steps=1)
        self.assertEqual(self.window.state, "walk_right")
        self.window._advance_walk()

        self.assertEqual(self.window.x(), start_x + self.window.WALK_STEP_PX)
        self.assertEqual(self.window.state, "idle")
        self.assertTrue(self.window.diagnostic_state()["observing_active"])
        self.assertTrue(self.window._observe_timer.isActive())
        self.window._finish_observing()
        self.assertFalse(self.window.diagnostic_state()["observing_active"])

    def test_walk_turns_around_at_screen_edge(self) -> None:
        screen = self.window.screen()
        self.assertIsNotNone(screen)
        bounds = screen.availableGeometry()
        rightmost_x = bounds.right() - self.window.width() + 1
        self.window.move(rightmost_x, bounds.top())

        self.window._start_walk(direction=1, steps=5)
        self.window._advance_walk()

        self.assertEqual(self.window.x(), rightmost_x)
        self.assertEqual(self.window._walk_direction, -1)
        self.assertEqual(self.window.state, "walk_left")
        self.assertEqual(self.window._walk_steps_remaining, 5)

    def test_walk_animation_uses_four_loaded_phases(self) -> None:
        diagnostics = self.window.diagnostic_state()
        self.assertTrue(diagnostics["walk_animation_loaded"])
        self.assertEqual(diagnostics["walk_animation_frames"], 4)

        self.window._start_walk(direction=1, steps=5)
        self.assertEqual(
            self.window.diagnostic_state()["walk_frame_index"],
            0,
        )
        self.window._advance_walk()
        self.window._advance_walk()
        self.assertEqual(
            self.window.diagnostic_state()["walk_frame_index"],
            1,
        )

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
