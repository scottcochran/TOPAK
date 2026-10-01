#!/usr/bin/env bash
# verify-manifest.sh MANIFEST COMMIT   — verify manifests/MANIFEST against the tree at COMMIT
# verify-manifest.sh --all             — every row of manifests/index.tsv that names a commit
# A manifest's entries are root-relative paths at the time it was cut; the tree at COMMIT is extracted
# to a temporary directory and shasum -c runs there, so a manifest is checked against what it measured
# and not against today's layout (reorganization proposal §4, P4).
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
one() {
  local m="$1" c="$2" tmp total out ok
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' RETURN
  git -C "$repo" archive "$c" | tar -x -C "$tmp"
  total=$(grep -cvE '^\s*(#|$)' "$repo/manifests/$m")
  out=$(cd "$tmp" && shasum -a 256 -c "$repo/manifests/$m" 2>/dev/null || true)
  ok=$(printf '%s\n' "$out" | grep -c ': OK$' || true)
  printf '%-28s @%-8s %3d/%-3d OK' "$m" "$c" "$ok" "$total"
  if [ -n "${3:-}" ]; then
    if [ "$ok" -eq "$3" ]; then printf '  (expected %s)\n' "$3"; else printf '  EXPECTED %s\n' "$3"; printf '%s\n' "$out" | grep -v ': OK$' | sed 's/^/    /'; fi
  else printf '\n'; [ "$ok" -eq "$total" ] || printf '%s\n' "$out" | grep -v ': OK$' | sed 's/^/    /'; fi
}
if [ "${1:-}" = "--all" ]; then
  tail -n +2 "$repo/manifests/index.tsv" | while IFS=$'\t' read -r name kind cut commit entries expected note; do
    [ "$commit" = "-" ] && { printf '%-28s %-9s historical, no commit\n' "$name" ""; continue; }
    one "$name" "$commit" "$expected"
  done
else
  one "$1" "$2" "${3:-}"
fi
