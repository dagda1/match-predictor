#!/usr/bin/env bash
set -euo pipefail

set -a
source .env
set +a

./scripts/db-up.sh
pnpm refresh
uv run --directory packages/ml alembic upgrade head
uv run --directory packages/ml python ../../scripts/seed-db.py
