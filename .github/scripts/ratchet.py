#!/usr/bin/env python3
"""Run a corpus checker on BASE and on the working tree, and fail only on failures BASE did not already have.

    ratchet.py BASE check-refs|proof-sync|lean-sync

The checkers exit 1 on main today for debts the state of record already carries (G11 §7): citations left stale in
frozen files, Workflow.tla and Mesh.tla without a proof or a reason (item 101), the Lean replays behind the
reference (A16, A17). A pull request may carry those debts; it may not add one. Each checker's output is reduced to
failure keys, the keys present at BASE are reported as carried, and any new key fails the check. When a debt is
paid on main it leaves BASE's keys, and from then on its return fails too.
"""
import os, re, subprocess, sys, tempfile

CHECKERS = {
    "check-refs": ["python3", "-I", "tools/check-refs.py"],
    "proof-sync": ["bash", "spec/proof-sync.sh"],
    "lean-sync": ["bash", "tools/lean-sync.sh"],
}
MARKERS = ("MISSING RESULTS", "NO REASON RECORDED", "NOT THE PINNED", "OFF THE PIN", "NOT STATED IN LEAN")


def keys(name, text):
    found = set()
    if name == "check-refs":
        section = False
        for line in text.splitlines():
            if line.startswith("MISSING paths") or line.startswith("date tokens"):
                section = True
            elif not line.startswith("  "):
                section = False
            elif section:
                found.add(line.strip())
        return found
    for line in text.splitlines():
        cols = [c.strip() for c in line.split(" | ")]
        if len(cols) >= 4 and cols[-1] != "state":
            state = cols[-1].split(":")[0]
            if state != "IN SYNC":
                found.add(f"{cols[0]}: {state}")  # the row and its state, not the digests, which move
        elif any(m in line for m in MARKERS):
            found.add(re.sub(r"\b[0-9a-f]{16,}\b", "<digest>", line.strip()))
    return found


def run(name, root):
    out = subprocess.run(CHECKERS[name], cwd=root, capture_output=True, text=True)
    return out.returncode, out.stdout + out.stderr


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in CHECKERS:
        sys.exit(__doc__)
    base, name = sys.argv[1], sys.argv[2]
    actions = os.environ.get("GITHUB_ACTIONS") == "true"
    code, head_out = run(name, ".")
    print(head_out)
    if code == 0:
        print(f"ratchet {name}: passes outright")
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        tree = os.path.join(tmp, "base")
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", tree, base], check=True)
        try:
            _, base_out = run(name, tree)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", tree], check=True)
    new, carried = keys(name, head_out) - keys(name, base_out), keys(name, head_out) & keys(name, base_out)
    for k in sorted(carried):
        print(f"::notice title={name} carried from base::{k}" if actions else f"carried  {k}")
    for k in sorted(new):
        print(f"::error title={name} new failure::{k}" if actions else f"NEW      {k}")
    if not new and not carried:
        print(f"ratchet {name}: exit {code} with no failure this script recognizes; read the output above")
        return 1
    print(f"ratchet {name}: {len(new)} new, {len(carried)} carried from {base[:12]}")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
