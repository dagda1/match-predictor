from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


OUTCOMES = ("home", "draw", "away")

OutcomeProbs = tuple[float, float, float]
PredictFn = Callable[[str, str, pd.Timestamp, pd.DataFrame], OutcomeProbs | None]


def outcome_of(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home"
    if home_goals < away_goals:
        return "away"
    return "draw"


def rps(probs: np.ndarray, actual_idx: int) -> float:
    actual = np.zeros(len(probs))
    actual[actual_idx] = 1.0
    cum_pred = np.cumsum(probs)
    cum_actual = np.cumsum(actual)
    return float(np.sum((cum_pred[:-1] - cum_actual[:-1]) ** 2) / (len(probs) - 1))


def evaluate(
    predict_fn: PredictFn,
    df: pd.DataFrame,
    holdout: pd.DataFrame,
) -> dict:
    probs_list = []
    actuals = []
    skipped = 0

    for _, match in holdout.iterrows():
        result = predict_fn(match["homeTeam"], match["awayTeam"], match["date"], df)
        if result is None:
            skipped += 1
            continue
        probs_list.append(np.array(result))
        actual = outcome_of(int(match["homeGoals"]), int(match["awayGoals"]))
        actuals.append(OUTCOMES.index(actual))

    probs_arr = np.array(probs_list)
    actuals_arr = np.array(actuals)

    rps_mean = float(np.mean([rps(p, a) for p, a in zip(probs_arr, actuals_arr)]))

    onehot = np.eye(3)[actuals_arr]
    brier = float(np.mean(np.sum((probs_arr - onehot) ** 2, axis=1)))

    log_loss_val = float(log_loss(actuals_arr, probs_arr, labels=[0, 1, 2]))

    return {
        "rps": rps_mean,
        "log_loss": log_loss_val,
        "brier": brier,
        "n": len(probs_list),
        "skipped": skipped,
    }
