#!/usr/bin/env bash
# Auto-restarting wrapper for asagent on :8899 (crash recovery without systemd).
# Launch detached, e.g.: setsid nohup bash deploy/run-watchdog.sh > backend/watchdog.log 2>&1 < /dev/null &
set -u
cd /home/ubuntu/dev/asagent/backend
PY=/home/ubuntu/miniconda3/envs/as/bin/python
while true; do
  echo "[watchdog $(date -u +%FT%TZ)] starting uvicorn on :8899" >&2
  "$PY" -m uvicorn app.main:app --host 0.0.0.0 --port 8899
  code=$?
  echo "[watchdog $(date -u +%FT%TZ)] uvicorn exited ($code), restarting in 3s" >&2
  sleep 3
done
