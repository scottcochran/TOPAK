"""B2 — The verified object and the parameterized edge (boundary B4), with the genesis floor in full."""
from lib import Canvas

ID, SLUG = "B2", "verified-object-and-edge"


def build():
    c = Canvas(ID, "The verified object and the parameterized edge: what is proved once, and what may only subtract",
               "Boundary B4. Inside: the enforcement mechanism, its version pinning, its epoch fencing, a minimal "
               "policy floor and a minimal rules floor, with the floor exceptions and the forensic classes written as "
               "floor entries. Outside: operational bundles, Personas and rungs, versioned parameters that may "
               "subtract authority and never add it. The genesis policy floor's seventeen policies are drawn in full; "
               "the text is a DRAFT, not ratified.",
               3200, "ToO rev 13 §2.5, §2.6, §2.9, §3.1–§3.3, §4.4, §6, §7.3, §7.4; G9 §2.1, §2.2, §2.3, §2.5, §2.7, §8, "
               "§7 items 25, 67, 83; "
               "ADR-0010 (A1, A2), ADR-0012, ADR-0013, ADR-0016, ADR-0018, ADR-0023, ADR-0026, ADR-0027, ADR-0028, "
               "ADR-0030 §1–§5, ADR-0031 §3, A2, ADR-0033 §5, A6, A7 and A8 (pending), ADR-0034, A2 (pending), ADR-0044; floor/genesis-floor.cedar, "
               "floor/README.md, floor/genesis-values.json, floor/genesis-gates-results-2026.10.01.txt; "
               "boundary register §6")
    X0, X1 = c.x0, c.x1
    y = c.y
    y += c.legend(X0, y, [
        ("box", "teal", "verified object"), ("box", "grey", "parameterized edge"), ("box", "violet", "draft"),
        ("box", "blue", "issued, ratified"), ("box", "red", "carve-out, exception, gap"),
        ("arrow", "green", "subtraction only", "7 5"),     ], title="Read as") + 34

    VW = 2080
    EX = X0 + VW + 170
    EW = X1 - EX
    top = y
    pad = 28
    ix = X0 + pad
    iw = VW - 2 * pad

    # ---------------------------------------------------------------- inside the verified object
    cy = top + 44
    w3 = (iw - 2 * 20) / 3
    trio = [
        ("Enforcement mechanism", "The admit path: epoch fence → lease → syntactic lift → floor → bundle → "
         "consensus-ordered admit → effect (ToO §15). The model-agnostic **validator** of the typed lift lives here "
         "(ADR-0018); schema S is enforced on every request (ADR-0030 §4)."),
        ("Version pinning", "The mechanism release carries the floor text, schema S, the values file, the Cedar "
         "engine and its version, and the resident genesis rules, each pinned by digest; at startup the reference "
         "refuses a floor whose bytes do not match the gated digests."),
        ("Epoch fencing", "Every action carries epoch and lease; actions under a fenced epoch are rejected **by the "
         "mechanism, ahead of the floor**, not by policy (ADR-0022 §2). The floor never decides whether an epoch is "
         "current."),
    ]
    th = max(c.card(0, 0, w3, t, [b], bullets=False, size=14.5, draw=False) for t, b in trio)
    trio_y = cy
    cy += th + 30

    # rules floor | exceptions | forensic
    rf = ("The rules floor (ADR-0026)", [
        "Bounds every **anchor issuance**, not admits; stays mechanism-checked, not Cedar (ADR-0030 §7).",
        "In force: **R1, R2, R5, R6, R7, R9**. R3 and R4 withdrawn. **R8** (break-glass TTL) drafted, pending.",
        "Changing it in either direction needs an anchor issuance and a promotion.",
    ])
    ex = ("Floor exceptions (ADR-0013 §2)", [
        "**X1 break-glass** (ADR-0009): adds authority; `Actuate` only; a quorum on the break-glass roster.",
        "**X2 erasure** (ADR-0006): destroys evidence; a quorum on the erasure roster, **none issued at genesis**.",
        "Count bounded by R6, currently two. **A bundle can narrow either, including break-glass**, never widen.",
    ])
    fo = ("Forensic floor (ADR-0028): one forbid on `Erase`", [
        "**F1** admit decisions · **F2** stop attribution · **F3** promotion votes · **F4** anchor issuances, genesis "
        "included · **F5** break-glass invocations · **F6** erasure events.",
        "No cognitive payload is in the floor. Removing a class is a floor relaxation.",
    ])
    TRIP = [(rf, "blue", "accepted", "bootstrap set"), (ex, "red", "accepted", "C1, C4"),
            (fo, "teal", "accepted", "C1")]
    # policy floor block
    pf_y = cy
    pf_head = ("The policy floor: Cedar, linked into the mechanism (ADR-0030 §2–§3)",
               ["**No process, no socket, no fetch.** The floor's only inputs are the typed lift and the issued rules, "
                "so no bundle can write a value the floor reads. Composition is a mechanism constant (§1, below).",
                "**The genesis floor is three files**, unchanged since G7 (G9 §2.2), gated six times, last on 2026.10.01, the first run "
                "with checked proofs. ADR-0030 ratified the language and the machinery, **not a floor**; ADR-0041 "
                "ratified what a Run floor must contain, not this one."])
    files = [
        ("`genesis-floor.cedar`", "17 policies, drawn in full below.", "sha256 `28ec0e4552c6a915`"),
        ("`genesis.cedarschema`: schema S", "The typed lift's type; the analyses quantify over every request and "
         "entity store S admits.", "sha256 `0ec2fa215eefe136`"),
        ("`genesis-values.json`", "`K` = 8, `T_obs` = 5000 ms, `T_persona` = 3 600 000 ms (1 h); θ_exact, θ_near, "
         "θ_gen, β, near_tool **unset**. **Every number is a placeholder.**", "sha256 `85ab6fefb66f0316`"),
    ]
    hh = c.card(0, 0, iw - 40, pf_head[0], pf_head[1], size=14.5, status="draft", draw=False)
    fw = (iw - 40 - 32 - 2 * 18) / 3
    fh = max(c.card(0, 0, fw, t, [b, d], bullets=False, size=14, draw=False) for t, b, d in files)
    pf_h = hh + fh + 12
    nb = ["**Epoch fencing**: the mechanism, ahead of the floor (ADR-0022 §2) · **the round bound**: a count, "
          "mechanism-checked, with `K < R` checked at startup (ADR-0022 §3) · **the rules floor**: bounds issuances, "
          "not admits (ADR-0030 §7) · **hermeticity of** `Invoke`: an obligation on each allowlist entry, not a request "
          "property."]
    nt = "Not in the policy floor, and why (header of `genesis-floor.cedar`)"
    nh = c.card(0, 0, iw, nt, nb, size=14, bullets=False, draw=False)
    eh = max(c.card(0, 0, w3, t[0], t[1], size=14, status=s, status_extra=e, draw=False) for t, a, s, e in TRIP)
    v_bot = pf_y + pf_h + 24 + eh + 24 + nh + 28
    c.region(X0, top, VW, v_bot - top, "The verified object (ADR-0010 with A1): proved once, with the mechanism",
             "teal", dash=None, sw=2.6, tint=True, size=16)
    for i, (t, b) in enumerate(trio):
        c.card(ix + i * (w3 + 20), trio_y, w3, t, [b], accent="teal", bullets=False, size=14.5, h=th)
    c.card(ix + 20, pf_y, iw - 40, pf_head[0], pf_head[1], accent="violet", size=14.5, status="draft",
           status_extra="floor text, S and values not ratified", h=pf_h)
    for i, (t, b, d) in enumerate(files):
        c.card(ix + 36 + i * (fw + 18), pf_y + hh - 4, fw, t, [b, d], accent="violet", bullets=False, size=14,
               h=fh, tint=False)
    cy = pf_y + pf_h + 24

    for i, (t, a, s, e) in enumerate(TRIP):
        c.card(ix + i * (w3 + 20), cy, w3, t[0], t[1], accent=a, size=14, status=s, status_extra=e, h=eh)
    cy += eh + 24
    c.card(ix, cy, iw, nt, nb, accent="grey", size=14, bullets=False, tint=False)
    cy += nh + 28
    v_bot = cy
    # ---------------------------------------------------------------- the edge
    ey = top + 44
    edge = [
        ("Operational bundles: OPA/Rego", "grey", [
            "Versioned parameters, promoted Build artifacts, at incident cadence. Evaluated per request over the "
            "lifted input; asked only **whether to refuse**, never whether to grant.",
            "A decision counts only from the revision the lease names; a sidecar with an in-process WASM fallback "
            "bound to that revision (ADR-0030 §1, ADR-0033 §5).",
            "Arguments and fine-grained rules live here, where they can only subtract (ADR-0041).",
        ], None, ""),
        ("A bundle is trusted by its signature, not its file name (ADR-0044)", "blue", [
            "The **bundle key** is in the issued rules (ADR-0025 §1 (f)); issuing or replacing it is an issuance.",
            "The signature covers the **content revision**, shipped as `<revision>.sig`; `load_dir` loads only what "
            "verifies; a sidecar's revision counts only if its signature was verified; a grant naming an unverified "
            "revision is refused.",
            "**Built** at the reference (ADR-0033 A6) under a dev key, custody (1, 0). **Not built**: signing at "
            "promotion as a pipeline step, and the key's custody row (G9 item 67).",
        ], "accepted", "C1"),
        ("Personas (ADR-0016 to ADR-0020)", "grey", [
            "Model, provenance, prompt, decoding parameters, **decoder** and seat binding, pinned; promoted, and a lease "
            "field, so re-attested at grant and renewal, at least every `T_persona` (ADR-0031 A2).",
            "The decoder ships in the Persona; the validator stays in the mechanism (ADR-0018).",
        ], None, ""),
        ("Rungs: deployment degeneracies (ADR-0023, ADR-0034)", "grey", [
            "Per-axis declarations: degenerate forms lose theorems, never gain capability. The confinement rung is a "
            "lease field, `[profile digest, rung]`. The reference grants rung 0 by operator, launches rung 1 on profiles "
            "that declare P3 `fail`, and rung 3 only **SIMULATED** (ADR-0033 A7, pending): **every real principal is** "
            "`Mediated` (G9 §2.3).",
            "Run's profile, with P4 replaced by **channel fidelity**, is ADR-0034 A2 (pending); the reference holds a "
            "Run profile's P4 at decide and at apply (A8, pending) and does not yet hold a Build profile's (G9 item 83).",
        ], None, ""),
    ]
    for t, a, b, s, e in edge:
        h = c.card(EX + 24, ey, EW - 48, t, b, accent=a, size=14, status=s, status_extra=e)
        ey += h + 18
    e_bot = max(ey + 10, v_bot)
    c.region(EX, top, EW, e_bot - top, "The parameterized edge", "grey", sw=2.4, size=16)
    # B4 between
    bx = X0 + VW + 85
    c.line(bx, top, bx, max(v_bot, e_bot), "teal", sw=3.2, dash="12 7")
    c.pill(bx, top - 13, "B4", "teal", size=16, solid=True, anchor="middle")
    c.arrow([(EX, top + 220), (X0 + VW, top + 220)], "green", dash="7 5", sw=2.6,
            label="refinements only:\nsubtraction", lpos=0.5, lw=150)
    y = max(v_bot, e_bot) + 40

    # ---------------------------------------------------------------- composition and residency
    w2 = (X1 - X0 - 30) / 2
    ch = c.card(X0, y, w2, "Composition: `admit ⟺ floor_permit ∧ ¬bundle_deny` (ADR-0030 §1)", [
        "`floor_permit` holds only when the floor returns Allow **with no evaluation error**: Cedar skips a policy that "
        "errors, so an erroring `forbid` would not fire, and any error is a deny.",
        "`bundle_deny` holds unless the bundle affirmatively allows: deny, error, undefined, absent and unreachable are "
        "all refusals. A floor deny short-circuits and **names its reason**: the forbids that fired, or no permit "
        "matched.",
        "So `bundle ⊑ floor` holds of the composed decision **for every bundle at every age**; stale bundles are "
        "monotone-safe, and nobody has to decide refinement at promotion. Given up: a bundle can never establish that "
        "something is allowed, and a bad bundle can disable break-glass, a liveness cost, never a widening.",
    ], accent="teal", size=14.5, status="accepted", status_extra="C1")
    c.card(X0 + w2 + 30, y, w2, "Residency: fail-closed with nothing to fetch", [
        "**The floor is resident** (ADR-0012): the default-deny bundle is pre-blessed, staged and instantiated, not "
        "fetched, so fail-closed works at cold start and under partition. Accepted ahead of its parent on that "
        "availability argument alone.",
        "**Genesis rules are resident** (ADR-0027): they ship with the mechanism release, and an admitted issuance is "
        "persisted with the same residency. Anchor unavailability blocks change, never operation.",
        "**The floor must stay minimal**: its reviewability by humans at deploy cadence is the basis for trusting "
        "promotion; a vacuous floor admits every bundle and discharges every property over nothing (ToO §3.1).",
    ], accent="teal", size=14.5, h=ch, status="accepted")
    y += ch + 60

    # ---------------------------------------------------------------- the seventeen policies
    c.text(X0, y + 22, "The genesis policy floor, all seventeen policies (`floor/genesis-floor.cedar`)", 22, "ink",
           bold=True)
    c.status(X0 + 1080, y + 4, "draft", "DRAFT · 2026.09.24, revised 2026.09.29")
    y += 40
    y += c.para(X0, y, X1 - X0,
                "Evaluation: any satisfied `forbid` denies; else any satisfied `permit` allows; else deny, and any "
                "evaluation error is a deny. Every permit is an envelope from a ratified record; every forbid is a "
                "carve-out the permits alone would not make. `ctx` is the request context; `alphabet` is the lease's; build and run abbreviate `principal.domain == \"build\"` and `== \"run\"`.",
                14.5, "muted") + 14
    cols = [("Policy `@id`", 330), ("Effect", 100, {"bold": True}),
            ("Action(s)", 300, {"mono": True}), ("When (condition, as written)", 1530), ("From the record", 0)]
    cols[-1] = ("From the record", X1 - X0 - sum(cc[1] for cc in cols[:-1]))
    P, F = "[[teal|permit]]", "[[red|forbid]]"
    rows = [
        {"cells": ["", "", "", "[[blue|" + "Build envelopes: ADR-0022 §1 (six)" + "]]", ""], "accent": "blue"},
        ["`B1-read-corpus`", P, "Read", "`principal.domain == \"build\"` ∧ `alphabet.contains(\"Read\")` ∧ "
         "`resource in context.corpusRoot`", "ADR-0022 §1"],
        ["`B2-draft-workspace`", P, "Draft", "build ∧ `alphabet.contains(\"Draft\")` ∧ `resource in context.workspace`",
         "ADR-0022 §1"],
        ["`B3-invoke-allowlisted`", P, "Invoke", "build ∧ `alphabet.contains(\"Invoke\")` ∧ `resource in "
         "context.toolAllowlist` ∧ `context.inputsInWorkspace`", "ADR-0022 §1, §3"],
        ["`B4-emit-own-topic`", P, "Emit", "build ∧ `alphabet.contains(\"Emit\")` ∧ `resource.owner == principal` ∧ "
         "`resource.epoch == context.epoch` ∧ `resource.round == context.round` ∧ `!resource.sealed`", "ADR-0022 §1"],
        ["`B5-submit-own-artifact`", P, "Submit", "build ∧ `alphabet.contains(\"Submit\")` ∧ `resource.author == "
         "principal`", "ADR-0022 §1"],
        ["`B6-vote-seated`", P, "Vote", "build ∧ `alphabet.contains(\"Vote\")` ∧ `context.voteRulesEpoch == "
         "context.rulesEpoch` ∧ ((`principal in context.grantRoster` ∧ `kind == \"grant\"`) ∨ (`principal in "
         "context.vetoRoster` ∧ `kind == \"observer\"`))", "ADR-0022 §1; tightened by ADR-0037 §4"],
        {"cells": ["", "", "", "[[red|" + "Carve-outs on the Build envelopes (four)" + "]]", ""], "accent": "red"},
        ["`B7-author-recused`", F, "Vote", "`resource.author == principal`. Recusal as floor text: relaxing it is a "
         "policy-floor relaxation (ADR-0022 A1)", "ADR-0022 §7, ADR-0024 §6"],
        ["`B8-grant-only-from-grant-seat`", F, "Vote", "`context.verdict == \"grant\"` ∧ `!(principal in "
         "context.grantRoster)`: a veto seat's alphabet lacks grant", "ADR-0024 §5"],
        ["`B9-voters-do-not-author`", F, "Draft, Invoke, Submit", "`context.roundRole == \"voter\"`: within a promotion "
         "round, voters review; they do not author", "ADR-0022 §7"],
        ["`B10-only-thinkers-author`", F, "Draft, Invoke, Submit, Actuate", "`principal.kind != \"thinker\"`: an Observer "
         "or a grant seat never authors, in either domain", "ADR-0037 §4"],
        {"cells": ["", "", "", "[[green|" + "Run envelopes: ADR-0040 §1, stated as ADR-0041 §1 (three)" + "]]", ""], "accent": "green"},
        ["`R1-actuate-allowlisted`", P, "Actuate", "`principal.domain == \"run\"` ∧ `alphabet.contains(\"Actuate\")` ∧ "
         "`resource in context.toolAllowlist`", "ADR-0040 §1, ADR-0041 §1"],
        ["`R2-report-own-topic`", P, "Report", "run ∧ `alphabet.contains(\"Report\")` ∧ `resource.owner == principal` ∧ "
         "current `epoch` and `round` ∧ `!resource.sealed`", "ADR-0040 §1, ADR-0041 §1"],
        ["`R4-consult-pinned`", P, "Consult", "run ∧ `alphabet.contains(\"Consult\")` ∧ `resource in context.runRoot`: "
         "ingress, not an effect; a live read is an `Actuate`", "ADR-0040 §1, ADR-0041 §1"],
        {"cells": ["", "", "", "[[pink|" + "Run carve-out (one)" + "]]", ""], "accent": "pink"},
        ["`R3-observer-live`", F, "Actuate, Report", "`principal.kind == \"thinker\"` ∧ `!context.observerLive`: every "
         "effect-bearing Run admit under a Thinker needs a live cell Observer (`T_obs`, `K`); `Consult` exempt; "
         "applies to break-glass too", "ADR-0039 §2, ADR-0041 §2"],
        {"cells": ["", "", "", "[[red|" + "Floor exceptions: ADR-0013 §2 (two; bounded by ADR-0026 R6)" + "]]", ""], "accent": "red"},
        ["`X1-break-glass`", P, "Actuate", "run ∧ `context.breakGlass.quorum` ∧ `resource in context.breakGlass.tools`: "
         "outside the allowlist, inside the issued envelope; never `Consult`, `Report`, `Vote`, `Submit` or `Erase`",
         "ADR-0009; ADR-0026 R7; ADR-0041 §3"],
        ["`X2-erasure`", P, "Erase", "`context.erasureQuorum`: FALSE from epoch 0, since genesis issues no erasure roster; "
         "admits nothing until bootstrap", "ADR-0006; ADR-0029 §5"],
        {"cells": ["", "", "", "[[teal|" + "The forensic floor: ADR-0028 (one)" + "]]", ""], "accent": "teal"},
        ["`F-forensic-classes`", F, "Erase", "`[\"F1\", \"F2\", \"F3\", \"F4\", \"F5\", \"F6\"].contains(resource.class)`: "
         "removing a class is a floor relaxation", "ADR-0028"],
    ]
    y += c.table(X0, y, cols, rows, size=14, accent="ink") + 24
    c.para(X0, y, X1 - X0,
           "Counts as `floor/README.md` gives them: six Build envelopes, four carve-outs, three Run envelopes, one Run "
           "carve-out, two exceptions, the forensic floor. One policy set serves both domains, scoped by "
           "`principal.domain`, because the per-class floor question is open (ToO §3.4; ADR-0014 reserved). Gate results "
           "for every policy are in B3.", 14.5, "muted")
    return c
