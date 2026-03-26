# pyre-ignore-all-errors
"""
Design System — Warm Charcoal Palette
Centralized color tokens, shadows, and global QSS stylesheet.
"""

from PySide6.QtGui import QColor


class Theme:
    """Centralized color palette and design tokens."""

    # Backgrounds — warm charcoal layers
    BG_BASE      = "#17171e"
    BG_RAISED    = "#1e1e28"
    BG_SURFACE   = "#252530"
    BG_ELEVATED  = "#2c2c3a"
    BG_OVERLAY   = "#33334a"

    # Borders — very subtle, warm grays
    BORDER_SUBTLE  = "#2e2e3c"
    BORDER_DEFAULT = "#38384a"
    BORDER_STRONG  = "#48486a"

    # Text hierarchy — soft cream tones
    TEXT_H1        = "#eeeef0"
    TEXT_BODY      = "#c8c8d0"
    TEXT_SECONDARY = "#8888a0"
    TEXT_MUTED     = "#5c5c74"

    # Accent — warm indigo
    ACCENT       = "#6c5ce7"
    ACCENT_HOVER = "#7e6ff0"
    ACCENT_MUTED = "rgba(108, 92, 231, 0.15)"
    ACCENT_GLOW  = "rgba(108, 92, 231, 0.25)"

    # Semantic colors
    SUCCESS       = "#48bb78"
    SUCCESS_MUTED = "rgba(72, 187, 120, 0.12)"
    WARNING       = "#ed8936"
    WARNING_MUTED = "rgba(237, 137, 54, 0.12)"
    ERROR         = "#fc5c65"
    ERROR_MUTED   = "rgba(252, 92, 101, 0.12)"

    # Blender accent (warm amber)
    BLENDER       = "#e8873a"
    BLENDER_HOVER = "#f09848"

    # Shadows
    SHADOW_COLOR = QColor(0, 0, 0, 60)


# Global QSS — minimal, only what can't be done inline
STYLESHEET = f"""
QMainWindow {{
    background: {Theme.BG_BASE};
}}
* {{
    font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
    outline: none;
}}
QToolTip {{
    background: {Theme.BG_ELEVATED};
    color: {Theme.TEXT_BODY};
    border: 1px solid {Theme.BORDER_DEFAULT};
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 11px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {Theme.BORDER_DEFAULT};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Theme.BORDER_STRONG};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {Theme.BORDER_DEFAULT};
    border-radius: 3px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {Theme.BORDER_STRONG};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
    width: 0;
}}
QMessageBox {{
    background: {Theme.BG_RAISED};
}}
QMessageBox QLabel {{
    color: {Theme.TEXT_BODY};
    font-size: 13px;
}}
QMessageBox QPushButton {{
    background: {Theme.BG_SURFACE};
    color: {Theme.TEXT_BODY};
    border: 1px solid {Theme.BORDER_DEFAULT};
    border-radius: 6px;
    padding: 6px 18px;
    font-size: 12px;
    min-width: 72px;
}}
QMessageBox QPushButton:hover {{
    background: {Theme.BG_ELEVATED};
    border-color: {Theme.ACCENT};
}}
"""
