#!/bin/bash
# Regenerates a Mechanism trace-validation results file (ADR-0045 T-0045-28, stage 1):
# runs the reference's core and e2e suites with tracing on, converts every trace, checks each
# against Mechanism.tla with TLC, and prints the results file.
#   usage: mechanism-trace-results.sh > Mechanism-trace-results-<date>.txt
# Needs: cargo (a built bundle under mechanism/bundles for the e2e suite), java, the TLC jar.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
jar=${TLA_JAR:-$root/tools/tla2tools.jar}
traces=$(mktemp -d /tmp/topak-traces.XXXXXX)
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "TOPAK — Mechanism.tla trace validation: the reference's recorded behaviours replayed through the operational model (ADR-0045 T-0045-28, stage 1)"
echo "Module: Mechanism.tla (sha256 $(shasum -a 256 "$here/Mechanism.tla" | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Reference: mechanism/ at $(cd "$root" && git rev-parse --short HEAD)$(cd "$root" && git diff --quiet -- mechanism || echo ' + working tree') · recorder: crates/topak-core/src/trace.rs · converter: trace2tla.py · driver: mechanism-trace-run.sh"
echo "Suites traced: topak-core tests/mutations.rs, tests/confinement.rs, tests/operators.rs and tests/emergency.rs (every state the helpers build) · topak-node tests/e2e.rs and tests/contain.rs (replica 1 of every cluster; contain.rs launches the demo guest, rung 3 SIMULATED)"
echo "A MATCH line means every recorded step's projected state and result equal the model's. A trace is one test; steps are applied log entries."
echo
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test mutations 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test confinement 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test operators 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-core --release --test emergency 2>&1 | grep "^test result")
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-node --release --test e2e 2>&1 | grep "^test result")
(cd "$root/mechanism" && cargo build -p topak-contain --release --bins 2>&1 | grep -E "^error" ; TOPAK_TRACE_DIR=$traces cargo test -p topak-node --release --test contain 2>&1 | grep "^test result")
echo
# One TLC per trace, ${JOBS:-6} at a time; each prints one line; sorted by trace name.
ls "$traces"/*.jsonl | TLA_JAR=$jar xargs -P "${JOBS:-6}" -n 1 "$here/mechanism-trace-run.sh" | sed 's/^Trace_//' | LC_ALL=C sort
echo
n=$(ls "$traces"/*.jsonl | wc -l | tr -d ' '); s=$(cat "$traces"/*.jsonl | grep -c '"index"')
echo "$n traces · $s steps"
rm -rf "$traces"
