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
               "floor/README.md, floor/proposed/README.md; mechanism/README.md, mechanism/corpus-pins.sha256; slm/README.md; "
               "tools/check-refs.py; the headers of checkpoints G1–G10; G9 §9; G10 header, §1, §1.1, §1.2, §2.2, §2.9, "
               "§3, §5, §6, §7 (items 12, 14, 73, 76, 79, 86, 90, 91, 98, 99), §9; ADR-0029 A4; ADR-0030 A3; ADR-0033 "
               "A9–A15 History; ADR-0046 A1; narrative/glossary.md and narrative/architecture-description.md headers; "
               "git log 44ff854 … bd26b97; git tags G10, ToO-rev14, glossary-2026.10.05, REF-2026.10.05 … f; "
               "ToO rev 14 header, §0 and Appendix J; ADR-0053 (Proposed) §4, §6; tools/LEAN-PIN; spec/lean/README.md, "
               "mechanism/lean/README.md, floor/lean/README.md")
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
            "**Current: Genesis Checkpoint G10** (2026.10.05, tag `G10`). Each checkpoint is **one cut, never "
            "revised**: what each record says, what was ratified and by whom, what is owed, what is open, and the "
            "manifest that measures it. G10 is the first to record a **provisional** record and a "
            "**genesis-provisional** floor (ADR-0029 A4; ADR-0030 A3).",
            "Where the narrative and the checkpoint disagree, **the checkpoint wins**. G10 names ToO revision 13 as "
            "standing, not revised at G10, and behind it on labels, the tool list, operators, break-glass, the floor "
            "and the reference (items 14, 86); revision 14 is cut against G10 afterwards.",
            "`checkpoints/README.md` names G10 and holds the 2026.09.30 layout map, the one place stale paths resolve.",
        ], "blue", None, ""),
    ], "Layer 1 · state of record", "blue")
    y = b1 + 60

    b2, cy2, ch2, xs2 = row(y, [
        ("`decisions/`: the records", [
            "ADR-0001 onward, one file each, numbered in the order settled; **51 files to ADR-0052**, ADR-0014 "
            "reserved.",
            "**Never edited after ratification** except by a typed History row: an amendment, an erratum, a revision "
            "before ratification, a dependent entry, or a withdrawal (ADR-0026 W1).",
            "[[blue|Provisional]] since Batch 34: ratified, in force, subject to redesign, saying what it lacked "
            "(ADR-0029 A4): ADR-0050, ADR-0052 and four amendments that depend on them.",
            "`decisions/README.md` gives status at G10 and is a convenience; the checkpoint is the state of record.",
        ], "blue", "accepted", "C1–C4 marked"),
        ("`narrative/`: the living layer", [
            "`theory-of-operation.md`, the head: **revision 14** (2026.10.05, tag `ToO-rev14`), cut against G10; "
            "**revision 13**, against G9, stands at G10 and is what G10's manifest measures. A revision is an edit, a "
            "Changes appendix, a commit and a tag.",
            "`glossary.md`, revised in place and tagged `glossary-<date>`; 2026.10.05 against G10.",
            "`architecture-description.md`: **a draft**, revision 2 against G10, untagged; an arc42 index over the "
            "records that decides nothing. G10 measures revision 1.",
            "`revisions/`: a **closed archive** of the dated revisions before the cut (09.10 to rev 9).",
        ], "violet", None, ""),
        ("`derived/`: dated, frozen", [
            "One-shot analyses, reviews and assessments. **A derived document is never revised; a new one is "
            "written.** 29 files in G10's manifest, eight added since G9 and indexed (G10 item 12).",
            "Ten accepted records cite files here by path in their provenance notes, so names do not change.",
            "The 09.17 and 09.26 glossaries stay here, frozen, because records cite them.",
        ], "grey", None, ""),
    ], "Layer 2 · the decisions, and what explains them", "blue", rdash="10 6")
    y = b2 + 60

    b3, cy3, ch3, xs3 = row(y, [
        ("`spec/`", ["TLA+ modules **checked** in TLC at small constants, with run scripts and dated results; "
                     "**twenty-two** `*_proof.tla` modules, 5,225 obligations **proved**, **nineteen certified** "
                     "(ADR-0046 A1; `proof-certification.md`). Cited modules are frozen; a successor takes `_A1`.",
                     "`theorem-premise-binding.md` (DRAFT): no rows for six modules (G10 item 90)."],
         "teal", None, ""),
        ("`floor/`", ["The genesis floor in Cedar, DRAFT, the text the stages are built from. `floor/proposed/`: "
                      "three gated stages, `labels`, `control`, `emergency` (28 policies, 107 cases); the reference "
                      "links the last (G10 §2.2).", "Ratified when the bootstrap reviewer finds it fit. Values are "
                      "placeholders."],
         "violet", "genprov", "ADR-0030 A3"),
        ("`policies/`", ["Rego bundle-tier policies and tests (the bundle entrypoint is `policies/bundle.rego`).",
                         "Measured with `mechanism/` by the reference manifests."], "teal", None, ""),
        ("`mechanism/`", ["Rust reference implementation of the admit path. **A reference, not a deployment**; "
                          "evidence, not the verified object (ADR-0033). Rebuilt in five stages on 2026.10.05; 133 tests.",
                          "Read `GAPS-AND-ASSUMPTIONS.md` first: **not a corpus record**."], "teal", "built", ""),
        ("`slm/`", ["Small-model pre-training and the ADR-0035 §8 lineage rehearsal. **Not a corpus record.**",
                    "Proves the pipeline and the rule's mechanics, not the guarantee."], "amber", None, ""),
    ], "Layer 3 · evidence", "teal", size=13.5)
    y = b3 + 60

    b4, cy4, ch4, xs4 = row(y, [
        ("`manifests/`", ["`SHA256SUMS-*`, each cut at one commit. **Verify a manifest against the tree it measured**, "
                          "not today's: `index.tsv` names the commit. Checkpoint, reference, rehearsal, historical "
                          "kinds (table in §4).", "`EXCLUDE` states the cut rule once."], "grey", None, ""),
        ("`tools/`", ["`verify-manifest.sh --all`, `check-refs.py`, `cut-manifest.sh`; `tlc`, `tlc-workers`, "
                      "`tlapm`; the installers.", "Measured deliberately: `tla2tools.jar` (T-0045-29), `tools/cpc/` "
                      "(T-0045-14) and `TLAPS-PIN`. The scripts are excluded; the prover is not tracked (T-0045-31)."],
         "grey", None, ""),
        ("`process/`", ["One-time logs of the genesis cleanup, 2026.09.15 to 09.17: the freeze, the recovery, the "
                        "fold, the normalization, two narrative logs.", "**Nothing is added here after the cut.**"],
         "grey", None, ""),
        ("`diagrams/`", ["Diagrams and their generators, this one among them.", "Excluded from every checkpoint "
                         "manifest (`EXCLUDE`: `^diagrams/`). Drawn from the records; not one. Whether to measure "
                         "them is G10 item 76."], "grey", None, ""),
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
    y += c.heading(X0, y, "2 · The checkpoint chain G1 → G10, and the narrative beside it", size=22)
    y += 10
    dates = ["09.10", "09.11", "09.12", "09.15", "09.23", "09.25", "09.28", "09.29", "09.30", "10.01", "10.02",
             "10.02b", "10.05"]
    tg = 22
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
        ("G10", "10.05", "rev 13 stands, not revised at G10; first with a provisional record and a "
         "genesis-provisional floor", "499", "499 at `029a31b`"),
    ]
    prev = None
    for name, d, note, n, ver in cps:
        x = pos[d] - cw / 2
        x = max(X0, min(x, X1 - cw))
        acc = "blue"
        h = c.card(x, y, cw, f"{name} · 2026.{d[:5]}", [note, f"`SHA256SUMS-{name}`: {n} entries; verifies {ver}"],
                   accent=acc, size=13, tsize=15, bullets=False, tint=(name == "G10"), draw=False)
        hs = max(c.card(0, 0, cw, f"{nm} · 2026.{dd[:5]}", [nt, f"`SHA256SUMS-{nm}`: {nn} entries; verifies {vv}"],
                        size=13, tsize=15, bullets=False, draw=False) for nm, dd, nt, nn, vv in cps)
        c.card(x, y, cw, f"{name} · 2026.{d[:5]}", [note, f"`SHA256SUMS-{name}`: {n} entries; verifies {ver}"],
               accent=acc, size=13, tsize=15, bullets=False, tint=(name == "G10"), h=hs)
        c.line(pos[d], y + hs, pos[d], ay - 8, "blue", 2, dash="3 3")
        if prev:
            c.arrow([(prev + 2, y + 26), (x - 3, y + 26)], "blue", sw=2)
        prev = x + cw
    c.card(X0, y, 3 * cw + 2 * tg, "Before G1", [
        "The first cut of all is the v1 corpus manifest (2026.09.15). Until G1 the Theory of Operation carried the "
        "state of record itself: G1 superseded manifest v1 in full and, as state of record, the 09.15 ToO rev 4's "
        "ledger, ADR log, open list, genesis plan and next steps; rev 4 stayed in force as narrative (G1 header).",
    ], accent="grey", size=13.5, bullets=False, h=hs, dash="6 4")
    c.pill(X1 - 4, y - 32, "G10: current state of record", "blue", 12.5, solid=True, anchor="end")
    # narrative revisions below the axis
    ny = ay + 52
    revs = [("09.10", "ToO 2026.09.10"), ("09.11", "ToO 09.11"), ("09.12", "ToO 09.12"),
            ("09.15", "ToO 09.15 and rev 5"), ("09.23", "rev 6"), ("09.25", "rev 7"), ("09.28", "rev 8"),
            ("09.29", "rev 9"), ("09.30", "rev 10 (the head's bytes at the cut; tag `ToO-rev10`)"),
            ("10.01", "**rev 11**: the first revision made as an edit; cut from G7 (tag `ToO-rev11`)"),
            ("10.02", "**rev 12**, against G8 (G8 item 72; tag `ToO-rev12`): MAP 2.3 struck; the words proved and "
                      "checked"),
            ("10.02b", "**rev 13**, against G9 (tag `ToO-rev13`): leases above rung 0; measured by G10"),
            ("10.05", "**rev 14**, the head, against G10 (tag `ToO-rev14`): labels, operators, break-glass as a "
                      "seating; §2.10, §7.10 new")]
    for d, lab in revs:
        x = pos[d] - cw / 2
        x = max(X0, min(x, X1 - cw))
        head = d in ("09.30", "10.01", "10.02", "10.02b", "10.05")
        c.line(pos[d], ay + 34, pos[d], ny, "violet", 1.6, dash="3 3")
        c.card(x, ny, cw, None, [lab + ("" if head else " · `narrative/revisions/`")], accent="violet",
               size=13, bullets=False, tint=head, h=96, dash=None if head else "6 4")
    c.text(X0, ny + 128, "Narrative revisions (violet): the nine dated files before the cut sit in `narrative/revisions/`, "
           "byte-identical moves, six of them from before git; revisions 7 to 14 are tagged `ToO-rev7` … `ToO-rev14`.",
           14, "muted")
    y = ny + 158

    # ================================================================ 3. how a change flows
    y += c.heading(X0, y, "3 · How a change moves through the corpus", size=22)
    y += 12
    steps = [
        ("1 · Draft", ["A record is drafted and revised **in place** while Proposed: History rows R1, R2 …, each "
                       "\"Applied — Proposed record, revised in place\".", "Status: Proposed (ADR-0035, 0036, 0051; "
                       "ADR-0022 §6 at G10)."], "amber", "proposed", ""),
        ("2 · Ratify, in a batch", ["The genesis custodian ratifies under ADR-0029 §2, in numbered batches (G9: "
                                    "Batch 26; G10: Batches 27–35, on two days).", "Accepted (genesis); a "
                                    "confirmation-required marker C1–C4 when the first post-bootstrap quorum must review "
                                    "it (ADR-0029 §4); **provisional** when it did not meet its own ratification "
                                    "condition and says what it lacked (A4)."],
         "blue", "accepted", "C1–C4 · or provisional"),
        ("3 · After ratification", ["Only typed History rows: an **amendment** (A1 …), an **erratum** (E1 …), or a "
                                    "**dependent entry** (B22 …) when another record's ratification touches it.",
                                    "A dependent amendment is drafted to be applied as marked, beside the text it "
                                    "changes (G10 §5); none is pending at G10. A pending amendment may be **withdrawn** "
                                    "(ADR-0026 W1)."], "blue", None, ""),
        ("4 · Checkpoint cut", ["Gn supersedes Gn−1 as the state of record: ratifications, ledger, open list. "
                                "`tools/cut-manifest.sh` cuts `SHA256SUMS-Gn` under `EXCLUDE`; `index.tsv` gains a "
                                "row naming the commit; a tag `Gn`."], "blue", None, ""),
        ("5 · Narrative revision", ["The ToO is edited against the checkpoint, with a \"Changes from revision N\" "
                                    "appendix, a commit and a tag `ToO-revN`; the glossary is revised in place. Until "
                                    "then the checkpoint wins (G10 item 86 owes rev 14 against G10)."], "violet", None, ""),
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
    y += c.para(X0, y, W, "Example, G10 (2026.10.04–05): ADR-0005 ratified alone in Batch 27 (`44ff854`) → "
                "Batches 28 to 31, among them ADR-0033 A7 ratified ahead of ADR-0036 and the Run profile (`9b3cecd`, "
                "`efd83b9`) → the reference rebuilt in five stages to records then Proposed, each with an ADR-0033 "
                "addendum and a manifest, `SHA256SUMS-REF-2026.10.05` to `-05e` (`7764e52`, `c15026d`, `c7de2ba`, "
                "`9c57221`, `7d8c7db`); A9 accepted alone in Batch 32 → Batch 33, the race (`65185ed`) → Batch 34, five "
                "records, two provisional, and twenty-six dependent amendments applied as marked (`075b2e7`) → Batch 35 "
                "(`e4b174e`) → G10 cut, `SHA256SUMS-G10`, 499 entries (`029a31b`) → ToO revision 14, the glossary, the "
                "architecture description's revision 2, the reviewer's guide and G10's index row (`bd26b97`). "
                "`SHA256SUMS-G9` fails at G10's tree, by construction.",
                14.5, "ink") + 40

    # ================================================================ 4. tables
    y += c.heading(X0, y, "4 · The layout, and what measures each part", size=22)
    lay = [
        ["`decisions/`", "Architecture decision records, ADR-0001 onward ([index](decisions/README.md))",
         "Immutable after ratification but for typed History rows", "checkpoint manifest: 51 records"],
        ["`checkpoints/`", "Genesis checkpoints, the state of record; the layout map from the 2026.09.30 cut",
         "One cut each, never revised", "checkpoint manifest: 11 (v1 and G1–G10)"],
        ["`narrative/`", "The living layer: the ToO and the glossary, cut with each checkpoint; the architecture "
         "description, a draft; the closed archive of earlier revisions", "Head edited per revision and tagged; "
         "`revisions/` closed", "checkpoint manifest: 12 (G9's 11 and `architecture-description.md`)"],
        ["`spec/`", "TLA+ modules and twenty-two proof modules, run scripts, generators and checkers, the binding table, "
         "the method and certification notes, dated TLC, proof and certified-proof results, trace results; since "
         "2026.10.05 `lean/`, fourteen modules re-encoded in Lean ([[amber|ADR-0053, Proposed]])",
         "Cited modules and proof modules frozen (successors `_A1`); results never change; `Mechanism.tla` pinned, "
         "not frozen; Lean re-encodings frozen with their modules on ADR-0053's ratification",
         "checkpoint manifest: 172; `lean/` enters the next (ADR-0053 §6)"],
        ["`floor/`", "The genesis policy floor in Cedar, with tests and gates, and three proposed stages under "
         "`proposed/`; since 2026.10.05 `lean/`, the genesis floor in Cedar's Lean model ([[amber|ADR-0053, "
         "Proposed]])", "Genesis text DRAFT; the floor in force genesis-provisional (ADR-0030 A3); dated gate runs "
         "never change", "checkpoint manifest: 146 (fourteen under `floor/proposed/`)"],
        ["`policies/`", "Rego bundle-tier policies and tests", "Reference material", "`SHA256SUMS-REF-<date>`"],
        ["`mechanism/`", "Rust reference implementation of the admit path; since 2026.10.05 `lean/`, `admit.rs` and "
         "`clock.rs` and the floor wrapper transcribed and proved in Lean, the decision a step of `FloorComposition` "
         "([[amber|ADR-0053, Proposed]])", "Evidence, not the verified "
         "object; pins what it follows; the Lean transcriptions are pinned to the Rust by digest, not frozen", "`SHA256SUMS-REF-<date>` (sixteen cuts)"],
        ["`slm/`", "Small-model pre-training and the ADR-0035 lineage rehearsal", "Not a corpus record",
         "`SHA256SUMS-SLM-2026.09.28`"],
        ["`derived/`", "Dated, frozen analyses, reviews and assessments", "Never revised; a new one is written",
         "checkpoint manifest: 29"],
        ["`manifests/`", "Digest manifests for checkpoint, reference and rehearsal cuts, with an index", "A manifest is "
         "verified at the commit it measured", "G10 measures 17: the sixteen REF manifests and the SLM manifest; not "
         "`index.tsv`, not earlier checkpoint manifests"],
        ["`process/`", "The genesis cleanup's process logs", "Closed: nothing added after the cut",
         "checkpoint manifest: 6"],
        ["`tools/`", "The TLC jar and wrappers, the TLAPS wrapper, the installers, and the manifest and reference "
         "checkers; since 2026.10.05 `LEAN-PIN`, `install-lean.sh`, `lean-report.sh` and `lean-sync.sh` "
         "([[amber|ADR-0053, Proposed]])", "Scripts excluded; the prover binary and the Lean toolchain not tracked",
         "checkpoint manifest: 55 (the jar, the 53 files of `tools/cpc/`, `TLAPS-PIN`); `LEAN-PIN` enters the next"],
        ["`diagrams/`", "Diagrams and their generators", "Derived from the records", "excluded"],
    ]
    for r in lay:
        r[1] = r[1].replace(" ([index](decisions/README.md))", "")
    wl = W * 0.58
    ty = y
    h1 = c.table(X0, ty, [("Path (README.md)", 190), ("Contents (README.md)", wl * 0.40), ("Rule", wl * 0.30),
                          ("Measured by (G10 §9; EXCLUDE)", wl - 190 - wl * 0.70)], lay, size=13.5, accent="blue")
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
        ["`-REF-2026.10.02`", "reference", "10.02", "`c536e21`", "82", "82", "ADR-0033 A7 (B29): the launcher"],
        ["`-REF-2026.10.02b`", "reference", "10.02", "`c534a42`", "84", "84", "ADR-0033 A8 (B31): Run's tools"],
        ["`-G9`", "checkpoint", "10.02", "`97a61e8`", "392", "392", "first with a lease above rung 0 at the "
         "reference (rung 1; rung 3 SIMULATED)"],
        ["`-REF-2026.10.05`", "reference", "10.05", "`7764e52`", "86", "86", "ADR-0033 A9 (B32): target from the "
         "entry; genesis floor"],
        ["`-REF-2026.10.05b`", "reference", "10.05", "`c15026d`", "87", "87", "A10 (B34): labels; the `labels` stage"],
        ["`-REF-2026.10.05c`", "reference", "10.05", "`c7de2ba`", "89", "89", "A11 (B34): operators; the `control` "
         "stage"],
        ["`-REF-2026.10.05d`", "reference", "10.05", "`9c57221`", "90", "90", "A12 (B34): the emergency seating; the "
         "`emergency` stage"],
        ["`-REF-2026.10.05e`", "reference", "10.05", "`7d8c7db`", "90", "90", "A13 (B33): the race; A14 (B34): trace "
         "validation"],
        ["`-REF-2026.10.05f`", "reference", "10.05", "`075b2e7`", "90", "90", "A15 (B35): the two issued lists"],
        ["`-G10`", "checkpoint", "10.05", "`029a31b`", "499", "499", "first with a provisional record and a "
         "genesis-provisional floor; `REVIEWERS_GUIDE_README.md` excluded"],
    ]
    wr = W - wl - 40
    h2 = c.table(X0 + wl + 40, ty, [("Manifest (`index.tsv`)", wr * 0.21), ("Kind", wr * 0.12), ("Cut", wr * 0.07),
                                    ("Commit", wr * 0.11), ("Entries", wr * 0.08), ("Verify", wr * 0.08),
                                    ("Note", wr * 0.33)], idx, size=13, accent="grey")
    ty0, ty = ty, ty + h1 + 30

    # status, layout map, tools
    ha = c.table(X0, ty, [("Record status at G10 (§1.1)", wl * 0.30), ("Count", wl * 0.08), ("Records", wl * 0.62)], [
        ["Accepted (genesis)", "18", "0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part), 0019, 0020, "
         "0022 (in part: §6 Proposed), 0024, 0025, 0026, 0027, 0032, 0033"],
        ["Accepted (genesis) · confirmation required", "26", "0003 (A2 only), **0005**, 0006, 0009, 0013, 0015, 0021, "
         "0023, 0028, 0029 (A2, A4 only), 0030, 0031 (C2 for A1 only), 0034, 0037, 0038, 0039, 0040, 0041, 0042 (now "
         "whole), 0043, 0044, 0045, 0046, **0047, 0048, 0049**"],
        {"cells": ["Accepted (genesis) · **provisional** (confirmation required)", "2", "**0050, 0052**"],
         "accent": "blue"},
        {"cells": ["Proposed", "3", "0035, 0036, 0051; and ADR-0022 §6"], "accent": "amber"},
        ["Superseded", "1", "0008, by 0038"],
        ["Tombstone", "1", "0011"],
        ["Reserved, no file", "1", "0014"],
        ["Pending amendments", "0", "none, down from four; ADR-0026 A1 (R8) **withdrawn** (W1)"],
        ["Provisional amendments", "4", "0024 A3, 0025 A3, 0026 A2 (bootstrap set); 0029 A3"],
    ], size=13.5, accent="blue")
    y = max(ty + ha, ty0 + h2) + 40
    w3 = (W - 30) / 2
    ty = y
    hb = c.table(X0, ty, [("Was (before 2026.09.30)", w3 * 0.5), ("Is now", w3 * 0.5)], [
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
    hc = c.table(X0 + w3 + 30, ty, [("Tool (`tools/`)", w3 * 0.36), ("What it does", w3 * 0.64)], [
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
        ["`TLAPS-PIN`", "The pinned prover; the wrapper refuses another binary (G10 item 73). Measured from G10"],
    ], size=13, accent="grey")
    y = ty + max(hb, hc) + 40

    w2 = (W - 30) / 2
    hh = c.card(X0, y, w2, "Two kinds of manifest failure that are correct", [
        "`SHA256SUMS-G9` fails at G10's tree by construction (twenty-six records changed, with the narrative, the "
        "binding table's neighbours under `spec/`, `Mechanism.tla` and the trace scripts) and verifies 392 of 392 at "
        "`97a61e8` (G10 §9).",
        "`SHA256SUMS-REF-2026.10.05f` fails two entries at G10's tree, the pin file and the register, which moved "
        "after `075b2e7`; 90 of 90 there. Each earlier reference manifest of 10.05 fails more and verifies whole at "
        "its own commit.",
        "Frozen records that cite pre-move paths are not edited: their digests are pinned. Two such citations are "
        "knowingly left stale and resolve through the layout map.",
    ], accent="grey", size=14)
    c.card(X0 + w2 + 30, y, w2, "Pointers still behind the state of record", [
        "G10's header names revision 13 as the standing narrative; revision 14 is written against G10 afterwards "
        "(items 14, 86). The tags item 86 owed, `G10`, `ToO-rev14`, `glossary-2026.10.05` and `REF-2026.10.05` to "
        "`-05f`, are made.",
        "The floor stages open with a comment that is wrong, \"not what the reference follows\" (G10 item 91); "
        "`floor/README.md` says the reference links the `labels` stage, where it links `emergency` (G10 §2.2), and "
        "that `T_persona` is not yet read, where it is (ADR-0033 A6); two policy comments call ADR-0049 Proposed "
        "(item 98).",
        "`decisions/README.md` gives status at G10 under a column still headed \"Status at G8\". "
        "`REVIEWERS_GUIDE_README.md` is kept current outside the manifest (item 99).",
    ], accent="amber", size=14, h=hh)
    return c
