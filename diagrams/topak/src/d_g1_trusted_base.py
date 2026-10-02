"""G1 — The trusted base: the admission rule, three classes and a refusal, and all thirty-one rows (ADR-0045)."""
import pathlib
import re

from lib import strip_external, Canvas

ID, SLUG = "G1", "trusted-base"

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "decisions" / "ADR-0045.md").exists()), _HERE.parents[3])
ADR = ROOT / "decisions" / "ADR-0045.md"

# Row tint by class (ADR-0045 §2). Green: delegated (subtract-only); blue: trust root (identity issued
# or promoted); grey: excluded (trusted for nothing). Refused components are not rows.
CLASS_ACC = {"delegated": "green", "trust root": "blue", "excluded": "grey"}


# ---------------------------------------------------------------------------------------------
# The tables are read from the record itself, so the diagram cannot drift from ADR-0045's text.

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


def _clean(s, keep_struck=False):
    """Markdown cell -> lib rich text. Struck text (superseded by a dependent entry) is dropped, or
    kept as a 'was …' note when keep_struck is set."""
    s = s.strip()
    if keep_struck:
        def was(m):
            old = re.sub(r"[*`]", "", m.group(1)).strip()
            return f"[[grey|was: {old}]] → "
        s = re.sub(r"~~(.+?)~~\s*", was, s)
    else:
        s = re.sub(r"~~(.+?)~~\s*", "", s)
    s = _boldfix(s)
    s = re.sub(r"(?<![*\w])\*(?!\*)([^*]+?)(?<!\*)\*(?![*\w])", r"\1", s)   # single-asterisk italics
    return s.strip()


def _class_cell(s):
    """Class column: show a post-ratification change as 'new · was old'."""
    m = re.match(r"~~(.+?)~~\s*(.+)", s.strip())
    if m:
        old = re.sub(r"[*`]", "", m.group(1)).strip()
        return _clean(m.group(2)) + f"\n[[red|was {old}]]"
    return _clean(s)


def _tables(text):
    """-> list of (heading line before the table, [rows]) for every markdown table in text."""
    out, cur, head, prev = [], None, None, ""
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c for c in line.strip().strip("|").split("|")]
            if cur is None:
                cur, head = [], prev
            if set(line.replace("|", "").strip()) <= set("-: "):
                continue
            cur.append(cells)
        else:
            if cur is not None:
                out.append((head, cur))
                cur = None
            if line.strip():
                prev = line.strip()
    if cur is not None:
        out.append((head, cur))
    return out


def _klass(cls_cell):
    c = re.sub(r"[*~]", "", cls_cell).lower()
    if "~~" in cls_cell:
        c = re.sub(r"~~.+?~~", "", cls_cell).lower()
    c = c.strip()
    for k in ("trust root", "delegated", "excluded"):
        if c.startswith(k):
            return k
    return "trust root" if "trust root" in c else "excluded"


def build():
    text = strip_external(ADR.read_text(encoding="utf-8"))
    annex_a_text = text.split("## Annex A")[1].split("## Annex B")[0]
    annex_b_text = text.split("## Annex B")[1].split("## History")[0]
    sec1 = text.split("### 1. A row has a fixed schema")[1].split("### 2.")[0]
    sec6 = text.split("### 6. The rule applied")[1].split("### 7.")[0]

    c = Canvas(ID, "The trusted base: a component enters only if its failure can only subtract, or its identity is issued",
               "ADR-0045 (Accepted (genesis) 2026.10.01, Batch 22, confirmation required C2 and C4) declares the trusted "
               "base row by row: a fixed schema, three classes and a refusal, thirty-one archetype rows in five groups "
               "(Annex A), and the reference's own declaration (Annex B), with the two rows that changed class after "
               "ratification and the one added since: T-0045-31, the TLA+ Proof System (B25, ADR-0046 §3). Tables "
               "below are drawn in full from the record; where the code has moved past Annex B (G9 §2.6, pending "
               "ADR-0033 A7 and ADR-0034 A2), the row's note says so.",
               3600, "ADR-0045 §1–§9, Findings 1–7, Annex A, Annex B, History (R1–R6, B22, B23, B24, B25); ADR-0046 §1–§3 (B25); "
               "ADR-0015 (authority "
               "changes); ADR-0023 §4a, §6a, §6b; ADR-0025 §1; ADR-0030 A1 (B24); ADR-0033 A6 (B23), A7 and A8 "
               "(pending); ADR-0034 §5, §6, A2 (pending); ADR-0036 §5, §6; G8 §2.6; "
               "G9 §1.1, §2.3, §2.6, §2.7, §2.9, §3, §7 items 35, 56, 57, 64, 67, 69, 73, 74, 80, 81, §8; "
               "ToO rev 13 §7.9; spec/theorem-premise-binding.md (BASE paragraph; 43 rows, revised 2026.10.02 "
               "pending A7 and A2)")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---- status band
    sx = X0
    sx += c.status(sx, y, "accepted", "C2, C4 · Batch 22, 2026.10.01") + 12
    c.text(sx, y + 16, "Annexes A and B are **declaration records** under ADR-0023, ratified with the record as "
                       "record-level entries; **no deployment declaration has been written** (G9 §8). Drafted by the "
                       "assistant at the custodian's request; every drafter's choice settled by ratification.", 14.5, "muted")
    y += 48

    # ======================================================================== top: rule + flow | schema + §6
    LW = 1560
    RX = X0 + LW + 60
    RW = X1 - RX

    # -- left: the rule
    ly = y
    ly += c.heading(X0, ly, "§2 · The admission rule", "blue")
    h = c.card(X0, ly, LW, "A component is a row only if its failure can only subtract, or its identity is issued", [
        "**\"Adds authority\" has an exact meaning** (Context, from ADR-0015: authority changes are exactly promotion and "
        "anchor issuance, “changes to the rules in force”). It is one of three things, and nothing else counts:",
        "**(1)** an admit the rules in force would refuse · **(2)** a promotion the tally would stall · **(3)** an "
        "issuance the rules floor would reject.",
        "Break-glass is not an addition: it happens within the rules in force.",
        "**Subtractions** (ADR-0031 §5): a denial, a lapsed lease, an ended round, a revocation, an epoch fence, a "
        "stalled promotion, lost evidence.",
    ], accent="blue", size=14.5)
    ly += h + 30

    # -- left: the decision flow
    ly += c.heading(X0, ly, "The classes as a decision (§2; the order of the questions is the diagram's)", "ink", 17)
    QW, OW = 600, 640
    qx, ox = X0, X0 + QW + 180
    q1 = ly + 6
    nodes = []

    def q(yq, title, body):
        hh = c.card(qx, yq, QW, title, body, accent="grey", bullets=False, size=14)
        return hh

    def out(yo, title, body, acc, dash=None, hh=None):
        return c.card(ox, yo, OW, title, body, accent=acc, bullets=False, size=14, dash=dash, h=hh)

    h0 = c.card(qx, q1, QW, "A component the deployment relies on", [
        "A program, a device, a person, a store or a value (§1, Component)."], accent="brown", bullets=False, size=14)
    y1 = q1 + h0 + 56
    h1 = q(y1, "Is it trusted for anything?", ["Does any theorem take a premise from it (its Trusted for "
                                              "sentence, a premise node, §3)?"])
    o1h = out(y1, "Excluded", ["Relied on in practice and trusted for **nothing**. The row exists so every theorem "
                               "premised on it is **computed void**, not silently assumed (§3 rule 1). Examples: "
                               "T-0045-13 gate runner, 22 host at rung 0, 23 native tool, 24 Run channel."], "grey")
    y2 = y1 + max(h1, o1h) + 56
    h2 = q(y2, "Can its failure add authority?", ["Can the worst it yields be one of the three additions, rather "
                                                 "than a subtraction (Failure can produce)?"])
    o2h = out(y2, "Delegated", ["Its failure can only subtract. **No proof, no key, no quorum**; may be commodity "
                                "substrate; declared per deployment, reopens nothing (ADR-0034 §5's delegation test, "
                                "met four times in the corpus). Examples: T-0045-4 clock, 5 Kafka, 6 bundle engines, 7 "
                                "archive."], "green")
    y3 = y2 + max(h2, o2h) + 56
    h3 = q(y3, "Is its identity fixed, and did it enter by its own record?", [
        "**Both**: identity fixed by an anchor issuance (a key under ADR-0025 §1 (c) or (f), a roster under (a) or "
        "(b)) or by a promotion (an artifact named by digest), so replacing it is an authority change; **and** it "
        "entered by a record of its own (ADR-0023's non-increasing-TCB rule)."])
    o3h = out(y3, "Trust root", ["Trusted although its failure can add. Its **residual is what its holder can do while "
                                 "the identity stands**. Model: ADR-0034 §2's verifier (T-0045-17). Examples: T-0045-1 "
                                 "replicas, 2 signature, 3 Cedar engine, 28–30 what runs, 31 the prover."], "blue")
    y4 = y3 + max(h3, o3h) + 56
    h4 = c.card(qx, y4, QW, "Refused: not a row", [
        "Either it moves **inside the verified object**, where it is checked and not trusted, or the design changes "
        "until its failure can only subtract. Applied in §6: **trusted time** refused; **the solver** refused, and "
        "the proof checker that replaced it is a trust root (B24)."], accent="red", bullets=False, size=14,
        tint=True, dash="6 4")
    ly = y4 + h4

    cx = qx + QW / 2
    c.arrow([(cx, q1 + h0), (cx, y1)], "ink")
    c.arrow([(cx, y1 + h1), (cx, y2)], "ink", label="yes", loff=(0, 0))
    c.arrow([(cx, y2 + h2), (cx, y3)], "ink", label="yes")
    c.arrow([(cx, y3 + h3), (cx, y4)], "red", label="no", dash="7 5")
    for yy, acc, lab in ((y1, "grey", "no"), (y2, "green", "no: subtract only"), (y3, "blue", "yes, both")):
        c.arrow([(qx + QW, yy + 40), (ox, yy + 40)], acc, label=lab)

    # -- right: §1 schema (full) and §6 candidates (full)
    ry = y
    ry += c.heading(RX, ry, "§1 · A row has a fixed schema", "blue")
    t1 = [t for t in _tables(sec1)][0][1]
    rows = [[f"**{_clean(r[0]).strip('*')}**", _clean(r[1])] for r in t1[1:]]
    ry += c.table(RX, ry, [("Field", 300), ("Content", RW - 300)], rows, size=13.5, accent="blue") + 14
    ry += c.para(RX, ry, RW, "Custody is not a field: it is a pointer to a custody declaration (ADR-0025's annex or "
                 "the deployment's), placed in Identity fixed by.", 14, "muted") + 26

    ry += c.heading(RX, ry, "§6 · The rule applied to the 09.28 prioritization's eight candidates", "blue")
    t6 = _tables(sec6)[0][1]
    rows = []
    for r in t6[1:]:
        cls = _clean(r[1], keep_struck=False)
        acc = "red" if "refused" in cls.lower() and "trust root" not in cls.lower() else None
        if "not a row" in cls.lower():
            acc = "teal"
        cells = [f"**{_clean(r[0])}**", cls, _clean(r[2])]
        rows.append({"cells": cells, "accent": acc} if acc else cells)
    ry += c.table(RX, ry, [("Candidate", 420), ("Class", 400), ("Why", RW - 820)], rows, size=13.5, accent="blue")
    ry += 12
    ry += c.para(RX, ry, RW, "**Also sorted:** the gate runner (G8) is refused as delegated and admissible as a trust "
                 "root once its evidence is signed under a key in issued rules (ADR-0025 §1 (f)); until then T-0045-13 "
                 "is **excluded** and gate evidence is an operator's assertion (I18; G9 item 57). The rung-1 launcher is "
                 "a trust root by ADR-0036 §5's own list; the launcher in the node is **built**, pending ADR-0033 A7 "
                 "(G9 item 35), and gives T-0045-19 and T-0045-20 a rung-1 instance (G9 §2.6).", 14, "ink")

    y = max(ly, ry) + 50

    # ======================================================================== §3, §4, §5, §8 band
    w4 = (X1 - X0 - 3 * 24) / 4
    cards = [
        ("§3 · Rows are premise nodes", [
            "**An undeclared row is false**: a deployment sits below every theorem whose premises include it.",
            "**Type changes are rows**: an ADR-0023 §4a degeneracy changes a row's class or rung range; §6b's field is "
            "a list of row ids (amendment owed, G9 item 64).",
            "**Membership per rung is the Rungs column**; the per-round slice (ADR-0031 §6) is derived from the lease.",
            "The binding table exists: `spec/theorem-premise-binding.md` (R6), **43 rows** at G9, revised pending "
            "A7 and A2 (G9 §2.6). At R6, three rows no theorem cited: T-0045-7, 21, 26. Since B25 the rows with a "
            "proof module (38 at G9) rest on **T-0045-31** for the invariant, in place of T-0045-29 (ADR-0046 §5).",
        ], "teal", None),
        ("§4 · Changing the table has a direction", [
            "**Removing** a row, or trust root → delegated: a tightening; an ordinary promotion (archetype version at "
            "archetype level).",
            "**Adding** a row, or delegated → trust root: a relaxation; its own record, and an issuance where it names "
            "a key (ADR-0034 added T-0045-17, ADR-0044 T-0045-27).",
            "**A deployment instantiates rows; it does not add them.** Trusting more is a §4a degeneracy with a D-row "
            "citing the T-row.",
            "Annex A carries its archetype version; non-increasing TCB is checked row set against row set.",
        ], "blue", None),
        ("§5 · The verified object is the specification; what runs is a row", [
            "Admit path, linked floor, `Authentic`, tally, rules floor, log: **checked as specified** (TLA+ with "
            "mutations at small constants, floor gates, tests) and not trusted.",
            "**Since B25 (ADR-0046)** the modules' invariants are **proved** with TLAPS, for every constant their "
            "assumptions admit: fifteen proof modules at G9, 3,036 obligations (G9 §2.9). The prover is trust root "
            "**T-0045-31**, and TLC (T-0045-29) keeps the mutations and witnesses.",
            "**What runs is not the specification** (R1): no refinement from TLA+ to Rust, an asserted build. Hence "
            "trust roots **T-0045-28 to 30** for every deployment; a proof is of the module, not of what runs.",
            "**A debt, owned by ADR-0033** (R2): the rows leave when a machine-checked chain is cited. Stage 1, trace "
            "validation, exists (R4), and since G9 reads every traced state against the abstract confinement "
            "invariants (A7, A8 pending); stages 2–3 open (G9 item 56).",
        ], "teal", None),
        ("§8 · D-0045-1: no declaration at all", [
            "**Kind**: declaration (ADR-0023 §6a). **Parameter**: the trusted-base declaration, published → absent.",
            "**Premises falsified**: every row (§3 rule 1). **Theorems voided**: every theorem with a premise node; "
            "the bottom of every axis, holding only the mechanism constants.",
            "**Type changes**: none declared, which is the failure.",
            "The reference's position before Annex B, and every deployment's before it declares.",
        ], "red", None),
    ]
    hs = [c.card(0, 0, w4, t, b, accent=a, draw=False, size=14) for t, b, a, _ in cards]
    hh = max(hs)
    for i, (t, b, a, _) in enumerate(cards):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, accent=a, h=hh, size=14,
               tint=(a != "red"), dash="6 4" if a == "red" else None)
    y += hh + 56

    # ======================================================================== Annex A in full
    y += c.heading(X0, y, "Annex A · The archetype's trusted base: thirty-one rows in five groups (archetype version: "
                          "the corpus at Batch 20, 2026.09.30; T-0045-31 added by dependent entry, B25)", "blue", 21)
    y += c.legend(X0, y, [("box", "blue", "trust root (identity issued or promoted)"),
                          ("box", "green", "delegated (failure only subtracts)"),
                          ("box", "grey", "excluded (trusted for nothing; premised theorems void)"),
                          ("box", "red", "struck by a dependent entry: the class it had before")],
                  title="Row tint = class") + 14
    cols = [("Id", 132, {"bold": True}), ("Component", 330), ("Layer", 160), ("Trusted for", 560), ("Rungs", 150),
            ("Class", 170), ("Failure can produce", 410), ("Identity fixed by", 540)]
    used = sum(cc[1] for cc in cols)
    cols.append(("Residual", (X1 - X0) - used))
    group_titles = {
        "Under the mechanism constants (all rungs)": "1 · Under the mechanism constants (all rungs): T-0045-1 to 12",
        "Toolchain, at the Build gate": "2 · Toolchain, at the Build gate: T-0045-13 to 15",
        "The verified object's evidence": "3 · The verified object's evidence (R1): what stands between the "
                                          "specification and a running deployment, and the tools that check it: T-0045-28 to 31",
        "Confinement axis (ADR-0034 §6, flattened)": "4 · Confinement axis (ADR-0034 §6, flattened): T-0045-16 to 22",
        "Tools and the cell": "5 · Tools and the cell: T-0045-23 to 27",
    }
    rows = []
    for head, tbl in _tables(annex_a_text):
        key = next((k for k in group_titles if head.strip("* ").startswith(k)), None)
        if not key:
            continue
        rows.append({"group": group_titles[key], "accent": "blue"})
        for r in tbl[1:]:
            k = _klass(r[5])
            cells = [_clean(r[0]).strip("*"), _clean(r[1]), _clean(r[2]), _clean(r[3]), _clean(r[4]),
                     _class_cell(r[5]), _clean(r[6]), _clean(r[7]), _clean(r[8])]
            rows.append({"cells": cells, "accent": CLASS_ACC[k]})
    y += c.table(X0, y, cols, rows, size=13.5, accent="blue") + 18

    nr = annex_a_text.split("**Not rows, and why.**")[1].split("---")[0]
    h = c.card(X0, y, X1 - X0, "Not rows, and why (Annex A)", [_clean(" ".join(nr.split()))], accent="teal",
               bullets=False, size=14.5)
    y += h + 56

    # ======================================================================== Annex B in full
    y += c.heading(X0, y, "Annex B · The reference's declaration, at fb40db1: every principal is Mediated, and this is "
                          "what that costs, row by row", "brown", 21)
    tb = _tables(annex_b_text)[0][1]
    rows = []
    for r in tb[1:]:
        k_raw = r[2]
        kl = _clean(k_raw).lower()
        acc = None
        if "trust root" in kl:
            acc = "blue"
        elif kl.startswith("delegated"):
            acc = "green"
        elif "excluded" in kl:
            acc = "grey"
        changed = "~~" in k_raw
        cells = [f"**{_clean(r[0])}**", _clean(r[1], keep_struck=True), _class_cell(k_raw), _clean(r[3])]
        if changed:
            batch = "B24" if "T-0045-14" in r[0] else "B23"
            cells[3] = (f"[[brown|Changed class after ratification, by dependent entry ({batch}).]] " + cells[3])
        if r[0].strip() == "T-0045-31":
            cells[3] = ("[[brown|Added by dependent entry (B25, ADR-0046 §3).]] " + cells[3])
        if r[0].strip() == "T-0045-6":
            cells[3] += (" [[red|Stale against G9 §2.7 (unchanged since G7): since ADR-0033 A6 (B23) the reference "
                         "loads a bundle only under a verified signature; the checkpoint wins.]]")
        if r[0].strip() == "T-0045-16 to 21":
            cells[3] += (" [[red|No longer matches the code (G9 §2.6): T-0045-19 and T-0045-20 have a rung-1 instance, "
                         "the node's launcher and its backends; T-0045-16 and T-0045-17 are played by test keys in "
                         "simulated runs only. Annex B moves with A7's dependent entries (pending; item 81).]]")
        if r[0].strip() == "T-0045-24":
            cells[3] += (" [[amber|Excluded → delegated is owed to an ADR-0045 amendment on ADR-0034 A2's "
                         "ratification (G9 §2.6, item 80).]]")
        if r[0].strip() == "T-0045-28":
            cells[3] += (" [[brown|At G9 (A7, A8 pending): 62 traces, 709 steps, every step matching and every state "
                         "keeping ConfinementRefinement.tla's invariants (G9 §3).]]")
        rows.append({"cells": cells, "accent": acc} if acc else cells)
    y += c.table(X0, y, [("Row", 150), ("Instance at the reference", 1340), ("Class here", 520),
                         ("Note", (X1 - X0) - 2010)], rows, size=13.5, accent="brown") + 18

    inv = annex_b_text.split("**Inventory.**")[1].split("---")[0]
    w2 = (X1 - X0 - 24) / 2
    h1 = c.card(0, 0, w2, "Inventory at the reference (Annex B)", [_clean(" ".join(inv.split()))], accent="brown",
                bullets=False, size=14.5, draw=False)
    chg = [
        "**T-0045-27, the bundle signer: excluded → trust root, degenerate** (B23, ADR-0033 A6): a dev bundle key "
        "generated by `dev-init.sh`, custody (1, 0). The inventory is unchanged: no theorem rests on T-0045-27 alone.",
        "**T-0045-14: refused solver → trust root proof checker** (B24, ADR-0030 A1): `ethos` 8dc85c4 against cvc5's "
        "CPC signature, with `floor/cvc5-checked` binding a proof to its query. The solver is trusted for nothing; an "
        "`unsat` the checker does not accept reaches cedar as `unknown`.",
        "**Still on the face** (G9 item 69, open): 25 of the 10.01 run's `holds` are `holds°`, folded by cedar with "
        "no query, and rest on T-0045-3, not the checker.",
        "**T-0045-31, the TLA+ Proof System, added** (B25, ADR-0046 §3): a toolchain trust root beside TLC's "
        "T-0045-29, since an unsound prover adds by accepting a false theorem. T-0045-29's residual gains a clause "
        "(small constants bound the mutations and witnesses only), and the inventory sentence one (the thirteen "
        "proved invariants rest on T-0045-31 in place of T-0045-29). The inventory is otherwise unchanged; "
        "T-0045-28 is untouched.",
        "**Still on the face** (G9 §8; items 73, 74, open): the prover's soundness is trusted as written; its "
        "1.9 GB install is not tracked, and the SMT backends' proofs are not rechecked by Isabelle (`tlapm -C`).",
        "**At G9 the record is unchanged** (G9 §2.6): thirty-one rows, no class change. The code moved under "
        "pending addenda: T-0045-19 and 20 have a rung-1 instance, 16 and 17 are test keys in simulated runs only "
        "(A7; Annex B's dependent entries owed, item 81), and T-0045-24's move to **delegated** is owed on A2's "
        "ratification (item 80).",
    ]
    h2 = c.card(0, 0, w2, "After ratification: two class changes and one new row (G8 §2.6); none since (G9 §2.6)",
                chg, accent="blue",
                size=14.5, draw=False)
    hh = max(h1, h2)
    c.card(X0, y, w2, "Inventory at the reference (Annex B)", [_clean(" ".join(inv.split()))], accent="brown",
           bullets=False, size=14.5, h=hh)
    c.card(X0 + w2 + 24, y, w2, "After ratification: two class changes and one new row (G8 §2.6); none since (G9 §2.6)",
           chg,
           accent="blue", size=14.5, h=hh)
    return c
