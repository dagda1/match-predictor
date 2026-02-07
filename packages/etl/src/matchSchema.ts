import { z } from 'zod';

const numericString = z.string().regex(/^\d+$/);
const floatString = z.string().regex(/^\d+(\.\d+)?$/);

export const matchInfoSchema = z.object({
  id: numericString,
  date: z.string().regex(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/),
  season: numericString,
  homeTeam: z.string().min(1),
  awayTeam: z.string().min(1),
  homeGoals: numericString,
  awayGoals: numericString,
  homeXg: floatString,
  awayXg: floatString,
  homeShots: numericString,
  awayShots: numericString,
  homeShotsOnTarget: numericString,
  awayShotsOnTarget: numericString,
  homeDeep: numericString,
  awayDeep: numericString,
  homePpda: floatString,
  awayPpda: floatString,
  homeWinProb: floatString,
  drawProb: floatString,
  awayWinProb: floatString,
});

export type MatchInfo = z.infer<typeof matchInfoSchema>;
