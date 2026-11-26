"""I8 — `Confinement_A1.tla`, the successor to `Confinement.tla` that carries ADR-0034 finding 6: one definition
changed, rung 0 a row of the module, and its state read by the reference's trace harness through
`ConfinementRefinement.tla`. Its proofs are **not certified**: three obligations failed in the certified run.

Built on I7's bands (d_i7_confinement), which draw the same machine. What is new here is drawn as such: the one
changed definition, every other definition compared with I7's module, and every row the two runs share compared."""
import re

import modules as M
import modpage as P
from lib import Canvas
from d_i7_confinement import (ROLES, band_machine, band_matrix, band_mutations, band_picture, band_proofs,
                              band_witnesses, rung)

ID, SLUG = "I8", "confinement-a1"
NAME = "Confinement_A1"
MODULE_FILES = ("spec/Confinement_A1.tla", "spec/Confinement_A1_proof.tla")
W = 3400

REC = "decisions/ADR-0034.md"
PRED = "spec/Confinement.tla"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "ContainedMeansConfined", "NoSilentDowngrade", "ContestedStopped", "FreshAppraisal"]
WITNESSES = ["NeverContainedEffect", "NeverMediatedEffect", "NeverContested", "NeverRenewContested"]
EXPECT_ROWS = {
    "safe0": H, "safe1": H, "safe2": H, "safe3": H, "wc0": H, "wc1": X, "wc3": X, "wm0": X, "wx0": H, "wx1": H,
    "wx3": X, "h0": H, "hx0": H, "h1": X, "h2": X, "h3": H, "hw3": X, "c3": X, "u3": X, "s3": X, "d3": X, "p3": X,
    "rl3": X, "wrc3": H}
F6_FIX = "`Evidence(p) == IF Declared <= 1 THEN guest[p].asked ELSE guest[p].boot`"
ELSEWHERE = ["C4", "G3", "H3"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def code_only(src):
    """A definition's text without its comments, whitespace collapsed."""
    src = re.sub(r"\(\*.*?\*\)", " ", src, flags=re.S)
    src = re.sub(r"\\\*[^\n]*", " ", src)
    return re.sub(r"\s+", " ", src).strip()


def build():
    ev = M.evidence(NAME)
    mod = ev["files"]["module"]
    res = ev["tlc"]
    rows = res["rows"]
    got = {r["name"]: r["verdict"] for r in rows}
    _need(got == EXPECT_ROWS, f"the file's rows are not the diagram's: "
                              f"{sorted(set(got.items()) ^ set(EXPECT_ROWS.items()))[:6]}")
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts][1:] == M.mutations(res), "the header's mutations are not the file's")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == PROPS[1:], "the header's properties")
    ce = ev["cert"]
    _need(not ce["certified"] and ce["last"] == "NOT CERTIFIED: 3 obligation(s) failed (last backend tried: isabelle).",
          f"the certified run's last line is {ce['last']!r}")
    _need([s["name"] for s in ev["statements"]] == list(ROLES), "the proof module's statements are not I7's")
    rec = re.sub(r"\s+", " ", M.text(REC))
    _need(F6_FIX in rec, "ADR-0034 finding 6 no longer gives the correction the diagram quotes")
    # the one change: every definition of the two modules compared, comments aside
    a_defs, p_defs = M.pin().defined_in(mod), M.pin().defined_in(PRED)
    _need(set(a_defs) == set(p_defs), f"the two modules define different names: {set(a_defs) ^ set(p_defs)}")
    mtext, ptext = M.text(mod), M.text(PRED)
    defs = [n_ for n_ in a_defs if re.search(rf"^{n_}\s*(?:\([^)]*\))?\s*==", mtext, re.M)]
    _need(all(re.search(rf"^{n_}\s*(?:\([^)]*\))?\s*==", ptext, re.M) for n_ in defs), "a definition is in one only")
    changed = [n_ for n_ in defs if code_only(M.definition(mod, n_)[1]) != code_only(M.definition(PRED, n_)[1])]
    _need(changed == ["Evidence"], f"the definitions that differ are {changed}, not Evidence alone")
    ea, ep = M.definition(mod, "Evidence"), M.definition(PRED, "Evidence")
    # the rows the two runs share
    pred = M.evidence("Confinement")["tlc"]["rows"]
    check = lambda r: (rung(r), r["mut"], r["prop"])  # noqa: E731
    prow = {check(r): r for r in pred}
    _need(len(prow) == len(pred), "a check run twice in the predecessor's files")
    shared = [r for r in rows if check(r) in prow]
    renamed = sorted({r["name"] for r in rows if r["name"] in {q["name"] for q in pred}} -
                     {r["name"] for r in shared if prow[check(r)]["name"] == r["name"]})
    upper = [r for r in shared if rung(r) >= 1]
    # a row that holds explores every reachable state, so its count is the model's; a counterexample's count is
    # where TLC stopped, which the two runs' TLC builds need not share
    _need(all(prow[check(r)]["verdict"] == r["verdict"] for r in upper), "a verdict at rungs 1 to 3 differs between "
          "the two runs, though the header says nothing there depends on the change")
    _need(all(prow[check(r)]["states"] == r["states"] for r in upper if r["verdict"] == H),
          "a full exploration at rungs 1 to 3 has another state count in the two runs")
    h0 = [r for r in shared if r["name"] == "h0"]
    _need(h0 and h0[0]["states"] > prow[check(h0[0])]["states"], "h0 does not explore more states than I7's")
    tlcs = []
    for f_ in [M.MODULES["Confinement"]["tlc"][0], res["file"]]:
        m_ = re.search(r"· (TLC[^·]+?) ·", M.text(f_).split("\n")[1] if f_ == res["file"] else
                       [ln for ln in M.text(f_).split("\n") if ln.startswith("Module: ")][0])
        _need(m_, f"{f_}: no TLC version")
        tlcs.append((f_, m_.group(1).strip()))
    diff0 = [r for r in shared if rung(r) == 0 and (prow[check(r)]["verdict"], prow[check(r)]["states"]) !=
             (r["verdict"], r["states"])]
    _need([r["name"] for r in diff0 if prow[check(r)]["verdict"] != r["verdict"]] == ["hx0"],
          "the rung-0 rows whose verdict moved are not hx0 alone")
    hc = M.header_comment(mod)
    rung_lines = []
    for ln in hc:
        t = ln.strip()
        if re.match(r"^rung [123]\s", t):
            rung_lines.append(f"**{t[:6]}**{t[6:]}")
        elif rung_lines and len(rung_lines) < 4 and re.match(r"^\s{10,}\S", ln) and not t.startswith("Profiles"):
            rung_lines[-1] += " " + t
        elif rung_lines:
            break
    _need(len(rung_lines) == 3, "the header's rung table")
    succ = " ".join(ln.strip() for ln in hc[2:16] if ln.strip())

    c = Canvas(ID,
               "`Confinement_A1.tla`: the successor that carries ADR-0034 finding 6. One definition changes, rung 0 "
               "becomes a row of the module, and nothing checked at rungs 1 to 3 moves: checked by TLC at rungs 0 to "
               "3, proved by TLAPS and in Lean, and **not certified**",
               "The successor to `Confinement.tla` (I7), drawn from its own text and its results file, all read at "
               "build time: the one changed definition, beside its predecessor's and with every other definition "
               "compared; every row the two runs share, compared; the same machine, properties, mutations and "
               "witnesses; every theorem and lemma; the proof run and the certified run that refused it; and the "
               "Lean re-encoding, which covers both modules. **What is checked or proved here is of the module, not "
               "of the reference**; the reference's recorded states are read against it through "
               "`ConfinementRefinement.tla` (I9). **The proofs are proved and not certified.**",
               W,
               f"spec/Confinement_A1.tla (its header, every definition); spec/Confinement.tla (every definition, for "
               f"the comparison); spec/Confinement_A1_proof.tla (every THEOREM and LEMMA); {res['file']}; "
               f"{' and '.join(M.MODULES['Confinement']['tlc'])} (the shared rows); {ev['files']['proof_results']}; "
               f"{ev['files']['cert']}; {M.LEAN_RESULTS} (compared with {M.LEAN_LATER[10:]}); "
               f"spec/lean/TopakSpec/Confinement.lean; {P.PREMISES}; ADR-0034 §2–§4, finding 6, B29; G10 item 74. "
               f"Every file read at the pin its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0034", "accepted", "C2, C4")]))
    y += c.para(X0, y, WW, "The module's header: \"" + succ + "\"", 14.5, "muted") + 34

    # ---- the one change
    y = P.band(c, X0, y, "The one change: `Evidence`, beside its predecessor's (ADR-0034 finding 6)")
    y += P.row_cards(c, X0, y, WW, 30, [
        (f"`Confinement.tla`, line {ep[0]} (I7)", P.code_lines(ep[1]), "grey", {"bullets": False}),
        (f"`Confinement_A1.tla`, line {ea[0]}", P.code_lines(ea[1]), "teal", {"bullets": False}),
        ("What it corrects", [
            "Under `M_HOST` at rung 0 the predecessor reached `Contested`, \"which §2 says rung 0 cannot produce\": "
            "rung 0 has no evidence at all (ADR-0034 finding 6).",
            f"The finding's correction, {F6_FIX}, is this definition (compared at build time).",
            f"Every other definition of the two modules is the same, comments aside: {len(defs)} definitions compared."],
         "amber", {}),
    ], size=13.5) + 24
    srows = []
    for r in sorted(shared, key=lambda r: (rung(r), r["name"])):
        q = prow[check(r)]
        same = q["verdict"] == r["verdict"] and (q["states"] == r["states"] or r["verdict"] == X)
        srows.append({"cells": [f"`{r['name']}`" + (f" (I7: `{q['name']}`)" if q["name"] != r["name"] else ""),
                                str(rung(r)), f"`{r['mut']}`", f"`{r['prop']}`", P.verdict(q),
                                P.verdict(r), "the same" if same else
                                ("[[red|the verdict moves]]: finding 6" if q["verdict"] != r["verdict"] else
                                 "the same verdict; the model's states differ (rung 0 changed)")],
                      "accent": None if same else "amber"})
    y += c.table(X0, y, [("Row", 160, {}), ("Rung", 80), ("Under", 200), ("Property", 360),
                         (f"`{PRED[5:]}` (I7)", 620), ("This module", 620), ("Against each other", WW - 2040)],
                 [r_ if r_["accent"] else r_["cells"] for r_ in srows], size=13, accent="teal") + 14
    y += c.para(X0, y, WW, f"The {len(shared)} checks the two runs share (rung, mutation, property), compared at build "
                f"time. A row name is not a check: {', '.join(f'`{n_}`' for n_ in renamed)} names another check in "
                f"each file. "
                f"At rungs 1 to 3 every verdict is the same, and every check that holds explores the same number of states, as "
                f"the header says (\"Nothing checked at rungs 1 to 3 depends on the change\"). A counterexample's count "
                f"is where TLC stopped, and the runs used different builds: " +
                "; ".join(f"`{f_[5:]}`, {v}" for f_, v in tlcs) + ". At rung 0 the model changed: `hx0`'s verdict "
                "moves, and `h0` explores more states.", 13.5, "muted") + 50

    # ---- the picture, the machine
    y = band_picture(c, X0, y, WW, mod, rung_lines, "at rungs 0 and 1 the profile the launcher was asked for, else "
                     "the launch measurement", ("What it is", [
                         "The successor: `Confinement.tla` is cited by digest and not edited, \"as `Lease_A1.tla` is "
                         "to `Lease.tla`\" (the header).",
                         "Rung 0 is a row of this module, not an addendum to it (the header).",
                         "The reference's trace harness reads its state through `ConfinementRefinement.tla` (I9)."],
                         "grey", {}))
    y = band_machine(c, X0, y, WW, mod, NAME)

    # ---- the properties, mutations, matrix, witnesses
    y = P.band(c, X0, y, "The four properties, the section of ADR-0034 each states, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, f"ADR-0034 {s}", w) for p, s, w in hp],
                     key=lambda r: f"{r['mut']} at rung {rung(r)}") + 50
    y = band_mutations(c, X0, y, WW, ev, mod, head_muts)
    y = band_matrix(c, X0, y, WW, rows, res, len(EXPECT_ROWS), {
        "hx0": "Finding 6, corrected: under `M_HOST` at rung 0 no `Contested` verdict is reached, because rung 0 now "
               "reads the profile asked for. In `Confinement.tla` the same row is a counterexample (I7)."},
        f"Every mutation by every property, at every rung it is run, read from `{res['file'][5:]}`")
    y = band_witnesses(c, X0, y, WW, mod, rows, WITNESSES, "Witnesses, by rung", readings={
        "NeverContainedEffect": "A `Contained` principal acts, at rungs 1 and 3. At rung 0 it **holds**: no "
                                "effect is counted `Contained` there (D-0034-4).",
        "NeverMediatedEffect": "A `Mediated` principal acts.",
        "NeverContested": "A rogue launch is detected at rung 3; at rungs 0 and 1 it **holds**.",
        "NeverRenewContested": "**Holds**: a renewal never turns `Contested`."})

    # ---- the proofs
    y = band_proofs(c, X0, y, WW, ev, ("The predecessor", [
        "`Confinement.tla` (I7) fails to certify in the same way: three obligations, last backend tried Isabelle. "
        "The two proof modules have the same statements."], "grey", {}))

    adr46 = re.sub(r"\s+", " ", M.text("decisions/ADR-0046.md"))
    cited = "`Confinement_A1_proof.tla` (`f4ffce6861f24e77`)"
    _need(cited in adr46 and M.sha16(ev["files"]["cert"]) == "f4ffce6861f24e77"
          and M.sha16(ev["files"]["proof"]) != "f4ffce6861f24e77", "ADR-0046's citation of the proof module")
    y += P.row_cards(c, X0, y, WW, 30, [
        ("[[red|A finding: ADR-0046 gives the certified results file's digest as the proof module's]]", [
            f"ADR-0046 (Open obligations, the two that are not certified) cites {cited}.",
            f"That digest is `{ev['files']['cert'][5:]}`'s; `Confinement_A1_proof.tla` is "
            f"`{M.sha16(ev['files']['proof'])}`, as the proof and certified results files both cite it (compared at "
            f"build time). The diagram's reading, for the custodian; the record is not changed by drawing it."],
         "red", {}),
    ], size=13.5) + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the two modules re-encoded under one flag")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.Confinement",
               extra_card="\"`Confinement.lean` covers `Confinement.tla` and `Confinement_A1.tla` under one flag\" "
                          "(the results file).") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, PROPS[1:], ["invariant(Confinement_A1)"]) + 50

    # ---- where else, digests
    y = P.band(c, X0, y, "Where else `Confinement_A1.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev)
    return c
