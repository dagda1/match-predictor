import type { Client } from 'pg';
import { z } from 'zod';

import type { MatchInfo } from './matchSchema';
import { matchInfoSchema } from './matchSchema';
import { MATCH_COLUMN_FIELDS, persistMatches } from './persistMatches';
import type { SeasonSummary } from './scrapeLeague';
import { findSeasons, scrapeLeagueMatchIds, scrapeSeason } from './scrapeLeague';
import { scrapeMatch } from './scrapeMatch';

export interface ScrapedSeason {
  season: string;
  scrapedCount: number;
  matches: MatchInfo[];
}

async function storedMatchIds(db: Client, season: string): Promise<Set<string>> {
  const result = await db.query<{ id: string }>('SELECT id FROM matches WHERE season = $1', [season]);

  return new Set(result.rows.map((row) => row.id));
}

export async function saveSeason(db: Client, summary: SeasonSummary): Promise<void> {
  await db.query(
    `INSERT INTO seasons (season, first_match_date, last_match_date, ended, teams)
     VALUES ($1, $2, $3, $4, $5)
     ON CONFLICT (season) DO UPDATE SET
       first_match_date = EXCLUDED.first_match_date,
       last_match_date = EXCLUDED.last_match_date,
       ended = EXCLUDED.ended,
       teams = EXCLUDED.teams`,
    [summary.season, summary.firstMatchDate, summary.lastMatchDate, summary.ended, summary.teams],
  );
}

function selectColumn(column: string, field: string): string {
  if (column === 'date') {
    return `to_char(date, 'YYYY-MM-DD HH24:MI:SS') AS date`;
  }

  return `${column} AS "${field}"`;
}

const SEASON_MATCHES_SQL = `
  SELECT ${Object.entries(MATCH_COLUMN_FIELDS).map(([column, field]) => selectColumn(column, field)).join(', ')}
  FROM matches
  WHERE season = $1
  ORDER BY date, id
`;

async function loadSeasonMatches(db: Client, season: string): Promise<MatchInfo[]> {
  const result = await db.query(SEASON_MATCHES_SQL, [season]);

  return z.array(matchInfoSchema).parse(result.rows);
}

export async function scrapeToDb(db: Client, now: Date): Promise<ScrapedSeason[]> {
  const scraped: ScrapedSeason[] = [];

  for (const season of await findSeasons(now)) {
    const matchIds = await scrapeLeagueMatchIds(season, await storedMatchIds(db, season));

    const matches = [];

    for (const id of matchIds) {
      matches.push(await scrapeMatch(id));
    }

    await persistMatches(db, matches);
    await saveSeason(db, await scrapeSeason(season));

    scraped.push({ season, scrapedCount: matchIds.length, matches: await loadSeasonMatches(db, season) });
  }

  return scraped;
}
