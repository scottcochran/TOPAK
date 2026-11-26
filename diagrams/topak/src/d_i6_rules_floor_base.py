"""I6 — `RulesFloorBase.tla`, the live definition of the rules floor: the rule space, the entries, the genesis rules
and the ASSUME that genesis satisfies the floor, shared by the ADR-0029 §5 bootstrap modules. It has no behaviour, no
TLC run and no proof module of its own; its two theorems are proved in Lean.

Built on modpage.py's bands (family I). ADR-0026 §2's table and ADR-0029 §5's are drawn whole and compared with the
module and the tree; the three copies of the floor (this, rev5's and G1's) are compared entry by entry."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I6", "rules-floor-base"
NAME = "RulesFloorBase"
MODULE_FILES = ("spec/RulesFloorBase.tla",)
W = 3400

REC26 = "decisions/ADR-0026.md"
REC29 = "decisions/ADR-0029.md"
COPIES = [("spec/RulesFloorBase.tla", "the live definition"),
          ("spec/RulesFloorNV_rev5.tla", "frozen, ADR-0026 §7 (I5)"),
          ("spec/RulesFloorNV.tla", "frozen, G1; ADR-0026 §6")]
EXTENDED_BY = ["spec/Anchor.tla", "spec/BreakGlass.tla", "spec/BreakGlass_A1.tla"]
S2_HEAD = ["Entry", "Bounds"]
S5_HEAD = ["Module", "Invariant"]
A2_SAYS = "R6 still bounds the number of floor exceptions; the count it bounds is 1, erasure."
ELSEWHERE = ["B2", "B4", "B7", "B8", "D4", "D5", "G3", "H3", "H5"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def arms(rel):
    """Entry's CASE arms: {entry: condition}, in order."""
    _, src = M.definition(rel, "Entry")
    out = dict(re.findall(r'e = "(R\d)"\s*->\s*(.+?)\s*$', src, re.M))
    _need(out, f"{rel}: Entry has no arms")
    return out


def build():
    ev = M.evidence(NAME)
    mod = ev["files"]["module"]
    _need(ev["tlc"] is None and "proof" not in ev, "the module has evidence of its own the diagram does not draw")
    copies = {rel: arms(rel) for rel, _ in COPIES}
    alls = {rel: re.findall(r'"(R\d)"', M.definition(rel, "AllEntries")[1]) for rel, _ in COPIES}
    for rel in copies:
        _need(sorted(alls[rel]) == sorted(copies[rel]), f"{rel}: AllEntries is not Entry's arms")
    rec26 = M.text(REC26)
    _need(A2_SAYS in re.sub(r"\s+", " ", rec26), "ADR-0026 A2 no longer says what the diagram quotes")
    r6 = copies[mod]["R6"]
    _, gsrc = M.definition(mod, "Genesis")
    gex = re.search(r"exceptions \|-> (\d+)", gsrc)
    _need(r6 == "r.exceptions <= 2" and gex and gex.group(1) == "2", f"R6 is {r6!r}, genesis exceptions {gex}")
    g1, r5, base = copies["spec/RulesFloorNV.tla"], copies["spec/RulesFloorNV_rev5.tla"], copies[mod]
    _need(g1["R1"] == 'r.quorum = "all"' and r5["R1"] == base["R1"] == 'r.quorum.mode = "all"', "R1's three forms")
    _need({"R3", "R4"} <= set(g1) and not ({"R3", "R4"} & (set(r5) | set(base))), "R3 and R4")
    _need("R6" in base and "R6" not in r5 and "R6" not in g1, "R6 is this copy's alone")
    _need("R9" in r5 and "R9" in base and "R9" not in g1, "R9 is in the two later copies")
    ext = sorted(f for f in M.pin().files if f.startswith("spec/") and f.endswith(".tla")
                 and re.search(r"^EXTENDS .*\bRulesFloorBase\b", M.text(f), re.M))
    _need(ext == EXTENDED_BY, f"the modules that extend it are {ext}")
    asm = [i + 1 for i, ln in enumerate(M.text(mod).split("\n")) if ln.startswith("ASSUME ")]
    _need(len(asm) == 1, "the module's ASSUMEs")
    files = M.pin().files

    def s2_compare(row):
        m = re.search(r"\*\*(R\d)\*\*", row[0])
        _need(m, f"§2 row {row[0][:30]!r}")
        e = m.group(1)
        struck = row[0].startswith("~~")
        if struck:
            _need(e not in copies[mod], f"{e} is withdrawn in §2 and an entry of the module")
            return f"withdrawn, and not an entry of the module"
        _need(e in copies[mod], f"{e} is in §2 and not an entry of the module")
        return f"`Entry`, arm `{e}`: `{copies[mod][e]}`"

    def s5_compare(row):
        mname = row[0].strip("`")
        inv = re.findall(r"`(\w+)`", row[1])[-1]
        rel = f"spec/{mname}.tla"
        if rel not in files:
            return f"[[red|no module `{mname}.tla` at the pin]]"
        defs = M.pin().defined_in(rel)
        has = inv in defs
        uses = rel in EXTENDED_BY
        return (f"`{mname}.tla` defines `{inv}` (line {defs[inv]})" if has else f"`{mname}.tla` has no `{inv}`") + \
               ("; extends this module" if uses else "")

    c = Canvas(ID,
               "`RulesFloorBase.tla`: the live definition of the rules floor, its six entries and the genesis rules "
               "that satisfy it, shared by the bootstrap modules. Definitions only: no TLC run and no proof module "
               "of its own; two theorems proved in Lean",
               "The module ADR-0029 §5's bootstrap modules extend, drawn from its own text, all read at build time: "
               "the rule space, the entries, the floor, the genesis rules and their ASSUME; ADR-0026 §2's table "
               "against the module's entries; the three copies of the floor compared entry by entry; ADR-0029 §5's "
               "modules against the tree; the modules that extend this one; and the Lean re-encoding. **It has no "
               "behaviour of its own: what is checked or proved of the floor is checked or proved in the modules "
               "that extend it, of their own machines.** A finding is drawn as one: the module's R6 bound and "
               "genesis count predate ADR-0026 A2.",
               W,
               f"spec/RulesFloorBase.tla (its header, every definition and its ASSUME); spec/RulesFloorNV_rev5.tla and "
               f"spec/RulesFloorNV.tla (Entry, AllEntries); spec/Anchor.tla, spec/BreakGlass.tla, "
               f"spec/BreakGlass_A1.tla (their EXTENDS lines, and the invariants ADR-0029 §5 names); "
               f"{M.LEAN_RESULTS} (compared with {M.LEAN_LATER[10:]}); spec/lean/TopakSpec/RulesFloorBase.lean; "
               f"ADR-0026 §2 (its table) and A2; ADR-0029 §5 (its table) and A1; ADR-0027 §2; the tracked files at "
               f"the pin; the manifest's titles of {', '.join(ELSEWHERE)}. Every file read at the pin its links "
               f"open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0026", "accepted", ""), ("ADR-0029", "accepted", "")]))
    hd = [ln.strip() for ln in M.header_comment(mod) if ln.strip()]
    y += c.para(X0, y, WW, "The module's header: \"" + " ".join(hd) + "\"", 14.5, "muted") + 34

    # ---- the definitions
    y = P.band(c, X0, y, "The definitions: the people, the acts, the rule space, the entries, the floor and the "
                         "genesis rules (`RulesFloorBase.tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("The people and the acts", ["Humans", "Author", "AnchorKeys", "AuthActs", "BGActs"],
          [f"`CONSTANT Active` (line {M.line_of(mod, r'^CONSTANT Active')}): the floor entries in force; \"drop "
           f"one to mutate\" (its comment)"], "grey"),
         ("The rule space", ["QVals", "RuleSpace"], ["`exceptions`: the declared policy-floor exceptions (ADR-0013 "
                                                     "§2), which this copy adds."], "grey"),
         ("The floor: six entries", ["Entry", "AllEntries", "Floor"], [], "blue"),
         (None, ["Genesis"], [f"`ASSUME \\A e \\in AllEntries : Entry(e, Genesis)` (line {asm[0]}): \"the shape "
                              f"of `GenesisSatisfiesFloor`\" (its comment; ADR-0027 §2, ADR-0029 §5)."], "blue")],
    ]) + 50

    # ---- ADR-0026 §2
    y = P.band(c, X0, y, "ADR-0026 §2's table, every row, against the module's entries")
    y += P.record_table(c, X0, y, WW, REC26, S2_HEAD, (900, 1300), s2_compare,
                        against="Against the module (compared at build time)") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("[[red|A finding: R6 and the genesis count predate ADR-0026 A2]]", [
            f"ADR-0026 A2 (ratified in Batch 34): \"{A2_SAYS}\"",
            f"The module: R6 is `{r6}`, and `Genesis` carries `exceptions |-> {gex.group(1)}`, \"erasure and "
            f"break-glass (ADR-0013 §3)\" (its comment). Its header dates its contents \"as ratified 2026.09.23\".",
            "The bound still admits a count of 1; the genesis value does not match the record. The diagram's "
            "reading, for the custodian; the record is not changed by drawing it."], "red", {}),
        ("Pending, not applied", ["ADR-0026 A1: R8 would enter the table as a break-glass TTL bound. The module "
                                  "reserves it: \"R8 reserved, candidate (break-glass grant TTL)\" (its header)."],
         "amber", {}),
    ], size=13.5) + 50

    # ---- three copies
    y = P.band(c, X0, y, "The three copies of the floor, entry by entry (each module's `Entry`)")
    every = sorted({e for a in copies.values() for e in a}, key=lambda e: int(e[1:]))
    rows = []
    for e in every:
        cells = [f"**{e}**"]
        for rel, _ in COPIES:
            cells.append(f"`{copies[rel][e]}`" if e in copies[rel] else "[[grey|not an entry]]")
        same = len({copies[rel].get(e) for rel, _ in COPIES if e in copies[rel]}) == 1
        rows.append(cells if same and all(e in copies[r_] for r_, _ in COPIES) else {"cells": cells, "accent": "amber"})
    cw = (WW - 160) / 3
    y += c.table(X0, y, [("Entry", 160, {})] + [(f"`{rel[5:]}` · {what}", cw) for rel, what in COPIES], rows,
                 size=13.5, accent="blue") + 14
    y += c.para(X0, y, WW, "Read from each module at build time. A row is amber where the copies differ, and plain where all three agree: R1's "
                "quorum is a string in G1's copy and tagged in the later two, R3 and R4 are withdrawn after G1, R6 "
                "is this copy's alone, and R9 is in the later two. \"Divergence between them and this module is "
                "expected and is what the dates are for\" (the header).", 13.5, "muted") + 50

    # ---- ADR-0029 §5
    y = P.band(c, X0, y, "ADR-0029 §5's bootstrap modules, against the tree")
    y += P.record_table(c, X0, y, WW, REC29, S5_HEAD, (500, 900), s5_compare,
                        against="Against the tree at the pin (compared at build time)") + 14
    y += c.para(X0, y, WW, "The `Genesis`, `RulesFloor` and `Promotion` modules are not at the pin; the binding lists "
                "`PromotionMeetsIssuedQuorum` as owed (\"the `Promotion` module, owed\"). This module's `ASSUME` is "
                "\"the shape of `GenesisSatisfiesFloor`\", not that invariant. TLC checking at small constants is "
                "\"recommended; it is not required\" (ADR-0029 §5).", 13.5, "muted") + 50

    # ---- who extends it
    y = P.band(c, X0, y, "The modules that extend it")
    rows = []
    for rel in EXTENDED_BY:
        stem = rel[5:-4]
        prf = f"spec/{stem}_proof.tla"
        ln = M.line_of(rel, r"^EXTENDS ")
        rows.append([f"`{rel[5:]}`", P.code(M.text(rel).split("\n")[ln - 1]) + f" (line {ln})",
                     f"`{prf[5:]}`" if prf in files else "[[red|no proof module]]"])
    y += c.table(X0, y, [("Module", 500, {}), ("Its EXTENDS line", 1400), ("Its proof module", WW - 1900)], rows,
                 size=13.5, accent="teal") + 14
    y += c.para(X0, y, WW, "Found at build time: every module under `spec/` whose `EXTENDS` names this one, compared "
                "with the diagram's list. `RulesFloorNV.tla` and `RulesFloorNV_rev5.tla` carry their own copies and do "
                "not extend it.", 13.5, "muted") + 50

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the definitions re-encoded, and genesis proved to satisfy the floor")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.RulesFloorBase",
               extra_card="`GenesisEntries` is the module's `ASSUME`, proved in Lean of the re-encoding; TLAPS has no "
                          "proof module for it.") + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `RulesFloorBase.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev)
    return c
