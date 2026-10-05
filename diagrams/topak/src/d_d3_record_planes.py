"""D3 — The record planes: log, transport, archive, plaintext store."""
import re

import lib
from lib import Canvas

ID, SLUG = "D3", "record-planes"

W = 3400

STORES = [
    ("Paxos log", "violet", "built", "3 replicas, WAL",
     "**The ordering authority and the causal frame** (ADR-0015; ADR-0005). Every effect has a consensus-ordered, "
     "signed, authorizing predecessor here; the log index is the fence. **Neither the topic nor the emission is the "
     "record; the log is** (ToO §4.4). No snapshots or compaction at the reference (G14)."),
    ("Kafka round topics", "amber", "accepted", "ADR-0005 · C4 · Batch 27 · built at reference",
     "**Transport with a durability window** (`acks=all`), neither ordering authority nor system of record "
     "(ADR-0005 §1, **ratified 2026.10.04** at R2). One single-partition topic per principal per epoch or round, "
     "sealed, per-topic ACL, per-use retention, **the unit of erasure** (ADR-0003). The debt ADR-0033 §2's K row "
     "carried since Batch 7 is discharged (G10 §1, item 5)."),
    ("Archive", "blue", "notbuilt", "T-0045-7 · register G9",
     "**The system of record** (ADR-0005 §1, Accepted; ADR-0004, Accepted, is scoped to it). Fed by its own ETL per use "
     "case; **not a tier of the topic**: read under its own authority, it neither extends a topic's life nor survives "
     "its erasure (ADR-0003 A3). The reference writes `archive.jsonl` per replica, a projection of the log, which is "
     "**not** this archive (register G9)."),
    ("Separately governed plaintext store", "brown", "notbuilt", "ADR-0004 is Accepted",
     "**Plaintext lives in a store built for deletion** (ADR-0004). Its readers are where the replay-harness "
     "attestation requirement attaches; the pointer to it is itself a disclosure (demand type 5, declined)."),
]

FACTS = [
    ["Every `Entry`, **fourteen kinds** at the rebuilt reference: `Grant`, `Renew`, `Admit`, `EndRound`, `Revoke`, "
     "`EpochIncrement`, `Contested`, `ProfileRegister`, `Issue`, `GatesPassed`; since 2026.10.05 an operator's "
     "signed `Control`, `EmergencySeating` (BOOTSTRAP) and `Activate`; and `BreakGlassApprove`, **retired and refused "
     "at apply** (`state.rs`). Each carries an `id` `n<replica>-<boot>-<counter>`, so a re-proposal applies once.",
     "Admits are **F1**; a vote's admit is **F3**; stops are **F2**, an operator's three denies among them; issuances "
     "**F4**; an activation and an emergency seat's calls **F5**; erasure events would be **F6** (unbuilt).",
     "A `Consult` admit carries the item's label and delivery mode; an `Actuate` admit its label facts "
     "(ADR-0042 A1; ADR-0047 §4).",
     "**Denials are not here**: a denial changes no state, so it is never proposed."],
    ["Every record's envelope: kind, seat, fence, the authorizing **admit index**, the per-lease **sequence number**, "
     "the payload digest (headers `topak-*`).",
     "**The opening record first**: the tool list, written by the mechanism at grant, with no admit and no sequence "
     "number (ADR-0048 §2; ADR-0042 A1). Then the `Actuate` record of ADR-0042 §3, now with four label fields; "
     "heartbeats; denial records (no admit, no sequence, with `at` and `decided_by`) while the round is open; on an "
     "operator's topic, its **control records**; the **seal marker**.",
     "Written only after the admit commits; denials unordered, by the deciding replica."],
    ["The control-plane record keeps a **hash and a pointer** for every cognitive payload (ADR-0004).",
     "Trace conformance needs actions, identities and ordering, not prompt text: the archive holds what replay and "
     "conformance need (ADR-0004 Context).",
     "Six forensic classes are non-erasable here for the declared horizon (ADR-0028)."],
    ["None: the store holds payloads only.",
     "Its entries are reached by the archive's pointers, and erased by deleting them (ADR-0006)."],
]

PAYLOADS = [
    ["**None.** A payload appears only as a digest: `Draft` content, `Emit`/`Report` records, `Invoke`/`Actuate` "
     "inputs, the frozen input (`Admitted`, `state.rs`)."],
    ["`Emit` and `Report` bodies; an `Actuate` record's inputs and result themselves, **in full whatever was "
     "delivered to the principal**, under the topic's ACL and in the round's unit of erasure (ADR-0042 §3, A1; "
     "ADR-0047 §5). The tool list in the opening record's payload, and a task's bytes, at the reference in the same record "
     "(ADR-0048 §2; ADR-0050 §5; ToO §7.10).",
     "A vote's emission carries the vote and a **hash-and-pointer** to its commentary, not the commentary (ToO §4.4).",
     "Cognitive intermediate state (scratchpads, chains of thought) is **never written** to round topics (ADR-0020)."],
    ["None in plaintext: a hash and a pointer per payload."],
    ["Prompts, reasoning, review commentary: **all erasable**. No cognitive payload is in the forensic floor "
     "(ADR-0028 §1)."],
]


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


def _build():
    c = Canvas(ID, "The record planes: what is ordered, what is carried, what is kept, what is erased",
               "Four stores hold the record. The Paxos log orders; Kafka carries, as transport only (ADR-0005, ratified "
               "Batch 27); the archive is the system of record; a separately governed store holds plaintext so it can be "
               "destroyed. A round's topic opens with the tool list, and its `Actuate` records carry labels. Across all four runs the plane "
               "boundary (B5): control-plane facts cross and survive, cognitive payloads are reduced to a hash and a "
               "pointer.",
               W, "ToO rev 14 §2.10, §4.1–§4.4, §5.1, §7.10, §15; ADR-0003 (0003.1–0003.7, A1, A2, A3); ADR-0004; "
               "ADR-0005 §1–§7 (B27); ADR-0006; ADR-0015; ADR-0020; ADR-0021 §3, §4, §7; ADR-0028 §1–§4; ADR-0033 §2, B27; "
               "ADR-0035 R5, R6 (Proposed); ADR-0038 §2; ADR-0042 §2–§5, A1, A2; ADR-0043 §4 A1; ADR-0047 §2, §4, §5; "
               "ADR-0048 §2; ADR-0050 §5, §6; ADR-0051 §5 (Proposed); ADR-0052 §4, §5; G10 §1, §2.4, §2.5, §7 items 5, "
               "46, 60; mechanism/crates/topak-transport/src/lib.rs (`EmitRecord`, `RecordKind`, headers); "
               "topak-core/src/lift.rs (`topic_name`, `after_topic_name`); topak-core/src/state.rs (`Entry`, `Admitted`, "
               "`EndReason`); topak-node/src/mechanism.rs (`record_denial`, `record_control`, `open_round`, "
               "`InFlight::record`, `apply_committed`); git diff 7075169..HEAD of those files; GAPS-AND-ASSUMPTIONS G9, "
               "G14, G15, G17, I23, I44, I45; boundary register B5, B9; derived/topak-format-and-schema-inventory-"
               "2026.10.03.md §4.6, §5.1, findings 13, 14")
    X0, X1 = c.x0, c.x1
    y = c.y
    gap = 170
    n = len(STORES)
    cw = (X1 - X0 - gap * (n - 1)) / n
    pad = 22
    iw = cw - 2 * pad

    # measure rows
    hdr_h = max(c.card(0, 0, iw, s[0], [s[4]], accent=s[1], status=s[2], status_extra=s[3], draw=False,
                       bullets=False, size=14, tsize=20) for s in STORES)
    fact_h = max(c.card(0, 0, iw, "Control-plane facts", f, accent="blue", draw=False, size=14) for f in FACTS)
    pay_h = max(c.card(0, 0, iw, "Cognitive payloads", p, accent="pink", draw=False, size=14) for p in PAYLOADS)
    top = y + 20
    fy = top + 34 + hdr_h + 30
    py = fy + fact_h + 64
    bot = py + pay_h + 30
    for i, (name, acc, st, sx, desc) in enumerate(STORES):
        x = X0 + i * (cw + gap)
        c.card(x + pad, top + 34, iw, name, [desc], accent=acc, status=st, status_extra=sx, h=hdr_h, bullets=False,
               size=14, tsize=20)
        c.card(x + pad, fy, iw, "Control-plane facts", FACTS[i], accent="blue", h=fact_h, size=14, tint=False)
        c.card(x + pad, py, iw, "Cognitive payloads", PAYLOADS[i], accent="pink", h=pay_h, size=14, tint=False,
               dash="6 4")
        dash = "2 3" if st == "notbuilt" else ("10 6" if st == "proposed" else None)
        c.region(x, top, cw, bot - top, {"violet": "P · the log", "amber": "K · transport",
                                         "blue": "the archive", "brown": "plaintext store"}[acc], acc,
                 dash=dash, size=15)
    # plane boundary
    by = fy + fact_h + 32
    c.line(X0 - 10, by, X1 + 10, by, "red", sw=2.4, dash="12 6")
    c.label(X0 + 330, by, "B5 plane boundary · facts cross and survive; payloads are reduced to hash + pointer",
            "red", 14)
    # flow arrows between stores (in the header row)
    ay = top + 34 + hdr_h - 30
    for i, lab in enumerate(["emission after commit:\nadmit index, fence, seq", "ETL per use case\n(not built)",
                             "hash + pointer\n(not built)"]):
        xa = X0 + i * (cw + gap) + cw - pad
        xb = X0 + (i + 1) * (cw + gap) + pad
        c.arrow([(xa, ay), (xb, ay)], ["violet", "amber", "blue"][i], sw=2.4,
                dash=None if i == 0 else "2 3")
        c.label((xa + xb) / 2, ay - 44, lab, ["violet", "amber", "blue"][i], 12.5)
    y = bot + 70

    # ---- the round topic: anatomy and lifecycle
    c.text(X0, y + 22, "One round topic, from open to erased (ADR-0003; ADR-0021; ADR-0042 §5)", 22, "amber", bold=True)
    y += 44
    lw = 1900
    c.para(X0, y, lw, "Identity: `topak.<chain>.<domain>.<seat>.e<epoch>.r<round>`. The **rules-epoch chain** is part "
           "of the name (ADR-0003 A1): re-genesis restarts epochs and rounds at zero, and two development resets once "
           "wrote into the same Kafka topic (finding 4). A sealed topic is never written again.", 14.5, "muted")
    y += 62
    stages = [
        ("Open", "amber", ["**Opens with the tool list**: the mechanism's opening record, written at grant before "
                           "the session exists; no admit, no `seq`, outside every watermark (ADR-0048 §2).",
                           "Admitted emissions at `seq` 1, 2, …; `Actuate` records; heartbeats.",
                           "Denials while open, unordered."]),
        ("Sealed", "amber", ["**Run**: when the lease ends: expiry, operator end, epoch fence, targeted revocation, a "
                             "new rules epoch; **not** on renewal (ADR-0042 §5).",
                             "**Build**: at gate submission, the principal's topic set (ADR-0021 §3).",
                             "In-flight `Actuate` calls written `unknown` ahead of the seal marker."]),
        ("`after` companion", "red", ["Denials under the round's lease once its topic is sealed; never an emission.",
                                      "Bounded: `after_topic_limit` (dev 64) **per deciding replica**, since the counter is not "
                                      "replicated (I23), then **one overflow marker**.",
                                      "ADR-0003 A2 · confirmation-required C1."]),
        ("Retained", "blue", ["**Run**: Run's horizon. **Build**: the production lifetime of any artifact promoted "
                              "from the round (ADR-0021 §7).",
                              "One store for the whole retention: no tiered storage (0003.7, scoped by A3)."]),
        ("Erased whole", "red", ["Erasure drops the sealed topic **and** its `after` companion, and the plaintext-store "
                                 "entries (ADR-0006). No signature or hash chain is edited.",
                                 "**Not built**; genesis issues no erasure roster, so `X2-erasure` admits nothing."]),
    ]
    sgap = 54
    sw = (lw - sgap * (len(stages) - 1)) / len(stages)
    sh = max(c.card(0, 0, sw, t, b, accent=a, draw=False, size=13.5) for t, a, b in stages)
    for i, (t, a, b) in enumerate(stages):
        x = X0 + i * (sw + sgap)
        dash = "6 4" if i in (2, 4) else None
        c.card(x, y, sw, t, b, accent=a, h=sh, size=13.5, dash=dash, tint=i != 4)
        if i:
            c.arrow([(x - sgap, y + 40), (x, y + 40)], "amber" if i < 3 else "red", sw=2.2,
                    dash="7 5" if i == 4 else None)
    c.status(X0 + 4 * (sw + sgap) + sw - 8, y - 30, "notbuilt", anchor="end")
    c.status(X0 + 2 * (sw + sgap) + sw - 8, y - 30, "accepted", "C1", anchor="end")
    y += sh + 40

    # record envelope table (EmitRecord) and Actuate record table (ADR-0042 §3)
    t1w = (lw - 40) / 2
    c.text(X0, y + 19, "What every topic record carries (`EmitRecord`)", 19, "amber", bold=True)
    c.text(X0 + t1w + 40, y + 19, "The `Actuate` record (ADR-0042 §3, with A1 and A2)", 19, "amber", bold=True)
    c.status(X0 + t1w + 40 + 520, y + 2, "accepted", "C4 · A1, A2 at Batch 34")
    y += 34
    h1 = c.table(X0, y, [("Field", t1w * 0.24, {"mono": True}), ("What it is", t1w * 0.76)], [
        ["topic", "The round topic, or its `.after` companion"],
        ["seat", "The principal's seat"],
        ["fence", "The lease's fence (log index of its grant)"],
        ["kind", "`open` (the opening record), `emit` (an admitted `Emit` or `Report`), `actuate`, `control` (an "
                 "operator's ordered request, on its own topic), `deny` or `overflow`. The seal is a marker record "
                 "with a `topak-seal` header whose reason is in Rust's Debug form (`Submitted`), not the serde form "
                 "(`submitted`) every other surface uses (inventory finding 14)"],
        ["admit", "Log index of the authorizing `Admit`, or of the ordered `Control`; **none for a denial or the "
                  "opening record**"],
        ["seq", "Per-round sequence: emissions in Build, effect-bearing admits in Run (ADR-0042 §2); none for a "
                "denial, a control record or the opening record"],
        ["digest", "Digest of the payload in canonical JSON. **The Kafka value itself is not canonical** "
                   "(`serde_json::to_vec`), so a reader re-canonicalizes to check it (inventory finding 13)"],
        ["payload", "The record itself: cognitive payload for an emission; for a denial `{denied, reason, epoch, "
                    "round, at, decided_by}` with content as digests; for the overflow marker `{overflow, limit, "
                    "epoch, round, at, decided_by}`; for the opening record `{tool_list, task}`; for a control record "
                    "`{control, sig, facts}`"],
    ], size=13.5, accent="amber")
    # the opening record (ADR-0048 §2; ADR-0042 A1), under the EmitRecord table
    oy = y + h1 + 40
    c.text(X0, oy + 19, "The round's opening record (ADR-0048 §2; ADR-0042 A1)", 19, "amber", bold=True)
    oy += 34
    h1 += 74 + c.table(X0, oy, [("Field", t1w * 0.24, {"mono": True}), ("What it is", t1w * 0.76)], [
        ["kind", "`open`: written by the mechanism at grant, before the session exists, so nothing the principal does "
                 "precedes it. The principal cannot write it. If it cannot be written, no session is opened (I45)"],
        ["admit, seq", "**None**: it is not an effect, so it has no sequence number and is **outside what a watermark "
                       "covers**; the mark does not assert it was read (ADR-0043 §4 A1)"],
        ["digest", "Digest of the rendered tool list; the bundle revision is in the list (ADR-0042 A1)"],
        ["payload", "The list itself: the interface of every entry of the lease's revision the lease may call, in the "
                    "mechanism's fixed form; and the round's task where the grant carried one (ADR-0050 §5). A renewal "
                    "writes none: the bundle is fixed across renewal (ADR-0031 R2)"],
    ], size=13.5, accent="amber")
    h2 = c.table(X0 + t1w + 40, y, [("Field", t1w * 0.2, {"mono": True}), ("What it is", t1w * 0.55),
                                    ("Plane", t1w * 0.25)], [
        ["seat, fence", "The principal's seat and the lease's fence", "Control plane"],
        ["admit", "The log index at which the admit committed", "Control plane"],
        ["seq", "The sequence number of §2", "Control plane"],
        ["tool", "Name and digest of the allowlist entry", "Control plane"],
        {"cells": ["breakGlass", "Was: whether the admit was under X1. **Replaced by `seatKind`** (A2): with X1 retired "
                   "no admit is under it", "—"], "accent": "grey"},
        {"cells": ["seatKind", "The kind of the seat that made the call; a call by an `emergency` seat is what a reader "
                   "looks for where it looked for `breakGlass`. The activation is the F5 record (ADR-0042 A2; "
                   "provisional with ADR-0052)", "Control plane"], "accent": "blue"},
        ["inputs", "Digest of the inputs", "Control plane"],
        ["outcome", "`returned`, `failed` or `unknown`", "Control plane"],
        ["result", "Digest of what the tool returned, when it returned", "Control plane"],
        {"cells": ["inputLabels", "The label of each input that is a handle (A1; ADR-0047 §5)", "Control plane"],
         "accent": "teal"},
        {"cells": ["resultLabel", "The result's label after the join of ADR-0047 §1", "Control plane"],
         "accent": "teal"},
        {"cells": ["delivery", "`clear` or `handle`: how the result reached the principal", "Control plane"],
         "accent": "teal"},
        {"cells": ["clearSet", "The labels of everything delivered clear to the principal in the round, as it stood "
                   "when the call was admitted (ADR-0047 §4)", "Control plane"], "accent": "teal"},
        {"cells": ["channel", "`{kind, target}` a hosted Wasm tool was held to: its entry's declaration in the lease's "
                   "revision. **Reference only**: not a field of ADR-0042 §3 (I44)", "Control plane"],
         "accent": "amber"},
        {"cells": ["payload", "The inputs and the result themselves, **in full whatever `delivery` says**: suppressed "
                   "to the Thinker is not suppressed to the Observer (ADR-0047 §5)", "**Cognitive payload**"],
         "accent": "pink"},
    ], size=13.5, accent="amber")
    y += max(h1, h2) + 50

    # ADR-0003 clause table, in full
    c.text(X0, y + 19, "ADR-0003, clause by clause (clause annotation C1, with A1–A3)", 19, "amber", bold=True)
    c.status(X0 + 600, y + 2, "accepted", "C1 for A2 only")
    y += 34
    cols = [("Clause", lw * 0.1, {"bold": True}), ("Content", lw * 0.36), ("Supersedable alone?", lw * 0.13),
            ("Note", lw * 0.41)]
    y += c.table(X0, y, cols, [
        ["0003.1", "Topic per principal per epoch/round", "No", "Core; 0003.2 and 0003.3 have no meaning without it"],
        {"cells": ["A1", "A topic is identified by its rules-epoch chain as well as by principal and epoch/round",
                   "—", "Ratified 2026.09.25 (Batch 5); not confirmation-required. Finding 4"], "accent": "blue"},
        ["0003.2", "Sealed on emit completion", "No", "Core; defines the unit of erasure"],
        {"cells": ["A2", "One companion topic, `after`, for denials after the seal: never an emission, same ACL and "
                   "retention, dropped with the round; bounded, with a marker", "—",
                   "Ratified 2026.09.25 (Batch 5); **confirmation-required C1**. Finding 11"], "accent": "red"},
        ["0003.3", "Per-topic ACL model", "No", "Follows from 0003.1"],
        ["0003.4", "Retention scoping", "**Yes**", "Entangled with the open raw-emission retention question (0003 vs "
                                                   "0006). Likely first to be superseded"],
        ["0003.5", "Replay authorization", "**Yes**", "Overlaps ADR-0020: authorization **to** replay and the scope **of** "
                                                      "replay are different decisions"],
        ["0003.6", "Wrapper-Rego masking", "**Yes**", "Confirmed independently supersedable. **Not built** at the "
                                                      "reference"],
        ["0003.7", "No tiered storage", "**Yes**", "Operational; a degeneracy candidate under ADR-0023"],
        {"cells": ["A3", "No tiered storage is one store for a topic's whole retention, not a retention length; the "
                   "archive is not a tier", "—", "Ratified 2026.09.30 (Batch 17) as a scoping, not a reversal"],
         "accent": "blue"},
        ["(unnumbered)", "Separate read-only principals for audit; archive is its own ETL per use case", "—",
         "Carry no clause number (S3-2)"],
    ], size=13.5, accent="amber") + 50

    # ADR-0005 §1 and §2, in full (ratified Batch 27)
    c.text(X0, y + 19, "ADR-0005 §1 · Three roles, three holders", 19, "amber", bold=True)
    c.status(X0 + 430, y + 2, "accepted", "C4 · Batch 27, at R2")
    y += 34
    y += c.table(X0, y, [("Role", lw * 0.17, {"bold": True}), ("Holder", lw * 0.43), ("Not the holder", lw * 0.40)], [
        ["Ordering authority", "The Paxos log. An effect is an admit (ADR-0015), and an admit has one position in the "
         "log", "The transport. A topic's offsets order one principal's round and nothing across rounds or principals "
         "(ADR-0003)"],
        ["System of record", "The archive (ADR-0004), with its governed plaintext store and the forensic horizon",
         "The transport. Retention is per use case and a round's topic is the unit of erasure, so what it holds is not "
         "durable in the sense a record needs"],
        ["Transport", "Kafka, at the reference: durability within the window (`acks=all`), delivery to the readers in "
         "`W(p)`", "—"],
    ], size=13.5, accent="amber") + 12
    y += c.para(X0, y, lw, "The K in TOPAK names the transport role; ordering and record-keeping are not asked of it "
                "(ADR-0045 T-0045-5, delegated). **No vector clock is designed, and none is owed** (R1).", 14,
                "muted") + 30
    c.text(X0, y + 19, "ADR-0005 §2 · What orders what", 19, "amber", bold=True)
    y += 34
    y += c.table(X0, y, [("What", lw * 0.27, {"bold": True}), ("Ordered by", lw * 0.48), ("Record", lw * 0.25)], [
        ["Admits, across the system", "The log index", "ADR-0015"],
        ["A principal's effects within a round", "The sequence number, assigned when the admit is applied, so every "
         "replica assigns the same one", "ADR-0042 §2 for Run; ADR-0039 §1"],
        ["An emission on its topic", "The log index and sequence number it carries. It is written only after its admit "
         "commits, so the topic never holds an emission the log does not order", "ADR-0033 §2, K row"],
        {"cells": ["A denial on a topic", "**Nothing.** It is written by the deciding replica, unordered, while the "
                   "topic is open and to the `after` companion once it is sealed", "ADR-0020; ADR-0003 A2"],
         "accent": "red"},
        ["Intervals and deadlines", "Not the frame at all: causality orders events and bounds no interval", "ADR-0032"],
    ], size=13.5, accent="amber") + 12
    c.para(X0, y, lw, "**A reader orders a topic by the numbers its records carry, not by their offsets**: offsets are "
           "evidence of arrival only. **Denials are the remaining gap**: a sequence number on denials is open (item 44, "
           "as at G9). ADR-0051 §5 (**Proposed**) would answer it without one: a denial record's `at`, the log index the "
           "deciding replica had applied, and `decided_by`, which the reference already writes, made part of its "
           "schema.", 14, "muted")

    # ---- right column: the arguments
    rx = X0 + lw + 70
    rw = X1 - rx
    cy = bot + 70
    for title, body, acc, kw in [
        ("Where a vote actually lives (ToO §4.4)", [
            "The **authoritative vote is the admit decision in the log**, which F3 retains.",
            "The voter's round-topic emission carries the vote together with a **hash-and-pointer** to its commentary in "
            "the separately governed store; the commentary is what erasure removes.",
            "Without the split the record contradicts itself: a topic holding vote and commentary is either erasable "
            "as a unit, losing F3, or unerasable, losing the commentary's erasability.",
        ], "blue", {}),
        ("Build topics seal at `Submit` (ADR-0021)", [
            "A Build round is one pipeline invocation; each seat holds its own topic, sealed when the artifact is "
            "submitted to the gate (§3).",
            "**Every vote covers artifact digest ∧ sealed topic-set digest** (§4): voters sign provenance, not only the "
            "product.",
            "Retained for the production lifetime of any artifact promoted from the round (§7); the topic stays the unit "
            "of erasure.",
        ], "blue", {"status": "accepted", "status_extra": "C4"}),
        ("Replay reconstructs what crossed the membrane (ADR-0020)", [
            "The replayable record of a round: actions attempted, **including those denied**; effects emitted; lease and "
            "epoch transitions; the Persona binding in force.",
            "**The Observer and replay read the same stream**: no privileged channel, so detection latency `L` stays an "
            "honest number.",
            "Root-cause analysis can establish **what** a principal did, never **why**.",
        ], "pink", {"status": "accepted"}),
        ("Ordering across topics comes from the log (ToO §4.2; ADR-0005 §2)", [
            "Within-partition order gives no global timeline once there is a topic per round. An emission carries the "
            "admit's log index, the fence and a per-lease sequence number, which closes ADR-0015's one residual: "
            "effects admitted in a round and emitted at different times (G15).",
            "The quarantine-gate question **no longer gates ADR-0005** and stays open on its own account (ADR-0005 §3; "
            "ADR-0039 finding 1).",
        ], "violet", {"status": "accepted", "status_extra": "ADR-0005 · C4"}),
        ("Who reads a round topic, and what gates the read", [
            "**`W(p)`**: the principal's cell Observer and its domain's correlators (ADR-0038 §2). An Observer is "
            "given its Thinker's tool list by reading the opening record (ADR-0043 §4 A1).",
            "**Operators** read each other's topics, where every control action is written (ADR-0050 §6), and an "
            "emergency seat's topic (ADR-0052 §4): both provisional.",
            "[[red|At the reference nothing gates a read]]: the mechanism has no read path for topics, so who may read "
            "one is the transport's configuration. Operators and emergency seats add readers that nothing gates "
            "(G10 item 46; I45).",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("A lineage reads the opening record (ADR-0035 R5, R6)", [
            "**A round's tool list is `ingress` and `consumed`**: it enters both sets as the object the opening "
            "record's digest names, and, shared by every lineage under one bundle, it can only move a pair toward "
            "refusal (R6).",
            "**An item delivered as a handle is `ingress` and not `consumed`** (R5). It applies to no lineage node "
            "today: Build's `Read` is not labelled.",
            "R7: an operator's lineage is declared, rooted in its identity provider.",
        ], "amber", {"status": "proposed", "status_extra": "ADR-0035, with R4 to R7"}),
        ("Crypto-shredding: considered and rejected", [
            "It leaves a verifying envelope over unreadable ciphertext, **a hole no auditor can tell from suppression** "
            "(ADR-0003 Context; ToO §4.3).",
            "Erasure is deletion of sealed topics and of plaintext-store entries (ADR-0006).",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("The topic's costs, stated", [
            "Topic count scales with principals × rounds: broker metadata pressure needs a lifecycle story.",
            "A masking miss has a blast radius of one round. Re-genesis migration of read access is open (G17).",
        ], "grey", {}),
    ]:
        h = c.card(rx, cy, rw, title, body, accent=acc, size=14, **kw)
        cy += h + 22

    ly = c.ymax + 44
    c.legend(c.x0, ly, [
        ("box", "violet", "the log (P)"), ("box", "amber", "transport (K)"), ("box", "blue", "archive, facts"),
        ("box", "brown", "plaintext store"), ("box", "pink", "cognitive payload"),
        ("line", "red", "plane boundary B5", "12 6"), ("arrow", "amber", "not built", "2 3"),
    ])
    return c
