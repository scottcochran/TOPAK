#!/usr/bin/env python3
"""Mechanical checks on a TOPAK ratification batch.

    batch_lint.py --next         print the next free batch number
    batch_lint.py <nn>           check batch <nn> as applied to the working tree

Run from anywhere inside the repository, or pass --root. Exits 1 if a check fails.

This reads form only. It can tell that a row exists and a pin matches. It cannot tell that the custodian decided
what a row says the custodian decided.
"""
import argparse
import hashlib
import pathlib
import re
import sys

A25 = "Not reviewed by a reader other than the drafter"
PINS = "mechanism/corpus-pins.sha256"
ROUTES_SOURCE = "decisions/ADR-0045.md"


def find_root(start):
    for p in [start, *start.parents]:
        if (p / "decisions").is_dir() and (p / PINS).is_file():
            return p
    sys.exit("batch_lint: not inside a TOPAK checkout (no decisions/ with mechanism/corpus-pins.sha256)")


def records(root):
    return sorted((root / "decisions").glob("ADR-*.md"))


def status_line(text):
    m = re.search(r"^\*\*Status:\*\*.*$", text, re.M)
    return m.group(0) if m else ""


def rows(text, tag_re):
    return re.findall(rf"^\| ({tag_re}) \| (.*)$", text, re.M)


def next_batch(root):
    seen = {0}
    for f in records(root):
        text = f.read_text()
        seen |= {int(n) for n in re.findall(r"⟨B(\d+)⟩", text)}
        seen |= {int(n) for n in re.findall(r"^\| B(\d+) \|", text, re.M)}
    return max(seen) + 1


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_cell(row):
    return row.rstrip().rstrip("|").rsplit(" | ", 1)[-1]


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def fail(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def check_record(f, n, text, r, index):
    name = f.stem
    mark, status = f"⟨B{n}⟩", status_line(text)
    b_rows = [c for t, c in rows(text, rf"B{n}")]
    if not (mark in status or b_rows):
        return False
    if b_rows and mark not in status:
        r.fail(f"{name}: has a B{n} History row but no {mark} on its status line")
    if mark in status and not b_rows:
        r.warn(f"{name}: {mark} on the status line and no B{n} row (Batches 26 and 37 did this for an erratum; Batch 38 wrote the row)")
    for c in b_rows:
        kind = c.split(" | ", 1)[0].strip()
        if kind == "Ratification" and A25 not in c:
            r.fail(f"{name}: lead B{n} row lacks the sentence '{A25}'")
        m = re.match(r"[^|]*\| \*\*((?:[AE]\d+)(?:, [AE]\d+)*(?: and [AE]\d+)?) ratified", c)
        if m:
            for tag in re.findall(r"[AE]\d+", m.group(1)):
                tr = [x for t, x in rows(text, re.escape(tag))]
                if not tr:
                    r.fail(f"{name}: B{n} ratifies {tag}, which has no History row")
                elif not any(mark in state_cell(x) for x in tr):
                    r.fail(f"{name}: B{n} ratifies {tag}, whose row's state does not carry {mark}")
    for tag, c in rows(text, r"[AE]\d+"):
        state = state_cell(c)
        if mark in state and "**Pending**" in state:
            r.fail(f"{name}: {tag} is marked {mark} and still **Pending**")
        if mark in state and re.search(rf"Pending ⟨{tag}⟩", text):
            r.fail(f"{name}: {tag} is applied in B{n} and its 'Pending ⟨{tag}⟩' note is still in the text")
    marks = re.findall(r"⟨B(\d+)⟩", status)
    if marks and marks[0] == str(n) and status.startswith("**Status:** Accepted"):
        if "DRAFT for the custodian" in text.split("\n", 1)[0]:
            r.fail(f"{name}: ratified in B{n}, header still says DRAFT for the custodian")
        row = re.search(rf"^\| \[{name}\].*$", index, re.M)
        if row and "Proposed" in row.group(0).split(" | ")[2]:
            r.fail(f"{name}: ratified in B{n}, decisions/README.md index row still says Proposed")
    return True


def check_pins(root, r):
    for line in (root / PINS).read_text().splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(None, 1)
        p = root / rel
        if not p.is_file():
            r.fail(f"pin: {rel} does not exist")
        elif sha(p) != digest:
            r.fail(f"pin: {rel} does not match {PINS}")


def check_routes(root, n, members, r):
    files = sorted((root / "spec").glob("premise-routes-results-*.txt"))
    if not files:
        return
    newest = files[-1]
    moved = ROUTES_SOURCE.split("/")[1].removesuffix(".md") in members
    report = r.fail if moved else r.warn
    text = newest.read_text()
    sources = re.findall(r"(\S+) \(sha256 ([0-9a-f]{16})\)", text.split("\n", 2)[1])
    for rel, digest in sources:
        p = root / rel
        if not p.is_file():
            report(f"routes: {newest.name} names {rel}, which does not exist")
        elif sha(p)[:16] != digest:
            report(f"routes: {newest.name} was generated against another {rel}")
    if moved:
        cited = re.findall(r"premise-routes-results-[\w.]+\.txt", " ".join(
            c for _, c in rows((root / ROUTES_SOURCE).read_text(), rf"B{n}")))
        if cited and newest.name not in cited:
            r.fail(f"routes: ADR-0045's B{n} row cites {cited[0]}; the newest results file is {newest.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("batch", nargs="?", type=int)
    ap.add_argument("--next", action="store_true", help="print the next free batch number")
    ap.add_argument("--root", type=pathlib.Path, help="repository root")
    args = ap.parse_args()
    root = args.root.resolve() if args.root else find_root(pathlib.Path.cwd())
    if args.next:
        print(next_batch(root))
        return 0
    if args.batch is None:
        ap.error("give a batch number, or --next")
    r = Report()
    index = (root / "decisions/README.md").read_text()
    members = [f.stem for f in records(root) if check_record(f, args.batch, f.read_text(), r, index)]
    if not members:
        r.fail(f"no record carries batch {args.batch}")
    check_pins(root, r)
    check_routes(root, args.batch, members, r)
    print(f"Batch {args.batch}: {len(members)} record(s): {', '.join(members)}")
    for w in r.warnings:
        print(f"  warning: {w}")
    for e in r.errors:
        print(f"  FAIL: {e}")
    print("Result: " + ("FAILED" if r.errors else "ok"))
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
