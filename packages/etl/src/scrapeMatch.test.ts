import { describe, expect, it } from 'vitest';

import expectedMatches from './expected-matches.json';
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
    expect(scraped.homeShots).toBe(expected.homeShots);
    expect(scraped.awayShots).toBe(expected.awayShots);
    expect(scraped.homeShotsOnTarget).toBe(expected.homeShotsOnTarget);
    expect(scraped.awayShotsOnTarget).toBe(expected.awayShotsOnTarget);
    expect(scraped.homeDeep).toBe(expected.homeDeep);
    expect(scraped.awayDeep).toBe(expected.awayDeep);
    expect(scraped.homePpda).toBe(expected.homePpda);
    expect(scraped.awayPpda).toBe(expected.awayPpda);
    expect(scraped.homeWinProb).toBe(expected.homeWinProb);
    expect(scraped.drawProb).toBe(expected.drawProb);
    expect(scraped.awayWinProb).toBe(expected.awayWinProb);
  });

  it.each(matchIds)('match %s returns numbers for numeric fields', async (matchId) => {
    const scraped = await scrapeMatch(matchId);
    expect(typeof scraped.homeGoals).toBe('number');
    expect(typeof scraped.homeXg).toBe('number');
    expect(typeof scraped.homePpda).toBe('number');
    expect(typeof scraped.homeWinProb).toBe('number');
  });
});
