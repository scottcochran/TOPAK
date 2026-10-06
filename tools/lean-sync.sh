#!/bin/bash
# Are the Lean results in step with what they transcribe, and with the pin? (ADR-0053, Proposed.) For each Lean
# package, the newest *-results-*.txt names the digest of every file it transcribes (`Transcribes:` or `Floor:`) and
# every Lean source it was built from (`Sources:`), by repository path. This script compares those digests with the
# tree and reports one row per package; then compares the kernel each results file names, each package's
# lean-toolchain, and floor/lean's cedar-spec and batteries commits with tools/LEAN-PIN; then lists the proved TLA+
# modules that have no Lean encoding, which is information, not a failure.
#   usage: tools/lean-sync.sh       exit 1 if a package's results are stale or missing, or anything is off the pin
# A stale `Transcribes:` digest means the thing transcribed moved: re-read the Lean against it, change the Lean if the
# Rust or the TLA+ changed in meaning, and regenerate the results file. A frozen TLA+ module does not move; its
# successor gets a successor encoding (spec/proof-method.md §6), and the results file names the successor.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
pin() { grep -E "^$1 " "$root/tools/LEAN-PIN" | head -1 | cut -d' ' -f2; }
status=0
echo "package | results file | files as built -> now | state"
for pkg in mechanism/lean spec/lean floor/lean; do
  res=$(ls -1 "$root/$pkg/"*-results-*.txt 2>/dev/null | sort | tail -1)
  if [ -z "$res" ]; then echo "$pkg | (none) | - | MISSING RESULTS"; status=1; continue; fi
  stale=""; n=0
  while read -r path dig; do
    n=$((n + 1))
    if [ ! -f "$root/$path" ]; then stale="$stale $path(gone)"; continue; fi
    now=$(shasum -a 256 "$root/$path" | cut -c1-16)
    [ "$now" = "$dig" ] || stale="$stale $path($dig->$now)"
  done < <(grep -E '^(Transcribes|Floor|Sources):' "$res" | grep -oE '[A-Za-z0-9_./-]+ \(sha256 [0-9a-f]{16}' | sed -E 's/ \(sha256 / /')
  if [ -z "$stale" ]; then echo "$pkg | $(basename "$res") | $n files ok | IN SYNC"
  else echo "$pkg | $(basename "$res") |$stale | STALE"; status=1; fi
done
echo
echo "pin (tools/LEAN-PIN):"
want=$(pin libleanshared_sha256_16); tc=$(pin toolchain); off=0
for pkg in mechanism/lean spec/lean floor/lean; do
  have=$(cat "$root/$pkg/lean-toolchain")
  [ "$have" = "$tc" ] || { echo "  $pkg/lean-toolchain: $have, pin $tc: OFF THE PIN"; off=1; }
  res=$(ls -1 "$root/$pkg/"*-results-*.txt 2>/dev/null | sort | tail -1); [ -n "$res" ] || continue
  k=$(grep -m1 '^Prover:' "$res" | grep -oE 'libleanshared \(sha256 [0-9a-f]{16}' | grep -oE '[0-9a-f]{16}$')
  [ "$k" = "$want" ] || { echo "  $(basename "$res"): kernel ${k:-unnamed}, pin $want: NOT THE PINNED KERNEL"; off=1; }
done
man="$root/floor/lean/lake-manifest.json"
for dep in "Cedar cedar_spec_commit" "batteries batteries_commit"; do
  name=${dep% *}; key=${dep#* }
  have=$(python3 -c "import json,sys;m=json.load(open(sys.argv[1]));print(next(p['rev'] for p in m['packages'] if p['name']==sys.argv[2]))" "$man" "$name")
  [ "$have" = "$(pin "$key")" ] || { echo "  floor/lean/lake-manifest.json: $name $have, pin $(pin "$key"): OFF THE PIN"; off=1; }
done
[ $off -eq 0 ] && echo "  every package names $tc, every results file names kernel $want, and cedar-spec is at $(pin cedar_spec_tag) ($(pin cedar_spec_commit | cut -c1-7))" || status=1
echo
echo "proved TLA+ modules without a Lean encoding (information):"
enc=$(grep -m1 '^Transcribes:' "$(ls -1 "$root/spec/lean/"*-results-*.txt | sort | tail -1)" | grep -oE 'spec/[A-Za-z0-9_]+\.tla' | sed 's|spec/||; s|\.tla||' | tr '\n' ' ')
for pf in "$root"/spec/*_proof.tla; do
  m=$(basename "$pf" _proof.tla)
  echo " $enc " | grep -q " $m " && continue
  echo "  $m: not yet encoded"
done
exit $status
