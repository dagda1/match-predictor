#!/usr/bin/env bash
set -euo pipefail

set -a
source .env
set +a

docker compose up -d
pnpm refresh
uv run --directory packages/ml alembic upgrade head
uv run python scripts/seed-db.py
