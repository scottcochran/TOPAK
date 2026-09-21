#!/usr/bin/env python3
"""Generate the G1 -> source control -> bootstrap process diagram (SVG).

Sources: Genesis Checkpoint G1 (2026.09.15) §1 conventions, §8 debt ledger, §11;
ADR-0029 §1-§7; SCRUB-LOG.md and the 09.15 migration session;
process/MIGRATION-PLAN-2026.09.18.md.
"""
from xml.sax.saxutils import escape

W, H = 1680, 1300

INK      = "#1e2430"
MUTED    = "#5a6374"
FAINT    = "#8b93a3"
BG       = "#ffffff"
LANE_BG  = "#f6f7f9"
LANE_BR  = "#e3e6ec"
OUT      = "#6b7280"
OUT_BG   = "#f1f2f4"
TMP      = "#b45309"
TMP_BG   = "#fdf6ec"
CAN      = "#2f5aa8"
CAN_BG   = "#eef3fb"
CUS      = "#166b5b"
CUS_BG   = "#ecf6f3"
NEVER    = "#a4262c"
NEVER_BG = "#fdf0f0"

F = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"
M = "'SF Mono', 'DejaVu Sans Mono', Menlo, Consolas, monospace"

out = []
add = out.append


def text(x, y, s, size=11, fill=INK, weight="normal", anchor="start", family=F, spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{sp}>{escape(s)}</text>')


def box(x, y, w, h, stroke, fill, dash=None, rx=7, sw=1.4):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def card(x, y, w, title, lines, stroke, fill, dash=None, pad=11, lead=14.5):
    h = pad + 15 + len(lines) * lead + pad - 3
    s = [box(x, y, w, h, stroke, fill, dash),
         text(x + pad, y + pad + 11, title, 12.5, stroke, "bold")]
    ty = y + pad + 27
    for ln in lines:
        s.append(text(x + pad, ty, ln, 10.5, MUTED))
        ty += lead
    return "\n".join(s), h


def arrow(x1, y1, x2, y2, stroke=MUTED, dash=None, sw=1.6, marker="arw"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')


def lane(y, h, label, sub_lines, accent):
    s = [box(44, y, W - 88, h, LANE_BR, LANE_BG, rx=10, sw=1),
         f'<rect x="44" y="{y}" width="4" height="{h}" rx="2" fill="{accent}"/>',
         text(62, y + 21, label, 12.5, accent, "bold", spacing="0.4")]
    yy = y + 37
    for ln in sub_lines:
        s.append(text(62, yy, ln, 9.8, FAINT))
        yy += 12
    return "\n".join(s)


# ------------------------------------------------------------------ frame
add(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
add(text(44, 46, "TOPAK — from Genesis Checkpoint G1 into source control, and on to bootstrap", 21, INK, "bold"))
add(text(44, 68, "The artifact ratchet (top three lanes) and the custody track (bottom)  ·  2026.09.18  ·  genesis custodian: Scott, (1, 0)",
         11.5, MUTED))
add(text(W - 44, 46, "process/MIGRATION-PLAN-2026.09.18.md", 10.5, FAINT, anchor="end", family=M))
add(text(W - 44, 65, "G1 §1 conventions · §8 debt ledger · ADR-0029 §5–§7", 10.5, FAINT, anchor="end"))

LA, LB, LC, LD = 90, 307, 548, 818
add(lane(LA, 187, "OUTSIDE SOURCE CONTROL", ["authored here,", "never canonical"], OUT))
add(lane(LB, 211, "TEMPORARY REPOSITORY", ["one per tranche,", "then deleted"], TMP))
add(lane(LC, 250, "CANONICAL PRIVATE REPOSITORY", ["main · signed tags"], CAN))
add(lane(LD, 245, "CUSTODY AND GOVERNANCE", ["who may admit", "a change"], CUS))

# ------------------------------------------------------------------ lane A
ay = LA + 50
a1, ha1 = card(190, ay, 268, "G1 corpus · 2026.09.15", [
    "49 files at corpus paths, each pinned",
    "by SHA-256 over its bytes (G-C1)",
    "SHA256SUMS-G1 · G1 = f46e88da…",
    "includes references/ — 3 files",
], OUT, OUT_BG)
add(a1)
a2, ha2 = card(742, ay, 300, "Produced since G1 · 37 sessions", [
    "Class A — 3 filed in the Project:",
    "critical review · log 09.17 · glossary",
    "Class C — 4 delivered, never filed:",
    "feature list rev 2 · LTRO assessment ·",
    "diagram sources · gap map",
    "+ this plan · SESSION-REGISTER.md",
], OUT, OUT_BG)
add(a2)
add(text(478, ay + 34, "the cut is the baseline:", 10.2, FAINT))
add(text(478, ay + 49, "G1 itself can never change,", 10.2, FAINT))
add(text(478, ay + 64, "so every later fix is a diff", 10.2, FAINT))

# ------------------------------------------------------------------ lane B
by = LB + 50
t1, ht1 = card(190, by, 268, "TEMP #1 — the G1 import · 09.15", [
    "1  import verbatim — 49/49 OK",
    "2  scrub by commit: remove only,",
    "    references/ ×3, named by digest",
    "3  review — genesis route:",
    "    the custodian, alone",
    "4  reviewed tree 8f3e297c… · 46/46",
    "— then deleted; never pushed",
], TMP, TMP_BG, dash="5 4")
add(t1)
t2, ht2 = card(742, by, 300, "TEMP #2 — import tranche I1 · next", [
    "1  import verbatim at corpus paths:",
    "    Class A digests + Class C bytes",
    "2  scrub: excluded items removed",
    "    by digest; nothing edited",
    "3  review — genesis route (as above)",
    "4  reviewed tree → SHA256SUMS-I1",
    "— then deleted; never pushed",
], TMP, TMP_BG, dash="5 4")
add(t2)
nv, hnv = card(478, by + 8, 246, "Never enters the repository", [
    "references/ — Moon & Varshney,",
    "NIST Playbook: not ours to give",
    "the unpublished draft article",
    "article-track drafts · stale scoring",
    "→ pinned by digest, REFERENCES.md",
], NEVER, NEVER_BG)
add(nv)
add(arrow(458, by + 62, 474, by + 62, NEVER, dash="4 3"))
add(arrow(742, by + 62, 726, by + 62, NEVER, dash="4 3"))

# A -> B
add(arrow(324, ay + ha1, 324, by - 4, OUT))
add(text(332, by - 16, "import", 10, MUTED))
add(arrow(892, ay + ha2, 892, by - 4, OUT))
add(text(900, by - 16, "import", 10, MUTED))

# ------------------------------------------------------------------ lane C
RAIL = LC + 146
add(arrow(300, by + ht1, 300, RAIL - 6, TMP))
add(arrow(892, by + ht2, 892, RAIL - 13, TMP))
add(text(440, LC + 44, "copy — git archive of the reviewed tree,", 10.2, TMP))
add(text(440, LC + 58, "never a fetch: pre-scrub objects", 10.2, MUTED))
add(text(440, LC + 72, "never reach canonical history", 10.2, MUTED))
add(text(900, LC + 44, "copy, then verify per-path blob equality", 10.2, TMP))
add(text(900, LC + 58, "against the reviewed tree — derived/ already", 10.2, MUTED))
add(text(900, LC + 72, "holds G1 files, so no subtree hash", 10.2, MUTED))

add(f'<line x1="200" y1="{RAIL}" x2="1560" y2="{RAIL}" stroke="{CAN}" stroke-width="2.4"/>')


def commit(cx, label, lines, above=False, r=9):
    s = [f'<circle cx="{cx}" cy="{RAIL}" r="{r}" fill="{BG}" stroke="{CAN}" stroke-width="2.6"/>']
    if above:
        top = RAIL - 30 - len(lines) * 13
        s.append(f'<line x1="{cx}" y1="{RAIL - r - 2}" x2="{cx}" y2="{RAIL - 26}" stroke="{FAINT}" stroke-width="1"/>')
        s.append(text(cx, top, label, 11, INK, "bold", anchor="middle"))
        for i, ln in enumerate(lines):
            s.append(text(cx, top + 13 * (i + 1), ln, 10, MUTED, anchor="middle"))
    else:
        s.append(f'<line x1="{cx}" y1="{RAIL + r + 2}" x2="{cx}" y2="{RAIL + 18}" stroke="{FAINT}" stroke-width="1"/>')
        s.append(text(cx, RAIL + 30, label, 11, INK, "bold", anchor="middle"))
        for i, ln in enumerate(lines):
            s.append(text(cx, RAIL + 30 + 13 * (i + 1), ln, 10, MUTED, anchor="middle"))
    return "\n".join(s)


def tagflag(cx, name, note):
    y = RAIL - 78
    s = [f'<line x1="{cx}" y1="{RAIL - 11}" x2="{cx}" y2="{y + 26}" stroke="{CUS}" stroke-width="1.6"/>',
         f'<path d="M {cx} {y} H {cx + 92} l -12 13 l 12 13 H {cx} Z" fill="{CUS_BG}" stroke="{CUS}" stroke-width="1.5"/>',
         text(cx + 11, y + 18, name, 12, CUS, "bold", family=M)]
    for i, ln in enumerate(note):
        s.append(text(cx, y + 42 + i * 13, ln, 9.8, MUTED if i else CUS))
    return "\n".join(s)


add(commit(324, "Genesis Checkpoint G1", ["root commit = the reviewed tree,", "byte for byte · 8f3e297c…"]))
add(tagflag(324, "g1", ["signed by the custodian — the attestation.",
                        "CI is evidence; it attests nothing."]))
add(commit(545, "Cleanup step 6", ["Theory of Operation rev 5", "+ narrative log (S6-1…18)"]))
add(commit(892, "Import I1", ["Class A + Class C at corpus paths", "SHA256SUMS-I1 · SCRUB-LOG §I1"]))
add(commit(1000, "Restructure", ["renames only — living docs", "drop their dates (S6-18)"], above=True))
add(commit(1100, "CI", ["manifest · lint · TLC rerun"]))
add(commit(1245, "Import rule (Proposed)", ["the route above, recorded"]))
for cx in (1320, 1342, 1364, 1386):
    add(f'<circle cx="{cx}" cy="{RAIL}" r="6.5" fill="{BG}" stroke="{CAN}" stroke-width="2.2"/>')
add(f'<line x1="1353" y1="{RAIL - 8}" x2="1353" y2="{RAIL - 26}" stroke="{FAINT}" stroke-width="1"/>')
add(f'<line x1="1353" y1="{RAIL - 26}" x2="1330" y2="{RAIL - 34}" stroke="{FAINT}" stroke-width="1"/>')
add(text(1330, RAIL - 69, "S6 fixes, then ratification", 11, INK, "bold", anchor="middle"))
add(text(1330, RAIL - 56, "S6-2 and S6-3 first — mechanism text,", 10, MUTED, anchor="middle"))
add(text(1330, RAIL - 43, "then the RulesFloorNV rerun", 10, MUTED, anchor="middle"))
add(commit(1470, "Genesis Checkpoint G2", ["records G1's digest, the I1 sources,", "the layout convention, the ledger"], r=10))
add(tagflag(1470, "g2", ["signed · SHA256SUMS-G2,",
                         "then the Project mirrors it."]))
for cx in (1522, 1537, 1552):
    add(f'<circle cx="{cx}" cy="{RAIL}" r="3" fill="{FAINT}"/>')
add(text(1636, RAIL + 82, "then the new records and the spec work → G3", 10, FAINT, anchor="end"))

# ------------------------------------------------------------------ lane D
dy = LD + 50
d1, hd1 = card(190, dy, 300, "Genesis — where the corpus is now", [
    "custody is declared: Scott, sole custodian (1, 0)",
    "the custodian may ratify unilaterally",
    "an import enters by the genesis route — one",
    "person reviews the temporary repository",
    "every checkpoint carries the debt ledger; at G1:",
    "2 ratified, +4 on queue C, +3 when written",
    "= a confirmation set of 9",
], CUS, CUS_BG)
add(d1)
d2, hd2 = card(524, dy, 300, "Bootstrap trigger — ADR-0029 §5", [
    "a drafted TLA+ bootstrap specification:",
    "Genesis · GenesisSatisfiesFloor",
    "Anchor · FloorPreserved",
    "RulesFloor · NoPromotionWithoutAllGrantSeats †",
    "Promotion · StaleVotesNeverCount",
    "BreakGlass · BreakGlassNeverChangesAuthority",
    "each invariant with a mutation that must fail;",
    "TLC at small constants advised, not required",
], CUS, CUS_BG)
add(d2)
d3, hd3 = card(858, dy, 292, "The ceremony", [
    "1  seat the key-holders under a declared",
    "    custody record — at least five humans",
    "2  assemble the genesis bundle: the manifest",
    "    incl. the confirmation-required set, the",
    "    spec digest marked checked or drafted-only,",
    "    and the genesis rules",
    "3  every key-holder signs the bundle digest —",
    "    this is issuance epoch 0",
], CUS, CUS_BG)
add(d3)
d4, hd4 = card(1184, dy, 300, "After bootstrap", [
    "custody moves from (1, 0) to a quorum",
    "first work: a confirmation promotion for every",
    "confirmation-required record, in dependency",
    "order, under ADR-0024, with author recusal —",
    "rejection means a superseding record, not an edit",
    "records without the marker are not re-reviewed",
    "an import now enters by promotion, and the",
    "genesis route is spent",
], CUS, CUS_BG)
add(d4)
for x1, x2 in ((490, 520), (824, 854), (1150, 1180)):
    add(arrow(x1, dy + 60, x2, dy + 60, CUS))

fy = dy + max(hd2, hd3) + 15
add(text(524, fy, "† the 09.16 spec-scope session argues this invariant belongs in Promotion — unrecorded (plan, Appendix B, R11).", 9.8, FAINT))
add(text(524, fy + 13, "At G1 the specification is not drafted; RulesFloorNV is a precursor to RulesFloor and Promotion.", 9.8, FAINT))
add(text(1184, fy, "the genesis bundle is the only artifact", 9.8, FAINT))
add(text(1184, fy + 13, "never promoted; genesis rules issue no erasure roster", 9.8, FAINT))

# custody ties into the repository lane
add(arrow(340, dy - 6, 340, LC + 254, CUS, dash="4 3", sw=1.3, marker="arwc"))
add(text(350, LD + 22, "the genesis route is a custody position, not a shortcut", 9.8, CUS))
add(f'<path d="M 1353 {dy - 6} V {LD + 16} H 1470 V {LC + 254}" fill="none" stroke="{CUS}" '
    f'stroke-width="1.3" stroke-dasharray="4 3" marker-end="url(#arwc)"/>')
add(text(1340, LD + 22, "bootstrap may be declared at any checkpoint", 9.8, CUS, anchor="end"))

# ------------------------------------------------------------------ notes
NY = LD + 245 + 44
add(text(44, NY - 14, "Solid = persistent · dashed = ephemeral or excluded · flags = signed checkpoint tags · circles on the rail = commits",
         10, FAINT))
add(box(44, NY, W - 88, 152, LANE_BR, "#fbfcfd", rx=10, sw=1))
cols = [
    ("Identity, and what git is for", [
        "SHA-256 over a file's bytes is the identity (G-C1). Git's hash is SHA-1",
        "over a header plus content, and GitHub hosts no SHA-256 repository —",
        "so SHA256SUMS stays the identity and the tags point at it.",
        "Git hashes are the transport check: tree equality for G1, per-path blob",
        "equality for I1.",
    ]),
    ("What keeps the route honest", [
        "A scrub removes; it never edits. Every removal is named by digest and",
        "reason, never by content.",
        "The transfer is a copy, so the temporary history cannot follow it.",
        "The temporary repository is deleted, and never pushed.",
        "CI enforces the never-enter list and the no-new-chat-URL rule.",
    ]),
    ("Two things that are easy to get wrong", [
        "A signed tag is the attestation. CI is evidence and sits outside the",
        "trusted base: a green pipeline ratifies nothing.",
        "Any history rewrite after g1 — authorship, trailers, link removal —",
        "breaks the signature. Those calls happen before g2, or not at all.",
        "At bootstrap the middle lane changes hands, not shape.",
    ]),
]
cx = 76
for title, lines in cols:
    add(text(cx, NY + 28, title, 12, INK, "bold"))
    yy = NY + 50
    for ln in lines:
        add(text(cx, yy, ln, 10.4, MUTED))
        yy += 15
    cx += 540

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<defs>'
       f'<marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker>'
       f'<marker id="arwc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
       f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{CUS}"/></marker>'
       f'</defs>\n' + "\n".join(out) + "\n</svg>\n")

open("/home/claude/out/diagrams/g1-to-bootstrap-2026.09.18.svg", "w").write(svg)
print("wrote", len(svg), "bytes; rail at", RAIL, "notes at", NY, "height", H)
