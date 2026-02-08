import json
from datetime import datetime, timedelta
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


FIRST_MATCHWEEK = datetime(2025, 12, 27)
PREDICTIONS_PATH = DATA_DIR / "predictions-2026.json"
UPCOMING_PATH = DATA_DIR / "upcoming.json"


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


class MatchweekSummaryResponse(BaseModel):
    week: int
    startDate: str
    endDate: str
    matchCount: int
    mlCorrect: int
    poissonCorrect: int


class MatchweekDetailSummary(BaseModel):
    mlCorrect: int
    mlTotal: int
    poissonCorrect: int
    poissonTotal: int


class MatchweekDetailResponse(BaseModel):
    week: int
    startDate: str
    endDate: str
    matches: list[MatchResult]
    summary: MatchweekDetailSummary


def _load_predictions() -> list[dict]:
    if not PREDICTIONS_PATH.exists():
        return []
    with open(PREDICTIONS_PATH) as f:
        return json.load(f)


def _matchweek_for_date(dt: datetime) -> int:
    days_since = (dt - FIRST_MATCHWEEK).days
    if days_since < 0:
        return 0
    return days_since // 7 + 1


def _matchweek_dates(week: int) -> tuple[datetime, datetime]:
    start = FIRST_MATCHWEEK + timedelta(days=(week - 1) * 7)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def _group_by_matchweek(predictions: list[dict]) -> dict[int, list[dict]]:
    groups: dict[int, list[dict]] = {}
    for p in predictions:
        dt = datetime.fromisoformat(p["date"])
        week = _matchweek_for_date(dt)
        if week < 1:
            continue
        groups.setdefault(week, []).append(p)
    return groups


@app.get("/matchweeks", response_model=list[MatchweekSummaryResponse])
def get_matchweeks():
    predictions = _load_predictions()
    groups = _group_by_matchweek(predictions)

    summaries = []
    for week in sorted(groups.keys()):
        matches = groups[week]
        start, end = _matchweek_dates(week)
        summaries.append(MatchweekSummaryResponse(
            week=week,
            startDate=start.strftime("%-d %b %Y"),
            endDate=end.strftime("%-d %b %Y"),
            matchCount=len(matches),
            mlCorrect=sum(1 for m in matches if m["ml"]["correct"]),
            poissonCorrect=sum(1 for m in matches if m["poisson"]["correct"]),
        ))

    return summaries


@app.get("/matchweeks/{week}", response_model=MatchweekDetailResponse)
def get_matchweek(week: int):
    predictions = _load_predictions()
    groups = _group_by_matchweek(predictions)

    if week not in groups:
        raise HTTPException(status_code=404, detail=f"matchweek {week} not found")

    matches = groups[week]
    start, end = _matchweek_dates(week)

    return MatchweekDetailResponse(
        week=week,
        startDate=start.strftime("%-d %b %Y"),
        endDate=end.strftime("%-d %b %Y"),
        matches=[MatchResult(**m) for m in matches],
        summary=MatchweekDetailSummary(
            mlCorrect=sum(1 for m in matches if m["ml"]["correct"]),
            mlTotal=len(matches),
            poissonCorrect=sum(1 for m in matches if m["poisson"]["correct"]),
            poissonTotal=len(matches),
        ),
    )


class UpcomingMlResult(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    predictedOutcome: str
    topScore: TopScore


class UpcomingPoissonResult(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    predictedOutcome: str
    homeLambda: float
    awayLambda: float
    topScore: TopScore


class UpcomingMatch(BaseModel):
    homeTeam: str
    awayTeam: str
    date: str
    ml: UpcomingMlResult
    poisson: UpcomingPoissonResult


class UpcomingResponse(BaseModel):
    startDate: str
    endDate: str
    matches: list[UpcomingMatch]


def _load_upcoming() -> list[dict]:
    if not UPCOMING_PATH.exists():
        return []
    with open(UPCOMING_PATH) as f:
        return json.load(f)


@app.get("/upcoming", response_model=UpcomingResponse)
def get_upcoming():
    matches = _load_upcoming()
    if not matches:
        return UpcomingResponse(startDate="", endDate="", matches=[])

    dates = [datetime.fromisoformat(m["date"]) for m in matches]
    return UpcomingResponse(
        startDate=min(dates).strftime("%-d %b %Y"),
        endDate=max(dates).strftime("%-d %b %Y"),
        matches=[UpcomingMatch(**m) for m in matches],
    )


def start():
    uvicorn.run(
        "match_predictor_api.main:app",
        host="0.0.0.0",
        port=4400,
        reload=True,
    )
