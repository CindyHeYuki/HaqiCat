"""Sprite-driven Haqi Cat desktop-pet window."""

from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtCore import QRect, QSize, QTimer, Qt
from PySide6.QtGui import (
    QContextMenuEvent,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import QMenu

from haqicat.window import PetWindow


class SpritePetWindow(PetWindow):
    """Desktop-pet window using transparent Haqi Cat sprites."""

    SPRITE_SIZE = QSize(256, 256)
    IDLE_INTERVAL_MS = 700
    HISS_DURATION_MS = 900
    BEHAVIOR_DELAY_RANGE_MS = (8_000, 16_000)

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(self.SPRITE_SIZE)
        self._move_to_initial_position()

        self._sprite_paths = self._resolve_sprite_paths()
        self._sprites = {
            state: QPixmap(str(path))
            for state, path in self._sprite_paths.items()
        }
        self._state = "idle"
        self._idle_phase = 0

        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(self.IDLE_INTERVAL_MS)
        self._idle_timer.timeout.connect(self._advance_idle_frame)
        self._idle_timer.start()

        self._behavior_timer = QTimer(self)
        self._behavior_timer.setSingleShot(True)
        self._behavior_timer.timeout.connect(self._start_hiss)

        self._reaction_timer = QTimer(self)
        self._reaction_timer.setSingleShot(True)
        self._reaction_timer.timeout.connect(self._finish_hiss)
        self._schedule_behavior()

    @staticmethod
    def _resolve_sprite_paths() -> dict[str, Path]:
        project_root = Path(__file__).resolve().parents[2]
        sprite_root = project_root / "assets" / "character" / "processed"
        return {
            "idle": sprite_root / "haqi_cat_idle.png",
            "hiss": sprite_root / "haqi_cat_hiss.png",
            "sleep": sprite_root / "haqi_cat_sleep.png",
            "walk_left": sprite_root / "haqi_cat_walk_left.png",
            "walk_right": sprite_root / "haqi_cat_walk_right.png",
        }

    @property
    def state(self) -> str:
        """Return the current visual state."""
        return self._state

    @property
    def sprite_paths(self) -> dict[str, Path]:
        """Return a copy of the state-to-file mapping."""
        return dict(self._sprite_paths)

    def set_state(self, state: str) -> None:
        """Switch to a known sprite state."""
        if state not in self._sprites:
            raise ValueError(f"Unknown pet state: {state}")
        if self._sprites[state].isNull():
            raise RuntimeError(f"Sprite could not be loaded: {self._sprite_paths[state]}")

        self._state = state
        self._idle_phase = 0
        if state == "sleep":
            self._idle_timer.stop()
            self._behavior_timer.stop()
            self._reaction_timer.stop()
        else:
            if not self._idle_timer.isActive():
                self._idle_timer.start()
        self.update()

    def _advance_idle_frame(self) -> None:
        """Advance a very low-frequency breathing cycle."""
        if self._state != "idle":
            return
        self._idle_phase = (self._idle_phase + 1) % 4
        self.update()

    def _schedule_behavior(self) -> None:
        """Schedule an occasional short hiss without a busy loop."""
        if self._state == "sleep":
            return
        delay = random.randint(*self.BEHAVIOR_DELAY_RANGE_MS)
        self._behavior_timer.start(delay)

    def _start_hiss(self) -> None:
        if self._state == "sleep":
            return
        self.set_state("hiss")
        self._reaction_timer.start(self.HISS_DURATION_MS)

    def _finish_hiss(self) -> None:
        if self._state == "hiss":
            self.set_state("idle")
        self._schedule_behavior()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Show state controls and the required exit action."""
        menu = QMenu(self)
        hiss_action = menu.addAction("哈气一下")
        sleep_action = menu.addAction(
            "恢复待机" if self._state == "sleep" else "趴下休息"
        )
        menu.addSeparator()
        exit_action = menu.addAction("退出")

        selected_action = menu.exec(event.globalPos())
        if selected_action == hiss_action:
            self._start_hiss()
        elif selected_action == sleep_action:
            if self._state == "sleep":
                self.set_state("idle")
                self._schedule_behavior()
            else:
                self.set_state("sleep")
        elif selected_action == exit_action:
            self.close()

    def diagnostic_state(self) -> dict[str, object]:
        """Extend the base diagnostics with sprite and timer information."""
        diagnostics = super().diagnostic_state()
        diagnostics.update(
            {
                "pet_state": self._state,
                "idle_interval_ms": self._idle_timer.interval(),
                "sprites_loaded": all(
                    not pixmap.isNull() for pixmap in self._sprites.values()
                ),
            }
        )
        return diagnostics

    def paintEvent(self, event: object) -> None:
        """Draw the active sprite with a subtle idle breathing scale."""
        del event
        sprite = self._sprites.get(self._state)
        if sprite is None or sprite.isNull():
            super().paintEvent(None)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        target = QRect(0, 0, self.width(), self.height())
        if self._state == "idle" and self._idle_phase in (1, 2):
            width = self.width() + 2
            height = self.height() + 2
            target = QRect(
                (self.width() - width) // 2,
                self.height() - height,
                width,
                height,
            )
        painter.drawPixmap(target, sprite)

