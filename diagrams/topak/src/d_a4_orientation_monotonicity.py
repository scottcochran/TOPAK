"""A4 — The orientation rule and monotonicity, layer by layer (ToO rev 15 §7.8)."""
from lib import AMENDED_G11, Canvas

ID, SLUG = "A4", "orientation-monotonicity"

# (layer, statement verbatim from ToO §7.8, source as printed + status, up reading, down reading, row accent)
ROWS = [
    ("Decision", "Consensus for grants, local for denials", "Established",
     "A grant is an admit, consensus-ordered in the Paxos log (ADR-0015)",
     "A denial is not ordered: absence of effect is not an event (ADR-0015)", None),
    ("Policy", "Bundles only subtract from the floor — by composition, for every bundle",
     "ADR-0010, ADR-0030 [[blue|C1]]",
     "No bundle path at all; the floor itself moves by promotion, and a relaxation adds an anchor issuance (§3.2)",
     "Any bundle, at any age, can only narrow: `admit ⟺ floor_permit ∧ ¬bundle_deny`", None),
    ("Change", "Authority-increasing changes need consensus; decreasing ones need no quorum, are attributed, and are "
     "ordered when they change replicated state", "Floor-rollout session; ADR-0033 §4",
     "Consensus", "No quorum; attributed; ordered only when replicated state changes (revocation, expiry, end of "
     "round)", None),
    ("Deployment", "Degenerate forms lose theorems, never gain capability", "ADR-0023 [[blue|C3]]",
     "A variation with a capability the archetype lacks fails admission: the archetype is incomplete (§8.1)",
     "A degeneracy loses premises and theorems, and carries a declaration record", None),
    ("Authority", "Relaxing rules needs the anchor; operating within them does not", "ADR-0025, ADR-0026",
     "An anchor issuance and a promotion (rules-floor changes: both keys in both directions, §7.3)",
     "Operate and subtract under the last resident rules; anchor loss freezes change, never operation", None),
    ("Evidence", "Authority facts survive erasure and break-glass", "ADR-0028 [[blue|C1]]",
     "Removing a forensic class is a floor relaxation (§4.4)",
     "F1–F6 are denials on the erasure envelope: bundles can only narrow erasure further", None),
    ("Credential", "Renewal only narrows and keeps the rung; widening needs a fresh grant after the round ends",
     "ADR-0031, A1 [[blue|C1; C2 for A1]]",
     "A fresh grant, once the round has ended: at most one live lease per principal",
     "Renewal narrows the alphabet or shortens the TTL; it keeps bundle, round, role and rung", None),
    ("Confinement", "A principal below the declared rung is refused, never granted lower; every host failure the "
     "archetype tolerates subtracts", "ADR-0034 [[blue|C2, C4]]",
     "A grant only on an `Attested` verdict at the deployment's declared rung",
     "`Unattestable` refuses; `Contested` refuses and revokes the principal; no silent downgrade", None),
    ("Lineage", "The projection over-approximates what a round could read, and adding to it can only fail a pair",
     "ADR-0035 ([[amber|Proposed]])",
     "Independence passes only on upper-bound shares, at the promotion tally and the declaration",
     "Charging a round with more corpus can only fail a pair", "amber"),
    ("Time", "An interval whose failure subtracts may use a local clock; one whose failure preserves authority needs "
     "trusted time", "ADR-0032",
     "Persona expiry: trusted time from outside the principal (A6). A break-glass grant no longer needs it: it ends "
     "with its round (§3.3; R8 withdrawn)",
     "Lease expiry, passive e-stop, vote timeout: a local monotonic clock, margin erring early", None),
    ("Seat", "Only a thinker seat is issued a variant that writes, runs or offers; adding a seat to a cell never adds "
     "authority", "ADR-0037 [[blue|C3, C4]]",
     "`Draft`, `Invoke`, `Submit`, `Actuate` only for a `thinker` seat, and `Actuate` for an `emergency` seat "
     "(ADR-0037 A3, provisional): floor forbid B10",
     "An `observer` or `grant` seat reads, emits and votes or denies; an `operator` seat holds no authoring variant "
     "(ADR-0037 A4); adding one adds no variant", None),
    ("Detection", "Observers combine by any-of, and coupling only refuses: more Observers never lower safety, and an "
     "absent one stalls", "ADR-0038, ADR-0039 [[blue|C3, C4 · C4]]",
     "None: a finding is deny-only and never an admit precondition (ADR-0007); no Observer quorum",
     "A finding from any member of `W(p)` takes effect; a dead or slow Observer stops its own Thinker", None),
    ("Bundle", "A bundle loads only under an issued key's signature; a file name is evidence of nothing",
     "ADR-0044 [[blue|C1]]",
     "Replacing the bundle key is an anchor issuance (ADR-0025 §1 (f))",
     "No verifying signature, no load; an empty key set loads nothing and denies", None),
    ("Trusted base", "A component enters only if its failure can only subtract, or its identity is issued; what can "
     "add and is fixed by nothing is refused", "ADR-0045 [[blue|C2, C4]]",
     "A row that can add enters only as a trust root with an issued identity; adding a row is a relaxation with its "
     "own record",
     "A delegated row's failure only subtracts and needs no proof, key or quorum; removing a row is a tightening",
     None),
    ("Ingress", "Suppression only subtracts, and the label forbids are monotone in what was read: delivering more in "
     "the clear can only refuse more", "ADR-0047 [[blue|C4; C2 for §3]]",
     "A bundle may move every label to `clear`, and buys a narrower round: `clearSet` grows and `R5`–`R7` refuse more "
     "(§2.10)",
     "A handle in place of the bytes keeps `clearSet` small; a suppressed item's bytes do not enter the guest", None),
    ("Operation", "A quorum seats; one operator keeps a quorum's grant going and may narrow it, never widen it; a deny "
     "needs no lease and no peer", "ADR-0050 ([[blue|provisional]]) [[blue|C1, C3, C4]]",
     "A first lease needs a quorum: a promotion of a seating or an anchor issuance; an operator's add needs a live "
     "lease and a live peer (§7.10)",
     "`EndRound`, `Revoke`: a live lease or a fresh sign-on, in its own domain; `FenceEpoch`: a live lease (§7.10)",
     "blue"),
    ("Workflow", "The orchestrator only selects among edges already enabled; a guard's value can change only towards "
     "disabled; a route that fails the re-check at apply is void", "ADR-0054, ADR-0055 ([[amber|Proposed]])",
     "Every lease in a workflow is its promotion's grant, voted on with the graph and the seatings; a mesh's "
     "promotion grants at most its budget (§2.11)",
     "The orchestrator chooses only among enabled edges; a finding, revocation or fence voids a route at apply; a "
     "lapsed orchestrator takes no default edge (§2.11)", "amber"),
    ("Evidence of proof", "A second derivation adds evidence and changes no claim: a Lean result is cited beside the "
     "TLAPS proof, and the premise table carries it as a derived premise", "ADR-0053 [[blue|C4, for refines(Seats)]]",
     "A stage of the refinement chain discharged through Lean needs an ADR-0033 addendum, and none may cite one until "
     "the table can say \"either proof\" (ADR-0053 §5)",
     "A Lean result is cited beside the TLAPS proof; T-0045-31's residual does not move and no claim widens (§7.11)",
     None),
]


def build():
    c = Canvas(ID, "One orientation, eighteen layers: toward more authority is consensus, toward less is local",
               "Every boundary in the design is asymmetric in the same direction. Crossing toward more authority needs "
               "consensus, an issuance or a fresh grant; crossing toward less is local and monotone, needs no quorum, "
               "and is attributed. The boundary register found it stated five times in five vocabularies; ToO rev 15 "
               "§7.8 states it at eighteen layers, two of them new at rev 15. At the pattern level it inverts.",
               2900, "ToO rev 15 §2.10, §2.11, §3.2, §3.3, §4.1, §4.4, §5.4, §7.1, §7.3, §7.8, §7.9, §7.10, §7.11, "
               "§8.1–§8.2, §10, §13 (A6, A16, A17), Appendices J, K; derived/topak-boundary-register-2026.09.13.md §5, "
               "§6, §7.3; G10 §1; G11 §1, §1.1, §8, §7 items 7, 8, 49, 88; ADR-0053; ADR-0054, ADR-0055 (Proposed); ADR-0007, ADR-0010, ADR-0015, ADR-0023, ADR-0025, ADR-0026 W1, ADR-0028, "
               "ADR-0030, ADR-0031, ADR-0032, ADR-0033 §4, ADR-0034, ADR-0035, ADR-0037, ADR-0038, ADR-0039 A2, "
               "ADR-0041 A1, ADR-0044, ADR-0045, ADR-0047, ADR-0050 and ADR-0052 (provisional)")
    c.note = AMENDED_G11
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---------------------------------------------------------------- the rule, then and now
    w2 = (X1 - X0 - 30) / 2
    left = [
        "\"Every boundary above is asymmetric in the same direction: **crossing toward more authority requires "
        "consensus, crossing toward less is local and monotone.**\"",
        "\"This is not a boundary: it is the orientation of all of them, and it is stated five times in five "
        "vocabularies across the current corpus.\"",
    ]
    lt = "The orientation rule (boundary register §6, 2026.09.13)"
    chips = [("Decision", "grants versus denials"), ("Policy", "subtraction from the floor"),
             ("Syntax", "parse failure is a deny"), ("Deployment", "rung subtraction"),
             ("Semantic", "findings may deny, never admit")]
    cw = (w2 - 32 - 4 * 12) / 5
    chh = max(c.card(0, 0, cw, a, [b], size=13.5, bullets=False, tsize=15, draw=False) for a, b in chips)
    note = ("The five are the register's own wording. ToO §7.8 keeps decision, policy and deployment as rows, has no "
            "syntax or semantic row of its own, and adds fifteen: change, authority, evidence, credential, confinement, "
            "lineage, time, seat, detection, bundle and trusted base, at rev 14 ingress and operation, and at rev 15 workflow "
            "and evidence of proof.")
    ph = c.para(0, 0, w2 - 32, note, 14, draw=False)
    h = max(c.card(0, 0, w2, lt, left, size=19, draw=False), 52 + chh + 16 + ph + 14)
    c.card(X0, y, w2, lt, left, accent="blue", size=19, h=h)
    cx = X0 + w2 + 30
    c.card(cx, y, w2, "Five vocabularies in 2026.09.13; eighteen layers at ToO rev 15", [], accent="grey", h=h)
    yy = y + 52
    for i, (a, b) in enumerate(chips):
        c.card(cx + 16 + i * (cw + 12), yy, cw, a, [b], accent="green", size=13.5, bullets=False, tsize=15, h=chh)
    c.para(cx + 16, yy + chh + 16, w2 - 32, note, 14, "muted")
    y += h + 50

    # ---------------------------------------------------------------- the axis and the table
    c.text(X0, y + 20, "Monotonicity, layer by layer (ToO rev 15 §7.8, every row)", 21, "ink", bold=True)
    y += 34
    y += c.para(X0, y, X1 - X0,
                "The **Statement** column is §7.8 verbatim, and so is **Source**, with confirmation markers added "
                "([[blue|C1–C4]]: author-ratified until confirmed; [[blue|provisional]]: in force and subject to "
                "redesign, ADR-0029 A4). The two direction columns are this diagram's reading of each row, drawn from "
                "the sections cited in them (§ alone means ToO rev 15). Ingress and Operation are new at rev 14 "
                "(Appendix J), Workflow and Evidence of proof at rev 15 (Appendix K).",
                14.5, "muted") + 16
    axis_w = 300
    tx = X0 + axis_w
    tw = X1 - tx
    cols = [("Layer", 170, {"bold": True}), ("Statement", 640),
            ("↑ Toward more authority: what it costs", (tw - 170 - 640 - 270) / 2, {"accent": "blue"}),
            ("↓ Toward less authority: what it takes", (tw - 170 - 640 - 270) / 2, {"accent": "green"}),
            ("Source", 270)]
    rows = []
    for layer, st, src, up, dn, acc in ROWS:
        cells = [layer, st, up, dn, src]
        rows.append({"cells": cells, "accent": acc} if acc else cells)
    th = c.table(tx, y, cols, rows, size=14.5, accent="ink")

    # axis: two arrows running the full height of the table
    top, bot = y + 14, y + th - 14
    ux, dx = X0 + 70, X0 + 210
    c.arrow([(ux, bot), (ux, top)], "blue", sw=5)
    c.arrow([(dx, top), (dx, bot)], "green", sw=5, dash="12 7")
    mid = (top + bot) / 2
    c.label(ux, mid - 160, "**toward more authority**\nconsensus\nissuance\nfresh grant", "blue", 14, 160)
    c.label(dx, mid + 160, "**toward less authority**\nlocal\nmonotone\nno quorum\nattributed", "green", 14, 160)
    c.label(ux, top + 70, "costs", "blue", 13)
    c.label(dx, bot - 70, "free", "green", 13)
    y += th + 60

    # ---------------------------------------------------------------- where it inverts, and where it is owed
    c.text(X0, y + 20, "At the pattern level it inverts", 21, "red", bold=True)
    y += 40
    iw = (X1 - X0 - 2 * 30) / 3
    ih = c.card(X0, y, iw, "Tighten the archetype", [
        "**Every conformant deployment goes into declaration debt** (§7.8): what it ran as the archetype is now a "
        "degeneracy it must declare.",
    ], accent="red", size=15)
    ih = max(ih, c.card(X0 + iw + 30, y, iw, "Relax the archetype", [
        "**Published theorems are voided** (§7.8): a property checked against the old archetype stops holding of it.",
    ], accent="red", size=15, draw=False))
    c.card(X0 + iw + 30, y, iw, "Relax the archetype", [
        "**Published theorems are voided** (§7.8): a property checked against the old archetype stops holding of it.",
    ], accent="red", size=15, h=ih)
    c.card(X0 + 2 * (iw + 30), y, iw, "Both directions cost something", [
        "Nothing bounds how the archetype grows: the archetype-evolution record (versioning, the dominance rule, "
        "non-increasing TCB) is **unwritten** (§8.2; G11 item 7).",
    ], accent="grey", size=15, h=ih, status="open")
    y += ih + 60

    c.text(X0, y + 20, "Where the orientation is not yet whole", 21, "ink", bold=True)
    y += 40
    ow = (X1 - X0 - 3 * 30) / 4
    items = [
        ("Break-glass ends with its round, on a provisional record", [
            "Register §7.3: a non-expiring grant broke the monotone story. Now a grant is one lease of an emergency "
            "seating and ends with its round; **R8 is withdrawn** (ADR-0026 W1; §3.3, §10; G10 item 8).",
            "X1's retirement is in force on ADR-0052, **provisional**: if it is redesigned, break-glass has no settled "
            "form until the redesign is ratified (G10 §8).",
        ], "blue", "provisional"),
        ("Detection fails open against collusion", [
            "Coupling separates a present Observer from an absent one, not an honest one from a colluding one: every "
            "fact it reads is the Observer's own assertion (§5.4).",
            "An emergency seat is not a `thinker` and is not coupled (ADR-0039 A2; G10 item 49). Operators observe "
            "each other by presence, not by anything read (G10 §8).",
        ], "pink", "open"),
        ("Two rows on Proposed records", [
            "**Lineage** rests on ADR-0035, Proposed; **Workflow** on ADR-0054 and ADR-0055, Proposed, which the "
            "reference already follows on a floor stage not in force (G11 item 102).",
            "Every other row cites Accepted (genesis) records or an established principle; most of those records carry "
            "confirmation markers and are author-ratified (§0).",
        ], "amber", "proposed"),
        ("A row on a provisional record", [
            "**Operation** rests on ADR-0050, provisional: its centre, a first lease from a quorum, **is not built**. At "
            "the reference an unsigned [[red|BOOTSTRAP]] socket seats in place of the quorum (§7.10; G10 item 88).",
            "Anything citing it says \"author-ratified, provisional\" (§0; A17).",
        ], "blue", "provisional"),
    ]
    oh = max(c.card(0, 0, ow, t, b, accent=a, size=14.5, status=s, draw=False) for t, b, a, s in items)
    for i, (t, b, a, s) in enumerate(items):
        c.card(X0 + i * (ow + 30), y, ow, t, b, accent=a, size=14.5, status=s, h=oh)
    return c
