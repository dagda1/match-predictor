export interface Scoreline {
  homeGoals: number;
  awayGoals: number;
  probability: number;
}

export interface MlPrediction {
  homeWin: number;
  draw: number;
  awayWin: number;
  scorelines: Scoreline[];
}

export interface PoissonPrediction {
  homeWin: number;
  draw: number;
  awayWin: number;
  homeLambda: number;
  awayLambda: number;
  scorelines: Scoreline[];
}

export interface PredictResponse {
  ml: MlPrediction;
  poisson: PoissonPrediction;
}

export interface Team {
  id: string;
  name: string;
}

export interface TopScore {
  homeGoals: number;
  awayGoals: number;
  probability: number;
}

export type Outcome = 'home' | 'draw' | 'away';

export interface MatchMlResult {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  correct: boolean | null;
  topScore: TopScore;
}

export interface MatchPoissonResult {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  correct: boolean | null;
  homeLambda: number;
  awayLambda: number;
  topScore: TopScore;
}

export interface MatchResult {
  homeTeam: string;
  awayTeam: string;
  date: string;
  actualHomeGoals: number | null;
  actualAwayGoals: number | null;
  actualOutcome: Outcome | null;
  ml: MatchMlResult;
  poisson: MatchPoissonResult;
}

export interface ResultsSummary {
  mlCorrect: number;
  mlTotal: number;
  poissonCorrect: number;
  poissonTotal: number;
}

export interface ResultsResponse {
  matches: MatchResult[];
  summary: ResultsSummary;
  hasEarlier: boolean;
  hasLater: boolean;
}
