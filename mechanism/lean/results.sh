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
echo "TOPAK — Lean results for admit.rs and clock.rs: every theorem of mechanism/lean/Topak/*.lean, checked by the kernel below"
echo "Transcribes: $(e mechanism/crates/topak-core/src/admit.rs) · $(e mechanism/crates/topak-node/src/mechanism.rs) · $(e mechanism/crates/topak-core/src/clock.rs)"
echo "Sources: $(e mechanism/lean/Topak/Admit.lean) · $(e mechanism/lean/Topak/Clock.lean) · $(e mechanism/lean/Topak.lean) · $(e mechanism/lean/lakefile.toml) · $(e mechanism/lean/lean-toolchain)"
"$root/tools/lean-report.sh" "$here" --prover
echo "Theorems (Admit): $(grep -oE '^(@\[simp\] )?theorem [A-Za-z0-9_]+' "$here/Topak/Admit.lean" | sed 's/.*theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "Theorems (Clock): $(grep -oE '^theorem [A-Za-z0-9_]+' "$here/Topak/Clock.lean" | sed 's/theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "A theorem holds of the transcription, not of the Rust: admit.rs's floor_gate and compose, the call site in mechanism.rs (steps 5 and 6), and clock.rs's subtracting_interval_elapsed are read against their Lean, each definition beside the Rust it transcribes. The lift, the store and the envelope (BundleCannotWriteFloorInputs, EnvelopeHolds) are outside these functions and stay with the TLA+ module."
echo
"$root/tools/lean-report.sh" "$here" Topak
