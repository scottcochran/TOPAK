#!/bin/bash
# Regenerates a Workflow.tla results file: header, then one TLC section per row.
# usage: workflow-gen-results.sh "<title line>" rows.txt > Workflow-results-<date>.txt
#   (rows: name mut invariant[,invariant...]; several invariants are checked together)
title=$1; rows=$2
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: Workflow.tla (sha256 $(shasum -a 256 Workflow.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | grep -v JAVA_TOOL_OPTIONS | head -1)"
echo "Runner: workflow-gen-results.sh · Nodes = {s, b, c, j} · one decision point s with chosen edges e1 (to b, clear) and e2 (to c, handle, outward); computed e3, e4 into j, joined on any · lineages {A, B} · one fence"
echo
while read -r name mut inv; do
  [ -z "$name" ] && continue
  echo "=== $name · Mut=$mut · INVARIANT ${inv//,/, }"
  { echo "SPECIFICATION Spec"; for i in ${inv//,/ }; do echo "INVARIANT $i"; done
    printf 'CONSTANTS\n  Mut = "%s"\n' "$mut"; } > $name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -metadir /tmp/tlc_$name Workflow.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating|Picked up JAVA_TOOL_OPTIONS)" \
    | grep -v "^$"
  rm -f $name.cfg; rm -rf /tmp/tlc_$name
  echo
done < "$rows"
