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
