import json
from collections.abc import Callable
from datetime import datetime, timedelta

import pandas as pd
import requests

from match_predictor.data import load_matches as load_matches_from_disk, DATA_DIR, format_date
from match_predictor.model import train, _scoreline_probabilities
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
    cutoff = now + timedelta(weeks=3)

    fixtures = []
    for entry in data["dates"]:
        if entry["isResult"]:
            continue
        dt = datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S")
        if dt > cutoff:
            continue
        fixtures.append({
            "homeTeam": entry["h"]["title"],
            "awayTeam": entry["a"]["title"],
            "date": format_date(pd.Timestamp(dt)),
        })

    return sorted(fixtures, key=lambda f: f["date"])


def _write_to_disk(predictions: list[dict]) -> None:
    f = open(UPCOMING_PATH, "w")
    json.dump(predictions, f, indent=2)
    f.close()


def generate(
    load_matches: Callable[[], pd.DataFrame],
    write_output: Callable[[list[dict]], None],
) -> str:
    print("fetching upcoming fixtures from Understat...")
    fixtures = _fetch_upcoming_fixtures()

    assert len(fixtures) > 0, "no upcoming fixtures in the next 3 weeks"

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

        ml_scorelines = _scoreline_probabilities(model, X)
        ml_top = ml_scorelines[0]

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
                "topScore": ml_top,
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

        print(f"  {home_team} vs {away_team}  ML:{ml_pred}  Poi:{poi_pred}  ML top:{ml_top['homeGoals']}-{ml_top['awayGoals']}  Poi top:{poisson_top['homeGoals']}-{poisson_top['awayGoals']}")

    write_output(predictions)

    summary = f"{len(predictions)} upcoming predictions"
    print(summary)

    return summary


if __name__ == "__main__":
    generate(load_matches_from_disk, _write_to_disk)
