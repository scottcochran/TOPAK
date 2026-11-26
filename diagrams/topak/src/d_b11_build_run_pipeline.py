"""B11 — The Build-Run pipeline (ADR-0069, Proposed): one ordered path from intake to rollout, keyed by digest; Run's
output re-enters only through intake and enables nothing; git and GitHub carry it and decide nothing. Every table of
the record, Annex A and B, the open questions and the ratification condition item by item. The CI files §10.2 cites
are read at build time and compared with the record's digests, at PIN_G12 (lib.py), the commit B11 was drawn at."""
import hashlib
import pathlib
import re

from lib import PIN_G12, Canvas, STATE_G12, STATUS, list_at, read_at, text_width

ID, SLUG = "B11", "build-run-pipeline"

W = 3400
S = 14

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "spec" / "Federation.tla").exists() and (p / "decisions").is_dir()), _HERE.parents[3])

# §10.2 "As built", at 6351039 on the record's branch: file -> the digest the record states.
ASBUILT = [
    (".github/workflows/checks.yml", "56f42cfdd435368a", "Every push to `main` and every pull request"),
    (".github/workflows/results.yml", "a21d1bd49ae033a5",
     "The suites a change touches, chosen by `tools/ci-plan.sh` (`880d7a3b83e39b5e`)"),
    (".github/workflows/sources.yml", "6de6aa2ad3817489", "On demand: `tools/check-sources.sh` (`4a3b4ef6ba95eff7`)"),
    ("tools/TLA-PIN", "3413293630da647c", "The jar's pin, which `tools/check-pins.sh` (`391fb7289dbc210f`) checks"),
    ("tools/check-results.sh", "2c6e088995f96772",
     "Regenerate and compare, over `spec/modules.tsv` (`011c990f416d8fe3`)"),
    ("tools/compare-results.py", "353afc6ccf3f4e85", "(with `tools/check-results.sh`)"),
    ("tools/ratchet.py", "2f4aa71a85cb3604", "Runs a ratcheted check on the base and on the change"),
]
# Digests the record states inside the "What it does" column, checked the same way.
ASBUILT_INNER = [("tools/ci-plan.sh", "880d7a3b83e39b5e"), ("tools/check-sources.sh", "4a3b4ef6ba95eff7"),
                 ("tools/check-pins.sh", "391fb7289dbc210f"), ("spec/modules.tsv", "011c990f416d8fe3")]
INVARIANTS = ["SignedOnlyAfterTally", "CarrierCannotPromote", "RootOnlyByIntake", "ReturnEnablesNothing",
              "ErasureReachesIngress", "GatedIntake", "OwnClassGates"]
LINT_PATH = ".claude/skills/drafting-records/scripts/record_lint.py"


# ---------------------------------------------------------------------------------------------- build-time reads
def _read(rel):
    """`rel` at PIN_G12, the commit B11 was drawn at, not the working tree (lib.py, diagrams/README.md)."""
    return read_at(ROOT, PIN_G12, rel)


def _digest(rel):
    return hashlib.sha256(_read(rel)).hexdigest()[:16]


def read_files():
    """The CI files §10.2 cites, compared with the record; spec/modules.tsv's tiers; the record lint's path; the
    workflows present; whether any module names §12's invariants. Raises when a file is missing or unparseable."""
    d = {}
    d["digests"] = {rel: _digest(rel) for rel, _, _ in ASBUILT}
    d["digests"].update({rel: _digest(rel) for rel, _ in ASBUILT_INNER})
    d["match"] = {rel: d["digests"][rel] == want for rel, want, _ in ASBUILT}
    d["match"].update({rel: d["digests"][rel] == want for rel, want in ASBUILT_INNER})
    tsv = _read("spec/modules.tsv").decode().splitlines()
    if not tsv or tsv[0].split("\t")[:4] != ["module", "runner", "rows", "tier"]:
        raise ValueError("B11: spec/modules.tsv has not the expected header")
    tiers = {}
    for ln in tsv[1:]:
        if not ln.strip():
            continue
        f = ln.split("\t")
        if len(f) < 4 or not f[3]:
            raise ValueError(f"B11: cannot parse spec/modules.tsv row {ln!r}")
        tiers.setdefault(f[3], []).append(f[0])
    if not tiers:
        raise ValueError("B11: spec/modules.tsv lists no module")
    d["tiers"] = tiers
    checks = _read(".github/workflows/checks.yml").decode()
    d["lint_at_skill"] = LINT_PATH in checks
    d["lint_in_tools"] = "tools/record_lint.py" in checks or "tools/record-lint" in checks
    wfs = [n for n in list_at(ROOT, PIN_G12, ".github/workflows") if n.endswith(".yml")]
    if not wfs:
        raise ValueError("B11: no workflow under .github/workflows")
    d["workflows"] = wfs
    d["extra_wf"] = {w: _digest(f".github/workflows/{w}") for w in wfs
                     if w not in ("checks.yml", "results.yml", "sources.yml")}
    pin = _read("tools/TLA-PIN").decode()
    m = re.search(r"^(v[\d.]+)\s+([0-9a-f]{64})\s*$", pin, re.M)
    if not m:
        raise ValueError("B11: cannot parse tools/TLA-PIN")
    d["tla_pin"] = (m.group(1), m.group(2)[:16])
    found = set()
    for name in (n for n in list_at(ROOT, PIN_G12, "spec") if n.endswith(".tla")):
        text = _read(f"spec/{name}").decode(errors="replace")
        for inv in INVARIANTS:
            if inv in text:
                found.add((name, inv))
    d["invariants_found"] = sorted(found)
    return d


# ---------------------------------------------------------------------------------------------- layout helpers
def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, measured over every card with every keyword it is drawn with.
    specs: (title, body, accent, kwargs). Returns the height."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, **k) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def status_strip(c, x0, x1, y, items):
    c.text(x0, y + 15, "Status", 15, "faint", bold=True)
    px0 = x0 + 80
    px = px0
    for lab, key, extra in items:
        lw = text_width(lab, 13.5, True) + 8
        if isinstance(key, tuple):
            plab, acc, dash = key
            pw = text_width(plab, 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > x1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if isinstance(key, tuple):
            px += c.pill(px, y, plab, acc, 11.5, dash=dash) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    return y + 42


NB = ("Not built", "red", "2 3")
NW = ("Not written", "red", "2 3")
NM = "[[red|Not met]]"


# ---------------------------------------------------------------------------------------------- the diagram
def build():
    F = read_files()
    c = Canvas(ID, "The Build-Run pipeline: one ordered path from intake to rollout, keyed by digest; Run's output "
               "re-enters only through intake and enables nothing; a carrier moves objects and decides nothing",
               "ADR-0069 (**Proposed**, 2026.11.12, revised R1 to R3 the same day; C1 to C4 attach) joins the steps "
               "that ADR-0024, ADR-0021, ADR-0044 and ADR-0031 decide into nine stages, each taking only the digest the "
               "stage before produced. Two stages are new: intake (§3, gated by §3a) and signing for every promoted "
               "class (§7). Authority runs one way; what Run produces returns as data through intake and enables nothing "
               "until a promotion. Git and GitHub are guidance (§10). **Nothing here is modelled or checked, no module is "
               "written, and the reference has no intake, no gate-evidence key, no signing stage and no pipeline around "
               "its tally.** What is built is stage 4's carrier for this repository: `checks`, `results` and `sources`, "
               "which promote nothing during genesis (§10.3). This diagram reads those files at build and compares them "
               "with the digests §10.2 states; columns headed as the diagram's are its own.",
               W, "ADR-0069 R3 (Proposed): provenance note, Status note, Context, §1 (its table, P-1 to P-4), §2, §3 "
               "(the manifest table, I-1 to I-5), §3a (the gate table IG-1 to IG-7), §4 (RR-1 to RR-4), §5 (LR-1 to "
               "LR-3), §6 (G-1 to G-4, the class table), §7 (S-1, S-2), §8, §9 (C-1 to C-5), §10.1 (the mapping "
               "table), §10.2 (the repurposing table, the As-built table, the two kinds of check, the pins, the TLC "
               "modules, the first green runs, Not yet), §10.3, §11 (the degeneracy table), §12 item by item, Options, "
               "Consequences, Open obligations, Annex A, Annex B, History; ADR-0033 §1, A6; ADR-0024 §4, A3; ADR-0045 "
               "§6, T-0045-13; ADR-0050; mechanism/GAPS-AND-ASSUMPTIONS.md I18; G12 §9 (the CI and pin tools row), "
               "items 113, 114; ToO rev 16 §7.14. Read at build and compared with §10.2: .github/workflows/checks.yml, "
               "results.yml, sources.yml and every other *.yml there; tools/TLA-PIN, check-pins.sh, check-results.sh, "
               "compare-results.py, check-sources.sh, ci-plan.sh, ratchet.py; spec/modules.tsv; every spec/*.tla "
               "(for §12's invariant names). The digest comparison and the two columns headed as the diagram's are the "
               "diagram's own; no record makes them.",
               state=STATE_G12)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    y += c.legend(X0, y, [
        ("box", "amber", "Proposed: nothing in force"), ("box", "blue", "accepted records; authority; the log"),
        ("box", "teal", "the mechanism; what is built"), ("box", "grey", "data; the carrier; external"),
        ("box", "red", "not built, not written, refused, residual"), ("box", "brown", "the custodian; humans"),
        ("box", "green", "subtraction; the safe direction"),
        ("arrow", "ink", "solid: authority or data"), ("arrow", "red", "dashed: denial, or a path that only removes", "7 5"),
    ], title="Read as") + 30

    # ---------------------------------------------------------------- status strip
    y = status_strip(c, X0, X1, y, [
        ("ADR-0069", "proposed", "2026.11.12 · R3 · C1, C2, C3, C4"),
        ("§12's module (seven invariants)", NW, ""),
        ("the reference: intake, extractor, `tally`, signing", "notbuilt", ""),
        ("gate-evidence key (G-2)", ("Not issued · D-0069-2 is today's position", "red", "2 3"), ""),
        ("Annex B's eight entries", ("Not drafted", "red", "2 3"), ""),
        ("stage 4's carrier for this repository", ("Built: checks, results, sources; promotes nothing (§10.3)",
                                                   "teal", None), ""),
        ("ADR-0035, ADR-0054 (relied on)", "proposed", ""),
        ("ADR-0050, ADR-0052 (restated)", "provisional", ""),
        ("ADR-0024, ADR-0044, ADR-0045, ADR-0033 (restated or resolved)", "accepted", ""),
    ])
    y += 6

    y += row_cards(c, X0, y, WW, 30, [
        ("Seven things the custodian settled (provenance note)", [
            "**⟨K1⟩** a new record for a Build-Run pipeline, which restates or reverses every earlier Build decision.",
            "**⟨K2⟩** generic in requirement, with specific guidance for git and GitHub.",
            "**⟨K3⟩** it repurposes f1-tla's CI/CD (three workflows at `5fe66dd`).",
            "**⟨K4⟩** the pipeline takes in what Run produces, for retraining on experience and as training data.",
            "**⟨K5⟩** intake from Run is a special case of intake, in this record.",
            "**⟨K6⟩** labelled return is a separate case.",
            "**⟨K7⟩** that Run does not adapt is cited and restated, not newly decided.",
            "Every other choice is the drafter's: (drafter's choice) where the alternative was live, (drafter's "
            "recommendation) where the custodian was asked and has not answered.",
        ], "brown", {}),
        ("Status note: four criteria attach, and what is built", [
            "**C1:** §5 puts a proof obligation on erasure, a privileged path.",
            "**C2:** §3 claims intake is the only path into a corpus root.",
            "**C3:** §7 reverses in effect ADR-0016 §1's \"Build promotion key\" (Annex B, item 1).",
            "**C4:** it resolves debts of ADR-0033 §1, ADR-0044 §4, ADR-0041 (the Build half) and ADR-0045 §6.",
            "**Built (R3):** stage 4's carrier for this repository, `checks` and `results`, green on pull requests "
            "into the record's branch \"and not yet on `main`\". **Nothing else is modelled, checked or built.**",
            "The reference has a promotion tally (`mechanism.rs`) and refuses a `Vote` until gate evidence is "
            "recorded (`mechanism/` I18), but **no pipeline around it, no intake, no gate-evidence key and no "
            "carrier configuration**. Pending: none. Deployment position: Archetype.",
        ], "amber", {"status": "proposed", "status_extra": "C1, C2, C3, C4"}),
        ("Four open questions, put 2026.11.12 and not answered (provenance note)", [
            "**The scope** (cited as \"§10.6\"; the record's §10 has §10.1 to §10.3, and no §10.6 exists in it: "
            "the diagram's observation).",
            "**Whether GitHub is a trust root** (§9; Options: not taken, drafter's recommendation).",
            "**Whether the CI runner is a principal** (§9 C-3; Options: not taken, drafter's recommendation).",
            "**Which reversals to make** (Annex A).",
            "Also unanswered: every (drafter's choice); the custodian's reading of them all is a §12 item.",
        ], "red", {"status": "open", "tint": False}),
    ]) + 44

    # ---------------------------------------------------------------- the picture: nine stages and the return path
    y = band(c, X0, y, "The path: nine stages, each taking only the digest the stage before produced (§1 ⟨K1⟩); "
                       "and the return path, which is data (§2, §4, §5)", status="proposed")
    gap = 48
    n = 9
    cw = (WW - (n - 1) * gap) / n
    xs = [X0 + i * (cw + gap) for i in range(n)]
    stages = [
        ("0 · Intake", "amber", {"status": "notbuilt", "status_extra": "no intake at the reference"}, [
            "**Takes** objects with their sources. **Produces** a corpus-root revision, promoted.",
            "**New here:** §3, §3a (its seven gates), §4, §5. The only way into a corpus root ⟨K5⟩.",
        ]),
        ("1 · Round", "blue", {}, [
            "**Takes** a corpus-root revision, a seating, a tool list. **Produces** leases at a fresh fence.",
            "Decided by ADR-0022 §2, §3; ADR-0024 A3; ADR-0048. Restated.",
        ]),
        ("2 · Author", "blue", {}, [
            "**Takes** `Read`, `Draft`, `Invoke`, `Emit`. **Produces** a workspace, round topics.",
            "Decided by ADR-0022 §1; ADR-0034 P1–P7; ADR-0021 §1. Restated.",
        ]),
        ("3 · Submit and seal", "blue", {}, [
            "**Takes** the workspace. **Produces** the artifact digest; the sealed topic-set digest.",
            "Decided by ADR-0022 §1; ADR-0021 §3; ADR-0044 §2. Restated.",
        ]),
        ("4 · Gates", "amber", {"status": "notbuilt", "status_extra": "no gate-evidence key"}, [
            "**Takes** the artifact digest. **Produces** gate evidence and its digest.",
            "**New here:** §6, who signs the evidence (G-2) and which gates each class has (G-4).",
            "**Carrier built** for this repository: `checks`, `results`, `sources` run gates and promote nothing (§10.2, "
            "§10.3).",
        ]),
        ("5 · Tally", "blue", {"status": "built", "status_extra": "the tally only: mechanism.rs, I18"}, [
            "**Takes** (artifact, evidence, epoch). **Produces** the promotion entry in the log.",
            "Decided by ADR-0024 §2, §3, §6, §8; ADR-0021 §4; ADR-0039 §3. Restated (§7).",
        ]),
        ("6 · Sign", "amber", {"status": "notbuilt", "status_extra": "a script with a secret (ADR-0033 A6)"}, [
            "**Takes** the promotion entry. **Produces** a signature over the artifact digest.",
            "**New here:** §7, every class, after its tally, and the separation S-1, S-2.",
        ]),
        ("7 · Publish", "amber", {"status": "notbuilt", "status_extra": "no pipeline around the tally"}, [
            "**Takes** the artifact and its signature. **Produces** a content-addressed copy.",
            "**New here:** §8. The location is not evidence (P-1).",
        ]),
        ("8 · Roll out", "blue", {}, [
            "**Takes** a promoted, signed revision. **Produces** leases naming it.",
            "Decided by ADR-0031; ADR-0024 §9. Restated (§8): a new revision reaches a live principal by ending its "
            "round.",
        ]),
    ]
    hs = max(c.card(0, 0, cw, t, b, draw=False, size=13.5, **k) for t, a, k, b in stages)
    for x, (t, a, k, b) in zip(xs, stages):
        c.card(x, y, cw, t, b, accent=a, size=13.5, h=hs, **k)
    ay = y + 30
    for i in range(n - 1):
        c.arrow([(xs[i] + cw, ay), (xs[i + 1], ay)], "blue", sw=2.6)
    # the return path
    lane_y = y + hs + 80
    lw2 = 2 * cw + gap
    lane = [
        (xs[1], "Extraction round (§4)", "teal", {}, [
            "**An object with `source: run` is computed from the log by an allowlisted tool in a Build round, never "
            "written by a principal.** ADR-0035 §1's \"projected from the log, not authored\", applied to data.",
            "An ordinary Build round; its artifact is the objects with the log positions they derive from. In git, "
            "a manifest change (§10.1). **IG-4 reruns the extractor at intake** (§3a).",
        ]),
        (xs[3], "What returns without a label (§4 ⟨K6⟩)", "grey", {}, [
            "A control-plane fact (ADR-0004), or a record derived only from such facts:",
            "admit decisions (ADR-0028 F1); stop attributions (F2, \"a feedback path, not merely evidence\"); "
            "promotion votes (F3); `Actuate` records, by digest (ADR-0042 §3, §4); Observer and correlator findings.",
            "**None is erasable**, so their return carries no erasure obligation.",
        ]),
        (xs[5], "Labelled return (§5 ⟨K6⟩): admits nothing today", "red", {"tint": False, "dash": "6 4"}, [
            "A Run item carrying an ADR-0047 label, or a cognitive payload: the task, a `Consult`'s content, an "
            "`Actuate`'s result, a principal's emission. Everything else a Run round holds.",
            "**Admitted only when LR-1, LR-2 and LR-3 hold. LR-1 (Build's Listener labels) is undecided, so no "
            "labelled return is admitted.** Never in git (§10.1).",
        ]),
        (xs[7], "`Run(Contain)`: what the pipeline delivers to", "teal", {}, [
            "**Run does not adapt** ⟨K7⟩: weights, a bundle, a profile or a seating that changed in Run would be one "
            "nobody promoted; the next attestation does not match it and the mechanism refuses the lease (§2).",
            "What Run holds returns to Build **as data**, and the notation `Build(Contain) → Run(Contain)` keeps its "
            "one arrow: a return path and no return arrow (§2).",
        ]),
    ]
    lh = max(c.card(0, 0, lw2, t, b, draw=False, size=13.5, **k) for _, t, a, k, b in lane)
    for x, t, a, k, b in lane:
        c.card(x, lane_y, lw2, t, b, accent=a, size=13.5, h=lh, **k)
    # stage 8 -> Run
    rx = xs[8] + cw / 2
    c.arrow([(rx, y + hs), (rx, lane_y)], "blue", sw=2.4, label="leases naming the promoted, signed revision (ADR-0031)",
            lpos=0.5, lw=cw - 20)
    # Run -> lane -> extraction round -> intake
    lane2 = lane_y + lh + 96
    run_cx = xs[7] + lw2 / 2
    ext_cx = xs[1] + lw2 / 2
    c.arrow([(run_cx, lane_y + lh), (run_cx, lane2), (ext_cx, lane2), (ext_cx, lane_y + lh)], "grey", sw=2.4,
            label="the return path: data, not authority; no arrow in the notation (§2). It enables nothing until a "
                  "round reads it and the round's artifact passes stages 3 to 8", lpos=0.5, lw=620)
    unl_cx = xs[3] + lw2 / 2
    c.arrow([(unl_cx, lane_y + lh), (unl_cx, lane2 - 4)], "grey", sw=2.2, head=False,
            label="joins the return (§4)", lpos=0.5, lw=200)
    lab_cx = xs[5] + lw2 / 2
    c.arrow([(lab_cx, lane_y + lh), (lab_cx, lane2 - 4)], "red", sw=2.2, dash="7 5", head=False,
            label="refused while LR-1 is unmet (§5)", lpos=0.5, lw=260)
    in_cx = xs[0] + cw / 2
    hseg = xs[1] - in_cx
    vseg = lane_y + lh / 2 - (y + hs)
    c.arrow([(xs[1], lane_y + lh / 2), (in_cx, lane_y + lh / 2), (in_cx, y + hs)], "grey", sw=2.4,
            label="`source: run` objects, `generatedBy` projected (RR-1), admitted as a corpus-root revision",
            lpos=(hseg + vseg * 0.45) / (hseg + vseg), lw=cw - 24)
    y = lane2 + 40
    y += c.para(X0, y, WW, "**Each solid blue arrow carries one digest, the one the stage before produced.** P-1: no "
                "stage starts on a name, and a stage refuses a digest the stage before it did not produce. P-3: the "
                "stages are not reordered. The grey path is what Run produced, admitted at stage 0 as an object in a "
                "corpus-root revision that is itself promoted through stages 1 to 8; so every lap of the loop passes "
                "the promotion gate, and the loop adds a path for influence and none for authority (§2, §4). The "
                "status pills say what the reference has: a tally, and nothing around it (Status note).",
                14.5, "muted") + 40

    # ---------------------------------------------------------------- §1 table and P-1..P-4
    y = band(c, X0, y, "§1 · The pipeline is one ordered path, keyed by digest: the record's table, whole, and "
                       "the four requirements on the path", status="proposed")
    y += c.table(X0, y, [("Stage", 230, {"bold": True}), ("Takes", 560), ("Produces", 560), ("Decided by", 880),
                         ("New here", WW - 2230)], [
        {"cells": ["0. Intake", "Objects with their sources", "A corpus-root revision, promoted", "—",
                   "**§3, §3a (its gates), §4, §5**"], "accent": "amber"},
        ["1. Round", "A corpus-root revision, a seating, a tool list", "Leases at a fresh fence",
         "ADR-0022 §2, §3; ADR-0024 A3; ADR-0048", "—"],
        ["2. Author", "`Read`, `Draft`, `Invoke`, `Emit`", "A workspace, round topics",
         "ADR-0022 §1; ADR-0034 P1–P7; ADR-0021 §1", "—"],
        ["3. Submit and seal", "The workspace", "The artifact digest; the sealed topic-set digest",
         "ADR-0022 §1; ADR-0021 §3; ADR-0044 §2", "—"],
        {"cells": ["4. Gates", "The artifact digest", "Gate evidence and its digest",
                   "ADR-0024 §4; ADR-0007; ADR-0010; ADR-0030 §5; ADR-0016; ADR-0023 §7b",
                   "**§6**: who signs the evidence, and which gates each class has (G-4)"], "accent": "amber"},
        ["5. Tally", "(artifact, evidence, epoch)", "The promotion entry in the log",
         "ADR-0024 §2, §3, §6, §8; ADR-0021 §4; ADR-0039 §3", "—"],
        {"cells": ["6. Sign", "The promotion entry", "A signature over the artifact digest", "ADR-0044 §4",
                   "**§7**: every class, and its separation"], "accent": "amber"},
        {"cells": ["7. Publish", "The artifact and its signature", "A content-addressed copy", "ADR-0044 §3",
                   "**§8**"], "accent": "amber"},
        ["8. Roll out", "A promoted, signed revision", "Leases naming it", "ADR-0031; ADR-0024 §9", "—"],
    ], size=13.5) + 24
    y += row_cards(c, X0, y, WW, 30, [
        ("P-1 · No stage starts on a name", [
            "**It starts on a digest, and refuses one the stage before it did not produce.** ADR-0044's \"A file "
            "name is no longer evidence of anything\", applied to every stage (drafter's choice).",
        ], "blue", {}),
        ("P-2 · A stage's output is a log fact or a signed object", [
            "**Either a log fact or an object signed under an issued key.** It is never a carrier's record of a step "
            "(§9).",
        ], "blue", {}),
        ("P-3 · The stages are not reordered", [
            "**Gates run before the tally** (ADR-0024 §4), **signing comes after the tally** (ADR-0044 §4). "
            "Publication follows signing, and rollout follows publication.",
        ], "blue", {}),
        ("P-4 · An artifact that stops at any stage has no egress", [
            "ADR-0039 §3 already holds this for an unsubmitted round: \"An authoring round that is never submitted "
            "has no egress\". The table restates; the new decisions are stage 0 and the rules for stages 4, 6 and 7.",
        ], "green", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §2
    y = band(c, X0, y, "§2 · Authority runs one way; what Run produces returns as data and enables nothing ⟨K4⟩ ⟨K7⟩",
             status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("The notation is ADR-0002's, unchanged", [
            "**`Build(Contain) → Run(Contain)`, with the arrow as authority flow (ADR-0001).** This record adds no "
            "arrow. A Run→Build arrow would say that Run grants Build authority, and no record allows that (Context).",
        ], "blue", {}),
        ("Restated: Run does not adapt ⟨K7⟩. Five accepted clauses settle it", [
            "ADR-0015: \"Authority changes: exactly {promotion, anchor issuance}\".",
            "ADR-0024 §1: \"Any artifact crossing from `Build` to `Run` requires promotion.\"",
            "ADR-0034 P5: a Persona's weights are part of the launch measurement.",
            "ADR-0034 P7: a change to either reference value is \"a new profile, and so a promotion\".",
            "ADR-0034 P6: \"Nothing survives except through `Submit` and `Emit`\"; the Run profile carries it over "
            "(ADR-0034 A2).",
            "**Learning from Run happens in a Build round, on data that intake admitted, and reaches Run only by "
            "promotion.**",
        ], "blue", {}),
        ("The return path ⟨K4⟩", [
            "**What Run produced enters Build only as an object admitted to a corpus root by intake (§4, §5).** It "
            "enables nothing until a round reads it and the round's artifact passes stages 3 to 8.",
            "Every lap of the loop passes the promotion gate, so the loop adds no path for authority. **What it adds "
            "is a path for influence**, and §4 and §5 bound that.",
        ], "grey", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §3
    y = band(c, X0, y, "§3 · Intake is the only way into a corpus root ⟨K5⟩: a corpus-root revision is a Build "
                       "artifact, promoted under ADR-0024 like any other", status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("The decision, and the drafter's choice", [
            "**Its content is a manifest with one line per object. Nothing else changes what a round may `Read`.** "
            "This answers the Build half of ADR-0041's open obligation, and agrees with ADR-0054's sentence on the "
            "corpus root (Proposed).",
            "(Drafter's choice: intake is a promotion. The alternative, an operator's attributed act, is in "
            "Options. Not taken because a corpus root decides the ingress of every round that pins it, and so the "
            "lineage of everything those rounds produce; ADR-0022 §3 calls the root \"the syntactic control over "
            "ingress\".)",
            "**The Run root is not decided here.** It crosses from Build to Run, so ADR-0024 §1 already requires it "
            "to be promoted; whether this manifest form is its form too is left open (Open obligations).",
        ], "amber", {}),
        ("I-1 to I-3", [
            "**I-1. An object with no source line is not admitted**, and a revision that drops a line drops the "
            "object.",
            "**I-2. An external source is pinned by digest at admission.** A check that an upstream is still served "
            "at its pin, and that no newer issue exists, reports and never edits. A finding against a pin is input to "
            "a new intake. This is f1-tla's `sources` workflow.",
            "**I-3. Intake does not judge content.** ADR-0022 §3: \"Whether the corpus is poisoned is an Observer "
            "finding, not an enforcement decision\". The intake round's Observer and the veto seats deny on it "
            "(ADR-0024 §5). The gates of §3a check the manifest's form and recompute what can be recomputed; none "
            "reads an object for its meaning.",
        ], "blue", {}),
        ("I-4, I-5", [
            "**I-4. A cognitive payload (ADR-0004) is admitted only under §5.**",
            "**I-5. A revision is classified against the one in force, by set difference on digests:** additions, "
            "removals, or both. An addition widens what a round may read, so it is the intake counterpart of a "
            "relaxation. It promotes as any artifact does, and its `generatedBy` lines feed ADR-0035's exclusion "
            "rule, which is monotone in them (drafter's choice).",
        ], "blue", {}),
    ], size=13.5) + 24
    y += c.table(X0, y, [("Field (each manifest line names)", 420, {"bold": True}), ("Content", WW - 420)], [
        ["`digest`", "SHA-256 of the object's bytes. The object's identity, as ADR-0044 §2's revision is a bundle's"],
        ["`source`", "One of `external` (with the upstream identifier and the digest it was pinned at), `promoted` "
                     "(with the promotion entry), or `run` (§4, §5)"],
        ["`generatedBy`, `curatedBy`", "The declaration ADR-0035 §1 says is made \"at corpus admission\", or the "
                                       "projection §4 requires for `run`"],
        ["`label`", "Empty, except under §5"],
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §3a
    y = band(c, X0, y, "§3a · What gates an intake (R1): seven mechanical gates, each a program named by digest, "
                       "and the residual no gate checks", status="proposed")
    y += c.card(X0, y, WW, "", [
        "**The vote on an intake opens only when all seven gates below have passed, and each has written evidence "
        "that is signed under §6 G-2,** or, while D-0069-2 holds, attributed by `AttestGates` (ADR-0050). They are "
        "mechanical, because ADR-0007 bars semantic judgment as an enabling condition. Each is a program named by "
        "digest (§6 G-1). The author of an intake is the principal that submits the manifest, and that principal is "
        "recused (ADR-0024 §6). ADR-0024 §4's two checks are ADR-0007's gates and `bundle ⊑ floor`; both are written "
        "for policy artifacts, and on a manifest they would pass on nothing. §6 G-4 says what replaces them for this "
        "class.",
    ], accent="amber", size=13.5, bullets=False) + 20
    y += c.table(X0, y, [("Gate", 230, {"bold": True}), ("Passes when", 2200), ("Enforces", WW - 2430)], [
        ["IG-1 Resolve", "Every digest in the manifest is in the store, and the stored bytes hash to it", "§3 identity"],
        ["IG-2 Complete", "Every object the revision admits has exactly one line, and every line has a `source` and "
                          "its `generatedBy` and `curatedBy` fields", "I-1"],
        ["IG-3 Pinned", "Every `external` line has an upstream identifier and the digest it was pinned at. Where the "
                        "upstream still serves the object, the runner fetches it and the bytes match. Where it does "
                        "not, the evidence says so and the line stands on its declaration (drafter's choice)", "I-2"],
        ["IG-4 Recompute", "For every `source: run` object, the allowlisted extractor named by digest is rerun on the "
                           "cited log positions, and its output has the object's digest. The `generatedBy` shares "
                           "are recomputed from the same positions and match",
         "§4 RR-1. Without this gate, \"computed, never written\" would be a claim the submitter makes"],
        ["IG-5 No payload", "No `run` object takes input from an entry in the governed store (ADR-0004) or from a "
                            "labelled item. While §5 LR-1 is unmet, no labelled object passes", "I-4, §5 LR-1"],
        ["IG-6 Labels grow", "Every object's label contains its label in Run. While IG-5 admits no labelled object, "
                             "this gate is vacuous, and its evidence says so", "§5 LR-2"],
        ["IG-7 Classify", "The additions and removals against the root in force are computed and written, with the "
                          "lineages whose `generatedBy` shares change. The gate always passes once its report exists. "
                          "At tally, an intake classified against a root that is no longer in force is refused and "
                          "gated again (drafter's choice)", "I-5; the grant seats' evidence"],
    ], size=13.5) + 24
    y += row_cards(c, X0, y, WW, 30, [
        ("IG-7's tally check keeps two intakes from racing", [
            "Each was classified against the root that was in force when it was gated. If one promotes, the other's "
            "report is stale, and the voters would be voting on a difference that no longer exists.",
        ], "blue", {}),
        ("What no gate checks: poisoning. I-3 leaves the content to the veto seats", [
            "**The Observer's coverage duty is to the seal of the intake round's topics** (ADR-0039 §3). The corpus "
            "objects are in those topics only as far as the round read them. A veto seat denies only on what it "
            "samples.",
            "**The grant seats vote on IG-7's report**, not on the data.",
            "**The first check of what the data does is Persona verification**, at the promotion of a Persona trained "
            "on it (ADR-0016). That is after the intake, and after the training.",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("A declared residual", [
            "**For a corpus of any size, intake checks where data came from and that it is what it claims to be. It "
            "does not check what the data will teach.** This is a declared residual, in the same place ADR-0022 §3 "
            "put it, and nothing here narrows it.",
            "Options rejects a content gate on intake: it would make semantic judgment an enabling condition, which "
            "ADR-0007 forbids; as a veto seat's tool it is admissible, and it subtracts only.",
        ], "red", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §4
    y = band(c, X0, y, "§4 · Intake from Run is a case of intake ⟨K5⟩: RR-1 to RR-4, and what this does not bound",
             status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("RR-1 · `generatedBy` is projected, not declared", [
            "It names the Personas whose principals' admits produced the source entries, each with its share. This "
            "gives ADR-0035's field a source in Run; that record says its rule \"applies to no lineage node today\", "
            "because every node is a Build round.",
        ], "blue", {}),
        ("RR-2 · A return is charged to every lineage named in its `generatedBy`", [
            "A successor trained on a cell's record has the cell's Thinker and its Observer both in its lineage. "
            "ADR-0035 §3's exclusion rule then decides what independence that successor can claim.",
            "A deployment that wants two lineages to stay independent admits each lineage's own record to that "
            "lineage's corpus root, and not the other's (drafter's recommendation; ADR-0017 requires \"two "
            "independent lineages\" at the archetype).",
        ], "blue", {}),
        ("RR-3 · Each object lists the findings recorded against its source rounds", [
            "So that the intake's veto seats read them. **A finding subtracts**, as ADR-0007 requires. It is never a "
            "precondition, and its absence is never a grant (drafter's choice).",
        ], "green", {}),
        ("RR-4 · Retention", [
            "The source entries keep their own horizon. The returned object is retained as a corpus object: for the "
            "production lifetime of any artifact promoted from a round that read it (ADR-0021 §7). This lengthens "
            "the life of the derived object and never that of the source topic (ADR-0003 A3).",
        ], "blue", {}),
        ("What this does not bound ⟨K4⟩: the residual", [
            "**A Byzantine Run principal can shape the record its successor trains on**: within its alphabet, it "
            "chooses what to `Consult` and what to `Actuate`. RR-1 and RR-3 make that influence visible and "
            "attributable. **Nothing in them makes it harmless.**",
            "The trained successor's behavior is checked only by Persona verification, \"a required Build gate\" "
            "(ADR-0016). ADR-0017's \"Thompson applies to the trainer\" now applies to Run as one of the trainer's "
            "sources.",
        ], "red", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §5
    y = band(c, X0, y, "§5 · Labelled return is a separate case, and admits nothing until Build labels ⟨K6⟩",
             status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("LR-1 · Build's Listener labels", [
            "ADR-0047 §9 leaves it open: \"Whether Build's Listener labels is not decided here.\" A labelled item "
            "read by an unlabelled Build round loses its label at the point it matters; an `untrusted` item would "
            "reach a Build Thinker in the clear.",
            "**Until a record decides that Build labels, no labelled return is admitted** (drafter's choice). "
            "[[red|Not decided: §5 admits nothing today.]]",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("LR-2 · The label travels, and only grows", [
            "An object's label in the corpus root contains its label in Run. An intake may add a name and never "
            "remove one (drafter's choice; the monotone direction ADR-0035 §2 takes for `ingress`). IG-6 checks it.",
        ], "blue", {}),
        ("LR-3 · Erasure follows the data: the reason C1 attaches", [
            "Each object names its erasure locus: the sealed topic, or the entry in the governed store (ADR-0004), it "
            "came from. An erasure of that locus (ADR-0006) obliges: **a new intake revision without the object**; "
            "and **for every promoted artifact whose lineage `ingress` contains it, withdrawal or a declaration**. "
            "Withdrawal means ending the rounds that name it (ADR-0031) and refusing grants that name it.",
            "Keyed on `ingress`, which ADR-0035 §2 allows to over-approximate, not on `consumed`, which must never "
            "over-approximate and so could miss an artifact (drafter's choice). **A proof obligation over a "
            "privileged path.**",
        ], "blue", {}),
        ("The forensic floor is untouched", [
            "An erasure that removes a payload leaves its F-class facts (ADR-0028 §1). A labelled return removes "
            "nothing from the log. In git, a labelled return is never stored: rewriting history to erase it would be "
            "the out-of-band deletion ADR-0006 forbids (§10.1).",
        ], "green", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §6
    y = band(c, X0, y, "§6 · A gate is a program named by digest, and its evidence counts once an issued key signs it",
             status="proposed")
    y += row_cards(c, X0, y, WW, 26, [
        ("Restated", [
            "`Vote` is enabled only after the gates pass (ADR-0024 §4): ADR-0007's totality, non-vacuity and "
            "discrimination gates; `bundle ⊑ floor` (ADR-0010), floor revisions classified mechanically (ADR-0030 "
            "§5); Persona verification (ADR-0016); the declaration check (ADR-0023 §7b).",
            "For a bundle, the gate \"reduces to the three ADR-0007 gates plus signing\" (ADR-0030).",
            "Gate evidence is recorded by an operator's `AttestGates` (ADR-0024 A3, ADR-0050): who asserted it, not "
            "whether it is true.",
        ], "blue", {}),
        ("G-1 · A gate is a program in the repository, named by digest", [
            "It runs the same way by hand and on a carrier. Its evidence is the file it writes, whose digest is "
            "ADR-0024 §3's gate-evidence digest. **A results file is never edited by hand; a rerun that changes "
            "anything is a new file** (drafter's choice; f1-tla's rule).",
        ], "amber", {}),
        ("G-2 · Evidence counts once a gate-evidence key, carried in the issued rules, signs it", [
            "ADR-0045 §6's terms for the gate runner: \"admissible as a trust root\" with \"its evidence signed by a "
            "key carried in issued rules, which ADR-0025 §1 (f) can now hold. Until that key exists, T-0045-13 is "
            "excluded\". This record names the key; issuing it is an ADR-0025 §1 (f) amendment (Annex B, item 5).",
            "[[red|Until the key is issued, T-0045-13 stays excluded and nothing here changes its class]] "
            "(D-0069-2, today's position).",
        ], "amber", {"status": "notbuilt", "status_extra": "key not issued"}),
        ("G-3 · A gate that cannot be rerun from its pin is checked for being in step, not re-derived", [
            "The pinned prover is tlapm `7824dab` (`tools/TLAPS-PIN`); its upstream tag now serves another build, and "
            "its binary is pinned for arm64-darwin. **No carrier can rerun the proofs with it unless the deployment "
            "hosts that binary.** A carrier runs `spec/proof-sync.sh` and reports which proofs are stale; the proofs "
            "are rerun where the pinned binary is.",
        ], "amber", {}),
        ("G-4 · A vote opens on its own class's gates, and a class with none stated does not promote (R1)", [
            "(Drafter's choice; the alternative is in Options.) ADR-0024 §4 states two checks for every class; "
            "they fit bundles and floors and say nothing about a manifest, a profile or a seating. A gate that says "
            "nothing about an artifact passes it, so the vote would open on nothing.",
            "A class whose row states none waits until a record writes them. Annex B, item 8, carries the change "
            "into ADR-0024 §4.",
        ], "amber", {}),
    ], size=13.5) + 24
    y += c.table(X0, y, [("Class", 300, {"bold": True}), ("Gates a record states", 1900), ("Where", WW - 2200)], [
        ["Operational bundle", "ADR-0007's three gates; `bundle ⊑ floor`; signed", "ADR-0024 §4; ADR-0030, its bundle row"],
        ["Policy-floor revision", "ADR-0030 §5's gates, and the computed classification", "ADR-0030 §5; ADR-0010 A2"],
        ["Rules-floor revision", "ADR-0007's gates on the rules floor, with an issuance alongside", "ADR-0026 §3, §4"],
        {"cells": ["Mechanism code", "**None.** A reproducible build is T-0045-30, a debt", "ADR-0045"], "accent": "red"},
        ["Persona", "Persona verification. The lineage is computed by the gate, and independence is checked in the "
                    "tally", "ADR-0016; ADR-0035 §1, §4 (Proposed); ADR-0024 A2"],
        {"cells": ["Confinement profile", "**None.** ADR-0034 states what a profile fixes, not a gate that checks it",
                   "ADR-0034 §1"], "accent": "red"},
        {"cells": ["Seating", "**None of its own.** ADR-0024 A3 records \"the gates of §4\" as run, and they do not "
                              "read a seating", "ADR-0024 A3"], "accent": "red"},
        ["Deployment declaration", "The composition note exists and states its delta. ADR-0058 adds the graph "
                                   "overlay (Proposed)", "ADR-0023 §7b; ADR-0058 §8"],
        ["Workflow", "Not re-read for this revision. ADR-0054 is Proposed", "ADR-0054"],
        {"cells": ["**Corpus-root revision**", "**IG-1 to IG-7**", "**§3a**"], "accent": "amber"},
    ], size=13.5) + 12
    y += c.para(X0, y, WW, "**Mechanism code, profiles and seatings cannot promote under this record until a record "
                "gives them gates.** During genesis, nothing promotes, so nothing waits yet (§6). Consequences: after "
                "bootstrap, that blocks every mechanism release until a code gate exists; the custodian may prefer a "
                "declared degeneracy (Options).", 14, "muted") + 40

    # ---------------------------------------------------------------- §7
    y = band(c, X0, y, "§7 · The tally is the log's; signing follows it, for every promoted artifact", status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("Restated: the tally", [
            "Unanimity over the grant seats; \"A timeout is never a grant\"; the round stalls without an independent "
            "veto seat and without coverage to the seal (ADR-0024 §2 and A2; ADR-0039 §3).",
            "A vote binds to the triple, and a change of epoch voids votes in flight (ADR-0024 §3).",
            "Author recusal is a mechanism constant (ADR-0024 §6).",
            "Votes are non-erasable; \"The authoritative vote is the admit decision in the consensus log\" (ADR-0024 §8).",
            "Every vote covers the sealed topic set (ADR-0021 §4).",
            "**Reconciled:** ADR-0024 §7 (promotion \"does not depend on\" ADR-0021) and A2 (stalls on ADR-0021 §3's "
            "seal) do not conflict: §7 is where the vote is recorded, A2 is when the tally may complete. No text "
            "changes.",
        ], "blue", {}),
        ("Signing, widened to every class: C3", [
            "ADR-0044 §4: \"The bundle key signs the revision that promotion admitted, after the tally and never "
            "before it.\" **Every artifact class promoted under ADR-0024 §1 is signed the same way:** bundles; "
            "mechanism releases; Personas; profiles; seatings; corpus-root revisions (§3); workflows, if ADR-0054 is "
            "ratified.",
            "Each is signed under an issued key, after its tally (drafter's choice; per-class keys are in "
            "Options). **This reverses in effect ADR-0016 §1**, whose Persona ID is \"Cryptographically signed by "
            "the Build promotion key\": ADR-0002 A1 struck the single human key at Build's commit point, and ADR-0025 "
            "§1 (f) lists no such key. Annex B, items 1 and 4.",
        ], "amber", {}),
        ("Separation: S-1, S-2", [
            "**S-1. The signing stage holds the key and nothing else.** It recomputes the artifact digest from the "
            "bytes, reads the promotion entry for that digest from the log, and signs only if the entry is there. No "
            "author code and no gate runs where the key is reachable.",
            "**S-2. The signature is over the digest, under domain separation**, as ADR-0044 §2 has it.",
        ], "amber", {"status": "notbuilt", "status_extra": "signing is a script with a secret (ADR-0033 A6)"}),
        ("The stronger successor, possible and not taken", [
            "ADR-0044 noted: no signature at all, with \"the mechanism checks the revision against a promotion entry "
            "in its own log\". This record makes the promotion entry name the artifact digest. **That successor is "
            "possible after this record, and it is not taken here** (Options).",
        ], "grey", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §8 and §9
    y = band(c, X0, y, "§8 · Publishing locates; rollout ends rounds — §9 · A carrier moves objects and decides nothing",
             status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("§8 · Publish and roll out", [
            "**Publishing places the artifact and its signature where nodes can fetch them by digest.** The location "
            "is not evidence (P-1). A node verifies the signature under the keys in force (ADR-0044 §3) before it "
            "loads anything.",
            "**Restated:** a new revision reaches a live principal by ending its round, and across the fleet by an "
            "epoch fence (ADR-0031). Runtime subtraction is not promotion (ADR-0024 §9). \"There is no emergency seat "
            "in Build; a promotion is Build's way to add authority\" (ADR-0052).",
            "**Restated:** the fast path for strictly subtractive bundles stays deferred (ADR-0024, Options).",
        ], "blue", {}),
        ("§9 · What a carrier is, and what it is not", [
            "**A carrier is every system that moves objects between stages or runs gates for an operator:** version "
            "control, CI runners, artifact hosting.",
            "**This record does not make a carrier a trust root** (drafter's recommendation). One of the four open "
            "questions (provenance note). GitHub as a trust root is in Options, not taken: admitting a provider's "
            "identity is an issuance a deployment may make, and would be declared.",
        ], "grey", {}),
    ], size=13.5) + 24
    y += row_cards(c, X0, y, WW, 26, [
        ("C-1 · A carrier's approval is not a vote, and its merge is not a promotion", [
            "The facts that count are the log's (ADR-0024 §8) and the issued keys' (§6, §7).",
        ], "grey", {}),
        ("C-2 · A carrier's checks may refuse and never admit", [
            "A branch rule or a required review is defence in depth: ADR-0044's Options gave OPA's signatures the "
            "same standing, \"Acceptable as an additional check\".",
        ], "green", {}),
        ("C-3 · A CI runner is not a principal", [
            "(Drafter's recommendation.) It holds no Build alphabet; it runs gates on an operator's behalf, and the "
            "operator's `AttestGates` records the result (ADR-0050). ADR-0022 §6's obligation (\"no shell, no network "
            "egress… no path into the artifactory except `Submit`\") binds Build principals, and a runner has all "
            "three. So a runner is in T-0045-13's row and counts only as G-2 allows.",
        ], "grey", {}),
        ("C-4 · Author code never runs where signing or gate-evidence keys are reachable", [
            "S-1. In GitHub terms, a job that holds a key runs no repository code except S-1's (§10.1, \"Should\").",
        ], "grey", {}),
        ("C-5 · A carrier's identifiers locate and do not identify", [
            "A commit hash, a tag or a release name points at an object. The SHA-256 in §3 and ADR-0044 §2 "
            "identifies it.",
        ], "grey", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §10.1
    y = band(c, X0, y, "§10 · Git and GitHub ⟨K2⟩ ⟨K3⟩: guidance. Its \"should\" is advice; what must be done is §1 to "
                       "§9's. §10.1 maps each generic requirement and says where GitHub stops", status="proposed")
    y += c.table(X0, y, [("Generic", 460, {"bold": True}), ("git and GitHub", 1500), ("Where it stops", WW - 1960)], [
        ["Corpus-root revision (§3)", "A manifest file in the repository, changed by pull request",
         "**The objects are not in git**, only their digests. They go in a content-addressed store"],
        ["Intake from Run (§4)", "An extraction round whose artifact is a manifest change",
         "The extractor is an allowlisted tool, not a workflow step"],
        {"cells": ["Labelled return (§5)", "**Never in git.** Rewriting history to erase it would be the out-of-band "
                                           "deletion ADR-0006 forbids", "—"], "accent": "red"},
        ["Round (§1, stage 1)", "A branch per round, in a worktree the mechanism owns",
         "A Build principal does not run git (ADR-0022: \"No shell, no package installation, no network, no git\")"],
        ["`Submit` and seal", "The mechanism commits the workspace and opens a pull request naming the artifact "
                              "digest and the sealed topic-set digest", "The pull request is a locator (C-5)"],
        ["Gates (§6)", "Required status checks: workflows that call repository scripts",
         "A check's green is the carrier's. The evidence file and its signature are what count (G-2)"],
        ["Gate evidence", "A workflow artifact, signed in a separate job under the gate-evidence key",
         "GitHub's artifact attestations may be added. They are signed under GitHub's identity and not an issued "
         "key, so they meet C-2 and not G-2"],
        ["Tally (§7)", "A required check, `tally`, that reads the log's promotion entry for the digest",
         "Reviews, CODEOWNERS and required approvals are defence in depth (C-2). GitHub's ban on approving one's own "
         "pull request echoes recusal, which is a mechanism constant"],
        ["Votes voided on change", "\"Dismiss stale approvals when new commits are pushed\"",
         "Covers a new artifact digest, not a new rules epoch. The `tally` check covers both"],
        ["Sign (§7)", "A job in a protected environment holding the key, triggered on the merged commit, which does "
                      "only S-1", "Environment reviewers approve any-of. They are not a quorum"],
        ["Publish (§8)", "A release carrying the artifact and `<digest>.sig`", "The tag locates (C-5)"],
        ["Roll out (§8)", "Outside GitHub. Nodes fetch by digest and verify", "The epoch fence is the mechanism's"],
        ["Upstream pins (I-2)", "An on-demand workflow that reports and never edits", "—"],
    ], size=13.5) + 20
    y += c.card(X0, y, WW, "Should, throughout (§10.1)", [
        "Workflows declare `permissions: contents: read` unless a job needs more.",
        "Third-party actions are pinned by commit SHA, not by tag. f1-tla pins by tag, and this is the one change to "
        "its workflows.",
        "A job that holds a key runs no repository code except S-1's.",
    ], accent="grey", size=13.5) + 44

    # ---------------------------------------------------------------- §10.2
    y = band(c, X0, y, "§10.2 · Repurposing f1-tla's workflows ⟨K3⟩: the record's table, whole", status="proposed")
    y += c.table(X0, y, [("f1-tla (at `5fe66dd`)", 1000), ("Becomes, for a TOPAK repository", 1400),
                         ("Owed", WW - 2400)], [
        ["`checks` (every push and PR, 10 minutes): the jar against `f1-tla/tools/TLA-PIN`; "
         "`f1-tla/tools/check-proofs.sh`; the incident inventory and its index",
         "`checks`:\n• the TLC jar, `tools/TLAPS-PIN` and `tools/LEAN-PIN`, each against its pin;\n• `spec/proof-sync.sh` "
         "(where f1-tla's script came from);\n• `tools/check-refs.py`;\n• the record lint;\n• `tools/verify-manifest.sh` "
         "on the latest manifest;\n• the corpus-pins drift test",
         "`tools/TLA-PIN` (TOPAK has none); the record lint moved to `tools/`"],
        ["`results` (on changes to `spec/` or `tools/`, 60 minutes): `f1-tla/tools/check-results.sh`, which "
         "regenerates each module's results and compares them with `compare-results.py`, writing nothing",
         "`results`:\n• each `spec/*-gen-results.sh` regenerated and compared;\n• `floor/run-gates.py`;\n• `cargo test` "
         "in `mechanism/`;\n• the Lean packages built at `tools/LEAN-PIN`",
         "A `spec/modules.tsv`, and `compare-results.py` ported"],
        ["`sources` (on demand): `f1-tla/tools/check-sources.py` against `f1-tla/rules/sources.tsv`",
         "`sources`:\n• the intake manifest's external pins (I-2);\n• the tlapm upstream tag against `tools/TLAPS-PIN`",
         "The intake manifest itself"],
        {"cells": ["—", "`tally`, `sign`, `publish` (§10.1)", "**All of it. Nothing in f1-tla corresponds**"],
         "accent": "red"},
    ], size=13.5) + 20
    y += c.para(X0, y, WW, "**What the carrier cannot do here** (G-3): rerun TLAPS, or the 16-minute `spec/proof-scan.sh`, "
                "with the pinned prover. `checks` reports which proofs are stale, and the proofs are rerun locally.",
                14, "muted") + 36

    # ---- as built, compared with this worktree
    y = band(c, X0, y, "§10.2 · \"As built\" (R3), at `6351039` on the record's branch: the record's table, and what "
                       "this worktree holds (the diagram's column, read at build)",
             status=None)
    c.pill(X0 + text_width("§10.2 · \"As built\" (R3), at `6351039` on the record's branch: the record's table, and what "
                           "this worktree holds (the diagram's column, read at build)", 22, True) + 20, y - 50,
           "Built: the carrier, not the reference", "teal", 11.5)
    dg = F["digests"]

    def cmp(rel, want):
        got = dg[rel]
        return f"[[teal|matches]] `{got}`" if got == want else f"[[red|differs]]: now `{got}`"

    mods = F["tiers"]
    pr_mods = mods.get("pr", [])
    other = {k: v for k, v in mods.items() if k != "pr"}
    other_s = "; ".join(f"`{k}`: {', '.join('`' + m + '`' for m in v)}" for k, v in sorted(other.items()))
    lint_s = ("still called at its skill's path (`.claude/skills/drafting-records/scripts/record_lint.py`)"
              if F["lint_at_skill"] and not F["lint_in_tools"] else
              ("moved to `tools/`" if F["lint_in_tools"] else "not called by name the diagram knows"))
    rows = [
        ["`.github/workflows/checks.yml`", "`56f42cfdd435368a`", "Every push to `main` and every pull request",
         cmp(".github/workflows/checks.yml", "56f42cfdd435368a") + f". The record lint is {lint_s}"],
        ["`.github/workflows/results.yml`", "`a21d1bd49ae033a5`",
         "The suites a change touches, chosen by `tools/ci-plan.sh` (`880d7a3b83e39b5e`)",
         cmp(".github/workflows/results.yml", "a21d1bd49ae033a5") + "; `tools/ci-plan.sh` " +
         cmp("tools/ci-plan.sh", "880d7a3b83e39b5e")],
        ["`.github/workflows/sources.yml`", "`6de6aa2ad3817489`", "On demand: `tools/check-sources.sh` (`4a3b4ef6ba95eff7`)",
         cmp(".github/workflows/sources.yml", "6de6aa2ad3817489") + "; `tools/check-sources.sh` " +
         cmp("tools/check-sources.sh", "4a3b4ef6ba95eff7") + ". G12 item 113: `sources` has never run"],
        ["`tools/TLA-PIN`", "`3413293630da647c`", "The jar's pin, which `tools/check-pins.sh` (`391fb7289dbc210f`) checks",
         cmp("tools/TLA-PIN", "3413293630da647c") + f"; it pins `{F['tla_pin'][0]}` `{F['tla_pin'][1]}`; "
         "`tools/check-pins.sh` " + cmp("tools/check-pins.sh", "391fb7289dbc210f")],
        ["`tools/check-results.sh`, `tools/compare-results.py`", "`2c6e088995f96772`, `353afc6ccf3f4e85`",
         "Regenerate and compare, over `spec/modules.tsv` (`011c990f416d8fe3`)",
         cmp("tools/check-results.sh", "2c6e088995f96772") + "; " + cmp("tools/compare-results.py", "353afc6ccf3f4e85") +
         "; `spec/modules.tsv` " + cmp("spec/modules.tsv", "011c990f416d8fe3") +
         f", listing **{len(pr_mods)} modules of tier `pr`** ({', '.join('`' + m + '`' for m in pr_mods)}); {other_s}"],
        ["`tools/ratchet.py`", "`2f4aa71a85cb3604`", "Runs a ratcheted check on the base and on the change (below)",
         cmp("tools/ratchet.py", "2f4aa71a85cb3604")],
    ]
    for w, dgs in sorted(F["extra_wf"].items()):
        rows.append({"cells": [f"`.github/workflows/{w}`", "—", "**Not in the record.** A fourth workflow; G12 items "
                               "113 and 114 name `frozen-files` (ruleset 03's status check, on every pull request)",
                               f"present, `{dgs}` (the diagram's row)"], "accent": "grey"})
    y += c.table(X0, y, [("File (the record)", 520), ("Digest (the record)", 330), ("What it does (the record)", 820),
                         ("In this worktree, 2026.11.17 (the diagram's column)", WW - 1670)], rows, size=13.5) + 24
    wf_s = ", ".join(f"`{w}`" for w in F["workflows"])
    y += row_cards(c, X0, y, WW, 26, [
        ("Two kinds of check", [
            "**Strict**, because each passed on `main` when CI was built: the jar's pin, `spec/proof-sync.sh`, "
            "`tools/verify-manifest.sh --all`.",
            "**Ratcheted**, because each already had findings: the corpus pins, `tools/lean-sync.sh`, "
            "`tools/check-refs.py`, the record lint. `tools/ratchet.py` runs a ratcheted check on the base and on "
            "the change, refuses only the findings the change adds, and lists the standing ones in the job summary: "
            "§9 C-2 applied to the carrier's own checks (drafter's choice).",
            "Consequences (R3): **a ratchet tolerates what stands.** Findings that predate CI pass every run until "
            "someone fixes them.",
        ], "grey", {}),
        ("The TLAPS and Lean pins, and TLC", [
            "**Checked where their binaries are cited**, since neither binary is tracked: `spec/proof-sync.sh` checks "
            "every proof results file names the pinned prover; `tools/lean-sync.sh` checks every `lean-toolchain` and "
            "results file against `tools/LEAN-PIN`.",
            "**TLC: 14 modules on every pull request that touches them, and Mesh on demand** (about 70 minutes). "
            "Five are not listed because their rows files are not tracked: Correlator, Emergency, Labels, Operators, "
            "ToolList; `tools/check-results.sh` gives each exclusion and its reason.",
            f"**The diagram's reading of `spec/modules.tsv` today: {len(pr_mods)} of tier `pr`** (the table above "
            "lists them). Where that is not 14, the file has moved since the record's digest.",
        ], "grey", {}),
        ("Every tool is pinned", [
            "Actions by commit SHA (the repository requires it), cvc5 1.4.0 and elan's installer by digest, Lean by "
            "`tools/LEAN-PIN`, and **Rust at 1.98.1**: `stable` moved to rustc 1.100.0 (2026.11.09), which moved test "
            "binaries out of `target/<profile>/deps`; the reference's `contain` tests find their guest relative to "
            "their own executable, so all 14 failed. The pin is a workaround; the lookup is owed a fix (Open "
            "obligations).",
        ], "grey", {}),
        ("First green runs, 2026.11.13 UTC, on pull request #50", [
            "`checks`, run 43350529281: every strict check passes, and every ratchet adds nothing.",
            "`results`, run 43350529296: all 14 TLC modules reproduce their committed results with no differences; "
            "`cargo test` passes; the three Lean packages build; the floor gates pass (\"all gates pass\": 81 cedar "
            "calls, 56 solver queries).",
            "These are the carrier's runs: **checked** is said of the gates and TLC's rows they reran, never of the "
            "pipeline, which has no module.",
        ], "teal", {}),
        ("Not yet (R3), and what the files and G12 say", [
            "**The record (R3, 2026.11.13):** the workflows are not on `main`, so a push to `main` runs nothing, and "
            "`sources` cannot be dispatched; the record lint is called at its skill's path and has not moved to "
            "`tools/`.",
            "**G12 (2026.11.16), §9 and item 113:** the CI and pin tools are measured in the corpus at the cut; "
            "\"`checks` and `frozen-files` pass on `main`; `sources` has never run\". Item 114: the required-checks "
            "ruleset (03) is disabled.",
            f"**This worktree (the diagram's):** `.github/workflows/` holds {wf_s}; the record lint is {lint_s}.",
        ], "amber", {}),
    ], size=13.5) + 24
    y += c.card(X0, y, WW, "§10.3 · The corpus repository during genesis (drafter's recommendation): gate evidence "
                            "for the custodian, and no promotion", [
        "**TOPAK's own repository runs `checks`, `results` and `sources` as gate evidence for the custodian's "
        "ratification and for the reference. During genesis they promote nothing.** Genesis ratification is the "
        "custodian's (ADR-0029 §2); no roster exists until the ceremony seats one (ADR-0029 §5, step 1); treating "
        "the custodian's merge as a promotion would make it D-0024-2, the single signer, entering unannounced, the "
        "ground on which ADR-0033 rejected promoting the reference in place.",
        "After bootstrap a record \"changes only through promotion\" (ADR-0029 §3). The same workflows then become "
        "stage 4 of the corpus's own promotions, and `tally`, `sign` and `publish` are added.",
    ], accent="brown", size=13.5, bullets=False) + 44

    # ---------------------------------------------------------------- §11
    y = band(c, X0, y, "§11 · Degeneracy on this record: the table, whole. D-0069-2 is today's position",
             status="proposed")
    y += c.table(X0, y, [("ID", 150, {"bold": True}), ("Axis", 300), ("Value", 520), ("Theorems voided", 860),
                         ("Declared consequence", WW - 1830)], [
        ["D-0069-1", "Carrier → authority", "A merge or an approval treated as a promotion",
         "§1 P-2, §9 C-1, and every theorem that assumes ADR-0024's tally",
         "The carrier's access control becomes the promotion rule. If one person can merge, this is D-0024-2"],
        {"cells": ["D-0069-2", "Gate-evidence key → absent", "Evidence attributed, not signed", "§6 G-2",
                   "T-0045-13 stays excluded, and ADR-0024 §3's gate-evidence digest is an operator's assertion. "
                   "**This is today's position**"], "accent": "red"},
        ["D-0069-3", "Intake → undeclared", "Objects admitted without source lines, or a root changed outside intake",
         "§3 I-1, §4 RR-1",
         "Lineage is declared, not projected (with D-0035-1), and a return from Run is indistinguishable from any "
         "other object"],
    ], size=13.5) + 44

    # ---------------------------------------------------------------- §12
    y = band(c, X0, y, "§12 · Ratification condition, item by item: what the record marks, and what the files show",
             status="proposed")
    inv_s = ", ".join(f"`{i}`" for i in INVARIANTS)
    if F["invariants_found"]:
        found_s = "[[red|found]] in " + ", ".join(f"`{p}` ({i})" for p, i in F["invariants_found"]) + \
                  ": the record's \"no module is written\" has moved"
    else:
        found_s = (f"No `spec/*.tla` names any of {inv_s} (every module read at build): [[red|no module is written]]")
    asb_ok = sum(1 for rel, _, _ in ASBUILT if F["match"][rel])
    mis = [rel for rel, _, _ in ASBUILT if not F["match"][rel]] + [rel for rel, _ in ASBUILT_INNER if not F["match"][rel]]
    mis_s = ("; every digest the As-built table states inside its cells matches too" if not mis else
             "; of the digests it states inside its cells, differs: " + ", ".join(f"`{m}`" for m in mis))
    y += c.table(X0, y, [("Condition (the record)", 1250), ("The record marks it", 560),
                         ("The files, 2026.11.17 (the diagram's column)", WW - 1810)], [
        ["**A module states the path and the return, and its mutations break them**, by ADR-0046's method. At "
         "least: `SignedOnlyAfterTally` (`M_SIGNEARLY`); `CarrierCannotPromote`, a havoc carrier that can merge, "
         "approve, drop and reorder causes no signature without a promotion entry (`M_MERGEISPROMOTION`); "
         "`RootOnlyByIntake` (`M_SIDEDOOR`); `ReturnEnablesNothing`, a `source: run` object enables no admit until "
         "a promotion over a round that read it (`M_RETURNGRANTS`); `ErasureReachesIngress`, after an erasure no "
         "grant names an artifact whose `ingress` held the erased object (`M_CONSUMEDONLY`); `GatedIntake` (R1): no "
         "corpus-root revision is promoted unless evidence of IG-1 to IG-7, signed or under D-0069-2 attributed, is "
         "bound to its votes, and the root in force at tally is the one IG-7 classified against (`M_UNGATED`, "
         "`M_WRITTENRETURN`, `M_STALEROOT`); `OwnClassGates` (R1): no artifact of a class whose gates are unstated "
         "is promoted (`M_VACUOUSGATE`)",
         NM + ": no module is written", found_s],
        ["**Gates are stated for mechanism code, confinement profiles and seatings** (§6 G-4), or a record says why "
         "one of them promotes without (R1)", NM + ": no record states them", "Not read by the diagram"],
        ["**A gate-evidence key is issued** under an ADR-0025 §1 (f) amendment",
         NM + ": Annex B, item 5, is owed and not drafted", "Not read by the diagram"],
        ["**The reference shows:** an intake promoted and a round pinned to it; an intake refused for each of IG-1 "
         "to IG-5 failing, and one refused at tally for IG-7's stale root (R1); a return from Run with projected "
         "`generatedBy`, which IG-4 recomputes, and a hand-edited one that it refuses (R1); a signature refused "
         "without a promotion entry; a node refusing a published artifact whose signature does not verify",
         NM + ": nothing is built",
         "The Status note: the reference has a promotion tally (`mechanism.rs`) and refuses a `Vote` until gate "
         "evidence is recorded (`mechanism/GAPS-AND-ASSUMPTIONS.md` I18), and nothing else of the path. The diagram "
         "does not read `mechanism/`"],
        ["**The repository carries `checks`, `results` and `sources` per §10.2**, and `tools/TLA-PIN`",
         "Not met, struck at R3. [[teal|Met on this record's branch]]: As built gives each file by digest; `checks` and "
         "`results` green on pull request #50 (runs 43350529281, 43350529296, 2026.11.13 UTC). " + NM +
         " on `main`: the workflows are not there, and `sources` has never run",
         f"The three workflows and `tools/TLA-PIN` are in this worktree; {asb_ok} of {len(ASBUILT)} files in the "
         f"As-built table match the record's digest{mis_s}. G12 §9 measures them in the corpus at the cut (2026.11.16) and item 113 "
         "says `checks` and `frozen-files` pass on `main` and `sources` has never run: **the \"not on `main`\" half "
         "is overtaken; the `sources` half stands**"],
        ["**The dependent entries in Annex B are drafted**, and the pins of the records they touch are moved", NM,
         "Not read by the diagram"],
        ["**ADR-0035 carries the return from Run** (Annex B, item 7)", NM, "Not read by the diagram"],
        ["**ADR-0024 §4 opens a vote on the class's own gates** (Annex B, item 8; R1)", NM, "Not read by the diagram"],
        ["**A record decides whether Build's Listener labels.** §5 admits nothing until one does; the rest of this "
         "record does not wait on it", NM, "—"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NM, "—"],
        ["**The custodian's reading of every drafter's choice and recommendation**, the four open questions of the "
         "provenance note among them", NM, "—"],
    ], size=13.5) + 44

    # ---------------------------------------------------------------- Options
    y = band(c, X0, y, "Options considered: the table, whole", status=None)
    y += c.table(X0, y, [("Option", 1000, {"bold": True}), ("Disposition", WW - 1000)], [
        ["Build → Run → Build as the notation, a return arrow",
         "Rejected (§2). The arrow is authority flow (ADR-0001), and Run grants nothing"],
        ["Online adaptation in Run, weights or memory that change across rounds without promotion",
         "Rejected by restatement (§2, ⟨K7⟩). It is an authority change outside ADR-0015's two"],
        ["Intake as an operator's attributed act, not a promotion",
         "Not taken (drafter's choice). It is cheaper, but a corpus root decides the ingress and lineage of every "
         "round that pins it. An operator's act is an assertion (ADR-0050), and this would make the corpus as strong "
         "as the weakest operator"],
        ["Intake from Run as its own record", "Not taken ⟨K5⟩"],
        ["Labelled return under the same rules as unlabelled",
         "Not taken ⟨K6⟩. Labels and erasure make it a different case (§5)"],
        ["Admit labelled return now, with labels dropped at Build",
         "Rejected (§5 LR-1). An `untrusted` item would reach a Build Thinker unmarked"],
        ["Key withdrawal on `consumed`", "Rejected (§5 LR-3). It could miss an artifact"],
        ["GitHub as a trust root: artifact attestations under GitHub's identity count as gate evidence",
         "Not taken (drafter's recommendation). ADR-0045 §6's terms ask for a key in the issued rules. Admitting a "
         "provider's identity is an issuance a deployment may make, and would be declared"],
        ["Per-class signing keys",
         "Open. One issued set for every class is the drafter's choice (§7). Per-class keys separate custody at the "
         "cost of more rows in ADR-0025 §1 (f)"],
        ["No signature: the promotion entry in the log is the identity (ADR-0044's successor)",
         "Not taken here, and made possible (§7)"],
        ["The runner as a Build principal under ADR-0022 §6",
         "Not taken (drafter's recommendation). A runner needs a shell and the network to run gates. As an "
         "operator's tool its output is attributed (C-3)"],
        ["Restating every earlier clause in prose",
         "Not taken. The restatement is Annex A's table, which cites and quotes. Prose would duplicate pinned text "
         "and drift from it"],
        ["The fast path for subtractive bundles", "Stays deferred (ADR-0024)"],
        ["Intake gated by the tally alone, as first drafted (R1)",
         "Withdrawn at R1. ADR-0024 §4's two checks say nothing about a manifest, so the vote opened on nothing, and "
         "§4 RR-1 was a claim the submitter made"],
        ["A class with no stated gate promotes on ADR-0024 §4's two checks, declared as a degeneracy (R1)",
         "Not taken (drafter's choice). A vacuous gate is the silent failure ADR-0030 closed for the floor, where "
         "\"Floor non-vacuity becomes proven\". Refusing until a gate is written fails closed, and costs nothing "
         "during genesis, when nothing promotes"],
        ["IG-3 fails a line whose upstream no longer serves it (R1)",
         "Not taken (drafter's choice). Upstreams withdraw documents, and the store already holds the bytes "
         "(IG-1). The evidence records that the fetch failed, and the voters see it"],
        ["A content gate on intake: a classifier or a model screening the corpus for poisoning (R1)",
         "Rejected. It would make semantic judgment an enabling condition, which ADR-0007 forbids. As a veto seat's "
         "tool it is admissible, and it subtracts only"],
    ], size=13.5) + 44

    # ---------------------------------------------------------------- Consequences and open obligations
    y = band(c, X0, y, "Consequences, and open obligations", status=None)
    y += row_cards(c, X0, y, WW, 30, [
        ("Positive", [
            "**The path ADR-0033 said did not exist is one object**, with each stage's owner named and two stages "
            "(intake, and signing for every class) newly decided.",
            "**The corpus root gets an admission rule**, and lineage's `generatedBy` gets a source in Run. "
            "Retraining on experience becomes a projected, attributable input and not a side channel. A return from "
            "Run is recomputed at intake (IG-4), not taken on the submitter's word (R1).",
            "**Every class's vote opens on gates that read that class** (G-4), and the classes that have none are "
            "named (R1).",
            "**A carrier can be replaced without touching a theorem.** GitHub is one instance. Every authoritative "
            "check is a script the mechanism owns, which the carrier only runs.",
            "**f1-tla's working pattern comes home**: thin workflows, scripts that run the same by hand, and results "
            "that are regenerated and compared, never edited.",
        ], "green", {}),
        ("Negative", [
            "**Every corpus change is a promotion.** A unanimous quorum per intake is slow, and that is the cost of "
            "making the root decide ingress.",
            "**The return path is a path for influence.** §4's residual stands: a Byzantine Run principal shapes its "
            "successor's data, and only Persona verification checks the result.",
            "**Labelled return waits on another record** (LR-1). Until Build labels, retraining on Run payload is not "
            "available.",
            "**Erasure grows a long tail.** An erasure can withdraw promoted artifacts (LR-3): expensive, disruptive, "
            "and the honest price of training on erasable data.",
            "**CI does not prove.** G-3 leaves the proofs to wherever the pinned prover is, and the carrier only says "
            "when they are stale.",
            "**Intake does not check what data teaches** (§3a; R1). The veto seats sample, the grant seats vote on a "
            "report, and the first behavioral check is a Persona's verification after training.",
            "**Mechanism code, profiles and seatings cannot promote until their gates are written** (G-4; R1). After "
            "bootstrap, that blocks every mechanism release until a code gate exists.",
            "**A ratchet tolerates what stands** (R3). The job summary lists the standing findings each time, which "
            "keeps them visible, and does not make them go away.",
        ], "red", {}),
        ("Open obligations", [
            "**The Run root's admission** (ADR-0041's other half): whether §3's manifest is its form.",
            "**Whether Build's Listener labels** (ADR-0047 §9). §5 waits on it.",
            "**The custody rows** for the artifact keys and the gate-evidence key, in the deployment declaration. "
            "ADR-0044's bundle-key row is still undeclared.",
            "**Annex B's entries**, drafted, with re-pins.",
            "**The module of §12**, and the reference's intake, extraction tool, `tally` check and signing stage.",
            "**Of the workflows, built (R3), what remains:** the workflows on `main`, and `sources` run once; rows "
            "files for Correlator, Emergency, Labels, Operators and ToolList, so `spec/modules.tsv` can list them; "
            "the record lint moved to `tools/`; the `contain` tests' guest lookup made independent of cargo's "
            "layout; the standing findings the ratchets list: two corpus pins (ADR-0054, ADR-0055), three Lean "
            "series, the record lint's four, and the path citations.",
            "**Hosting the pinned prover**, if a carrier is ever to rerun the proofs (G-3).",
            "**Gates for mechanism code, confinement profiles and seatings** (G-4), and a reading of ADR-0054 for a "
            "workflow's gates (R1).",
            "**The seven intake gates as programs**, and the extractor IG-4 reruns as an allowlist entry (R1).",
            "**Two questions not moved by this record:** ADR-0010's \"One floor, shared by Build and Run\" against "
            "ADR-0022's evidence pointing \"at **per class**\" (ADR-0041 leaves it with G5 item 9); and ADR-0012's "
            "\"the one artifact verified rather than promoted\", beside ADR-0010 A2's \"Policy-floor tightening is an "
            "ordinary promotion\".",
        ], "amber", {}),
    ], size=13.5) + 44

    # ---------------------------------------------------------------- Annex A
    y = band(c, X0, y, "Annex A · Disposition of every earlier Build decision ⟨K1⟩: the table, whole", status=None)
    y += c.para(X0, y, WW, "**Restated** means in force and unchanged, cited where this record relies on it. "
                "**Reversed** and **Corrected** mean an entry owed in that record (Annex B); an accepted record's text "
                "is changed only by that entry, never by this one. **Reconciled** means read together with no text "
                "change. **Not moved** means open, with its owner. A row marked (inventory) was not re-read for this "
                "draft.", 14, "muted") + 20
    y += c.table(X0, y, [("Record", 380, {"bold": True}), ("Decides", 1080), ("Status", 480), ("Here", WW - 1940)], [
        {"group": "Domain structure", "accent": "blue"},
        ["ADR-0001", "`Build → Run(Contain)`; the arrow is authority flow",
         "Accepted; its own Status note says superseded per ADR-0002",
         "Arrow restated (§2). The asymmetric form is **Corrected**: ADR-0002 asked to \"Amend it to the symmetric "
         "form\", and this was never done (Annex B, item 2)"],
        ["ADR-0002", "`Contain` at both domains; Build's commit point is a quorum (A1); evictability (A2)", "Accepted",
         "Restated (§2, §7)"],
        ["ADR-0002, ADR-0016, ADR-0017", "\"Build's membrane has no effect stream\"",
         "Accepted; overtaken by ADR-0021 §1 (B18)", "**Corrected**: errata (Annex B, item 3)"],
        ["ADR-0002; ADR-0007 (inventory)", "ADR-0007's checks are a required Build gate", "Accepted", "Restated (§6)"],
        {"group": "Build containment and alphabet", "accent": "blue"},
        ["ADR-0022 §1, §2", "Six variants; epoch and lease on every action", "Accepted", "Restated (§1, stage 2)"],
        ["ADR-0022 §3", "The corpus root is pinned and content-addressed; poisoning is an Observer finding; tool "
                        "allowlist (A3); round bound", "Accepted", "Restated. §3 adds how an object enters the root"],
        ["ADR-0022 §6", "No residual channel for Build principals", "**Proposed** (not ratified)",
         "Not moved. §9 C-3 says why a runner is not under it"],
        ["ADR-0022 §7", "`Submit` and `Vote` holders are disjoint", "Accepted", "Restated (§7)"],
        ["ADR-0022 Consequences", "Egress is `Submit` then `Vote(grant)`; \"no git\"", "Accepted", "Restated (§1, §10.1)"],
        ["ADR-0034 §1", "The profile is a promoted Build artifact; P1–P7; Build and Run share the schema", "Accepted",
         "Restated (§2 uses P5–P7). It states no gate for a profile (G-4) (R1)"],
        ["ADR-0037 §4", "Build alphabets by seat kind; `operator` (A4)", "Accepted",
         "Restated. Its `grant` row (`Read`, `Emit`, `Vote`) is wider than ADR-0024 §5's column (`Vote(grant)`, "
         "`Vote(deny)`). Reconciled: §5 lists the voting alphabet"],
        ["ADR-0040 (inventory)", "No variant name is common to Build and Run; Build's round ends at `Submit`",
         "Accepted", "Restated"],
        ["ADR-0047 §9", "Whether Build labels is not decided", "Accepted", "Not moved. §5 waits on it"],
        ["ADR-0048, ADR-0049 (inventory)", "A Build round's tool list is `ingress` and `consumed`; a Build entry has "
                                             "no channel", "Accepted", "Restated"],
        {"group": "Promotion", "accent": "blue"},
        ["ADR-0024 §1", "Everything crossing Build to Run is promoted; a promotion seats (A3)", "Accepted",
         "Restated (§1, §2)"],
        ["ADR-0024 §1 A4", "A workflow is a set of seatings and a graph", "**Pending**, not in force",
         "Not moved. A workflow travels the path like any artifact"],
        ["ADR-0024 §2", "Unanimity; a timeout is never a grant; the independence and coverage stall (A2)",
         "Accepted. A2's independence cites ADR-0035, which is Proposed", "Restated (§7)"],
        ["ADR-0024 §3, §4, §6, §8, §9", "Vote triple; gates enable votes; recusal; votes in the log; subtraction is "
                                        "not promotion", "Accepted",
         "Restated (§6, §7, §8). §4's two checks are extended by class (G-4; Annex B, item 8) (R1)"],
        ["ADR-0024 §7", "A promotion is a pipeline invocation keyed by digest; no dependence on ADR-0021", "Accepted",
         "Restated (§1). **Reconciled** with A2 (§7)"],
        ["ADR-0024 Options and degeneracies", "Fast path deferred; D-0024-1, D-0024-2", "Accepted",
         "Restated (§8, §10.3)"],
        ["ADR-0026 R1, R2, R5, R7, R9; §3 (R1); §4", "Quorum bounds; ADR-0007's gates run on the rules floor (R1); a "
                                                     "rules-floor change is two-key", "Accepted",
         "Restated (G-4's table) (R1)"],
        ["ADR-0010", "Refinement at promotion; tightening is ordinary, relaxation needs an issuance (A2); one floor",
         "Accepted", "Restated, except one floor, which is **Not moved** (Open obligations)"],
        ["ADR-0012", "The floor is verified, not promoted", "Accepted", "Not moved (Open obligations)"],
        ["ADR-0030 §5", "Floor revisions are classified mechanically; the bundle gate is three gates plus signing",
         "Accepted", "Restated (§6)"],
        {"cells": ["ADR-0016 §1", "Persona ID \"signed by the Build promotion key\"", "Accepted",
                   "**Reversed** in effect (§7; Annex B, item 1). C3"], "accent": "amber"},
        ["ADR-0016 Consequences", "Persona verification is a required Build gate", "Accepted", "Restated (§4, §6)"],
        ["ADR-0017", "Training is a Build effect; two independent lineages at the archetype", "Accepted",
         "Restated (§2, §4 RR-2)"],
        ["ADR-0023 §7b", "A declaration without its note fails at the Build promotion gate", "Accepted", "Restated (§6)"],
        ["ADR-0027", "A later release with resident rules is checked at its promotion", "Accepted", "Restated"],
        ["ADR-0029 §3, §5", "Post-bootstrap change is by promotion; the genesis bundle is never promoted", "Accepted",
         "Restated (§10.3)"],
        ["ADR-0050 (inventory)", "`AttestGates` is attributed and still an assertion", "Accepted · provisional",
         "Restated (§6)"],
        ["ADR-0052", "No emergency seat in Build", "Accepted · provisional", "Restated (§8)"],
        {"group": "Evidence, Observer, retention", "accent": "blue"},
        ["ADR-0021 §1–§7", "Build emits; a round is one pipeline invocation; seal at submission; votes cover "
                           "provenance; a cross-family, deny-only Observer; retention for the artifact's life",
         "Accepted", "Restated (§1, §4 RR-4, §7)"],
        ["ADR-0003 A3", "Retention per domain; the archive does not extend a topic", "Accepted", "Restated (§4 RR-4)"],
        ["ADR-0038 §6 (inventory)", "Every cell Observer and correlator seat in Build holds a veto", "Accepted",
         "Restated (§7)"],
        ["ADR-0039 §3", "Coverage to the seal; no cross-round rule in Build", "Accepted", "Restated (§1 P-4, §7)"],
        ["ADR-0004, ADR-0006, ADR-0028 §1", "Payload is erasable and kept apart; erasure is an event; F1–F6 survive",
         "Accepted", "Restated (§4, §5, §10.1)"],
        {"group": "Signing, keys, the trusted base", "accent": "blue"},
        ["ADR-0044 §1–§4", "Bundle keys are issued; identity is the revision; unsigned is refused; signed after the "
                           "tally", "Accepted",
         "Restated. §4 is **widened** to every promoted class (§7; Annex B, item 4)"],
        ["ADR-0025 §1 (a), (f)", "The roster is issued; the keys accepted in place of a check", "Accepted",
         "Restated. (f) gains the gate-evidence key and the artifact keys (Annex B, item 5)"],
        ["ADR-0045 §6, T-0045-13", "The gate runner's terms for becoming a trust root; T-0045-13 excluded",
         "Accepted", "Restated. §6 G-2 names the key, and the row changes class only when the key is issued"],
        {"group": "Handoff and debts", "accent": "blue"},
        ["ADR-0031", "Rollout by ending the round; the fleet by an epoch fence", "Accepted", "Restated (§8)"],
        ["ADR-0015", "Authority changes are exactly promotion and anchor issuance", "Accepted", "Restated (§2) ⟨K7⟩"],
        {"cells": ["ADR-0033", "No promotion pipeline exists; signing is a script (A6)", "Accepted",
                   "**Resolved in the record** (C4). Discharged only when built, as an ADR-0033 addendum"],
         "accent": "amber"},
        {"cells": ["ADR-0041 Open obligations", "Who admits to the corpus roots", "Accepted",
                   "Build half **Resolved** (§3). Run half Not moved"], "accent": "amber"},
        {"group": "Proposed records", "accent": "amber"},
        ["ADR-0035", "Lineage projected; `generatedBy` declared at admission; independence enforced in the tally",
         "Proposed", "Relied on. An R-revision is owed for the return from Run (Annex B, item 7)"],
        ["ADR-0036", "A profile is promoted as a one-file workspace", "Proposed", "Consistent"],
        ["ADR-0054, ADR-0055 (inventory)", "A workflow is a promoted Build artifact; Build has \"promotion into the "
                                             "corpus root\"", "Proposed", "Consistent (§3)"],
        ["ADR-0051, ADR-0056, ADR-0058, ADR-0059, ADR-0060 (inventory)",
         "A correlator's `Vote(deny)` in Build; Build entries have no credential; the gate reads the overlay; "
         "everything crossing is promoted; an autonomous plane has no Build", "Proposed", "Not moved"],
        {"group": "Mentions in passing (inventory)", "accent": "grey"},
        ["ADR-0009, ADR-0042, ADR-0043, ADR-0045 Annex B toolchain rows, ADR-0053", "(\"Build\" in ADR-0053 is a Lean "
                                                                                     "package build)", "Accepted",
         "Not moved"],
    ], size=13.5) + 44

    # ---------------------------------------------------------------- Annex B
    y = band(c, X0, y, "Annex B · Dependent entries owed: none is drafted. Each would be drafted in its own record, "
                       "pending, and each moves that record's pin", accent="red")
    y += c.table(X0, y, [("#", 60, {"bold": True}), ("Record and kind", 620), ("Content", WW - 680)], [
        ["1", "ADR-0016 §1, Persona ID row. Amendment (dependent), C3",
         "\"Cryptographically signed by the Build promotion key\" would read: signed after the tally under an "
         "artifact key in the issued rules (ADR-0044 §4 as widened by ADR-0069 §7, ADR-0025 §1 (f)); there is no "
         "Build promotion key. The note goes below the table, naming the row"],
        ["2", "ADR-0001, Decision. Amendment",
         "Carrying out ADR-0002's \"Amend it to the symmetric form before ratifying\""],
        ["3", "ADR-0002, ADR-0016 and ADR-0017. Errata",
         "On \"Build's membrane has no effect stream\": the open item was closed by ADR-0021 §1 (Batch 18)"],
        ["4", "ADR-0044 §4. Amendment (dependent)",
         "Signing at promotion covers every class promoted under ADR-0024 §1"],
        ["5", "ADR-0025 §1 (f). Amendment (dependent)",
         "The issued keys gain the gate-evidence key (ADR-0069 §6 G-2, ADR-0045 §6) and the artifact keys (§7). "
         "ADR-0025 is in the bootstrap set, so this amendment changes what genesis issues"],
        ["6", "ADR-0041, Open obligations. Amendment (dependent)",
         "The Build half of the corpus-root question is answered by ADR-0069 §3"],
        ["7", "ADR-0035. R-revision (dependent on ADR-0069, Proposed)",
         "Lineage nodes with `source: run` (§4 RR-1, RR-2), and withdrawal keyed on `ingress` (§5 LR-3)"],
        ["8", "ADR-0024 §4. Amendment (dependent) (R1)",
         "`Vote` is enabled only after the gates of the artifact's class pass, as ADR-0069 §6 G-4 lists them, and "
         "an artifact whose class has none stated is not promoted. The two checks §4 names remain the gates of a "
         "bundle. ADR-0024 is in the bootstrap set"],
    ], size=13.5, accent="red") + 12
    y += c.para(X0, y, WW, "When this record is built, ADR-0033 takes an addendum with the run, as for A6. The header "
                "also carries a debt against ADR-0016 (§7 reverses §1's signing key); ADR-0002, ADR-0016 and ADR-0017 "
                "(errata owed); ADR-0025 and ADR-0044 (amendments owed); ADR-0024 (§4, an amendment owed; R1); ADR-0035 "
                "(an R-revision owed). Resolves debts of ADR-0033, ADR-0044, ADR-0041 and ADR-0045 on ratification, and "
                "only as far as Annex B's entries and the reference carry them. Closes nothing.", 14, "muted") + 40

    # ---------------------------------------------------------------- History
    y = band(c, X0, y, "History: four rows, every one drafted by the assistant on 2026.11.12 and not reviewed",
             status=None)
    y += c.table(X0, y, [("Tag", 80, {"bold": True}), ("Kind", 220), ("Change", 2000), ("Source", 620),
                         ("State", WW - 2920)], [
        ["—", "—", "Initial draft. Build and Run are one ordered path, keyed by digest: intake, round, author, submit "
                   "and seal, gates, tally, sign, publish, roll out. Intake is the only way into a corpus root and is "
                   "a promotion. Run's output returns only through intake, as projected control-plane facts or, once "
                   "Build labels, as labelled payload whose erasure reaches every artifact with it in `ingress`. Gate "
                   "evidence counts once an issued key signs it. Every promoted class is signed after its tally, which "
                   "reverses in effect ADR-0016 §1's promotion key. A carrier decides nothing. Guidance for git and "
                   "GitHub, with f1-tla's three workflows repurposed. Annex A disposes of every earlier Build clause; "
                   "Annex B lists seven dependent entries owed",
         "The discussion of 2026.11.12; f1-tla at `5fe66dd`",
         "Drafted 2026.11.12 by the assistant at the custodian's direction, not reviewed"],
        ["R1", "Revision before ratification",
         "**Intake has gates of its own, and every class's vote opens on its own gates.** New §3a: seven mechanical "
         "intake gates. IG-1 resolves digests; IG-2 checks every object has a complete line; IG-3 checks external "
         "pins, fetching where the upstream still serves the object; IG-4 reruns the extractor on the cited log "
         "positions for every `run` object; IG-5 excludes payload; IG-6 checks labels only grow; IG-7 classifies, and "
         "an intake classified against a superseded root is refused at tally. §3a also declares the residual: no "
         "gate checks what data teaches. §3 I-3: the struck \"The gates check only the manifest's form\" is "
         "replaced. §6 gains G-4 and a gate table by class, which finds no stated gate for mechanism code, profiles "
         "or seatings; those do not promote until one is written. §1's table, §12 (`GatedIntake`, `OwnClassGates`, "
         "gates for the three classes, the reference's refusals, the ADR-0024 §4 item), Options (four rows), "
         "Consequences, Open obligations, Annex A (ADR-0024, ADR-0026, ADR-0034 rows), the header's debts and Annex "
         "B (item 8, ADR-0024 §4) follow",
         "The custodian's question of 2026.11.12, \"What gates intake?\", and instruction to make this revision. The "
         "answer found that ADR-0024 §4's two checks say nothing about a manifest",
         "Drafted 2026.11.12 by the assistant at the custodian's direction, not reviewed"],
        ["R2", "Revision before ratification",
         "**Citations of f1-tla's files name that repository.** The provenance note and §10.2's table cited "
         "f1-tla's files root-relative (tools/check-proofs.sh, tools/check-sources.py, and three more), which reads "
         "as TOPAK's own paths: two did not exist in TOPAK, and three now name TOPAK files with other digests. Each "
         "is now cited from `f1-tla/`. The struck paths are shown without code formatting, so that the path check "
         "does not read struck text as a citation. No decision text changes",
         "`checks` on PR #48, 2026.11.12: the path-citation ratchet refused the two that did not resolve",
         "Drafted 2026.11.12 by the assistant at the custodian's direction, not reviewed"],
        ["R3", "Revision before ratification",
         "**The carrier for this repository is built and running.** The Status note no longer says nothing is "
         "built. §10.2 gains \"As built\": each file by digest at `6351039`; the strict and ratcheted checks and the "
         "ratchet's rationale (§9 C-2); where the TLAPS and Lean pins are checked; which TLC modules run and why "
         "five do not; every tool pinned, with Rust at 1.98.1 after `stable` moved; the first green runs; and what "
         "is not yet done. §12's workflows item is Met on this record's branch and Not met on `main`. Consequences "
         "gain the ratchet's cost. Open obligations: the workflows item is struck, and what remains of it is listed. "
         "No decision text changes",
         "Pull requests #46, #47 and #50 into this record's branch, and runs 43350529281 (`checks`) and "
         "43350529296 (`results`) of 2026.11.13 UTC",
         "Drafted 2026.11.12 by the assistant at the custodian's direction, not reviewed"],
    ], size=13.5) + 20
    return c
