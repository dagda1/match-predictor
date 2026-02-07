import { describe, expect, it } from 'vitest';

import expectedMatches from './expected-matches.json';
import { matchInfoSchema } from './matchSchema';
import { scrapeMatch } from './scrapeMatch';

const matchIds = expectedMatches.map((m) => m.id);

describe('scrapeMatch', () => {
  it.each(matchIds)('scrapes match %s and matches expected data', async (matchId) => {
    const scraped = await scrapeMatch(matchId);
    const expected = expectedMatches.find((m) => m.id === matchId)!;
    expect(scraped.homeTeam).toBe(expected.homeTeam);
    expect(scraped.awayTeam).toBe(expected.awayTeam);
    expect(scraped.homeGoals).toBe(expected.homeGoals);
    expect(scraped.awayGoals).toBe(expected.awayGoals);
    expect(scraped.homeXg).toBe(expected.homeXg);
    expect(scraped.awayXg).toBe(expected.awayXg);
  });

  it.each(matchIds)('match %s passes schema validation', async (matchId) => {
    const scraped = await scrapeMatch(matchId);
    const result = matchInfoSchema.safeParse(scraped);
    expect(result.success).toBe(true);
  });
});
