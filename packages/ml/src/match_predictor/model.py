from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.ensemble import HistGradientBoostingRegressor

from match_predictor.features import build_feature_row, build_training_data
from match_predictor.grid import (
    MAX_GOALS,
    build_grid,
    outcome_probs_from_grid,
    top_scorelines_from_grid,
)


RHO_UPPER = 0.05


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


def train(df: pd.DataFrame) -> TrainedModel:
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

    rho = _fit_rho(
        home_reg.predict(X),
        away_reg.predict(X),
        y_home.to_numpy(),
        y_away.to_numpy(),
    )

    return TrainedModel(
        home_goals_regressor=home_reg,
        away_goals_regressor=away_reg,
        df=df,
        rho=rho,
        feature_names=list(X.columns),
    )


def _fit_rho(
    home_lambdas: np.ndarray,
    away_lambdas: np.ndarray,
    actual_home: np.ndarray,
    actual_away: np.ndarray,
) -> float:
    capped_home = np.minimum(actual_home.astype(int), MAX_GOALS)
    capped_away = np.minimum(actual_away.astype(int), MAX_GOALS)

    max_lambda = float(max(home_lambdas.max(), away_lambdas.max()))
    safe_lower = -1.0 / max_lambda + 1e-3

    def negative_log_likelihood(rho: float) -> float:
        total = 0.0
        for lh, la, kh, ka in zip(home_lambdas, away_lambdas, capped_home, capped_away):
            grid = build_grid(float(lh), float(la), rho=rho)
            p = grid[kh, ka]
            if p <= 0.0:
                return float("inf")
            total += float(np.log(p))
        return -total

    result = minimize_scalar(
        negative_log_likelihood,
        bounds=(safe_lower, RHO_UPPER),
        method="bounded",
    )
    return float(result.x)


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
