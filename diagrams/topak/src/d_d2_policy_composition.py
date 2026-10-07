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
    ["B10-only-thinkers-author", "forbid", "`Draft` `Invoke` `Submit` `Actuate`", "The seat kind is not `thinker`, "
     "and, for `Actuate`, not `emergency`", "ADR-0037 §4; ADR-0041 A2"],
    {"group": "Run envelopes (ADR-0040 §1, stated as ADR-0041 §1) and their carve-outs", "accent": "green"},
    ["R1-actuate-allowlisted", "permit", "`Actuate`", "Run seat; in the alphabet; tool on the allowlist. An "
     "`emergency` seat's allowlist is its envelope", "ADR-0041 §1; ADR-0052 §2"],
    ["R2-report-own-topic", "permit", "`Report`", "Run; in the alphabet; own topic of this epoch and round; not sealed",
     "ADR-0041 §1"],
    ["R4-consult-pinned", "permit", "`Consult`", "Run; in the alphabet; object in the pinned Run root", "ADR-0041 §1"],
    ["R3-observer-live", "forbid", "`Actuate` `Report`", "A `thinker` seat without `observerLive` (the lift's `live(o)`)",
     "ADR-0039 §2, ADR-0041 §2"],
    ["R5-no-read-then-send", "forbid", "`Actuate`", "Outward tool; `clearSet` holds `untrusted`; `restricted` in "
     "`clearSet` or `inputLabels`", "ADR-0047 F1; ADR-0041 A1"],
    ["R6-no-steered-destination", "forbid", "`Actuate`", "Outward tool; `clearSet` holds `untrusted`; a destination "
     "input is a literal", "ADR-0047 F2; ADR-0041 A1"],
    ["R7-no-replayed-destination", "forbid", "`Actuate`", "Outward tool; a destination handle's label holds `untrusted`",
     "ADR-0047 F3; ADR-0041 A1"],
    {"group": "Floor exceptions (ADR-0013 §2, A1): count 1, bounded by rules-floor R6", "accent": "violet"},
    {"cells": ["X1-break-glass", "[[grey|removed]]", "`Actuate`", "Retired: break-glass is an emergency seating, "
               "admitted by `R1` (not counted)", "ADR-0041 A2; ADR-0052"], "accent": "grey"},
    ["X2-erasure", "permit", "`Erase`", "An erasure quorum on the issued roster: **FALSE at genesis**, which issues no "
     "roster", "ADR-0006, ADR-0013"],
    {"group": "The forensic floor (ADR-0028)", "accent": "brown"},
    ["F-forensic-classes", "forbid", "`Erase`", "The record's class is one of F1–F6", "ADR-0028 §2"],
    {"group": "Control entries: an `operator` seat (ADR-0050 §4, provisional; ADR-0041 A3)", "accent": "blue"},
    ["C1-regrant-successor", "permit", "`Regrant`", "Operator; target in its domain, seated, not live; same binding, "
     "next round; alphabet the last one's or narrower", "ADR-0050 §2, §4"],
    ["C2-renew", "permit", "`Renew`", "Operator; target live, in its domain", "ADR-0050 §4"],
    ["C3-attest-gates", "permit", "`AttestGates`", "Operator, in Build", "ADR-0050 §4"],
    ["C4-deny", "permit", "`EndRound` `Revoke` `FenceEpoch`", "Operator; Persona in force; a live lease or a fresh "
     "sign-on assertion", "ADR-0050 §4 (R1)"],
    ["C5-add-needs-lease-and-peer", "forbid", "`Regrant` `Renew` `AttestGates`", "No live lease, or no live peer in the "
     "domain", "ADR-0050 §4, §6"],
    ["C6-no-self", "forbid", "`Regrant` `Renew`", "The target is the operator itself", "ADR-0050 §4"],
    ["C7-fence-needs-lease", "forbid", "`FenceEpoch`", "No live lease", "ADR-0050 §4 (R5)"],
    ["C8-task-label-in-bounds", "forbid", "`Regrant`", "The task is unlabelled, or labelled outside its seating's "
     "bounds", "ADR-0050 §5"],
    ["C9-stop-in-own-domain", "forbid", "`EndRound` `Revoke`", "The target is in another domain", "ADR-0050 §4 (R5)"],
]


def build():
    c = Canvas(ID, "Policy composition: `admit ⟺ floor_permit ∧ ¬bundle_deny`",
               "Two tiers decide every admit over one frozen input. The floor, a verified evaluator linked into the "
               "mechanism, is the only tier that can permit. The bundle, per-request and signed, is asked only whether "
               "to refuse, and only after the floor permits, and only from a bundle that loaded signed and "
               "well-formed. Composition is a mechanism constant, so `bundle ⊑ floor` holds for every bundle at every "
               "age; what it cannot bound, delivery over labels, the floor bounds with a minimum no bundle can loosen. "
               "An operator's control request is decided by the floor alone.",
               W, "ADR-0030 §1–§8 with A1, A2, A3; ADR-0044 §1–§5; ADR-0033 §2, §5, A6, A8–A12, A15; ADR-0031 §1; "
               "ADR-0013 §2, A1; ADR-0028 §2; ADR-0039 §1, §2; ADR-0041 §1–§5, A1–A3; ADR-0034 A2; ADR-0042 §6; "
               "ADR-0043 A1; ADR-0047 §1, §2, §4, §7, §8; ADR-0049 §1, §3–§6; ADR-0025 A2; ADR-0050 §2, §4–§6; "
               "ADR-0052 §1, §2; mechanism/GAPS-AND-ASSUMPTIONS.md G19, I33, I44, I46; ToO rev 14 §2.10, §3.1, §3.3, "
               "§7.10; G10 §2.2, §2.5, §2.7, §3 (results 5, 6), §7 items 67, 84, 87, 92, 93, 94, 98; "
               "floor/proposed/emergency-floor.cedar, emergency.cedarschema, emergency-tests.json; "
               "floor/genesis-values.json; policies/bundle.rego, tool_invocation.rego, actuate.rego, tool_schema.rego, "
               "data.json; mechanism/crates/topak-core/src/admit.rs, lift.rs (`FrozenInput`, `bundle_input`, "
               "`lift_control`), control.rs, rules.rs; topak-floor/src/lib.rs; topak-bundle/src/lib.rs, allowlist.rs; "
               "topak-node/src/lib.rs; scripts/build-bundle.sh; GAPS G11; "
               "derived/topak-format-and-schema-inventory-2026.10.03.md §2.1, §3.1, §3.2, findings 11, 23; ADR-0053 (B36) "
               "§1, §2, R2; mechanism/lean/Topak/Admit.lean, FloorRefinement.lean and mechanism/lean/Admit-results-2026.10.06.txt; "
               "mechanism/lean/README.md (mutation check)")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---- the formula banner
    bh = 128
    c.rect(X0, y, X1 - X0, bh, "teal", tint=True, sw=2.2)
    c.text(X0 + 30, y + 64, "admit  ⟺  floor_permit  ∧  ¬bundle_deny", 40, "teal", bold=True)
    c.text(X0 + 30, y + 100, "evaluated by the mechanism over **one frozen input** (ADR-0030 §1, §4); fail-closed on "
           "both sides; a floor deny short-circuits", 16, "muted")
    px = X1 - 30
    for key, extra, lab in [("accepted", "C1", "ADR-0044"), ("accepted", "Batch 34", "ADR-0030 A2"),
                            ("accepted", "Batch 24", "ADR-0030 A1"), ("accepted", "C1", "ADR-0030")][::1]:
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
        "Context: epoch, fence, rules epoch, round, round role, lease fields; for Run `observerLive` and the label "
        "facts `clearSet`, `inputLabels`, `destLiteral`, `destLabels`, with `Tool.outward` (ADR-0030 A2); for a "
        "control action `ControlCtx`, thirteen facts the mechanism holds (ADR-0050 §4); `erasureQuorum` for `Erase`.",
        "The label facts are computed from the record and the granted revision's allowlist entry: **the lift's "
        "work, not a re-fetch**, and both tiers see the same values (ADR-0030 A2).",
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
        "path**; the replica refuses to start unless their bytes match the gated digests (ADR-0033 §2): since "
        "`9c57221` the `emergency` stage's, `15c941b9…` and `d3c8145c…` (A12).",
        "**Schema S enforced on every request**: a non-conforming input is a deny. S changes only with a mechanism "
        "release (§4).",
        "**Any evaluation error is a deny**: Cedar skips a policy that errors, so a skipped `forbid` would let a "
        "permit through.",
        "**A deny names its reason**: the forbids that fired, or `FloorNoPermit` when none did (finding 10).",
        "Evaluation: any satisfied `forbid` denies; else any satisfied `permit` allows; else deny.",
    ], accent="blue", size=14, status="accepted", status_extra="C1 · ADR-0030")
    ty = fy + fhd + 22
    c.text(fx + pad, ty + 18, "The floor in force, all 28 policies (`emergency` stage)", 18, "blue", bold=True)
    c.status(fx + fw - pad, ty, "genprov", "ADR-0030 A3 · gated 2026.10.04", anchor="end")
    ty += 36
    tw = fw - 2 * pad
    cols = [("`@id`", tw * 0.25, {"mono": True}), ("Effect", tw * 0.08), ("Action", tw * 0.16),
            ("Holds when", tw * 0.35), ("Record", tw * 0.16)]
    th = c.table(fx + pad, ty, cols, FLOOR_ROWS, size=13, accent="blue")
    ty += th + 14
    ty += c.para(fx + pad, ty, tw, "Built from the genesis draft (17 policies) in three gated stages, `labels`, "
                 "`control`, `emergency` (diagram B8). **Genesis-provisional**: gated, pinned and enforced, and ratified "
                 "only when the bootstrap reviewer establishes that it is fit, with no test (ADR-0029 A4; G10 item 87). "
                 "Not in the floor, and why (file header): epoch fencing and the round bound are the mechanism's; the "
                 "rules floor bounds issuances, not admits (§7); `Invoke` hermeticity is an obligation on each allowlist "
                 "entry; F4 to F6 are load checks (right). Values file (ADR-0039 §1): `T_obs`, `K`, `T_persona`, the "
                 "unset θ, **every number a placeholder**.", 13.5, "muted") + 10
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
        "**Loads only if its allowlist is well-formed**: W1 to W10 (ADR-0049 §6), checked by the mechanism after "
        "the signature and before any decision counts. A mechanism constant, as composition is; a bundle cannot "
        "waive them (ADR-0030 A2). Table below.",
        "Today the key is a throwaway dev key with custody (1, 0); signing at promotion is a script step, since no "
        "promotion pipeline exists (item 67, open).",
        "**Not consulted for a control request**: at the reference an operator's request is decided by the floor's "
        "`C1` to `C9` alone (ADR-0033 A11).",
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
        ["tool_invocation.rego", "Build `Invoke` whose inputs do not match the tool's entry"],
        ["actuate.rego", "Run `Actuate` whose inputs do not match, or whose entry declares **no effect channel**. "
                         "The mechanism refuses such a bundle at load (W4); the check is repeated because a sidecar "
                         "evaluates over data the mechanism did not load. `kind` is declared, not interpreted; "
                         "`target` is where the tool host binds a Wasm tool's one connection (ADR-0034 A2; ADR-0033 "
                         "A8, A9), and the entry is its only declaration (G10 item 84, closed); a native tool's is G19"],
        ["tool_schema.rego", "Decides nothing alone. The check both domains share, on ADR-0049's entry: each input's "
                             "`type` and `required`, no unknown input, the entry's `domain` matching the action; an "
                             "input given as a **handle** only where its `accepts` admits the label the mechanism "
                             "supplied in `input.handles` (ADR-0049 §3)"],
        ["data.json", "`topak.tools`: entries in ADR-0049's form, `tlc@d1` (Build) and `search@d3` (Run: result "
                      "label `untrusted`, channel `https` to `search.internal:443`). `topak.labels`: the vocabulary, "
                      "the delivery table for `thinker` and `observer`, the root's label (ADR-0047 §1, §2)"],
    ], size=13.5, accent="amber") + 12
    sy += c.para(bx + pad, sy, btw, "Revision `3e98ed176ba6c339…` since `c15026d` (ADR-0033 A10): SHA-256 over the "
                 "sorted (path, bytes) of every non-test `.rego` and `data.json`, **the source, not the compiled "
                 "module**. `build-bundle.sh` compiles it to `policy.wasm` in the `openpolicyagent/opa` image at its "
                 "floating `latest` tag, so one revision can carry a different module (inventory finding 11), and "
                 "signs the revision into `<revision>.sig` (ADR-0033 A6). 38 Rego tests. **Two comments still call "
                 "ADR-0049 Proposed**, and a comment is part of the revision, so correcting them is a new bundle (G10 "
                 "item 98; ADR-0033 A15).", 13.5, "muted") + 22
    c.text(bx + pad, sy + 18, "Degeneracy on ADR-0044 (§5)", 17, "amber", bold=True)
    sy += 34
    sy += c.table(bx + pad, sy, [("ID", btw * 0.13, {"bold": True}), ("Axis", btw * 0.24),
                                 ("Theorems voided", btw * 0.2), ("Declared consequence", btw * 0.43)], [
        ["D-0044-1", "Bundle signing → off (empty key set, unsigned load)", "ADR-0030 §2's \"Signed\"",
         "A swapped tarball with a matching manifest is trusted. The reference's position before ADR-0044, and **no "
         "longer since 2026.10.01** (ADR-0033 A6): with an empty key set **nothing loads**, which is §1, not this row"],
    ], size=13.5, accent="amber") + 22
    c.text(bx + pad, sy + 18, "A bundle loads only if its allowlist is well-formed (ADR-0049 §6)", 17, "amber", bold=True)
    sy += 34
    wx, cw3 = bx + pad, btw
    sy += c.table(wx, sy, [("", cw3 * 0.1, {"bold": True}), ("The bundle is refused when", cw3 * 0.66),
                             ("From", cw3 * 0.24)], [
        ["W1", "an entry's key is not its `name` and `digest`, or its `domain` is missing", "§1"],
        ["W2", "an input lacks `type` or `required`, or the type is not one of the three", "§3"],
        ["W3", "`purpose` is empty, an input has no `note`, or either is over the size bound", "ADR-0048 §1"],
        ["W4", "a Run entry has no `channel`, or a `channel` lacks `kind` or `target`", "ADR-0040 §3; I33"],
        ["W5", "a Build entry has a `channel`", "§1"],
        ["W6", "a Run entry has no `result.label`, or a label name is outside the bundle's vocabulary",
         "ADR-0047 §1, F6"],
        ["W7", "an outward entry's `result.label` lacks `untrusted`", "ADR-0047 F4"],
        ["W8", "`result.releases` holds a reserved name and the issued rules do not name the entry", "ADR-0047 F5"],
        ["W9", "an outward entry takes inputs and marks none a `destination`, without saying it has none",
         "ADR-0047 F6"],
        ["W10", "an entry or input carries a field the record does not define, or a Build entry carries the "
                "labels part (restated at R4)", "§1, §3"],
    ], size=13, accent="amber") + 10
    sy += c.para(wx, sy, cw3, "Checked by the mechanism after the signature and before any decision counts; a "
                  "mechanism constant no bundle can waive (ADR-0030 A2). **\"Outward\" is derived, never declared**: "
                  "W7 and W9 read the targets the issued rules list as inside the deployment, and W8 the entries they "
                  "name as allowed to release a reserved name (ADR-0025 A2; ADR-0030 A2). The rules' well-formedness reads both, "
                  "and the rules floor bounds neither (ADR-0033 A15). **Read once**, from the genesis rules, when "
                  "bundles load: an issuance that changes a list does not re-check a bundle already loaded (I46; G10 "
                  "item 94).", 13.5, "muted")
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

    # ---- since Batch 34: labels, control requests, load checks
    y = max(ry + rh, c.ymax) + 70
    c.text(X0, y + 21, "What the floor bounds that composition cannot, and what reaches the floor alone (Batch 34)", 21,
           "ink", bold=True)
    y += 44
    g3 = 36
    cw1 = (X1 - X0 - g3) / 2
    cw2 = cw1
    lab = c.card(X0, y, cw1, "A minimum over labels that no bundle can loosen", [
        "**Run's ingress is four items, each with a label** (ADR-0043 A1): the task, consulted content, tool results "
        "and the tool list. An item is delivered **clear with its label, or as a handle** with no bytes, by a "
        "delivery table in bundle data, per seat kind (ADR-0047 §2).",
        "**Delivery is not bounded by** `bundle ⊑ floor`, which is decided over action variants. A promoted bundle "
        "may move every label to clear (ADR-0047 §8).",
        "**So the floor carries a minimum** (ADR-0047 §7; ADR-0041 A1): `R5` to `R7`, forbids over the label facts "
        "the lift supplies. They are monotone in `clearSet`: **delivering more in the clear buys a narrower round** "
        "(G10 §2.5). Relaxing them is an issuance with the floor's gates.",
        "A bundle may add rules over `clearSet` and `inputLabels`, and can only narrow (ADR-0041 §5).",
        "**At the reference**: the label facts are the deciding replica's and `apply` re-checks only `clearSet` "
        "(G10 item 93); a person on an `emergency` seat is given handles unless the bundle says otherwise, since "
        "the load check asks for no delivery row for that kind (G10 §3, result 6; item 92).",
    ], accent="teal", size=14, status="accepted", status_extra="ADR-0047 · ADR-0041 A1")
    ctl = c.card(X0 + cw1 + g3, y, cw2, "An operator's request: the floor alone", [
        "**Six control actions** of an `operator` seat (ADR-0050 §4): `Regrant`, `Renew`, `AttestGates` add and need "
        "a live lease and a live peer; `EndRound`, `Revoke`, `FenceEpoch` deny and need no lease, except the fleet fence; a lapsed operator "
        "denies on a fresh sign-on assertion.",
        "**Signed** with the seat's key, with the fleet epoch and a counter. The deciding replica computes "
        "thirteen facts into `ControlCtx`; the operator supplies none (ADR-0033 A11).",
        "`C1` **to** `C9` **decide, and there is no bundle tier**: `admit ⟺ floor_permit` for these actions at the "
        "reference. Every replica verifies the signature, refuses a replayed counter, recomputes the facts and "
        "refuses the entry if they differ, and restates the envelope before applying (`control.rs`).",
        "**The envelope is stated twice**, in Cedar and in Rust, and only the tests hold them together (A11).",
        "**BOOTSTRAP**: the unsigned socket is kept and **seats, and does nothing else**; a first lease from a "
        "completed tally is not built (ADR-0050 §10; G10 item 88).",
    ], accent="blue", size=14, status="provisional", status_extra="ADR-0050")
    y = max(y + lab, y + ctl) + 70

    # ---- truth table and consequences
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
        {"group": "A control request from an `operator` seat (ADR-0050, provisional): no bundle tier at the reference "
                  "(ADR-0033 A11)", "accent": "blue"},
        {"cells": ["Allow, no errors (`C1` to `C4`, no control forbid)", "no", "—", "[[green|ADMIT]]",
                   "the request, its signature and the facts; every replica recomputes and restates"],
         "accent": "green"},
        ["Deny, a control forbid fired, or no permit, or an error", "no", "—", "[[red|deny]]",
         "`Floor([ids])` · `FloorNoPermit` · `FloorError`"],
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
        "**A bundle can narrow a floor exception** (§5) and the emergency seat's calls, which `R1` admits like any "
        "other: a bad bundle can disable an emergency seat's tools, a liveness cost, never a widening (ToO rev 14 §3.1).",
        "`bundle ⊑ floor` **says nothing about delivery**: it is decided over action variants. A promoted bundle may "
        "move every label to clear; only the floor's `R5` to `R7` bound that (ADR-0047 §8).",
        "Two languages and two engines; the floor must fit PARC: no aggregation, no regex, no computed data.",
    ], accent="red", size=14, tint=False, dash="6 4")
    cy += h + 24
    h = c.card(rx, cy, rw, "Nothing translates (§6)", [
        "Neither Rego → Cedar nor Cedar → Rego is in the archetype. A transpiler is a **Build artifact whose output "
        "becomes the enforced floor**, and Build is where the Byzantine threat lives: a silent mistranslation means "
        "the proven text is not the enforced text.",
        "Cedar's analyses compare Cedar with Cedar. A deployment that keeps a Rego floor declares **D-0030-1**.",
    ], accent="blue", size=14)
    cy += h + 24
    c.card(rx, cy, rw, "The truth table's first two groups, proved of the code (ADR-0053, B36)", [
        "`mechanism/lean/Topak/Admit.lean` transcribes `floor_gate` and `compose` from `admit.rs`, and the call site in "
        "`mechanism.rs`, and proves of the transcription: **`admit_iff`**, that the decision is "
        "`floor_permit ∧ ¬bundle_deny` at every floor and bundle outcome; that an admit carries exactly the floor's "
        "reasons and the bundle's engine and digest; that a floor error is a deny whatever the bundle said; that every "
        "floor deny names a reason, `FloorNoPermit` and never an empty `Floor([])`; and that the node's own gate check "
        "before the bundle call is `compose`.",
        "Of the transcription, read beside the Rust; on the Lean kernel (T-0045-37). Three mutated "
        "transcriptions (`M_OVERRIDE`, `M_ERR`, the empty-reason deny) each fail to build.",
        "**Since 2026.10.06 the whole decision refines the module** (ADR-0053 R2): `FloorRefinement.lean` transcribes "
        "the `topak-floor` wrapper, which makes any Cedar error diagnostic an `Error` whatever Cedar decided, and proves "
        "wrapper and `compose` together a `Decide` step of `FloorComposition`'s re-encoding, on Cedar's rule over the "
        "module's four policies as the engine premise (T-0045-3). Not a stage of T-0045-28's chain.",
        "**The control-request rows are not covered**: there `mechanism.rs` matches the floor's outcome directly, "
        "without `floor_gate` or `compose`, and a deny with no forbid fired is returned with its facts and an empty "
        "reason list rather than as `FloorNoPermit`.",
    ], accent="amber", status="accepted", status_extra="ADR-0053 · B36", size=14)

    # ---- schema S, drawn
    y = c.ymax + 60
    c.text(X0, y + 21, "Schema S, as the lift types it (`floor/proposed/emergency.cedarschema`, namespace `Topak`; "
           "`lift.rs`)", 21, "blue", bold=True)
    c.status(X1, y + 3, "genprov", "digest d3c8145c6af2d9a3", anchor="end")
    y += 42
    g = 36
    ew_, cw_ = 1130, 920
    aw_ = X1 - X0 - ew_ - cw_ - 2 * g
    mono = {"mono": True}
    h_e = c.table(X0, y, [("Entity", ew_ * 0.2, mono), ("Parents", ew_ * 0.17, mono),
                          ("Attributes (none optional)", ew_ * 0.63)], [
        ["Roster", "", "—"],
        ["Seat", "Roster", "`domain: String` (build | run), `kind: String` (thinker | observer | grant | operator | "
                           "emergency)"],
        ["CorpusRoot", "", "—"],
        ["CorpusObject", "CorpusRoot", "—"],
        ["Workspace", "", "—"],
        ["WorkspaceTarget", "Workspace", "—"],
        ["ToolSet", "", "—"],
        ["Tool", "ToolSet", "`digest: String`, `outward: Bool` (derived by the lift, never declared)"],
        ["Topic", "", "`owner: Seat`, `epoch: Long`, `round: Long`, `sealed: Bool`"],
        ["Artifact", "", "`author: Seat`"],
        ["Fleet", "", "— (what `FenceEpoch` acts on: every lease at the epoch)"],
        {"cells": ["ArchiveRecord", "", "`class: String` (F1..F6 | payload); **never produced** by the lift"],
         "accent": "red"},
    ], size=13.5, accent="blue")
    h_c = c.table(X0 + ew_ + g, y, [("Context record", cw_ * 0.18, mono), ("Fields", cw_ * 0.82)], [
        ["Lease", "`alphabet: Set<String>`, `rulesEpoch: Long`"],
        ["BuildCtx", "`lease`, `epoch`, `round`, `roundRole` (author | voter), `corpusRoot`, `workspace`, "
                     "`toolAllowlist`, `inputsInWorkspace: Bool`"],
        ["VoteCtx", "`lease`, `epoch`, `rulesEpoch`, `verdict` (grant | deny), `voteRulesEpoch`, `grantRoster`, "
                    "`vetoRoster`"],
        ["RunCtx", "`lease`, `epoch`, `round`, `runRoot`, `toolAllowlist`, `observerLive: Bool`, `clearSet`, "
                   "`inputLabels: Set<String>`, `destLiteral: Bool`, `destLabels: Set<String>`; no `breakGlass` "
                   "since the `emergency` stage"],
        ["ControlCtx", "`personaInForce`, `hasLease`, `peerLive`, `freshAssertion`, `targetSeated`, `targetLive`, "
                       "`sameBinding`, `nextRound`, `taskLabelled: Bool`; `lastAlphabet`, `newAlphabet`, `taskLabel`, "
                       "`taskLabelsAllowed: Set<String>`"],
        {"cells": ["EraseCtx", "`erasureQuorum: Bool` (FALSE at genesis); **never produced** by the lift"],
         "accent": "red"},
    ], size=13.5, accent="blue")
    h_a = c.table(X0 + ew_ + g + cw_ + g, y, [("Action (principal: `Seat`)", aw_ * 0.3, mono),
                                            ("Resource", aw_ * 0.34, mono), ("Context", aw_ * 0.36, mono)], [
        ["Read", "CorpusObject", "BuildCtx"], ["Draft", "WorkspaceTarget", "BuildCtx"],
        ["Invoke", "Tool", "BuildCtx"], ["Emit", "Topic", "BuildCtx"], ["Submit", "Artifact", "BuildCtx"],
        ["Vote", "Artifact", "VoteCtx"], ["Consult", "CorpusObject", "RunCtx"], ["Actuate", "Tool", "RunCtx"],
        ["Report", "Topic", "RunCtx"],
        ["Regrant", "Seat", "ControlCtx"], ["Renew", "Seat", "ControlCtx"], ["AttestGates", "Artifact", "ControlCtx"],
        ["EndRound", "Seat", "ControlCtx"], ["Revoke", "Seat", "ControlCtx"], ["FenceEpoch", "Fleet", "ControlCtx"],
        {"cells": ["Erase", "ArchiveRecord", "EraseCtx"], "accent": "red"},
    ], size=13.5, accent="blue")
    y += max(h_e, h_c, h_a) + 24
    w3s = (X1 - X0 - 2 * g) / 3
    sc = [
        ("What the lift always builds (`lift.rs`)", "teal", {}, [
            "Entities present in every request: `Roster::grant`, `Roster::veto`, the requesting `Seat` with its roster "
            "parents, `CorpusRoot::pinned` and `run-pinned`, the `Workspace` `ws-<seat>-e<epoch>-r<round>`, "
            "`ToolSet::build-allow` and `run-allow`; then the action's resource, with `Tool.outward` from the label "
            "facts, and the context in the shapes above. No `bg-tools` since the `emergency` stage.",
            "For a control request (`lift_control`): the two rosters, the operator's seat, the target seat, artifact "
            "or `Fleet`, and `ControlCtx` from the facts (51 entities in the stage's test slice, `emergency-tests.json`).",
            "`Erase`, `EraseCtx` and `ArchiveRecord` are typed, gated and **never produced**: no lift path exists and "
            "`Rules.erasure_roster` is never read (G11).",
        ]),
        ("Read by no policy", "red", {"tint": False, "dash": "6 4"}, [
            "`Lease.rulesEpoch`, `Tool.digest` and `VoteCtx.epoch` are typed and lifted and **no policy reads them**: "
            "`B6` reads `context.rulesEpoch`, and a tool's digest is in its entity id `name@digest` (inventory "
            "finding 23).",
            "`Report` takes `clearSet` and no entry reads it yet (ADR-0041 §4, A1).",
            "S is enforced on every request, so an attribute's absence is a deny even where no policy would read it.",
        ]),
        ("The bundle's input document (`bundle_input`, lift.rs; `policies/bundle.rego`)", "amber", {}, [
            "`{action, principal: {seat, domain}, resource: {object} | {target} | {tool, digest} | {topic} | "
            "{artifact[, evidence]}, inputs, handles: {input: <label>}, request: <the typed Action>, context: {epoch, "
            "round, roundRole, rulesEpoch, lease: <fence>}}`.",
            "The modules read only `input.action`, `input.resource.tool`, `input.resource.digest`, `input.inputs` and "
            "`input.handles`. A handle that names nothing in the round is refused before either tier (`lift.rs`). "
            "`violations` strings exist for a decision log nobody writes.",
        ]),
    ]
    hs = max(c.card(0, 0, w3s, t, b, accent=a, draw=False, size=14, **kw) for t, a, kw, b in sc)
    for i, (t, a, kw, b) in enumerate(sc):
        c.card(X0 + i * (w3s + g), y, w3s, t, b, accent=a, h=hs, size=14, **kw)
    y += hs

    ly = c.ymax + 44
    c.legend(c.x0, ly, [
        ("box", "blue", "floor tier, verified object"), ("box", "amber", "bundle tier, parameter"),
        ("box", "teal", "the mechanism's input"), ("box", "green", "admit"), ("box", "red", "refusal"),
        ("arrow", "blue", "the admit path"), ("arrow", "red", "refusal: not ordered", "7 5"),
    ])
    return c
