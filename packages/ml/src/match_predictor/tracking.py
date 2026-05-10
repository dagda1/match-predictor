from pathlib import Path

import mlflow

REPO_ROOT = Path(__file__).resolve().parents[4]
TRACKING_URI = f"file://{REPO_ROOT}/mlruns"
EXPERIMENT_NAME = "match-predictor"


def configure() -> None:
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
