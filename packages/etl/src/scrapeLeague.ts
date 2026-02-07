import { assert } from '@cutting/assert';

export async function scrapeLeagueMatchIds(season: string): Promise<string[]> {
  const response = await fetch(`https://understat.com/getLeagueData/EPL/${season}`, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Referer': `https://understat.com/league/EPL/${season}`,
    },
  });
  assert(response.ok, `failed to fetch league data for season ${season}: ${response.status}`);

  const data = await response.json();

  return data.dates
    .filter((entry: { isResult: boolean }) => entry.isResult)
    .map((entry: { id: string }) => entry.id);
}
