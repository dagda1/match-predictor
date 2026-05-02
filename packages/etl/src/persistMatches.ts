import type { Client } from 'pg';
import type { MatchInfo } from './matchSchema';

const MATCH_COLUMNS = [
  'id',
  'date',
  'season',
  'home_team',
  'away_team',
  'home_goals',
  'away_goals',
  'home_xg',
  'away_xg',
  'home_shots',
  'away_shots',
  'home_shots_on_target',
  'away_shots_on_target',
  'home_deep',
  'away_deep',
  'home_ppda',
  'away_ppda',
  'home_win_prob',
  'draw_prob',
  'away_win_prob',
] as const;

function buildMatchInsert(): string {
  const placeholders = MATCH_COLUMNS.map((_, index) => `$${index + 1}`).join(', ');
  const updateAssignments = MATCH_COLUMNS
    .filter((column) => column !== 'id')
    .map((column) => `${column} = EXCLUDED.${column}`)
    .join(', ');

  return `
    INSERT INTO matches (${MATCH_COLUMNS.join(', ')})
    VALUES (${placeholders})
    ON CONFLICT (id) DO UPDATE SET ${updateAssignments}
  `;
}

function matchValues(match: MatchInfo): unknown[] {
  return [
    match.id,
    match.date,
    match.season,
    match.homeTeam,
    match.awayTeam,
    match.homeGoals,
    match.awayGoals,
    match.homeXg,
    match.awayXg,
    match.homeShots,
    match.awayShots,
    match.homeShotsOnTarget,
    match.awayShotsOnTarget,
    match.homeDeep,
    match.awayDeep,
    match.homePpda,
    match.awayPpda,
    match.homeWinProb,
    match.drawProb,
    match.awayWinProb,
  ];
}

function uniqueTeamNames(matches: MatchInfo[]): string[] {
  const names = new Set<string>();

  for (const match of matches) {
    names.add(match.homeTeam);
    names.add(match.awayTeam);
  }

  return [...names];
}

export async function persistMatches(client: Client, matches: MatchInfo[]): Promise<void> {
  const insertMatch = buildMatchInsert();

  await client.query('BEGIN');

  for (const teamName of uniqueTeamNames(matches)) {
    await client.query('INSERT INTO teams (name) VALUES ($1) ON CONFLICT (name) DO NOTHING', [teamName]);
  }

  for (const match of matches) {
    await client.query(insertMatch, matchValues(match));
  }

  await client.query('COMMIT');
}
