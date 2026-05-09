import { gunzipSync } from 'node:zlib';

import type { FirehoseTransformationHandler, FirehoseTransformationResultRecord } from 'aws-lambda';
import { z } from 'zod';

const cloudWatchLogsEnvelopeSchema = z.object({
  messageType: z.string(),
  logGroup: z.string(),
  logStream: z.string(),
  logEvents: z.array(
    z.object({
      id: z.string(),
      timestamp: z.number(),
      message: z.string(),
    }),
  ),
});

export function transformRecord(record: { recordId: string; data: string }): FirehoseTransformationResultRecord {
  const decoded = Buffer.from(record.data, 'base64');
  const unzipped = gunzipSync(decoded).toString('utf-8');
  const envelope = cloudWatchLogsEnvelopeSchema.parse(JSON.parse(unzipped));

  if (envelope.messageType !== 'DATA_MESSAGE') {
    return { recordId: record.recordId, result: 'Dropped', data: '' };
  }

  const lines = envelope.logEvents.map((event) =>
    JSON.stringify({
      timestamp: event.timestamp,
      message: event.message,
      logGroup: envelope.logGroup,
      logStream: envelope.logStream,
    }),
  );

  const joined = `${lines.join('\n')}\n`;

  return {
    recordId: record.recordId,
    result: 'Ok',
    data: Buffer.from(joined).toString('base64'),
  };
}

export const handler: FirehoseTransformationHandler = async (event) => {
  return { records: event.records.map(transformRecord) };
};
