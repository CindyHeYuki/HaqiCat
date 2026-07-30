"""Transparent, draggable desktop-pet window."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import QWidget


class PetWindow(QWidget):
    """A minimal transparent and always-on-top desktop-pet window."""

    WINDOW_SIZE = QSize(240, 220)

    def __init__(self) -> None:
        super().__init__()
        self._drag_offset: QPoint | None = None

        self.setObjectName("haqicatPetWindow")
        self.setWindowTitle("HaqiCat")
        self.setFixedSize(self.WINDOW_SIZE)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self._move_to_initial_position()

    def _move_to_initial_position(self) -> None:
        """Place the pet near the bottom-right of the primary work area."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        work_area = screen.availableGeometry()
        margin = 28
        self.move(
            work_area.right() - self.width() - margin + 1,
            work_area.bottom() - self.height() - margin + 1,
        )

    @staticmethod
    def clamp_to_bounds(position: QPoint, bounds: QRect, size: QSize) -> QPoint:
        """Clamp a top-left window position to a screen work area."""
        maximum_x = max(bounds.left(), bounds.right() - size.width() + 1)
        maximum_y = max(bounds.top(), bounds.bottom() - size.height() + 1)
        return QPoint(
            min(max(position.x(), bounds.left()), maximum_x),
            min(max(position.y(), bounds.top()), maximum_y),
        )

    def _clamp_position(self, position: QPoint, cursor_position: QPoint) -> QPoint:
        """Clamp a requested move to the screen currently under the cursor."""
        screen = QGuiApplication.screenAt(cursor_position)
        if screen is None:
            screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return position
        return self.clamp_to_bounds(
            position,
            screen.availableGeometry(),
            self.size(),
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Start dragging with the left mouse button."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Move the pet while keeping it inside the active screen."""
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            cursor_position = event.globalPosition().toPoint()
            requested_position = cursor_position - self._drag_offset
            self.move(
                self._clamp_position(requested_position, cursor_position)
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Finish a drag operation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def diagnostic_state(self) -> dict[str, object]:
        """Return observable window properties for native smoke tests."""
        flags = self.windowFlags()
        return {
            "visible": self.isVisible(),
            "frameless": bool(flags & Qt.WindowType.FramelessWindowHint),
            "always_on_top": bool(
                flags & Qt.WindowType.WindowStaysOnTopHint
            ),
            "tool_window": bool(flags & Qt.WindowType.Tool),
            "translucent_background": self.testAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground
            ),
            "position": [self.x(), self.y()],
            "size": [self.width(), self.height()],
        }

    def paintEvent(self, event: object) -> None:
        """Draw a lightweight placeholder cat until character assets arrive."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(28, 20, 42, 70))
        painter.drawEllipse(35, 178, 172, 24)

        body_path = QPainterPath()
        body_path.addRoundedRect(55, 92, 132, 96, 46, 46)
        painter.setBrush(QColor("#8F78B8"))
        painter.drawPath(body_path)

        left_ear = QPolygonF(
            [QPoint(62, 82), QPoint(78, 24), QPoint(112, 70)]
        )
        right_ear = QPolygonF(
            [QPoint(130, 69), QPoint(170, 25), QPoint(181, 86)]
        )
        painter.setBrush(QColor("#725C9B"))
        painter.drawPolygon(left_ear)
        painter.drawPolygon(right_ear)

        painter.setBrush(QColor("#B6A0D6"))
        painter.drawEllipse(54, 54, 134, 118)

        painter.setBrush(QColor("#E8A6B5"))
        painter.drawPolygon(
            QPolygonF([QPoint(76, 67), QPoint(81, 43), QPoint(96, 67)])
        )
        painter.drawPolygon(
            QPolygonF([QPoint(148, 67), QPoint(166, 44), QPoint(168, 72)])
        )

        eye_pen = QPen(QColor("#30253E"), 7)
        eye_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(eye_pen)
        painter.drawLine(83, 103, 103, 100)
        painter.drawLine(141, 100, 160, 104)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#D97891"))
        painter.drawEllipse(117, 115, 12, 9)

        mouth_pen = QPen(QColor("#3B2A49"), 4)
        mouth_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(mouth_pen)
        painter.drawArc(101, 119, 22, 20, 215 * 16, 105 * 16)
        painter.drawArc(124, 119, 22, 20, 220 * 16, 105 * 16)

        whisker_pen = QPen(QColor("#665476"), 3)
        whisker_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(whisker_pen)
        painter.drawLine(88, 128, 56, 122)
        painter.drawLine(88, 137, 53, 141)
        painter.drawLine(157, 128, 190, 121)
        painter.drawLine(157, 137, 193, 142)

