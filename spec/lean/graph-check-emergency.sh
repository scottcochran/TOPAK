#!/bin/bash
# Checks the Lean re-encoding of Emergency and Emergency_live (TopakSpec/Emergency.lean) against TLC's state graphs
# (ADR-0053), as graph-check.sh checks those of Seats and FloorComposition. For each module and value of Mut, TLC dumps
# every reachable state and transition of the TLA+ module at MaxRound = 2, the value its TLC results use, with a
# derived variable carrying each property's value (a wrapper module, written here, that leaves the graph's shape
# unchanged); dot2lines.py reads the dump; graphcheck-emergency, through the proved mirror
# (TopakSpec/Mirror/Emergency.lean), checks that every TLC edge is a step of the encoding's relation, that every step of
# that relation from a TLC state is a TLC edge or a stutter, that the initial states agree, and that every property
# has TLC's value in every state. Emergency's rows check its Spec, whose relation is Next; Emergency_live's check its
# SpecL, whose relation is NextL.
# Emergency_live's two properties over ENABLED ride in the derived variable like its other six: TLC evaluates them
# in each state the dump reaches, and the check compares them as it compares the others.
# -deadlock: a state without successors belongs to the graph, and check 2 compares its successors, none, with the
# encoding's.
# A results series of its own, apart from graph-check.sh's: the premise binding takes the faithfulness of the Seats
# and FloorComposition encodings from the newest GraphCheck-results-*.txt, and only while every file that file names is
# as the tree has it, so Emergency's files are kept out of it. The two series share Prelude.lean, GraphCheckCore.lean, dot2lines.py, lakefile.toml and lean-toolchain, and an edit to
# any of them stales both; lakefile.toml also holds graphcheck-emergency's stanza, since one Lake package builds both.
#   usage: graph-check-emergency.sh > GraphCheckEmergency-results-<date>.txt     (from spec/lean/)
# Needs java, the TLC jar, python3 and the toolchain tools/LEAN-PIN names. Exits non-zero if any graph does not match.
# GRAPHS_KEEP=<dir> keeps each converted graph as <dir>/<module>-<Mut>.lines; GRAPHCHECK=<binary> runs another checker
# on them (a mutated encoding's, in a scratch copy). The dumps go under $TMPDIR (else /tmp) and are removed.
set -u
here=$(cd "$(dirname "$0")" && pwd)
spec=$(cd "$here/.." && pwd)
root=$(cd "$spec/.." && pwd)
export PATH="$HOME/.elan/bin:$PATH"
jar=${TLA_JAR:-$root/tools/tla2tools.jar}
tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-graphs.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
(cd "$here" && lake build graphcheck-emergency >/dev/null 2>&1) || { echo "graphcheck-emergency does not build"; exit 1; }
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "TOPAK — the Emergency encoding checked against TLC's state graphs: every edge a Next step (NextL for Emergency_live), every such step an edge, the same initial states, the same property values, those over ENABLED included"
echo "Transcribes: $(e spec/Emergency.tla) · $(e spec/Emergency_live.tla)"
echo "Sources: $(e spec/lean/TopakSpec/Prelude.lean) · $(e spec/lean/TopakSpec/Temporal.lean) · $(e spec/lean/TopakSpec/Emergency.lean) · $(e spec/lean/TopakSpec/Mirror/Emergency.lean) · $(e spec/lean/GraphCheckCore.lean) · $(e spec/lean/GraphCheckEmergency.lean) · $(e spec/lean/dot2lines.py) · $(e spec/lean/graph-check-emergency.sh) · $(e spec/lean/lakefile.toml) · $(e spec/lean/lean-toolchain)"
echo "Checker: TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1) · $(cd "$here" && lean --version)"
echo "The mirror's theorems (next_iff, nextL_iff, init_iff, eqC_iff, one per property) are proved and replayed in TopakSpec-results; this run evaluates them on the graphs, a test. A MATCH line: no edge that is not a step of the row's relation, no step of it that is not an edge or a stutter, the initial states the encoding's Init, and every property TLC's value in every state. Emergency and Emergency_live at MaxRound = 2; Emergency's rows are of its Spec and Next, Emergency_live's of its SpecL and NextL, whose two properties over ENABLED ride in the derived variable like its other six."
echo
status=0
em="EmergencyLeaseHasARosterQuorum EmergencyLeaseIsOneRound NoAgentHoldsAnEmergencySeat CallsAreAllowlisted ThinkerStillCoupled ActivationIsForensic"
en="EmergencyNeverCoupled EmergencyCallsWithoutObserver"
# module | Mut | properties, carried by the derived variable
rows="Emergency|none|$em
Emergency|M_NOQUORUM|$em
Emergency|M_REGRANT|$em
Emergency|M_RENEW|$em
Emergency|M_AGENT|$em
Emergency|M_X1|$em
Emergency|M_UNCOUPLE|$em
Emergency|M_ERASE|$em
Emergency_live|none|$em $en
Emergency_live|M_EMCOUPLE|$em $en
Emergency_live|M_EMCOUPLE2|$em $en"
while IFS='|' read -r mod mut props; do
  d="$tmp/$mod-$mut"; mkdir -p "$d"
  # the modules to copy and the relation
  case $mod in
    Emergency) srcs="Emergency"; next=Next;;
    Emergency_live) srcs="Emergency Emergency_live"; next=NextL;;
    *) echo "$mod Mut=$mut | UNKNOWN MODULE"; status=1; rm -rf "$d"; continue;;
  esac
  for s in $srcs; do cp "$spec/$s.tla" "$d/"; done
  fields=$(for p in $props; do printf '%s |-> %s, ' "$p" "$p"; done | sed 's/, $//')
  cat > "$d/${mod}Dump.tla" <<TLA
---- MODULE ${mod}Dump ----
EXTENDS $mod
VARIABLE props
Props == [$fields]
DInit == Init /\\ props = Props
DNext == $next /\\ props' = Props'
DSpec == DInit /\\ [][DNext]_<<vars, props>>
====
TLA
  printf 'SPECIFICATION DSpec\nCONSTANTS\n  Mut = "%s"\n  MaxRound = 2\n' "$mut" > "$d/d.cfg"
  (cd "$d" && java -XX:+UseParallelGC -Djava.io.tmpdir="$d" -cp "$jar" tlc2.TLC -config d.cfg -workers 1 -deadlock \
        -dump dot,actionlabels graph.dot -metadir "$d/meta" "${mod}Dump.tla" > "$d/tlc.out" 2>&1)
  if ! grep -q "No error has been found" "$d/tlc.out"; then
    echo "$mod Mut=$mut | TLC ERROR"; tail -5 "$d/tlc.out"; status=1; rm -rf "$d"; continue
  fi
  python3 "$here/dot2lines.py" "$d/graph.dot" > "$d/graph.lines" || { echo "$mod Mut=$mut | CONVERSION ERROR"; status=1; rm -rf "$d"; continue; }
  [ -n "${GRAPHS_KEEP:-}" ] && cp "$d/graph.lines" "$GRAPHS_KEEP/$mod-$mut.lines"
  "${GRAPHCHECK:-$here/.lake/build/bin/graphcheck-emergency}" "$mod" "$mut" "$d/graph.lines" || status=1
  rm -rf "$d"
done <<< "$rows"
exit $status
