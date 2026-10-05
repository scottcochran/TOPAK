"""B6 — The trust anchor is a havoc issuer; custody is declared per rung (ADR-0025 and its annex)."""
from lib import Canvas

ID, SLUG = "B6", "anchor-custody"


def build():
    c = Canvas(ID, "The trust anchor is a havoc issuer, and its custody is a declaration",
               "Promotion moves the gate up one level: the authority that defines who votes cannot itself be voted "
               "in without regress. ADR-0025 makes that authority a havoc issuer, splits \"infallible\" three ways, and "
               "declares custody per rung as a pair (capture threshold, loss tolerance) that never enters a proof.",
               3000, "ADR-0025 Decomposition, Context, §1 (a)–(h) with A1, A2, A3 and B29, §2, Options, Consequences, "
               "Open obligations, Annex (A-0025, D-0025-1, D-0025-2, axis position), History R1, B2, B17, B23, B29, "
               "B34; ADR-0002 A2; ADR-0024 §1 with A3, §2, 'Why this rule is modeled'; ADR-0026 §4, A2; ADR-0027 §3, "
               "§4; ADR-0028 §3; ADR-0029 §1, §4 with A4, §5 with A3; ADR-0033 A6, A7, A11; ADR-0034 A3; ADR-0044 §1; "
               "ADR-0047 §7; ADR-0049 §6; ADR-0050 §1, §2, §3, §10; ADR-0045 Annex A T-0045-8, T-0045-9, T-0045-11, "
               "T-0045-35, T-0045-36, Annex B T-0045-27; ToO rev 14 §7.1, §7.2, §7.5, §7.6, §7.7, §7.10, §9; G10 "
               "header, §1.1, §1.2, §2.1, §2.9, §8, §7 items 10, 11, 67 (as at G9), 88; ADR-0046 header (Discharges), "
               "§4, A1; ADR-0029 B25; spec/Anchor-proof-cert-results-2026.10.04.txt; boundary register B14")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y + 6

    # ------------------------------------------------------------------ row 1: treatments and the three-way split
    lw = 1060
    c.heading(X0, y, "Three treatments were weighed (ADR-0025 Context, Options)", "ink", 20)
    c.heading(X0 + lw + 50, y, "Havoc, with \"infallible\" split three ways (ADR-0025 §2; ToO §7.2)", "ink", 20)
    y += 44
    tcols = [("Treatment", 250, {"bold": True}), ("Disposition", lw - 250)]
    trows = [
        {"cells": ["(A) Infallible: the anchor is an oracle",
                   "**Rejected.** Key theft becomes infallible too; the rules floor loses its justification; silent "
                   "degradation escapes declaration; P1 is abandoned at the top of the authority chain; residual risk "
                   "and GOVERN 2.3 accountability become unstatable."], "accent": "red"},
        {"cells": ["(B) Havoc: any authentic issuance, bounded by a verified floor",
                   "**Chosen.** Safety is proven for every issuance the anchor could make, so its composition never "
                   "enters the proof."], "accent": "blue"},
        {"cells": ["(C) Characterized: havoc plus a model of how members decide",
                   "**Rejected.** Adds governance content, not proof content; every custody change would couple to "
                   "re-verification."], "accent": "red"},
        {"cells": ["Verified anchor", "**Rejected.** Relocates the axiom without removing it."], "accent": "red"},
    ]
    t1 = c.table(X0, y, tcols, trows, size=14, accent="grey")
    sx = X0 + lw + 50
    sw = X1 - sx
    scols = [("Property", 170, {"bold": True}), ("Treatment", 250), ("Statement", sw - 170 - 250 - 330),
             ("Where it lives", 330)]
    srows = [
        {"cells": ["Intent", "**ASSUMED**, the sole axiom",
                   "*An authentic issuance at the current anchor epoch is what the anchor intended.*".replace("*", ""),
                   "Above every proof: **no safety theorem covers it**"], "accent": "brown"},
        {"cells": ["Integrity", "**MODELED** under havoc",
                   "`Issue` is an environment action, constrained only by `Authentic`, epoch increment and the rules "
                   "floor (ADR-0026). Safety is proven for every issuance sequence satisfying those constraints.",
                   "Inside the specification and the verified object. **Discharged as written** since 2026.10.02: "
                   "`Anchor_proof.tla` proves `FloorPreserved` for every floor subset and epoch bound (ADR-0046; "
                   "ADR-0029 B25), of the module; certified, 2 of 40 obligations resting on LS4, which no checker "
                   "confirms (ADR-0046 A1)"], "accent": "teal"},
        {"cells": ["Custody", "**DECLARED** per rung (ADR-0023)",
                   "The pair (capture threshold, loss tolerance), plus the composition and eviction rules that make "
                   "it true. Not in the model.",
                   "A declaration record; **changing it never reopens a proof**"], "accent": "violet"},
    ]
    t2 = c.table(sx, y, scols, srows, size=14, accent="blue")
    y += max(t1, t2) + 60

    # ------------------------------------------------------------------ row 2: modeled vs declared, as a diagram
    c.heading(X0, y, "Modeled versus declared: where `Authentic` is instantiated (ADR-0025 §2; ToO §7.7)", "ink", 20)
    y += 50
    rw_in = 1260
    gap_mid = 200
    rw_out = 860
    xin, xout = X0, X0 + rw_in + gap_mid
    xr = xout + rw_out + 50
    rwr = X1 - xr
    top = y
    cy = top + 34
    iw = (rw_in - 3 * 26) / 2
    b_issue = ["Constrained only by `Authentic(i)`, an epoch increment and the rules floor.",
               "`Authentic(i)` is **opaque** in the specification.",
               "An admitted issuance voids in-flight votes at the new rules epoch (ADR-0024 §3), and is persisted with "
               "genesis residency (ADR-0027 §3)."]
    b_floor = ["Bounds every issuance: a havoc issuer with no floor could set a roster of one.",
               "The quorum's archetype values live here, so **a promotion degeneracy is a mechanism release** and "
               "reopens the promotion theorem (ADR-0024).",
               "Changing the floor needs two keys: an issuance plus a promotion (ADR-0026 §4)."]
    hb = max(c.card(0, 0, iw, "`Issue` · environment action", b_issue, draw=False),
             c.card(0, 0, iw, "Rules floor (ADR-0026)", b_floor, draw=False))
    c.card(xin + 26, cy, iw, "`Issue` · environment action", b_issue, accent="teal", h=hb)
    c.card(xin + 52 + iw, cy, iw, "Rules floor (ADR-0026)", b_floor, accent="teal", h=hb)
    c.arrow([(xin + 26 + iw, cy + 60), (xin + 52 + iw, cy + 60)], "teal", sw=2)
    in_h = hb + 34 + 26
    hc0 = c.card(0, 0, rw_out - 52, "Custody declaration (annex)", ["Which keys, and how many signatures: the declaration **instantiates** `Authentic`.", "Plus the composition and eviction rules that make the pair true.", "**A custody degeneracy is a declaration** and reopens nothing.", "The two axes, approver fault tolerance and anchor recoverability, are declared independently."], draw=False)
    in_h = max(in_h, max(hc0, hb) + 34 + 26)
    c.region(xin, top, rw_in, in_h, "Modeled · inside the specification and the verified object", "teal",
             dash=None)
    b_cust = ["Which keys, and how many signatures: the declaration **instantiates** `Authentic`.",
              "Plus the composition and eviction rules that make the pair true.",
              "**A custody degeneracy is a declaration** and reopens nothing.",
              "The two axes, approver fault tolerance and anchor recoverability, are declared independently."]
    hc = c.card(0, 0, rw_out - 52, "Custody declaration (annex)", b_cust, draw=False)
    c.card(xout + 26, cy, rw_out - 52, "Custody declaration (annex)", b_cust, accent="violet", h=max(hc, hb))
    out_h = max(hc, hb) + 34 + 26
    c.region(xout, top, rw_out, max(in_h, out_h), "Declared · outside the model, per rung", "violet")
    c.arrow([(xout, cy + 120), (xin + rw_in, cy + 120)], "violet", sw=2.4, label="instantiates `Authentic`",
            loff=(0, -22))
    ax = c.card(xr, top, rwr, "Intent · the sole axiom", [
        "*An authentic issuance at the current anchor epoch is what the anchor intended.*".replace("*", ""),
        "**The authority regress ends here** (ToO §7.6): ADR-0002 a declared axiom set; ADR-0010 a verified "
        "artifact; ADR-0025 with ADR-0026 **one axiom, bounded by two verified floors**.",
    ], accent="brown", size=14.5, h=max(in_h, out_h))
    y = top + max(in_h, out_h, ax) + 70

    # ------------------------------------------------------------------ row 2b: what an issuance carries, at G10
    c.heading(X0, y, "What the anchor issues at G10: the rules, item by item (ADR-0025 §1; ToO rev 14 §7.2)", "ink",
              20)
    y += 50
    iw_ = 1720
    icols = [("Item", 70, {"bold": True}), ("Rules (ADR-0025 §1)", 1010), ("Since (batch)", 240), ("Status", iw_ - 1320)]
    PV = "[[blue|Accepted · provisional]]"
    irows = [
        ["(a)", "The promotion roster and its parameters, `quorum` and `minGrant` (ADR-0024). **Read to include the "
         "seats of kind** `operator` **and, at genesis, the first operators' seatings**: something must be seated before "
         "anything can be promoted, and only an issuance can do it (A3)", "Batch 2; **A3, B34**",
         "Accepted; A3 " + PV + " (ADR-0050)"],
        ["(b)", "The break-glass and erasure quorum rosters. For break-glass the rules carry the roster and its "
         "quorum; its envelope is an emergency seating's (ADR-0026 A2; ADR-0052 §2)", "Batch 2; B34",
         "Accepted; the break-glass reading " + PV],
        ["(c)", "The anchor's own key set", "Batch 2", "Accepted"],
        ["(d)", "Any change that relaxes the policy floor or adds a floor exception", "Batch 2", "Accepted"],
        ["(e)", "Any change to the rules floor, in either direction (ADR-0026 §4)", "R1; Batch 2", "Accepted"],
        {"cells": ["(f)", "Keys accepted in place of the mechanism's own check: the rung-3 verifier's appraisal key "
                   "(ADR-0034 §2) and the bundle-signing key (ADR-0044 §1); **and an identity provider's key**, under "
                   "which an operator's sign-on assertion is accepted at a lease boundary. Each provider is a trust "
                   "root for the operators it vouches for and no others (T-0045-35)",
                   "A1, B17; **A3, B34**", "Accepted; the provider's key " + PV], "accent": "blue"},
        ["(g)", "The independence criterion in force (ADR-0034 §4; ADR-0035): set or not, by digest; it decides "
         "which principals may be `Contained`. The mechanism reads that it is set and evaluates nothing",
         "B29 (ADR-0034 A3)", "Accepted"],
        {"cells": ["(h)", "**The two lists a bundle's load checks read**: the allowlist entries, by name and digest, "
                   "that may release a reserved label name; and the channel targets inside the deployment. Each widens "
                   "what a bundle may declare, so adding to either is an issuance. With neither issued, no entry "
                   "releases a reserved name and every entry with a channel is outward (ADR-0047 §7; ADR-0049 §6, W7, "
                   "W8)", "**A2, B34**", "Accepted"], "accent": "blue"},
    ]
    ith = c.table(X0, y, icols, irows, size=14, accent="brown")
    gx = X0 + iw_ + 40
    gw_ = X1 - gx
    gh1 = c.card(gx, y, gw_, "The issuer now seats (ADR-0025 A3; ADR-0024 A3)", [
        "**At genesis an issuance seats the first operators**, at least three in each domain at the archetype, each "
        "with a Persona and a key, the providers' keys in the issued rules (ADR-0029 §5 with A3; ADR-0050 §2).",
        "**After that a promotion seats**: a seating names a principal, its seat, Persona, bundle revision, "
        "confinement and alphabet, and the labels its task may carry; the completed tally grants the first lease "
        "at a fresh fence, with no request from anyone (ADR-0024 A3).",
        "All three amendments are in the **bootstrap set**: not confirmation-required, and covered by the genesis "
        "attestation, which must **name them as provisional** (ADR-0029 A4; G10 §1.2).",
    ], accent="blue", size=14, status="provisional", status_extra="ADR-0024 A3, ADR-0025 A3")
    gh2 = c.card(gx, y + gh1 + 20, gw_, "Not built: neither seating path", [
        "No first operator is seated by an issuance and no seating is promoted at the reference. Its unsigned socket "
        "is kept as a **BOOTSTRAP** path that seats and does nothing else, so **whoever reaches it can seat** "
        "(ADR-0050 §10; ADR-0033 A11; G10 §8, item 88).",
    ], accent="red", size=14, status="notbuilt", status_extra="BOOTSTRAP stands in")
    c.para(X0, y + ith + 12, iw_, "Replacing any (f) key, or adding to either (h) list, adds authority and is an "
           "issuance. **The rules floor bounds none of the three new issued things** (G10 §2.1). At the reference "
           "`verifier_keys` and `bundle_keys` exist (ADR-0033 A6) and the verifier key is read at every rung-3 grant, "
           "renewal and Contested entry under test keys, in **SIMULATED** runs (ADR-0033 A7, B29).", 14, "muted")
    y += max(ith + 70, gh1 + 20 + gh2) + 70

    # ------------------------------------------------------------------ row 3: the axis and the full custody table
    c.heading(X0, y, "Custody is a declaration axis: anchor recoverability (ADR-0025 Annex; ToO §7.2)", "ink", 20)
    y += 50
    nodes = [("A-0025", "(n, 0)", "Archetype · strict unanimity", "blue"),
             ("D-0025-2", "(n−1, 1)", "n−1 eviction with replacement", "amber"),
             ("D-0025-1", "(k, n−k)", "TUF-style threshold with recovery", "amber"),
             ("— single custodian", "(1, 0)", "Genesis custody today (ADR-0029 §1)", "brown")]
    nw = 520
    ngap = (W - 4 * nw) / 3
    nh = 104
    for i, (rec, pair, name, acc) in enumerate(nodes):
        nx = X0 + i * (nw + ngap)
        c.rect(nx, y, nw, nh, acc, tint=True, rx=10, sw=2)
        c.text(nx + 18, y + 34, rec, 19, acc, bold=True)
        c.text(nx + nw - 18, y + 36, pair, 24, acc, bold=True, anchor="end")
        c.text(nx + 18, y + 72, name, 15, "ink")
        if i < 3:
            c.arrow([(nx + nw, y + nh / 2), (nx + nw + ngap, y + nh / 2)], "grey", sw=2)
    c.text(X0, y + nh + 30, "Order is position on the axis, not record number: \"record numbers follow drafting "
           "order; position on the axis does not.\" Every pair is (capture threshold, loss tolerance).", 14, "muted")
    y += nh + 60

    cols = [("Field", 220, {"bold": True}),
            ("A-0025 · archetype", 0), ("D-0025-2 · n−1 eviction", 0), ("D-0025-1 · TUF threshold", 0),
            ("Single custodian", 0)]
    cw = (W - 220) / 4
    cols = [cols[0]] + [(t, cw) for t, _ in cols[1:]]
    nd = "[[grey|Not declared in the annex]]"
    rows = [
        ["Custody model", "Strict unanimity, n ≥ 3", "n−1 eviction with replacement",
         "Threshold with recovery, in the shape of The Update Framework (TUF) root role", "Single custodian"],
        ["Pair (capture, loss)", "**(n, 0)**", "**(n−1, 1)**", "**(k, n−k)**, k < n−1", "**(1, 0)**"],
        ["Premise falsified", "— (the archetype)", "No key-holder is removed without their own consent",
         "Rule changes carry unanimous consent", nd],
        ["`Authentic`", "Signed by every key in the anchor key set at the current epoch",
         "Unanimity of the remaining n−1 evicts one key-holder, atomically with seating a replacement",
         "k of n signatures; a genesis-declared recovery rule lets k rotate any key", nd],
        ["Composition / preconditions", "Unanimous quorum of `Mediated` key-holders, n ≥ 3",
         "One eviction per anchor epoch; n ≥ 3; the replacement countersigns", "—", "One person: Scott (ADR-0029 §1)"],
        {"cells": ["Key-holder type", "**At the gate** (ADR-0002 A2): removable only with their own consent. "
                   "`Mediated` applies as an attribution predicate only",
                   "**Principals.** The gate moves to the genesis-declared eviction rule",
                   "**Principals.** The gate moves to the genesis threshold-and-recovery rule", nd],
         "accent": "brown"},
        ["Loss behavior", "Any permanent loss **freezes the rules**: the system can run and subtract, but cannot "
         "change", "Freeze requires a **second** loss within one replacement window", "Liveness under up to n−k "
         "losses", nd],
        {"cells": ["Resignation (R1)", "A permanent loss, therefore **a freeze**. Unanimity leaves no rule to seat a "
                   "replacement; to leave without freezing, first move the deployment to D-0025-2",
                   "The eviction rule run **with the departing key-holder's consent**; consumes the epoch's one "
                   "eviction, so a resignation and a compromise cannot be handled in the same anchor epoch",
                   "**Absorbed by the recovery rule**: k rotate the resigning key. No freeze while k remain; dropping "
                   "below k is a loss like any other", nd], "accent": "violet"},
        ["Gained", "— (the archetype is the reference point)",
         "A compromised key-holder's permanent veto ends", "Liveness under up to n−k losses", nd],
        ["Sacrificed", "—", "Consent to one's own removal", "A k-coalition can issue rules over n−k objections", nd],
        ["Exit / mitigation", "**Re-genesis**: a successor system, not a continuation",
         "Optional: a time-locked notice window in which an outside quorum may deny (subtractive, so admissible)",
         "Prior art: TUF root role and root-key rotation; RFC 6024", nd],
    ]
    th = c.table(X0, y, cols, rows, size=14, accent="brown")
    c.para(X0, y + th + 12, W, "The annex entries are declaration records under ADR-0023, separately supersedable, "
           "and not decision clauses of ADR-0025; they ratified with it in Batch 2 as declarations. The single "
           "custodian appears only as an axis position: its pair is (1, 0), and the annex writes no row for it.",
           14, "muted")
    y += th + 80

    # ------------------------------------------------------------------ row 4: gate, freeze, residual, genesis
    w4 = (W - 3 * 30) / 4
    g = ["**Archetype custody**: key-holders are removable only with their own consent, so **they sit at the "
         "gate** (B14): attributable non-principals, `Mediated` as attribution only.",
         "**Degenerate custody**: the eviction or threshold rule can remove a key-holder, so key-holders become "
         "**principals** and the gate moves to that rule. **That is a type change, and it moves the TCB** (§8.2); "
         "it voids no theorem, so it is declared and checked (ADR-0023).",
         "**Operators are principals** (ADR-0050, provisional): an operator was whoever reached a socket, neither a "
         "principal nor at the gate. It now holds a seat, is seated by a quorum and can be revoked by a peer, so the "
         "evictability test puts it inside; `Mediated`.",
         "**Promotion voters are principals on every rung**, because the anchor can evict them."]
    f = ["At A-0025, a permanent loss (or a resignation) **freezes the rules**.",
         "Frozen: the system runs and subtracts, but cannot change; anchor unavailability blocks change, never "
         "operation (ADR-0027 §3).",
         "**The only exit is re-genesis**: a successor system and a new rules-epoch chain (ADR-0027 §4).",
         "That fragility pushes operators toward degenerate custody, which is correct as long as it is declared.",
         "**Re-genesis migration is open** (item 10, as at G9): what a successor inherits, including read access to the "
         "forensic classes, whose horizon is the epoch chain (ADR-0028 §3)."]
    r = ["**A coalition at the capture threshold can issue any rules-floor-conformant roster.**",
         "No safety theorem covers anchor intent. The rules floor bounds what it can issue; nothing bounds why.",
         "The residual becomes numeric: the capture threshold feeds NIST MANAGE 1.4.",
         "Trusted-base rows (ADR-0045, in force, C2/C4): T-0045-8 the anchor key store, T-0045-9 the key-holders "
         "\"honest at the declared capture threshold\", both trust roots."]
    gc = ["**Genesis custody: Scott, sole custodian, (1, 0)** (ADR-0029 §1; G10 header). Genesis, not a "
          "degeneracy: there is no archetype custody before the anchor exists.",
          "The corpus's own row is T-0045-11, in force; **the dev bundle key is a second (1, 0) custody** "
          "(items 11 and 67, as at G9; T-0045-27). Bundles are signed under a throwaway key (G10 §8).",
          "**A solo bootstrap is not a bootstrap.** The ceremony seats key-holders under a declared custody "
          "record and, since ADR-0029 A3 (provisional), the first operators by issuance (§5); the archetype needs "
          "three key-holders (A-0025) of the five humans.",
          "Owed: the genesis key-ceremony procedure, and a named owner and role for every custody declaration "
          "(GOVERN 2.3)."]
    hh = max(c.card(0, 0, w4, "Who is at the gate, per custody (ToO §7.5)", g, draw=False),
             c.card(0, 0, w4, "Loss freezes the rules → re-genesis", f, draw=False),
             c.card(0, 0, w4, "The headline residual", r, draw=False),
             c.card(0, 0, w4, "Custody today", gc, draw=False))
    c.card(X0, y, w4, "Who is at the gate, per custody (ToO §7.5)", g, accent="brown", h=hh)
    c.card(X0 + (w4 + 30), y, w4, "Loss freezes the rules → re-genesis", f, accent="grey", h=hh)
    c.card(X0 + 2 * (w4 + 30), y, w4, "The headline residual", r, accent="red", h=hh, tint=False, dash="6 4")
    c.card(X0 + 3 * (w4 + 30), y, w4, "Custody today", gc, accent="brown", h=hh)
    y += hh + 30
    c.para(X0, y, W, "Status: ADR-0025 is **Accepted (genesis), 2026.09.23** (Batch 2), with no confirmation marker: "
           "a bootstrap record (ADR-0029 §4). A1 ratified 2026.09.30 (Batch 17) added item (f), the keys that vouch "
           "for artifacts; B29 (2026.10.04) added (g); **A2 and A3 ratified 2026.10.05 (Batch 34)**, A2 adding (h) "
           "and A3 the provider's key and the genesis seating. **A3 is provisional** with ADR-0050, and the genesis "
           "attestation must name it so (ADR-0029 A4). Not reviewed by a reader other than the drafter (ADR-0025 "
           "B34; G10 §4: no bootstrap reviewer is engaged).", 14.5, "muted")
    return c
