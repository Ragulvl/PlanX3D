import sys

try:
    sys.path.insert(0, sys.path[0] + "/..")
    from FloorplanToBlenderLib import *  # floorplan to blender lib
except ImportError:
    raise ImportError  # floorplan to blender lib


def test_validate_shape_basic():
    result = generate.validate_shape([1, 1, 1], [2, 3, 4])
    assert result == [2, 3, 4]


def test_validate_shape_takes_max():
    result = generate.validate_shape([5, 1, 3], [2, 6, 1])
    assert result == [5, 6, 3]


def test_validate_shape_equal():
    result = generate.validate_shape([2, 2, 2], [2, 2, 2])
    assert result == [2, 2, 2]


def test_validate_shape_zeros():
    result = generate.validate_shape([0, 0, 0], [0, 0, 0])
    assert result == [0, 0, 0]
