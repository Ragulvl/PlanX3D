import sys

try:
    sys.path.insert(0, sys.path[0] + "/..")
    from FloorplanToBlenderLib import *  # floorplan to blender lib
except ImportError:
    raise ImportError  # floorplan to blender lib


def test_floorplan_creates_from_default():
    """Floorplan loads from default config without error."""
    fp = floorplan.Floorplan()
    assert hasattr(fp, "image_path")
    assert hasattr(fp, "conf")


def test_floorplan_str():
    fp = floorplan.Floorplan()
    s = str(fp)
    assert isinstance(s, str)
    assert "image_path" in s


def test_floorplan_repr():
    fp = floorplan.Floorplan()
    r = repr(fp)
    assert r.startswith("Floorplan(conf=")
    assert "image_path" in r


def test_new_floorplan_factory():
    """Factory function returns a Floorplan instance."""
    fp = floorplan.new_floorplan()
    assert isinstance(fp, floorplan.Floorplan)
