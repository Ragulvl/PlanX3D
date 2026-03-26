import cv2
import math
import logging
import numpy as np
from typing import List, Tuple, Optional, Sequence

from . import detect
from . import const

logger = logging.getLogger(__name__)

"""
Calculate
This file contains functions for handling math or calculations.

FloorplanToBlender3d
"""


def average(lst: Sequence[float]) -> float:
    if not lst:
        raise ValueError("Cannot compute average of an empty sequence")
    return sum(lst) / len(lst)


def points_inside_contour(points: Sequence[Tuple[float, float]], contour: np.ndarray) -> bool:
    """
    Return True if any of the points are inside the contour.
    """
    contour = contour.astype(np.float32)
    for x, y in points:
        point = np.array([x, y], dtype=np.float32)
        if cv2.pointPolygonTest(contour, tuple(point), False) >= 0:
            return True
    return False


def remove_walls_not_in_contour(walls: List[np.ndarray], contour: np.ndarray) -> List[np.ndarray]:
    """
    Returns a list of boxes where walls outside of contour are removed.
    """
    return [wall for wall in walls if any(points_inside_contour(point, contour) for point in wall)]


def wall_width_average(img: np.ndarray) -> Optional[float]:
    """
    Calculate average wall width in a floorplan image.
    Used to scale the image for better detection accuracy.
    Returns the average as float, or None if no walls are detected.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img.shape[:2]
    blank_image = np.zeros((height, width, 3), np.uint8)

    wall_img = detect.wall_filter(gray)
    boxes, _ = detect.precise_boxes(wall_img, blank_image)

    # Keep only quadrilateral contours and measure their shortest side
    wall_widths = [
        min(cv2.boundingRect(box)[2], cv2.boundingRect(box)[3])
        for box in boxes
        if len(box) == 4
    ]

    if not wall_widths:
        return None

    return average(wall_widths)


def best_matches_with_modulus_angle(match_list):
    """
    This function compare matching matches from orb feature matching,
    by rotating in steps over 360 degrees in order to find the best fit for door rotation.
    """
    # calculate best matches by looking at the most significant feature distances
    index1 = 0
    index2 = 0
    best = math.inf

    for i, _ in enumerate(match_list):
        for j, _ in enumerate(match_list):

            pos1_model = match_list[i][0]
            pos2_model = match_list[j][0]

            pos1_cap = match_list[i][1]
            pos2_cap = match_list[j][1]

            pt1 = (pos1_model[0] - pos2_model[0], pos1_model[1] - pos2_model[1])
            pt2 = (pos1_cap[0] - pos2_cap[0], pos1_cap[1] - pos2_cap[1])

            if pt1 == pt2 or pt1 == (0, 0) or pt2 == (0, 0):
                continue

            ang = math.degrees(angle_between_vectors_2d(pt1, pt2))
            diff = ang % const.DOOR_ANGLE_HIT_STEP

            if diff < best:
                best = diff
                index1 = i
                index2 = j

    return index1, index2


def points_are_inside_or_close_to_box(door, box):
    """
    Calculate if a point is within vicinity of a box.
    @parameter Door is a list of points
    @parameter Box is a numpy box
    """
    for point in door:
        if rect_contains_or_almost_contains_point(point, box):
            return True
    return False


def angle_between_vectors_2d(vector1: Tuple[float, float], vector2: Tuple[float, float]) -> float:
    """
    Get angle between two 2D vectors.
    Returns angle in radians.
    """
    x1, y1 = vector1
    x2, y2 = vector2
    inner_product = x1 * x2 + y1 * y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    denominator = len1 * len2
    if denominator == 0:
        return 0.0
    # Clamp to [-1, 1] to handle floating-point rounding
    return math.acos(max(-1.0, min(1.0, inner_product / denominator)))


def rect_contains_or_almost_contains_point(pt, box):
    """
    Calculate if a point is within vicinity of a box. Help function.
    """

    x, y, w, h = cv2.boundingRect(box)
    is_inside = x < pt[0] < x + w and y < pt[1] < y + h

    almost_inside = False

    min_dist = 0
    if w < h:
        min_dist = w
    else:
        min_dist = h

    for point in box:
        dist = abs(point[0][0] - pt[0]) + abs(point[0][1] - pt[1])
        if dist <= min_dist:
            almost_inside = True
            break

    return is_inside or almost_inside


def box_center(box):
    """
    Get center position of box
    """
    x, y, w, h = cv2.boundingRect(box)
    return (x + w / 2, y + h / 2)


def euclidean_distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two 2D points.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def magnitude_2d(point):
    """
    Calculate magnitude of two points
    """
    return math.sqrt(point[0] * point[0] + point[1] * point[1])


def normalize_2d(normal: List[float]) -> List[float]:
    """
    Normalize a 2D vector in-place. Returns [0, 0] for zero-length vectors.
    """
    mag = magnitude_2d(normal)
    if mag == 0:
        return [0.0, 0.0]
    for i, val in enumerate(normal):
        normal[i] = val / mag
    return normal
