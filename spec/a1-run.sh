#!/usr/bin/env bash
# a1-run.sh <Module> <rows-file> <title>   — TLC rows for a successor module, as a results file.
# Each row: name Mut invariant [Active], whitespace-separated; Active is given for modules that
# extend RulesFloorBase (default: every entry). MaxEpoch = 2 and MaxRound = 2 unless set in the
# environment. Used for BreakGlass_A1.tla and NonComposition_A1.tla (ADR-0052 §9).
set -u
mod=$1; rows=$2; title=$3
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
maxe=${MAXEPOCH:-2}; maxr=${MAXROUND:-2}
all='{"R1","R2","R5","R6","R7","R9"}'
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "$title"
deps=""; grep -q "^EXTENDS RulesFloorBase" $mod.tla && deps=" · RulesFloorBase.tla (sha256 $(shasum -a 256 RulesFloorBase.tla | cut -c1-16))"
echo "Module: $mod.tla (sha256 $(shasum -a 256 $mod.tla | cut -c1-16))$deps · TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1)"
echo "Runner: a1-run.sh · rows: $rows · MaxRound = $maxr$(grep -q MaxEpoch $mod.tla && echo " · MaxEpoch = $maxe")"
echo
while read -r name mut inv active; do
  [ -z "$name" ] && continue
  case "$name" in \#*) continue ;; esac
  consts="  Mut = \"$mut\"\n  MaxRound = $maxr\n"
  if grep -q "^EXTENDS RulesFloorBase" $mod.tla; then
    consts="$consts  MaxEpoch = $maxe\n  Active = ${active:-$all}\n"
    echo "=== $name · Mut=$mut · Active=${active:-$all} · INVARIANT $inv"
  else
    echo "=== $name · Mut=$mut · INVARIANT $inv"
  fi
  printf "SPECIFICATION Spec\nINVARIANT $inv\nCONSTANTS\n$consts" > a1_$name.cfg
  java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config a1_$name.cfg -workers auto -deadlock -metadir /tmp/tlc_a1_$name $mod.tla 2>&1 \
    | grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" \
    | grep -v "^$"
  rm -f a1_$name.cfg; rm -rf /tmp/tlc_a1_$name
  echo
done < "$rows"
