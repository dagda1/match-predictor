import os
from pathlib import Path

import mlflow

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_TRACKING_URI = f"file://{REPO_ROOT}/mlruns"
TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", DEFAULT_TRACKING_URI)
EXPERIMENT_NAME = "match-predictor"


def configure() -> None:
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
