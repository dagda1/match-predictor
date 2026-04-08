from pydantic import BaseModel


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


class Team(BaseModel):
    id: str
    name: str


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
