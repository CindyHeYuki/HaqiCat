"""Polished motion and pointer interactions for the desktop pet."""

from __future__ import annotations

import math

from PySide6.QtCore import QPoint, QRect, QTimer, Qt
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtWidgets import QApplication

from haqicat.sprite_window import SpritePetWindow


class InteractivePetWindow(SpritePetWindow):
    """Add visible low-frame-rate motion and click reactions."""

    ACTIVE_FRAME_INTERVAL_MS = 80
    SLEEP_FRAME_INTERVAL_MS = 200
    DRAG_THRESHOLD_PX = 6
    DRAG_LIFT_Y_PX = 18

    def __init__(self) -> None:
        super().__init__()
        self._idle_timer.stop()

        self._motion_frame = 0
        self._drag_pose_active = False
        self._press_position: QPoint | None = None
        self._dragged_since_press = False
        self._suppress_next_release = False

        self._motion_timer = QTimer(self)
        self._motion_timer.setInterval(self.ACTIVE_FRAME_INTERVAL_MS)
        self._motion_timer.timeout.connect(self._advance_motion)
        self._motion_timer.start()

        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(QApplication.doubleClickInterval() + 50)
        self._click_timer.timeout.connect(self._handle_single_click)

        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip("拖动我，单击哈气，双击休息")

    def set_state(self, state: str) -> None:
        """Keep motion timing appropriate for the selected state."""
        super().set_state(state)
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
        if self.state == "sleep":
            self.set_state("idle")
            self._schedule_behavior()
        else:
            self.set_state("sleep")

    def _advance_motion(self) -> None:
        self._motion_frame = (self._motion_frame + 1) % 10_000
        self.update()

    def _begin_drag_pose(self) -> None:
        """Switch to the lifted pose and anchor it beneath the cursor."""
        if self._drag_pose_active:
            return
        self._drag_pose_active = True
        self._click_timer.stop()
        self._drag_offset = QPoint(self.width() // 2, self.DRAG_LIFT_Y_PX)
        self.update()

    def _end_drag_pose(self) -> None:
        """Restore normal rendering after the pointer releases the pet."""
        self._drag_pose_active = False
        self.update()

    def _start_hiss(self) -> None:
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
            }
        )
        return diagnostics

    def paintEvent(self, event: object) -> None:
        """Render smooth breathing, swaying, and hissing shake motion."""
        visual_state = "drag" if self._drag_pose_active else self.state
        sprite = self._sprites.get(visual_state)
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
