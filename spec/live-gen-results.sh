#!/bin/bash
# Regenerates a results file for a module that adds liveness or ENABLED properties to a frozen one
# (Coupling_live.tla, Emergency_live.tla): header, then one TLC section per row, each ending with its verdict and
# whether it is the one the row expects.
#   usage: live-gen-results.sh <Module> <rows-file> "<title line>" ["<expected line>"] > <Module>-results-<date>.txt
# Run from spec/. A row is: name mut spec kind property expected [CONST=value ...] [states=N], whitespace-separated.
# kind is INVARIANT, PROPERTY (a temporal property, checked by TLC's liveness checker) or DEADLOCK (the invariant,
# with TLC's deadlock check on). expected is HOLDS or VIOLATED. CONST=value overrides the module's default for that
# row: K=1 R=3 MaxRound=2 for Coupling_live, MaxRound=2 for Emergency_live, $DEFAULTS for any other module. states=N
# also expects TLC to find exactly N distinct states. Lines starting with # are comments, and so is the rest of a
# row from a #; a "# expected: ..." line in the rows file is the header's expected line when no fourth argument is
# given.
# Verdicts: HOLDS when TLC completes with no error (exit 0). VIOLATED when TLC reports the row's invariant violated
# (exit 12); on a PROPERTY row, "Temporal properties were violated" or the action property violated (exit 13), or a
# []P property violated, which TLC reports as an invariant of the property's name (exit 12); on a DEADLOCK row,
# "Deadlock reached" (exit 11), and nothing else: an invariant violated on a DEADLOCK row is ERROR. ERROR otherwise.
# Exits non-zero if any row is ERROR or not as expected, or if the rows file has no rows.
# -deadlock is passed except on a DEADLOCK row. For a temporal property TLC reads a state with no successor as
# stuttering forever, which is how TLA+ reads a behaviour that stops. Neither module has such a state: the
# Observer's GrantO and EndO (Coupling) and ObsToggle (Emergency) are always enabled, which the DEADLOCK rows check.
# One worker and a fixed fingerprint function (-workers 1 -fp 0): with TLC's random choice of fingerprint function
# a liveness counterexample changes from run to run. Each row's .cfg, output, metadir and java.io.tmpdir are in a
# mktemp directory, removed when the row ends; nothing is written to spec/. The private java.io.tmpdir is where TLC
# unpacks Naturals.tla and the other standard modules: in the shared one, a TLC run at the same time can remove them
# under this one, which then prints "Encountered an exception while attempt to validate".
set -u
set -f
usage='usage: live-gen-results.sh <Module> <rows-file> "<title line>" ["<expected line>"]'
mod=${1:?$usage}; rows=${2:?$usage}; title=${3:?$usage}; expected=${4:-}
mod=${mod%.tla}
[ -f "$rows" ] || { echo "no rows file $rows" >&2; exit 2; }
rowsabs=$(cd "$(dirname "$rows")" && pwd)/$(basename "$rows")
here=$(cd "$(dirname "$0")" && pwd)
cd "$here" || exit 2
[ -f "$mod.tla" ] || { echo "no $here/$mod.tla" >&2; exit 2; }
jar=${TLA_JAR:-../tools/tla2tools.jar}; [ -f "$jar" ] || jar=tla2tools.jar
case "$mod" in
  Coupling_live)  defaults="K=1 R=3 MaxRound=2"
                  model="one Thinker, its cell Observer, one correlator" ;;
  Emergency_live) defaults="MaxRound=2"
                  model="roster of three, quorum two · one person, one agent · tools t1, t2 (promoted), te (emergency-only), tx (in no bundle)" ;;
  *)              defaults=${DEFAULTS:-}; model="" ;;
esac
d16() { shasum -a 256 "$1" | cut -c1-16; }
# Every local module the module reaches through EXTENDS, in dependency order.
chain=""
visit() {
  local m=$1 d
  case " $chain " in *" $m "*) return ;; esac
  for d in $(grep -m1 '^EXTENDS' "$m.tla" | sed 's/^EXTENDS//; s/,/ /g'); do
    [ -f "$d.tla" ] && visit "$d"
  done
  chain="$chain $m"
}
visit "$mod"
ext=""
for m in $chain; do [ "$m" = "$mod" ] || ext="$ext${ext:+ · }$m.tla (sha256 $(d16 "$m.tla"))"; done
tlcv=$(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE "Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+" | head -1)
shown=""
for kv in $defaults; do shown="$shown · ${kv%%=*} = ${kv#*=}"; done
[ -n "$expected" ] || expected=$(grep -m1 '^# expected: ' "$rowsabs" | sed 's/^# //')
[ -n "$expected" ] || expected="expected: as each row's verdict line states"
case "$expected" in expected:*) ;; *) expected="expected: $expected" ;; esac
echo "$title"
echo "Module: $mod.tla (sha256 $(d16 "$mod.tla"))${ext:+ · extends $ext} · TLC $tlcv (jar sha256 $(d16 "$jar")) · $(java -version 2>&1 | head -1)"
echo "Runner: live-gen-results.sh (sha256 $(d16 "$here/live-gen-results.sh")) · rows: $(basename "$rows") (sha256 $(d16 "$rowsabs"))${shown:+ ·${shown# ·} unless the row says otherwise}${model:+ · $model} · TLC -workers 1 -fp 0, with -deadlock except on a DEADLOCK row"
echo "$expected"
echo
tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-live.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
status=0; n=0; nok=0; bad=""; errs=""
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in \#*) continue ;; esac
  line=${line%%#*}
  set -- $line
  [ $# -eq 0 ] && continue
  n=$((n + 1))
  if [ $# -lt 6 ]; then
    echo "=== malformed row: $line"; echo "→ ERROR (the row has fewer than six fields)"; echo
    errs="$errs $1"; status=1; continue
  fi
  name=$1; mut=$2; spec=$3; kind=$4; prop=$5; exp=$6; shift 6
  want=""; over=""; malformed=""
  for kv in "$@"; do
    case "$kv" in
      states=*) want=${kv#states=} ;;
      *=*)      over="$over $kv" ;;
      *)        malformed="$malformed $kv" ;;
    esac
  done
  case "$kind" in INVARIANT|PROPERTY|DEADLOCK) ;; *) malformed="$malformed kind=$kind" ;; esac
  case "$exp" in HOLDS|VIOLATED) ;; *) malformed="$malformed expected=$exp" ;; esac
  consts=""
  for d in $defaults; do
    k=${d%%=*}; v=${d#*=}
    for kv in $over; do [ "${kv%%=*}" = "$k" ] && v=${kv#*=}; done
    consts="$consts $k=$v"
  done
  for kv in $over; do
    case " $defaults " in *" ${kv%%=*}="*) ;; *) consts="$consts $kv" ;; esac
  done
  consts=${consts# }
  tk=$kind; dl="-deadlock"; note=""
  if [ "$kind" = DEADLOCK ]; then tk=INVARIANT; dl=""; note=" · deadlock check on"; fi
  echo "=== $name · Mut=$mut${consts:+ · $consts} · SPECIFICATION $spec · $tk $prop$note"
  if [ -n "$malformed" ]; then
    echo "→ ERROR (malformed row:$malformed)"; echo
    errs="$errs $name"; status=1; continue
  fi
  cfg="$tmp/$name.cfg"; out="$tmp/$name.out"
  {
    echo "SPECIFICATION $spec"
    echo "$tk $prop"
    echo "CONSTANTS"
    echo "  Mut = \"$mut\""
    for kv in $consts; do echo "  ${kv%%=*} = ${kv#*=}"; done
  } > "$cfg"
  mkdir -p "$tmp/$name.jtmp"
  java -XX:+UseParallelGC -Djava.io.tmpdir="$tmp/$name.jtmp" -cp "$jar" tlc2.TLC -config "$cfg" -workers 1 -fp 0 $dl \
    -metadir "$tmp/$name" "$mod.tla" > "$out" 2>&1
  rc=$?
  grep -vE "^(TLC2|Running breadth|Computing initial|Finished computing|Checking temporal|Progress\(|Starting\.\.\.|Parsing|Semantic|Implied-temporal|Warning: Please run|Loading|Computed|Generating)" "$out" \
    | grep -v "^$"
  got=ERROR
  if [ $rc -eq 0 ] && grep -q "^Model checking completed. No error has been found." "$out"; then got=HOLDS
  elif [ $rc -eq 12 ] && [ "$kind" = INVARIANT ] && grep -q "^Error: Invariant $prop is violated" "$out"; then got=VIOLATED
  elif [ $rc -eq 13 ] && [ "$kind" = PROPERTY ] \
       && grep -qE "^Error: (Temporal properties were violated|Action property $prop is violated)" "$out"; then got=VIOLATED
  elif [ $rc -eq 12 ] && [ "$kind" = PROPERTY ] && grep -q "^Error: Invariant $prop is violated" "$out"; then got=VIOLATED
  elif [ $rc -eq 11 ] && [ "$kind" = DEADLOCK ] && grep -q "^Error: Deadlock reached" "$out"; then got=VIOLATED
  fi
  ok=1
  if [ "$got" = "$exp" ]; then verdict="→ $got (expected $exp: as expected)"; else verdict="→ $got (expected $exp: NOT AS EXPECTED)"; ok=0; fi
  if [ -n "$want" ]; then
    states=$(grep -oE "[0-9]+ distinct states found" "$out" | tail -1 | grep -oE "^[0-9]+")
    if [ "${states:-}" = "$want" ]; then verdict="$verdict · $states distinct states (expected $want: as expected)"
    else verdict="$verdict · ${states:-no count of} distinct states (expected $want: NOT AS EXPECTED)"; ok=0; fi
  fi
  [ "$got" = ERROR ] && { errs="$errs $name"; ok=0; }
  if [ $ok -eq 1 ]; then nok=$((nok + 1)); else status=1; [ "$got" = ERROR ] || bad="$bad $name"; fi
  echo "$verdict"
  echo
  rm -rf "$tmp/$name" "$tmp/$name.jtmp" "$cfg" "$out"
done < "$rowsabs"
echo "Rows: $n · as expected: $nok · not as expected:${bad:- none} · ERROR:${errs:- none}"
[ $n -gt 0 ] || { echo "no rows"; exit 1; }
exit $status
