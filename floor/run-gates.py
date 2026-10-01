#!/usr/bin/env python3
"""Run the ADR-0030 §5 floor gates on the genesis floor with `cedar symcc`.

Gates, per action signature (principal type, action, resource type) over schema S:
  totality        never-errors, for every policy on every action it applies to
  non-vacuity     always-allows must be REFUTED (the floor refuses something)
  discrimination  always-denies must be REFUTED (the floor admits something)
  entry matters   removing any one policy changes the floor's meaning on some action it
                  applies to (equivalent must be REFUTED) - no dead entries
  routing         three candidate revisions are classified by implies in both directions
                  and routed per ToO §3.2; incomparable routes as a relaxation

Every solver call goes through `cvc5-checked` (ADR-0030 §5 A1): the query is kept, the solver runs with
proof production on, and an `unsat` reaches cedar only after the pinned checker (ethos) accepts a proof of
false from the query's own declarations and assertions. A `holds` is marked `holds✓` when every query behind
it was so checked, and `holds°` when cedar decided it without a solver query (a syntactic subset). The
queries, proofs and verdicts are copied beside the results file as `<results>.evidence/`, and their tree
digest is printed at the end: that is what joins the gate-evidence digest.

Requires: cedar built with `--features analyze`; CVC5 pointing at a cvc5 1.4.0 binary; ETHOS pointing at
the checker (default tools/ethos-8dc85c4/bin/ethos, from tools/install-ethos.sh).
Usage: run-gates.py [results-file]
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "genesis.cedarschema")
FLOOR = os.path.join(HERE, "genesis-floor.cedar")
VALUES = os.path.join(HERE, "genesis-values.json")   # policy-floor values (ADR-0039 §1)

SIGS = {
    "Read": "CorpusObject", "Draft": "WorkspaceTarget", "Invoke": "Tool", "Emit": "Topic",
    "Submit": "Artifact", "Vote": "Artifact",
    "Consult": "CorpusObject", "Actuate": "Tool", "Report": "Topic",      # ADR-0040 §1
    "Erase": "ArchiveRecord",
}

TMP = tempfile.mkdtemp(prefix="floor-gates-")
LOG = []

TOOLS = os.path.join(os.path.dirname(HERE), "tools")
WRAPPER = os.path.join(HERE, "cvc5-checked")
REAL_CVC5 = os.environ.get("CVC5", "cvc5")
ETHOS = os.environ.get("ETHOS", os.path.join(TOOLS, "ethos-8dc85c4", "bin", "ethos"))
CPC = os.path.join(TOOLS, "cpc")
CALLS = os.path.join(TMP, "calls")
STATS = {"calls": 0, "queries": 0, "checked": 0, "sat": 0, "unknown": 0}
INDEX = []   # one row per cedar call: call, cmd, action, result, queries, checked, sat, unknown


def tree_digest(root, suffix=None):
    """sha256 over 'relpath  sha256' lines of every file under root (sorted); 16 hex chars."""
    lines = []
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if suffix and not fn.endswith(suffix):
                continue
            p = os.path.join(dp, fn)
            lines.append(f"{os.path.relpath(p, root)}  {hashlib.sha256(open(p, 'rb').read()).hexdigest()}")
    return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()[:16]


def out(line=""):
    print(line)
    LOG.append(line)


def split_policies(text):
    """Return [(id, policy_text)] in file order. Each policy runs from @id to its closing '};'."""
    pols = []
    for m in re.finditer(r'@id\("([^"]+)"\)(.*?)\};', text, re.S):
        pols.append((m.group(1), m.group(0)))
    return pols


def actions_of(policy_text):
    one = re.findall(r'action\s*==\s*Topak::Action::"(\w+)"', policy_text)
    many = re.search(r'action\s+in\s*\[([^\]]*)\]', policy_text, re.S)
    if many:
        one += re.findall(r'Topak::Action::"(\w+)"', many.group(1))
    return one


def write(name, text):
    p = os.path.join(TMP, name)
    with open(p, "w") as f:
        f.write(text)
    return p


def symcc(action, cmd, *args, solver=None):
    """One cedar analysis. Returns (verdict, raw output). The verdict is `holds✓` when every solver query
    behind it came back as a checked proof, `holds°` when cedar needed no query, else `refuted`/`ERROR`."""
    STATS["calls"] += 1
    d = os.path.join(CALLS, f"{STATS['calls']:03d}")
    os.makedirs(d)
    env = dict(os.environ, CVC5=WRAPPER, TOPAK_CVC5=solver or REAL_CVC5, TOPAK_ETHOS=ETHOS,
               TOPAK_CPC=CPC, TOPAK_PROOF_DIR=d)
    argv = ["cedar", "symcc", "--schema", SCHEMA, "--principal-type", "Topak::Seat",
            "--action", f'Topak::Action::"{action}"', "--resource-type", f"Topak::{SIGS[action]}",
            "--error-format", "plain", cmd, *args]
    r = subprocess.run(argv, capture_output=True, text=True, env=env)
    s = r.stdout + r.stderr
    vs = [json.load(open(os.path.join(d, f))) for f in sorted(os.listdir(d)) if f.endswith(".json")]
    q, c = len(vs), sum(v["checked"] for v in vs)
    sat, unk = sum(v["forwarded"] == "sat" for v in vs), sum(v["forwarded"] not in ("sat", "unsat") for v in vs)
    STATS["queries"] += q; STATS["checked"] += c; STATS["sat"] += sat; STATS["unknown"] += unk
    # symcc prints "✓ …: VERIFIED" when a property holds and "✗ …: DOES NOT HOLD" when refuted.
    if "DOES NOT HOLD" in s:
        res = "refuted"
    elif ": VERIFIED" in s:
        res = "holds✓" if (c == q and q > 0) else ("holds°" if q == 0 else "holds?")
    else:
        res = "ERROR"
    INDEX.append(f"{STATS['calls']:03d}\t{cmd}\t{action}\t{res}\t{q}\t{c}\t{sat}\t{unk}")
    return res, s


def unchecked_holds():
    """A cedar `holds` that no checked proof backs: never acceptable under ADR-0030 §5 A1."""
    return sum(1 for row in INDEX if row.split("\t")[3] == "holds?")


def main():
    text = open(FLOOR).read()
    pols = split_policies(text)
    ver = subprocess.run(["cedar", "--version"], capture_output=True, text=True).stdout.strip()
    cvc = subprocess.run([REAL_CVC5, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    out("TOPAK — genesis policy floor: ADR-0030 §5 gates")
    dig = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    out(f"Floor: {os.path.basename(FLOOR)} (sha256 {dig(FLOOR)}) · {len(pols)} policies · "
        f"schema {os.path.basename(SCHEMA)} (sha256 {dig(SCHEMA)}) · "
        f"values {os.path.basename(VALUES)} (sha256 {dig(VALUES)})")
    ethos_commit = open(os.path.join(os.path.dirname(os.path.dirname(ETHOS)), "COMMIT")).read().strip()[:7] \
        if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(ETHOS)), "COMMIT")) else "?"
    out(f"{ver} · {cvc} (binary sha256 {dig(REAL_CVC5)})")
    out(f"Checker: ethos {ethos_commit} (binary sha256 {dig(ETHOS)}) · CPC signature tools/cpc from cvc5-1.4.0 "
        f"(tree sha256 {tree_digest(CPC, '.eo')}) · wrapper cvc5-checked (sha256 {dig(WRAPPER)})")
    failures = 0
    os.makedirs(CALLS)

    # ADR-0039 §1: the values file is part of the floor bundle. The gate checks its shape; the
    # K < R comparison needs the mechanism's round bound and is the mechanism's startup check.
    out("\n=== values: policy-floor numbers the lift reads (placeholders; ADR-0039 §1)")
    vals = json.load(open(VALUES))
    obs = vals.get("observer", {})
    k, t_obs = obs.get("K"), obs.get("T_obs_ms")
    ok = isinstance(k, int) and k >= 0 and isinstance(t_obs, int) and t_obs > 0
    failures += not ok
    out(f"  observer.K = {k!r}, observer.T_obs_ms = {t_obs!r}  {'pass' if ok else 'FAIL'}  (K < R is checked by the mechanism at startup)")
    lin = vals.get("lineage", {})
    unset = [x for x in ("theta_exact", "theta_near", "theta_gen", "beta", "near_tool") if lin.get(x) is None]
    out(f"  lineage: {len(unset)} of 5 values unset (ADR-0035; G4 item 30): {', '.join(unset)}")

    out("\n=== totality: never-errors, per policy per applicable action")
    for pid, ptext in pols:
        f = write(f"{pid}.cedar", ptext + "\n")
        for a in actions_of(ptext):
            res, raw = symcc(a, "never-errors", "-p", f)
            ok = res in ("holds✓", "holds°")
            failures += not ok
            out(f"  {pid:34} {a:10} {res:8} {'pass' if ok else 'FAIL'}")
            if res == "ERROR":
                out("    " + raw.strip().replace("\n", "\n    "))

    out("\n=== non-vacuity (always-allows refuted) and discrimination (always-denies refuted)")
    for a in SIGS:
        r1, raw1 = symcc(a, "always-allows", "-p", FLOOR)
        r2, raw2 = symcc(a, "always-denies", "-p", FLOOR)
        ok = r1 == "refuted" and r2 == "refuted"
        failures += not ok
        out(f"  {a:10} always-allows {r1:8} always-denies {r2:8} {'pass' if ok else 'FAIL'}")
        for r, raw in ((r1, raw1), (r2, raw2)):
            if r == "ERROR":
                out("    " + raw.strip().replace("\n", "\n    "))

    out("\n=== every entry matters: floor minus one policy is not equivalent to the floor")
    for pid, ptext in pols:
        without = write(f"without-{pid}.cedar", text.replace(ptext, ""))
        verdicts = []
        for a in actions_of(ptext):
            res, raw = symcc(a, "equivalent", "--policies1", FLOOR, "--policies2", without)
            verdicts.append((a, res))
            if res == "ERROR":
                out("    " + raw.strip().replace("\n", "\n    "))
        ok = any(r == "refuted" for _, r in verdicts)
        failures += not ok
        detail = ", ".join(f"{a}:{'differs' if r == 'refuted' else r}" for a, r in verdicts)
        out(f"  {pid:34} {'pass' if ok else 'DEAD ENTRY'}  ({detail})")

    out("\n=== routing: candidate revisions classified by implies both ways (ToO §3.2)")
    forensic = next(p for i, p in pols if i == "F-forensic-classes")
    tighten = text + '\n@id("T-no-read-by-voters")\nforbid (principal, action == Topak::Action::"Read", resource)\nwhen { context.roundRole == "voter" };\n'
    relax = text.replace(forensic, forensic.replace('"F1", ', ""))  # F1 becomes erasable
    incomparable = relax + '\n@id("T-no-erase-payload")\nforbid (principal, action == Topak::Action::"Erase", resource)\nwhen { resource.class == "payload" };\n'
    # ADR-0041 §2: the exemption of Consult from R3 rests on R4's pinning. A floor whose R4 omits the
    # Run-root conjunct still refuses Build seats and leases without Consult, so it is NOT vacuous and
    # the non-vacuity gate does not see it. It is a relaxation, and routing is the gate that says so.
    pinned = '  context.lease.alphabet.contains("Consult") &&\n  resource in context.runRoot\n'
    assert text.count(pinned) == 1, "R4-consult-pinned has changed shape; update this control"
    unpinned = text.replace(pinned, '  context.lease.alphabet.contains("Consult")\n')
    cands = [("tighten: voters may not Read", "Read", tighten, "tightening"),
             ("relax: F1 removed from the forensic floor", "Erase", relax, "relaxation"),
             ("incomparable: F1 erasable, payload not", "Erase", incomparable, "incomparable"),
             ("relax: R4 without the Run-root condition", "Consult", unpinned, "relaxation")]
    cf_unpinned = None
    for n, (name, a, ctext, expect) in enumerate(cands):
        cf = write(f"cand-{n}-{expect}.cedar", ctext)
        if ctext is unpinned:
            cf_unpinned = cf
        new_old, _ = symcc(a, "implies", "--policies1", cf, "--policies2", FLOOR)   # F' => F
        old_new, _ = symcc(a, "implies", "--policies1", FLOOR, "--policies2", cf)   # F  => F'
        h = lambda v: "holds" if v in ("holds✓", "holds°") else v
        cls = {("holds", "holds"): "equivalent", ("holds", "refuted"): "tightening",
               ("refuted", "holds"): "relaxation", ("refuted", "refuted"): "incomparable"}.get((h(new_old), h(old_new)), "ERROR")
        route = "ordinary promotion" if cls in ("equivalent", "tightening") else "anchor issuance + promotion"
        ok = cls == expect
        failures += not ok
        out(f"  {name:44} F'=>F {new_old:8} F=>F' {old_new:8} -> {cls:12} -> {route:28} {'pass' if ok else 'FAIL'}")

    out("\n=== negative controls: each gate must CATCH a defective floor")
    vac = write("ctl-vacuous.cedar", text + '\n@id("CTL-permit-all")\npermit (principal, action, resource);\n')
    # On Read, which no forbid covers. On Vote a permit-all is NOT vacuous: B7 and B8 still refuse.
    # cedar decides a permit-all without a solver query (the authorizer term folds to true): holds°.
    r, _ = symcc("Read", "always-allows", "-p", vac)
    ok = r in ("holds✓", "holds°")
    failures += not ok
    out(f"  {'vacuous floor: permit-all added (Read)':44} always-allows  {r:8} -> {'caught' if ok else 'MISSED'}")
    # Consult, like Read, is covered by no forbid: R3 and B10 do not name it (ADR-0041 §1, §2).
    r, _ = symcc("Consult", "always-allows", "-p", vac)
    ok = r in ("holds✓", "holds°")
    failures += not ok
    out(f"  {'vacuous floor: permit-all added (Consult)':44} always-allows  {r:8} -> {'caught' if ok else 'MISSED'}")
    err = write("ctl-overflow.cedar", '@id("CTL-overflow")\npermit (principal, action == Topak::Action::"Emit", resource)\nwhen { context.epoch + 1 > context.round };\n')
    r, _ = symcc("Emit", "never-errors", "-p", err)
    ok = r == "refuted"
    failures += not ok
    out(f"  {'erroring policy: Long overflow':44} never-errors   {r:8} -> {'caught' if ok else 'MISSED'}")
    dup = text + '\n@id("CTL-redundant")\nforbid (principal, action == Topak::Action::"Erase", resource)\nwhen { resource.class == "F1" };\n'
    dupf = write("ctl-redundant.cedar", dup)
    dupless = write("ctl-redundant-without.cedar", text)
    r, _ = symcc("Erase", "equivalent", "--policies1", dupf, "--policies2", dupless)
    ok = r == "holds✓"
    failures += not ok
    out(f"  {'dead entry: forbid F1 duplicated':44} equivalent     {r:8} -> {'caught' if ok else 'MISSED'}")

    out("\n=== checker controls: a solver that lies must not produce a holds (ADR-0030 §5 A1)")
    # Under the wrapper, cedar sees `unknown` (an analysis failure) unless the checker accepts a proof of
    # false from the query's own assertions. Three fake solvers stand in for cvc5 on F => F' for the
    # unpinned-R4 candidate, an implication that holds (the relaxation's second direction).
    fakes = {
        "answers unsat with no proof": '#!/bin/bash\nwhile read -r l; do [ "$l" = "(check-sat)" ] && echo unsat; done\n',
        "answers unsat with a proof of another query": f'#!/bin/bash\n'
            f'# ignore the query; prove (assert false) instead and present that proof\n'
            f'while read -r l; do [ "$l" = "(check-sat)" ] && break; done\n'
            f'printf "(set-logic ALL)(assert false)(check-sat)\\n" | {REAL_CVC5} "$@"\n',
        "answers unsat with a proof missing a step": f'#!/bin/bash\n'
            f'{REAL_CVC5} "$@" | python3 -c "import sys; L=sys.stdin.read().splitlines(); '
            f'i=max(k for k,l in enumerate(L) if l.startswith(\'(step\')); del L[i-1]; print(\'\\n\'.join(L))"\n',
    }
    for n, (name, body) in enumerate(fakes.items()):
        fp = write(f"fake-solver-{n}.sh", body)
        os.chmod(fp, 0o755)
        before = STATS["calls"]
        r, raw = symcc("Consult", "implies", "--policies1", FLOOR, "--policies2", cf_unpinned, solver=fp)
        reason = ""
        for row in INDEX[before:]:
            d = os.path.join(CALLS, row.split("\t")[0])
            for f in sorted(os.listdir(d)):
                if f.endswith(".json"):
                    reason = json.load(open(os.path.join(d, f))).get("reason") or ""
        ok = r == "ERROR" and "unknown" in raw
        failures += not ok
        out(f"  {name:44} F=>F' {r:8} -> {'caught' if ok else 'MISSED'}  ({reason[:70]})")
    bad = unchecked_holds()
    failures += bad
    out(f"  {'holds without a checked proof, whole run':44} {bad:8} -> {'none' if bad == 0 else 'FAIL'}")

    out(f"\n=== evidence: every solver query, its proof and the checker's verdict (ADR-0030 §5 A1)")
    with open(os.path.join(CALLS, "index.tsv"), "w") as f:
        f.write("call\tanalysis\taction\tresult\tqueries\tchecked\tsat\tunknown\n" + "\n".join(INDEX) + "\n")
    out(f"  {STATS['calls']} cedar calls · {STATS['queries']} solver queries · {STATS['checked']} unsat with a checked proof · "
        f"{STATS['sat']} sat (counterexample) · {STATS['unknown']} unknown/unchecked (the three controls)")
    ev_digest = tree_digest(CALLS)
    if len(sys.argv) > 1:
        ev = os.path.splitext(sys.argv[1])[0].replace("results", "evidence")
        import shutil
        if os.path.exists(ev):
            shutil.rmtree(ev)
        shutil.copytree(CALLS, ev)
        out(f"  evidence tree sha256 {ev_digest} · copied to {os.path.relpath(ev, HERE)}/")
    else:
        out(f"  evidence tree sha256 {ev_digest} · left in {CALLS}")

    out(f"\nRESULT: {'all gates pass' if failures == 0 else f'{failures} failure(s)'}")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            f.write("\n".join(LOG) + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
