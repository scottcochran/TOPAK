#!/bin/bash
# Regenerates TLC results from their rows and compares each with the newest committed results file.
#   usage: tools/check-results.sh [Module ...]     the named modules, or every module in spec/modules.tsv
#          tools/check-results.sh --matrix TIER    print the modules of a tier as a JSON list, for CI; TIER is pr
#                                                  (the modules CI runs on a pull request) or all
# spec/modules.tsv lists each module with its runner, its rows file, its tier and, for live-gen-results.sh, the
# DEFAULTS the committed file was made with. Runners:
#   live     spec/live-gen-results.sh <Module> <rows> "<title>"   (the expected line comes from the rows file)
#   a1       spec/a1-run.sh <Module> <rows> "<title>"
#   <script> spec/<script> "<title>" <rows>                     (workflow-, mesh-, runconfinement-gen-results.sh)
# The fresh file reuses the committed file's title line and is written to a temporary directory; nothing under
# spec/ is kept (the gen-results scripts write a .cfg there per row and remove it). Exits non-zero if any module's
# results differ (tools/compare-results.py says how), its generator fails, or it has no committed results file.
#
# Not listed in spec/modules.tsv, and why (each is owed a row once it can be reproduced):
#   Correlator, Emergency, Labels, Operators, ToolList: their generators read a rows file that is not tracked. The
#     rows can be read back from the results headers, which is not the same as having them.
#   Confinement: its newest results file (2026.09.30) is a one-row supplement over a dated rows file, and its
#     Module line has no jar digest. Confinement_A1: confinement-run.sh runs one row per call, with no rows file.
#   Modules with only a -run.sh script and no results generator (Lease, Seats, Coupling, ...): no rows file.
#   Mesh is listed with tier `manual`: about 70 minutes on the machine that made it, so CI runs it on demand.
# Adapted from f1-tla's tools/check-results.sh (Apache-2.0); ADR-0069 §10.2 (Proposed).
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
tsv="$root/spec/modules.tsv"
if [ "${1:-}" = "--matrix" ]; then
  tier=${2:-pr}
  awk -F'\t' -v t="$tier" 'NR>1 && $1!="" && (t=="all" || $4==t) {printf "%s\"%s\"", (n++?",":"["), $1} END {print (n?"]":"[]")}' "$tsv"
  exit 0
fi
cd "$root/spec" || exit 2
tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-results.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
status=0; n=0
while IFS=$'\t' read -r mod runner rows tier defaults; do
  [ "$mod" = module ] && continue
  [ -z "$mod" ] && continue
  if [ $# -gt 0 ]; then case " $* " in *" $mod "*) ;; *) continue ;; esac; fi
  n=$((n + 1))
  committed=$(ls "$mod"-results-*.txt 2>/dev/null | sort | tail -1)
  if [ -z "$committed" ]; then echo "$mod: no committed results file"; status=1; continue; fi
  title=$(head -1 "$committed")
  start=$(date +%s)
  case "$runner" in
    live) DEFAULTS="$defaults" ./live-gen-results.sh "$mod" "$rows" "$title" > "$tmp/$mod.txt" ;;
    a1)   ./a1-run.sh "$mod" "$rows" "$title" > "$tmp/$mod.txt" ;;
    *)    "./$runner" "$title" "$rows" > "$tmp/$mod.txt" ;;
  esac
  gen=$?
  echo "$mod: regenerated in $(( $(date +%s) - start ))s against $committed (generator exit $gen)"
  python3 "$root/tools/compare-results.py" "$committed" "$tmp/$mod.txt" || status=1
  [ $gen -eq 0 ] || status=1
  if [ -n "${RESULTS_OUT:-}" ]; then mkdir -p "$RESULTS_OUT" && cp "$tmp/$mod.txt" "$RESULTS_OUT/$mod-results-fresh.txt"; fi
done < "$tsv"
[ $n -gt 0 ] || { echo "no modules checked"; exit 1; }
exit $status
