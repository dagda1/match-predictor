from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import poisson
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

    p_home_at_obs = poisson.pmf(capped_home, home_lambdas)
    p_away_at_obs = poisson.pmf(capped_away, away_lambdas)
    p_obs_indep = p_home_at_obs * p_away_at_obs

    p_h0 = poisson.pmf(0, home_lambdas)
    p_h1 = poisson.pmf(1, home_lambdas)
    p_a0 = poisson.pmf(0, away_lambdas)
    p_a1 = poisson.pmf(1, away_lambdas)
    p00 = p_h0 * p_a0
    p01 = p_h0 * p_a1
    p10 = p_h1 * p_a0
    p11 = p_h1 * p_a1

    mask_00 = (capped_home == 0) & (capped_away == 0)
    mask_01 = (capped_home == 0) & (capped_away == 1)
    mask_10 = (capped_home == 1) & (capped_away == 0)
    mask_11 = (capped_home == 1) & (capped_away == 1)

    max_lambda = float(max(home_lambdas.max(), away_lambdas.max()))
    safe_lower = -1.0 / max_lambda + 1e-3

    def negative_log_likelihood(rho: float) -> float:
        tau00 = 1.0 - home_lambdas * away_lambdas * rho
        tau01 = 1.0 + home_lambdas * rho
        tau10 = 1.0 + away_lambdas * rho
        tau11 = 1.0 - rho

        z = 1.0 + (tau00 - 1) * p00 + (tau01 - 1) * p01 + (tau10 - 1) * p10 + (tau11 - 1) * p11

        tau_at_obs = np.ones_like(p_obs_indep)
        tau_at_obs = np.where(mask_00, tau00, tau_at_obs)
        tau_at_obs = np.where(mask_01, tau01, tau_at_obs)
        tau_at_obs = np.where(mask_10, tau10, tau_at_obs)
        tau_at_obs = np.where(mask_11, tau11, tau_at_obs)

        p = (tau_at_obs * p_obs_indep) / z

        if np.any(p <= 0.0):
            return float("inf")

        return -float(np.sum(np.log(p)))

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
