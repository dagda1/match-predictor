import json

import numpy as np
import pandas as pd

from match_predictor.data import load_matches, DATA_DIR
from match_predictor.model import train
from match_predictor.features import build_feature_row
from match_predictor.poisson_baseline import poisson_predict

CUTOFF = pd.Timestamp("2026-01-01")
PREDICTIONS_PATH = DATA_DIR / "predictions-2025.json"


def _outcome(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home"
    if home_goals < away_goals:
        return "away"
    return "draw"


def _predicted_outcome(home_win: float, draw: float, away_win: float) -> str:
    best = max(home_win, draw, away_win)
    if best == home_win:
        return "home"
    if best == draw:
        return "draw"
    return "away"


def generate() -> None:
    df = load_matches()

    train_df = df[df["date"] < CUTOFF]
    predict_df = df[df["date"] >= CUTOFF]

    if predict_df.empty:
        print(f"no matches after {CUTOFF.date()}")
        return

    print(f"training on {len(train_df)} matches before {CUTOFF.date()}")
    print(f"predicting {len(predict_df)} matches from {CUTOFF.date()} onwards")

    model = train(train_df)

    predictions = []

    for _, match in predict_df.iterrows():
        home_team = match["homeTeam"]
        away_team = match["awayTeam"]
        match_date = match["date"]

        features = build_feature_row(df, match_date, home_team, away_team)
        if features is None:
            print(f"  skipping {home_team} vs {away_team} — insufficient history")
            continue

        X = pd.DataFrame([features])
        proba = model.classifier.predict_proba(X)[0]
        classes = list(model.classifier.classes_)

        ml_home_win = float(proba[classes.index("home")])
        ml_draw = float(proba[classes.index("draw")])
        ml_away_win = float(proba[classes.index("away")])

        home_xg = features["homeXgFor"]
        away_xg = features["awayXgFor"]

        rng = np.random.default_rng(42)
        sim_home = rng.poisson(home_xg, 10_000)
        sim_away = rng.poisson(away_xg, 10_000)

        scoreline_counts: dict[tuple[int, int], int] = {}
        for h, a in zip(sim_home, sim_away):
            key = (int(h), int(a))
            scoreline_counts[key] = scoreline_counts.get(key, 0) + 1
        ml_top = sorted(scoreline_counts.items(), key=lambda x: x[1], reverse=True)[0]

        prior_df = df[df["date"] < match_date]
        poisson_result = poisson_predict(prior_df, home_team, away_team)
        poisson_top = poisson_result.scorelines[0]

        actual_home = int(match["homeGoals"])
        actual_away = int(match["awayGoals"])
        actual_outcome = _outcome(actual_home, actual_away)
        ml_pred = _predicted_outcome(ml_home_win, ml_draw, ml_away_win)
        poisson_pred = _predicted_outcome(poisson_result.home_win, poisson_result.draw, poisson_result.away_win)

        predictions.append({
            "homeTeam": home_team,
            "awayTeam": away_team,
            "date": match_date.isoformat(),
            "actualHomeGoals": actual_home,
            "actualAwayGoals": actual_away,
            "actualOutcome": actual_outcome,
            "ml": {
                "homeWin": ml_home_win,
                "draw": ml_draw,
                "awayWin": ml_away_win,
                "predictedOutcome": ml_pred,
                "correct": ml_pred == actual_outcome,
                "topScore": {
                    "homeGoals": ml_top[0][0],
                    "awayGoals": ml_top[0][1],
                    "probability": ml_top[1] / 10_000,
                },
            },
            "poisson": {
                "homeWin": poisson_result.home_win,
                "draw": poisson_result.draw,
                "awayWin": poisson_result.away_win,
                "predictedOutcome": poisson_pred,
                "correct": poisson_pred == actual_outcome,
                "homeLambda": poisson_result.home_lambda,
                "awayLambda": poisson_result.away_lambda,
                "topScore": {
                    "homeGoals": poisson_top["homeGoals"],
                    "awayGoals": poisson_top["awayGoals"],
                    "probability": poisson_top["probability"],
                },
            },
        })

        print(f"  {home_team} {actual_home}-{actual_away} {away_team}  ML:{ml_pred}({'✓' if ml_pred == actual_outcome else '✗'})  Poi:{poisson_pred}({'✓' if poisson_pred == actual_outcome else '✗'})")

    with open(PREDICTIONS_PATH, "w") as f:
        json.dump(predictions, f, indent=2)

    ml_correct = sum(1 for p in predictions if p["ml"]["correct"])
    poi_correct = sum(1 for p in predictions if p["poisson"]["correct"])
    print(f"\nsaved {len(predictions)} predictions to {PREDICTIONS_PATH}")
    print(f"ML: {ml_correct}/{len(predictions)} ({ml_correct/len(predictions)*100:.0f}%)")
    print(f"Poisson: {poi_correct}/{len(predictions)} ({poi_correct/len(predictions)*100:.0f}%)")


if __name__ == "__main__":
    generate()
