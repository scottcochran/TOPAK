"""I14 — `ToolList.tla`, the tool list: ADR-0048's ratification condition (§8), drawn whole from the module's own
text and every results file about it. Five properties, stated over what the Thinker was actually told; four
mutations, each breaking exactly what the header says and nothing else; checked by TLC, proved and certified by
TLAPS.

Built on modpage.py's bands (family I). Every row's verdict, the header's "must break" lists and ADR-0048 §8's
figures and digests are compared with the files at build time."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I14", "tool-list"
NAME = "ToolList"
MODULE_FILES = ("spec/ToolList.tla", "spec/ToolList_proof.tla")
W = 3400

REC = "decisions/ADR-0048.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["ToolListIsExact", "ToldMatchesDecided", "ListFixedForRound", "OpeningRecordFirst", "OpenedListIsTold"]
MUST_BREAK = {"M_RECOMPUTE": ["ToolListIsExact", "ToldMatchesDecided", "ListFixedForRound", "OpenedListIsTold"],
              "M_WIDE": ["ToolListIsExact", "ToldMatchesDecided"],
              "M_DECIDELATEST": ["ToldMatchesDecided"], "M_LATE": ["OpeningRecordFirst"]}
CITES = {"spec/ToolList.tla": "7c0a18b897e6cb98", "spec/ToolList-results-2026.10.04.txt": "2875c9159cac8027",
         "spec/ToolList_proof.tla": "c6b7ac1be332dfd6", "spec/ToolList-proof-results-2026.10.04.txt": "6e9fdc63ede2bf6e",
         "spec/ToolList-proof-cert-results-2026.10.04.txt": "1397c5d11022cd96"}
MET_SAYS = ("27 rows: the five hold, each of the four mutations breaks exactly the properties the module says and no "
            "other, and six witnesses are reached, a promotion in the middle of a round among them")
OWED = "**Rows for `spec/ToolList.tla` in `spec/theorem-premise-binding`.**"
ELSEWHERE = ["C7", "H3", "H6"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    rows = res["rows"]
    head_muts = M.header_mutations(mod)
    hm = dict(head_muts)
    _need([m for m, _ in head_muts][1:] == list(MUST_BREAK) == M.mutations(res), "the mutations")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == PROPS, "the header's properties")
    for mt, props in MUST_BREAK.items():
        run = {r["prop"]: r["verdict"] for r in rows if r["mut"] == mt}
        _need(sorted(run) == sorted(PROPS), f"{mt} is not run on every property")
        _need(sorted(p for p, v in run.items() if v == X) == sorted(props), f"{mt} breaks other than the header says")
        _need(all(p in hm[mt] for p in props), f"the header's text for {mt}")
    _need([r["verdict"] for r in rows if r["name"] == "safe"] == [H], "Safe")
    ws = M.witnesses(res)
    _need(len(rows) == 27 and len(ws) == 6 and all(r["verdict"] == X for r in ws), "27 rows, six witnesses reached")
    rec = re.sub(r"\s+", " ", M.text(REC))
    _need(MET_SAYS in rec, "ADR-0048 §8's Met line")
    for rel, sha in CITES.items():
        _need(f"`{sha}`" in rec and M.sha16(rel) == sha, f"ADR-0048 §8's digest of {rel}")
    ce = ev["cert"]
    counts = {r_: n_ for r_, n_, _ in ce["routes"]}
    _need(ev["proof"]["obligations"] == 215 and counts.get("trivial, closed by tlapm with no backend") == 133 and
          counts.get("SMT, proof accepted by ethos") == 75 and ce["ls4"] == 7 and
          "133 trivial, 75 by SMT with a proof the checker accepted, 7 temporal steps by LS4" in rec,
          "ADR-0048 §8's counts")
    _need(OWED in rec, "ADR-0048's open obligation for binding rows")
    _need(not [r for r in P.md_table(P.PREMISES, P.PREMISE_HEAD) if "ToolList" in r[1]], "the binding now has rows")
    hc = M.header_comment(mod)
    j0 = next(i for i, ln in enumerate(hc) if ln.strip().startswith("Not modelled:"))
    notm = " ".join(ln.strip() for ln in hc[j0:j0 + 5] if ln.strip())
    _need(notm.endswith("One principal, any number of rounds."), "the header's not-modelled paragraph")

    c = Canvas(ID,
               "`ToolList.tla`: the Thinker is told exactly the tools its lease may call, the list is fixed for the "
               "round, and the Observer reads the same list. Five properties, four mutations, each breaking exactly "
               "what the header says: checked by TLC, proved and certified by TLAPS",
               "The module ADR-0048 §8 asks for, drawn from its own text and from every results file about it, all "
               "read at build time: the grant, the opening record and a promotion in the middle of a round; the five "
               "properties, stated over what the Thinker was actually told (ghost state the mechanism never reads); "
               "every property by every mutation, beside what the header says each must break; the witnesses; ADR-0048 "
               "§8's figures and digests, compared; every theorem and lemma; and the certified run. **What is checked "
               "or proved here is of the module, not of the reference; \"refused\" means refused at the allowlist** "
               "(its header). ADR-0048 was ratified on 2026.10.05 in Batch 34; the module's header, written before, "
               "calls it Proposed.",
               W,
               f"spec/ToolList.tla (its header, every definition); spec/ToolList_proof.tla (every THEOREM and LEMMA); "
               f"{res['file']}; {ev['files']['proof_results']}; {ev['files']['cert']}; {P.PREMISES} (its theorem "
               f"table); ADR-0048 §2, §4, §5, §8 (R4), Open obligations; ADR-0031 §1, §4. Every file read at the pin "
               f"its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0048", "accepted", "C3, C4")], tail=[
        ("Lean", ("Not re-encoded in Lean", "grey", "2 3"), "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    gl, wl, pl, cl = (M.definition(mod, n_)[0] for n_ in ("Grant", "WriteOpen", "Promote", "Call"))
    y = P.band(c, X0, y, "The mechanism, as the module states it: a grant tells the Thinker the list once, the opening "
                         "record carries the same list, and a promotion mid-round changes neither")
    y = P.flow_picture(
        c, X0, y, WW,
        ("A grant", ["at the revision promoted at that moment, with any narrowing (ADR-0031 §1, §4)"], "brown"),
        (f"The grant, and the opening record (`Grant`, line {gl}; `WriteOpen`, line {wl})", [
            "**①** the Thinker is told `List(rev, n)`: the granted revision's allowlist, narrowed by the lease. "
            "`M_WIDE` [[red|ignores the narrowing]].",
            "**②** the round's topic opens with a record of the same list, before any effect. `M_LATE` [[red|writes "
            "it when the mechanism gets to it]].",
            f"**③** a promotion (`Promote`, line {pl}) changes the latest revision, not a live round's list. "
            f"`M_RECOMPUTE` [[red|re-delivers the list]]."], "teal"),
        None,
        ("The round", "teal", [
            ("The lease: `live`, `rev`, `narrow`", ["the revision it was granted at, and its narrowing"], "teal"),
            ("What the Thinker was told: `told`", ["ghost state: the list it was given, and at the grant "
                                                   "(`toldAtGrant`)"], "teal"),
            ("The opening record: `opened`, `openList`", ["what the Observer reads"], "pink")]),
        ("The calls: `admitted`, `refused`", [f"a call (`Call`, line {cl}) is decided against the lease's revision, "
                                              f"and records whether its tool was told. `M_DECIDELATEST` [[red|decides "
                                              f"against the latest]]."], "grey"),
        [("ADR-0048 §2, read on the calls", ["`ToldMatchesDecided`"], "record"),
         ("ADR-0048 §2 and §4, read on the round", ["`ToolListIsExact`, `ListFixedForRound`, `OpeningRecordFirst`, "
                                                    "`OpenedListIsTold`"], "state")],
        {"ask": "grants", "write": "the list", "act": "④ a call"},
        "**Key.** ① to ③ are the grant, the opening record and a promotion; ④ a call by the Thinker, which is havoc: "
        "\"it calls any tool, told or not\" (the header). Red marks where each mutation acts. The picture is the "
        "diagram's own drawing of the definitions below.") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("Two revisions (the header)", ["\"Two bundle revisions with different allowlists, so that a promotion in the "
                                        "middle of a round changes which tools exist\": " +
                                        P.code(M.definition(mod, "Allow")[1])], "brown", {}),
        ("Not modelled (the header)", [notm], "red", {}),
    ], size=13.5) + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: the list, the grant, the opening record, a promotion and a call "
                         "(`ToolList.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("The tools, the revisions, and the start", ["Tools", "Revs", "Allow", "Init"],
          [f"`CONSTANT Mut` (line {M.line_of(mod, r'^CONSTANT Mut$')})"], "grey"),
         ("The list, and the grant", ["List", "Grant"], [], "teal"),
         ("The opening record, and a promotion", ["WriteOpen", "Promote"], [], "teal")],
        [("A call, decided against a revision", ["DecideRev", "Call"], [], "teal"),
         ("The end of a round, and `Next`", ["EndRound", "Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The five properties, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, "ADR-0048 §8, named in the condition", w) for p, _, w in hp]) + 50

    # ---- the mutations
    y = P.band(c, X0, y, "The mutations: what each does, and what the header says it must break")
    lines = M.text(mod).split("\n")
    mrows = []
    for mt in MUST_BREAK:
        at = M.code_lines_with(mod, f'"{mt}"')
        lem = [s for s in ev["statements"] if s["kind"] == "LEMMA" and f'"{mt}"' in (s["assume"] or "") + s["prove"]]
        mrows.append([f"`{mt}`", hm[mt], "; ".join(f"`{M.enclosing(mod, ln)}`, line {ln}: {P.code(lines[ln - 1])}"
                                                   for ln in at),
                      ", ".join(f"`{p}`" for p in MUST_BREAK[mt]), "; ".join(f"`{s['name']}`" for s in lem) or "—"])
    y += c.table(X0, y, [("Mutation", 240, {}), ("What it does (the module's header)", 900), ("Where it acts", 1000),
                         ("Must break (the header), and does (TLC)", 600), ("The proof module's lemma", WW - 2740)],
                 mrows, size=13, accent="red", anchor="mutations") + 50

    # ---- the matrix
    y = P.band(c, X0, y, f"Every property by every mutation, read from `{res['file'][5:]}`")
    cols = ["none"] + list(MUST_BREAK)
    mrows = []
    for p in ["Safe"] + PROPS:
        r_ = [f"`{p}`"]
        for mt in cols:
            h_ = [r for r in rows if r["mut"] == mt and r["prop"] == p]
            if not h_:
                r_.append("[[grey|—]]")
                continue
            r = h_[0]
            v = "[[red|COUNTEREXAMPLE]]" if r["verdict"] == X else "**HOLDS**"
            mark = "must break" if p in MUST_BREAK.get(mt, []) else ("must hold" if mt != "none" else "")
            r_.append(f"{v} · `{r['name']}` · {P.n(r['states'])}" + (f"\n{mark}" if mark else ""))
        mrows.append(r_)
    cw = (WW - 330) / len(cols)
    y += c.table(X0, y, [("Property", 330, {})] + [(f"`{m}`", cw) for m in cols], mrows, size=13,
                 anchor="matrix") + 14
    y += c.para(X0, y, WW, f"Every mutation is run on every property, and breaks exactly the ones the header names "
                f"(compared at build time): ADR-0048 §8's \"{MET_SAYS}\".", 13.5, "muted") + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverPromotedMidRound": "A promotion in the middle of a round: the case the module exists for.",
        "NeverNarrowed": "A lease's narrowing shortens the list.",
        "NeverAdmitted": "A call is admitted.", "NeverRefused": "A call is refused at the allowlist.",
        "NeverNewList": "A round is granted at revision 2, whose list holds `t3`.",
        "NeverRefusedNewTool": "A call to a tool the latest revision allows, and the round's does not, is refused.",
    }) + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, None) + 14
    y += c.para(X0, y, WW, "\"The module found no fault in the record\" (ADR-0048 §8). ADR-0048 cites each of the five "
                "files by digest, and the certified run's counts, compared at build time.", 13.5, "muted") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y += c.para(X0, y, WW, f"`{P.PREMISES[5:]}`'s theorem table has no row whose \"Checked in\" names `ToolList.tla` "
                "(checked at build time). ADR-0048 lists them as owed, among its open obligations: \"Rows for "
                "`spec/ToolList.tla` in `spec/theorem-premise-binding`\".", 14, "ink") + 50

    # ---- where else, digests
    y = P.band(c, X0, y, "Where else `ToolList.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, note="ADR-0048 §8 cites each of these files by digest, compared at build time.")
    return c
