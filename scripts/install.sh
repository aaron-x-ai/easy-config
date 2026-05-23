#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Prefer 3.11 when available (Hermes-friendly); fall back to python3.
if command -v python3.11 >/dev/null 2>&1; then
  PYTHON="python3.11"
else
  PYTHON="${PYTHON:-python3}"
fi

if ! "$PYTHON" -c 'import venv' 2>/dev/null; then
  echo "[install] $PYTHON with venv module required" >&2
  exit 1
fi

if [[ ! -d "$ROOT/.venv" ]]; then
  "$PYTHON" -m venv "$ROOT/.venv"
fi
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

# macOS 系统代理（如 127.0.0.1:7890）未启动时，需绕过以免 pip 失败
export HTTP_PROXY= HTTPS_PROXY= http_proxy= https_proxy= ALL_PROXY= all_proxy=
export NO_PROXY='*' no_proxy='*'

pip install -U pip setuptools wheel
pip install -r requirements.txt
pip install --no-build-isolation -e .
echo "[install] Easy Config installed in $ROOT/.venv (python: $(python -V))"
