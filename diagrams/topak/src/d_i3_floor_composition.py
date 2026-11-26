"""I3 — `FloorComposition.tla`, ADR-0030's verified floor tier: monotone composition of a verified floor with an
unverified bundle (§1), the bundle's lack of a write path to the floor's inputs (§3), and the envelope the floor's
analysis proves, drawn whole from the module's own text and every results file about it.

Built on modpage.py's bands (family I). ADR-0030 §9's table is drawn whole and each row compared with the results
file; I4 imports s9_compare for the same table."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I3", "floor-composition"
NAME = "FloorComposition"
MODULE_FILES = ("spec/FloorComposition.tla", "spec/FloorComposition_proof.tla")
W = 3400

REC = "decisions/ADR-0030.md"
CODE_LEAN = "mechanism/lean/Admit-results-2026.10.06c.txt"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "AdmitImpliesFloorPermit", "EnvelopeHolds", "FloorErrorIsDeny", "BundleRefusalHonored",
         "BundleCannotWriteFloorInputs"]
EXPECT = {("none", "Safe"): H,
          ("M_OVERRIDE", "AdmitImpliesFloorPermit"): X, ("M_OVERRIDE", "EnvelopeHolds"): X,
          ("M_ERR", "FloorErrorIsDeny"): X, ("M_ERR", "EnvelopeHolds"): X,
          ("M_FAILOPEN", "BundleRefusalHonored"): X, ("M_FAILOPEN", "EnvelopeHolds"): H,
          ("M_WRITE", "BundleCannotWriteFloorInputs"): X, ("M_WRITE", "EnvelopeHolds"): X}
S9_HEAD = ["Module", "Check", "Mut", "Invariant", "Result"]
S3_SAYS = "No bundle has a write path to any value the floor reads."
ELSEWHERE = ["G1", "G3", "H3", "H7", "H9"]
POLICIES = ["P1", "P2", "P3", "F1"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def s9_compare(full):
    """ADR-0030 §9's rows against the whole results file (both modules' sections): each row's module, mutation,
    invariants and result must be rows of the file with those verdicts. Returns compare(row) for
    modpage.record_table."""
    mods = {"Composition": "FloorComposition", "Routing": "FloorRouting"}

    def compare(row):
        mod = mods.get(row[0])
        if mod is None:
            raise M.CorpusError(f"{REC} §9: module {row[0]!r}")
        muts = re.findall(r"`(\w+)`", row[2]) or [row[2].strip()]
        _need(len(muts) == 1, f"§9 row {row[1][:30]!r} names {muts}")
        mut = muts[0]
        if "witnesses" in row[3]:
            props = [r["prop"] for r in full if r["module"] == mod and r["mut"] == mut and r["prop"].startswith("Never")]
            _need(len(props) == 3 and "three" in row[3], f"§9 row {row[1][:30]!r}: witnesses {props}")
        else:
            props = re.findall(r"`(\w+)`", row[3])
        word = H if "holds" in row[4].lower() else X if "counterexample" in row[4].lower() else None
        _need(word and props, f"§9 row {row[1][:30]!r} does not read")
        names = []
        for p in props:
            hit = [r for r in full if r["module"] == mod and r["mut"] == mut and r["prop"] == p]
            _need(len(hit) == 1, f"§9 row {row[1][:30]!r}: {len(hit)} rows for {mod} {mut} {p}")
            _need(hit[0]["verdict"] == word, f"§9 row {row[1][:30]!r}: {p} is {hit[0]['verdict']} in the file")
            names.append(f"`{hit[0]['name']}`")
        return "agrees: " + ", ".join(names)

    return compare


def full_log():
    rows = M.tlc_log(M.MODULES[NAME]["tlc"])["rows"]
    for r in rows:
        r["mut"] = r["params"]["Mut"]
    return rows


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts] == ["none"] + M.mutations(res), "the header's mutations are not the file's")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == ["AdmitImpliesFloorPermit", "FloorErrorIsDeny", "BundleRefusalHonored",
                                    "BundleCannotWriteFloorInputs", "EnvelopeHolds"], "the header's properties")
    head_props = [(p, f"ADR-0030 {s}" if s else None, w) for p, s, w in hp]
    rec = M.text(REC)
    _need(S3_SAYS in re.sub(r"\s+", " ", rec), "ADR-0030 §3 no longer says what the diagram quotes")
    binding = P.md_rows(P.PREMISES, P.PREMISE_HEAD, ["BundleCannotWriteFloorInputs"])[0]
    _need(binding[2] == "ADR-0030 §4", f"the binding's row for BundleCannotWriteFloorInputs cites {binding[2]}")
    header = M.header_comment(mod)
    pol = []
    for p in POLICIES:
        hit = [ln.strip() for ln in header if re.match(rf"^\s+{p}\s{{2}}", ln)]
        _need(len(hit) == 1, f"the header's policy {p}")
        pol.append(hit[0])
    for g in ev["graph"]["rows"]:
        full = [r for r in res["rows"] if r["mut"] == g["mut"] and r["verdict"] == H]
        _need(all(r["states"] == g["states"] for r in full),
              f"the graph check's {g['mut']} graph has {g['states']} states, the file's HOLDS rows "
              f"{[r['states'] for r in full]}")
    code = M.lean_results(CODE_LEAN)
    model = "mechanism/lean/Topak/FloorRefinement.lean"
    _need(code["sources"].get(model) == M.sha16(model), f"{CODE_LEAN} cites {model} at another digest")
    fr = {k.split(".")[-1]: v for k, v in code["axioms"].items() if k.startswith("Topak.FloorRefinement.")}
    _need(sorted(fr) == sorted(code["theorems"]["FloorRefinement"]) or set(fr) <= set(code["theorems"]["FloorRefinement"]),
          "FloorRefinement's reported theorems")
    fr_words = re.search(r"FloorRefinement proves.*?discharges no stage of T-0045-28 \(ADR-0053 §5\)", code["words"])
    _need(fr_words, f"{CODE_LEAN}'s words no longer describe FloorRefinement as drawn")
    full = full_log()

    c = Canvas(ID,
               "`FloorComposition.tla`: nothing is admitted without a clean floor permit, whatever the bundle says, "
               "and the bundle cannot write what the floor reads. Five invariants, each with the mutations that "
               "break it: checked by TLC, proved by TLAPS and in Lean",
               "The module ADR-0030 §9 reports, drawn from its own text and from every results file about it, all "
               "read at build time: the decision, the floor's four policies and the havoc bundle, the five "
               "properties and the section each states, the mutation matrix, the witnesses, ADR-0030 §9's table "
               "compared row by row, every theorem and lemma, the certified run, the Lean encoding, mirror and graph "
               "check, and the model of the code's decision that refines it. **What is checked or proved here is "
               "checked or proved of the module, at its constants or by its proofs: one small floor text and havoc "
               "bundles, not Cedar, not the floor in force and not the reference** (ADR-0030 §9, Scope). The "
               "module is frozen, cited by digest (ADR-0030 §9, ADR-0046, ADR-0053).",
               W,
               f"spec/FloorComposition.tla (its header, every definition); spec/FloorComposition_proof.tla (every "
               f"THEOREM and LEMMA); {res['file']} (its FloorComposition sections, and for §9's table all of it); "
               f"{ev['files']['proof_results']}; {ev['files']['cert']}; {M.LEAN_RESULTS} (compared with "
               f"{M.LEAN_LATER[10:]}); {M.GRAPH_RESULTS} (compared with {M.GRAPH_LATER[10:]}); "
               f"spec/lean/TopakSpec/FloorComposition.lean; spec/lean/TopakSpec/Mirror/FloorComposition.lean; "
               f"{CODE_LEAN}; {model}; {P.PREMISES} (the FloorComposition rows and invariant(FloorComposition)); "
               f"ADR-0030 §1, §3, §4, §9 (its table, findings and scope); the manifest's titles of "
               f"{', '.join(ELSEWHERE)}. Every file read at the pin its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0030", "accepted", "C1")], tail=[
        ("`FloorRefinement.lean`", ("Proved of a transcription of the code's decision · ADR-0053", "blue", "4 3"),
         "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    y = P.band(c, X0, y, "The mechanism, as the module states it: an admit needs a clean floor permit and an "
                         "affirmative bundle allow, and every decision records what it did against each property")
    dl = M.definition(mod, "Decide")[0]
    y = P.flow_picture(
        c, X0, y, WW,
        ("A request, and a havoc bundle", ["a seat, an act and a target; the bundle's answer is any of "
                                           "`BundleOutcomes`, at every decision"], "brown"),
        (f"The decision (`Decide`, line {dl})", [
            "**①** the slice may drop `owner` or `sealed`: a fault §4 forbids, modelled so that §1 holds without it",
            "**②** `FloorPermit`: the engine allows **and** no policy errored (ADR-0030 §1). `M_ERR` [[red|takes "
            "the engine's decision, errors ignored]].",
            "**③** `BundleDeny`: anything but `allow` denies (§1). `M_FAILOPEN` [[red|denies only on]] `deny`.",
            "**④** `Admit` is ② and not ③. `M_OVERRIDE` [[red|admits on a bundle allow alone]]."], "teal"),
        ("Not admitted", ["Only the witnesses' flags may change."], "red"),
        ("What each decision records: one flag per property", "teal", [
            ("Flag `admitNoFloor`", ["set when an admit had no clean floor permit"], "teal"),
            ("Flag `admitWithErr`", ["set when an admit came with an engine error"], "teal"),
            ("Flag `admitNoBundle`", ["set when an admit had no bundle allow"], "teal"),
            ("Flag `admitOutside`", ["set when an admit lies outside `Envelope`, stated on `truth`"], "teal")]),
        None,
        [("ADR-0030 §1, read on the flags", ["`AdmitImpliesFloorPermit`, `FloorErrorIsDeny`, "
                                             "`BundleRefusalHonored`: each flag never set"], "state"),
         ("The envelope, read on the flags", ["`EnvelopeHolds`: `admitOutside` never set"], "state")],
        {"ask": "asks", "write": "⑤ the flags"},
        "**Key.** ① to ④ are `Decide`'s steps; ⑤ the flags it sets, one per property (and three witnesses' flags, "
        "below). Red marks where each mutation acts. The picture is the diagram's own drawing of the definitions "
        "below.") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("The floor: four policies, evaluated with Cedar's rules (the module's header)",
         [f"`{x}`" for x in pol] + ["\"any satisfied forbid denies; else any satisfied permit allows; else deny. "
                                    "A policy whose condition reads a missing attribute errors and is SKIPPED\""],
         "blue", {"bullets": False}),
        ("The floor's inputs: written by the lift alone (ADR-0030 §3)",
         [f"`Reassign(t, s)` (line {M.definition(mod, 'Reassign')[0]}) and `Seal(t)` (line "
          f"{M.definition(mod, 'Seal')[0]}) write `fstore` and the ghost `truth` together.",
          f"`BundleWrite(t, s)` (line {M.definition(mod, 'BundleWrite')[0]}) writes `fstore` alone, and is "
          f"enabled [[red|only under]] `M_WRITE`."], "green", {}),
        ("ADR-0030 §3, read on the stores", ["`BundleCannotWriteFloorInputs`: `fstore = truth`, the floor reads "
                                             "only what the lift wrote"], "blue", {}),
    ], size=13.5) + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: the floor's evaluation, the bundle's answer, and the decision "
                         "(`FloorComposition.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Constants: the model", ["Seats", "Targets", "Acts", "NONE", "BundleOutcomes"],
          [f"`CONSTANTS Mut` (line {M.line_of(mod, r'^CONSTANTS Mut$')}): `none` or one of four mutations"],
          "grey"),
         ("The policies, three-valued", ["OwnerIs", "SealedIs", "Permits", "Forbids"], [], "blue"),
         ("The engine, and the floor's permit", ["EngineAllow", "EngineErr", "FloorPermit"],
          ["ADR-0030 §1: a permit with an error is not a permit."], "teal"),
         ("The bundle, and the admit", ["BundleDeny", "Admit"], ["Composition is monotone: the bundle can only "
                                                                 "subtract."], "teal")],
        [("State, and the start", ["Rec", "Init", "Flags"],
          [f"`VARIABLES` (line {M.line_of(mod, r'^VARIABLES truth')}): `truth`, `fstore`, four property flags and "
           f"three witness flags"], "grey"),
         (None, ["Envelope"], ["What the floor's analysis would prove, stated against `truth`, not the slice "
                               "(ADR-0030 §9)."], "blue"),
         (None, ["Decide"], [], "teal"),
         ("The lift, a bundle's write, and `Next`", ["Reassign", "Seal", "BundleWrite", "Next", "Spec"],
          ["No fairness: safety only."], "grey")],
    ]) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The five properties, the section of ADR-0030 each states, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, head_props, note={
        "BundleCannotWriteFloorInputs": "[[red|The binding's row says ADR-0030 §4]] (`theorem-premise-binding.md`); "
                                        "§3's text is \"No bundle has a write path to any value the floor reads\" "
                                        "(a finding: the diagram's)",
        "EnvelopeHolds": "ADR-0030 §9: \"what the floor's analysis would prove, against what the lift actually "
                         "wrote\""}) + 50

    # ---- mutations
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    y = P.mutations(c, X0, y, WW, ev, head_muts) + 50

    # ---- the matrix
    y = P.band(c, X0, y, f"Every mutation by every property, read from `{res['file'][5:]}` (its "
                         f"`FloorComposition` sections)")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, dict(head_muts)) + 14
    y += c.para(X0, y, WW, "Each mutation is run on the properties ADR-0030 §9 lists for it and on `EnvelopeHolds`; "
                "the other cells are not run. `Safe` is run unmutated. Under `M_FAILOPEN` the envelope still holds: "
                "ADR-0030 §9 finding 3, \"Bundle fail-closed protects the bundle, not the floor\".", 13.5,
                "muted") + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated, so what the properties "
                         "forbid is not forbidden vacuously")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverAdmitted": "Something is admitted: every property ranges over reachable admits.",
        "NeverNarrowed": "A bundle refuses what the floor permits, the one ADR-0030 names: "
                         "`AdmitImpliesFloorPermit` does not hold because the tiers never disagree (§9 finding 4).",
        "NeverFloorError": "The floor errors: `FloorErrorIsDeny` is not met by an engine that never errs.",
    }) + 50

    # ---- the record's table
    y = P.band(c, X0, y, "ADR-0030 §9's table, every row and column, each compared with the results file")
    y += P.record_table(c, X0, y, WW, REC, S9_HEAD, (170, 720, 170, 560, 260), s9_compare(full)) + 14
    y += c.para(X0, y, WW, "The `Routing` rows are `FloorRouting.tla`'s, in the same results file (I4). Each row is "
                "matched to the file's rows by module, mutation and invariant, and its result to theirs; a row the "
                "file does not bear out fails the build.", 13.5, "muted") + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, {
        "DecideFlags": "What a decision writes: the flags, from one bundle answer and one slice.",
        "InitTypeOK": "Typing, at the start.",
        "NextTypeOK": "Typing is kept, under every mutation.",
        "AdmitIsFloorPermit": "Unless `M_ERR` or `M_OVERRIDE`, an admit is a clean floor permit.",
        "AdmitIsBundleAllow": "Unless `M_FAILOPEN` or `M_OVERRIDE`, an admit had a bundle allow.",
        "PermitWithinEnvelope": "A clean permit on the lift's store lies inside the envelope, whatever the slice "
                                "dropped.",
        "FlagsUnchanged": "Only a decision moves the flags.",
        "NextFloorFlags": "The two floor flags stay clear unless `M_ERR` or `M_OVERRIDE`.",
        "NextBundleFlag": "The bundle flag stays clear unless `M_FAILOPEN` or `M_OVERRIDE`.",
        "NextInputs": "The stores stay equal unless `M_WRITE`.",
        "NextInvE": "The envelope's invariant is kept unless `M_WRITE`, `M_ERR` or `M_OVERRIDE`.",
        "InitAll": "Typing and all five, at the start.",
        "AdmitImpliesFloorPermitAlways": "ADR-0030 §1, for every behaviour, unless `M_ERR` or `M_OVERRIDE`.",
        "FloorErrorIsDenyAlways": "ADR-0030 §1, unless `M_ERR` or `M_OVERRIDE`.",
        "BundleRefusalHonoredAlways": "ADR-0030 §1, unless `M_FAILOPEN` or `M_OVERRIDE`.",
        "BundleCannotWriteFloorInputsAlways": "ADR-0030 §3, unless `M_WRITE`.",
        "EnvelopeHoldsAlways": "The envelope, unless `M_WRITE`, `M_ERR` or `M_OVERRIDE`.",
        "SafeAlways": "All five, unmutated.",
        "MutOverrideAdmitsOnAllow": "Why `M_OVERRIDE` must fail: a bundle allow admits.",
        "MutErrPermitsWithError": "Why `M_ERR` must fail: an engine allow is a permit, errors or not.",
        "MutFailOpenPassesErrors": "Why `M_FAILOPEN` must fail: an error or an absence is not a deny.",
        "MutWriteDivergesInputs": "Why `M_WRITE` must fail: a bundle's write splits `fstore` from `truth`.",
    }) + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the module re-encoded, its theorems proved again, and the encoding checked "
                         "against TLC's state graphs")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.FloorComposition", "Topak.Spec.FloorComposition.Mirror") + 50

    # ---- beyond
    y = P.band(c, X0, y, "Beyond the module: what a theorem about it rests on, and a transcription of the code's "
                         "decision that refines it")
    y = P.premises(c, X0, y, WW, ev, head_props and [p for p, _, _ in head_props],
                   ["invariant(FloorComposition)"],
                   note="The `EnvelopeHolds` row is shared with `FloorRouting.tla`'s `FloorNeverVacuous`.") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("`FloorRefinement.lean`: the code's decision, transcribed, proved a `Decide` step",
         [f"`{t}` (line {v[1]}): depends on {', '.join(f'`{a}`' for a in v[2]) or 'no axioms'}"
          for t, v in fr.items()] + [f"\"{fr_words.group(0)}\" (`{CODE_LEAN[10:]}`)"], "blue",
         {"sub": "ADR-0053"}),
        ("What this does not show", [
            "That Cedar decides as the module's three-valued evaluation does: the engine premise, T-0045-3.",
            "Anything of the floor in force: one four-policy floor text is modelled, and the floor in force is "
            "Genesis-provisional (ADR-0030 A3)."], "red", {}),
    ], size=13.5) + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `FloorComposition.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, extra=[(model, M.sha16(model), f"`{CODE_LEAN}`")],
              note=f"`{res['file']}`'s header cites `FloorComposition.tla` by digest, compared above.")
    return c
