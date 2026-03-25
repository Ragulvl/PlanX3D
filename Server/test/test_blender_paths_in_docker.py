from subprocess import check_output
import os
import sys

"""
FloorplanToBlender3d
Copyright (C) 2021 Daniel Westberg
"""

sys.path.insert(0, "../..")
from FloorplanToBlenderLib import *  # floorplan to blender lib


if __name__ == "__main__":

    # Debug print
    print(
        str(
            check_output(
                [
                    "/usr/local/blender/blender",
                    "-noaudio",
                    "--background",
                    "--python",
                    "../Blender/build_3d_scene.py",
                    "/home/floorplan_to_blender/Server/",
                    "storage/objects/" + str(sys.argv[1]) + ".blend",
                    "storage/data/" + str(sys.argv[1]) + "0/",
                ]
            )
        )
    )

    # Create blender project
    check_output(
        [
            "/usr/local/blender/blender",
            "-noaudio",
            "--background",
            "--python",
            "../Blender/build_3d_scene.py",
            "/home/floorplan_to_blender/Server/",
            "storage/objects/" + str(sys.argv[1]) + ".blend",
            "storage/data/" + str(sys.argv[1]) + "0/",
        ]
    )
