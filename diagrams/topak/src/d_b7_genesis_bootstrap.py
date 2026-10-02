"""B7 — From genesis to bootstrap: the state of record at G8 (ADR-0029 with A1, A2)."""
from lib import Canvas, text_width

ID, SLUG = "B7", "genesis-to-bootstrap"

# The 22 confirmation-required records at G8 (G8 §1.1, §4; ToO rev 11 §9; each record's Status note).
CONF = [
    ("ADR-0003", "Topic per principal per round, sealed on emit, as the unit of erasure", "C1 · **A2 only**",
     "09.11; A2 Batch 5 (09.25)", "A2 adds the `after` companion topic to the unit of erasure: a claim over the "
     "erasure path"),
    ("ADR-0006", "Erasure is a privileged, modeled, consensus-ordered event", "C1, C4 via 0013", "09.12",
     "Marked retroactively under C1 (ADR-0029 §4 minimum set); its debt resolved by ADR-0013"),
    ("ADR-0009", "Break-glass is a modeled, quorum-witnessed path, not a prohibition", "C1, C4 via 0013", "09.12",
     "As ADR-0006: a privileged path; its debt resolved by ADR-0013"),
    ("ADR-0013", "Exception mechanism for privileged paths through the floor", "C1, C4", "09.23 · B4",
     "Proof obligation over privileged paths; resolves the debts of 0006 and 0009. NC-1 and NC-2 checked and, since "
     "B25, proved; author-run"),
    ("ADR-0015", "Effects are boundary crossings; every crossing is authorized, ordered, and auditable", "C2",
     "09.23 · B3", "Both sets claimed exhaustive; the effect set's exhaustiveness unenforced while the sandbox gap "
     "stands"),
    ("ADR-0021", "Build emits to the effect stream; Build has an Observer", "C4", "09.30 · B18",
     "ADR-0039 §3, accepted, couples Build's promotion to the seal this record defines"),
    ("ADR-0023", "Degeneracy as the deployment-variation relation; archetype as its unique maximum", "C3",
     "09.23 · B3", "§5 reverses in effect ADR-0008's Observer scoping and ADR-0017's ordering-primacy clause"),
    ("ADR-0028", "The forensic floor: authority facts survive erasure and break-glass", "C1", "09.23 · B4",
     "Proof obligation over privileged paths; four open obligations carried into confirmation"),
    ("ADR-0029", "The design process is genesis; unilateral ratification; bootstrap on a drafted TLA+ spec",
     "C3 · **A2 only**", "09.15; A2 09.25", "A2 reverses in effect two clauses of this record: the full-corpus "
     "review"),
    ("ADR-0030", "Bundles cannot add authority by construction; the floor runs on a verified evaluator", "C1",
     "09.25 · B6; A1 B24", "Floor exceptions and forensic classes re-expressed in the floor language; now carries A1, "
     "the checker as a trust root and the solver trusted for nothing"),
    ("ADR-0031", "The lease is the composite credential, and its grant is the instant", "C1; C2 for A1 only",
     "09.25 · B5; A1 B10", "§5 lapses break-glass approvals on a targeted revocation; A1 says how a confinement "
     "claim survives renewal"),
    ("ADR-0034", "Confinement is attested at lease grant; the archetype rung is a confidential VM", "C2, C4",
     "09.28 · B10", "A confinement claim; resolves ADR-0031's attestation-rung debt"),
    ("ADR-0037", "The LTRO decomposes into principals: seats and stages", "C3, C4", "09.29 · B12",
     "§3 reverses in effect ADR-0018's Reader scope correction; resolves seat-scoping debts"),
    ("ADR-0038", "Observers are per cell, the shared group becomes the correlator", "C3, C4", "09.29 · B13",
     "Supersedes ADR-0008; discharges ADR-0023's carried scope for that supersession"),
    ("ADR-0039", "Observer liveness is progress, not presence", "C4", "09.29 · B14",
     "Resolves ADR-0024's open obligation on veto-seat outage"),
    ("ADR-0040", "Run has its own alphabet: `Consult`, `Actuate`, `Report`", "C3, C4", "09.30 · B20",
     "Reverses in effect ADR-0022 §5's sentence that `Read` and `Emit` are common; resolves ADR-0030's debt"),
    ("ADR-0041", "Policy obligations for Run: one envelope per variant, coupling on effects only", "C1, C4",
     "09.30 · B20", "§3 restates break-glass over a renamed action; resolves ADR-0039 finding 2"),
    ("ADR-0042", "Mechanism obligations for Run (§1–§5, §7, §8 only; **§6 Proposed**)", "C4 (§6 would carry C2)",
     "09.30 · B20", "Resolves ADR-0039 finding 3 in part; §6, Run's confinement claim, left out of ratification"),
    ("ADR-0043", "Cell obligations for Run", "C4", "09.30 · B20",
     "Resolves the provisional Run column of ADR-0037 §4"),
    ("ADR-0044", "A bundle is trusted by its signature, not its file name", "C1", "09.30 · B17",
     "§3 is a check on the privileged path. **Drafted by the assistant**"),
    ("ADR-0045", "The trusted base is declared row by row", "C2, C4", "10.01 · B22",
     "Annex A claims to enumerate what the theorems assume; resolves debts of 0030, 0034, 0036, 0037, 0042, 0043. "
     "**Drafted by the assistant**; new at G7. T-0045-31 added by its B25 dependent entry"),
    ("ADR-0046", "The formal layer's method is declared: TLC checks mutations and witnesses at small constants, TLAPS "
     "proves the invariants, and the prover is a trusted-base row", "C2, C4", "10.02 · B25",
     "§4 claims that every invariant the thirteen modules state is proved (exhaustiveness); resolves MAP 2.3 and the "
     "method half of CR-4. **Drafted by the assistant**; new at G8"),
]


def build():
    c = Canvas(ID, "From genesis to bootstrap: where the corpus stands at G8",
               "The design process is genesis, not a degeneracy (ADR-0029): one custodian ratifies, the risky part is "
               "tracked as debt, and the anchor may bootstrap once a drafted TLA+ specification exists and the whole "
               "corpus has been independently reviewed. This is the G8 state (2026.10.02); "
               "`diagrams/g1-to-bootstrap-2026.09.18.svg` shows the earlier G1 state.",
               3200, "ADR-0029 §1–§7, A1, A2 (A2.1–A2.5), Options, Consequences; ADR-0024 §6; ADR-0025 Annex A-0025; "
               "ADR-0026 §2 R2, R5, §6 finding 5, §7 finding 3; ADR-0027 §2, §4; ADR-0035 Status note; ADR-0045 "
               "Annex A, T-0045-31; ADR-0046 §4, B25; every listed record's Status line and Status note; decisions/README.md; "
               "G8 header, §1, §1.1, §1.2, §4, §6, §7 items 8, 66, 74, §8; ToO rev 11 §0, §7.1, §7.4, §9; "
               "spec/README.md; spec/bootstrap-results-2026.09.23.txt; spec/Anchor-proof-results-2026.10.02.txt, "
               "spec/BreakGlass-proof-results-2026.10.02.txt")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y + 20

    # ------------------------------------------------------------------ row 1: the four phases
    pw = (W - 3 * 140) / 4
    phases = [
        ("Genesis · now", "brown", [
            "Custody declared: **Scott, sole custodian, (1, 0)** (§1). Genesis custody, not a degeneracy: no archetype "
            "custody exists before the anchor does.",
            "**Unilateral ratification** of any record with decision text (§2); a record without it cannot be "
            "ratified. Ratification is available, not required.",
            "Everything ratified is **trusted by declaration** and joins the genesis TCB.",
            "No forcing function (§7): genesis may last indefinitely; every checkpoint carries a debt ledger.",
        ]),
        ("Bootstrap trigger · not met", "red", [
            "**(a)** a drafted TLA+ bootstrap specification: five modules, five invariants, a mutation each that must "
            "fail (§5). TLC checking recommended, not required. **Two of five drafted, checked and, since G8, proved** "
            "(ADR-0046 §4).",
            "**(b)** an **independent review of the entire corpus** at one named manifest digest, by at least one "
            "reviewer who is not the author, every finding dispositioned (A2.1). **Not met**: nothing at G8 is "
            "independently reviewed (G8 §8).",
            "**Permission, not obligation**: bootstrap happens when the custodian declares it **and** the trigger is "
            "met (§7).",
        ]),
        ("Ceremony · epoch 0", "blue", [
            "Seat the key-holders under a declared custody record.",
            "Assemble the **genesis bundle** (contents below).",
            "**Every key-holder signs its digest. That is issuance epoch 0**, the root of the rules-epoch chain "
            "(ADR-0027 §4).",
            "The genesis bundle is **the only artifact never promoted**; the genesis rules are checked by "
            "`GenesisSatisfiesFloor`, not a promotion (ADR-0027 §2).",
        ]),
        ("After bootstrap · confirmation", "green", [
            "Each confirmation-required record passes a **confirmation promotion** under ADR-0024 with author recusal, "
            "in dependency order (§6).",
            "**Confirmed**: becomes Accepted; the marker is removed. **Rejected**: a superseding record is required.",
            "Unmarked genesis records get no confirmation promotion; their review happened at the gate (A2.4).",
            "The bootstrap set (0024–0027) can never carry the marker: confirmation runs under it (§4).",
        ]),
    ]
    ph = max(c.card(0, 0, pw, t, b, draw=False, size=14.5) for t, b, _ in [(p[0], p[2], 0) for p in phases])
    for i, (t, acc, b) in enumerate(phases):
        px = X0 + i * (pw + 140)
        c.card(px, y, pw, t, b, accent=acc, h=ph, size=14.5, tint=(i != 1), dash="6 4" if i == 1 else None)
        if i < 3:
            lab = ["(a) and (b) met", "custodian declares", "epoch 0 issued"][i]
            c.arrow([(px + pw, y + ph / 2), (px + pw + 140, y + ph / 2)], ["red", "blue", "green"][i], sw=2.6)
            c.label(px + pw + 70, y + ph / 2 - 34, lab, ["red", "blue", "green"][i], 12.5, 110)
    y += ph + 70

    # ------------------------------------------------------------------ row 2: counts, criteria, status classes
    c.heading(X0, y, "Where ratification stands (G8 §1.1; ToO §0, §9)", "ink", 21)
    y += 46
    tiles = [("40", "Accepted (genesis)", "18 unmarked + 22 confirmation-required; **2 ratified in part**: ADR-0022 "
              "and ADR-0042, each without §6", "blue"),
             ("22", "Confirmation required", "**Up from 21** at G7: ADR-0046 (C2, C4), Batch 25", "red"),
             ("3", "Proposed", "ADR-0005 (blocked on a decision), ADR-0035, ADR-0036 (on evidence and a review); and "
              "ADR-0042 §6", "amber"),
             ("1", "Superseded", "ADR-0008, by ADR-0038 (2026.09.29)", "grey"),
             ("1 + 1", "Tombstone · reserved", "ADR-0011 tombstone; ADR-0014 reserved, no file", "grey")]
    tw = (W - 4 * 24) / 5
    th_ = 150
    for i, (n, lab, note, acc) in enumerate(tiles):
        tx = X0 + i * (tw + 24)
        c.rect(tx, y, tw, th_, acc, tint=True, rx=10, sw=2)
        c.text(tx + 20, y + 62, n, 52, acc, bold=True)
        nw = text_width(n, 52, True)
        c.text(tx + 20 + nw + 16, y + 56, lab, 18, acc, bold=True)
        c.para(tx + 20, y + 78, tw - 40, note, 13.5, "ink")
    c.text(X0, y + th_ + 28, "45 record files, numbered to 0046; 0014 is the only reserved number. One pending "
           "amendment: ADR-0026 A1 (R8), none of its four conditions met. Ratified in part is distinct from "
           "ADR-0018, which is accepted and **reversed in part** by ADR-0037 §3 (G8 §1.2).", 14, "muted")
    y += th_ + 64

    lw = 1500
    ccols = [("Criterion (ADR-0029 §4)", 520, {"bold": True}), ("Examples in the record", lw - 520)]
    crows = [
        {"cells": ["C1 · carries a proof obligation over privileged paths (erasure, break-glass, exceptions)",
                   "0013, 0028, and the accepted 0006 and 0009"], "accent": "red"},
        {"cells": ["C2 · carries an exhaustiveness or confinement claim", "0015, 0022 §6"], "accent": "red"},
        {"cells": ["C3 · supersedes, or reverses in effect, an accepted record",
                   "0008 supersession; 0017 ordering-clause supersession"], "accent": "red"},
        {"cells": ["C4 · resolves a debt owed by an accepted record", "0013 (debts of 0006 and 0009)"],
         "accent": "red"},
    ]
    h1 = c.table(X0, y, ccols, crows, size=14, accent="red")
    c.para(X0, y + h1 + 12, lw, "Marked on ratification if **any** applies. Until confirmed, a publication citing "
           "the guarantee says **\"author-ratified\"**. Minimum set: 0013, 0028, 0015, 0022 §6 (whenever ratified), "
           "the two supersession records (whenever written), 0006 and 0009 retroactively.", 14, "ink")
    sx = X0 + lw + 40
    sw = X1 - sx
    scols = [("Status class during genesis (§3)", 470, {"bold": True}), ("Meaning", sw - 470)]
    srows = [
        {"cells": ["Accepted (genesis)", "Ratified by the custodian and trusted by declaration. Post-bootstrap it "
                   "changes only through promotion."], "accent": "blue"},
        {"cells": ["Accepted (genesis) · confirmation required", "As above, plus a confirmation promotion after "
                   "bootstrap (§6)."], "accent": "red"},
        {"cells": ["Proposed / Draft", "Unratified; may stay Proposed indefinitely."], "accent": "amber"},
    ]
    h2 = c.table(sx, y, scols, srows, size=14, accent="blue")
    c.para(sx, y + h2 + 12, sw, "**Markings with no criterion**: ADR-0035 R2 (Proposed) is confirmation-required by "
           "custodian instruction; and four ratified texts were **drafted by the assistant** (ADR-0044, ADR-0045, "
           "ADR-0030 A1, ADR-0046), for which ADR-0029 has no criterion (G8 item 66).", 14, "ink")
    y += max(h1, h2) + 110

    # ------------------------------------------------------------------ row 3: the 21-record ledger
    c.heading(X0, y, "The genesis debt ledger: all 22 confirmation-required records (G8 §4)", "ink", 21)
    y += 46
    cols = [("Record", 130, {"bold": True}), ("Title", 860), ("Criteria", 270, {"bold": False}),
            ("Ratified", 260), ("Why it is marked (Status note)", W - 130 - 860 - 270 - 260)]
    rows = []
    for rec, title, crit, rat, why in CONF:
        cr = crit.split(" · ")
        crit_s = f"[[red|{cr[0]}]]" + (f" · {cr[1]}" if len(cr) > 1 else "")
        r = [rec, title, crit_s, rat, why]
        rows.append({"cells": r, "accent": "red"} if rec == "ADR-0046" else r)
    lt = c.table(X0, y, cols, rows, size=14, accent="red")
    c.para(X0, y + lt + 12, W, "The bootstrap set, ADR-0024 to ADR-0027, is Accepted with no marker and cannot carry "
           "one. Since A2 it is reached by the bootstrap review with everything else, before the rules it defines take "
           "effect: a reader, not a confirmation promotion. ADR-0029 itself is marked for A2 only. **Batch 25** "
           "added dependent entries to 0013, 0026, 0029, 0030, 0031, 0034, 0037, 0038, 0039, 0041, 0042, 0043 (the "
           "proofs of their modules' invariants) and 0045 (T-0045-31); no decision text changed in any of them, so "
           "what the first quorum reviews in them is unchanged from G7 (G8 §4, §6).", 14, "muted")
    y += lt + 80

    # ------------------------------------------------------------------ row 4: modules, bundle, headcount
    c.heading(X0, y, "What the trigger and the ceremony need", "ink", 21)
    y += 46
    mw = 1240
    mcols = [("Module (§5)", 190, {"mono": True}), ("Invariant", 380, {"mono": True}), ("State at G8", mw - 570)]
    mrows = [
        {"cells": ["Genesis", "GenesisSatisfiesFloor", "[[red|Not drafted]]: waits on the genesis rules contents. Its "
                   "shape is a lemma in both proofs below, proved of the floor's definition and not of genesis "
                   "contents (G8 §4)"], "accent": "red"},
        {"cells": ["Anchor", "FloorPreserved", "[[teal|Drafted and checked]] 2026.09.23, TLC2 2.19, floor as ratified "
                   "(R1, R2, R5, R6, R7, R9); [[teal|proved]] 2026.10.02, `Anchor_proof.tla`, 40 obligations, for every "
                   "floor subset and epoch bound"], "accent": "teal"},
        {"cells": ["RulesFloor", "PromotionMeetsIssuedQuorum", "[[red|Not drafted]]: waits on modeling decisions about "
                   "epochs, the vote triple and veto seats. Invariant renamed by A1 from "
                   "`NoPromotionWithoutAllGrantSeats`"], "accent": "red"},
        {"cells": ["Promotion", "StaleVotesNeverCount", "[[red|Not drafted]]: same decisions, and a model of deciding "
                   "before committing, which the reference had to implement"], "accent": "red"},
        {"cells": ["BreakGlass", "BreakGlassNeverChangesAuthority", "[[teal|Drafted and checked]] 2026.09.23; "
                   "[[teal|proved]] 2026.10.02, `BreakGlass_proof.tla`, 37 obligations"], "accent": "teal"},
    ]
    mh = c.table(X0, y, mcols, mrows, size=14, accent="grey")
    c.para(X0, y + mh + 12, mw, "**Bootstrap specification: partial** (G8 §4): two of five modules, `Anchor` and "
           "`BreakGlass`, are now proved and not only checked; `Genesis`, `RulesFloor` and `Promotion` are still owed. "
           "`RulesFloorNV` and its rev5 rerun are precursors, not substitutes. The ceremony accepts a specification "
           "digest marked drafted-only.", 14, "ink")
    bx = X0 + mw + 40
    bw = 900
    bh = c.card(bx, y, bw, "The genesis bundle (§5 with A2.2; ToO §9)", [
        "The **corpus manifest** at bootstrap, including the confirmation-required set",
        "The **TLA+ specification digest**, marked checked or drafted-only",
        "The **review attestation** (A2.2): reviewers, manifest digest reviewed, scope, findings disposition",
        "The **genesis rules**, which issue **no erasure roster**; resident with the mechanism release (ADR-0027)",
        "The **trusted-base declaration** beside the custody record, now that ADR-0045 is in force: the five modules "
        "rest on its rung-0 rows",
        "Every key-holder signs the digest → **issuance epoch 0**. Without the attestation it is not a bootstrap",
    ], accent="blue", size=14, h=mh + 80)
    hx = bx + bw + 40
    hw = X1 - hx
    # headcount derivation
    hh = 0
    c.rect(hx, y, hw, max(bh, mh + 80), "brown", tint=True, rx=8, sw=1.6)
    c.text(hx + 18, y + 32, "Headcount: five humans, or six", 16, "brown", bold=True)
    c.text(hx + 18, y + 56, "ADR-0029 Consequences; ADR-0026 §6 finding 5; ToO §9", 13, "muted")
    bxw = (hw - 36 - 2 * 50) / 3
    by = y + 80
    boxes = [("3", "anchor key-holders", "A-0025, n ≥ 3"), ("2", "counted grant seats", "R2 `minGrant ≥ 2`"),
             ("= 5", "humans", "disjoint by R5")]
    for i, (n, l1, l2) in enumerate(boxes):
        xx = hx + 18 + i * (bxw + 50)
        c.rect(xx, by, bxw, 120, "brown" if i < 2 else "blue", tint=False, rx=8, sw=1.6)
        c.text(xx + bxw / 2, by + 50, n, 36, "brown" if i < 2 else "blue", bold=True, anchor="middle")
        c.text(xx + bxw / 2, by + 78, l1, 13.5, "ink", anchor="middle")
        c.text(xx + bxw / 2, by + 100, l2, 12.5, "muted", anchor="middle")
        if i == 0:
            c.text(xx + bxw + 25, by + 66, "+", 26, "ink", bold=True, anchor="middle")
    c.para(hx + 18, by + 136, hw - 36, "**Six** if the author holds a seat: recusal raises the roster to three. "
           "**Four** was a property of the 09.15 *model* (custody (1, 0)), and too few to check R1 (09.23). "
           "**A solo bootstrap is not a bootstrap**, and custody today is (1, 0).".replace("*model*", "model"),
           14, "ink")
    y += max(bh, mh + 80) + 40
    c.para(X0, y, W, "Debts no confirmation repays are carried beside the ledger (G8 §4). Those of G2 to G7 stand, "
           "among them the checker's authorship (the proof-rule signature in `tools/cpc/` is cvc5's own formalization, "
           "trusted as written). G8 adds two: **the prover's soundness is trusted as written** (no mutation of it is "
           "run; the SMT backends' proofs are not rechecked by Isabelle, item 74), and **the proofs are the same "
           "hand's**: the condition meant to make the cited digests someone else's was run by the drafter. Four "
           "ratified texts were drafted by the assistant. **The debt is visible, not bounded.**", 14.5, "muted")
    return c
