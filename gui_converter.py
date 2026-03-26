# pyre-ignore-all-errors
"""
PlanX3D — Main Window
Desktop GUI for converting 2D floorplan blueprints into 3D Blender models.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QFileDialog, QMessageBox, QProgressBar,
    QFrame, QScrollArea, QGraphicsDropShadowEffect, QSizePolicy,
    QStackedWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPalette

# Import modular GUI components
from gui.theme import Theme, STYLESHEET
from gui.widgets import (
    make_primary_button, make_ghost_button, make_blender_button, SidebarButton,
)
from gui.upload_zone import UploadZone
from gui.worker import ConversionWorker, find_blender


class MainWindow(QMainWindow):
    """Primary application window with sidebar navigation and stacked pages."""

    def __init__(self):
        super().__init__()
        self.selected_file: Optional[str] = None
        self.blender_path: Optional[str] = None
        self.worker: Optional[ConversionWorker] = None
        self._last_blend: Optional[str] = None
        self._build_ui()
        self._detect_blender()
        self._load_blender_path()

    # ════════════════════════════════════════════════════════════════
    #  UI Construction
    # ════════════════════════════════════════════════════════════════

    def _build_ui(self):
        self.setWindowTitle("PlanX3D")
        self.setMinimumSize(1040, 680)
        self.resize(1120, 740)

        central = QWidget()
        central.setStyleSheet(f"background: {Theme.BG_BASE}; color: {Theme.TEXT_BODY};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._build_sidebar())

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(self._build_topbar())

        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("background: transparent;")
        self.page_stack.addWidget(self._build_convert_page())
        self.page_stack.addWidget(self._build_history_page())
        self.page_stack.addWidget(self._build_settings_page())
        content_layout.addWidget(self.page_stack, 1)

        root.addWidget(content, 1)

        self._page_meta = [
            ("Convert Blueprint", "Upload a 2D floorplan and generate a 3D model"),
            ("Conversion History", "Previously generated 3D models"),
            ("Settings", "Application configuration"),
        ]

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_RAISED};
                border-right: 1px solid {Theme.BORDER_SUBTLE};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Brand
        brand = QFrame()
        brand.setFixedHeight(64)
        brand.setStyleSheet("background: transparent; border: none;")
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(16, 0, 16, 0)
        app_name = QLabel("PlanX3D")
        app_name.setStyleSheet(f"""
            font-size: 17px; font-weight: 700; color: {Theme.TEXT_H1};
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        brand_layout.addWidget(app_name)
        brand_layout.addStretch()
        layout.addWidget(brand)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {Theme.BORDER_SUBTLE}; border: none;")
        layout.addWidget(div)
        layout.addSpacing(8)

        # Nav label
        nav_label = QLabel("   WORKSPACE")
        nav_label.setStyleSheet(f"""
            font-size: 10px; font-weight: 600; color: {Theme.TEXT_MUTED};
            letter-spacing: 1.2px; padding: 8px 0 4px 0;
            background: transparent; border: none;
        """)
        layout.addWidget(nav_label)

        # Nav buttons
        self.nav_buttons = []
        for i, (label, active) in enumerate([("Convert", True), ("History", False), ("Settings", False)]):
            btn = SidebarButton(label, active=active)
            btn.clicked.connect(lambda checked, idx=i: self._switch_page(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # Blender status
        self.blender_label = QLabel()
        self.blender_label.setWordWrap(True)
        self.blender_label.setStyleSheet(f"""
            font-size: 10px; color: {Theme.TEXT_MUTED};
            padding: 12px 16px; background: transparent;
            border-top: 1px solid {Theme.BORDER_SUBTLE};
        """)
        layout.addWidget(self.blender_label)

        return sidebar

    def _build_topbar(self) -> QFrame:
        topbar = QFrame()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_RAISED};
                border-bottom: 1px solid {Theme.BORDER_SUBTLE};
            }}
        """)
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(28, 0, 28, 0)

        self.page_title = QLabel("Convert Blueprint")
        self.page_title.setStyleSheet(f"""
            font-size: 15px; font-weight: 600; color: {Theme.TEXT_H1};
            background: transparent; border: none;
        """)
        layout.addWidget(self.page_title)
        layout.addStretch()

        self.page_desc = QLabel("Upload a 2D floorplan and generate a 3D model")
        self.page_desc.setStyleSheet(f"""
            font-size: 11px; color: {Theme.TEXT_SECONDARY};
            background: transparent; border: none;
        """)
        layout.addWidget(self.page_desc)
        return topbar

    # ── Page Builders ────────────────────────────────────────────────

    def _build_convert_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        page_layout = QVBoxLayout(page)
        page_layout.setSpacing(0)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # Body: two columns
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QHBoxLayout(body)
        body_layout.setSpacing(24)
        body_layout.setContentsMargins(28, 24, 28, 16)

        # Left column — Upload
        left_col = QVBoxLayout()
        left_col.setSpacing(14)
        left_heading = QLabel("Upload")
        left_heading.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Theme.TEXT_SECONDARY};
            letter-spacing: 0.4px; background: transparent;
        """)
        left_col.addWidget(left_heading)

        self.upload_zone = UploadZone()
        self.upload_zone.file_dropped.connect(self._on_file_selected)
        left_col.addWidget(self.upload_zone)

        self.browse_btn = make_ghost_button("Browse files...", tooltip="Select a PNG or JPG blueprint image")
        self.browse_btn.clicked.connect(self._browse_file)
        left_col.addWidget(self.browse_btn)
        left_col.addStretch()
        body_layout.addLayout(left_col, 42)

        # Right column — Preview
        right_col = QVBoxLayout()
        right_col.setSpacing(14)
        right_heading = QLabel("Preview")
        right_heading.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Theme.TEXT_SECONDARY};
            letter-spacing: 0.4px; background: transparent;
        """)
        right_col.addWidget(right_heading)

        preview_frame = QFrame()
        preview_frame.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_RAISED};
                border: 1px solid {Theme.BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(Theme.SHADOW_COLOR)
        preview_frame.setGraphicsEffect(shadow)

        pf_layout = QVBoxLayout(preview_frame)
        pf_layout.setContentsMargins(12, 12, 12, 12)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.preview_label = QLabel("No blueprint selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(280)
        self.preview_label.setStyleSheet(f"""
            color: {Theme.TEXT_MUTED}; font-size: 12px;
            background: {Theme.BG_SURFACE};
            border: 1px dashed {Theme.BORDER_SUBTLE}; border-radius: 8px;
        """)
        self.scroll_area.setWidget(self.preview_label)
        pf_layout.addWidget(self.scroll_area)
        right_col.addWidget(preview_frame)
        body_layout.addLayout(right_col, 58)

        page_layout.addWidget(body, 1)

        # Action bar
        action_bar = QFrame()
        action_bar.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_RAISED};
                border-top: 1px solid {Theme.BORDER_SUBTLE};
            }}
        """)
        ab_layout = QVBoxLayout(action_bar)
        ab_layout.setSpacing(10)
        ab_layout.setContentsMargins(28, 14, 28, 14)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {Theme.BG_SURFACE}; border: none; border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {Theme.ACCENT}, stop:1 #8b5cf6);
                border-radius: 2px;
            }}
        """)
        ab_layout.addWidget(self.progress_bar)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            font-size: 11px; color: {Theme.TEXT_SECONDARY}; background: transparent;
        """)
        btn_row.addWidget(self.status_label)
        btn_row.addStretch()

        self.blender_btn = make_blender_button("Open in Blender", "Open the generated .blend file")
        self.blender_btn.clicked.connect(self._open_in_blender)
        self.blender_btn.setEnabled(False)
        btn_row.addWidget(self.blender_btn)

        self.convert_btn = make_primary_button("Convert to 3D", "Start the floorplan-to-3D conversion")
        self.convert_btn.clicked.connect(self._convert)
        self.convert_btn.setEnabled(False)
        btn_row.addWidget(self.convert_btn)

        ab_layout.addLayout(btn_row)
        page_layout.addWidget(action_bar)
        return page

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        page_layout = QVBoxLayout(page)
        page_layout.setSpacing(0)
        page_layout.setContentsMargins(28, 24, 28, 24)

        top_row = QHBoxLayout()
        heading = QLabel("Exported Models")
        heading.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Theme.TEXT_SECONDARY};
            letter-spacing: 0.4px; background: transparent;
        """)
        top_row.addWidget(heading)
        top_row.addStretch()

        refresh_btn = make_ghost_button("Refresh", tooltip="Reload the list of exported models")
        refresh_btn.clicked.connect(self._refresh_history)
        top_row.addWidget(refresh_btn)
        page_layout.addLayout(top_row)
        page_layout.addSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.history_list = QWidget()
        self.history_list.setStyleSheet("background: transparent;")
        self.history_list_layout = QVBoxLayout(self.history_list)
        self.history_list_layout.setSpacing(8)
        self.history_list_layout.setContentsMargins(0, 0, 0, 0)
        self.history_list_layout.addStretch()

        scroll.setWidget(self.history_list)
        page_layout.addWidget(scroll, 1)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        page_layout = QVBoxLayout(page)
        page_layout.setSpacing(20)
        page_layout.setContentsMargins(28, 24, 28, 24)

        # Blender Configuration Card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_RAISED};
                border: 1px solid {Theme.BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 20, 24, 20)

        card_title = QLabel("Blender Configuration")
        card_title.setStyleSheet(f"""
            font-size: 14px; font-weight: 600; color: {Theme.TEXT_H1};
            background: transparent; border: none;
        """)
        card_layout.addWidget(card_title)

        card_desc = QLabel(
            "Configure the path to your Blender installation. "
            "PlanX3D uses Blender to generate 3D models from processed blueprint data."
        )
        card_desc.setWordWrap(True)
        card_desc.setStyleSheet(f"""
            font-size: 12px; color: {Theme.TEXT_SECONDARY};
            background: transparent; border: none; line-height: 1.5;
        """)
        card_layout.addWidget(card_desc)

        path_label = QLabel("Installation Path")
        path_label.setStyleSheet(f"""
            font-size: 11px; font-weight: 600; color: {Theme.TEXT_SECONDARY};
            letter-spacing: 0.3px; background: transparent; border: none;
        """)
        card_layout.addWidget(path_label)

        self.settings_path_label = QLabel("Not configured")
        self.settings_path_label.setWordWrap(True)
        self.settings_path_label.setStyleSheet(f"""
            font-size: 12px; color: {Theme.TEXT_BODY};
            background: {Theme.BG_SURFACE};
            border: 1px solid {Theme.BORDER_DEFAULT};
            border-radius: 6px; padding: 10px 14px;
        """)
        card_layout.addWidget(self.settings_path_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        detect_btn = make_ghost_button("Auto-detect", tooltip="Scan common installation paths")
        detect_btn.clicked.connect(self._settings_detect_blender)
        btn_row.addWidget(detect_btn)
        browse_btn = make_ghost_button("Browse...", tooltip="Manually select blender.exe")
        browse_btn.clicked.connect(self._settings_browse_blender)
        btn_row.addWidget(browse_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        self.settings_status = QLabel("")
        self.settings_status.setStyleSheet(f"""
            font-size: 11px; color: {Theme.TEXT_MUTED};
            background: transparent; border: none;
        """)
        card_layout.addWidget(self.settings_status)
        page_layout.addWidget(card)

        # About Card
        about_card = QFrame()
        about_card.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_RAISED};
                border: 1px solid {Theme.BORDER_SUBTLE};
                border-radius: 10px;
            }}
        """)
        about_layout = QVBoxLayout(about_card)
        about_layout.setSpacing(8)
        about_layout.setContentsMargins(24, 20, 24, 20)

        about_title = QLabel("About PlanX3D")
        about_title.setStyleSheet(f"""
            font-size: 14px; font-weight: 600; color: {Theme.TEXT_H1};
            background: transparent; border: none;
        """)
        about_layout.addWidget(about_title)

        about_text = QLabel(
            "PlanX3D converts 2D floorplan blueprints into 3D models using \n"
            "computer vision (OpenCV) for feature detection and Blender for \n"
            "3D scene generation. Supports PNG, JPG, and JPEG inputs."
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet(f"""
            font-size: 12px; color: {Theme.TEXT_SECONDARY};
            background: transparent; border: none; line-height: 1.5;
        """)
        about_layout.addWidget(about_text)
        page_layout.addWidget(about_card)
        page_layout.addStretch()
        return page

    # ════════════════════════════════════════════════════════════════
    #  Navigation
    # ════════════════════════════════════════════════════════════════

    def _switch_page(self, index: int):
        self.page_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        title, desc = self._page_meta[index]
        self.page_title.setText(title)
        self.page_desc.setText(desc)
        if index == 1:
            self._refresh_history()
        if index == 2:
            self._update_settings_display()

    # ════════════════════════════════════════════════════════════════
    #  History
    # ════════════════════════════════════════════════════════════════

    def _refresh_history(self):
        # Clear existing items (keep trailing stretch)
        while self.history_list_layout.count() > 1:
            item = self.history_list_layout.takeAt(0)
            if (w := item.widget()):
                w.deleteLater()

        target = Path("Target")
        blend_files = sorted(target.glob("*.blend"), key=lambda x: x.stat().st_mtime, reverse=True) if target.exists() else []

        if not blend_files:
            empty = QLabel("No models exported yet. Convert a blueprint to see results here.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"""
                color: {Theme.TEXT_MUTED}; font-size: 12px;
                padding: 40px; background: transparent;
            """)
            self.history_list_layout.insertWidget(0, empty)
            return

        for i, bf in enumerate(blend_files):
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: {Theme.BG_RAISED};
                    border: 1px solid {Theme.BORDER_SUBTLE};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    background: {Theme.BG_ELEVATED};
                    border-color: {Theme.BORDER_DEFAULT};
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(16, 12, 16, 12)
            row_layout.setSpacing(12)

            info_col = QVBoxLayout()
            info_col.setSpacing(2)

            name_lbl = QLabel(bf.name)
            name_lbl.setStyleSheet(f"""
                font-size: 12px; font-weight: 600; color: {Theme.TEXT_H1};
                background: transparent; border: none;
            """)
            info_col.addWidget(name_lbl)

            stat = bf.stat()
            size_mb = stat.st_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%b %d, %Y  %H:%M")
            meta_lbl = QLabel(f"{size_mb:.1f} MB  ·  {mod_time}")
            meta_lbl.setStyleSheet(f"""
                font-size: 10px; color: {Theme.TEXT_MUTED};
                background: transparent; border: none;
            """)
            info_col.addWidget(meta_lbl)
            row_layout.addLayout(info_col)
            row_layout.addStretch()

            open_btn = make_ghost_button("Open", color=Theme.BLENDER)
            open_btn.setFixedWidth(80)
            blend_path = str(bf)
            open_btn.clicked.connect(lambda checked, p=blend_path: self._open_blend_file(p))
            row_layout.addWidget(open_btn)

            self.history_list_layout.insertWidget(i, row)

    def _open_blend_file(self, path: str):
        blender = self.blender_path
        if not blender:
            QMessageBox.warning(self, "Blender Required",
                                "Blender path not configured. Go to Settings to set it up.")
            return
        try:
            subprocess.Popen([blender, path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Blender: {e}")

    # ════════════════════════════════════════════════════════════════
    #  Settings
    # ════════════════════════════════════════════════════════════════

    def _update_settings_display(self):
        if self.blender_path:
            self.settings_path_label.setText(self.blender_path)
            self.settings_path_label.setStyleSheet(f"""
                font-size: 12px; color: {Theme.SUCCESS};
                background: {Theme.BG_SURFACE};
                border: 1px solid {Theme.BORDER_DEFAULT};
                border-radius: 6px; padding: 10px 14px;
            """)
            self.settings_status.setText("Blender detected and ready")
            self.settings_status.setStyleSheet(f"""
                font-size: 11px; color: {Theme.SUCCESS};
                background: transparent; border: none;
            """)
        else:
            self.settings_path_label.setText("Not configured")
            self.settings_path_label.setStyleSheet(f"""
                font-size: 12px; color: {Theme.TEXT_MUTED};
                background: {Theme.BG_SURFACE};
                border: 1px solid {Theme.BORDER_DEFAULT};
                border-radius: 6px; padding: 10px 14px;
            """)
            self.settings_status.setText("")

    def _settings_detect_blender(self):
        self.blender_path = None
        self._detect_blender()
        self._update_settings_display()
        if self.blender_path:
            self.settings_status.setText("Auto-detected successfully")
            self.settings_status.setStyleSheet(f"""
                font-size: 11px; color: {Theme.SUCCESS};
                background: transparent; border: none;
            """)
        else:
            self.settings_status.setText("Could not auto-detect Blender. Use Browse to set manually.")
            self.settings_status.setStyleSheet(f"""
                font-size: 11px; color: {Theme.WARNING};
                background: transparent; border: none;
            """)

    def _settings_browse_blender(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Blender Executable", "", "Executable (*.exe)")
        if path:
            self.blender_path = path
            self._save_blender_path(path)
            self._update_settings_display()
            self.settings_status.setText("Path saved")
            self.settings_status.setStyleSheet(f"""
                font-size: 11px; color: {Theme.SUCCESS};
                background: transparent; border: none;
            """)

    # ════════════════════════════════════════════════════════════════
    #  Blender Detection (uses shared find_blender)
    # ════════════════════════════════════════════════════════════════

    def _detect_blender(self):
        self.blender_path = find_blender()
        if self.blender_path:
            ver = os.path.basename(os.path.dirname(self.blender_path))
            self.blender_label.setText(f"Blender · {ver}")
            self.blender_label.setStyleSheet(f"""
                font-size: 10px; color: {Theme.SUCCESS};
                padding: 12px 16px; background: {Theme.SUCCESS_MUTED};
                border-top: 1px solid {Theme.BORDER_SUBTLE};
            """)
        else:
            self.blender_label.setText("Blender not detected")
            self.blender_label.setStyleSheet(f"""
                font-size: 10px; color: {Theme.WARNING};
                padding: 12px 16px; background: {Theme.WARNING_MUTED};
                border-top: 1px solid {Theme.BORDER_SUBTLE};
            """)

    # ════════════════════════════════════════════════════════════════
    #  File Handling
    # ════════════════════════════════════════════════════════════════

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Blueprint", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self._on_file_selected(path)

    def _on_file_selected(self, path: str):
        self.selected_file = path
        self.upload_zone.set_file(path)
        self._load_preview(path)
        self.convert_btn.setEnabled(True)
        self._set_status("Blueprint loaded — ready to convert", Theme.TEXT_BODY)

    def _load_preview(self, path: str):
        pix = QPixmap(path)
        if not pix.isNull():
            scaled = pix.scaled(560, 440, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled)
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.preview_label.setStyleSheet(f"""
                background: {Theme.BG_SURFACE}; border: none;
                border-radius: 8px; padding: 8px;
            """)
        else:
            self.preview_label.setText("Failed to load image")

    # ════════════════════════════════════════════════════════════════
    #  Conversion
    # ════════════════════════════════════════════════════════════════

    def _convert(self):
        if not self.selected_file:
            return
        self.convert_btn.setEnabled(False)
        self.blender_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self._set_status("Processing blueprint...", Theme.ACCENT)

        worker = ConversionWorker(self.selected_file, self.blender_path)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)
        worker.progress.connect(lambda msg: self._set_status(msg, Theme.ACCENT))
        worker.start()
        self.worker = worker

    def _on_finished(self, blend_path: str):
        self._last_blend = blend_path
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.blender_btn.setEnabled(True)
        name = os.path.basename(blend_path)
        self._set_status(f"Done — {name}", Theme.SUCCESS)

    def _on_error(self, msg: str):
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self._set_status(msg, Theme.ERROR)
        QMessageBox.critical(self, "Conversion Error", msg)

    # ════════════════════════════════════════════════════════════════
    #  Open in Blender
    # ════════════════════════════════════════════════════════════════

    def _open_in_blender(self):
        blend: Optional[str] = None
        last = self._last_blend
        if last is not None and os.path.exists(last):
            blend = last
        else:
            td = Path("Target")
            if td.exists():
                files = list(td.glob("*.blend"))
                if files:
                    blend = str(max(files, key=lambda x: x.stat().st_mtime))

        if not blend:
            QMessageBox.warning(self, "Not Found", "No .blend file found. Convert a blueprint first.")
            return

        blender = self.blender_path
        if not blender:
            p, _ = QFileDialog.getOpenFileName(self, "Select Blender", "", "Executable (*.exe)")
            if p:
                self.blender_path = p
                self._save_blender_path(p)
                blender = p
            else:
                return
        try:
            subprocess.Popen([blender, blend])
            self._set_status("Opening in Blender...", Theme.BLENDER)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Blender: {e}")

    # ════════════════════════════════════════════════════════════════
    #  Helpers
    # ════════════════════════════════════════════════════════════════

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            font-size: 11px; color: {color}; background: transparent;
        """)

    def _save_blender_path(self, path: str):
        try:
            with open("blender_path.txt", "w") as f:
                f.write(path)
        except Exception:
            pass

    def _load_blender_path(self):
        try:
            if os.path.exists("blender_path.txt"):
                with open("blender_path.txt") as f:
                    p = f.read().strip()
                    if os.path.exists(p):
                        self.blender_path = p
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(Theme.BG_BASE))
    pal.setColor(QPalette.WindowText,      QColor(Theme.TEXT_BODY))
    pal.setColor(QPalette.Base,            QColor(Theme.BG_RAISED))
    pal.setColor(QPalette.AlternateBase,   QColor(Theme.BG_SURFACE))
    pal.setColor(QPalette.ToolTipBase,     QColor(Theme.BG_ELEVATED))
    pal.setColor(QPalette.ToolTipText,     QColor(Theme.TEXT_BODY))
    pal.setColor(QPalette.Text,            QColor(Theme.TEXT_BODY))
    pal.setColor(QPalette.Button,          QColor(Theme.BG_SURFACE))
    pal.setColor(QPalette.ButtonText,      QColor(Theme.TEXT_BODY))
    pal.setColor(QPalette.Highlight,       QColor(Theme.ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.Disabled, QPalette.Text,       QColor(Theme.TEXT_MUTED))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(Theme.TEXT_MUTED))
    app.setPalette(pal)
    app.setStyleSheet(STYLESHEET)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
