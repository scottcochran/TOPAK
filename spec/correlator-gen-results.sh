#!/bin/bash
# Regenerates a Correlator.tla results file: header, then one TLC section per row.
# usage: correlator-gen-results.sh "<title line>" rows.txt > Correlator-results-<date>.txt   (rows: name mut invariant nstores maxsends mmiss)
title=$1; rows=$2
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: Correlator.tla (sha256 $(shasum -a 256 Correlator.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: correlator-gen-results.sh · Thinkers = {t1, t2} · Corrs = {c1, c2} · Honest = {c1} · MaxRound = 2 · Items = {i} · Stores = {a}, or {a, b} where the row says Stores=2 · MaxSends and MMiss as the row says"
echo
while read -r name mut inv nst maxs mm; do
  [ -z "$name" ] && continue
  if [ "$nst" = 2 ]; then st='{"a", "b"}'; else st='{"a"}'; fi
  echo "=== $name · Stores=$nst · MaxSends=$maxs · MMiss=$mm · Mut=$mut · INVARIANT $inv"
  printf 'SPECIFICATION Spec\nINVARIANT %s\nCONSTANTS\n  Mut = "%s"\n  Thinkers = {"t1", "t2"}\n  Stores = %s\n  Corrs = {"c1", "c2"}\n  Honest = {"c1"}\n  MaxRound = 2\n  MaxSends = %s\n  MMiss = %s\n' "$inv" "$mut" "$st" "$maxs" "$mm" > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Correlator.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f $name.cfg; rm -rf /tmp/tlc_$name
  echo
done < "$rows"
