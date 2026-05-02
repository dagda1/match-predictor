import { assert } from '@cutting/assert';
import { PutObjectCommand, S3Client } from '@aws-sdk/client-s3';
import { SendMessageCommand, SQSClient } from '@aws-sdk/client-sqs';

import { createClient } from './db';
import { persistMatches } from './persistMatches';
import { scrapeLeagueMatchIds } from './scrapeLeague';
import { scrapeMatch } from './scrapeMatch';

const s3 = new S3Client({});
const sqs = new SQSClient({});
const BUCKET = process.env.BUCKET_NAME;
const QUEUE_URL = process.env.QUEUE_URL;
assert(!!BUCKET, 'BUCKET_NAME is required');
assert(!!QUEUE_URL, 'QUEUE_URL is required');

export async function handler(): Promise<void> {
  const db = await createClient();

  for (const season of ['2024', '2025']) {
    const matchIds = await scrapeLeagueMatchIds(season, new Set());

    const matches = [];

    for (const id of matchIds) {
      matches.push(await scrapeMatch(id));
    }

    await persistMatches(db, matches);

    const body = matches.map((match) => JSON.stringify(match)).join('\n');
    await s3.send(
      new PutObjectCommand({
        Bucket: BUCKET,
        Key: `matches/matches-${season}.json`,
        Body: body,
      }),
    );
  }

  await db.end();

  await sqs.send(
    new SendMessageCommand({
      QueueUrl: QUEUE_URL,
      MessageBody: 'scrape-complete',
    }),
  );
}
