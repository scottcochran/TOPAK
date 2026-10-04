#!/bin/bash
# Certified TLAPS run: checks one proof module with every SMT obligation routed through spec/smt-checked
# (cvc5 with proof production, each proof accepted by the pinned ethos checker before `unsat` is forwarded)
# and with Zenon's proofs checked by Isabelle (`tlapm -C`), then prints a results file that accounts for
# every obligation by the route that discharged it. The analogue for proofs of the checked floor gates
# (ADR-0030 §5 A1; floor/cvc5-checked); it answers ADR-0046's open obligation on the proof-checking backend.
#   usage: proof-cert.sh <Module>_proof [evidence-dir] > <Module>-proof-cert-results-<date>.txt
# The evidence (one query, one proof and one verdict per SMT obligation) lands in evidence-dir, by default a
# temp dir that is removed; the results file carries its digest. Exits non-zero if any obligation is unproved,
# if an SMT-proved obligation has no accepted proof, or if Isabelle refuses a Zenon proof.
# Needs the prover, cvc5 and ethos under tools/ (CVC5= and ETHOS= override the last two). STRETCH= multiplies
# tlapm's backend timeouts (default 1); the results file names the value used.
set -u
mod=${1:?usage: proof-cert.sh <Module>_proof [evidence-dir]}
mod=${mod%.tla}
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
tlapm="$root/tools/tlapm"
export TOPAK_CVC5=${CVC5:-$root/tools/cvc5-macOS-arm64-static/bin/cvc5}
export TOPAK_ETHOS=${ETHOS:-$root/tools/ethos-8dc85c4/bin/ethos}
export TOPAK_CPC=${TOPAK_CPC:-$root/tools/cpc}
[ -f "$here/$mod.tla" ] || { echo "no $here/$mod.tla" >&2; exit 2; }
for x in "$TOPAK_CVC5" "$TOPAK_ETHOS"; do [ -x "$x" ] || { echo "missing $x" >&2; exit 2; }; done
keep=${2:-}
ev=${keep:-$(mktemp -d /tmp/tlapm_cert_ev.XXXXXX)}
mkdir -p "$ev"; export TOPAK_PROOF_DIR=$ev
cache=$(mktemp -d /tmp/tlapm_cert.XXXXXX)
cfg=$("$tlapm" --config 2>/dev/null)
bin=$(echo "$cfg" | sed -n 's/^tlapm_executable == "\(.*\)"$/\1/p')
ver() { echo "$cfg" | sed -n "s/^$1 version == \"\(.*\)\"$/\1/p" | head -1; }
chain=""
visit() {
  local m=$1 d
  case " $chain " in *" $m "*) return ;; esac
  for d in $(grep -m1 '^EXTENDS' "$here/$m.tla" | sed 's/^EXTENDS//; s/,/ /g'); do
    [ -f "$here/$d.tla" ] && visit "$d"
  done
  chain="$chain $m"
}
visit "$mod"
digests=""
for m in $chain; do digests="$digests · $m.tla (sha256 $(shasum -a 256 "$here/$m.tla" | cut -c1-16))"; done
cpcd=$(cd "$TOPAK_CPC" && find . -type f -name '*.eo' | LC_ALL=C sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16)
echo "TOPAK — TLAPS certified proof results for ${mod%_proof}.tla: every obligation of $mod.tla, by the route that discharged it"
echo "Modules:${digests# ·}"
echo "Prover: tlapm $("$tlapm" --version) (binary sha256 $(shasum -a 256 "$bin" | cut -c1-16)) · $(ver zenon) · $(ver Isabelle) · LS4 for PTL · driver: proof-cert.sh"
echo "Checked SMT route: smt-checked (sha256 $(shasum -a 256 "$here/smt-checked" | cut -c1-16)) · $("$TOPAK_CVC5" --version | head -1) (sha256 $(shasum -a 256 "$TOPAK_CVC5" | cut -c1-16)) · ethos (sha256 $(shasum -a 256 "$TOPAK_ETHOS" | cut -c1-16)) · CPC signature (sha256 $cpcd over its .eo files)"
echo "An obligation proved by SMT counts only with a proof of false, from the query's own declarations and assertions, that ethos accepted. Z3 is not run. Backend timeouts x${STRETCH:-1}."
echo
(cd "$here" && "$tlapm" -C --cleanfp --strict --stretch "${STRETCH:-1}" --cache-dir "$cache" --toolbox 0 0 \
    --solver "$here/smt-checked \"\$file\"" "$mod.tla" > "$cache/toolbox.txt" 2>&1)
status=$?
python3 - "$cache/toolbox.txt" "$ev" "$status" <<'PY'
import collections, glob, hashlib, json, os, re, sys
tb, ev, status = open(sys.argv[1]).read(), sys.argv[2], int(sys.argv[3])
final = {}                                  # obligation id -> (status, prover), last message wins
reused = set()                              # obligations proved from a fingerprint made earlier in this run
for blk in tb.split("@!!BEGIN"):
    if "@!!type:obligation" not in blk:
        continue
    f = dict(re.findall(r"@!!(\w+):(.*)", blk))
    if f.get("status") in ("proved", "trivial", "failed", "interrupted", "omitted", "missing"):
        final[f["id"]] = (f["status"], f.get("prover", "-"))
        if f.get("already", "").strip() == "true":
            reused.add(f["id"])
ids = set(re.findall(r"@!!id:(\d+)", tb))
routes = collections.Counter()
for i in ids:
    st, pr = final.get(i, ("unproved", "-"))
    routes[(st, pr)] += 1
verdicts = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(ev, "*.json")))]
checked = [v for v in verdicts if v["checked"] and v["forwarded"] == "unsat"]
refused = [v for v in verdicts if v["answer"] == "unsat" and not v["checked"]]
calls = [l.split() for l in open(os.path.join(ev, "calls.log"))] if os.path.exists(os.path.join(ev, "calls.log")) else []
accepted_calls = sum(1 for c in calls if c[1] == "unsat" and c[2] == "1")
smt = routes[("proved", "smt")]
smt_reused = sum(1 for i in ids if final.get(i) == ("proved", "smt") and i in reused)
rejected = sorted(set(re.findall(r"Isabelle/TLA\+ rejected the proof of obligation (\d+)", tb)), key=int)
zen = routes[("proved", "zenon")]
isa = routes[("proved", "isabelle")]
ls4 = routes[("proved", "ls4")]
triv = routes[("trivial", "tlapm")]
known = {("proved", "smt"), ("proved", "zenon"), ("proved", "isabelle"), ("proved", "ls4"), ("trivial", "tlapm")}
other = {k: n for k, n in routes.items() if k not in known}
isa_ok = "Proof checking done. No errors found." in tb and not rejected
evd = hashlib.sha256("\n".join(sorted(v["query_sha256"] + " " + v.get("proof_sha256", "-") for v in checked)).encode()).hexdigest()[:16]
total = len(ids)
print(f"Obligations: {total}")
print(f"  trivial, closed by tlapm with no backend            {triv}")
print(f"  SMT, proof accepted by ethos                        {smt}   ({accepted_calls} calls forwarded on an accepted proof; {smt_reused} obligations identical to one already proved in this run; evidence digest {evd})")
print(f"  Zenon, proof checked by Isabelle                    {zen}" + ("" if zen == 0 else ("   (Isabelle: no errors)" if isa_ok else f"   (ISABELLE REJECTED {len(rejected)}: obligations {', '.join(rejected) or '?'})")))
print(f"  Isabelle                                            {isa}")
print(f"  LS4, temporal step, NOT certified                   {ls4}")
for (st, pr), n in sorted(other.items()):
    print(f"  {st} / {pr}: {n}")
if refused:
    print(f"  cvc5 answered unsat and the proof was not accepted  {len(refused)}   (not forwarded; tlapm went on to its next backend)")
    for r, n in collections.Counter(v["reason"][:110] for v in refused).most_common(5):
        print(f"      {n} x {r}")
ok = status == 0 and not other and smt - smt_reused <= accepted_calls and (zen == 0 or isa_ok)
print()
if ok:
    print(f"All {total} obligations proved. {total - ls4} of them rest on tlapm's own normalization or on a checked proof; "
          f"{ls4} rest on LS4, whose answer no checker confirms.")
else:
    why = []
    if other: why.append("; ".join(f"{n} obligation(s) {st} (last backend tried: {pr})" for (st, pr), n in sorted(other.items())))
    if zen and not isa_ok: why.append(f"Isabelle rejected {len(rejected)} of Zenon's proofs")
    if smt - smt_reused > accepted_calls: why.append(f"{smt - smt_reused} SMT-proved obligations against {accepted_calls} accepted proofs")
    if status and not why: why.append(f"tlapm exit {status}")
    print("NOT CERTIFIED: " + "; ".join(why) + ".")
sys.exit(0 if ok else 1)
PY
rc=$?
rm -rf "$cache"; [ -z "$keep" ] && rm -rf "$ev"
exit $rc
