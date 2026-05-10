import math

import numpy as np
import pandas as pd

from match_predictor.evaluate import OUTCOMES, evaluate, outcome_of, rps


def test_rps_perfect_prediction_is_zero():
    probs = np.array([0.0, 1.0, 0.0])
    assert rps(probs, OUTCOMES.index("draw")) == 0.0


def test_rps_uniform_prediction():
    probs = np.array([1 / 3, 1 / 3, 1 / 3])
    score = rps(probs, OUTCOMES.index("draw"))
    expected = ((1 / 3 - 0) ** 2 + (2 / 3 - 1) ** 2) / 2
    assert math.isclose(score, expected)


def test_rps_distant_miss_worse_than_adjacent_miss():
    probs = np.array([0.9, 0.05, 0.05])
    adjacent = rps(probs, OUTCOMES.index("draw"))
    distant = rps(probs, OUTCOMES.index("away"))
    assert distant > adjacent


def test_outcome_of():
    assert outcome_of(2, 1) == "home"
    assert outcome_of(1, 2) == "away"
    assert outcome_of(1, 1) == "draw"


def test_evaluate_returns_metrics_for_each_holdout_match():
    holdout = pd.DataFrame([
        {"homeTeam": "A", "awayTeam": "B", "date": pd.Timestamp("2026-01-01"), "homeGoals": 2, "awayGoals": 0},
        {"homeTeam": "C", "awayTeam": "D", "date": pd.Timestamp("2026-01-02"), "homeGoals": 1, "awayGoals": 1},
        {"homeTeam": "E", "awayTeam": "F", "date": pd.Timestamp("2026-01-03"), "homeGoals": 0, "awayGoals": 2},
    ])
    df = holdout

    def perfect(home, away, date, df):
        match = holdout[(holdout["homeTeam"] == home) & (holdout["awayTeam"] == away)].iloc[0]
        outcome = outcome_of(int(match["homeGoals"]), int(match["awayGoals"]))
        probs = [0.0, 0.0, 0.0]
        probs[OUTCOMES.index(outcome)] = 1.0
        return tuple(probs)

    result = evaluate(perfect, df, holdout)

    assert result["n"] == 3
    assert result["skipped"] == 0
    assert result["rps"] == 0.0
    assert result["brier"] == 0.0


def test_evaluate_skips_when_predict_fn_returns_none():
    holdout = pd.DataFrame([
        {"homeTeam": "A", "awayTeam": "B", "date": pd.Timestamp("2026-01-01"), "homeGoals": 1, "awayGoals": 0},
        {"homeTeam": "C", "awayTeam": "D", "date": pd.Timestamp("2026-01-02"), "homeGoals": 1, "awayGoals": 0},
    ])

    def predict(home, away, date, df):
        if home == "C":
            return None
        return (0.5, 0.3, 0.2)

    result = evaluate(predict, holdout, holdout)

    assert result["n"] == 1
    assert result["skipped"] == 1


def test_evaluate_uniform_prediction_gives_known_rps():
    holdout = pd.DataFrame([
        {"homeTeam": "A", "awayTeam": "B", "date": pd.Timestamp("2026-01-01"), "homeGoals": 0, "awayGoals": 0},
    ])

    def uniform(home, away, date, df):
        return (1 / 3, 1 / 3, 1 / 3)

    result = evaluate(uniform, holdout, holdout)
    expected_rps = ((1 / 3 - 0) ** 2 + (2 / 3 - 1) ** 2) / 2

    assert math.isclose(result["rps"], expected_rps)
