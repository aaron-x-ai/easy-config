#!/bin/bash
# Easy Config — GitHub release helper (commit → push → tag → optional gh release)
#
# Usage (from repo root):
#   ./scripts_dev/github-release.sh -m "feat: …" --release
#   ./scripts_dev/github-release.sh v0.1.0 -m "chore(release): v0.1.0"
#   ./scripts_dev/github-release.sh --dry-run --no-release -m "test"
#
# Options:
#   --dry-run       print commands only
#   --no-push       local commit + tag only
#   --no-release    skip gh release create
#   --release       create GitHub release (default when non-interactive)
#   --skip-commit   tag current HEAD only
#   -m / --message  commit message (required unless --skip-commit)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${GIT_REMOTE_NAME:-origin}"
DRY=0
NO_PUSH=0
DO_RELEASE=-1
SKIP_COMMIT=0
MSG=""
TAG=""

say() { printf '[github-release] %s\n' "$*"; }
die() { printf '%s\n' "$*" >&2; exit 1; }

_next_patch_tag() {
  local last
  last="$(git -C "$ROOT" tag -l 'v[0-9]*.[0-9]*.[0-9]*' 2>/dev/null | sort -V | tail -n 1)"
  [[ -z "$last" ]] && { printf 'v0.1.0\n'; return; }
  local vn="${last#v}" maj min pat
  IFS=. read -r maj min pat <<< "$vn"
  pat=$((10#${pat:-0} + 1))
  printf 'v%s.%s.%s\n' "$maj" "$min" "$pat"
}

run() {
  if [[ "$DRY" -eq 1 ]]; then
    say "[dry-run] $*"
  else
    eval "$@"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --dry-run) DRY=1; shift ;;
    --no-push) NO_PUSH=1; shift ;;
    --no-release) DO_RELEASE=0; shift ;;
    --release) DO_RELEASE=1; shift ;;
    --skip-commit) SKIP_COMMIT=1; shift ;;
    -m|--message) MSG="${2:-}"; shift 2 ;;
    v[0-9]*.[0-9]*.[0-9]*) TAG="$1"; shift ;;
    *) die "unknown arg: $1" ;;
  esac
done

[[ -z "$TAG" ]] && TAG="$(_next_patch_tag)"
[[ "$SKIP_COMMIT" -eq 0 && -z "$MSG" ]] && die "commit message required (-m) unless --skip-commit"

if [[ "$DO_RELEASE" -eq -1 ]]; then
  if [[ -t 0 ]]; then
  say "Default: create GitHub Release for tag $TAG? [y/N]"
  read -r ans
  [[ "$ans" == "y" || "$ans" == "Y" ]] && DO_RELEASE=1 || DO_RELEASE=0
  else
    DO_RELEASE=1
  fi
fi

cd "$ROOT"
if [[ "$SKIP_COMMIT" -eq 0 ]]; then
  run "git add -A"
  run "git commit -m $(printf '%q' "$MSG")"
fi
if [[ "$NO_PUSH" -eq 0 ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD)"
  run "git push $REMOTE $branch"
  run "git tag -a $(printf '%q' "$TAG") -m $(printf '%q' "$TAG")"
  run "git push $REMOTE $(printf '%q' "$TAG")"
fi
if [[ "$DO_RELEASE" -eq 1 ]] && command -v gh >/dev/null 2>&1; then
  run "gh release create $(printf '%q' "$TAG") --title $(printf '%q' "$TAG") --notes $(printf '%q' "$MSG")"
elif [[ "$DO_RELEASE" -eq 1 ]]; then
  say "gh not found; create release manually for $TAG"
fi
say "done: $TAG"
