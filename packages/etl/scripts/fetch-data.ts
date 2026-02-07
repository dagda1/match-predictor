import { mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

import { scrapeLeagueMatchIds } from '../src/scrapeLeague';
import { scrapeMatch } from '../src/scrapeMatch';

const DATA_DIR = join(import.meta.dirname, '../data');
const SEASONS = ['2024', '2025'];

async function fetchSeason(season: string): Promise<void> {
  console.log(`\nFetching match IDs for ${season} season...`);
  const matchIds = await scrapeLeagueMatchIds(season);
  console.log(`Found ${matchIds.length} completed matches`);

  const matches = [];
  for (const [i, id] of matchIds.entries()) {
    process.stdout.write(`\rScraping match ${i + 1}/${matchIds.length} (${id})`);
    const match = await scrapeMatch(id);
    matches.push(match);
  }

  const outPath = join(DATA_DIR, `matches-${season}.json`);
  await writeFile(outPath, JSON.stringify(matches, null, 2));
  console.log(`\nWrote ${matches.length} matches to ${outPath}`);
}

await mkdir(DATA_DIR, { recursive: true });

for (const season of SEASONS) {
  await fetchSeason(season);
}

console.log('\nDone.');
