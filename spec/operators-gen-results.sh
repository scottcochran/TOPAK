#!/bin/bash
# Regenerates an Operators.tla results file: header, then one TLC section per row.
# usage: operators-gen-results.sh "<title line>" rows.txt [maxround] > Operators-results-<date>.txt   (rows: name mut invariant nops)
title=$1; rows=$2; maxr=${3:-2}
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: Operators.tla (sha256 $(shasum -a 256 Operators.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: operators-gen-results.sh · MaxRound = $maxr · Workers = {w} · Ops = {a, b}, or {a, b, c} where the row says Ops=3 · widths 1..2"
echo
while read -r name mut inv nops; do
  [ -z "$name" ] && continue
  if [ "$nops" = 3 ]; then ops='{"a", "b", "c"}'; else ops='{"a", "b"}'; fi
  echo "=== $name · Ops=$nops · Mut=$mut · INVARIANT $inv"
  printf 'SPECIFICATION Spec\nINVARIANT %s\nCONSTANTS\n  Mut = "%s"\n  Ops = %s\n  MaxRound = %s\n' "$inv" "$mut" "$ops" "$maxr" > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Operators.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f $name.cfg; rm -rf /tmp/tlc_$name
  echo
done < "$rows"
