#!/bin/bash
# usage: mechanism-trace-run.sh <trace.jsonl>...
# Checks each recorded trace of the reference against Mechanism.tla (ADR-0045 T-0045-28, stage 1), and its
# states against ConfinementRefinement.tla (the abstract confinement invariants).
# Prints one line per trace: name | steps | MATCH, or the first mismatching step.
# Jar location: $TLA_JAR, else ../tools/tla2tools.jar, else ./tla2tools.jar
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
here=$(cd "$(dirname "$0")" && pwd)
for t in "$@"; do
  gen=$(python3 "$here/trace2tla.py" "$t" "$here") || { echo "$t | ERROR converting"; continue; }
  mod=${gen% *}; steps=${gen#* }
  # Each TLC has its own temp directory: it unpacks the standard modules there, and runs in
  # parallel (mechanism-trace-results.sh) collide on a shared one.
  mkdir -p /tmp/tlc_$mod/tmp
  out=$(cd "$here" && java -XX:+UseParallelGC -Djava.io.tmpdir=/tmp/tlc_$mod/tmp -cp "$jar" tlc2.TLC -config $mod.cfg -workers 1 -deadlock -metadir /tmp/tlc_$mod $mod.tla 2>&1)
  if echo "$out" | grep -q "No error has been found"; then r="MATCH"
  elif echo "$out" | grep -q "is violated"; then
    at=$(echo "$out" | grep -oE "^/\\\\ i = [0-9]+" | tail -1 | grep -oE "[0-9]+")
    if echo "$out" | grep -q "Invariant TraceMatches is violated"; then r="MISMATCH at step $((at + 1))"
    else r="REFINEMENT $(echo "$out" | grep -oE "Invariant [A-Za-z]+ is violated" | head -1 | cut -d' ' -f2) violated at step $at"; fi
  else r="ERROR"; fi
  echo "$mod | $steps steps | $r"
  [ "$r" = "ERROR" ] && echo "$out" | grep -v "^$" | tail -15
  rm -f "$here/$mod.cfg"; rm -rf /tmp/tlc_$mod
done
exit 0
