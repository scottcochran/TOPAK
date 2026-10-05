#!/bin/bash
# Regenerates an Emergency.tla results file: header, then one TLC section per row.
# usage: emergency-gen-results.sh "<title line>" rows.txt [maxround] > Emergency-results-<date>.txt   (rows: name mut invariant)
title=$1; rows=$2; maxr=${3:-2}
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: Emergency.tla (sha256 $(shasum -a 256 Emergency.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: emergency-gen-results.sh · MaxRound = $maxr · roster of three, quorum two · one person, one agent · tools t1, t2 (promoted), te (emergency-only), tx (in no bundle)"
echo
while read -r name mut inv; do
  [ -z "$name" ] && continue
  echo "=== $name · Mut=$mut · INVARIANT $inv"
  printf 'SPECIFICATION Spec\nINVARIANT %s\nCONSTANTS\n  Mut = "%s"\n  MaxRound = %s\n' "$inv" "$mut" "$maxr" > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Emergency.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f $name.cfg; rm -rf /tmp/tlc_$name
  echo
done < "$rows"
