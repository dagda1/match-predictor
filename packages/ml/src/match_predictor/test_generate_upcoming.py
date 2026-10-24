import json
from datetime import datetime

import pandas as pd

from match_predictor.data import DATA_DIR, to_match_dataframe
from match_predictor.generate_upcoming import generate


def _load_two_seasons() -> pd.DataFrame:
    frames = []
    for season in ("2024", "2025"):
        with open(DATA_DIR / f"matches-{season}.json") as f:
            frames.append(pd.DataFrame(json.load(f)))
    return to_match_dataframe(frames)


def _entry(home: str, away: str, kickoff: str, is_result: bool) -> dict:
    entry = {
        "id": f"{home}-{away}-{kickoff}",
        "isResult": is_result,
        "h": {"id": f"{home}-id", "title": home, "short_title": home[:3].upper()},
        "a": {"id": f"{away}-id", "title": away, "short_title": away[:3].upper()},
        "goals": {"h": None, "a": None},
        "xG": {"h": None, "a": None},
        "datetime": kickoff,
    }

    if is_result:
        entry["goals"] = {"h": "1", "a": "0"}
        entry["xG"] = {"h": "1.2", "a": "0.8"}
        entry["forecast"] = {"w": "0.5", "d": "0.3", "l": "0.2"}

    return entry


LEAGUE_DATA = {
    "2025": {"teams": {}, "players": [], "dates": [
        _entry("Liverpool", "Bournemouth", "2025-08-15 19:00:00", True),
        _entry("Everton", "Fulham", "2026-08-12 19:00:00", False),
    ]},
    "2026": {"teams": {}, "players": [], "dates": [_entry("Arsenal", "Chelsea", "2026-08-21 19:00:00", False)]},
}

NO_FIXTURES = {"teams": [], "players": [], "dates": []}


def _fetch_league_data(season: str) -> dict:
    return LEAGUE_DATA.get(season, NO_FIXTURES)


def test_summer_break_writes_no_upcoming_matches():
    written: list[list[dict]] = []

    generate(
        _load_two_seasons,
        written.append,
        fetch_league_data=_fetch_league_data,
        now=datetime(2026, 7, 1, 12, 0, 0),
    )

    assert written == [[]]


def test_upcoming_includes_current_and_next_season_matches():
    written: list[list[dict]] = []

    generate(
        _load_two_seasons,
        written.append,
        fetch_league_data=_fetch_league_data,
        now=datetime(2026, 8, 10, 12, 0, 0),
    )

    fixtures = [(m["homeTeam"], m["awayTeam"], m["date"]) for m in written[0]]

    assert fixtures == [
        ("Everton", "Fulham", "2026-08-12 19:00:00"),
        ("Arsenal", "Chelsea", "2026-08-21 19:00:00"),
    ]
