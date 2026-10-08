#!/bin/bash
# Regenerates a Mesh.tla results file: header, then one TLC section per row.
# usage: mesh-gen-results.sh "<title line>" rows.txt > Mesh-results-<date>.txt
#   (rows: name mut invariant[,invariant...] [constraint]; several invariants are checked together; a row with a
#   fourth column is checked under that state constraint, and its section header says so)
title=$1; rows=$2
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
echo "Module: Mesh.tla (sha256 $(shasum -a 256 Mesh.tla | cut -c1-16)) · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | grep -v JAVA_TOOL_OPTIONS | head -1)"
echo "Runner: mesh-gen-results.sh · Nodes = {s, w, x} · a clear cycle s -e1-> w -e3-> s (e1 chosen, e3 computed) and a chosen handle exit e2 from s to the outward sink x, guarded by s ok · budget N = 6 · lineages {A, B}"
echo
while read -r name mut inv cons; do
  [ -z "$name" ] && continue
  echo "=== $name · Mut=$mut · INVARIANT ${inv//,/, }${cons:+ · CONSTRAINT $cons}"
  { echo "SPECIFICATION Spec"; for i in ${inv//,/ }; do echo "INVARIANT $i"; done
    [ -n "$cons" ] && echo "CONSTRAINT $cons"
    printf 'CONSTANTS\n  Mut = "%s"\n' "$mut"; } > mesh_$name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config mesh_$name.cfg -workers ${TLC_WORKERS:-auto} -deadlock -metadir ${TLC_METADIR:-/tmp}/tlc_mesh_$name Mesh.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating|Picked up JAVA_TOOL_OPTIONS|Checkpointing)" \
    | grep -v "^$"
  rm -f mesh_$name.cfg; rm -rf ${TLC_METADIR:-/tmp}/tlc_mesh_$name
  echo
done < "$rows"
