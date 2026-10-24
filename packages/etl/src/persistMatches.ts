import type { Client } from 'pg';
import type { MatchInfo } from './matchSchema';

export const MATCH_COLUMN_FIELDS = {
  id: 'id',
  date: 'date',
  season: 'season',
  home_team: 'homeTeam',
  away_team: 'awayTeam',
  home_goals: 'homeGoals',
  away_goals: 'awayGoals',
  home_xg: 'homeXg',
  away_xg: 'awayXg',
  home_shots: 'homeShots',
  away_shots: 'awayShots',
  home_shots_on_target: 'homeShotsOnTarget',
  away_shots_on_target: 'awayShotsOnTarget',
  home_deep: 'homeDeep',
  away_deep: 'awayDeep',
  home_ppda: 'homePpda',
  away_ppda: 'awayPpda',
  home_win_prob: 'homeWinProb',
  draw_prob: 'drawProb',
  away_win_prob: 'awayWinProb',
} as const satisfies Record<string, keyof MatchInfo>;

const MATCH_COLUMNS = Object.keys(MATCH_COLUMN_FIELDS);
const MATCH_FIELDS = Object.values(MATCH_COLUMN_FIELDS);

function matchValues(match: MatchInfo): (string | number)[] {
  return MATCH_FIELDS.map((field) => match[field]);
}

function uniqueTeamNames(matches: MatchInfo[]): string[] {
  const names = new Set<string>();

  for (const match of matches) {
    names.add(match.homeTeam);
    names.add(match.awayTeam);
  }

  return [...names];
}

function buildBatchInsert(rowCount: number): string {
  const columnCount = MATCH_COLUMNS.length;
  const valueGroups: string[] = [];

  for (let rowIndex = 0; rowIndex < rowCount; rowIndex += 1) {
    const placeholders: string[] = [];

    for (let colIndex = 0; colIndex < columnCount; colIndex += 1) {
      placeholders.push(`$${rowIndex * columnCount + colIndex + 1}`);
    }

    valueGroups.push(`(${placeholders.join(', ')})`);
  }

  const updateAssignments = MATCH_COLUMNS
    .filter((column) => column !== 'id')
    .map((column) => `${column} = EXCLUDED.${column}`)
    .join(', ');

  return `
    INSERT INTO matches (${MATCH_COLUMNS.join(', ')})
    VALUES ${valueGroups.join(', ')}
    ON CONFLICT (id) DO UPDATE SET ${updateAssignments}
  `;
}

export async function persistMatches(client: Client, matches: MatchInfo[]): Promise<void> {
  if (matches.length === 0) {
    return;
  }

  await client.query('BEGIN');

  for (const teamName of uniqueTeamNames(matches)) {
    await client.query('INSERT INTO teams (name) VALUES ($1) ON CONFLICT (name) DO NOTHING', [teamName]);
  }

  const sql = buildBatchInsert(matches.length);
  const values = matches.flatMap((match) => matchValues(match));
  await client.query(sql, values);

  await client.query('COMMIT');
}
