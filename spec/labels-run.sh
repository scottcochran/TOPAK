#!/bin/bash
# usage: labels-run.sh name mut kind property [maxseq]
# One row of Labels.tla (ADR-0047, Proposed: labels on Run's ingress). kind is INVARIANT or PROPERTY.
name=$1; mut=$2; kind=$3; inv=$4; maxseq=${5:-3}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
$kind $inv
CONSTANTS
  Mut = "$mut"
  MaxSeq = $maxseq
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Labels.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9,]+ distinct states found" | head -1)
echo "$name | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg; rm -rf /tmp/tlc_$name
exit 0
