#!/bin/bash
# Regenerates the Lean results file for the admit composition: a clean build of Topak/Admit.lean, which
# transcribes crates/topak-core/src/admit.rs and proves FloorComposition.tla's properties of the transcription,
# with the digests of the Rust it transcribes, the Lean sources and the toolchain, and what each theorem rests on.
#   usage: results.sh > Admit-results-<date>.txt     (from mechanism/lean/)
# What each theorem claims and what is read rather than checked are in the Lean file's header.
# Needs the toolchain `lean-toolchain` names, installed by elan; exits non-zero if any theorem fails.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
d16() { shasum -a 256 "$1" | cut -c1-16; }
rs="mechanism/crates/topak-core/src/admit.rs"
echo "TOPAK — Lean results for admit.rs: every theorem of mechanism/lean/Topak/Admit.lean, checked by the kernel below"
echo "Transcribes: $rs (sha256 $(d16 "$root/$rs")) · topak-node/src/mechanism.rs call site, steps 5 and 6"
echo "Sources: Topak/Admit.lean (sha256 $(d16 "$here/Topak/Admit.lean")) · lakefile.toml (sha256 $(d16 "$here/lakefile.toml")) · lean-toolchain $(cat "$here/lean-toolchain")"
echo "Prover: $(cd "$here" && lean --version) · $(cd "$here" && lake --version | head -1) · no Mathlib, no dependencies · driver: results.sh"
echo "Theorems: $(grep -oE '^(@\[simp\] )?theorem [A-Za-z0-9_]+' "$here/Topak/Admit.lean" | sed 's/.*theorem //' | paste -sd '|' - | sed 's/|/ · /g')"
echo "A theorem holds of the transcription, not of the Rust; the transcription's fidelity to admit.rs is read, each definition beside the Rust it transcribes. The lift, the store and the envelope (BundleCannotWriteFloorInputs, EnvelopeHolds) are outside this function and stay with the TLA+ module."
echo
(cd "$here" && rm -rf .lake && lake build 2>&1 | grep -vE '^\s*$|^trace:')
status=${PIPESTATUS[0]}
exit $status
