#!/bin/bash
# Regenerates a Labels.tla results file: header, then one TLC section per row.
# usage: labels-gen-results.sh "<title line>" rows.txt [maxseq] > Labels-results-<date>.txt   (rows: name mut kind property)
title=$1; rows=$2; maxseq=${3:-3}
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: Labels.tla (sha256 $(shasum -a 256 Labels.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: labels-gen-results.sh · MaxSeq = $maxseq · Tools = {fetch: outward, send: outward with a destination, vault: inside, restricted, echo: inside} · Names = {untrusted, restricted}"
echo
while read -r name mut kind inv; do
  [ -z "$name" ] && continue
  echo "=== $name · Mut=$mut · $kind $inv"
  printf 'SPECIFICATION Spec\n%s %s\nCONSTANTS\n  Mut = "%s"\n  MaxSeq = %s\n' "$kind" "$inv" "$mut" "$maxseq" > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Labels.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f $name.cfg; rm -rf /tmp/tlc_$name
  echo
done < "$rows"
