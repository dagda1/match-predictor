import type { MatchInfo } from './matchSchema';

export type { MatchInfo };

export async function scrapeMatch(_matchId: string): Promise<MatchInfo> {
  throw new Error('scrapeMatch not implemented');
}
