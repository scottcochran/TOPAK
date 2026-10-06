#!/bin/bash
# Replays the reference's recorded traces through the Seats-shaped model of State::apply (Topak/SeatsModel.lean,
# ADR-0053, Proposed): runs the suites mechanism-trace-results.sh runs, with tracing on, and runs every trace
# through SeatsReplay.lean, which applies each recorded entry with the model's `apply` and compares the leases, the
# live index, the seat kinds and the result with the reference's. A test of the model against the code, not a proof.
#   usage: seats-replay.sh > SeatsReplay-results-<date>.txt     (from mechanism/lean/)
# Needs cargo (a built bundle under mechanism/bundles for the e2e suite) and the toolchain tools/LEAN-PIN names.
# Not byte for byte: the e2e traces are named after their process ids. Exits non-zero if a trace does not match.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
export PATH="$HOME/.elan/bin:$PATH"
traces=$(mktemp -d /tmp/topak-seats-traces.XXXXXX)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
echo "TOPAK — the reference's recorded behaviours replayed through the Seats-shaped model of State::apply (mechanism/lean/Topak/SeatsModel.lean)"
echo "Model: $(e mechanism/lean/Topak/SeatsModel.lean) · replay: $(e mechanism/lean/SeatsReplay.lean) · $(cd "$here" && lean --version) · driver: seats-replay.sh"
echo "Reference: mechanism/ at $(cd "$root" && git rev-parse --short HEAD)$(cd "$root" && git diff --quiet -- mechanism || echo ' + working tree') · $(e mechanism/crates/topak-core/src/state.rs) · recorder: $(e mechanism/crates/topak-core/src/trace.rs)"
echo "Suites traced: topak-core tests/mutations.rs, tests/confinement.rs, tests/operators.rs and tests/emergency.rs · topak-node tests/e2e.rs and tests/contain.rs (replica 1 of every cluster), as mechanism-trace-results.sh"
echo "A MATCH line means that at every recorded step the model, given whether the reference applied the entry, returned the reference's result and left the leases (seat, principal, Persona, confinement digest, alphabet, ended), live_by_seat, the seat kinds and last_applied as the reference did."
echo
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test mutations 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test confinement 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test operators 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test emergency 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-node --release --test e2e 2>&1 | grep "^test result")
(cd "$root/mechanism" && cargo build -p topak-contain --release --bins 2>&1 | grep -E "^error" ; TOPAK_TRACE_DIR=$traces cargo test -p topak-node --release --test contain 2>&1 | grep "^test result")
echo
(cd "$here" && lake build Topak.SeatsModel >/dev/null 2>&1) || { echo "the model does not build"; exit 1; }
(cd "$here" && lake env lean --run SeatsReplay.lean "$traces"/*.jsonl)
rc=$?
rm -rf "$traces"
exit $rc
