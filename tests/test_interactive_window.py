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

    def test_crawl_moves_then_stops_to_observe(self) -> None:
        screen = self.window.screen()
        self.assertIsNotNone(screen)
        bounds = screen.availableGeometry()
        self.window.move(bounds.left() + 50, bounds.top() + 50)
        start_x = self.window.x()

        self.window._start_crawl(direction=1, steps=1)
        self.assertEqual(self.window.state, "crawl_right")
        self.window._advance_crawl()

        self.assertEqual(
            self.window.x(),
            start_x + self.window.CRAWL_DISPLACEMENT_PATTERN_PX[0],
        )
        self.assertEqual(self.window.state, "observe_right")
        self.assertTrue(self.window.diagnostic_state()["observing_active"])
        self.assertTrue(self.window._observe_timer.isActive())
        self.window._finish_observing()
        self.assertFalse(self.window.diagnostic_state()["observing_active"])
        self.assertTrue(self.window.diagnostic_state()["rising_active"])
        self.assertEqual(self.window.state, "rise_right")
        self.window._finish_rising()
        self.assertFalse(self.window.diagnostic_state()["rising_active"])
        self.assertEqual(self.window.state, "idle")

    def test_crawl_turns_around_at_screen_edge(self) -> None:
        screen = self.window.screen()
        self.assertIsNotNone(screen)
        bounds = screen.availableGeometry()
        rightmost_x = bounds.right() - self.window.width() + 1
        self.window.move(rightmost_x, bounds.top())

        self.window._start_crawl(direction=1, steps=5)
        self.window._advance_crawl()

        self.assertEqual(self.window.x(), rightmost_x)
        self.assertEqual(self.window._crawl_direction, -1)
        self.assertEqual(self.window.state, "crawl_left")
        self.assertEqual(self.window._crawl_steps_remaining, 5)

    def test_crawl_animation_uses_four_loaded_phases(self) -> None:
        diagnostics = self.window.diagnostic_state()
        self.assertTrue(diagnostics["crawl_animation_loaded"])
        self.assertEqual(diagnostics["crawl_animation_frames"], 4)

        self.window._start_crawl(direction=1, steps=5)
        self.assertEqual(
            self.window.diagnostic_state()["crawl_frame_index"],
            0,
        )
        self.window._advance_crawl()
        self.window._advance_crawl()
        self.window._advance_crawl()
        self.assertEqual(
            self.window.diagnostic_state()["crawl_frame_index"],
            1,
        )

    def test_crawl_displacement_pauses_on_planted_paws(self) -> None:
        screen = self.window.screen()
        self.assertIsNotNone(screen)
        bounds = screen.availableGeometry()
        self.window.move(bounds.center())
        previous_x = self.window.x()
        observed_steps = []

        self.window._start_crawl(direction=1, steps=6)
        for _ in range(6):
            self.window._advance_crawl()
            observed_steps.append(self.window.x() - previous_x)
            previous_x = self.window.x()

        self.assertEqual(
            observed_steps,
            list(self.window.CRAWL_DISPLACEMENT_PATTERN_PX[:6]),
        )
        self.assertIn(0, observed_steps)
        self.assertGreater(max(observed_steps), min(observed_steps))

    def test_observation_settles_before_holding_low_pose(self) -> None:
        diagnostics = self.window.diagnostic_state()
        self.assertTrue(diagnostics["observe_animation_loaded"])
        self.assertEqual(diagnostics["observe_animation_frames"], 2)

        self.window._start_crawl(direction=-1, steps=1)
        self.window._advance_crawl()
        self.assertEqual(self.window.state, "observe_left")
        self.assertEqual(
            self.window.diagnostic_state()["observe_frame_index"],
            0,
        )

        for _ in range(self.window.OBSERVE_SETTLE_TICKS):
            self.window._advance_motion()
        self.assertEqual(
            self.window.diagnostic_state()["observe_frame_index"],
            1,
        )

    def test_observation_rises_through_two_frames_before_idle(self) -> None:
        self.window._start_crawl(direction=-1, steps=1)
        self.window._advance_crawl()
        self.window._finish_observing()

        diagnostics = self.window.diagnostic_state()
        self.assertEqual(self.window.state, "rise_left")
        self.assertTrue(diagnostics["rising_active"])
        self.assertTrue(diagnostics["rise_animation_loaded"])
        self.assertEqual(diagnostics["rise_animation_frames"], 2)
        self.assertEqual(diagnostics["rise_frame_index"], 0)

        for _ in range(self.window.RISE_FRAME_HOLD_TICKS):
            self.window._advance_motion()
        self.assertEqual(
            self.window.diagnostic_state()["rise_frame_index"],
            1,
        )

        self.window._finish_rising()
        self.assertEqual(self.window.state, "idle")
        self.assertFalse(self.window.diagnostic_state()["rising_active"])

    def test_sleep_interrupts_low_observation(self) -> None:
        self.window._start_crawl(direction=1, steps=1)
        self.window._advance_crawl()
        self.assertTrue(self.window.diagnostic_state()["observing_active"])

        self.window.toggle_sleep()

        self.assertEqual(self.window.state, "sleep")
        self.assertFalse(self.window.diagnostic_state()["observing_active"])
        self.assertFalse(self.window._observe_timer.isActive())

    def test_idle_blink_runs_half_closed_half_sequence(self) -> None:
        diagnostics = self.window.diagnostic_state()
        self.assertTrue(diagnostics["blink_animation_loaded"])
        self.assertEqual(diagnostics["blink_animation_frames"], 3)

        self.window._start_blink()
        self.assertTrue(self.window.diagnostic_state()["blink_active"])
        self.assertEqual(self.window.diagnostic_state()["blink_frame_index"], 0)

        for expected_index in (1, 2):
            for _ in range(self.window.BLINK_FRAME_HOLD_TICKS):
                self.window._advance_motion()
            self.assertEqual(
                self.window.diagnostic_state()["blink_frame_index"],
                expected_index,
            )

        for _ in range(self.window.BLINK_FRAME_HOLD_TICKS):
            self.window._advance_motion()
        self.assertFalse(self.window.diagnostic_state()["blink_active"])
        self.assertTrue(self.window._blink_timer.isActive())

    def test_hiss_animation_uses_three_loaded_phases(self) -> None:
        diagnostics = self.window.diagnostic_state()
        self.assertTrue(diagnostics["hiss_animation_loaded"])
        self.assertEqual(diagnostics["hiss_animation_frames"], 3)

        self.window._start_hiss()
        self.assertEqual(self.window.state, "hiss")
        self.assertEqual(self.window.diagnostic_state()["hiss_frame_index"], 0)

        for expected_index in (1, 2):
            for _ in range(self.window.HISS_FRAME_HOLD_TICKS):
                self.window._advance_motion()
            self.assertEqual(
                self.window.diagnostic_state()["hiss_frame_index"],
                expected_index,
            )

        self.window._finish_hiss()
        self.assertEqual(self.window.state, "idle")
        self.assertEqual(self.window.diagnostic_state()["hiss_frame_index"], 0)

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
