"""B2 — The verified object and the parameterized edge (boundary B4), with the policy floor in force in full."""
from lib import Canvas
from d_b8_floor_stages import POLICIES

ID, SLUG = "B2", "verified-object-and-edge"


def build():
    c = Canvas(ID, "The verified object and the parameterized edge: what is proved once, and what may only subtract",
               "Boundary B4. Inside: the enforcement mechanism, its version pinning, its epoch fencing, a minimal "
               "policy floor and a minimal rules floor, with the floor exceptions and the forensic classes written as "
               "floor entries. Outside: operational bundles, Personas and rungs, versioned parameters that may "
               "subtract authority and never add it. The policy floor in force, the `emergency` stage's twenty-eight "
               "policies, is drawn in full: it is genesis-provisional (ADR-0030 A3), gated, pinned and enforced, and "
               "not ratified.",
               3200, "ToO rev 14 §2.5, §2.6, §2.9, §2.10, §3.1–§3.3, §4.4, §6, §7.3, §7.4, §7.10; G10 §1.2, §2.1, §2.2, "
               "§2.3, §2.5, §2.7, §8, §7 items 1, 2, 25, 87, 90, 91, 92 (items 67 and 83 as at G9); "
               "ADR-0009 A1, ADR-0010 (A1, A2), ADR-0012, ADR-0013 §2, A1, ADR-0016 A1, A2, ADR-0018, ADR-0023, "
               "ADR-0025 A2, A3, ADR-0026 W1, A2, ADR-0027, ADR-0028, ADR-0029 A4, ADR-0030 §1–§5, A2, A3, ADR-0031 §3, "
               "A2, ADR-0033 §5, A6–A12, ADR-0034 A2, ADR-0039 A2, ADR-0041 A1–A3, ADR-0042 §6, ADR-0044, ADR-0047 §7, "
               "§8, ADR-0049 §6, ADR-0050 §4, ADR-0052 §1, §2; floor/proposed/emergency-floor.cedar, "
               "emergency.cedarschema, README.md; floor/genesis-floor.cedar, floor/genesis-values.json; "
               "mechanism/crates/topak-floor/src/lib.rs; boundary register §6")
    X0, X1 = c.x0, c.x1
    y = c.y
    y += c.legend(X0, y, [
        ("box", "teal", "verified object"), ("box", "grey", "parameterized edge"),
        ("box", "violet", "draft or genesis-provisional: not ratified"),
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
         "(ADR-0018); schema S is enforced on every request (ADR-0030 §4). It computes the label facts the floor "
         "reads (ADR-0030 A2) and checks a bundle's allowlist at load (ADR-0049 §6)."),
        ("Version pinning", "The mechanism release carries the floor text, schema S, the values file, the Cedar "
         "engine and its version, and the resident genesis rules, each pinned by digest; at startup the reference "
         "refuses a floor whose bytes do not match the gated digests, since `9c57221` the `emergency` stage's "
         "(ADR-0033 A12)."),
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
        "In force: **R1, R2, R5, R6, R7, R9**. R3 and R4 withdrawn. **R8 withdrawn** (ADR-0026 W1): a break-glass "
        "grant ends with its round.",
        "**R6** bounds the floor exceptions, and the count is **one**; **R7** reads \"no activation of an emergency "
        "seating grants a lease whose alphabet holds an authority act\" (ADR-0026 A2, [[blue|provisional]]).",
        "The rules gain three issued things the rules floor bounds none of: an identity provider's key (ADR-0025 A3, "
        "[[blue|provisional]]) and the two lists a bundle's load checks read (A2). `RulesFloorBase.tla` still "
        "carries `bgScope` and a bound of two (G10 item 90).",
        "Changing it in either direction needs an anchor issuance and a promotion.",
    ])
    ex = ("Floor exceptions (ADR-0013 §2, A1): one", [
        "**X2 erasure** (ADR-0006): destroys evidence; a quorum on the erasure roster, **none issued at genesis**.",
        "**X1 break-glass is retired** (ADR-0013 A1; ADR-0041 A2; ADR-0009 A1): break-glass is an emergency seating "
        "(ADR-0052, [[blue|provisional]]). The roster's quorum seats a named person on a seat of kind `emergency` for "
        "one round, and `R1` admits its calls over the envelope computed at activation. X1's retirement is in force on "
        "a record subject to redesign (G10 §1.2).",
        "Count bounded by R6, now one. A bundle can narrow it, never widen; a bad bundle can disable an emergency "
        "seat's tools, a liveness cost (ToO rev 14 §3.1).",
    ])
    fo = ("Forensic floor (ADR-0028): one forbid on `Erase`", [
        "**F1** admit decisions · **F2** stop attribution · **F3** promotion votes · **F4** anchor issuances, genesis "
        "included · **F5** break-glass invocations, now an emergency activation (ADR-0052) · **F6** erasure events.",
        "No cognitive payload is in the floor. Removing a class is a floor relaxation.",
    ])
    TRIP = [(rf, "blue", "accepted", "bootstrap set"), (ex, "red", "accepted", "C1, C4"),
            (fo, "teal", "accepted", "C1")]
    # policy floor block
    pf_y = cy
    pf_head = ("The policy floor: Cedar, linked into the mechanism (ADR-0030 §2–§3)",
               ["**No process, no socket, no fetch.** The floor's only inputs are the typed lift and the issued rules, "
                "so no bundle can write a value the floor reads. Composition is a mechanism constant (§1, below).",
                "**The floor in force is the** `emergency` **stage** of `floor/proposed/`, built in three gated stages from "
                "the genesis draft (`labels`, `control`, `emergency`; diagram B8) and linked by the reference since "
                "`9c57221`. The entries in force changed for the first time since G7 (G10 §2.2): **three forbids over "
                "labels, nine control entries, and X1 removed** (ADR-0041 A1 to A3).",
                "**Genesis-provisional** (ADR-0030 A3): gated, pinned and enforced, and ratified by no batch. It is "
                "ratified when the bootstrap reviewer establishes that it is fit (ADR-0029 A4), and nothing says how "
                "fitness is tested (G10 item 87). ADR-0030 ratified the language and the machinery; ADR-0041 what the "
                "floor must contain, entry by entry, not a text. The stage files' opening comment says they are not "
                "what the reference follows, which is wrong (item 91)."])
    files = [
        ("`emergency-floor.cedar`", "28 policies, drawn in full below. Gated 2026.10.04, 107 cases.",
         "sha256 `15c941b9a56a09f7`"),
        ("`emergency.cedarschema`: schema S", "The typed lift's type, now with the label facts, `ControlCtx` and the "
         "kinds `operator` and `emergency`; no break-glass fields.", "sha256 `d3c8145c6af2d9a3`"),
        ("`genesis-values.json`", "`K` = 8, `T_obs` = 5000 ms, `T_persona` = 1 h; θ_exact, θ_near, θ_gen, β, "
         "near_tool **unset**. Unchanged by the stages. **Every number is a placeholder.**",
         "sha256 `85ab6fefb66f0316`"),
        ("`genesis-floor.cedar` and its schema", "The DRAFT the stages are built from, unchanged: 17 policies, 62 "
         "cases, `X1` among them. Linked until `7764e52`.", "sha256 `28ec0e4552c6a915`, `0ec2fa215eefe136`"),
    ]
    hh = c.card(0, 0, iw - 40, pf_head[0], pf_head[1], size=14.5, status="genprov", draw=False)
    fw = (iw - 40 - 32 - 3 * 18) / 4
    fh = max(c.card(0, 0, fw, t, [b, d], bullets=False, size=14, draw=False) for t, b, d in files)
    pf_h = hh + fh + 12
    nb = ["**Epoch fencing**: the mechanism, ahead of the floor (ADR-0022 §2) · **the round bound**: a count, "
          "mechanism-checked, with `K < R` checked at startup (ADR-0022 §3) · **the rules floor**: bounds issuances, "
          "not admits (ADR-0030 §7) · **hermeticity of** `Invoke`: an obligation on each allowlist entry, not a request "
          "property · **F4 to F6**: load checks on bundle data, W7 to W9 (ADR-0049 §6), made by the mechanism · "
          "**a first lease**: granted by the mechanism when a quorum completes (ADR-0050 §2), not an action."]
    nt = "Not in the policy floor, and why (the floor text's header; ADR-0049 §6; ADR-0050 §2)"
    nh = c.card(0, 0, iw, nt, nb, size=14, bullets=False, draw=False)
    eh = max(c.card(0, 0, w3, t[0], t[1], size=14, status=s, status_extra=e, draw=False) for t, a, s, e in TRIP)
    v_bot = pf_y + pf_h + 24 + eh + 24 + nh + 28
    c.region(X0, top, VW, v_bot - top, "The verified object (ADR-0010 with A1): proved once, with the mechanism",
             "teal", dash=None, sw=2.6, tint=True, size=16)
    for i, (t, b) in enumerate(trio):
        c.card(ix + i * (w3 + 20), trio_y, w3, t, [b], accent="teal", bullets=False, size=14.5, h=th)
    c.card(ix + 20, pf_y, iw - 40, pf_head[0], pf_head[1], accent="violet", size=14.5, status="genprov",
           status_extra="ADR-0030 A3 · ratified at bootstrap", h=pf_h)
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
            "Arguments and fine-grained rules live here, where they can only subtract (ADR-0041 §5). So do **the "
            "label declarations and the delivery table** (ADR-0041 A1 §5; ADR-0047 §8): a promotion may move every "
            "label to clear, and cannot loosen `R5` to `R7`, which then refuse more.",
            "**A bundle loads only if its allowlist is well-formed**: W1 to W10 on ADR-0049's one entry schema, after "
            "the signature and before any decision counts; a mechanism constant no bundle can waive (ADR-0030 A2).",
        ], None, ""),
        ("A bundle is trusted by its signature, not its file name (ADR-0044)", "blue", [
            "The **bundle key** is in the issued rules (ADR-0025 §1 (f)); issuing or replacing it is an issuance.",
            "The signature covers the **content revision**, shipped as `<revision>.sig`; `load_dir` refuses any file "
            "that does not verify, and **one refused file stops the node from starting** rather than being skipped "
            "(inventory finding 20); a sidecar's revision counts only if its signature was verified; a grant naming an "
            "unverified revision is refused.",
            "**Built** at the reference (ADR-0033 A6) under a throwaway dev key, custody (1, 0). **Not built**: signing "
            "at promotion as a pipeline step, and the key's custody row (item 67, open).",
        ], "accepted", "C1"),
        ("Personas (ADR-0016 to ADR-0020)", "grey", [
            "Model, provenance, prompt, decoding parameters, **decoder** and seat binding, pinned; promoted, and a lease "
            "field, so re-attested at grant and renewal, at least every `T_persona` (ADR-0031 A2).",
            "The decoder ships in the Persona; the validator stays in the mechanism (ADR-0018).",
            "**A person's Persona** (ADR-0016 A1, A2): a key, a role, a domain and a lineage rooted in an identity "
            "provider. `Seat binding` gains `operator` and `emergency` ([[blue|provisional]], with ADR-0050 and "
            "ADR-0052); no model's Persona binds to `emergency`.",
        ], None, ""),
        ("Rungs: deployment degeneracies (ADR-0023, ADR-0034)", "grey", [
            "Per-axis declarations: degenerate forms lose theorems, never gain capability. The confinement rung is a "
            "lease field, `[profile digest, rung]`. The reference grants rung 0, launches rung 1 on profiles that "
            "declare P3 `fail`, and rung 3 only **SIMULATED** (ADR-0033 A7, Batch 29): **no real principal is** "
            "`Contained` (G10 §2.3, item 1). An operator and an emergency seat are `Mediated` by design: a person is "
            "not confined.",
            "**The Run profile is in force**: ADR-0034 A2 with ADR-0042 §6 (Batch 30), P4 replaced by **channel "
            "fidelity**. The tool host binds a Wasm tool's one connection to the target its allowlist entry declares "
            "(ADR-0033 A8, A9); a Build profile's P4 is not yet held (item 83).",
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
        "something is allowed, and a bad bundle can disable an emergency seat's tools, a liveness cost, never a "
        "widening.",
        "`bundle ⊑ floor` is decided over action variants and says nothing about delivery, so **the label minimum is in "
        "the floor**, where a bundle cannot loosen it: delivering more in the clear buys a narrower round (ADR-0047 "
        "§7, §8; G10 §2.5). An operator's control request is decided by the floor's `C1` to `C9` alone: at the "
        "reference there is no bundle tier for it (ADR-0033 A11).",
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

    # ---------------------------------------------------------------- the twenty-eight policies
    c.text(X0, y + 22, "The policy floor in force, all twenty-eight policies (`floor/proposed/emergency-floor.cedar`)",
           22, "ink", bold=True)
    c.status(X1, y + 4, "genprov", "ADR-0030 A3 · gated 2026.10.04 · 15c941b9a56a09f7", anchor="end")
    y += 40
    y += c.para(X0, y, X1 - X0,
                "Evaluation: any satisfied `forbid` denies; else any satisfied `permit` allows; else deny, and any "
                "evaluation error is a deny. Every permit is an envelope from a ratified record; every forbid is a "
                "carve-out the permits alone would not make. `alphabet` is `context.lease.alphabet`; build and run "
                "abbreviate `principal.domain == \"build\"` and `== \"run\"`; operator abbreviates `principal.kind == "
                "\"operator\"`. The retired `X1` is shown where it stood and is not counted. The control entries rest on "
                "ADR-0050 and the emergency change on ADR-0052, both [[blue|provisional]].",
                14.5, "muted") + 14
    cols = [("Policy `@id`", 330), ("Effect", 100, {"bold": True}),
            ("Action(s)", 330), ("When (condition, as written)", 1530), ("From the record", 0)]
    cols[-1] = ("From the record", X1 - X0 - sum(cc[1] for cc in cols[:-1]))
    rows = []
    for r in POLICIES:
        if isinstance(r, dict) and "group" in r:
            rows.append(r)
        elif isinstance(r, dict):
            rows.append({**r, "cells": r["cells"][:5]})
        else:
            rows.append(r[:5])
    y += c.table(X0, y, cols, rows, size=14, accent="ink") + 24
    c.para(X0, y, X1 - X0,
           "Counts: six Build envelopes, four Build carve-outs, three Run envelopes, four Run carve-outs (`R3`, and "
           "`R5` to `R7` over labels), one exception, the forensic floor, four control permits and five control "
           "forbids: **28**, where the genesis draft has 17. One policy set serves both domains, scoped by "
           "`principal.domain` and `principal.kind`, because the per-class floor question is open (ToO rev 14 §3.4; "
           "ADR-0014 reserved). How each stage was built and what its gates show is B8.", 14.5, "muted")
    return c
