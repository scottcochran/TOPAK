"""D2 — Policy composition: admit ⟺ floor_permit ∧ ¬bundle_deny."""
from lib import Canvas, text_width

ID, SLUG = "D2", "policy-composition"

W = 3100

FLOOR_ROWS = [
    {"group": "Build envelopes (ADR-0022 §1)", "accent": "blue"},
    ["B1-read-corpus", "permit", "`Read`", "Build seat; `Read` in the lease's alphabet; object in the corpus root", "ADR-0022 §1"],
    ["B2-draft-workspace", "permit", "`Draft`", "Build; in the alphabet; target in the round workspace", "ADR-0022 §1"],
    ["B3-invoke-allowlisted", "permit", "`Invoke`", "Build; in the alphabet; tool on the allowlist (`name@digest`); "
     "inputs in the workspace", "ADR-0022 §1, §3"],
    ["B4-emit-own-topic", "permit", "`Emit`", "Build; in the alphabet; own topic of this epoch and round; not sealed",
     "ADR-0022 §1"],
    ["B5-submit-own-artifact", "permit", "`Submit`", "Build; in the alphabet; the principal is the artifact's author",
     "ADR-0022 §1"],
    ["B6-vote-seated", "permit", "`Vote`", "Build; in the alphabet; the vote's rules epoch is current; on the grant roster "
     "as a `grant` seat, or on the veto roster as an `observer` seat", "ADR-0037 §4"],
    {"group": "Carve-outs on the Build envelopes", "accent": "red"},
    ["B7-author-recused", "forbid", "`Vote`", "The voter authored the artifact", "ADR-0022 §7, ADR-0024 §6"],
    ["B8-grant-only-from-grant-seat", "forbid", "`Vote`", "Verdict `grant` from a seat not on the grant roster",
     "ADR-0024 §5"],
    ["B9-voters-do-not-author", "forbid", "`Draft` `Invoke` `Submit`", "The round role is `voter`", "ADR-0022 §7"],
    ["B10-only-thinkers-author", "forbid", "`Draft` `Invoke` `Submit` `Actuate`", "The seat kind is not `thinker`",
     "ADR-0037 §4"],
    {"group": "Run envelopes (ADR-0040 §1, stated as ADR-0041 §1) and their carve-out", "accent": "green"},
    ["R1-actuate-allowlisted", "permit", "`Actuate`", "Run seat; in the alphabet; tool on the allowlist", "ADR-0041 §1"],
    ["R2-report-own-topic", "permit", "`Report`", "Run; in the alphabet; own topic of this epoch and round; not sealed",
     "ADR-0041 §1"],
    ["R4-consult-pinned", "permit", "`Consult`", "Run; in the alphabet; object in the pinned Run root", "ADR-0041 §1"],
    ["R3-observer-live", "forbid", "`Actuate` `Report`", "A `thinker` seat without `observerLive` (the lift's `live(o)`); "
     "applies to break-glass too", "ADR-0039 §2, ADR-0041 §2"],
    {"group": "Floor exceptions (ADR-0013 §2): count 2, bounded by rules-floor R6", "accent": "violet"},
    ["X1-break-glass", "permit", "`Actuate`", "Run seat; break-glass quorum; tool inside the issued break-glass envelope",
     "ADR-0009, ADR-0013"],
    ["X2-erasure", "permit", "`Erase`", "An erasure quorum on the issued roster: **FALSE at genesis**, which issues no "
     "roster", "ADR-0006, ADR-0013"],
    {"group": "The forensic floor (ADR-0028)", "accent": "brown"},
    ["F-forensic-classes", "forbid", "`Erase`", "The record's class is one of F1–F6", "ADR-0028 §2"],
]


def build():
    c = Canvas(ID, "Policy composition: `admit ⟺ floor_permit ∧ ¬bundle_deny`",
               "Two tiers decide every admit over one frozen input. The floor, a verified evaluator linked into the "
               "mechanism, is the only tier that can permit. The bundle, per-request and signed, is asked only whether "
               "to refuse, and only after the floor permits. Composition is a mechanism constant, so `bundle ⊑ floor` "
               "holds for every bundle at every age.",
               W, "ADR-0030 §1–§8 with A1; ADR-0044 §1–§5; ADR-0033 §2, §5, A6; ADR-0031 §1; ADR-0013 §2; ADR-0028 §2; "
               "ADR-0039 §1, §2; ADR-0041 §1, §2; ADR-0034 A2 and ADR-0033 A8 (pending); ADR-0042 §6 (Proposed); "
               "mechanism/GAPS-AND-ASSUMPTIONS.md G19, I33, I44; ToO rev 13 §3.1, §3.3; G7 §1.1; G9 §2.2, §2.5, §2.7, "
               "§7 items 67, 80, 84; "
               "floor/genesis-floor.cedar, genesis.cedarschema, genesis-values.json; policies/bundle.rego, "
               "tool_invocation.rego, actuate.rego, tool_schema.rego, data.json; mechanism/crates/topak-core/src/admit.rs, "
               "lift.rs; topak-floor/src/lib.rs; topak-bundle/src/lib.rs; scripts/build-bundle.sh")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---- the formula banner
    bh = 128
    c.rect(X0, y, X1 - X0, bh, "teal", tint=True, sw=2.2)
    c.text(X0 + 30, y + 64, "admit  ⟺  floor_permit  ∧  ¬bundle_deny", 40, "teal", bold=True)
    c.text(X0 + 30, y + 100, "evaluated by the mechanism over **one frozen input** (ADR-0030 §1, §4); fail-closed on "
           "both sides; a floor deny short-circuits", 16, "muted")
    px = X1 - 30
    for key, extra, lab in [("accepted", "C1", "ADR-0044"), ("accepted", "Batch 24", "ADR-0030 A1"),
                            ("accepted", "C1", "ADR-0030")][::1]:
        w = c.status(px, y + 48, key, extra, size=13, anchor="end")
        px -= w + 8
        c.text(px, y + 64, lab, 15, "ink", anchor="end", bold=True)
        px -= text_width(lab, 15, True) + 26
    y += bh + 56

    # ---- columns of the flow
    iw, gap = 430, 92
    fw, bw_, aw = 1080, 900, 0
    fx = X0 + iw + gap
    bx = fx + fw + gap
    ax = bx + bw_ + gap
    aw = X1 - ax
    top = y

    # input
    ih = c.card(X0, top + 30, iw, "One frozen input (the lift, step 4)", [
        "Principal (the seat), action, resource, context and the **complete entity slice**, in schema S's shape, "
        "plus the bundle's view built from the same facts (`FrozenInput`, `lift.rs`).",
        "Resolved **once**. Floor and bundle read the same facts; the bundle may not re-fetch anything about the "
        "request. Its own shipped `data` is not a re-fetch (ADR-0030 §4 R1).",
        "Written only by the typed lift and the issued rules: **no bundle has a write path** to any value the floor "
        "reads (§3).",
        "Context: epoch, fence, rules epoch, round, round role, lease fields; `observerLive`, `breakGlass` for Run; "
        "`erasureQuorum` for `Erase`.",
        "Its digest is recorded in the admit.",
    ], accent="teal", size=14)

    # floor region
    pad = 24
    fy = top + 30
    fhd = c.card(fx + pad, fy, fw - 2 * pad, "Floor tier · Cedar, linked · the only tier that can permit", [
        "**Obligation** (§2): an evaluator with a mechanized semantics; an implementation checked against it; a "
        "**decidable** comparison of two policy sets over a declared schema (implies, equivalent, always-allows, "
        "always-denies, never-errors); resident and linked; minimal. Cedar meets it; the reference links "
        "`cedar-policy` 4.13, the Rust engine, the shorter chain to the Lean model (§3).",
        "**A library, not a service**: no process, no socket, no fetch. Text, schema S and values file compiled in **by "
        "path**; the replica refuses to start unless their bytes match the gated digests (ADR-0033 §2).",
        "**Schema S enforced on every request**: a non-conforming input is a deny. S changes only with a mechanism "
        "release (§4).",
        "**Any evaluation error is a deny**: Cedar skips a policy that errors, so a skipped `forbid` would let a "
        "permit through.",
        "**A deny names its reason**: the forbids that fired, or `FloorNoPermit` when none did (finding 10).",
        "Evaluation: any satisfied `forbid` denies; else any satisfied `permit` allows; else deny.",
    ], accent="blue", size=14, status="accepted", status_extra="C1 · ADR-0030")
    ty = fy + fhd + 22
    c.text(fx + pad, ty + 18, "The genesis floor, all 17 policies", 18, "blue", bold=True)
    c.status(fx + pad + 330, ty, "draft", "gated 2026.10.01, checked proofs")
    ty += 36
    tw = fw - 2 * pad
    cols = [("`@id`", tw * 0.25, {"mono": True}), ("Effect", tw * 0.08), ("Action", tw * 0.16),
            ("Holds when", tw * 0.35), ("Record", tw * 0.16)]
    th = c.table(fx + pad, ty, cols, FLOOR_ROWS, size=13, accent="blue")
    ty += th + 14
    ty += c.para(fx + pad, ty, tw, "Not in the floor, and why (file header): epoch fencing and the round bound are the "
                 "mechanism's; the rules floor bounds issuances, not admits (§7); `Invoke` hermeticity is an obligation on "
                 "each allowlist entry. Values file (ADR-0039 §1): `T_obs`, `K`, `T_persona`, the unset θ, **every number a "
                 "placeholder**.", 13.5, "muted") + 10
    f_bot = ty + 12

    # bundle region
    by = top + 30
    bhd = c.card(bx + pad, by, bw_ - 2 * pad, "Bundle tier · OPA/Rego sidecar, WASM fallback · can only refuse", [
        "**Obligation** (§2): signed; evaluated per request over syntactically lifted input; the three ADR-0007 gates. "
        "Any per-request engine discharges it, because the mechanism does the composition.",
        "Consulted **only after a floor permit**, and asked only whether to refuse: the mechanism reads "
        "`data.topak.bundle.allow`, and `allow if not refused`.",
        "**Counts only from the revision the lease names** (ADR-0031 §1 `bundle`); a renewal keeps the bundle.",
        "**Loads only under a signature** over its content revision that verifies under a key in the issued rules' "
        "`bundle_keys` (ADR-0044 §1–§3); implemented at the reference by ADR-0033 A6 (Batch 23). A sidecar's answer counts "
        "only from a verified revision; a grant naming an unverified one is refused.",
        "Today the key is a dev key with custody (1, 0); signing at promotion is a script step, since no promotion "
        "pipeline exists (G9 item 67).",
    ], accent="amber", size=14, status="accepted", status_extra="C1 · ADR-0044")
    sy = by + bhd + 22
    c.text(bx + pad, sy + 18, "Engine fallback, bound to the lease (ADR-0030 §1, folded from ADR-0033 §5)", 17,
           "amber", bold=True)
    sy += 34
    btw = bw_ - 2 * pad
    sy += c.table(bx + pad, sy, [("The sidecar…", btw * 0.55), ("Result", btw * 0.45)], [
        ["returns `true` from the lease's revision", "**Allow**"],
        {"cells": ["returns anything else from the lease's revision", "**Refuse. Authoritative**: no fallback"],
         "accent": "red"},
        ["is unreachable, errors, times out, or serves another revision",
         "The local WASM engine decides **iff** it holds the lease's revision"],
        {"cells": ["— and the local engine holds no such revision", "Refuse: the bundle \"cannot be reached\""],
         "accent": "red"},
    ], size=13.5, accent="amber") + 12
    sy += c.para(bx + pad, sy, btw, "Without the binding, a sidecar outage would lift every narrowing pushed since the "
                 "local copy was built. Every admit records which engine decided. Checked by `fallback.rs`.", 13.5,
                 "muted") + 22
    c.text(bx + pad, sy + 18, "The bundle as built: `policies/`", 17, "amber", bold=True)
    c.status(bx + pad + 290, sy, "draft", "placeholder, not promoted")
    sy += 36
    sy += c.table(bx + pad, sy, [("File", btw * 0.28, {"mono": True}), ("What it refuses", btw * 0.72)], [
        ["bundle.rego", "The entrypoint: `default allow := false`; `allow if not refused`; composes the two modules "
                        "below"],
        ["tool_invocation.rego", "Build `Invoke` whose inputs do not match the tool's declared schema"],
        ["actuate.rego", "Run `Actuate` whose inputs do not match, or whose tool's entry declares **no effect "
                         "channel**. The channel is declared here, not interpreted: fidelity is **owned** by the tool "
                         "host's Wasm runtime under ADR-0034 A2 and **built** for Wasm-hosted tools by ADR-0033 A8 "
                         "(both pending); a native tool's is G19. The node's config declares it again, unchecked "
                         "against this (G9 item 84)"],
        ["tool_schema.rego", "Decides nothing alone: the flat-object schema check both domains share"],
        ["data.json", "Tool schemas keyed `name@digest` (`tlc@d1`, `search@d3`) and `search@d3`'s declared channel; "
                      "bundle data, not a re-fetch"],
    ], size=13.5, accent="amber") + 12
    sy += c.para(bx + pad, sy, btw, "Revision `be46c574dfeeed16…`: SHA-256 over the sorted (path, bytes) of every "
                 "non-test `.rego` and `data.json`; built to OPA WASM by `build-bundle.sh` and signed into "
                 "`<revision>.sig` (ADR-0033 A6).", 13.5, "muted") + 22
    c.text(bx + pad, sy + 18, "Degeneracy on ADR-0044 (§5)", 17, "amber", bold=True)
    sy += 34
    sy += c.table(bx + pad, sy, [("ID", btw * 0.13, {"bold": True}), ("Axis", btw * 0.24),
                                 ("Theorems voided", btw * 0.2), ("Declared consequence", btw * 0.43)], [
        ["D-0044-1", "Bundle signing → off (empty key set, unsigned load)", "ADR-0030 §2's \"Signed\"",
         "A swapped tarball with a matching manifest is trusted. The reference's position before ADR-0044, and **no "
         "longer since 2026.10.01** (ADR-0033 A6): with an empty key set **nothing loads**, which is §1, not this row"],
    ], size=13.5, accent="amber") + 10
    b_bot = sy + 12

    reg_bot = max(f_bot, b_bot)
    c.region(fx, top, fw, reg_bot - top, "Floor tier · in the verified object (B4)", "blue", size=15)
    c.region(bx, top, bw_, reg_bot - top, "Bundle tier · a versioned parameter (B4)", "amber", size=15)

    # admit sink
    ah = c.card(ax, top + 30, aw, "ADMIT", [
        "Only on a floor permit **and** an affirmative `true` from the lease's revision.",
        "Recorded with the floor reasons, the bundle revision and the deciding engine; then ordered (D1 step 7).",
    ], accent="green", size=14, tsize=22)
    # arrows along the flow
    fy_a = top + 92
    c.arrow([(X0 + iw, fy_a), (fx + pad, fy_a)], "teal", sw=2.6, label="same input", lpos=0.5, loff=(0, -18))
    c.arrow([(fx + fw - pad, fy_a), (bx + pad, fy_a)], "blue", sw=2.6, label="permit, no error", lpos=0.5,
            loff=(0, -18))
    c.arrow([(bx + bw_ - pad, fy_a), (ax, fy_a)], "green", sw=2.6, label="`true`", lpos=0.5, loff=(0, -18))

    # refusal bar
    ry = reg_bot + 80
    rh = c.card(fx, ry, X1 - fx, "REFUSE · fail-closed on both sides · never ordered, always recorded (ADR-0020)", [
        "**From the floor**, and the bundle is never consulted: `Floor([forbids that fired])` · `FloorNoPermit` (outside "
        "every envelope) · `FloorError` (any evaluation error, or input outside schema S).",
        "**From the bundle**: `Bundle(reason)` for a deny, an error, undefined, an absent bundle, an unreachable "
        "bundle, or a revision other than the lease's. **A bundle is never asked whether to grant.**",
    ], accent="red", size=14.5, tsize=19)
    c.arrow([(fx + fw / 2, reg_bot), (fx + fw / 2, ry)], "red", dash="7 5", sw=2.2,
            label="deny · no permit · error: short-circuit", lpos=0.5)
    c.arrow([(bx + bw_ / 2, reg_bot), (bx + bw_ / 2, ry)], "red", dash="7 5", sw=2.2,
            label="anything but `true`", lpos=0.5)
    # input column filler: what the lift does not do
    c.card(X0, top + 30 + ih + 40, iw, "Epoch fencing stays ahead of the floor", [
        "The floor never decides whether an epoch is current (§4); the mechanism checks of D1 step 3 run first.",
        "The composition is **one** decision: the floor and bundle are not re-run at apply; their verdict is recorded "
        "with the input's digest (ADR-0033 §4).",
    ], accent="teal", size=14, tint=False)

    # ---- truth table and consequences
    y = ry + rh + 70
    lw = 1500
    c.text(X0, y + 21, "The whole composition, as a truth table (`compose`, `floor_gate` in admit.rs)", 21, "ink",
           bold=True)
    y2 = y + 40
    tcols = [("Floor engine returns", lw * 0.22), ("Bundle consulted?", lw * 0.12), ("Bundle returns", lw * 0.30),
             ("Decision", lw * 0.12), ("Reason recorded", lw * 0.24)]
    trows = [
        {"group": "Floor permits: the bundle decides whether to refuse", "accent": "blue"},
        {"cells": ["Allow, no errors", "yes", "`true`, from the lease's revision (sidecar, or WASM holding it)",
                   "[[green|ADMIT]]", "permitting policy ids, engine, revision"], "accent": "green"},
        ["Allow, no errors", "yes", "`false`: some refusal fired", "[[red|refuse]]", "`Bundle(reason)`"],
        ["Allow, no errors", "yes", "an evaluation error", "[[red|refuse]]", "`Bundle(reason)`"],
        ["Allow, no errors", "yes", "undefined", "[[red|refuse]]", "`Bundle(reason)`"],
        ["Allow, no errors", "yes", "absent: no verified revision is held", "[[red|refuse]]", "`Bundle(reason)`"],
        ["Allow, no errors", "yes", "unreachable, and the local engine lacks the lease's revision", "[[red|refuse]]",
         "`Bundle(reason)`"],
        {"group": "Floor does not permit: short-circuit", "accent": "red"},
        ["Allow **with** an error diagnostic", "no", "—", "[[red|deny]]", "`FloorError(diagnostics)`"],
        ["Input fails validation against S", "no", "—", "[[red|deny]]", "`FloorError(diagnostics)`"],
        ["Deny, forbids fired", "no", "—", "[[red|deny]]", "`Floor([ids])`"],
        ["Deny, no permit matched", "no", "—", "[[red|deny]]", "`FloorNoPermit`"],
    ]
    th2 = c.table(X0, y2, tcols, trows, size=13.5, accent="grey")
    # degeneracy table under it
    y3 = y2 + th2 + 40
    c.text(X0, y3 + 21, "Declared axis: floor verification (ADR-0030 §8)", 21, "ink", bold=True)
    y3 += 40
    dcols = [("Record", lw * 0.12, {"bold": True}), ("Rule", lw * 0.24), ("Premise falsified", lw * 0.18),
             ("Sacrificed", lw * 0.26), ("Gained", lw * 0.20)]
    th3 = c.table(X0, y3, dcols, [
        {"cells": ["A-0030", "Floor on a verified evaluator (§2); monotone composition (§1)", "—", "—", "—"],
         "accent": "blue"},
        ["D-0030-2", "Routing verdicts unchecked: a `holds` from the solver is taken on trust",
         "A routing verdict is checked", "§5's classification as a **checked** result; it becomes the solver's "
         "assertion", "The gate run as it stood before 2026.10.01; a run without the checker"],
        ["D-0030-1", "Floor in Rego, with tests over a bounded schema and `RulesFloorNV`-style witnesses",
         "The floor's evaluator is faithful to a mechanized semantics", "Floor non-vacuity, never-errors and revision "
         "classification as **proven** properties; they become **measured**",
         "One engine and one language, where the deployment already runs OPA"],
    ], size=13.5, accent="grey")
    y3 += th3 + 12
    c.para(X0, y3, lw, "**bundle ⊑ floor survives D-0030-1**: composition is a mechanism constant and does not depend "
           "on the floor's language. The reference declares neither degeneracy since 2026.10.01 (ADR-0030 A1, Batch 24).",
           13.5, "muted")

    rx = X0 + lw + 60
    rw = X1 - rx
    cy = y
    h = c.card(rx, cy, rw, "What composition buys (§1; ToO §3.1)", [
        "**bundle ⊑ floor for every bundle, at every age**, of the composed decision. It is no longer something a "
        "bundle can fail; a bundle whose text permits more than the floor is **inert, not inadmissible**. Refinement is "
        "still discharged at promotion, now by construction.",
        "**Containment is checked against the floor**, and no bundle can weaken it.",
        "**Stale bundles are monotone-safe**, with no refinement premise: local enforcement under partition survives, "
        "sound by construction (the same shape as the lease argument).",
        "**No cross-language check.** Deciding refinement with an SMT solver over Rego needed a mechanized Rego "
        "semantics that does not exist; composition removes the need.",
        "Floor tightening never invalidates a promoted bundle.",
    ], accent="green", size=14)
    cy += h + 24
    h = c.card(rx, cy, rw, "What is given up", [
        "**A bundle cannot establish that something is allowed**: `always_allows` over the composed decision is not "
        "provable.",
        "Over-denial by a bundle is a modeled, attributed local event (`deny=all` is F2, ADR-0028).",
        "**A bundle can narrow a floor exception, including break-glass** (§5): a bad bundle can disable break-glass, "
        "a liveness cost, never a widening.",
        "Two languages and two engines; the floor must fit PARC: no aggregation, no regex, no computed data.",
    ], accent="red", size=14, tint=False, dash="6 4")
    cy += h + 24
    c.card(rx, cy, rw, "Nothing translates (§6)", [
        "Neither Rego → Cedar nor Cedar → Rego is in the archetype. A transpiler is a **Build artifact whose output "
        "becomes the enforced floor**, and Build is where the Byzantine threat lives: a silent mistranslation means "
        "the proven text is not the enforced text.",
        "Cedar's analyses compare Cedar with Cedar. A deployment that keeps a Rego floor declares **D-0030-1**.",
    ], accent="blue", size=14)

    ly = c.ymax + 44
    c.legend(c.x0, ly, [
        ("box", "blue", "floor tier, verified object"), ("box", "amber", "bundle tier, parameter"),
        ("box", "teal", "the mechanism's input"), ("box", "green", "admit"), ("box", "red", "refusal"),
        ("arrow", "blue", "the admit path"), ("arrow", "red", "refusal: not ordered", "7 5"),
    ])
    return c
