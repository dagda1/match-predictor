import json
from pathlib import Path

import pandas as pd
from sqlalchemy.engine import Engine

DATA_DIR = Path(__file__).resolve().parents[3] / "etl" / "data"

DB_TO_DATAFRAME_COLUMNS = {
    "id": "id",
    "date": "date",
    "season": "season",
    "home_team": "homeTeam",
    "away_team": "awayTeam",
    "home_goals": "homeGoals",
    "away_goals": "awayGoals",
    "home_xg": "homeXg",
    "away_xg": "awayXg",
    "home_shots": "homeShots",
    "away_shots": "awayShots",
    "home_shots_on_target": "homeShotsOnTarget",
    "away_shots_on_target": "awayShotsOnTarget",
    "home_deep": "homeDeep",
    "away_deep": "awayDeep",
    "home_ppda": "homePpda",
    "away_ppda": "awayPpda",
    "home_win_prob": "homeWinProb",
    "draw_prob": "drawProb",
    "away_win_prob": "awayWinProb",
}


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
        f = open(path)
        matches = json.load(f)
        f.close()
        frames.append(pd.DataFrame(matches))

    return to_match_dataframe(frames)


def load_matches_from_db(engine: Engine) -> pd.DataFrame:
    db_columns = list(DB_TO_DATAFRAME_COLUMNS.keys())
    query = f"SELECT {', '.join(db_columns)} FROM matches ORDER BY date"
    df = pd.read_sql(query, engine)
    df = df.rename(columns=DB_TO_DATAFRAME_COLUMNS)
    return to_match_dataframe([df])


def format_date(dt: pd.Timestamp) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")
