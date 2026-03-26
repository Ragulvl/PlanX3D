# pyre-ignore-all-errors
"""
ConversionWorker — Background thread for floorplan-to-3D conversion.
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal

from FloorplanToBlenderLib.execution import simple_single
from FloorplanToBlenderLib.floorplan import floorplan

logger = logging.getLogger(__name__)

# Blender version search order (newest first)
_BLENDER_VERSIONS = [
    "5.2", "5.1", "5.0", "4.5", "4.4", "4.3", "4.2", "4.1", "4.0",
    "3.6", "3.5", "3.4", "3.3", "3.2", "3.1", "3.0",
]


def find_blender() -> Optional[str]:
    """
    Auto-detect Blender installation path.
    Checks common Windows paths, then falls back to PATH lookup.
    """
    for v in _BLENDER_VERSIONS:
        p = rf"C:\Program Files\Blender Foundation\Blender {v}\blender.exe"
        if os.path.exists(p):
            return p
    try:
        r = subprocess.run(['where', 'blender'], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return None


class ConversionWorker(QThread):
    """Background thread that runs the CV + Blender pipeline."""

    finished = Signal(str)
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, image_path: str, blender_path: Optional[str] = None):
        super().__init__()
        self.image_path = image_path
        self.blender_path = blender_path

    def run(self):
        try:
            self.progress.emit("Loading and preprocessing image...")
            fp = floorplan("Configs/default.ini")
            fp.image_path = self.image_path

            self.progress.emit("Detecting walls, rooms & floor geometry...")
            data_path = simple_single(fp, show=False)

            self.progress.emit("Launching Blender to generate 3D model...")
            target_dir = Path("Target")
            target_dir.mkdir(exist_ok=True)

            blender_path = self.blender_path or find_blender()
            if not blender_path:
                self.error.emit("Blender not found. Please install Blender or configure the path.")
                return

            self._verify_blender(blender_path)

            input_name = Path(self.image_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_file = target_dir / f"{input_name}_{timestamp}.blend"
            self._create_blend(blender_path, data_path, target_file)

            if target_file.exists():
                self.finished.emit(str(target_file))
            else:
                self.error.emit("Failed to create .blend file")
        except Exception as e:
            logger.exception("Conversion failed")
            self.error.emit(f"Error: {e}")

    def _verify_blender(self, blender_path: str):
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError("Blender installation invalid")
        if not os.path.exists("Blender/build_3d_scene.py"):
            raise FileNotFoundError("Blender script not found")

    def _create_blend(self, blender_path: str, data_path: str, target_file: Path):
        script = "Blender/build_3d_scene.py"
        if not os.path.exists(script):
            scripts = list(Path("Blender").glob("*.py"))
            if scripts:
                script = str(scripts[0])
            else:
                raise FileNotFoundError("No Blender script found")
        subprocess.run(
            [
                blender_path, "-noaudio", "--background",
                "--python", script,
                str(Path.cwd()), target_file.name, str(data_path),
            ],
            check=True, capture_output=True, text=True,
        )
