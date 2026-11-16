#!/usr/bin/env python3
"""The checks every deployment owes before a simulation means anything. From a simulation's directory:

    uv run --with pyyaml <skill>/scripts/check_deployment.py [--mutate] [SIM_DIR]

  1  every bundle's own tests pass under `opa test`
  2  no rule formats with %q or %v, which trap under opa-wasm and lose the refusal's reason
  3  every bundle has data.topak.bundle.allow and compiles to Wasm with its entrypoints
  4  every pin the scenario declares matches the file it pins
  5  every chain names only declared bundles
  6  every workflow parses in the reference and its load check is read out
  --mutate  every refusal rule is needed by some test. A rule no test needs is a failure. A condition
            dropped or a boundary moved with no test noticing is printed as advice, to decide one by one.
            Files a bundle copies unchanged from policies/ go in its "copied" list and are skipped.

It says nothing about whether a value is right. A use case's own cross-file facts belong in the
configuration's tools/check_consistency.py.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from topak_sim.core import Core  # noqa: E402
from topak_sim.policy import ALLOW, OPA, VIOL, Engine, bundle_rev  # noqa: E402
from topak_sim.trace import canonical  # noqa: E402
from topak_sim.workflow import OVERLAY_NODE_FIELDS, OVERLAY_TOP_FIELDS  # noqa: E402

fails = []


def report(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


RULE = re.compile(r"^violations contains .*\{\s*$")


def rule_blocks(lines):
    """(start, end) of each multi-line refusal rule, opa-fmt style: closed by a `}` in column 0."""
    i = 0
    while i < len(lines):
        if RULE.match(lines[i]):
            j = i + 1
            while j < len(lines) and lines[j].rstrip() != "}":
                j += 1
            yield i, j
            i = j
        i += 1


FLIPS = [(" <= ", " < "), (" >= ", " > "), (" < ", " <= "), (" > ", " >= "), (" == ", " != "), (" != ", " == ")]


def is_guard(line):
    """A kind-of-request guard or a bare predicate: dropping it rarely changes a test, and tells you nothing."""
    t = line.strip()
    return t.startswith("input.action ==") or t.startswith("input.action in ") or re.fullmatch(r"[a-z_][a-z0-9_.]*", t) is not None


def mutants(lines):
    for s, e in rule_blocks(lines):
        yield "delete the rule", s, lines[:s] + lines[e + 1:]
        body = [k for k in range(s + 1, e) if lines[k].strip() and not lines[k].strip().startswith("#")]
        if len(body) > 1:
            for k in body:
                if not is_guard(lines[k]):
                    yield "drop a condition", k, lines[:k] + lines[k + 1:]
        for k in body:
            for a, b in FLIPS:
                if a in lines[k]:
                    yield f"flip{a.rstrip()} to{b.rstrip()}", k, lines[:k] + [lines[k].replace(a, b, 1)] + lines[k + 1:]
                    break


def mutate(cfg, name, rel, copied=()):
    d = cfg / rel
    survived, advice, invalid, total = [], [], 0, 0
    with tempfile.TemporaryDirectory() as t:
        work = pathlib.Path(t) / "b"
        shutil.copytree(d, work)
        for p in sorted(d.rglob("*.rego")):
            if p.name.endswith("_test.rego") or p.name in copied:
                continue
            rp = p.relative_to(d)
            text = p.read_text().split("\n")
            for what, line, new in mutants(text):
                (work / rp).write_text("\n".join(new))
                r = subprocess.run([OPA, "test", str(work)], capture_output=True, text=True)
                out = r.stdout + r.stderr
                if "rego_" in out or "1 error occurred" in out:
                    invalid += 1
                    continue
                total += 1
                if r.returncode == 0:
                    (survived if what == "delete the rule" else advice).append(f"{rp}:{line + 1} {what}: {text[line].strip()}")
            (work / rp).write_text("\n".join(text))
    report(not survived, f"mutation of {name}: {total} mutants, {len(survived)} rules no test needs, {len(advice)} advisory survivors, {invalid} did not compile")
    for s in survived:
        print("        rule no test needs:", s)
    for s in advice:
        print("        advice:", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sim", nargs="?", default=".")
    ap.add_argument("--mutate", action="store_true")
    a = ap.parse_args()
    sim = pathlib.Path(a.sim).resolve()
    sc = json.loads((sim / "scenario.json").read_text())
    dep = sc["deployment"]
    cfg = (sim / dep["config"]).resolve()
    bad_fmt = re.compile(r'sprintf\("[^"]*%[qv]')
    for name, b in dep["bundles"].items():
        d = cfg / b["dir"]
        r = subprocess.run([OPA, "test", str(d)], capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or [r.stderr.strip()])[-1]
        report(r.returncode == 0 and "PASS" in r.stdout, f"opa test {name}: {tail}")
        hits = [f"{p.name}:{i + 1}" for p in d.rglob("*.rego") if not p.name.endswith("_test.rego") for i, l in enumerate(p.read_text().split("\n")) if bad_fmt.search(l)]
        report(not hits, f"{name} has no %q or %v in sprintf" + (f": {hits}" if hits else ""))
        out = pathlib.Path(tempfile.mkdtemp()) / "b.tar.gz"
        cmd = [OPA, "build", "-t", "wasm", "--ignore", "*_test.rego", "-o", str(out), str(d)]
        for e in [ALLOW, VIOL] + b.get("extra_violations", []):
            cmd += ["-e", e]
        r = subprocess.run(cmd, capture_output=True, text=True)
        report(r.returncode == 0, f"{name} compiles to Wasm" + (f": {r.stderr.strip()[:300]}" if r.returncode else ""))
    checker = Core.__new__(Core)
    checker.dep, checker.cfg = dep, cfg
    checker.revs = {n: bundle_rev(cfg / b["dir"]) for n, b in dep["bundles"].items()}
    try:
        checker.verify_pins()
        report(True, f"{len(dep.get('pins', []))} pins match")
    except SystemExit as e:
        report(False, f"pins: {e}")
    for plane, chain in dep["chains"].items():
        unknown = [b for b in chain if b not in dep["bundles"]]
        report(not unknown and bool(chain), f"chain {plane}: {chain}")
    if dep.get("workflows"):
        eng = Engine(cfg, dep["bundles"])
        for rel in dep["workflows"]:
            d = checker.load_cfg(rel)
            stripped = {k: v for k, v in d.items() if k not in OVERLAY_TOP_FIELDS}
            stripped["nodes"] = {n: {k: v for k, v in nd.items() if k not in OVERLAY_NODE_FIELDS} for n, nd in d["nodes"].items()}
            seats = {nd["seat"]: {"kind": "thinker", "domain": "run", "rung": 0} for nd in d["nodes"].values()}
            if d.get("orchestrator"):
                seats[d["orchestrator"]["seat"]] = {"kind": "orchestrator", "domain": "run", "rung": 0}
            r = eng.request({"op": "wf_load", "run": rel, "text": canonical(stripped), "seats": seats})
            if "err" in r:
                report(False, f"{rel}: the reference's parser refuses it: {r['err']}")
                continue
            hard = [c for c in r["check"] if "above rung 0" not in c]
            soft = len(r["check"]) - len(hard)
            report(not hard, f"{rel} parses; {soft} seatings above rung 0 (the reference's provisional limit), {len(hard)} other load errors")
            for h in hard:
                print("        ", h)
        eng.close()
    if a.mutate:
        for name, b in dep["bundles"].items():
            mutate(cfg, name, b["dir"], b.get("copied", ()))
    print(f"\n{'all checks passed' if not fails else str(len(fails)) + ' failed'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
