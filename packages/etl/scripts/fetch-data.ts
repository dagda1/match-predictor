import { access, readFile, mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

import { z } from 'zod';

import type { MatchInfo } from '../src/matchSchema';
import { matchInfoSchema } from '../src/matchSchema';
import { scrapeLeagueMatchIds } from '../src/scrapeLeague';
import { scrapeMatch } from '../src/scrapeMatch';

const matchesArraySchema = z.array(matchInfoSchema);

const DATA_DIR = join(import.meta.dirname, '../data');
const SEASONS = ['2024', '2025'];

async function loadExisting(season: string): Promise<MatchInfo[]> {
  const filePath = join(DATA_DIR, `matches-${season}.json`);
  const exists = await access(filePath).then(
    () => true,
    (error: NodeJS.ErrnoException) => {
      if (error.code === 'ENOENT') {
        return false;
      }
      throw error;
    },
  );
  if (!exists) {
    return [];
  }
  const raw = await readFile(filePath, 'utf-8');
  return matchesArraySchema.parse(JSON.parse(raw));
}

const force = process.argv.includes('--force');

async function fetchSeason(season: string): Promise<void> {
  const existing = force ? [] : await loadExisting(season);
  const existingIds = new Set(existing.map((m) => m.id));

  console.log(`\n${season} season: ${existing.length} existing matches`);

  const newIds = await scrapeLeagueMatchIds(season, existingIds);
  if (newIds.length === 0) {
    console.log('No new matches');
    return;
  }

  console.log(`${newIds.length} new matches to scrape`);

  const newMatches = [];
  for (const [i, id] of newIds.entries()) {
    process.stdout.write(`\rScraping match ${i + 1}/${newIds.length} (${id})`);
    const match = await scrapeMatch(id);
    newMatches.push(match);
  }

  const all = [...existing, ...newMatches];
  const outPath = join(DATA_DIR, `matches-${season}.json`);
  await writeFile(outPath, JSON.stringify(all, null, 2));
  console.log(`\nWrote ${all.length} matches to ${outPath} (+${newMatches.length} new)`);
}

await mkdir(DATA_DIR, { recursive: true });

for (const season of SEASONS) {
  await fetchSeason(season);
}

console.log('\nDone.');
