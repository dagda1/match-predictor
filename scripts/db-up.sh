#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if grep -n "rds_iam" packages/db-bootstrap/sql/bootstrap.sql; then
  echo "bootstrap.sql also runs in local Postgres, which has no rds_iam role. Put RDS-only grants in packages/db-bootstrap/sql/aws-iam.sql." >&2
  exit 1
fi

docker compose up -d --wait postgres

cd packages/ml
DB_HOST=localhost \
DB_USER=match_predictor_migrator \
DB_PASSWORD=migrator \
DB_NAME=match_predictor \
DB_SSLMODE=disable \
  uv run alembic upgrade head

echo
echo "Local DB ready at localhost:5432/match_predictor"
echo "  Master:    psql 'postgresql://local:local@localhost:5432/match_predictor'"
echo "  Migrator:  psql 'postgresql://match_predictor_migrator:migrator@localhost:5432/match_predictor'"
echo "  App:       psql 'postgresql://match_predictor_app:app@localhost:5432/match_predictor'"
