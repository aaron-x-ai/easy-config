#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "[pytest] .venv not found; run: bash scripts/install.sh --dev" >&2
  exit 1
fi
if ! "$PY" -m pytest --version >/dev/null 2>&1; then
  echo "[pytest] pytest not installed; run: bash scripts/install.sh --dev" >&2
  exit 1
fi
# Ignore accidental copy-paste of shell comments (e.g. "# 7 passed")
args=()
for a in "$@"; do
  [[ "$a" == \#* ]] && continue
  args+=("$a")
done
exec "$PY" -m pytest tests "${args[@]}"
