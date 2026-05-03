import os
import tempfile

import boto3
import joblib

from match_predictor.data import load_matches_from_db
from match_predictor.db import create_db_engine
from match_predictor.generate_predictions import generate as generate_predictions
from match_predictor.generate_upcoming import generate as generate_upcoming
from match_predictor.persistence import write_predictions, write_upcoming

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]


def save_model_to_s3(model) -> None:
    tmp = tempfile.NamedTemporaryFile(suffix=".joblib", delete=False)
    joblib.dump(model, tmp.name)
    tmp.seek(0)
    s3.put_object(Bucket=BUCKET, Key="model/model.joblib", Body=tmp.read())
    tmp.close()
    os.unlink(tmp.name)


def handler(_event, _context):
    engine = create_db_engine()

    generate_predictions(
        lambda: load_matches_from_db(engine),
        lambda predictions: write_predictions(engine, predictions),
        save_model_to_s3,
    )
    generate_upcoming(
        lambda: load_matches_from_db(engine),
        lambda predictions: write_upcoming(engine, predictions),
    )
