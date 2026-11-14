#!/bin/bash
# Regenerates a Paxos trace-validation results file: runs the reference's consensus simulation with tracing on,
# converts every trace, replays each through Paxos.tla with TLC (PaxosTrace.tla), and prints the results file.
#   usage: paxos-trace-results.sh > Paxos-trace-results-<date>.txt
# Needs: cargo, java, python3, the TLC jar. JOBS (default 4) is the number of replays run at a time.
# Exits non-zero unless every line is the one expected: a run of the unmutated code matches; a run of mutated
# code matches the module under the same mutation up to its last event, where the property that mutation must
# break is violated; and the same run does not match the module under Mut = "none".
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
jar=${TLA_JAR:-$root/tools/tla2tools.jar}
traces=$(mktemp -d "${TMPDIR:-/tmp}/topak-paxos-traces.XXXXXX") || exit 2
out=$(mktemp -d "${TMPDIR:-/tmp}/topak-paxos-out.XXXXXX") || exit 2
trap 'rm -rf -- "${traces:?}" "${out:?}"' EXIT
d16() { shasum -a 256 "$1" | cut -c1-16; }
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "TOPAK — Paxos.tla trace validation: the reference's recorded consensus runs replayed through the operational model (PaxosTrace.tla; ADR-0033 §2 row P, finding 9)"
echo "Modules: Paxos.tla (sha256 $(d16 "$here/Paxos.tla")) · PaxosTrace.tla (sha256 $(d16 "$here/PaxosTrace.tla")) · TLC $tlcv (jar sha256 $(d16 "$jar")) · $(java -version 2>&1 | head -1)"
echo "Reference: mechanism/ at $(cd "$root" && git rev-parse --short HEAD)$(cd "$root" && git diff --quiet HEAD -- mechanism || echo ' + working tree') · recorder: crates/topak-paxos/tests/sim.rs over Replica::snapshot · converter: paxos-trace2tla.py (sha256 $(d16 "$here/paxos-trace2tla.py")) · driver: paxos-trace-run.sh (sha256 $(d16 "$here/paxos-trace-run.sh"))"
echo "Suite traced: topak-paxos tests/sim.rs, traced_runs_under_faults (the unmutated replica, three and five replicas, under loss, delay, duplication, partition and restarts) and traced_runs_under_each_mutation (the first seed a check catches, recorded up to the event that check fails on)"
echo "A trace is one simulated run of every replica; an event is one call of Replica::handle that did something. MATCH means that at every event the replica's state after the call, and what it sent, are the model's, and that the model's properties hold of every replayed state."
echo "expected: every run of the unmutated code is MATCH under Mut=none; every run of mutated code, replayed under its own mutation, matches to its last event, after which the property that mutation must break is violated (ChosenUnique, or NoAmplification for M_REQUEUE); replayed under Mut=none it is a MISMATCH"
echo
(cd "$root/mechanism" && TOPAK_TRACE_DIR=$traces cargo test -p topak-paxos --release --test sim 2>&1 | grep "^test result" | sed 's/; finished in.*//')
echo
echo "Each run, under the mutation the code ran under:"
ls "$traces"/*.jsonl | TLA_JAR=$jar xargs -P "${JOBS:-4}" -n 1 "$here/paxos-trace-run.sh" | LC_ALL=C sort | tee "$out/own"
echo
echo "Each run of mutated code, under Mut=none:"
ls "$traces"/paxos-M_*.jsonl | TLA_JAR=$jar xargs -P "${JOBS:-4}" -n 1 "$here/paxos-trace-run.sh" --as none | LC_ALL=C sort | tee "$out/asnone"
echo
n=$(ls "$traces"/*.jsonl | wc -l | tr -d ' '); e=$(cat "$traces"/*.jsonl | grep -c '"ev"')
unmutated=$(ls "$traces"/paxos-none-*.jsonl 2>/dev/null | wc -l | tr -d ' '); mutated=$(ls "$traces"/paxos-M_*.jsonl 2>/dev/null | wc -l | tr -d ' ')
ok=1
[ "$unmutated" -gt 0 ] && [ "$mutated" -gt 0 ] || ok=0
[ "$(grep -c '^paxos_none_.* | Mut=none | MATCH$' "$out/own")" = "$unmutated" ] || ok=0
# A mutated run under its own mutation: the property violated after event k, where k is the trace's last event.
good=$(awk -F' [|] ' '/^paxos_M_/ { split($2, a, " "); want = ($1 ~ /^paxos_M_REQUEUE_/) ? "NoAmplification" : "ChosenUnique";
                                    if ($4 == "PROPERTY " want " violated after event " a[1]) c++ } END { print c + 0 }' "$out/own")
[ "$good" = "$mutated" ] || ok=0
[ "$(grep -c ' | Mut=none | MISMATCH at event [0-9]* ([A-Z]*)$' "$out/asnone")" = "$mutated" ] || ok=0
echo "$n traces · $e events · $unmutated unmutated, $mutated mutated · $([ $ok -eq 1 ] && echo 'every line as expected' || echo 'NOT AS EXPECTED')"
[ $ok -eq 1 ]
