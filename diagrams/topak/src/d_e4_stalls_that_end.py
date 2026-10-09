"""E4 — Stalls that end: liveness stated for the first time (2026.10.07), checked by TLC and not yet proved.

ToO rev 15 §5.5; the liveness plan (derived/topak-liveness-2026.10.07.md); spec/Coupling_live.tla and
spec/Emergency_live.tla with their rows, results, proof and certified-proof results; the deadlock audit; the Lean
encoding of Emergency_live and its graph check. The two TLC matrices, the counterexample strip, the certified
counts, the graph-check table and the audit table are read from the results files at build time, so none of them
can drift from the record; the build fails if a results file has a row not as expected. E2 draws the coupling rule
itself; this diagram draws only what the liveness work added to it."""
import pathlib
import re

import lib
from lib import Canvas

ID, SLUG = "E4", "stalls-that-end"

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "spec" / "Coupling_live.tla").exists()), _HERE.parents[3])
SPEC = ROOT / "spec"


# ---------------------------------------------------------------------------------------------- readers

def read_rows(mod):
    """-> list of rows of spec/<mod>-rows.txt: name mut spec kind property expected [CONST=v ...] [states=N]."""
    out = []
    for ln in (SPEC / f"{mod}-rows.txt").read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        body, _, note = ln.partition("#")
        f = body.split()
        extra = f[6:]
        out.append({"name": f[0], "mut": f[1], "spec": f[2], "kind": f[3], "prop": f[4], "exp": f[5],
                    "consts": " ".join(x for x in extra if not x.startswith("states=")),
                    "states": next((x[7:] for x in extra if x.startswith("states=")), None),
                    "note": note.strip()})
    return out


def read_results(mod):
    """-> (file name, {row: verdict}, summary line) of the newest spec/<mod>-results-*.txt. Refuses a row not as
    expected, so the diagram cannot draw a results file that disagrees with its rows."""
    f = sorted(SPEC.glob(f"{mod}-results-*.txt"))[-1]
    t = f.read_text(encoding="utf-8")
    verdict, cur = {}, None
    for ln in t.splitlines():
        m = re.match(r"=== (\S+) ·", ln)
        if m:
            cur = m.group(1)
        m = re.match(r"→ (HOLDS|VIOLATED) \(expected (\w+): (.+?)\)", ln)
        if m and cur:
            if m.group(3) != "as expected":
                raise SystemExit(f"{f.name}: row {cur} is not as expected")
            verdict[cur] = m.group(1)
    summary = [ln for ln in t.splitlines() if ln.startswith("Rows: ")][-1]
    return f.name, verdict, summary


def read_trace(mod, row):
    """-> list of (action, {var: value}) of the counterexample a results file prints for one row, and the loop."""
    f = sorted(SPEC.glob(f"{mod}-results-*.txt"))[-1]
    t = f.read_text(encoding="utf-8")
    sec = t.split(f"=== {row} ·")[1].split("\n=== ")[0]
    states, back = [], None
    for ln in sec.splitlines():
        m = re.match(r"State (\d+): <(\S+)", ln)
        if m:
            states.append((m.group(2), {}))
            continue
        m = re.match(r"/\\ (\S+) = (.+)$", ln)
        if m and states:
            states[-1][1][m.group(1)] = m.group(2).strip()
        m = re.match(r"Back to state (\d+): <(\S+)", ln)
        if m:
            back = (int(m.group(1)), m.group(2))
    return f.name, states, back


def read_cert(mod):
    """-> dict of a certified results file's routes (spec/proof-certification.md §5)."""
    f = sorted(SPEC.glob(f"{mod}-proof-cert-results-*.txt"))[-1]
    t = f.read_text(encoding="utf-8")

    def n(pat):
        m = re.search(pat, t)
        return int(m.group(1)) if m else 0
    last = [ln for ln in t.strip().splitlines() if ln.startswith("All ") or ln.startswith("NOT CERTIFIED")][-1]
    return {"file": f.name, "n": n(r"Obligations: (\d+)"),
            "triv": n(r"trivial, closed by tlapm with no backend\s+(\d+)"),
            "smt": n(r"SMT, proof accepted by ethos\s+(\d+)"),
            "zen": n(r"Zenon, proof checked by Isabelle\s+(\d+)"),
            "isa": n(r"\n  Isabelle\s+(\d+)"),
            "ls4": n(r"LS4, temporal step, NOT certified\s+(\d+)"),
            "certified": last.startswith("All ")}


def read_graph_check():
    f = sorted((SPEC / "lean").glob("GraphCheckEmergency-results-*.txt"))[-1]
    rows = []
    lines = f.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r"(Emergency(?:_live)?) Mut=(\S+) \| (\d+) states · (\d+) edges · (\d+) (Next|NextL) steps · "
                     r"(\d+) initial \| (\w+)", ln)
        if not m:
            continue
        detail = lines[i + 1]
        fl = {p: re.search(p + r" agrees on \d+ of \d+ states, false in (\d+)", detail)
              for p in ("EmergencyNeverCoupled", "EmergencyCallsWithoutObserver")}
        bad = re.search(r"edges not \w+ steps: (\d+) · \w+ steps not TLC edges: (\d+)", detail)
        rows.append({"mod": m.group(1), "mut": m.group(2), "states": int(m.group(3)), "edges": int(m.group(4)),
                     "steps": int(m.group(5)), "rel": m.group(6), "res": m.group(8),
                     "enc": fl["EmergencyNeverCoupled"].group(1) if fl["EmergencyNeverCoupled"] else None,
                     "ecwo": (fl["EmergencyCallsWithoutObserver"].group(1)
                              if fl["EmergencyCallsWithoutObserver"] else None),
                     "bad": (bad.group(1), bad.group(2)) if bad else ("?", "?")})
    return f.name, rows


def read_audit():
    f = SPEC / "deadlock-audit-results-2026.10.07.txt"
    rows, summary = [], ""
    for ln in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"(.+?) \| (.*) \| (\d+) distinct states \| (.+)$", ln)
        if m:
            rows.append(m.groups())
        if ln.startswith("Lines: "):
            summary = ln
    return f.name, rows, summary


def n_(x):
    return f"{int(x):,}"


# ---------------------------------------------------------------------------------------------- helpers

def row_of_cards(c, y, items, gap=28, size=14):
    """items: (x, w, title, body, accent, kwargs). One height for the row, measured over every card in it."""
    hs = [c.card(x, y, w, t, b, a, draw=False, size=size, **kw) for x, w, t, b, a, kw in items]
    h = max(hs)
    for x, w, t, b, a, kw in items:
        c.card(x, y, w, t, b, a, size=size, h=h, **kw)
    return h


def even(x0, x1, k, gap=28):
    w = (x1 - x0 - (k - 1) * gap) / k
    return [(x0 + i * (w + gap), w) for i in range(k)]


HOLD, BREAK = "[[green|holds]]", "[[red|broken]]"


def verdict_cell(v, spec=None, states=None):
    s = HOLD if v == "HOLDS" else BREAK
    if spec:
        s += f" · `{spec}`"
    if states:
        s += f" · {n_(states)} states"
    return s


# ---------------------------------------------------------------------------------------------- the build

def build():
    cl_rows = read_rows("Coupling_live")
    cl_file, cl_res, cl_sum = read_results("Coupling_live")
    el_rows = read_rows("Emergency_live")
    el_file, el_res, el_sum = read_results("Emergency_live")
    for rows, res, mod in ((cl_rows, cl_res, "Coupling_live"), (el_rows, el_res, "Emergency_live")):
        if {r["name"] for r in rows} != set(res) or any(res[r["name"]] != r["exp"] for r in rows):
            raise SystemExit(f"{mod}: the results file and its rows disagree")
    tr_file, trace, back = read_trace("Coupling_live", "m-hblive-grant")
    ce, cc = read_cert("Emergency_live"), read_cert("Coupling_live")
    gc_file, gc = read_graph_check()
    au_file, audit, au_sum = read_audit()

    c = Canvas(ID, "Stalls that end: liveness stated for the first time, checked by TLC and not yet proved",
               "The corpus's answer to failure is to stall, and every check before 2026.10.07 was of safety, under "
               "which a stall that never ends is as safe as one that ends (CR-37; ToO rev 15 §5.5). The liveness plan "
               "sorts the stalls into tiers. Two modules now **extend** frozen ones, so that the base's safety carries "
               "over, and add what those cannot state. `Emergency_live` makes ADR-0039 A2's escape hatch two "
               "invariants over `ENABLED`: **proved** (through Isabelle), **certified**, and **proved in Lean**, of "
               "the encoding. `Coupling_live` states that ADR-0039 §2's stall ends as four leads-to properties, under "
               "fairness conditions each named for whose obligation it is (ToO §13 A12, A18): **checked** by TLC, "
               "**not proved**. One mutation, `M_HBLIVE`, passes every safety check and every witness, and only a "
               "leads-to property catches it. The proofs are owed, and the four properties have the shape of the "
               "prover's first known unsound case (ADR-0046 A2). Neither module is a record: they sit under ADR-0039 "
               "(accepted, C4) and its A2 (provisional, with ADR-0052), and G11 cites them by digest.",
               3000,
               "derived/topak-liveness-2026.10.07.md (the plan: already safety, Tier 0, Tier 1 items 1–5, Tier 2, "
               "\"Why it's worth the cost\"); spec/Coupling_live.tla (d65189d3c71b30b4), Coupling_live-rows.txt and "
               f"{cl_file}, read at build time (rows, verdicts and the m-hblive-grant counterexample); "
               f"spec/Coupling_live_proof.tla, Coupling_live-proof-results-2026.10.08.txt and {cc['file']} (read at "
               "build time); spec/Coupling.tla (Next, GrantT, Heartbeat); spec/Emergency_live.tla (9685c67b42910b85), "
               f"Emergency_live-rows.txt and {el_file} (read at build time); spec/Emergency_live_proof.tla, "
               f"Emergency_live-proof-results-2026.10.07.txt and {ce['file']} (read at build time); "
               "spec/Emergency_proof.tla (the dropped lemma); spec/README.md (the \"Liveness (2026.10.07)\" "
               "paragraph, certified runs, the two proof-module rows, Practice item 1); "
               f"spec/{au_file} (read at build time); spec/lean/TopakSpec/Emergency.lean, "
               f"spec/lean/TopakSpec-results-2026.10.07.txt and spec/lean/{gc_file} (read at build time); "
               "spec/RunCoupling_proof.tla, Correlator_proof.tla, Operators_proof.tla (the Tier 0 theorems); "
               "ADR-0039 §1, §2 with A2, §4, finding 3, B14, B34; ADR-0046 §3 with A2, B37; ADR-0052 (provisional, "
               "B34); ADR-0053 (B36); ADR-0024 open obligations; derived/topak-critical-review-2026.10.02.md CR-37; "
               "G11 §2.9, §3 (the liveness rows; results 1 and 8; \"What these checks are\"), §5, §7 items 104, 105, "
               "§8; ToO rev 15 §3.3, §5.5, §11.3, §12 item 21, §13 rows A12 and A18",
               # drawn new against G11 and ToO rev 15 (lib.STATE_G11), where lib offers the footer for it
               **({"state": lib.STATE_G11} if hasattr(lib, "STATE_G11") else {}))
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ---- status band
    sx = X0
    sx += c.status(sx, y, "accepted", "ADR-0039 · C4 · B14: the stall, §2") + 10
    sx += c.status(sx, y, "provisional", "ADR-0039 A2 · B34, with ADR-0052: the escape hatch") + 10
    sx += c.status(sx, y, "accepted", "ADR-0046 A2 · C2 · B37: the prover's two unsound cases") + 10
    sx += c.status(sx, y, "accepted", "ADR-0053 · B36: the Lean route") + 10
    sx += c.pill(sx, y, "Not a record: the two _live modules, cited by digest at G11 §3, frozen from G11", "grey",
                 11.5) + 10
    c.status(sx, y, "open", "G11 §7 item 105: liveness checked, not proved")
    y += 54

    # ================================================================ 1. why
    y += c.heading(X0, y, "1 · Why: a stall is safe, and so is a stall that never ends", "ink", 21)
    cols = even(X0, X1, 4)
    h = row_of_cards(c, y, [
        (*cols[0], "The design's answer to failure is to stall (ToO rev 15 §5.5)", [
            "A Thinker without a live Observer waits, a promotion without coverage waits, and a domain without an "
            "operator waits.",
            "Every check before 2026.10.07 was of safety, and a stall is safe; **so is a stall that never ends**.",
            "ADR-0039 §2 makes a liveness claim in so many words: \"The Thinker waits; it is not evicted. When the "
            "Observer catches up, admits resume within the same round, or the next round is granted.\"",
        ], "grey", {}),
        (*cols[1], "CR-37: no liveness property anywhere (critical review 2026.10.02)", [
            r"Every module was `Init /\ [][Next]_vars` with no fairness, and every property an invariant "
            "(`spec/proof-method.md` §5). That is what made the proofs cheap (ToO §11.3).",
            "Coupling across rounds, coverage at the tally, the correlator's exemption and `K < R` are all arguments "
            "that a stall resolves, \"and nothing checks that it does\"; the model \"cannot distinguish stall from "
            "deadlock\".",
            "CR-37 proposed one liveness property per coupling module under **weak fairness on the heartbeat**. That "
            "is not enough, even strong (§5, `SpecAnyBeat`).",
            "ToO §12 item 21: **no stall is shown to end.**",
        ], "red", {}),
        (*cols[2], "The liveness that matters (the plan)", [
            "Not \"a bad principal eventually stops\", but **the stalls TOPAK chooses do end**, and **the emergency "
            "paths stay open while everything else is stalled**.",
            "The method stays as it is: **a mutation that must break each liveness property**, as with the "
            "invariants.",
            "The plan's route: TLC's liveness checker at small constants first, then a TLAPS WF1/SF1 proof on a "
            "decreasing measure such as `seal[r] − mark[r]` or `seq − mark`, and Lean later.",
        ], "teal", {}),
        (*cols[3], "Why TLC's deadlock check cannot see it (Coupling_live.tla header)", [
            "In `Coupling` every state has a successor: the Observer's lease, granted or ended, and the correlator "
            "always step.",
            "So a Thinker stalled for good is a **livelock**, not a deadlock: with the check on, TLC reports nothing "
            "even under the mutation that stalls the next round for good (row `d-hblive-deadlock`).",
            "Several run scripts pass `-deadlock`, which turns the check off altogether (the plan; §9 below).",
            "**Only a leads-to property**, `P ~> Q` (whenever `P`, eventually `Q`), tells a stall that ends from one "
            "that does not.",
        ], "red", {}),
    ])
    y += h + 50

    # ================================================================ 2. the plan's tiers
    y += c.heading(X0, y, "2 · The plan's tiers, and where each item stands at G11 "
                          "(derived/topak-liveness-2026.10.07.md; G11 §7 item 105)", "ink", 21)
    st_proved = "[[teal|Stated · proved · certified]]"
    st_checked = "[[blue|Stated · checked by TLC]] · [[red|not proved]]"
    st_none = "[[red|Not stated · unmodelled]]"
    st_decl = "[[grey|Declared, not proved]]"
    st_safe = "[[green|Already safety]]"
    y += c.table(X0, y, [("Plan item", 330, {"bold": True}), ("The claim, in the plan's words", 1000),
                         ("Rests on", 330), ("Where it stands at G11", W - 1660)], [
        {"group": "Already safety: withdrawing authority. \"Don't spend a liveness proof here\"", "accent": "green"},
        ["Expiry", "Checked at decide time on a local clock whose error margin ends the lease early.",
         "ADR-0032 §1, §2",
         st_safe + ": `RevokedStaysStopped`, `NoActionUnderFencedEpoch` and ADR-0032 §1, \"clocks buy liveness, "
                   "never safety\", already cover it"],
        ["Epoch fence and lease", "Re-checked at apply.", "ADR-0033 §4", st_safe],
        ["Partition", "Effects need an ordered admit, so during a partition nothing commits.", "ADR-0033 §4",
         st_safe + ". Only the replicated bookkeeping, freeing the slot and writing the seal, depends on progress: "
                   "Tier 1 item 3"],
        {"group": "Tier 0: \"X can't block Y\", invariants over ENABLED. \"Prove all of these; it's cheap\"",
         "accent": "teal"},
        ["Stated before", "`ConsultNeverCoupled` (`RunCoupling`), `LagNeverGates` (`Correlator`), "
                          "`DenyAlwaysAvailable` (`Operators`).",
         "ADR-0041 §2; ADR-0051 (Proposed); ADR-0050 (provisional)",
         st_proved + ", before 2026.10.07: `ConsultNeverCoupledAlways`, `LagNeverGatesAlways`, "
                     "`DenyAlwaysAvailableAlways`, in proof modules that certify"],
        {"cells": ["**The gap**", "\"An emergency call is admitted with no live Observer.\" It is the one escape "
                   "hatch from the coupling stall, and it rested only on a TLC reachability witness. Its `ENABLED` "
                   "lemma was dropped because only Zenon proved it and Isabelle couldn't check Zenon's script "
                   "(`Emergency_proof.tla:401`). A witness shows the call can happen in some run; the claim needs it "
                   "possible in every state where the Observer is dead.",
                   "ADR-0039 A2 (provisional, with ADR-0052)",
                   st_proved + " · [[teal|proved in Lean]], of the encoding: `Emergency_live.tla`, 32 TLC rows, two "
                               "invariants proved through Isabelle; the encoding checked against TLC's graphs (§4)"],
         "accent": "teal"},
        {"group": "Tier 1: real leads-to properties to model and prove, in priority order", "accent": "blue"},
        {"cells": ["**1 · The Run coupling stall resolves**", "If the cell Observer eventually holds its lease and "
                   "keeps up, every Thinker refused for its backlog is eventually admitted again, and round `r+1` is "
                   "eventually granted once round `r` is sealed. The assumption should be A12 written as a fairness "
                   "condition, so that the proof says exactly what a deployment must guarantee. \"Repeat it for "
                   "`Actuate`/`Report` in `RunCoupling`.\"",
                   "ADR-0039 §2; ToO §13 A12",
                   st_checked + ": `Coupling_live.tla`, four leads-to properties, 69 TLC rows (§5). The proofs are "
                                "owed. The repeat for `RunCoupling` has no module: spec/README.md lists two `_live` "
                                "modules"], "accent": "blue"},
        ["2 · The Build promotion stall resolves", "Under ADR-0024's two weak-fairness assumptions, a gated round "
         "that no seat denies eventually promotes. A proof will force a missing premise (§8).", "ADR-0024 §2, A2.3",
         st_none + ". Belongs in the still-owed bootstrap `Promotion` module"],
        ["3 · Every ended lease eventually yields a seal", "Expiry, revocation and fence. A seal that never lands is "
         "a silent deadlock of the next round. Assumes consensus progress.", "the plan; I15", st_none],
        ["4 · A lapsed operator is eventually re-seated by a quorum", "Lower priority: the stall is declared, and "
         "resolving it rests on people.", "ADR-0050 (provisional)", st_none],
        ["5 · Detection eventually happens", "Each correlator's watermark eventually passes every send, so "
         "`CarriedCoversSplitPath` eventually applies. Useful but advisory: detection can only subtract.",
         "ADR-0051 (Proposed)", st_none],
        {"group": "Tier 2: declare as assumptions, don't prove", "accent": "grey"},
        ["Paxos liveness", "An eventually stable leader under partial synchrony. Textbook, and the reference already "
         "tests \"liveness after healing\". Model it as fairness on an abstract ordering action.", "ADR-0033",
         st_decl + ": every step `Coupling_live`'s conditions name is one the mechanism decides and orders, so each "
                   "also assumes the ordering makes progress, \"which the liveness plan declares (Tier 2) and nothing "
                   "here models\""],
        ["Timing budgets", "`W + L + D < T_irrev`, `T_obs`, `K`: measurements, not theorems. ADR-0032 rightly "
         "defers UPPAAL; measure them with the rehearsal rig (CR-36).", "ADR-0032 §4",
         st_decl + ": `T_obs` and `K` are still placeholders (ADR-0039 §1; E2)"],
        ["Human responsiveness", "Weak fairness on `Vote`: an assumption about people, as ADR-0024 says.",
         "ADR-0024 open obligations",
         st_decl + ". `Coupling_live`'s `GrantsMade` is of the same kind, \"an assumption about people, declared as "
                   "one\", now ToO §13 A18"],
        ["Kafka delivery", "Lost records leave the Observer short of the seal, which shows up as a stall under A12. "
         "It doesn't need its own property.", "—", st_decl],
    ], size=13.5, accent="grey") + 50

    # ================================================================ 3. the extension relation
    y += c.heading(X0, y, "3 · Liveness lives in an extension, not a successor (G11 §5; spec/README.md, \"Liveness "
                          "(2026.10.07)\")", "ink", 21)
    GW = 960
    gapx = 120
    bw = (GW - gapx) / 2

    fam = {
        "Coupling": [
            ("`Coupling.tla` · frozen", ["`6d1e7a07f3d102ef`, cited by ADR-0039 and ADR-0046 §4.",
                                         r"`Spec == Init /\ [][Next]_vars`: no fairness; three invariants; "
                                         "`M_NOCOUPLE`, `M_MARK`, `M_ROUNDS`, `M_CORR`."], "grey"),
            ("`Coupling_proof.tla`", ["`9c37a36c2e607d54`. The three invariants, for every K, R and MaxRound; "
                                      "certified (ADR-0046 A1)."], "grey"),
            ("`Coupling_live.tla`", ["`d65189d3c71b30b4`. `NextL`: `Next` with the heartbeat open to `M_HBLIVE` and "
                                     "`M_HBCOUPLED`; `KeepUp`; four fairness conditions; four leads-to properties; "
                                     "three witnesses."], "blue"),
            ("`Coupling_live_proof.tla`", ["`9efafeccf705dde2`. `SpecLImpliesSpec`; the three `…AlwaysL`; "
                                           f"`SafeAlwaysL`. {cc['n']} obligations, certified. **Not the leads-to "
                                           "properties.**"], "teal"),
        ],
        "Emergency": [
            ("`Emergency.tla` · frozen", ["`1abae9beb82b00fa`, cited by ADR-0052 (provisional).",
                                          "Six invariants; seven mutations; the witness w3, an emergency call with no "
                                          "live Observer."], "grey"),
            ("`Emergency_proof.tla`", ["`a1e5a82ad625496b`. The six, certified; the `ENABLED` lemma for w3 dropped "
                                       "(line 401)."], "grey"),
            ("`Emergency_live.tla`", ["`9685c67b42910b85`. `EmCall` split into `EmAdmit` and `EmRefuse`; two "
                                      "`ENABLED` invariants; `M_EMCOUPLE`, `M_EMCOUPLE2`."], "teal"),
            ("`Emergency_live_proof.tla`", ["`63c8ec703e6097d9`. The two invariants; `SpecLImpliesSpec`; the six for "
                                            f"`SpecL`. {ce['n']} obligations, certified."], "teal"),
        ],
    }
    # one row height for the top boxes and one for the bottom, over all eight
    ht = max(c.card(0, 0, bw, t, b, a, draw=False, size=13.5, tsize=15) for f in fam.values() for t, b, a in f[:2])
    hb = max(c.card(0, 0, bw, t, b, a, draw=False, size=13.5, tsize=15) for f in fam.values() for t, b, a in f[2:])
    vgap = 70
    gy0 = y + 6
    for k, (name, boxes) in enumerate(fam.items()):
        gx = X0 + k * (GW + 40)
        pos = [(gx, gy0, ht), (gx + bw + gapx, gy0, ht), (gx, gy0 + ht + vgap, hb),
               (gx + bw + gapx, gy0 + ht + vgap, hb)]
        for (t, b, a), (bx, by, bh) in zip(boxes, pos):
            c.card(bx, by, bw, t, b, a, size=13.5, tsize=15, h=bh, dash="7 4" if "frozen" in t else None)
        my = gy0 + 44
        c.arrow([(gx + bw + gapx, my), (gx + bw, my)], "grey", label="EXTENDS", lsize=12)
        c.arrow([(gx + bw / 2, gy0 + ht + vgap), (gx + bw / 2, gy0 + ht)], "blue", label="EXTENDS", lsize=12)
        c.arrow([(gx + bw + gapx + bw / 2, gy0 + ht + vgap), (gx + bw + gapx + bw / 2, gy0 + ht)], "teal",
                label="EXTENDS", lsize=12)
        c.arrow([(gx + bw + gapx, gy0 + ht + vgap + 44), (gx + bw, gy0 + ht + vgap + 44)], "teal",
                label="EXTENDS", lsize=12)
    gh = ht + vgap + hb
    cx = X0 + 2 * (GW + 40)
    hcard = c.card(cx, y, X1 - cx, "What the extension relation gives, and what it adds", [
        "**Under every `Mut` of the base, `NextL` is the base's `Next`** (`NextIsNextL`, proved), so the state graph "
        "is the same: 1,124 states for `Coupling`, 25,728 for `Emergency`.",
        "**Under the extension's own mutations `NextL` is a restriction of `Next`** (`NextLIsNext`, proved under every "
        "`Mut`).",
        r"**So `SpecL => Spec` is proved** (`SpecLImpliesSpec`), and every invariant the base's proof module proves "
        "holds of `SpecL`, each under the hypothesis it has there: **the safety carries over**.",
        r"Fairness is conjoined, as `SpecA12 == SpecL /\ A12`, so a theorem about `SpecL` holds of every fair spec "
        "the module defines.",
        "The base is never edited. The plan had said \"a successor module, as `Lease_A1` did\"; the modules extend "
        "instead, as a proof module does.",
        "**Frozen from G11 on**: the two modules, their proof modules and their results files (G11 §3).",
    ], "blue", size=14, h=max(0, gh + 6 - 0))
    y += max(gh + 6, hcard) + 54

    # ================================================================ 4. Emergency_live
    y += c.heading(X0, y, "4 · Tier 0: the escape hatch is a property, not only a witness: `Emergency_live` "
                          "(ADR-0039 A2; ToO rev 15 §3.3)", "teal", 21)
    lw = 1000
    props = [
        "A2: \"a person seated by the break-glass roster's quorum for one round does not wait on an Observer.\" "
        "`Emergency.tla` showed this as a behaviour, its witness w3. The claim is that **once the seat is live, "
        "nothing the Observer does can stop its calls, in any state**.",
        r"`EmergencyNeverCoupled == \A t \in Tools : (em.live /\ t \in em.envelope)` "
        r'`=> ENABLED EmAdmit(t)`: "while the seat is live, a call of any tool in its envelope can be admitted, '
        "whatever the Observer's state\".",
        r"`EmergencyCallsWithoutObserver == (em.live /\ ~obsLive)` `=> \E t \in Tools : ENABLED EmAdmit(t)`: "
        "\"while the seat is live and the Observer is not, some emergency call can be admitted\". The envelope is "
        "never empty: it holds `te` (ADR-0052 R1) and, in this model, `t1` (`EnvelopeHasT1`, which holds).",
        "To ask `ENABLED` of the admit, `EmCall` is split into its two outcomes, `EmAdmit` and `EmRefuse`; under "
        "every `Mut` of `Emergency.tla` the two together are `EmCall` exactly, so the state graph is the same.",
        "**Scope**: the calls of a live seat, not the seating. \"An activation that waited for a live Observer would "
        "pass every check here.\"",
        "`M_EMCOUPLE`: R3 extended to the emergency seat. `M_EMCOUPLE2`: the same from the seat's second round on; "
        "every invariant holds and w3 is still reached, in round one, so **only the two properties catch it**.",
    ]
    hp = c.card(X0, y, lw, "The two invariants over `ENABLED`, quoted from the module", props, "teal", size=14)
    tx = X0 + lw + 30
    tw = X1 - tx
    tlab = {"none": "unmutated", "M_EMCOUPLE": "`M_EMCOUPLE`: R3 extended to the emergency seat",
            "M_EMCOUPLE2": "`M_EMCOUPLE2`: coupled from the seat's second round on"}
    order = []
    for r in el_rows:
        k = (r["mut"], r["consts"])
        if k not in order:
            order.append(k)
    ecols = [("Configuration (Emergency_live-rows.txt)", 400, {}), ("`Safe`", 210),
             ("Deadlock check on", 190), ("Witness w3: an unobserved emergency call", 260),
             ("`EmergencyNeverCoupled`", 270), ("`EmergencyCallsWithoutObserver`", 300)]
    ecols.append(("`EnvelopeHasT1`", tw - sum(x[1] for x in ecols)))

    def ecell(k, prop, kind=None):
        rs = [r for r in el_rows if (r["mut"], r["consts"]) == k and r["prop"] == prop
              and (kind is None or r["kind"] == kind)]
        if not rs:
            return "—"
        r = rs[0]
        v = el_res[r["name"]]
        if kind == "DEADLOCK":
            return "[[green|no terminal state]]" if v == "HOLDS" else "[[red|deadlock]]"
        if prop.startswith("Never"):
            return "reached" if v == "VIOLATED" else "[[red|not reached]]"
        return verdict_cell(v, states=r["states"])

    trows = []
    for k in order:
        mut, consts = k
        lab = tlab.get(mut, f"`{mut}` (`Emergency.tla`'s)")
        if consts:
            lab += f" · `{consts}`"
        cells = [lab, ecell(k, "Safe", "INVARIANT"), ecell(k, "Safe", "DEADLOCK"),
                 ecell(k, "NeverUnobservedEmergencyCall"), ecell(k, "EmergencyNeverCoupled"),
                 ecell(k, "EmergencyCallsWithoutObserver"), ecell(k, "EnvelopeHasT1")]
        trows.append({"cells": cells, "accent": "red"} if mut.startswith("M_EMCOUPLE") else cells)
    th = c.table(tx, y, ecols, trows, size=13.5, accent="teal")
    th += c.para(tx, y + th + 8, tw, f"**TLC checks** ({el_file}): {el_sum.replace(' · ERROR: none', '')}. "
                 "Emergency's seven mutations each leave both properties holding on that mutation's own state graph: "
                 "none of them couples the emergency seat. — : no row of this file.", 13.5, "muted") + 8
    y += max(hp, th) + 34

    # proof, Lean, graph check
    w1, w2 = 820, 820
    xs = [X0, X0 + w1 + 28, X0 + w1 + w2 + 56]
    w3 = X1 - xs[2]
    tl = [
        r"For every round bound: `EmergencyNeverCoupledAlways` and `EmergencyCallsWithoutObserverAlways` under "
        r'`Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}`; `SpecLImpliesSpec` under every `Mut`, and with it '
        "`Emergency_proof`'s six for `SpecL`; `SafeAlwaysL`.",
        "`EmergencyNeverCoupled` holds in every state under its hypothesis, reachable or not: the admit's guard does "
        "not read the Observer. `EmergencyCallsWithoutObserver` needs one fact of the reachable states, "
        "`EnvelopeHasTe`, inductive under every `Mut`.",
        f"**Certified** ({ce['file']}): {ce['n']} obligations: {ce['triv']} trivial, closed by tlapm; {ce['smt']} SMT, "
        f"each proof accepted by `ethos`; {ce['zen']} Zenon; {ce['isa']} Isabelle; **{ce['ls4']} LS4, which no "
        "checker confirms**.",
        "**Why Isabelle.** The dropped lemma failed on the record the admit writes to `calls'`: cvc5 could not "
        "eliminate `calls' = {...}`, and Zenon's script left the equality of two records unproved, which Isabelle "
        "refuses. Here Isabelle proves each property in one step from its expansion (`ExpandENABLED, Isa`).",
        r"**Why one step each.** Under a binder, tlapm 7824dab hands an unexpanded `ENABLED` to its backends as a "
        r"constant that does not depend on the bound variable: it proves `(\E t \in Tools : ENABLED EmAdmit(t))` "
        r"`=> (\A t \in Tools : ENABLED EmAdmit(t))`, which is false, and `ethos` accepts cvc5's proof. **Found "
        "writing this module** (G11 §3 result 1; ADR-0046 A2).",
    ]
    ll = [
        "`Emergency.tla` and `Emergency_live.tla` re-encoded in one file as a transition system. `ENABLED A` is "
        "`Enabled A` (`Temporal.lean`): a successor in the encoding's `State` type; `EmAdmit` fixes each primed "
        "variable to a value of its type, so the two agree.",
        "`EmergencyNeverCoupledValid`: under every other `Mut`, in every state, reachable or not.",
        "`EmergencyNeverCoupledAlways`, `EmergencyCallsWithoutObserverAlways`: in every state `Spec` reaches, and so "
        "every state `SpecL` reaches, under `NoCoupledRound`, that no round in which the seat can be live is coupled. "
        "**The weakest hypothesis there is**: the two `…Iff` theorems prove each property holds exactly when it does.",
        "`UnobservedEmergencyCallEnabledAlways`, in place of the lemma `Emergency_proof` dropped: stated of the "
        "frozen module's own `Next`, for every `Mut` and every `MaxRound`.",
        "Induction on reachable states, in place of LS4; kernel-checked and replayed "
        "(`TopakSpec-results-2026.10.07.txt`, `d365231c3ae3dd61`). **A theorem of the encoding, not of the frozen "
        "text**; its fidelity is read, and here also checked (right).",
    ]
    gcols = [("Module", 175), ("`Mut`", 160), ("States", 100), ("Edges", 110), ("Steps", 110),
             ("`ENABLED` invariants false in", 190)]
    gcols.append(("Result", w3 - sum(x[1] for x in gcols)))
    grows = []
    for r in gc:
        if r["enc"] is None:
            fl = "—"
        elif r["enc"] == r["ecwo"]:
            fl = f"{n_(r['enc'])} and {n_(r['ecwo'])}"
        else:
            fl = f"{n_(r['enc'])}; {n_(r['ecwo'])}"
        cells = [f"`{r['mod']}`", f"`{r['mut']}`", n_(r["states"]), n_(r["edges"]), f"{n_(r['steps'])} `{r['rel']}`",
                 fl, ("[[green|MATCH]]" if r["res"] == "MATCH" else f"[[red|{r['res']}]]")]
        grows.append({"cells": cells, "accent": "teal"} if r["mod"] == "Emergency_live" else cells)
    gintro = (f"**The encoding checked against TLC's state graphs** (ADR-0053 R6; `{gc_file}`, `a18bf90ba38eca61`). "
              "A MATCH: no edge that is not a step of the relation, no step that is not an edge or a stutter, the same "
              "initial states, and every property TLC's value in every state, the two over `ENABLED` included (— for "
              "`Emergency`, which does not state them). At `MaxRound = 2`.")
    gout = ("Under the two coupling mutations the two properties are false in the same states in TLC's graph and in "
            "the encoding. The mirror's theorems are proved; this run evaluates them on the graphs, a test.")
    gh1 = c.para(0, 0, w3, gintro, 13.5, draw=False)
    gh2 = c.table(0, 0, gcols, grows, size=13, draw=False)
    gh3 = c.para(0, 0, w3, gout, 13.5, draw=False)
    gtot = gh1 + 10 + gh2 + 10 + gh3
    h1 = c.card(0, 0, w1, f"`Emergency_live_proof.tla` · **proved, and certified**", tl, "teal", draw=False, size=14)
    h2 = c.card(0, 0, w2, "`spec/lean/TopakSpec/Emergency.lean` · proved in Lean, of the encoding", ll, "teal",
                draw=False, size=14, status="accepted", status_extra="ADR-0053 · B36 · T-0045-37")
    hh = max(h1, h2, gtot)
    c.card(xs[0], y, w1, f"`Emergency_live_proof.tla` · **proved, and certified**", tl, "teal", size=14, h=hh)
    c.card(xs[1], y, w2, "`spec/lean/TopakSpec/Emergency.lean` · proved in Lean, of the encoding", ll, "teal",
           size=14, h=hh, status="accepted", status_extra="ADR-0053 · B36 · T-0045-37")
    yy = y
    yy += c.para(xs[2], yy, w3, gintro, 13.5) + 10
    yy += c.table(xs[2], yy, gcols, grows, size=13, accent="teal") + 10
    c.para(xs[2], yy, w3, gout, 13.5, "muted")
    y += hh + 60

    # ================================================================ 5. Coupling_live
    y += c.heading(X0, y, "5 · Tier 1 item 1: the coupling stall ends: `Coupling_live` (ADR-0039 §2; ToO rev 15 "
                          "§5.5): **checked by TLC, not proved**", "blue", 21)
    pc = [("Property", 230, {"bold": True}), ("As `Coupling_live.tla` states it", 560),
          ("What it says (ADR-0039 §2)", 520), ("Quantified", 140), ("Fairness it needs", 300),
          ("TLC, K=1 R=3 MaxRound=2 and K=2 R=4 MaxRound=3", 300), ("At K = 0, the quarantine hold", 250)]
    pc.append(("What must break it, and what must not", W - sum(x[1] for x in pc)))

    def cl_v(name):
        return cl_res[name]

    def two(a, b):
        return verdict_cell(cl_v(a)) + (" at both" if cl_v(a) == cl_v(b) else f"; {verdict_cell(cl_v(b))}")
    y += c.table(X0, y, pc, [
        ["`AdmitStallEnds`", r"`(tLive /\ seq < R) ~> (~tLive \/ ENABLED Admit)`",
         "The stall in a round ends: a live Thinker below its round bound is eventually admissible, unless it ends "
         "its round first", "no", "A12 (`SpecA12`)", two("l-none-admit", "b-none-admit"),
         verdict_cell(cl_v("f-k0-admit")) + ": `K = 0` admits nothing (§1)",
         "**Broken by** `M_HBCOUPLED` (the Observer's own heartbeat needs `live(o)`) and `M_CORR` (the stall then "
         "waits on the correlator too, which A12 does not cover, §4). **Holds under** `M_HBLIVE` and `M_MARK`; "
         "`M_NOCOUPLE` removes the stall, and it holds with no fairness"],
        ["`GrantStallEnds`", r"`(~tLive /\ round < MaxRound) ~> ENABLED GrantT`",
         "R1: once a round has ended, a grant for the next eventually becomes possible: coverage reaches the seal",
         "no", "A12 (`SpecA12`)", two("l-none-grant", "b-none-grant"), verdict_cell(cl_v("k0-grant")),
         "**Broken by** `M_HBLIVE` (also at the larger constants; §6). **Holds under** `M_CORR` (the grant does not "
         "read the correlator), `M_MARK`, and `M_HBCOUPLED` only because no grant stall is reachable; `M_ROUNDS` "
         "removes the stall"],
        ["`AdmitsResume`", r"`\A n \in 0..R : (tLive /\ seq = n /\ n < R)` `~> (~tLive \/ seq > n)`",
         "The first as progress: the Thinker is admitted again, unless it ends its round first",
         "**yes**, over `n`", "A12 and `ThinkerAsks` (`SpecResume`)", two("l-none-resume", "b-none-resume"),
         verdict_cell(cl_v("f-k0-resume")), "**Broken by** dropping `ThinkerAsks` to weak fairness (`SpecWFAdmit`). "
         "**Holds under** `M_HBLIVE`"],
        ["`NextRoundGranted`", r"`\A r \in 0..MaxRound : (~tLive /\ round = r` `/\ r < MaxRound) ~> (round > r)`",
         "The second as progress: the next round is granted", "**yes**, over `r`", "A12 and `GrantsMade` (`SpecNext`)",
         two("l-none-next", "b-none-next"), verdict_cell(cl_v("k0-next")),
         "**Broken by** `M_HBLIVE` (also at the larger constants) and by dropping `GrantsMade` (`SpecNoGrant`). "
         "**Holds under** `M_HBCOUPLED`: no grant stall is reachable"],
    ], size=13.5, accent="blue") + 10
    y += c.para(X0, y, W, "ADR-0046 A2: \"Two of the four leads-to properties `Coupling_live.tla` states are "
                "quantified and all four have `ENABLED` premises.\" The two admit properties also need `K ≥ 1`; the two "
                "grant properties hold at `K = 0` as well (the module's header).", 14, "muted") + 34

    # fairness table + rejected
    fw = 1940
    fc = [("Condition", 200, {"bold": True}), ("Definition", 190), ("What it says, and whose obligation it is", 720),
          ("ToO §13", 100), ("Strength, and why", 380)]
    fc.append(("Dropped or weakened (TLC rows)", fw - sum(x[1] for x in fc)))
    frows = [
        ["`ObserverRegranted`", "`WF_vars(GrantO)`", "An Observer without a lease is granted its next round. The first "
         "grant is the mechanism's, on its seating's tally; every later one is an operator's successor grant, made "
         "with a live lease and a live peer (ADR-0031 A3; ADR-0050 §2, §4). **In part an assumption about "
         "operators.**", "A12", "Weak",
         "`SpecNoRegrant`: " + BREAK + " `AdmitStallEnds`, `GrantStallEnds`"],
        ["`ObserverKeepsUp`", "`SF_vars(KeepUp)`", "`KeepUp`: the heartbeat that reports a watermark within `K` of the "
         "Thinker's sequence while its round is live (§1, condition 3), and the seal once it has ended (§2, coverage): "
         "in some tenure, the Observer keeps up. A lease is granted for one round (ADR-0031 §2), so an Observer is "
         "without a lease between its rounds and its heartbeats stop there (ADR-0039 finding 3).", "A12",
         "**Strong**, because its lease may end first, so `KeepUp` is enabled only intermittently and weak fairness "
         "on it is not enough",
         "`SpecNoKeepUp`, `SpecWFKeepUp` (\"the lease ends before every heartbeat that keeps up\"), `SpecAnyBeat`: "
         + BREAK + " both stall properties"],
        ["`ThinkerAsks`", "`SF_vars(Admit)`", "The Thinker keeps asking, and not only while its Observer is stale or "
         "without a lease. Met jointly: by the Thinker's asking, by heartbeats within `T_obs`, and by how the operators "
         "lay out the Observer's rounds against the Thinker's (finding 3). Rounds that overlap need two cell Observers, "
         "since a principal holds one lease at a time.", "A18",
         "**Strong**, because `Stale` or `EndO` may follow every heartbeat that keeps up, so `Admit` is enabled only "
         "intermittently", "`SpecWFAdmit`: " + BREAK + " `AdmitsResume`"],
        ["`GrantsMade`", "`WF_vars(GrantT)`", "A grant that can be made is made. The Thinker asks for none: its first "
         "round is granted by the mechanism when its seating's tally completes, and every later round by an operator "
         "with a live lease and a live peer. **An assumption about people, declared as one.**", "A18", "Weak",
         "`SpecNoGrant`: " + BREAK + " `NextRoundGranted`"],
        {"cells": ["no name", "—", "**The ordering makes progress.** Every step these conditions name is one the "
                   "mechanism decides and orders (ADR-0033 §4), so each also assumes it.", "—",
                   "Declared (the plan's Tier 2)", "**Nothing models it**"], "accent": "grey"},
    ]
    fth = c.table(X0, y, fc, frows, size=13.5, accent="blue")
    a12 = ("**A12** (ToO rev 15 §13): \"Every Run Thinker's cell Observer keeps up: heartbeats within `T_obs`, "
           "watermark within `K`, coverage to each seal\". If it fails, nothing is lost to safety: the Thinker's admits "
           "and its next round stall, and a deployment that will not accept the stall declares D-0039-1. **A18**, new "
           "in revision 15: \"A refused Thinker asks again, and grants are made\". If it fails, the coupling stall may "
           "never end, and the leads-to properties that say it ends are void. G11 item 105 had found that §13 did not "
           "yet list these two.")
    fth += 10 + c.para(X0, y + fth + 10, fw, a12, 13.5, "muted")
    rx = X0 + fw + 30
    rej = c.card(rx, y, X1 - rx, "What the module did not assume, and why (its header; the plan)", [
        "**\"The lease is eventually held for good\"** would be simpler, \"and no one-Observer cell meets it\": its "
        "lease is for one round.",
        "**Fairness on any heartbeat**, which CR-37 proposed weak, \"is not enough even strong: a heartbeat that "
        "repeats an old watermark keeps the Observer fresh and never covers the backlog\" (`SpecAnyBeat`).",
        "**Weak fairness on `KeepUp` or on `Admit`** (`SpecWFKeepUp`, `SpecWFAdmit`): each action is enabled only "
        "intermittently, and each row breaks its property.",
        "**`Stale` restricted to \"no heartbeat since\"**: the plan offered it beside strong fairness on `Admit`. The "
        "module takes strong fairness, as `ThinkerAsks`; `Stale` is `Coupling.tla`'s, which is frozen.",
        "**Fairness only on actions of `NextL`**, \"so no choice of them can leave a spec with no behaviour\"; the "
        "`NoBehaviour` rows check it of each fair spec under which a row holds.",
    ], "red", size=14)
    y += max(fth, rej) + 40

    # the 69 rows as a matrix
    y += c.text(X0, y + 18, f"Every row of `Coupling_live-rows.txt`, by configuration ({cl_file}: "
                f"{cl_sum.replace(' · ERROR: none', '')})", 17, "blue", bold=True) or 34
    FAIR = {"SpecA12", "SpecResume", "SpecNext", "SpecFull"}

    def variant(spec):
        return "fair" if spec in FAIR else spec
    vdesc = {
        "SpecL": "no fairness: `SpecL`, `Coupling`'s `Spec`",
        "fair": "the conditions each property needs; must-break rows under all (`SpecFull`)",
        "SpecNoRegrant": "`ObserverRegranted` dropped",
        "SpecNoKeepUp": "`ObserverKeepsUp` dropped",
        "SpecWFKeepUp": "weak fairness on `KeepUp` in place of strong",
        "SpecAnyBeat": "strong fairness on any heartbeat in place of `KeepUp`'s",
        "SpecWFAdmit": "weak fairness on `Admit` in place of strong",
        "SpecNoGrant": "`GrantsMade` dropped",
    }
    mdesc = {
        "none": "unmutated",
        "M_HBLIVE": "`M_HBLIVE`: the Observer heartbeats only while its Thinker's lease is live",
        "M_HBCOUPLED": "`M_HBCOUPLED`: the Observer's own heartbeat needs `live(o)`",
        "M_CORR": "`M_CORR` (`Coupling`'s): the correlator coupled",
        "M_MARK": "`M_MARK` (`Coupling`'s): tests heartbeat time, not watermark",
        "M_NOCOUPLE": "`M_NOCOUPLE` (`Coupling`'s): the check dropped",
        "M_ROUNDS": "`M_ROUNDS` (`Coupling`'s): coverage not carried across rounds",
    }
    keys = []
    for r in cl_rows:
        k = (r["mut"], variant(r["spec"]), r["consts"])
        if k not in keys:
            keys.append(k)
    groups = [("Unmutated", lambda k: k[0] == "none" and k[1] in ("SpecL", "fair")),
              ("Each condition dropped or weakened, the others kept (unmutated)",
               lambda k: k[0] == "none" and k[1] not in ("SpecL", "fair")),
              ("The two liveness mutations", lambda k: k[0] in ("M_HBLIVE", "M_HBCOUPLED")),
              ("`Coupling`'s own mutations", lambda k: k[0] in ("M_CORR", "M_MARK", "M_NOCOUPLE", "M_ROUNDS"))]
    LP = ["AdmitStallEnds", "GrantStallEnds", "AdmitsResume", "NextRoundGranted"]
    mcols = [("Configuration", 470), ("Fairness", 430), ("`Safe`", 190), ("Deadlock check on", 170),
             ("Witnesses (each must be reached)", 520)]
    mcols += [(f"`{p}`", 200) for p in LP]
    mcols.append(("Has a behaviour", 130))
    mcols.append(("Rows", W - sum(x[1] for x in mcols)))
    mrows = []
    nrows = 0
    morder = ["none", "M_HBLIVE", "M_HBCOUPLED", "M_CORR", "M_MARK", "M_NOCOUPLE", "M_ROUNDS"]
    for gname, pred in groups:
        mrows.append({"group": gname, "accent": "blue"})
        for k in sorted([k for k in keys if pred(k)], key=lambda k: (morder.index(k[0]), keys.index(k))):
            rs = [r for r in cl_rows if (r["mut"], variant(r["spec"]), r["consts"]) == k]
            nrows += len(rs)

            def find(prop, kind=None):
                return [r for r in rs if r["prop"] == prop and (kind is None or r["kind"] == kind)]
            cell = {}
            s = find("Safe", "INVARIANT")
            cell["safe"] = verdict_cell(cl_res[s[0]["name"]], states=s[0]["states"]) if s else "—"
            d = find("Safe", "DEADLOCK")
            cell["dl"] = ("[[green|no terminal state]]" if cl_res[d[0]["name"]] == "HOLDS" else "[[red|deadlock]]") \
                if d else "—"
            wit = [r for r in rs if r["prop"].startswith("Never")]
            if wit:
                reached = [r["prop"] for r in wit if cl_res[r["name"]] == "VIOLATED"]
                missed = [r["prop"] for r in wit if cl_res[r["name"]] == "HOLDS"]
                if not missed:
                    cell["w"] = f"all {len(wit)} reached"
                else:
                    cell["w"] = ("reached: " + ", ".join(f"`{p}`" for p in reached) + "; [[red|not reached]]: "
                                 + ", ".join(f"`{p}`" for p in missed))
            else:
                cell["w"] = "—"
            lp = []
            for p in LP:
                f = find(p)
                if not f:
                    lp.append("—")
                    continue
                r = f[0]
                sp = r["spec"] if k[1] == "fair" else None
                lp.append(verdict_cell(cl_res[r["name"]], sp, r["states"]))
            nb = find("NoBehaviour")
            cell["nb"] = ("yes" if cl_res[nb[0]["name"]] == "VIOLATED" else "[[red|none]]") if nb else "—"
            lab = mdesc[k[0]] + (f" · `{k[2]}`" if k[2] else "")
            fair = vdesc[k[1]] if k[1] in vdesc else f"`{k[1]}`"
            if k[1] != "fair" and k[1] != "SpecL":
                fair = f"`{k[1]}`: " + fair
            cells = [lab, fair, cell["safe"], cell["dl"], cell["w"], *lp, cell["nb"], str(len(rs))]
            mrows.append({"cells": cells, "accent": "red"} if k[0] == "M_HBLIVE" else cells)
    if nrows != len(cl_rows):
        raise SystemExit("Coupling_live matrix lost a row")
    mrows.append({"cells": ["**All rows**", "", "", "", "", "", "", "", "", "", f"**{nrows}**"], "accent": "grey"})
    y += c.table(X0, y, mcols, mrows, size=13, accent="blue") + 10
    y += c.para(X0, y, W, "Witnesses: `Coupling`'s four, `NeverRoundTwo`, `NeverRefused`, `NeverStaleRefusal` and "
                "`NeverBacklogRefusal`, and the module's three: `NeverRoundTwoAfterReading` (a round that admitted "
                "something, read to its seal and followed), `NeverBacklogRefusalStep` (a refusal for the backlog, as a "
                "step) and `NeverAdmitted`. \"Has a behaviour\": `NoBehaviour == <>FALSE` is violated, so the fair "
                "spec is not vacuous. One worker and a fixed fingerprint function, so a liveness counterexample is the "
                "same on every run (spec/README.md).", 13.5, "muted") + 30

    # checked, not proved
    cols = even(X0, X1, 2, 30)
    h = row_of_cards(c, y, [
        (*cols[0], "What TLC's rows are evidence of", [
            f"**Checked**: {cl_sum.replace(' · ERROR: none', '')} ({cl_file}).",
            "At small constants only: K=1, R=3, MaxRound=2 (1,124 states) and K=2, R=4, MaxRound=3 (11,908); one "
            "Thinker, its cell Observer and one correlator.",
            "\"A leads-to property checked by TLC is checked at small constants\" (G11 §3, \"What these checks are\").",
            "Each fairness condition is dropped or weakened in a row that must break, and each mutation that must "
            "break a property has a row that does: the method of the invariants, kept.",
        ], "blue", {}),
        (*cols[1], "`Coupling_live_proof.tla`: the safety is proved, the liveness is not", [
            r"**Proved**, for every K, R and MaxRound in Nat: `SpecLImpliesSpec == SpecL => Spec` under every `Mut`; "
            "`NoAdmitWithoutLiveObserverAlwaysL`, `UnreadBoundedAlwaysL`, `CorrelatorNeverGatesAlwaysL`, each under "
            "the hypothesis it has in `Coupling_proof`; `SafeAlwaysL` under `none`, `M_HBLIVE`, `M_HBCOUPLED`.",
            f"**Certified** ({cc['file']}): {cc['n']} obligations: {cc['triv']} trivial, {cc['smt']} SMT accepted by "
            f"`ethos`, **{cc['ls4']} LS4**, which no checker confirms.",
            "Nothing in it uses fairness: a theorem about `SpecL` holds of every fair spec, since each adds "
            "conjuncts to it.",
            "[[red|Not proved: the four leads-to properties.]] They are owed, with `K ≥ 1` a hypothesis of the two "
            "admit properties (G11 §7 item 105; §8: \"No liveness is proved\").",
        ], "red", {"status": "open", "status_extra": "the four proofs owed"}),
    ])
    y += h + 60

    # ================================================================ 6. M_HBLIVE
    y += c.heading(X0, y, "6 · `M_HBLIVE`: every safety check and every witness pass, and only a leads-to property "
                          "catches it (G11 §3 result 8; ToO §5.5, §11.3)", "red", 21)
    y += c.para(X0, y, W, "**The mutation** (`Coupling_live.tla`): `HeartbeatL(r, w)` adds `Mut # \"M_HBLIVE\" \\/ "
                "tLive` to `Heartbeat`, so an Observer may heartbeat only while its Thinker's lease is live. **The trace** "
                f"is TLC's counterexample to `GrantStallEnds` under `SpecFull`, every fairness condition on (row "
                f"`m-hblive-grant`, {tr_file}), read at build time: {len(trace)} states, then back to state "
                f"{back[0]} by `{back[1]}`, for ever. Shown: the variables that move.", 14) + 14
    show = [("round", "round"), ("tLive", "tLive"), ("oLease", "oLease"), ("fresh.o", "fresh"), ("seq", "seq"),
            ("mark[1]", "mark"), ("seal[1]", "seal"), ("refused", "refused")]

    def val(st, key, var):
        v = st[var]
        if var == "fresh":
            m = re.search(r"o \|-> (\w+)", v)
            return m.group(1)
        if var in ("mark", "seal"):
            return v.strip("<>").split(",")[0].strip()
        return v
    gap = 46
    sw = (W - (len(trace) - 1) * gap) / len(trace)
    bodies = []
    prev = None
    for i, (act, st) in enumerate(trace):
        lines = []
        for key, var in show:
            v = val(st, key, var)
            changed = prev is not None and val(prev, key, var) != v
            lines.append(f"[[teal|{key} = {v}]]" if changed else f"`{key} = {v}`")
        bodies.append(lines)
        prev = st
    accs = []
    for i, (act, st) in enumerate(trace):
        if i + 1 >= back[0]:
            accs.append("red")
        elif act == "EndRoundT":
            accs.append("blue")
        else:
            accs.append("grey")
    subs = [("initial" if a == "Initial" else f"by `{a}`") for a, _ in trace]
    sh = max(c.card(0, 0, sw, f"State {i + 1}", b, "grey", draw=False, size=13.5, tsize=15, sub=s, bullets=False,
                    pad=12) for i, (b, s) in enumerate(zip(bodies, subs)))
    sy = y
    for i, (b, s, a) in enumerate(zip(bodies, subs, accs)):
        bx = X0 + i * (sw + gap)
        c.card(bx, sy, sw, f"State {i + 1}", b, a, size=13.5, tsize=15, sub=s, bullets=False, pad=12, h=sh)
        if i:
            c.arrow([(bx - gap, sy + sh / 2), (bx, sy + sh / 2)], "grey")
    # the lasso: from the last state back to state `back`
    lx = X0 + (len(trace) - 1) * (sw + gap) + sw / 2
    bx8 = X0 + (back[0] - 1) * (sw + gap) + sw / 2
    ly = sy + sh + 40
    c.arrow([(lx, sy + sh), (lx, ly), (bx8, ly), (bx8, sy + sh)], "red", sw=2.4,
            label=f"`{back[1]}`: back to state {back[0]}, for ever", lpos=0.5)
    y = ly + 34
    cols = even(X0, X1, 3, 28)
    h = row_of_cards(c, y, [
        (*cols[0], "What the trace shows", [
            "States 1–6: round 1 is granted, the Observer leased, the Thinker refused (the Observer stale), the "
            "Observer heartbeats at watermark 0, and one effect is admitted: `seq` = 1, `mark[1]` = 0.",
            "State 7: `EndRoundT` seals round 1 at 1. **The round ends unread.**",
            "States 8–9: `tLive` = FALSE, so under `M_HBLIVE` no heartbeat is enabled and `mark[1]` stays 0 "
            "below `seal[1]` = 1: **never read**. `GrantT` asks `mark[round] >= seal[round]` (`Coupling.tla` §2) and "
            "is never enabled: **round 2 is never granted**.",
            "The Observer's lease toggles, `EndO` and `GrantO`, so every state has a successor. Unmutated, the same "
            "prefix ends: row `l-none-grant` holds.",
        ], "red", {}),
        (*cols[1], "What every other check sees under `M_HBLIVE`", [
            f"`Safe` {verdict_cell(cl_res['s-hblive-safe'])}, on all of `Coupling`'s 1,124 states: \"no invariant "
            "over the variables can tell `M_HBLIVE` from none\" (the rows file).",
            "Every witness is reached, `NeverRoundTwoAfterReading` among them: some behaviours read round 1 to its "
            "seal before it ends.",
            "TLC's deadlock check, on: no terminal state (`d-hblive-deadlock`).",
            "`AdmitStallEnds` and `AdmitsResume` hold. **`GrantStallEnds` and `NextRoundGranted` break**, also at "
            "K=2, R=4, MaxRound=3.",
            "`Coupling_live_proof` proves `SafeAlwaysL` under `M_HBLIVE`: the safety theorems are true of it.",
        ], "grey", {}),
        (*cols[2], "Why it is worth the cost (the plan)", [
            "\"Here is a mutation that the current method would miss.\" Every safety property passes; several run "
            "scripts also pass `-deadlock`. \"Only a leads-to property catches this.\"",
            "ToO §5.5: only a leads-to property sees it, \"and that is the case for stating them\".",
            "Its twin, `M_HBCOUPLED`, is caught twice: it breaks `AdmitStallEnds`, and it admits nothing, so "
            "`Coupling`'s own witness run catches it too (`NeverAdmitted` holds).",
        ], "teal", {}),
    ])
    y += h + 60

    # ================================================================ 7. why the proof is owed
    y += c.heading(X0, y, "7 · Why the proof is owed, and why it is hard (ADR-0046 A2; Coupling_live_proof.tla's "
                          "header; ToO §5.5)", "ink", 21)
    cols = even(X0, X1, 4)
    h = row_of_cards(c, y, [
        (*cols[0], "What a proof of a leads-to needs", [
            "A WF1 or SF1 step on a decreasing measure, such as `seal[r] − mark[r]` or `seq − mark` (the plan's "
            "route).",
            "That step needs **a quantified leads-to hypothesis inside the proof**, which `PTL` cannot combine from "
            "instances.",
            "spec/README.md: \"A liveness property also needs a variant and a WF1-shaped proof; for `Coupling_live` "
            "it is owed.\"",
        ], "grey", {}),
        (*cols[1], "The prover's two known unsound cases (T-0045-31; Batch 37)", [
            r"**First: a term under a binder.** tlapm 7824dab hands SMT, Zenon and Isabelle an untranslated term, an "
            r"unexpanded `ENABLED` or `\cdot` or a temporal formula, as an opaque constant that does not depend on any "
            "variable bound around it, so a false statement can prove and certify.",
            "Among those that certify: a universal temporal statement from a true one-instance lemma, and "
            "`Spec => []P` for a quantified `P` from a true `Spec => []P'`. **No check detects this case** (G11 item "
            "104).",
            "**Second: two terms with one name**, by a 20-bit hash tlapm does not check; `FALSE` proves and "
            "certifies through SMT and through `PTL`.",
            "No result in the 24 proof modules rests on either (`proof-scan-results-2026.10.08.txt`).",
        ], "red", {"status": "accepted", "status_extra": "ADR-0046 A2 · C2 · B37"}),
        (*cols[2], "The four have the first case's shape", [
            "**Two of the four are quantified**: `AdmitsResume` over `n`, `NextRoundGranted` over `r`.",
            "**All four have `ENABLED` premises** (ADR-0046 A2).",
            "So a TLAPS proof would put the very terms the first case drops a bound variable from under the "
            "binders a measure step needs.",
            "In TLAPS, **no route for a measure step under the rule is known yet**.",
        ], "red", {}),
        (*cols[3], "The rule, and the other route", [
            "**The rule** (`spec/proof-certification.md` §10): in a step SMT, Zenon or Isabelle discharges, no "
            "untranslated term may mention a variable bound in the obligation. A temporal property of a parameter is "
            "a hidden definition, `LT(n) == ...`, expanded only in a `PTL` step; an `ENABLED` goal is proved by "
            "expanding it in its own step.",
            "`Emergency_live_proof` is written so: each `ENABLED` goal is expanded in the one step that proves it.",
            "**Lean (ADR-0053)**: \"A proof of them in Lean cannot meet either case.\" The plan put Lean later, "
            "because its packages would first need a model of infinite behaviours and fairness.",
        ], "teal", {}),
    ])
    y += h + 60

    # ================================================================ 8. what is not stated
    y += c.heading(X0, y, "8 · What is not stated: Tier 1 items 2–5, each unmodelled (ToO rev 15 §5.5; G11 §7 item "
                          "105)", "red", 21)
    cols = even(X0, X1, 4)
    h = row_of_cards(c, y, [
        (*cols[0], "2 · The Build promotion stall resolves (ADR-0024 §2, A2.3)", [
            "Under the two weak-fairness assumptions ADR-0024 already states, on `Vote` and on the Observer's lease "
            "and coverage, a gated round that no seat denies eventually promotes.",
            "**The missing premise: the rules epoch eventually stops changing.** Every epoch change voids votes in "
            "flight, so repeated fences can starve a promotion forever. A proof will force it, and the corpus does "
            "not have it (ToO §12 item 21).",
            "Belongs in the still-owed bootstrap `Promotion` module.",
            "The reference's e2e shows one stalled promotion completed by a heartbeat (CR-37): a run, not a "
            "property.",
        ], "red", {"status": "open", "status_extra": "not stated · a premise missing"}),
        (*cols[1], "3 · Every ended lease eventually yields a seal", [
            "Expiry (I15, proposed as `EndRound(Expired)` and ordered), revocation and fence.",
            "The grant guard reads `seal[r]`, so **a seal that never lands is a silent deadlock of the next round**.",
            "Assumes consensus progress (Tier 2).",
        ], "red", {"status": "open", "status_extra": "not stated"}),
        (*cols[2], "4 · A lapsed operator is eventually re-seated by a quorum", [
            "ADR-0050 (provisional): a domain without an operator waits.",
            "Lower priority: the stall is declared, and resolving it rests on people.",
        ], "red", {"status": "open", "status_extra": "not stated"}),
        (*cols[3], "5 · Detection eventually happens", [
            "Under fairness on the correlator's fold, each correlator's watermark eventually passes every send, so "
            "`CarriedCoversSplitPath` eventually applies (ADR-0051, Proposed).",
            "Useful but advisory, since detection can only subtract.",
        ], "red", {"status": "open", "status_extra": "not stated"}),
    ])
    y += h + 60

    # ================================================================ 9. the deadlock audit
    y += c.heading(X0, y, f"9 · The `-deadlock` audit: what the flag hides ({au_file}, `f1d55bccc100481e`; G11 §3; "
                          "ToO §11.3)", "ink", 21)
    cols = even(X0, X1, 3, 28)
    h = row_of_cards(c, y, [
        (*cols[0], "What a line claims", [
            "Every run script listed passes `-deadlock`, which turns off TLC's report of a state with no successor. "
            "Each line is one module at one set of constants, unmutated, through a wrapper that `EXTENDS` it and adds "
            "only definitions, so the state graph is the module's own.",
            "TLC checks `NotTerminal` (`Terminal == ~ENABLED` of the next-state relation) and, where that is "
            "violated, `TerminalAtBound`: every terminal state is at the module's own end.",
        ], "grey", {}),
        (*cols[1], "What it does not claim", [
            "Nothing at other constants, where an end can fall elsewhere, nor under a mutation, whose rows may stop "
            "anywhere.",
            "**Not that the module never stalls**: a state whose only step leaves it unchanged has a successor, for "
            "`ENABLED` as for TLC's check. Nor a livelock: `Coupling_live` has no terminal state, nor under "
            "`M_HBLIVE` (its row `d-hblive-deadlock`).",
            "Not run: `Operators` at three operators (more than 91,597,194 states after 40 minutes, none terminal). "
            "That none is terminal there is a reading of `Operators.tla`, not a check.",
        ], "red", {}),
        (*cols[2], "Result", [
            "**" + re.sub(r" · ERROR: \w+", "", au_sum).replace("STRAY DEADLOCK: 0", "stray deadlock: 0") + "**.",
            "Where there are terminal states, every one is at the bound its line names: the flag turns off the report "
            "of the module's end and hides nothing else. Elsewhere the flag is inert.",
            "**No stray deadlock was found** (spec/README.md; G11 §3).",
        ], "green", {}),
    ])
    y += h + 24
    half = (W - 30) / 2
    acols = [("Module", 270, {"bold": False}), ("Constants", 560), ("States", 130)]
    acols.append(("Terminal states", half - sum(x[1] for x in acols)))

    def arow(r):
        mod, consts, states, res = r
        if res == "no terminal state":
            rc = "[[green|none]]"
        else:
            m = re.match(r"every terminal state at the bound: (.+)$", res)
            rc = ("at the bound: `" + m.group(1) + "`") if m else f"[[red|{res}]]"
        cells = [f"`{mod}`" if " " not in mod else f"`{mod.split(' ')[0]}` " + " ".join(mod.split(" ")[1:]),
                 consts.replace(" · ", "; "), n_(states), rc]
        return {"cells": cells, "accent": "blue"} if mod.endswith("(SpecL)") else cells
    k = (len(audit) + 1) // 2
    h1 = c.table(X0, y, acols, [arow(r) for r in audit[:k]], size=12.5, accent="grey")
    h2 = c.table(X0 + half + 30, y, acols, [arow(r) for r in audit[k:]], size=12.5, accent="grey")
    y += max(h1, h2) + 50

    # ================================================================ legend
    c.legend(X0, y, [
        ("box", "teal", "proved; certified; proved in Lean"),
        ("box", "blue", "checked by TLC; the extension"),
        ("box", "red", "not proved; unmodelled; a mutation; a gap", "6 4"),
        ("box", "grey", "frozen base; neutral", "7 4"),
        ("box", "green", "already safety; holds; no stray deadlock"),
        ("arrow", "grey", "EXTENDS"),
    ])
    return c
