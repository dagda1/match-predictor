import type { PredictResponse, ResultsResponse, Team } from './types';

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

export async function fetchResults(startDate: string, endDate?: string): Promise<ResultsResponse> {
  const params = new URLSearchParams({ startDate });
  if (endDate) {
    params.set('endDate', endDate);
  }
  const response = await fetch(`/api/results?${params}`);
  if (!response.ok) {
    throw new Error(`failed to fetch results: ${response.status}`);
  }
  return response.json();
}
