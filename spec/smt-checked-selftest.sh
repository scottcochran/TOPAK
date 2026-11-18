#!/bin/bash
# Self-test of spec/smt-checked: the wrapper must forward `unsat` for an honest solver and must not for a
# solver that proves something other than the query, proves nothing, or emits a proof the checker refuses.
#   usage: smt-checked-selftest.sh <file.smt>     (any SMT file tlapm wrote; `tlapm --debug tempfiles` keeps them)
# Three more cases run on small queries written here, for `let` (which tlapm writes for CASE from ff40755):
# the wrapper must expand a let with its bindings in parallel, must refuse a proof of the query with a let's
# value changed, and must refuse a let whose value a binder in its body would capture.
# Prints one line per case and exits non-zero if any case behaves wrongly.
set -u
q=${1:?usage: smt-checked-selftest.sh <file.smt>}
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/.." && pwd)
real=${CVC5:-$root/tools/cvc5-macOS-arm64-static/bin/cvc5}
export TOPAK_ETHOS=${ETHOS:-$root/tools/ethos-8dc85c4/bin/ethos} TOPAK_CPC=${TOPAK_CPC:-$root/tools/cpc}
tmp=$(mktemp -d /tmp/smt_selftest.XXXXXX); fail=0
shim() {  # name, body: a stand-in solver; $REAL is the real one, the last argument is the query file
  printf '#!/bin/bash\nREAL=%q\nf="${@: -1}"\n%s\n' "$real" "$2" > "$tmp/$1"; chmod +x "$tmp/$1"
}
run() {   # solver, expected forwarded answer, expected reason fragment[, query file, case name]
  c=${5:-$1}
  out=$(TOPAK_CVC5=$tmp/$1 TOPAK_PROOF_DIR=$tmp/ev_$c "$here/smt-checked" "${4:-$q}")
  reason=$(python3 -c "import json,glob;print(json.load(open(glob.glob('$tmp/ev_$c/*.json')[0]))['reason'])")
  if [ "$out" = "$2" ] && echo "$reason" | grep -q "$3"; then r=ok; else r=WRONG; fail=1; fi
  echo "$r | $c | forwarded: $out | $reason" | cut -c1-200
}
shim honest '"$REAL" "$@"'
# The solver is given the query plus one more assertion, false, and proves that instead.
shim other 'sed "s/^(check-sat)/(assert false)\n(check-sat)/" "$f" > "$f.x"; "$REAL" "${@:1:$#-1}" "$f.x"'
# The solver says unsat and dumps an empty proof.
shim empty 'printf "unsat\n(\n)\n"'
# The solver dumps an honest proof with its last step removed, so nothing concludes false.
shim cut '"$REAL" "$@" | python3 -c "
import sys
l=sys.stdin.read().splitlines()
i=max(k for k,x in enumerate(l) if x.startswith(\"(step\"))
print(\"\n\".join(l[:i]+l[i+1:]))"'
run honest unsat "checker accepted"
run other unknown "not one of the query"
run empty unknown "assumes nothing"
run cut unknown "checker refused"
# let. Each query declares a sort U, constants a and b, and a predicate p.
decls='(set-logic UF)
(declare-sort U 0)
(declare-fun a () U)
(declare-fun b () U)
(declare-fun p (U) Bool)'
# Parallel bindings: the inner y is the outer x, so y is a and the assertion is p(a) and not p(a). Read in
# sequence, y would be b, and the expansion would not be the formula cvc5 proves false.
printf '%s\n(assert (! (let ((x a)) (let ((x b) (y x)) (and (p y) (not (p a))))) :named h))\n(check-sat)\n' "$decls" > "$tmp/let.smt"
# Satisfiable as written: p(a) and not p(b). The stand-in changes the let's value from a to b and proves that.
printf '%s\n(assert (let ((x a)) (p x)))\n(assert (not (p b)))\n(check-sat)\n' "$decls" > "$tmp/letother.smt"
shim letother 'sed "s/((x a))/((x b))/" "$f" > "$f.x"; "$REAL" "${@:1:$#-1}" "$f.x"'
# Satisfiable when U has two elements: every z has some other element. Substituting the outer z for x under
# the inner exists, without renaming, gives "some z differs from itself", which is false. The stand-in proves
# that formula; in the proof's notation both z's are (@var "z" U), so only the refusal keeps it out.
printf '%s\n(assert (forall ((z U)) (let ((x z)) (exists ((z U)) (not (= x z))))))\n(assert (not (= a b)))\n(check-sat)\n' "$decls" > "$tmp/letcapture.smt"
shim letcapture 'sed "s/(let ((x z)) (exists ((z U)) (not (= x z))))/(exists ((z U)) (not (= z z)))/" "$f" > "$f.x"; "$REAL" "${@:1:$#-1}" "$f.x"'
run honest unsat "checker accepted" "$tmp/let.smt" let-parallel
run letother unknown "not one of the query" "$tmp/letother.smt" let-other
run letcapture unknown "would capture" "$tmp/letcapture.smt" let-capture
rm -rf "$tmp"
exit $fail
