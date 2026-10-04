#!/bin/bash
# usage: toollist-run.sh name mut invariant
# One row of ToolList.tla (ADR-0048, Proposed: the tool list).
name=$1; mut=$2; inv=$3
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
printf 'SPECIFICATION Spec\nINVARIANT %s\nCONSTANTS\n  Mut = "%s"\n' "$inv" "$mut" > $name.cfg
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name ToolList.tla 2>&1)
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"; elif echo "$out" | grep -q "No error has been found"; then r="HOLDS"; else r="ERROR"; fi
states=$(echo "$out" | grep -oE "[0-9,]+ distinct states found" | head -1)
echo "$name | Mut=$mut | $inv | $r | $states"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg; rm -rf /tmp/tlc_$name
exit 0
