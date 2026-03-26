import sys
import numpy as np

try:
    sys.path.insert(0, sys.path[0] + "/..")
    from FloorplanToBlenderLib import *  # floorplan to blender lib
except ImportError:
    raise ImportError  # floorplan to blender lib

height = 500
width = 500
blank_image = np.zeros((height, width, 3), np.uint8)
gray = np.ones((height, width), dtype=np.uint8)


def test_cv2_rescale_image():
    result = image.cv2_rescale_image(blank_image, 3)
    assert isinstance(result, np.ndarray)
    assert result.shape[0] == height * 3
    assert result.shape[1] == width * 3


def test_calculate_scale_factor():
    result = image.calculate_scale_factor(20, 30)
    assert isinstance(result, (int, float))
    assert result > 0


def test_denoising():
    result = image.denoising(blank_image)
    assert isinstance(result, np.ndarray)
    assert result.shape == blank_image.shape


def test_detect_wall_rescale():
    result = image.detect_wall_rescale(blank_image, blank_image)
    # May return None or a float depending on input
    assert result is None or isinstance(result, (int, float))
