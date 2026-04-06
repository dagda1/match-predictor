import json
import os
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from match_predictor import load_matches, predict_match, poisson_predict
from match_predictor.data import DATA_DIR
from match_predictor.model import load_model

BUCKET_NAME = os.environ.get("BUCKET_NAME")
MODEL_PATH = DATA_DIR / "model.joblib"


def _load_model():
    if BUCKET_NAME:
        import boto3
        s3 = boto3.client("s3")
        local_path = Path("/tmp/model.joblib")
        s3.download_file(BUCKET_NAME, "model/model.joblib", str(local_path))
        return load_model(local_path)
    return load_model(MODEL_PATH)

ORIGIN_SECRET_ARN = os.environ.get("ORIGIN_SECRET_ARN")

_cached_secret: str | None = None


def _get_origin_secret() -> str | None:
    global _cached_secret
    if _cached_secret:
        return _cached_secret
    if not ORIGIN_SECRET_ARN:
        return None
    import boto3
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=ORIGIN_SECRET_ARN)
    _cached_secret = response["SecretString"]
    return _cached_secret


class OriginVerifyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        secret = _get_origin_secret()
        if secret:
            header_value = request.headers.get("x-origin-verify")
            if header_value != secret:
                return JSONResponse(status_code=403, content={"detail": "forbidden"})
        return await call_next(request)


app = FastAPI(title="Match Predictor API")

app.add_middleware(OriginVerifyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3300"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = load_matches()
model = _load_model()


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
    correct: bool | None = None
    topScore: TopScore


class MatchPoissonResult(BaseModel):
    homeWin: float
    draw: float
    awayWin: float
    predictedOutcome: str
    correct: bool | None = None
    homeLambda: float
    awayLambda: float
    topScore: TopScore


class MatchResult(BaseModel):
    homeTeam: str
    awayTeam: str
    date: str
    actualHomeGoals: int | None = None
    actualAwayGoals: int | None = None
    actualOutcome: str | None = None
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
    earlierMatchDate: str | None = None
    laterMatchDate: str | None = None


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _all_matches() -> list[dict]:
    predictions = _load_json(PREDICTIONS_PATH)
    upcoming = _load_json(UPCOMING_PATH)

    prediction_keys = {(p["homeTeam"], p["awayTeam"], p["date"][:10]) for p in predictions}
    unique_upcoming = [
        u for u in upcoming
        if (u["homeTeam"], u["awayTeam"], u["date"][:10]) not in prediction_keys
    ]

    return predictions + unique_upcoming


@app.get("/results", response_model=ResultsResponse)
def get_results(startDate: str, endDate: str | None = None):
    all_matches = _all_matches()

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
