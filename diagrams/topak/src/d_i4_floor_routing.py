"""I4 — `FloorRouting.tla`, ADR-0030 §5: floor revisions classified mechanically and routed to the authority ToO
§3.2 requires, drawn whole from the module's own text and every results file about it.

Built on modpage.py's bands (family I). Its TLC rows are sections of FloorComposition's results file; ADR-0030 §9's
table is compared with them by I3's s9_compare."""
import modules as M
import modpage as P
from lib import Canvas
from d_i3_floor_composition import full_log, s9_compare, S9_HEAD

ID, SLUG = "I4", "floor-routing"
NAME = "FloorRouting"
MODULE_FILES = ("spec/FloorRouting.tla", "spec/FloorRouting_proof.tla")
W = 3400

REC = "decisions/ADR-0030.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "NoWideningWithoutIssuance", "FloorNeverVacuous"]
EXPECT = {("none", "Safe"): H, ("M_ROUTE", "NoWideningWithoutIssuance"): X, ("M_GATE", "FloorNeverVacuous"): X}
FIRST_LINE = "Properties for ADR-0030 §5: floor revisions are classified mechanically and"
ELSEWHERE = ["G3", "H3"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts] == ["none"] + M.mutations(res), "the header's mutations are not the file's")
    hp = M.header_properties(mod)
    _need([(p, s) for p, s, _ in hp] == [("NoWideningWithoutIssuance", None), ("FloorNeverVacuous", None)],
          "the header's properties")
    _need(M.header_comment(mod)[0].strip() == FIRST_LINE, "the header's first line has changed")
    head_props = [(p, "ADR-0030 §5 (the header's first line)", w) for p, _, w in hp]
    hyps = {s["name"]: s["assume"] for s in ev["statements"] if s["kind"] == "THEOREM"}
    _need(set(hyps.values()) == {'Mut = "none"'}, f"the theorems' hypotheses are {set(hyps.values())}")
    full = full_log()
    rl, pl, il, gl = (M.definition(mod, n_)[0] for n_ in ("Route", "Promote", "IssueAndPromote", "PassesGates"))

    c = Canvas(ID,
               "`FloorRouting.tla`: a floor that permits anything its predecessor did not is never deployed without "
               "an anchor issuance, and the deployed floor never permits everything. Two invariants, each with the "
               "mutation that breaks it: checked by TLC, proved by TLAPS and in Lean",
               "The routing half of ADR-0030 §9's property check, drawn from the module's own text and from every "
               "results file about it, all read at build time: the router, the two properties, the mutation matrix, "
               "the witnesses, ADR-0030 §9's table compared row by row, every theorem and lemma, the certified run "
               "and the Lean re-encoding. **A floor is modelled by its meaning, the set of requests it permits, over "
               "a three-request universe, and implication is inclusion: the module \"checks the routing logic, not "
               "the analyzer\"** (its header), on the solver-trust assumption ADR-0030 states. Nothing here is said "
               "of the reference. The module is frozen, cited by digest (ADR-0030 §9, ADR-0046, ADR-0053).",
               W,
               f"spec/FloorRouting.tla (its header, every definition); spec/FloorRouting_proof.tla (every THEOREM and "
               f"LEMMA); {res['file']} (its FloorRouting sections, and for §9's table all of it); "
               f"{ev['files']['proof_results']}; {ev['files']['cert']}; {M.LEAN_RESULTS} (compared with "
               f"{M.LEAN_LATER[10:]}); spec/lean/TopakSpec/FloorRouting.lean; {P.PREMISES} (the FloorRouting rows "
               f"and invariant(FloorRouting)); ADR-0030 §5, §9 (its table and scope); the manifest's titles of "
               f"{', '.join(ELSEWHERE)}. Every file read at the pin its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0030", "accepted", "C1")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    y = P.band(c, X0, y, "The mechanism, as the module states it: a proposal that passes the gate is promoted by "
                         "quorum only if it implies the floor in force, and goes to the anchor otherwise")
    y = P.flow_picture(
        c, X0, y, WW,
        ("A proposal", ["any floor `new` over `U`: \"a Build author, Byzantine by premise, may propose any "
                        "floor\" (the header)"], "brown"),
        ("The router", [
            f"**①** `PassesGates(new)` (line {gl}): the non-vacuity gate, `new # U` (ADR-0030 §5). `M_GATE` "
            f"[[red|turns it off]].",
            f"**②** `Route(new, deployed)` (line {rl}): a revision that implies the floor in force, `new \\subseteq "
            f"deployed`, is promoted by quorum; any other goes to the anchor. `M_ROUTE` [[red|sends only a strict "
            f"superset]] to the anchor, so an incomparable revision is promoted by quorum."], "teal"),
        ("Refused, at ① or by the anchor", ["Nothing changes. An anchor's refusal is a stutter, and the module "
                                            "omits it (its comment)."], "red"),
        ("`deployed`: the floor in force, as the requests it permits", "teal", [
            (f"Promoted by quorum: `Promote`, line {pl}", ["only a narrowing, unless `M_ROUTE`"], "teal"),
            (f"Issued, then promoted: `IssueAndPromote`, line {il}", ["anything else, with the anchor's consent"],
             "blue"),
            ("At the start: `Genesis`", ["the floor permits `r1` of `U = {r1, r2, r3}`"], "grey")]),
        ("The flags", ["`wideNoIssue`: set when a widening was promoted without an issuance; three witnesses' "
                       "flags"], "grey"),
        [("ADR-0030 §5, read on the flags", ["`NoWideningWithoutIssuance`: `wideNoIssue` never set"], "record"),
         ("ADR-0030 §5, read on `deployed`", ["`FloorNeverVacuous`: `deployed # U`"], "state")],
        {"ask": "proposes", "write": "③ a new floor", "act": "④ the flags"},
        "**Key.** ① and ② are the router's two checks; ③ the floor it deploys; ④ the flags it sets. Red marks where "
        "each mutation acts. The picture is the diagram's own drawing of the definitions below.") + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: a floor as a set, the router, and the two ways a floor is deployed "
                         "(`FloorRouting.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Constants and state", ["U", "Genesis", "Init"],
          [f"`CONSTANTS Mut` (line {M.line_of(mod, r'^CONSTANTS Mut$')}): `none`, `M_ROUTE` or `M_GATE`",
           f"`VARIABLES` (line {M.line_of(mod, r'^VARIABLES deployed')}): `deployed` and four flags"], "grey"),
         ("Implication is inclusion", ["NewImpliesOld", "OldImpliesNew", "Incomparable"],
          ["\"`F' => F` is `F' \\subseteq F`\" (the header): the analyzer's answer, trusted."], "blue"),
         (None, ["Route"], [], "teal"),
         (None, ["PassesGates"], [], "teal")],
        [(None, ["Promote"], [], "teal"),
         (None, ["IssueAndPromote"], [], "blue"),
         ("`Next` and `Spec`", ["Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The two properties, the section of ADR-0030 they state, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, head_props) + 50

    # ---- mutations
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    y = P.mutations(c, X0, y, WW, ev, head_muts) + 50

    # ---- the matrix
    y = P.band(c, X0, y, f"Every mutation by every property, read from `{res['file'][5:]}` (its `FloorRouting` "
                         f"sections)")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, dict(head_muts)) + 14
    y += c.para(X0, y, WW, "Each mutation is run on the property it must break; `Safe` is run unmutated. The rows are "
                "sections of `FloorComposition`'s results file, whose header cites this module's digest.", 13.5,
                "muted") + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverIncomparable": "An incomparable revision is deployed: the case `M_ROUTE` mishandles is reached.",
        "NeverRelaxIssued": "A relaxation goes to the anchor and is issued: the anchor's path is used.",
        "NeverTightened": "A strict narrowing is promoted by quorum: the ordinary path is used.",
    }) + 50

    # ---- the record's table
    y = P.band(c, X0, y, "ADR-0030 §9's table, every row and column, each compared with the results file")
    y += P.record_table(c, X0, y, WW, REC, S9_HEAD, (170, 720, 170, 560, 260), s9_compare(full)) + 14
    y += c.para(X0, y, WW, "The `Composition` rows are `FloorComposition.tla`'s (I3).", 13.5, "muted") + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, {
        "InitSafe": "Both properties, at the start.",
        "PromoteNarrows": "Unmutated, a revision promoted by quorum implies the floor in force.",
        "NextSafe": "Both are kept, unmutated.",
        "SafeAlways": "Both, for every behaviour, unmutated.",
        "NoWideningAlways": "ADR-0030 §5's routing, unmutated.",
        "NeverVacuousAlways": "ADR-0030 §5's non-vacuity gate, unmutated.",
        "MutGateAdmitsU": "Why `M_GATE` must fail: the always-allowing floor passes.",
        "MutRoutePromotesIncomparable": "Why `M_ROUTE` must fail: an incomparable revision is promoted.",
    }) + 14
    y += c.para(X0, y, WW, "Every theorem here takes `Mut = \"none\"` as its hypothesis, where `Seats_proof.tla` and "
                "`FloorComposition_proof.tla` take only the mutations that break each property: each property is "
                "proved unmutated, and not shown to survive the other mutation (the diagram's reading).", 13.5,
                "muted") + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the module re-encoded and its theorems proved again")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.FloorRouting") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, ["NoWideningWithoutIssuance", "FloorNeverVacuous"], ["invariant(FloorRouting)"],
                   note="The `FloorNeverVacuous` row is shared with `FloorComposition.tla`'s `EnvelopeHolds`.") + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `FloorRouting.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, note=f"`{res['file']}`'s header cites `FloorRouting.tla` by digest, compared above.")
    return c
