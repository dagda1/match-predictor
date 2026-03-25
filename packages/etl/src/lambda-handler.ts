import { PutObjectCommand, S3Client } from '@aws-sdk/client-s3';

import { scrapeLeagueMatchIds } from './scrapeLeague';
import { scrapeMatch } from './scrapeMatch';

const s3 = new S3Client({});
const BUCKET = process.env.BUCKET_NAME;

export async function handler(): Promise<void> {
  for (const season of ['2024', '2025']) {
    const matchIds = await scrapeLeagueMatchIds(season, new Set());

    const matches = [];

    for (const id of matchIds) {
      matches.push(await scrapeMatch(id));
    }

    const body = matches.map((match) => JSON.stringify(match)).join('\n');
    await s3.send(
      new PutObjectCommand({
        Bucket: BUCKET,
        Key: `matches/matches-${season}.json`,
        Body: body,
      }),
    );
  }
}
