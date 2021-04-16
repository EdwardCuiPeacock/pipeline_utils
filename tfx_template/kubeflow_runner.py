"""Define KubeflowDagRunner to run the pipeline using Kubeflow."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from absl import logging
from typing import Text, Optional


from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.proto import trainer_pb2
from tfx.utils import telemetry_utils

from utils.metadata_utils import get_metadata, get_config
from pipeline import pipeline


def run(metadata_file: Optional[Text] = None):
    """Define a kubeflow pipeline."""

    # Metadata config. The defaults works work with the installation of
    # KF Pipelines using Kubeflow. If installing KF Pipelines using the
    # lightweight deployment option, you may need to override the defaults.
    # If you use Kubeflow, metadata will be written to MySQL database inside
    # Kubeflow cluster.
    metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()

    # Load settings from metadata.yaml
    metadata = get_metadata(metadata_file)
    system_config = get_config(metadata, "system_configurations")
    model_config = get_config(metadata, "model_configurations")

    # This pipeline automatically injects the Kubeflow TFX image if the
    # environment variable 'KUBEFLOW_TFX_IMAGE' is defined. Currently, the tfx
    # cli tool exports the environment variable to pass to the pipelines.
    # TODO(b/157598477) Find a better way to pass parameters from CLI handler to
    # pipeline DSL file, instead of using environment vars.
    tfx_image = os.environ.get("KUBEFLOW_TFX_IMAGE", None)
    logging.info(f"Current tfx image used: {tfx_image}")

    runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
        kubeflow_metadata_config=metadata_config, tfx_image=tfx_image
    )
    pod_labels = kubeflow_dag_runner.get_default_pod_labels()
    pod_labels.update(
        {
            telemetry_utils.LABEL_KFP_SDK_ENV: metadata["pipeline_name"]
            + "_"
            + metadata["pipeline_version"]
        }
    )
    kubeflow_dag_runner.KubeflowDagRunner(
        config=runner_config, pod_labels_to_attach=pod_labels
    ).run(
        pipeline.create_pipeline(
            pipeline_name=metadata["pipeline_name"]
            + "_"
            + metadata["pipeline_version"],
            pipeline_root=system_config["PIPELINE_ROOT"],
            data_path=model_config["data_path"],
            # TODO(step 7): (Optional) Uncomment below to use BigQueryExampleGen.
            # query=model_config["query_script_path"],
            preprocessing_fn=system_config["preprocessing_fn"],
            run_fn=system_config["run_fn"],
            train_args=trainer_pb2.TrainArgs(num_steps=model_config["TRAIN_NUM_STEPS"]),
            eval_args=trainer_pb2.EvalArgs(num_steps=model_config["EVAL_NUM_STEPS"]),
            eval_accuracy_threshold=model_config["EVAL_ACCURACY_THRESHOLD"],
            serving_model_dir=system_config["MODEL_SERVE_DIR"],
            # TODO(step 7): (Optional) Uncomment below to use provide GCP related
            #               config for BigQuery with Beam DirectRunner.
            # beam_pipeline_args=system_config["BIG_QUERY_WITH_DIRECT_RUNNER_BEAM_PIPELINE_ARGS"]
            # TODO(step 8): (Optional) Uncomment below to use Dataflow.
            # beam_pipeline_args=system_config["DATAFLOW_BEAM_PIPELINE_ARGS"],
            # TODO(step 9): (Optional) Uncomment below to use Cloud AI Platform.
            # ai_platform_training_args=system_config["GCP_AI_PLATFORM_TRAINING_ARGS"],
            # TODO(step 9): (Optional) Uncomment below to use Cloud AI Platform.
            # ai_platform_serving_args=system_configs["GCP_AI_PLATFORM_SERVING_ARGS"],
            enable_cache=system_config["enable_cache"],
            system_config=system_config,  # passing config parameters downstream
            model_config=model_config,  # passing model parameters downstream
        )
    )


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    run()
