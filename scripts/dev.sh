#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi
docker compose up -d --wait db mail
(cd services/analytics-api && ../../.venv/bin/alembic upgrade head && ../../.venv/bin/python -c 'from app.config import settings; from app.seed import seed; seed() if settings.demo_mode else None')
(cd services/analytics-api && exec ../../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000) &
api_pid=$!
web_pid=""
cleanup() {
  kill "$api_pid" 2>/dev/null || true
  if [[ -n "$web_pid" ]]; then kill "$web_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/api/v1/health >/dev/null; then break; fi
  if ! kill -0 "$api_pid" 2>/dev/null; then echo 'API exited before readiness' >&2; exit 1; fi
  sleep 1
done
curl --fail --silent http://127.0.0.1:8000/api/v1/health >/dev/null
(cd apps/web && NEXT_TELEMETRY_DISABLED=1 exec ../../node_modules/.bin/next dev --hostname 0.0.0.0) &
web_pid=$!
wait "$web_pid"
