"""G3 — Theorem-to-premise DAG: the binding table ADR-0045 §3 owes, drawn in full, as an incidence matrix and as
three node-link chains (Contained, promotion, floor routing), with the proof column and the corrections ADR-0046 §5
made at Batch 25, the launcher's revision of 2026.10.02, the certification of each bound module (ADR-0046 A1), and the
gap G10 records: six proof modules with no row, and RulesFloorBase.tla behind ADR-0026 A2 (G10 §2.6, item 90).

The table is read at build time from spec/theorem-premise-binding.md (relative to the repository root), so the
43-row table below is the file's text. The premise incidences are computed from its "Row premises" column (every
T-0045-n token, ranges expanded, BASE expanded to its five rows, and to T-0045-31 as well for a row whose "Checked in"
column names a proof module); parameter and gap premises, the verdict labels, the rung-conditional marks, the proof
status and the 2026.10.02 corrections are transcribed here and asserted against the parsed rows (parameter tokens
outside struck text, "proved in", the correction notes), so a change to the file fails the build instead of drawing
a stale matrix.
"""
import pathlib
import re

import lib
from lib import AMENDED_G11, strip_external, Canvas, render_line, parse, wrap, text_width, fill, sonly, fs

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
        if len(cells) != 7:      # the derived-premises tables below the theorem table (ADR-0053, B36)
            continue
        rows.append(cells)
    return rows


def t_rows(cell, proved=False):
    """Every T-0045-n named in a Row premises cell; ranges expanded; BASE expanded (with the prover if proved)."""
    out = (set(BASE) | ({PROVER} if proved else set())) if "BASE" in cell else set()
    cell = re.sub(r"T-0045-\d+ as `[^`]+`", "", cell)   # "T-0045-29 as `invariant(M)`": a BASE row, renamed (B36)
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
# verdict classes: holds, holdsq (holds, qualified), void, notenf, owed, harness, pending (a record not ratified)

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
    ("NoSilentDowngrade", "`NoSilentDowngrade`", "Confinement", "holdsq", "holds, per seat (A7, B29)", [],
     {17, 18, 19}),
    ("ContestedStopped", "`ContestedStopped`", "Confinement", "void", "void: no real measurement", ["c2"],
     {16, 18}),
    ("FreshAppraisal", "`FreshAppraisal`", "Confinement", "holdsq", "holds at rung 1 (A7, B29)", ["c1"], set()),
    ("EffectsOnDeclaredChannels", "`EffectsOnDeclaredChannels`, `Contained…`", "RunConfinement", "stale",
     "table: pending · A2 ratified B30", ["p4run", "runc"], set()),
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
    ("Trace validation", "Trace validation, refinement check", "Unmodelled", "harness", "57 traces match; invariants kept",
     ["orc"], set()),
]

GROUPS = {
    "Lease": "`Lease.tla`, `Lease_A1.tla` · ADR-0031",
    "Floor": "`FloorComposition.tla`, `FloorRouting.tla` · ADR-0030",
    "NonComposition": "`NonComposition.tla` · ADR-0013 · models X1, retired; its successor `NonComposition_A1` has no row",
    "Rules": "`RulesFloorNV_rev5.tla` · the rules floor, ADR-0026, ADR-0024",
    "Bootstrap": "`Anchor.tla`, `BreakGlass.tla` · the bootstrap pair, ADR-0029 §5 · both extend `RulesFloorBase.tla`, "
                 "and `BreakGlass.tla` models X1, retired; its successor `BreakGlass_A1` has no row",
    "Confinement": "`Confinement.tla`, `Confinement_A1.tla`; on traces `ConfinementRefinement.tla` · ADR-0034",
    "RunConfinement": "`RunConfinement.tla` · ADR-0034 A2 and ADR-0042 §6, both in force since B30; the table still "
                      "calls them pending and Proposed",
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
    "pending": ("amber", "5 3", "pending: the record it rests on is drafted, not ratified"),
    "stale":   ("amber", "5 3", "the table's verdict predates a ratification and was not recomputed (G10 item 90)"),
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
    "sim":    ("red", "SIMULATED only (test keys)"),
    "inst1":  ("blue", "trust root: rung-1 instance (A7, B29)"),
    "rootp":  ("blue", "trust root, in part (A2, B34)"),
}
TROWS = {
    1: ("replicas, crash-fault", "root"), 2: ("signature primitive", "root"), 3: ("Cedar engine", "root"),
    4: ("monotonic clock", "deleg"), 5: ("round-topic transport", "deleg"), 6: ("bundle-tier engines", "deleg"),
    7: ("archive, plaintext store", "deleg"), 8: ("anchor key store", "rootd"), 9: ("anchor key-holders", "rootd"),
    10: ("resident genesis rules", "root"), 11: ("corpus and custodian", "root"),
    12: ("break-glass approvers", "root"), 13: ("gate runner, evidence", "excl"),
    14: ("proof checker (B24)", "root"), 15: ("lineage gate tools", "noinst"),
    16: ("CPU root of trust", "sim"), 17: ("independent verifier", "sim"), 18: ("firmware, hypervisor", "none"),
    19: ("host operator", "inst1"), 20: ("image, profile P1–P7", "inst1"), 21: ("inference attestation", "none"),
    22: ("the host at rung 0", "excl"), 23: ("native tool (Invoke)", "excl"), 24: ("Run tool channel", "excl"),
    25: ("tool host", "root"), 26: ("decoding conformance", "none"), 27: ("bundle signer (B23)", "rootd"),
    28: ("code refines spec", "root"), 29: ("TLC, its constants", "root"), 30: ("build toolchain", "root"),
    31: ("TLA+ Proof System (B25)", "root"),
    32: ("label computation (A1)", "root"), 33: ("label declarations (A1)", "excl"),
    34: ("handles, tool list (A1)", "root"), 35: ("operator's provider (A2)", "rootp"),
    36: ("operator's key custody (A2)", "rootp"),
}
NT = 36
# Proof certification (ADR-0046 A1; spec/proof-certification.md §9; G10 §2.9): the three modules that do not certify.
UNCERT = {"RulesFloorNV_rev5", "Confinement", "Confinement_A1"}
# Every proof module at G10, with its certified results file's obligation count (spec/*-proof-cert-results-*.txt).
# bound: named in the binding table's Checked-in column. record: the record the module is owed by.
MODULES = [
    # (module, record, obligations, bound)
    ("Lease_A1", "ADR-0031 §4, §5, A1", 200, True),
    ("FloorComposition", "ADR-0030 §1, §4", 171, True),
    ("FloorRouting", "ADR-0030 §5", 36, True),
    ("NonComposition", "ADR-0013 §4 (models X1)", 58, True),
    ("RulesFloorNV_rev5", "ADR-0026; ADR-0024", 262, True),
    ("Anchor", "ADR-0029 §5", 40, True),
    ("BreakGlass", "ADR-0029 §5; ADR-0026 R7 (models X1)", 37, True),
    ("Confinement", "ADR-0034 §3, §4", 502, True),
    ("Confinement_A1", "ADR-0034 §3, §4 (finding 6)", 503, True),
    ("RunConfinement", "ADR-0034 A2", 116, True),
    ("Seats", "ADR-0037", 110, True),
    ("Observers", "ADR-0038", 65, True),
    ("Coupling", "ADR-0039", 320, True),
    ("RunCoupling", "ADR-0041, ADR-0042", 469, True),
    ("RunSeats", "ADR-0040, ADR-0043", 147, True),
]
# The proof modules G11 §2.6 and item 90 name: (module, record, TLC rows, properties, obligations). G10 §3; G11 §3.
UNBOUND = [
    ("Labels", "ADR-0047 §11", 37, "ten properties", 651),
    ("ToolList", "ADR-0048 §8", 27, "five properties", 215),
    ("Operators", "ADR-0050 §10 (provisional)", 32, "thirteen invariants", 354),
    ("Emergency", "ADR-0052 §9 (provisional)", 51, "six properties", 373),
    ("BreakGlass_A1", "ADR-0052 R5; ADR-0026 A2 (successor to BreakGlass)", 8, "`EmergencyNeverChangesAuthority`", 45),
    ("NonComposition_A1", "ADR-0052 R5; ADR-0013 A1 (successor to NonComposition)", 14, "NC-1, NC-2", 96),
    ("Emergency_live", "ADR-0039 A2; ADR-0052 §9 (provisional; extends Emergency)", 32,
     "two invariants over `ENABLED`", 160),
    ("Coupling_live", "ADR-0039 §2 (extends Coupling); leads-to checked, not proved", 69,
     "`SpecL ⇒ Spec` and safety", 31),
]
# The modules G11 item 90 names that have no proof at all: their records are Proposed (G11 §2.9, item 101).
UNPROVED = [("Workflow", "ADR-0054 §12 (Proposed)", 33, "ten properties"),
            ("Mesh", "ADR-0055 §11 (Proposed)", 23, "seven properties")]
CORRELATOR = ("Correlator", "ADR-0051 §10 (Proposed)", 22, "the properties of §10", 455)
TGROUPS = [
    ("Mechanism constants (all rungs)", list(range(1, 13)) + [35, 36]),
    ("Build-gate toolchain", [13, 14, 15]),
    ("Verified object's evidence", [28, 29, 30, 31]),
    ("Confinement axis", list(range(16, 23))),
    ("Tools and the cell", [23, 24, 25, 27, 26, 32, 33, 34]),
]
# Parameter and gap premises: code -> (column label, written as, falsified by / note, accent at the reference)
PARAMS = [
    ("fver", "floor verified", "floor verified", "D-0030-1 drops the proven status", "green"),
    ("fdraft", "floor text DRAFT", "the floor text is DRAFT, so the envelope it permits is the draft's",
     "qualifier: no floor is ratified (G10 §8). The floor the reference links is now the proposed floor's "
     "`emergency` stage, genesis-provisional (ADR-0030 A3; G10 §2.2)", "violet"),
    ("rchk", "routing checked", "routing checked (ADR-0030 §5 A1)", "D-0030-2: gates run without the checker",
     "green"),
    ("bsig", "bundle signed", "bundle signed", "D-0044-1: the revision is a file name", "green"),
    ("r67", "rules floor R6, R7", "rules floor R6, R7 in force", "dropping either entry", "green"),
    ("qall", "quorum = \"all\"", "`quorum = \"all\"`", "D-0024-1 voids it; R9 keeps D-0024-2 out", "green"),
    ("ming", "minGrant ≥ 2", "`minGrant ≥ 2`", "dropping R2", "green"),
    ("qge2", "threshold ≥ 2", "`quorum ≥ 2` when a threshold",
     "dropping R9 with R1 relaxed; the proof's hypothesis is R2 and (R1 or R9)", "green"),
    ("c1", "confinement ≥ 1", "confinement ≥ 1",
     "D-0034-1, -2 lower it; D-0034-4 is rung 0. Declared per seat (ADR-0023 §6c, B29): rung 1 real at the "
     "reference (A7, B29)",
     "amber"),
    ("c2", "confinement ≥ 2", "confinement ≥ 2",
     "rungs 0 and 1 cannot produce Contested; at the reference rung 3 is SIMULATED, rung 2 a seam", "red"),
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
    ("runc", "Run's confinement", "Run's confinement delivered; ADR-0042 §6 in force",
     "ADR-0042 §6 in force since B30 with ADR-0034 A2; the reference follows by ADR-0033 A8, A9. No Run principal is "
     "`Contained` (G10 §2.3, §2.5). The table still calls §6 Proposed", "amber"),
    ("p4run", "Run profile's P4", "the Run profile's P4 passes",
     "ADR-0034 A2 (B30): P4 for Run is channel fidelity, owned by the tool host's Wasm runtime", "amber"),
    ("g18", "gap: independence table", "gap: no independence table", "G18", "red"),
    ("orc", "trace oracles", "the oracles: issuance validity, approval signatures, the parameter digest; an "
     "appraisal's signature and key, a session proof, a profile's parse", "taken from the trace, not computed", "blue"),
]
PCODE = {p[0]: p for p in PARAMS + GAPS}
# Status at the reference where the accent's default word would mislead.
PSTAT = {"c1": "per seat (A7, B29)", "p4run": "in force (B30); table stale", "runc": "in force (B30); table stale"}

# How each parameter, gap or input premise is written in the file (searched in the "Row premises" and "Parameter and
# gap premises" cells with struck text removed). Every token found must be transcribed in META, and vice versa.
TOKENS = {
    "fver": r"floor verified", "fdraft": r"the floor text is DRAFT", "rchk": r"routing checked",
    "bsig": r"bundle signed", "r67": r"R6, R7 in force", "qall": r'quorum = "all"', "ming": r"minGrant ≥ 2",
    "qge2": r"quorum ≥ 2", "c1": r"confinement ≥ 1", "c2": r"confinement ≥ 2", "obs": r"an Observer per cell",
    "coup": r"coupling on", "corr": r"a correlator exists", "effc": r"effects counted",
    "root": r"the Run root is pinned", "a22": r"A2\.2 and A2\.3 as tally constants",
    "wm": r"watermark is honest|honest watermark", "indep": r"independence criterion in force",
    "runc": r"Run's confinement delivered|ADR-0042 §6 in force", "p4run": r"the Run profile's P4 passes",
    "g18": r"no independence table", "orc": r"the oracles \(",
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
    assert len(table) == len(META) == 43, (len(table), len(META))
    out = []
    for cells, meta in zip(table, META):
        match, label, group, vcls, vlab, params, cond = meta
        assert match in cells[0], (match, cells[0])
        proved = bool(re.search(r"proved in `[A-Za-z0-9_]+_proof\.tla`", cells[1]))   # TLAPS, not "proved in Lean"
        assert proved == (group != "Unmodelled"), (match, "proof column", cells[1])
        prem = _unstruck(cells[4] + " ; " + cells[5])
        found = {k for k, t in TOKENS.items() if re.search(t, prem)}
        assert found == set(params), (match, "parameter premises", sorted(found), sorted(params))
        # a results file's date is not a correction note
        nofile = [re.sub(r"[\w.-]*2026\.10\.02[\w.-]*\.txt", "", x) for x in cells]
        noted = any("2026.10.02" in x or "proof's hypothesis" in x for x in nofile)
        assert noted == (match in CORR and match not in UNNOTED), (match, "correction note", noted)
        ts = t_rows(cells[4], proved)
        assert cond <= ts, (match, cond, ts)
        pmods = re.findall(r"`(\w+)_proof\.tla`", cells[1])
        assert proved == bool(pmods), (match, pmods)
        known = {m[0] for m in MODULES}
        assert set(pmods) <= known, (match, pmods)
        cert = proved and not (set(pmods) & UNCERT)
        out.append(dict(cells=cells, label=label, group=group, vcls=vcls, vlab=vlab, params=params, cond=cond,
                        ts=ts, explicit=explicit_t(cells[4]), base="BASE" in cells[4], proved=proved,
                        corr=CORR.get(match), match=match, cert=cert, pmods=pmods))
    assert sum(r["proved"] for r in out) == 38, "proved rows"
    bound = {m for r in out for m in r["pmods"]}
    assert bound == {m[0] for m in MODULES}, sorted(bound)
    assert sum(m[2] for m in MODULES) == 3036
    assert sum(m[2] for m in MODULES) + sum(u[4] for u in UNBOUND) + CORRELATOR[4] == 5416
    assert len(MODULES) + len(UNBOUND) + 1 == 24
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


def pill_lines(row, maxw, size=12):
    """The pills of a theorem node (verdict, proved, certified), flowed into lines that fit maxw."""
    labels = [("v", row["vlab"])]
    if row["proved"]:
        labels += [("p", "proved"), ("c", "certified") if row["cert"] else ("n", "not certified")]
    lines, cur, w = [], [], 0
    for kind, lab in labels:
        pw = text_width(lab, size, True) + 18
        if cur and w + pw > maxw:
            lines.append(cur)
            cur, w = [], 0
        cur.append(kind)
        w += pw + 8
    lines.append(cur)
    return lines


def vpill(c, x, y, row, size=12.5, anchor="start"):
    acc, dash, _ = VERDICT[row["vcls"]]
    solid = row["vcls"] in ("holds", "void", "harness")
    return c.pill(x, y, row["vlab"], acc, size, dash=dash, solid=solid, anchor=anchor)


# ---------------------------------------------------------------------------------------------

def build():
    rows = model()
    c = Canvas(ID, "Theorem to premise: what every checked or proved property rests on, and what is void at the "
               "reference",
               "`spec/theorem-premise-binding.md` (2026.09.30, revised 2026.10.01, 2026.10.02 with ADR-0046, "
               "2026.10.02 for the launcher, \"pending\" ADR-0033 A7, and 2026.10.06 with ADR-0053's derived premises; "
               "**DRAFT**, revised with the records it binds) is the table ADR-0045 §3 owes and ADR-0023 §2 assumes: "
               "one row per checked property, naming the trusted-base rows (ADR-0045 Annex A), the degeneracy "
               "parameters (ADR-0023 §6a) and the declared gaps it rests on. A property holds for a deployment when "
               "every row it names is declared delegated or trust root, every parameter holds and no gap premise is "
               "false; otherwise it is void. 38 of its 43 rows name a proof module, 15 modules in all; at G11 "
               "**twelve of those certify and three do not**, and **nine of the twenty-four proof modules have no row**: "
               "the eight G11 names behind the records (§2.6, item 90, open) and `Correlator`, whose record is Proposed; "
               "nor do `Workflow` and `Mesh`, which have no proof (item 101). "
               "Where a record moved and the table did not (A7, B29; ADR-0034 A2 and ADR-0042 §6, B30), the verdict is "
               "drawn as the table states it and marked. Drawn four ways: the gap, the key chains as a DAG, the full "
               "incidence matrix, and the table itself, all 43 rows. `spec/theorem-premise-binding.json` carries the "
               "same table as a Boolean matrix and `spec/inventory.py --check` fails when the two disagree; this "
               "diagram reads the Markdown.",
               3600,
               "spec/theorem-premise-binding.md (all 43 rows, read at build time; revised 2026.10.06, B36); "
               "spec/theorem-premise-binding.json (2026.10.03); ADR-0045 §3, §5, Annex A, Annex B "
               "(B23, B24, B25, B28, B29, B30, A1, A2, B34); ADR-0046 §1–§5 (Batch 25), A1 (Batch 28); "
               "spec/proof-certification.md §9; spec/*-proof-cert-results-2026.10.04.txt and -2026.10.05.txt; "
               "spec/premise-corrections-results-2026.10.02.txt; ADR-0053 §5 and finding 2 (B36; R1); spec/lean's results "
               "file; spec/RulesFloorBase.tla; spec/BreakGlass_A1.tla, "
               "spec/NonComposition_A1.tla (headers); ADR-0023 §2, §6a, A1 §6c; ADR-0026 A2 (provisional); ADR-0033 "
               "A5 to A9, A14; ADR-0034 A2 (B30); ADR-0042 §6 (B30); ADR-0030 §5 A1, A3; ADR-0047 §11; ADR-0048 §8; "
               "ADR-0050 §10; ADR-0051 (Proposed); ADR-0052 §9, R5; G8 §2.2, §3; "
               "G10 §2.1, §2.3, §3, §7 items 80, 89; G11 §2.6, §2.9, §3, §7 items 7, 74, 90, 101, §8; "
               "spec/Emergency_live.tla, spec/Coupling_live.tla, spec/Workflow.tla, spec/Mesh.tla (headers and results); "
               "spec/Mechanism-trace-results-2026.10.02.txt, spec/Mechanism-trace-results-2026.10.05.txt")
    c.note = AMENDED_G11
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
            "Since B25 the **Checked in** column names the proof module beside the base module (ADR-0046 §5); "
            "38 rows name one.",
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
            "archetype-evolution record, still unwritten (G11 item 7). Its rows were last revised 2026.10.02, "
            "\"pending\" ADR-0033 A7; **A7 and ADR-0034 A2 have been ratified since** (B29, B30) and the rows were "
            "not revised; Batch 36 added derived premises and changed no row's verdict (G11 §2.6, item 90). `Never…` "
            "witnesses are not theorems and are omitted.",
        ], "violet"),
    ]
    hh = max(c.card(0, 0, w4, t, b, accent=a, draw=False, size=14.5) for t, b, a in intro)
    for i, (t, b, a) in enumerate(intro):
        c.card(X0 + i * (w4 + gap), y, w4, t, b, accent=a, h=hh, size=14.5)
    c.status(X0 + 3 * (w4 + gap) + w4 - 16, y + 16, "accepted", "C2, C4", anchor="end")
    y += hh + 54

    # ---------------------------------------------------------------- the gap at G10 (item 90) and certification
    hx = X0 + c.pill(X0, y + 2, "Open · G11 §7 item 90", "red", 13, dash="6 4") + 14
    c.text(hx, y + 18, "**0 · What the table covers at G11, and what it does not: twenty-four proof modules, fifteen "
                       "bound, twelve of those certified; nine with no row; two modules with no proof**", 22, "ink")
    y += 44
    y += c.para(X0, y, W, "G11 item 90: \"The binding table has no rows for `Labels`, `ToolList`, `Operators`, "
                "`Emergency`, `BreakGlass_A1` or `NonComposition_A1`, nor now for `Emergency_live`, `Coupling_live`, "
                "`Workflow` or `Mesh`.\" It also names `RulesFloorBase.tla`. Certification is ADR-0046 A1's (Batch 28): every obligation closed by the "
                "prover's normalization, an SMT proof the `ethos` checker accepted, a Zenon proof Isabelle checked, or "
                "an LS4 temporal step no checker confirms (`spec/proof-certification.md` §2, §9; G10 §2.9). Obligation "
                "counts are each module's certified results file.", 15, "muted") + 16
    TW = 2140
    nrow = {m[0]: sum(1 for r in rows if m[0] in r["pmods"]) for m in MODULES}
    why = {"RulesFloorNV_rev5": "five obligations are Zenon's, and Isabelle refuses the script for one",
           "Confinement": "three large type-invariant steps proved by Z3 and by nothing else; cvc5 does not prove them",
           "Confinement_A1": "the same three steps"}
    mrows = [{"group": f"Bound: named in the table's Checked-in column · {len(MODULES)} modules, "
                       f"{sum(m[2] for m in MODULES):,} obligations · "
                       f"{sum(1 for m in MODULES if m[0] not in UNCERT)} certify, {len(UNCERT)} do not",
              "accent": "teal"}]
    for mod, rec, n, _ in MODULES:
        if mod in UNCERT:
            cert = f"[[red|not certified]]: {why[mod]}. Restructuring deferred by the custodian (G11 item 74)"
            acc = "red"
        else:
            cert = "[[teal|certified]]"
            acc = "teal"
        mrows.append({"cells": [f"`{mod}`", rec, "—", f"{n:,}", cert, f"{nrow[mod]} row" + ("s" if nrow[mod] != 1 else "")],
                      "accent": acc})
    mrows.append({"group": f"No row: G11 item 90, open · {len(UNBOUND)} modules, "
                           f"{sum(u[4] for u in UNBOUND):,} obligations · every one certified · their records in "
                           "force since Batch 34, two provisional; two liveness extensions since 2026.10.07",
                  "accent": "red"})
    for mod, rec, tlc, props, n in UNBOUND:
        mrows.append({"cells": [f"`{mod}`", rec, f"{tlc} TLC rows; {props}", f"{n:,}", "[[teal|certified]]",
                                "[[red|no row]]"], "accent": "red"})
    mrows.append({"group": "No row, and its record is Proposed: not named by item 90", "accent": "amber"})
    mod, rec, tlc, props, n = CORRELATOR
    mrows.append({"cells": [f"`{mod}`", rec, f"{tlc} TLC rows; {props}", f"{n:,}", "[[teal|certified]]",
                            "[[amber|no row; record Proposed]]"], "accent": "amber"})
    tot = sum(m[2] for m in MODULES) + sum(u[4] for u in UNBOUND) + n
    ncert = sum(1 for m in MODULES if m[0] not in UNCERT) + len(UNBOUND) + 1
    nall = len(MODULES) + len(UNBOUND) + 1
    mrows.append({"cells": ["**All**", f"**{nall} proof modules** (G11 §2.9)", "", f"**{tot:,}**",
                            f"**{ncert} of {nall} certify**", f"**{len(MODULES)} bound, {nall - len(MODULES)} not**"]})
    mrows.append({"group": "No row and no proof: TLC-checked modules of Proposed records (G11 items 90, 101)",
                  "accent": "amber"})
    for mod, rec, tlc, props in UNPROVED:
        mrows.append({"cells": [f"`{mod}`", rec, f"{tlc} TLC rows; {props}", "—", "[[red|no proof]]",
                                "[[amber|no row; record Proposed]]"], "accent": "amber"})
    mth = c.table(X0, y, [("Proof module", 300), ("Record it is owed by", 620), ("TLC rows; properties (G10 §3, G11 §3; for the modules with no row)", 400),
                          ("Obligations", 150), ("Certified (ADR-0046 A1)", 470), ("In the binding table", 200)],
                  mrows, size=13.5, accent="teal")
    gx = X0 + TW + 40
    gw = X1 - gx
    gcards = [
        ("Eight modules, 1,925 obligations, no premise rows; and two unproved", [
            "Every property `Labels`, `ToolList`, `Operators`, `Emergency`, `BreakGlass_A1`, `NonComposition_A1`, "
            "`Emergency_live` and `Coupling_live` prove is **outside the inventory**: no row names what it rests on, "
            "so the last column computes nothing for it, at the reference or for any deployment. `Coupling_live`'s "
            "four leads-to properties are checked, not proved, and are not rows either.",
            "`Workflow` and `Mesh` have neither a proof nor a row; their records are Proposed (G11 item 101).",
            "So **T-0045-32 to 36**, the five trusted-base rows Batch 34 added for the same records, are premises of "
            "no row (the matrix below draws their columns empty).",
            "The record behind each is in force; two are **provisional** (ADR-0050, ADR-0052), so their properties "
            "would bind to text that is subject to redesign (ADR-0029 A4).",
        ], "red", "open"),
        ("`RulesFloorBase.tla` still carries `bgScope` and R6's bound of two", [
            "The rule space has `bgScope : SUBSET BGActs`, and `Entry` reads `\"R6\" -> r.exceptions <= 2` and "
            "`\"R7\" -> r.bgScope \\cap AuthActs = {}`.",
            "**ADR-0026 A2** (Batch 34, provisional with ADR-0052): R6's count is **one**, X1 being retired; R7 is read "
            "as \"no activation of an emergency seating grants a lease whose alphabet holds an authority act\" "
            "(G11 §2.1).",
            "`Anchor.tla` and `BreakGlass.tla` extend it, so the rows `FloorPreserved` and "
            "`BreakGlassNeverChangesAuthority` rest on the old rule space. `BreakGlass_A1` extends it too and reads "
            "`bgScope` for nothing (its header). The ADR-0026 §6 rerun is still owed (G11 §2.1).",
        ], "red", "open"),
        ("Two rows proved of modules that model X1, and one on R7 as first written", [
            "`NC1`, `NC2` (`NonComposition.tla`) and `BreakGlassNeverChangesAuthority` (`BreakGlass.tla`) are proved of "
            "predecessors that model X1, which is retired. Their successors, `NonComposition_A1` and `BreakGlass_A1`, "
            "are proved and certified and have no row; the predecessors stay frozen and cited by digest (G10 §3).",
            "`P7_BGNoAuthority` is R7 as first written; A2 changed R7's subject.",
        ], "amber", None),
        ("What certifying does not change", [
            "**Certified is not verified.** It removes the SMT solver's soundness as a premise; the prover's translation, "
            "its normalization, LS4 and the checker stay trusted, and the translation is known to be unsound in two "
            "ways (G11 §2.9, §8; ADR-0046 A2; T-0045-31).",
            "It changes **no verdict** in the last column: a proof is of the module, not of what runs (T-0045-28). "
            "`Operators.tla` and `Emergency.tla` are tied to the reference by tests and no refinement (item 90).",
        ], "teal", None),
    ]
    gy = y
    for t, b, a, st in gcards:
        gy += c.card(gx, gy, gw, t, b, accent=a, size=14, status=st, tint=a != "red") + 18
    y = max(y + mth, gy - 18) + 60

    # ---------------------------------------------------------------- the B25 band: proofs and corrections
    y += c.heading(X0, y, "Batch 25 (ADR-0046 §4, §5): the proof column, and five corrections the proofs found",
                   size=22)
    y += c.para(X0, y, W, "Each proof module takes as hypothesis only the mutations that break each invariant, written "
                "independently of the table; where the two disagreed TLC agreed with the proof, and the table was "
                "corrected (G8 §3, result 2). The corrections' TLC rows are `spec/premise-corrections-results-"
                "2026.10.02.txt` (`2669499135d2ea42`), every outcome as predicted.", 15, "muted") + 16
    b25 = [
        ("The proof column", [
            "**38 of 43 rows** name a proof module: fifteen modules (thirteen at B25), **3,036 obligations** "
            "(2,417 at B25), each invariant proved as `Spec => []P` under the module's named assumptions and the "
            "absence of the mutations that break it. At G10 there are 22 modules and 5,225 obligations (§2.9); "
            "the seven others have no row (section 0).",
            "**No proof**: effect exclusivity (a claim), `PromotionMeetsIssuedQuorum` (module unwritten), the Paxos "
            "simulation, the floor gates, and trace validation (`Mechanism.tla` is a trace replay and "
            "`ConfinementRefinement.tla` a predicate set; the target is the refinement, T-0045-28).",
            "A proof of a module **adds nothing at the reference** (G10 §8), certified or not: the last column moved "
            "at 2026.10.02 for the launcher, not for the proofs.",
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

    # ---------------------------------------------------------------- ADR-0053 (B36): the Lean route
    import json
    from d_h7_lean_route import ENC
    lean_proofs = {f"{m}_proof.tla" for m, _ in ENC}
    bj = json.loads((ROOT / "spec" / "theorem-premise-binding.json").read_text(encoding="utf-8"))
    th = bj["theorems"]
    n_lean = sum(1 for t in th if t.get("proved_in") and set(t["proved_in"]) <= lean_proofs)
    ov = json.loads((ROOT / "spec" / "theorem-premise-binding-ADR-0053.json").read_text(encoding="utf-8"))
    n_inv = sum(1 for k in ov["derived"] if k.startswith("invariant(") and "," not in k)
    n_chk = sum(1 for p in ov["premises"].values() if p["kind"] == "check")
    rt = sorted((ROOT / "spec").glob("premise-routes-results-*.txt"))[-1]
    rtx = rt.read_text(encoding="utf-8")
    import re as _re
    held = dict(_re.findall(r"=== (\S+)[^\n]*\n(?:.*\n)*?(\d+) of 43 rows hold", rtx))
    no_ov = next((m.group(1) for f in sorted((ROOT / "spec").glob("premise-routes-results-*.txt"))
                  for m in [_re.search(r"without the overlay[^\n]*\n(\d+) of 43", f.read_text(encoding="utf-8"))] if m),
                 "?")
    y += c.heading(X0, y, "Since Batch 36 (ADR-0053 §5, R7): a Lean route beside the proof column, as derived premises",
                   "amber", 22)
    y += c.para(X0, y, W, "Ratified 2026.10.06 in Batch 36: the table carries what follows. Counts "
                "are computed from `spec/theorem-premise-binding.json` at build time against the proof modules "
                "`spec/lean` re-encodes (H7).", 15, "muted") + 16
    b53 = [
        ("What the table gained", [
            f"**{n_lean} of 43 rows** name only proof modules `spec/lean` re-encodes: their *Checked in* column gains "
            "the Lean file, \"proved in Lean in `spec/lean/TopakSpec/<M>.lean`\".",
            f"**`FloorComposition`'s rows** also gain \"the code's decision refines its `Decide`, in Lean\" "
            "(`mechanism/lean`, ADR-0053 R2): its invariants hold of every behaviour in which the code decides, on "
            "T-0045-3 at the module's size.",
            "**The floor gates' row** gains `floor/lean` for totality, non-vacuity and discrimination, on the genesis "
            "floor and the floor in force.",
        ], "blue"),
        ("Two proofs, one derived premise (R7)", [
            "Two proofs give a disjunction: a property holds if **T-0045-31** holds, or if **T-0045-37** holds and the "
            "encoding is the module. A **derived premise** names it: `invariant(M)`, an OR of AND-routes, still "
            "monotone, so excluding a premise only voids.",
            f"`{rt.name}`, read at build time: {n_inv} `invariant(M)`, {n_chk} encodings whose faithfulness is a "
            f"`check` on the graph check, and `refines(Seats)`, T-0045-28 or the Lean stage. With T-0045-31 excluded and "
            f"T-0045-37 trusted, **{held.get('2-lean-not-tlaps', '?')} of 43** rows hold, where the binding before the "
            f"merge said {no_ov} (finding 13: no row named T-0045-31).",
        ], "blue"),
        ("The one reference verdict whose reason changed", [
            "Totality's `holds°` rows rested until Batch 36 on cedar's term folding, under T-0045-3. Proved in Lean of "
            "the genesis floor and the floor in force (R3) under cedar-spec's model, they rest on **T-0045-37 and "
            "T-0045-3's own premise**, "
            "\"the Cedar engine, as faithful to the Lean model\".",
            "The verdict at the reference is unchanged: T-0045-3 is a trust root either way.",
        ], "blue"),
        ("What is still open", [
            "**R1's precondition** (ADR-0053): (a) the table states alternative sets, since the merge; (b) each refined "
            "encoding a named premise with a check: `Seats` and `FloorComposition` have the graph check, eleven do not.",
            "`refines(Seats)` is a route a deployment may declare, by declaring the Seats-shaped model faithful; **no "
            "ADR-0033 addendum cites it as a stage**, and confirmation is required for it (ADR-0029 C4).",
        ], "red"),
    ]
    bw = (W - (len(b53) - 1) * bg) / len(b53)
    bh = max(c.card(0, 0, bw, t, b, accent=a, draw=False, size=14, status="accepted" if a == "blue" else "open")
             for t, b, a in b53)
    for i, (t, b, a) in enumerate(b53):
        c.card(X0 + i * (bw + bg), y, bw, t, b, accent=a, h=bh, size=14,
               status="accepted" if a == "blue" else "open", status_extra="ADR-0053 · B36" if a == "blue" else "")
    y += bh + 54

    # ---------------------------------------------------------------- part 1: the key chains as a DAG
    y += c.heading(X0, y, "1 · Three chains, drawn as a DAG: each property points at the premises it rests on "
                          "(BASE omitted)", size=22)
    y += c.para(X0, y, W, "Left: premise nodes, coloured by their class at the reference (ADR-0045 Annex B, with its B29 "
                "dependent entry). Right: properties, coloured by the table's last column; a teal **proved** pill "
                "marks a property whose invariant is proved in a proof module (ADR-0046), and the pill beside it says "
                "whether that module **certifies** (ADR-0046 A1). Neither changes a verdict. An edge runs from a "
                "property to a premise it names; a dashed edge is a premise that applies only at one declared rung. "
                "Edges take the colour of the property, so a red edge ends at what makes its property void.",
                15, "muted") + 18
    panels = [
        ("Contained: confinement and effect exclusivity", "teal",
         ["ContainedMeansConfined", "NoSilentDowngrade", "ContestedStopped", "FreshAppraisal",
          "EffectsOnDeclaredChannels", "Effect exclusivity"],
         [("T", 16), ("T", 17), ("T", 18), ("T", 19), ("T", 20), ("T", 21), ("T", 22), ("T", 23), ("T", 24),
          ("T", 25), ("P", "c1"), ("P", "c2"), ("P", "indep"), ("P", "runc"), ("P", "p4run")],
         "The reference issues rung 1 for real and rung 3 only SIMULATED (ADR-0033 A7, B29; G10 §2.3): T-0045-19 "
         "and 20 have a rung-1 instance, 16 and 17 are test keys in simulated runs only (Annex B, B29). "
         "`NoSilentDowngrade` and `FreshAppraisal` **hold**, per seat; `ContainedMeansConfined` and "
         "`ContestedStopped` are **void** for a real deployment. **No real principal is `Contained`** (G10 §8). "
         "The four confinement rows rest on `Confinement` and `Confinement_A1`, **which do not certify**. Run's two "
         "invariants are proved and certified; the table still marks them **pending** A2, ratified since (B30). "
         "Effect exclusivity stays void."),
        ("Promotion and the rules floor", "blue",
         ["PromotionMeetsIssuedQuorum", "P1_Unanimity", "P2_TwoSeatsCounted", "P5_AnchorNotApprover",
          "P9_NoSoloGrant", "FloorPreserved"],
         [("T", 2), ("T", 8), ("T", 9), ("T", 10), ("T", 13), ("T", 15), ("P", "qall"), ("P", "ming"),
          ("P", "qge2"), ("P", "a22"), ("P", "g18")],
         "The rules floor and the anchor hold, at the dev rules, which are not genesis rules (G6); their properties "
         "are proved (B25), each under the entry it rests on; `RulesFloorNV_rev5` **does not certify**, `Anchor` "
         "does. The promotion property has no module: gate evidence is an operator's assertion (T-0045-13 "
         "**excluded**), A2.2 is not built, and there is no independence table (G18)."),
        ("Floor composition and routing", "blue",
         ["AdmitImpliesFloorPermit", "FloorErrorIsDeny", "BundleRefusalHonored", "EnvelopeHolds",
          "NoWideningWithoutIssuance", "The floor gates"],
         [("T", 3), ("T", 6), ("T", 14), ("T", 27), ("P", "fver"), ("P", "fdraft"), ("P", "rchk"), ("P", "bsig")],
         "Since 2026.10.01 the routing theorem and the gate verdicts rest on checked proofs (T-0045-14, a trust root "
         "since Batch 24), where before they were the solver's assertion. The floor holds **of the draft floor**: "
         "its text is not ratified: the floor linked at G10 is genesis-provisional (ADR-0030 A3). "
         "`FloorComposition` and `FloorRouting` are proved and certified: proofs of the composition model, distinct "
         "from the gates' checked proofs, which concern the floor's Cedar text (G8 §2.2)."),
    ]
    pgap = 40
    pw = (W - 2 * pgap) / 3
    byname = {m[0]: r for m, r in zip(META, rows)}

    def prem_info(kind, k):
        if kind == "T":
            name, st = TROWS[k]
            acc, stl = ST[st]
            return f"**T-0045-{k}**", name, acc, stl, st in ("none", "excl", "sim")
        p = PCODE[k]
        stl = PSTAT.get(k) or {"green": "holds at the reference", "red": "false at the reference" if k in ("c2", "a22")
                               else "declared open", "amber": "Proposed record", "violet": "draft",
                               "blue": "asserted input"}[p[4]]
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
            nl = len(pill_lines(r, tnw - 24))
            hh_ = 16 + len(wrap(r["label"], tnw - 24, 14.5, True)) * 20 + 8 + 22 * nl + 8 * (nl - 1) + 12
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
            for li, line in enumerate(pill_lines(r, tnw - 24)):
                px_ = rx + 12
                for kind in line:
                    if kind == "v":
                        px_ += vpill(c, px_, ly + 6, r, 12) + 8
                    elif kind == "p":
                        px_ += c.pill(px_, ly + 6, "proved", "teal", 12, solid=True) + 8
                    elif kind == "c":
                        px_ += c.pill(px_, ly + 6, "certified", "teal", 12) + 8
                    else:
                        px_ += c.pill(px_, ly + 6, "not certified", "red", 12, dash="4 3") + 8
                ly += 30
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
        ("box", "amber", "premise: a Proposed record, or one the table still calls pending", "5 3"),
        ("box", "violet", "qualifier: draft text"),
        ("line", "green", "property holds"),
        ("line", "red", "property void"),
        ("line", "amber", "property the table calls pending"),
        ("line", "grey", "premise only at one declared rung", "6 4"),
        ("box", "teal", "proved: a proof module proves the invariant (ADR-0046)"),
    ], title="Key")
    y += 64

    # ---------------------------------------------------------------- part 2: the incidence matrix
    y += c.heading(X0, y, "2 · The full incidence matrix: 43 rows × 36 trusted-base rows, 16 parameters, "
                          "6 gaps, Proposed or stale premises and inputs, with the proof and certification columns",
                   size=22)
    y += c.para(X0, y, W, "Rows in the table's order, grouped by module. A column's chip and every dot in it carry the "
                "premise's class at the reference, so a void row shows the red dot that voids it. A large dot is a "
                "premise the row names; a ring is one it names only at a declared rung; a small grey dot is a BASE "
                "premise; a square is a parameter, gap or input premise. Uncited rows (T-0045-7, T-0045-26) are drawn "
                "so their absence shows, and so are **T-0045-32 to 36**, added at Batch 34 for modules the table has "
                "no rows for (item 90). T-0045-31, the prover, is a BASE premise of the 38 proved rows only, for the "
                "invariant; T-0045-29 stays in every row's BASE for the mutations and witnesses. The struck `K < R` "
                "has no column. Chips follow Annex B: T-0045-19 and 20 have a rung-1 instance and 16 and 17 are "
                "SIMULATED (B29); T-0045-24 is excluded there although the reason ended with ADR-0033 A9 (item 89). "
                "The certification pill reads the proof modules a row names: a row is certified only if every one is.", 15, "muted") + 14

    LBL, VW, PFW, CW, GG = 420, 270, 270, 41, 18
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
    col_groups.append(("Gaps, Proposed and stale premises, inputs", gx0, cx, "grey"))
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
    c.text(X0 + LBL + VW, base_y - 8, "Proof (B25), certification (B28)", 14, "faint", bold=True)
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
            px_ += (c.pill(px_, y + 5, "certified", "teal", 12) if r["cert"] else
                    c.pill(px_, y + 5, "not certified", "red", 12, dash="4 3")) + 6
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
        ("box", "red", "not enforced, or owed", "5 3"), ("box", "amber", "the table says pending; record since ratified",
                                                         "5 3"),
        ("box", "teal", "harness or gate run"),
        ("box", "teal", "proof column: proved in a proof module"),
        ("box", "teal", "certified (ADR-0046 A1)"), ("box", "red", "proved, not certified", "4 3"),
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
    count = {t: sum(1 for r in rows if t in r["ts"]) for t in range(1, NT + 1)}
    expl = {t: sum(1 for r in rows if t in r["explicit"]) for t in range(1, NT + 1)}
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
        lab = PSTAT.get(code) or {'green': 'holds', 'red': 'false', 'violet': 'draft'}[acc]
        prow.append([written, falsified, f"[[{acc}|{lab}]]", str(n)])
    prow.append({"group": "Gap premises, Proposed premises, premises the table has not caught up with, and asserted "
                          "inputs", "accent": "grey"})
    for code, short, written, note, acc in GAPS:
        n = sum(1 for r in rows if code in r["params"])
        lab = PSTAT.get(code) or {"red": "open", "amber": "Proposed", "blue": "asserted"}[acc]
        prow.append([written, note, f"[[{acc}|{lab}]]", str(n)])
    prow.append({"group": "Struck 2026.10.02 (ADR-0046 §5)", "accent": "grey"})
    for written, note in STRUCK:
        prow.append([f"[[grey|{written}]]", note, "[[grey|struck]]", "0"])
    h2 = c.table(X0 + kw + 40, ty, [("Premise as the table writes it", kw * 0.38), ("Falsified by, or source", kw * 0.36),
                                    ("At the reference", kw * 0.14), ("Rows", kw * 0.12)], prow, size=13.5)
    y = ty + max(h1, h2) + 50

    # ---------------------------------------------------------------- part 4: the table in full
    y += c.heading(X0, y, "4 · The binding table, verbatim except one omitted external citation: all 43 rows (`spec/theorem-premise-binding.md`)", size=22)
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
        "the archetype-evolution record owns that rule (G10 item 7).",
        "[[red|Stale as drawn:]] the inventory sentence still says \"the bundle's revision is a file name\" while its "
        "own `BundleRefusalHonored` row says the revision is verified since 2026.10.01, and calls every theorem "
        "premised on confinement void while `FreshAppraisal` now holds at rung 1; \"What this is not\" says "
        "thirty-seven rows are proved, where 38 name a proof module; the trace row says **57 traces, 642 steps** "
        "(`Mechanism-trace-results-2026.10.02.txt`), where G10 §3 records **82 traces, 1,007 steps** "
        "(`Mechanism-trace-results-2026.10.05.txt`, ADR-0033 A14), every step matching and every state keeping "
        "`ConfinementRefinement.tla`'s invariants.",
        "[[red|Stale against G10]] (§2.6, item 90): four confinement rows still say \"pending ADR-0033 A7\", "
        "ratified at B29; the `RunConfinement` row says \"pending: A2 is not ratified\" and \"ADR-0042 §6 in force "
        "(Proposed)\", both ratified at B30; no rows for six modules; `RulesFloorBase.tla` behind ADR-0026 A2 "
        "(section 0). The verdicts above are the table's, marked where a record has moved.",
    ], accent="amber", size=14.5, h=hh)
    return c
