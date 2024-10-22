"""Script for running the simulation."""

import argparse
import os
import shutil
import subprocess
import sys

import foampy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--turbulence-model",
        choices=["laminar", "k-epsilon", "k-omega"],
        default="k-epsilon",
    )
    parser.add_argument(
        "--overwrite", "-f", action="store_true", default=False
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        default=False,
        help="Do not create a new directory for this case.",
    )
    args = parser.parse_args()
    ny = 40
    case_name = f"{args.turbulence_model}"
    if not args.in_place:
        case_dir = os.path.join("cases", case_name)
    else:
        case_dir = "."
    # Copy case files into a case directory, deleting anything that might
    # exist
    # If the case has already been run, we should see it in the results, or
    # maybe we should use DVC to sort this out
    if (
        not args.overwrite
        and not args.in_place
        and os.path.isdir(case_dir)
        and os.listdir(case_dir)
    ):
        print("Case directory is not empty; exiting")
        sys.exit(0)
    if args.overwrite and not args.in_place and os.path.isdir(case_dir):
        # Delete the case and recreate from scratch
        shutil.rmtree(case_dir)
    if not os.path.isdir(case_dir):
        print(f"Creating case directory {case_dir}")
    nx_base = [6, 350, 20, 20, 8]
    ny_base = 40
    nx = [int(x * ny / ny_base) for x in nx_base]
    os.makedirs(case_dir, exist_ok=True)
    system_dir = os.path.join(case_dir, "system")
    os.makedirs(system_dir, exist_ok=True)
    blockmeshdict_fpath = os.path.join(system_dir, "blockMeshDict")
    foampy.fill_template(
        "system/blockMeshDict.template", blockmeshdict_fpath, nx=nx, ny=ny
    )
    model_names = {
        "k-epsilon": "kEpsilon",
        "laminar": "kEpsilon",
        "k-omega": "kOmega",
    }
    constant_dir = os.path.join(case_dir, "constant")
    os.makedirs(constant_dir, exist_ok=True)
    foampy.fill_template(
        "constant/turbulenceProperties.template",
        os.path.join(constant_dir, "turbulenceProperties"),
        turbulence_model=model_names[args.turbulence_model],
        turbulence_on="off" if args.turbulence_model == "laminar" else "on",
        simulation_type=(
            "laminar" if args.turbulence_model == "laminar" else "RAS"
        ),
    )
    if not args.in_place:
        shutil.copytree("0", os.path.join(case_dir, "0"))
        # All other non template files to copy over
        paths = [
            "constant/transportProperties",
            "system/controlDict",
            "system/fvSchemes",
            "system/fvSolution",
            "system/sample",
        ]
        for path in paths:
            shutil.copy(path, os.path.join(case_dir, path))
    # Move into the case directory
    print(f"Changing working directory to {case_dir}")
    os.chdir(case_dir)
    # Create the mesh
    foampy.run("blockMesh", overwrite=args.overwrite)
    # Run simpleFoam
    foampy.run(
        "simpleFoam",
        overwrite=args.overwrite,
    )
    # Post-process
    foampy.run(
        "postProcess",
        args=["-latestTime", "-func", "sample"],
        overwrite=args.overwrite,
    )
    # Touch case.foam file so we can easily open with ParaView
    subprocess.call(["touch", "case.foam"])
