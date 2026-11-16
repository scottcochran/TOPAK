#!/usr/bin/env python3
"""Flip one mutation hypothesis in a proof module and check that the proof breaks.

    flip_test.py <Module> <M_X> [<M_Y> ...] [--threads N] [--dir D]

For each mutation named, copies the module chain and <Module>_proof.tla to a scratch directory, rewrites every
`Mut # "M_X"` in the proof module to `Mut = "M_X"`, and runs tlapm --cleanfp --strict on the copy. The prover
must report failed obligations: a proof that survives with the hypothesis flipped is proving something the
mutation does not break. Each failure is attributed to the THEOREM or LEMMA that contains it, and a flip passes
only if some failure lies in a statement, other than SafeAlways, whose text carried the flipped hypothesis.
(SafeAlways's Mut = "none" citation steps fail under any flip; a failure elsewhere can be a timeout on a loaded
machine.)

Prints one line per mutation. The copies are deleted, the prover's backends are killed with it, and nothing is
written to the tree: a mutated proof is not an artefact. Exits non-zero if any flipped proof still proves, fails
nowhere that carries the hypothesis, stops without an obligation count (ERROR), or a mutation's hypothesis does
not occur in the module. The prover must be the pinned one unless TLAPM_UNPINNED=1.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True  # leave no __pycache__ in the skill directory
import tla_common as t  # noqa: E402


def statement_spans(text):
    """(start, end, name) of every THEOREM or LEMMA in text."""
    ms = list(t.STATEMENT.finditer(text))
    return [(m.start(), ms[i + 1].start() if i + 1 < len(ms) else len(text), m.group(2)) for i, m in enumerate(ms)]


def failing_statements(text, out, proof):
    """Names of the THEOREMs and LEMMAs containing each failed obligation."""
    starts = [(text[:m.start()].count("\n") + 1, m.group(2)) for m in t.STATEMENT.finditer(text)]
    names = []
    lines = out.splitlines()
    for i, line in enumerate(lines):
        if "Could not prove or check" in line and i > 0:
            m = re.search(r'File "(?:\./)?' + re.escape(proof) + r'\.tla", line (\d+)', lines[i - 1])
            if m:
                ln = int(m.group(1))
                owner = [name for start, name in starts if start <= ln]
                name = owner[-1] if owner else f"line {ln}"
                if name not in names:
                    names.append(name)
    return names


def flip(layout, prover, module, mut, threads=None):
    """(passed?, the line to print) for one mutation."""
    proof = module + "_proof"
    tmp = tempfile.mkdtemp(prefix=f"flip_{module}_{mut}_")
    try:
        for m in t.module_chain(proof, layout.spec):
            shutil.copy(layout.module(m), tmp)
        path = os.path.join(tmp, proof + ".tla")
        text = t.read(path)
        pat = re.compile(r'Mut\s*#\s*"' + re.escape(mut) + '"')
        n = len(pat.findall(text))
        if n == 0:
            return False, f'{module} flip {mut}: no `Mut # "{mut}"` hypothesis in {proof}.tla'
        with open(path, "w", encoding="utf-8") as f:
            f.write(pat.sub(f'Mut = "{mut}"', text))
        code, out = t.run_group(t.tlapm_cmd(prover, os.path.join(tmp, "cache"), threads) + [proof + ".tla"], tmp)
        head = f"{module} flip {mut} ({n} hypothes{'is' if n == 1 else 'es'} flipped): "
        failed = re.search(r"(\d+)/(\d+) obligations? failed", out)
        proved = re.search(r"All \d+ obligations? proved", out)
        if failed:
            carriers = {name for a, b, name in statement_spans(text) if pat.search(text[a:b])}
            where = failing_statements(text, out, proof)
            relevant = [w for w in where if w != "SafeAlways" and w in carriers]
            verdict = "as required" if relevant else "fails nowhere that carries the hypothesis - not load-bearing"
            return bool(relevant), f"{head}{failed.group(0)} in {', '.join(where) or '?'} - {verdict}"
        if proved:
            return False, f"{head}{proved.group(0)} - the hypothesis is NOT load-bearing"
        return False, f"{module} flip {mut}: ERROR, no obligation count (tlapm exit {code})\n" + \
            "\n".join(out.rstrip().splitlines()[-15:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("module")
    ap.add_argument("mutations", nargs="+", metavar="M_X")
    ap.add_argument("--threads")
    ap.add_argument("--dir")
    a = ap.parse_args(argv)
    layout = t.Layout(a.dir)
    module = a.module.removesuffix(".tla").removesuffix("_proof")
    if not os.path.exists(layout.module(module + "_proof")):
        raise SystemExit(f"no {layout.module(module + '_proof')}")
    prover = t.require_prover(layout)
    bad = 0
    for mut in a.mutations:
        ok, line = flip(layout, prover, module, mut, a.threads)
        print(line, flush=True)
        bad += not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
