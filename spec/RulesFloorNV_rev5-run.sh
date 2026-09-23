#!/bin/bash
# usage: RulesFloorNV_rev5-run.sh name mech "active-set" invariant
# Jar location: $TLA_JAR, else ../tools/tla2tools.jar, else ./tla2tools.jar
name=$1; mech=$2; active=$3; inv=$4
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Active = $active
  Mech = "$mech"
CFG
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name RulesFloorNV_rev5.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9]+ distinct states found" | head -1)
echo "$name | $mech | $active | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
exit 0
