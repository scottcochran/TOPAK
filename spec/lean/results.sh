#!/bin/bash
# Regenerates the Lean results file for the spec/ modules re-encoded in Lean (ADR-0053, Proposed): a clean build of
# TopakSpec/*.lean, each a transition system transcribed from a spec/*.tla module with its *_proof.tla theorems proved
# by induction on reachable states, with the digests of the TLA+ modules transcribed, the Lean sources and the
# toolchain, the `#print axioms` of every theorem, and the kernel replay. Regenerates byte for byte on the same machine.
#   usage: results.sh > TopakSpec-results-<date>.txt     (from spec/lean/)
# What each file claims and where its encoding departs from the TLA+ text are in the file's header and in
# TopakSpec/Prelude.lean's conventions. Needs the toolchain tools/LEAN-PIN names (tools/install-lean.sh); exits
# non-zero if a theorem or the replay fails. tools/lean-sync.sh says whether the newest results file matches the tree.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
tla="Seats Observers RunSeats FloorRouting NonComposition RulesFloorBase Anchor BreakGlass Coupling Lease_A1 RulesFloorNV_rev5 Confinement Confinement_A1"
modules="Prelude Seats Observers RunSeats FloorRouting NonComposition RulesFloorBase Anchor BreakGlass Coupling Lease_A1 RulesFloorNV_rev5 Confinement"
echo "TOPAK — Lean results for the spec/ modules re-encoded in Lean: every theorem of spec/lean/TopakSpec/*.lean, checked by the kernel below"
line="Transcribes:"; for m in $tla; do line="$line $(e spec/$m.tla) ·"; done; echo "${line% ·}"
line="Sources:"; for m in $modules; do line="$line $(e spec/lean/TopakSpec/$m.lean) ·"; done
echo "$line $(e spec/lean/TopakSpec.lean) · $(e spec/lean/lakefile.toml) · $(e spec/lean/lean-toolchain)"
"$root/tools/lean-report.sh" "$here" --prover
for m in $modules; do
  [ "$m" = Prelude ] && continue
  thms=$(grep -oE '^theorem [A-Za-z0-9_]+Always|^theorem NeverChangesAuthority|^theorem GenesisEntries|^theorem GenesisFloor|^theorem Confinement[A-Za-z0-9_]*SafeAlways' "$here/TopakSpec/$m.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')
  echo "Theorems ($m): ${thms:-none}"
done
echo "A theorem holds of the Lean re-encoding, not of the frozen TLA+ text; the encoding's fidelity is read, each definition beside the TLA+ it transcribes. Spec => []P is induction on reachable states (Prelude.invariant), in place of LS4; the arithmetic the TLAPS proofs hand to SMT is closed by omega; Confinement.lean covers Confinement.tla and Confinement_A1.tla under one flag. Mutations and witnesses stay with TLC."
echo
"$root/tools/lean-report.sh" "$here" TopakSpec
