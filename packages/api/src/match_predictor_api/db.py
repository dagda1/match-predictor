import os

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from match_predictor.db_models import Match

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


def get_session() -> Session:
    return Session(engine)


def load_matches_dataframe() -> pd.DataFrame:
    session = get_session()
    rows = session.execute(select(Match).order_by(Match.date)).scalars().all()
    session.close()

    return pd.DataFrame([{
        "homeTeam": r.home_team,
        "awayTeam": r.away_team,
        "date": r.date,
        "homeGoals": r.home_goals,
        "awayGoals": r.away_goals,
        "homeXg": r.home_xg,
        "awayXg": r.away_xg,
        "homeShots": r.home_shots,
        "awayShots": r.away_shots,
        "homeShotsOnTarget": r.home_shots_on_target,
        "awayShotsOnTarget": r.away_shots_on_target,
        "homeDeep": r.home_deep,
        "awayDeep": r.away_deep,
        "homePpda": r.home_ppda,
        "awayPpda": r.away_ppda,
    } for r in rows])
