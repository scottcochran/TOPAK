#!/usr/bin/env python3
"""Refuse only the findings a change adds: run a check on the base commit and on the working tree, and compare.

  tools/ratchet.py --base REF --include REGEX [--context REGEX] [--name NAME] -- COMMAND [ARG ...]

COMMAND runs from the repository root, once here and once in a temporary detached worktree at REF; its exit status
is ignored, and its output (stdout and stderr) is read for findings. A line matching --include is a finding. A line
matching --context sets the context for the findings below it (a record's name, a section header), and the context
is part of the finding's key, so the same message under two records is two findings. Keys are normalised so that a
finding which only moved is the same finding: hex runs of 7 or more characters become '#', and a parenthesised
count becomes '(n)'.

Prints every standing finding, the ones this change adds, and the ones it removes. Exit 1 if it adds any, 0
otherwise; 2 on a usage error or when the base worktree cannot be made. With GITHUB_STEP_SUMMARY set, the same
report is appended to the job summary, so standing findings stay visible on every run.

Why: several checks report findings that predate CI (check-refs, the record lint, lean-sync, the corpus pins). A
check that is red on every run is ignored; a check that is green because it was switched off says nothing. The
ratchet keeps the check, shows what stands, and refuses what is new (ADR-0069 §10.2, Proposed).
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

HEX = re.compile(r"\b[0-9a-f]{7,}\b")
COUNT = re.compile(r"\(\d+\)")


def norm(s):
    return COUNT.sub("(n)", HEX.sub("#", s.rstrip()))


def findings(cwd, cmd, include, context):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    keys, ctx = {}, ""
    for ln in p.stdout.splitlines():
        if context and context.search(ln):
            ctx = norm(ln)
        if include.search(ln):
            keys.setdefault(f"{ctx} :: {norm(ln)}" if ctx else norm(ln), ln.rstrip())
    return keys


def main():
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--include", required=True)
    ap.add_argument("--context")
    ap.add_argument("--name")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        print(__doc__)
        return 2
    inc = re.compile(a.include)
    ctx = re.compile(a.context) if a.context else None
    name = a.name or " ".join(cmd)
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()

    head = findings(root, cmd, inc, ctx)
    tmp = tempfile.mkdtemp(prefix="ratchet-")
    wt = os.path.join(tmp, "base")
    r = subprocess.run(["git", "-C", root, "worktree", "add", "--detach", "--quiet", wt, a.base],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{name}: cannot check out base {a.base}: {r.stderr.strip()}")
        return 2
    try:
        base = findings(wt, cmd, inc, ctx)
    finally:
        subprocess.run(["git", "-C", root, "worktree", "remove", "--force", wt], capture_output=True)

    added = [head[k] for k in head if k not in base]
    removed = [base[k] for k in base if k not in head]
    out = [f"## {name}",
           f"base {a.base[:12]}: {len(base)} standing · this change: {len(head)} · added {len(added)} · "
           f"removed {len(removed)}"]
    if added:
        out += ["", "**Added by this change (refused):**", "```"] + added + ["```"]
    if removed:
        out += ["", "Removed by this change:", "```"] + removed + ["```"]
    if head:
        out += ["", "<details><summary>Standing findings</summary>", "", "```"] + list(head.values()) + ["```",
                                                                                                         "</details>"]
    text = "\n".join(out)
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(text + "\n\n")
    return 1 if added else 0


if __name__ == "__main__":
    sys.exit(main())
