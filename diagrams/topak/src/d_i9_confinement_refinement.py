"""I9 — `ConfinementRefinement.tla`, the reference's confinement path read against `Confinement_A1.tla` (ADR-0045
T-0045-28, stage one): a mapping from `Mechanism.tla`'s state onto the abstract module's, and four invariants checked
on every recorded state of the reference's test suites by the trace validation. No TLC run of its own, no proof.

Built on modpage.py's bands (family I). The trace results are read through modules.trace_results; the generator that
writes each trace's module and configuration is read to show that every MATCH line includes these invariants."""
import re
from collections import OrderedDict

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I9", "confinement-refinement"
NAME = "ConfinementRefinement"
MODULE_FILES = ("spec/ConfinementRefinement.tla",)
W = 3400

ABSTRACT = "spec/Confinement_A1.tla"
GEN = "spec/trace2tla.py"
RUNNER = "spec/mechanism-trace-run.sh"
G10 = "checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md"
INVS = OrderedDict([("RNoSilentDowngrade", "NoSilentDowngrade"), ("RContestedStopped", "ContestedStopped"),
                    ("RFreshAppraisal", "FreshAppraisal"), ("RContainedAttested", "Contained")])
G10_SAYS = "**82 traces, 1,007 steps, every step matching**, and every state keeping `ConfinementRefinement.tla`'s invariants"
ELSEWHERE = ["D1", "G1", "G3", "H3", "H9"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def build():
    ev = M.evidence(NAME)
    mod = ev["files"]["module"]
    tr = M.trace_results(M.TRACE_RESULTS)
    _need(all(r["verdict"] == "MATCH" for r in tr["rows"]), "a trace does not match")
    mech = "spec/Mechanism.tla"
    _need(tr["module"] == {"Mechanism.tla": M.sha16(mech)}, "the trace results cite Mechanism.tla at another digest")
    _need(re.search(r"^EXTENDS Mechanism$", M.text(mod), re.M), "the module no longer extends Mechanism")
    gen = M.text(GEN)
    _need('"EXTENDS ConfinementRefinement"' in gen and "INVARIANT TraceMatches\\nINVARIANT ConfinementRefined" in gen,
          f"{GEN} no longer writes each trace against ConfinementRefined")
    run = M.text(RUNNER)
    _need('r="REFINEMENT' in run and 'r="MATCH"' in run, f"{RUNNER} no longer tells a refinement failure from a match")
    _need(M.unchanged_since(M.TRACE_RESULTS, mod), "the module changed after the trace results were committed")
    g10 = M.text(G10)
    rsha = M.sha16(M.TRACE_RESULTS)
    _need(f"`{M.TRACE_RESULTS}` (`{rsha}`)" in g10 and G10_SAYS in re.sub(r"[ \t]+", " ", g10),
          "G10's row on the trace validation no longer says what the diagram quotes")
    gl = g10.split("\n")
    row_at = next(i for i, ln in enumerate(gl) if f"`{M.TRACE_RESULTS}` (`{rsha}`)" in ln)
    head = next(ln for ln in reversed(gl[:row_at]) if re.match(r"^#{1,6} ", ln))
    g10sec = "§" + re.match(r"^#{1,6} (\d+(?:\.\d+)*)\.", head).group(1)
    # the mapping the header states, two columns
    hc = M.header_comment(mod)
    i0 = next(i for i, ln in enumerate(hc) if ln.strip().startswith("Confinement_A1") and "here" in ln)
    mapping = []
    for ln in hc[i0 + 1:]:
        if not ln.strip():
            break
        cols = re.split(r"\s{2,}", ln.strip())
        _need(len(cols) == 2, f"a mapping line does not have two columns: {ln!r}")
        mapping.append(cols)
    head_words = " ".join(ln.strip() for ln in hc[i0 + 1 + len(mapping):] if ln.strip())
    # each invariant beside its abstract counterpart
    inv_rows = []
    lines = M.text(mod).split("\n")
    for r_, a_ in INVS.items():
        ln, src = M.definition(mod, r_)
        note = lines[ln - 2].strip()
        _need(note.startswith("\\*"), f"{r_} has no comment line")
        aln, asrc = M.definition(ABSTRACT, a_)
        inv_rows.append([f"`{r_}`", note[2:].strip(), " ".join(P.code_lines(src)),
                         f"`{a_}` (`Confinement_A1.tla`, line {aln}): " + " ".join(P.code_lines(asrc))])
    _, cr = M.definition(mod, "ConfinementRefined")
    _need(sorted(re.findall(r"\bR[A-Z]\w+", cr.split("==", 1)[1])) == sorted(INVS),
          "ConfinementRefined is not the four invariants")
    groups = OrderedDict()
    for r in tr["rows"]:
        g = r["name"].split("_")[0]
        groups.setdefault(g, [0, 0])
        groups[g][0] += 1
        groups[g][1] += r["steps"]

    c = Canvas(ID,
               "`ConfinementRefinement.tla`: the reference's own confinement states, mapped onto `Confinement_A1.tla` "
               "and held to four of its invariants at every recorded step. Checked by trace validation: 82 traces, "
               "1,007 steps, every one matching",
               "The first stage of ADR-0045's refinement chain (T-0045-28) for confinement, drawn from the module's "
               "own text and the trace validation that runs it, all read at build time: the mapping from "
               "`Mechanism.tla`'s state onto the abstract module's, the four invariants beside the abstract ones they "
               "stand for, what is not checkable here, and the run, trace by trace. **A trace validation is a test of "
               "recorded behaviours, not a proof: it shows that the reference's recorded states keep these "
               "invariants, not that every state it could reach does.** The module has no TLC run and no proof of "
               "its own.",
               W,
               f"spec/ConfinementRefinement.tla (its header, every definition); spec/Confinement_A1.tla (the four "
               f"abstract definitions); {M.TRACE_RESULTS}; {GEN} (the module and configuration it writes per trace); "
               f"{RUNNER}; spec/Mechanism.tla (its digest); Genesis Checkpoint G10 {g10sec} (the trace validation row); "
               f"ADR-0045 T-0045-28; ADR-0034 §3, §4; ADR-0031 A1. Every file read at the pin its links open, and "
               f"checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0034", "accepted", "C2, C4")], tail=[
        ("The trace validation", (f"Checked · {tr['traces']} traces, {P.n(tr['steps'])} steps, every one MATCH · a test",
                                  "teal", "6 4"), "")]))
    y += c.para(X0, y, WW, "**Checked** here means trace validation: each of the reference's recorded behaviours is "
                "replayed through `Mechanism.tla`, and every state it reaches is read against this module's "
                "invariants. Nothing here is proved.", 14.5, "muted") + 34

    # ---- the picture
    y = P.band(c, X0, y, "The mechanism of the check: every recorded step is replayed, matched and read against the "
                         "abstract invariants")
    y = P.flow_picture(
        c, X0, y, WW,
        ("The reference's recorded behaviours", [f"the suites: {tr['suites'][:150]}…"], "brown"),
        (f"One module per trace (`{GEN[5:]}`)", [
            "**①** each recorded step becomes a step of `TraceSpec`, which `EXTENDS ConfinementRefinement`, itself "
            "`EXTENDS Mechanism`",
            "**②** `INVARIANT TraceMatches`: the model's state and result equal the recorded ones at every step",
            "**③** `INVARIANT ConfinementRefined`: every state keeps the four invariants below"], "teal"),
        ("A mismatch, or a refinement violated", ["the run prints the step (`MISMATCH at step n`, `REFINEMENT … "
                                                  "violated at step n`); none did"], "red"),
        ("`st`: the reference's projected state, step by step", "teal", [
            ("The live leases: `LiveFences(st)`", ["the fences `liveBySeat` names"], "teal"),
            ("Each lease's rung, appraisal and profile", ["`st.leases[f]`: `rung`, `att`, `conf`, `seat`, "
                                                          "`principal`, `epoch`"], "teal"),
            ("`contested`, `revoked`, `contained`", ["the principals Contested, the revocation targets, the fences "
                                                     "counted Contained"], "teal")]),
        None,
        [("ADR-0034 §3, read on `st`", ["`RNoSilentDowngrade`, `RContestedStopped`, `RFreshAppraisal`"], "state"),
         ("ADR-0034 §4, read on `st`", ["`RContainedAttested`: `Contained`'s premises"], "state")],
        {"ask": "recorded", "write": "④ each state"},
        "**Key.** ① to ③ are what `trace2tla.py` writes for each trace (read at build time); ④ each state the replay "
        "reaches. The picture is the diagram's own drawing of the generator and the definitions below.") + 50

    # ---- the mapping
    y = P.band(c, X0, y, "The mapping: `Confinement_A1.tla`'s variables, as this module reads them in the reference's "
                         "state (the module's header)")
    half = (WW - 30) / 2
    t1 = c.table(X0, y, [("`Confinement_A1`", 520, {}), ("here (per live lease `f`)", half - 520)],
                 [[f"`{a}`", f"`{b}`"] for a, b in mapping], size=13.5, accent="teal")
    h2 = c.card(0, 0, half, "What the header says it does not check", [head_words], draw=False, size=13.5)
    c.card(X0 + half + 30, y, half, "What the header says it does not check", [head_words], accent="red", size=13.5,
           h=max(h2, t1))
    y += max(t1, h2) + 50

    # ---- the invariants
    y = P.band(c, X0, y, "The four invariants, each beside the abstract definition it stands for")
    y += c.table(X0, y, [("Invariant", 280, {}), ("Its comment (the section it states)", 620), ("Its definition", 1100),
                         ("The abstract counterpart", WW - 2000)], inv_rows, size=13, accent="teal",
                 anchor="properties") + 14
    y += c.para(X0, y, WW, "`ConfinementRefined` is their conjunction (checked at build time). `RContainedAttested` "
                "is not `ContainedMeansConfined`: that is \"about the image the host actually ran, which the mechanism "
                "never sees\", so its premises are checked in its place (the header). The machine is `Mechanism.tla`'s, "
                "which this module extends.", 13.5, "muted") + 24
    y = P.machine(c, X0, y, WW, mod, [[(None, ["LiveFences"], [], "teal"),
                                       ("`ConfinementRefined`", ["ConfinementRefined"], [], "blue")]]) + 50

    # ---- the run
    y = P.band(c, X0, y, f"The trace validation, read from `{M.TRACE_RESULTS[5:]}`")
    y += P.row_cards(c, X0, y, WW, 30, [
        ("What was traced", [f"Reference: {tr['reference']}", f"Suites: {tr['suites']}",
                             f"Model: `Mechanism.tla` (`{M.sha16(mech)}`, the digest the file cites)"], "grey", {}),
        ("What a line means", [f"\"{tr['words']}\"", "With the runner (`mechanism-trace-run.sh`), a line also fails "
                               "as `REFINEMENT … violated` when a state breaks `ConfinementRefined`: every MATCH below "
                               "includes it."], "teal", {}),
        ("The suites' own runs", tr["tests"], "grey", {"bullets": False}),
    ], size=13.5) + 24
    y += c.table(X0, y, [("Traces from", 300, {}), ("Traces", 160), ("Steps", 160), ("Every one", WW - 620)],
                 [[f"`{g}_…`", str(n_), P.n(s_), "**MATCH**"] for g, (n_, s_) in groups.items()] +
                 [{"cells": ["**All**", f"**{tr['traces']}**", f"**{P.n(tr['steps'])}**", "**MATCH**"],
                   "accent": "teal"}], size=13.5, accent="teal") + 24
    k = 3
    per = -(-len(tr["rows"]) // k)
    cw = (WW - (k - 1) * 30) / k
    hs = []
    for i in range(k):
        chunk = tr["rows"][i * per:(i + 1) * per]
        hs.append(c.table(X0 + i * (cw + 30), y, [("Trace", cw - 220, {}), ("Steps", 100), ("Verdict", 120)],
                          [[f"`{r['name']}`", str(r["steps"]), f"**{r['verdict']}**"] for r in chunk], size=12))
    y += max(hs) + 14
    y += c.para(X0, y, WW, f"Every trace, as the file lists it. G10 cites the file (`{rsha}`): \"82 traces, 1,007 "
                "steps, every step matching, and every state keeping `ConfinementRefinement.tla`'s invariants\". The "
                "file cites `Mechanism.tla`'s digest and not this module's: the build checks that this module has not "
                "changed since the file was committed (git, at the pin), which shows order only.", 13.5, "muted") + 50

    # ---- where else, digests
    y = P.band(c, X0, y, "Where else `ConfinementRefinement.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, extra=[(mech, M.sha16(mech), f"`{M.TRACE_RESULTS}`"),
                                       (M.TRACE_RESULTS, rsha, f"Genesis Checkpoint G10 {g10sec}")],
              note="No results file cites this module's digest; the trace results cite `Mechanism.tla`'s.")
    return c
