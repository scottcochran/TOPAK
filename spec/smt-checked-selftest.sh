#!/bin/bash
# Self-test of spec/smt-checked: the wrapper must forward `unsat` for an honest solver and must not for a
# solver that proves something other than the query, proves nothing, or emits a proof the checker refuses.
#   usage: smt-checked-selftest.sh <file.smt>     (any SMT file tlapm wrote; `tlapm --debug tempfiles` keeps them)
# Prints one line per case and exits non-zero if any case behaves wrongly.
set -u
q=${1:?usage: smt-checked-selftest.sh <file.smt>}
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/.." && pwd)
real=${CVC5:-$root/tools/cvc5-macOS-arm64-static/bin/cvc5}
export TOPAK_ETHOS=${ETHOS:-$root/tools/ethos-8dc85c4/bin/ethos} TOPAK_CPC=$root/tools/cpc
tmp=$(mktemp -d /tmp/smt_selftest.XXXXXX); fail=0
shim() {  # name, body: a stand-in solver; $REAL is the real one, the last argument is the query file
  printf '#!/bin/bash\nREAL=%q\nf="${@: -1}"\n%s\n' "$real" "$2" > "$tmp/$1"; chmod +x "$tmp/$1"
}
run() {   # name, expected forwarded answer, expected reason fragment
  out=$(TOPAK_CVC5=$tmp/$1 TOPAK_PROOF_DIR=$tmp/ev_$1 "$here/smt-checked" "$q")
  reason=$(python3 -c "import json,glob;print(json.load(open(glob.glob('$tmp/ev_$1/*.json')[0]))['reason'])")
  if [ "$out" = "$2" ] && echo "$reason" | grep -q "$3"; then r=ok; else r=WRONG; fail=1; fi
  echo "$r | $1 | forwarded: $out | $reason" | cut -c1-200
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
rm -rf "$tmp"
exit $fail
