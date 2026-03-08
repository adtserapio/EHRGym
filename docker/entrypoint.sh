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

# ── Start nginx FIRST so HF Spaces sees port 7860 open immediately ──
if command -v nginx &>/dev/null && [[ -f /app/docker/nginx.conf ]]; then
  echo "[entrypoint] Starting nginx reverse proxy on :7860 …"
  nginx -c /app/docker/nginx.conf -g 'daemon off;' &
  NGINX_PID=$!
  echo "[entrypoint] nginx started (pid=$NGINX_PID)."
fi

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

echo "[entrypoint] All services launched (nginx=$NGINX_PID, env=$ENV_SERVER_PID, ehr=$EHR_PID). EHRGym is ready."

# ── Wait on nginx (foreground process for Docker) ──
if [[ -n "${NGINX_PID:-}" ]]; then
  wait "$NGINX_PID"
else
  wait "$EHR_PID"
fi

