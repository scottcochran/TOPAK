"""B7 — From genesis to bootstrap: the state of record at G11 (ADR-0029 with A1 to A4)."""
from lib import AMENDED_G11, Canvas, text_width

ID, SLUG = "B7", "genesis-to-bootstrap"

# The 29 confirmation-required records at G11: G9's 22, G10's ADR-0005, 0047, 0048, 0049 and the two provisional
# records, and G11's ADR-0053 (G10 §1.1, §4; G11 §1.1, §4, §6; ToO rev 15 §9; each record's Status line and note).
NEW = ("ADR-0053",)
PROV = ("ADR-0050", "ADR-0052")
CONF = [
    ("ADR-0003", "Topic per principal per round, sealed on emit, as the unit of erasure", "C1 · **A2 only**",
     "09.11; A2 Batch 5 (09.25)", "A2 adds the `after` companion topic to the unit of erasure: a claim over the "
     "erasure path"),
    ("ADR-0005", "Kafka is neither the ordering authority nor the system of record", "C4", "10.04 · B27",
     "Discharges the debt ADR-0033 §2's K row carried since Batch 7, and ADR-0015's open item 1 as it bore on "
     "ordering. **New at G10**"),
    ("ADR-0006", "Erasure is a privileged, modeled, consensus-ordered event", "C1, C4 via 0013", "09.12",
     "Marked retroactively under C1 (ADR-0029 §4 minimum set); its debt resolved by ADR-0013"),
    ("ADR-0009", "Break-glass is a modeled, quorum-witnessed path, not a prohibition", "C1, C4 via 0013",
     "09.12; A1 B34", "As ADR-0006: a privileged path. **A1** (provisional with ADR-0052): the path stays and is a "
     "seating, no longer a floor exception"),
    ("ADR-0013", "Exception mechanism for privileged paths through the floor", "C1, C4", "09.23 · B4; A1 B34",
     "Resolves the debts of 0006 and 0009; NC-1, NC-2 proved. **A1** (provisional): a grant ends with its round; the "
     "exception count is 1; NC restated in `NonComposition_A1`"),
    ("ADR-0015", "Effects are boundary crossings; every crossing is authorized, ordered, and auditable", "C2",
     "09.23 · B3", "Both sets claimed exhaustive; the effect set's exhaustiveness unenforced while the sandbox gap "
     "stands"),
    ("ADR-0021", "Build emits to the effect stream; Build has an Observer", "C4", "09.30 · B18",
     "ADR-0039 §3, accepted, couples Build's promotion to the seal this record defines"),
    ("ADR-0023", "Degeneracy as the deployment-variation relation; archetype as its unique maximum", "C3",
     "09.23 · B3; A1 B29", "§5 reverses in effect ADR-0008's Observer scoping and ADR-0017's ordering-primacy "
     "clause. A1: the declared rung is per seat (§6c)"),
    ("ADR-0028", "The forensic floor: authority facts survive erasure and break-glass", "C1", "09.23 · B4",
     "Proof obligation over privileged paths; four open obligations carried into confirmation"),
    ("ADR-0029", "The design process is genesis; unilateral ratification; bootstrap on a drafted TLA+ spec",
     "C3 · **A2 and A4 only**", "09.15; A2 09.25; A3, A4 B34", "A2 reverses two clauses (the full-corpus review); "
     "**A4** adds a way to ratify the phase did not have: provisional, and floor fitness at bootstrap"),
    ("ADR-0030", "Bundles cannot add authority by construction; the floor runs on a verified evaluator", "C1",
     "09.25 · B6; A1 B24; A2, A3 B34", "Floor exceptions and forensic classes in the floor language; A1 the checker; "
     "**A2** label attributes in S and the allowlist's load checks; **A3** the floor genesis-provisional"),
    ("ADR-0031", "The lease is the composite credential, and its grant is the instant", "C1; C2 for A1 only",
     "09.25 · B5; A1 B10; A3 B34", "§5 lapses break-glass approvals on a targeted revocation; A1 confinement "
     "across renewal. **A3** (C1, C3; provisional): who grants and who denies"),
    ("ADR-0034", "Confinement is attested at lease grant; the archetype rung is a confidential VM", "C2, C4",
     "09.28 · B10; A3 B29; A2 B30", "A confinement claim; resolves ADR-0031's attestation-rung debt. **A2, the Run "
     "profile** (with ADR-0042 §6) and **A3**, four choices of the reference, now ratified (G10 §4)"),
    ("ADR-0037", "The LTRO decomposes into principals: seats and stages", "C3, C4", "09.29 · B12; A2–A4 B34",
     "§3 reverses in effect ADR-0018's Reader scope correction. A2–A4: the Listener labels and delivers the list; the "
     "kinds `emergency` and `operator`"),
    ("ADR-0038", "Observers are per cell, the shared group becomes the correlator", "C3, C4", "09.29 · B13",
     "Supersedes ADR-0008; discharges ADR-0023's carried scope for that supersession"),
    ("ADR-0039", "Observer liveness is progress, not presence", "C4", "09.29 · B14; A2 B34",
     "Resolves ADR-0024's open obligation on veto-seat outage. A2 (provisional): an emergency seat is not coupled"),
    ("ADR-0040", "Run has its own alphabet: `Consult`, `Actuate`, `Report`", "C3, C4", "09.30 · B20; A1 B34",
     "Reverses in effect ADR-0022 §5's sentence that `Read` and `Emit` are common. A1: the root declares a label; the "
     "entry's form"),
    ("ADR-0041", "Policy obligations for Run: one envelope per variant, coupling on effects only", "C1, C4",
     "09.30 · B20; A1–A3 B34", "A1 `R5`–`R7`; **A2 X1 retired**; **A3** `C1`–`C9`; A2 and A3 provisional"),
    ("ADR-0042", "Mechanism obligations for Run (**whole**, §6 since B30)", "C4; C2 for §6",
     "09.30 · B20; §6 B30; A1, A2 B34", "Resolves ADR-0039 finding 3 in part; **§6, Run's confinement claim, ratified "
     "with the Run profile, carries C2**. A2: `seatKind`"),
    ("ADR-0043", "Cell obligations for Run", "C4", "09.30 · B20; A1, A2 B34",
     "Resolves the provisional Run column of ADR-0037 §4. A1, A2: four items and handles; what carries the task"),
    ("ADR-0044", "A bundle is trusted by its signature, not its file name", "C1", "09.30 · B17",
     "§3 is a check on the privileged path. **Drafted by the assistant**"),
    ("ADR-0045", "The trusted base is declared row by row", "C2, C4", "10.01 · B22; A1, A2 B34",
     "Annex A claims to enumerate what the theorems assume; **thirty-seven rows**, five added at B34, T-0045-37 at "
     "B36; **A3, E1 (B37, C2 on A3)**: T-0045-31's residual names two known unsound cases"),
    ("ADR-0046", "The formal layer's method is declared: TLC checks, TLAPS proves, the prover is a trusted-base row",
     "C2, C4", "10.02 · B25; E1 B26; E2, A1 B28; A2, E3, E4 B37", "§4 claims every invariant is proved "
     "(exhaustiveness). A1: the certified configuration, twenty-one of twenty-four modules. **A2 (B37, C2)**: two "
     "known unsound cases in the prover's translation, and that no cited result rests on either"),
    ("ADR-0047", "The Listener labels what it delivers: a label on every item, a handle for what is suppressed",
     "C4 · C2 for §3", "10.05 · B34", "Decides the sentence ADR-0037 §2 left open; CR-6, CR-32 in part. §3: a "
     "suppressed item's bytes do not enter the guest. **New at G10**"),
    ("ADR-0048", "A Thinker learns its tools from the mechanism", "C4, C3", "10.05 · B34",
     "Run's ingress a closed list of four where two ratified sentences said three; the list the only description "
     "with standing. **New at G10**"),
    ("ADR-0049", "The allowlist entry has one schema", "C4 · C2 for §5", "10.05 · B34",
     "Discharges ADR-0040's obligation on the entry's schema; §5: the entry is the one statement of a tool's "
     "channel. **New at G10**"),
    ("ADR-0050", "An operator is a principal: seated by promotion, renewing under a lease, denying without one",
     "C1, C3, C4 · [[blue|provisional]]", "10.05 · B34", "Who may put a lease on the log. **And that the record is in "
     "force without its central behaviour built**: a first lease from a quorum (G10 §4)"),
    ("ADR-0052", "Break-glass is an emergency seating; the floor's exception for it is retired",
     "C1, C3, C4 · [[blue|provisional]]", "10.05 · B34", "The replacement of a privileged path, and the retirement "
     "of a floor exception. Rests on ADR-0050; a seating prepared by promotion is not built"),
    ("ADR-0053", "A second deductive method: Lean re-encodings, code transcriptions, the floor in Cedar's model; the "
     "Lean kernel a trusted-base row", "C4 · **for `refines(Seats)` only**", "10.06 · B36; E1 B37",
     "`refines(Seats)` gives the two `Seats` theorems a route around T-0045-28, ADR-0033's ratified debt; no "
     "ADR-0033 addendum cites it as a stage. **New at G11**"),
]


def build():
    c = Canvas(ID, "From genesis to bootstrap: where the corpus stands at G11",
               "The design process is genesis, not a degeneracy (ADR-0029): one custodian ratifies, the risky part is "
               "tracked as debt, and the anchor may bootstrap once a drafted TLA+ specification exists and the whole "
               "corpus has been independently reviewed. Since Batch 34 a record may be ratified **provisional**, and "
               "the ceremony gains two steps: seating the first operators, and floor fitness. This is the G11 state "
               "(2026.10.09); `diagrams/g1-to-bootstrap-2026.09.18.svg` shows the earlier G1 state.",
               3200, "ADR-0029 §1–§7, A1, A2 (A2.1–A2.5), A3, A4, B25, B34, Options, Consequences; ADR-0024 §6, A3; "
               "ADR-0025 Annex A-0025, A3; ADR-0026 §2 R2, R5, §6 finding 5, §7 finding 3, W1, A2; ADR-0027 §2, §4; "
               "ADR-0030 A3; ADR-0050 §1, §2, §6, §10; ADR-0052 §9; ADR-0035 Status note; ADR-0045 Annex A; ADR-0046 "
               "§4, A1, E1, A2, E3, E4; ADR-0053 B36, E1; ADR-0054, ADR-0055 (Proposed); every listed record's Status line "
               "and Status note; decisions/README.md; G10 header, §1, §1.2, §4, §6; G11 §1, §1.1, §1.2, §2.9, §3, §4, "
               "§5, §6, §7 items 2, 66, 85, 87, 88, 90, 92, 100, 101, §8; ToO rev 15 §0, §7.1, "
               "§7.10, §9; glossary (Bootstrap reviewer, Headcount); spec/README.md; "
               "spec/bootstrap-results-2026.09.23.txt; spec/Anchor-proof-results-2026.10.02.txt, "
               "spec/BreakGlass-proof-results-2026.10.02.txt, spec/Anchor- and BreakGlass-proof-cert-results-"
               "2026.10.04.txt, spec/BreakGlass_A1-results-2026.10.05.txt; spec/RulesFloorBase.tla")
    c.note = AMENDED_G11
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
            "**Since A4, provisional**: ratified without meeting its own condition, in force and subject to redesign, "
            "its exit stated (§3).",
            "Everything ratified is **trusted by declaration** and joins the genesis TCB. No forcing function (§7): "
            "every checkpoint carries a debt ledger.",
        ]),
        ("Bootstrap trigger · not met", "red", [
            "**(a)** a drafted TLA+ bootstrap specification: five modules, five invariants, a mutation each that must "
            "fail (§5). **Two of five drafted, checked, proved and certified**, and proved in Lean too (ADR-0053); "
            "`BreakGlass_A1` succeeds the second where it models X1.",
            "**(b)** an **independent review of the entire corpus** at one named manifest digest, by at least one "
            "reviewer who is not the author, every finding dispositioned (A2.1). **Not met: no reviewer is engaged "
            "and no pass has been run** (G11 §4).",
            "**Permission, not obligation**: bootstrap happens when the custodian declares it **and** the trigger is "
            "met (§7).",
        ]),
        ("Ceremony · epoch 0", "blue", [
            "Seat the key-holders under a declared custody record, **and the first operators by issuance**, at least "
            "three in each domain at the archetype (A3, [[blue|provisional]]).",
            "**Floor fitness** (A4, step 6): the bootstrap reviewer establishes that the policy floor is fit, in the "
            "attestation, and with that the floor is ratified.",
            "Assemble the **genesis bundle**; **every key-holder signs its digest: issuance epoch 0** (ADR-0027 §4).",
            "The genesis bundle is **the only artifact never promoted**; the genesis rules are checked by "
            "`GenesisSatisfiesFloor`, not a promotion (ADR-0027 §2).",
        ]),
        ("After bootstrap · confirmation", "green", [
            "Each confirmation-required record passes a **confirmation promotion** under ADR-0024 with author recusal, "
            "in dependency order (§6).",
            "**Confirmed**: becomes Accepted; the marker is removed. **Rejected**: a superseding record is required.",
            "A provisional record also stops being provisional only when its debt is built and seen and a reader has "
            "reviewed it; the custodian records it (§3, A4).",
            "The bootstrap set (0024–0027) can never carry the marker: confirmation runs under it (§4).",
        ]),
    ]
    ph = max(c.card(0, 0, pw, t, b, draw=False, size=14.5) for t, _, b in phases)
    for i, (t, acc, b) in enumerate(phases):
        px = X0 + i * (pw + 140)
        c.card(px, y, pw, t, b, accent=acc, h=ph, size=14.5, tint=(i != 1), dash="6 4" if i == 1 else None)
        if i < 3:
            lab = ["(a) and (b) met", "custodian declares", "epoch 0 issued"][i]
            c.arrow([(px + pw, y + ph / 2), (px + pw + 140, y + ph / 2)], ["red", "blue", "green"][i], sw=2.6)
            c.label(px + pw + 70, y + ph / 2 - 34, lab, ["red", "blue", "green"][i], 12.5, 110)
    y += ph + 70

    # ------------------------------------------------------------------ row 2: counts, criteria, status classes
    c.heading(X0, y, "Where ratification stands (G11 §1.1; ToO rev 15 §9)", "ink", 21)
    y += 46
    tiles = [("47", "Accepted (genesis)", "18 unmarked + 27 confirmation-required + 2 provisional. **Ratified in part**: "
              "ADR-0022 only (§6 Proposed); ADR-0042 is whole", "blue"),
             ("29", "Confirmation required", "**Up from 28**: 27, adding 0053 (C4, for one route), and the two "
              "provisional records", "red"),
             ("2", "Provisional", "ADR-0050 and ADR-0052, Batch 34: in force, **subject to redesign**, "
              "confirmation-required (ADR-0029 A4)", "blue"),
             ("5", "Proposed", "ADR-0035, ADR-0036, ADR-0051; ADR-0054 and ADR-0055 (workflows, built at the "
              "reference); and ADR-0022 §6", "amber"),
             ("1", "Superseded", "ADR-0008, by ADR-0038 (2026.09.29)", "grey"),
             ("1 + 1", "Tombstone · reserved", "ADR-0011 tombstone; ADR-0014 reserved, no file", "grey")]
    tw = (W - 5 * 24) / 6
    th_ = 150
    for i, (n, lab, note, acc) in enumerate(tiles):
        tx = X0 + i * (tw + 24)
        c.rect(tx, y, tw, th_, acc, tint=True, rx=10, sw=2, dash="4 3" if lab == "Provisional" else None)
        c.text(tx + 20, y + 62, n, 52, acc, bold=True)
        nw = text_width(n, 52, True)
        c.text(tx + 20 + nw + 16, y + 56, lab, 18, acc, bold=True)
        c.para(tx + 20, y + 78, tw - 40, note, 13.5, "ink")
    c.para(X0, y + th_ + 14, W, "54 record files, numbered to 0055; three added since G10 (0053 to 0055); 0014 is the "
           "only reserved number. **Twelve amendments are pending**, up from none, every one on a Proposed record: "
           "ten of ADR-0054's and ADR-0033 A16, A17; **ADR-0026 A1, R8, was withdrawn** (W1, 2026.10.04). **Two batches "
           "since G10, 36 and 37.** Ratified in part is distinct from ADR-0018, which is accepted and **reversed in "
           "part** by ADR-0037 §3 (G11 §1.2, as at G9). 18 + 27 + 2 accepted, 5 Proposed, 1 superseded and 1 tombstone "
           "make the 54 files.",
           14, "muted")
    y += th_ + 82

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
    h1 += c.para(X0, y + h1 + 12, lw, "Marked on ratification if **any** applies. Until confirmed, a publication citing "
                 "the guarantee says **\"author-ratified\"**, and of a provisional record **\"author-ratified, "
                 "provisional\"**. Minimum set: 0013, 0028, 0015, 0022 §6 (whenever ratified), the two supersession "
                 "records (whenever written), 0006 and 0009 retroactively. **A provisional record is "
                 "confirmation-required whatever its content** (§3, A4).", 14, "ink") + 12
    sx = X0 + lw + 40
    sw = X1 - sx
    scols = [("Status class during genesis (§3)", 470, {"bold": True}), ("Meaning", sw - 470)]
    srows = [
        {"cells": ["Accepted (genesis)", "Ratified by the custodian and trusted by declaration. Post-bootstrap it "
                   "changes only through promotion."], "accent": "blue"},
        {"cells": ["Accepted (genesis) · confirmation required", "As above, plus a confirmation promotion after "
                   "bootstrap (§6)."], "accent": "red"},
        {"cells": ["Proposed / Draft", "Unratified; may stay Proposed indefinitely."], "accent": "amber"},
        {"cells": ["**Accepted (genesis) · provisional** (A4, Batch 34)", "Ratified, in force and **subject to "
                   "redesign**; did not meet its own ratification condition and says on its face what it lacked. "
                   "Confirmation-required. Stops being provisional when the debt is built and seen at the reference "
                   "**and** a reader who is not the drafter has reviewed it; the custodian records it by a History "
                   "row."], "accent": "blue"},
    ]
    h2 = c.table(sx, y, scols, srows, size=14, accent="blue")
    h2 += c.para(sx, y + h2 + 12, sw, "**A provisional record's amendments may land in the bootstrap set** (§4, A4), "
                 "and three do: **ADR-0024 A3, ADR-0025 A3, ADR-0026 A2**. Not confirmation-required, for the reason "
                 "the set cannot be; covered by the genesis attestation, **which names them as provisional**. "
                 "**Markings with no criterion**: ADR-0035 R2 (Proposed), by custodian instruction; and assisted "
                 "drafting, on which nearly everything ratified since G9 rests (item 66).", 14, "ink") + 12
    y += max(h1, h2) + 60

    # ------------------------------------------------------------------ row 3: the 28-record ledger
    c.heading(X0, y, "The genesis debt ledger: all 29 confirmation-required records (G11 §4, with G10's 28)", "ink", 21)
    y += 46
    cols = [("Record", 130, {"bold": True}), ("Title", 820), ("Criteria", 300, {"bold": False}),
            ("Ratified", 300), ("Why it is marked; what changed since G9 (Status note; G10 §4, §6; G11 §4, §6)",
                                W - 130 - 820 - 300 - 300)]
    rows = []
    for rec, title, crit, rat, why in CONF:
        cr = crit.split(" · ")
        crit_s = f"[[red|{cr[0]}]]" + (f" · {cr[1]}" if len(cr) > 1 else "")
        r = [rec, title, crit_s, rat, why]
        if rec in PROV:
            rows.append({"cells": r, "accent": "blue"})
        elif rec in NEW:
            rows.append({"cells": r, "accent": "red"})
        else:
            rows.append(r)
    lt = c.table(X0, y, cols, rows, size=14, accent="red")
    c.para(X0, y + lt + 12, W, "Highlighted: the record new to the set at G11, ADR-0053, and the two provisional in "
           "blue; the rows marked new at G10 came in at that cut. "
           "The bootstrap set, ADR-0024 to ADR-0027, is Accepted with no marker and cannot carry one; since A2 it is "
           "reached by the bootstrap review with everything else, before the rules it defines take effect. ADR-0029 "
           "itself is marked for A2 and A4 only. **The twenty-six dependent amendments of Batch 34 were applied as "
           "marked**, beside the text they change; each depending on ADR-0050 or ADR-0052 is provisional with it "
           "(G10 §1.2, §6). G11 adds ADR-0046 A2 and ADR-0045 A3 to records already marked (C2); ADR-0054's ten pending "
           "amendments land in records of this ledger and are not in force (G11 §1.1, §4).", 14, "muted")
    y += lt + 100

    # ------------------------------------------------------------------ row 3b: the A2.5 line
    c.heading(X0, y, "The ADR-0029 A2.5 line, carried since G10 (G11 §4; the 10.02 review's CR-28 (ii))",
              "ink", 21)
    y += 46
    aw = 1900
    ah = c.table(X0, y, [("Field", 380, {"bold": True}), ("Value at G11", aw - 380)], [
        {"cells": ["Bootstrap reviewer engaged", "**None.** Every record, amendment, proof, module and reference tree is "
                   "one hand's, drafted or ratified by the genesis custodian with the assistant; no reviewer "
                   "independent of the author has read any record"], "accent": "red"},
        {"cells": ["Last completed review pass", "**None.** No confirmation pass has been run and no review attestation "
                   "exists; the field has no manifest digest to name. The dated reviews under `derived/` are the "
                   "drafter's own, as are the review runs behind ADR-0046 A2, and do not count under A2.1"], "accent": "red"},
    ], size=14, accent="red")
    c.para(X0, y + ah + 12, aw, "G4 to G9 did not carry this line, though A2.5 (ratified 2026.09.25) asks for it.", 14,
           "muted")
    bx2 = X0 + aw + 40
    dh = c.card(bx2, y, X1 - bx2, "The bootstrap reviewer's two new duties (ADR-0029 A4)", [
        "**Establish that the policy floor is fit**, with which it is ratified (ADR-0030 A3). The gates show "
        "consistent, total, non-vacuous and minimal; **what makes a floor fit is not written** (items 2, 87).",
        "**Attest to rules that include three provisional amendments**, named as such: ADR-0024 A3, ADR-0025 A3, "
        "ADR-0026 A2.",
    ], accent="blue", size=14, status="provisional", status_extra="what the attestation names")
    y += max(ah + 50, dh) + 60

    # ------------------------------------------------------------------ row 4: modules, bundle, headcount
    c.heading(X0, y, "What the trigger and the ceremony need", "ink", 21)
    y += 46
    mw = 1240
    mcols = [("Module (§5)", 190, {"mono": True}), ("Invariant", 380, {"mono": True}), ("State at G11", mw - 570)]
    mrows = [
        {"cells": ["Genesis", "GenesisSatisfiesFloor", "[[red|Not drafted]]: waits on the genesis rules contents. Its "
                   "shape is a lemma in both proofs below, proved of the floor's definition and not of genesis "
                   "contents. Whether a module is owed for the genesis seating is not decided (A3)"], "accent": "red"},
        {"cells": ["Anchor", "FloorPreserved", "[[teal|Drafted and checked]] 2026.09.23, floor as ratified (R1, R2, R5, "
                   "R6, R7, R9); [[teal|proved]] 2026.10.02, `Anchor_proof.tla`, 40 obligations, for every floor subset "
                   "and epoch bound; **certified** (ADR-0046 A1), 2 resting on LS4; **proved in Lean** of its re-encoding "
                   "(ADR-0053)"], "accent": "teal"},
        {"cells": ["RulesFloor", "PromotionMeetsIssuedQuorum", "[[red|Not drafted]]: waits on modeling decisions about "
                   "epochs, the vote triple and veto seats. Invariant renamed by A1 from "
                   "`NoPromotionWithoutAllGrantSeats`"], "accent": "red"},
        {"cells": ["Promotion", "StaleVotesNeverCount", "[[red|Not drafted]]: same decisions, and a model of deciding "
                   "before committing, which the reference had to implement"], "accent": "red"},
        {"cells": ["BreakGlass", "BreakGlassNeverChangesAuthority", "[[teal|Drafted, checked, proved]] (37 obligations) "
                   "and **certified**; **models X1**, so it is frozen and succeeded by `BreakGlass_A1` (2026.10.05): "
                   "`EmergencyNeverChangesAuthority`, 8 rows, 45 obligations, nothing assumed, R7 not assumed, "
                   "certified. `BreakGlass` is **proved in Lean** too (ADR-0053)"], "accent": "teal"},
    ]
    mh = c.table(X0, y, mcols, mrows, size=14, accent="grey")
    c.para(X0, y + mh + 12, mw, "**Bootstrap specification: partial**, as at G9 (G11 §4): two of five modules, `Anchor` "
           "and `BreakGlass`, are proved, and certified; `Genesis`, `RulesFloor` and `Promotion` are still owed. Both "
           "proofs extend `RulesFloorBase.tla`, live and not frozen (ADR-0046 E1), which **has not caught up**: it "
           "still carries `bgScope` and R6's bound of two (ADR-0026 A2; item 90). `RulesFloorNV` and its rev5 rerun "
           "are precursors, not substitutes. The ceremony accepts a specification digest marked drafted-only.", 14,
           "ink")
    bx = X0 + mw + 40
    bw = 900
    bh = c.card(bx, y, bw, "The genesis bundle (§5 with A2.2, A3, A4; ToO §9)", [
        "The **corpus manifest** at bootstrap, including the confirmation-required set",
        "The **TLA+ specification digest**, marked checked or drafted-only",
        "The **review attestation** (A2.2): reviewers, manifest digest reviewed, scope, findings disposition; "
        "**the reviewer's word that the floor is fit** (A4), and **the three provisional amendments named as such**",
        "The **genesis rules**, which issue **no erasure roster**, and carry the **identity providers' keys** and the "
        "**first operators' seatings** (A3); resident with the mechanism release (ADR-0027)",
        "The **trusted-base declaration** beside the custody record: the five modules rest on its rung-0 rows",
        "Every key-holder signs the digest → **issuance epoch 0**. Without the attestation it is not a bootstrap",
    ], accent="blue", size=14)
    hx = bx + bw + 40
    hw = X1 - hx
    HB = max(bh, mh + 120)
    c.rect(hx, y, hw, HB, "brown", tint=True, rx=8, sw=1.6)
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
           "**Four** was a property of the 09.15 model (custody (1, 0)), and too few to check R1 (09.23). "
           "**Operators**: since A3 ([[blue|provisional]]) the ceremony also seats the first operators, **at least "
           "three in each domain** at the archetype, each with a Persona, a key and an independent identity provider "
           "(ADR-0050 §6); a person who operates and also votes holds two seats and is two principals (§1). "
           "**A solo bootstrap is not a bootstrap**, and custody today is (1, 0).", 14, "ink")
    y += HB + 40
    c.para(X0, y, W, "Debts no confirmation repays are carried beside the ledger (G11 §4). Those of G2 to G9 stand, "
           "among them the checker's authorship, **the prover's soundness trusted as written** and **the proofs the same "
           "hand's**. G10 adds three: **five records, twenty-eight amendments, six modules and their proofs, a rebuilt "
           "reference and the model it is checked against are one hand's**, drafted, built, checked and ratified "
           "across three days with no second reader; **two records are in force without meeting their own "
           "conditions**, which is what provisional means; and **the reference was built to records before they were "
           "ratified**, so for two days it followed text that was not in force and did not follow text that was. Of "
           "G9's six choices accepted in conversation, five are now in records (item 85). G11 adds: **one record, six "
           "amendments and errata, three Lean packages, two liveness modules, two Proposed records with twelve pending "
           "amendments, two modules, a floor stage and a rebuilt reference are one hand's**, across five days; **a trust "
           "root is kept in use with two known defects**, unreported upstream; and **the reference again follows text "
           "that is not in force**. **The debt is visible, not bounded.**", 14.5, "muted")
    return c
