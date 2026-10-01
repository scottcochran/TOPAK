#!/usr/bin/env python3
"""Walk every tracked .md and check that each backticked root-relative path exists; flag date tokens that are
not 20YY.MM.DD. Run at every cut. Paths moved by the 2026.09.30 reorganization are reported once as
information when they appear in frozen records; checkpoints/README.md carries the map."""
import os, re, subprocess, sys
repo = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
files = subprocess.run(["git", "ls-files", "*.md"], capture_output=True, text=True, cwd=repo).stdout.split()
PATH = re.compile(r"`((?:decisions|spec|floor|policies|mechanism|slm|derived|checkpoints|narrative|process|manifests|tools)/[^`\s]+)`")
ROOTNAME = re.compile(r"`((?:FOLD-LOG|FREEZE-AND-BATCH-A|NARRATIVE-LOG|NORMALIZATION-LOG|RECOVERY-REGISTRY)-[0-9.]+\.md|SHA256SUMS[-A-Za-z0-9.]*|tlc|tlc-workers|install-tla\.sh)`")
BADDATE = re.compile(r"\b20\d\d-\d\d-\d\d\b|\b201\d\.\d\d\.\d\d\b")
# Citations knowingly left stale, each with its reason; remove a line when the citing file is revised.
KNOWN = {
    ("derived/topak-rungs-axes-degeneracies-accounting-2026.09.26.md", "derived/derived/topak-glossary-2026.09.26.md"),  # the f160660 doubling, in a frozen file
    ("derived/topak-repo-reorganization-proposal-2026.09.30.md", "2016.09.27"),  # the proposal names the typo it corrects
    ("derived/topak-vs-nvidia-open-agent-safety-platform-2026.09.28.md", "tools/call"),  # an MCP method name, not a path
    ("slm/README.md", "mechanism/dev"),  # a runtime directory dev-init.sh creates, gitignored
    ("derived/topak-vs-nvidia-open-agent-safety-platform-2026.09.28.md", "2026-09-10"),  # an external release date, quoted
}
# Files exempt as a whole: they describe paths rather than cite them.
KNOWN_FILES = {"derived/topak-repo-reorganization-proposal-2026.09.30.md", "checkpoints/README.md"}  # the proposal and the layout map name old paths on purpose
MOVED = {"checkpoints/topak-theory-of-operation-": "narrative/", "SHA256SUMS": "manifests/", "FOLD-LOG": "process/", "FREEZE-AND": "process/",
         "NARRATIVE-LOG": "process/", "NORMALIZATION-LOG": "process/", "RECOVERY-REGISTRY": "process/", "derived/topak-glossary-2026.09.29.md": "narrative/glossary.md"}
missing, moved, dates = [], [], []
for f in files:
    if f in KNOWN_FILES:
        continue
    text = open(os.path.join(repo, f), encoding="utf-8").read()
    for m in PATH.finditer(text):
        p = m.group(1).rstrip(".,;:)")
        if any(ch in p for ch in "*<>") or (f, p) in KNOWN:
            continue
        if not os.path.exists(os.path.join(repo, p)):
            (moved if any(p.startswith(k) for k in MOVED) else missing).append((f, p))
    for m in ROOTNAME.finditer(text):
        if not os.path.exists(os.path.join(repo, m.group(1))):
            moved.append((f, m.group(1)))
    for m in BADDATE.finditer(text):
        before = text[max(0, m.start()-120):m.start()]
        if "claude.ai" in before or "<!--" in before.rsplit("-->", 1)[-1] or (f, m.group(0)) in KNOWN:
            continue
        dates.append((f, m.group(0)))
def show(title, rows):
    if rows:
        print(f"{title} ({len(rows)}):")
        for f, p in sorted(set(rows)): print(f"  {f}: {p}")
show("MISSING paths", missing)
show("date tokens not 20YY.MM.DD", dates)
if "-v" in sys.argv:
    show("moved by the 2026.09.30 cut (resolved by checkpoints/README.md)", moved)
else:
    print(f"moved by the 2026.09.30 cut and resolved by checkpoints/README.md: {len(set(moved))} citations (-v lists them)")
sys.exit(1 if missing or dates else 0)
