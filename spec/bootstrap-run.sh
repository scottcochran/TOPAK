#!/bin/bash
# usage: bootstrap-run.sh name module mut "active-set" invariant [maxepoch]
# Runs one invariant of one ADR-0029 §5 bootstrap module under one setting.
name=$1; mod=$2; mut=$3; active=$4; inv=$5; maxep=${6:-2}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Active = $active
  Mut = "$mut"
  MaxEpoch = $maxep
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name $mod.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9]+ distinct states found" | head -1)
echo "$name | $mod | Mut=$mut | $active | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
exit 0
