#!/usr/bin/env python3
"""Mechanical checks on a Lean development that stands beside a source.

    lean_lint.py <dir-or-file> [...]                        scan for constructs that widen what is trusted
    lean_lint.py <file.lean> --module M.tla [--proof P.tla] also check coverage of a TLA+ module and its proof

Exits 1 if a forbidden construct is found. Reports `native_decide` and classical reasoning, which are allowed when
explained, as notes, and coverage gaps as `check` lines to look at: an encoding may fairly inline an operator or drop a
type invariant. This reads text. It cannot tell that the Lean means what the source means, and `#print axioms` is the
authority on what a theorem uses.
"""
import argparse
import pathlib
import re
import sys

FORBIDDEN = {
    r"\bsorry\b": "sorry",
    r"^\s*(private\s+|protected\s+)?axiom\b": "axiom declaration",
    r"\bdebug\.skipKernelTC\b": "kernel check switched off",
    r"\bunsafe\s+(def|theorem|instance)\b": "unsafe declaration",
    r"@\[\s*(implemented_by|extern)\b": "implementation replaced outside the kernel",
    r"\baddDecl\b": "declaration added by metaprogram",
}
NOTES = {r"\bnative_decide\b": "native_decide (trusts the compiler)", r"\b[Cc]lassical\b": "classical reasoning (choice)"}
# Stay with the model checker or carry no content: reachability witnesses, the tuple of variables.
NOT_ENCODED = re.compile(r"^(.*Never[A-Z].*|vars)$")
TLA_DEF = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(\([^)]*\))?\s*==", re.M)
TLA_THM = re.compile(r"^(?:THEOREM|LEMMA)\s+([A-Za-z_][A-Za-z0-9_]*)\s*==", re.M)


def strip_comments(text):
    """Lean's block comments nest. Line comments and strings are enough for what this looks for."""
    out, depth, i = [], 0, 0
    while i < len(text):
        two = text[i:i + 2]
        if two == "/-":
            depth, i = depth + 1, i + 2
        elif two == "-/" and depth:
            depth, i = depth - 1, i + 2
        elif depth:
            out.append("\n" if text[i] == "\n" else " ")
            i += 1
        else:
            out.append(text[i])
            i += 1
    return re.sub(r"--.*$", "", "".join(out), flags=re.M)


def files(paths):
    for p in map(pathlib.Path, paths):
        if p.is_dir():
            yield from sorted(f for f in p.rglob("*.lean") if ".lake" not in f.parts)
        else:
            yield p


def scan(paths):
    errors, notes, n = [], {}, 0
    for f in files(paths):
        n += 1
        code = strip_comments(f.read_text())
        for i, line in enumerate(code.splitlines(), 1):
            for pat, what in FORBIDDEN.items():
                if re.search(pat, line):
                    errors.append(f"{f}:{i}: {what}")
            for pat, what in NOTES.items():
                if re.search(pat, line):
                    notes.setdefault(what, set()).add(str(f))
    return errors, notes, n


def coverage(lean, module, proof):
    text = pathlib.Path(lean).read_text()
    missing, axioms = [], []
    src = pathlib.Path(module).read_text()
    # Only top-level definitions are named at column zero, and the module's own comments are not definitions.
    src = re.sub(r"\(\*.*?\*\)", "", src, flags=re.S)
    for name, _ in TLA_DEF.findall(src):
        if not NOT_ENCODED.match(name) and not re.search(rf"\b{re.escape(name)}\b", text):
            missing.append(f"operator {name} of {module} appears nowhere in {lean}, not even in a comment")
    if proof:
        ptext = pathlib.Path(proof).read_text()
        for name in re.findall(r"^THEOREM\s+([A-Za-z_][A-Za-z0-9_]*)\s*==", ptext, re.M):
            if not re.search(rf"\b{re.escape(name)}\b", text):
                missing.append(f"THEOREM {name} of {proof} has no counterpart in {lean}")
    code = strip_comments(text)
    for name in re.findall(r"^theorem\s+([A-Za-z0-9_]+Always)\b", code, re.M):
        if not re.search(rf"#print axioms\s+\S*{re.escape(name)}\b", code):
            axioms.append(f"theorem {name} has no #print axioms")
    return missing + axioms


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--module", help="the TLA+ module the single .lean file encodes")
    ap.add_argument("--proof", help="its TLAPS proof module")
    a = ap.parse_args()
    errors, notes, n = scan(a.paths)
    for e in errors:
        print(f"FAIL {e}")
    if a.module:
        if len(a.paths) != 1 or not a.paths[0].endswith(".lean"):
            ap.error("--module needs exactly one .lean file")
        for m in coverage(a.paths[0], a.module, a.proof):
            print(f"check {m}")
    for what, fs in sorted(notes.items()):
        print(f"note {what}: {len(fs)} file(s): {', '.join(sorted(pathlib.Path(x).name for x in fs))}")
    print(f"{n} file(s): {'FAILED' if errors else 'ok'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
