"""G3 — Theorem-to-premise DAG: the binding table ADR-0045 §3 owes, drawn in full, as an incidence matrix and as
three node-link chains (Contained, promotion, floor routing), with the proof column and the corrections ADR-0046 §5
made at Batch 25.

The table is read at build time from spec/theorem-premise-binding.md (relative to the repository root), so the
42-row table below is the file's text. The premise incidences are computed from its "Row premises" column (every
T-0045-n token, ranges expanded, BASE expanded to its five rows, and to T-0045-31 as well for a row whose "Checked in"
column names a proof module); parameter and gap premises, the verdict labels, the rung-conditional marks, the proof
status and the 2026.10.02 corrections are transcribed here and asserted against the parsed rows (parameter tokens
outside struck text, "proved in", the correction notes), so a change to the file fails the build instead of drawing
a stale matrix.
"""
import pathlib
import re

import lib
from lib import strip_external, Canvas, render_line, parse, wrap, text_width, fill, sonly, fs

ID, SLUG = "G3", "theorem-premise-dag"

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / "spec" / "theorem-premise-binding.md"

BASE = (1, 11, 28, 29, 30)
PROVER = 31    # T-0045-31: in BASE for a proved row, for the invariant (ADR-0046 §3; the table's BASE paragraph)


# ---------------------------------------------------------------------------------------------
# Parse the binding table

def _clean(s):
    s = re.sub(r"~~(.+?)~~", lambda m: "[[grey|struck: " + m.group(1).replace("`", "") + "]]", s)  # ~~x~~
    s = re.sub(r"\*\*(`[^`]+`)\*\*", r"\1", s)                     # **`x`** -> `x`
    s = re.sub(r"(?<![*\w])\*(?!\*)([^*]+?)(?<!\*)\*(?![*\w])", r"\1", s)   # *italic* -> plain
    return s


def load_table():
    rows = []
    for line in strip_external(SRC.read_text(encoding="utf-8")).splitlines():
        if not line.startswith("| ") or line.startswith("| Theorem"):
            continue
        cells = [_clean(c.strip()) for c in line.strip()[1:-1].split(" | ")]
        assert len(cells) == 7, line
        rows.append(cells)
    return rows


def t_rows(cell, proved=False):
    """Every T-0045-n named in a Row premises cell; ranges expanded; BASE expanded (with the prover if proved)."""
    out = (set(BASE) | ({PROVER} if proved else set())) if "BASE" in cell else set()
    for m in re.finditer(r"T-0045-(\d+)(?:\s+to\s+(\d+))?", cell):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        out.update(range(a, b + 1))
    return out


def explicit_t(cell):
    """T rows named explicitly (not only through BASE)."""
    return t_rows(cell.replace("BASE", ""))


# ---------------------------------------------------------------------------------------------
# Transcription: one entry per table row, in file order.
# (match, matrix label, group, verdict class, verdict label, parameter/gap premises, rung-conditional T rows)
# verdict classes: holds, holdsq (holds, qualified), void, notenf, owed, harness

META = [
    ("LeaseAuthorityMonotone", "`LeaseAuthorityMonotone`", "Lease", "holds", "holds", [], set()),
    ("NoActionUnderFencedEpoch", "`NoActionUnderFencedEpoch`", "Lease", "holds", "holds", [], set()),
    ("Rung0NeverContained", "`Rung0NeverContained`", "Lease", "holds", "holds", [], set()),
    ("RevokedStaysStopped", "`RevokedStaysStopped`", "Lease", "holds", "holds", [], set()),
    ("AdmitImpliesFloorPermit", "`AdmitImpliesFloorPermit`", "Floor", "holdsq", "holds, of the draft floor",
     ["fver", "fdraft"], set()),
    ("FloorErrorIsDeny", "`FloorErrorIsDeny`", "Floor", "holds", "holds", ["fver"], set()),
    ("BundleRefusalHonored", "`BundleRefusalHonored`", "Floor", "holds", "holds (dev bundle key)", ["bsig"], set()),
    ("BundleCannotWriteFloorInputs", "`BundleCannotWriteFloorInputs`", "Floor", "holds", "holds", [], set()),
    ("EnvelopeHolds", "`EnvelopeHolds`, `FloorNeverVacuous`", "Floor", "holdsq", "holds, of the draft floor",
     ["fver", "fdraft"], set()),
    ("NoWideningWithoutIssuance", "`NoWideningWithoutIssuance`", "Floor", "holds", "holds since 2026.10.01",
     ["rchk"], set()),
    ("NC1", "`NC1`, `NC2`", "NonComposition", "holds", "holds", ["r67"], set()),
    ("P1_Unanimity", "`P1_Unanimity`", "Rules", "holdsq", "holds at the dev rules", ["qall"], set()),
    ("P2_TwoSeatsCounted", "`P2_TwoSeatsCounted`", "Rules", "holds", "holds", ["ming"], set()),
    ("P3_AuthorNotCounted", "`P3_AuthorNotCounted`", "Rules", "holds", "holds", [], set()),
    ("P5_AnchorNotApprover", "`P5_AnchorNotApprover`", "Rules", "holds", "holds", [], set()),
    ("P7_BGNoAuthority", "`P7_BGNoAuthority`", "Rules", "holds", "holds", [], set()),
    ("P9_NoSoloGrant", "`P9_NoSoloGrant`", "Rules", "holds", "holds", ["qge2"], set()),
    ("FloorPreserved", "`FloorPreserved`", "Bootstrap", "holds", "holds", [], set()),
    ("BreakGlassNeverChangesAuthority", "`BreakGlassNeverChangesAuthority`", "Bootstrap", "holds", "holds", [],
     set()),
    ("ContainedMeansConfined", "`ContainedMeansConfined`", "Confinement", "void", "void", ["c1", "indep"],
     {16, 17, 18, 19}),
    ("NoSilentDowngrade", "`NoSilentDowngrade`", "Confinement", "holdsq", "holds trivially (rung 0)", [],
     {17, 18, 19}),
    ("ContestedStopped", "`ContestedStopped`", "Confinement", "void", "void", ["c2"], {16, 18}),
    ("FreshAppraisal", "`FreshAppraisal`", "Confinement", "void", "void", ["c1"], set()),
    ("OnlyThinkersAuthor", "`OnlyThinkersAuthor`", "Seats", "holds", "holds", [], set()),
    ("OneSeatPerPrincipal", "`OneSeatPerPrincipal`", "Seats", "holds", "holds", [], set()),
    ("DenyByAnyOf", "`DenyByAnyOf`", "Observers", "holdsq", "holds of the tally", ["obs"], set()),
    ("ReachIsBounded", "`ReachIsBounded`", "Observers", "notenf", "declared, not enforced", [], set()),
    ("NoAdmitWithoutLiveObserver", "`NoAdmitWithoutLiveObserver`", "Coupling", "holdsq", "holds, modulo the gap",
     ["coup", "wm"], set()),
    ("UnreadBounded", "`UnreadBounded`", "Coupling", "holdsq", "holds, modulo the gap", ["coup", "wm"], set()),
    ("CorrelatorNeverGates", "`CorrelatorNeverGates`", "Coupling", "holds", "holds", ["corr"], set()),
    ("UnreadEffectsBounded", "`UnreadEffectsBounded`", "RunCoupling", "holdsq", "holds, modulo the gap",
     ["effc", "coup", "wm"], set()),
    ("ConsultNeverCoupled", "`ConsultNeverCoupled`", "RunCoupling", "holds", "holds", ["root"], set()),
    ("SealCountsEffects", "`SealCountsEffects`", "RunCoupling", "holds", "holds", ["effc"], set()),
    ("RoundBoundCountsAll", "`RoundBoundCountsAll`", "RunCoupling", "holds", "holds", [], set()),
    ("NoEffectWithoutLiveObserver", "`NoEffectWithoutLiveObserver`", "RunCoupling", "holdsq",
     "holds, modulo the gap", ["coup", "wm"], set()),
    ("OnlyThinkersActuate", "`OnlyThinkersActuate`, `ObserversConsult…`", "RunSeats", "holds", "holds", [], set()),
    ("NoNameCrossesDomains", "`NoNameCrossesDomains`", "RunSeats", "holds", "holds", [], set()),
    ("Effect exclusivity", "Effect exclusivity (a claim)", "Unmodelled", "void", "void", ["c1", "runc"],
     {16, 17, 18, 19, 20, 21, 22}),
    ("PromotionMeetsIssuedQuorum", "`PromotionMeetsIssuedQuorum`", "Unmodelled", "owed",
     "module unwritten; evidence asserted", ["a22", "g18"], set()),
    ("OneValuePerBallot", "`OneValuePerBallot`, agreement", "Unmodelled", "holdsq", "holds of the simulation", [],
     set()),
    ("The floor gates", "The floor gates", "Unmodelled", "harness", "pass (2026.10.01)", ["rchk"], set()),
    ("Trace validation", "Trace validation `TraceMatches`", "Unmodelled", "harness", "21 traces match", ["orc"],
     set()),
]

GROUPS = {
    "Lease": "`Lease.tla`, `Lease_A1.tla` · ADR-0031",
    "Floor": "`FloorComposition.tla`, `FloorRouting.tla` · ADR-0030",
    "NonComposition": "`NonComposition.tla` · ADR-0013",
    "Rules": "`RulesFloorNV_rev5.tla` · the rules floor, ADR-0026, ADR-0024",
    "Bootstrap": "`Anchor.tla`, `BreakGlass.tla` · the bootstrap pair, ADR-0029 §5",
    "Confinement": "`Confinement.tla` · ADR-0034",
    "Seats": "`Seats.tla` · ADR-0037",
    "Observers": "`Observers.tla` · ADR-0038",
    "Coupling": "`Coupling.tla` · ADR-0039",
    "RunCoupling": "`RunCoupling.tla` · ADR-0041, ADR-0042",
    "RunSeats": "`RunSeats.tla` · ADR-0040, ADR-0043",
    "Unmodelled": "No TLA+ module: a claim, an owed module, a simulation, the gates, the trace harness",
}

VERDICT = {
    # class: (accent, dash, legend)
    "holds":   ("green", None, "holds at the reference"),
    "holdsq":  ("green", "5 3", "holds, with the qualifier the table states"),
    "void":    ("red", None, "void at the reference"),
    "notenf":  ("red", "5 3", "declared, not enforced"),
    "owed":    ("red", "5 3", "owed: module unwritten, evidence an operator's assertion"),
    "harness": ("teal", None, "a harness or gate run, not a theorem"),
}

# Premise columns. Trusted-base rows: Annex A group, short name, class at the reference (Annex B).
# status at the reference -> accent
ST = {
    "root":   ("blue", "trust root"),
    "rootd":  ("blue", "trust root, degenerate"),
    "deleg":  ("green", "delegated"),
    "excl":   ("red", "excluded"),
    "none":   ("red", "no instance (—)"),
    "noinst": ("grey", "not yet instantiated"),
}
TROWS = {
    1: ("replicas, crash-fault", "root"), 2: ("signature primitive", "root"), 3: ("Cedar engine", "root"),
    4: ("monotonic clock", "deleg"), 5: ("round-topic transport", "deleg"), 6: ("bundle-tier engines", "deleg"),
    7: ("archive, plaintext store", "deleg"), 8: ("anchor key store", "rootd"), 9: ("anchor key-holders", "rootd"),
    10: ("resident genesis rules", "root"), 11: ("corpus and custodian", "root"),
    12: ("break-glass approvers", "root"), 13: ("gate runner, evidence", "excl"),
    14: ("proof checker (B24)", "root"), 15: ("lineage gate tools", "noinst"),
    16: ("CPU root of trust", "none"), 17: ("independent verifier", "none"), 18: ("firmware, hypervisor", "none"),
    19: ("host operator", "none"), 20: ("image, profile P1–P7", "none"), 21: ("inference attestation", "none"),
    22: ("the host at rung 0", "excl"), 23: ("native tool (Invoke)", "excl"), 24: ("Run tool channel", "excl"),
    25: ("tool host", "root"), 26: ("decoding conformance", "none"), 27: ("bundle signer (B23)", "rootd"),
    28: ("code refines spec", "root"), 29: ("TLC, its constants", "root"), 30: ("build toolchain", "root"),
    31: ("TLA+ Proof System (B25)", "root"),
}
TGROUPS = [
    ("Mechanism constants (all rungs)", list(range(1, 13))),
    ("Build-gate toolchain", [13, 14, 15]),
    ("Verified object's evidence", [28, 29, 30, 31]),
    ("Confinement axis", list(range(16, 23))),
    ("Tools and the cell", [23, 24, 25, 27, 26]),
]
# Parameter and gap premises: code -> (column label, written as, falsified by / note, accent at the reference)
PARAMS = [
    ("fver", "floor verified", "floor verified", "D-0030-1 drops the proven status", "green"),
    ("fdraft", "floor text DRAFT", "the floor text is DRAFT, so the envelope it permits is the draft's",
     "qualifier: no floor is ratified (G8 §8)", "violet"),
    ("rchk", "routing checked", "routing checked (ADR-0030 §5 A1)", "D-0030-2: gates run without the checker",
     "green"),
    ("bsig", "bundle signed", "bundle signed", "D-0044-1: the revision is a file name", "green"),
    ("r67", "rules floor R6, R7", "rules floor R6, R7 in force", "dropping either entry", "green"),
    ("qall", "quorum = \"all\"", "`quorum = \"all\"`", "D-0024-1 voids it; R9 keeps D-0024-2 out", "green"),
    ("ming", "minGrant ≥ 2", "`minGrant ≥ 2`", "dropping R2", "green"),
    ("qge2", "threshold ≥ 2", "`quorum ≥ 2` when a threshold",
     "dropping R9 with R1 relaxed; the proof's hypothesis is R2 and (R1 or R9)", "green"),
    ("c1", "confinement ≥ 1", "confinement ≥ 1", "D-0034-1, -2 lower it; D-0034-4 is rung 0", "red"),
    ("c2", "confinement ≥ 2", "confinement ≥ 2", "rungs 0 and 1 cannot produce Contested", "red"),
    ("obs", "Observer per cell", "an Observer per cell", "D-0037-1: no Observer; D-0038-1: the shared group only",
     "green"),
    ("coup", "coupling on", "coupling on", "D-0039-1", "green"),
    ("corr", "correlator exists", "a correlator exists", "D-0038-2", "green"),
    ("effc", "effects counted", "effects counted", "D-0042-1", "green"),
    ("root", "Run root pinned", "the Run root is pinned (ADR-0040 §3)", "a live Consult would be egress", "green"),
    ("a22", "A2.2, A2.3 constants", "A2.2 and A2.3 as tally constants", "A2.2 not built at the reference", "red"),
]
GAPS = [
    ("wm", "gap: honest watermark", "gap: the watermark is honest", "ADR-0039 §5: collusion uncovered; A13",
     "red"),
    ("indep", "independence criterion", "the independence criterion in force", "ADR-0035, Proposed", "amber"),
    ("runc", "Run's confinement", "Run's confinement delivered", "ADR-0042 §6, Proposed", "amber"),
    ("g18", "gap: independence table", "gap: no independence table", "G18", "red"),
    ("orc", "three trace oracles", "the three oracles: issuance validity, approval signatures, the parameter digest",
     "taken from the trace, not computed", "blue"),
]
PCODE = {p[0]: p for p in PARAMS + GAPS}

# How each parameter, gap or input premise is written in the file (searched in the "Row premises" and "Parameter and
# gap premises" cells with struck text removed). Every token found must be transcribed in META, and vice versa.
TOKENS = {
    "fver": r"floor verified", "fdraft": r"the floor text is DRAFT", "rchk": r"routing checked",
    "bsig": r"bundle signed", "r67": r"R6, R7 in force", "qall": r'quorum = "all"', "ming": r"minGrant ≥ 2",
    "qge2": r"quorum ≥ 2", "c1": r"confinement ≥ 1", "c2": r"confinement ≥ 2", "obs": r"an Observer per cell",
    "coup": r"coupling on", "corr": r"a correlator exists", "effc": r"effects counted",
    "root": r"the Run root is pinned", "a22": r"A2\.2 and A2\.3 as tally constants",
    "wm": r"watermark is honest|honest watermark", "indep": r"independence criterion in force",
    "runc": r"Run's confinement delivered", "g18": r"no independence table", "orc": r"the three oracles",
}
# Premises the table struck on 2026.10.02 (ADR-0046 §5): drawn in the key, cited by no row.
STRUCK = [("K < R", "struck from `UnreadBounded` and `UnreadEffectsBounded` (ADR-0046 §5): both are proved for "
           "every K and R; ADR-0039 §1 keeps it so that condition 3 can refuse, a non-vacuity claim TLC shows")]

# The 2026.10.02 revision (ADR-0046 §5), transcribed per row: (number, what changed). Rows whose cells carry the
# file's correction notes ("2026.10.02", "the proof's hypothesis") must be exactly the rows marked here, except
# EnvelopeHolds, whose breakers the revision wrote out without a note.
CORR = {
    "AdmitImpliesFloorPermit": ("2", "also breaks under `M_ERR`"),
    "FloorErrorIsDeny": ("2", "also breaks under `M_OVERRIDE`"),
    "BundleRefusalHonored": ("2", "also breaks under `M_OVERRIDE`"),
    "EnvelopeHolds": ("·", "breakers named: `M_WRITE`, `M_ERR`, `M_OVERRIDE`; `M_GATE`"),
    "P9_NoSoloGrant": ("·", "rests on R2 and (R1 or R9)"),
    "ContainedMeansConfined": ("4", "`SameGuest` at grant not load-bearing"),
    "UnreadBounded": ("5", "`K < R` struck"),
    "UnreadEffectsBounded": ("5", "`K < R` struck"),
    "SealCountsEffects": ("3", "`M_EMITSEQ`, not `M_ROUNDS`"),
    "OnlyThinkersActuate": ("1", "`M_OBSEMIT` breaks neither; `M_DOMAIN` breaks `ObserversConsultAndReport`"),
}
UNNOTED = {"EnvelopeHolds"}


def _unstruck(s):
    return re.sub(r"\[\[grey\|struck: .*?\]\]", "", s)


def model():
    table = load_table()
    assert len(table) == len(META) == 42, (len(table), len(META))
    out = []
    for cells, meta in zip(table, META):
        match, label, group, vcls, vlab, params, cond = meta
        assert match in cells[0], (match, cells[0])
        proved = "proved in" in cells[1]
        assert proved == (group != "Unmodelled"), (match, "proof column", cells[1])
        prem = _unstruck(cells[4] + " ; " + cells[5])
        found = {k for k, t in TOKENS.items() if re.search(t, prem)}
        assert found == set(params), (match, "parameter premises", sorted(found), sorted(params))
        noted = any("2026.10.02" in x or "proof's hypothesis" in x for x in cells)
        assert noted == (match in CORR and match not in UNNOTED), (match, "correction note", noted)
        ts = t_rows(cells[4], proved)
        assert cond <= ts, (match, cond, ts)
        out.append(dict(cells=cells, label=label, group=group, vcls=vcls, vlab=vlab, params=params, cond=cond,
                        ts=ts, explicit=explicit_t(cells[4]), base="BASE" in cells[4], proved=proved,
                        corr=CORR.get(match), match=match))
    assert sum(r["proved"] for r in out) == 37, "proved rows"
    return out


# ---------------------------------------------------------------------------------------------
# Drawing helpers local to this module

def vtext(c, x, y, s, size=13, color="ink", bold=False):
    """Text rotated -90 degrees, reading upward from (x, y). Not entered in the overlap check (it is rotated)."""
    ln = wrap(s, 10_000, size, bold)[0]
    svg = render_line(x, y, ln, size, color, "start", bold)
    lib.TEXT_BOXES.pop()
    c.add(f'<g transform="rotate(-90 {x:.1f} {y:.1f})">{svg}</g>')


def dot(c, x, y, acc, kind):
    if kind == "solid":
        c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" {fs(acc, acc)} stroke-width="1.5"/>')
    elif kind == "hollow":
        c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" {fs("bg", acc)} stroke-width="2.4"/>')
    elif kind == "base":
        c.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" {fill("faint")}/>')
    elif kind == "square":
        c.add(f'<rect x="{x - 7:.1f}" y="{y - 7:.1f}" width="14" height="14" rx="2" {fs(acc, acc)} '
              f'stroke-width="1.5"/>')


def vpill(c, x, y, row, size=12.5, anchor="start"):
    acc, dash, _ = VERDICT[row["vcls"]]
    solid = row["vcls"] in ("holds", "void", "harness")
    return c.pill(x, y, row["vlab"], acc, size, dash=dash, solid=solid, anchor=anchor)


# ---------------------------------------------------------------------------------------------

def build():
    rows = model()
    c = Canvas(ID, "Theorem to premise: what every checked or proved property rests on, and what is void at the "
               "reference",
               "`spec/theorem-premise-binding.md` (2026.09.30, revised 2026.10.01 and 2026.10.02 with ADR-0046, "
               "**DRAFT**, revised with the records it binds) is the table ADR-0045 §3 owes and ADR-0023 §2 assumes: "
               "one row per checked property, naming the trusted-base rows (ADR-0045 Annex A), the degeneracy "
               "parameters (ADR-0023 §6a) and the declared gaps it rests on. A property holds for a deployment when "
               "every row it names is declared delegated or trust root, every parameter holds and no gap premise is "
               "false; otherwise it is void. Since Batch 25 the table names the proof module of 37 rows and carries "
               "five corrections the proofs found. Drawn three ways: the key chains as a DAG, the full incidence "
               "matrix, and the table itself, all 42 rows.",
               3600,
               "spec/theorem-premise-binding.md (all 42 rows, read at build time); ADR-0045 §3, §5, Annex A, Annex B "
               "(with the B23, B24 and B25 dependent entries); ADR-0046 §1–§5 (Batch 25); "
               "spec/premise-corrections-results-2026.10.02.txt; ADR-0023 §2, §6a; ADR-0033 A5, A6; ADR-0030 §5 A1; "
               "G8 §2.1–§2.3, §2.6, §2.9, §3, §8; G7 §3; spec/Mechanism-trace-results-2026.10.01.txt")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ---------------------------------------------------------------- intro band
    gap = 24
    w4 = (W - 3 * gap) / 4
    intro = [
        ("What the table is", [
            "One row per checked property: what it **assumed**. A property is **void** for a deployment when a row it "
            "names is excluded, undeclared (ADR-0045 §3 rule 1) or refused, or a parameter or gap premise is false.",
            "The last column computes ADR-0023 §2's inventory for the reference against ADR-0045 Annex B.",
            "Since B25 the **Checked in** column names the proof module beside the base module for 37 rows "
            "(ADR-0046 §5).",
        ], "blue"),
        ("What it is not", [
            "The file's words: \"**A proof by itself.** Every property here was checked by TLC at small constants, "
            "or restated as a test, by the same hands that wrote the records, and the invariants of thirty-seven rows "
            "are also proved\" by the proof module the **Checked in** column cites, by the same hands.",
            "A row says what a check or a proof assumed; it strengthens neither. **Proved** is of the module and under "
            "named hypotheses (ADR-0046 §1); neither method claims anything of the running reference (T-0045-28).",
        ], "red"),
        ("BASE: premises every row shares", [
            "T-0045-1 replicas apply the ordered log as crash-fault machines; T-0045-11 the records are the ratified "
            "records; T-0045-29 TLC at the constants run; T-0045-30 the build toolchain.",
            "**T-0045-28**: the running code refines the specification. **No refinement exists**, so for a running "
            "deployment every property is conditional on this row.",
            "**A row with a proof module** (B25): the invariant rests on **T-0045-31**, the prover, in place of "
            "T-0045-29, for every constant the proof's assumptions admit; the mutations and witnesses rest on "
            "T-0045-29 as before.",
        ], "grey"),
        ("Status of the table and its records", [
            "ADR-0045 is **Accepted (genesis)**, confirmation required C2, C4 (Batch 22, R6 added the table). "
            "**ADR-0046** revised it in place (Batch 25, 2026.10.02; C2, C4): the proof column and five corrections.",
            "The table itself is a **DRAFT**, revised with the records it binds; its versioning belongs to the "
            "archetype-evolution record, still unwritten (G8 item 7). `Never…` witnesses are not theorems and are "
            "omitted.",
        ], "violet"),
    ]
    hh = max(c.card(0, 0, w4, t, b, accent=a, draw=False, size=14.5) for t, b, a in intro)
    for i, (t, b, a) in enumerate(intro):
        c.card(X0 + i * (w4 + gap), y, w4, t, b, accent=a, h=hh, size=14.5)
    c.status(X0 + 3 * (w4 + gap) + w4 - 16, y + 16, "accepted", "C2, C4", anchor="end")
    y += hh + 54

    # ---------------------------------------------------------------- the B25 band: proofs and corrections
    y += c.heading(X0, y, "Batch 25 (ADR-0046 §4, §5): the proof column, and five corrections the proofs found",
                   size=22)
    y += c.para(X0, y, W, "Each proof module takes as hypothesis only the mutations that break each invariant, written "
                "independently of the table; where the two disagreed TLC agreed with the proof, and the table was "
                "corrected (G8 §3, result 2). The corrections' TLC rows are `spec/premise-corrections-results-"
                "2026.10.02.txt` (`2669499135d2ea42`), every outcome as predicted.", 15, "muted") + 16
    b25 = [
        ("The proof column", [
            "**37 of 42 rows** name a proof module: thirteen modules, **2,417 obligations**, each invariant proved "
            "as `Spec => []P` under the module's named assumptions and the absence of the mutations that break it.",
            "**No proof**: effect exclusivity (a claim), `PromotionMeetsIssuedQuorum` (module unwritten), the Paxos "
            "simulation, the floor gates, and trace validation (`Mechanism.tla` is a trace replay; its target is the "
            "refinement, T-0045-28).",
            "The last column is **unchanged**: a proof of a module adds nothing at the reference (G8 §2.3).",
        ], "teal"),
        ("1 · RunSeats", [
            "`M_OBSEMIT` breaks **none** of the three invariants: it narrows an observer's bound, and they are upper "
            "bounds.",
            "`ObserversConsultAndReport` breaks under `M_DOMAIN` as well as `M_KIND`.",
            "TLC: `rs-obsemit-safe` holds; `rs-mdomain-observer` is a counterexample.",
        ], "blue"),
        ("2 · FloorComposition", [
            "`M_OVERRIDE` admits on a bundle allow whatever the floor said: it also breaks `FloorErrorIsDeny` and "
            "`BundleRefusalHonored`.",
            "`M_ERR` admits on an engine error: it also breaks `AdmitImpliesFloorPermit`.",
            "`EnvelopeHolds` is written out: `M_WRITE`, `M_ERR`, `M_OVERRIDE`. Three new TLC rows, each a "
            "counterexample.",
        ], "blue"),
        ("3 · SealCountsEffects", [
            "Breaks under `M_EMITSEQ`, **not** `M_ROUNDS`, which never touches a seal.",
            "A transcription error: the results file's rows `rc-emitseq-seal` (counterexample) and `rc-rounds-seal` "
            "(holds) already said so.",
        ], "blue"),
        ("4 · ContainedMeansConfined", [
            "The five breakers stand. The lease's binding to its guest is enforced by `Act`'s generation check, which "
            "`M_UNBOUND` removes, and **not by `SameGuest` at grant**, which the proof never uses.",
            "A statement about the proof; no TLC row.",
        ], "blue"),
        ("5 · K < R struck as a premise", [
            "`UnreadBounded` and `UnreadEffectsBounded` are proved for every K and R; neither rests on `K < R`. TLC: "
            "both hold at K = 3 (and 5), R = 2.",
            "ADR-0039 §1 keeps `K < R` so that condition 3 can refuse at all: a non-vacuity claim, shown by the "
            "control rows (a backlog refusal is reachable only when K < R).",
        ], "blue"),
        ("Also made exact: P9_NoSoloGrant", [
            "Its hypothesis is **R2 and (R1 or R9)**: under unanimity R2 makes the counted approvers at least two; "
            "under a threshold R9 does; R2 is needed either way.",
            "The table read \"drop R9 (binds only with R1 relaxed)\"; it now adds \"or drop R2\".",
        ], "blue"),
    ]
    bg = 20
    bw = (W - (len(b25) - 1) * bg) / len(b25)
    bh = max(c.card(0, 0, bw, t, b, accent=a, draw=False, size=14) for t, b, a in b25)
    for i, (t, b, a) in enumerate(b25):
        c.card(X0 + i * (bw + bg), y, bw, t, b, accent=a, h=bh, size=14)
    y += bh + 54

    # ---------------------------------------------------------------- part 1: the key chains as a DAG
    y += c.heading(X0, y, "1 · Three chains, drawn as a DAG: each property points at the premises it rests on "
                          "(BASE omitted)", size=22)
    y += c.para(X0, y, W, "Left: premise nodes, coloured by their class at the reference (ADR-0045 Annex B). Right: "
                "properties, coloured by the table's last column; a teal **proved** pill marks a property whose "
                "invariant is proved in a proof module (ADR-0046), which changes no verdict. An edge runs from a "
                "property to a premise it names; a dashed edge is a premise that applies only at one declared rung. "
                "Edges take the colour of the property, so a red edge ends at what makes its property void.",
                15, "muted") + 18
    panels = [
        ("Contained: confinement and effect exclusivity", "teal",
         ["ContainedMeansConfined", "NoSilentDowngrade", "ContestedStopped", "FreshAppraisal", "Effect exclusivity"],
         [("T", 16), ("T", 17), ("T", 18), ("T", 19), ("T", 20), ("T", 21), ("T", 22), ("T", 23), ("T", 24),
          ("T", 25), ("P", "c1"), ("P", "c2"), ("P", "indep"), ("P", "runc")],
         "Every property premised on confinement is void: the reference issues rung 0 only, T-0045-16 to 21 have no "
         "instance, T-0045-22 to 24 are excluded rows. `NoSilentDowngrade` holds trivially because rung 0 is the "
         "declared rung. `Contained` **is empty** (G8 §8). The four `Confinement` invariants are proved for every "
         "rung at once (ADR-0034 B25), which adds nothing at the reference (G8 §2.3)."),
        ("Promotion and the rules floor", "blue",
         ["PromotionMeetsIssuedQuorum", "P1_Unanimity", "P2_TwoSeatsCounted", "P5_AnchorNotApprover",
          "P9_NoSoloGrant", "FloorPreserved"],
         [("T", 2), ("T", 8), ("T", 9), ("T", 10), ("T", 13), ("T", 15), ("P", "qall"), ("P", "ming"),
          ("P", "qge2"), ("P", "a22"), ("P", "g18")],
         "The rules floor and the anchor hold, at the dev rules, which are not genesis rules (G6); their properties "
         "are proved (B25), each under the entry it rests on. The promotion property has no module: gate evidence "
         "is an operator's assertion (T-0045-13 **excluded**), A2.2 is not built, and there is no independence "
         "table (G18)."),
        ("Floor composition and routing", "blue",
         ["AdmitImpliesFloorPermit", "FloorErrorIsDeny", "BundleRefusalHonored", "EnvelopeHolds",
          "NoWideningWithoutIssuance", "The floor gates"],
         [("T", 3), ("T", 6), ("T", 14), ("T", 27), ("P", "fver"), ("P", "fdraft"), ("P", "rchk"), ("P", "bsig")],
         "Since 2026.10.01 the routing theorem and the gate verdicts rest on checked proofs (T-0045-14, a trust root "
         "since Batch 24), where before they were the solver's assertion. The floor holds **of the draft floor**: "
         "its text is not ratified. `FloorComposition` and `FloorRouting` are proved (B25): proofs of the "
         "composition model, distinct from the gates' checked proofs, which concern the floor's Cedar text "
         "(G8 §2.2)."),
    ]
    pgap = 40
    pw = (W - 2 * pgap) / 3
    byname = {m[0]: r for m, r in zip(META, rows)}

    def prem_info(kind, k):
        if kind == "T":
            name, st = TROWS[k]
            acc, stl = ST[st]
            return f"**T-0045-{k}**", name, acc, stl, st in ("none", "excl")
        p = PCODE[k]
        stl = {"green": "holds at the reference", "red": "false at the reference" if k in ("c1", "c2", "a22")
               else "declared open", "amber": "Proposed record", "violet": "draft", "blue": "asserted input"}[p[4]]
        note = p[3] if p[4] in ("amber", "violet", "blue") or k in ("wm", "g18") else f"[falsified by {p[3]}]"
        return f"**{p[1]}**", note, p[4], stl, p[4] in ("red", "amber")

    def edges_of(r):
        out = []
        for t in sorted(r["explicit"]):
            out.append((("T", t), t in r["cond"]))
        for p in r["params"]:
            out.append((("P", p), False))
        return out

    def prem_h_of(kind, k, pnw):
        ty, nm, pacc, stl, bad = prem_info(kind, k)
        return 14 + len(wrap(ty + "  " + nm, pnw - 24, 13.5)) * 19 + 26

    # measure panels
    ph_max = 0
    layouts = []
    for title, acc, thms, prems, note in panels:
        pnw, tnw = 350, 330
        bh_p = [prem_h_of(kind, k, pnw) for kind, k in prems]
        n_p = len(prems)
        prem_h = sum(bh_p) + (n_p - 1) * 12
        trs = [byname[t] for t in thms]
        th_h = []
        for r in trs:
            hh_ = 16 + len(wrap(r["label"], tnw - 24, 14.5, True)) * 20 + 8 + 22 + 12
            th_h.append(hh_)
        thm_total = sum(th_h) + (len(trs) - 1) * 24
        body = max(prem_h, thm_total)
        note_h = c.para(0, 0, pw - 48, note, 14, draw=False)
        layouts.append((pnw, tnw, bh_p, prem_h, trs, th_h, thm_total, body, note_h))
        ph_max = max(ph_max, 70 + body + 30 + note_h + 26)

    for pi, ((title, acc, thms, prems, note), lay) in enumerate(zip(panels, layouts)):
        pnw, tnw, bh_p, prem_h, trs, th_h, thm_total, body, note_h = lay
        px = X0 + pi * (pw + pgap)
        c.region(px, y, pw, ph_max, title, acc, dash=None, sw=2, size=16)
        top = y + 50
        # premises (left)
        ppos = {}
        py0 = top + (body - prem_h) / 2
        lx = px + 24
        yy = py0
        for i, (kind, k) in enumerate(prems):
            ty, nm, pacc, stl, bad = prem_info(kind, k)
            bh = bh_p[i]
            c.rect(lx, yy, pnw, bh, pacc, tint=True, dash="5 3" if bad else None, rx=7, sw=1.6)
            ly = yy + 8
            for ln in wrap(ty + "  " + nm, pnw - 24, 13.5):
                c.add(render_line(lx + 12, ly + 14, ln, 13.5, "ink"))
                ly += 19
            c.text(lx + 12, ly + 15, stl, 12.5, pacc, bold=True)
            ppos[(kind, k)] = (lx + pnw, yy, bh)
            yy += bh + 12
        # theorems (right)
        rx = px + pw - 24 - tnw
        tpos = []
        ty0 = top + (body - thm_total) / 2
        yy = ty0
        for r, h in zip(trs, th_h):
            vacc, vdash, _ = VERDICT[r["vcls"]]
            c.rect(rx, yy, tnw, h, vacc, tint=True, dash=vdash, rx=7, sw=2)
            ly = yy + 16
            for ln in wrap(r["label"], tnw - 24, 14.5, True):
                c.add(render_line(rx + 12, ly + 13, ln, 14.5, "ink", bold=True))
                ly += 20
            pw_ = vpill(c, rx + 12, ly + 6, r, 12)
            if r["proved"]:
                c.pill(rx + 12 + pw_ + 8, ly + 6, "proved", "teal", 12, solid=True)
            tpos.append((r, rx, yy, h))
            yy += h + 24
        # edges: from the theorem's left edge to the premise's right edge
        for r, tx, tyy, th in tpos:
            es = [e for e in edges_of(r) if e[0] in ppos]
            es.sort(key=lambda e: ppos[e[0]][1])
            vacc = VERDICT[r["vcls"]][0]
            n = len(es)
            for j, (key, cond) in enumerate(es):
                sx, sy = tx, tyy + th * (j + 1) / (n + 1)
                pxr, pyy, ph_ = ppos[key]
                # spread arrival points across the premise's right edge by source order
                ex, ey = pxr + 2, pyy + ph_ / 2
                mx = (sx + ex) / 2
                d = ' stroke-dasharray="6 4"' if cond else ""
                c.add(f'<path d="M {sx:.1f} {sy:.1f} C {mx:.1f} {sy:.1f}, {mx:.1f} {ey:.1f}, {ex + 10:.1f} {ey:.1f}" '
                      f'{sonly(vacc)} stroke-width="1.7" stroke-opacity="0.85"{d} marker-end="url(#arw-{vacc})"/>')
        c.para(px + 24, y + 70 + body + 24, pw - 48, note, 14, "ink")
    y += ph_max + 30
    c.legend(X0, y, [
        ("box", "blue", "premise: trust root at the reference"),
        ("box", "green", "premise: delegated, or a parameter that holds"),
        ("box", "red", "premise: excluded, no instance, or false", "5 3"),
        ("box", "amber", "premise: a Proposed record", "5 3"),
        ("box", "violet", "qualifier: draft text"),
        ("line", "green", "property holds"),
        ("line", "red", "property void"),
        ("line", "grey", "premise only at one declared rung", "6 4"),
        ("box", "teal", "proved: a proof module proves the invariant (ADR-0046)"),
    ], title="Key")
    y += 64

    # ---------------------------------------------------------------- part 2: the incidence matrix
    y += c.heading(X0, y, "2 · The full incidence matrix: 42 rows × 31 trusted-base rows, 16 parameters, "
                          "5 gaps and inputs, with the proof column", size=22)
    y += c.para(X0, y, W, "Rows in the table's order, grouped by module. A column's chip and every dot in it carry the "
                "premise's class at the reference, so a void row shows the red dot that voids it. A large dot is a "
                "premise the row names; a ring is one it names only at a declared rung; a small grey dot is a BASE "
                "premise; a square is a parameter, gap or input premise. Uncited rows (T-0045-7, T-0045-26) are drawn "
                "so their absence shows. T-0045-31, the prover, is a BASE premise of the 37 proved rows only, for "
                "the invariant; T-0045-29 stays in every row's BASE for the mutations and witnesses. The struck "
                "`K < R` has no column.", 15, "muted") + 14

    LBL, VW, PFW, CW, GG = 420, 270, 190, 46, 18
    cols = []   # (x, kind, key)
    cx = X0 + LBL + VW + PFW
    col_groups = []
    for gname, ids in TGROUPS:
        gx0 = cx
        for t in ids:
            cols.append((cx + CW / 2, "T", t))
            cx += CW
        col_groups.append((gname, gx0, cx, "grey"))
        cx += GG
    gx0 = cx
    for p in PARAMS:
        cols.append((cx + CW / 2, "P", p[0]))
        cx += CW
    col_groups.append(("Parameter premises (ADR-0023 §6a)", gx0, cx, "grey"))
    cx += GG
    gx0 = cx
    for p in GAPS:
        cols.append((cx + CW / 2, "P", p[0]))
        cx += CW
    col_groups.append(("Gaps, Proposed premises, inputs", gx0, cx, "grey"))
    mx1 = cx
    assert mx1 <= X1 + 1, mx1

    # group bands above the column labels
    for gname, a, b, acc in col_groups:
        lines = wrap(gname, b - a - 12, 13, True)
        for i, ln in enumerate(lines):
            c.add(render_line((a + b) / 2, y + 16 + i * 17, ln, 13, "muted", "middle", True))
        c.line(a + 3, y + 22 + (len(lines) - 1) * 17 + 6, b - 3, y + 22 + (len(lines) - 1) * 17 + 6, "faint", 1.4)
    y += 22 + 17 + 14
    LH = 250
    base_y = y + LH
    for x, kind, key in cols:
        if kind == "T":
            name, st = TROWS[key]
            acc = ST[st][0]
            vtext(c, x + 5, base_y - 6, f"T-{key} · {name}", 13, "ink")
        else:
            p = PCODE[key]
            acc = p[4]
            vtext(c, x + 5, base_y - 6, p[1], 13, "ink")
        c.add(f'<rect x="{x - CW / 2 + 5:.1f}" y="{base_y + 4:.1f}" width="{CW - 10:.1f}" height="10" rx="3" '
              f'{fs(acc, acc)} stroke-width="1"/>')
    c.text(X0, base_y - 8, "Checked property (table order)", 14, "faint", bold=True)
    c.text(X0 + LBL, base_y - 8, "At the reference", 14, "faint", bold=True)
    c.text(X0 + LBL + VW, base_y - 8, "Proof (B25)", 14, "faint", bold=True)
    y = base_y + 24

    RH = 32
    mtop = y
    cur = None
    zebra = 0
    for r in rows:
        if r["group"] != cur:
            cur = r["group"]
            c.add(f'<rect x="{X0}" y="{y:.1f}" width="{mx1 - X0:.1f}" height="28" {fs("panel", "line")} '
                  f'stroke-width="1"/>')
            c.text(X0 + 10, y + 19, GROUPS[cur], 13.5, "muted", bold=True)
            y += 28
        if zebra % 2:
            c.add(f'<rect x="{X0}" y="{y:.1f}" width="{mx1 - X0:.1f}" height="{RH}" {fill("zebra")}/>')
        zebra += 1
        cy = y + RH / 2
        vacc = VERDICT[r["vcls"]][0]
        c.add(f'<rect x="{X0}" y="{y:.1f}" width="5" height="{RH}" {fill(vacc)}/>')
        c.text(X0 + 14, cy + 5, r["label"], 14)
        vpill(c, X0 + LBL, y + 5, r, 12)
        if r["proved"]:
            px_ = X0 + LBL + VW
            px_ += c.pill(px_, y + 5, "proved", "teal", 12, solid=True) + 6
            if r["corr"]:
                c.pill(px_, y + 5, f"corrected {r['corr'][0]}" if r["corr"][0] != "·" else "corrected", "blue", 12)
        else:
            c.text(X0 + LBL + VW, cy + 5, "no proof module", 13, "faint")
        for x, kind, key in cols:
            if kind == "T":
                acc = ST[TROWS[key][1]][0]
                if key in r["cond"]:
                    dot(c, x, cy, acc, "hollow")
                elif key in r["explicit"]:
                    dot(c, x, cy, acc, "solid")
                elif key in r["ts"]:
                    dot(c, x, cy, acc, "base")
            elif key in r["params"]:
                dot(c, x, cy, PCODE[key][4], "square")
        y += RH
    # column rules
    for gname, a, b, acc in col_groups:
        c.line(a, mtop, a, y, "line", 1.2)
        c.line(b, mtop, b, y, "line", 1.2)
    c.line(X0, y, mx1, y, "line", 1.2)
    y += 22
    c.legend(X0, y, [
        ("box", "green", "holds"), ("box", "green", "holds, qualified", "5 3"), ("box", "red", "void"),
        ("box", "red", "not enforced, or owed", "5 3"), ("box", "teal", "harness or gate run"),
        ("box", "teal", "proof column: proved in a proof module"),
        ("box", "blue", "corrected 2026.10.02 (number as in the band above)"),
    ], title="Row verdict (last column)")
    y += 34
    # glyph legend drawn by hand
    gx = X0
    c.text(gx, y + 13, "Cell glyph", 13, "faint", bold=True)
    gx += 100
    for kind, acc, lab in [("solid", "blue", "names the premise"), ("hollow", "red", "names it at one declared rung"),
                           ("base", "faint", "BASE premise"), ("square", "green", "parameter, gap or input premise")]:
        dot(c, gx + 8, y + 8, acc if acc != "faint" else "grey", kind)
        c.text(gx + 24, y + 13, lab, 13, "muted")
        gx += 24 + text_width(lab, 13) + 36
    y += 54

    # ---------------------------------------------------------------- part 3: premise keys
    y += c.heading(X0, y, "3 · The premise columns", size=22)
    kw = (W - 40) / 2
    ty = y
    trows = []
    count = {t: sum(1 for r in rows if t in r["ts"]) for t in range(1, 32)}
    expl = {t: sum(1 for r in rows if t in r["explicit"]) for t in range(1, 32)}
    for gname, ids in TGROUPS:
        trows.append({"group": gname, "accent": "grey"})
        for t in ids:
            name, st = TROWS[t]
            acc, stl = ST[st]
            n = expl[t]
            inbase = t in BASE or t == PROVER
            cited = f"{n} by name" + (f", {count[t]} with BASE" if inbase else "") if n or inbase else \
                "[[red|uncited]]"
            trows.append([f"**T-0045-{t}**", name, f"[[{acc}|{stl}]]", cited])
    h1 = c.table(X0, ty, [("Row (ADR-0045 Annex A)", kw * 0.24), ("Component, short", kw * 0.34),
                          ("Class at the reference (Annex B)", kw * 0.24), ("Rows citing it", kw * 0.18)],
                 trows, size=13.5)
    prow = [{"group": "Parameter premises: archetype value, with the degeneracy that falsifies it", "accent": "grey"}]
    for code, short, written, falsified, acc in PARAMS:
        n = sum(1 for r in rows if code in r["params"])
        prow.append([written, falsified, f"[[{acc}|{ {'green': 'holds', 'red': 'false', 'violet': 'draft'}[acc]}]]",
                     str(n)])
    prow.append({"group": "Gap premises, Proposed premises and asserted inputs", "accent": "grey"})
    for code, short, written, note, acc in GAPS:
        n = sum(1 for r in rows if code in r["params"])
        lab = {"red": "open", "amber": "Proposed", "blue": "asserted"}[acc]
        prow.append([written, note, f"[[{acc}|{lab}]]", str(n)])
    prow.append({"group": "Struck 2026.10.02 (ADR-0046 §5)", "accent": "grey"})
    for written, note in STRUCK:
        prow.append([f"[[grey|{written}]]", note, "[[grey|struck]]", "0"])
    h2 = c.table(X0 + kw + 40, ty, [("Premise as the table writes it", kw * 0.38), ("Falsified by, or source", kw * 0.36),
                                    ("At the reference", kw * 0.14), ("Rows", kw * 0.12)], prow, size=13.5)
    y = ty + max(h1, h2) + 50

    # ---------------------------------------------------------------- part 4: the table in full
    y += c.heading(X0, y, "4 · The binding table, verbatim except one omitted external citation: all 42 rows (`spec/theorem-premise-binding.md`)", size=22)
    cols_t = [("Theorem", 330), ("Checked in (and, since B25, proved in)", 330), ("Record", 220),
              ("Breaks under", 420), ("Row premises", 640), ("Parameter and gap premises", 680),
              ("At the reference (Annex B)", 868)]
    trs = []
    cur = None
    for r in rows:
        if r["group"] != cur:
            cur = r["group"]
            trs.append({"group": GROUPS[cur], "accent": "grey"})
        trs.append({"cells": r["cells"], "accent": VERDICT[r["vcls"]][0]})
    y += c.table(X0, y, cols_t, trs, size=13.5) + 40

    # ---------------------------------------------------------------- closing
    w2 = (W - 24) / 2
    hh = c.card(X0, y, w2, "Reading the last column as an inventory (the file's own words)", [
        "At the reference, every theorem premised on confinement, gate evidence, hermeticity or channel fidelity is "
        "**void**; the routing theorem and the gate verdicts rest on checked proofs since 2026.10.01, where before "
        "they were the solver's assertion; the bundle's revision is a file name; the reach bound is declared and not "
        "enforced.",
        "What remains holds of the modules and, by trace validation, of the running code on every tested path: the "
        "lease, the fence, revocation, composition, the rules floor, the bootstrap pair, seats, any-of, coupling with "
        "its collusion gap, Run's counters and seal. That is ADR-0045 Annex B's inventory sentence, computed.",
    ], accent="blue", size=14.5)
    c.card(X0 + w2 + 24, y, w2, "Keeping it current, and where it is stale", [
        "A new property adds a row; a new T-row or degeneracy adds a premise; an ADR-0033 addendum that changes a "
        "row's class at the reference changes the last column. `tools/check-refs.py` does not read this file.",
        "A premise edge added into an existing theorem weakens it and needs its own record (ADR-0023 carried scope); "
        "the archetype-evolution record owns that rule (G6 item 7).",
        "[[red|Stale as drawn:]] the inventory sentence still says \"the bundle's revision is a file name\" while its "
        "own `BundleRefusalHonored` row says the revision is verified since 2026.10.01; the trace row says 21 traces, "
        "where G7 §3 records **22 traces, 168 steps** at 2026.10.01.",
    ], accent="amber", size=14.5, h=hh)
    return c
