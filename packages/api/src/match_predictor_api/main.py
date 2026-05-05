import os
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text

from match_predictor.db_models import Team as TeamRow, TeamFeatures, Prediction as PredictionRow, Upcoming as UpcomingRow
from match_predictor.model import load_model, _scoreline_probabilities
from match_predictor.poisson_baseline import poisson_predict

from match_predictor_api.db import get_session, load_matches_dataframe
from match_predictor_api.middleware import OriginVerifyMiddleware
from match_predictor_api.models import (
    MlPrediction,
    MatchResult,
    PoissonPrediction,
    PredictRequest,
    PredictResponse,
    ResultsResponse,
    ResultsSummary,
    Scoreline,
    Team,
)

_env_model_path = os.environ.get("MODEL_PATH")
if _env_model_path:
    MODEL_PATH = Path(_env_model_path)
else:
    MODEL_PATH = Path(__file__).resolve().parents[4] / "packages" / "etl" / "data" / "model.joblib"

_model_cache = None
_match_df_cache = None


def _maybe_load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    if not MODEL_PATH.exists():
        return None
    _model_cache = load_model(MODEL_PATH)
    return _model_cache


def _get_match_df():
    global _match_df_cache
    if _match_df_cache is None:
        _match_df_cache = load_matches_dataframe()
    return _match_df_cache


app = FastAPI(title="Match Predictor API")
app.add_middleware(OriginVerifyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3300"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status")
def get_status():
    session = get_session()
    matches_count, matches_latest = session.execute(
        text("SELECT count(*), max(date) FROM matches")
    ).one()
    teams_count = session.execute(text("SELECT count(*) FROM teams")).scalar()
    predictions_count, predictions_latest, predictions_correct, predictions_scored = session.execute(
        text(
            "SELECT count(*), max(date), "
            "count(*) FILTER (WHERE ml_correct), "
            "count(*) FILTER (WHERE ml_correct IS NOT NULL) "
            "FROM predictions"
        )
    ).one()
    upcoming_count, upcoming_latest = session.execute(
        text("SELECT count(*), max(date) FROM upcoming")
    ).one()
    features_count = session.execute(text("SELECT count(*) FROM team_features")).scalar()
    alembic_revision = session.execute(text("SELECT version_num FROM alembic_version")).scalar()
    session.close()

    now = datetime.now(timezone.utc)
    scraped_hours_ago = None
    if matches_latest is not None:
        latest_aware = matches_latest if matches_latest.tzinfo else matches_latest.replace(tzinfo=timezone.utc)
        scraped_hours_ago = round((now - latest_aware).total_seconds() / 3600, 1)

    return {
        "matches": {
            "count": matches_count,
            "latest": matches_latest.isoformat() if matches_latest else None,
        },
        "teams": {"count": teams_count},
        "predictions": {
            "count": predictions_count,
            "latest": predictions_latest.isoformat() if predictions_latest else None,
            "correct": predictions_correct,
            "scored": predictions_scored,
        },
        "upcoming": {
            "count": upcoming_count,
            "latest": upcoming_latest.isoformat() if upcoming_latest else None,
        },
        "team_features": {"count": features_count},
        "alembic_revision": alembic_revision,
        "scraped_hours_ago": scraped_hours_ago,
    }


@app.get("/teams", response_model=list[Team])
def get_teams():
    session = get_session()
    rows = session.execute(select(TeamRow).order_by(TeamRow.name)).scalars().all()
    session.close()
    return [Team(id=row.name, name=row.name) for row in rows]


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    model = _maybe_load_model()
    if model is None:
        return JSONResponse(status_code=503, content={"detail": "model not ready, predictor has not run yet"})

    session = get_session()
    home = session.get(TeamFeatures, req.homeTeamId)
    away = session.get(TeamFeatures, req.awayTeamId)
    session.close()

    if not home or not away:
        return JSONResponse(status_code=400, content={"detail": "insufficient data"})

    feature_row = {
        "homeXgFor": home.xg_for_avg,
        "homeXgAgainst": home.xg_against_avg,
        "homeXgOverperf": home.xg_overperformance,
        "homeShotConv": home.shot_conversion,
        "homeSotPct": home.sot_pct,
        "homePpda": home.ppda,
        "homeDeep": home.deep_avg,
        "awayXgFor": away.xg_for_avg,
        "awayXgAgainst": away.xg_against_avg,
        "awayXgOverperf": away.xg_overperformance,
        "awayShotConv": away.shot_conversion,
        "awaySotPct": away.sot_pct,
        "awayPpda": away.ppda,
        "awayDeep": away.deep_avg,
        "homeAdvantage": home.home_advantage,
    }

    X = pd.DataFrame([feature_row])
    proba = model.classifier.predict_proba(X)[0]
    classes = list(model.classifier.classes_)

    poisson_result = poisson_predict(_get_match_df(), req.homeTeamId, req.awayTeamId)

    return PredictResponse(
        ml=MlPrediction(
            homeWin=float(proba[classes.index("home")]),
            draw=float(proba[classes.index("draw")]),
            awayWin=float(proba[classes.index("away")]),
            scorelines=[Scoreline(**s) for s in _scoreline_probabilities(model, X)],
        ),
        poisson=PoissonPrediction(
            homeWin=poisson_result.home_win,
            draw=poisson_result.draw,
            awayWin=poisson_result.away_win,
            homeLambda=poisson_result.home_lambda,
            awayLambda=poisson_result.away_lambda,
            scorelines=[Scoreline(**s) for s in poisson_result.scorelines],
        ),
    )


def _to_match_result(row, is_prediction: bool) -> dict:
    result = {
        "homeTeam": row.home_team,
        "awayTeam": row.away_team,
        "date": row.date.isoformat(),
        "ml": {
            "homeWin": row.ml_home_win,
            "draw": row.ml_draw,
            "awayWin": row.ml_away_win,
            "predictedOutcome": row.ml_predicted_outcome,
            "correct": row.ml_correct if is_prediction else None,
            "topScore": {
                "homeGoals": row.ml_top_home_goals,
                "awayGoals": row.ml_top_away_goals,
                "probability": row.ml_top_probability,
            },
        },
        "poisson": {
            "homeWin": row.poisson_home_win,
            "draw": row.poisson_draw,
            "awayWin": row.poisson_away_win,
            "predictedOutcome": row.poisson_predicted_outcome,
            "correct": row.poisson_correct if is_prediction else None,
            "homeLambda": row.poisson_home_lambda,
            "awayLambda": row.poisson_away_lambda,
            "topScore": {
                "homeGoals": row.poisson_top_home_goals,
                "awayGoals": row.poisson_top_away_goals,
                "probability": row.poisson_top_probability,
            },
        },
    }

    if is_prediction:
        result["actualHomeGoals"] = row.actual_home_goals
        result["actualAwayGoals"] = row.actual_away_goals
        result["actualOutcome"] = row.actual_outcome

    return result


@app.get("/results", response_model=ResultsResponse)
def get_results(startDate: str, endDate: str | None = None):
    session = get_session()
    predictions = session.execute(select(PredictionRow)).scalars().all()
    upcoming = session.execute(select(UpcomingRow)).scalars().all()
    session.close()

    all_matches = [_to_match_result(p, True) for p in predictions]

    prediction_keys = {(m["homeTeam"], m["awayTeam"], m["date"][:10]) for m in all_matches}
    for u in upcoming:
        key = (u.home_team, u.away_team, u.date.isoformat()[:10])
        if key not in prediction_keys:
            all_matches.append(_to_match_result(u, False))

    start = date.fromisoformat(startDate)
    end = date.fromisoformat(endDate) if endDate else None

    filtered = []
    earlier_date: date | None = None
    later_date: date | None = None

    for match in all_matches:
        match_date = datetime.fromisoformat(match["date"]).date()

        if match_date < start:
            if earlier_date is None or match_date > earlier_date:
                earlier_date = match_date
        elif end and match_date > end:
            if later_date is None or match_date < later_date:
                later_date = match_date
        else:
            filtered.append(match)

    played = [m for m in filtered if m.get("ml", {}).get("correct") is not None]

    return ResultsResponse(
        matches=[MatchResult(**m) for m in filtered],
        summary=ResultsSummary(
            mlCorrect=sum(1 for m in played if m["ml"]["correct"]),
            mlTotal=len(played),
            poissonCorrect=sum(1 for m in played if m["poisson"]["correct"]),
            poissonTotal=len(played),
        ),
        earlierMatchDate=earlier_date.isoformat() if earlier_date else None,
        laterMatchDate=later_date.isoformat() if later_date else None,
    )


def start():
    import uvicorn
    uvicorn.run(
        "match_predictor_api.main:app",
        host="0.0.0.0",
        port=4400,
        reload=True,
    )
