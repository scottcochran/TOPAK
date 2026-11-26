"""The corpus as it is at a pinned commit, read with git: what a link out may open, and the line it lands on.

Every link out of a diagram opens a file at a commit (lib.PIN_LINKS, or the diagram's own pin), never a branch, so
it lands on the line the diagram was linked against even after the file moves on in the tree. A target is looked up
in the file at that commit; one that is not there is not linked. Nothing here reads the working tree.

A Markdown file is opened as plain text at its line (`?plain=1#L<n>`, which GitHub highlights); a file named
without a line opens rendered. Standard library only.
"""
import pathlib
import re
import subprocess

REPO = "scottcochran/TOPAK"
GITHUB = f"https://github.com/{REPO}"
ROOT = pathlib.Path(__file__).resolve().parents[3]

_CACHE = {}


def _git(*args):
    if args not in _CACHE:
        r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)
        _CACHE[args] = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
    return _CACHE[args]


class Pin:
    """The tracked tree at one commit."""

    _ALL = {}

    def __new__(cls, commit):
        if commit not in cls._ALL:
            self = super().__new__(cls)
            self.commit = commit
            out = _git("ls-tree", "-r", "--name-only", commit)
            if out is None:
                raise FileNotFoundError(f"sources: commit {commit[:12]} is not in this checkout (the checkout needs "
                                        f"the full history)")
            self.files = frozenset(out.splitlines())
            dirs = set()
            for f in self.files:
                p = pathlib.PurePosixPath(f).parent
                while str(p) != ".":
                    dirs.add(str(p))
                    p = p.parent
            self.dirs = frozenset(dirs)
            base = {}
            for f in self.files:
                base.setdefault(pathlib.PurePosixPath(f).name, []).append(f)
            self.by_name = {k: v[0] for k, v in base.items() if len(v) == 1}
            self._text, self._lines, self._defs = {}, {}, None
            cls._ALL[commit] = self
        return cls._ALL[commit]

    # -- files
    def text(self, rel):
        if rel not in self._text:
            self._text[rel] = _git("show", f"{self.commit}:{rel}") if rel in self.files else None
        return self._text[rel]

    def lines(self, rel):
        if rel not in self._lines:
            t = self.text(rel)
            self._lines[rel] = t.split("\n") if t is not None else None
        return self._lines[rel]

    def url(self, rel, line=None):
        """The file (or directory) at the pin, at a line when one is given; None when the pin has no such path."""
        rel = rel.strip("/")
        if rel in self.dirs:
            return f"{GITHUB}/tree/{self.commit}/{rel}"
        if rel not in self.files:
            return None
        if line is None:
            return f"{GITHUB}/blob/{self.commit}/{rel}"
        plain = "?plain=1" if rel.endswith(".md") else ""
        return f"{GITHUB}/blob/{self.commit}/{rel}{plain}#L{line}"

    def path(self, name):
        """A code run that names a tracked path: itself, or a file name only one tracked file has."""
        n = name.strip()
        if n.startswith("./"):
            n = n[2:]
        if not n or any(c in n for c in " *<>{}|$"):
            return None
        n = n.rstrip("/") if n.endswith("/") and n.rstrip("/") in self.dirs else n
        if n in self.files or n in self.dirs:
            return n
        if "/" not in n and n in self.by_name and "." in n:
            return self.by_name[n]
        return None

    def find(self, rel, pattern, start=0, flags=0):
        """The 1-based number of the first line at or after `start` (0-based) that matches, or None."""
        ls = self.lines(rel)
        if ls is None:
            return None
        rx = re.compile(pattern, flags)
        for i in range(start, len(ls)):
            if rx.search(ls[i]):
                return i + 1
        return None

    # -- records, checkpoints, the narrative
    def record(self, n):
        rel = f"decisions/ADR-{n}.md"
        return rel if rel in self.files else None

    def section_line(self, rel, sec):
        """The heading of section `sec` ("2", "2.1", "6a"): the deepest numbered heading that names it, else its
        parent's."""
        parts = sec.split(".")
        while parts:
            s = re.escape(".".join(parts))
            ln = self.find(rel, rf"^#{{1,6}}\s+(?:§\s*)?{s}(?:\.|\b)(?![\d.]*\d)(?!\.\d)")
            if ln:
                return ln
            m = re.fullmatch(r"(\d+)[a-z]", parts[-1])
            parts = parts[:-1] + [m.group(1)] if m else parts[:-1]
        return None

    def mark_line(self, rel, mark):
        """An amendment, erratum or revision (A19, E1, R4): the heading that carries ⟨A19⟩, else its History row,
        else the first line that carries the marker."""
        m = re.escape(mark)
        return (self.find(rel, rf"^#{{1,6}} .*⟨{m}⟩") or self.find(rel, rf"^\|\s*(?:\*\*)?{m}(?:\*\*)?\s*\|")
                or self.find(rel, rf"⟨{m}⟩"))

    def annex_line(self, rel, letter):
        return self.find(rel, rf"^#{{1,6}} .*\bAnnex {letter}\b")

    def finding_line(self, rel, n):
        start = self.find(rel, r"^#{1,6} .*\bFindings\b")
        if start is None:
            return None
        return self.find(rel, rf"^(?:\|\s*{n}\s*\||{n}\.\s|\*\*{n}\.?\*\*)", start)

    def row_line(self, rel, key):
        """A table row keyed by `key` in bold (`| **T-0045-31** |`) or plain."""
        k = re.escape(key)
        return self.find(rel, rf"^\|\s*\*\*{k}\*\*\s*\|") or self.find(rel, rf"^\|\s*{k}\s*\|")

    def checkpoint(self, n):
        hits = sorted(f for f in self.files if re.fullmatch(rf"checkpoints/topak-genesis-checkpoint-G{n}-[\d.]+\.md", f))
        return hits[0] if len(hits) == 1 else None

    def item_line(self, rel, n):
        return self.find(rel, rf"^\|\s*(?:\*\*)?{n}(?:\*\*)?\s*\|")

    # -- TLA+ definitions
    _DEF = re.compile(r"^(?:(?:THEOREM|LEMMA|COROLLARY|PROPOSITION|ASSUME|AXIOM)\s+)?([A-Za-z_]\w*)\s*"
                      r"(?:\([^)]*\)|\[[^\]]*\])?\s*==", re.M)
    _DECL = re.compile(r"^(?:CONSTANTS?|VARIABLES?)\b(.*?)(?=^\S|\Z)", re.M | re.S)

    def definitions(self):
        """Name -> (file, line) for every name exactly one module under spec/ defines or declares."""
        if self._defs is None:
            seen = {}
            for rel in sorted(f for f in self.files if f.startswith("spec/") and f.endswith(".tla")):
                for k, v in self.defined_in(rel).items():
                    seen.setdefault(k, []).append((rel, v))
            self._defs = {k: v[0] for k, v in seen.items() if len(v) == 1}
        return self._defs

    def defined_in(self, rel):
        """Name -> line of every constant and variable `rel` declares and every name it defines (the first
        occurrence of each), in the order found; {} when the pin has no such file."""
        if not hasattr(self, "_defs_in"):
            self._defs_in = {}
        if rel not in self._defs_in:
            text = self.text(rel) or ""
            found = {}
            for m in self._DECL.finditer(text):
                base = text.count("\n", 0, m.start(1)) + 1
                body = re.sub(r"\(\*.*?\*\)", lambda c: re.sub(r"[^\n]", " ", c.group(0)), m.group(1), flags=re.S)
                for i, ln in enumerate(body.split("\n")):
                    ln = re.sub(r"\\\*.*$", "", ln)
                    for name in re.findall(r"(?:^|,)\s*([A-Za-z_]\w*)", ln):
                        found.setdefault(name, base + i)
            for m in self._DEF.finditer(text):
                found.setdefault(m.group(1), text.count("\n", 0, m.start()) + 1)
            self._defs_in[rel] = found
        return self._defs_in[rel]

    def module_definitions(self, rels):
        """Name -> (file, line) over the files of one module's diagram (its module first, then its proof module):
        an earlier file's definition wins, so a name the module defines opens the module."""
        out = {}
        for rel in rels:
            for k, v in self.defined_in(rel).items():
                out.setdefault(k, (rel, v))
        return out

    # -- commits and pull requests
    def commit_url(self, sha):
        """A commit the pin's history holds, named by an abbreviation of at least seven hex digits."""
        if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
            return None
        full = _git("rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}")
        if not full:
            return None
        full = full.strip()
        if subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", full, self.commit]).returncode:
            return None
        return f"{GITHUB}/commit/{full}"

    def merged_prs(self):
        if not hasattr(self, "_prs"):
            out = _git("log", "--merges", "--format=%s", self.commit) or ""
            self._prs = frozenset(int(n) for n in re.findall(r"^Merge pull request #(\d+)", out, re.M))
        return self._prs

    def pr_url(self, n):
        return f"{GITHUB}/pull/{n}" if int(n) in self.merged_prs() else None


def at(commit):
    return Pin(commit)
