#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 13:18:03 2021

Initialize the tree of TFX pipeline

.
├── Dockerfile
├── __init__.py
├── build.yaml
├── data
│   └── data.csv
├── data_validation.ipynb
├── kubeflow_runner.py: define runners for each orchestration engine
├── kubeflow_v2_dag_runner.py: define runners for each orchestration engine
├── local_runner.py: define runners for each orchestration engine
├── model_analysis.ipynb
├── models: This directory contains ML model definitions
│   ├── __init__.py
│   ├── estimator: This directory contains an Estimator based model
│   │   ├── __init__.py
│   │   ├── constants.py: defines constants of the model
│   │   ├── model.py: defines DNN model using TF estimator
│   │   └── model_test.py: defines DNN model using TF estimator
│   ├── keras: This directory contains a Keras based model.
│   │   ├── __init__.py
│   │   ├── constants.py: defines constants of the model
│   │   ├── model.py: defines DNN model using TF estimator
│   │   └── model_test.py: defines DNN model using TF estimator
│   ├── features.py: defines features for the model
│   ├── features_test.py: defines features for the model
│   ├── preprocessing.py: defines preprocessing jobs using tf::Transform
│   └── preprocessing_test.py: defines preprocessing jobs using tf::Transform
├── my_pipeline.tar.gz: {pipeline_name} tar ball
└── pipeline: This directory contains the definition of the pipeline
    ├── __init__.py
    ├── configs.py: defines common constants for pipeline runners
    └── pipeline.py: defines TFX components and a pipeline


@author: edwardcui
"""

import os
import shutil
import re
import argparse
import urllib.request

from recipe_utils import run_shell_command

# Additional arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-n",
    "--name",
    type=str,
    help="Pipeline name",
    default="my_pipeline",
    dest="pipeline_name",
)
parser.add_argument(
    "-d",
    "--destination",
    type=str,
    help="Pipeline directory",
    default=".",
    dest="project_dir",
)
parser.add_argument(
    "-t",
    "--type",
    type=str,
    help="Recipe type, either tfx [default] or zenml",
    choices=["tfx", "zenml"],
    default="tfx",
    dest="pipeline_type",
)


def recipe_init(pipeline_name="my_pipeline", project_dir=".", pipeline_type="tfx"):
    """
    Initialize the pipeline project from a template.

    Parameters
    ----------
    pipeline_name : str, optional
        Pipeline name. The default is "my_pipeline".
    project_dir : str, optional
        Directory where the pipeline is created.
        The default is ".".
    pipeline_type : str, optional
        Pipeline type, either tfx or zenml.
        The default is tfx
    """
    # directories
    source_dir = os.path.join(os.path.dirname(__file__), f"{pipeline_type}_template")
    target_dir = os.path.realpath(
        os.path.abspath(os.path.join(project_dir, pipeline_name))
    )

    # Copy the template folder
    if not os.path.isdir(target_dir):
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    else:
        print("Pipeline folder exists.")

    # Change the pipeline name in the global variable in `config.py` file
    config_filepath = os.path.join(target_dir, "metadata.yaml")
    with open(config_filepath, "r") as forig:
        script_data = forig.read()  # read everything

    script_data = re.sub(
        r"pipeline_name: \w+", f"pipeline_name: {pipeline_name}", script_data
    )

    with open(config_filepath, "w") as fnew:
        fnew.write(script_data)

    # For TFX pipeline, also download the skaffold bin
    if pipeline_type == "tfx" and not os.path.isfile(os.path.join(target_dir, "bin", "skaffold")):
        print("Downloading 'skaffold'")
        save_path = os.path.join(target_dir, "bin")
        os.makedirs(save_path, exist_ok=True)
        urllib.request.urlretrieve("https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64",
            os.path.join(save_path, "skaffold")
        )

    print(f"Successfully initialized {pipeline_type.upper()} pipeline recipe.")    

if __name__ == "__main__":
    args = parser.parse_args()
    recipe_init(args.pipeline_name, args.project_dir, args.pipeline_type)
