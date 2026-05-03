from datetime import datetime

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from match_predictor.db_models import Prediction, Upcoming


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
