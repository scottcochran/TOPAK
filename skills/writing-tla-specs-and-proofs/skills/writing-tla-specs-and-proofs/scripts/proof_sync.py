#!/usr/bin/env python3
"""Report whether every results file is in step with the tree.

    proof_sync.py [--run [--threads N]] [--dir D] [--results-dir R]

For every base module (a .tla in the spec directory that is not a proof module or a trace TLC left behind):

  - TLC: the newest <M>-results-*.txt; each digest on its Modules: line is compared with the tree and the
    Checker: digest with the pin. Prints IN SYNC, STALE: <what moved>, or MISSING.
  - Proof: if <M>_proof.tla exists, the newest <M>-proof-results-*.txt, compared the same way (its Modules:
    line names the proof module too) and its Prover: digest with tools/TLAPS-PIN. If there is no proof module,
    the reason recorded for it in PROOF-GAPS.txt in the spec directory (one line, `<Module>: <reason>`) is
    printed; a module with neither a proof nor a reason is a failure. A module that needs no results of its own
    (shared definitions with no Spec) says so there too, as `<Module>: no results: <reason>`.

Exit non-zero on any STALE, MISSING or unpinned row, or an unexplained gap. With --run, each stale proof is
re-checked with tlapm --cleanfp --strict, so the output says whether the drift broke the proof or only the
digest; no results file is written (proof_results.py does that, deliberately).
"""
import argparse
import glob
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True  # leave no __pycache__ in the skill directory
import tla_common as t  # noqa: E402


def field(path, key):
    for line in t.read(path).splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def moved_modules(layout, path):
    pairs = re.findall(r"(\S+\.tla) ([0-9a-f]{64})", field(path, "Modules"))
    if not pairs:
        return ["no Modules: line"]
    moved = []
    for name, digest in pairs:
        p = os.path.join(layout.root, name)
        if not os.path.exists(p):
            moved.append(f"{name} (gone)")
        elif t.sha256(p) != digest:
            moved.append(name)
    return moved


def gaps(layout):
    path = os.path.join(layout.spec, "PROOF-GAPS.txt")
    out = {}
    if os.path.exists(path):
        for line in t.read(path).splitlines():
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def status(layout, results, pin_digest, tool_field, what):
    moved = moved_modules(layout, results)
    s = "IN SYNC" if not moved else "STALE: " + ", ".join(moved)
    unpinned = not pin_digest or pin_digest not in field(results, tool_field)
    if unpinned:
        s += f"; {what} is not the pin" if pin_digest else f"; no pin for the {what}"
    return s, moved, bool(moved or unpinned)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--threads")
    ap.add_argument("--dir")
    ap.add_argument("--results-dir")
    a = ap.parse_args(argv)
    layout = t.Layout(a.dir, a.results_dir)
    tlc_pin = t.find_checker(layout).want
    prover = t.find_prover(layout)
    reasons = gaps(layout)
    bases = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(layout.spec, "*.tla"))
                   if not p.endswith("_proof.tla") and "_TTrace_" not in p)
    if not bases:
        print(f"no modules in {layout.spec}")
        return 1
    w = max(len(m) for m in bases)
    bad = 0
    for m in bases:
        reason = reasons.get(m, "")
        r = t.newest(layout, f"{m}-results-*.txt")
        if r:
            s, _, wrong = status(layout, r, tlc_pin, "Checker", "checker")
            bad += wrong
            print(f"{m:{w}} TLC    {s}  ({os.path.basename(r)})")
        elif reason.startswith("no results:"):
            print(f"{m:{w}} TLC    none: {reason[len('no results:'):].strip()}")
        else:
            print(f"{m:{w}} TLC    MISSING: no {m}-results-*.txt in {layout.rel(layout.results)}")
            bad += 1
        if not os.path.exists(layout.module(m + "_proof")):
            if reason:
                print(f"{m:{w}} PROOF  none: {reason}")
            else:
                print(f"{m:{w}} PROOF  none and no reason in PROOF-GAPS.txt")
                bad += 1
            continue
        r = t.newest(layout, f"{m}-proof-results-*.txt")
        if not r:
            print(f"{m:{w}} PROOF  MISSING: no {m}-proof-results-*.txt in {layout.rel(layout.results)}")
            bad += 1
            continue
        s, moved, wrong = status(layout, r, prover.want, "Prover", "prover")
        bad += wrong
        print(f"{m:{w}} PROOF  {s}  ({os.path.basename(r)}; {field(r, 'Result')})")
        if moved and a.run:
            p = t.require_prover(layout)
            cache = tempfile.mkdtemp(prefix="tlapm_sync_")
            try:
                code, out = t.run_group(t.tlapm_cmd(p, cache, a.threads) + [f"{m}_proof.tla"], layout.spec)
            finally:
                shutil.rmtree(cache, ignore_errors=True)
            mm = re.search(r"All \d+ obligations? proved|\d+/\d+ obligations? failed", out)
            print(f"{'':{w}}        re-run: {mm.group(0) if mm else 'no count'} (exit {code})")
    print("sync: " + ("OK" if not bad else f"{bad} problem(s)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
