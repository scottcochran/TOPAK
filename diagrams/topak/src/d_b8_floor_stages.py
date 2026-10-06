"""B8 — The policy floor in force: three gated stages from the genesis draft."""
from lib import Canvas

ID, SLUG = "B8", "floor-stages"

W = 3400

P, F = "[[teal|permit]]", "[[red|forbid]]"

# Every policy of floor/proposed/emergency-floor.cedar, in file order, with the stage that put it there.
# (id, effect, actions, condition as written, from the record, stage)
POLICIES = [
    {"group": "Build envelopes: ADR-0022 §1 (six) · from the genesis draft", "accent": "blue"},
    ["`B1-read-corpus`", P, "`Read`", "`principal.domain == \"build\"` ∧ `context.lease.alphabet.contains(\"Read\")` ∧ "
     "`resource in context.corpusRoot`", "ADR-0022 §1", "genesis"],
    ["`B2-draft-workspace`", P, "`Draft`", "build ∧ `alphabet.contains(\"Draft\")` ∧ `resource in context.workspace`",
     "ADR-0022 §1", "genesis"],
    ["`B3-invoke-allowlisted`", P, "`Invoke`", "build ∧ `alphabet.contains(\"Invoke\")` ∧ `resource in "
     "context.toolAllowlist` ∧ `context.inputsInWorkspace`", "ADR-0022 §1, §3", "genesis"],
    ["`B4-emit-own-topic`", P, "`Emit`", "build ∧ `alphabet.contains(\"Emit\")` ∧ `resource.owner == principal` ∧ "
     "`resource.epoch == context.epoch` ∧ `resource.round == context.round` ∧ `!resource.sealed`", "ADR-0022 §1",
     "genesis"],
    ["`B5-submit-own-artifact`", P, "`Submit`", "build ∧ `alphabet.contains(\"Submit\")` ∧ `resource.author == "
     "principal`", "ADR-0022 §1", "genesis"],
    ["`B6-vote-seated`", P, "`Vote`", "build ∧ `alphabet.contains(\"Vote\")` ∧ `context.voteRulesEpoch == "
     "context.rulesEpoch` ∧ ((`principal in context.grantRoster` ∧ `principal.kind == \"grant\"`) ∨ (`principal in "
     "context.vetoRoster` ∧ `principal.kind == \"observer\"`))", "ADR-0022 §1; ADR-0037 §4", "genesis"],
    {"group": "Carve-outs on the Build envelopes (four) · B10 amended at the `emergency` stage", "accent": "red"},
    ["`B7-author-recused`", F, "`Vote`", "`resource.author == principal`", "ADR-0022 §7; ADR-0024 §6", "genesis"],
    ["`B8-grant-only-from-grant-seat`", F, "`Vote`", "`context.verdict == \"grant\"` ∧ `!(principal in "
     "context.grantRoster)`", "ADR-0024 §5", "genesis"],
    ["`B9-voters-do-not-author`", F, "`Draft` `Invoke` `Submit`", "`context.roundRole == \"voter\"`", "ADR-0022 §7",
     "genesis"],
    {"cells": ["`B10-only-thinkers-author`", F, "`Draft` `Invoke` `Submit` `Actuate`",
               "`principal.kind != \"thinker\"` ∧ `!(principal.kind == \"emergency\" && action == Actuate)`: an "
               "`emergency` seat, held by a person for one round, may `Actuate` and nothing else here",
               "ADR-0037 §4; ADR-0052 §1; ADR-0041 A2", "genesis, [[violet|amended: emergency]]"], "accent": "violet"},
    {"group": "Run envelopes: ADR-0040 §1, stated as ADR-0041 §1 (three) · from the genesis draft", "accent": "green"},
    ["`R1-actuate-allowlisted`", P, "`Actuate`", "`principal.domain == \"run\"` ∧ `alphabet.contains(\"Actuate\")` ∧ "
     "`resource in context.toolAllowlist`. Also admits an `emergency` seat, over the envelope computed at "
     "activation", "ADR-0040 §1; ADR-0041 §1; ADR-0052 §2", "genesis"],
    ["`R2-report-own-topic`", P, "`Report`", "run ∧ `alphabet.contains(\"Report\")` ∧ `resource.owner == principal` ∧ "
     "current `epoch` and `round` ∧ `!resource.sealed`", "ADR-0040 §1; ADR-0041 §1", "genesis"],
    ["`R4-consult-pinned`", P, "`Consult`", "run ∧ `alphabet.contains(\"Consult\")` ∧ `resource in context.runRoot`",
     "ADR-0040 §1; ADR-0041 §1", "genesis"],
    {"group": "Run carve-outs: coupling (one) and the label minimum (three)", "accent": "pink"},
    ["`R3-observer-live`", F, "`Actuate` `Report`", "`principal.kind == \"thinker\"` ∧ `!context.observerLive`. Names "
     "`thinker` seats, so it does not reach an `emergency` seat", "ADR-0039 §2, A2; ADR-0041 §2", "genesis"],
    {"cells": ["`R5-no-read-then-send`", F, "`Actuate`", "`resource.outward` ∧ `context.clearSet.contains(\"untrusted\")` "
               "∧ (`context.clearSet.contains(\"restricted\")` ∨ `context.inputLabels.contains(\"restricted\")`)",
               "ADR-0047 §7 F1; ADR-0041 A1", "[[teal|labels]]"], "accent": "teal"},
    {"cells": ["`R6-no-steered-destination`", F, "`Actuate`", "`resource.outward` ∧ "
               "`context.clearSet.contains(\"untrusted\")` ∧ `context.destLiteral`", "ADR-0047 §7 F2; ADR-0041 A1",
               "[[teal|labels]]"], "accent": "teal"},
    {"cells": ["`R7-no-replayed-destination`", F, "`Actuate`", "`resource.outward` ∧ "
               "`context.destLabels.contains(\"untrusted\")`", "ADR-0047 §7 F3; ADR-0041 A1", "[[teal|labels]]"],
     "accent": "teal"},
    {"group": "Floor exceptions: ADR-0013 §2, count 1, bounded by ADR-0026 R6 (A2)", "accent": "red"},
    {"cells": ["`X1-break-glass`", "[[grey|removed]]", "`Actuate`", "**Deleted.** Was: run ∧ "
               "`context.breakGlass.quorum` ∧ `resource in context.breakGlass.tools`; the `breakGlass` fields left "
               "schema S with it. Not counted in the 28", "ADR-0041 A2; ADR-0013 A1; ADR-0052 §2 (provisional)",
               "[[grey|retired: emergency]]"], "accent": "grey"},
    ["`X2-erasure`", P, "`Erase`", "`context.erasureQuorum`: FALSE from epoch 0, since genesis issues no erasure roster",
     "ADR-0006; ADR-0013 §2; ADR-0029 §5", "genesis"],
    {"group": "The forensic floor: ADR-0028 (one)", "accent": "brown"},
    ["`F-forensic-classes`", F, "`Erase`", "`[\"F1\", \"F2\", \"F3\", \"F4\", \"F5\", \"F6\"].contains(resource.class)`",
     "ADR-0028", "genesis"],
    {"group": "Control entries: an `operator` seat's requests, ADR-0050 §4 (provisional), named by ADR-0041 A3 (nine)",
     "accent": "blue"},
    ["`C1-regrant-successor`", P, "`Regrant`", "`principal.kind == \"operator\"` ∧ `resource.domain == "
     "principal.domain` ∧ `context.targetSeated` ∧ `!context.targetLive` ∧ `context.sameBinding` ∧ "
     "`context.nextRound` ∧ `context.lastAlphabet.containsAll(context.newAlphabet)`", "ADR-0050 §2, §4",
     "[[blue|control]]"],
    ["`C2-renew`", P, "`Renew`", "operator ∧ `resource.domain == principal.domain` ∧ `context.targetLive`",
     "ADR-0050 §4; ADR-0031 §4", "[[blue|control]]"],
    ["`C3-attest-gates`", P, "`AttestGates`", "operator ∧ `principal.domain == \"build\"`", "ADR-0050 §4",
     "[[blue|control]]"],
    ["`C4-deny`", P, "`EndRound` `Revoke` `FenceEpoch`", "operator ∧ `context.personaInForce` ∧ (`context.hasLease` ∨ "
     "`context.freshAssertion`): a deny needs no lease", "ADR-0050 §4 (R1)", "[[blue|control]]"],
    ["`C5-add-needs-lease-and-peer`", F, "`Regrant` `Renew` `AttestGates`", "`!context.hasLease` ∨ `!context.peerLive`",
     "ADR-0050 §4, §6", "[[blue|control]]"],
    ["`C6-no-self`", F, "`Regrant` `Renew`", "`resource == principal`", "ADR-0050 §4", "[[blue|control]]"],
    ["`C7-fence-needs-lease`", F, "`FenceEpoch`", "`!context.hasLease`: the one deny that needs a live lease",
     "ADR-0050 §4 (R5)", "[[blue|control]]"],
    ["`C8-task-label-in-bounds`", F, "`Regrant`", "`!context.taskLabelled` ∨ "
     "`!context.taskLabelsAllowed.containsAll(context.taskLabel)`", "ADR-0050 §5; ADR-0047 §1", "[[blue|control]]"],
    ["`C9-stop-in-own-domain`", F, "`EndRound` `Revoke`", "`resource.domain != principal.domain`. Not in ADR-0050's "
     "first list of eight; confirmed by the custodian 2026.10.05", "ADR-0050 §4 (R5), R9; ADR-0041 A3",
     "[[blue|control]]"],
]


def build():
    c = Canvas(ID, "The policy floor in force: three gated stages from the genesis draft",
               "`floor/proposed/build.py` builds the floor that the entries in force describe from "
               "`floor/genesis-floor.cedar`, in three cumulative stages, each validated, tested and gated: `labels` "
               "(ADR-0041 A1), `control` (A3) and `emergency` (A2). The reference links the last. The floor is "
               "genesis-provisional (ADR-0030 A3): gated, pinned and enforced, ratified by no batch, and ratified when "
               "the bootstrap reviewer establishes that it is fit, for which no test exists (G10 item 87).",
               W, "G10 §1 (Batch 34), §1.2, §2.1, §2.2, §2.3, §2.9, §3, §4, §7 items 2, 25, 87, 90, 91, 92, 93, §8; "
               "ToO rev 14 §2.10, §3.1, §3.3, §7.10; ADR-0041 §1–§4, A1, A2, A3, R2; ADR-0030 §5, A1, A2, A3; "
               "ADR-0029 §5 step 6, A4; ADR-0047 §7, §8, R16; ADR-0050 §2, §4–§6, R8, R9; ADR-0052 §1, §2, R4; "
               "ADR-0033 A9–A12, A15; ADR-0013 A1; ADR-0026 A2; ADR-0039 A2; ADR-0045 T-0045-3; "
               "floor/proposed/README.md, build.py, run-gates.py, labels-, control-, emergency-floor.cedar and "
               ".cedarschema, the three *-gates-results-2026.10.04.txt, emergency-tests.json; floor/genesis-floor.cedar, "
               "genesis.cedarschema, genesis-values.json, genesis-tests.json, run-gates.py, "
               "genesis-gates-results-2026.10.01.txt; mechanism/crates/topak-floor/src/lib.rs (the pins); ADR-0053 R3 "
               "(Proposed); floor/lean/TopakFloor/InForce.lean and floor/lean/TopakFloor-results-2026.10.06.txt")
    X0, X1 = c.x0, c.x1
    y = c.y
    y += c.legend(X0, y, [
        ("box", "violet", "draft or genesis-provisional: not ratified"), ("box", "teal", "labels stage"),
        ("box", "blue", "control stage; ratified records"), ("box", "green", "emergency stage, linked"),
        ("box", "red", "carve-out, gap, what the gates do not show"), ("box", "grey", "removed"),
        ("arrow", "ink", "build step: one stage is the previous plus one batch of records"),
    ], title="Read as") + 30

    # ---------------------------------------------------------------- status band
    g = 30
    sw = (X1 - X0 - g) * 0.6
    sw2 = X1 - X0 - g - sw
    st = ("The floor is genesis-provisional (ADR-0030 A3, Batch 34)", [
        "**Gated, pinned by digest and enforced, and ratified by no batch.** It is ratified when **the bootstrap "
        "reviewer establishes that it is fit**, and says so in the review attestation the genesis bundle carries "
        "(ADR-0029 §5 step 6, A4). That gives floor fitness an owner and a time.",
        "**It does not give it a test** (G10 item 2; item 87, new). The gates show a floor is consistent, total, "
        "non-vacuous and minimal; whether it is the right floor is the reviewer's judgment, and no record says how a "
        "reviewer tests that. **No bootstrap reviewer is engaged** and no review pass has run (G10 §4).",
        "**The floor in question is the one the entries in force describe** (ADR-0030 A3): since Batch 34 that is "
        "`emergency-floor.cedar` and its schema. ADR-0041 ratified what the floor must contain, entry by entry, not a "
        "text. The control entries and the emergency change rest on records ratified **provisional** (ADR-0050, "
        "ADR-0052; ADR-0029 A4).",
    ])
    wc = ("The stage files open with a comment that is wrong (G10 item 91)", [
        "Every stage's floor and schema open: `// PROPOSED · built by floor/proposed/build.py from the genesis floor "
        "· stage: emergency · not ratified, // and not what the reference follows.` The reference has linked a "
        "stage since `c15026d`, and links `emergency` now.",
        "**The bytes are kept as gated**, so the digests the gate results and the records cite are the digests the "
        "reference pins. Correcting the comment is a gate rerun and **new digests in ADR-0047, ADR-0050 and "
        "ADR-0052** (and the pins of ADR-0033 A10 to A12).",
    ])
    h1 = c.card(0, 0, sw, st[0], st[1], size=14.5, status="genprov", draw=False)
    h2 = c.card(0, 0, sw2, wc[0], wc[1], size=14.5, draw=False)
    hh = max(h1, h2)
    c.card(X0, y, sw, st[0], st[1], accent="violet", size=14.5, status="genprov",
           status_extra="ADR-0030 A3 · ratified at bootstrap", h=hh)
    c.card(X0 + sw + g, y, sw2, wc[0], wc[1], accent="red", size=14.5, h=hh, tint=False, dash="6 4")
    y += hh + 56

    # ---------------------------------------------------------------- the pipeline
    c.text(X0, y + 22, "The build: genesis draft → `labels` → `control` → `emergency`", 22, "ink", bold=True)
    y += 44
    ag = 120
    cw = (X1 - X0 - 3 * ag) / 4
    xs = [X0 + i * (cw + ag) for i in range(4)]
    stages = [
        ("`floor/genesis-floor.cedar`", "violet", "draft", "the text the stages are built from", None, [
            "**17 policies · 62 cases** (`genesis-tests.json`).",
            "Floor `28ec0e4552c6a915` · schema `0ec2fa215eefe136`.",
            "**Unchanged since G7**, and not edited by the build. Gated six times, last 2026.10.01 with checked proofs; "
            "that run's evidence is copied beside it.",
            "Linked by the reference until `7764e52` (ADR-0033 A9, 116 tests).",
            "Holds `X1-break-glass`; the exceptions were two.",
        ]),
        ("Stage `labels`", "teal", None, "", "Gated 2026.10.04 · linked at `c15026d` (ADR-0033 A10), replaced at "
         "`c7de2ba`", [
            "**Records:** ADR-0047, with ADR-0048 and ADR-0049; **ADR-0041 A1**; ADR-0030 A2.",
            "**Adds** `R5`, `R6`, `R7`: three forbids on `Actuate` over labels.",
            "**20 policies · 74 cases.**",
            "Floor `9aab481d02414de2` · schema `9beda963b076cb06`.",
            "Cited by ADR-0047 R16 and ADR-0033 A10 (119 tests at the reference).",
            "Break-glass here is still the genesis one: `R5` to `R7` hold under `X1`, and the tests say so.",
        ]),
        ("Stage `control`", "blue", None, "", "Gated 2026.10.04 · linked at `c7de2ba` (ADR-0033 A11), replaced at "
         "`9c57221`", [
            "**Records:** + ADR-0050 (**provisional**); **ADR-0041 A3**.",
            "**Adds** `C1` to `C9`: six actions and nine entries for an `operator` seat.",
            "**29 policies · 106 cases.**",
            "Floor `4341ede9e26419cc` · schema `4e24033b547f1ed2`.",
            "Cited by ADR-0050 R8 and ADR-0033 A11 (126 tests).",
            "At the reference the floor alone decides a control request: there is no bundle tier (A11).",
        ]),
        ("Stage `emergency`: the floor in force", "green", "genprov", "linked by the reference",
         "Gated 2026.10.04 · linked since `9c57221` (ADR-0033 A12)", [
            "**Records:** + ADR-0052 (**provisional**); **ADR-0041 A2**; ADR-0013 A1; ADR-0026 A2.",
            "**Removes** `X1-break-glass`; `B10` **now** lets a seat of kind `emergency` `Actuate`. No new entry.",
            "**28 policies · 107 cases.** The floor's exceptions are one.",
            "Floor `15c941b9a56a09f7` · schema `d3c8145c6af2d9a3`.",
            "Cited by ADR-0052 R4, ADR-0033 A12 and G10 §2.2; pinned in `topak-floor` (`PINNED_FLOOR_SHA256`); the "
            "replica refuses to start on other bytes.",
            "The 107 cases replay through the linked engine; 131 tests at A12, 133 at `075b2e7` (A15).",
        ]),
    ]
    hs = max(c.card(0, 0, cw, t, b, size=14, status=s, status_extra=e, sub=sub, draw=False)
             for t, a, s, e, sub, b in stages)
    for x, (t, a, s, e, sub, b) in zip(xs, stages):
        c.card(x, y, cw, t, b, accent=a, size=14, status=s, status_extra=e, sub=sub, h=hs)
    ay = y + 120
    steps = [("+3 forbids\n(ADR-0041 A1)", "teal"), ("+9 control entries\n(ADR-0041 A3)", "blue"),
             ("−1 permit, B10 amended\n(ADR-0041 A2)", "green")]
    for i, (lab, acc) in enumerate(steps):
        c.arrow([(xs[i] + cw, ay), (xs[i + 1], ay)], acc, sw=2.6)
        c.label(xs[i] + cw + ag / 2, ay + 52, lab, acc, 12.5, maxw=ag - 4)
    y += hs + 18
    vb = c.card(X0, y, X1 - X0, "", [
        "**The values file is the same in every stage**: `genesis-values.json` `85ab6fefb66f0316`: `K` = 8, `T_obs` = "
        "5000 ms, `T_persona` = 1 h, the five θ values unset. **Every number is a placeholder.** Each stage's gate run "
        "checks it first (ADR-0039 §1). Each step **replaces a string asserted to occur exactly once** in the genesis "
        "text, so a change to the genesis floor the build does not expect stops it instead of producing a wrong floor."
    ], accent="grey", size=14, bullets=False, tint=False)
    y += vb + 50

    # ---------------------------------------------------------------- what each stage changes
    c.text(X0, y + 22, "What each stage adds, removes and asks of the lift", 22, "ink", bold=True)
    y += 46
    col_top = y
    mono = {"mono": True}
    # column 0: how a stage is made
    cy = col_top
    cy += c.card(xs[0], cy, cw, "How a stage is made and checked", [
        "`python3 build.py` writes, per stage, `<stage>.cedarschema`, `<stage>-floor.cedar` and `<stage>-tests.json`. "
        "Generated: edit `build.py`, not the files.",
        "`cedar validate` against the stage's schema, then `cedar run-tests` on its cases.",
        "`run-gates.py <stage>` drives the genesis runner `../run-gates.py` **unchanged**: same gates, same checked "
        "solver, same negative and checker controls; then adds routing controls for the new entries.",
        "**A rerun reproduces each results file byte for byte**, evidence digest included. The evidence itself (every "
        "query, proof and checker verdict) is left in a temporary directory and **not copied**.",
        "`emergency-tests.json` is tracked because the reference's floor tests replay it; the other two stages' "
        "cases are not (about 2 MB).",
    ], accent="grey", size=14) + 18
    cy += c.card(xs[0], cy, cw, "Not in the floor, at any stage (header of the genesis text)", [
        "**Epoch fencing**: the mechanism, ahead of the floor (ADR-0022 §2).",
        "**The round bound**: a count, mechanism-checked (ADR-0022 §3).",
        "**The rules floor**: bounds issuances, not admits (ADR-0030 §7).",
        "`Invoke` **hermeticity**: an obligation on each allowlist entry.",
        "**ADR-0047's F4 to F6**: checks on bundle data at load (ADR-0049 §6, W7 to W9), made by the mechanism. Not "
        "Cedar, and not here.",
        "**A first lease**: granted by the mechanism when a quorum completes (ADR-0050 §2); not an action, no entry.",
    ], accent="grey", size=14, tint=False)
    b0 = cy

    # column 1: labels
    cw_in = cw
    cy = col_top
    c.text(xs[1], cy + 18, "`labels`: three forbids over labels", 18, "teal", bold=True)
    cy += 32
    cy += c.table(xs[1], cy, [("Id", cw_in * 0.40, mono), ("Refuses an outward call when", cw_in * 0.60)], [
        ["R5-no-read-then-send", "`clearSet` holds `untrusted`, and `restricted` is in `clearSet` or in `inputLabels`"],
        ["R6-no-steered-destination", "`clearSet` holds `untrusted`, and a destination input is a literal"],
        ["R7-no-replayed-destination", "a destination input is a handle whose label holds `untrusted`"],
    ], size=13.5, accent="teal") + 12
    cy += c.para(xs[1], cy, cw_in, "Each is a set-membership test on attributes the mechanism computed. `untrusted` "
                 "and `restricted` are the two names the floor reserves. As forbids they deny whatever permit is "
                 "satisfied (ADR-0047 §7).", 13.5, "muted") + 14
    c.text(xs[1], cy + 16, "Schema S gains (ADR-0030 A2; ADR-0041 §4 A1)", 16, "teal", bold=True)
    cy += 28
    cy += c.table(xs[1], cy, [("Where", cw_in * 0.22, mono), ("Attribute", cw_in * 0.30, mono),
                              ("What it is", cw_in * 0.48)], [
        ["Tool", "outward: Bool", "derived by the lift from the entry's channel and the issued rules' list of targets "
                                  "inside the deployment; **never declared**"],
        ["RunCtx", "clearSet: Set<String>", "labels of everything delivered clear to this principal this round"],
        ["RunCtx", "inputLabels: Set<String>", "join of the labels of the call's inputs that are handles"],
        ["RunCtx", "destLiteral: Bool", "an input the entry marks a destination is a literal"],
        ["RunCtx", "destLabels: Set<String>", "join of the labels of destination inputs that are handles"],
    ], size=13.5, accent="teal") + 12
    cy += c.para(xs[1], cy, cw_in, "Written by the lift, from the record and the entry of the granted bundle "
                 "revision; no policy computes them. `clearSet` is the first attribute in S that depends on the round's "
                 "history, a monotone fold, and **history enters S only so** (ADR-0030 A2). `Report` takes `clearSet` "
                 "and no entry reads it yet.", 13.5, "muted") + 10
    cy += c.para(xs[1], cy, cw_in, "**Cases 62 → 74**: twelve added, two of them `R5` and `R6` holding under `X1`. "
                 "**Routing controls: four** (below).", 13.5, "ink")
    b1 = cy

    # column 2: control
    cy = col_top
    c.text(xs[2], cy + 18, "`control`: six actions, nine entries", 18, "blue", bold=True)
    cy += 32
    cy += c.table(xs[2], cy, [("Id", cw_in * 0.40, mono), ("Kind", cw_in * 0.12), ("Says", cw_in * 0.48)], [
        ["C1-regrant-successor", "permit", "an operator grants a seated target's next round, in its own domain, same "
                                           "binding, an alphabet the last one's or narrower"],
        ["C2-renew", "permit", "an operator renews a live lease in its domain"],
        ["C3-attest-gates", "permit", "a Build operator records that the gates ran"],
        ["C4-deny", "permit", "an operator whose Persona is in force ends a round, revokes or fences, under a live "
                              "lease or a fresh sign-on assertion"],
        ["C5-add-needs-lease-and-peer", "forbid", "no add without a live lease and a live peer"],
        ["C6-no-self", "forbid", "no regrant or renewal of oneself"],
        ["C7-fence-needs-lease", "forbid", "no fleet fence without a live lease"],
        ["C8-task-label-in-bounds", "forbid", "no regrant whose task is unlabelled, or labelled outside its "
                                              "seating's bounds"],
        ["C9-stop-in-own-domain", "forbid", "no ending of a round or revocation outside the operator's domain"],
    ], size=13.5, accent="blue") + 12
    c.text(xs[2], cy + 16, "Schema S gains the kind `operator`, `Fleet`, six actions and `ControlCtx`", 16, "blue",
           bold=True)
    cy += 28
    cy += c.table(xs[2], cy, [("`ControlCtx`: thirteen facts", cw_in * 0.38, mono), ("The mechanism holds", cw_in * 0.62)], [
        ["personaInForce", "the operator's Persona is promoted and not revoked"],
        ["hasLease", "the operator holds a live lease"],
        ["peerLive", "another operator in the domain holds a live lease"],
        ["freshAssertion", "a sign-on assertion naming the key and the current fence verified"],
        ["targetSeated", "the target was seated by a quorum and is not revoked"],
        ["targetLive", "the target holds a live lease"],
        ["sameBinding", "Persona, bundle, confinement and seat are the last lease's"],
        ["nextRound", "the round named is the last lease's, advanced by one"],
        ["lastAlphabet · newAlphabet", "the last lease's alphabet · the alphabet asked for"],
        ["taskLabelled", "the task carries a label (ADR-0047 §1)"],
        ["taskLabel · taskLabelsAllowed", "the task's label · the labels the target's seating allows (ADR-0050 §5)"],
    ], size=13.5, accent="blue") + 12
    cy += c.para(xs[2], cy, cw_in, "**The operator supplies none of them.** `sameBinding` and `nextRound` are compared "
                 "by the lift, not in Cedar: a round comparison is arithmetic on a `Long`, which the totality gate "
                 "refuses because it can overflow; the alphabets are compared in Cedar (ADR-0041 A3). Actions: "
                 "`Regrant`, `Renew`, `AttestGates`, `EndRound`, `Revoke` (resource `Seat` or `Artifact`) and "
                 "`FenceEpoch` (resource `Fleet`).", 13.5, "muted") + 10
    cy += c.para(xs[2], cy, cw_in, "**Cases 74 → 106**: thirty-two added. **Routing controls: nine**, the four of "
                 "`labels` and five more.", 13.5, "ink")
    b2 = cy

    # column 3: emergency
    cy = col_top
    c.text(xs[3], cy + 18, "`emergency`: one permit removed, one forbid amended", 18, "green", bold=True)
    cy += 32
    cy += c.table(xs[3], cy, [("Entry", cw_in * 0.27, mono), ("Genesis to `control`", cw_in * 0.36),
                              ("`emergency`", cw_in * 0.37)], [
        {"cells": ["X1-break-glass", "permit `Actuate`: run ∧ `breakGlass.quorum` ∧ `resource in breakGlass.tools`",
                   "**deleted**"], "accent": "grey"},
        ["B10-only-thinkers-author", "`when { principal.kind != \"thinker\" }`",
         "`principal.kind != \"thinker\"` ∧ `!(principal.kind == \"emergency\" && action == Actuate)`"],
    ], size=13.5, accent="green") + 12
    cy += c.table(xs[3], cy, [("Schema S", cw_in * 0.27), ("Change", cw_in * 0.73)], [
        ["`Seat.kind`", "gains `\"emergency\"` (ADR-0052 §1)"],
        ["`RunCtx`", "loses `breakGlass: {quorum: Bool, tools: ToolSet}`: an emergency seat's envelope is its "
                     "`toolAllowlist`, computed at activation; the roster's quorum granted its lease and is not a "
                     "request property (ADR-0052 §2)"],
    ], size=13.5, accent="green") + 12
    cy += c.card(xs[3], cy, cw_in, "How break-glass reads now (ADR-0041 §3 as A2 replaces it)", [
        "**No break-glass permit.** The roster's quorum seats a named person on a seat of kind `emergency` for one "
        "round, on a bundle revision whose allowlist is the envelope; its `Actuate` is admitted by `R1` like any other.",
        "`R3` **is unchanged** and does not reach the seat: it names `thinker` seats (ADR-0039 A2). No exemption "
        "was written into it.",
        "`R5` **to** `R7` **bind the person**: they are forbids on `Actuate` whatever the seat's kind (A2, beside A1).",
        "The seat holds `Consult`, `Actuate` and `Report`, and cannot vote, draft or submit, which is what ADR-0026 R7 "
        "asked of a break-glass grant.",
        "**The exceptions are one**, erasure (ADR-0013 A1; ADR-0026 A2: R6's count is one).",
    ], accent="green", size=13.5, status="provisional", status_extra="rests on ADR-0052") + 12
    cy += c.para(xs[3], cy, cw_in, "**Cases 106 → 107**: the seven `X1` and break-glass cases removed, eight added: "
                 "an emergency seat calls a tool in its envelope; is not coupled with no live Observer; is refused a "
                 "tool outside it; reports with no live Observer; `X1` retired, a Thinker cannot reach the envelope; "
                 "`R6` binds the person; the seat cannot draft; cannot submit. **Routing controls: eleven.**", 13.5,
                 "ink")
    b3 = cy
    y = max(b0, b1, b2, b3) + 56

    # ---------------------------------------------------------------- the gates
    c.text(X0, y + 22, "The gates, stage by stage (ADR-0030 §5 with A1): every gate passes in all three", 22, "ink",
           bold=True)
    y += 46
    gw = 1880
    gc = [("Gate (ADR-0030 §5)", gw * 0.30), ("Genesis, 2026.10.01", gw * 0.16), ("`labels`", gw * 0.18),
          ("`control`", gw * 0.18), ("`emergency`", gw * 0.18)]
    grows = [
        ["Floor · schema", "`28ec0e45…` · `0ec2fa21…`", "`9aab481d…` · `9beda963…`", "`4341ede9…` · `4e24033b…`",
         "`15c941b9…` · `d3c8145c…`"],
        ["Policies · cases", "17 · 62", "20 · 74", "29 · 106", "28 · 107"],
        ["Values: `K`, `T_obs` read and placeholders named", "pass", "pass", "pass", "pass"],
        ["**Totality**: never-errors, per policy per action it applies to", "23 rows", "26 rows", "41 rows",
         "41 rows"],
        ["**Non-vacuity** and **discrimination**: always-allows and always-denies both refuted, per action", "10 actions",
         "10 actions", "16 actions", "16 actions"],
        ["**Every entry matters**: the floor minus one policy is not equivalent", "17", "20", "29", "28"],
        ["**Routing**: the four genesis candidates, classed by implies both ways", "4 pass", "4 pass", "4 pass",
         "4 pass"],
        ["**Routing, new entries**: weakened is a relaxation, strengthened a tightening", "—", "4 pass", "9 pass",
         "11 pass"],
        ["**Negative controls**: each gate catches a defective floor", "4 caught", "4 caught", "4 caught", "4 caught"],
        ["**Checker controls**: a solver that lies yields no `holds` (A1)", "3 caught", "3 caught", "3 caught",
         "3 caught"],
        ["`holds` without a checked proof, whole run", "0", "0", "0", "0"],
        ["cedar calls · solver queries", "81 · 56", "95 · 67", "147 · 104", "151 · 108"],
        ["unsat with a checked proof · sat · unknown (the three checker controls)", "4 · 49 · 3", "8 · 56 · 3",
         "13 · 88 · 3", "15 · 90 · 3"],
        ["Evidence tree", "`f8b1196a427a35ed`, copied", "`ede6f4546ae6db48`, not copied", "`d1e617defade056b`, not copied",
         "`974f339662a5289d`, not copied"],
        ["Results file (sha256)", "`genesis-gates-results-2026.10.01.txt`", "`labels-…-2026.10.04.txt` "
         "`3579b95a42573958`", "`control-…-2026.10.04.txt` `aa96c96916a87c05`",
         "`emergency-…-2026.10.04.txt` `7deaf26c1dc49422`"],
        {"cells": ["RESULT", "all gates pass", "all gates pass", "all gates pass", "all gates pass"], "accent": "green"},
    ]
    gh = c.table(X0, y, gc, grows, size=13.5, accent="ink")
    gy = y + gh + 12
    c.para(X0, gy, gw, "**Checked, not proved** (ADR-0046 §1). A `holds✓` rests on the solver's proof, which the "
           "pinned `ethos` checker accepted against cvc5's rule signature (ADR-0030 A1); a `holds°` is one cedar decided "
           "without a solver query, by folding the authorizer term, and rests on the engine's faithfulness (T-0045-3). "
           "Every totality row in every stage is `holds°`; the `emergency` stage's are also proved in Lean under "
           "cedar-spec's model ([[amber|ADR-0053 R3, Proposed]]; H7). A `refuted` needs no proof: it can only subtract. Toolchain: "
           "cedar-policy-cli 4.13.0, cvc5 1.4.0, `ethos` 8dc85c4.", 13.5, "muted")
    rx = X0 + gw + 40
    rw = X1 - rx
    c.text(rx, y - 8, "The eleven new-entry routing controls, as the `emergency` run reports them", 16, "ink",
           bold=True)
    rc = [("Candidate F′ (from the stage that adds it)", rw * 0.42), ("F′⇒F", rw * 0.11), ("F⇒F′", rw * 0.11),
          ("Classed · routed", rw * 0.36)]
    REL = "[[red|relaxation]] · anchor issuance + promotion"
    TIG = "[[green|tightening]] · ordinary promotion"
    rr = [
        {"group": "`labels` (four)", "accent": "teal"},
        ["`R6` removed", "refuted", "holds✓", REL],
        ["`R5` reads only what was read in the clear", "refuted", "holds✓", REL],
        ["`R6` without the untrusted-read condition", "holds✓", "refuted", TIG],
        ["`R7` removed", "refuted", "holds✓", REL],
        {"group": "`control` (five more)", "accent": "blue"},
        ["`C5` without the peer condition", "refuted", "holds✓", REL],
        ["`C7` removed: a lapsed operator may fence", "refuted", "holds✓", REL],
        ["`C4` needs a live lease", "holds✓", "refuted", TIG],
        ["`C1` without the alphabet comparison", "refuted", "holds✓", REL],
        ["`C8` removed: an unlabelled task", "refuted", "holds✓", REL],
        {"group": "`emergency` (two more)", "accent": "green"},
        ["`B10` as at genesis: no emergency seat", "holds✓", "refuted", TIG],
        ["`B10` admits every kind for `Actuate`", "refuted", "holds✓", REL],
    ]
    rh = c.table(rx, y + 8, rc, rr, size=13.5, accent="ink")
    c.para(rx, y + 8 + rh + 12, rw, "Every one passes: the class computed is the class expected. A Byzantine author "
           "cannot relabel a relaxation as a tightening to take the cheaper path (ToO rev 14 §3.2).", 13.5, "muted")
    y = c.ymax + 56

    # ---------------------------------------------------------------- what the gates show, and what they do not
    w2 = (X1 - X0 - g) / 2
    show = ("What the gates show", [
        "**The floor is consistent, total, non-vacuous and minimal** (ADR-0030 A3): no policy errors on any action it "
        "covers, no action is always allowed or always denied, and removing any one policy changes the floor.",
        "**Each new entry is routed correctly**: dropped or weakened, it is classed a relaxation; strengthened, a "
        "tightening. `B10` is shown to admit the new kind for `Actuate` and nothing else (ADR-0041 A2).",
        "**Each stage passes the genesis gates as they stand**, with no `holds` lacking a checked proof.",
        "**The cases**: each stage validates against its schema and passes its cases; `emergency`'s 107 replay "
        "through the engine the reference links (ADR-0033 A12).",
    ])
    noshow = ("What they do not show", [
        "**That it is the right floor.** Fitness is the bootstrap reviewer's judgment, with no test (items 2, 87).",
        "**The admit-time half only.** F4 to F6 are load checks, W7 to W9, in Rust (ADR-0049 §6; ADR-0030 A2).",
        "**The floor trusts its inputs.** `clearSet`, `destLiteral`, `peerLive` and the rest are facts the lift "
        "supplies; `Labels.tla` and `Operators.tla` model how they are computed. At the reference they are the "
        "deciding replica's, and `apply` re-checks only `clearSet` (G10 item 93).",
        "**An operator's request is decided twice over**: the envelope is stated in Cedar and in Rust, and only the "
        "tests hold them together (ADR-0033 A11). The floor's decision on one is not modelled by trace validation "
        "(G10 §3).",
        "`spec/` **is behind**: `RulesFloorBase.tla` still carries `bgScope` and R6's bound of two (G10 item 90).",
    ])
    h3 = max(c.card(0, 0, w2, t, b, size=14, draw=False) for t, b in (show, noshow))
    c.card(X0, y, w2, show[0], show[1], accent="teal", size=14, h=h3)
    c.card(X0 + w2 + g, y, w2, noshow[0], noshow[1], accent="red", size=14, h=h3, tint=False, dash="6 4")
    y += h3 + 60

    # ---------------------------------------------------------------- every policy
    c.text(X0, y + 22, "Every policy in the `emergency` stage, the floor in force: 28, in file order "
           "(`floor/proposed/emergency-floor.cedar`)", 22, "ink", bold=True)
    c.status(X1, y + 4, "genprov", "15c941b9a56a09f7 · ADR-0030 A3", anchor="end")
    y += 42
    y += c.para(X0, y, X1 - X0,
                "Evaluation: any satisfied `forbid` denies; else any satisfied `permit` allows; else deny, and the "
                "mechanism treats any evaluation error as a deny (ADR-0030 §1). `build` and `run` abbreviate "
                "`principal.domain == \"build\"` and `== \"run\"`; `alphabet` is `context.lease.alphabet`; operator "
                "abbreviates `principal.kind == \"operator\"`. The retired `X1` is shown where it stood, and is not "
                "counted.", 14.5, "muted") + 14
    cols = [("Policy `@id`", 330), ("Effect", 100, {"bold": True}), ("Action(s)", 330),
            ("When (condition, as written)", 1800), ("From the record", 470), ("Stage", 0)]
    cols[-1] = ("Stage", X1 - X0 - sum(cc[1] for cc in cols[:-1]))
    y += c.table(X0, y, cols, POLICIES, size=14, accent="ink") + 20
    c.para(X0, y, X1 - X0,
           "Counts: six Build envelopes, four Build carve-outs, three Run envelopes, four Run carve-outs, one exception, "
           "the forensic floor, four control permits and five control forbids: **28**. The genesis draft's 17, plus three "
           "at `labels`, plus nine at `control`, less one at `emergency`. One policy set serves both domains, scoped by "
           "`principal.domain` and `principal.kind`, because the per-class floor question is open (ToO rev 14 §3.4).",
           14.5, "muted")
    return c
