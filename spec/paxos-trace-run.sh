#!/bin/bash
# usage: paxos-trace-run.sh [--as Mut] <trace.jsonl>...
# Replays each recorded run of the reference's replicas (mechanism/crates/topak-paxos/tests/sim.rs, with
# TOPAK_TRACE_DIR set) through Paxos.tla (PaxosTrace.tla). Prints one line per trace:
#   name | N events | Mut=<the module's mutation> | MATCH
# or, in place of MATCH, the first event the code and the model disagree on and which comparison failed
# (RECEIVE, STATE or SENDS: PaxosTrace.tla's three invariants), or the property of Paxos.tla the replayed
# states violate. --as replays under that mutation of the module whatever the code ran under.
# Jar location: $TLA_JAR, else ../tools/tla2tools.jar, else ./tla2tools.jar
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
here=$(cd "$(dirname "$0")" && pwd)
as=""
if [ "${1:-}" = "--as" ]; then as=$2; shift 2; fi
for t in "$@"; do
  gen=$(python3 "$here/paxos-trace2tla.py" "$t" "$here" $as) || { echo "$t | ERROR converting"; continue; }
  read -r mod steps mut <<< "$gen"
  # Each TLC has its own temp directory: it unpacks the standard modules there, and runs in parallel collide
  # on a shared one.
  work=$(mktemp -d "${TMPDIR:-/tmp}/tlc_paxos.XXXXXX") || exit 2
  mkdir -p "$work/tmp"
  out=$(cd "$here" && java -XX:+UseParallelGC -Djava.io.tmpdir="$work/tmp" -cp "$jar" tlc2.TLC -config "$mod.cfg" -workers 1 -deadlock -metadir "$work/meta" "$mod.tla" 2>&1)
  if echo "$out" | grep -q "No error has been found"; then r="MATCH"
  elif echo "$out" | grep -q "is violated"; then
    at=$(echo "$out" | grep -oE "^/\\\\ i = [0-9]+" | tail -1 | grep -oE "[0-9]+")
    inv=$(echo "$out" | grep -oE "Invariant [A-Za-z]+ is violated" | head -1 | cut -d' ' -f2)
    case "$inv" in
      TraceReceivable)   r="MISMATCH at event $((at + 1)) (RECEIVE)" ;;
      TraceStateMatches) r="MISMATCH at event $((at + 1)) (STATE)" ;;
      TraceSendsMatch)   r="MISMATCH at event $((at + 1)) (SENDS)" ;;
      *)                 r="PROPERTY $inv violated after event $at" ;;
    esac
  else r="ERROR"; fi
  echo "${mod#Trace_} | $steps events | Mut=$mut | $r"
  [ "$r" = "ERROR" ] && echo "$out" | grep -v "^$" | tail -15
  (cd "$here" && rm -f -- "./${mod:?}.cfg" "./${mod:?}.tla")
  rm -rf -- "${work:?}"
done
exit 0
