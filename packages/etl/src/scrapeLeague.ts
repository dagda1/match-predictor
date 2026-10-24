import { assert } from '@cutting/assert';
import { z } from 'zod';

const FIRST_SEASON = 2024;

const leagueEntrySchema = z.object({
  id: z.string(),
  isResult: z.boolean(),
  datetime: z.string(),
});

const leagueDataSchema = z.object({
  dates: z.array(leagueEntrySchema),
});

type LeagueEntry = z.infer<typeof leagueEntrySchema>;

async function fetchLeagueData(season: string): Promise<z.infer<typeof leagueDataSchema>> {
  const response = await fetch(`https://understat.com/getLeagueData/EPL/${season}`, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      Referer: `https://understat.com/league/EPL/${season}`,
    },
  });
  assert(response.ok, `failed to fetch league data for season ${season}: ${response.status}`);

  return leagueDataSchema.parse(await response.json());
}

function toUnderstatDate(date: Date): string {
  return date.toISOString().slice(0, 19).replace('T', ' ');
}

function sortedDates(entries: LeagueEntry[]): string[] {
  return entries.map((entry) => entry.datetime).sort();
}

export async function findSeasons(now: Date): Promise<string[]> {
  const kickedOff = toUnderstatDate(now);
  const seasons: string[] = [];

  for (let year = FIRST_SEASON; ; year += 1) {
    const season = String(year);
    const data = await fetchLeagueData(season);
    const dates = sortedDates(data.dates);

    if (dates.length === 0 || dates[0] > kickedOff) {
      return seasons;
    }

    seasons.push(season);
  }
}

export async function scrapeLeagueMatchIds(season: string, existingIds: Set<string>): Promise<string[]> {
  const data = await fetchLeagueData(season);

  return data.dates
    .filter((entry) => entry.isResult && !existingIds.has(entry.id))
    .map((entry) => entry.id);
}
