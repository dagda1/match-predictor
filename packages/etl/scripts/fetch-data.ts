import { access, readFile, mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

import type { MatchInfo } from '../src/matchSchema';
import { scrapeLeagueMatchIds } from '../src/scrapeLeague';
import { scrapeMatch } from '../src/scrapeMatch';

const DATA_DIR = join(import.meta.dirname, '../data');
const SEASONS = ['2024', '2025'];

async function loadExisting(season: string): Promise<MatchInfo[]> {
  const filePath = join(DATA_DIR, `matches-${season}.json`);
  try {
    await access(filePath);
  } catch {
    return [];
  }
  const raw = await readFile(filePath, 'utf-8');
  return JSON.parse(raw) as MatchInfo[];
}

function maxDate(matches: MatchInfo[]): string | undefined {
  if (matches.length === 0) {
    return undefined;
  }
  return matches.reduce((max, m) => (m.date > max ? m.date : max), matches[0].date);
}

async function fetchSeason(season: string): Promise<void> {
  const existing = await loadExisting(season);
  const after = maxDate(existing);

  console.log(`\n${season} season: ${existing.length} existing matches${after ? `, last: ${after}` : ''}`);

  const newIds = await scrapeLeagueMatchIds(season, after);
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
