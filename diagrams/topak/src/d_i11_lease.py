"""I11 — `Lease.tla`, ADR-0031's lease schema: authority monotone across renewal, the epoch fence, targeted revocation
and rung 0 never `Contained`, drawn whole from the module's own text and the results file ADR-0031 §8 cites. Frozen
by digest; no proof module of its own: its successor `Lease_A1.tla` (I12) is proved.

Built on modpage.py's bands (family I). The bands both lease modules draw are defined here and imported by I12;
ADR-0031 §8's table, which covers both, is compared with each module's file."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I11", "lease"
NAME = "Lease"
MODULE_FILES = ("spec/Lease.tla",)
W = 3400

REC = "decisions/ADR-0031.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "LeaseAuthorityMonotone", "NoActionUnderFencedEpoch", "Rung0NeverContained", "RevokedStaysStopped"]
EXPECT = {("none", "Safe"): H, ("M_RENEW", "LeaseAuthorityMonotone"): X, ("M_FENCE", "NoActionUnderFencedEpoch"): X,
          ("M_RUNG", "Rung0NeverContained"): X, ("M_ROLE", "LeaseAuthorityMonotone"): X,
          ("M_REVOKE", "RevokedStaysStopped"): X}
S8_HEAD = ["Check", "Mut", "Invariant", "Result"]
R3_SAYS = "with `RevokedStaysStopped` in `Safe`, which holds over 1,746,048 distinct states"
ELSEWHERE = ["C3", "G3", "H3"]
WITNESS_READINGS = {
    "NeverActed": "An action is admitted: `NoActionUnderFencedEpoch` ranges over real actions.",
    "NeverRenewed": "A renewal happens: `LeaseAuthorityMonotone`'s antecedent is reached.",
    "NeverRenewedAbove0": "A renewal at rung 1 or above: the rung clause of `Refines` does not hold only because "
                          "rung-0 leases were the only ones renewed (A1).",
    "NeverRevoked": "A fleet fence happens.",
    "NeverStaleLease": "A lease outlives a revocation: \"the one that matters for §5\"; without it the fence would "
                       "protect nothing (ADR-0031 §8).",
    "NeverSelectiveRevoke": "One principal is revoked while another's lease stays live: finding 5's case, made "
                            "reachable (R3).",
}


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def s8_compare(rows, a1, module):
    """ADR-0031 §8's rows against one module's file: an ⟨A1⟩ row is run on the successor only."""
    def compare(row):
        mut = (re.findall(r"`(\w+)`", row[1]) or [row[1].strip()])[0]
        inv = re.findall(r"`(\w+)`", row[2])[0]
        word = H if "holds" in row[3].lower() else X if "counterexample" in row[3].lower() else None
        hit = [r for r in rows if r["mut"] == mut and r["prop"] == inv]
        if "⟨A1⟩" in row[0] and not a1:
            _need(not hit, f"§8's A1 row {row[0][:30]!r} is run on {module}")
            return "an A1 row: not run on `Lease.tla`; run on `Lease_A1.tla` (I12)"
        _need(len(hit) == 1 and word, f"§8 row {row[0][:40]!r}: {len(hit)} rows in {module}")
        _need(hit[0]["verdict"] == word, f"§8 row {row[0][:40]!r}: {module} says {hit[0]['verdict']}")
        return f"agrees: `{hit[0]['name']}`, {P.n(hit[0]['states'])} states"
    return compare


def band_picture(c, X0, y, WW, mod, a1):
    gl, rl, al, cl, el = (M.definition(mod, n_)[0] for n_ in ("Grant", "Renew", "Act", "Contained", "EndRound"))
    refine = ("a narrower alphabet, **the same rung** and the same role (A1)" if a1 else
              "a narrower alphabet, a rung no higher, and the same role")
    y = P.band(c, X0, y, "The mechanism, as the module states it: one lease per principal per round, a renewal only "
                         "narrows it, and the epoch fences every lease issued before it")
    return P.flow_picture(
        c, X0, y, WW,
        ("A principal, in its round", ["asks for a grant, a renewal, or an action"], "brown"),
        (f"Grant and renewal (`Grant`, line {gl}; `Renew`, line {rl})", [
            "**①** a grant only with no live lease: one per round (ADR-0031 §2), and not to a revoked principal "
            "(§5 R3). `M_REVOKE` [[red|ignores the revocation set]].",
            f"**②** a renewal at the same epoch must refine the lease: {refine} (§4). `M_RENEW` [[red|checks "
            f"nothing]]; `M_ROLE` [[red|drops the role]]" + ("; `M_LOWER` [[red|lets the rung fall]], the frozen "
                                                             "rule." if a1 else "."),
            "**③** an action only under a live lease at the current epoch (ADR-0022 §2). `M_FENCE` [[red|skips the "
            "epoch check]]."], "teal"),
        ("Refused", ["a second lease in the round, a revoked principal's grant, a renewal that does not refine, an "
                     "action at a fenced epoch"], "red"),
        ("`lease` and `prev`: each principal's lease, and the one it replaced", "teal", [
            ("A live lease", ["alphabet, rung, role, epoch and fence"], "teal"),
            (f"Counted Contained (line {cl})", ["live and at rung 1 or above; rung 0 is `Mediated`, always (§3). "
                                                "`M_RUNG` [[red|ignores the rung]]."], "green"),
            ("Revocation (`Revoke`, `RevokeLease`)", ["the fleet fence raises the epoch; a targeted revocation ends one "
                                                      "lease and bars later grants (§5 R3)"], "red")]),
        ("The record of actions: `acted`", ["each admitted action, with the epoch it was admitted at and its lease's "
                                            "epoch"], "grey"),
        [("ADR-0031 §5, read on `acted`", ["`NoActionUnderFencedEpoch`"], "record"),
         ("ADR-0031 §4, §3 and §5 R3, read on `lease`", ["`LeaseAuthorityMonotone`, `Rung0NeverContained`, "
                                                         "`RevokedStaysStopped`"], "state")],
        {"ask": "asks", "write": "④ a lease", "act": f"⑤ `Act(p)`, line {al}",
         "end": f"⑥ `EndRound(p)`, line {el}: the lease ends with the round"},
        "**Key.** ① to ③ are the mechanism's checks; ④ the lease; ⑤ an admitted action; ⑥ the end of the round. Red "
        "marks where each mutation acts. The picture is the diagram's own drawing of the definitions below.") + 50


def band_machine(c, X0, y, WW, mod, name, a1):
    y = P.band(c, X0, y, f"The machine: grants, renewals, actions, the fleet fence and targeted revocation "
                         f"(`{name}.tla`)")
    return P.machine(c, X0, y, WW, mod, [
        [("Constants, and the empty lease", ["Principals", "Acts", "Rungs", "Roles", "NoLease"],
          [f"`CONSTANTS Mut, MaxEpoch, MaxFence` (line {M.line_of(mod, r'^CONSTANTS Mut, MaxEpoch, MaxFence$')})"],
          "grey"),
         ("What a renewal must do", ["Narrows"] + (["LowerOrSame"] if a1 else []) + ["Refines", "RenewalAllowed"],
          ["ADR-0031 §4." + (" `LowerOrSame` is the frozen rule, kept as `M_LOWER`." if a1 else "")], "blue"),
         (None, ["Grant"], [], "teal"),
         (None, ["Renew"], [], "teal")],
        [("The fence, and an action", ["Revoke", "EpochOK", "Act"], [], "teal"),
         ("Targeted revocation, and the round's end", ["RevokeLease", "EndRound"], ["ADR-0031 §5 R3; §2."], "red"),
         (None, ["Contained"], ["\"Confinement is necessary, not sufficient\": only the rung half (its comment)."],
          "green"),
         ("State, and `Next`", ["Init", "Next", "Spec"], ["No fairness: safety only."], "grey")],
    ]) + 50


def band_record(c, X0, y, WW, rows, a1, module, note):
    y = P.band(c, X0, y, "ADR-0031 §8's table, every row and column, compared with this module's results file")
    y += P.record_table(c, X0, y, WW, REC, S8_HEAD, (900, 220, 520, 360), s8_compare(rows, a1, module)) + 14
    return y + c.para(X0, y, WW, note, 13.5, "muted") + 50


def build():
    ev = M.evidence(NAME)
    mod = ev["files"]["module"]
    res = ev["tlc"]
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts] == ["none"] + M.mutations(res), "the header's mutations are not the file's")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == ["LeaseAuthorityMonotone", "NoActionUnderFencedEpoch", "RevokedStaysStopped",
                                    "Rung0NeverContained"], "the header's properties")
    rec = re.sub(r"\s+", " ", M.text(REC))
    base = [r for r in res["rows"] if r["name"] == "base"][0]
    _need(R3_SAYS in rec and base["states"] == 1746048, "ADR-0031 §8's R3 sentence, or the file's base row")
    _need("`spec/Lease.tla` · digest `7636c6c3364bca9c`" in rec and M.sha16(mod) == "7636c6c3364bca9c",
          "ADR-0031 §8's digest of the module")
    _need(re.search(r"^Rungs\s+== 0\.\.2$", M.text(mod), re.M), "the module's rungs are not 0..2")
    adr34 = re.sub(r"\s+", " ", M.text("decisions/ADR-0034.md"))
    d8 = "The second half of discrepancy 8, `Lease.tla` declaring rungs 0 to 2 where the schema has 0 to 3, is not addressed here."
    _need(d8 in adr34, "ADR-0034's sentence on discrepancy 8")
    _need("Lease.tla is frozen at digest 7636c6c3364bca9c" in " ".join(M.header_comment("spec/Lease_A1.tla")),
          "Lease_A1.tla's header no longer names this module frozen")

    c = Canvas(ID,
               "`Lease.tla`: a renewal never adds authority, no action is admitted at a fenced epoch, a revoked "
               "principal stays stopped, and rung 0 is never `Contained`. Four invariants, each broken by its "
               "mutation: checked by TLC; frozen, and proved only as its successor",
               "The module ADR-0031 §8 reports for the lease schema as ratified at R3, drawn from its own text and the "
               "results file that section cites, all read at build time: the mechanism, the four properties and the "
               "section each states, the mutation matrix, the witnesses, and ADR-0031 §8's table compared row by row. "
               "**It has no proof module: it is frozen by digest, and its properties are proved of `Lease_A1.tla` "
               "(I12), which differs from it only where marked A1.** What is checked here is checked of the module, "
               "at its constants, and not of the reference.",
               W,
               f"spec/Lease.tla (its header, every definition); {res['file']}; spec/Lease_A1.tla (its header); "
               f"{P.PREMISES} (the four rows); ADR-0031 §2–§5, §8 (its table and notes), R1, R3, A1, B10; ADR-0034 "
               f"§7 (discrepancy 8); ADR-0022 §2. Every file read at the pin its links open, and checked equal to the "
               f"tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0031", "accepted", "C1")], tail=[
        ("`Lease_A1.tla`", ("Its successor, proved (I12)", "blue", "4 3"), "")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    y = band_picture(c, X0, y, WW, mod, a1=False)
    y = band_machine(c, X0, y, WW, mod, NAME, a1=False)

    y = P.band(c, X0, y, "The four properties, the section of ADR-0031 each states, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, f"ADR-0031 {s}", w) for p, s, w in hp]) + 50
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    y = P.mutations(c, X0, y, WW, ev, head_muts) + 50
    y = P.band(c, X0, y, f"Every mutation by every property, read from `{res['file'][5:]}`")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, dict(head_muts)) + 50
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated")
    y += P.witnesses_table(c, X0, y, WW, ev, {w: WITNESS_READINGS[w] for w in
                                              [r["prop"] for r in M.witnesses(res)]}) + 50
    y = band_record(c, X0, y, WW, res["rows"], False, "`Lease.tla`",
                    "\"The R3 rerun, the same day, repeated every row again with `RevokedStaysStopped` in `Safe`, which "
                    "holds over 1,746,048 distinct states\" (ADR-0031 §8): the file's `base` row, compared.")

    y = P.band(c, X0, y, "What the frozen module does not have")
    y += P.row_cards(c, X0, y, WW, 30, [
        ("No proof module", ["`Lease.tla` is frozen at its digest, cited by ADR-0031 §8; \"this module is its A1 "
                             "successor and differs from it only where marked A1\" (`Lease_A1.tla`'s header). The "
                             "successor's four invariants are proved and certified (I12)."], "blue", {}),
        ("Rungs 0 to 2", [f"\"{d8}\" (ADR-0034 §7). The successor runs rungs 0 to 3 (A1)."], "amber", {}),
        ("The rung across renewal", ["Here a renewal may lower the rung: the rule as ratified at R3. A1 (ratified in "
                                     "Batch 10) keeps it, and the successor's `M_LOWER` is this module's rule."],
         "amber", {}),
    ], size=13.5) + 50

    y = P.band(c, X0, y, "What a theorem about the module's properties rests on")
    y = P.premises(c, X0, y, WW, ev, PROPS[1:], [],
                   note="The theorems are `Lease_A1_proof.tla`'s; each row's \"Checked in\" names this module.") + 50
    y = P.band(c, X0, y, "Where else `Lease.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, note="ADR-0031 §8 cites the module as `7636c6c3364bca9c`.")
    return c
