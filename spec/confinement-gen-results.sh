#!/bin/bash
# Regenerates a Confinement.tla results file: header, then one TLC section per row (CR-23: one driver per results file).
# usage: confinement-gen-results.sh "<title line>" rows.txt > Confinement-results-<date>.txt   (rows: name mut declared invariant)
title=$1; rows=$2; mod=${MODULE:-Confinement}
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: $mod.tla (sha256 $(shasum -a 256 $mod.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: confinement-run.sh · Constants: MaxEpoch = 1 · MaxIdx = 4 · MaxGen = 2 · Principals = {p1, p2} · Promoted = {arch, med}"
echo
while read -r name mut decl inv; do
  [ -z "$name" ] && continue
  echo "=== $name · Declared=$decl · Mut=$mut · INVARIANT $inv"
  cat > $name.cfg <<CFG
SPECIFICATION Spec
INVARIANT $inv
CONSTANTS
  Mut = "$mut"
  Declared = $decl
  MaxEpoch = 1
  MaxIdx = 4
  MaxGen = 2
CFG
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name $mod.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  echo
done < "$rows"
