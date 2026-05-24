#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "[e2e] .venv not found; run: bash scripts/install.sh --dev" >&2
  exit 1
fi
if ! "$PY" -m playwright --version >/dev/null 2>&1; then
  echo "[e2e] installing playwright package..." >&2
  HTTP_PROXY= HTTPS_PROXY= NO_PROXY='*' "$PY" -m pip install playwright -q
fi
if ! "$PY" -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.launch(headless=True).close()" 2>/dev/null; then
  echo "[e2e] installing chromium browser (one-time)..." >&2
  "$PY" -m playwright install chromium
fi
export EASY_CONFIG_SKILLS_ROOT="$ROOT/tests/fixtures"
exec "$PY" -m pytest tests/e2e -m e2e "$@"
