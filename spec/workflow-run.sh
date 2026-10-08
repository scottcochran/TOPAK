#!/bin/bash
# usage: workflow-run.sh name mut invariant[,invariant...]
# One row of Workflow.tla (ADR-0054, Proposed: a promoted workflow). Several invariants, comma-separated, are
# checked together; on a counterexample TLC names the one violated.
name=$1; mut=$2; inv=$3
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
{ echo "SPECIFICATION Spec"; for i in ${inv//,/ }; do echo "INVARIANT $i"; done
  printf 'CONSTANTS\n  Mut = "%s"\n' "$mut"; } > $name.cfg
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Workflow.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE $(echo "$out" | grep -oE "Invariant [A-Za-z]+ is violated" | head -1 | cut -d' ' -f2)"
elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "states generated, [0-9,]+ distinct states found" | tail -1 | grep -oE "[0-9,]+ distinct states found")
echo "$name | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg; rm -rf /tmp/tlc_$name
exit 0
