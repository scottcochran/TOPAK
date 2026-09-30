#!/bin/bash
# usage: runcoupling-run.sh name mut invariant [K] [R] [MaxRound]
name=$1; mut=$2; inv=$3; k=${4:-1}; r=${5:-4}; mr=${6:-2}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  K = $k
  R = $r
  MaxRound = $mr
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name RunCoupling.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9]+ distinct states found" | head -1)
echo "$name | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -25
rm -f $name.cfg
exit 0
