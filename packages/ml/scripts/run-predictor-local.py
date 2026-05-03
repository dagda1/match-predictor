import os
from pathlib import Path

import joblib

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_USER", "match_predictor_app")
os.environ.setdefault("DB_PASSWORD", "app")
os.environ.setdefault("DB_NAME", "match_predictor")
os.environ.setdefault("DB_SSLMODE", "disable")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-west-2")

from match_predictor.data import load_matches_from_db
from match_predictor.db import create_db_engine
from match_predictor.generate_predictions import generate as generate_predictions
from match_predictor.generate_upcoming import generate as generate_upcoming
from match_predictor.persistence import write_predictions, write_upcoming

MODEL_PATH = Path(__file__).resolve().parents[1] / "local-model.joblib"


def save_model_local(model) -> None:
    joblib.dump(model, MODEL_PATH)
    print(f"saved model to {MODEL_PATH}")


engine = create_db_engine()

print("=== generate_predictions ===")
generate_predictions(
    lambda: load_matches_from_db(engine),
    lambda predictions: write_predictions(engine, predictions),
    save_model_local,
)

print("\n=== generate_upcoming ===")
generate_upcoming(
    lambda: load_matches_from_db(engine),
    lambda predictions: write_upcoming(engine, predictions),
)
