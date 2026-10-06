#!/bin/bash
# Are the Lean results in step with what they transcribe, and with the pin? (ADR-0053, Proposed.) For each Lean
# package, the newest results file of each series names the digest of every file it transcribes (`Transcribes:` or
# `Floor:`) and every Lean source it was built from (`Sources:`), by repository path; mechanism/lean's trace replay
# (SeatsReplay-results-*.txt) names its model and the Rust the traces were recorded from (`Model:`, `Reference:`).
# This script compares those digests with the tree and reports one row per series; then compares the kernel each
# results file names, each package's lean-toolchain, and floor/lean's cedar-spec and batteries commits with
# tools/LEAN-PIN; then checks that the floor and schema mechanism/crates/topak-floor links are among those the newest
# floor/lean results file states (ADR-0053 finding 6); then lists the proved TLA+ modules that have no Lean encoding,
# which is information, not a failure.
#   usage: tools/lean-sync.sh       exit 1 if a package's results are stale or missing, anything is off the pin, or the
#                                   floor the reference links is not stated in Lean
# A stale `Transcribes:` digest means the thing transcribed moved: re-read the Lean against it, change the Lean if the
# Rust or the TLA+ changed in meaning, and regenerate the results file. A stale replay means state.rs or the recorder
# moved: run mechanism/lean/seats-replay.sh again. A frozen TLA+ module does not move; its successor gets a successor
# encoding (spec/proof-method.md §6), and the results file names the successor.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
pin() { grep -E "^$1 " "$root/tools/LEAN-PIN" | head -1 | cut -d' ' -f2; }
# The newest results file of a series: a package's proofs, or mechanism/lean's trace replay.
series() { case $1 in mechanism/lean) echo Admit;; spec/lean) echo TopakSpec;; floor/lean) echo TopakFloor;; replay) echo SeatsReplay;; esac; }
dir() { [ "$1" = replay ] && echo mechanism/lean || echo "$1"; }
newest() { ls -1 "$root/$(dir "$1")/$(series "$1")-results-"*.txt 2>/dev/null | sort | tail -1; }
status=0
echo "package | results file | files as built -> now | state"
for pkg in mechanism/lean replay spec/lean floor/lean; do
  res=$(newest "$pkg")
  if [ -z "$res" ]; then echo "$pkg | (none) | - | MISSING RESULTS"; status=1; continue; fi
  stale=""; n=0
  while read -r path dig; do
    n=$((n + 1))
    if [ ! -f "$root/$path" ]; then stale="$stale $path(gone)"; continue; fi
    now=$(shasum -a 256 "$root/$path" | cut -c1-16)
    [ "$now" = "$dig" ] || stale="$stale $path($dig->$now)"
  done < <(grep -E '^(Transcribes|Floor|Sources|Model|Reference):' "$res" | grep -oE '[A-Za-z0-9_./-]+ \(sha256 [0-9a-f]{16}' | sed -E 's/ \(sha256 / /')
  name=$pkg; [ "$pkg" = replay ] && name="mechanism/lean (trace replay)"
  if [ -z "$stale" ]; then echo "$name | $(basename "$res") | $n files ok | IN SYNC"
  else echo "$name | $(basename "$res") |$stale | STALE"; status=1; fi
done
echo
echo "pin (tools/LEAN-PIN):"
want=$(pin libleanshared_sha256_16); tc=$(pin toolchain); off=0
for pkg in mechanism/lean spec/lean floor/lean; do
  have=$(cat "$root/$pkg/lean-toolchain")
  [ "$have" = "$tc" ] || { echo "  $pkg/lean-toolchain: $have, pin $tc: OFF THE PIN"; off=1; }
  res=$(newest "$pkg"); [ -n "$res" ] || continue
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
echo "the floor the reference links (mechanism/crates/topak-floor):"
fres=$(newest floor/lean)
linked=$(grep -oE 'include_str!\("[^"]+\.(cedar|cedarschema)"\)' "$root/mechanism/crates/topak-floor/src/lib.rs" | sed -E 's/include_str!\("(\.\.\/)*//; s/"\)$//')
for f in $linked; do
  if [ -n "$fres" ] && grep -m1 '^Floor:' "$fres" | grep -q " $f (sha256"; then echo "  $f: stated in Lean ($(basename "$fres"))"
  else echo "  $f: NOT STATED IN LEAN: the floor the reference runs has no Lean statement"; status=1; fi
done
echo
echo "proved TLA+ modules without a Lean encoding (information):"
enc=$(grep -m1 '^Transcribes:' "$(newest spec/lean)" | grep -oE 'spec/[A-Za-z0-9_]+\.tla' | sed 's|spec/||; s|\.tla||' | tr '\n' ' ')
for pf in "$root"/spec/*_proof.tla; do
  m=$(basename "$pf" _proof.tla)
  echo " $enc " | grep -q " $m " && continue
  echo "  $m: not yet encoded"
done
exit $status
