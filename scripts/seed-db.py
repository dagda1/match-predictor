#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[0] / ".." / "packages" / "ml" / "src"))

from match_predictor.db_models import Team, Match, TeamFeatures, Prediction, Upcoming

DATABASE_URL = os.environ["DATABASE_URL"]
DATA_DIR = Path(__file__).resolve().parent.parent / "packages" / "etl" / "data"

engine = create_engine(DATABASE_URL)


def seed_teams(session: Session) -> None:
    matches = []
    for path in sorted(DATA_DIR.glob("matches-*.json")):
        with open(path) as f:
            matches.extend(json.load(f))

    teams = sorted(set(m["homeTeam"] for m in matches) | set(m["awayTeam"] for m in matches))

    for name in teams:
        session.merge(Team(name=name))

    session.commit()
    print(f"seeded {len(teams)} teams")


def seed_matches(session: Session) -> None:
    count = 0
    for path in sorted(DATA_DIR.glob("matches-*.json")):
        with open(path) as f:
            matches = json.load(f)

        for match in matches:
            session.merge(Match(
                id=match["id"],
                date=datetime.fromisoformat(match["date"]),
                season=match["season"],
                home_team=match["homeTeam"],
                away_team=match["awayTeam"],
                home_goals=int(match["homeGoals"]),
                away_goals=int(match["awayGoals"]),
                home_xg=float(match["homeXg"]),
                away_xg=float(match["awayXg"]),
                home_shots=int(match["homeShots"]),
                away_shots=int(match["awayShots"]),
                home_shots_on_target=int(match["homeShotsOnTarget"]),
                away_shots_on_target=int(match["awayShotsOnTarget"]),
                home_deep=int(match["homeDeep"]),
                away_deep=int(match["awayDeep"]),
                home_ppda=float(match["homePpda"]),
                away_ppda=float(match["awayPpda"]),
                home_win_prob=float(match["homeWinProb"]),
                draw_prob=float(match["drawProb"]),
                away_win_prob=float(match["awayWinProb"]),
            ))
            count += 1

    session.commit()
    print(f"seeded {count} matches")


def seed_features(session: Session) -> None:
    from match_predictor.data import load_matches
    from match_predictor.features import _rolling_stats, _home_advantage
    import pandas as pd

    df = load_matches()
    teams = sorted(set(df["homeTeam"]) | set(df["awayTeam"]))
    now = pd.Timestamp.now()
    home_advantage = _home_advantage(df)
    count = 0

    for team in teams:
        stats = _rolling_stats(df, team, now)
        if not stats:
            continue
        session.merge(TeamFeatures(
            team_name=team,
            xg_for_avg=float(stats["xgForAvg"]),
            xg_against_avg=float(stats["xgAgainstAvg"]),
            xg_overperformance=float(stats["xgOverperformance"]),
            shot_conversion=float(stats["shotConversion"]),
            sot_pct=float(stats["sotPct"]),
            ppda=float(stats["ppda"]),
            deep_avg=float(stats["deepAvg"]),
            goals_for_avg=float(stats["goalsForAvg"]),
            goals_against_avg=float(stats["goalsAgainstAvg"]),
            home_advantage=float(home_advantage),
        ))
        count += 1

    session.commit()
    print(f"seeded features for {count} teams")


def seed_predictions(session: Session) -> None:
    path = DATA_DIR / "predictions-2026.json"
    if not path.exists():
        print("no predictions file, skipping")
        return

    with open(path) as f:
        predictions = json.load(f)

    for pred in predictions:
        session.add(Prediction(
            home_team=pred["homeTeam"],
            away_team=pred["awayTeam"],
            date=datetime.fromisoformat(pred["date"]),
            actual_home_goals=pred.get("actualHomeGoals"),
            actual_away_goals=pred.get("actualAwayGoals"),
            actual_outcome=pred.get("actualOutcome"),
            ml_home_win=pred["ml"]["homeWin"],
            ml_draw=pred["ml"]["draw"],
            ml_away_win=pred["ml"]["awayWin"],
            ml_predicted_outcome=pred["ml"]["predictedOutcome"],
            ml_correct=pred["ml"].get("correct"),
            ml_top_home_goals=pred["ml"]["topScore"]["homeGoals"],
            ml_top_away_goals=pred["ml"]["topScore"]["awayGoals"],
            ml_top_probability=pred["ml"]["topScore"]["probability"],
            poisson_home_win=pred["poisson"]["homeWin"],
            poisson_draw=pred["poisson"]["draw"],
            poisson_away_win=pred["poisson"]["awayWin"],
            poisson_predicted_outcome=pred["poisson"]["predictedOutcome"],
            poisson_correct=pred["poisson"].get("correct"),
            poisson_home_lambda=pred["poisson"]["homeLambda"],
            poisson_away_lambda=pred["poisson"]["awayLambda"],
            poisson_top_home_goals=pred["poisson"]["topScore"]["homeGoals"],
            poisson_top_away_goals=pred["poisson"]["topScore"]["awayGoals"],
            poisson_top_probability=pred["poisson"]["topScore"]["probability"],
        ))

    session.commit()
    print(f"seeded {len(predictions)} predictions")


def seed_upcoming(session: Session) -> None:
    path = DATA_DIR / "upcoming.json"
    if not path.exists():
        print("no upcoming file, skipping")
        return

    with open(path) as f:
        upcoming = json.load(f)

    for match in upcoming:
        session.add(Upcoming(
            home_team=match["homeTeam"],
            away_team=match["awayTeam"],
            date=datetime.fromisoformat(match["date"]),
            ml_home_win=match["ml"]["homeWin"],
            ml_draw=match["ml"]["draw"],
            ml_away_win=match["ml"]["awayWin"],
            ml_predicted_outcome=match["ml"]["predictedOutcome"],
            ml_top_home_goals=match["ml"]["topScore"]["homeGoals"],
            ml_top_away_goals=match["ml"]["topScore"]["awayGoals"],
            ml_top_probability=match["ml"]["topScore"]["probability"],
            poisson_home_win=match["poisson"]["homeWin"],
            poisson_draw=match["poisson"]["draw"],
            poisson_away_win=match["poisson"]["awayWin"],
            poisson_predicted_outcome=match["poisson"]["predictedOutcome"],
            poisson_home_lambda=match["poisson"]["homeLambda"],
            poisson_away_lambda=match["poisson"]["awayLambda"],
            poisson_top_home_goals=match["poisson"]["topScore"]["homeGoals"],
            poisson_top_away_goals=match["poisson"]["topScore"]["awayGoals"],
            poisson_top_probability=match["poisson"]["topScore"]["probability"],
        ))

    session.commit()
    print(f"seeded {len(upcoming)} upcoming")


with Session(engine) as session:
    for table in [Upcoming, Prediction, TeamFeatures, Match, Team]:
        session.execute(table.__table__.delete())
    session.commit()
    print("cleared all tables")

    seed_teams(session)
    seed_matches(session)
    seed_features(session)
    seed_predictions(session)
    seed_upcoming(session)
    print("done")
