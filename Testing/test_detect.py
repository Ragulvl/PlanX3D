import sys
import numpy as np
import cv2

try:
    sys.path.insert(0, sys.path[0] + "/..")
    from FloorplanToBlenderLib import *  # floorplan to blender lib
except ImportError:
    raise ImportError  # floorplan to blender lib

height = 500
width = 500
blank_image = np.zeros((height, width, 3), np.uint8)
gray = np.ones((height, width), dtype=np.uint8)


def test_wall_filter():
    result = detect.wall_filter(gray)
    assert isinstance(result, np.ndarray)
    assert result.shape == (height, width)


def test_precise_boxes():
    boxes, out = detect.precise_boxes(gray)
    assert isinstance(boxes, list)


def test_find_room():
    components, img = detect.find_rooms(gray)
    assert isinstance(components, list)
    assert isinstance(img, np.ndarray)


def test_and_remove_precise_boxes():
    boxes, out = detect.and_remove_precise_boxes(gray)
    assert isinstance(boxes, list)


def test_outer_contours():
    contour, out = detect.outer_contours(gray)
    assert isinstance(contour, np.ndarray)
    assert contour.ndim >= 2


def test_find_details():
    components, img = detect.find_details(gray)
    assert isinstance(components, list)
    assert isinstance(img, np.ndarray)
