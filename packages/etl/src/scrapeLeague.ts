import { assert } from '@cutting/assert';

interface LeagueEntry {
  id: string;
  isResult: boolean;
  datetime: string;
}

export async function scrapeLeagueMatchIds(season: string, after?: string): Promise<string[]> {
  const response = await fetch(`https://understat.com/getLeagueData/EPL/${season}`, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Referer': `https://understat.com/league/EPL/${season}`,
    },
  });
  assert(response.ok, `failed to fetch league data for season ${season}: ${response.status}`);

  const data = await response.json();

  return data.dates
    .filter((entry: LeagueEntry) => entry.isResult && (!after || entry.datetime > after))
    .map((entry: LeagueEntry) => entry.id);
}
