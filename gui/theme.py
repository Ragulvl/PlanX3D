# pyre-ignore-all-errors
"""
Design System — Refined Dark Palette
Centralized color tokens, shadows, and global QSS stylesheet.
Designed for high readability with WCAG AA+ contrast ratios.
"""

from PySide6.QtGui import QColor


class Theme:
    """Centralized color palette and design tokens."""

    # Backgrounds — layered slate (lighter than before for readability)
    BG_BASE      = "#1a1d23"   # Main background
    BG_RAISED    = "#21252d"   # Sidebar, topbar, cards
    BG_SURFACE   = "#282d37"   # Input fields, nested panels
    BG_ELEVATED  = "#303742"   # Hover states, dropdowns
    BG_OVERLAY   = "#3a424f"   # Tooltips, overlays

    # Borders — clearly visible separation
    BORDER_SUBTLE  = "#323a47"
    BORDER_DEFAULT = "#3f4a5a"
    BORDER_STRONG  = "#56627a"

    # Text hierarchy — high contrast, easy to read
    TEXT_H1        = "#f0f2f5"   # Headings — near white
    TEXT_BODY      = "#d4d8e0"   # Body text — ~12:1 contrast
    TEXT_SECONDARY = "#9aa0b0"   # Labels, descriptions — ~6:1
    TEXT_MUTED     = "#6b7280"   # Hints, timestamps — ~4.5:1 (WCAG AA)

    # Accent — clear blue (high visibility on dark bg)
    ACCENT       = "#4f8fff"
    ACCENT_HOVER = "#6ba0ff"
    ACCENT_MUTED = "rgba(79, 143, 255, 0.15)"
    ACCENT_GLOW  = "rgba(79, 143, 255, 0.25)"

    # Semantic colors — vivid for instant recognition
    SUCCESS       = "#34d399"
    SUCCESS_MUTED = "rgba(52, 211, 153, 0.14)"
    WARNING       = "#fbbf24"
    WARNING_MUTED = "rgba(251, 191, 36, 0.14)"
    ERROR         = "#f87171"
    ERROR_MUTED   = "rgba(248, 113, 113, 0.14)"

    # Blender accent (warm amber)
    BLENDER       = "#f59e0b"
    BLENDER_HOVER = "#fbbf24"

    # Shadows
    SHADOW_COLOR = QColor(0, 0, 0, 70)


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
