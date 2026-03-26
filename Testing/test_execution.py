import sys
import math
import numpy as np

try:
    sys.path.insert(0, sys.path[0] + "/..")
    from FloorplanToBlenderLib import *  # floorplan to blender lib
except ImportError:
    raise ImportError  # floorplan to blender lib


def test_rotate_around_axis():
    """Rotating (1,0,0) by 90° around Z-axis should give approx (0,1,0)."""
    result = execution.rotate_around_axis(
        np.array([0, 0, 1]), np.array([1, 0, 0]), 90
    )
    assert abs(result[0] - 0) < 0.01
    assert abs(result[1] - 1) < 0.01
    assert abs(result[2] - 0) < 0.01


def test_angle_between_points():
    """Angle from origin to (1,1) should be 45°."""
    angle = execution.angle_between_points((0, 0), (1, 1))
    assert abs(angle - 45.0) < 0.01


def test_angle_between_points_horizontal():
    """Angle from origin to (1,0) should be 0°."""
    angle = execution.angle_between_points((0, 0), (1, 0))
    assert abs(angle - 0.0) < 0.01


def test_angle_between_points_vertical():
    """Angle from origin to (0,1) should be 90°."""
    angle = execution.angle_between_points((0, 0), (0, 1))
    assert abs(angle - 90.0) < 0.01
