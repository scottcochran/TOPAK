#!/bin/bash
# Reruns every proof module and compares each one's outcome with its newest committed results file. Counts only:
# no results file is written (ADR-0077 §3, Proposed).
#   usage: tools/check-proofs.sh [Module ...]    the named modules (M for spec/M_proof.tla), or every spec/*_proof.tla
# Each module is proved by spec/proof-results.sh, which runs tools/tlapm with --cleanfp and --strict, and the lines in
# which tlapm states the outcome ("All N obligations proved.", "M/N obligations failed.") are compared with the
# committed file's. The prover is whatever tools/tlapm runs. Until ADR-0077 §5 moves tools/TLAPS-PIN, the image's
# prover is not the pinned one, so CI sets TLAPM_UNPINNED=1 and a pass corroborates and regenerates nothing: a
# failure may be the newer prover's and not the proof's, and is read as such.
# PROOFS_OUT=<dir> keeps each module's output there, as working output that names the prover it ran.
# Exits 1 if any module's outcome differs, its run fails, or it has no committed results file.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root/spec" || exit 2
out=${PROOFS_OUT:-}
tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-proofs.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
outcome() { grep -E '^\[(INFO|ERROR)\]: .*obligations? (proved|failed)' "$1" | sed 's/  */ /g'; }
pin=$(grep -E '^binary_sha256_16 ' "$root/tools/TLAPS-PIN" | cut -d' ' -f2)
bin=$("$root/tools/tlapm" --config 2>/dev/null | sed -n 's/^tlapm_executable == "\(.*\)"$/\1/p')
[ -n "$bin" ] || { echo "tools/tlapm does not run (set TLAPM, and TLAPM_UNPINNED=1 for a prover other than the pin's)"; exit 2; }
have=$(shasum -a 256 "$bin" | cut -c1-16)
if [ "$have" = "$pin" ]; then echo "prover: $bin (sha256 ${have}…), the pinned one (tools/TLAPS-PIN)"
else echo "prover: $bin (sha256 ${have}…), NOT tools/TLAPS-PIN's (${pin}…): counts are compared, nothing is regenerated"; fi
status=0; n=0; start=$(date +%s)
for pf in *_proof.tla; do
  m=${pf%_proof.tla}
  if [ $# -gt 0 ]; then case " $* " in *" $m "*) ;; *) continue ;; esac; fi
  n=$((n + 1))
  committed=$(ls "$m"-proof-results-*.txt 2>/dev/null | sort | tail -1)
  if [ -z "$committed" ]; then echo "$m: no committed results file"; status=1; continue; fi
  t=$(date +%s)
  ./proof-results.sh "${m}_proof" > "$tmp/$m.txt" 2>&1; rc=$?
  was=$(outcome "$committed"); now=$(outcome "$tmp/$m.txt")
  if [ $rc -eq 0 ] && [ -n "$now" ] && [ "$was" = "$now" ]; then v=same; else v=DIFFERS; status=1; fi
  printf '%-20s %-7s %4ss  exit %d  committed (%s): %s  now: %s\n' "$m" "$v" "$(( $(date +%s) - t ))" "$rc" \
    "$committed" "$(echo $was)" "$(echo ${now:-no outcome line})"
  if [ -n "$out" ]; then mkdir -p "$out" && cp "$tmp/$m.txt" "$out/$m-proof-working-output.txt"; fi
done
[ $n -gt 0 ] || { echo "no proof modules checked"; exit 1; }
echo "$n proof modules in $(( $(date +%s) - start ))s: $([ $status -eq 0 ] && echo "every outcome as committed" || echo "SOME DIFFER")"
exit $status
