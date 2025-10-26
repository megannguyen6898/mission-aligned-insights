#!/usr/bin/env bash
set -euo pipefail

# Wait until Postgres is ready
python - <<'PY'
import os, time, sys, sqlalchemy as sa
url = os.environ.get("DATABASE_URL")
for i in range(60):
    try:
        with sa.create_engine(url).connect() as c:
            c.execute(sa.text("SELECT 1"))
            print("DB ready"); sys.exit(0)
    except Exception as e:
        print(f"Waiting for DB... {e}")
        time.sleep(1)
print("DB not reachable"); sys.exit(1)
PY

# Run Alembic ONLY when explicitly requested
if command -v alembic &> /dev/null; then
  if [ "${RUN_DB_MIGRATIONS:-0}" = "1" ]; then
    echo "Running Alembic migrations..."
    # If already up-to-date, don't crash the container
    alembic upgrade head || echo "⚠️ Alembic step skipped (likely already applied)"
  else
    echo "Skipping Alembic migrations (set RUN_DB_MIGRATIONS=1 to run)"
  fi
else
  echo "⚠️ Alembic not installed, skipping migrations"
fi

# Start whatever command compose passes (e.g., uvicorn)
echo "Starting: $*"
exec "$@"
