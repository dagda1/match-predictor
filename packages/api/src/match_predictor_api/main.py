import json
from datetime import date, datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from match_predictor import load_matches, train, predict_match, poisson_predict
from match_predictor.data import DATA_DIR

app = FastAPI(title="Match Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3300"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = load_matches()
model = train(df)


class PredictRequest(BaseModel):
    homeTeamId: str
    awayTeamId: str


class Scoreline(BaseModel):
    homeGoals: int
    awayGoals: int
    probability: float


class MlPrediction(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    scorelines: list[Scoreline]


class PoissonPrediction(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    homeLambda: float
    awayLambda: float
    scorelines: list[Scoreline]


class PredictResponse(BaseModel):
    ml: MlPrediction
    poisson: PoissonPrediction


class Team(BaseModel):
    id: str
    name: str


class MetricsResponse(BaseModel):
    accuracy: float
    brierScore: float
    logLoss: float
    rocAuc: float
    baselineAccuracy: float


@app.get("/teams", response_model=list[Team])
def get_teams():
    home_teams = df["homeTeam"].unique()
    away_teams = df["awayTeam"].unique()
    all_teams = sorted(set(home_teams) | set(away_teams))
    return [Team(id=name, name=name) for name in all_teams]


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    ml_result = predict_match(model, req.homeTeamId, req.awayTeamId)
    poisson_result = poisson_predict(df, req.homeTeamId, req.awayTeamId)
    return PredictResponse(
        ml=MlPrediction(
            homeWin=ml_result.home_win,
            draw=ml_result.draw,
            awayWin=ml_result.away_win,
            scorelines=[Scoreline(**s) for s in ml_result.scorelines],
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


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    m = model.metrics
    return MetricsResponse(
        accuracy=m.accuracy,
        brierScore=m.brier_score,
        logLoss=m.log_loss_val,
        rocAuc=m.roc_auc,
        baselineAccuracy=m.baseline_accuracy,
    )


PREDICTIONS_PATH = DATA_DIR / "predictions-2026.json"


class TopScore(BaseModel):
    homeGoals: int
    awayGoals: int
    probability: float


class MatchMlResult(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    predictedOutcome: str
    correct: bool
    topScore: TopScore


class MatchPoissonResult(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    predictedOutcome: str
    correct: bool
    homeLambda: float
    awayLambda: float
    topScore: TopScore


class MatchResult(BaseModel):
    homeTeam: str
    awayTeam: str
    date: str
    actualHomeGoals: int
    actualAwayGoals: int
    actualOutcome: str
    ml: MatchMlResult
    poisson: MatchPoissonResult


class ResultsSummary(BaseModel):
    mlCorrect: int
    mlTotal: int
    poissonCorrect: int
    poissonTotal: int


class ResultsResponse(BaseModel):
    matches: list[MatchResult]
    summary: ResultsSummary
    hasEarlier: bool
    hasLater: bool


def _load_predictions() -> list[dict]:
    if not PREDICTIONS_PATH.exists():
        return []
    with open(PREDICTIONS_PATH) as f:
        return json.load(f)


@app.get("/results", response_model=ResultsResponse)
def get_results(startDate: str, endDate: str | None = None):
    predictions = _load_predictions()

    start = date.fromisoformat(startDate)
    end = date.fromisoformat(endDate) if endDate else None

    filtered = []
    has_earlier = False
    has_later = False

    for prediction in predictions:
        match_date = datetime.fromisoformat(prediction["date"]).date()

        if match_date < start:
            has_earlier = True
        elif end and match_date > end:
            has_later = True
        else:
            filtered.append(prediction)

    return ResultsResponse(
        matches=[MatchResult(**m) for m in filtered],
        summary=ResultsSummary(
            mlCorrect=sum(1 for m in filtered if m["ml"]["correct"]),
            mlTotal=len(filtered),
            poissonCorrect=sum(1 for m in filtered if m["poisson"]["correct"]),
            poissonTotal=len(filtered),
        ),
        hasEarlier=has_earlier,
        hasLater=has_later,
    )


def start():
    uvicorn.run(
        "match_predictor_api.main:app",
        host="0.0.0.0",
        port=4400,
        reload=True,
    )
