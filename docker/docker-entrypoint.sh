#!/bin/sh
set -e

# ── Cron schedule for data collection ────────────────────────────────────────
# Default: weekdays at 18:00 Beijing time (TZ=Asia/Shanghai set in Dockerfile)
# Override with COLLECT_CRON env var, e.g. "*/30 9-15 * * 1-5" for every 30 min
# during trading hours.
# Set COLLECT_ENABLED=0 to disable scheduled collection entirely.
# ─────────────────────────────────────────────────────────────────────────────

COLLECT_ENABLED="${COLLECT_ENABLED:-1}"
COLLECT_CRON="${COLLECT_CRON:-0 18 * * 1-5}"

if [ "$COLLECT_ENABLED" = "1" ]; then
    # Build cron job: run collector, log output
    echo "${COLLECT_CRON} cd /app && python src/collect_stocks.py >> /app/logs/collect.log 2>&1" \
        > /etc/cron.d/stock-collect
    chmod 0644 /etc/cron.d/stock-collect
    crontab /etc/cron.d/stock-collect
    echo "[entrypoint] Scheduled collection: ${COLLECT_CRON}"

    # Start cron daemon in background
    cron
else
    echo "[entrypoint] Scheduled collection disabled (COLLECT_ENABLED=0)"
fi

# ── Start Flask app ──────────────────────────────────────────────────────────
echo "[entrypoint] Starting web server on :5000 ..."
exec python -m gunicorn \
    --bind 0.0.0.0:5000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout 120 \
    --access-logfile - \
    src.server:app 2>/dev/null \
  || exec python -c "
import sys; sys.path.insert(0,'.')
from src.server import app
app.run(host='0.0.0.0', port=5000)
"
