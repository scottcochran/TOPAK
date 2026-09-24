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

Requires: cedar built with `--features analyze`, and CVC5 pointing at a cvc5 binary.
Usage: run-gates.py [results-file]
"""
import hashlib
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "genesis.cedarschema")
FLOOR = os.path.join(HERE, "genesis-floor.cedar")

SIGS = {
    "Read": "CorpusObject", "Draft": "WorkspaceTarget", "Invoke": "Tool", "Emit": "Topic",
    "Submit": "Artifact", "Vote": "Artifact", "RunInvoke": "Tool", "RunEmit": "Topic",
    "Erase": "ArchiveRecord",
}

TMP = tempfile.mkdtemp(prefix="floor-gates-")
LOG = []


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


def symcc(action, cmd, *args):
    argv = ["cedar", "symcc", "--schema", SCHEMA, "--principal-type", "Topak::Seat",
            "--action", f'Topak::Action::"{action}"', "--resource-type", f"Topak::{SIGS[action]}",
            "--error-format", "plain", cmd, *args]
    r = subprocess.run(argv, capture_output=True, text=True)
    s = r.stdout + r.stderr
    # symcc prints "✓ …: VERIFIED" when a property holds and "✗ …: DOES NOT HOLD" when refuted.
    if "DOES NOT HOLD" in s:
        return "refuted", s
    if ": VERIFIED" in s:
        return "holds", s
    return "ERROR", s


def main():
    text = open(FLOOR).read()
    pols = split_policies(text)
    ver = subprocess.run(["cedar", "--version"], capture_output=True, text=True).stdout.strip()
    cvc = subprocess.run([os.environ.get("CVC5", "cvc5"), "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    out("TOPAK — genesis policy floor: ADR-0030 §5 gates")
    dig = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    out(f"Floor: {os.path.basename(FLOOR)} (sha256 {dig(FLOOR)}) · {len(pols)} policies · "
        f"schema {os.path.basename(SCHEMA)} (sha256 {dig(SCHEMA)})")
    out(f"{ver} · {cvc}")
    failures = 0

    out("\n=== totality: never-errors, per policy per applicable action")
    for pid, ptext in pols:
        f = write(f"{pid}.cedar", ptext + "\n")
        for a in actions_of(ptext):
            res, raw = symcc(a, "never-errors", "-p", f)
            ok = res == "holds"
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
    cands = [("tighten: voters may not Read", "Read", tighten, "tightening"),
             ("relax: F1 removed from the forensic floor", "Erase", relax, "relaxation"),
             ("incomparable: F1 erasable, payload not", "Erase", incomparable, "incomparable")]
    for name, a, ctext, expect in cands:
        cf = write(f"cand-{expect}.cedar", ctext)
        new_old, _ = symcc(a, "implies", "--policies1", cf, "--policies2", FLOOR)   # F' => F
        old_new, _ = symcc(a, "implies", "--policies1", FLOOR, "--policies2", cf)   # F  => F'
        cls = {("holds", "holds"): "equivalent", ("holds", "refuted"): "tightening",
               ("refuted", "holds"): "relaxation", ("refuted", "refuted"): "incomparable"}.get((new_old, old_new), "ERROR")
        route = "ordinary promotion" if cls in ("equivalent", "tightening") else "anchor issuance + promotion"
        ok = cls == expect
        failures += not ok
        out(f"  {name:44} F'=>F {new_old:8} F=>F' {old_new:8} -> {cls:12} -> {route:28} {'pass' if ok else 'FAIL'}")

    out("\n=== negative controls: each gate must CATCH a defective floor")
    vac = write("ctl-vacuous.cedar", text + '\n@id("CTL-permit-all")\npermit (principal, action, resource);\n')
    # On Read, which no forbid covers. On Vote a permit-all is NOT vacuous: B7 and B8 still refuse.
    r, _ = symcc("Read", "always-allows", "-p", vac)
    ok = r == "holds"
    failures += not ok
    out(f"  {'vacuous floor: permit-all added (Read)':44} always-allows  {r:8} -> {'caught' if ok else 'MISSED'}")
    err = write("ctl-overflow.cedar", '@id("CTL-overflow")\npermit (principal, action == Topak::Action::"Emit", resource)\nwhen { context.epoch + 1 > context.round };\n')
    r, _ = symcc("Emit", "never-errors", "-p", err)
    ok = r == "refuted"
    failures += not ok
    out(f"  {'erroring policy: Long overflow':44} never-errors   {r:8} -> {'caught' if ok else 'MISSED'}")
    dup = text + '\n@id("CTL-redundant")\nforbid (principal, action == Topak::Action::"Erase", resource)\nwhen { resource.class == "F1" };\n'
    dupf = write("ctl-redundant.cedar", dup)
    dupless = write("ctl-redundant-without.cedar", text)
    r, _ = symcc("Erase", "equivalent", "--policies1", dupf, "--policies2", dupless)
    ok = r == "holds"
    failures += not ok
    out(f"  {'dead entry: forbid F1 duplicated':44} equivalent     {r:8} -> {'caught' if ok else 'MISSED'}")

    out(f"\nRESULT: {'all gates pass' if failures == 0 else f'{failures} failure(s)'}")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            f.write("\n".join(LOG) + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
