#!/bin/bash
# usage: confinement-run.sh name mut declared invariant [maxepoch] [maxidx] [maxgen]
name=$1; mut=$2; decl=$3; inv=$4; maxep=${5:-1}; maxi=${6:-4}; maxg=${7:-2}; mod=${MODULE:-Confinement}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  Declared = $decl
  MaxEpoch = $maxep
  MaxIdx = $maxi
  MaxGen = $maxg
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name $mod.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9,]+ distinct states found" | head -1)
echo "$name | Declared=$decl | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
exit 0
