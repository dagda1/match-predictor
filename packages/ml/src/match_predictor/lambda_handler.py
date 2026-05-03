import os
from pathlib import Path

import joblib

from match_predictor.data import load_matches_from_db
from match_predictor.db import create_db_engine
from match_predictor.generate_predictions import generate as generate_predictions
from match_predictor.generate_upcoming import generate as generate_upcoming
from match_predictor.persistence import write_predictions, write_team_features, write_upcoming

MODEL_PATH = Path(os.environ["MODEL_PATH"])


def save_model(model) -> None:
    joblib.dump(model, MODEL_PATH)


def handler(_event, _context):
    engine = create_db_engine()
    df = load_matches_from_db(engine)

    write_team_features(engine, df)

    generate_predictions(
        lambda: df,
        lambda predictions: write_predictions(engine, predictions),
        save_model,
    )
    generate_upcoming(
        lambda: df,
        lambda predictions: write_upcoming(engine, predictions),
    )
