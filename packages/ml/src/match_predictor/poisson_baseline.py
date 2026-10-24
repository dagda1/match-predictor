from dataclasses import dataclass

import pandas as pd

from match_predictor.features import MIN_MATCHES, match_count, relegated_teams
from match_predictor.grid import (
    build_grid,
    outcome_probs_from_grid,
    top_scorelines_from_grid,
)


@dataclass
class PoissonPrediction:
    home_win: float
    draw: float
    away_win: float
    scorelines: list[dict]
    home_lambda: float
    away_lambda: float


def _team_xg(df: pd.DataFrame, team: str, is_home: bool) -> pd.DataFrame:
    if is_home:
        return df[df["homeTeam"] == team][["date", "homeXg"]].rename(
            columns={"homeXg": "xgFor"}
        )
    return df[df["awayTeam"] == team][["date", "awayXg"]].rename(
        columns={"awayXg": "xgFor"}
    )


def _lambda(df: pd.DataFrame, team: str, is_home: bool) -> float:
    if match_count(df, team) < MIN_MATCHES:
        relegated = relegated_teams(df)
        if relegated:
            means = [float(_team_xg(df, relegated_team, is_home)["xgFor"].mean()) for relegated_team in relegated]
            return sum(means) / len(means)

    matches = _team_xg(df, team, is_home)
    if matches.empty:
        raise ValueError(f"no {'home' if is_home else 'away'} match data for {team}")

    return float(matches["xgFor"].mean())


def poisson_predict(
    df: pd.DataFrame,
    home_team: str,
    away_team: str,
) -> PoissonPrediction:
    home_lambda = _lambda(df, home_team, is_home=True)
    away_lambda = _lambda(df, away_team, is_home=False)

    grid = build_grid(home_lambda, away_lambda)
    home_win, draw, away_win = outcome_probs_from_grid(grid)

    return PoissonPrediction(
        home_win=home_win,
        draw=draw,
        away_win=away_win,
        scorelines=top_scorelines_from_grid(grid, n=10),
        home_lambda=home_lambda,
        away_lambda=away_lambda,
    )
