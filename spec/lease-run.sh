#!/bin/bash
# usage: lease-run.sh name mut invariant [maxepoch] [maxfence]
name=$1; mut=$2; inv=$3; maxep=${4:-2}; maxf=${5:-3}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  MaxEpoch = $maxep
  MaxFence = $maxf
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Lease.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9]+ distinct states found" | head -1)
echo "$name | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
exit 0
