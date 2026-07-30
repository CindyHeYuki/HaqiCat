"""Polished motion and pointer interactions for the desktop pet."""

from __future__ import annotations

import math
import random

from PySide6.QtCore import QElapsedTimer, QPoint, QRect, QTimer, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

from haqicat.sprite_window import SpritePetWindow


class InteractivePetWindow(SpritePetWindow):
    """Add visible low-frame-rate motion and click reactions."""

    ACTIVE_FRAME_INTERVAL_MS = 80
    SLEEP_FRAME_INTERVAL_MS = 200
    DRAG_THRESHOLD_PX = 6
    DRAG_LIFT_Y_PX = 18
    LANDING_DURATION_MS = 760
    BEHAVIOR_DELAY_RANGE_MS = (4_000, 8_000)
    CRAWL_STEP_PX = 2
    CRAWL_STEP_RANGE = (18, 40)
    OBSERVE_DURATION_MS = 1_400
    CRAWL_FRAME_HOLD_TICKS = 3

    def __init__(self) -> None:
        super().__init__()
        self._idle_timer.stop()

        self._motion_frame = 0
        self._drag_pose_active = False
        self._landing_active = False
        self._crawl_direction = 0
        self._crawl_steps_remaining = 0
        self._observing_active = False
        self._observe_direction = 1
        self._crawl_animation_tick = 0
        self._press_position: QPoint | None = None
        self._dragged_since_press = False
        self._suppress_next_release = False

        self._motion_timer = QTimer(self)
        self._motion_timer.setInterval(self.ACTIVE_FRAME_INTERVAL_MS)
        self._motion_timer.timeout.connect(self._advance_motion)
        self._motion_timer.start()

        self._landing_clock = QElapsedTimer()
        self._landing_timer = QTimer(self)
        self._landing_timer.setSingleShot(True)
        self._landing_timer.timeout.connect(self._finish_landing_animation)

        self._observe_timer = QTimer(self)
        self._observe_timer.setSingleShot(True)
        self._observe_timer.timeout.connect(self._finish_observing)

        self._behavior_timer.timeout.disconnect()
        self._behavior_timer.timeout.connect(self._choose_autonomous_behavior)

        self._crawl_frames = self._load_crawl_frames()

        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(QApplication.doubleClickInterval() + 50)
        self._click_timer.timeout.connect(self._handle_single_click)

        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip("拖动我，单击哈气，双击休息")

    def _load_crawl_frames(self) -> dict[str, tuple[QPixmap, ...]]:
        """Load four low-profile creeping phases in each direction."""
        sprite_root = self.sprite_paths["crawl_left"].parent
        return {
            direction: tuple(
                QPixmap(
                    str(sprite_root / f"haqi_cat_crawl_{side}_{index:02d}.png")
                )
                for index in range(1, 5)
            )
            for direction, side in (
                ("crawl_left", "left"),
                ("crawl_right", "right"),
            )
        }

    def set_state(self, state: str) -> None:
        """Keep motion timing appropriate for the selected state."""
        super().set_state(state)
        if state == "sleep" and hasattr(self, "_observe_timer"):
            self._crawl_steps_remaining = 0
            self._crawl_direction = 0
            self._cancel_observing()
        self._idle_timer.stop()
        if hasattr(self, "_motion_timer"):
            interval = (
                self.SLEEP_FRAME_INTERVAL_MS
                if state == "sleep"
                else self.ACTIVE_FRAME_INTERVAL_MS
            )
            self._motion_timer.start(interval)

    def toggle_sleep(self) -> None:
        """Toggle between the sleeping and idle states."""
        self._cancel_landing_animation()
        self._cancel_autonomous_motion()
        if self.state == "sleep":
            self.set_state("idle")
            self._schedule_behavior()
        else:
            self.set_state("sleep")

    def _advance_motion(self) -> None:
        self._motion_frame = (self._motion_frame + 1) % 10_000
        self._advance_crawl()
        self.update()

    def _choose_autonomous_behavior(self) -> None:
        """Choose a short stealthy crawl most of the time, otherwise hiss."""
        if (
            self.state != "idle"
            or self._drag_pose_active
            or self._landing_active
            or self._observing_active
        ):
            return
        if random.random() < 0.72:
            self._start_crawl()
        else:
            self._start_hiss()

    def _start_crawl(
        self,
        direction: int | None = None,
        steps: int | None = None,
    ) -> None:
        """Begin a bounded, low-profile crawl in the chosen direction."""
        if self.state == "sleep" or self._drag_pose_active:
            return
        self._cancel_landing_animation()
        self._cancel_observing()
        self._behavior_timer.stop()
        self._reaction_timer.stop()

        if direction is None:
            screen = self.screen()
            if screen is not None:
                bounds = screen.availableGeometry()
                left_space = self.x() - bounds.left()
                right_space = bounds.right() - self.frameGeometry().right()
                if left_space < 40:
                    direction = 1
                elif right_space < 40:
                    direction = -1
            if direction is None:
                direction = random.choice((-1, 1))
        if direction not in (-1, 1):
            raise ValueError("Crawl direction must be -1 or 1.")

        self._crawl_direction = direction
        self._crawl_steps_remaining = max(
            1,
            steps if steps is not None else random.randint(*self.CRAWL_STEP_RANGE),
        )
        self._crawl_animation_tick = 0
        self.set_state("crawl_left" if direction < 0 else "crawl_right")

    def _advance_crawl(self) -> None:
        if (
            self.state not in ("crawl_left", "crawl_right")
            or self._crawl_steps_remaining <= 0
            or self._drag_pose_active
            or self._landing_active
        ):
            return
        screen = self.screen()
        if screen is None:
            self._start_observing()
            return

        requested = QPoint(
            self.x() + self._crawl_direction * self.CRAWL_STEP_PX,
            self.y(),
        )
        clamped = self.clamp_to_bounds(
            requested,
            screen.availableGeometry(),
            self.size(),
        )
        if clamped.x() != requested.x():
            self._crawl_direction *= -1
            self.set_state(
                "crawl_left" if self._crawl_direction < 0 else "crawl_right"
            )
            self._crawl_animation_tick = 0
            return

        self.move(clamped)
        frame_count = len(self._crawl_frames[self.state])
        self._crawl_animation_tick = (
            self._crawl_animation_tick + 1
        ) % (frame_count * self.CRAWL_FRAME_HOLD_TICKS)
        self._crawl_steps_remaining -= 1
        if self._crawl_steps_remaining <= 0:
            self._start_observing()

    def _start_observing(self) -> None:
        """Pause after crawling and look around before idling again."""
        self._observe_direction = self._crawl_direction or self._observe_direction
        self._crawl_direction = 0
        self._crawl_steps_remaining = 0
        self._crawl_animation_tick = 0
        self.set_state("idle")
        self._observing_active = True
        self._observe_timer.start(self.OBSERVE_DURATION_MS)
        self.update()

    def _cancel_observing(self) -> None:
        if not self._observing_active:
            return
        self._observe_timer.stop()
        self._observing_active = False
        self.update()

    def _finish_observing(self) -> None:
        if not self._observing_active:
            return
        self._observe_timer.stop()
        self._observing_active = False
        self.update()
        if self.state == "idle":
            self._schedule_behavior()

    def _cancel_autonomous_motion(self) -> None:
        self._crawl_direction = 0
        self._crawl_steps_remaining = 0
        self._crawl_animation_tick = 0
        if self.state in ("crawl_left", "crawl_right"):
            self.set_state("idle")
        self._cancel_observing()

    def _begin_drag_pose(self) -> None:
        """Switch to the lifted pose and anchor it beneath the cursor."""
        if self._drag_pose_active:
            return
        self._drag_pose_active = True
        self._cancel_landing_animation()
        self._cancel_autonomous_motion()
        self._click_timer.stop()
        self._drag_offset = QPoint(self.width() // 2, self.DRAG_LIFT_Y_PX)
        self.update()

    def _end_drag_pose(self) -> None:
        """Restore normal rendering after the pointer releases the pet."""
        self._drag_pose_active = False
        self._start_landing_animation()

    def _start_landing_animation(self) -> None:
        """Play a short drop, rebound, and head-shake sequence."""
        self._cancel_autonomous_motion()
        self._behavior_timer.stop()
        self._reaction_timer.stop()
        self.set_state("idle")
        self._landing_active = True
        self._landing_clock.restart()
        self._landing_timer.start(self.LANDING_DURATION_MS)
        self.update()

    def _cancel_landing_animation(self) -> None:
        if not self._landing_active:
            return
        self._landing_timer.stop()
        self._landing_active = False
        self.update()

    def _finish_landing_animation(self) -> None:
        if not self._landing_active:
            return
        self._landing_timer.stop()
        self._landing_active = False
        self.update()
        if self.state == "idle":
            self._schedule_behavior()

    def _start_hiss(self) -> None:
        self._cancel_landing_animation()
        self._cancel_autonomous_motion()
        self._behavior_timer.stop()
        super()._start_hiss()

    def _handle_single_click(self) -> None:
        if self.state == "sleep":
            self.set_state("idle")
            self._schedule_behavior()
            return
        self._start_hiss()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._cancel_autonomous_motion()
            self._press_position = event.globalPosition().toPoint()
            self._dragged_since_press = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press_position is not None:
            distance = (
                event.globalPosition().toPoint() - self._press_position
            ).manhattanLength()
            if distance >= self.DRAG_THRESHOLD_PX:
                self._dragged_since_press = True
                self._begin_drag_pose()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        is_click = (
            event.button() == Qt.MouseButton.LeftButton
            and not self._dragged_since_press
            and not self._suppress_next_release
        )
        was_dragging = self._drag_pose_active
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if was_dragging:
                self._end_drag_pose()
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self._press_position = None
            if self._suppress_next_release:
                self._suppress_next_release = False
            elif is_click:
                self._click_timer.start()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_timer.stop()
            self._suppress_next_release = True
            self.toggle_sleep()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def diagnostic_state(self) -> dict[str, object]:
        diagnostics = super().diagnostic_state()
        diagnostics.update(
            {
                "motion_interval_ms": self._motion_timer.interval(),
                "single_click_reaction": "hiss",
                "double_click_reaction": "toggle_sleep",
                "drag_pose_active": self._drag_pose_active,
                "landing_active": self._landing_active,
                "observing_active": self._observing_active,
                "crawl_direction": self._crawl_direction,
                "crawl_steps_remaining": self._crawl_steps_remaining,
                "autonomous_mode": (
                    "drag"
                    if self._drag_pose_active
                    else "landing"
                    if self._landing_active
                    else "observe"
                    if self._observing_active
                    else "crawl"
                    if self.state in ("crawl_left", "crawl_right")
                    else self.state
                ),
                "crawl_animation_frames": min(
                    len(frames) for frames in self._crawl_frames.values()
                ),
                "crawl_animation_loaded": all(
                    not frame.isNull()
                    for frames in self._crawl_frames.values()
                    for frame in frames
                ),
                "crawl_frame_index": (
                    self._crawl_animation_tick // self.CRAWL_FRAME_HOLD_TICKS
                ),
            }
        )
        return diagnostics

    def paintEvent(self, event: object) -> None:
        """Render smooth breathing, swaying, and hissing shake motion."""
        if self._drag_pose_active:
            visual_state = "drag"
        elif self._landing_active:
            visual_state = "landing"
        elif self._observing_active:
            visual_state = "observe"
        else:
            visual_state = self.state
        sprite_state = (
            "idle" if visual_state in ("landing", "observe") else visual_state
        )
        sprite = self._sprites.get(sprite_state)
        if visual_state in self._crawl_frames:
            frames = self._crawl_frames[visual_state]
            frame_index = (
                self._crawl_animation_tick // self.CRAWL_FRAME_HOLD_TICKS
            ) % len(frames)
            candidate = frames[frame_index]
            if not candidate.isNull():
                sprite = candidate
        if sprite is None or sprite.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        phase = self._motion_frame * self._motion_timer.interval() / 1000.0
        x_offset = 0.0
        y_offset = 0.0
        x_scale = 1.0
        y_scale = 1.0
        rotation = 0.0

        if visual_state == "drag":
            y_offset = 1.5 * math.sin(phase * 4.0)
            rotation = 2.5 * math.sin(phase * 3.0)
        elif visual_state == "landing":
            progress = min(
                1.0,
                self._landing_clock.elapsed() / self.LANDING_DURATION_MS,
            )
            if progress < 0.22:
                local = progress / 0.22
                y_offset = -8.0 + 18.0 * local
                y_scale = 1.0 + 0.04 * local
            elif progress < 0.48:
                local = (progress - 0.22) / 0.26
                y_offset = 10.0 * (1.0 - local) - 4.0 * math.sin(math.pi * local)
                x_scale = 1.0 + 0.08 * (1.0 - local)
                y_scale = 1.0 - 0.06 * (1.0 - local)
            else:
                local = (progress - 0.48) / 0.52
                damping = 1.0 - local
                rotation = 4.0 * damping * math.sin(local * math.pi * 5.0)
        elif visual_state == "observe":
            x_offset = 2.0 * self._observe_direction
            y_offset = -1.0
            rotation = (
                2.0 * self._observe_direction
                + 0.8 * math.sin(phase * 2.2)
            )
        elif visual_state == "idle":
            breath = (math.sin(phase * 2.4) + 1.0) / 2.0
            y_offset = -2.0 * breath
            x_scale = 1.0 - 0.008 * breath
            y_scale = 1.0 + 0.018 * breath
            rotation = 1.2 * math.sin(phase * 1.2)
        elif visual_state == "hiss":
            x_offset = 3.0 * math.sin(phase * 28.0)
            y_offset = -2.0
            x_scale = 1.02
            y_scale = 1.02
        elif visual_state == "sleep":
            breath = (math.sin(phase * 1.5) + 1.0) / 2.0
            y_scale = 1.0 + 0.008 * breath
            y_offset = -1.0 * breath

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        painter.translate(center_x + x_offset, center_y + y_offset)
        painter.rotate(rotation)
        painter.scale(x_scale, y_scale)
        painter.translate(-center_x, -center_y)
        painter.drawPixmap(QRect(0, 0, self.width(), self.height()), sprite)
