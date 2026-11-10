#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Regenerate the whole diagram family and report what changed, as a regression test over the corpus.

The family is deterministic: a diagram whose inputs have not moved regenerates byte for byte. So after a full run
every changed file is one of three things:

  new         a diagram that did not exist before the run (needs a README row)
  expected    a change you declared with --expect (an amendment you are making on purpose)
  unexpected  a FINDING: something a diagram reads (a record, a results file, a pin) has moved, or the generator
              or the library changed under it

The run also fails on any generator WARNING (overlap) or ERROR (a module that would not build, or a build-time
read that no longer matches what the diagram expects), and lists every SVG with no row in the family README.

  uv run scripts/regen_check.py                     # check
  uv run scripts/regen_check.py --expect A5 B9      # declared amendments
  uv run scripts/regen_check.py --restore           # put back unexpected changes after reporting them

THE INTERPRETER IS PART OF THE INPUT. Python 3.12 made sum() over floats compensated (Neumaier), so the same
generator writes different coordinates from 3.12 on (x="123.86280000000001" becomes x="123.8628"). The family's
bytes are those of the interpreter it was generated with, so this script runs the generator under a pinned one,
`uv run --no-project --python <PYTHON>`, default 3.9 (the interpreter TOPAK's family was generated with). Change
the pin only together with a regeneration of the whole family, committed as such.

Exit status: 0 clean, 1 findings, 2 usage or environment error. --restore writes back the bytes each unexpected
file had before the run, so it never discards a change you had made yourself.
"""
import argparse
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

ID = re.compile(r"^([A-Z]\d+)-")


def repo_root():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return pathlib.Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("regen_check: not inside a git repository", file=sys.stderr)
        sys.exit(2)


def snapshot(family):
    return {p.name: p.read_bytes() for p in family.glob("*.svg")}


def digest(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generator", default="diagrams/gen-topak-family.py")
    ap.add_argument("--family-dir", default="diagrams/topak")
    ap.add_argument("--readme", default="diagrams/README.md")
    ap.add_argument("--expect", nargs="*", default=[], metavar="ID", help="ids you are amending on purpose")
    ap.add_argument("--restore", action="store_true", help="write back unexpected changes after reporting them")
    ap.add_argument("--python", default="3.9", help="interpreter the family is pinned to (default 3.9; see above)")
    a = ap.parse_args()
    if not shutil.which("uv"):
        print("regen_check: uv not found; it pins the generator's interpreter", file=sys.stderr)
        sys.exit(2)
    py = ["uv", "run", "--no-project", "--python", a.python, "python"]

    root = repo_root()
    family = root / a.family_dir
    gen = root / a.generator
    if not gen.exists() or not family.is_dir():
        print(f"regen_check: no generator at {gen} or no family at {family}", file=sys.stderr)
        sys.exit(2)
    expect = {e.upper() for e in a.expect}

    ver = subprocess.run(py + ["-c", "import sys; print(sys.version.split()[0])"], cwd=root, capture_output=True,
                         text=True)
    if ver.returncode != 0:
        print(f"regen_check: uv could not provide Python {a.python}:\n{ver.stderr}", file=sys.stderr)
        sys.exit(2)
    version = ver.stdout.strip()

    before = snapshot(family)
    run = subprocess.run(py + [str(gen)], cwd=root, capture_output=True, text=True)
    after = snapshot(family)

    warnings, errors, current = [], [], None
    for line in (run.stdout + run.stderr).splitlines():
        if line.endswith(".svg"):
            current = pathlib.Path(line).name
        elif line.strip().startswith("WARNING"):
            warnings.append((current, line.strip()))
        elif line.startswith("ERROR") or line.startswith("Traceback"):
            errors.append(line.strip())
    if run.returncode != 0 and not errors:
        errors.append(f"generator exited {run.returncode}")
        errors.extend(run.stderr.strip().splitlines()[-5:])

    new = sorted(n for n in after if n not in before)
    changed = sorted(n for n in after if n in before and after[n] != before[n])
    gone = sorted(n for n in before if n not in after)
    exp = [n for n in changed if ID.match(n) and ID.match(n).group(1) in expect]
    unexp = [n for n in changed if n not in exp]

    readme = (root / a.readme).read_text(encoding="utf-8") if (root / a.readme).exists() else ""
    no_row = sorted(n for n in after if n not in readme)

    print(f"regenerated {len(after)} diagrams with Python {version} (pinned {a.python})")
    print(f"  unchanged   {len(after) - len(new) - len(changed)}")
    for label, names in (("new", new), ("expected", exp), ("UNEXPECTED", unexp), ("vanished", gone)):
        for n in names:
            d = f"{digest(before[n])} -> {digest(after[n])}" if n in before and n in after else ""
            print(f"  {label:<11} {n} {d}".rstrip())
    for svg, w in warnings:
        print(f"  WARNING in {svg}: {w}")
    for e in errors:
        print(f"  ERROR {e}")
    for n in no_row:
        print(f"  no README row: {n}")
    if unexp:
        print("\nUnexpected changes are findings: a diagram's input moved (a record, a results file, a pin), or the "
              "library changed. Read the diff (git diff --word-diff on the SVG) before amending or restoring.")
        if a.restore:
            for n in unexp:
                (family / n).write_bytes(before[n])
            print(f"restored {len(unexp)} file(s) to their bytes before the run")

    bad = bool(warnings or errors or unexp or gone or no_row)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
