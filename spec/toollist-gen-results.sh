#!/bin/bash
# Regenerates a ToolList.tla results file: header, then one TLC section per row.
# usage: toollist-gen-results.sh "<title line>" rows.txt > ToolList-results-<date>.txt   (rows: name mut invariant)
title=$1; rows=$2
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: ToolList.tla (sha256 $(shasum -a 256 ToolList.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: toollist-gen-results.sh · Tools = {t1, t2, t3} · revision 1 allows {t1, t2}, revision 2 allows {t2, t3} · one principal"
echo
while read -r name mut inv; do
  [ -z "$name" ] && continue
  echo "=== $name · Mut=$mut · INVARIANT $inv"
  printf 'SPECIFICATION Spec\nINVARIANT %s\nCONSTANTS\n  Mut = "%s"\n' "$inv" "$mut" > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name ToolList.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f $name.cfg; rm -rf /tmp/tlc_$name
  echo
done < "$rows"
