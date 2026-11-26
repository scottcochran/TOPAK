"""I5 — `RulesFloorNV_rev5.tla`, ADR-0026 §7's non-vacuity rerun of the rules floor against ADR-0024 revision 5,
drawn whole from the module's own text and every results file about it. Its proofs are **not certified**: Isabelle
rejected one of Zenon's proofs.

Built on modpage.py's bands (family I). A variant here is a dropped floor entry (the constant `Active`) or the
mechanism without recusal (`Mech = "norecuse"`), so the matrix is keyed by the results file's row. ADR-0026 §7's
table is drawn whole and each row compared with the results file."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I5", "rules-floor-nv-rev5"
NAME = "RulesFloorNV_rev5"
MODULE_FILES = ("spec/RulesFloorNV_rev5.tla", "spec/RulesFloorNV_rev5_proof.tla")
W = 3400

REC26 = "decisions/ADR-0026.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "P1_Unanimity", "P9_NoSoloGrant", "P2_TwoSeatsCounted", "P3_AuthorNotCounted",
         "P5_AnchorNotApprover", "P7_BGNoAuthority"]
EXPECT = {("base", "Safe"): H, ("dropR1", "P1_Unanimity"): X, ("dropR1R9", "P9_NoSoloGrant"): X,
          ("dropR2", "P2_TwoSeatsCounted"): X, ("envrecuse", "P3_AuthorNotCounted"): X,
          ("dropR5", "P5_AnchorNotApprover"): X, ("dropR7", "P7_BGNoAuthority"): X}
# each property, the entry (or mechanism constant) it rests on, and what its theorem must assume for it
ENTRY = {"P1_Unanimity": ("ADR-0026 R1", '"R1" \\in Active'),
         "P2_TwoSeatsCounted": ("ADR-0026 R2", '"R2" \\in Active'),
         "P3_AuthorNotCounted": ("ADR-0024 §6: recusal, a mechanism constant; R3 withdrawn", 'Mech # "norecuse"'),
         "P5_AnchorNotApprover": ("ADR-0026 R5", '"R5" \\in Active'),
         "P7_BGNoAuthority": ("ADR-0026 R7", '"R7" \\in Active'),
         "P9_NoSoloGrant": ("ADR-0026 R9, conditional (§7 finding 1)", '"R1" \\in Active \\/ "R9" \\in Active')}
S7_HEAD = ["Check", "Active floor", "Invariant", "Result"]
ELSEWHERE = ["B4", "G3", "H3"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def entries(active):
    return re.findall(r'"(R\d)"', active)


def assumes(rel):
    """Each top-level ASSUME, as (line, its lines)."""
    lines = M.text(rel).split("\n")
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("ASSUME "):
            j = i + 1
            while j < len(lines) and lines[j].startswith(" "):
                j += 1
            out.append((i + 1, "\n".join(lines[i:j])))
    return out


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    rows = res["rows"]
    all_entries = re.findall(r'"(R\d)"', M.definition(mod, "AllEntries")[1])
    head_mech = M.header_mutations(mod, var="Mech")
    _need([m for m, _ in head_mech] == ["rev5", "norecuse"], f"the header's mechanisms are {head_mech}")
    for p, (_, hyp) in ENTRY.items():
        t = P.theorem_for(ev, p)
        _need(t and hyp in t["assume"], f"{p}'s theorem does not assume {hyp}")
    asm = assumes(mod)
    _need(len(asm) == 3, f"the module has {len(asm)} ASSUMEs")
    lemma_names = [s["name"] for s in ev["statements"]]
    for nm in ("GenesisEntries", "EntriesIndependent", "R9IndependentUnderThreshold"):
        _need(nm in lemma_names, f"no lemma {nm}")
    ce = ev["cert"]
    _need(not ce["certified"] and ce["last"] == "NOT CERTIFIED: Isabelle rejected 1 of Zenon's proofs.",
          f"the certified run's last line is {ce['last']!r}")
    zen = [r for r in ce["routes"] if r[0].startswith("Zenon")]
    _need(zen and zen[0][2] == "ISABELLE REJECTED 1: obligations 55", f"the Zenon route's note is {zen}")
    _need("`spec/RulesFloorNV_rev5.tla` · digest `3034df144d75ec3a`" in M.text(REC26)
          and M.sha16(mod) == "3034df144d75ec3a", "ADR-0026 §7's cited digest is not the module's")
    base_entries = re.findall(r'"(R\d)"', M.definition("spec/RulesFloorBase.tla", "AllEntries")[1])
    labels = {}
    for r in rows:
        act = entries(r["params"]["Active"])
        dropped = [e for e in all_entries if e not in act]
        labels[r["name"]] = (f"`Mech = \"{r['params']['Mech']}\"` · `Active` drops "
                             f"{', '.join(dropped) if dropped else 'nothing'}")
    key = lambda r: r["name"]  # noqa: E731

    def s7_compare(row):
        if row[0].startswith("Satisfiability"):
            return (f"the module's three `ASSUME`s (lines {', '.join(str(l_) for l_, _ in asm)}); proved as "
                    f"`GenesisEntries`, `EntriesIndependent`, `R9IndependentUnderThreshold`")
        act = row[1].split()
        inv = re.findall(r"`(\w+)`", row[2])
        mech = "norecuse" if "Recusal removed" in row[0] else "rev5"
        word = H if "holds" in row[3].lower() else X if "counterexample" in row[3].lower() else None
        _need(len(inv) == 1 and word, f"§7 row {row[0]!r} does not read")
        hit = [r for r in rows if sorted(entries(r["params"]["Active"])) == sorted(act) and r["prop"] == inv[0]
               and r["params"]["Mech"] == mech]
        _need(len(hit) == 1, f"§7 row {row[0]!r}: {len(hit)} rows in the file")
        _need(hit[0]["verdict"] == word, f"§7 row {row[0]!r}: the file says {hit[0]['verdict']}")
        return f"agrees: `{hit[0]['name']}`, {P.n(hit[0]['states'])} states"

    c = Canvas(ID,
               "`RulesFloorNV_rev5.tla`: every rules-floor entry is non-vacuous against ADR-0024 revision 5, and "
               "each property holds with its entry in force. Six invariants, each broken by dropping its entry: "
               "checked by TLC, proved by TLAPS and in Lean, and **not certified**",
               "The module ADR-0026 §7 reports, drawn from its own text and from every results file about it, all "
               "read at build time: one havoc issuance and one promotion, the floor's entries, the six properties "
               "and the entry each rests on, every variant by every property, the witness, ADR-0026 §7's table "
               "compared row by row, every theorem and lemma, the proof run and the certified run that refused it, "
               "and the Lean re-encoding. **The proofs are proved and not certified: Isabelle rejected one of "
               "Zenon's proofs**, and restructuring the module is deferred by the custodian (G10 item 74). **What is "
               "checked or proved here is of the module, at its constants or by its proofs, and not of the "
               "reference.** The module is a frozen, dated artifact (ADR-0026 §7); the live floor is "
               "`RulesFloorBase.tla` (I6).",
               W,
               f"spec/RulesFloorNV_rev5.tla (its header, every definition and ASSUME); spec/RulesFloorNV_rev5_proof.tla "
               f"(every THEOREM and LEMMA); {res['file']}; {ev['files']['proof_results']}; {ev['files']['cert']}; "
               f"{M.LEAN_RESULTS} (compared with {M.LEAN_LATER[10:]}); spec/lean/TopakSpec/RulesFloorNV_rev5.lean; "
               f"{P.PREMISES} (the six rows and invariant(RulesFloorNV_rev5)); spec/RulesFloorBase.tla (AllEntries); "
               f"ADR-0026 R1, R2, R5, R7, R9, §7 (its table and findings), B25; ADR-0024 §6, revision 5; G10 item 74; "
               f"the manifest's titles of {', '.join(ELSEWHERE)}. Every file read at the pin its links open, and "
               f"checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0026", "accepted", ""), ("ADR-0024", "accepted", "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    il, vl, pl, bl = (M.definition(mod, n_)[0] for n_ in ("Issue", "Vote", "Promote", "BreakGlass"))
    y = P.band(c, X0, y, "The mechanism, as the module states it: one havoc issuance of any rule set the floor "
                         "admits, then votes, then a promotion that the six properties judge")
    y = P.flow_picture(
        c, X0, y, WW,
        ("A havoc anchor", ["\"any floor-conformant rule set, once; fences in-flight votes\" (the module's comment)"],
         "brown"),
        (f"The issuance (`Issue`, line {il})", [
            "**①** any `r` in `RuleSpace` with `Floor(r)`: every entry in `Active` holds of it (ADR-0026). Dropping "
            "an entry from `Active` [[red|is the mutation]].",
            "**②** the votes are fenced: every vote back to `none`."], "teal"),
        ("No such rule set", ["Nothing changes."], "red"),
        ("`rules` and `votes`", "teal", [
            ("At the start: `Genesis`", ["the roster without the author and the anchor key-holder; `all`; "
                                         "`minGrant` 2"], "grey"),
            (f"Each vote: `Vote(h)`, line {vl}", ["a seat on the roster, never the author: the ADR-0022 envelope. "
                                                  "`norecuse` [[red|lets the author vote]]."], "teal"),
            ("Who is counted: `Counted`", ["the roster without the author (ADR-0024 §6). `norecuse` [[red|counts "
                                           "the author]]."], "teal"),
            (f"Break-glass: `BreakGlass`, line {bl}", ["any act in `bgScope`"], "grey")]),
        (f"The promotion (`Promote`, line {pl})", ["when `PromotionEnabled`: enough counted seats, and every "
                                                    "counted seat granted (`all`) or `k` grants; records `approvers` "
                                                    "and `seats`"], "grey"),
        [("ADR-0026 R1, R2, R5, R9 and ADR-0024 §6, read on the promotion",
          ["`P1_Unanimity`, `P2_TwoSeatsCounted`, `P3_AuthorNotCounted`, `P5_AnchorNotApprover`, "
           "`P9_NoSoloGrant`"], "record"),
         ("ADR-0026 R7, read on break-glass", ["`P7_BGNoAuthority`: no authority-changing act in `bgDid`"],
          "state")],
        {"ask": "issues", "write": "③ the rules", "act": "④ `Promote`"},
        "**Key.** ① and ② are the issuance; ③ the rule set it installs; ④ the promotion, when the votes allow it. "
        "Red marks where each variant acts: an entry dropped from `Active`, or recusal removed. The picture is the "
        "diagram's own drawing of the definitions below.") + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: the rule space, the floor's entries, the genesis rules and their ASSUMEs, and "
                         "four actions (`RulesFloorNV_rev5.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Constants: five humans, one author, one anchor key-holder", ["Humans", "Author", "AnchorKeys", "AuthActs",
                                                                        "BGActs"],
          [f"`CONSTANTS Active, Mech` (line {M.line_of(mod, r'^CONSTANTS Active, Mech$')}): the entries in force, "
           f"and `rev5` or `norecuse`", "Five, not four: at four a threshold over two counted seats is unanimity, "
           "so dropping R1 proved nothing (ADR-0026 §7 finding 3; the module's comment)."], "grey"),
         ("The rule space", ["QVals", "RuleSpace"], ["The tagged quorum is the model's encoding, not the record's "
                                                     "(the module's comment)."], "grey"),
         ("The floor: five entries", ["Entry", "AllEntries", "Floor"], [], "blue"),
         (None, ["Genesis"], [], "blue")],
        [("Who counts, and when a promotion is enabled", ["Counted", "Recorded", "PromotionEnabled"],
          ["ADR-0024 revision 5: only recorded votes count; a timeout is never a grant."], "teal"),
         (None, ["Issue"], [], "teal"),
         (None, ["Vote"], ["The ADR-0022 `Vote` envelope, modelled for the first time (ADR-0026 §7)."], "teal"),
         (None, ["Promote"], [], "teal"),
         ("Break-glass, and `Next`", ["BreakGlass", "Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 24
    ah = [P.code(ln) for _, src in asm for ln in src.split("\n")]
    y += P.row_cards(c, X0, y, WW, 30, [
        (f"The three `ASSUME`s, lines {', '.join(str(l_) for l_, _ in asm)}", ah, "blue", {"bullets": False}),
        ("What they say", [
            "**Satisfiability:** every entry holds of `Genesis`.",
            "**Independence:** for every entry but R9, a rule set that violates it and satisfies the others.",
            "**R9, conditionally:** every rule set R9 excludes R1 excludes too, so R9's independence is stated on a "
            "floor without R1 (ADR-0026 §7 finding 1). Each is proved as a lemma (below)."], "grey", {}),
    ], size=13.5) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The six properties, the entry each rests on, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, ENTRY[p][0], None) for p in
                                        ("P1_Unanimity", "P2_TwoSeatsCounted", "P3_AuthorNotCounted",
                                         "P5_AnchorNotApprover", "P7_BGNoAuthority", "P9_NoSoloGrant")],
                     key=key) + 14
    y += c.para(X0, y, WW, "The module's header has no property table: \"Properties, one per entry. R1 and R9 protect "
                "different things: R1 that every counted seat granted, R9 that no single grant promotes once R1 is "
                "relaxed\" (its comment). Each entry here is checked against the hypothesis of the property's theorem.",
                13.5, "muted") + 50

    # ---- the variants
    y = P.band(c, X0, y, "The variants: an entry dropped from `Active`, or recusal removed from the mechanism")
    mech_rows = []
    lines = M.text(mod).split("\n")
    for mt, words in head_mech:
        at = M.code_lines_with(mod, f'"{mt}"')
        lem = [s for s in ev["statements"] if s["kind"] == "LEMMA" and f'Mech = "{mt}"' in (s["assume"] or "")]
        mech_rows.append([f"`Mech = \"{mt}\"`", words,
                          "; ".join(f"`{M.enclosing(mod, ln)}`, line {ln}: {P.code(lines[ln - 1])}" for ln in at)
                          or "no line names it: it is every `Mech # \"norecuse\"`", ", ".join(f"`{r['name']}`" for r in rows if r["params"]["Mech"] == mt),
                          "; ".join(f"`{s['name']}` (line {s['line']}): `{s['prove']}`" for s in lem) or "—"])
    y += c.table(X0, y, [("Mechanism", 260, {}), ("What it is (the module's header)", 900), ("Where it acts", 900),
                         ("Rows run under it", 500), ("The proof module's lemma", WW - 2560)], mech_rows,
                 size=13.5, accent="red", anchor="mutations") + 50

    # ---- the matrix
    y = P.band(c, X0, y, f"Every variant by every property, read from `{res['file'][5:]}`")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, labels, key=key, head="Row") + 14
    y += c.para(X0, y, WW, "Each variant is run on the property its entry protects, and the full floor on `Safe`; "
                "the other cells are not run. `dropR1` breaks unanimity and leaves `P9_NoSoloGrant` to R9; only "
                "`dropR1R9` reaches a single-grant promotion (ADR-0026 §7 finding 1).", 13.5, "muted") + 50

    # ---- the witness
    y = P.band(c, X0, y, "The witness: a promotion is reachable, or every property above is vacuous")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverPromoted": "A promotion happens under the full floor: each property's antecedent, `promoted`, is "
                         "reached."}, unmutated=("rev5",)) + 50

    # ---- the record's table
    y = P.band(c, X0, y, "ADR-0026 §7's table, every row and column, each compared with the results file")
    y += P.record_table(c, X0, y, WW, REC26, S7_HEAD, (620, 380, 460, 300), s7_compare) + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, the run that proved it, and the certified run "
                         f"that refused it")
    y = P.proofs(c, X0, y, WW, ev, {
        "GenesisEntries": "The first ASSUME: the floor admits genesis.",
        "GenesisRules": "Genesis is a rule set.",
        "EntriesIndependent": "The second ASSUME: every entry but R9 is independent.",
        "R9IndependentUnderThreshold": "The third: R9 is independent on a floor without R1.",
        "InitBase": "`Base` (typing, and the floor holds of `rules`) at the start.",
        "NextBase": "`Base` is kept: an issuance installs only a floor-conformant rule set.",
        "InForce": "An entry in `Active` holds of the rules in force.",
        "Steps": "A step either leaves the promotion's record alone or is `Promote`.",
        "PromoteSets": "What a promotion records.",
        "RecordedWithin": "Recorded votes are counted seats, and counted seats are on the roster.",
        "HumansFinite": "Five humans: a finite set.",
        "RecordedCardinality": "The number of recorded votes is a natural number.",
        "NextP1": "`P1_Unanimity` is kept with R1 in force.",
        "NextP2": "`P2_TwoSeatsCounted` is kept with R2 in force.",
        "NextP3": "`P3_AuthorNotCounted` is kept with recusal.",
        "NextP5": "`P5_AnchorNotApprover` is kept with R5 in force.",
        "NextP9": "`P9_NoSoloGrant` is kept with R2, and R1 or R9.",
        "NextP7": "`P7_BGNoAuthority` is kept with R7 in force.",
        "InitAll": "`Base` and all six, at the start.",
        "P1Always": "ADR-0026 R1's property, for every behaviour, with R1 in force.",
        "P2Always": "R2's, with R2 in force.",
        "P3Always": "Recusal's, ADR-0024 §6, with recusal in the mechanism.",
        "P5Always": "R5's, with R5 in force.",
        "P7Always": "R7's, with R7 in force.",
        "P9Always": "R9's, with R2 and either R1 or R9.",
        "SafeAlways": "All six, with the whole floor and recusal.",
        "MutNoRecuseCountsAuthor": "Why `norecuse` must fail: the author is counted.",
    }, assumptions_note="the proof module's `ASSUME`: the entries in force are floor entries") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("[[red|Proved, and not certified]]", [
            f"The proof run printed \"{ev['proof']['notes'][0]}\" and then \"All {ev['proof']['obligations']} "
            f"obligations proved.\"",
            f"The certified run's Zenon route: \"{zen[0][2]}\"; its last line: \"{ce['last']}\" Obligation 55 is "
            f"named by number only.",
            "Restructuring the module is deferred by the custodian (G10 item 74). **Proved is not certified.**"],
         "red", {}),
        ("What B4 says of it", [
            "B4, the rules floor, draws the same refusal: \"This proof does not certify\", Isabelle rejected one of "
            "Zenon's proofs (obligation 55)."], "grey", {}),
    ], size=13.5) + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the module re-encoded and its theorems proved again")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.RulesFloorNV_rev5",
               extra_card="The Lean proofs are not a certification of the TLAPS proofs: they are a second proof, of the "
                          "re-encoding.") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, list(ENTRY), ["invariant(RulesFloorNV_rev5)"]) + 50

    # ---- the live floor
    y = P.band(c, X0, y, "The frozen copy and the live floor")
    extra = [e for e in base_entries if e not in all_entries]
    y += P.row_cards(c, X0, y, WW, 30, [
        ("This module's entries", [f"{', '.join(all_entries)}: its own frozen copy of the floor, cited by digest in "
                                   f"ADR-0026 §7."], "blue", {}),
        ("`RulesFloorBase.tla`'s entries (I6)", [
            f"{', '.join(base_entries)}: the live definition. It has {', '.join(extra) if extra else 'nothing'} that "
            f"this module does not (computed from the two modules' `AllEntries`)."], "teal", {}),
        ("Why the two differ", ["\"Divergence between them and this module is expected and is what the dates are "
                                "for\" (`RulesFloorBase.tla`'s header)."], "grey", {}),
    ], size=13.5) + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `RulesFloorNV_rev5.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, note="ADR-0026 §7 cites the module as `3034df144d75ec3a`.")
    return c
