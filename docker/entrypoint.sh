#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting EHRGym …"

cleanup() {
  echo "[entrypoint] Shutting down …"
  kill "${NGINX_PID:-}" "${ENV_SERVER_PID:-}" "${EHR_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

export DATABASE_URL="${DATABASE_URL:-file:/app/prisma/dev.db}"
export PORT="${PORT:-3000}"
export EHR_BASE_URL="${EHR_BASE_URL:-http://127.0.0.1:${PORT}}"
export EHRGYM_SERVER_URL="${EHRGYM_SERVER_URL:-http://127.0.0.1:8000}"

# ── Database setup (only if DB file is missing) ──
DB_PATH="/app/prisma/dev.db"
if [[ ! -f "$DB_PATH" ]]; then
  echo "[entrypoint] Database not found — seeding …"
  npx prisma generate
  npx prisma db push
  npx prisma db seed
  echo "[entrypoint] Database ready."
else
  echo "[entrypoint] Database exists at $DB_PATH — skipping seed."
fi

# ── Start env server (FastAPI + Playwright) on :8000 ──
echo "[entrypoint] Starting env server on :8000 …"
uvicorn env_server.app.main:app --host 127.0.0.1 --port 8000 &
ENV_SERVER_PID=$!

# ── Start Next.js EHR on internal :3000 ──
echo "[entrypoint] Starting Next.js EHR on :${PORT} …"
npm run start --workspace @ehrgym/ehr -- --hostname 127.0.0.1 --port "$PORT" &
EHR_PID=$!

# ── Wait briefly for services to start ──
sleep 3
echo "[entrypoint] Services started (env=$ENV_SERVER_PID, ehr=$EHR_PID)."

# ── Start nginx reverse-proxy on :7860 (the HF Spaces public port) ──
if command -v nginx &>/dev/null && [[ -f /app/docker/nginx.conf ]]; then
  echo "[entrypoint] Starting nginx reverse proxy on :7860 …"
  nginx -c /app/docker/nginx.conf -g 'daemon off;' &
  NGINX_PID=$!
  echo "[entrypoint] nginx started (pid=$NGINX_PID). EHRGym is ready."
  wait "$NGINX_PID"
else
  # Fallback (local dev / docker-compose): no nginx, just wait on EHR
  echo "[entrypoint] nginx not found — services on :${PORT} (EHR) and :8000 (env server)"
  wait "$EHR_PID"
fi

