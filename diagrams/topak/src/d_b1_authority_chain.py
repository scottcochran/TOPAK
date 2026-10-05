"""B1 — The authority chain: from the sole axiom to an effect, and the audit chain back up."""
from lib import Canvas

ID, SLUG = "B1", "authority-chain"


def build():
    c = Canvas(ID, "The authority chain: one axiom, two verified floors, and every effect traced back up",
               "Authority flows down from a single assumed sentence, anchor intent, through anchor issuance bounded by "
               "the rules floor, issued rules, the promotion quorum, the policy floor and its bundles, the operators "
               "who put successor leases on the log, the lease, and the admit, to an effect. The audit chain runs the "
               "same links back up, and no link is assumed except the last. This is how the authority regress ends: one "
               "axiom, bounded by two verified floors. Since Batch 34 the operator is a principal and break-glass an "
               "emergency seating, both **provisional**.",
               3000, "ToO rev 14 §2.5, §3.1, §3.2, §3.3, §4.1, §4.4, §7.1–§7.7, §7.10, §9, §12, §15; G10 header, §1.1, "
               "§1.2, §2.1, §2.2, §2.3, §2.6, §3, §4, §5, §8, §7 items 8, 46, 57, 88, 92, and 11, 25, 27, 67 as at G9; "
               "ADR-0013 §1, §3 with A1; ADR-0015; ADR-0024 (§1–§9, A2, A3); ADR-0025 (§1 (a)–(h) with A1, A2, A3, "
               "§2, Annex); ADR-0026 (§1–§5, W1, A2); ADR-0027; ADR-0028 F2, F5; ADR-0029 §5 with A3, A4; ADR-0030 §1, "
               "§5, A3; ADR-0031 §1–§5, A2, A3; ADR-0033 §4, A6, A7, A11, A12; ADR-0041 A2, A3; ADR-0044; ADR-0045 "
               "T-0045-35, T-0045-36; ADR-0050 §1–§6, §10; ADR-0052 §1–§5, §9")
    X0, X1 = c.x0, c.x1
    y = c.y

    y += c.legend(X0, y, [
        ("box", "brown", "the anchor, humans, custody"), ("box", "blue", "issued rules, promotion"),
        ("box", "teal", "verified object, mechanism"), ("box", "green", "subtraction"),
        ("arrow", "blue", "authority flows down"), ("arrow", "violet", "the audit chain, back up"),
        ("arrow", "green", "subtraction: no quorum, attributed", "7 5"),
    ], title="Read as") + 34

    LW, RW = 760, 640
    gap = 70
    CX = X0 + LW + gap
    CW = X1 - RW - gap - CX
    RX = X1 - RW
    G = 74          # vertical gap between chain nodes (arrow + label)
    nodes = {}      # name -> (top, bottom)

    def node(name, title, body, accent, status=None, extra="", table=None, size=14.5):
        nonlocal y
        h = c.card(CX, y, CW, title, body, accent=accent, status=status, status_extra=extra, size=size,
                   draw=False)
        th = 0
        if table:
            th = c.table(0, 0, table[0], table[1], size=13.5, draw=False) + 16
        c.card(CX, y, CW, title, body, accent=accent, status=status, status_extra=extra, size=size, h=h + th)
        if table:
            c.table(CX + 16, y + h - 6, table[0], table[1], size=13.5, accent=accent)
        nodes[name] = (y, y + h + th)
        y += h + th + G

    def flow(a, b, label, acc="blue"):
        ya, yb = nodes[a][1], nodes[b][0]
        c.arrow([(CX + CW / 2, ya), (CX + CW / 2, yb)], acc, sw=2.6, label=label, lpos=0.5)

    # ---------------------------------------------------------------- the chain, top to bottom
    node("axiom", "0 · The sole axiom: anchor intent (ADR-0025 §2)", [
        "An authentic issuance at the current anchor epoch is what the anchor intended.",
        "**Assumed**, not modeled. No safety theorem covers it: a coalition at the capture threshold can issue any "
        "rules-floor-conformant roster. That is the headline residual (ToO §7.2).",
    ], "brown", status="accepted", extra="bootstrap set: no marker possible")
    node("issue", "1 · Anchor issuance: `Issue`, a havoc environment event (ADR-0025 §1–§2)", [
        "The trust anchor is the **sole issuer of rules**. `Issue` is constrained only by an opaque `Authentic`, "
        "epoch increment and the rules floor; safety must hold for **every** issuance the anchor could make, so its "
        "composition never enters the proof.",
        "Consensus-ordered; non-erasable as forensic class **F4**, genesis included (ADR-0028). Authority changes are "
        "exactly **{promotion, anchor issuance}** (ADR-0015).",
    ], "brown", status="accepted")
    node("rfloor", "2 · The rules floor bounds every issuance (ADR-0026)", [
        "Part of the verified object: the mechanism **rejects** any issuance that violates it. **Two keys, both "
        "directions**: a rules-floor change needs an anchor issuance and a promotion under the rules being replaced.",
    ], "teal", status="accepted", table=(
        [("Entry", 90, {"bold": True}), ("Bound (ToO §7.3, every row)", CW - 32 - 90 - 210), ("State at G10", 210)],
        [["R1", "`quorum = \"all\"` over counted grant seats", "In force"],
         ["R2", "`minGrant ≥ 2`", "In force"],
         {"cells": ["R3", "Withdrawn: recusal is enforced by the `Vote` envelope, so no issued value exists to bound",
                    "Withdrawn"], "accent": "grey"},
         {"cells": ["R4", "Withdrawn: a timeout never grants, now a mechanism constant", "Withdrawn"],
          "accent": "grey"},
         ["R5", "No key both in the anchor key set and on the promotion roster", "In force"],
         ["R6", "Exception-count bound; **the count it bounds is one, erasure**, since X1 was retired "
                "(ADR-0026 A2)", "In force · count [[blue|provisional]]"],
         ["R7", "No activation of an emergency seating grants a lease whose alphabet holds an authority act "
                "(A2); the kind's alphabet makes that true, and R7 is kept for the day it changes",
          "In force · subject [[blue|provisional]]"],
         ["R9", "`quorum = \"all\"` or `quorum ≥ 2`: a conditional entry, binding only once R1 is relaxed",
          "In force"],
         {"cells": ["R8", "A break-glass grant TTL. It needed trusted time; a grant now ends with its round "
                          "(ADR-0052 §3)", "Withdrawn 10.04 (W1), never in force"], "accent": "grey"}]))
    node("rules", "3 · Issued rules: the authority-defining set (ADR-0025 §1, with A1 to A3)", [
        "**(a)** the promotion roster and its parameters, `quorum` and `minGrant`; **(b)** the break-glass and erasure "
        "rosters; **(c)** the anchor's own key set; **(d)** any relaxation of the policy floor or new floor exception; "
        "**(e)** any change to the rules floor, either direction.",
        "**(f)** the keys the mechanism accepts a signature from in place of its own check: the **rung-3 verifier's "
        "appraisal key** and the **bundle-signing key** (A1, Batch 17), and since A3 **an identity provider's key**, "
        "under which an operator's sign-on is accepted (provisional). Replacing any adds authority, so it is an "
        "issuance. The first two exist at the reference (ADR-0033 A6); the verifier key is read at every rung-3 grant, "
        "renewal and Contested entry (A7, Batch 29), and the only keys in it are test keys, in **SIMULATED** runs.",
        "**(g)** the independence criterion in force (B29); **(h)** the **two lists** a bundle's load checks read "
        "(A2): the entries that may release a reserved label, and the channel targets inside the deployment. "
        "**(a)** is read to include the `operator` seats and, at genesis, the first operators' seatings (A3). "
        "**The rules floor bounds none of the three new things** (G10 §2.1).",
        "**Genesis rules are resident** (ADR-0027): they ship with the mechanism release, are fetched from nowhere, "
        "and are epoch 0, the root of the rules-epoch chain. Anchor unavailability blocks change, never operation. "
        "At bootstrap genesis issues **no erasure roster**.",
    ], "blue", status="accepted")
    node("promo", "4 · The promotion quorum (ADR-0024, with A2)", [
        "Everything crossing Build → Run is promoted: bundles, mechanism releases (floor changes included), Personas.",
        "**Every counted grant seat must grant** (`quorum = \"all\"`); a grant-seat deny or abstention denies; **a "
        "timeout is never a grant**. Veto seats (every cell Observer and correlator) can only deny; their silence is "
        "not a veto.",
        "Votes bind to **(artifact digest, gate-evidence digest, rules epoch)**: any rules-epoch change voids "
        "in-flight votes. The author is recused by the `Vote` envelope. Gates enable voting; they do not vote.",
        "A round stalls unless an independent veto seat was leased and the author's cell Observer covered the seal "
        "(A2.2, A2.3; A2.2 not yet in the reference, item 46).",
        "**A promotion seats** (A3, provisional): a promoted **seating** names a principal, its seat, Persona, bundle "
        "revision, confinement and alphabet, and the labels its task may carry; the completed tally grants the first "
        "lease at a fresh fence, with no request from anyone. [[red|Not built at the reference]] (G10 item 88).",
    ], "blue", status="accepted", extra="bootstrap set · A3 provisional")
    node("floor", "5 · Policy floor and bundle: `admit ⟺ floor_permit ∧ ¬bundle_deny` (ADR-0030 §1)", [
        "**The policy floor** is in the verified object, Cedar linked into the mechanism and resident. The floor in "
        "force is the proposed floor's `emergency` stage (28 policies, `15c941b9a56a09f7`), built in gated stages "
        "from the genesis draft: **genesis-provisional**, gated, pinned and enforced, ratified only when the bootstrap "
        "reviewer finds it fit (ADR-0030 A3; G10 §2.2). It decides operators' requests too, by `C1` to `C9`. "
        "Tightening it is an ordinary promotion; relaxing it adds an anchor issuance; the route is computed (§5).",
        "**The bundle** is a promoted parameter that can only subtract, at every age; it loads only under a signature "
        "from a key in the issued rules (ADR-0044; built at the reference under a dev key, custody (1, 0)).",
    ], "teal", status="accepted", extra="C1")
    node("op", "6 · Who puts a lease on the log (ADR-0031 A3; ADR-0050 §2, §4)", [
        "**A first lease comes from a quorum**, granted by the mechanism with no request: an anchor issuance for the "
        "rostered seats and the first operators at genesis, a promotion's tally on a seating for everyone else.",
        "**An operator renews what a quorum granted.** An operator is a principal on a seat of kind `operator`, a "
        "person, `Mediated`, treated as havoc. Its requests are signed with its Persona's key and decided by the "
        "floor's nine control entries, `C1` to `C9`, then re-checked by every replica at apply.",
    ], "blue", status="provisional", extra="ADR-0050 · C1, C3, C4", table=(
        [("Request", 300), ("Kind", 80), ("Needs (ToO §7.10; ADR-0041 A3)", CW - 32 - 380)],
        [["`Regrant` (a successor grant: the next round, nothing wider), `Renew`, `AttestGates`", "Add",
          "A live lease and **a live peer** in the domain; never oneself (`C1`–`C3`, `C5`, `C6`, `C8`)"],
         ["`EndRound`, `Revoke`", "Deny", "A Persona in force, and a live lease **or a fresh sign-on**; own domain "
          "only (`C4`, `C9`)"],
         ["`FenceEpoch`", "Deny", "A Persona in force **and a live lease** (`C4`, `C7`)"]]))
    node("lease", "7 · The lease: one composite credential per round (ADR-0031)", [
        "Twelve fields, a closed schema: `principal`, `seat`, `persona`, `epoch`, `fence`, `rulesEpoch`, `bundle`, "
        "`confinement`, `alphabet`, `round`, `role`, `ttl`. **A capability that is not a field is not carried.**",
        "The **fence is the Paxos log index at grant**; `rulesEpoch` and `bundle` bind the lease to the rules and "
        "the bundle revision in force; `ttl ≤ T_persona` (A2). Renewal only narrows; at most one live lease per "
        "principal.",
    ], "green", status="accepted", extra="C1; C2 for A1")
    node("admit", "8 · The admit: decided, ordered, re-checked (ADR-0015; ADR-0033 §4)", [
        "Epoch fence → lease → syntactic lift → floor → bundle → **consensus-ordered admit**. The mechanism checks "
        "run twice: before the floor, and again at the entry's log position; an admit that fails the second is "
        "**void**: ordered, recorded, without effect.",
        "Every effect therefore has a consensus-ordered, signed, authorizing predecessor in the Paxos log. **Denials "
        "are not ordered**, and they are recorded (ADR-0020).",
    ], "teal", status="accepted", extra="ADR-0015: C2")
    node("effect", "9 · The effect: exactly {tool invocation, principal emission} (ADR-0015)", [
        "Build: `Invoke`, and the emissions `Emit`, `Submit`, `Vote`; Run: `Actuate` and `Report` (`Consult` is "
        "ingress, no effect). The effect runs only after commit; a crash between commit and effect leaves no effect, "
        "which is safe.",
    ], "grey")
    y -= G

    flow("axiom", "issue", "an authentic issuance at epoch e + 1", "brown")
    flow("issue", "rfloor", "checked against", "brown")
    flow("rfloor", "rules", "admitted: rules epoch e + 1, persisted with genesis residency")
    flow("rules", "promo", "roster, `quorum`, `minGrant`, veto seats")
    flow("promo", "floor", "promoted artifact: floor release, signed bundle")
    flow("floor", "op", "`C1` to `C9` decide every operator request")
    flow("op", "lease", "the lease names the bundle revision and rules epoch")
    flow("lease", "admit", "every action carries epoch and lease")
    flow("admit", "effect", "after commit, on the deciding replica", "teal")

    # ---------------------------------------------------------------- left: the three treatments, custody
    ly = nodes["axiom"][0]
    th = c.table(X0, ly, [("Property", 130, {"bold": True}), ("Treatment (ADR-0025 §2; ToO §7.2)", LW - 130)], [
        {"cells": ["Intent", "**Assumed**, the sole axiom: an authentic issuance at the current anchor epoch is what "
                   "the anchor intended."], "accent": "red"},
        {"cells": ["Integrity", "**Modeled**: `Issue` is an environment action bounded by an opaque `Authentic`, "
                   "epoch increment, and the rules floor"], "accent": "teal"},
        {"cells": ["Custody", "**Declared** per deployment position: the pair (capture threshold, loss tolerance)"],
         "accent": "brown"},
    ], size=14, accent="brown")
    c.arrow([(X0 + LW, ly + 60), (CX, ly + 60)], "brown", dash="4 4", head=False)
    ly2 = nodes["issue"][0] + 10
    ly2 = max(ly2, ly + th + 30)
    ch = c.table(X0, ly2, [("Record", 150, {"bold": True}), ("Custody model", LW - 150 - 150),
                           ("(capture, loss)", 150, {"mono": True})], [
        ["A-0025 (archetype)", "Strict unanimity, n ≥ 3", "(n, 0)"],
        ["D-0025-2", "n−1 eviction with replacement", "(n−1, 1)"],
        ["D-0025-1", "Threshold with recovery, in the shape of The Update Framework (TUF) root role", "(k, n−k)"],
        {"cells": ["—", "Single custodian: **genesis today**, Scott (G10 header; item 11)", "(1, 0)"],
         "accent": "red"},
    ], size=14, accent="brown")
    ly3 = ly2 + ch + 20
    c_h = c.card(X0, ly3, LW, "Custody is a declaration, not a proof", [
        "Custody instantiates `Authentic` outside the model, so degrading it reopens nothing; the quorum's archetype "
        "values live inside the rules floor, so degrading them is a mechanism release (ToO §7.7).",
        "At archetype custody **loss freezes the rules**: the system runs and subtracts but cannot change; the only "
        "exit is **re-genesis**, a successor system. At archetype custody the key-holders sit at the gate (§7.5).",
        "A solo bootstrap is not a bootstrap: the archetype needs five humans, three key-holders plus two counted "
        "grant seats, disjoint by R5 (ToO §9).",
    ], accent="brown", size=14)

    # left, lower: what does not go through the chain, and what stands in for a quorum
    bgy = max(nodes["promo"][0], ly3 + c_h + 30)
    bgh = c.card(X0, bgy, LW, "Break-glass is an emergency seating, not a third kind (ADR-0052)", [
        "**The roster's quorum activates** a seating prepared by promotion: **one lease, for one named person and one "
        "round**, with the round's task. No successor, no renewal; another round is another quorum. It ends with its "
        "round, which is why R8 was withdrawn (ADR-0013 A1; ADR-0026 W1).",
        "**The envelope is an ordinary allowlist**, by default every Run entry in force in the domain, so the floor "
        "needs no exception: `X1-break-glass` **is retired**, and the floor's one exception is erasure (R6). Erasure "
        "stays an admit against its exception entry (ADR-0015 R2).",
        "The seat is a person's, kind `emergency`, alphabet `Consult`, `Actuate`, `Report`: R7 has nothing to refuse. "
        "Privileged grants still share one model, a quorum on an **anchor-issued roster**, bounded by the rules floor.",
        "[[red|Not built]]: a seating prepared by promotion; the reference makes it by the BOOTSTRAP socket "
        "(item 92). X1's retirement stands on a record subject to redesign.",
    ], accent="red", size=14, status="provisional", status_extra="ADR-0052 · C1, C3, C4")
    oy = max(nodes["op"][0], bgy + bgh + 30)
    oh = c.card(X0, oy, LW, "BOOTSTRAP: whoever reaches the socket can seat", [
        "The reference keeps its unsigned operator socket as a **marked BOOTSTRAP path that seats and does nothing "
        "else** (ADR-0050 §10, R9; ADR-0033 A11). It stands in for the quorum a first lease should come from: "
        "**D-0050-1 for that one step**, and the debt ADR-0050's provisional status carries.",
        "Everything after the first seating is a signed request decided by `C1` to `C9`: successor grants, renewals, "
        "gate attestations, ends of round, revocations, the fence (ToO §15).",
        "Exit from provisional (item 88): a first lease from a completed tally, the first operators seated by an "
        "issuance, a `Regrant` at rung 1 or above, an operator's Persona record and lineage, and a review.",
    ], accent="red", size=14, status="notbuilt", status_extra="a first lease from a quorum")
    c.arrow([(X0 + LW, oy + 40), (CX, oy + 40)], "red", dash="4 4", head=False)
    sy = max(nodes["lease"][0], oy + oh + 30)
    c.card(X0, sy, LW, "Runtime subtraction is not promotion", [
        "E-stop, lease expiry, targeted revocation, epoch fence, abstention, end of round and `deny=all` **need no "
        "quorum** and are attributed (ADR-0024 §9, ADR-0031).",
        "**Who denies** (ADR-0031 A3): both revocation tools are an operator's signed act, with no quorum and no peer; "
        "a revocation or end of round needs a live lease or a fresh sign-on, the fence a live lease. **A deny needs no "
        "lease**, and the signature is the attribution F2 asks for (ADR-0028).",
        "**Ordering is not authorization**: where they change replicated state they are still consensus-ordered, or "
        "replicas disagree about what is live (ADR-0033 §4).",
        "Denials are local and unordered: a denied effect never crosses the boundary.",
    ], accent="green", size=14, dash="6 4", tint=False)
    c.arrow([(X0 + LW, sy + 40), (CX, sy + 40)], "green", dash="7 5")

    # ---------------------------------------------------------------- right: the audit chain, back up
    ax = RX + 70
    top = nodes["axiom"][0] + 30
    bot = nodes["effect"][1] - 30
    c.arrow([(ax, bot), (ax, top)], "violet", sw=5)
    c.text(RX, nodes["axiom"][0] - 26, "The audit chain (ToO §4.1)", 19, "violet", bold=True)
    steps = [
        ("effect", "**effect**: the tool invocation or emission"),
        ("admit", "→ **admit**: the consensus-ordered decision, kept as F1"),
        ("lease", "→ **lease**: a quorum's first lease, or a signed operator request under it"),
        ("floor", "→ **floor ∧ bundle**, at the lease's bundle revision, with the digest of the frozen input"),
        ("rules", "→ **rules epoch**: the rules in force at grant"),
        ("issue", "→ **issuance**: the `Issue` that defined those rules, kept as F4"),
        ("axiom", "→ **ADR-0025's intent axiom**"),
    ]
    for key, txt in steps:
        t, b = nodes[key]
        yy = min(t + 40, b - 40)
        c.line(CX + CW, yy, ax, yy, "violet", sw=1.4, dash="3 4")
        c.rect(ax - 9, yy - 9, 18, 18, "violet", tint=False, rx=9, sw=2)
        c.para(ax + 26, yy - 12, RW - 100, txt, 14.5, "ink")
    c.card(ax + 34, nodes["promo"][0], X1 - ax - 34, "No link is assumed except the last", [
        "Every authorization is traceable to a consensus-ordered issuance that defined the rules in force "
        "(ADR-0015).",
        "Votes in the chain are the admit decisions in the consensus log (F3), not the topic emissions that carry "
        "them; commentary is erasable, the vote is not (ToO §4.4).",
        "Since 2026.10.01 the gate evidence a vote binds to carries a checked proof for every solver-backed routing "
        "`holds` (ADR-0030 A1). The evidence itself is an operator's `AttestGates`: **attributed, and still an "
        "assertion** (ADR-0024 A3; G10 item 57).",
        "A stop is signed: the signature is the attribution ADR-0028's F2 asks for (ADR-0031 A3). An activation of an "
        "emergency seating is a forensic-floor record, F5 (ADR-0052 §5).",
    ], accent="violet", size=14, tint=False)

    # ---------------------------------------------------------------- bottom: how the regress ends
    y += 70
    c.text(X0, y + 22, "How the regress ends (ToO §7.6)", 22, "ink", bold=True)
    y += 44
    tw = 1400
    rh = c.table(X0, y, [("Record", 300, {"bold": True}), ("Terminus", tw - 300)], [
        ["ADR-0002 (09.12)", "A declared axiom set"],
        ["ADR-0010 (09.12)", "A verified artifact, the policy floor, rather than an axiom set"],
        {"cells": ["ADR-0025 with ADR-0026", "**One axiom (anchor intent), bounded by two verified floors**"],
         "accent": "blue"},
    ], size=15, accent="ink")
    c.card(X0, y + rh + 20, tw, "Stages of one argument", [
        "The authority regress now ends the way the policy regress does: **a verified floor, with a single sentence "
        "assumed above it** (§7.6). The two floors are the rules floor (step 2) and the policy floor (step 5).",
    ], accent="blue", size=15, bullets=False)
    bx = X0 + tw + 40
    bw = X1 - bx
    fl = 180
    for i, (t, a) in enumerate([("Anchor intent: assumed", "red"), ("Rules floor: verified", "teal"),
                                ("Policy floor: verified (genesis-provisional)", "teal")]):
        c.rect(bx + i * 60, y + i * (fl / 3 + 16), bw - 2 * i * 60, fl / 3, a, tint=True, rx=8, sw=2)
        c.text(bx + bw / 2, y + i * (fl / 3 + 16) + fl / 6 + 6, t, 17, a, bold=True, anchor="middle")
    c.para(bx, y + fl + 50, bw,
           "**Not yet in force anywhere:** only two of the five bootstrap modules are drafted (`BreakGlass_A1` "
           "succeeds the second); bootstrap needs a drafted specification and an independent review of the whole "
           "corpus (ADR-0029 A2), and **no bootstrap reviewer is engaged** (G10 §4). Until then everything ratified is "
           "the genesis custodian's declaration, custody (1, 0), and two records are provisional (ToO §9).", 14.5,
           "muted")
    return c
