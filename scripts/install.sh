#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEV=0
for arg in "$@"; do
  case "$arg" in
    --dev) DEV=1 ;;
    -h|--help)
      echo "Usage: bash scripts/install.sh [--dev]"
      echo "  --dev  also install pytest, httpx, ruff (for development)"
      exit 0
      ;;
  esac
done

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

export HTTP_PROXY= HTTPS_PROXY= http_proxy= https_proxy= ALL_PROXY= all_proxy=
export NO_PROXY='*' no_proxy='*'

pip install -U pip setuptools wheel
pip install -r requirements.txt
pip install --no-build-isolation -e .
if [[ "$DEV" -eq 1 ]]; then
  pip install -e ".[dev]"
fi

VPY="$ROOT/.venv/bin/python"
echo ""
echo "[install] Done. Python: $($VPY -V)"
echo "[install] Virtualenv: $ROOT/.venv"
echo ""
echo "Next steps (pick one):"
echo ""
echo "  A) Activate venv, then run commands:"
echo "     source .venv/bin/activate"
echo "     python -m easy_config doctor"
if [[ "$DEV" -eq 1 ]]; then
  echo "     bash scripts/pytest.sh -q"
else
  echo "     bash scripts/install.sh --dev"
  echo "     (then) bash scripts/pytest.sh -q"
fi
echo ""
echo "  B) Without activating (always works):"
echo "     bash scripts/doctor.sh"
echo "     bash scripts/pytest.sh -q          (needs install.sh --dev once)"
echo "     export EASY_CONFIG_SKILLS_ROOT=\"\$PWD/tests/fixtures\""
echo "     bash scripts/serve.sh --skill demo-skill --dry-run"
echo ""
