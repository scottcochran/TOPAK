#!/usr/bin/env python3
"""Mechanical checks on TOPAK decision records.

    record_lint.py --next                  print the next free ADR and T-0045 numbers
    record_lint.py decisions/ADR-nnnn.md   check one or more records

Run from inside the repository, or pass --root. Exits 1 if a check fails; `warn` lines are for reading.

This reads form. It cannot tell whether a mark is true: that the custodian said what ⟨K1⟩ says, or that Met is met.
"""
import argparse
import hashlib
import pathlib
import re
import sys

ROW = re.compile(r"^\| ([A-Z]\d+) \| ([^|]*) \|", re.M)
DIGEST = re.compile(r"`([\w./-]+\.[a-z]+)` \(`?(?:sha256 )?([0-9a-f]{16})`?\)")
ORDER = ("Status", "Status note", "Pending", "Ratification phase", "Deployment position", "Scope", "Owner", "Supersedes",
         "Split from", "Amends", "Amends in effect", "Revises", "Narrows", "Depends on", "Depended on by", "Companions",
         "Precedent", "Relates to", "Resolves", "Resolves debts of", "Closes", "Unblocks", "Blocked on", "Blocks",
         "Creates a debt against", "Carries scope into", "Note")


def find_root(start):
    for p in [start, *start.parents]:
        if (p / "decisions").is_dir() and (p / "mechanism/corpus-pins.sha256").is_file():
            return p
    sys.exit("record_lint: not inside a TOPAK checkout")


def next_numbers(root):
    ids, t = [], [0]
    for f in (root / "decisions").glob("ADR-*.md"):
        ids.append(int(f.stem.split("-")[1]))
        t += [int(n) for n in re.findall(r"T-0045-(\d+)", f.read_text())]
    return f"ADR-{max(ids) + 1:04d}", f"T-0045-{max(t) + 1}"


def state(rowtext):
    return rowtext.rstrip().rstrip("|").rsplit(" | ", 1)[-1]


def header(text):
    head = text.split("\n---", 1)[0]
    return re.findall(r"^\*\*([A-Z][A-Za-z -]+):\*\*", head, re.M)


def condition(text):
    m = re.search(r"^#+ [^\n]*Ratification condition[^\n]*\n(.*?)(?=^#|\Z)", text, re.M | re.S)
    if not m:
        return None
    return re.findall(r"^- (.*?)(?=^- |\Z)", m.group(1), re.M | re.S)


def check(path, root, index):
    fails, warns = [], []
    text = path.read_text()
    name = path.stem
    status = next(iter(re.findall(r"^\*\*Status:\*\*.*$", text, re.M)), "")
    proposed = status.startswith("**Status:** Proposed")
    rows = dict(ROW.findall(text))
    full = {m.group(1): m.group(0) for m in re.finditer(r"^\| ([A-Z]\d+) \| .*$", text, re.M)}

    for tag in sorted(set(re.findall(r"⟨([RAE]\d+)⟩", text))):
        if tag not in rows:
            warns.append(f"⟨{tag}⟩ is used and has no History row here (fine if it quotes another record's)")
    pending = next(iter(re.findall(r"^\*\*Pending:\*\*.*$", text, re.M)), "")
    for tag, line in full.items():
        if tag[0] in "AE" and "**Pending**" in state(line):
            if tag not in re.findall(r"\b[AE]\d+\b", pending):
                fails.append(f"{tag} has a Pending row and is not on the Pending line")
            if f"Pending ⟨{tag}⟩" not in text and "quoted" not in line.lower():
                warns.append(f"{tag} has a Pending row and no 'Pending ⟨{tag}⟩' note in the text")
            if "dependent" in rows.get(tag, "") and "Takes force only with" not in line:
                warns.append(f"{tag} is dependent and its row does not say 'Takes force only with'")
    if proposed:
        if re.search(r"⟨B\d+⟩", status):
            fails.append("a Proposed record's status line carries a batch mark")
        items = condition(text)
        if items is None:
            warns.append("no Ratification condition section")
        else:
            for it in items:
                if not re.search(r"\b(Met|met)\b", it):
                    warns.append(f"condition item not marked Met or Not met: {it.strip()[:70]}")
        for rel, digest in DIGEST.findall(text):
            p = root / rel
            if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()[:16] != digest:
                warns.append(f"cites {rel} at {digest}; the file is now another digest")
        if "*(drafter's choice" not in text and re.search(r"drafter's, marked", text):
            warns.append("the provenance note says choices are marked, and none is")
    fields = [f for f in header(text) if f in ORDER]
    if [ORDER.index(f) for f in fields] != sorted(ORDER.index(f) for f in fields):
        warns.append(f"header fields out of order: {', '.join(fields)}")
    if not re.search(rf"^\| \[?{name}\]?", index, re.M):
        fails.append("no row in decisions/README.md")
    return fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("records", nargs="*")
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--root", type=pathlib.Path)
    a = ap.parse_args()
    root = a.root.resolve() if a.root else find_root(pathlib.Path.cwd())
    if a.next:
        print(*next_numbers(root))
        return 0
    if not a.records:
        ap.error("name a record, or --next")
    index = (root / "decisions/README.md").read_text()
    bad = False
    for r in a.records:
        fails, warns = check(pathlib.Path(r).resolve(), root, index)
        bad |= bool(fails)
        print(f"{pathlib.Path(r).stem}: {'FAILED' if fails else 'ok'}")
        for f in fails:
            print(f"  FAIL {f}")
        for w in warns:
            print(f"  warn {w}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
