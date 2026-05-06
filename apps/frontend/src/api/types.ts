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

interface MlBase {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  topScore: TopScore;
}

interface PoissonBase {
  homeWin: number;
  draw: number;
  awayWin: number;
  predictedOutcome: Outcome;
  homeLambda: number;
  awayLambda: number;
  topScore: TopScore;
}

export interface PlayedMatch {
  played: true;
  homeTeam: string;
  awayTeam: string;
  date: string;
  actualHomeGoals: number;
  actualAwayGoals: number;
  actualOutcome: Outcome;
  ml: MlBase & { correct: boolean };
  poisson: PoissonBase & { correct: boolean };
}

export interface UpcomingMatch {
  played: false;
  homeTeam: string;
  awayTeam: string;
  date: string;
  ml: MlBase;
  poisson: PoissonBase;
}

export type MatchResult = PlayedMatch | UpcomingMatch;

export interface ResultsSummary {
  mlCorrect: number;
  mlTotal: number;
  poissonCorrect: number;
  poissonTotal: number;
}

export interface ResultsResponse {
  matches: MatchResult[];
  summary: ResultsSummary;
  earlierMatchDate: string | null;
  laterMatchDate: string | null;
}

export interface ApiMatchResult {
  homeTeam: string;
  awayTeam: string;
  date: string;
  actualHomeGoals: number | null;
  actualAwayGoals: number | null;
  actualOutcome: Outcome | null;
  ml: MlBase & { correct: boolean | null };
  poisson: PoissonBase & { correct: boolean | null };
}

export interface ApiResultsResponse {
  matches: ApiMatchResult[];
  summary: ResultsSummary;
  earlierMatchDate: string | null;
  laterMatchDate: string | null;
}
