"""
PlanX3D CLI Pipeline
Interactive command-line entry point for converting 2D floorplan images
into 3D Blender projects. Supports single floorplans, config-based
batches, and stacking files.
"""

from subprocess import check_output
from FloorplanToBlenderLib import (
    IO,
    config,
    const,
    execution,
    dialog,
    floorplan,
    stacking,
)

import os


def create_blender_project(
    data_paths,
    blender_install_path,
    target_folder,
    blender_script_path,
    program_path,
):
    """Build a Blender .blend project from pre-generated data files."""
    if not os.path.exists("." + target_folder):
        os.makedirs("." + target_folder)

    target_base = target_folder + const.TARGET_NAME
    target_path = target_base + const.BASE_FORMAT
    target_path = (
        IO.get_next_target_base_name(target_base, target_path) + const.BASE_FORMAT
    )

    check_output(
        [
            blender_install_path,
            "-noaudio",
            "--background",
            "--python",
            blender_script_path,
            program_path,
            target_path,
        ]
        + data_paths
    )

    outformat = config.get(
        const.SYSTEM_CONFIG_FILE_NAME, "SYSTEM", const.STR_OUT_FORMAT
    ).replace('"', "")

    if outformat != ".blend":
        check_output(
            [
                blender_install_path,
                "-noaudio",
                "--background",
                "--python",
                "./Blender/export_format_converter.py",
                "." + target_path,
                outformat,
                target_base + outformat,
            ]
        )
        print("Object created at:" + program_path + target_base + outformat)

    print("Project created at: " + program_path + target_path)


def main():
    """Interactive CLI workflow: configure Blender, select images, generate 3D."""
    blender_install_path = ""
    data_folder = const.BASE_PATH
    target_folder = const.TARGET_PATH
    blender_install_path = config.get_default_blender_installation_path()
    floorplans = []
    program_path = os.path.dirname(os.path.realpath(__file__))
    blender_script_path = const.BLENDER_SCRIPT_PATH
    dialog.init()
    data_paths = list()

    auto_blender_install_path = IO.blender_installed()

    if auto_blender_install_path is not None:
        blender_install_path = auto_blender_install_path

    var = input(
        "Please enter your blender installation path [default = "
        + blender_install_path
        + "]: "
    )
    if var:
        blender_install_path = var

    var = input(
        "Do you want to build from StackingFile or ConfigFile list ? [default = ConfigFile]: "
    )
    if var in ["N", "n", "StackingFile", "stacking", "stackingfile"]:
        stacking_def_path = "./Stacking/all_separated_example.txt"
        var = input(f"Enter path to Stacking file : [default = {stacking_def_path}]: ")
        if var:
            stacking_def_path = var
        data_paths = stacking.parse_stacking_file(stacking_def_path)

        print("")
        var = input(
            "This program is about to run and create blender3d project, continue? : "
        )
        if var:
            print("Program stopped.")
            exit(0)

    else:

        config_path = "./Configs/default.ini"
        var = input(
            "Use default config or import from file paths separated by space [default = "
            + config_path
            + "]: "
        )

        if var:
            config_path = var
            floorplans.append(
                floorplan.new_floorplan(c) for c in config_path.split(" ")
            )

        else:
            floorplans.append(floorplan.new_floorplan(config_path))

        var = input("Do you want to set images to use in each config file? [N/y]: ")
        if var in ["y", "Y"]:
            for fp in floorplans:
                var = input(
                    "For config file "
                    + fp.conf
                    + " write path for image to use "
                    + "[Default="
                    + fp.image_path
                    + "]:"
                )
                if var:
                    fp.image_path = var
        print("")
        var = input(
            "This program is about to run and create blender3d project, continue? : "
        )
        if var:
            print("Program stopped.")
            exit(0)

        print("")
        print("Generate datafiles in folder: Data")
        print("")
        print("Clean datafiles")

        print("")
        var = input("Clear all cached data before run: [default = yes] : ")

        if not var or var.lower() == "yes" or var.lower() == "y":
            IO.clean_data_folder(data_folder)

        if len(floorplans) > 1:
            data_paths.append(execution.simple_single(f) for f in floorplans)
        else:
            data_paths = [execution.simple_single(floorplans[0])]

    print("")
    print("Creates blender project")
    print("")

    if isinstance(data_paths[0], list):
        for paths in data_paths:
            create_blender_project(
                paths, blender_install_path, target_folder,
                blender_script_path, program_path,
            )
    else:
        create_blender_project(
            data_paths, blender_install_path, target_folder,
            blender_script_path, program_path,
        )

    print("")
    print("Done, Have a nice day!")


if __name__ == "__main__":
    main()
