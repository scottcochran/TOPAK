#!/bin/bash
# Regenerates the Anchor proof results file: checks Anchor_proof.tla with the TLA+ Proof System and prints
# the results file with the digests of the modules and the prover.
#   usage: anchor-proof-results.sh > Anchor-proof-results-<date>.txt
# Needs the prover under tools/ (tools/install-tlaps.sh); exits non-zero if any obligation fails.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
tlapm="$root/tools/tlapm"
bin=$("$tlapm" --config 2>/dev/null | sed -n 's/^tlapm_executable == "\(.*\)"$/\1/p')
cfg=$("$tlapm" --config 2>/dev/null)
ver() { echo "$cfg" | sed -n "s/^$1 version == \"\(.*\)\"$/\1/p" | head -1; }
cache=$(mktemp -d /tmp/tlapm_anchor.XXXXXX)
echo "TOPAK — Anchor.tla proved in TLAPS: FloorPreserved and EpochMonotone for every Active ⊆ AllEntries and MaxEpoch ∈ Nat (ADR-0029 §5, bootstrap module 2 of 5)"
echo "Modules: Anchor_proof.tla (sha256 $(shasum -a 256 "$here/Anchor_proof.tla" | cut -c1-16)) · Anchor.tla (sha256 $(shasum -a 256 "$here/Anchor.tla" | cut -c1-16)) · RulesFloorBase.tla (sha256 $(shasum -a 256 "$here/RulesFloorBase.tla" | cut -c1-16))"
echo "Prover: tlapm $("$tlapm" --version) (binary sha256 $(shasum -a 256 "$bin" | cut -c1-16)) · backends: $(ver SMT) · $(ver zenon) · $(ver Isabelle) · LS4 for PTL · driver: anchor-proof-results.sh"
echo "Assumptions: ActiveEntries (Active ⊆ AllEntries), MaxEpochNat (MaxEpoch ∈ Nat); FloorPreservedAlways takes Mut = \"none\" as its hypothesis."
echo "Not proved here: the mutation M_FLOOR and the witness NeverIssued are behaviours, and remain TLC's (bootstrap-results-2026.09.23.txt). MutAdmitsAll states why M_FLOOR must fail."
echo "A proved obligation is a theorem of the module under its assumptions; the prover, not the constants, bounds the claim."
echo
echo "Statements: $(grep -oE '^(THEOREM|LEMMA) [A-Za-z0-9_]+' "$here/Anchor_proof.tla" | sed 's/THEOREM /THEOREM /; s/LEMMA /lemma /' | paste -sd ',' - | sed 's/,/ · /g')"
echo
(cd "$here" && "$tlapm" --cleanfp --strict --cache-dir "$cache" Anchor_proof.tla 2>&1 | grep -vE '^\(\* ')
status=${PIPESTATUS[0]}
rm -rf "$cache"
exit $status
