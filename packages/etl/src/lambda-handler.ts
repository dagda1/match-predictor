import { PutObjectCommand, S3Client } from '@aws-sdk/client-s3';
import { SendMessageCommand, SQSClient } from '@aws-sdk/client-sqs';

import { scrapeLeagueMatchIds } from './scrapeLeague';
import { scrapeMatch } from './scrapeMatch';

const s3 = new S3Client({});
const sqs = new SQSClient({});
const BUCKET = process.env.BUCKET_NAME;
const QUEUE_URL = process.env.QUEUE_URL;

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

  await sqs.send(
    new SendMessageCommand({
      QueueUrl: QUEUE_URL,
      MessageBody: 'scrape-complete',
    }),
  );
}
