#!/usr/bin/env bash
# Optional: invoke target skill scripts/reload.sh after successful save (P1+).
set -euo pipefail
SKILL_DIR="${1:-}"
if [[ -z "$SKILL_DIR" || ! -d "$SKILL_DIR" ]]; then
  echo "[reload-hook] skill directory required" >&2
  exit 1
fi
RELOAD="$SKILL_DIR/scripts/reload.sh"
if [[ -x "$RELOAD" ]]; then
  exec "$RELOAD"
fi
echo "[reload-hook] no executable scripts/reload.sh; skip"
exit 0
