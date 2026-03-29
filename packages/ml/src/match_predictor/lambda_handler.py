import json
import os

import boto3
import pandas as pd

from match_predictor.data import to_match_dataframe
from match_predictor.generate_predictions import generate as generate_predictions
from match_predictor.generate_upcoming import generate as generate_upcoming

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
SEASONS = ["2024", "2025"]


def load_matches_from_s3() -> pd.DataFrame:
    frames = []
    for season in SEASONS:
        key = f"matches/matches-{season}.json"
        body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode()
        rows = [json.loads(line) for line in body.strip().split("\n") if line]
        frames.append(pd.DataFrame(rows))

    return to_match_dataframe(frames)


def write_predictions_to_s3(predictions: list[dict]) -> None:
    body = "\n".join(json.dumps(row) for row in predictions)
    s3.put_object(Bucket=BUCKET, Key="predictions/predictions-2026.json", Body=body)


def write_upcoming_to_s3(predictions: list[dict]) -> None:
    body = "\n".join(json.dumps(row) for row in predictions)
    s3.put_object(Bucket=BUCKET, Key="upcoming/upcoming.json", Body=body)


def save_model_to_s3(model) -> None:
    import tempfile
    import joblib
    with tempfile.NamedTemporaryFile(suffix=".joblib") as tmp:
        joblib.dump(model, tmp.name)
        tmp.seek(0)
        s3.put_object(Bucket=BUCKET, Key="model/model.joblib", Body=tmp.read())


def handler(_event, _context):
    generate_predictions(load_matches_from_s3, write_predictions_to_s3, save_model_to_s3)
    generate_upcoming(load_matches_from_s3, write_upcoming_to_s3)
