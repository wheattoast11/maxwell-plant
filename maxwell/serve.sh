#!/usr/bin/env bash
# The Maxwell workspace on loopback, sign-in on; tej is the installation admin.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
export PLANTCRAFT_SCENARIO="$ROOT/scenarios/maxwell.json"
DATA="$("$PY" -c 'from maxwell.seats import db_path; print(db_path().parent)')"
export PLANTCRAFT_DEMO_USERS=0 PLANTCRAFT_LLM="${PLANTCRAFT_LLM:-off}"
export PLANTCRAFT_BASIC_AUTH_ENABLED=1 PLANTCRAFT_BASIC_AUTH_USERNAME=tej
export PLANTCRAFT_BASIC_AUTH_PASSWORD_FILE="$DATA/seats/tej.password"
"$PY" -m maxwell.seats
exec "$ROOT/.venv/bin/processcraft" --scenario "$PLANTCRAFT_SCENARIO" \
  --host "${HOST:-127.0.0.1}" --port "${PORT:-8765}" --workers 1 "$@"
