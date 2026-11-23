#!/usr/bin/env bash
# Engine API (FastAPI) + Next.js dashboard in demo mode (no Supabase needed).
set -euo pipefail
cd "$(dirname "$0")/.."
PNPM="$(command -v pnpm || echo 'npx -y pnpm@9.15.0')"
[ -d node_modules ] || $PNPM install --frozen-lockfile=false
(cd engine && ../.venv/bin/uvicorn server:app --port 8000 --log-level warning) &
API=$!
trap 'kill $API 2>/dev/null' EXIT
NEXT_PUBLIC_RELICON_DEMO=1 NEXT_PUBLIC_ENGINE_URL=http://localhost:8000 $PNPM dev
