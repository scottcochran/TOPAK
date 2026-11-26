"""I10 — `RunConfinement.tla`, channel fidelity for Run: ADR-0034 A2's P4 for Run and its ratification condition
(ii), drawn whole from the module's own text and every results file about it.

Built on modpage.py's bands (family I). The deployment's declaration `Filtered` (D-0034-5) is a constant of the runs,
so results are drawn by mutation, property and declaration; every row's verdict is held as a literal and compared both
ways, and A2's condition and its Met line are compared with the rows."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I10", "run-confinement"
NAME = "RunConfinement"
MODULE_FILES = ("spec/RunConfinement.tla", "spec/RunConfinement_proof.tla")
W = 3400

REC = "decisions/ADR-0034.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "EffectsOnDeclaredChannels", "ContainedEffectsUseHeldTools"]
WITNESSES = ["NeverContainedEffect", "NeverMediatedEffect", "NeverRefused", "NeverUndeclaredTarget"]
EXPECT_ROWS = {"safe": H, "safef": H, "ch": X, "chh": H, "nat": X, "nath": X, "fil": X, "fil0": H, "wc": X,
               "wm": X, "wr": X, "wrf": X, "wu": X}
COND_SAYS = ("both invariants hold as specified and under D-0034-5's filter; `M_CHANNEL` and `M_NATIVE` break them as "
             "stated; a third mutation, `M_FILTER`, shows the filter is load-bearing only where D-0034-5 is declared; "
             "five witnesses are violated")
MET_SAYS = ("`Safe` holds with and without the filter; `M_CHANNEL` and `M_NATIVE` break `EffectsOnDeclaredChannels`, "
            "`M_NATIVE` breaks `ContainedEffectsUseHeldTools`, and `M_FILTER` breaks the first where D-0034-5 is "
            "declared")
ADR46_CITES = "`RunConfinement_proof.tla` (`823ae3479ef38845`)"
ELSEWHERE = ["C4", "G3", "H3"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def filt(r):
    return r["params"]["Filtered"] == "TRUE"


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    rows = res["rows"]
    got = {r["name"]: r["verdict"] for r in rows}
    _need(got == EXPECT_ROWS, f"the file's rows are not the diagram's: {sorted(set(got.items()) ^ set(EXPECT_ROWS.items()))}")
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts][1:] == M.mutations(res), "the header's mutations are not the file's")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == PROPS[1:], "the header's properties")
    rec = re.sub(r"\s+", " ", M.text(REC))
    _need(COND_SAYS in rec and MET_SAYS in rec, "ADR-0034 A2's condition or its Met line no longer says what the "
                                                "diagram quotes")
    _need("*paid by A2, ratified 2026.10.04 (Batch 30)*" in rec, "ADR-0034 no longer records A2 as ratified in Batch 30")
    _need(len([r for r in rows if r["prop"].startswith("Never") and r["verdict"] == X]) == 5, "five witnesses violated")
    _need(M.header_comment(mod)[0].strip().startswith("Channel fidelity for Run: ADR-0034 A2 (pending)"),
          "the header's first line has changed")
    adr46 = re.sub(r"\s+", " ", M.text("decisions/ADR-0046.md"))
    _need(ADR46_CITES in adr46 and M.sha16(ev["files"]["cert"]) == "823ae3479ef38845" and
          M.sha16(prf) != "823ae3479ef38845", "ADR-0046's citation of the proof module")
    _need(f"`spec/RunConfinement_proof.tla`, `{M.sha16(prf)}`" in rec, "ADR-0034 B30's digest of the proof module")
    brow = P.md_rows(P.PREMISES, P.PREMISE_HEAD, ["EffectsOnDeclaredChannels"])[0]
    binding = brow[0]
    _need("(**pending** ADR-0034 A2)" in binding and brow[-1].startswith("**pending**: A2 is not ratified"),
          "the binding's row no longer marks A2 pending")
    hc = M.header_comment(mod)
    i0 = next(i for i, ln in enumerate(hc) if ln.strip().startswith("What holds a tool to its channel"))
    kinds = []
    for ln in hc[i0 + 1:]:
        t = ln.strip()
        if not t:
            break
        m_ = re.match(r"^(wasm|filtered|native)\s{2,}(.*)$", t)
        if m_:
            kinds.append([m_.group(1), m_.group(2)])
        else:
            kinds[-1][1] += " " + t
    _need([k for k, _ in kinds] == ["wasm", "filtered", "native"], "the header's table of what holds a tool")
    _, held = M.definition(mod, "Held")
    _need('Kind[t] = "wasm" \\/ (Kind[t] = "filtered" /\\ Filtered)' in held, "Held is not the header's table")

    c = Canvas(ID,
               "`RunConfinement.tla`: every effect admitted under a `Contained` Run lease reached its tool's declared "
               "target, through a tool something holds to its channel. Two invariants, each with the mutations that "
               "break it: checked by TLC with and without D-0034-5's filter, proved by TLAPS",
               "The module ADR-0034 A2's ratification condition (ii) asks for, drawn from its own text and from every "
               "results file about it, all read at build time: the tools and what holds each to its channel, the "
               "mechanism's check and the tool host, the two properties, every mutation by every property under "
               "each declaration, the witnesses, A2's condition and its Met line compared with the rows, every theorem "
               "and lemma, and the certified run. **What is checked or proved here is of the module and not of the "
               "reference: only P4 is modelled, and what a tool says on its channel is not** (its header). A2 was "
               "ratified on 2026.10.04 in Batch 30; the module's header, written before, calls it pending.",
               W,
               f"spec/RunConfinement.tla (its header, every definition); spec/RunConfinement_proof.tla (every THEOREM "
               f"and LEMMA); {res['file']}; {ev['files']['proof_results']}; {ev['files']['cert']}; {P.PREMISES} (the "
               f"two rows and invariant(RunConfinement)); ADR-0034 A2 (its condition, Met at ratification, B30), "
               f"D-0034-5, D-0034-6; ADR-0040 §3; ADR-0046 (Open obligations); ADR-0045 T-0045-24. Every file read at "
               f"the pin its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0034 A2", "accepted", "B30")], tail=[
        ("Lean", ("Not re-encoded in Lean", "grey", "2 3"), "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    fl, rl, al = (M.definition(mod, n_)[0] for n_ in ("Fidelity", "Reach", "Actuate"))
    y = P.band(c, X0, y, "The mechanism, as the module states it: under a lease whose Run profile says P4 passes, an "
                         "`Actuate` names only a held tool, and the tool opens only the target the tool host lets it")
    y = P.flow_picture(
        c, X0, y, WW,
        ("A Run principal", ["a lease on a Run profile whose P4 says `pass` or `fail`"], "brown"),
        (f"The check, and the tool host (`Actuate`, line {al})", [
            f"**①** `Fidelity` (line {fl}), the mechanism's `State::channel_fidelity`: a P4-pass lease names only a "
            f"held tool. `M_NATIVE` [[red|drops the check]].",
            f"**②** `Reach` (line {rl}), the tool host: a Wasm tool opens only its declared target, `M_CHANNEL` "
            f"[[red|any]]; a filtered tool only its own while the filter binds, `M_FILTER` [[red|any]]; a native tool "
            f"any target."], "teal"),
        ("Refused at apply", ["a P4-pass lease names a tool nothing holds"], "red"),
        ("The tools, and what holds each to its channel", "teal", [
            ("Tool `w` · Wasm · target `a`", ["held by the runtime: \"a check, by construction\""], "green"),
            ("Tool `f` · filtered · target `b`", ["held by an egress filter, only where the deployment declares "
                                                   "`Filtered` (D-0034-5): \"a trust\""], "teal"),
            ("Tool `n` · native · target `c`", ["held by nothing (D-0034-6; T-0045-24 excluded)"], "red")]),
        ("The record of effects: `effects`", ["one per effect: whether its lease was `Contained`, the tool and the "
                                              "target it reached"], "grey"),
        [("ADR-0034 A2's P4, read on `effects`", ["`EffectsOnDeclaredChannels`: a `Contained` effect reached its "
                                                  "tool's declared target"], "record"),
         ("ADR-0034 A2's P4, read on `effects`", ["`ContainedEffectsUseHeldTools`: a `Contained` effect used a held "
                                                  "tool"], "record")],
        {"ask": "actuates", "write": "③ a target", "act": "④ the effect"},
        "**Key.** ① is the mechanism's check, ② the tool host; ③ the target the tool opens; ④ the effect, recorded "
        "with what its lease was. Red marks where each mutation acts. The picture is the diagram's own drawing of the "
        "definitions below.") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("What holds a tool to its channel, by kind (the module's header)", [f"**`{k}`**: {v}" for k, v in kinds],
         "brown", {}),
        ("What the module does not model", [
            "\"Only P4 is modelled. A lease here is attested at its declared rung, its Persona in house and the "
            "criterion in force, so `Contained` reduces to the profile's P4; those conjuncts are `Confinement_A1.tla`'s "
            "and ADR-0034 §4's\" (the header).",
            "\"What a tool says on its channel is not modelled: fidelity is about which channel, not what is said on "
            "it\" (the header)."], "red", {}),
    ], size=13.5) + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: three tools, three targets, a grant, an `Actuate` and the end of a round "
                         "(`RunConfinement.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Constants: tools, kinds and targets", ["Principals", "Tools", "Kind", "Targets", "Declared"],
          [f"`CONSTANTS Mut, Filtered` (line {M.line_of(mod, r'^CONSTANTS Mut, Filtered$')}): the mutation, and "
           f"whether the deployment declares the egress filter (D-0034-5)"], "grey"),
         ("What holds, and what the host lets through", ["Held", "Reach"], [], "teal"),
         ("The check, and membership", ["Fidelity", "Contained"], [], "teal")],
        [("State", ["NoLease", "Init"], [f"`VARIABLES lease, effects, refused` (line "
                                         f"{M.line_of(mod, r'^VARIABLES lease, effects, refused$')})"], "grey"),
         (None, ["Grant"], [], "teal"),
         (None, ["Actuate"], [], "teal"),
         ("The end of a round, and `Next`", ["EndRound", "Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 50

    # ---- the properties, mutations
    y = P.band(c, X0, y, "The two properties, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, "ADR-0034 A2, P4 for Run (the header's first line)", w) for p, _, w in hp],
                     key=lambda r: f"{r['mut']} (Filtered = {r['params']['Filtered']})") + 50
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    mrows = []
    lines = M.text(mod).split("\n")
    for mt, words in head_muts[1:]:
        at = M.code_lines_with(mod, f'"{mt}"')
        lem = [s for s in ev["statements"] if s["kind"] == "LEMMA" and f'Mut = "{mt}"' in s["prove"]]
        mrows.append([f"`{mt}`", words, "; ".join(f"`{M.enclosing(mod, ln)}`, line {ln}: {P.code(lines[ln - 1])}"
                                                 for ln in at),
                      "; ".join(f"`{s['name']}` (line {s['line']}): `{s['prove']}`" for s in lem) or "—"])
    y += c.table(X0, y, [("Mutation", 200, {}), ("What it does (the module's header)", 900), ("Where it acts", 1100),
                         ("Why it must fail (the proof module's lemma)", WW - 2200)], mrows, size=13.5, accent="red",
                 anchor="mutations") + 50

    # ---- the matrix, by declaration
    y = P.band(c, X0, y, f"Every mutation by every property, with and without the filter declared, read from "
                         f"`{res['file'][5:]}`")
    muts = ["none"] + M.mutations(res)
    mrows = []
    for mt in muts:
        r_ = [f"`{mt}`"]
        for p in PROPS:
            hits = sorted([r for r in rows if r["mut"] == mt and r["prop"] == p], key=filt)
            r_.append("\n".join(f"`Filtered = {r['params']['Filtered']}`: {P.verdict(r)}" for r in hits)
                      or "[[grey|not run]]")
        mrows.append({"cells": r_, "accent": "grey" if mt == "none" else "red"})
    pw = (WW - 210) / len(PROPS)
    y += c.table(X0, y, [("Mutation", 210, {})] + [(f"`{p}`", pw) for p in PROPS], mrows, size=13,
                 anchor="matrix") + 14
    y += c.para(X0, y, WW, f"Every row's verdict is held by the diagram ({len(EXPECT_ROWS)} rows) and compared with "
                "the file both ways. `M_FILTER` breaks `EffectsOnDeclaredChannels` where the filter is declared and "
                "changes nothing where it is not: \"the filter is load-bearing only where D-0034-5 is declared\".",
                13.5, "muted") + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each must be violated, so neither property is true by the model's construction")
    readings = {
        "NeverContainedEffect": "A `Contained` Run principal acts: the properties are not vacuous.",
        "NeverMediatedEffect": "A `Mediated` Run principal acts too: `Contained` is not everyone.",
        "NeverRefused": "The check fires: a native tool under a P4-pass lease is refused, with and without the filter.",
        "NeverUndeclaredTarget": "An undeclared target is reached at all, by a `Mediated` principal's native tool: "
                                 "\"the model lets a tool misbehave\".",
    }
    ws = [r for r in rows if r["mut"] == "none" and r["prop"].startswith("Never")]
    _need(sorted({r["prop"] for r in ws}) == sorted(WITNESSES), "the witnesses")
    wrows = []
    for w in WITNESSES:
        ln, src = M.definition(mod, w)
        cells = [f"`{w}`", " ".join(P.code_lines(src))]
        for f_ in ("FALSE", "TRUE"):
            h_ = [r for r in ws if r["prop"] == w and r["params"]["Filtered"] == f_]
            cells.append(P.verdict(h_[0]) if h_ else "[[grey|not run]]")
        cells.append(readings[w])
        wrows.append(cells)
    y += c.table(X0, y, [("Witness", 280, {}), ("Its definition", 760), ("`Filtered = FALSE`", 500),
                         ("`Filtered = TRUE`", 500), ("What it shows (the diagram's reading)", WW - 2040)], wrows,
                 size=13, anchor="witnesses") + 50

    # ---- the record
    y = P.band(c, X0, y, "ADR-0034 A2's ratification condition (ii), and what was met at ratification")
    y += P.row_cards(c, X0, y, WW, 30, [
        ("The condition, as the record states what the run showed", [f"\"{COND_SAYS}\" (ADR-0034 A2)"], "blue", {}),
        ("Met at ratification (Batch 30)", [f"\"{MET_SAYS}\" (ADR-0034 A2, ⟨B30⟩)"], "blue", {}),
        ("Against the file", [
            "Each clause is a set of rows above, compared at build time: `Safe` holds with the filter (`safef`) and "
            "without (`safe`); `ch` and `nat` break `EffectsOnDeclaredChannels`, `nath` breaks "
            "`ContainedEffectsUseHeldTools`; `fil` breaks it with the filter declared and `fil0` holds without; five "
            "witnesses are violated."], "teal", {}),
    ], size=13.5) + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, {
        "KindValues": "Each tool's kind.", "ToolCases": "There are three tools.",
        "HeldReachesDeclared": "A held tool reaches only its declared target, unless a mutation unbinds it.",
        "ContainedHeld": "Unless `M_NATIVE`, a `Contained` lease's admitted tool is held.",
        "ActuateEffect": "What an `Actuate` records, or that it changes nothing.",
        "NextDeclared": "`EffectsOnDeclaredChannels` is kept unless `M_CHANNEL`, `M_NATIVE`, or `M_FILTER` with the "
                        "filter declared.",
        "NextHeld": "`ContainedEffectsUseHeldTools` is kept unless `M_NATIVE`.",
        "InitBoth": "Both, at the start.",
        "EffectsOnDeclaredChannelsAlways": "For every behaviour, under those exclusions.",
        "ContainedEffectsUseHeldToolsAlways": "For every behaviour, unless `M_NATIVE`.",
        "SafeAlways": "Both, unmutated.",
        "MutChannelReachesAll": "Why `M_CHANNEL` must fail: the Wasm tool reaches every target.",
        "MutNativeAdmitsAll": "Why `M_NATIVE` must fail: every tool passes the check.",
        "MutFilterReachesAll": "Why `M_FILTER` must fail: the filtered tool reaches every target.",
        "NativeIsNeverHeld": "The native tool is held by nothing.",
    }, assumptions_note="`Filtered` is a Boolean") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("[[red|A finding: ADR-0046 gives the certified results file's digest as the proof module's]]", [
            f"ADR-0046 (Open obligations, outside the thirteen modules it cites) cites {ADR46_CITES}.",
            f"That digest is `{ev['files']['cert'][5:]}`'s; `RunConfinement_proof.tla` is `{M.sha16(prf)}`, as "
            f"ADR-0034 B30 and both results files cite it (compared at build time). The diagram's reading, for the "
            f"custodian."], "red", {}),
        ("[[red|A finding: the binding still marks A2 pending]]", [
            f"`theorem-premise-binding.md` heads the two properties' row \"{binding}\", and its last cell begins "
            f"\"**pending**: A2 is not ratified\". ADR-0034 records A2 \"ratified 2026.10.04 (Batch 30)\". The "
            f"diagram's reading, for the custodian."], "red", {}),
    ], size=13.5) + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, PROPS[1:], ["invariant(RunConfinement)"],
                   note="`RunConfinement` is not re-encoded in Lean, so its derived premise has the TLAPS route only.") + 50

    # ---- where else, digests
    y = P.band(c, X0, y, "Where else `RunConfinement.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, extra=[(ev["files"]["cert"], M.sha16(ev["files"]["cert"]), "ADR-0034 B30; ADR-0046 "
                                        "(as the proof module's)")])
    return c
