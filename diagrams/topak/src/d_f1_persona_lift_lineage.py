"""F1 — Persona, lift and lineage: the model enters as a verified artifact; its lineage is a projection (Proposed)."""
import re

import lib
from lib import Canvas

ID, SLUG = "F1", "persona-lift-lineage"


def _boldfix(s):
    """Split a **bold** span that holds `code` into bold runs around the code (lib cannot nest them)."""
    segs = s.split("**")
    if len(segs) % 2 == 0:
        return s
    out = []
    for k, seg in enumerate(segs):
        if k % 2 == 0:
            out.append(seg)
        elif "`" in seg:
            parts = re.split(r"(`[^`]+`)", seg)
            out.append("".join(p if p.startswith("`") else (f"**{p}**" if p.strip() else p) for p in parts))
        else:
            out.append(f"**{seg}**")
    return "".join(out)


def build():
    orig = lib.parse
    lib.parse = lambda s: orig(_boldfix(s))
    try:
        return _build()
    finally:
        lib.parse = orig


def _row_cards(c, x, y, w, gap, specs, size=14):
    """Draw a row of cards with equal heights. specs: (title, body, accent, kwargs). Returns height."""
    n = len(specs)
    cw = (w - gap * (n - 1)) / n
    hs = [c.card(0, 0, cw, t, b, a, draw=False, size=size, **kw) for t, b, a, kw in specs]
    hh = max(hs)
    for i, (t, b, a, kw) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, a, h=hh, size=size, **kw)
    return hh


def _build():
    c = Canvas(ID, "The model enters as a Persona: a pinned identity, a split lift, and a lineage computed from the log",
               "ADR-0016 to ADR-0020 (Accepted (genesis) 2026.09.12) pin the one component that was a name: the Persona "
               "binds a model to its whole runtime configuration, is a verified Build artifact and a lease field. ADR-0035 "
               "(Proposed, not in force) would make lineage a projection of the Build log and independence an exclusion "
               "rule over two projections. Boundary B8: Persona / occupant identity.",
               3200, "ADR-0016 §1–§9 (B12); ADR-0017 and its ratification note; ADR-0018 (B12, reversed in part by "
               "ADR-0037 §3); ADR-0019; ADR-0020; ADR-0023 §5; ADR-0031 A2; ADR-0035 §1–§9, Findings 1–5, R1–R4 "
               "(Proposed); ADR-0037 §2, §3; ADR-0045 T-0045-15, finding 2; floor/genesis-values.json; "
               "derived/topak-boundary-register-2026.09.13.md B8; ToO rev 11 §6, §8.3, §10, §16; slm/ results "
               "2026.09.25 and 2026.09.28; G7 §1.1, §1.2, §7 items 6, 17, 20, 21, 30, 33, 62; mechanism/crates/topak-core/src/rules.rs (`personas`), confine.rs (`Provenance`); topak-contain (`model.json`); slm/lineage/record.py, thresholds.example.json; GAPS G13; derived/topak-format-and-schema-inventory-2026.10.03.md §1.6, §1.7, §8, finding 15")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y
    sx = X0
    sx += c.status(sx, y, "accepted", "ADR-0016, 0017, 0019, 0020 · 2026.09.12") + 10
    sx += c.status(sx, y, "accepted", "ADR-0018 in part: Reader scope reversed by ADR-0037 §3") + 10
    sx += c.status(sx, y, "accepted", "ADR-0017: ordering-primacy reversed in effect by ADR-0023, supersession unwritten") + 10
    sx += c.status(sx, y, "proposed", "ADR-0035 lineage, R4, C4 on ratification") + 10
    y += 52

    # ======================================================================== B8 region: Persona and its lifecycle
    btop = y + 16
    pad = 30
    ix = X0 + pad
    iw = W - 2 * pad
    ly = btop + 34
    lw = 1500
    # left: the Persona record
    ly += c.heading(ix, ly, "ADR-0016 §1 · A Persona binds, at minimum", "teal", 19)
    rows = [
        ["Provenance / lineage", "Training corpora identifiers, base-model ancestry, fine-tune chain. Degrades across "
         "rungs (ADR-0017). **Under ADR-0035 (Proposed): the digest of a projected lineage record**"],
        ["Persona ID", "Cryptographically signed by the Build promotion key; the signature is over the whole record, "
         "not the model alone"],
        ["Sequence number", "Monotonically increasing per Persona line. **Ordering only**, not the floor/bundle "
         "authority-monotonicity"],
        ["System prompt", "Byte-exact, hashed"],
        ["Decoding parameters", "Temperature, top-k, top-p, penalties, stop sequences"],
        ["Decoding stack version", "The sampler implementation: identical weights under a different sampler is a "
         "different Persona"],
        ["Determinism class", "Reproducible, seeded-reproducible or non-reproducible. Inventory and incident context; "
         "**not** an admission precondition (ADR-0020)"],
        ["Context window and truncation policy", "An unpinned truncation rule silently changes what the Thinker saw"],
        ["Decoder", "Identifier and hash of the model-specific emission decoder shipped with this Persona (ADR-0018)"],
        ["Decode observability", "`none` | `topk_logprobs`. Optional, rung-gated; non-default only within ADR-0019's "
         "narrow scope (§9)"],
        ["Seat binding", "Since ADR-0037 §2 (B12): `thinker` and `observer`. The Listener and the Reader are stages "
         "and bind no Persona"],
    ]
    ly += c.table(ix, ly, [("Field", 330, {"bold": True}), ("Notes", lw - 330)], rows, size=13.5, accent="teal") + 18
    ly += _row_cards(c, ix, ly, lw, 20, [
        ("§2 · Verification is a precondition", [
            "The artifact is what it claims to be: signature, hash, provenance chain, record completeness. Decidable.",
            "**TOPAK verifies Personas. It does not verify models.**"], "teal", {}),
        ("§3 · Suitability is evidence, and deny-only", [
            "Evaluations, benchmarks, red-team findings: statistical, no safety property.",
            "A passing evaluation can never admit a Persona; a failing one can deny or quarantine it (ADR-0007)."],
         "red", {}),
    ])
    left_bottom = ly

    # right: lifecycle flow
    rx = ix + lw + 70
    rw = ix + iw - rx
    ry = btop + 34
    ry += c.heading(rx, ry, "The Persona's path: a Build artifact, admitted per seat, carried in the lease", "teal", 19)
    steps = [
        ("Build: promoted and signed (§1, §2)", [
            "Every parameter change is a new Persona and a new promotion: temperature is a deploy-cadence change.",
            "Imported models pass the same gate; provenance degrades, the gate does not: **verified → attested → "
            "asserted** (§4)."], "blue"),
        ("Bundle policy admits Personas per seat (§5)", [
            "**Seat distinctness**: the Observer's Persona differs from the Thinker's by **lineage**, not configuration; "
            "since ADR-0037 one (`thinker`, `observer`) pair per cell. Enforcement moves to the tally and declaration "
            "(ADR-0035 §5, finding 1).",
            "**Floor bound**: the floor names admissible Persona classes; bundles only subtract."], "blue"),
        ("The lease carries the Persona ID (§6)", [
            "Attested at grant and at renewal; unattestable means deny, and the principal is evicted by the passive path.",
            "**`ttl ≤ T_persona`** (ADR-0031 A2), refused at grant and renewal at the reference since ADR-0033 A6 (I35). "
            "Expiry runs on the local clock, so the interval is `T_persona` plus drift (ADR-0045 finding 2; G7 item 62)."],
         "teal"),
        ("Revocation is an ordinary deny (§7)", [
            "Local, no consensus, no floor exception; not an ADR-0013 carve-out. A revoked Persona's leases end, it is "
            "barred from later grants, and no other round stops."], "green"),
    ]
    for i, (t, b, a) in enumerate(steps):
        h = c.card(rx, ry, rw, t, b, a, size=14)
        if i < len(steps) - 1:
            c.arrow([(rx + rw / 2, ry + h), (rx + rw / 2, ry + h + 34)], a)
        ry += h + 34
    ry -= 34
    ry += 24
    ry += c.card(rx, ry, rw, "B8 in the boundary register (09.13) and since", [
        "**As registered**: outer cadence Provider (uncontrolled) / Persona promotion; instant: Persona promotion only; "
        "interval of untruth unbounded (no expiry, no re-attestation); behaviour when unavailable undefined. \"The "
        "largest empty cell in the grid\" (ToO §10: the most critical boundary).",
        "**Since**: model change has an event (lease attestation catches a declared change, ADR-0019 drift an undeclared "
        "one); the interval is bounded by `T_persona` on the value, not on the clock.",
    ], "brown", size=14)
    ry += 24
    ry += c.card(rx, ry, rw, "At the reference: no Persona record, a `model.json` stand-in", [
        "The reference has **none of §1's fields**. Its Persona is a `model.json` bundle, `{family, params, weights, "
        "weights_sha256}`, whose id is the SHA-256 of the file's bytes (`topak-contain`; `slm/`). `Rules.personas` maps "
        "that digest to an ADR-0017 provenance (`in_house_pretrain`, `in_house_finetune`, `attested_external`, "
        "`asserted_external`) and is empty in dev.",
        "For an operator grant `persona` is an operator-supplied digest, checked against nothing (G13); a launch "
        "checks the guest's reported digest against the profile's, which is all a rung detects. `ttl ≤ T_persona` "
        "is the one rule of §6 the code enforces (inventory §1.6).",
    ], "red", size=14, status="notbuilt", status_extra="the record proper; the stand-in is built", tint=False,
                 dash="6 4")
    bottom = max(left_bottom, ry) + 30
    c.region(X0, btop, W, bottom - btop, "B8 · Persona / occupant identity (ADR-0016, ADR-0017)", "teal", dash=None,
             sw=2.4, size=15)
    y = bottom + 60

    # ======================================================================== the typed lift
    y += c.heading(X0, y, "ADR-0018 · The typed lift splits: the decoder ships in the Persona, the validator stays in the "
                          "mechanism", "teal", 20)
    fy = y + 10
    nodes = [
        ("Thinker's model", ["The occupant, under its Persona."], "grey", 300),
        ("Raw emission", ["**Cognitive payload.** Retained in the round topic at the archetype (ADR-0037; D-0037-2 "
                          "is its absence)."], "pink", 420),
        ("Decoder", ["In the **Persona**. Owner Persona, cadence Persona promotion, model-specific, **not trusted**: "
                     "a hostile decoder cannot produce an inadmissible action."], "amber", 470),
        ("Candidate typed action", ["Control plane, if it validates."], "grey", 330),
        ("Validator", ["In the **mechanism**. Owner `Contain`, cadence release, model-agnostic, **trusted**: total over "
                       "the floor's action alphabet, verified once."], "teal", 470),
    ]
    gapf = (W - 270 - sum(n[3] for n in nodes)) / (len(nodes) - 1)
    hs = [c.card(0, 0, n[3], n[0], n[1], n[2], draw=False, size=14, bullets=False) for n in nodes]
    hh = max(hs)
    x = X0
    xs = []
    for (t, b, a, w), in zip(nodes):
        c.card(x, fy, w, t, b, a, h=hh, size=14, bullets=False)
        xs.append((x, w))
        x += w + gapf
    for (xa, wa), (xb, wb) in zip(xs, xs[1:]):
        c.arrow([(xa + wa, fy + hh / 2), (xb, fy + hh / 2)], "ink")
    ox = xs[-1][0] + xs[-1][1] + 60
    c.pill(ox, fy + 10, "admit: a boundary event", "green", 13)
    c.pill(ox, fy + hh - 34, "deny: local, monotone", "red", 13)
    c.arrow([(xs[-1][0] + xs[-1][1], fy + 22), (ox, fy + 22)], "green")
    c.arrow([(xs[-1][0] + xs[-1][1], fy + hh - 22), (ox, fy + hh - 22)], "red", dash="7 5")
    y = fy + hh + 40
    w2 = (W - 30) / 2
    t1h = c.table(X0, y, [("Artifact (ADR-0018)", 330, {"bold": True}), ("Nature", 330), ("Admission role", w2 - 660)], [
        ["Logits / top-k logprobs", "Side channel, optional", "Decoding attestation: may admit (ADR-0019)"],
        ["Raw emission", "Cognitive payload", "None: it is the decoder's input"],
        ["Typed action", "Control plane", "Boundary event; may admit"],
        ["Interpreted output", "Cognitive", "**Deny-only**, per ADR-0007"],
    ], size=14, accent="teal")
    rh = c.card(X0 + w2 + 30, y, w2, "What the split buys, and what it concedes", [
        "**Adding a model family is a Persona promotion, not a mechanism release**: the verified object never learns "
        "any model's output format (the ADR-0010 move, applied to syntax).",
        "**The validator guarantees admissibility, not fidelity**: a decoder can turn “read A” into “read B”, both within "
        "policy. The record keeps \"this principal emitted admissible action Y\" and loses \"the model meant X\": "
        "ADR-0020's concession from a second direction.",
        "**Reader scope correction reversed in effect** by ADR-0037 §3 (C3): the Reader is a stage, not a seat, with no "
        "Persona; two bullets struck (B12). The split itself stands.",
        "Open: decoder–alphabet compatibility across floor changes (G7 item 17).",
    ], "teal", size=14)
    y += max(t1h, rh) + 40

    y += _row_cards(c, X0, y, W, 30, [
        ("ADR-0019 · Decode observability is narrow", [
            "`decode_observability: topk_logprobs`, rung-gated, for **decoding attestation, not introspection**. "
            "`none` is the only unconditional value (ADR-0016 §9).",
            "**Decoding conformance**: sampled token + distribution + declared parameters is a decidable predicate, the "
            "only new admitting check. Since ADR-0037 §3 it may admit **only where inference is attested** (rung 3, "
            "T-0045-21, T-0045-26: no theorem cites them yet).",
            "**Substitution detection**: distributional drift catches an undeclared model change. A threshold on drift "
            "is semantic: deny-only.",
            "Top-k, not full logits; not in round topics (cognitive payload; storage is ADR-0006's question). **Never "
            "cited for any claim about `L`.**",
        ], "violet", {}),
        ("ADR-0020 · Replay reconstructs what crossed the membrane", [
            "The replayable record: actions attempted **including denied ones**, effects emitted, lease and epoch "
            "transitions, the Persona binding in force.",
            "Scratchpads, chains of thought and token traces are out of scope and not written to round topics.",
            "**The Observer and replay read the same stream**, so `L` is not measured against hindsight.",
            "**The cost**: root-cause analysis establishes what a principal did, never why. Revisit triggers: a demand "
            "to attribute intent; a detection strategy needing pre-effect cognitive signal; ADR-0013's forensic floor.",
        ], "grey", {}),
        ("ADR-0017 · The archetype admits only in-house pre-trained Personas", [
            "**Two independent lineages** at the archetype, with separate corpora and architecture ancestry: a single "
            "lineage reproduces the monoculture blind spot inside the rung meant to sacrifice nothing.",
            "**External model implies `Mediated`**: prompt egress is an out-of-band effect, so effect exclusivity is "
            "false by construction (derived, not asserted).",
            "**Ratified with its criterion outstanding**: until a decidable or auditable independence criterion exists, "
            "the archetype may be described but **no deployment may be declared at archetype rung**. ADR-0035 writes "
            "it, and is Proposed (G7 item 20).",
        ], "blue", {}),
    ]) + 24
    pw = 1500
    pth = c.table(X0, y, [("Provenance rung (ADR-0017)", 300, {"bold": True}), ("Provenance", 760),
                          ("Principal class", pw - 1060)], [
        ["Archetype", "In-house pre-train, two independent lineages", "`Contained`"],
        ["1", "In-house fine-tune on external base", "`Contained`, with a lineage debt stated"],
        ["2", "Attested external: provider signs a version statement", "`Mediated`"],
        ["3", "Asserted external: endpoint and version string only", "`Mediated`"],
    ], size=14, accent="blue")
    c.card(X0 + pw + 30, y, W - pw - 30, "This table's ordering is no longer the deployment axis", [
        "**Ordering-primacy reversed in effect** by ADR-0023 §5 (C3): rungs are per-axis, and provenance is one axis "
        "among many. The admission clause stands; **the superseding record is unwritten** (G7 items 6, 50).",
        "Numbers here ascend with **weakness** and the archetype is unnumbered; confinement rungs ascend with strength. "
        "Always qualify \"rung\" (ToO §8.2).",
        "ADR-0035 adds a second route to rung 1: **distillation**, in-house weights on generated content (finding 2).",
    ], "amber", size=14, h=pth)
    y += pth + 60

    # ======================================================================== ADR-0035 (Proposed)
    ptop = y
    py = ptop + 40
    c.status(X0 + 30, py, "proposed", "2026.09.25, revised R1–R4; not in force; R2's bound marked for "
             "independent review (G7 item 33)")
    py += 44
    py += c.heading(X0 + 30, py, "Lineage is projected from the Build log, never authored (§1, §2)", "amber", 19)
    # the DAG
    dag_y = py + 10
    ext_w = 430
    ext = [
        ("External object: a synthetic corpus", ["Content **generated by** a model, e.g. TinyStories (GPT-3.5, GPT-4). "
                                                 "`generatedBy` declared at corpus admission."]),
        ("External object: a filtered crawl", ["Content **selected by** a model, e.g. FineWeb-Edu (a classifier trained "
                                               "on Llama-3-70B-Instruct annotations). `curatedBy` declared at admission."]),
    ]
    eh = max(c.card(0, 0, ext_w, t, b, "grey", draw=False, size=13.5, bullets=False) for t, b in ext)
    for i, (t, b) in enumerate(ext):
        c.card(X0 + 30, dag_y + i * (eh + 24), ext_w, t, b, "grey", size=13.5, bullets=False, h=eh)
    rounds = ["Corpus preparation", "Tokenizer training", "Pre-tokenisation", "Pre-training", "Fine-tuning"]
    rx0 = X0 + 30 + ext_w + 90
    persona_w = 300
    rgap = 46
    rwid = (X1 - 30 - persona_w - 70 - rx0 - rgap * (len(rounds) - 1)) / len(rounds)
    rbody = {
        "Corpus preparation": ["A Build round. `ingress` ⊇ `consumed`."],
        "Tokenizer training": ["Produces the `tokenizer` digest."],
        "Pre-tokenisation": ["Reads shards into the workspace."],
        "Pre-training": ["`root`: the from-scratch init. `trainer`: tool, config, seed. `family`: **declared** tag."],
        "Fine-tuning": ["`parents` names the weights it consumed (E1 sees it)."],
    }
    rh = max(c.card(0, 0, rwid, r, rbody[r], "amber", draw=False, size=13.5, bullets=False) for r in rounds)
    ry0 = dag_y + 20
    for i, r in enumerate(rounds):
        x = rx0 + i * (rwid + rgap)
        c.card(x, ry0, rwid, r, rbody[r], "amber", size=13.5, bullets=False, h=rh)
        c.pill(x + 10, ry0 + rh + 10, "its lease's rung", "violet", 11.5)
        if i:
            c.arrow([(x - rgap, ry0 + rh / 2), (x, ry0 + rh / 2)], "amber", sw=2.2)
    px = X1 - 30 - persona_w
    c.card(px, ry0, persona_w, "Persona weights", ["Provenance field = digest of the projected lineage record."],
           "teal", size=13.5, bullets=False, h=rh)
    c.arrow([(rx0 + 4 * (rwid + rgap) + rwid, ry0 + rh / 2), (px, ry0 + rh / 2)], "teal", sw=2.2)
    c.arrow([(X0 + 30 + ext_w, dag_y + eh / 2), (rx0 - 40, dag_y + eh / 2), (rx0 - 40, ry0 + rh / 2 - 10),
             (rx0, ry0 + rh / 2 - 10)], "grey", label="Read", lpos=0.62)
    c.arrow([(X0 + 30 + ext_w, dag_y + eh + 24 + eh / 2), (rx0 - 40, dag_y + eh + 24 + eh / 2),
             (rx0 - 40, ry0 + rh / 2 + 10), (rx0, ry0 + rh / 2 + 10)], "grey", label="Read", lpos=0.62)
    dag_bottom = max(dag_y + 2 * eh + 24, ry0 + rh + 40)
    c.para(rx0, ry0 + rh + 46, X1 - 30 - rx0,
           "**`rung`** = the lowest confinement rung over every round in the DAG: **a lineage is only as strong as its "
           "weakest round**. A round is **ingress-bounded** only at rung ≥ 1 on an Attested verdict under a profile "
           "meeting ADR-0034 P1 and P2, with every tool it invokes inside the guest (R1, R4); any other round makes the "
           "whole record **declared** (D-0035-1). Until ADR-0034 is in force for such rounds, every lineage is declared.",
           14, "ink")
    py = max(dag_bottom, ry0 + rh + 46 + 90) + 30

    w2 = (W - 60 - 30) / 2
    fields = [
        ["`root`", "Digest of the from-scratch initialisation", "`Invoke` inputs of the pre-training round", "Projected"],
        ["`parents`", "Records of the artifacts the round consumed", "Artifacts `Read` into the workspace", "Projected"],
        ["`ingress`", "Objects the round **could** read", "Corpus root in force for the round's admits, plus parents' "
         "`ingress`", "Projected, **over-approximated**"],
        ["`consumed`", "Objects the round **did** read (R2)", "`ingress` objects `Read`, plus authored drafts, plus "
         "parents' `consumed`", "Projected, **never over-approximated**"],
        ["`generatedBy`", "Models whose outputs are in `ingress`, with shares", "Parents; for external objects, the "
         "admission declaration", "Projected, or declared at admission"],
        ["`curatedBy`", "Models that selected or filtered `ingress`", "The same", "Projected, or declared at admission"],
        ["`tokenizer`", "Tokenizer digest", "A parent artifact", "Projected"],
        ["`family`", "Architecture family tag (`decoder-transformer`, `ssm`, `rwkv`)", "Trainer configuration",
         "**Declared** (code digest projected)"],
        ["`trainer`", "Tool digest, configuration digest, seed", "The `Invoke` admit (I13)", "Projected"],
        ["`rung`", "Lowest confinement rung over the DAG", "The rounds' leases (ADR-0031)", "Projected"],
    ]
    fth = c.table(X0 + 30, py, [("Field (§1)", 190, {"bold": True}), ("Content", 400), ("Source", 450),
                                ("Strength", w2 - 1040)], fields, size=13.5, accent="amber")
    ex = [
        ["**E1** Weights", "`root(A) ≠ root(B)`, and neither DAG contains the other's weights as a parent",
         "Fine-tunes, merges, **every pair of versions of one lineage**"],
        ["**E2** Generators", "No model in both `generatedBy` sets; neither lineage's generators include a model of the "
         "other", "A common teacher; one distilled from the other"],
        ["**E3** Corpus overlap", "Exact overlap over `ingress`, as a share of the smaller `consumed` set, ≤ θ_exact; "
         "near-duplicate overlap by a pinned gate tool ≤ θ_near. Both upper bounds", "**The overlapping-corpora case** "
         "ADR-0017 names"],
        ["**E4** Architecture", "Different `family` tags and different tokenizer digests", "The same design trained twice"],
        ["**E5** Curators", "No model in both `curatedBy` sets", "Two corpora selected by the same classifier"],
        {"cells": ["**Distillation**", "Known-generated bytes in `ingress` > θ_gen of `consumed`: a distillation of its "
                   "generator. Provenance rung 1, still `Contained`, never the archetype", "Content lineage from an "
                   "external model"], "accent": "amber"},
    ]
    c.table(X0 + 30 + w2 + 30, py, [("Clause (§3)", 200), ("Independent only if", w2 - 200 - 330),
                                    ("Rejects", 330)], ex, size=13.5, accent="amber")
    eth = c.table(0, 0, [("Clause (§3)", 200), ("Independent only if", w2 - 200 - 330), ("Rejects", 330)], ex,
                  size=13.5, draw=False)
    py += max(fth, eth) + 14
    py += c.para(X0 + 30, py, W - 60, "The rehearsal's record, `topak.lineage/0` (`slm/lineage/record.py`), carries these "
                 "ten fields and adds `weight_ancestry`, `ingress_bytes`, `consumed_bytes`, `generated_share`, "
                 "`generated_bytes`, `trainer = {tool, config, seed}` and a `strength` of `projected` or `declared`, "
                 "which drops to declared at rung 0 or under a declared parent (inventory §1.7, §8).", 13.5, "muted") + 24

    py += _row_cards(c, X0 + 30, py, W - 60, 24, [
        ("§2 · Every share is an upper bound (R2)", [
            "**Ingress enters only numerators**; the denominator is the smaller `consumed` set. Adding ingress can turn a "
            "pass into a fail, never a fail into a pass.",
            "As first drafted the shares were of ingress and the claim was false: 13 of 2,000 E3 fails and 241 of "
            "2,000 distillation fails turned into passes by adding ingress (finding 5).",
            "The relation is symmetric, irreflexive and **not transitive**: every seat pair is checked on its own.",
        ], "amber", {}),
        ("§3 · θ are policy-floor values, not yet set", [
            "θ_exact, θ_near, θ_gen, β and the near-duplicate tool's digest live in `floor/genesis-values.json` "
            "(R3) and are **`null`**: the independence table is not computed while any is null.",
            "Relaxing one is an issuance and a promotion; tightening, an ordinary promotion.",
            "Set from measurements at training scale, not before (G7 item 30). Gate tools would be trust root T-0045-15, "
            "cited by no theorem until ratification.",
            "**Three field sets, not one**: the floor's `lineage` block has θ_exact, θ_near, θ_gen, β and `near_tool`; "
            "the rehearsal's `slm/lineage/thresholds.example.json` has the three θ, byte thresholds and a "
            "`granularity`, no β, and non-null numbers marked PLACEHOLDER; the gate suite hard-codes a third "
            "(inventory finding 15).",
        ], "violet", {"status": "draft", "status_extra": "values file"}),
        ("§4, §5 · Computed at the gate; enforced where refusal stalls", [
            "The gate recomputes each record from the log, checks the authored manifest (**divergence = Contested**, "
            "attributed), evaluates E1–E5, and emits an **independence table**, a promoted artifact. The admit path only "
            "looks up a pair of digests.",
            "**At the promotion tally (Build)**: at least one veto seat leased with a Persona independent of the "
            "author's, or the promotion stalls.",
            "**At the deployment declaration**: archetype provenance only if every (Thinker, Observer) pair is in the "
            "table as projected.",
            "**Never at grant**: refusing an Observer's lease leaves an empty seat, which vetoes nothing and adds "
            "authority to the author. Run has no tally: declaration only.",
        ], "blue", {}),
        ("§6, §7 · What only subtracts, and what is outside", [
            "**Correlated-miss test**: a pair fails when its joint miss rate exceeds β times the product of individual "
            "rates; a failure removes the pair; **a pass grants nothing**.",
            "**Declared residuals**: unlabeled model text in crawls; shared human feedback (no `feedback` field); shared "
            "priors below dedup granularity; a shared training stack (MLX on Apple silicon); reading more than is "
            "trained on (padding).",
            "Structural independence does not imply uncorrelated failures; detection carries no safety theorem.",
        ], "red", {}),
    ]) + 30

    dw = W - 60
    py += c.table(X0 + 30, py, [("Id (§9)", 150, {"bold": True}), ("Parameter → deployed value", 760),
                                ("Premises falsified", 260), ("Voided", dw - 150 - 760 - 260 - 330),
                                ("Type changes", 330)], [
        ["D-0035-1", "Lineage strength: projected → declared (a rung-0 round in the DAG, an external base, an unbounded "
         "ingress, or an empty consumed set)", "§2's bound", "**No theorem**: detection carries none. Voids the ability "
         "to declare archetype provenance. The tally condition is still checked, but met by declared entries resting on "
         "the author's claim", "None: no participant changes type"],
    ], size=13.5, accent="amber") + 36

    # rehearsal
    py += c.heading(X0 + 30, py, "The rehearsal (§8; ToO §16; `slm/`): evidence for the pipeline and the thresholds, not "
                                 "for the guarantee", "amber", 18)
    rw1 = 1400
    rth = c.table(X0 + 30, py, [("Pair", 170, {"bold": True}), ("Lineages", 900), ("Expected", rw1 - 1070)], [
        ["Pass", "L-A: Llama-style, FineWeb-Edu slice, own 16k BPE · L-B: SSM or RWKV, a non-web, non-synthetic corpus "
         "such as public-domain books, own tokenizer", "Independent (E1–E5 hold)"],
        ["E1", "L-A and L-A′, a fine-tune of L-A", "Fail"],
        ["E3", "L-A and L-C: an unfiltered FineWeb slice, of which FineWeb-Edu is a subset", "Fail: the overlapping-corpora "
         "case on real data"],
        ["E4", "L-A and L-D: Llama-style on the books corpus", "Fail on E4 alone, while E3 passes"],
        ["E2", "Two lineages on synthetic sets that name a common generator", "Fail"],
        ["Distillation", "L-T on TinyStories", "Provenance rung 1 (content from GPT-3.5 and GPT-4)"],
        ["E5", "Two lineages on corpora filtered by the same classifier", "Fail"],
    ], size=13.5, accent="amber")
    found = [
        "**The gate suite passes**: every clause fires alone at least once; the relation is irreflexive, symmetric, not "
        "transitive; E3 fails closed without a measurement or with an unpinned tool; strength is weakest-link.",
        "**Overlap separates the cases by orders of magnitude, as shares**: FineWeb-Edu inside a FineWeb slice 1.0000; two "
        "dumps of one filtered crawl 0.002; filtered web against books 0. Measured at 20 MB: too small to set θ.",
        "**A lineage was projected from the reference's log** and matched its manifest; three tampered manifests (an "
        "omitted object, a changed seed, an injected draft) were each **Contested**, attributed to seat, lease and log "
        "slot. Rerun 09.28 with the same verdicts. The records are **declared**: the trainer runs outside the guest.",
        "**The soundness claim was false, and the repair is a bound**: holds over 2,000 trials; padding measured at 24 "
        "of 2,000 (E3) and 250 of 2,000 (distillation), declared as a residual.",
        "**Not shown**: that θ is right, that the near tool is right, that independent lineages fail independently, or "
        "that the bound is how anyone else measures overlap.",
    ]
    c.card(X0 + 30 + rw1 + 30, py, W - 60 - rw1 - 30, "What the rehearsal found (ToO §16)", found, "amber", size=13.5,
           h=max(rth, c.card(0, 0, W - 60 - rw1 - 30, "What the rehearsal found (ToO §16)", found, "amber", size=13.5,
                                 draw=False)))
    fh = c.card(0, 0, W - 60 - rw1 - 30, "What the rehearsal found (ToO §16)", found, "amber", size=13.5, draw=False)
    py += max(rth, fh) + 30
    c.region(X0, ptop, W, py - ptop, "ADR-0035 · Persona lineage is a projection of the Build log, and independence is "
                                     "an exclusion rule over it", "amber", dash="10 6", sw=2.4, size=15)
    return c
