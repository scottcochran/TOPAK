#!/usr/bin/env python3
"""A record's clauses and their pins (ADR-0057 §2, §7, Proposed).

The binding point of the specification graph above the model layer is the clause: a numbered subsection of a record's
Decision, with its inline amendments, cited as the corpus cites it ("ADR-0031 §4"). A clause pin is the digest of a
clause's text, so that a History row, a status line or an amendment drafted as its own pending subsection changes no
pin, and a changed clause does.

How a record is split, in order:

- **The header is no clause.** Everything from the first line to the first `---` line or `## ` heading (the title, the
  provenance note, Status, Status note, Pending, Depends on and the other fields) is left out.
- **`## History` is no clause**, wherever it stands.
- **A record with a `## Decision` section**: each `### ` subsection of it is a clause, `§N` when its heading begins
  `N.` and otherwise its heading, markers ⟨…⟩ and emphasis removed; text before the first `### ` is the clause
  `Decision`. A level-two section whose heading begins `N.` (ADR-0033's `## 7. Evidence`) is the clause `§N`, its
  subsections with it, and `## Annex X — …` is the clause `Annex X`. Context, Options considered, Consequences,
  Findings, Open obligations and every other level-two section are not clauses.
- **A record without one** (the recovered records of the first days) is one clause, `text`: every section but the
  header and History.
- **A subsection whose first line begins `*Pending ⟨`** is an amendment drafted as its own subsection and not yet
  applied (ADR-0033's pending addenda). It is left out of the clause it stands in. Pending text marked inline within a
  clause's own text is part of the clause, and changes its pin: the reference may follow it before it is in force,
  as it follows ADR-0054's.

A clause's digest is the SHA-256 of its lines, trailing whitespace stripped, joined with newlines; its pin is the first
16 hex digits, as every results file in the corpus prints a digest.

    clauses.py <record.md> ...        one line per clause: <pin>  <record> <clause>  (<first words of its heading>)
"""
import hashlib
import re
import sys

NUM = re.compile(r"^(\d+[a-z]?)\.\s")
ANNEX = re.compile(r"^Annex ([A-Z])\b")
MARK = re.compile(r"\s*⟨[^⟩]*⟩")


def _clean(heading):
    h = MARK.sub("", heading).replace("**", "").replace("*", "").strip()
    return re.sub(r"\s+", " ", h)


def _clause_id(heading):
    h = _clean(heading)
    m = NUM.match(h + " ")
    if m:
        return f"§{m.group(1)}"
    m = ANNEX.match(h)
    if m:
        return f"Annex {m.group(1)}"
    return h


def _drop_pending(lines):
    """Leave out every `###`/`####` subsection whose first non-blank line begins `*Pending ⟨`."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(#{3,4}) ", ln)
        if m:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith("*Pending ⟨"):
                depth = len(m.group(1))
                k = j
                while k < len(lines):
                    h = re.match(r"^(#{1,6}) ", lines[k])
                    if h and len(h.group(1)) <= depth:
                        break
                    k += 1
                i = k
                continue
        out.append(ln)
        i += 1
    return out


def _digest(lines):
    text = "\n".join(ln.rstrip() for ln in lines).strip("\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def sections(text):
    """(level, heading, body lines) for every `#`/`##` section after the header."""
    lines = text.splitlines()
    start = 0
    for n, ln in enumerate(lines):
        if n > 0 and (ln.strip() == "---" or ln.startswith("## ")):
            start = n
            break
    out, cur = [], None
    for ln in lines[start:]:
        m = re.match(r"^(#{1,2}) (.*)$", ln)
        if m:
            cur = (len(m.group(1)), m.group(2), [])
            out.append(cur)
        elif cur is not None:
            cur[2].append(ln)
    return out


def clauses(path):
    """[(clause id, heading, pin)] for one record, in order."""
    return clauses_of(open(path, encoding="utf-8").read())


def clauses_of(text):
    """[(clause id, heading, pin)] for a record's text, in order."""
    secs = [s for s in sections(text) if not _clean(s[1]).startswith("History")]
    has_decision = any(lvl == 2 and _clean(h) == "Decision" for lvl, h, _ in secs)
    out = []
    if not has_decision:
        body = []
        for lvl, h, b in secs:
            body += [("#" * lvl) + " " + h] + b
        body = _drop_pending(body)
        if any(ln.strip() for ln in body):
            out.append(("text", "the record's text", _digest(body)))
        return out
    for lvl, h, body in secs:
        name = _clean(h)
        if lvl == 2 and name == "Decision":
            pre, subs, cur = [], [], None
            for ln in body:
                m = re.match(r"^### (.*)$", ln)
                if m:
                    cur = (m.group(1), [ln])
                    subs.append(cur)
                elif cur is None:
                    pre.append(ln)
                else:
                    cur[1].append(ln)
            if any(ln.strip() and ln.strip() != "---" for ln in pre):
                out.append(("Decision", "Decision", _digest(pre)))
            for sh, sb in subs:
                sb = _drop_pending(sb)
                if sb and sb[0].startswith("### ") and len(sb) >= 1:
                    out.append((_clause_id(sh), _clean(sh), _digest(sb)))
        elif lvl == 2 and (NUM.match(name + " ") or ANNEX.match(name)):
            out.append((_clause_id(h), name, _digest(_drop_pending(["## " + h] + body))))
    seen = {}
    for i, (cid, h, d) in enumerate(out):
        if cid in seen:
            seen[cid] += 1
            out[i] = (f"{cid} ({seen[cid]})", h, d)
        else:
            seen[cid] = 1
    return out


def record_name(path):
    m = re.search(r"(ADR-\d{4})", path)
    return m.group(1) if m else path


def main():
    for p in sys.argv[1:]:
        for cid, h, d in clauses(p):
            print(f"{d}  {record_name(p)} {cid}  ({h[:60]})")


if __name__ == "__main__":
    main()
