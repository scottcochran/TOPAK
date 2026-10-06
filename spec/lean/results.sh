#!/bin/bash
# Regenerates the Lean results file for the re-encoded TLA+ modules: a clean build of TopakSpec/*.lean, each a
# transition system transcribed from a spec/*.tla module with its *_proof.tla theorems proved by induction on
# reachable states, with the digests of the TLA+ modules transcribed, the Lean sources and the toolchain, and what
# each theorem rests on (`#print axioms`).
#   usage: results.sh > TopakSpec-results-<date>.txt     (from spec/lean/)
# What each file claims and where its encoding departs from the TLA+ text are in the file's header and in
# TopakSpec/Prelude.lean's conventions. Needs the toolchain `lean-toolchain` names, installed by elan; exits
# non-zero if any theorem fails.
set -u
here=$(cd "$(dirname "$0")" && pwd)
spec=$(cd "$here/.." && pwd)
d16() { shasum -a 256 "$1" | cut -c1-16; }
modules="Seats Observers RunSeats FloorRouting NonComposition RulesFloorBase Anchor BreakGlass"
echo "TOPAK — Lean results for the small spec/ modules: every theorem of spec/lean/TopakSpec/*.lean, checked by the kernel below"
line="Transcribes:"
for m in $modules; do line="$line $m.tla (sha256 $(d16 "$spec/$m.tla")) ·"; done
echo "${line% ·}"
line="Sources: Prelude.lean (sha256 $(d16 "$here/TopakSpec/Prelude.lean")) ·"
for m in $modules; do line="$line $m.lean (sha256 $(d16 "$here/TopakSpec/$m.lean")) ·"; done
echo "$line lakefile.toml (sha256 $(d16 "$here/lakefile.toml")) · lean-toolchain $(cat "$here/lean-toolchain")"
echo "Prover: $(cd "$here" && lean --version) · $(cd "$here" && lake --version | head -1) · no Mathlib, no dependencies · driver: results.sh"
for m in $modules; do
  thms=$(grep -oE '^theorem [A-Za-z0-9_]+Always|^theorem NeverChangesAuthority|^theorem GenesisEntries|^theorem GenesisFloor' "$here/TopakSpec/$m.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')
  echo "Theorems ($m): ${thms:-none}"
done
echo "A theorem holds of the Lean re-encoding, not of the frozen TLA+ text; the encoding's fidelity is read, each definition beside the TLA+ it transcribes. Spec => []P is induction on reachable states (Prelude.invariant), in place of LS4. Mutations and witnesses stay with TLC."
echo
(cd "$here" && rm -rf .lake && lake build 2>&1 | grep -vE '^\s*$|^trace:')
status=${PIPESTATUS[0]}
exit $status
