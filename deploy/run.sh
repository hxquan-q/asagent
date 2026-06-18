#!/usr/bin/env bash
# Run asagent backend on 0.0.0.0:8899 (serves UI + API in one process).
# Uses conda env `as`. Run from anywhere; cd's into backend/ so .env is loaded.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/backend"
exec /home/ubuntu/miniconda3/envs/as/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8899
