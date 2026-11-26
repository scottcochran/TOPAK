"""I1 — `Seats.tla`, the module ADR-0037 §9 asks for, drawn whole: its machine, its two properties and the record
section each states, the mutation matrix, the witnesses, every theorem and lemma of `Seats_proof.tla`, the certified
run, the Lean re-encoding and its check against TLC's state graphs, the premises the binding names, the model of the
code that refines it, and what of ADR-0037 §4 the frozen module does not model.

The pilot of the per-module family (derived/topak-module-diagrams-scope-2026.11.26.md). Every count, verdict,
definition and statement is read at build time through modules.py; what the diagram expects the files to say is
recorded below as literals and compared with them both ways, so a file that moves fails the build."""
import json
import pathlib
import re

import lib
import modules as M
import modpage as P
from lib import Canvas, linked, poster_link

ID, SLUG = "I1", "seats"
NAME = "Seats"
MODULE_FILES = ("spec/Seats.tla", "spec/Seats_proof.tla")
W = 3400
S = 14

REC = "decisions/ADR-0037.md"
PREMISES = "spec/theorem-premise-binding.md"
CODE_LEAN = "mechanism/lean/Admit-results-2026.10.06c.txt"   # cited by ADR-0053 (its table of results)
REPLAY = "mechanism/lean/SeatsReplay-results-2026.10.06.txt"  # cited by ADR-0037 B36 and ADR-0053
MODEL = "mechanism/lean/Topak/SeatsModel.lean"

# ---- what the diagram expects the files to say; the build compares each with its file, in both directions
PROPS = ["OnlyThinkersAuthor", "OneSeatPerPrincipal"]
SECTION = {"OnlyThinkersAuthor": "§4", "OneSeatPerPrincipal": "§1"}
H, X = "HOLDS", "COUNTEREXAMPLE"
EXPECT = {("none", PROPS[0]): H, ("none", PROPS[1]): H,
          ("M_KIND", PROPS[0]): X, ("M_KIND", PROPS[1]): H,
          ("M_SEAT", PROPS[0]): H, ("M_SEAT", PROPS[1]): X}
THEOREM_OF = {"OnlyThinkersAuthor": ("OnlyThinkersAuthorAlways", 'Mut # "M_KIND"'),
              "OneSeatPerPrincipal": ("OneSeatPerPrincipalAlways", 'Mut # "M_SEAT"'),
              "Safe": ("SafeAlways", 'Mut = "none"')}
KINDS = {"s1": "thinker", "s2": "observer", "s3": "grant"}
# ADR-0037's R5 History row, as the record states the run's outcome
R5_SAYS = "`M_KIND` breaks only §4 and `M_SEAT` breaks only §1; three witnesses reachable"
# §4's table at the pin: its header, every row drawn
S4_HEAD = ["Kind", "Build", "~~Run (provisional: G4 item 13)~~ struck at B20", "Run ⟨A1⟩ (ADR-0043 §2)"]
# the marks on §4 for the kinds the module predates, as the record carries them
S4_MARKS = [("operator", "⟨A4⟩ ⟨B34⟩ The table gains a kind: **`operator`**"),
            ("emergency", "⟨A3⟩ ⟨B34⟩ The table gains a kind: **`emergency`**"),
            ("orchestrator", "Pending ⟨A5⟩, not applied. The table gains a kind: **`orchestrator`**")]
PREMISE_HEAD = ["Theorem", "Checked in", "Record", "Breaks under", "Row premises", "Parameter and gap premises",
                "At the reference (Annex B)"]
DERIVED_HEAD = ["Derived premise", "Holds when (any route)", "Record"]
# the diagrams that draw Seats.tla beside this one (each checked: its committed SVG names the module)
ELSEWHERE = ["C1", "C2", "G1", "G3", "H3", "H7", "H9"]

MUT_LABEL = {}   # filled from the module's header at build time


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"I1: {what}")


def kind_bound():
    """KindBound's CASE arms, from the module: {kind: [acts]}."""
    _, src = M.definition(MODULE_FILES[0], "KindBound")
    arms = re.findall(r'k = "(\w+)"\s*->\s*\{([^}]*)\}', src)
    _need([k for k, _ in arms] == list(KINDS.values()), f"KindBound's arms are {[k for k, _ in arms]}")
    return {k: re.findall(r'"(\w+)"', v) for k, v in arms}


def kind_of():
    _, src = M.definition(MODULE_FILES[0], "KindOf")
    got = dict(re.findall(r'(\w+) \|-> "(\w+)"', src))
    _need(got == KINDS, f"KindOf is {got}")
    return got


def set_of(rel, name):
    _, src = M.definition(rel, name)
    return re.findall(r'"(\w+)"', src)


def picture(c, X0, y, WW, kb, ko, principals):
    """Principals -> the grant path -> one lease per seat -> acted, and the two properties on what they read.
    Arrows are numbered and keyed; every element names the line or section it draws."""
    gl = M.definition(MODULE_FILES[0], "Grant")[0]
    al = M.definition(MODULE_FILES[0], "Act")[0]
    el = M.definition(MODULE_FILES[0], "EndRound")[0]
    sz = 13.5
    # columns
    xa, wa = X0, 300
    xb, wb = X0 + 420, 760
    xc, wc = X0 + 1360, 820
    xd, wd = X0 + 2340, 470
    xe = X0 + 2940
    we = WW - (xe - X0)
    gap = 18
    seat_specs = []
    for s_, k in ko.items():
        seat_specs.append((f"Seat `{s_}` · kind `{k}`",
                           [f"alphabet {', '.join(f'`{a}`' for a in kb[k])}"],
                           "teal"))
    sh = [c.card(0, 0, wc - 40, t, b, draw=False, size=sz) for t, b, _ in seat_specs]
    region_h = 40 + sum(sh) + gap * (len(sh) - 1) + 24
    top = y + 14
    # the leases
    c.region(xc, top, wc, region_h, "`lease`: one record per seat (line 39)", "teal")
    sy = top + 40
    for (t, b, acc), h in zip(seat_specs, sh):
        c.card(xc + 20, sy, wc - 40, t, b, accent=acc, size=sz, h=h)
        sy += h + gap
    mid = top + region_h / 2
    # principals
    pb = [f"`{p}`" for p in principals]
    ph = c.card(0, 0, wa, "Principals", pb, draw=False, size=sz)
    # the grant path
    gb = [f"**①** `~lease[s].live`: the seat is free",
          f"**②** `~HoldsElsewhere(p, s)`: `p` holds no live lease on another seat (ADR-0037 §1, §9). "
          f"`M_SEAT` [[red|drops it.]]",
          f"**③** the lease is issued `KindBound(KindOf[s])`, whatever was asked (§4). "
          f"`M_KIND` [[red|issues all of]] `Acts`."]
    gh = c.card(0, 0, wb, f"The grant path (`Grant`, line {gl})", gb, draw=False, size=sz, bullets=False)
    gy = top + 10
    c.card(xb, gy, wb, f"The grant path (`Grant`, line {gl})", gb, accent="teal", size=sz, h=gh, bullets=False)
    c.card(xa, gy + gh / 2 - ph / 2, wa, "Principals", pb, accent="brown", size=sz, h=ph)
    rb = ["Nothing changes: no lease, no act."]
    rh = c.card(0, 0, wb, "Refused, at ① or ②", rb, draw=False, size=sz)
    ry = top + region_h - rh
    c.card(xb, ry, wb, "Refused, at ① or ②", rb, accent="red", size=sz, h=rh, dash="6 4")
    # acted, and the two properties
    db = ["one record per admitted act: `[act |-> a, kind |-> KindOf[s]]`"]
    dh = c.card(0, 0, wd, "The record of acts: `acted`", db, draw=False, size=sz)
    dy = top + 10
    c.card(xd, dy, wd, "The record of acts: `acted`", db, accent="grey", size=sz, h=dh)
    p1 = ["`OnlyThinkersAuthor`: an authoring act only from a `thinker` seat, and `Vote` never from one"]
    p2 = ["`OneSeatPerPrincipal`: two live leases never belong to one principal"]
    h1 = c.card(0, 0, we, "ADR-0037 §4, read on `acted`", p1, draw=False, size=sz)
    h2 = c.card(0, 0, we, "ADR-0037 §1, read on `lease`", p2, draw=False, size=sz)
    c.card(xe, dy, we, "ADR-0037 §4, read on `acted`", p1, accent="blue", size=sz, h=h1)
    y2 = top + region_h - h2
    c.card(xe, y2, we, "ADR-0037 §1, read on `lease`", p2, accent="blue", size=sz, h=h2)
    # arrows
    ay = gy + gh / 2
    c.arrow([(xa + wa, ay), (xb, ay)], "brown", label="asks: `Grant(p, s)`", lpos=0.5, loff=(0, -16))
    c.arrow([(xb + wb, ay), (xc, ay)], "teal", label="④ a live lease", lpos=0.5, loff=(0, -16))
    c.arrow([(xb + wb / 2, gy + gh), (xb + wb / 2, ry)], "red", dash="7 5")
    c.arrow([(xc + wc, dy + dh / 2), (xd, dy + dh / 2)], "teal", label=f"⑤ `Act(s)`, line {al}", lpos=0.5,
            loff=(0, -16))
    c.arrow([(xd + wd, dy + h1 / 2), (xe, dy + h1 / 2)], "blue", dash="4 4")
    c.arrow([(xc + wc, y2 + h2 / 2), (xe, y2 + h2 / 2)], "blue", dash="4 4")
    end_y = top + region_h + 40
    c.arrow([(xc + wc / 2, top + region_h), (xc + wc / 2, end_y)], "green", dash="7 5", head=True)
    c.label(xc + wc / 2, end_y + 14, f"⑥ `EndRound(s)`, line {el}: the lease becomes `NoLease`", "green", sz)
    key_y = end_y + 44
    kh = c.para(X0, key_y, WW,
                "**Key.** ① to ③ are `Grant`'s conjuncts in order; ④ is the lease it writes; ⑤ an act from the "
                "live alphabet, recorded with the seat's kind; ⑥ ends a lease and nothing else. Dotted blue lines "
                "show what each property reads. The picture is the diagram's own drawing of the module's "
                "definitions below; red marks where each mutation acts.", 13.5, "muted")
    return key_y + kh


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res, pr, ce, lr = ev["tlc"], ev["proof"], ev["cert"], ev["lean"]
    head_muts = M.header_mutations(mod)
    MUT_LABEL.update(dict(head_muts))
    _need([m for m, _ in head_muts] == ["none"] + M.mutations(res),
          "the header's mutations are not the results file's, in order")
    head_props = M.header_properties(mod)
    _need([(p, s) for p, s, _ in head_props] == [(p, SECTION[p]) for p in PROPS],
          "the header's properties or their sections are not the diagram's")
    rec = M.text(REC)
    _need(R5_SAYS in rec, "ADR-0037's R5 row no longer says what the diagram quotes")
    for _, mark in S4_MARKS:
        _need(mark in rec, f"ADR-0037 §4 no longer carries {mark[:30]!r}")
    for rel, adr in (("spec/Operators.tla", "ADR-0050"), ("spec/Emergency.tla", "ADR-0052")):
        _need(adr in "\n".join(M.header_comment(rel)[:2]), f"{rel}'s header no longer states {adr}")
    kb, ko = kind_bound(), kind_of()
    acts, authoring = set_of(mod, "Acts"), set_of(mod, "Authoring")
    st = {s["name"]: s for s in ev["statements"]}
    for p, (thm, hyp) in THEOREM_OF.items():
        _need(st[thm]["assume"] == hyp and st[thm]["prove"] == f"Spec => []{p}",
              f"{thm} is not `{hyp}` ⊢ `Spec => []{p}`")
    # TLC's own graphs, re-run for the graph check at the module's cited digest, have the results file's states
    for g in ev["graph"]["rows"]:
        full = [r for r in res["rows"] if r["mut"] == g["mut"] and r["verdict"] == H]
        _need(full and all(r["states"] == g["states"] for r in full),
              f"the graph check's {g['mut']} graph has {g['states']} states, the results file's HOLDS rows "
              f"{[r['states'] for r in full]}")
    code = M.lean_results(CODE_LEAN)
    _need(code["sources"].get(MODEL) == M.sha16(MODEL), f"{CODE_LEAN} cites {MODEL} at another digest")
    model_thms = {k: v for k, v in code["axioms"].items() if k.startswith("Topak.SeatsModel.")}
    _need(sorted(model_thms) == ["Topak.SeatsModel.Inst.model_refines_seats", "Topak.SeatsModel.Inst.model_seats_safe",
                                 "Topak.SeatsModel.model_inv"], f"SeatsModel's reported theorems are {sorted(model_thms)}")
    words_model = re.search(r"SeatsModel is a model of State::apply.*?on the premise that the log delivers "
                            r"increasing indices", code["words"])
    _need(words_model, f"{CODE_LEAN}'s words no longer describe SeatsModel as drawn")
    rp = M.text(REPLAY)
    rp_sum = re.search(r"^(\d+) traces · (\d+) steps · (\d+) not matching$", rp, re.M)
    rp_res = re.search(r"^model results: (.+)$", rp, re.M)
    _need(rp_sum and rp_res, f"{REPLAY}: no summary lines")
    manifest = json.loads((pathlib.Path(__file__).resolve().parents[1] / "manifest.json").read_text("utf-8"))
    for pid in ELSEWHERE:
        svg = pathlib.Path(__file__).resolve().parents[1] / manifest[pid]["file"]
        _need("Seats.tla" in svg.read_text("utf-8"), f"{pid} no longer names Seats.tla")

    rows9 = len(res["rows"])
    ls4 = ce["ls4"]
    c = Canvas(ID,
               "`Seats.tla`: a principal holds one seat, and a seat's kind bounds what it may do. Two invariants, "
               "each broken by its own mutation: checked by TLC, proved by TLAPS and in Lean",
               "The module ADR-0037 §9 asks for, drawn from its own text and from every results file about it, all "
               "read at build time: the machine, its two properties and the section each states, the mutation "
               "matrix, the witnesses, every theorem and lemma, the certified run, the Lean re-encoding and its "
               "check against TLC's state graphs. **What is checked or proved here is checked or proved of the "
               "module, at its constants or by its proofs, and not of the reference**; a model of the code's "
               "`apply` that refines it is drawn at the end, as a model. **The module is frozen**: cited by digest "
               "(Genesis Checkpoint G5, ADR-0046, ADR-0053) and unchanged since 2026.09.29, it models the three "
               "kinds and the Build column ADR-0037 §4 had then, not the kinds the record has gained since.",
               W,
               f"spec/Seats.tla (its header, every definition); spec/Seats_proof.tla (every THEOREM and LEMMA); "
               f"{res['file']}; {pr and ev['files']['proof_results']}; {ev['files']['cert']}; {M.LEAN_RESULTS} "
               f"(compared with {M.LEAN_LATER[10:]}); {M.GRAPH_RESULTS} (compared with {M.GRAPH_LATER[10:]}); "
               f"spec/lean/TopakSpec/Seats.lean; spec/lean/TopakSpec/Mirror/Seats.lean; {CODE_LEAN}; {REPLAY}; "
               f"{MODEL}; {PREMISES} (the two Seats rows and invariant(Seats)); ADR-0037 §1, §4 (its table, and "
               f"the A3, A4 and A5 marks), §9, History R5, B25, B36; ADR-0053; the manifest's titles of "
               f"{', '.join(ELSEWHERE)}. Every file read at the pin its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ---- status
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0037", "accepted", "C3, C4")], tail=[
        ("`SeatsModel.lean`", ("Proved of a model of the code · ADR-0053", "blue", "4 3"), "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    y = P.band(c, X0, y, "The mechanism, as the module states it: a grant seats one principal on one seat with "
                         "its kind's alphabet, and every act is recorded with the kind of the seat it came from")
    y = picture(c, X0, y, WW, kb, ko, set_of(mod, "Principals")) + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: two principals, three seats of fixed kinds, three actions (`Seats.tla`)")
    cl, csrc = M.definition(mod, "KindBound")
    consts = [f"`CONSTANTS Mut` (line {M.line_of(mod, r'^CONSTANTS Mut$')}): `none`, `M_KIND` or `M_SEAT`, the "
              f"only constant"]
    for nm in ("Principals", "Seats", "Acts", "Authoring"):
        ln, src = M.definition(mod, nm)
        consts.append(P.code(src))
    seat_cards = [("Constants: the model is these sets, and `Mut`", consts, "grey", {"bullets": False})]
    for s_, k in ko.items():
        body = [f"`KindBound(\"{k}\")` = {', '.join(f'`{a}`' for a in kb[k])}"]
        if k == "thinker":
            body.append(f"Holds {', '.join(f'`{a}`' for a in authoring)}, the module's one authoring act; never "
                        f"`Vote`")
        else:
            body.append("Holds `Vote` and no authoring act" + (" (the module: \"`Vote` stands for `Vote(deny)` "
                                                                "on an observer seat\")" if k == "observer" else ""))
        seat_cards.append((f"Seat `{s_}`: kind `{k}`", body, "teal",
                           {"sub": f"`KindOf` (line {M.definition(mod, 'KindOf')[0]}) · `KindBound` (line {cl}) · "
                                   f"ADR-0037 §2, §4"}))
    y += P.row_cards(c, X0, y, WW, 30, seat_cards, size=13.5) + 30

    gl, gsrc = M.definition(mod, "Grant")
    hl, hsrc = M.definition(mod, "HoldsElsewhere")
    al, asrc = M.definition(mod, "Act")
    el, esrc = M.definition(mod, "EndRound")
    il, isrc = M.definition(mod, "Init")
    nl, nsrc = M.definition(mod, "Next")
    sl, ssrc = M.definition(mod, "Spec")
    nol, nosrc = M.definition(mod, "NoLease")
    _need('Mut = "M_SEAT"' in gsrc and 'Mut = "M_KIND"' in gsrc, "Grant no longer carries both mutations")
    y += P.row_cards(c, X0, y, WW, 30, [
        ("State: `lease` and `acted`",
         [f"`VARIABLES lease, acted` (line {M.line_of(mod, r'^VARIABLES lease, acted$')})"] + P.code_lines(nosrc)
         + P.code_lines(isrc) + ["**`lease`** is one record per seat; **`acted`** is every admitted act, with the "
                                 "kind of the seat it was admitted under."], "grey", {"bullets": False}),
        (f"`Grant(p, s)` · line {gl}", P.code_lines(gsrc) + P.code_lines(hsrc) +
         ["**§1, §9:** a principal live on another seat is refused. **§4:** the seat is issued its kind's bound, "
          "whatever is asked. `M_SEAT` drops the refusal; `M_KIND` issues all of `Acts`."],
         "teal", {"bullets": False}),
        (f"`Act(s)` · line {al}", P.code_lines(asrc) +
         ["Any act in the live alphabet, recorded with the seat's kind: what `OnlyThinkersAuthor` reads."],
         "teal", {"bullets": False}),
        (f"`EndRound(s)` · line {el}", P.code_lines(esrc) + ["A live lease ends; nothing else changes."],
         "teal", {"bullets": False}),
        (f"`Next` and `Spec` · lines {nl}, {sl}", P.code_lines(nsrc) + P.code_lines(ssrc) +
         ["No fairness: the module states safety only."], "grey", {"bullets": False}),
    ], size=13.5) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The two properties, the section of ADR-0037 each states, and how each is shown")
    m_muts = ["none"] + M.mutations(res)
    y = P.properties(c, X0, y, WW, ev, [(p_, f"ADR-0037 {s_}", w_) for p_, s_, w_ in head_props]) + 50

    # ---- mutations
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    y = P.mutations(c, X0, y, WW, ev, head_muts) + 24
    exp_line = res["head"].get("expected")
    _need(exp_line == "none HOLDS on both; M_KIND breaks §4 only; M_SEAT breaks §1 only; witnesses VIOLATED",
          f"{res['file']}'s expected: line is {exp_line!r}")
    y += P.row_cards(c, X0, y, WW, 30, [
        (f"The results file expects", [f"\"{exp_line}\" (`{res['file'][5:]}`, line 3)"], "grey", {}),
        ("The record says", [f"\"{R5_SAYS}\" (ADR-0037 R5)"], "blue", {}),
        ("The diagram expects, and compares", [
            f"Every cell below against its own literal, both ways: {len(EXPECT)} cells, every one as expected. A "
            f"file that changes a verdict, adds a row or drops one fails the build."], "grey", {}),
    ], size=13.5) + 50

    # ---- the matrix
    y = P.band(c, X0, y, f"Every mutation by every property, read from `{res['file'][5:]}`: "
                         f"{len(m_muts) * len(PROPS)} rows, one cell each")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, MUT_LABEL) + 14
    y += c.para(X0, y, WW, f"Constants: \"{res['head']['jar'].split(' · ', 1)[1]}\" (the file's header; "
                f"`{res['head']['jar'].split(' · ')[0]}`). **The file names no digest of the module**: the build "
                f"checks that `Seats.tla` has not changed since the file was committed (git, at the pin), which "
                f"shows order, not which text TLC ran. The graph check below re-ran TLC on the module at its cited "
                f"digest, and its graphs have the results file's state counts: "
                + "; ".join(f"`{g['mut']}` {P.n(g['states'])}" for g in ev["graph"]["rows"]) + ".",
                13.5, "muted") + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated, so what the two "
                         "properties forbid is not forbidden vacuously")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverActed": "A seat is granted and acts: `OnlyThinkersAuthor` ranges over a non-empty `acted`.",
        "NeverTwoLive": "Two leases live at once: `OneSeatPerPrincipal`'s antecedent is reached, by two "
                        "principals.",
        "NeverObserverVoted": "An observer seat votes: `Vote` is reachable where it is allowed, so "
                              "`OnlyThinkersAuthor`'s second conjunct is not met by forbidding `Vote` everywhere.",
    }) + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, {
        "KindBoundActs": "Every kind's bound is within `Acts`: the type of an issued alphabet.",
        "KindBoundKinds": "The table itself: an authoring act only for a thinker, `Vote` only for the others.",
        "InitTypeOK": "Typing, at the start.",
        "NextTypeOK": "Typing is kept, under every mutation.",
        "InitInvA": "`InvA` (typing, `Alphabets`, `OnlyThinkersAuthor`) at the start.",
        "NextInvA": "`InvA` is inductive unless `M_KIND`: a live alphabet is its seat's bound.",
        "OnlyThinkersAuthorAlways": "ADR-0037 §4, for every behaviour, unless `M_KIND`.",
        "InitInvS": "`InvS` (typing, `OneSeatPerPrincipal`) at the start.",
        "NextInvS": "`InvS` is inductive unless `M_SEAT`: the grant refuses a principal live elsewhere.",
        "OneSeatPerPrincipalAlways": "ADR-0037 §1, for every behaviour, unless `M_SEAT`.",
        "SafeAlways": "Both, unmutated.",
        "MutKindGrantsAll": "Why `M_KIND` must fail: it issues every act to every seat.",
        "MutSeatIgnoresHolder": "Why `M_SEAT` must fail: the grant no longer looks at other seats.",
    }, assumptions_note="\"The module has no constants beyond `Mut`, so the proof carries no model assumptions\": "
                        "the proof module's header") + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the module re-encoded, its theorems proved again, and the encoding checked "
                         "against TLC's state graphs")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.Seats", "Topak.Spec.Seats.Mirror",
               extra_card="Each theorem takes as hypothesis only the mutation that breaks it, as in TLAPS "
                          "(`Seats.lean`'s header).") + 50

    # ---- beyond the module
    y = P.band(c, X0, y, "Beyond the module: what a theorem about it rests on, and a model of the code that refines it")
    y = P.premises(c, X0, y, WW, ev, PROPS, ["invariant(Seats)"]) + 24
    mt = {k.split(".")[-1]: v for k, v in model_thms.items()}
    y += P.row_cards(c, X0, y, WW, 30, [
        ("`SeatsModel.lean`: a model of `State::apply`, proved of the model",
         [f"`{t}` (line {mt[t][1]}): depends on {', '.join(f'`{a}`' for a in mt[t][2])}"
          for t in ("model_inv", "model_refines_seats", "model_seats_safe")] +
         [f"\"{words_model.group(0)}\" (`{CODE_LEAN[10:]}`)"], "blue",
         {"sub": "ADR-0053; ADR-0037 B36"}),
        ("`SeatsReplay.lean`: the reference's recorded traces, run through the model",
         [f"**{rp_sum.group(1)} traces · {P.n(int(rp_sum.group(2)))} steps · {rp_sum.group(3)} not matching** "
          f"(`{REPLAY[10:]}`)", f"model results: {rp_res.group(1)}",
          "**A test, not a proof**: every recorded code step is a model step, the direction the proofs need "
          "(`SeatsModel.lean`'s header)."], "teal", {"sub": "ADR-0053; ADR-0037 B36"}),
        ("What this does not show", [
            "That the code is the model: the model is written from the Rust and read against it, and the replay "
            "tests it; ADR-0053 §5 names the route (`enc-faithful`, T-0045-37).",
            "Anything at constants other than the module's for `model_refines_seats`; `model_inv` holds at any "
            "number of seats and principals."], "red", {}),
    ], size=13.5) + 50

    # ---- what the module models of §4
    y = P.band(c, X0, y, "What the frozen module models of ADR-0037 §4, and what it does not")
    s4 = P.md_table(REC, S4_HEAD)

    def strike(cell):
        return re.sub(r"~~(.+?)~~", r"struck: \1", cell)

    half = (WW - 30) / 2
    t1 = c.table(X0, y, [("Kind", 150, {}), ("Build", 560), ("Run, provisional (G4 item 13), struck at B20", 450),
                         ("Run ⟨A1⟩ (ADR-0043 §2)", half - 1160)],
                 [[strike(x) for x in r] for r in s4], size=13.5, accent="blue")
    rows = []
    for k in KINDS.values():
        rec_build = [b for b in re.findall(r"`(\w+)(?:\(\w+\))?`", [r for r in s4 if r[0] == f"`{k}`"][0][1])]
        not_mod = [a for a in rec_build if a not in acts]
        rows.append([f"`{k}`", ", ".join(f"`{a}`" for a in kb[k]),
                     ", ".join(f"`{a}`" for a in not_mod) if not_mod else "—"])
    x2 = X0 + half + 30
    t2 = c.table(x2, y, [("Kind", 150, {}), ("The module's `KindBound`", 520),
                         ("In §4's Build column, not in the module's `Acts` (the diagram's reading)", half - 670)],
                 rows, size=13.5, accent="teal")
    y += max(t1, t2) + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("Acts the module does not have", [
            f"The module's `Acts` are {', '.join(f'`{a}`' for a in acts)}: `Invoke` and `Submit` are not among them, "
            f"so `Draft` alone stands for \"writes, runs or offers\" (§4), and `Vote` for both `Vote` and "
            f"`Vote(deny)`. The module's own comment says the second."], "grey", {}),
        ("Kinds the record gained after the module", [
            "**`operator`** (ADR-0037 A4, ratified in Batch 34) and **`emergency`** (A3, Batch 34): ADR-0050 and "
            "ADR-0052 state their own modules, `Operators.tla` and `Emergency.tla`. **`orchestrator`** (A5) is "
            "pending and not applied.",
            "None of them is a kind of `Seats.tla`, which is not edited: its theorems are about three kinds."],
         "amber", {}),
        ("The Run column", [
            "§4's Run column (A1, after ADR-0043 §2) is `RunSeats.tla`'s, whose `M_OBSEMIT` is the provisional "
            "column A1 struck (ADR-0037 A1). This module has the Build column only."], "grey", {}),
    ], size=13.5) + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `Seats.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    y = P.digests(c, X0, y, WW, ev, extra=[(MODEL, M.sha16(MODEL), f"`{CODE_LEAN}`")])
    return c
