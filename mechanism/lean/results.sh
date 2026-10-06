#!/bin/bash
# Regenerates the Lean results file for the mechanism's code-level proofs (ADR-0053, Proposed): a clean build of this
# package, which transcribes crates/topak-core/src/admit.rs (and its call site in topak-node) and clock.rs and proves
# properties of the transcriptions, with the digests of the Rust transcribed, the Lean sources and the toolchain, the
# `#print axioms` of every theorem, and the kernel replay. Regenerates byte for byte on the same machine.
#   usage: results.sh > Admit-results-<date>.txt     (from mechanism/lean/)
# Needs the toolchain tools/LEAN-PIN names (tools/install-lean.sh); exits non-zero if a theorem or the replay fails.
# tools/lean-sync.sh says whether the newest results file still matches the tree.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
echo "TOPAK — Lean results for admit.rs, clock.rs and the topak-floor wrapper: every theorem of mechanism/lean/Topak/*.lean, and of the spec/lean module it refines, checked by the kernel below"
echo "Transcribes: $(e mechanism/crates/topak-core/src/admit.rs) · $(e mechanism/crates/topak-node/src/mechanism.rs) · $(e mechanism/crates/topak-core/src/clock.rs) · $(e mechanism/crates/topak-floor/src/lib.rs) · $(e spec/FloorComposition.tla)"
echo "Sources: $(e mechanism/lean/Topak/Admit.lean) · $(e mechanism/lean/Topak/Clock.lean) · $(e mechanism/lean/Topak/FloorRefinement.lean) · $(e mechanism/lean/Topak.lean) · $(e mechanism/lean/lakefile.toml) · $(e mechanism/lean/lake-manifest.json) · $(e mechanism/lean/lean-toolchain) · $(e spec/lean/TopakSpec/Prelude.lean) · $(e spec/lean/TopakSpec/FloorComposition.lean)"
"$root/tools/lean-report.sh" "$here" --prover
echo "Theorems (Admit): $(grep -oE '^(@\[simp\] )?theorem [A-Za-z0-9_]+' "$here/Topak/Admit.lean" | sed 's/.*theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (Clock): $(grep -oE '^theorem [A-Za-z0-9_]+' "$here/Topak/Clock.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (FloorRefinement): $(grep -oE '^theorem [A-Za-z0-9_]+' "$here/Topak/FloorRefinement.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "A theorem holds of the transcription, not of the Rust: admit.rs's floor_gate and compose, the call site in mechanism.rs (steps 5 and 6), clock.rs's subtracting_interval_elapsed and topak-floor's Floor::evaluate are read against their Lean, each definition beside the Rust it transcribes. FloorRefinement proves the code's decision a Decide step of spec/lean's re-encoding of FloorComposition.tla, on the engine premise T-0045-3 (Cedar's rule over the module's four policies) and with the module's own lift; it is not a refinement of the floor in force, and discharges no stage of T-0045-28 (ADR-0053 §5)."
echo
"$root/tools/lean-report.sh" "$here" Topak
