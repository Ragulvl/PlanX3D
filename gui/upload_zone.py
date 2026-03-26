# pyre-ignore-all-errors
"""
UploadZone — Custom-painted drag-and-drop file upload widget.
"""

import os
from typing import Optional

from PySide6.QtWidgets import QFrame, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, QFont, QColor,
    QPainter, QPen, QBrush, QPainterPath,
)

from .theme import Theme


class UploadZone(QFrame):
    """Drag-and-drop zone for blueprint image upload with QPainter-drawn icons."""

    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._hover = False
        self._drag_active = False
        self._selected_path: Optional[str] = None
        self._selected_name = ""
        self._selected_size = ""
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)

    # ── Rendering ────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)

        # Background
        bg = QColor(Theme.BG_SURFACE)
        if self._drag_active:
            bg = QColor(108, 92, 231, 38)
        elif self._hover:
            bg = QColor(Theme.BG_ELEVATED)

        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        p.fillPath(path, QBrush(bg))

        # Border
        if self._drag_active:
            pen = QPen(QColor(Theme.ACCENT), 2, Qt.DashLine)
            pen.setDashPattern([6, 4])
        elif self._selected_path:
            pen = QPen(QColor(Theme.SUCCESS), 1.5, Qt.SolidLine)
        elif self._hover:
            pen = QPen(QColor(Theme.BORDER_STRONG), 1.5, Qt.DashLine)
            pen.setDashPattern([6, 4])
        else:
            pen = QPen(QColor(Theme.BORDER_DEFAULT), 1, Qt.DashLine)
            pen.setDashPattern([8, 5])
        p.setPen(pen)
        p.drawPath(path)

        # Centre content
        cx = self.width() / 2
        cy = self.height() / 2

        if self._selected_path:
            self._paint_selected_state(p, cx, cy)
        else:
            self._paint_upload_state(p, cx, cy)

        p.end()

    def _paint_selected_state(self, p: QPainter, cx: float, cy: float):
        """Draw the 'file selected' visual state."""
        self._draw_check_icon(p, cx, cy - 36, 20)

        p.setPen(QColor(Theme.SUCCESS))
        f = QFont("Segoe UI Variable", 13)
        f.setWeight(QFont.DemiBold)
        p.setFont(f)
        p.drawText(QRectF(0, cy - 8, self.width(), 28), Qt.AlignCenter, "Blueprint Selected")

        p.setPen(QColor(Theme.TEXT_SECONDARY))
        p.setFont(QFont("Segoe UI Variable", 10))
        p.drawText(
            QRectF(0, cy + 20, self.width(), 22), Qt.AlignCenter,
            f"{self._selected_name}  ·  {self._selected_size}",
        )

        p.setPen(QColor(Theme.TEXT_MUTED))
        p.setFont(QFont("Segoe UI Variable", 9))
        p.drawText(
            QRectF(0, cy + 48, self.width(), 20), Qt.AlignCenter,
            "Drop another file to replace",
        )

    def _paint_upload_state(self, p: QPainter, cx: float, cy: float):
        """Draw the default 'upload' visual state."""
        self._draw_upload_icon(p, cx, cy - 38, 22)

        p.setPen(QColor(Theme.TEXT_BODY if not self._drag_active else Theme.ACCENT))
        f = QFont("Segoe UI Variable", 14)
        f.setWeight(QFont.DemiBold)
        p.setFont(f)
        label = "Drop your blueprint here" if self._drag_active else "Drag & drop your blueprint"
        p.drawText(QRectF(0, cy - 4, self.width(), 28), Qt.AlignCenter, label)

        p.setPen(QColor(Theme.TEXT_MUTED))
        p.setFont(QFont("Segoe UI Variable", 10))
        p.drawText(
            QRectF(0, cy + 24, self.width(), 22), Qt.AlignCenter,
            "PNG, JPG or JPEG  ·  or click Browse below",
        )

    # ── Icon Drawing ─────────────────────────────────────────────────

    def _draw_upload_icon(self, p: QPainter, cx: float, cy: float, size: float):
        """Minimal line-art upload arrow icon."""
        p.save()
        pen = QPen(QColor(Theme.ACCENT if self._drag_active else Theme.TEXT_SECONDARY), 2.0)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)

        p.drawLine(QPointF(cx, cy + size * 0.8), QPointF(cx, cy - size * 0.4))
        p.drawLine(QPointF(cx - size * 0.35, cy - size * 0.05), QPointF(cx, cy - size * 0.4))
        p.drawLine(QPointF(cx + size * 0.35, cy - size * 0.05), QPointF(cx, cy - size * 0.4))
        p.drawLine(QPointF(cx - size * 0.6, cy + size * 0.8), QPointF(cx + size * 0.6, cy + size * 0.8))
        p.drawLine(QPointF(cx - size * 0.6, cy + size * 0.8), QPointF(cx - size * 0.6, cy + size * 1.1))
        p.drawLine(QPointF(cx + size * 0.6, cy + size * 0.8), QPointF(cx + size * 0.6, cy + size * 1.1))
        p.drawLine(QPointF(cx - size * 0.75, cy + size * 1.1), QPointF(cx + size * 0.75, cy + size * 1.1))
        p.restore()

    def _draw_check_icon(self, p: QPainter, cx: float, cy: float, size: float):
        """Minimal checkmark circle icon."""
        p.save()
        pen = QPen(QColor(Theme.SUCCESS), 2.0)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), size, size)
        p.drawLine(QPointF(cx - size * 0.4, cy), QPointF(cx - size * 0.05, cy + size * 0.35))
        p.drawLine(QPointF(cx - size * 0.05, cy + size * 0.35), QPointF(cx + size * 0.45, cy - size * 0.3))
        p.restore()

    # ── File Handling ────────────────────────────────────────────────

    def set_file(self, file_path: str):
        """Update the zone to show a selected file."""
        self._selected_path = file_path
        self._selected_name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        if size < 1024:
            self._selected_size = f"{size} B"
        elif size < 1024 * 1024:
            self._selected_size = f"{size / 1024:.1f} KB"
        else:
            self._selected_size = f"{size / (1024 * 1024):.1f} MB"
        self.update()

    # ── Events ───────────────────────────────────────────────────────

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._drag_active = True
            self.update()

    def dragLeaveEvent(self, event):
        self._drag_active = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        self._drag_active = False
        self.update()
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            f = files[0]
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                self.file_dropped.emit(f)
            else:
                QMessageBox.warning(self, "Invalid File", "Please select a PNG or JPG image file.")
        event.acceptProposedAction()
