import type { Client } from 'pg';
import type { MatchInfo } from './matchSchema';

type ColumnGetter = (match: MatchInfo) => string | number;

const MATCH_COLUMN_MAP = {
  id: (match) => match.id,
  date: (match) => match.date,
  season: (match) => match.season,
  home_team: (match) => match.homeTeam,
  away_team: (match) => match.awayTeam,
  home_goals: (match) => match.homeGoals,
  away_goals: (match) => match.awayGoals,
  home_xg: (match) => match.homeXg,
  away_xg: (match) => match.awayXg,
  home_shots: (match) => match.homeShots,
  away_shots: (match) => match.awayShots,
  home_shots_on_target: (match) => match.homeShotsOnTarget,
  away_shots_on_target: (match) => match.awayShotsOnTarget,
  home_deep: (match) => match.homeDeep,
  away_deep: (match) => match.awayDeep,
  home_ppda: (match) => match.homePpda,
  away_ppda: (match) => match.awayPpda,
  home_win_prob: (match) => match.homeWinProb,
  draw_prob: (match) => match.drawProb,
  away_win_prob: (match) => match.awayWinProb,
} satisfies Record<string, ColumnGetter>;

const MATCH_COLUMNS = Object.keys(MATCH_COLUMN_MAP);
const MATCH_GETTERS: ColumnGetter[] = Object.values(MATCH_COLUMN_MAP);

function matchValues(match: MatchInfo): (string | number)[] {
  return MATCH_GETTERS.map((getter) => getter(match));
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
