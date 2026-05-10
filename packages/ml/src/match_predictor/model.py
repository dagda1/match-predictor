from dataclasses import dataclass, field
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from match_predictor.features import build_feature_row, build_training_data
from match_predictor.grid import (
    build_grid,
    outcome_probs_from_grid,
    top_scorelines_from_grid,
)


@dataclass
class Prediction:
    home_win: float
    draw: float
    away_win: float
    scorelines: list[dict]


@dataclass
class TrainedModel:
    home_goals_regressor: HistGradientBoostingRegressor
    away_goals_regressor: HistGradientBoostingRegressor
    df: pd.DataFrame
    rho: float = 0.0
    feature_names: list[str] = field(default_factory=list)


def train(df: pd.DataFrame, rho: float = 0.0) -> TrainedModel:
    X, y_home, y_away = build_training_data(df)

    home_reg = HistGradientBoostingRegressor(
        loss="poisson",
        max_iter=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    home_reg.fit(X, y_home)

    away_reg = HistGradientBoostingRegressor(
        loss="poisson",
        max_iter=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    away_reg.fit(X, y_away)

    return TrainedModel(
        home_goals_regressor=home_reg,
        away_goals_regressor=away_reg,
        df=df,
        rho=rho,
        feature_names=list(X.columns),
    )


def save_model(model: TrainedModel, path: Path) -> None:
    joblib.dump(model, path)


def load_model(path: Path) -> TrainedModel:
    return joblib.load(path)


def _grid_for(model: TrainedModel, X: pd.DataFrame):
    lambda_home = float(model.home_goals_regressor.predict(X)[0])
    lambda_away = float(model.away_goals_regressor.predict(X)[0])
    return build_grid(lambda_home, lambda_away, rho=model.rho)


def outcome_probabilities(
    model: TrainedModel, X: pd.DataFrame,
) -> tuple[float, float, float]:
    return outcome_probs_from_grid(_grid_for(model, X))


def scoreline_probabilities(
    model: TrainedModel, X: pd.DataFrame, n: int = 10,
) -> list[dict]:
    return top_scorelines_from_grid(_grid_for(model, X), n=n)


def predict_match(
    model: TrainedModel,
    home_team: str,
    away_team: str,
) -> Prediction:
    features = build_feature_row(model.df, pd.Timestamp.now(), home_team, away_team)
    if features is None:
        raise ValueError(f"not enough match history for {home_team} or {away_team}")

    X = pd.DataFrame([features])
    grid = _grid_for(model, X)
    home_win, draw, away_win = outcome_probs_from_grid(grid)

    return Prediction(
        home_win=home_win,
        draw=draw,
        away_win=away_win,
        scorelines=top_scorelines_from_grid(grid, n=10),
    )
