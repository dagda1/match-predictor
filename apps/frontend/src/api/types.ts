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
  correct: boolean;
  topScore: TopScore;
}

export interface MatchPoissonResult {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  correct: boolean;
  homeLambda: number;
  awayLambda: number;
  topScore: TopScore;
}

export interface MatchResult {
  homeTeam: string;
  awayTeam: string;
  date: string;
  actualHomeGoals: number;
  actualAwayGoals: number;
  actualOutcome: Outcome;
  ml: MatchMlResult;
  poisson: MatchPoissonResult;
}

export interface MatchweekSummary {
  week: number;
  startDate: string;
  endDate: string;
  matchCount: number;
  mlCorrect: number;
  poissonCorrect: number;
}

export interface UpcomingMlResult {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  topScore: TopScore;
}

export interface UpcomingPoissonResult {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  homeLambda: number;
  awayLambda: number;
  topScore: TopScore;
}

export interface UpcomingMatch {
  homeTeam: string;
  awayTeam: string;
  date: string;
  ml: UpcomingMlResult;
  poisson: UpcomingPoissonResult;
}

export interface UpcomingResponse {
  startDate: string;
  endDate: string;
  matches: UpcomingMatch[];
}

export interface MatchweekDetail {
  week: number;
  startDate: string;
  endDate: string;
  matches: MatchResult[];
  summary: {
    mlCorrect: number;
    mlTotal: number;
    poissonCorrect: number;
    poissonTotal: number;
  };
}
