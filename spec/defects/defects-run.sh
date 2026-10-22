#!/bin/bash
# Reproduces the prover's two unsound cases (proof-certification.md §8; ADR-0046 A2, ADR-0045 A3) from the modules
# in this directory, which are §8's listings as files. Three steps, as §8 and ADR-0046's ratification condition
# describe them: (1) tlapm --toolbox 0 0 on each prover module, reporting the backend that closed each obligation,
# against what §8 says proves and what must not; (2) proof-cert.sh on each, which must certify ten and not HiddenDef
# or HiddenBox; (3) TLC on BinderDefectTLC, which must find each of the eight statements false.
#   usage: defects/defects-run.sh > defects/defects-results-<date>.txt      (from spec/)
# The modules EXTEND Emergency_live and Emergency_live_proof, which live in spec/, so tlapm runs with -I .. and TLC
# runs from spec/ on the path defects/BinderDefectTLC.tla; proof-cert.sh takes the module as defects/<Module>.
# Every cache, evidence dir, .cfg and metadir is in a mktemp directory removed at the end; nothing is written here.
# Exits 1 if any outcome differs from §8, 2 if a step could not run, else 0.
set -u
here=$(cd "$(dirname "$0")" && pwd)       # spec/defects
spec=$(cd "$here/.." && pwd)              # spec
root=$(cd "$spec/.." && pwd)
cd "$spec" || exit 2
tlapm="$root/tools/tlapm"; jar="$root/tools/tla2tools.jar"
[ -x "$tlapm" ] && [ -f "$jar" ] || { echo "need tools/tlapm and tools/tla2tools.jar" >&2; exit 2; }
tmp=$(mktemp -d "${TMPDIR:-/tmp}/topak-defects.XXXXXX") || exit 2
trap 'rm -rf "$tmp"' EXIT
d16() { shasum -a 256 "$1" | cut -c1-16; }
cfg=$("$tlapm" --config 2>/dev/null)
bin=$(echo "$cfg" | sed -n 's/^tlapm_executable == "\(.*\)"$/\1/p')
ver() { echo "$cfg" | sed -n "s/^$1 version == \"\(.*\)\"$/\1/p" | head -1; }
provers="EnabledUnderBinder TemporalUnderBinder CdotUnderBinder CombineUnderBinder BoxNorm HiddenDef HiddenBox ConjBox NameCollision EnabledCollision CaptureName CapturePTL"
# What §8 says of each lemma: proved, and by which backend where the table names one; or failed.
expect() {
cat <<'ROWS'
EnabledUnderBinder  Bad            proved smt
TemporalUnderBinder BadEventually  proved smt
TemporalUnderBinder BadLeadsTo     proved smt
CdotUnderBinder     BadCdot        proved smt
CombineUnderBinder  OneInst        proved -
CombineUnderBinder  AllFromOne     proved smt
BoxNorm             InvSmallAlways proved -
BoxNorm             InvBigAlways   proved smt
HiddenDef           InstTe         proved -
HiddenDef           Closure        proved -
HiddenDef           Literal        proved -
HiddenDef           SuperBad       failed -
HiddenDef           OutsideBad     failed -
HiddenBox           Small          proved -
HiddenBox           BigBad         proved smt
HiddenBox           BigPTL         failed -
ConjBox             SmallI         proved -
ConjBox             BigI           proved smt
ConjBox             BigE           proved -
ConjBox             SmallE         proved smt
NameCollision       BoxD33         proved -
NameCollision       NotBoxE280     proved -
NameCollision       FalseBySMT     proved smt
NameCollision       In             proved -
NameCollision       Out            proved -
NameCollision       FalseByPTL     proved ls4
EnabledCollision    TwoNew         proved smt
CaptureName         Capture        proved smt
CapturePTL          DiagAlways     proved -
CapturePTL          LHInst         proved ls4
CapturePTL          LHAll          proved smt
ROWS
}
certexp() { case "$1" in HiddenDef|HiddenBox) echo "not certified";; *) echo "certified";; esac; }
tlcrows() {
cat <<'ROWS'
INVARIANT BadInv
PROPERTY BadEventually
PROPERTY BadLeadsTo
PROPERTY AllTools
INVARIANT InvBig
INVARIANT ConjBig
PROPERTY SmallE
PROPERTY AllHas
ROWS
}
chain="Emergency.tla Emergency_live.tla Emergency_live_proof.tla"
mods=""; for m in $chain; do mods="$mods · $m (sha256 $(d16 "$m"))"; done
for m in $provers BinderDefectTLC; do mods="$mods · defects/$m.tla (sha256 $(d16 "defects/$m.tla"))"; done
tlcver="TLC $(java -cp "$jar" tlc2.TLC -h 2>&1 | grep -oE 'Version [0-9.]+ of [^ ]+ [^ ]+ [0-9]+' | head -1)"
echo "TOPAK — the prover's two unsound cases reproduced from spec/defects/: each listing of proof-certification.md §8 as a file, under tlapm, under the certified run, and under TLC"
echo "Runner: defects-run.sh (sha256 $(d16 "$here/defects-run.sh")) · tlapm $("$tlapm" --version) (binary sha256 $(d16 "$bin")) · $(ver zenon) · $(ver Isabelle) · LS4 for PTL · proof-cert.sh (sha256 $(d16 proof-cert.sh)) · $tlcver (jar sha256 $(d16 "$jar")) · $(java -version 2>&1 | head -1)"
echo "Modules:${mods# ·}"
echo "The modules EXTEND Emergency_live and Emergency_live_proof in spec/, so tlapm runs with -I .. and TLC runs from spec/. Section 1 is each lemma's outcome under tlapm --toolbox 0 0, with the backend that closed its last obligation, against what §8 says: a false statement that proves is the case, and HiddenDef's SuperBad and OutsideBad and HiddenBox's BigPTL must fail (§10's rule). Section 2 is proof-cert.sh on each prover module, which must certify ten and not those two. Section 3 is TLC on BinderDefectTLC at SpecL, Mut = \"none\", MaxRound = 2, one worker, -fp 0: each statement must be violated."
echo
fail=0
echo "1. Under tlapm"
for m in $provers; do
  mkdir -p "$tmp/cache-$m"
  (cd defects && "$tlapm" --cleanfp --cache-dir "$tmp/cache-$m" -I .. --toolbox 0 0 "$m.tla" > "$tmp/$m.toolbox.txt" 2>&1)
  summary=$(grep -E '^\[(INFO|ERROR)\]' "$tmp/$m.toolbox.txt" | tail -1 | sed 's/^\[[A-Z]*\]: //')
  echo "  $m · $summary"
  expect | awk -v m="$m" '$1==m{print $2, $3, $4}' > "$tmp/$m.expect"
  python3 - "defects/$m.tla" "$tmp/$m.toolbox.txt" "$tmp/$m.expect" <<'PY' || fail=1
import re, sys
src, tb, ex = sys.argv[1:4]
lemmas = []
for n, l in enumerate(open(src), 1):
    mm = re.match(r'(LEMMA|THEOREM)\s+(\w+)', l)
    if mm: lemmas.append((n, mm.group(2)))
final = {}
for blk in open(tb).read().split("@!!BEGIN"):
    if "@!!type:obligation\n" not in blk: continue
    oid = re.search(r"@!!id:(\d+)", blk); loc = re.search(r"@!!loc:(\d+):", blk)
    st = re.search(r"@!!status:(.*)", blk); pr = re.search(r"@!!prover:(.*)", blk)
    if not (oid and loc and st): continue
    final[oid.group(1)] = (int(loc.group(1)), st.group(1).strip(), pr.group(1).strip() if pr else "tlapm")
by = {name: [] for _, name in lemmas}
for line, st, pr in final.values():
    owner = None
    for n, name in lemmas:
        if n <= line: owner = name
    if owner: by[owner].append((line, st, pr))
bad = 0
for row in open(ex):
    name, want, backend = row.split()
    obs = by.get(name, [])
    sts = [s for _, s, _ in obs]
    got = "failed" if "failed" in sts else ("proved" if obs and all(s in ("proved", "trivial") for s in sts) else "unproved")
    last = max(obs, key=lambda o: (o[0], o[1] != "trivial")) if obs else None
    closer = next((p for l, s, p in sorted(obs, key=lambda o: -o[0]) if s == "proved"), None)
    lastfail = next((p for l, s, p in sorted(obs, key=lambda o: -o[0]) if s == "failed"), "")
    route = "failed" if got == "failed" else (closer or "tlapm")
    counts = "%d obligations: %d trivial, %d proved, %d failed" % (len(obs), sts.count("trivial"), sts.count("proved"), sts.count("failed"))
    ok = got == want and (backend == "-" or (got == "proved" and closer == backend))
    exp = want + ("" if backend == "-" else " by " + backend.upper())
    how = ("by " + route.upper()) if route != "failed" else ("last backend tried " + lastfail.upper())
    print("    %-14s %s %s · %s · expected %s · %s" % (name, got, how, counts, exp, "as §8 says" if ok else "DIFFERS"))
    bad |= not ok
sys.exit(1 if bad else 0)
PY
done
echo
echo "2. Under the certified run (proof-cert.sh)"
for m in $provers; do
  mkdir -p "$tmp/ev-$m"
  ./proof-cert.sh "defects/$m" "$tmp/ev-$m" > "$tmp/$m.cert.txt" 2>&1; st=$?
  n=$(sed -n 's/^Obligations: //p' "$tmp/$m.cert.txt")
  tr_=$(grep -E '^  trivial' "$tmp/$m.cert.txt" | awk '{print $NF}'); sm=$(grep -E '^  SMT' "$tmp/$m.cert.txt" | awk '{print $6}'); ze=$(grep -E '^  Zenon' "$tmp/$m.cert.txt" | awk '{print $NF}'); is=$(grep -E '^  Isabelle' "$tmp/$m.cert.txt" | awk '{print $NF}'); ls=$(grep -E '^  LS4' "$tmp/$m.cert.txt" | awk '{print $NF}')
  if [ "$st" -eq 0 ]; then got="certified"; else got="not certified"; fi
  last=$(grep -E '^(All |NOT CERTIFIED)' "$tmp/$m.cert.txt" | tail -1)
  want=$(certexp "$m"); [ "$got" = "$want" ] && v="as §8 says" || { v="DIFFERS"; fail=1; }
  echo "  $m · $got · $n obligations: $tr_ trivial, $sm SMT (ethos), $ze Zenon (Isabelle), $is Isabelle, $ls LS4 · $last · expected $want · $v"
done
echo
echo "3. Under TLC (BinderDefectTLC, SpecL, Mut = \"none\", MaxRound = 2)"
tlcrows | while read -r kind prop; do
  printf 'SPECIFICATION SpecL\n%s %s\nCONSTANTS Mut = "none"  MaxRound = 2\n' "$kind" "$prop" > "$tmp/$prop.cfg"
  java -XX:+UseParallelGC -Djava.io.tmpdir="$tmp" -jar "$jar" -workers 1 -fp 0 -config "$tmp/$prop.cfg" -metadir "$tmp/meta-$prop" defects/BinderDefectTLC.tla > "$tmp/$prop.log" 2>&1
  if grep -q -E "Invariant $prop is violated|Temporal properties were violated" "$tmp/$prop.log"; then got="violated"; v="as §8 says"; else got="NOT violated"; v="DIFFERS"; echo DIFFERS > "$tmp/tlcfail"; fi
  states=$(grep -o -E '[0-9]+ distinct states found' "$tmp/$prop.log" | tail -1)
  echo "  $prop ($kind) · $got · ${states:-no state count} · expected violated · $v"
done
[ -f "$tmp/tlcfail" ] && fail=1
echo
if [ "$fail" -eq 0 ]; then echo "Verdict: every outcome as §8 says. Both cases reproduce under tlapm $("$tlapm" --version): a false statement under a binder proves and certifies by SMT, and two terms with one name prove FALSE by SMT and by PTL."; else echo "Verdict: DIFFERS from §8 at the lines marked; the record is not reproduced by this run."; fi
exit "$fail"
