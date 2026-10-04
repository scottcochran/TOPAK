#!/bin/bash
# usage: operators-run.sh name mut invariant [nops] [maxround]
# One row of Operators.tla (ADR-0050, Proposed: the operator as a principal).
name=$1; mut=$2; inv=$3; nops=${4:-2}; maxr=${5:-2}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
if [ "$nops" = 3 ]; then ops='{"a", "b", "c"}'; else ops='{"a", "b"}'; fi
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  Ops = $ops
  MaxRound = $maxr
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Operators.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9,]+ distinct states found" | head -1)
echo "$name | Ops=$nops | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg; rm -rf /tmp/tlc_$name
exit 0
