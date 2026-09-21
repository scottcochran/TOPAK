#!/bin/bash
# usage: run.sh name mech "active-set" invariant
name=$1; mech=$2; active=$3; inv=$4
cat > $name.cfg <<CFG
CONSTANTS
  Humans = {h1, h2, h3, h4}
  Author = h1
  AnchorKeys = {h4}
  Active = $active
  Mech = "$mech"
  h1 = h1
  h2 = h2
  h3 = h3
  h4 = h4
SPECIFICATION Spec
INVARIANT $inv
CFG
out=$(java -XX:+UseParallelGC -cp tla2tools.jar tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name RulesFloorNV.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9]+ distinct states found" | head -1)
echo "$name | $mech | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -25
exit 0
