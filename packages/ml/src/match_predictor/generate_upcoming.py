import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

from match_predictor.data import load_matches, DATA_DIR
from match_predictor.model import train
from match_predictor.features import build_feature_row
from match_predictor.poisson_baseline import poisson_predict

UPCOMING_PATH = DATA_DIR / "upcoming.json"
SEASON = "2025"


def _fetch_upcoming_fixtures() -> list[dict]:
    response = requests.get(
        f"https://understat.com/getLeagueData/EPL/{SEASON}",
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://understat.com/league/EPL/{SEASON}",
        },
    )
    response.raise_for_status()

    data = response.json()

    now = datetime.now()
    cutoff = now + timedelta(days=8)

    fixtures = []
    for entry in data["dates"]:
        if entry["isResult"]:
            continue
        dt = datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S")
        if dt < now or dt > cutoff:
            continue
        fixtures.append({
            "homeTeam": entry["h"]["title"],
            "awayTeam": entry["a"]["title"],
            "date": dt.isoformat(),
        })

    return sorted(fixtures, key=lambda f: f["date"])


def generate() -> None:
    print("fetching upcoming fixtures from Understat...")
    fixtures = _fetch_upcoming_fixtures()

    if not fixtures:
        print("no upcoming fixtures in the next 7 days")
        with open(UPCOMING_PATH, "w") as f:
            json.dump([], f)
        return

    print(f"found {len(fixtures)} upcoming fixtures")

    df = load_matches()
    model = train(df)

    predictions = []
    for fixture in fixtures:
        home_team = fixture["homeTeam"]
        away_team = fixture["awayTeam"]
        match_date = pd.Timestamp(fixture["date"])

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

        poisson_result = poisson_predict(df, home_team, away_team)
        poisson_top = poisson_result.scorelines[0]

        best_ml = max(ml_home_win, ml_draw, ml_away_win)
        ml_pred = "home" if best_ml == ml_home_win else ("draw" if best_ml == ml_draw else "away")
        best_poi = max(poisson_result.home_win, poisson_result.draw, poisson_result.away_win)
        poi_pred = "home" if best_poi == poisson_result.home_win else ("draw" if best_poi == poisson_result.draw else "away")

        predictions.append({
            "homeTeam": home_team,
            "awayTeam": away_team,
            "date": fixture["date"],
            "ml": {
                "homeWin": ml_home_win,
                "draw": ml_draw,
                "awayWin": ml_away_win,
                "predictedOutcome": ml_pred,
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
                "predictedOutcome": poi_pred,
                "homeLambda": poisson_result.home_lambda,
                "awayLambda": poisson_result.away_lambda,
                "topScore": {
                    "homeGoals": poisson_top["homeGoals"],
                    "awayGoals": poisson_top["awayGoals"],
                    "probability": poisson_top["probability"],
                },
            },
        })

        print(f"  {home_team} vs {away_team}  ML:{ml_pred}  Poi:{poi_pred}  ML top:{ml_top[0][0]}-{ml_top[0][1]}  Poi top:{poisson_top['homeGoals']}-{poisson_top['awayGoals']}")

    with open(UPCOMING_PATH, "w") as f:
        json.dump(predictions, f, indent=2)

    print(f"\nsaved {len(predictions)} upcoming predictions to {UPCOMING_PATH}")


if __name__ == "__main__":
    generate()
