#!/bin/bash
# Are the proofs in step with the specifications? For every spec/<M>_proof.tla, the newest
# <M>-proof-results-*.txt names the digest of each module in the proof's EXTENDS chain as it was proved. This
# script compares those digests with the tree and reports, one row per proof module, then lists the base modules
# that have no proof and why.
#   usage: proof-sync.sh            report; exit 1 if any proof is stale or its results file is missing
#          proof-sync.sh --run      also re-check every stale proof with the prover (no results file is written;
#                                   regenerate one with proof-results.sh once the proof is repaired)
# A base module cited by digest in a record is frozen, so a stale row normally means a successor module was
# written (Lease -> Lease_A1) and needs a successor proof: copy the proof module, point its EXTENDS at the
# successor, re-prove, and generate a results file in the same commit (proof-method.md §7).
set -u
here=$(cd "$(dirname "$0")" && pwd)
run=${1:-}
status=0
digest() { shasum -a 256 "$here/$1" | cut -c1-16; }
echo "proof module | results file | modules as proved -> now | state"
for pf in "$here"/*_proof.tla; do
  m=$(basename "$pf" _proof.tla)
  res=$(ls -1 "$here/$m-proof-results-"*.txt 2>/dev/null | sort | tail -1)
  if [ -z "$res" ]; then echo "${m}_proof.tla | (none) | - | MISSING RESULTS"; status=1; continue; fi
  stale=""; detail=""
  while read -r mod dig; do
    now=$(digest "$mod")
    if [ "$now" = "$dig" ]; then detail="$detail $mod ok;"; else detail="$detail $mod $dig -> $now;"; stale="$stale $mod"; fi
  done < <(grep -m1 '^Modules:' "$res" | grep -oE '[A-Za-z0-9_]+\.tla \(sha256 [0-9a-f]{16}\)' | sed -E 's/ \(sha256 ([0-9a-f]+)\)/ \1/')
  if [ -z "$stale" ]; then
    echo "${m}_proof.tla | $(basename "$res") |$detail | IN SYNC"
  else
    echo "${m}_proof.tla | $(basename "$res") |$detail | STALE:$stale"; status=1
    if [ "$run" = "--run" ]; then
      cache=$(mktemp -d /tmp/tlapm_sync.XXXXXX)
      (cd "$here" && "$here/../tools/tlapm" --cleanfp --strict --cache-dir "$cache" "${m}_proof.tla" 2>&1 | grep -E 'INFO|obligations failed' | sed 's/^/    prover now: /')
      rm -rf "$cache"
    fi
  fi
done
echo
echo "base modules without a proof:"
for bf in "$here"/*.tla; do
  b=$(basename "$bf" .tla)
  case "$b" in Trace_*|*_proof) continue ;; esac
  [ -f "$here/${b}_proof.tla" ] && continue
  case "$b" in
    RulesFloorBase) why="shared definitions, no Spec; its genesis fact is proved as a lemma in Anchor_proof and BreakGlass_proof" ;;
    RulesFloorNV)   why="frozen (G1) and superseded by RulesFloorNV_rev5, which is proved" ;;
    Lease)          why="frozen and superseded by Lease_A1, which is proved; its invariants are Lease_A1's at rungs 0..2" ;;
    Mechanism)      why="a trace replay, not a transition system with invariants; its target is the refinement (T-0045-28)" ;;
    *)              why="NO REASON RECORDED: write the proof or add the reason here"; status=1 ;;
  esac
  echo "  $b.tla: $why"
done
exit $status
