#!/bin/bash
# Checks the Lean re-encodings against TLC's state graphs (ADR-0053, Proposed). For each module and value of Mut, TLC
# dumps every reachable state and transition of the TLA+ module at its configured constants, with a derived variable
# carrying each property's value (a wrapper module, written here, that leaves the graph's shape unchanged);
# dot2lines.py reads the dump; graphcheck, through the module's proved mirror (TopakSpec/Mirror/*.lean), checks that
# every TLC edge is a step of the encoding's Next, that every Next step from a TLC state is a TLC edge or a stutter,
# that the initial states agree, and that every property has TLC's value in every state.
#   usage: graph-check.sh > GraphCheck-results-<date>.txt     (from spec/lean/)
# Needs java, the TLC jar, python3 and the toolchain tools/LEAN-PIN names. Exits non-zero if any graph does not match.
# GRAPHS_KEEP=<dir> keeps each converted graph as <dir>/<module>-<Mut>.lines; GRAPHCHECK=<binary> runs another checker
# on them (a mutated encoding's, in a scratch copy).
set -u
here=$(cd "$(dirname "$0")" && pwd)
spec=$(cd "$here/.." && pwd)
root=$(cd "$spec/.." && pwd)
export PATH="$HOME/.elan/bin:$PATH"
jar=${TLA_JAR:-$root/tools/tla2tools.jar}
tmp=$(mktemp -d /tmp/topak-graphs.XXXXXX)
d16() { shasum -a 256 "$root/$1" | cut -c1-16; }
e() { echo "$1 (sha256 $(d16 "$1"))"; }
(cd "$here" && lake build graphcheck >/dev/null 2>&1) || { echo "graphcheck does not build"; exit 1; }
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
echo "TOPAK — the Lean re-encodings checked against TLC's state graphs: every edge a Next step, every Next step an edge, the same initial states, the same property values"
echo "Transcribes: $(e spec/Seats.tla) · $(e spec/FloorComposition.tla)"
echo "Sources: $(e spec/lean/TopakSpec/Seats.lean) · $(e spec/lean/TopakSpec/FloorComposition.lean) · $(e spec/lean/TopakSpec/Mirror/Seats.lean) · $(e spec/lean/TopakSpec/Mirror/FloorComposition.lean) · $(e spec/lean/GraphCheck.lean) · $(e spec/lean/dot2lines.py) · $(e spec/lean/graph-check.sh) · $(e spec/lean/lakefile.toml)"
echo "Checker: TLC $tlcv (jar sha256 $(shasum -a 256 "$jar" | cut -c1-16)) · $(java -version 2>&1 | head -1) · $(cd "$here" && lean --version)"
echo "The mirrors' theorems (next_iff, init_iff, eqC_iff, one per property) are proved and replayed in TopakSpec-results; this run evaluates them on the graphs, a test. A MATCH line: no edge that is not a Next step, no Next step that is not an edge or a stutter, the initial states the encoding's Init, and every property TLC's value in every state."
echo
status=0
# module | Mut | properties
rows="Seats|none|OnlyThinkersAuthor OneSeatPerPrincipal
Seats|M_KIND|OnlyThinkersAuthor OneSeatPerPrincipal
Seats|M_SEAT|OnlyThinkersAuthor OneSeatPerPrincipal
FloorComposition|none|AdmitImpliesFloorPermit FloorErrorIsDeny BundleRefusalHonored BundleCannotWriteFloorInputs EnvelopeHolds
FloorComposition|M_OVERRIDE|AdmitImpliesFloorPermit FloorErrorIsDeny BundleRefusalHonored BundleCannotWriteFloorInputs EnvelopeHolds
FloorComposition|M_ERR|AdmitImpliesFloorPermit FloorErrorIsDeny BundleRefusalHonored BundleCannotWriteFloorInputs EnvelopeHolds
FloorComposition|M_FAILOPEN|AdmitImpliesFloorPermit FloorErrorIsDeny BundleRefusalHonored BundleCannotWriteFloorInputs EnvelopeHolds
FloorComposition|M_WRITE|AdmitImpliesFloorPermit FloorErrorIsDeny BundleRefusalHonored BundleCannotWriteFloorInputs EnvelopeHolds"
while IFS='|' read -r mod mut props; do
  d="$tmp/$mod-$mut"; mkdir -p "$d"
  cp "$spec/$mod.tla" "$d/"
  fields=$(for p in $props; do printf '%s |-> %s, ' "$p" "$p"; done | sed 's/, $//')
  cat > "$d/${mod}Dump.tla" <<TLA
---- MODULE ${mod}Dump ----
EXTENDS $mod
VARIABLE props
Props == [$fields]
DInit == Init /\\ props = Props
DNext == Next /\\ props' = Props'
DSpec == DInit /\\ [][DNext]_<<vars, props>>
====
TLA
  printf 'SPECIFICATION DSpec\nCONSTANTS\n  Mut = "%s"\n' "$mut" > "$d/d.cfg"
  out=$(cd "$d" && java -XX:+UseParallelGC -Djava.io.tmpdir="$d" -cp "$jar" tlc2.TLC -config d.cfg -workers 1 -deadlock \
        -dump dot,actionlabels graph.dot -metadir "$d/meta" "${mod}Dump.tla" 2>&1)
  if ! echo "$out" | grep -q "No error has been found"; then
    echo "$mod Mut=$mut | TLC ERROR"; echo "$out" | tail -5; status=1; continue
  fi
  python3 "$here/dot2lines.py" "$d/graph.dot" > "$d/graph.lines" || { echo "$mod Mut=$mut | CONVERSION ERROR"; status=1; continue; }
  [ -n "${GRAPHS_KEEP:-}" ] && cp "$d/graph.lines" "$GRAPHS_KEEP/$mod-$mut.lines"
  "${GRAPHCHECK:-$here/.lake/build/bin/graphcheck}" "$mod" "$mut" "$d/graph.lines" || status=1
done <<< "$rows"
rm -rf "$tmp"
exit $status
