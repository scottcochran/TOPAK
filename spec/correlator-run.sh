#!/bin/bash
# usage: correlator-run.sh name mut invariant [nstores] [maxsends] [mmiss]
# One row of Correlator.tla (ADR-0051, Proposed: the correlator's detection function).
name=$1; mut=$2; inv=$3; nst=${4:-1}; maxs=${5:-1}; mm=${6:-1}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
if [ "$nst" = 2 ]; then st='{"a", "b"}'; else st='{"a"}'; fi
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  Thinkers = {"t1", "t2"}
  Stores = $st
  Corrs = {"c1", "c2"}
  Honest = {"c1"}
  MaxRound = 2
  MaxSends = $maxs
  MMiss = $mm
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Correlator.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9,]+ distinct states found" | head -1)
echo "$name | Stores=$nst | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg; rm -rf /tmp/tlc_$name
exit 0
