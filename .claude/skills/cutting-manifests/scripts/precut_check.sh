#!/usr/bin/env bash
# precut_check.sh      what tools/cut-manifest.sh would hash that it should not, or could not hash at all
#
# cut-manifest.sh hashes tracked and untracked unignored files alike, minus manifests/EXCLUDE. So a stray file in the
# working tree enters a checkpoint manifest silently, and a tracked file removed without staging stops the cut.
# Exits 1 if anything needs attention. Changes nothing.
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"; cd "$repo"
status=0
stray="$(git ls-files -o --exclude-standard | grep -vE -f manifests/EXCLUDE || true)"
if [ -n "$stray" ]; then
  echo "UNTRACKED AND WOULD BE HASHED (each must be meant for the checkpoint):"; printf '  %s\n' $stray; status=1
fi
gone="$(git ls-files -d | grep -vE -f manifests/EXCLUDE || true)"
if [ -n "$gone" ]; then
  echo "TRACKED BUT MISSING (the cut fails on these; a deliberate removal must be staged with git rm):"; printf '  %s\n' $gone; status=1
fi
links="$(git ls-files -co --exclude-standard | grep -vE -f manifests/EXCLUDE | while read -r f; do [ -L "$f" ] && echo "$f"; done || true)"
if [ -n "$links" ]; then
  echo "SYMLINKS (hashed as what they point at):"; printf '  %s\n' $links; status=1
fi
last="$(awk -F'\t' '$2 == "checkpoint" { n = $1; c = $5 } END { print n, c }' manifests/index.tsv)"
now="$(git ls-files -co --exclude-standard | grep -vE -f manifests/EXCLUDE | grep -c . || true)"
echo "would hash $now entries; the last checkpoint row is: $last"
reference="$(awk -F'\t' '$2 == "reference" { n = $1 } END { print n }' manifests/index.tsv)"
[ -n "$reference" ] && echo "newest reference manifest in the index: $reference"
[ "$status" -eq 0 ] && echo "ok: nothing unexpected would enter the cut"
exit "$status"
