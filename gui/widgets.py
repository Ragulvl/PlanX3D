# pyre-ignore-all-errors
"""
Reusable styled widgets — button factories and sidebar navigation.
"""

from typing import Optional

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

from .theme import Theme


# ─────────────────────────────────────────────────────────────────────────────
#  Button Factories
# ─────────────────────────────────────────────────────────────────────────────

def make_primary_button(text: str, tooltip: str = "") -> QPushButton:
    """Accent-colored primary action button."""
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setToolTip(tooltip)
    btn.setFixedHeight(44)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.ACCENT}, stop:1 #3a6fd8);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            padding: 0 28px;
            letter-spacing: 0.3px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.ACCENT_HOVER}, stop:1 #5580e0);
        }}
        QPushButton:pressed {{
            background: {Theme.ACCENT};
        }}
        QPushButton:disabled {{
            background: {Theme.BG_SURFACE};
            color: {Theme.TEXT_MUTED};
            border: 1px solid {Theme.BORDER_SUBTLE};
        }}
    """)
    return btn


def make_ghost_button(text: str, color: Optional[str] = None, tooltip: str = "") -> QPushButton:
    """Outlined / ghost button."""
    c = color or Theme.TEXT_BODY
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setToolTip(tooltip)
    btn.setFixedHeight(40)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {c};
            border: 1px solid {Theme.BORDER_DEFAULT};
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            padding: 0 20px;
        }}
        QPushButton:hover {{
            background: {Theme.BG_ELEVATED};
            border-color: {Theme.BORDER_STRONG};
            color: {Theme.TEXT_H1};
        }}
        QPushButton:pressed {{
            background: {Theme.BG_OVERLAY};
        }}
        QPushButton:disabled {{
            color: {Theme.TEXT_MUTED};
            border-color: {Theme.BORDER_SUBTLE};
        }}
    """)
    return btn


def make_blender_button(text: str, tooltip: str = "") -> QPushButton:
    """Warm amber button for Blender actions."""
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setToolTip(tooltip)
    btn.setFixedHeight(44)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.BLENDER}, stop:1 #d97b2c);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            padding: 0 24px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.BLENDER_HOVER}, stop:1 #e89040);
        }}
        QPushButton:pressed {{
            background: {Theme.BLENDER};
        }}
        QPushButton:disabled {{
            background: {Theme.BG_SURFACE};
            color: {Theme.TEXT_MUTED};
            border: 1px solid {Theme.BORDER_SUBTLE};
        }}
    """)
    return btn


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar Navigation
# ─────────────────────────────────────────────────────────────────────────────

class SidebarButton(QPushButton):
    """Thin sidebar nav item with subtle active indicator."""

    def __init__(self, label: str, active: bool = False):
        super().__init__(label)
        self._active = active
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(38)
        self._apply_style()

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()

    def _apply_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.ACCENT_MUTED};
                    color: {Theme.ACCENT_HOVER};
                    border: none;
                    border-left: 2px solid {Theme.ACCENT};
                    border-radius: 0px;
                    font-size: 12px;
                    font-weight: 600;
                    text-align: left;
                    padding-left: 14px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Theme.TEXT_SECONDARY};
                    border: none;
                    border-left: 2px solid transparent;
                    border-radius: 0px;
                    font-size: 12px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 14px;
                }}
                QPushButton:hover {{
                    color: {Theme.TEXT_BODY};
                    background: {Theme.BG_SURFACE};
                }}
            """)
