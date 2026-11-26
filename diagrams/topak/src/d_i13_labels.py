"""I13 — `Labels.tla`, labels on Run's ingress: ADR-0047's ratification condition (§11), drawn whole from the module's
own text and every results file about it. Ten properties, stated over what the labels are about as well as over the
labels; eight mutations, each breaking what the header says it must; checked by TLC, proved and certified by TLAPS.

Built on modpage.py's bands (family I). The results are drawn property by mutation; every row's verdict, the header's
"must break" lists and ADR-0047 §11's figures and digests are compared with the files at build time."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I13", "labels"
NAME = "Labels"
MODULE_FILES = ("spec/Labels.tla", "spec/Labels_proof.tla")
W = 3400

REC = "decisions/ADR-0047.md"
EARLIER = "spec/Labels-results-2026.10.03.txt"
H, X = "HOLDS", "COUNTEREXAMPLE"
EXPECT_ROWS = {
    "safe": H, "grow": H, "lit1": X, "lit2": X, "join1": X, "join2": X, "join3": X, "load1": X, "load2": X,
    "load3": X, "load4": X, "reset1": X, "reset2": X, "reset3": X, "del1": X, "del2": X, "f1a": X, "f1b": H,
    "f2a": X, "f2b": H, "f3a": X, "f3b": H, "lit3": H, "lit4": H, "w1": X, "w2": X, "w3": X, "w4": X, "w5": X,
    "w6": X, "w7": X, "w8": X, "w9": X, "load5": X, "reset4": X, "del3": X, "del4": X}
# what the module's header says each mutation must break
MUST_BREAK = {
    "M_LITERAL": ["LabelsCoverTruth", "NoSteeredDestination"],
    "M_JOIN": ["ResultLabelCoversInputs", "LabelsCoverTruth", "FloorMinimumHolds"],
    "M_LOAD": ["NoUnlabelledDelivery", "OutsideResultIsUntrusted", "ReservedReleasedOnlyIfIssued", "LabelsCoverTruth",
               "FloorMinimumHolds"],
    "M_RESET": ["ClearSetOnlyGrows", "ClearSetCoversGuest", "LabelsCoverTruth", "FloorMinimumHolds"],
    "M_DELIVER": ["SuppressedNeverInGuest", "ClearSetCoversGuest", "LabelsCoverTruth", "FloorMinimumHolds"],
    "M_F1": ["NoReadThenSend"], "M_F2": ["NoSteeredDestination"], "M_F3": ["NoSteeredDestination"]}
ADDED_BY_PROOF = ["load5", "reset4", "del3", "del4"]
NAMED_IN_S11 = ["NoUnlabelledDelivery", "SuppressedNeverInGuest", "ClearSetOnlyGrows", "ResultLabelCoversInputs",
                "FloorMinimumHolds"]
# ADR-0047 §11 R10 and R12, as the record cites the files
CITES = {"spec/Labels.tla": "cc124f5c406aedac", "spec/Labels_proof.tla": "877d9361051a9fbb",
         "spec/Labels-proof-results-2026.10.04.txt": "b35cf57d8c465c2a",
         "spec/Labels-proof-cert-results-2026.10.04.txt": "4f79314ec7972ece",
         "spec/Labels-results-2026.10.04.txt": "2a8c20cf62d53f49", EARLIER: "c9c5bc19e8594713"}
EARLIER_MODULE = "337d7c4bb55e13db"
ELSEWHERE = ["B3", "B8", "C6", "G2", "H3"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    rows = res["rows"]
    got = {r["name"]: r["verdict"] for r in rows}
    _need(got == EXPECT_ROWS, f"the file's rows: {sorted(set(got.items()) ^ set(EXPECT_ROWS.items()))}")
    head_muts = M.header_mutations(mod)
    hm = dict(head_muts)
    _need([m for m, _ in head_muts][1:] == list(MUST_BREAK), "the header's mutations")
    muts = M.mutations(res)
    _need(sorted(muts) == sorted(MUST_BREAK), "the file's mutations")
    for mt, props in MUST_BREAK.items():
        broke = sorted({r["prop"] for r in rows if r["mut"] == mt and r["verdict"] == X})
        _need(broke == sorted(set(props)), f"{mt} breaks {broke}, the header says {props}")
        _need(all(p in hm[mt] for p in props), f"the header's text for {mt} does not name {props}")
    hp = M.header_properties(mod)
    rec = re.sub(r"\s+", " ", M.text(REC))
    for rel, sha in CITES.items():
        _need(f"`{sha}`" in rec and M.sha16(rel) == sha, f"ADR-0047 §11's digest of {rel}")
    _need(f"`spec/Labels.tla` (`{EARLIER_MODULE}`)" in rec, "ADR-0047 R10's digest of the earlier module")
    earlier = M.tlc_log(EARLIER)
    _need(f"Labels.tla (sha256 {EARLIER_MODULE})" in earlier["head"][1] and len(earlier["rows"]) == 33,
          "the 2026.10.03 file is not the run of the earlier module, 33 rows")
    _need(sorted({r["name"] for r in rows} - {r["name"] for r in earlier["rows"]}) == sorted(ADDED_BY_PROOF),
          "the rows the 2026.10.04 file adds")
    _need(all(e_["verdict"] == got[e_["name"]] for e_ in earlier["rows"]), "a row's verdict moved between the files")
    ce = ev["cert"]
    counts = {r_: n_ for r_, n_, _ in ce["routes"]}
    _need(counts.get("trivial, closed by tlapm with no backend") == 421 and counts.get("SMT, proof accepted by ethos")
          == 216 and ce["ls4"] == 14 and "421 obligations closed by the prover's normalization, 216 by SMT" in rec,
          "ADR-0047 R12's counts of the certified run")
    _need(ev["proof"]["obligations"] == 651 and "651 obligations" in rec, "651 obligations")
    for p in NAMED_IN_S11:
        _need(f"`{p}`" in rec, f"§11 no longer names {p}")
    _, fmh = M.definition(mod, "FloorMinimumHolds")
    _need(re.sub(r"\s+", " ", fmh) == "FloorMinimumHolds == NoReadThenSend /\\ NoSteeredDestination",
          "FloorMinimumHolds is not the two")
    binding = P.md_table(P.PREMISES, P.PREMISE_HEAD)
    _need(not [r for r in binding if "Labels" in r[1]], "the binding now has a row for this module")
    hc = M.header_comment(mod)
    i0 = next(i for i, ln in enumerate(hc) if ln.strip().startswith("Four tools"))
    tools = []
    for ln in hc[i0 + 1:]:
        t = ln.strip()
        if not t:
            break
        m_ = re.match(r"^(fetch|send|vault|echo)\s+(.*)$", t)
        if m_:
            tools.append([m_.group(1), m_.group(2)])
        elif tools and not t.startswith("An input"):
            tools[-1][1] += " " + t
        else:
            break
    _need([t for t, _ in tools] == ["fetch", "send", "vault", "echo"], "the header's four tools")
    j0 = next(i for i, ln in enumerate(hc) if ln.strip().startswith("Declared premises, not modelled"))
    premises = []
    for ln in hc[j0:]:
        if not ln.strip():
            break
        premises.append(ln.strip())
    premises = " ".join(premises)

    c = Canvas(ID,
               "`Labels.tla`: every item of Run's ingress is labelled and delivered clear or as a handle, and the floor "
               "refuses an outward call that would carry a secret out after tainted bytes were read, or go where "
               "tainted bytes steer it. Ten properties, eight mutations: checked by TLC, proved and certified by TLAPS",
               "The module ADR-0047 §11 asks for, drawn from its own text and from every results file about it, all "
               "read at build time: the Listener, the guest's clear set and the floor's three forbids; the four tools; "
               "the properties, stated over what the labels are about (tainted and secret bytes, as ghost state the "
               "mechanism never reads) and not only over the labels; every property by every mutation, beside what the "
               "header says each must break; the four rows the proof found; the witnesses; every theorem and lemma; "
               "and the certified run. **What is checked or proved here is of the module, for every `MaxSeq` in the "
               "proofs and at `MaxSeq = 3` in TLC, and not of the reference.** ADR-0047 was ratified on 2026.10.05 "
               "in Batch 34; the module's header, written before, calls it Proposed.",
               W,
               f"spec/Labels.tla (its header, every definition); spec/Labels_proof.tla (every THEOREM and LEMMA); "
               f"{res['file']}; {EARLIER} (the run of the module as it was at R10); {ev['files']['proof_results']}; "
               f"{ev['files']['cert']}; {P.PREMISES} (its theorem table); ADR-0047 §1–§4, §7, §11 (R10, R12), R16; "
               f"ADR-0041 A1; ADR-0045 A1 (T-0045-33); ADR-0049 §3. Every file read at the pin its links open, and "
               f"checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0047", "accepted", "C4; C2 for §3")], tail=[
        ("Lean", ("Not re-encoded in Lean", "grey", "2 3"), "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- the picture
    dl, cl, al = (M.definition(mod, n_)[0] for n_ in ("Deliver", "Consult", "Actuate"))
    y = P.band(c, X0, y, "The mechanism, as the module states it: the Listener labels and delivers, the guest's "
                         "clear set grows, a result takes its inputs' labels, and the floor refuses three outward calls")
    y = P.flow_picture(
        c, X0, y, WW,
        ("Ingress", ["the task, the Run root's object, and every tool's result"], "brown"),
        (f"The Listener (`Deliver`, line {dl}; `Consult`, line {cl})", [
            "**①** every item is labelled by its source: an outward tool's result carries `untrusted` (F4). The load "
            "checks F4 to F6 refuse a bundle that would break them; `M_LOAD` [[red|drops them]].",
            "**②** an item is delivered clear, and its label joins `clearSet`, or as a handle when the bundle's "
            "table suppresses it. `M_RESET` [[red|replaces]] `clearSet`; `M_DELIVER` [[red|sends a suppressed item's "
            "bytes]]."], "teal"),
        None,
        ("The round's items, and the guest", "teal", [
            ("Each item: its id, label and mode", ["clear or handle; and, as ghost state, whether its bytes are "
                                                   "tainted or secret"], "teal"),
            ("The guest, and `clearSet`", ["the items the Thinker has read in the clear, and every label among them"],
             "teal"),
            (f"A result (`Actuate`, line {al})", ["its label holds its handle inputs' labels, and `clearSet` for a "
                                                   "literal. `M_JOIN` and `M_LITERAL` [[red|drop those]]."], "teal")]),
        ("The outward calls: `effects`", ["each admitted outward `Actuate`, with whether it carried a secret out after "
                                          "a tainted read, and whether its destination was tainted"], "grey"),
        [("ADR-0047 §7's floor minimum, read on `effects`", ["`NoReadThenSend` (F1), `NoSteeredDestination` (F2, F3): "
                                                             "the forbids, over the truth. `M_F1`–`M_F3` "
                                                             "[[red|drop one]]."], "record"),
         ("ADR-0047 §1–§4, read on the items", ["`NoUnlabelledDelivery`, `SuppressedNeverInGuest`, "
                                                "`ClearSetCoversGuest`, `ClearSetOnlyGrows`, `ResultLabelCoversInputs`, "
                                                "`LabelsCoverTruth` and F4, F5"], "state")],
        {"ask": "arrives", "write": "③ an item", "act": "④ an outward call"},
        "**Key.** ① and ② are the Listener; ③ an item of the round; ④ an outward `Actuate` the floor admitted. The "
        "properties are stated over the ghost truth as well as the labels, \"so that a label rule that is satisfied by "
        "the mechanism's own bookkeeping and wrong about the world is a counterexample and not a pass\" (the header). "
        "The picture is the diagram's own drawing of the definitions below.") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("Four tools, one of each kind the rules distinguish (the header)", [f"**`{t}`**: {d}" for t, d in tools],
         "brown", {}),
        ("Declared premises, not modelled (the header)", [premises], "red", {}),
    ], size=13.5) + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: the bundle and the grant chosen at the start, the Listener, and the Thinker's "
                         "calls (`Labels.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Names, tools and inputs", ["U", "R", "Names", "Tools", "Outward", "HasDest", "HasBody", "None", "Lit", "Doc",
                                      "Ids"],
          [f"`CONSTANTS Mut, MaxSeq` (line {M.line_of(mod, r'^CONSTANTS Mut, MaxSeq$')})"], "grey"),
         ("What the load checks allow, and the start", ["WellFormed", "Init"], [], "blue"),
         ("An item, a declaration, a release", ["Item", "Exists", "Decl", "Releases"], [], "teal"),
         ("What the Thinker has read, and an input's label", ["ThinkerTainted", "ThinkerSecret", "IsHandle",
                                                              "InLabel", "InTaint", "InSecret"], [], "teal")],
        [("Delivery", ["Clear", "Deliver"], [], "teal"),
         (None, ["Consult"], [], "teal"),
         (None, ["Actuate"], [], "teal"),
         ("`Next` and `Spec`", ["Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The properties, as the header lists them, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, ("ADR-0047 §11, named in the condition" if p in NAMED_IN_S11 else None), w)
                                        for p, _, w in hp], note={
        "FloorMinimumHolds": "No theorem of its own: the conjunction of `NoReadThenSendAlways` and "
                             "`NoSteeredDestinationAlways` (checked at build time).",
        "ClearSetOnlyGrows": "A step property: TLC checks it as a `PROPERTY`, and its theorem is `Spec => "
                             "ClearSetOnlyGrows`."}) + 14
    y += c.para(X0, y, WW, "ADR-0047 §11 asks for \"at least\" five of these by name. The header names no section for "
                "any, so a red cell here is the header's, not a gap in the record.", 13.5, "muted") + 50

    # ---- the mutations
    y = P.band(c, X0, y, "The mutations: what each does, and what the header says it must break")
    mrows = []
    lines = M.text(mod).split("\n")
    for mt in MUST_BREAK:
        at = M.code_lines_with(mod, f'"{mt}"')
        lem = [s for s in ev["statements"] if s["kind"] == "LEMMA" and re.search(rf'"{mt}"', (s["assume"] or "") +
                                                                                  s["prove"])]
        mrows.append([f"`{mt}`", hm[mt], "; ".join(f"`{M.enclosing(mod, ln)}`, line {ln}" for ln in at),
                      ", ".join(f"`{p}`" for p in MUST_BREAK[mt]),
                      "; ".join(f"`{s['name']}`" for s in lem) or "—"])
    y += c.table(X0, y, [("Mutation", 200, {}), ("What it does (the module's header)", 1200), ("Where it acts", 600),
                         ("Must break (the header), and does (TLC)", 700), ("The proof module's lemma", WW - 2700)],
                 mrows, size=13, accent="red", anchor="mutations") + 50

    # ---- the matrix, property by mutation
    y = P.band(c, X0, y, f"Every property by every mutation, read from `{res['file'][5:]}`")
    props = list(dict.fromkeys(r["prop"] for r in rows if not r["prop"].startswith("Never")))
    cols = ["none"] + list(MUST_BREAK)
    mrows = []
    for p in props:
        r_ = [f"`{p}`"]
        for mt in cols:
            h_ = [r for r in rows if r["mut"] == mt and r["prop"] == p]
            if not h_:
                r_.append("[[grey|—]]")
                continue
            r = h_[0]
            v = f"[[red|COUNTEREXAMPLE]]" if r["verdict"] == X else "**HOLDS**"
            mark = "must break" if p in MUST_BREAK.get(mt, []) else ("must hold" if mt != "none" else "")
            r_.append(f"{v}\n`{r['name']}` · {P.n(r['states'])}" + (f"\n{mark}" if mark else "") +
                      ("\n[[amber|found writing the proof]]" if r["name"] in ADDED_BY_PROOF else ""))
        mrows.append(r_)
    cw = (WW - 330) / len(cols)
    y += c.table(X0, y, [("Property", 330, {})] + [(f"`{m}`", cw) for m in cols], mrows, size=12.5,
                 anchor="matrix") + 14
    y += c.para(X0, y, WW, f"Every row's verdict is held by the diagram ({len(EXPECT_ROWS)} rows), and every mutation's "
                "counterexamples are exactly the properties the header says it must break (compared at build time). "
                "Each of F1, F2 and F3 is shown needed on its own: dropping one breaks its own property and leaves the "
                "other holding. \"must hold\" marks a property a mutation is run on and must not break.", 13.5,
                "muted") + 50

    # ---- the four rows the proof found
    y = P.band(c, X0, y, "The four rows the proof found, and the two results files")
    y += P.row_cards(c, X0, y, WW, 30, [
        ("What ADR-0047 R12 says", [
            "\"The proof found no fault in the record. It did correct the module's account of itself in four rows: "
            "`M_LOAD`, `M_RESET` and `M_DELIVER` each break `LabelsCoverTruth` as well, and `M_DELIVER` breaks "
            "`ClearSetCoversGuest`\" (ADR-0047 §11 ⟨R12⟩)."], "blue", {}),
        ("The two files", [
            f"`{EARLIER[5:]}` (`{CITES[EARLIER]}`): {len(earlier['rows'])} rows, the run of the module at R10 "
            f"(`{EARLIER_MODULE}`).",
            f"`{res['file'][5:]}` (`{CITES[res['file']]}`): {len(rows)} rows, of the module now (`{CITES[mod]}`); it "
            f"adds {', '.join(f'`{n_}`' for n_ in ADDED_BY_PROOF)}, and every row both carry has the same verdict "
            f"(compared at build time)."], "teal", {}),
    ], size=13.5) + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverOutwardEffect": "An outward call is admitted.",
        "NeverTaintedOutward": "An outward call by a Thinker that has read tainted bytes is admitted.",
        "NeverF1": "F1 refuses a call.", "NeverF2": "F2 refuses a call.", "NeverF3": "F3 refuses a call.",
        "NeverSuppressed": "An item is delivered as a handle.",
        "NeverHandleInput": "A tool is given a handle as input.",
        "NeverCleanLeak": "A secret goes out with no tainted read before it: F1 is not met by refusing every send.",
        "NeverReleased": "A releasing entry releases `restricted`.",
    }) + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, None, assumptions_note="`MaxSeq` is a natural number: the proofs hold for every "
                                                          "value, where TLC ran at 3") + 14
    y += c.para(X0, y, WW, "\"The proof also needed an invariant no property names: only an item that exists is in "
                "the guest\" (ADR-0047 R12): `GuestIn`, part of `BaseAlways`.", 13.5, "muted") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y += c.para(X0, y, WW, f"`{P.PREMISES[5:]}`'s theorem table has no row whose \"Checked in\" names `Labels.tla`, and "
                "its derived premises name no `invariant(Labels)` (checked at build time).", 14, "ink") + 50

    # ---- where else, digests
    y = P.band(c, X0, y, "Where else `Labels.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, extra=[(EARLIER, CITES[EARLIER], "ADR-0047 §11 ⟨R10⟩")],
              note="ADR-0047 §11 cites each of these files by digest, compared at build time.")
    return c
