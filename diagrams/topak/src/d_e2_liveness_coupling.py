"""E2 — Liveness coupling: progress, not presence; the effect counter; the clock model and the timing budget."""
import re

import lib
from lib import Canvas, fill, fs, sonly

ID, SLUG = "E2", "liveness-coupling"


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
    c = Canvas(ID, "Observer liveness is progress, not presence: `live(o)`, the `K` window, and what clocks may decide",
               "ADR-0039 (Accepted (genesis) 2026.09.29, Batch 14, C4; A1 ratified Batch 20) couples Run's effect-bearing "
               "admits and Build's promotion gate to a live, keeping-up cell Observer, never to the correlator. ADR-0042 "
               "§2 makes the sequence count effects. ADR-0032 says why a local clock may be used for this and for "
               "nothing that preserves authority. Every clause subtracts; no Observer judgment enters the admit path.",
               3000, "ADR-0039 §1–§8, Options, Findings 1–4, History R1–R5, A1, B14, B20; ADR-0042 §1–§5, §7, §8 (B20; §6 "
               "Proposed); ADR-0041 §2; ADR-0032 §1–§6 (B5); ADR-0007; ADR-0024 §2; ADR-0038 §2; floor/genesis-floor.cedar "
               "R3-observer-live (DRAFT floor); floor/genesis-values.json (DRAFT, placeholders); spec/Coupling.tla, "
               "spec/RunCoupling.tla and their 2026.09.29 results; ToO rev 11 §5.4, §10; G7 §2.2, §7 items 46–49, 60")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y
    sx = X0
    sx += c.status(sx, y, "accepted", "ADR-0039 · C4 · B14, A1 at B20") + 10
    sx += c.status(sx, y, "accepted", "ADR-0042 §1–§5, §7, §8 · C4 · B20") + 10
    sx += c.status(sx, y, "proposed", "ADR-0042 §6 (confinement)") + 10
    sx += c.status(sx, y, "accepted", "ADR-0032 · B5 · not confirmation-required") + 10
    sx += c.status(sx, y, "draft", "the floor and its values file") + 14
    y += 50

    # ======================================================================== the definition
    w3 = (W - 2 * 28) / 3
    a = ["**Heartbeat**: an `observer` seat's fixed-schema fact with two fields, the **watched round topic** and its "
         "**watermark**, the sequence number through which it says it has read. A fact, not a finding: it says nothing "
         "about what was read. Carried by `Report` in Run (ADR-0043 §4), `Emit` in Build.",
         "**`heard(o)`**: the mechanism's local monotonic time at which it last admitted a heartbeat under `o`'s live "
         "lease. **Per replica**, as lease expiry is; never the Observer's timestamp (ADR-0032 §3).",
         "**`mark(o, r)`**: the latest watermark for the Thinker's round `r`. **Replicated from the log**, and "
         "**monotone**: a falling watermark is refused. Kept per seat, not per lease, so the Observer's next lease "
         "continues where it left off (R1)."]
    b = ["**1.** `o` holds a live lease.",
         "**2.** fewer than `T_obs` have elapsed since `heard(o)`, read with ADR-0032 §2's **asymmetric margin** "
         "(elapsing early).",
         "**3.** `seq(t) − mark(o, r) < K` for `t`'s current round `r`. **Strict**, because the admit being decided "
         "counts: after it, at most `K` of the round's effects are unread. `≤ K` admits a `K+1` backlog, which "
         "`Coupling.tla` found (R4, applied at R5).",
         "Computed by the typed lift from mechanism state and handed to the floor as `context.observerLive`: a "
         "syntactic lift (ADR-0007)."]
    d = ["**At apply, the deterministic half is re-checked**: conditions 1 and 3. An Observer whose lease ended, or "
         "whose watermark fell behind, between decide and commit voids the admit (R5).",
         "**Condition 2 is checked at decide only**: it is a per-replica clock, as lease expiry is. A heartbeat gone "
         "stale in that window is caught at the next admit.",
         "**`K < R` is required** and refused at startup for each domain: with `K ≥ R` condition 3 never refuses what "
         "the round bound has not (the ground on which ADR-0026 R3 was withdrawn). The gate-side `K < R` check is not "
         "realized (G7 item 46).",
         "`K = 0` admits nothing until the quarantine hold exists (finding 1; G7 item 48)."]
    hs = [c.card(0, 0, w3, t, bb, acc, draw=False, size=14) for t, bb, acc in
          (("§1 · The heartbeat and two values in mechanism state", a, "pink"),
           ("§1 · `live(o)` holds when all three hold", b, "teal"),
           ("Decide, order, re-check (ADR-0033 §4)", d, "grey"))]
    hh = max(hs)
    c.card(X0, y, w3, "§1 · The heartbeat and two values in mechanism state", a, "pink", size=14, h=hh)
    c.card(X0 + w3 + 28, y, w3, "§1 · `live(o)` holds when all three hold", b, "teal", size=14, h=hh, bullets=False)
    c.card(X0 + 2 * (w3 + 28), y, w3, "Decide, order, re-check (ADR-0033 §4)", d, "grey", size=14, h=hh)
    c.arrow([(X0 + w3, y + 60), (X0 + w3 + 28, y + 60)], "pink")
    c.arrow([(X0 + 2 * w3 + 28, y + 60), (X0 + 2 * w3 + 56, y + 60)], "teal")
    y += hh + 56

    # ======================================================================== the timeline
    y += c.heading(X0, y, "One Thinker, its cell Observer, two Run rounds: `seq` against `mark` and the `K` window "
                          "(illustrative sequence; `K` = 8, the placeholder)", "ink", 20)
    K = 8
    # events: (kind, arg)  A actuate, R report, C consult, H heartbeat(mark), D denied attempt, S seal,
    # G- grant refused, G grant, N new round
    ev = [("A",), ("A",), ("C",), ("R",), ("A",), ("H", 2), ("A",), ("A",), ("C",), ("A",), ("R",), ("A",), ("A",),
          ("D",), ("H", 6), ("A",), ("R",), ("S",), ("G-",), ("H", 12), ("G",),
          ("A",), ("C",), ("R",), ("H", 2), ("A",), ("A",)]
    px0 = X0 + 110
    px1 = X1 - 40
    dx = (px1 - px0) / (len(ev) + 0.5)
    unit = 30
    py_base = y + 40 + 14 * unit      # y of seq 0
    ptop = py_base - 14 * unit

    def Y(v):
        return py_base - v * unit

    # axes
    c.line(px0, py_base, px1, py_base, "muted", 1.6)
    c.line(px0, ptop - 10, px0, py_base, "muted", 1.6)
    for v in range(0, 14, 2):
        c.line(px0 - 6, Y(v), px0, Y(v), "muted", 1.2)
        c.text(px0 - 12, Y(v) + 5, str(v), 13, "muted", anchor="end")
    c.text(px0 - 96, ptop + 4, "sequence", 13.5, "muted", bold=True)
    c.text(px0 - 96, ptop + 22, "number", 13.5, "muted", bold=True)

    # compute series per round
    seq, mark, rnd = 0, 0, 1
    seq_pts, mark_pts, band = [], [], []
    xs_round_start = px0
    round_spans = []
    markers = []
    pending_grant = False
    for i, e in enumerate(ev):
        x = px0 + (i + 0.5) * dx
        k = e[0]
        if k == "G":
            round_spans.append((xs_round_start, x - dx / 2, rnd))
            rnd += 1
            xs_round_start = x - dx / 2 + 0.01
            seq, mark = 0, 0
            seq_pts.append(None)
            mark_pts.append(None)
            markers.append((x, k, seq, mark))
            continue
        if k in ("A", "R"):
            seq += 1
        elif k == "H":
            mark = e[1]
        markers.append((x, k, seq, mark))
        seq_pts.append((x, seq))
        mark_pts.append((x, mark))
    round_spans.append((xs_round_start, px1, rnd))

    # round bands and labels
    for (xa, xb, r) in round_spans:
        c.add(f'<rect x="{xa:.1f}" y="{ptop - 34:.1f}" width="{xb - xa:.1f}" height="{py_base - ptop + 34:.1f}" '
              f'{fill("blue-t" if r == 1 else "green-t")} opacity="0.55"/>')
        c.text(xa + 14, ptop - 14, f"Round {'r' if r == 1 else 'r+1'}: Thinker's lease {r}, its own round topic; "
               f"`seq` and the round count restart with each lease", 14, "blue" if r == 1 else "green", bold=True)

    # K window: band between mark and mark+K, drawn as steps
    def steps(pts, off=0):
        segs, cur = [], []
        for p in pts:
            if p is None:
                if cur:
                    segs.append(cur)
                cur = []
                continue
            cur.append(p)
        if cur:
            segs.append(cur)
        out = []
        for s in segs:
            path = []
            for j, (x, v) in enumerate(s):
                xl = x - dx / 2
                if j == 0:
                    path.append((xl, min(13.6, v + off)))
                else:
                    path.append((xl, min(13.6, s[j - 1][1] + off)))
                    path.append((xl, min(13.6, v + off)))
            path.append((s[-1][0] + dx / 2, min(13.6, s[-1][1] + off)))
            out.append(path)
        return out

    for low, high in zip(steps(mark_pts), steps(mark_pts, K)):
        poly = [(x, Y(v)) for x, v in low] + [(x, Y(v)) for x, v in reversed(high)]
        d = "M " + " L ".join(f"{x:.1f} {yy:.1f}" for x, yy in poly) + " Z"
        c.add(f'<path d="{d}" {fs("teal-t", "teal")} stroke-width="1" stroke-dasharray="4 3" opacity="0.9"/>')
        hx, hv = high[0]
        c.add(f'<path d="M ' + " L ".join(f"{x:.1f} {Y(v):.1f}" for x, v in high) +
              f'" {sonly("teal")} stroke-width="1.6" stroke-dasharray="6 4"/>')
    for path in steps(mark_pts):
        c.add('<path d="M ' + " L ".join(f"{x:.1f} {Y(v):.1f}" for x, v in path) +
              f'" {sonly("pink")} stroke-width="3"/>')
    for path in steps(seq_pts):
        c.add('<path d="M ' + " L ".join(f"{x:.1f} {Y(v):.1f}" for x, v in path) +
              f'" {sonly("green")} stroke-width="3"/>')

    # markers and tick labels
    names = {"A": "Actuate", "R": "Report", "C": "Consult", "H": "heartbeat", "D": "Actuate?", "S": "expiry",
             "G-": "grant r+1?", "G": "grant r+1"}
    for x, k, s, m in markers:
        lab = names[k]
        col = {"A": "green", "R": "green", "C": "grey", "H": "pink", "D": "red", "S": "blue", "G-": "red",
               "G": "blue"}[k]
        if k in ("A", "R"):
            c.add(f'<circle cx="{x:.1f}" cy="{Y(s):.1f}" r="5.5" {fs("green", "green")}/>')
        elif k == "C":
            c.add(f'<circle cx="{x:.1f}" cy="{Y(s):.1f}" r="5.5" {fs("bg", "grey")} stroke-width="2"/>')
        elif k == "H":
            c.add(f'<rect x="{x - 6:.1f}" y="{Y(m) - 6:.1f}" width="12" height="12" {fs("pink", "pink")} '
                  f'transform="rotate(45 {x:.1f} {Y(m):.1f})"/>')
        elif k == "D":
            yy = Y(s + 1)
            c.add(f'<path d="M {x - 8:.1f} {yy - 8:.1f} L {x + 8:.1f} {yy + 8:.1f} M {x - 8:.1f} {yy + 8:.1f} '
                  f'L {x + 8:.1f} {yy - 8:.1f}" {sonly("red")} stroke-width="3.2"/>')
        elif k == "S":
            c.line(x, ptop - 34, x, py_base, "blue", 2.6)
        elif k == "G-":
            yy = Y(1)
            c.add(f'<path d="M {x - 8:.1f} {yy - 8:.1f} L {x + 8:.1f} {yy + 8:.1f} M {x - 8:.1f} {yy + 8:.1f} '
                  f'L {x + 8:.1f} {yy - 8:.1f}" {sonly("red")} stroke-width="3.2"/>')
        # tick labels below the axis, two lines staggered
        c.line(x, py_base, x, py_base + 6, "muted", 1.2)
        c.text(x, py_base + 24, lab, 12, col, anchor="middle", bold=k in ("D", "G-", "S", "G"))
        if k == "H":
            c.text(x, py_base + 41, f"w = {m}", 12, "pink", anchor="middle")
        if k in ("A", "R"):
            c.text(x, py_base + 41, f"seq {s}", 12, "green", anchor="middle")
    # callouts on the chart
    xd = [x for x, k, *_ in markers if k == "D"][0]
    c.label(xd, Y(13.2), "denied by R3: seq − mark = 10 − 2 = 8, not < K. Waits; not evicted", "red", 13)
    xs = [x for x, k, *_ in markers if k == "S"][0]
    c.label(xs - 10, Y(13.7) - 2, "seal at 12: the round's effects", "blue", 13)
    xg = [x for x, k, *_ in markers if k == "G-"][0]
    c.label(xg + 70, Y(4.0), "grant refused: mark(o, r) = 6 < seal 12", "red", 13)
    xg2 = [x for x, k, *_ in markers if k == "G"][0]
    c.label(xg2 + 46, Y(8.0), "granted once mark(o, r) ≥ seal", "blue", 13)
    xc = [x for x, k, *_ in markers if k == "C"][0]
    c.label(xc + 10, Y(5.6), "Consult: no step, never coupled", "grey", 13)
    c.label(px0 + 9 * dx, Y(9.4), "admit window: seq − mark < K", "teal", 13)
    y = py_base + 62
    y += c.legend(X0 + 110, y, [("line", "green", "seq(t): Actuate and Report admits in the round (ADR-0042 §2)"),
                                ("line", "pink", "mark(o, r): the Observer's watermark, monotone"),
                                ("box", "teal", "the K window above mark", "4 3"),
                                ("line", "blue", "seal: lease expiry ends the round (ADR-0042 §5)")],
                  title="Chart") + 50

    # ======================================================================== heard(o) and T_obs
    tl_y = y
    y += c.heading(X0, y, "Condition 2 on the mechanism's clock: `heard(o)` and `T_obs` (placeholder 5000 ms)", "ink", 18)
    lx0, lx1 = X0 + 110, X0 + 1700
    ly = y + 46
    c.arrow([(lx0, ly), (lx1, ly)], "muted", sw=1.6)
    c.text(lx1 + 10, ly + 5, "replica's local monotonic clock", 13, "muted")
    hb = [lx0 + 80, lx0 + 420, lx0 + 760]
    for hx in hb:
        c.add(f'<rect x="{hx - 6:.1f}" y="{ly - 6:.1f}" width="12" height="12" {fs("pink", "pink")} '
              f'transform="rotate(45 {hx:.1f} {ly:.1f})"/>')
        c.text(hx, ly - 16, "heartbeat admitted", 12, "pink", anchor="middle")
    tobs = 560
    marg = 70
    last = hb[-1]
    c.add(f'<rect x="{last:.1f}" y="{ly + 14:.1f}" width="{tobs - marg:.1f}" height="16" {fs("teal-t", "teal")}/>')
    c.add(f'<rect x="{last + tobs - marg:.1f}" y="{ly + 14:.1f}" width="{marg:.1f}" height="16" '
          f'{fs("amber-t", "amber")} stroke-dasharray="3 2"/>')
    c.text(last + (tobs - marg) / 2, ly + 48, "live: now − heard(o) < T_obs", 12.5, "teal", anchor="middle")
    c.text(last + tobs - marg / 2, ly + 66, "margin: elapses early", 12.5, "amber", anchor="middle")
    c.add(f'<rect x="{last + tobs:.1f}" y="{ly + 14:.1f}" width="{lx1 - last - tobs - 20:.1f}" height="16" '
          f'{fs("red-t", "red")}/>')
    c.text(last + tobs + (lx1 - last - tobs) / 2, ly + 48, "stale: Actuate and Report under t denied, locally", 12.5,
           "red", anchor="middle")
    tx = lx1 + 300
    c.card(tx, tl_y, X1 - tx, "Why a local clock may decide this", [
        "Expiry of liveness **subtracts**: a stale heartbeat refuses an admit. ADR-0032 §2 lets a subtracting "
        "interval run on a local monotonic clock with a margin that errs early.",
        "Clock error therefore costs availability (an early refusal), never an admit the envelope forbids "
        "(ADR-0032 §1).",
    ], "teal", size=14)
    y = max(ly + 90, tl_y + 200) + 40

    # ======================================================================== coupling by domain
    y += c.heading(X0, y, "Where liveness is coupled, and where it is not", "pink")
    w4 = (W - 3 * 24) / 4
    cards = [
        ("Run: every effect-bearing admit under a Thinker (§2, A1)", [
            "Floor entry **`R3-observer-live`**: forbid `Actuate` and `Report` when `principal.kind == \"thinker\"` "
            "and `!context.observerLive`. In the genesis floor, which is **DRAFT** (G7 §2.2).",
            "Needs `live(o)` for **at least one** cell Observer in the cell (any-of).",
            "**Not `Consult`** (ADR-0041 §2): a read of pinned content adds nothing to the backlog and can be "
            "reconstructed from its digest; a lagging Observer leaves its Thinker able to read and unable to act.",
            "Not an Observer's own emissions, or R3 would refuse the heartbeat it exists to receive.",
            "Denied locally, no consensus, attributed to the Thinker's lease; **the Thinker waits, it is not "
            "evicted**.",
        ], "green"),
        ("Run: coverage carries across rounds, at the grant (§2, R1)", [
            "**A Thinker's lease for round `r+1` is granted only if a cell Observer's `mark(o, r)` is at or beyond the "
            "seal of round `r`'s topic.**",
            "A grant-path check, not a floor entry: the floor evaluates actions and a grant is not one.",
            "At the grant, not the first admit, so a waiting Thinker holds no lease and burns no TTL.",
            "Why: `seq` and the watermark restart with each lease, so the first draft passed at the start of every "
            "round; within a round `R` bounds the backlog, across rounds nothing did (finding 4, `M_ROUNDS`).",
        ], "green"),
        ("Build: couples the gate, not each admit (§3)", [
            "**A promotion completes only if the author's cell Observer has a watermark at or beyond the seal of the "
            "author's round topic set** (ADR-0024 A2.3).",
            "Coverage is not a \"no finding\" attestation (ADR-0024 §2 forbids that): objection is still only "
            "`Vote(deny)`, and silence is still not a veto.",
            "Withholding coverage stalls the promotion and adds nothing.",
            "No cross-round rule: Build's only egress is promotion, which already requires coverage.",
        ], "blue"),
        ("The correlator is never coupled (§4)", [
            "No admit and no promotion waits on a correlator: coupling to it would make one seat's liveness a "
            "precondition for every admit in its domain, the fleet-wide stall ADR-0038 exists to avoid.",
            "It heartbeats too, so **its absence is visible**; that visibility is all this record gives it.",
            "Its absence costs cross-cell detection: D-0038-2.",
            "`Coupling.tla` `CorrelatorNeverGates` holds; `M_CORR` breaks it.",
        ], "grey"),
    ]
    hs = [c.card(0, 0, w4, t, b, a2, draw=False, size=14) for t, b, a2 in cards]
    hh = max(hs)
    for i, (t, b, a2) in enumerate(cards):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, a2, size=14, h=hh)
    y += hh + 50

    # ======================================================================== effect counter + degeneracies
    w2 = (W - 30) / 2
    ec = [
        "**`seq(t)` is the number of `Actuate` and `Report` admits applied under `t`'s lease in its current round**, "
        "assigned at apply so every replica assigns the same number. `Consult` does not advance it.",
        "**The round bound `R` counts every admit**, `Consult` included: a termination bound (ADR-0022 §3).",
        "**Every `Actuate` leaves a record** on the round topic, written by the mechanism when the call returns "
        "(`seat`, `fence`, `admit`, `seq`, `tool`, `breakGlass`, `inputs`, `outcome`, `result`), so the Observer has "
        "something to mark (§3). The seal counts every effect (§5).",
        "**Why** (Context): the reference had counted emissions only. A Thinker that never reported could invoke up to "
        "`R` (64) unread, not `K` (8), and its round sealed at zero, so coverage across rounds was vacuous. "
        "`RunCoupling.tla`'s **`M_EMITSEQ`** is that reference: it breaks `UnreadEffectsBounded` and "
        "`SealCountsEffects`. Closed in the reference at `1e6c0c4` (ADR-0033 A3).",
    ]
    bound = [
        "**Bounded**: at any moment **at most `K` of a Thinker's effects, all in its current round, are unread** by an "
        "Observer that has reported in within `T_obs`, because every earlier round was read to its seal. The first "
        "mechanism-enforced limit on what can happen inside `L`: **a count, not a time**.",
        "**Not bounded**: `L` itself, still unmeasured (ADR-0032 §4).",
        "**Only for an honest watermark.** A colluding Observer heartbeats, reports a watermark and finds nothing, all "
        "its own assertions: the bound is empty under collusion.",
    ]
    h1 = c.card(0, 0, w2, "ADR-0042 §2 · The sequence counts effects (Accepted, B20)", ec, "teal", draw=False, size=14)
    h2 = c.card(0, 0, w2, "§2, §5 · What this bounds, and what it does not", bound, "pink", draw=False, size=14)
    hh = max(h1, h2)
    c.card(X0, y, w2, "ADR-0042 §2 · The sequence counts effects (Accepted, B20)", ec, "teal", size=14, h=hh)
    c.card(X0 + w2 + 30, y, w2, "§2, §5 · What this bounds, and what it does not", bound, "pink", size=14, h=hh)
    y += hh + 30

    y += c.table(X0, y, [("CR-2 case (09.16 review)", 330, {"bold": True}), ("What it looks like", 1100),
                         ("Under coupling (ADR-0039 §5)", W - 1430)], [
        {"cells": ["Dead", "An Observer that is not there produces the same observable as a clean system",
                   "**Closed**: no live lease or no heartbeat within `T_obs`, so its Thinker's effects are refused"],
         "accent": "green"},
        {"cells": ["Partitioned", "Its heartbeats do not reach the mechanism",
                   "**Closed**: `heard(o)` goes stale, and R3 refuses"], "accent": "green"},
        {"cells": ["Starved", "Alive, heartbeating, falling behind (accelerator contention, an availability attack "
                   "ADR-0008 named)", "**Closed** by the watermark: presence without progress fails condition 3 "
                   "(`M_MARK`: testing the time and not the watermark lets a starved Observer pass)"], "accent": "green"},
        {"cells": ["Colluding", "Heartbeats, reports a watermark and finds nothing",
                   "**Open.** Cover, as far as there is one: lineage independence (ADR-0016 §5, ADR-0035, Proposed) and "
                   "the subtract-only correlated-miss test. **The residual-risk statement must say: detection fails open "
                   "against a colluding Observer** (unwritten; G7 §8)"], "accent": "red"},
    ], size=14, accent="pink") + 40

    # ======================================================================== degeneracies
    y += c.heading(X0, y, "Degeneracies (record-level entries; both void no safety theorem and state their losses in "
                          "prose)", "pink")
    y += c.table(X0, y, [("Id", 130, {"bold": True}), ("Kind", 300), ("Parameter → deployed value", 520),
                         ("Premises falsified", 480), ("Theorems voided / properties lost", W - 1430 - 300),
                         ("Type changes", 300)], [
        ["D-0039-1", "Mechanism (a policy-floor entry and a grant-path check, ADR-0023 §6a)",
         "Coupling in Run: `R3-observer-live` and the cross-round grant condition in force → absent",
         "Every Run admit has a live, keeping-up cell Observer, and every earlier round was read before the next was "
         "granted", "**None.** Properties lost: `UnreadBounded`, and (A1) `UnreadEffectsBounded`. The in-round bound "
         "loosens from `K` to `R`; across rounds the backlog grows by up to `R` a round. **Detection fails open against "
         "a dead, partitioned or starved Observer.** Keeps the round bound", "No participant changes type"],
        ["D-0042-1", "Mechanism (ADR-0023 §6a)", "Effects counted and recorded: `Actuate` and `Report` → `Report` only",
         "Every effect-bearing admit advances the sequence and leaves a record an Observer can mark",
         "**None.** Property lost: `UnreadBounded` for invocations: bounded by `R`, not `K`, in a round; unbounded "
         "across rounds. Fails open against a starved Observer for every principal that does not report. **The "
         "reference as it stood on 2026.09.29**; composes with D-0039-1 with no loss beyond the union",
         "No participant changes type"],
    ], size=14, accent="pink") + 12
    y += c.para(X0, y, W, "**Composition (ADR-0039 §7).** Under coupling a cell with no Observer makes no Run admits, so "
                "ADR-0037 D-0037-1 and ADR-0038 D-0038-1 are usable in Run only together with D-0039-1; declared "
                "together, no theorem is lost beyond the union.", 14) + 44

    # ======================================================================== costs, placeholders
    cw = 900
    ch = c.card(X0, y, cw, "§6 · The Observer is on Run's hot path, for liveness not judgment", [
        "**Latency**: when the Observer lags by more than `K` the Thinker waits; a new round waits until the last is read.",
        "**Availability**: a cell's availability is the product of its Thinker's and its Observer's. Extra Observers "
        "raise it: any one live Observer is enough.",
        "**Throughput**: heartbeats are admits on the consensus log, one per `T_obs` per Observer.",
        "**R3 couples break-glass too**: an emergency path waits on a dead Observer. Ratified as written (B14), \"the "
        "first thing a reviewer should reopen\" (ToO §5.4; G7 item 49).",
        "A Byzantine Observer can stop its own cell by withholding heartbeats: availability, within one cell.",
        "None of these is a term in `W + L + D < T_irrev`.",
    ], "red", size=14)
    tx = X0 + cw + 30
    tw = X1 - tx
    th = c.text
    yy = y
    c.text(tx, yy + 20, "§1 (R3) · The placeholders: chosen 2026.09.29 for order of magnitude, none measured", 17,
           "amber", bold=True)
    c.status(tx + 820, yy + 2, "draft", "values file: DRAFT · PLACEHOLDERS · not ratified")
    yy += 38
    yy += c.table(tx, yy, [("Value", 120, {"bold": True}), ("Placeholder", 130), ("Lives in", 300),
                           ("Why this number", tw - 120 - 130 - 300 - 360), ("What a deployment sets it from", 360)], [
        ["`T_obs`", "5000 ms", "values file (`floor/genesis-values.json`)",
         "About five propagation windows `W` (~1 s at the archetype), ten of the reference's lease margins (500 ms), "
         "well inside a lease TTL (120 s in the smoke test). Read with the asymmetric margin",
         "The Observer's measured heartbeat cadence and the margin"],
        ["`K`", "8", "values file", "`T_obs` at roughly one admit per second, rounded up, so an Observer keeping pace "
         "never blocks. `K = 0` is the quarantine hold (finding 1)", "The Observer's measured lag; the tolerated "
         "unread backlog"],
        ["`R` (Build)", "200", "mechanism parameters (I21; `dev-init.sh`)", "The reference's existing dev value",
         "Termination and state-space size (ADR-0022 §3)"],
        ["`R` (Run)", "64", "mechanism parameters, **per domain**", "Run actions are effect-bearing and Run rounds "
         "short: 64 admits at about one per second is a minute, the order of a Run lease's TTL",
         "The same, per Run's alphabet"],
    ], size=13.5, accent="amber") + 12
    yy += c.para(tx, yy, tw, "**`R` is not in the values file**: a mechanism parameter, digested into every admit. "
                 "Relaxing `T_obs` or `K` is an anchor issuance and a promotion; tightening is an ordinary promotion. "
                 "Each is a deployment or rung choice declared under ADR-0023 §6, not the pattern's value. Measured "
                 "values are open (G7 item 47).", 14)
    y = max(y + ch, yy) + 56

    # ======================================================================== the clock model
    y += c.heading(X0, y, "ADR-0032 · The clock model: clocks buy liveness, never safety; intervals are trusted by "
                          "failure direction", "teal", 20)
    lw = 900
    h1 = c.card(X0, y, lw, "§1 · Epoch fencing carries safety without reading a clock", [
        "An action under a stale epoch is rejected because the epoch does not match, not because a timer expired. An "
        "expired lease its holder still believes in is **not a containment violation**.",
        "So clock misbehaviour costs **availability or detection lag, never containment**: a fast clock evicts early "
        "and subtracts; a slow one delays an eviction the fence would still catch.",
        "**§3 · No safety decision reads a clock supplied by a principal**; a timestamp in a payload is cognitive "
        "content (open: `NoAdmitOnPrincipalTime`, a TLA+ property).",
        "**§6** decides no drift bound and no wall-clock behaviour: neither can reach containment.",
    ], "teal", size=14)
    tx = X0 + lw + 30
    tw = X1 - tx
    yy = y
    yy += c.table(tx, yy, [("If the interval's failure…", 300, {"bold": True}), ("Then it may use", 560),
                           ("Examples (§2)", 560), ("Here", tw - 1420)], [
        {"cells": ["**Subtracts** authority", "A **local monotonic clock**, read with an **asymmetric margin** that "
                   "elapses early, so clock error removes authority rather than extending it",
                   "Lease expiry, passive e-stop, vote timeout", "`T_obs` (heartbeat freshness) is this row"],
         "accent": "green"},
        {"cells": ["**Adds or preserves** authority", "**Trusted time**: a signed, attested time source outside the "
                   "principal", "Break-glass TTL, Persona expiry, re-attestation intervals",
                   "No time source is a row: trusted time is **refused** by ADR-0045 §6. R8 (break-glass TTL) stays "
                   "pending (G7 item 8); `T_persona` runs on the local clock (item 62)"], "accent": "red"},
    ], size=14, accent="teal") + 24
    yy += c.table(tx, yy, [("Term of `W + L + D < T_irrev` (§4)", 360, {"bold": True}), ("Meaning", 620),
                           ("Kind", 520), ("State", tw - 1500)], [
        ["`W`", "Effect propagation window, about a second at the archetype", "**Guaranteed by the mechanism**",
         "Proven"],
        ["`L`", "Observer detection latency", "**Emergent property of a component**",
         "**Unmeasured**; coupling bounds a count next to it, not `L`"],
        ["`D`", "Human response budget", "**Organizational commitment**", "Promised"],
        ["`T_irrev`", "Time from emission until the effect is irreversible", "Declared per effect class",
         "No effect class enumerated yet"],
    ], size=14, accent="teal") + 12
    yy += c.para(tx, yy, tw, "**The sum is the property; the ordering `W < L < D` is demoted** to a description of "
                 "magnitudes. Where `T_irrev` is smaller than any budget, the answer is not a faster clock: **the effect "
                 "must not be expressible in the alphabet at all.** `L` and `D` keep their 09.12-onward meanings (§5).",
                 14)
    y = max(y + h1, yy) + 50

    # ======================================================================== checks
    y += c.heading(X0, y, "What was checked (each property broken by its mutation, small constants)", "ink", 18)
    y += c.table(X0, y, [("Module", 300, {"bold": True}), ("Property", 520, {"mono": False}),
                         ("Mutation that must break it", 900), ("Result", W - 1720)], [
        ["`Coupling.tla` (B14)", "`NoAdmitWithoutLiveObserver`", "`M_NOCOUPLE`: the check dropped",
         "Breaks, and takes `UnreadBounded` with it: D-0039-1 as stated"],
        ["", "`UnreadBounded` (over all rounds)", "`M_MARK`: tests heartbeat time, not watermark · `M_ROUNDS`: coverage "
         "not carried across rounds (the record before R1)", "Each breaks only `UnreadBounded`; `M_ROUNDS` with the "
         "trace \"round 2 granted while round 1 unread\""],
        ["", "`CorrelatorNeverGates` (an `ENABLED` predicate)", "`M_CORR`: the correlator coupled", "Breaks only §4"],
        ["`RunCoupling.tla` (ADR-0042 §8)", "`UnreadEffectsBounded`, `SealCountsEffects`",
         "`M_EMITSEQ`: only `Report` advances the sequence (the reference before ADR-0042)",
         "Breaks both and nothing else (K=1, R=4, two rounds)"],
        ["", "`ConsultNeverCoupled`", "`M_COUPLEALL`: `Consult` coupled", "Breaks only it"],
        ["", "`RoundBoundCountsAll`", "`M_BOUNDEFF`", "Breaks it"],
    ], size=13.5, accent="grey") + 10
    c.para(X0, y, W, "At the reference (R4): every refusal seen to fire: no Observer lease, no heartbeat, a dishonest "
           "heartbeat, a backlog of `K`, presence without progress, staleness after `T_obs`, a round-2 grant while round "
           "1 is unread; one Build promotion stalled for coverage and completed by a heartbeat to the seal. Not realized: "
           "`W(p)` as an ACL and the gate-side `K < R` check (G7 item 46); a scripted cell Observer (item 45); how "
           "Observer rounds are laid out against Thinker rounds (finding 3; item 60).", 14, "muted")
    return c
