#!/usr/bin/env python3
"""Fail a change that edits what the corpus has frozen.

    frozen-files.py BASE HEAD [--override]

Compares HEAD against its merge base with BASE and checks every changed path against the freeze rules below.
Adding a file is always allowed; the rules are about modifying, deleting and renaming what is already there.
--override reports violations as warnings and exits 0; the workflow passes it only when the custodian has
labelled the pull request `frozen-override`.

F1  checkpoints/*.md, except checkpoints/README.md: a checkpoint is one cut, never revised; errata go in the README
F2  derived/*.md, except derived/README.md: a derived document is never revised; a new one is written
F3  narrative/revisions/*: the closed archive of earlier revisions
F4  process/*, except process/README.md: the genesis cleanup's dated logs
F5  manifests/SHA256SUMS*: a manifest measures one commit; index.tsv, README.md and EXCLUDE may change
F6  every *-results-*.txt, and everything under a *-evidence-* directory: dated, generated, never edited
F7  a .tla module whose digest at BASE is cited by a decision record whose status is not Proposed: a change is a
    successor module (spec/README.md)
F8  decisions/ADR-*.md may not be deleted or renamed; its content changes only by typed History rows, which the
    custodian checks at review and this script does not
F2 and F6 allow a dated file to change on its own date (the date in its name equals HEAD's commit date), so a
results file regenerated the day it was written, or a derived document finished that day, passes; the next day
it is frozen.
F9  no .pdf or .zip (not ours to redistribute; .gitignore), and no file over 5 MB
"""
import hashlib, os, re, subprocess, sys

MAX_BYTES = 5 * 1024 * 1024
RULES = [
    ("F1", re.compile(r"^checkpoints/(?!README\.md$)[^/]+\.md$"), "a checkpoint is never revised; record an erratum in checkpoints/README.md and correct it in the next cut"),
    ("F2", re.compile(r"^derived/(?!README\.md$)[^/]+\.md$"), "a derived document is never revised; write a new dated one"),
    ("F3", re.compile(r"^narrative/revisions/"), "the narrative archive is closed"),
    ("F4", re.compile(r"^process/(?!README\.md$)"), "process logs are dated and frozen"),
    ("F5", re.compile(r"^manifests/SHA256SUMS"), "a manifest measures the commit it was cut at; cut a new one"),
    ("F6", re.compile(r"(^|/)[^/]*-results-[^/]*\.txt$|(^|/)[^/]*-evidence-[^/]*/"), "results and evidence are generated and never edited; generate a new dated file"),
]


def git(*args, binary=False):
    out = subprocess.run(["git", *args], capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode("utf-8", "replace")


def cited_digests(base):
    """16-hex prefixes cited in records at BASE whose status is not Proposed."""
    cited = set()
    for path in git("ls-tree", "--name-only", base, "decisions/").split():
        if not re.match(r"decisions/ADR-\d+\.md$", path):
            continue
        text = git("show", f"{base}:{path}")
        status = re.search(r"^\*\*Status:\*\*\s*(.*)$", text, re.M)
        if status and status.group(1).startswith("Proposed"):
            continue
        cited.update(m.lower() for m in re.findall(r"\b[0-9a-f]{16}", text))
    return cited


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    override = "--override" in sys.argv
    if len(args) != 2:
        sys.exit(__doc__)
    base = git("merge-base", args[0], args[1]).strip()
    head = args[1]
    rows = git("diff", "--name-status", "-M", base, head).splitlines()
    actions = os.environ.get("GITHUB_ACTIONS") == "true"
    found, cited = [], None
    today = git("log", "-1", "--format=%cd", "--date=format:%Y.%m.%d", head).strip()

    for row in rows:
        parts = row.split("\t")
        kind, paths = parts[0][0], parts[1:]
        old, new = paths[0], paths[-1]
        verb = {"M": "modified", "D": "deleted", "R": f"renamed to {new}", "T": "changed type"}.get(kind)

        if verb:  # an existing path changed: F1 to F8
            for rule, pattern, why in RULES:
                if pattern.search(old):
                    dated = re.search(r"20\d\d\.\d\d\.\d\d", os.path.basename(old.rstrip("/")) if rule == "F2" else old)
                    if rule in ("F2", "F6") and kind == "M" and dated and dated.group(0) == today:
                        break  # still its own day
                    found.append((rule, old, f"{old} {verb}: {why}"))
                    break
            else:
                if old.endswith(".tla"):
                    if cited is None:
                        cited = cited_digests(base)
                    digest = hashlib.sha256(git("show", f"{base}:{old}", binary=True)).hexdigest()[:16]
                    if digest in cited:
                        found.append(("F7", old, f"{old} {verb}: its digest {digest} is cited by a record that is not Proposed; write a successor module"))
                if re.match(r"decisions/ADR-\d+\.md$", old) and kind in "DR":
                    found.append(("F8", old, f"{old} {verb}: a record is never removed; supersede or tombstone it"))

        if kind in "AMRC":  # what HEAD holds: F9
            if re.search(r"\.(pdf|zip)$", new, re.I):
                found.append(("F9", new, f"{new}: PDFs and zips are not tracked (.gitignore)"))
            else:
                size = int(git("cat-file", "-s", f"{head}:{new}").strip())
                if size > MAX_BYTES:
                    found.append(("F9", new, f"{new}: {size} bytes, over the {MAX_BYTES} byte limit"))

    level = "warning" if override else "error"
    for rule, path, message in found:
        print(f"::{level} file={path},title={rule}::{message}" if actions else f"{level.upper()} {rule} {message}")
    changed = len(rows)
    if not found:
        print(f"frozen-files: {changed} changed paths since {base[:12]}, none frozen")
        return 0
    print(f"frozen-files: {len(found)} of {changed} changed paths touch frozen content" + (" (overridden by the custodian)" if override else ""))
    return 0 if override else 1


if __name__ == "__main__":
    sys.exit(main())
