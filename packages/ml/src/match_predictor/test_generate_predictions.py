import json

import pandas as pd
import pytest

from match_predictor.data import DATA_DIR, to_match_dataframe
from match_predictor.generate_predictions import generate


def _load_two_seasons() -> pd.DataFrame:
    frames = []
    for season in ("2024", "2025"):
        with open(DATA_DIR / f"matches-{season}.json") as f:
            frames.append(pd.DataFrame(json.load(f)))
    return to_match_dataframe(frames)


@pytest.fixture(scope="module")
def generated() -> tuple[pd.DataFrame, list[dict]]:
    df = _load_two_seasons()
    predictions: list[dict] = []
    generate(lambda: df, predictions.extend, lambda model: None)
    return df, predictions


def test_cutoff_is_first_kickoff_of_newest_season(generated):
    _, predictions = generated

    dates = sorted(p["date"] for p in predictions)

    assert dates[0] == "2025-08-15 19:00:00"


def test_promoted_teams_get_predictions_from_their_first_match(generated):
    df, predictions = generated

    newest_season_matches = df[df["season"] == "2025"]
    predicted = {(p["homeTeam"], p["awayTeam"], p["date"]) for p in predictions}

    assert len(predictions) == len(newest_season_matches)
    assert ("Sunderland", "West Ham", "2025-08-16 14:00:00") in predicted
    assert ("Tottenham", "Burnley", "2025-08-16 14:00:00") in predicted
    assert ("Leeds", "Everton", "2025-08-18 19:00:00") in predicted


def test_promoted_team_poisson_uses_relegated_teams_average_xg(generated):
    _, predictions = generated

    match = next(
        p for p in predictions
        if (p["homeTeam"], p["awayTeam"], p["date"]) == ("Sunderland", "West Ham", "2025-08-16 14:00:00")
    )

    assert match["poisson"]["homeLambda"] == pytest.approx(1.0646667368, abs=1e-6)
    assert match["poisson"]["awayLambda"] == pytest.approx(1.3227651579, abs=1e-6)
