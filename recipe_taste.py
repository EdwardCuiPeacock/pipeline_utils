#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 12:42:22 2021

@author: edwardcui
"""

import os
import argparse
import subprocess

from recipe_utils import get_metadata, get_config, run_shell_command

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "metadata_yaml",
    type=str,
    help="Path to metadata.yaml file",
)
parser.add_argument(
    "-t",
    "--type",
    type=str,
    help="Recipe type, either tfx [default] or zenml",
    choices=["tfx", "zenml", "auto"],
    default="tfx",
    dest="pipeline_type",
)
parser.add_argument(
    "--update",
    action="store_true",
    dest="update_pipeline",
)


def set_tfx_environments(pipeline_path):
    """Set up the local environments."""
    # pip install -r requirements.txt
    print("Installing requirements.txt")
    returncode, _ = run_shell_command(
        ["pip", "install", "--user", "-r", os.path.join(pipeline_path, "requirements.txt")],
        verbose=True,
    )
    if returncode == 0:
        print("Successfully installed requirements.txt")
    else:
        raise (Exception("requirements.txt not successfully installed"))

    # Add the bin path to the running directory
    bin_path = os.path.realpath(os.path.join(pipeline_path, "bin"))
    if bin_path not in os.environ["PATH"].split(":"):
        os.environ["PATH"] += f":{bin_path}"


def parse_tfx_run_output(stdout):
    return {"asf": 1}


def taste_tfx_recipe(metadata_yaml, update=False, engine="kubeflow"):
    # Get the path of the pipeline
    pipeline_path = os.path.dirname(metadata_yaml)

    # Set some envrionments
    if not update:
        set_tfx_environments(pipeline_path)

    # Get some global variables
    metadata = get_metadata(metadata_yaml)
    PIPELINE_NAME = metadata["pipeline_name"]
    system_config = get_config(metadata, "system_configurations")
    CUSTOM_TFX_IMAGE = (
        "gcr.io/" + system_config["GOOGLE_CLOUD_PROJECT"] + "/" + system_config["TFX_IMAGE_REPO_NAME"]
    )
    ENDPOINT = system_config["ENDPOINT"]
    KUBEFLOW_RUNNER = os.path.join(pipeline_path, system_config["KUBEFLOW_RUNNER"])

    # Prepare the pipeline running commands
    if update:
        # Update the pipeline
        init_command = [
            "tfx",
            "pipeline",
            "update",
            f"--pipeline-path={KUBEFLOW_RUNNER}",
            f"--endpoint={ENDPOINT}",
            f"--engine={engine}",
        ]
    else:
        # Create the pipeline
        init_command = [
            "tfx",
            "pipeline",
            "create",
            f"--pipeline-path={KUBEFLOW_RUNNER}",
            f"--endpoint={ENDPOINT}",
            f"--engine={engine}" f"--build-target-image={CUSTOM_TFX_IMAGE}",
        ]

    # Run the pipeline
    run_command = [
        "tfx",
        "run",
        "create",
        f"--pipeline-name={PIPELINE_NAME}",
        f"--endpoint={ENDPOINT}",
    ]

    # Execute the pipeline
    run_shell_command(init_command, verbose=True)
    _, stdout = run_shell_command(run_command, verbose=True)

    # Parse outputs
    parsed_outputs = parse_tfx_run_output(stdout)
    print(parsed_outputs)


def taste_zenml_recipe(metadata_yaml, update=False):
    pass


if __name__ == "__main__":
    metadata_yaml = (
        "/Users/edwardcui/Documents/Scripts/pipeline_utils/tfx_template/metadata.yaml"
    )
    taste_tfx_recipe(metadata_yaml)

if __name__ == "__main__2":
    args = parser.parse_args()
    print(args.__dict__)
    if args.pipeline_type == "tfx":
        taste_tfx_recipe(args.metadata_yaml, args.update_pipeline)
    elif args.pipeline_type == "zenml":
        taste_zenml_recipe(args.metadata_yaml, args.update_pipeline)
    elif args.pipeline_type == "auto":
        # auto detect pipeline type based on structure
        raise (
            NotImplementedError(
                f"Taste for pipeline type '{args.pipeline_type}' is not implemented"
            )
        )
    else:
        raise (
            NotImplementedError(
                f"Taste for pipeline type '{args.pipeline_type}' is not implemented"
            )
        )
