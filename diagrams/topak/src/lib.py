"""Shared drawing library for the TOPAK diagram family.

Dependency-free. Every diagram is a Canvas; primitives measure their own text with the
Liberation Sans advance widths in metrics.py (metric-compatible with Arial/Helvetica), wrap it,
and return the height they used, so layouts are computed rather than hand-tuned.

Theming: every colour is written twice, once as a presentation attribute (the light theme, for
renderers without CSS) and once as a class whose CSS custom property switches under
`prefers-color-scheme: dark`. CSS beats presentation attributes, so browsers adapt and
everything else falls back to light. The light theme's page, behind the cards, is a grey matched to the
content's mean luminance (diagrams/PAGE.md), as in gov-tla and riemann-diagrams; the cards stay white.

Inline markup in any text: **bold**, `code`, and [[accent|text]] for an accent-coloured run.
"""
import functools
import pathlib
import re
import subprocess
from xml.sax.saxutils import escape, unescape

from metrics import W as _W

SANS = "Helvetica, Arial, 'Liberation Sans', sans-serif"
MONO = "'DejaVu Sans Mono', Menlo, Consolas, monospace"
MONO_EM = 0.602          # DejaVu Sans Mono / Menlo advance
MONO_SCALE = 0.92        # code runs are set slightly smaller than the surrounding text

DATE = "2026.10.05"
STATE = "State of record: Genesis Checkpoint G10 (2026.10.05) · narrative: Theory of Operation rev 14"
# A diagram amended after a cut says so in its footer (Canvas note=), beside the state it was drawn against; a diagram
# drawn new against a later cut states that cut (Canvas state=). Unamended diagrams regenerate byte for byte.
AMENDED_G11 = "amended 2026.10.09 against Genesis Checkpoint G11 (2026.10.09) and Theory of Operation rev 15"
STATE_G11 = "State of record: Genesis Checkpoint G11 (2026.10.09) · narrative: Theory of Operation rev 15 · drawn 2026.10.09"
# The command-chain overlay (ADR-0059 to ADR-0068, Proposed), drawn after G11 and Batches 38 and 39.
STATE_CC = ("State of record: Genesis Checkpoint G11 (2026.10.09), with Batches 38 and 39 · narrative: Theory of "
            "Operation rev 15 · drawn 2026.11.10 for ADR-0059 to ADR-0068 (Proposed, 2026.11.10; ADR-0059 to ADR-0067 "
            "revised R1 the same day)")
# Genesis Checkpoint G12 (2026.11.16) and Batch 40 (2026.11.17): diagrams amended or drawn new after the G12 cut.
AMENDED_G12 = "amended 2026.11.17 against Genesis Checkpoint G12 (2026.11.16), Batch 40 and Theory of Operation rev 16"
STATE_G12 = ("State of record: Genesis Checkpoint G12 (2026.11.16), with Batch 40 (2026.11.17) · narrative: Theory of "
             "Operation rev 16 · drawn 2026.11.17")

# A diagram that reads corpus files at build time reads them with git at the commit it was drawn at, once those files
# have moved on: it then regenerates as drawn, and a later change to the files is not a change to the diagram
# (diagrams/README.md). Moving a diagram's pin is an amendment of that diagram.
PIN_G12 = "4cbb883795d9e3b04a8eb252c81b31821dc2b0b9"   # main as the G12 amendment was drawn: the merge of PR #86, 2026.11.17


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True).stdout


def read_at(root, commit, rel):
    """The bytes of the tracked file `rel` (relative to the repository root) at `commit`."""
    try:
        return _git(root, "show", f"{commit}:{rel}")
    except subprocess.CalledProcessError:
        raise FileNotFoundError(f"{rel} at {commit[:7]} (the checkout needs the full history)") from None


def list_at(root, commit, rel_dir):
    """The names of the tracked files directly in `rel_dir` at `commit`, sorted."""
    out = _git(root, "ls-tree", "--name-only", commit, rel_dir.rstrip("/") + "/").decode()
    return sorted(pathlib.PurePosixPath(p).name for p in out.splitlines())


# ---------------------------------------------------------------------------------------------
# Links (the linking-posters method of riemann-diagrams' proof-posters plugin; diagrams/README.md § Links).
#
# Names open where they are drawn in full: a record (ADR-0069) its own diagram (B11, which names it in RECORDS),
# a trusted-base row (T-0045-31) its row on G1, a deployment row (D-0024-2) its card on G2, a code-font name the
# card or row that anchors it, on this diagram or the one other that does. References open their line in the source
# at the pin: a record's section, amendment, erratum, revision, annex or finding; a checkpoint's section or item; the
# Theory of Operation's section at its revision's tag. A file or directory in code font opens itself, a TLA+ name that
# one module defines its definition, a commit or merged pull request its page. Every link out is at a commit, never a
# branch: PIN_LINKS, or the diagram's own when it reads its files at a pin (PIN_LINKS = PIN_G12 in B11 and H9).
PIN_LINKS = "ffd02f1363a10bd0db03533f38c6a20fa0f18cab"      # main at 2026.11.20, after PR #99: the records as linked
# The Theory of Operation is one file, rewritten at each revision; a revision is read at its tag.
PIN_TOO_REV14 = "bd26b97375ebf1fce8821ac883a48cfe7743dc2d"  # tag ToO-rev14
PIN_TOO_REV15 = "a77d226932854312594b92b8480d43846b50dd58"  # tag ToO-rev15
PIN_TOO_REV16 = "603847533c835df720ea55bb5abd6a5236a70576"  # tag ToO-rev16
TOO_PINS = {"14": PIN_TOO_REV14, "15": PIN_TOO_REV15, "16": PIN_TOO_REV16}
TOO_FILE = "narrative/theory-of-operation.md"
# Which diagram draws a family of rows in full: a row named on another diagram opens there.
ROW_HOME = {"T": "G1", "D": "G2"}
TOP = "top"
HALO_PAD = 7
POSTERS, ANCHORS_OF, HOME_OF = {}, {}, {}   # from the manifest: id -> file; file -> anchors; record -> diagram id
_ANCHOR = re.compile(r"[A-Za-z_][\w.-]*")
_KEY = re.compile(r"([A-Za-z_][\w.-]*)(?:\([^`]*\))?")
_RESERVED = {"t", "d", TOP}


class _Context:
    """The diagram being built: its id, the records it draws (RECORDS), the commit its links open (PIN_LINKS), and
    its canvas, whose footer names the Theory of Operation revision an unversioned "ToO §x" means."""
    ident, records, pin, canvas = None, (), PIN_LINKS, None

    def too_rev(self):
        c = self.canvas
        revs = re.findall(r"Theory of Operation rev (\d+)", f"{(c and c.state) or STATE} {(c and c.note) or ''}")
        return max(revs, key=int) if revs else None


CTX = _Context()


def begin(module):
    """Called by the generator before a diagram's build(): what its text's references resolve against."""
    CTX.ident = module.ID
    CTX.records = tuple(getattr(module, "RECORDS", ()))
    CTX.pin = getattr(module, "PIN_LINKS", PIN_LINKS)
    _spans_cached.cache_clear()


def load_registry(manifest):
    """The links between diagrams resolve against the committed manifest, loaded before any diagram is built."""
    POSTERS.clear()
    ANCHORS_OF.clear()
    HOME_OF.clear()
    for pid, m in sorted(manifest.items()):
        POSTERS[pid] = m["file"]
        ANCHORS_OF[m["file"]] = frozenset(m.get("anchors", ()))
        for r in m.get("records", ()):
            HOME_OF[r] = pid


def poster_link(pid, frag=TOP):
    """file#frag of another diagram, when the manifest lists it and the anchor; else None."""
    f = POSTERS.get(pid)
    if f and (frag == TOP or frag in ANCHORS_OF[f]):
        return f"{f}#{frag}"
    return None


def linked(url, text):
    """A link run, or the text alone when there is no target."""
    return f"[[@{url}|{text}]]" if url else text


def unlinked(s):
    """Rich text with its link markup dropped: for a <title>, a <desc> and the manifest."""
    return re.sub(r"\[\[@[^|\]]+\|(.+?)\]\]", r"\1", s or "")


def halo(x, y, w, h, accent, pad=HALO_PAD, rx=14):
    """The frame behind an anchored group: one class attribute, the frame's and the colours'."""
    return (f'<rect x="{x - pad:.1f}" y="{y - pad:.1f}" width="{w + 2 * pad:.1f}" height="{h + 2 * pad:.1f}" '
            f'rx="{rx}" fill="{light(accent + "-t")}" stroke="{light(accent)}" '
            f'class="rd-target ft-{accent} s-{accent}" stroke-width="3.5" opacity="0"/>')

# ---------------------------------------------------------------------------------------------
# Theme tokens: name -> (light, dark)
BASE = {
    "bg":    ("#ffffff", "#12151b"),
    "page":  ("#eaeaea", "#12151b"),   # the page behind the cards: in light, the mean luminance of the content (PAGE.md)
    "ink":   ("#1e2430", "#e6e9ef"),
    "muted": ("#4a5262", "#b0b8c6"),
    "faint": ("#7d8596", "#7f8898"),
    "panel": ("#f5f6f8", "#1a1e26"),
    "line":  ("#d4d8e0", "#363d4a"),
    "zebra": ("#fafbfc", "#161a21"),
}
# accent -> (stroke light, tint light, stroke dark, tint dark)
ACCENTS = {
    "blue":   ("#2f5aa8", "#edf2fb", "#8fb0ec", "#1a2540"),   # authority, ratified
    "teal":   ("#166b5b", "#e8f5f1", "#6cc7b0", "#12302a"),   # mechanism, verified object
    "amber":  ("#a35a00", "#fdf3e4", "#f0b15c", "#33260f"),   # Proposed
    "violet": ("#6b46a8", "#f3eefb", "#b9a0e8", "#261d38"),   # draft
    "red":    ("#a4262c", "#fcefef", "#f08a8f", "#3a1a1d"),   # gap, deny, refused
    "grey":   ("#5f6878", "#f1f2f4", "#a3abb9", "#22262e"),   # neutral, external, withdrawn
    "brown":  ("#8a4b14", "#f9f0e6", "#e0a56b", "#2f2215"),   # humans, custody
    "pink":   ("#9d2f6e", "#fbeef5", "#ec8cc2", "#351a2a"),   # detection, Observer
    "green":  ("#2e7d32", "#edf6ee", "#85c98a", "#17291a"),   # subtraction, safe direction
}

STATUS = {
    # key: (label, accent, dash)
    "accepted":   ("Accepted", "blue", None),
    "proposed":   ("Proposed", "amber", "6 4"),
    "draft":      ("Draft, not ratified", "violet", "6 4"),
    "notbuilt":   ("Not built", "red", "2 3"),
    "built":      ("Built at reference", "teal", None),
    "superseded": ("Superseded", "grey", "2 3"),
    "withdrawn":  ("Withdrawn", "grey", "2 3"),
    "open":       ("Open", "red", "6 4"),
    # ratified and in force, subject to redesign (ADR-0029 A4); dashed so it never reads as settled
    "provisional": ("Accepted · provisional", "blue", "4 3"),
    # gated, pinned and enforced, ratified only when the bootstrap reviewer finds it fit (ADR-0030 A3)
    "genprov":    ("Genesis-provisional", "violet", "4 3"),
}


def _css():
    lines = []
    def block(idx_base, idx_s, idx_t):
        out = []
        for k, v in BASE.items():
            out.append(f"--{k}:{v[idx_base]};")
        for k, v in ACCENTS.items():
            out.append(f"--{k}:{v[idx_s]};--{k}-t:{v[idx_t]};")
        return "".join(out)
    lines.append("svg{" + block(0, 0, 1) + "}")
    lines.append("@media (prefers-color-scheme: dark){svg:not([data-theme=light]){" + block(1, 2, 3) + "}}")
    lines.append("svg[data-theme=dark]{" + block(1, 2, 3) + "}")
    lines.append("a:hover tspan,a:focus tspan,a:hover>text{text-decoration:underline}")
    lines.append(".rd-target{opacity:0} g:target>.rd-target{opacity:1;animation:rd-pulse 0.9s ease-in-out 3} "
                 "@keyframes rd-pulse{50%{stroke-width:9}} g[id]{scroll-margin-top:90px} "
                 "g.rd-row:target>rect:first-child{fill:var(--amber-t);stroke:var(--amber);stroke-width:3;"
                 "animation:rd-pulse 0.9s ease-in-out 3} "
                 "@media (prefers-reduced-motion:reduce){g:target>.rd-target,g.rd-row:target>rect:first-child"
                 "{animation:none}}")
    for k in BASE:
        lines.append(f".f-{k}{{fill:var(--{k})}} .s-{k}{{stroke:var(--{k})}}")
    for k in ACCENTS:
        lines.append(f".f-{k}{{fill:var(--{k})}} .ft-{k}{{fill:var(--{k}-t)}} .s-{k}{{stroke:var(--{k})}}")
    return "\n".join(lines)


_EXTERNAL = re.compile(r"\s*[^.|]*Moon & Varshney[^.|]*(?:\.|(?=\s*\|)|$)")


def strip_external(text):
    """Drop every sentence that cites Moon & Varshney from record text read at build time."""
    return _EXTERNAL.sub("", text)


def light(name):
    if name in BASE:
        return BASE[name][0]
    if name.endswith("-t"):
        return ACCENTS[name[:-2]][1]
    return ACCENTS[name][0]


def fill(name):
    """fill attribute + class for a token ('ink', 'blue', 'blue-t')."""
    cls = f"ft-{name[:-2]}" if name.endswith("-t") else f"f-{name}"
    return f'fill="{light(name)}" class="{cls}"'


def stroke(name):
    return f'stroke="{light(name)}"'


def fs(fill_name, stroke_name):
    """fill + stroke on one element (classes combined)."""
    fcls = f"ft-{fill_name[:-2]}" if fill_name.endswith("-t") else f"f-{fill_name}"
    return (f'fill="{light(fill_name)}" stroke="{light(stroke_name)}" '
            f'class="{fcls} s-{stroke_name}"')


def sonly(stroke_name):
    return f'fill="none" stroke="{light(stroke_name)}" class="s-{stroke_name}"'


# ---------------------------------------------------------------------------------------------
# Text measurement and rich-text wrapping

_RUN = re.compile(r"(\[\[@[^|\]]+\|.+?\]\]|\*\*.+?\*\*|`.+?`|\[\[[a-z]+\|.+?\]\])")


def _markup(s):
    runs = []
    for part in _RUN.split(s):
        if not part:
            continue
        if part.startswith("[[@") and part.endswith("]]"):
            url, txt = part[3:-2].split("|", 1)
            runs.extend((t, st, f"@{_color(a) or ''}|{url}") for t, st, a in _markup(txt))
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            # code inside bold: the code run is set in mono (which has no bold), the rest stays bold
            for sub in re.split(r"(`[^`]+`)", part[2:-2]):
                if sub.startswith("`") and sub.endswith("`") and len(sub) > 2:
                    runs.append((sub[1:-1], "m", None))
                elif sub:
                    runs.append((sub, "b", None))
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            runs.append((part[1:-1], "m", None))
        elif part.startswith("[[") and part.endswith("]]"):
            acc, txt = part[2:-2].split("|", 1)
            runs.append((txt, "b", acc))
        else:
            runs.append((part, "r", None))
    return runs


def _color(acc):
    """The colour token of a run's accent: a link run's accent is '@<colour>|<url>'."""
    if acc and acc.startswith("@"):
        return acc[1:].split("|", 1)[0] or None
    return acc


def _url(acc):
    return acc[1:].split("|", 1)[1] if acc and acc.startswith("@") else None


def parse(s):
    """-> list of (text, style, accent) runs. style in r/b/m (regular, bold, mono). A run inside [[@url|text]], or
    in a reference the text names (_references), carries the accent '@<colour>|<url>', and render_line makes it a
    link; the text, its style and so every measured width are as without it."""
    return _apply(_markup(s), _spans(s))


def _spans(s):
    return _spans_cached(s, CTX.ident, CTX.too_rev())


@functools.lru_cache(maxsize=None)
def _spans_cached(s, ident, too_rev):
    return tuple(_autolink(_markup(s)))


# -- references in running text
# A reference list is a document and what of it is cited, in order: "ADR-0033 §1–§3, §7 finding 9, A7, A10–A12",
# "G12 §8; item 88", "ToO rev 16 §2.3". What follows a document belongs to it while only these separators come
# between; anything else ends the list.
_SEP = re.compile(r"(?:'s)?\s*(?:[,;–—(]|\band\b|\bto\b|\bor\b|\bwith\b|\band\s+with\b)?\s*(?:\band\b\s*)?")
_FILE_EXT = r"(?:md|tla|txt|py|sh|rs|cedar|json|toml|yml|yaml|lean|tsv|cfg|sha256)"
_REF = re.compile(
    r"(?P<path>(?<![\w/.@-])(?:(?:\.?[\w-]+/)+(?:[\w.-]*[\w/])?|[\w-]+(?:\.[\w-]+)*\." + _FILE_EXT + r")(?![\w/-]))"
    r"|(?P<adr>ADR-(?P<adrn>\d{4})(?!\d))"
    r"|(?P<gck>(?P<gpre>Genesis Checkpoint )?\bG(?P<gn>\d{1,2})(?!\d))"
    r"|(?P<too>(?:\bToO|\bTheory of Operation)(?:,? rev(?:ision)? (?P<toon>\d+)\b)?)"
    r"|(?P<sec>§\s?(?P<secn>\d+(?:\.\d+)*[a-z]?)(?![\w.]*\d))"
    r"|(?P<mark>\b(?P<markk>[AER]\d{1,3})\b(?!\.\d|-))"
    r"|(?P<annex>\bAnnex (?P<annexk>[A-Z])\b)"
    r"|(?P<item>\bitems? (?P<itemn>\d+)\b)"
    r"|(?P<num>\b(?P<numn>\d+)\b)"
    r"|(?P<finding>\b[Ff]inding (?P<findingn>\d+)\b)"
    r"|(?P<row>\b(?P<rowk>T-0045-\d+|D-\d{4}-\d+)\b)"
    r"|(?P<pr>\b(?:PR|pull request) #(?P<prn>\d+)\b)")


def _ref_url(doc, kind, key):
    """The line a reference opens, or None. doc: ("adr", "0033") | ("g", "12") | ("too", "16") | ("md", path)."""
    import sources
    if doc[0] == "too":
        commit = TOO_PINS.get(doc[1])
        if not commit:
            return None
        p, rel = sources.at(commit), TOO_FILE
    elif doc[0] == "md":
        p, rel = sources.at(CTX.pin), doc[1]
        if kind != "sec":
            return None
    else:
        p = sources.at(CTX.pin)
        rel = p.record(doc[1]) if doc[0] == "adr" else p.checkpoint(doc[1])
    if not rel:
        return None
    if kind is None:
        return p.url(rel)
    ln = {"sec": lambda: p.section_line(rel, key),
          "mark": lambda: p.mark_line(rel, key) if doc[0] == "adr" else None,
          "annex": lambda: p.annex_line(rel, key) if doc[0] == "adr" else None,
          "finding": lambda: p.finding_line(rel, key) if doc[0] == "adr" else None,
          "item": lambda: p.item_line(rel, key) if doc[0] == "g" else None}[kind]()
    return p.url(rel, ln) if ln else None


_OTHER_SOURCE = re.compile(r"\bG\d{1,2}\b|\bToO\b|Theory of Operation|ADR-\d{4}|\bREADME\b|\.md\b")


def _references(text, codes=()):
    """(start, end, url) of every reference in `text`, in order; a url 'ref:<name>' is a name, resolved when the
    diagram is drawn (Canvas.link). Code runs are blanked in `text` (NUL), so nothing in code is read here; codes
    gives each one's (start, end, text), so that a section after a Markdown file in code is that file's."""
    import sources
    spans = []
    doc, last, prev_kind = None, None, None
    default = ("adr", CTX.records[0][4:]) if len(CTX.records) == 1 else None
    pin = sources.at(CTX.pin)
    # a Markdown file in code opens a reference list of its own: "`proof-certification.md` §2, §4"
    md = {b: pin.path(code) for a, b, code in codes if (pin.path(code) or "").endswith(".md")}
    raw = list(text)
    for a, b, code in codes:
        raw[a:b] = list(code[:b - a].ljust(b - a))
    raw = "".join(raw)
    for m in _REF.finditer(text):
        k = m.lastgroup
        if k == "path":
            # a path or file name in running text opens the file; a Markdown file opens a reference list
            rel = pin.path(m.group("path").rstrip("."))
            if rel:
                end = m.start() + len(m.group("path").rstrip("."))
                spans.append([m.start(), end, pin.url(rel), "doc"])
                if rel.endswith(".md"):
                    doc, last, prev_kind = ("md", rel), end, "doc"
                    continue
            doc, last = None, None
            continue
        # a section may take the diagram's one record only where nothing before it names another source
        explicit = _OTHER_SOURCE.search(raw, 0, m.start()) is not None
        if k == "sec":
            for end, rel in md.items():
                if (last is None or end >= last) and end <= m.start() and _SEP.fullmatch(text[end:m.start()]):
                    doc, last, prev_kind = ("md", rel), end, "doc"
        gap = text[last:m.start()] if last is not None else None
        attached = doc is not None and gap is not None and "\x00" not in gap and _SEP.fullmatch(gap) is not None
        if k == "adr":
            doc, last, prev_kind = ("adr", m.group("adrn")), m.end(), "doc"
            spans.append([m.start(), m.end(), "ref:ADR-" + m.group("adrn"), "doc"])
            continue
        if k == "gck":
            n = m.group("gn")
            nxt = text[m.end():m.end() + 14]
            is_ck = (m.group("gpre") or re.match(r"\s*(?:§|items? \d|\(20\d\d\.)", nxt)) \
                and sources.at(CTX.pin).checkpoint(n)
            if is_ck:
                doc, last, prev_kind = ("g", n), m.end(), "doc"
                spans.append([m.start(), m.end(), _ref_url(("g", n), None, None), "doc"])
            else:
                doc, last = None, None
            continue
        if k == "too":
            rev = m.group("toon") or CTX.too_rev()
            doc, last, prev_kind = ("too", rev), m.end(), "doc"
            spans.append([m.start(), m.end(), _ref_url(doc, None, None), "doc"])
            continue
        if k == "row":
            spans.append([m.start(), m.end(), "ref:" + m.group("rowk"), "name"])
            doc, last = None, None
            continue
        if k == "pr":
            spans.append([m.start(), m.end(), sources.at(CTX.pin).pr_url(m.group("prn")), "name"])
            doc, last = None, None
            continue
        # a part of a document: of the document before it, or, for a section with no document named anywhere
        # before it in the text, of the one record this diagram draws
        if not attached:
            if k == "sec" and default and not explicit:
                d = default
            else:
                if k not in ("num",):
                    doc, last = None, None
                continue
        else:
            d = doc
        if k == "num":
            if prev_kind != "item" or not attached:
                continue
            kind, key = "item", m.group("numn")
        else:
            kind = k
            key = m.group({"sec": "secn", "mark": "markk", "annex": "annexk", "item": "itemn",
                           "finding": "findingn"}[k])
        url = _ref_url(d, kind, key)
        if url and attached and spans and spans[-1][3] == "doc" and spans[-1][1] == m.start() - 1 \
                and text[m.start() - 1] == " ":
            # the document and its first part read as one: "ADR-0033 §2" opens §2
            spans[-1][1:4] = [m.end(), url, "part"]
        elif url:
            spans.append([m.start(), m.end(), url, "part"])
        doc, last, prev_kind = d, m.end(), kind
    return [(a, b, u) for a, b, u, _ in spans if u]


def _autolink(runs):
    """The (start, end, url) of every reference the runs' plain text makes (_references); code runs and runs
    already linked take no part."""
    text, codes, pos = [], [], 0
    for t, st, a in runs:
        if st == "m" or _url(a):
            text.append("\x00" * len(t))
            if st == "m":
                codes.append((pos, pos + len(t), t))
        else:
            text.append(t)
        pos += len(t)
    return _references("".join(text), codes)


def _apply(runs, spans, start=0):
    """Split runs (whose text begins at offset `start` of the string the spans were found in) at the spans, and
    give the pieces inside one its link. Code runs and runs already linked are left as they are."""
    if not spans:
        return list(runs)
    out, pos = [], start
    for t, st, acc in runs:
        end = pos + len(t)
        if st == "m" or _url(acc):
            out.append((t, st, acc))
            pos = end
            continue
        cuts = sorted({pos, end} | {x for a, b, _ in spans for x in (a, b) if pos < x < end})
        for a, b in zip(cuts, cuts[1:]):
            url = next((u for s0, s1, u in spans if s0 <= a and b <= s1), None)
            out.append((t[a - pos:b - pos], st, f"@{acc or ''}|{url}" if url else acc))
        pos = end
    return out


def width(s, size, style="r"):
    if style == "m":
        return len(s) * MONO_EM * size * MONO_SCALE
    tbl = _W["b" if style == "b" else "r"]
    return sum(tbl.get(c, 0.62) for c in s) * size


def text_width(s, size, bold=False):
    # measured on the runs as written: a link splits a run, and the sum must not move by a rounding
    return sum(width(t, size, "b" if (bold and st == "r") else st) for t, st, _ in _markup(s))


def wrap(s, maxw, size, bold=False):
    """Greedy wrap of rich text. Returns list of lines, each a list of runs. '\n' forces a break."""
    lines_out = []
    for para in s.split("\n"):
        # Lines are broken on the runs as written, and links are applied to each line after, so that a link never
        # adds a place to break: the layout is the same with links as without.
        spans = _spans(para)
        words = []  # (text, style, accent, offset in the paragraph) with trailing space info
        off = 0
        for txt, st, acc in _markup(para):
            if bold and st == "r":
                st = "b"
            parts = re.split(r"( )", txt)
            for p in parts:
                if p == "":
                    continue
                words.append((p, st, acc, off))
                off += len(p)
        line, lw = [], 0.0
        for w in words:
            ww = width(w[0], size, w[1])
            if w[0] == " ":
                if line:
                    line.append(w)
                    lw += ww
                continue
            if line and lw + ww > maxw:
                while line and line[-1][0] == " ":
                    lw -= width(" ", size, line[-1][1]); line.pop()
                lines_out.append(finish(line, spans))
                line, lw = [], 0.0
            line.append(w)
            lw += ww
        while line and line[-1][0] == " ":
            line.pop()
        lines_out.append(finish(line, spans))
    return lines_out


def finish(line, spans):
    """A wrapped line's words, with the links of the paragraph's spans applied (_apply)."""
    return [piece for t, st, acc, off in line for piece in _apply([(t, st, acc)], spans, off)]


def _merge(line):
    out = []
    for t, st, acc in line:
        if out and out[-1][1] == st and out[-1][2] == acc:
            out[-1] = (out[-1][0] + t, st, acc)
        else:
            out.append((t, st, acc))
    return out


def line_width(line, size):
    return sum(width(t, size, st) for t, st, _ in line)


TEXT_BOXES = []   # (x0, y0, x1, y1, text) of every line drawn, for the overlap check


def render_line(x, y, line, size, color="ink", anchor="start", bold=False):
    lw = line_width(line, size)
    bx = x if anchor == "start" else (x - lw / 2 if anchor == "middle" else x - lw)
    TEXT_BOXES.append((bx, y - size * 0.75, bx + lw, y + size * 0.2, "".join(t for t, _, _ in line)))
    spans, link, linked_ = [], None, []

    def flush():
        if linked_:
            spans.append(f'<a href="{escape(link, {chr(34): "&quot;"})}">{"".join(linked_)}</a>')
            linked_.clear()
    for t, st, acc in _merge(line):
        attrs = []
        if st == "b" or bold:
            attrs.append('font-weight="bold"')
        if st == "m":
            attrs.append(f'font-family="{MONO}" font-size="{size * MONO_SCALE:.1f}"')
        rcol, url = _color(acc), _url(acc)
        if rcol:
            attrs.append(fill(rcol))
        span = f'<tspan {" ".join(attrs)}>{escape(t)}</tspan>' if attrs else escape(t)
        if url != link:
            flush()
            link = url
        (linked_ if url else spans).append(span)
    flush()
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" '
            f'{fill(color)} text-anchor="{anchor}">{"".join(spans)}</text>')


# ---------------------------------------------------------------------------------------------

class Canvas:
    """One diagram. Primitives append SVG and track the lowest y used so height is computed."""

    def __init__(self, ident, title, subtitle, width, sources, pad=56, note=None, state=None):
        self.ident, self.title, self.subtitle, self.W = ident, title, subtitle, width
        self.sources = sources
        self.note, self.state = note, state
        self.pad = pad
        self.out = []
        self.ymax = 0
        self.x0, self.x1 = pad, width - pad
        self.blocks = []   # (x0, y0, x1, y1, name) of cards and tables, for the overlap check
        if CTX.ident == ident:
            CTX.canvas = self
        self.pin = CTX.pin if CTX.ident == ident else PIN_LINKS
        self.records = CTX.records if CTX.ident == ident else ()
        self.anchors = []  # ids of anchored groups, in the order drawn: the manifest lists them
        self.links = self.links_out = self.links_ext = 0   # made by link(): on this diagram, to another, out
        self.y = self._header()

    # -- bookkeeping
    def add(self, s, bottom=None):
        self.out.append(s)
        if bottom is not None:
            self.ymax = max(self.ymax, bottom)

    def _header(self):
        import sources
        p = self.pad
        self.add(f'<g id="{TOP}">')
        mark = len(self.out)
        label = (f'<text x="{p}" y="{p + 8}" font-family="{SANS}" font-size="13" letter-spacing="1.5" '
                 f'font-weight="bold" {fill("faint")}>TOPAK · {escape(self.ident)}</text>')
        # the label opens this diagram's row in the family's table (diagrams/README.md at the pin)
        pin = sources.at(self.pin)
        row = pin.find("diagrams/README.md", rf"^\|\s*{re.escape(self.ident)}\s*\|")
        back = pin.url("diagrams/README.md", row) if row else None
        self.add(f'<a href="{escape(back)}">{label}</a>' if back else label)
        y = p + 44
        for ln in wrap(self.title, self.W - 2 * p, 30, bold=True):
            self.add(render_line(p, y, ln, 30, "ink", bold=True))
            y += 38
        y += 2
        for ln in wrap(self.subtitle, self.W - 2 * p, 16):
            self.add(render_line(p, y, ln, 16, "muted"))
            y += 23
        y += 10
        self.out.insert(mark, halo(p - 10, p - 12, self.W - 2 * p + 20, y - p + 4, "grey"))
        self.add("</g>")
        self.add(f'<line x1="{p}" y1="{y}" x2="{self.W - p}" y2="{y}" {sonly("line")} stroke-width="1.5"/>', y)
        return y + 34

    # -- anchors
    _IDKEY = re.compile(r"(?:\*\*)?(?:\[\[[a-z]+\|)?(ADR-\d{4}|T-0045-\d+|D-\d{4}-\d+)(?:\]\])?(?:\*\*)?"
                        r"(?:\s*·.*|\s*\(.*|:\s.*)?", re.S)
    _CODEKEY = re.compile(r"(?:\*\*)?`([^`]+)`(?:\*\*)?(?:\s*·.*|\s+\(.*)?", re.S)

    def key_of(self, s, mono=False):
        """The anchor a card title or a row's first cell names, when it leads with a source's own key: a record,
        a trusted-base or deployment row (`ADR-0069`, `T-0045-31 · new`, `D-0024-2: …`), or one code run
        (`RulesFloorBase.tla`, `Read(ref)` -> Read); None otherwise."""
        s = (s or "").strip()
        m = self._IDKEY.fullmatch(s)
        if m:
            return m.group(1)
        if mono:
            code = s
        else:
            m = self._CODEKEY.fullmatch(s)
            code = m.group(1) if m else None
        k = _KEY.fullmatch(code.strip()) if code else None
        return k.group(1) if k else None

    def _usable(self, anchor):
        return (anchor and anchor not in self.anchors and anchor not in _RESERVED and not anchor.startswith("arw-")
                and _ANCHOR.fullmatch(anchor))

    def open_anchor(self, anchor, explicit=False):
        """Start an anchored group; returns the mark the halo goes at, or None when the id is taken or unusable
        (an explicit anchor that cannot be used raises)."""
        if not self._usable(anchor):
            if explicit:
                raise ValueError(f"{self.ident}: anchor {anchor!r} is taken or not an XML name")
            return None
        self.anchors.append(anchor)
        self.add(f'<g id="{escape(anchor)}">')
        return len(self.out)

    def close_anchor(self, mark, x, y, w, h, accent="grey", pad=HALO_PAD, rx=14):
        if mark is not None:
            self.out.insert(mark, halo(x, y, w, h, accent, pad, rx))
            self.add("</g>")

    # -- primitives
    def text(self, x, y, s, size=14, color="ink", anchor="start", bold=False):
        self.add(render_line(x, y, _merge([(t, "b" if bold and st == "r" else st, a) for t, st, a in parse(s)]),
                             size, color, anchor), y + size * 0.3)

    def para(self, x, y, w, s, size=14, color="ink", lead=None, bold=False, anchor="start", draw=True):
        lead = lead or round(size * 1.42, 1)
        lines = wrap(s, w, size, bold)
        if draw:
            for i, ln in enumerate(lines):
                ax = x if anchor == "start" else (x + w / 2 if anchor == "middle" else x + w)
                self.add(render_line(ax, y + size + i * lead, ln, size, color, anchor, bold))
            self.ymax = max(self.ymax, y + size * 0.35 + (len(lines) - 1) * lead + size)
        return (len(lines) - 1) * lead + size * 1.35

    def rect(self, x, y, w, h, accent="grey", tint=True, dash=None, rx=8, sw=1.6, fill_token=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        f = fill_token or (f"{accent}-t" if tint else "bg")
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'{fs(f, accent)} stroke-width="{sw}"{d}/>', y + h)

    def pill(self, x, y, label, accent="grey", size=12, dash=None, solid=False, anchor="start"):
        w = text_width(label, size, bold=True) + 18
        h = size + 10
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w / 2
        d = f' stroke-dasharray="{dash}"' if dash else ""
        if solid:
            self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" '
                     f'{fs(accent, accent)} stroke-width="1.2"/>')
            self.add(render_line(x + 9, y + size + 2.5, [(label, "b", None)], size, "bg"), y + h)
        else:
            self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="{h / 2}" '
                     f'{fs(accent + "-t", accent)} stroke-width="1.2"{d}/>')
            self.add(render_line(x + 9, y + size + 2.5, [(label, "b", None)], size, accent), y + h)
        return w

    def status(self, x, y, key, extra="", size=11.5, anchor="start"):
        label, acc, dash = STATUS[key]
        return self.pill(x, y, label + (f" · {extra}" if extra else ""), acc, size, dash, anchor=anchor)

    def card(self, x, y, w, title, body=(), accent="grey", status=None, status_extra="", dash=None,
             h=None, size=14, tsize=16, tint=True, draw=True, sub=None, pad=16, bullets=True, lead=None,
             anchor=None):
        """A titled box. body: list of rich strings (bulleted when bullets=True). Returns height. A card whose
        title leads with a source's key (key_of) is anchored by it; anchor= names it explicitly."""
        inner = w - 2 * pad
        lead = lead or round(size * 1.42, 1)
        tlines = wrap(title, inner - (0 if not status else 0), tsize, bold=True) if title else []
        hh = pad
        hh += len(tlines) * (tsize + 6)
        if sub:
            sublines = wrap(sub, inner, size - 1)
            hh += len(sublines) * round((size - 1) * 1.4, 1) + 2
        else:
            sublines = []
        status_h = 0
        if status:
            status_h = 11.5 + 10 + 8
            hh += status_h
        if tlines and body:
            hh += 6
        blines = []
        bul = "•  " if bullets else ""
        indent = width(bul, size) if bullets else 0
        for item in body:
            ls = wrap(item, inner - indent, size)
            blines.append(ls)
            hh += len(ls) * lead + 3
        hh += pad - 4
        if h is not None:
            hh = max(h, hh)
        if not draw:
            return hh
        mark = self.open_anchor(anchor or self.key_of(title), explicit=bool(anchor))
        if dash is None and status:
            dash = STATUS[status][2]
        self.blocks.append((x, y, x + w, y + hh, "card " + (title or "")[:40]))
        self.rect(x, y, w, hh, accent, tint=tint, dash=dash)
        cy = y + pad
        for ln in tlines:
            self.add(render_line(x + pad, cy + tsize - 2, ln, tsize, accent, bold=True))
            cy += tsize + 6
        for ln in sublines:
            self.add(render_line(x + pad, cy + size - 3, ln, size - 1, "muted"))
            cy += round((size - 1) * 1.4, 1)
        if sublines:
            cy += 2
        if status:
            cy += 2
            self.status(x + pad, cy, status, status_extra)
            cy += status_h - 2
        if tlines and body:
            cy += 6
        for ls in blines:
            for i, ln in enumerate(ls):
                if i == 0 and bullets:
                    self.add(render_line(x + pad, cy + size, [("•", "b", None)], size, accent))
                self.add(render_line(x + pad + indent, cy + size, ln, size, "ink"))
                cy += lead
            cy += 3
        self.close_anchor(mark, x, y, w, hh, accent)
        return hh

    def region(self, x, y, w, h, label, accent="grey", dash="10 6", sw=2.2, tint=False, size=14, rx=14):
        """A boundary container with a label tab on its top edge."""
        self.rect(x, y, w, h, accent, tint=tint, dash=dash, sw=sw, rx=rx, fill_token=None if tint else "bg")
        if tint is False:
            # transparent fill: overwrite the bg fill with none so nested content shows the canvas
            self.out[-1] = self.out[-1].replace(f'fill="{light("bg")}" ', 'fill="none" ').replace("f-bg ", "")
        if label:
            tw = text_width(label, size, bold=True) + 20
            self.add(f'<rect x="{x + 18:.1f}" y="{y - size / 2 - 6:.1f}" width="{tw:.1f}" height="{size + 12}" rx="6" '
                     f'{fs("bg", accent)} stroke-width="1.4"/>')
            self.add(render_line(x + 28, y + size / 2 - 1.5, parse(label), size, accent, bold=True))

    def arrow(self, pts, accent="grey", dash=None, sw=2, label=None, lsize=12.5, lpos=0.5, head=True,
              both=False, loff=(0, 0), lw=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        me = f' marker-end="url(#arw-{accent})"' if head else ""
        ms = f' marker-start="url(#arw-{accent})"' if both else ""
        self.add(f'<path d="{path}" {sonly(accent)} stroke-width="{sw}"{d}{me}{ms} '
                 f'stroke-linejoin="round"/>', max(p[1] for p in pts))
        if label:
            # label at fraction lpos along the polyline length
            segs = list(zip(pts, pts[1:]))
            lens = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs]
            tgt = sum(lens) * lpos
            for (a, b), L in zip(segs, lens):
                if tgt <= L or (a, b) == segs[-1]:
                    f = 0 if L == 0 else min(1, tgt / L)
                    mx, my = a[0] + (b[0] - a[0]) * f + loff[0], a[1] + (b[1] - a[1]) * f + loff[1]
                    break
                tgt -= L
            self.label(mx, my, label, accent, lsize, lw)

    def label(self, cx, cy, s, accent="grey", size=12.5, maxw=None):
        maxw = maxw or 10_000
        lines = wrap(s, maxw, size)
        lw = max(line_width(ln, size) for ln in lines)
        lead = size * 1.35
        h = len(lines) * lead + 6
        self.add(f'<rect x="{cx - lw / 2 - 7:.1f}" y="{cy - h / 2:.1f}" width="{lw + 14:.1f}" height="{h:.1f}" '
                 f'rx="5" {fs("bg", accent)} stroke-width="1"/>')
        for i, ln in enumerate(lines):
            self.add(render_line(cx, cy - h / 2 + 3 + size + i * lead - 2, ln, size, accent, "middle"))

    def line(self, x1, y1, x2, y2, accent="line", sw=1.4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {sonly(accent)} '
                 f'stroke-width="{sw}"{d}/>', max(y1, y2))

    def heading(self, x, y, s, accent="ink", size=19, w=None):
        """A section heading with a short rule under it. Returns height used."""
        self.text(x, y + size, s, size, accent, bold=True)
        return size + 16

    def table(self, x, y, cols, rows, size=13.5, header=True, hsize=13.5, pad=9, zebra=True, draw=True,
              accent="grey", anchor=None):
        """cols: list of (title, width[, opts]) where opts may hold mono/bold/accent/align.
        rows: list of lists of rich strings; or {'group': label, 'accent': a}; or
        {'cells': [...], 'accent': a, 'dash': bool} to tint a row. Returns height.
        anchor names the whole table (a list a count opens). A row whose first cell leads with a source's key
        (key_of) is anchored by it, unless the diagram anchors it already (the first drawn keeps it)."""
        lead = round(size * 1.38, 1)
        tw = sum(c[1] for c in cols)
        cy = y
        parts = []

        def cell_lines(s, cw, opt):
            s = s if s is not None else ""
            if opt.get("mono") and s:
                s = f"`{s}`"
            return wrap(s, cw - 2 * pad, size, bold=opt.get("bold", False))

        if header:
            hl = [wrap(c[0], c[1] - 2 * pad, hsize, bold=True) for c in cols]
            hh = max(len(l) for l in hl) * round(hsize * 1.35, 1) + 2 * pad - 2
            if draw:
                parts.append(f'<rect x="{x}" y="{cy:.1f}" width="{tw}" height="{hh:.1f}" {fs(accent, accent)} '
                             f'stroke-width="1"/>')
                cx = x
                for (c, ls) in zip(cols, hl):
                    for i, ln in enumerate(ls):
                        parts.append(render_line(cx + pad, cy + pad + hsize - 1 + i * round(hsize * 1.35, 1),
                                                 ln, hsize, "bg", bold=True))
                    cx += c[1]
            cy += hh
        for ri, r in enumerate(rows):
            if isinstance(r, dict) and "group" in r:
                gacc = r.get("accent", accent)
                gl = wrap(r["group"], tw - 2 * pad, size, bold=True)
                gh = len(gl) * lead + 2 * pad - 4
                if draw:
                    parts.append(f'<rect x="{x}" y="{cy:.1f}" width="{tw}" height="{gh:.1f}" '
                                 f'{fs(gacc + "-t", "line")} stroke-width="1"/>')
                    for i, ln in enumerate(gl):
                        parts.append(render_line(x + pad, cy + pad + size - 2 + i * lead, ln, size, gacc, bold=True))
                cy += gh
                continue
            racc, rdash = None, False
            if isinstance(r, dict):
                racc, rdash, r = r.get("accent"), r.get("dash", False), r["cells"]
            ls = [cell_lines(s, c[1], c[2] if len(c) > 2 else {}) for s, c in zip(r, cols)]
            rh = max(max(len(l), 1) for l in ls) * lead + 2 * pad - 4
            rkey = self.key_of(r[0], (cols[0][2] if len(cols[0]) > 2 else {}).get("mono")) if draw and r else None
            rkey = rkey if self._usable(rkey) else None
            if rkey:
                self.anchors.append(rkey)
                parts.append(f'<g id="{escape(rkey)}" class="rd-row">')   # framed by recolouring its own rect
            if draw:
                bgtok = f"{racc}-t" if racc else ("zebra" if zebra and ri % 2 else "bg")
                parts.append(f'<rect x="{x}" y="{cy:.1f}" width="{tw}" height="{rh:.1f}" {fs(bgtok, "line")} '
                             f'stroke-width="1"/>')
                if racc:
                    parts.append(f'<rect x="{x}" y="{cy:.1f}" width="5" height="{rh:.1f}" {fill(racc)}/>')
                cx = x
                for c, cl in zip(cols, ls):
                    opt = c[2] if len(c) > 2 else {}
                    col = opt.get("accent", "ink")
                    for i, ln in enumerate(cl):
                        parts.append(render_line(cx + pad, cy + pad + size - 2 + i * lead, ln, size, col,
                                                 bold=opt.get("bold", False)))
                    cx += c[1]
            if rkey:
                parts.append("</g>")
            cy += rh
        if draw:
            self.blocks.append((x, y, x + tw, cy, "table " + cols[0][0][:30]))
            # column rules
            cx = x
            for c in cols[:-1]:
                cx += c[1]
                parts.append(f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{cy:.1f}" {sonly("line")} stroke-width="1"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{cy - y:.1f}" {sonly(accent)} '
                         f'stroke-width="1.4"/>')
            mark = self.open_anchor(anchor, explicit=True) if anchor else None
            self.add("\n".join(parts), cy)
            self.close_anchor(mark, x, y, tw, cy - y, "amber")   # a list lands framed as a row does
        return cy - y

    def legend(self, x, y, items, title="Legend", size=13, maxw=None):
        """items: list of (kind, accent, label, dash) where kind is 'box', 'line', 'arrow', 'status'."""
        maxw = maxw or (self.x1 - x)
        cx, cy = x, y
        self.text(cx, cy + size, title, size, "faint", bold=True)
        cx += text_width(title, size, True) + 18
        for it in items:
            kind, acc, lab = it[0], it[1], it[2]
            dash = it[3] if len(it) > 3 else None
            iw = 34 + text_width(lab, size) + 26
            if cx + iw > x + maxw:
                cx = x + text_width(title, size, True) + 18
                cy += size + 16
            d = f' stroke-dasharray="{dash}"' if dash else ""
            if kind == "box":
                self.add(f'<rect x="{cx}" y="{cy + 1}" width="26" height="{size + 3}" rx="4" {fs(acc + "-t", acc)} '
                         f'stroke-width="1.6"{d}/>')
            elif kind == "line":
                self.add(f'<line x1="{cx}" y1="{cy + size / 2 + 2}" x2="{cx + 26}" y2="{cy + size / 2 + 2}" '
                         f'{sonly(acc)} stroke-width="2.2"{d}/>')
            elif kind == "arrow":
                self.add(f'<path d="M {cx} {cy + size / 2 + 2} L {cx + 24} {cy + size / 2 + 2}" {sonly(acc)} '
                         f'stroke-width="2"{d} marker-end="url(#arw-{acc})"/>')
            self.text(cx + 34, cy + size, lab, size, "muted")
            cx += iw
        self.ymax = max(self.ymax, cy + size + 6)
        return cy + size + 6 - y

    # -- output
    def check(self):
        """Warn about text lines whose boxes intersect, or that leave the canvas. Returns the warnings."""
        boxes = [b for b in TEXT_BOXES if b[4].strip()]
        warn = []
        for b in boxes:
            if b[0] < 0 or b[2] > self.W + 0.5:
                warn.append(f"off-canvas: {b[4][:60]!r} x={b[0]:.0f}..{b[2]:.0f}")
        bl = self.blocks
        for i, a in enumerate(bl):
            for b in bl[i + 1:]:
                inter = a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1
                if not inter:
                    continue
                a_in_b = b[0] <= a[0] and a[2] <= b[2] and b[1] <= a[1] and a[3] <= b[3]
                b_in_a = a[0] <= b[0] and b[2] <= a[2] and a[1] <= b[1] and b[3] <= a[3]
                if not (a_in_b or b_in_a):
                    warn.append(f"block overlap: {a[4]!r} and {b[4]!r}")
        boxes.sort(key=lambda b: b[1])
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                if b[1] >= a[3] - 1:
                    break
                if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                    warn.append(f"overlap: {a[4][:50]!r} @({a[0]:.0f},{a[1]:.0f}) with {b[4][:50]!r} "
                                f"@({b[0]:.0f},{b[1]:.0f})")
        return warn

    # -- links
    _TOKEN = re.compile(r'(<g\b[^>]*>|</g>|<a href="ref:([^"]*)">(.*?)</a>|<a href="[^"]*">.*?</a>'
                        r'|<tspan ((?:[^<>]*? )?font-family="' + re.escape(MONO) + r'"[^<>]*)>([^<>]+)</tspan>)',
                        re.S)
    # code runs that are words of the prose, never names to open
    _PLAIN = {"none", "true", "false", "main", "and", "or", "not", "if", "then", "else"}

    def _anchored_elsewhere(self, key):
        """file#key of the one other diagram that anchors `key`, else None."""
        homes = [f for f in sorted(ANCHORS_OF) if key in ANCHORS_OF[f] and f != POSTERS.get(self.ident)]
        return f"{homes[0]}#{key}" if len(homes) == 1 else None

    def resolve_name(self, name, inside):
        """Where a name in running text opens: a record, a trusted-base row or a deployment row. inside: the ids of
        the groups it is drawn in, so that a row's own key opens its source rather than itself."""
        import sources
        pin = sources.at(self.pin)
        own = name in self.anchors and name not in inside
        if own:
            return f"#{name}", "in"
        if name.startswith("ADR-"):
            home = HOME_OF.get(name)
            if home and home != self.ident:
                u = poster_link(home)
                if u:
                    return u, "out"
            rel = pin.record(name[4:])
            return (pin.url(rel), "ext") if rel else (None, None)
        fam = name[0]
        home = ROW_HOME.get(fam)
        if home and home != self.ident:
            u = poster_link(home, name)
            if u:
                return u, "out"
        if fam == "D":
            rhome = HOME_OF.get(f"ADR-{name[2:6]}")
            u = poster_link(rhome, name) if rhome and rhome != self.ident else None
            if u:
                return u, "out"
        rel = pin.record("0045" if fam == "T" else name[2:6])
        ln = pin.row_line(rel, name) if rel else None
        return (pin.url(rel, ln), "ext") if ln else (None, None)

    def resolve_code(self, name, inside):
        """Where a code run opens: an anchor on this diagram; a tracked file or directory; the one other diagram
        that anchors the name; the definition, when one module under spec/ defines it; a commit of the pin's
        history. None when none of them."""
        import sources
        pin = sources.at(self.pin)
        raw = unescape(name)
        k = _KEY.fullmatch(raw.strip())
        key = k.group(1) if k else None
        if key and key in self.anchors:
            if key not in inside:
                return f"#{key}", "in"
        path = pin.path(raw)
        if path:
            return pin.url(path), "ext"
        if not key or len(key) < 3 or key.lower() in self._PLAIN:
            return None, None
        u = pin.commit_url(raw.strip())
        if u:
            return u, "ext"
        # Beyond this diagram, only a name no prose word could be: `clearSet`, `KUp`, `M_KIND`, `topak-floor`,
        # never `seat`, `Read` or `input`, which mean different things on different diagrams; and never a short
        # id such as `B10` or `R5`, which may be a boundary, a rule, a gate or a diagram.
        if not self._distinctive(key):
            return None, None
        u = self._anchored_elsewhere(key) if key not in inside else None
        if u:
            return u, "out"
        d = pin.definitions().get(key) if key == raw.strip() else None
        if d:
            return pin.url(d[0], d[1]), "ext"
        return None, None

    @staticmethod
    def _distinctive(key):
        if re.fullmatch(r"[A-Z]{1,3}-?\d+[a-z]?", key):
            return False
        return re.search(r"[a-z][A-Z]|[A-Z][A-Z]|_|\d|[a-z]-[a-z]|\.[a-z]", key) is not None

    def link(self):
        """Resolve the names the text made links of (ref:<name>), and make every code run that names an anchor or a
        source a link. A name with nowhere to go is left as text. Plain href, SVG's own <a> inside <text>; no glyph
        is added, so the measured widths and the overlap check are unchanged."""
        text = "\n".join(self.out)
        stack, out, pos = [], [], 0
        for m in self._TOKEN.finditer(text):
            out.append(text[pos:m.start()])
            pos = m.end()
            tok = m.group(1)
            href, kind = None, None
            if tok.startswith("<g"):
                im = re.match(r'<g id="([^"]*)"', tok)
                stack.append(unescape(im.group(1)) if im else None)
            elif tok == "</g>":
                stack.pop()
            elif m.group(2) is not None:
                href, kind = self.resolve_name(unescape(m.group(2)), stack)
                tok = f'<a href="{escape(href, {chr(34): "&quot;"})}">{m.group(3)}</a>' if href else m.group(3)
            elif m.group(5) is not None:
                href, kind = self.resolve_code(m.group(5), stack)
                if href:
                    tok = f'<a href="{escape(href, {chr(34): "&quot;"})}">{tok}</a>'
            elif tok.startswith("<a "):
                h = unescape(re.match(r'<a href="([^"]*)"', tok).group(1))
                kind = "ext" if "://" in h else ("in" if h.startswith("#") else "out")
                href = h
            if href:
                attr = {"in": "links", "out": "links_out", "ext": "links_ext"}[kind]
                setattr(self, attr, getattr(self, attr) + 1)
            out.append(tok)
        out.append(text[pos:])
        if stack:
            raise ValueError(f"{self.ident}: groups left open: {stack}")
        self.out = ["".join(out)]

    def check_links(self):
        """Every link lands: on an id of this diagram, on an anchor the manifest lists for another, or on a file at
        a pinned commit (or a commit or pull request page). No link markup is left as text, and no id is drawn
        twice."""
        import sources
        body = "\n".join(self.out)
        warn = []
        ids = re.findall(r' id="([^"]*)"', body)
        for i in sorted({i for i in ids if ids.count(i) > 1}):
            warn.append(f"id drawn twice: {i!r}")
        own = set(self.anchors) | {TOP}
        pins = {self.pin, *TOO_PINS.values()}
        ok_out = tuple(f"{sources.GITHUB}/{k}/{c}/" for c in pins for k in ("blob", "tree")) + \
            (f"{sources.GITHUB}/commit/", f"{sources.GITHUB}/pull/")
        for h in sorted(set(re.findall(r' href="([^"]*)"', body))):
            f, _, frag = unescape(h).partition("#")
            if "://" in f:
                if not f.startswith(ok_out):
                    warn.append(f"link out not at a pinned commit: {h}")
            elif f.startswith("ref:"):
                warn.append(f"name left unresolved: {h}")
            elif not f:
                if frag not in own:
                    warn.append(f"link to no anchor on this diagram: #{frag}")
            elif f not in ANCHORS_OF:
                warn.append(f"link to a diagram the manifest does not list: {f}")
            elif not frag:
                warn.append(f"link to a diagram with no target: {f}")
            elif frag != TOP and frag not in ANCHORS_OF[f]:
                warn.append(f"link to an anchor {f} does not draw: #{frag}")
        if "[[@" in body:
            warn.append("link markup left as text: [[@")
        return warn

    def svg(self):
        p = self.pad
        y = self.ymax + 44
        self.add(f'<line x1="{p}" y1="{y}" x2="{self.W - p}" y2="{y}" {sonly("line")} stroke-width="1.2"/>')
        y += 26
        src = "Sources: " + self.sources
        for ln in wrap(src, self.W - 2 * p, 13):
            self.add(render_line(p, y, ln, 13, "faint"))
            y += 19
        foot = (f"{self.state or STATE}{' · ' + self.note if self.note else ''} · generated {DATE} by "
                f"diagrams/gen-topak-family.py · "
                f"documentation licence CC BY 4.0 (LICENSE-DOCS)")
        for ln in wrap(foot, self.W - 2 * p, 13):
            self.add(render_line(p, y, ln, 13, "faint"))
            y += 19
        H = int(y + p - 20)
        markers = "".join(
            f'<marker id="arw-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="13" markerHeight="13" '
            f'orient="auto-start-reverse" markerUnits="userSpaceOnUse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" {fill(k)}/></marker>'
            for k in list(ACCENTS) + ["ink", "muted", "faint"])
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{H}" '
                f'viewBox="0 0 {self.W} {H}" aria-labelledby="t d">\n'
                f'<title id="t">TOPAK {escape(self.ident)} — {escape(re.sub(r"[*`]", "", unlinked(self.title)))}</title>\n'
                f'<desc id="d">{escape(re.sub(r"[*`]", "", unlinked(self.subtitle)))}</desc>\n'
                f'<style>\n{_css()}\n</style>\n<defs>{markers}</defs>\n'
                f'<rect width="{self.W}" height="{H}" {fill("page")}/>\n')
        self.warnings = self.check()
        self.link()
        self.warnings += self.check_links()
        TEXT_BOXES.clear()
        return head + "\n".join(self.out) + "\n</svg>\n"
