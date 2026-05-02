# Database

## Local development

Spin up Postgres locally with the same users and schema as RDS.

```bash
pnpm db:up
```

This:
1. Starts Postgres in Docker (image `postgres:17`, port 5432).
2. Runs `packages/db-bootstrap/sql/bootstrap.sql` to create `match_predictor_migrator` and `match_predictor_app` with the same grants as production.
3. Runs `packages/db-bootstrap/sql/local-passwords.sql` to set passwords (locally only — AWS uses IAM tokens instead).
4. Runs `alembic upgrade head` as the migrator.

### Connect

```bash
psql 'postgresql://local:local@localhost:5432/match_predictor'                       # master
psql 'postgresql://match_predictor_migrator:migrator@localhost:5432/match_predictor' # ddl
psql 'postgresql://match_predictor_app:app@localhost:5432/match_predictor'           # dml
```

### Reset

```bash
pnpm db:reset   # drops the volume and re-runs bootstrap + migrations
pnpm db:down    # stop without dropping data
```

### Source of truth for grants

`packages/db-bootstrap/sql/bootstrap.sql` is shared between Docker init and the AWS bootstrap Lambda. Edit it once, both environments pick it up.

The platform-specific bits are tiny:
- `aws-iam.sql` — `GRANT rds_iam` (only on AWS).
- `local-passwords.sql` — `ALTER USER ... WITH PASSWORD` (only locally).

## TLS — RDS CA bundle

The scraper Lambda connects to RDS over TLS and validates the server certificate against the AWS RDS global CA bundle.

The bundle lives at `packages/etl/src/rds-ca-bundle.pem`. It contains every root CA AWS uses to sign RDS instance certs in every region. It is downloaded once from the AWS-published URL below and committed to the repo.

### Why it's checked in

- The Lambda runs in a private subnet with no internet route to AWS public endpoints during cold start. Downloading at runtime would require a NAT route or a VPC endpoint we don't have.
- esbuild needs the file at bundle time to copy it into the Lambda image (via the `IncludeRdsCaBundle` command hook in `packages/deploy/.../functions.py`).

### How it gets into the Lambda

1. CDK `NodejsFunction` bundles the scraper.
2. The `IncludeRdsCaBundle` command hook runs `cp packages/etl/src/rds-ca-bundle.pem $outputDir/` after esbuild finishes.
3. At runtime, `db.ts` reads it via `readFileSync(join(import.meta.dirname, 'rds-ca-bundle.pem'))` and passes it to `pg` as `ssl: { ca: bundle, rejectUnauthorized: true }`.

Locally the bundle is never loaded — `DB_SSLMODE=disable` skips the SSL config entirely.

### When to refresh

AWS rotates the RDS CA bundle every few years. Symptoms of an expired or rotated bundle:
- Scraper Lambda fails with `Error: unable to verify the first certificate` or `CERT_HAS_EXPIRED`.
- AWS publishes a notice in the RDS console / health dashboard ahead of rotation.

To refresh:

```bash
curl -sSf -o packages/etl/src/rds-ca-bundle.pem \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

Commit and deploy. Per-region bundles are also available at `https://truststore.pki.rds.amazonaws.com/<region>/<region>-bundle.pem` if a smaller payload is wanted later.

## AWS — RDS instance status

```bash
aws rds describe-db-instances \
  --query "DBInstances[].{Id:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Endpoint:Endpoint.Address,Port:Endpoint.Port}" \
  --output table
```

## AWS — bootstrap resources deployed

```bash
aws cloudformation describe-stack-resources \
  --stack-name DeployStack \
  --query "StackResources[?contains(LogicalResourceId, 'Bootstrap')].[LogicalResourceId,ResourceStatus,PhysicalResourceId]" \
  --output table
```

## AWS — tail bootstrap Lambda logs

```bash
aws logs tail "/aws/lambda/DeployStack-DatabaseBootstrapHandlerFunction53F127-6d7FnL3CRGae" --since 24h
```

## AWS — tail migration Lambda logs

```bash
aws logs tail "/aws/lambda/DeployStack-DatabaseMigrationHandlerFunction71FE85-3g41IqYpfNUU" --since 24h
```
