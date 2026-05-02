import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { z } from 'zod';

import { createClient } from '../src/db';
import { matchInfoSchema } from '../src/matchSchema';
import { persistMatches } from '../src/persistMatches';

const matchesArraySchema = z.array(matchInfoSchema);

async function loadMatches(season: string): Promise<unknown[]> {
  const path = resolve(import.meta.dirname, '..', 'data', `matches-${season}.json`);
  const raw = await readFile(path, 'utf-8');
  return JSON.parse(raw);
}

async function main(): Promise<void> {
  process.env.DB_HOST ??= 'localhost';
  process.env.DB_USER ??= 'match_predictor_app';
  process.env.DB_PASSWORD ??= 'app';
  process.env.DB_NAME ??= 'match_predictor';
  process.env.DB_SSLMODE ??= 'disable';

  const db = await createClient();

  for (const season of ['2024', '2025']) {
    const raw = await loadMatches(season);
    const matches = matchesArraySchema.parse(raw);
    await persistMatches(db, matches);
    console.log(`seeded season ${season}: ${matches.length} matches`);
  }

  const counts = await db.query<{ matches: string; teams: string }>(`
    SELECT
      (SELECT count(*) FROM matches)::text AS matches,
      (SELECT count(*) FROM teams)::text AS teams
  `);
  console.log('totals:', counts.rows[0]);

  await db.end();
}

await main();
