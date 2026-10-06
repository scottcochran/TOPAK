#!/bin/bash
# Regenerates the Lean results file for the mechanism's code-level proofs (ADR-0053, Proposed): a clean build of this
# package, which transcribes crates/topak-core/src/admit.rs (and its call site in topak-node), clock.rs and the
# topak-floor wrapper, models the Seats-shaped part of state.rs's State::apply, and proves properties of each, with the digests of the Rust transcribed, the Lean sources and the toolchain, the
# `#print axioms` of every theorem, and the kernel replay. Regenerates byte for byte on the same machine.
#   usage: results.sh > Admit-results-<date>.txt     (from mechanism/lean/)
# Needs the toolchain tools/LEAN-PIN names (tools/install-lean.sh); exits non-zero if a theorem or the replay fails.
# tools/lean-sync.sh says whether the newest results file still matches the tree.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
echo "TOPAK — Lean results for admit.rs, clock.rs, the topak-floor wrapper and a Seats-shaped model of State::apply: every theorem of mechanism/lean/Topak/*.lean, and of the spec/lean modules they refine, checked by the kernel below"
echo "Transcribes: $(e mechanism/crates/topak-core/src/admit.rs) · $(e mechanism/crates/topak-node/src/mechanism.rs) · $(e mechanism/crates/topak-core/src/clock.rs) · $(e mechanism/crates/topak-floor/src/lib.rs) · $(e spec/FloorComposition.tla) · $(e mechanism/crates/topak-core/src/state.rs) · $(e mechanism/crates/topak-core/src/types.rs) · $(e mechanism/crates/topak-core/src/lease.rs) · $(e spec/Seats.tla)"
echo "Sources: $(e mechanism/lean/Topak/Admit.lean) · $(e mechanism/lean/Topak/Clock.lean) · $(e mechanism/lean/Topak/FloorRefinement.lean) · $(e mechanism/lean/Topak/SeatsModel.lean) · $(e mechanism/lean/Topak.lean) · $(e mechanism/lean/lakefile.toml) · $(e mechanism/lean/lake-manifest.json) · $(e mechanism/lean/lean-toolchain) · $(e spec/lean/TopakSpec/Prelude.lean) · $(e spec/lean/TopakSpec/FloorComposition.lean) · $(e spec/lean/TopakSpec/Seats.lean)"
"$root/tools/lean-report.sh" "$here" --prover
echo "Theorems (Admit): $(grep -oE '^(@\[simp\] )?theorem [A-Za-z0-9_]+' "$here/Topak/Admit.lean" | sed 's/.*theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (Clock): $(grep -oE '^theorem [A-Za-z0-9_]+' "$here/Topak/Clock.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (FloorRefinement): $(grep -oE '^theorem [A-Za-z0-9_]+' "$here/Topak/FloorRefinement.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (SeatsModel): $(grep -oE '^theorem [A-Za-z0-9_.]+' "$here/Topak/SeatsModel.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "A theorem holds of the transcription, not of the Rust: admit.rs's floor_gate and compose, the call site in mechanism.rs (steps 5 and 6), clock.rs's subtracting_interval_elapsed and topak-floor's Floor::evaluate are read against their Lean, each definition beside the Rust it transcribes. FloorRefinement proves the code's decision a Decide step of spec/lean's re-encoding of FloorComposition.tla, on the engine premise T-0045-3 (Cedar's rule over the module's four policies) and with the module's own lift; it is not a refinement of the floor in force, and discharges no stage of T-0045-28 (ADR-0053 §5). SeatsModel is a model of State::apply, not a transcription: each arm keeps its checks and effects on the leases, the live index, the seat kinds and the admitted acts, and every other check is one oracle that can only refuse; it proves ADR-0037 §1 and §4 of the model at any size (model_inv) and the model a refinement of spec/lean's Seats.tla at that module's constants (model_refines_seats), on the premise that the log delivers increasing indices; seats-replay.sh checks the model against the reference's recorded traces (SeatsReplay-results-*.txt). Evidence, not a stage of T-0045-28 (ADR-0053 §5, R1)."
echo
"$root/tools/lean-report.sh" "$here" Topak
