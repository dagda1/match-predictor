from dataclasses import dataclass

import pandas as pd

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


def poisson_predict(
    df: pd.DataFrame,
    home_team: str,
    away_team: str,
) -> PoissonPrediction:
    home_matches = _team_xg(df, home_team, is_home=True)
    away_matches = _team_xg(df, away_team, is_home=False)

    if home_matches.empty:
        raise ValueError(f"no home match data for {home_team}")
    if away_matches.empty:
        raise ValueError(f"no away match data for {away_team}")

    home_lambda = float(home_matches["xgFor"].mean())
    away_lambda = float(away_matches["xgFor"].mean())

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
