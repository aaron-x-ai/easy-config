#!/usr/bin/env bash
# Dev/serve wrapper — uses .venv Python without requiring `source .venv/bin/activate`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "[serve] .venv not found; run: bash scripts/install.sh" >&2
  exit 1
fi
exec "$PY" -m easy_config serve "$@"
