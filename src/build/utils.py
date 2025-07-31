"""
Utilities for creating result directories and exporting configurations
for Retinotectal Projection simulations.

This module provides two main functions:

- create_simulation_folder(): Creates a timestamped, branch-specific results folder and updates
                              cfg.current_config with its path.

- write_config_to_text(folder_path): Writes the key/value pairs from cfg.current_config into a 'config.txt'.
- build_gc_mask(radius): Creates a mask to calculate gc discretely
"""

import os
import build.config as cfg
import datetime
import subprocess
import numpy as np


def create_simulation_folder():
    """
    Create a structured results directory for the current simulation run.

    The resulting path has the form:
      <repo_root>/../Retinotectal_Results/<git_branch>/<cfg.FOLDER_PATH>/<cfg.FOLDER_NAME or timestamp>/

    Steps:
    1. Determine repository root (three levels up from this file -> One level above the repo).
    2. Append 'Retinotectal_Results' and current Git branch name.
    3. Incorporate user-specified subpath from cfg.current_config[FOLDER_PATH].
    4. Use cfg.current_config[FOLDER_NAME] or generate a timestamp.
    5. Create the directory (exist_ok=True).
    6. Update cfg.current_config[FOLDER_PATH] to the new absolute path.

    Returns:
        str: Absolute path to the newly created results folder.

    Raises:
        subprocess.CalledProcessError: If the Git command fails.
    """
    # Create path outside of repository
    basedir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            os.pardir
        )
    )
    results_dir = os.path.join(basedir, "Retinotectal_Results")

    # Read current branch name
    branch = (
        subprocess
        .check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .strip()
        .decode("utf-8")
    )

    # Add branch-specific name to path
    results_dir = os.path.join(results_dir, branch)

    # Add in config specified folder path to path
    existing_subpath = cfg.current_config.get(cfg.FOLDER_PATH, "")
    target_base = os.path.join(results_dir, existing_subpath)

    # If no folder name is specified in config use a timestamp
    if cfg.current_config[cfg.FOLDER_NAME] != "":
        folder_name = cfg.current_config[cfg.FOLDER_NAME]
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"simulation_run_{timestamp}"
    new_folder_path = os.path.join(target_base, folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    cfg.current_config[cfg.FOLDER_PATH] = new_folder_path
    return new_folder_path


def write_config_to_text(folder_path):
    """
    Write the current configuration to a 'config.txt' file in the specified folder.

    Each line in the file has the format:
        key: value

    Args:
        folder_path (str): Path to the folder where 'config.txt' will be created.
    """

    file_path = os.path.join(folder_path, "config.txt")
    with open(file_path, 'w') as f:
        for key, value in cfg.current_config.items():
            f.write(f"{key}: {value}\n")


def build_gc_mask(radius: int) -> np.ndarray:
    """ build a mask to project growth cones on a discrete coordinate system

    Args:
        radius: radius of the growth cone.

    Returns:
        mask: array of True and False values to determine, where growth cones are projected on
    """
    coords = np.arange(-radius, radius + 1)
    X, Y = np.meshgrid(coords, coords, indexing='ij')
    mask = (X**2 + Y**2) <= radius**2
    return mask
