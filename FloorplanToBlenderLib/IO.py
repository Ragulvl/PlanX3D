"""
IO
File I/O utilities for reading images, managing data paths,
and persisting generated geometry to disk.
"""

import json
import logging
import os
from shutil import which
import shutil
import cv2
import platform
from sys import platform as pf
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from . import const
from . import image
from . import config
from .exceptions import ImageProcessingError

logger = logging.getLogger(__name__)


def find_reuseable_data(image_path: str, path: str) -> Tuple[Optional[str], Optional[List[float]]]:
    """
    Check if floorplan data already exists and can be reused.

    @Param image_path: path to the source image
    @Param path: base data directory to scan
    @Return: (origin_path, shape) or (None, None) if not found
    """
    if not os.path.exists(path):
        return None, None
    try:
        for entry in os.scandir(path):
            if entry.is_dir():
                transform_file = path + entry.name + const.TRANSFORM_PATH
                try:
                    with open(transform_file) as f:
                        data = f.read()
                    js = json.loads(data)
                    if image_path == js[const.STR_IMAGE_PATH]:
                        return js[const.STR_ORIGIN_PATH], js[const.STR_SHAPE]
                except (IOError, json.JSONDecodeError, KeyError) as exc:
                    logger.debug("Skipping transform file %s: %s", transform_file, exc)
                    continue
    except OSError as exc:
        logger.debug("Error scanning data directory %s: %s", path, exc)
    return None, None


def find_files(filename: str, search_path: str) -> Optional[str]:
    """
    Find filename in root search path.

    @Param filename: name of the file to locate
    @Param search_path: root directory to walk
    @Return: absolute path if found, else None
    """
    for root, _, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


def blender_installed() -> Optional[str]:
    """
    Find path to blender installation.
    Tested on Ubuntu and Windows; macOS support is best-effort.
    """
    if pf == "linux" or pf == "linux2":
        return find_files("blender", "/")
    elif pf == "darwin":
        # Known limitation: macOS search may be slow on large volumes
        return find_files("blender", "/")
    elif pf == "win32":
        return find_files("blender.exe", "C:\\")
    return None


def get_blender_os_path() -> str:
    """Return the default Blender install path for the current OS."""
    _platform = platform.system().lower()
    if _platform in ("linux", "linux2", "ubuntu"):
        return const.LINUX_DEFAULT_BLENDER_INSTALL_PATH
    elif _platform == "darwin":
        return const.MAC_DEFAULT_BLENDER_INSTALL_PATH
    elif "win" in _platform:
        return const.WIN_DEFAULT_BLENDER_INSTALL_PATH
    return const.LINUX_DEFAULT_BLENDER_INSTALL_PATH


def read_image(path: str, floorplan: Any = None) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Read image, resize/rescale and return with grayscale.

    @Param path: path to the image file
    @Param floorplan: optional Floorplan instance for noise/rescale settings
    @Return: (colour_image, grayscale_image, scale_factor)
    @Raises ImageProcessingError: if the image cannot be read
    """
    if not os.path.isfile(path):
        raise ImageProcessingError(f"Image file does not exist: {path}")

    img = cv2.imread(path)
    if img is None:
        raise ImageProcessingError(
            f"OpenCV could not decode image (corrupt or unsupported format): {path}"
        )

    scale_factor: float = 1.0
    if floorplan is not None:
        if floorplan.remove_noise:
            img = image.denoising(img)
        if floorplan.rescale_image:
            calibrations = config.read_calibration(floorplan)
            floorplan.wall_size_calibration = calibrations
            scale_factor = image.detect_wall_rescale(float(calibrations), img)
            if scale_factor is None:
                logger.warning(
                    "Auto rescale failed — no suitable walls found. "
                    "If rescale is still needed, please rescale manually."
                )
                scale_factor = 1.0
            else:
                img = image.cv2_rescale_image(img, scale_factor)

    return img, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), scale_factor


def readlines_file(path):
    res = []
    with open(path, "r") as f:
        res = f.readlines()
    return res


def ndarrayJsonDumps(obj):
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj.item()
    raise TypeError("Unknown type:", type(obj))


def save_to_file(file_path: str, data: Any, show: bool = True) -> None:
    """
    Serialise data as JSON and write to disk.

    @Param file_path: path without extension (SAVE_DATA_FORMAT is appended)
    @Param data: data to serialise
    @Param show: if True, log the created file path
    """
    with open(file_path + const.SAVE_DATA_FORMAT, "w") as f:
        try:
            f.write(json.dumps(data))
        except TypeError:
            f.write(json.dumps(data, default=ndarrayJsonDumps))

    if show:
        logger.info("Created file: %s%s", file_path, const.SAVE_DATA_FORMAT)


def read_from_file(file_path: str) -> Any:
    """
    Read JSON-serialised vertex/face data from file.

    @Param file_path: path without extension (SAVE_DATA_FORMAT is appended)
    @Return: deserialised data
    """
    with open(file_path + const.SAVE_DATA_FORMAT, "r") as f:
        data = json.loads(f.read())
    return data


def clean_data_folder(folder):
    """
    Remove old data files
    Don't want to fill memory
    @Param folder, path to data folder
    """
    for root, dirs, files in os.walk(folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def create_new_floorplan_path(path):
    """
    Creates next free name to floorplan data
    @Param path, path to floorplan
    @Return end path
    """
    res = 0
    for _, dirs, _ in os.walk(path):
        for _ in dirs:
            try:
                name_not_found = True
                while name_not_found:
                    if not os.path.exists(path + str(res) + "/"):
                        break
                    res += 1
            except Exception:
                continue

    res = path + str(res) + "/"
    if not os.path.exists(res):
        os.makedirs(res)
    return res


def get_current_path():
    """
    Get path to this programs path
    @Return path to working directory
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path


def find_program_path(name):
    """
    Find program path
    @Param name, name of program to find
    """
    return which(name)


def get_next_target_base_name(target_base, target_path):
    """
    Generate appropriate next target name
    If blender target file already exist, get next id
    """
    fid = 0
    if os.path.isfile("." + target_path):
        for file in os.listdir("." + const.TARGET_PATH):
            filename = os.fsdecode(file)
            if filename.endswith(const.BASE_FORMAT):
                fid += 1
        target_base += str(fid)

    return target_base
