import type { MatchweekDetail, MatchweekSummary, PredictResponse, Team } from './types';

export async function fetchTeams(): Promise<Team[]> {
  const response = await fetch('/api/teams');
  if (!response.ok) {
    throw new Error(`failed to fetch teams: ${response.status}`);
  }
  return response.json();
}

export async function fetchPrediction(homeTeamId: string, awayTeamId: string): Promise<PredictResponse> {
  const response = await fetch('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ homeTeamId, awayTeamId }),
  });
  if (!response.ok) {
    throw new Error(`prediction failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchMatchweeks(): Promise<MatchweekSummary[]> {
  const response = await fetch('/api/matchweeks');
  if (!response.ok) {
    throw new Error(`failed to fetch matchweeks: ${response.status}`);
  }
  return response.json();
}

export async function fetchMatchweek(week: number): Promise<MatchweekDetail> {
  const response = await fetch(`/api/matchweeks/${week}`);
  if (!response.ok) {
    throw new Error(`failed to fetch matchweek ${week}: ${response.status}`);
  }
  return response.json();
}
