#!/bin/bash
# Statistical model checking: TLC in simulation mode, random behaviours to a depth, at constants the exhaustive
# runs cannot reach. A "No error" here is evidence of a different kind from a results row: it says no sampled
# behaviour violated the invariant, not that none does. Record it as a simulation, never cite it as a check.
#   usage: simulate-run.sh name module invariant "constants" [depth] [traces] [seed]
#   constants: one assignment per item, ';'-separated, as the module's cfg would carry them, e.g.
#              'Mut = "none"; K = 8; R = 64; MaxRound = 3'
#   example:   ./simulate-run.sh c-sim Coupling UnreadBounded 'Mut = "none"; K = 8; R = 64; MaxRound = 3' 200 2000
name=$1; mod=$2; inv=$3; consts=$4; depth=${5:-100}; num=${6:-1000}; seed=${7:-0}
jar=${TLA_JAR:-../tools/tla2tools.jar}
[ -f "$jar" ] || jar=tla2tools.jar
{
  echo "SPECIFICATION Spec"
  echo "INVARIANT $inv"
  echo "CONSTANTS"
  echo "$consts" | tr ';' '\n' | sed 's/^ *//; /^$/d; s/^/  /'
} > $name.cfg
out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -config $name.cfg -workers auto -deadlock -simulate num=$num -depth $depth -seed $seed -metadir /tmp/tlc_$name $mod.tla 2>&1)
# In simulation mode TLC prints no "No error has been found"; a run that finishes without an Error line sampled
# its traces and found no violation. "states checked" counts every successor TLC evaluated while sampling.
if echo "$out" | grep -q "is violated"; then r="COUNTEREXAMPLE"
elif echo "$out" | grep -q "^Finished in" && ! echo "$out" | grep -qE "^Error|Exception"; then r="NO ERROR SAMPLED"
else r="ERROR"; fi
checked=$(echo "$out" | grep -oE "[0-9,]+ states checked" | tail -1)
took=$(echo "$out" | grep -oE "Finished in [^(]+" | head -1 | sed 's/ at *$//')
echo "$name | $mod | $inv | $(echo "$consts" | tr -s ' ') | simulate depth=$depth traces=$num seed=$seed | $r | ${checked:-no progress line} | $took"
[ "$r" = "ERROR" ] && echo "$out" | tail -20
rm -f $name.cfg
exit 0
