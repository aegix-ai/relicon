#!/usr/bin/env bash
# Zero-key demo: local Postgres if docker works, SQLite otherwise. No keys, no cloud.
set -euo pipefail
cd "$(dirname "$0")/.."
if docker compose up -d --wait postgres >/dev/null 2>&1; then
  export DATABASE_URL="postgresql://relicon:relicon@localhost:55432/relicon"
  echo "DB: local Postgres (docker compose)"
else
  echo "DB: docker not usable here, falling back to SQLite at .relicon/relicon.db"
fi
.venv/bin/relicon demo
echo
echo "Starting dashboard: http://localhost:5000/dashboard  (engine API on :8000)"
exec bash scripts/dashboard.sh
