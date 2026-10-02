"""H1 — Corpus structure: the repository's layers, their precedence, how a change flows through them, and what
measures each one."""
from lib import Canvas, wrap, render_line, text_width

ID, SLUG = "H1", "corpus-structure"


def build():
    c = Canvas(ID, "The corpus: layers, precedence, and how a change moves through them",
               "TOPAK is a design corpus in its genesis phase. The checkpoint is the state of record and wins over the "
               "narrative; records are immutable after ratification except by typed History rows; the narrative and "
               "the glossary are cut with each checkpoint; derived analyses are dated and frozen; specifications, the "
               "floor, the reference and the rehearsal are evidence; manifests measure every cut at the commit it "
               "measured, and the reference pins what it follows.",
               3200,
               "README.md; checkpoints/README.md; narrative/README.md; decisions/README.md; derived/README.md; "
               "manifests/README.md, manifests/index.tsv, manifests/EXCLUDE; process/README.md; spec/README.md; "
               "floor/README.md; mechanism/README.md, mechanism/corpus-pins.sha256; slm/README.md; tools/check-refs.py; "
               "the headers of checkpoints G1–G9; G8 §1, §5, §9; G9 header, §1, §1.1, §1.2, §2.9, §5, §6, §7 (items 12, "
               "14, 63, 71, 72, 76, 77, 79), §9; ADR-0033 A7, A8 History; ADR-0034 A2 History; ADR-0046 E1; "
               "narrative/glossary.md header; git log 4b417ba … 9e811bc; ToO rev 13 header and §0")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ================================================================ 1. precedence
    y += c.heading(X0, y, "1 · Precedence: who wins, who explains, who is evidence, who measures", size=22)
    y += 16
    G = 30

    def row(y, items, region_label, region_acc, pad=26, size=14, rdash=None):
        n = len(items)
        cw = (W - 2 * pad - G * (n - 1)) / n
        h = max(c.card(0, 0, cw, t, b, accent=a, draw=False, size=size, status=s, status_extra=se)
                for t, b, a, s, se in items)
        top = y
        yy = y + 36
        xs = []
        for i, (t, b, a, s, se) in enumerate(items):
            x = X0 + pad + i * (cw + G)
            c.card(x, yy, cw, t, b, accent=a, h=h, size=size, status=s, status_extra=se)
            xs.append((x, cw))
        bottom = yy + h + 22
        c.region(X0, top, W, bottom - top, region_label, region_acc, dash=rdash, sw=2, size=15)
        return bottom, yy, h, xs

    b1, cy1, ch1, xs1 = row(y, [
        ("`checkpoints/`: the state of record", [
            "**Current: Genesis Checkpoint G9** (2026.10.02, tag `G9`). Each checkpoint is **one cut, never revised**: "
            "what each record says, what was ratified and by whom, what is owed, what is open, and the manifest that "
            "measures it.",
            "Where the narrative and the checkpoint disagree, **the checkpoint wins**. G9 names ToO revision 12 as "
            "standing, not revised at G9, and wins over it where it says every lease the reference issues is rung 0 "
            "(items 14, 79); revision 13 is cut against G9 afterwards.",
            "`checkpoints/README.md` is the 2026.09.30 layout map, the one place stale paths resolve.",
        ], "blue", None, ""),
    ], "Layer 1 · state of record", "blue")
    y = b1 + 60

    b2, cy2, ch2, xs2 = row(y, [
        ("`decisions/`: the records", [
            "ADR-0001 onward, one file each, numbered in the order settled; 45 files to ADR-0046, ADR-0014 reserved.",
            "**Never edited after ratification** except by a typed History row: an amendment, an erratum, a revision "
            "before ratification, or a dependent entry when another record's ratification touches it.",
            "`decisions/README.md` gives status (still headed G8) and is a convenience; the checkpoint is the state of "
            "record.",
        ], "blue", "accepted", "C1–C4 marked"),
        ("`narrative/`: the living layer", [
            "`theory-of-operation.md`, the head: **revision 13** (2026.10.02, tag `ToO-rev13`), cut against G9; "
            "**revision 12**, against G8, stands at G9 (G9 header). A revision is an edit, a Changes appendix, a commit "
            "and a tag.",
            "`glossary.md`, revised in place and tagged `glossary-<date>`; revised twice on 2026.10.02, against G8 and "
            "against G9 (tag `glossary-2026.10.02b`, owed; a second revision on one date takes a suffix).",
            "`revisions/`: a **closed archive** of the dated revisions before the cut (09.10 to rev 9); nothing is "
            "added after the cut.",
        ], "violet", None, ""),
        ("`derived/`: dated, frozen", [
            "One-shot analyses, reviews and assessments. **A derived document is never revised; a new one is "
            "written.** 21 files in G9's manifest, every one in the derived index (item 77 closed with G9); new: "
            "`topak-contain-wrapper-design-2026.10.02.md`.",
            "Ten accepted records cite files here by path in their provenance notes, so names do not change.",
            "The 09.17 and 09.26 glossaries stay here, frozen, because records cite them.",
        ], "grey", None, ""),
    ], "Layer 2 · the decisions, and what explains them", "blue", rdash="10 6")
    y = b2 + 60

    b3, cy3, ch3, xs3 = row(y, [
        ("`spec/`", ["TLA+ modules **checked** in TLC at small constants, with run scripts, the converter and dated "
                     "results; **fifteen** `*_proof.tla` modules whose invariants TLAPS **proves** (thirteen at G8, "
                     "ADR-0046), with dated proof results and `proof-method.md`. Cited modules and proofs are frozen; a "
                     "change is a successor module.", "`theorem-premise-binding.md`: the table ADR-0045 §3 owes (DRAFT, revised again at G9)."],
         "teal", None, ""),
        ("`floor/`", ["The genesis policy floor in Cedar, with tests and gates, the proof-checking wrapper and six dated "
                      "gate runs.", "**DRAFT · not ratified.** Every number in the values file is a placeholder."],
         "violet", "draft", ""),
        ("`policies/`", ["Rego bundle-tier policies and tests (the bundle entrypoint is `policies/bundle.rego`).",
                         "Measured with `mechanism/` by the reference manifests."], "teal", None, ""),
        ("`mechanism/`", ["Rust reference implementation of the admit path. **A reference, not a deployment**; "
                          "evidence, not the verified object (ADR-0033).", "Read `GAPS-AND-ASSUMPTIONS.md` first: "
                          "**not a corpus record**."], "teal", "built", ""),
        ("`slm/`", ["Small-model pre-training and the ADR-0035 §8 lineage rehearsal. **Not a corpus record.**",
                    "Proves the pipeline and the rule's mechanics, not the guarantee."], "amber", None, ""),
    ], "Layer 3 · evidence", "teal", size=13.5)
    y = b3 + 60

    b4, cy4, ch4, xs4 = row(y, [
        ("`manifests/`", ["`SHA256SUMS-*`, each cut at one commit. **Verify a manifest against the tree it measured**, "
                          "not today's: `index.tsv` names the commit. Checkpoint, reference, rehearsal, historical "
                          "kinds (table in §4).", "`EXCLUDE` states the cut rule once."], "grey", None, ""),
        ("`tools/`", ["`verify-manifest.sh --all`, `check-refs.py`, `cut-manifest.sh`; `tlc`, `tlc-workers`, "
                      "`tlapm`; the installers.", "Measured deliberately: `tla2tools.jar` (T-0045-29) and `tools/cpc/` "
                      "(T-0045-14). The scripts are excluded; the prover is not tracked (T-0045-31)."],
         "grey", None, ""),
        ("`process/`", ["One-time logs of the genesis cleanup, 2026.09.15 to 09.17: the freeze, the recovery, the "
                        "fold, the normalization, two narrative logs.", "**Nothing is added here after the cut.**"],
         "grey", None, ""),
        ("`diagrams/`", ["Diagrams and their generators, this one among them.", "Excluded from every checkpoint "
                         "manifest (`EXCLUDE`: `^diagrams/`). Drawn from the records; not one. Whether to measure "
                         "them is G9 item 76."], "grey", None, ""),
    ], "Layer 4 · integrity, tooling and history", "grey", rdash="10 6", size=13.5)
    y = b4 + 30

    # arrows between layers, with labels
    def down(x, ya, yb, acc, label, dash=None, lpos=0.5):
        c.arrow([(x, ya), (x, yb)], acc, dash=dash, label=label, lpos=0.36, sw=2.2)
    cx_ = X0 + W / 2
    down(X0 + W * 0.18, b1 + 2, b1 + 60 + 34, "blue", "states each record's status; wins on conflict")
    down(X0 + W * 0.5, b1 + 2, b1 + 60 + 34, "violet", "narrative cut from the checkpoint", "7 5")
    down(X0 + W * 0.82, b1 + 2, b1 + 60 + 34, "grey", "measured by its manifest")
    down(X0 + W * 0.18, b2 + 2, b2 + 60 + 34, "teal", "records cite modules and runs by digest")
    down(X0 + W * 0.5, b2 + 2, b2 + 60 + 34, "teal", "`corpus-pins.sha256`: the reference pins records")
    down(X0 + W * 0.82, b2 + 2, b2 + 60 + 34, "grey", "ADR-0033 addenda cite REF manifests")
    down(X0 + W * 0.18, b3 + 2, b3 + 60 + 34, "grey", "measured by checkpoint, REF and SLM manifests")
    down(X0 + W * 0.82, b3 + 2, b3 + 60 + 34, "grey", "`check-refs.py` checks every cited path")
    y += 30

    # ================================================================ 2. checkpoint chain and narrative revisions
    y += c.heading(X0, y, "2 · The checkpoint chain G1 → G9, and the narrative beside it", size=22)
    y += 10
    dates = ["09.10", "09.11", "09.12", "09.15", "09.23", "09.25", "09.28", "09.29", "09.30", "10.01", "10.02",
             "10.02b"]
    tg = 26
    cw = (W - tg * (len(dates) - 1)) / len(dates)
    step = cw + tg
    pos = {d: X0 + cw / 2 + i * step for i, d in enumerate(dates)}
    # axis
    ay = y + 210
    c.line(X0 + 20, ay, X1 - 20, ay, "muted", 2)
    for d in dates:
        c.line(pos[d], ay - 6, pos[d], ay + 6, "muted", 2)
        c.text(pos[d], ay + 26, "2026." + d[:5], 13, "muted", anchor="middle", bold=True)
    cps = [
        ("G1", "09.15", "cleanup step 5; supersedes corpus manifest v1", "49", "29 at `8fdbe97` (pre-git)"),
        ("G2", "09.23", "narrative: rev 6", "64", "60 at `8fdbe97` (pre-git)"),
        ("G3", "09.25", "narrative: rev 6, rev 7 owed", "86", "86 at `27ea3ff`"),
        ("G4", "09.28", "narrative: rev 8, cut with it", "108", "108 at `7542730`"),
        ("G5", "09.29", "narrative: rev 9, cut with it", "130", "130 at `64e5413`"),
        ("G6", "09.30", "narrative: rev 10, cut with it; cut before the reorganization", "159",
         "159 at `5244aab`; first with the TLC jar"),
        ("G7", "10.01", "rev 10 stands, not revised at G7; first cut under the new layout", "336",
         "336 at `97d1b81`; measures `tools/cpc/`"),
        ("G8", "10.02", "rev 11 stands, not revised at G8; first with proofs and a prover row (ADR-0046)", "372",
         "372 at `1151832`"),
        ("G9", "10.02b", "rev 12 stands, not revised at G9; first with a lease above rung 0 at the reference", "392",
         "392 at `97a61e8`"),
    ]
    prev = None
    for name, d, note, n, ver in cps:
        x = pos[d] - cw / 2
        x = max(X0, min(x, X1 - cw))
        acc = "blue"
        h = c.card(x, y, cw, f"{name} · 2026.{d[:5]}", [note, f"`SHA256SUMS-{name}`: {n} entries; verifies {ver}"],
                   accent=acc, size=13, tsize=15, bullets=False, tint=(name == "G9"), draw=False)
        hs = max(c.card(0, 0, cw, f"{nm} · 2026.{dd[:5]}", [nt, f"`SHA256SUMS-{nm}`: {nn} entries; verifies {vv}"],
                        size=13, tsize=15, bullets=False, draw=False) for nm, dd, nt, nn, vv in cps)
        c.card(x, y, cw, f"{name} · 2026.{d[:5]}", [note, f"`SHA256SUMS-{name}`: {n} entries; verifies {ver}"],
               accent=acc, size=13, tsize=15, bullets=False, tint=(name == "G9"), h=hs)
        c.line(pos[d], y + hs, pos[d], ay - 8, "blue", 2, dash="3 3")
        if prev:
            c.arrow([(prev + 2, y + 26), (x - 3, y + 26)], "blue", sw=2)
        prev = x + cw
    c.card(X0, y, 3 * cw + 2 * tg, "Before G1", [
        "The first cut of all is the v1 corpus manifest (2026.09.15). Until G1 the Theory of Operation carried the "
        "state of record itself: G1 superseded manifest v1 in full and, as state of record, the 09.15 ToO rev 4's "
        "ledger, ADR log, open list, genesis plan and next steps; rev 4 stayed in force as narrative (G1 header).",
    ], accent="grey", size=13.5, bullets=False, h=hs, dash="6 4")
    c.pill(X1 - 4, y - 32, "G9: current state of record", "blue", 12.5, solid=True, anchor="end")
    # narrative revisions below the axis
    ny = ay + 52
    revs = [("09.10", "ToO 2026.09.10"), ("09.11", "ToO 09.11"), ("09.12", "ToO 09.12"),
            ("09.15", "ToO 09.15 and rev 5"), ("09.23", "rev 6"), ("09.25", "rev 7"), ("09.28", "rev 8"),
            ("09.29", "rev 9"), ("09.30", "rev 10 (the head's bytes at the cut; tag `ToO-rev10`)"),
            ("10.01", "**rev 11**: the first revision made as an edit; cut from G7 (tag `ToO-rev11`)"),
            ("10.02", "**rev 12**, against G8 (G8 item 72; tag `ToO-rev12`): MAP 2.3 struck; the words proved and "
                      "checked"),
            ("10.02b", "**rev 13**, the head, against G9 (tag `ToO-rev13`): leases above rung 0; the "
                       "Run profile draft")]
    for d, lab in revs:
        x = pos[d] - cw / 2
        x = max(X0, min(x, X1 - cw))
        head = d in ("09.30", "10.01", "10.02", "10.02b")
        c.line(pos[d], ay + 34, pos[d], ny, "violet", 1.6, dash="3 3")
        c.card(x, ny, cw, None, [lab + ("" if head else " · `narrative/revisions/`")], accent="violet",
               size=13, bullets=False, tint=head, h=96, dash=None if head else "6 4")
    c.text(X0, ny + 128, "Narrative revisions (violet): the nine dated files before the cut sit in `narrative/revisions/`, "
           "byte-identical moves, six of them from before git; revisions 7 to 13 are tagged `ToO-rev7` … `ToO-rev13`.",
           14, "muted")
    y = ny + 158

    # ================================================================ 3. how a change flows
    y += c.heading(X0, y, "3 · How a change moves through the corpus", size=22)
    y += 12
    steps = [
        ("1 · Draft", ["A record is drafted and revised **in place** while Proposed: History rows R1, R2 …, each "
                       "\"Applied — Proposed record, revised in place\".", "Status: Proposed (ADR-0005, 0035, 0036; "
                       "ADR-0042 §6 at G9)."], "amber", "proposed", ""),
        ("2 · Ratify, in a batch", ["The genesis custodian ratifies under ADR-0029 §2, in numbered batches (G7: "
                                    "Batches 22–24, one day; G8: Batch 25; G9: Batch 26).", "Accepted (genesis); a confirmation-required marker "
                                    "C1–C4 when the first post-bootstrap quorum must review it (ADR-0029 §4)."],
         "blue", "accepted", "C1–C4"),
        ("3 · After ratification", ["Only typed History rows: an **amendment** (A1 …), an **erratum** (E1 …), or a "
                                    "**dependent entry** (B22 …) when another record's ratification touches it.",
                                    "A dependent entry may change an Annex B row's class (G7 §5). A **pending** amendment is marked inline "
                                    "and not applied (G9 §5)."], "blue", None, ""),
        ("4 · Checkpoint cut", ["Gn supersedes Gn−1 as the state of record: ratifications, ledger, open list. "
                                "`tools/cut-manifest.sh` cuts `SHA256SUMS-Gn` under `EXCLUDE`; `index.tsv` gains a "
                                "row naming the commit; a tag `Gn`."], "blue", None, ""),
        ("5 · Narrative revision", ["The ToO is edited against the checkpoint, with a \"Changes from revision N\" "
                                    "appendix, a commit and a tag `ToO-revN`; the glossary is revised in place. Until "
                                    "then the checkpoint wins (G9 item 79 owes rev 13 against G9)."], "violet", None, ""),
        ("6 · Re-pin", ["`mechanism/corpus-pins.sha256`: the drift test fails when a pinned record moves; review, bring "
                        "the code into line or register the divergence, then replace the pin line.",
                        "An ADR-0033 addendum cites the new `SHA256SUMS-REF-<date>`."], "teal", "built", ""),
    ]
    n = len(steps)
    gap = 46
    sw_ = (W - gap * (n - 1)) / n
    hh = max(c.card(0, 0, sw_, t, b, accent=a, status=s, status_extra=se, draw=False, size=14, bullets=False)
             for t, b, a, s, se in steps)
    for i, (t, b, a, s, se) in enumerate(steps):
        x = X0 + i * (sw_ + gap)
        c.card(x, y, sw_, t, b, accent=a, status=s, status_extra=se, h=hh, size=14, bullets=False)
        if i < n - 1:
            c.arrow([(x + sw_ + 2, y + 34), (x + sw_ + gap - 3, y + 34)], "grey", sw=2.2)
    y += hh + 20
    y += c.para(X0, y, W, "Example, G9 (2026.10.02): ADR-0046 E1, an erratum, ratified alone in Batch 26 "
                "(`4b417ba`) → the launcher built at the reference (`c536e21`) and its addendum drafted as ADR-0033 A7, "
                "pending, citing `SHA256SUMS-REF-2026.10.02` (`441b56d`) → the Run profile drafted as ADR-0034 A2, "
                "marked inline and not applied (`ec08884`) → Run's tools built (`c534a42`) and ADR-0033 A8 drafted, "
                "pending, citing `SHA256SUMS-REF-2026.10.02b`, with the ADR-0033 pin replaced (`66b8e55`) → G9 cut, "
                "`SHA256SUMS-G9`, 392 entries (`97a61e8`), and its index row (`a15f7f1`) → ToO revision 13 and the "
                "glossary against G9 (`9e811bc`). `SHA256SUMS-G8` fails 14 entries at G9's tree, by construction.",
                14.5, "ink") + 40

    # ================================================================ 4. tables
    y += c.heading(X0, y, "4 · The layout, and what measures each part", size=22)
    lay = [
        ["`decisions/`", "Architecture decision records, ADR-0001 onward ([index](decisions/README.md))",
         "Immutable after ratification but for typed History rows", "checkpoint manifest: 45 records"],
        ["`checkpoints/`", "Genesis checkpoints, the state of record; the layout map from the 2026.09.30 cut",
         "One cut each, never revised", "checkpoint manifest: 10 (v1 and G1–G9)"],
        ["`narrative/`", "The living layer: the ToO and the glossary, cut with each checkpoint, and the closed archive "
         "of earlier revisions", "Head edited per revision and tagged; `revisions/` closed", "checkpoint manifest: 11"],
        ["`spec/`", "TLA+ modules and fifteen proof modules, run scripts, generators and checkers, the binding table, "
         "the method note, dated TLC and proof results", "Cited modules and proof modules frozen (successor modules); "
         "results never change; `Mechanism.tla` pinned, not frozen", "checkpoint manifest: 102"],
        ["`floor/`", "Draft genesis policy floor in Cedar, with tests and gates", "DRAFT; dated gate runs never change",
         "checkpoint manifest: 132 (118 the evidence tree)"],
        ["`policies/`", "Rego bundle-tier policies and tests", "Reference material", "`SHA256SUMS-REF-<date>`"],
        ["`mechanism/`", "Rust reference implementation of the admit path", "Evidence, not the verified object; pins "
         "what it follows", "`SHA256SUMS-REF-<date>` (ten cuts)"],
        ["`slm/`", "Small-model pre-training and the ADR-0035 lineage rehearsal", "Not a corpus record",
         "`SHA256SUMS-SLM-2026.09.28`"],
        ["`derived/`", "Dated, frozen analyses, reviews and assessments", "Never revised; a new one is written",
         "checkpoint manifest: 21"],
        ["`manifests/`", "Digest manifests for checkpoint, reference and rehearsal cuts, with an index", "A manifest is "
         "verified at the commit it measured", "G9 measures 11: the ten REF manifests and the SLM manifest; not `index.tsv`, "
         "not earlier checkpoint manifests"],
        ["`process/`", "The genesis cleanup's process logs", "Closed: nothing added after the cut",
         "checkpoint manifest: 6"],
        ["`tools/`", "The TLC jar and wrappers, the TLAPS wrapper, the installers, and the manifest and reference "
         "checkers", "Scripts excluded; the prover binary not tracked", "checkpoint manifest: 54 (the jar and the 53 "
         "files of `tools/cpc/`)"],
        ["`diagrams/`", "Diagrams and their generators", "Derived from the records", "excluded"],
    ]
    for r in lay:
        r[1] = r[1].replace(" ([index](decisions/README.md))", "")
    wl = W * 0.58
    ty = y
    h1 = c.table(X0, ty, [("Path (README.md)", 190), ("Contents (README.md)", wl * 0.40), ("Rule", wl * 0.30),
                          ("Measured by (G9 §9; EXCLUDE)", wl - 190 - wl * 0.70)], lay, size=13.5, accent="blue")
    idx = [
        ["`SHA256SUMS`", "historical", "09.15", "—", "60", "—", "pre-layout flat paths; the record of its cut"],
        ["`-G1`", "checkpoint", "09.15", "`8fdbe97`", "49", "29", "pre-git; the nearest tree"],
        ["`-G2`", "checkpoint", "09.23", "`8fdbe97`", "64", "60", "pre-git; four records changed 09.23–09.25"],
        ["`-G3`", "checkpoint", "09.25", "`27ea3ff`", "86", "86", ""],
        ["`-G4`", "checkpoint", "09.28", "`7542730`", "108", "108", ""],
        ["`-G5`", "checkpoint", "09.29", "`64e5413`", "130", "130", ""],
        ["`-G6`", "checkpoint", "09.30", "`5244aab`", "159", "159", "first with `tools/tla2tools.jar`; pre-cut paths"],
        ["`-REF-2026.09.24`", "reference", "09.24", "`4fd9677`", "59", "59", "ADR-0033 §7"],
        ["`-REF-2026.09.25`", "reference", "09.25", "`453801c`", "61", "61", "ADR-0033 §7 R13"],
        ["`-REF-2026.09.28`", "reference", "09.28", "`5b25245`", "61", "61", "ADR-0033 A1"],
        ["`-REF-2026.09.29`", "reference", "09.29", "`7f74c0b`", "62", "62", "ADR-0033 A2"],
        ["`-REF-2026.09.29b`", "reference", "09.29", "`1e6c0c4`", "65", "64", "A3; pin file moved after the cut"],
        ["`-REF-2026.09.30`", "reference", "09.30", "`fb40db1`", "65", "65", "ADR-0033 A4"],
        ["`-REF-2026.09.30b`", "reference", "09.30", "`8cf9bd1`", "66", "66", "A5; the pin moved in the next commit"],
        ["`-SLM-2026.09.28`", "rehearsal", "09.28", "`7542730`", "40", "40", "ADR-0035 §8"],
        ["`-REF-2026.10.01`", "reference", "10.01", "`dacbb0c`", "66", "66", "A6; the pin moves in the next commit"],
        ["`-G7`", "checkpoint", "10.01", "`97d1b81`", "336", "336", "first cut under the new layout; measures `tools/cpc`"],
        ["`-G8`", "checkpoint", "10.02", "`1151832`", "372", "372", "first with a prover in the trusted base "
         "(T-0045-31); `tools/tlapm` excluded"],
        ["`-REF-2026.10.02`", "reference", "10.02", "`c536e21`", "82", "82", "ADR-0033 A7 (pending): the launcher"],
        ["`-REF-2026.10.02b`", "reference", "10.02", "`c534a42`", "84", "84", "ADR-0033 A8 (pending): Run's tools"],
        ["`-G9`", "checkpoint", "10.02", "`97a61e8`", "392", "392", "first with a lease above rung 0 at the "
         "reference (rung 1; rung 3 SIMULATED)"],
    ]
    wr = W - wl - 40
    h2 = c.table(X0 + wl + 40, ty, [("Manifest (`index.tsv`)", wr * 0.21), ("Kind", wr * 0.12), ("Cut", wr * 0.07),
                                    ("Commit", wr * 0.11), ("Entries", wr * 0.08), ("Verify", wr * 0.08),
                                    ("Note", wr * 0.33)], idx, size=13, accent="grey")
    y = ty + max(h1, h2) + 40

    # status, layout map, tools
    w3 = (W - 2 * 30) / 3
    ty = y
    ha = c.table(X0, ty, [("Record status at G9 (§1.1)", w3 * 0.42), ("Count", w3 * 0.13), ("Records", w3 * 0.45)], [
        ["Accepted (genesis)", "18", "0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part), 0019, 0020, "
         "0022 (in part), 0024, 0025, 0026, 0027, 0032, 0033"],
        ["Accepted (genesis) · confirmation required", "22", "0003 (A2 only), 0006, 0009, 0013, 0015, 0021, 0023, "
         "0028, 0029 (A2 only), 0030, 0031, 0034, 0037, 0038, 0039, 0040, 0041, 0042 (in part), 0043, 0044, 0045, "
         "0046; as at G8"],
        ["Proposed", "3", "0005, 0035, 0036; and ADR-0042 §6"],
        ["Superseded", "1", "0008, by 0038"],
        ["Tombstone", "1", "0011"],
        ["Reserved, no file", "1", "0014"],
        ["Pending amendments", "4", "0026 A1 (R8); 0033 **A7**, **A8**; 0034 **A2** (C2, C4)"],
    ], size=13.5, accent="blue")
    hb = c.table(X0 + w3 + 30, ty, [("Was (before 2026.09.30)", w3 * 0.5), ("Is now", w3 * 0.5)], [
        ["`SHA256SUMS*` at the root (fifteen files)", "`manifests/<same name>`"],
        ["the six process logs (FOLD-LOG, FREEZE-AND-BATCH-A, two NARRATIVE-LOGs, NORMALIZATION-LOG, "
         "RECOVERY-REGISTRY)", "`process/<same name>`"],
        ["`tlc`, `tlc-workers`, `install-tla.sh`", "`tools/<same name>`; the wrappers find the jar beside them"],
        ["`checkpoints/topak-theory-of-operation-2026.09.30-rev10.md`", "`narrative/theory-of-operation.md` (the head)"],
        ["the nine earlier ToO files in `checkpoints/`", "`narrative/revisions/<same name>`"],
        ["`derived/topak-glossary-2026.09.29.md`", "`narrative/glossary.md` (the head)"],
        ["`derived/topak-rung-DAG-2016.09.27.md`", "`…-2026.09.27.md` (a year typo)"],
        ["`derived/topak-gaps-prioritization-2026-09-28.md`", "`…-2026.09.28.md` (the dated-name convention)"],
    ], size=13, accent="grey")
    hc = c.table(X0 + 2 * (w3 + 30), ty, [("Tool (`tools/`)", w3 * 0.36), ("What it does", w3 * 0.64)], [
        ["`verify-manifest.sh --all`", "Reads `index.tsv` and checks every manifest at its commit; "
         "`verify-manifest.sh SHA256SUMS-G6 5244aab` checks one"],
        ["`check-refs.py`", "Walks every tracked `.md`; checks each backticked root-relative path exists; flags dates "
         "not `20YY.MM.DD`. Run at every cut. Does not read the binding table"],
        ["`cut-manifest.sh`", "Cuts a manifest under the rule `manifests/EXCLUDE` states once"],
        ["`tlc`, `tlc-workers`", "Wrap TLC over the tracked `tla2tools.jar`; each module has a `*-run.sh` in `spec/`"],
        ["`tlapm`", "Wraps the TLA+ Proof System; `spec/proof-results.sh` runs it per proof module (excluded from the "
         "manifest, G8 §5)"],
        ["`install-tlaps.sh`", "Installs the pinned prover, `tlapm` 1.6.0-pre at `7824dab`, beside the wrapper "
         "(1.9 GB, not tracked; T-0045-31)"],
        ["`install-tla.sh`", "Downloads a jar; run it only to reinstall the pinned digest (T-0045-29)"],
        ["`install-ethos.sh`", "Builds the pinned proof checker `ethos` 8dc85c4 (binary not tracked)"],
        ["`tla2tools.jar`, `cpc/`", "Measured: the TLC jar (since G6) and the CPC rule signature (from G7)"],
    ], size=13, accent="grey")
    y = ty + max(ha, hb, hc) + 40

    w2 = (W - 30) / 2
    hh = c.card(X0, y, w2, "Two kinds of manifest failure that are correct", [
        "`SHA256SUMS-G8` fails 14 entries at G9's tree by construction (ADR-0033 A7, A8, ADR-0034 A2, ADR-0046 E1; "
        "the ToO and glossary revised after its cut; nine files under `spec/`) and verifies 372 of 372 at "
        "`1151832` (G9 §9).",
        "`SHA256SUMS-REF-2026.10.02b` fails two entries at G9's tree, the pin file and the register, which moved "
        "after `c534a42`; 84 of 84 there. `-REF-2026.10.02` fails 18; 82 of 82 at `c536e21`.",
        "Frozen records that cite pre-move paths are not edited: their digests are pinned. Two such citations are "
        "knowingly left stale and resolve through the layout map.",
    ], accent="grey", size=14)
    c.card(X0 + w2 + 30, y, w2, "Pointers still behind the state of record, as the records say", [
        "G9's header names revision 12 as the standing narrative; revision 13 is written against G9 afterwards "
        "(items 14, 79). `ToO-rev13` is made; `glossary-2026.10.02b`, which the glossary cites, is owed.",
        "`mechanism/GAPS-AND-ASSUMPTIONS.md` names G9 and revision 12 in its header (item 71, discharged at G9), "
        "and `decisions/README.md` still gives status at G8.",
        "`floor/README.md` says `T_persona` is not yet read by the reference; G7 §2.2 says it now is (ADR-0033 A6).",
    ], accent="amber", size=14, h=hh)
    return c
