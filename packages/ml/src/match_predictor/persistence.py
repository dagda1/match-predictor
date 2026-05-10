from datetime import datetime

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from match_predictor.db_models import Prediction, TeamFeatures, Upcoming
from match_predictor.features import WINDOWS, _home_advantage, _rolling_stats


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _to_prediction_row(item: dict) -> Prediction:
    ml = item["ml"]
    poisson = item["poisson"]
    ml_top = ml["topScore"]
    poisson_top = poisson["topScore"]

    return Prediction(
        home_team=item["homeTeam"],
        away_team=item["awayTeam"],
        date=_parse_date(item["date"]),
        actual_home_goals=item["actualHomeGoals"],
        actual_away_goals=item["actualAwayGoals"],
        actual_outcome=item["actualOutcome"],
        ml_home_win=ml["homeWin"],
        ml_draw=ml["draw"],
        ml_away_win=ml["awayWin"],
        ml_predicted_outcome=ml["predictedOutcome"],
        ml_correct=ml["correct"],
        ml_top_home_goals=ml_top["homeGoals"],
        ml_top_away_goals=ml_top["awayGoals"],
        ml_top_probability=ml_top["probability"],
        poisson_home_win=poisson["homeWin"],
        poisson_draw=poisson["draw"],
        poisson_away_win=poisson["awayWin"],
        poisson_predicted_outcome=poisson["predictedOutcome"],
        poisson_correct=poisson["correct"],
        poisson_home_lambda=poisson["homeLambda"],
        poisson_away_lambda=poisson["awayLambda"],
        poisson_top_home_goals=poisson_top["homeGoals"],
        poisson_top_away_goals=poisson_top["awayGoals"],
        poisson_top_probability=poisson_top["probability"],
    )


def _to_upcoming_row(item: dict) -> Upcoming:
    ml = item["ml"]
    poisson = item["poisson"]
    ml_top = ml["topScore"]
    poisson_top = poisson["topScore"]

    return Upcoming(
        home_team=item["homeTeam"],
        away_team=item["awayTeam"],
        date=_parse_date(item["date"]),
        ml_home_win=ml["homeWin"],
        ml_draw=ml["draw"],
        ml_away_win=ml["awayWin"],
        ml_predicted_outcome=ml["predictedOutcome"],
        ml_top_home_goals=ml_top["homeGoals"],
        ml_top_away_goals=ml_top["awayGoals"],
        ml_top_probability=ml_top["probability"],
        poisson_home_win=poisson["homeWin"],
        poisson_draw=poisson["draw"],
        poisson_away_win=poisson["awayWin"],
        poisson_predicted_outcome=poisson["predictedOutcome"],
        poisson_home_lambda=poisson["homeLambda"],
        poisson_away_lambda=poisson["awayLambda"],
        poisson_top_home_goals=poisson_top["homeGoals"],
        poisson_top_away_goals=poisson_top["awayGoals"],
        poisson_top_probability=poisson_top["probability"],
    )


def write_predictions(engine: Engine, predictions: list[dict]) -> None:
    session = Session(engine)
    session.query(Prediction).delete()
    session.add_all(_to_prediction_row(item) for item in predictions)
    session.commit()
    session.close()


def write_upcoming(engine: Engine, predictions: list[dict]) -> None:
    session = Session(engine)
    session.query(Upcoming).delete()
    session.add_all(_to_upcoming_row(item) for item in predictions)
    session.commit()
    session.close()


def _team_feature_row(team: str, stats: dict, home_advantage: float) -> TeamFeatures:
    return TeamFeatures(
        team_name=team,
        xg_for_avg=float(stats["xgForAvg"]),
        xg_against_avg=float(stats["xgAgainstAvg"]),
        xg_overperformance=float(stats["xgOverperformance"]),
        shot_conversion=float(stats["shotConversion"]),
        sot_pct=float(stats["sotPct"]),
        ppda=float(stats["ppda"]),
        deep_avg=float(stats["deepAvg"]),
        goals_for_avg=float(stats["goalsForAvg"]),
        goals_against_avg=float(stats["goalsAgainstAvg"]),
        home_advantage=float(home_advantage),
    )


def write_team_features(engine: Engine, df: pd.DataFrame) -> None:
    cutoff = df["date"].max() + pd.Timedelta(days=1)
    home_advantage = _home_advantage(df)

    teams = sorted(set(df["homeTeam"]) | set(df["awayTeam"]))
    rows: list[TeamFeatures] = []

    for team in teams:
        stats = _rolling_stats(df, team, cutoff, n=WINDOWS[0])
        if not stats:
            continue
        rows.append(_team_feature_row(team, stats, home_advantage))

    session = Session(engine)
    session.query(TeamFeatures).delete()
    session.add_all(rows)
    session.commit()
    session.close()
