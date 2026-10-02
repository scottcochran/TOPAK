#!/bin/bash
# Regenerates a RunConfinement.tla results file: header, then one TLC section per row.
# usage: runconfinement-gen-results.sh "<title line>" rows.txt > RunConfinement-results-<date>.txt   (rows: name mut filtered invariant)
title=$1; rows=$2
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: RunConfinement.tla (sha256 $(shasum -a 256 RunConfinement.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: runconfinement-gen-results.sh · Principals = {p1, p2} · Tools = {w: wasm, f: filtered, n: native} · Targets = {a, b, c}"
echo
while read -r name mut filt inv; do
  [ -z "$name" ] && continue
  echo "=== $name · Filtered=$filt · Mut=$mut · INVARIANT $inv"
  printf 'SPECIFICATION Spec\nINVARIANT %s\nCONSTANTS\n  Mut = "%s"\n  Filtered = %s\n' "$inv" "$mut" "$filt" > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name RunConfinement.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f $name.cfg
  echo
done < "$rows"
