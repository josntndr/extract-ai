#!/usr/bin/env sh
# Production entrypoint.
#
# On managed hosts (Railway) the private network to Postgres isn't ready the
# instant the container starts, so `alembic upgrade head` can fail to connect on
# the first try. Retry a few times, then start the server regardless so the
# /health check can pass and the platform doesn't kill a salvageable container.

set -u

PORT="${PORT:-8000}"

n=0
until alembic upgrade head; do
  n=$((n + 1))
  if [ "$n" -ge 10 ]; then
    echo "[start] migrations still failing after $n attempts — starting server anyway"
    break
  fi
  echo "[start] alembic upgrade failed (attempt $n/10) — DB likely warming up, retrying in 3s..."
  sleep 3
done

echo "[start] launching uvicorn on 0.0.0.0:${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
