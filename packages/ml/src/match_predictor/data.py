import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[3] / "etl" / "data"


def to_match_dataframe(frames: list[pd.DataFrame]) -> pd.DataFrame:
    df = pd.concat(frames, ignore_index=True)

    numeric_cols = [
        "homeGoals", "awayGoals",
        "homeXg", "awayXg",
        "homeShots", "awayShots",
        "homeShotsOnTarget", "awayShotsOnTarget",
        "homeDeep", "awayDeep",
        "homePpda", "awayPpda",
        "homeWinProb", "drawProb", "awayWinProb",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


def load_matches() -> pd.DataFrame:
    frames = []
    for path in sorted(DATA_DIR.glob("matches-*.json")):
        with open(path) as f:
            matches = json.load(f)
        frames.append(pd.DataFrame(matches))

    return to_match_dataframe(frames)


def format_date(dt: pd.Timestamp) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")
