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
