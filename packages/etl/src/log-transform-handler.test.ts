import { gzipSync } from 'node:zlib';

import { assert } from '@cutting/assert';
import { describe, expect, it } from 'vitest';

import { transformRecord } from './log-transform-handler';

const realEnvelope = {
  messageType: 'DATA_MESSAGE',
  owner: '313095418189',
  logGroup: '/aws/lambda/DeployStack-ApiApiFunctionAA82C666-POOunoG59B74',
  logStream: '2026/05/09/[$LATEST]6e99b6dc7ad14aa1a1c1c6511be6b0d9',
  subscriptionFilters: ['DeployStack-FirehoseSubscriptionFilter2A224098-KikOEUIpvZeV'],
  logEvents: [
    {
      id: '39657664412271498507074877030934581598874765928431353856',
      timestamp: 1778311175668,
      message: 'START RequestId: dd78440b-81cb-4ff0-a062-ed3ece272a8a Version: $LATEST\n',
    },
    {
      id: '39657664412316099997471938277217653035420062651443314689',
      timestamp: 1778311175670,
      message: 'END RequestId: dd78440b-81cb-4ff0-a062-ed3ece272a8a\n',
    },
    {
      id: '39657664412316099997471938277217653035420062651443314690',
      timestamp: 1778311175670,
      message:
        'REPORT RequestId: dd78440b-81cb-4ff0-a062-ed3ece272a8a\tDuration: 1.63 ms\tBilled Duration: 2 ms\tMemory Size: 1024 MB\tMax Memory Used: 355 MB\t\n',
    },
  ],
};

function packRecord(envelope: unknown, recordId = 'r1') {
  return {
    recordId,
    data: gzipSync(Buffer.from(JSON.stringify(envelope))).toString('base64'),
  };
}

function unpackResultData(data: string): Array<Record<string, unknown>> {
  return Buffer.from(data, 'base64')
    .toString('utf-8')
    .split('\n')
    .filter((line) => line.length > 0)
    .map((line) => JSON.parse(line));
}

describe('transformRecord', () => {
  it('flattens a DATA_MESSAGE envelope into one NDJSON line per logEvent', () => {
    const result = transformRecord(packRecord(realEnvelope));

    expect(result.recordId).toBe('r1');
    expect(result.result).toBe('Ok');

    assert(result.data !== undefined, 'Ok records must have data');
    const lines = unpackResultData(result.data);
    expect(lines).toHaveLength(3);
  });

  it('preserves timestamp, message, logGroup and logStream on each line', () => {
    const result = transformRecord(packRecord(realEnvelope));
    assert(result.data !== undefined, 'Ok records must have data');
    const lines = unpackResultData(result.data);

    expect(lines[0]).toEqual({
      timestamp: 1778311175668,
      message: 'START RequestId: dd78440b-81cb-4ff0-a062-ed3ece272a8a Version: $LATEST\n',
      logGroup: realEnvelope.logGroup,
      logStream: realEnvelope.logStream,
    });
  });

  it('preserves recordId from the input', () => {
    const result = transformRecord(packRecord(realEnvelope, 'incoming-id-42'));
    expect(result.recordId).toBe('incoming-id-42');
  });

  it('drops CONTROL_MESSAGE records (e.g. CloudWatch Logs heartbeats)', () => {
    const controlMessage = { ...realEnvelope, messageType: 'CONTROL_MESSAGE' };
    const result = transformRecord(packRecord(controlMessage));

    expect(result.result).toBe('Dropped');
    expect(result.data).toBe('');
  });
});
