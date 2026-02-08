from dataclasses import dataclass

import numpy as np
import pandas as pd


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
    n_simulations: int = 10_000,
) -> PoissonPrediction:
    home_matches = _team_xg(df, home_team, is_home=True)
    away_matches = _team_xg(df, away_team, is_home=False)

    if home_matches.empty:
        raise ValueError(f"no home match data for {home_team}")
    if away_matches.empty:
        raise ValueError(f"no away match data for {away_team}")

    home_lambda = float(home_matches["xgFor"].mean())
    away_lambda = float(away_matches["xgFor"].mean())

    rng = np.random.default_rng()
    home_goals = rng.poisson(home_lambda, n_simulations)
    away_goals = rng.poisson(away_lambda, n_simulations)

    home_wins = int(np.sum(home_goals > away_goals))
    draws = int(np.sum(home_goals == away_goals))
    away_wins = int(np.sum(home_goals < away_goals))

    scoreline_counts: dict[tuple[int, int], int] = {}
    for h, a in zip(home_goals, away_goals):
        key = (int(h), int(a))
        scoreline_counts[key] = scoreline_counts.get(key, 0) + 1

    top_scorelines = sorted(
        scoreline_counts.items(), key=lambda x: x[1], reverse=True
    )[:10]

    return PoissonPrediction(
        home_win=home_wins / n_simulations,
        draw=draws / n_simulations,
        away_win=away_wins / n_simulations,
        scorelines=[
            {
                "homeGoals": score[0],
                "awayGoals": score[1],
                "probability": count / n_simulations,
            }
            for score, count in top_scorelines
        ],
        home_lambda=home_lambda,
        away_lambda=away_lambda,
    )
