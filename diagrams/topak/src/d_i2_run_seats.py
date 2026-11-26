"""I2 — `RunSeats.tla`, the module ADR-0043 §8 asks for: Run's alphabets by seat kind (ADR-0043 §2) and no variant
name common to Build and Run (ADR-0040 §2), drawn whole from its own text and every results file about it.

Built on modpage.py's bands (family I). What the diagram expects the files to say is recorded below as literals and
compared with them both ways at build time."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I2", "run-seats"
NAME = "RunSeats"
MODULE_FILES = ("spec/RunSeats.tla", "spec/RunSeats_proof.tla")
W = 3400

REC43 = "decisions/ADR-0043.md"
REC37 = "decisions/ADR-0037.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["OnlyThinkersActuate", "ObserversConsultAndReport", "NoNameCrossesDomains", "Safe"]
EXPECT = {("none", PROPS[0]): H, ("none", PROPS[1]): H, ("none", PROPS[2]): H,
          ("M_KIND", PROPS[0]): X, ("M_KIND", PROPS[1]): X, ("M_KIND", PROPS[2]): H,
          ("M_DOMAIN", PROPS[2]): X, ("M_DOMAIN", PROPS[0]): H, ("M_DOMAIN", PROPS[1]): X,
          ("M_OBSEMIT", "Safe"): H}
EXPECTED_LINE = ("none HOLDS on all three; M_KIND breaks OnlyThinkersActuate and ObserversConsultAndReport only; "
                 "M_DOMAIN breaks NoNameCrossesDomains and, with it, ObserversConsultAndReport (a Run observer seat "
                 "issued a Build variant holds something else); witnesses VIOLATED under none; under M_OBSEMIT (the "
                 "provisional column of ADR-0037 §4) every property HOLDS and NeverObserverConsulted HOLDS")
B25_SAYS = ("proves `OnlyThinkersActuate` unless `M_KIND`, `ObserversConsultAndReport` unless `M_KIND` or "
            "`M_DOMAIN`, and `NoNameCrossesDomains` unless `M_DOMAIN`; `M_OBSEMIT` breaks none of them")
SEATS = {"rt": ("thinker", "run"), "ro": ("observer", "run"), "bt": ("thinker", "build"), "bo": ("observer", "build")}
S2_HEAD = ["Kind", "Run", "Why"]
S4_HEAD = ["Kind", "Build", "~~Run (provisional: G4 item 13)~~ struck at B20", "Run ⟨A1⟩ (ADR-0043 §2)"]
ELSEWHERE = ["C2", "G3", "H3"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"I2: {what}")


def sets(rel, name):
    return re.findall(r'"(\w+)"', M.definition(rel, name)[1])


def alphabets(mod):
    """The alphabet the module issues each seat, unmutated and under M_OBSEMIT: KindBound(kind) ∩ DomainActs(domain),
    read from the module's definitions."""
    _, kb = M.definition(mod, "KindBound")
    th = re.search(r'k = "thinker"\s*->\s*\{([^}]*)\}', kb)
    ob = re.search(r'k = "observer"\s*->\s*IF Mut = "M_OBSEMIT" THEN \{([^}]*)\}\s*ELSE \{([^}]*)\}', kb)
    _need(th and ob, "KindBound is not the shape the diagram reads")
    bound = {"none": {"thinker": re.findall(r'"(\w+)"', th.group(1)), "observer": re.findall(r'"(\w+)"', ob.group(2))},
             "M_OBSEMIT": {"thinker": re.findall(r'"(\w+)"', th.group(1)),
                           "observer": re.findall(r'"(\w+)"', ob.group(1))}}
    _, da = M.definition(mod, "DomainActs")
    _need(re.search(r'IF d = "run" THEN RunActs ELSE BuildActs', da), "DomainActs is not the shape the diagram reads")
    dom = {"run": sets(mod, "RunActs"), "build": sets(mod, "BuildActs")}
    kof = dict(re.findall(r'(\w+) \|-> "(\w+)"', M.definition(mod, "KindOf")[1]))
    dof = dict(re.findall(r'(\w+) \|-> "(\w+)"', M.definition(mod, "DomainOf")[1]))
    _need({s: (kof[s], dof[s]) for s in kof} == SEATS, f"KindOf and DomainOf are not the diagram's seats")
    out = {}
    for mt in bound:
        out[mt] = {s: [a for a in bound[mt][k] if a in dom[d]] for s, (k, d) in SEATS.items()}
    return out, dom


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts] == ["none"] + M.mutations(res), "the header's mutations are not the file's")
    head_props = [(p, "ADR-" + s.replace(" ", " ", 1), w) for p, s, w in M.header_properties(mod)]
    _need([p for p, _, _ in head_props] == PROPS[:3], "the header's properties are not the diagram's")
    _need(res["head"].get("expected") == EXPECTED_LINE, "the results file's expected: line has changed")
    _need(B25_SAYS in M.text(REC43), "ADR-0043 B25 no longer says what the diagram quotes")
    alph, dom = alphabets(mod)
    s2 = P.md_table(REC43, S2_HEAD, occurrence=0)
    s2_run = {r[0].strip("`"): re.findall(r"`(\w+)`", r[1]) for r in s2}
    for s, (k, d) in SEATS.items():
        if d == "run":
            _need(sorted(alph["none"][s]) == sorted(s2_run[k]),
                  f"the module issues {s} {alph['none'][s]}, ADR-0043 §2's {k} row is {s2_run[k]}")
    s4 = P.md_table(REC37, S4_HEAD)
    s4_build = {r[0].strip("`"): re.findall(r"`(\w+)(?:\(\w+\))?`", r[1]) for r in s4}

    c = Canvas(ID,
               "`RunSeats.tla`: in Run, only a thinker seat actuates and an observer seat consults and reports, and "
               "no variant name is shared by Build and Run. Three invariants, each with the mutations that break "
               "it: checked by TLC, proved by TLAPS and in Lean",
               "The module ADR-0043 §8 asks for, drawn from its own text and from every results file about it, all "
               "read at build time: the four seats and what the grant issues each, the three properties and the "
               "section each states (ADR-0043 §2, ADR-0040 §2), the mutation matrix, the provisional column's row, "
               "the witnesses, every theorem and lemma, the certified run and the Lean re-encoding. **What is "
               "checked or proved here is checked or proved of the module, at its constants or by its proofs, and "
               "not of the reference.** The module is frozen, cited by digest (ADR-0043 B25, ADR-0046, ADR-0053). "
               "It has no principals: the one-seat rule is `Seats.tla`'s, and is not restated here (its header).",
               W,
               f"spec/RunSeats.tla (its header, every definition); spec/RunSeats_proof.tla (every THEOREM and LEMMA); "
               f"{res['file']}; {ev['files']['proof_results']}; {ev['files']['cert']}; {M.LEAN_RESULTS} (compared "
               f"with {M.LEAN_LATER[10:]}); spec/lean/TopakSpec/RunSeats.lean; {P.PREMISES} (the RunSeats rows and "
               f"invariant(RunSeats)); ADR-0043 §2 (its table), §8, B20, B25; ADR-0040 §2; ADR-0037 §4 (its table), "
               f"A1; the manifest's titles of {', '.join(ELSEWHERE)}. Every file read at the pin its links open, and "
               f"checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0043", "accepted", "C4"),
                                                         ("ADR-0040", "accepted", "C3, C4")]))
    y += c.para(X0, y, WW, P.WORDS + " The module's header still calls ADR-0043 Proposed: it was written on "
                "2026.09.29, before Batch 20 ratified the record.", 14.5, "muted") + 34

    # ---- the picture
    y = P.band(c, X0, y, "The mechanism, as the module states it: a seat is issued what its kind and its domain "
                         "both allow, and every act is recorded with both")
    gl, al, el = (M.definition(mod, n_)[0] for n_ in ("Grant", "Act", "EndRound"))
    seat_cards = []
    for s, (k, d) in SEATS.items():
        seat_cards.append((f"Seat `{s}` · `{k}` · {'Run' if d == 'run' else 'Build'}",
                           [f"issued {', '.join(f'`{a}`' for a in alph['none'][s])}"],
                           "green" if d == "run" else "teal"))
    y = P.flow_picture(
        c, X0, y, WW,
        ("A grant, for one seat", ["`Grant(s)` names a seat and no principal"], "brown"),
        (f"The grant path (`Grant`, line {gl})", [
            "**①** `~lease[s].live`: the seat is free",
            "**②** by kind, `KindBound(KindOf[s])` (ADR-0043 §2). `M_KIND` [[red|issues all of]] `Acts`.",
            "**③** by domain, `DomainActs(DomainOf[s])` (ADR-0040 §2). `M_DOMAIN` [[red|issues all of]] `Acts`.",
            "**④** the lease holds the two bounds' intersection. `M_OBSEMIT` [[red|narrows]] an observer's bound "
            "to the provisional column."], "teal"),
        ("Refused, at ①", ["The seat is live: nothing changes."], "red"),
        (f"`lease`: one record per seat (line {M.line_of(mod, r'^VARIABLES lease, acted$')})", "teal", seat_cards),
        ("The record of acts: `acted`", ["one per admitted act: `[act |-> a, kind |-> KindOf[s], domain |-> "
                                         "DomainOf[s]]`"], "grey"),
        [("ADR-0043 §2, read on `acted`", ["`OnlyThinkersActuate`: `Actuate` only from a `thinker` seat"], "record"),
         ("ADR-0043 §2, read on `acted`", ["`ObserversConsultAndReport`: a Run observer seat only `Consult`s and "
                                           "`Report`s"], "record"),
         ("ADR-0040 §2, read on `acted`", ["`NoNameCrossesDomains`: a Run variant only under a Run seat, a Build "
                                           "variant only under a Build seat"], "record")],
        {"ask": "asks", "write": "⑤ a live lease", "act": f"⑥ `Act(s)`, line {al}",
         "end": f"⑦ `EndRound(s)`, line {el}: the lease becomes `NoLease`"},
        "**Key.** ① to ④ are `Grant`'s conjuncts and the alphabet it writes; ⑤ is the lease; ⑥ an act from the live "
        "alphabet, recorded with the seat's kind and domain; ⑦ ends a lease and nothing else. Dotted blue lines show "
        "what each property reads; red marks where each mutation acts. Each seat's alphabet is computed from the "
        "module's `KindBound` and `DomainActs`. The picture is the diagram's own drawing of the definitions below.") + 50

    # ---- the machine
    y = P.band(c, X0, y, "The machine: four seats, two domains, three actions (`RunSeats.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Constants: the seats and the acts", ["Seats", "BuildActs", "RunActs", "Acts"],
          [f"`CONSTANTS Mut` (line {M.line_of(mod, r'^CONSTANTS Mut$')}): `none`, `M_KIND`, `M_DOMAIN` or "
           f"`M_OBSEMIT`, the only constant"], "grey"),
         ("Each seat's kind and domain, fixed at declaration", ["KindOf", "DomainOf"], [], "teal"),
         (None, ["DomainActs"], ["A domain's variants: what ADR-0040 §2 keeps apart."], "teal"),
         (None, ["KindBound"], ["ADR-0037 §4's Build column and ADR-0043 §2's Run column, in one table. A "
                                "`grant` seat is not modelled: it holds nothing in Run."], "teal")],
        [("State: `lease` and `acted`", ["NoLease", "Init"],
          [f"`VARIABLES lease, acted` (line {M.line_of(mod, r'^VARIABLES lease, acted$')})"], "grey"),
         (None, ["Grant"], ["The lease is the kind's bound **and** the domain's. Either mutation drops one."], "teal"),
         (None, ["Act"], ["The act is recorded with its seat's kind and domain: what every property reads."], "teal"),
         (None, ["EndRound"], ["A live lease ends; nothing else changes."], "teal"),
         ("`Next` and `Spec`", ["Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 50

    # ---- the properties
    y = P.band(c, X0, y, "The three properties, the record section each states, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, head_props) + 50

    # ---- mutations
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    y = P.mutations(c, X0, y, WW, ev, head_muts) + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("The results file expects", [f"\"{EXPECTED_LINE}\" (`{res['file'][5:]}`, line 3)"], "grey", {}),
        ("The record says", [f"\"{B25_SAYS}\" (ADR-0043 B25)"], "blue", {}),
        ("The diagram expects, and compares", [
            f"Every cell below against its own literal, both ways: {len(EXPECT)} cells, every one as expected."],
         "grey", {}),
    ], size=13.5) + 50

    # ---- the matrix
    y = P.band(c, X0, y, f"Every mutation by every property, read from `{res['file'][5:]}`")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, dict(head_muts)) + 14
    y += c.para(X0, y, WW, f"Constants: \"{res['head']['jar'].split(' · ', 1)[1]}\" (the file's header). "
                "`M_OBSEMIT` is run on `Safe` only, and on one witness (below); the other cells are not run.",
                13.5, "muted") + 24
    y += P.other_rows_table(c, X0, y, WW, ev, {
        "rs-obsemit-consulted": "Under the provisional column an observer seat never consults: `Consult` is what "
                                "ADR-0043 §2 gives an observer, and the provisional column could not. The header: "
                                "\"which shows what the provisional column could not do\"."}) + 50

    # ---- witnesses
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated, so what the three "
                         "properties forbid is not forbidden vacuously")
    y += P.witnesses_table(c, X0, y, WW, ev, {
        "NeverActuated": "A seat actuates: `OnlyThinkersActuate` ranges over a reachable `Actuate`.",
        "NeverObserverReported": "An observer seat reports: what `ObserversConsultAndReport` allows is reached.",
        "NeverObserverConsulted": "An observer seat consults: `Consult`, new for an observer in ADR-0043 §2, is "
                                  "reached. Under `M_OBSEMIT` it is not (above).",
    }) + 50

    # ---- the alphabets against the records
    y = P.band(c, X0, y, "The alphabets the module issues, against ADR-0043 §2 and ADR-0037 §4")
    half = (WW - 30) / 2
    t1 = c.table(X0, y, [("Kind", 150, {}), ("Run", 420), ("Why", half - 570)], s2, size=13.5, accent="blue")
    rows = []
    for s, (k, d) in SEATS.items():
        got = alph["none"][s]
        if d == "run":
            rec, agree = s2_run[k], "agrees (checked at build time)"
        else:
            rec = s4_build[k]
            extra = [a for a in rec if a not in dom["build"]]
            agree = (f"the module's `BuildActs` has no {', '.join(f'`{a}`' for a in extra)} (the diagram's "
                     f"reading)") if extra else "agrees"
        rows.append([f"`{s}`", f"`{k}` · {d}", ", ".join(f"`{a}`" for a in got),
                     f"{'ADR-0043 §2' if d == 'run' else 'ADR-0037 §4 Build'}: {', '.join(f'`{a}`' for a in rec)}",
                     agree])
    t2 = c.table(X0 + half + 30, y, [("Seat", 110, {}), ("Kind · domain", 220), ("The module issues", 330),
                                     ("The record's row", 420), ("Against it", half - 1080)],
                 rows, size=13.5, accent="teal")
    y += max(t1, t2) + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("ADR-0043 §2's table, drawn whole", [
            "The first table under §2. Its second, the `orchestrator` row (A3, after ADR-0054 §3), is **pending and "
            "not applied**, and the module has no such kind."], "blue", {}),
        ("The provisional column", [
            f"Under `M_OBSEMIT` an observer is issued {', '.join(f'`{a}`' for a in alph['M_OBSEMIT']['ro'])} in "
            f"Run: ADR-0037 §4's struck column. It breaks no invariant, since the invariants are upper bounds "
            f"(the proof module's header)."], "amber", {}),
        ("What the module does not model", [
            "A `grant` seat, which holds nothing in Run; principals, and the one-seat rule (`Seats.tla`); `Invoke`, "
            "`Submit` and `Vote` in Build."], "grey", {}),
    ], size=13.5) + 50

    # ---- the proofs
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, {
        "GrantAlphabet": "What a grant writes: the two bounds' intersection.",
        "BoundsInActs": "Every issued alphabet is within `Acts`.",
        "KindActuate": "Unless `M_KIND`, only a thinker's bound holds `Actuate`.",
        "ObserverRun": "Unless `M_KIND` or `M_DOMAIN`, a Run observer's alphabet is `Consult` and `Report`.",
        "DomainNames": "Unless `M_DOMAIN`, a seat's variants are its domain's.",
        "InitTypeOK": "Typing, at the start.",
        "NextTypeOK": "Typing is kept, under every mutation.",
        "InitInv": "`Inv` (a live alphabet is the intersection) at the start.",
        "NextInv": "`Inv` is kept.",
        "ActRecord": "What an act records.",
        "NextActuate": "`OnlyThinkersActuate` is kept unless `M_KIND`.",
        "NextObservers": "`ObserversConsultAndReport` is kept unless `M_KIND` or `M_DOMAIN`.",
        "NextDomains": "`NoNameCrossesDomains` is kept unless `M_DOMAIN`.",
        "InitAll": "All three, at the start.",
        "OnlyThinkersActuateAlways": "ADR-0043 §2, for every behaviour, unless `M_KIND`.",
        "ObserversConsultAndReportAlways": "ADR-0043 §2, unless `M_KIND` or `M_DOMAIN`.",
        "NoNameCrossesDomainsAlways": "ADR-0040 §2, unless `M_DOMAIN`.",
        "SafeAlways": "All three, unmutated.",
        "MutKindObserverActuates": "Why `M_KIND` must fail: the Run observer is issued `Actuate`.",
        "MutDomainCrosses": "Why `M_DOMAIN` must fail: the Build thinker is issued `Actuate`.",
    }, assumptions_note="\"No constants beyond `Mut`, so no model assumptions\": the proof module's header") + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the module re-encoded and its theorems proved again")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.RunSeats") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, PROPS[:3], ["invariant(RunSeats)"]) + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `RunSeats.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev)
    return c
