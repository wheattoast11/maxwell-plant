#!/usr/bin/env bash
# The Maxwell workspace on loopback, sign-in on; tej is the installation admin.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="${MAXWELL_PLANT_DATA:-$HOME/.local/share/maxwell-plant}"
export PLANTCRAFT_DEMO_USERS=0 PLANTCRAFT_LLM="${PLANTCRAFT_LLM:-off}"
export PLANTCRAFT_BASIC_AUTH_ENABLED=1 PLANTCRAFT_BASIC_AUTH_USERNAME=tej
export PLANTCRAFT_BASIC_AUTH_PASSWORD_FILE="$DATA/seats/tej.password"
"$ROOT/.venv/bin/python" -m maxwell.seats --scenario "$ROOT/scenarios/maxwell.json"
exec "$ROOT/.venv/bin/processcraft" --scenario "$ROOT/scenarios/maxwell.json" \
  --host "${HOST:-127.0.0.1}" --port "${PORT:-8765}" --workers 1 "$@"
