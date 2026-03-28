import json
import os

import boto3
import pandas as pd

from match_predictor.data import to_match_dataframe
from match_predictor.generate_predictions import generate as generate_predictions
from match_predictor.generate_upcoming import generate as generate_upcoming

s3 = boto3.client("s3")
sns = boto3.client("sns")
BUCKET = os.environ["BUCKET_NAME"]
TOPIC_ARN = os.environ["TOPIC_ARN"]
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


def handler(_event, _context):
    predictions_summary = generate_predictions(load_matches_from_s3, write_predictions_to_s3)
    upcoming_summary = generate_upcoming(load_matches_from_s3, write_upcoming_to_s3)

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Predictions completed",
        Message=f"{predictions_summary}\n{upcoming_summary}",
    )
