import { assert } from '@cutting/assert';
import { Signer } from '@aws-sdk/rds-signer';
import { Client } from 'pg';

interface DbConfig {
  host: string;
  user: string;
  database: string;
  region: string;
  sslmode: string;
  password?: string;
}

function readConfig(): DbConfig {
  const host = process.env.DB_HOST;
  const user = process.env.DB_USER;
  const database = process.env.DB_NAME;

  assert(!!host, 'DB_HOST is required');
  assert(!!user, 'DB_USER is required');
  assert(!!database, 'DB_NAME is required');

  return {
    host,
    user,
    database,
    region: process.env.DB_REGION ?? 'us-west-2',
    sslmode: process.env.DB_SSLMODE ?? 'require',
    password: process.env.DB_PASSWORD,
  };
}

async function resolvePassword(config: DbConfig): Promise<string> {
  if (config.password !== undefined) {
    return config.password;
  }

  const signer = new Signer({
    hostname: config.host,
    port: 5432,
    region: config.region,
    username: config.user,
  });

  return signer.getAuthToken();
}

export async function createClient(): Promise<Client> {
  const config = readConfig();
  const password = await resolvePassword(config);

  const client = new Client({
    host: config.host,
    user: config.user,
    database: config.database,
    password,
    port: 5432,
    ssl: config.sslmode === 'disable' ? false : { rejectUnauthorized: false },
  });

  await client.connect();

  return client;
}
