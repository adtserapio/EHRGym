#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  if [[ -n "${ENV_SERVER_PID:-}" ]]; then
    kill "$ENV_SERVER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

export DATABASE_URL="${DATABASE_URL:-file:/app/prisma/dev.db}"
export PORT="${PORT:-3000}"
export EHR_BASE_URL="${EHR_BASE_URL:-http://127.0.0.1:${PORT}}"

npx prisma generate
npx prisma db push
npx prisma db seed

uvicorn env_server.app.main:app --host 0.0.0.0 --port 8000 &
ENV_SERVER_PID=$!

npm run start --workspace @ehrgym/ehr -- --hostname 0.0.0.0 --port "$PORT"
