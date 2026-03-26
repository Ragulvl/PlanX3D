"""
Generate
Orchestrates full 3D data generation from a parsed floorplan image.
Delegates geometry creation to generator classes (Floor, Wall, Room, etc.)
and persists transform metadata to disk.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from . import IO
from . import const
from . import transform
from . import detect
from .generator import Door, Floor, Room, Wall, Window

def generate_all_files(
    floorplan: Any,
    info: bool,
    world_direction: Optional[int] = None,
    world_scale: np.ndarray = np.array([1, 1, 1]),
    world_position: np.ndarray = np.array([0, 0, 0]),
    world_rotation: np.ndarray = np.array([0, 0, 0]),
) -> Tuple[str, List[float]]:
    """
    Generate all 3D data files for a single floorplan.

    @Param floorplan: Floorplan instance with image path and feature flags
    @Param info: if True, print progress info
    @Param world_direction: build direction (+1 or -1)
    @Param world_scale: global scale multiplier
    @Param world_position: global position offset
    @Param world_rotation: global rotation offset
    @Return: (path_to_generated_data, shape)
    """
    if world_direction is None:
        world_direction = 1

    scale = [
        floorplan.scale[0] * world_scale[0],
        floorplan.scale[1] * world_scale[1],
        floorplan.scale[2] * world_scale[2],
    ]

    if info:
        print(
            " ----- Generate ",
            floorplan.image_path,
            " at pos ",
            transform.list_to_nparray(floorplan.position)
            + transform.list_to_nparray(world_position),
            " rot ",
            transform.list_to_nparray(floorplan.rotation)
            + transform.list_to_nparray(world_rotation),
            " scale ",
            scale,
            " -----",
        )

    # Get path to save data
    path = IO.create_new_floorplan_path(const.BASE_PATH)

    origin_path, shape = IO.find_reuseable_data(floorplan.image_path, const.BASE_PATH)

    if origin_path is None:
        origin_path = path

        src_img, gray, scale_factor = IO.read_image(floorplan.image_path, floorplan)

        # ── Pre-compute expensive shared CV results ONCE ──
        wall_img = detect.wall_filter(gray)
        contour, _ = detect.outer_contours(gray)
        shared = dict(wall_img=wall_img, contour=contour, src_img=src_img)

        if floorplan.floors:
            shape = Floor(gray, path, scale, info, **shared).shape

        if floorplan.walls:
            if shape is not None:
                new_shape = Wall(gray, path, scale, info, **shared).shape
                shape = validate_shape(shape, new_shape)
            else:
                shape = Wall(gray, path, scale, info, **shared).shape

        if floorplan.rooms:
            if shape is not None:
                new_shape = Room(gray, path, scale, info, **shared).shape
                shape = validate_shape(shape, new_shape)
            else:
                shape = Room(gray, path, scale, info, **shared).shape

        if floorplan.windows:
            Window(gray, path, floorplan.image_path, scale_factor, scale, info, **shared)

        if floorplan.doors:
            Door(gray, path, floorplan.image_path, scale_factor, scale, info, **shared)

    generate_transform_file(
        floorplan.image_path,
        path,
        info,
        floorplan.position,
        world_position,
        floorplan.rotation,
        world_rotation,
        scale,
        shape,
        path,
        origin_path,
    )

    if floorplan.position is not None:
        shape = [
            world_direction * shape[0] + floorplan.position[0] + world_position[0],
            world_direction * shape[1] + floorplan.position[1] + world_position[1],
            world_direction * shape[2] + floorplan.position[2] + world_position[2],
        ]

    if shape is None:
        shape = [0, 0, 0]

    return path, shape


def validate_shape(old_shape: List[float], new_shape: List[float]) -> List[float]:
    """
    Merge two bounding shapes, keeping the maximum extent on each axis.

    @Param old_shape: previous [x, y, z] extents
    @Param new_shape: new [x, y, z] extents
    @Return: combined [x, y, z] extents
    """
    return [
        max(old_shape[0], new_shape[0]),
        max(old_shape[1], new_shape[1]),
        max(old_shape[2], new_shape[2]),
    ]


def generate_transform_file(
    img_path: str,
    path: str,
    info: bool,
    position: Optional[np.ndarray],
    world_position: np.ndarray,
    rotation: Optional[np.ndarray],
    world_rotation: np.ndarray,
    scale: Optional[List[float]],
    shape: Optional[List[float]],
    data_path: str,
    origin_path: str,
) -> Dict[str, Any]:
    """
    Generate and persist transform metadata (position, rotation, scale, shape).

    @Param img_path: source image path
    @Param info: if True, log output
    @Param position: local position vector
    @Param world_position: global position offset
    @Param rotation: local rotation vector
    @Param world_rotation: global rotation offset
    @Param scale: scale vector
    @Param shape: bounding shape
    @Param data_path: path to generated data
    @Param origin_path: path to original data
    @Return: transform dictionary
    """
    # create map
    transform = {}
    if position is None:
        transform[const.STR_POSITION] = np.array([0, 0, 0])
    else:
        transform[const.STR_POSITION] = position + world_position

    if scale is None:
        transform["scale"] = np.array([1, 1, 1])
    else:
        transform["scale"] = scale

    if rotation is None:
        transform[const.STR_ROTATION] = np.array([0, 0, 0])
    else:
        transform[const.STR_ROTATION] = rotation + world_rotation

    if shape is None:
        transform[const.STR_SHAPE] = np.array([0, 0, 0])
    else:
        transform[const.STR_SHAPE] = shape

    transform[const.STR_IMAGE_PATH] = img_path

    transform[const.STR_ORIGIN_PATH] = origin_path

    transform[const.STR_DATA_PATH] = data_path

    IO.save_to_file(path + "transform", transform, info)

    return transform
