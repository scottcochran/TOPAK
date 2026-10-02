#!/bin/bash
# usage: runconfinement-run.sh name mut filtered invariant
# One row of RunConfinement.tla (ADR-0034 A2, pending: channel fidelity for Run).
name=$1; mut=$2; filt=$3; inv=$4
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  Filtered = $filt
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name RunConfinement.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9,]+ distinct states found" | head -1)
echo "$name | Filtered=$filt | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg
exit 0
