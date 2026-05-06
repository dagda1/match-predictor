import type {
  ApiMatchResult,
  ApiResultsResponse,
  MatchResult,
  ResultsResponse,
} from './types';

function toMatchResult(api: ApiMatchResult): MatchResult {
  if (
    api.actualOutcome === null ||
    api.actualHomeGoals === null ||
    api.actualAwayGoals === null ||
    api.ml.correct === null ||
    api.poisson.correct === null
  ) {
    return {
      played: false,
      homeTeam: api.homeTeam,
      awayTeam: api.awayTeam,
      date: api.date,
      ml: {
        homeWin: api.ml.homeWin,
        draw: api.ml.draw,
        awayWin: api.ml.awayWin,
        predictedOutcome: api.ml.predictedOutcome,
        topScore: api.ml.topScore,
      },
      poisson: {
        homeWin: api.poisson.homeWin,
        draw: api.poisson.draw,
        awayWin: api.poisson.awayWin,
        predictedOutcome: api.poisson.predictedOutcome,
        homeLambda: api.poisson.homeLambda,
        awayLambda: api.poisson.awayLambda,
        topScore: api.poisson.topScore,
      },
    };
  }

  return {
    played: true,
    homeTeam: api.homeTeam,
    awayTeam: api.awayTeam,
    date: api.date,
    actualHomeGoals: api.actualHomeGoals,
    actualAwayGoals: api.actualAwayGoals,
    actualOutcome: api.actualOutcome,
    ml: {
      homeWin: api.ml.homeWin,
      draw: api.ml.draw,
      awayWin: api.ml.awayWin,
      predictedOutcome: api.ml.predictedOutcome,
      correct: api.ml.correct,
      topScore: api.ml.topScore,
    },
    poisson: {
      homeWin: api.poisson.homeWin,
      draw: api.poisson.draw,
      awayWin: api.poisson.awayWin,
      predictedOutcome: api.poisson.predictedOutcome,
      correct: api.poisson.correct,
      homeLambda: api.poisson.homeLambda,
      awayLambda: api.poisson.awayLambda,
      topScore: api.poisson.topScore,
    },
  };
}

export function toResultsResponse(api: ApiResultsResponse): ResultsResponse {
  return {
    matches: api.matches.map(toMatchResult),
    summary: api.summary,
    earlierMatchDate: api.earlierMatchDate,
    laterMatchDate: api.laterMatchDate,
  };
}
