"""I7 — `Confinement.tla`, ADR-0034's attested confinement: what an effect counted `Contained` means at each
confinement rung, drawn whole from the module's own text and the two results files ADR-0034 §7 cites. Its proofs are
**not certified**: three obligations failed in the certified run.

Built on modpage.py's bands (family I). The same mutation is run at several rungs (`Declared`), so the results are
drawn as mutation by property by rung; every row's verdict is held as a literal and compared both ways, and ADR-0034
§7's two tables are drawn whole and compared with the files row by row."""
import re

import modules as M
import modpage as P
from lib import Canvas

ID, SLUG = "I7", "confinement"
NAME = "Confinement"
MODULE_FILES = ("spec/Confinement.tla", "spec/Confinement_proof.tla")
W = 3400

REC = "decisions/ADR-0034.md"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "ContainedMeansConfined", "NoSilentDowngrade", "ContestedStopped", "FreshAppraisal"]
WITNESSES = ["NeverContainedEffect", "NeverMediatedEffect", "NeverContested", "NeverRefused", "NeverTamperKilled",
             "NeverRenewed", "NeverLapsed", "NeverRenewContested"]
# every row of the two files: its verdict, as the diagram reads ADR-0034 §7 and A1
EXPECT_ROWS = {
    "safe1": H, "safe2": H, "safe3": H, "wc1": X, "wm1": X, "wx1": H, "wc2": X, "wm2": X, "wx2": X, "wc3": X,
    "wm3": X, "wx3": X, "wr3": X, "wt3": X, "wn1": X, "wrc1": H, "wn2": X, "wrc2": H, "wn3": X, "wrc3": H,
    "wl3": X, "h1": X, "h2": X, "h3": H, "hw3": X, "c2": X, "c3": X, "u1": X, "u3": X, "s3": X, "s3x": H, "d3": X,
    "d3x": H, "p3": X, "rl3": X, "rl3x": H, "rl1": H, "rl2": H,
    "safe0": H, "wc0": H, "wm0": X, "wx0": H, "wn0": X, "wrc0": H, "rl0": H, "u0": H, "h0": H, "hx0": X}
S7_HEAD = ["Check", "Rung", "Mut", "Invariant", "Result"]
ELSEWHERE = ["C4", "G1", "G3", "H3"]
F6_SAYS = "(`hx0` in the 2026.09.30 results, 159 states), which §2 says rung 0 cannot produce"
HX0_READING = ("ADR-0034 finding 6: the module reaches `Contested` at rung 0, \"which §2 says rung 0 cannot "
               "produce\": `Evidence` reads the launch measurement at every rung but 1. Neither §7 table carries the "
               "row. `Confinement_A1.tla` corrects `Evidence`, and there `hx0` holds (I8).")


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def rung(r):
    return int(r["params"]["Declared"])


def s7_compare(rows, used):
    """ADR-0034 §7's rows against the files: rungs ("1, 2, 3", "2 · 3", "**3**"), the mutation, the invariants
    (paired with the rungs where both are split by "·"), and the result; the states in a holds cell, when it gives
    them, compared in order. Records each file row it matches in `used`."""
    def compare(row):
        rung_groups = [re.findall(r"\d", g) for g in re.sub(r"\*", "", row[1]).split("·")]
        muts = re.findall(r"`(\w+)`", row[2]) or [row[2].strip()]
        invs = [re.findall(r"`(\w+)`", g)[0] for g in row[3].split("·")]
        word = H if "holds" in row[4].lower() else X if "counterexample" in row[4].lower() else None
        _need(len(muts) == 1 and word and invs and all(rung_groups), f"§7 row {row[0][:40]!r} does not read")
        pairs = []
        for gi, g in enumerate(rung_groups):
            for d in g:
                for inv in ([invs[gi]] if len(invs) == len(rung_groups) > 1 else invs):
                    pairs.append((int(d), inv))
        hits = []
        for d, inv in pairs:
            h_ = [r for r in rows if rung(r) == d and r["mut"] == muts[0] and r["prop"] == inv]
            _need(len(h_) == 1, f"§7 row {row[0][:40]!r}: {len(h_)} rows at rung {d} for {inv}")
            _need(h_[0]["verdict"] == word, f"§7 row {row[0][:40]!r}: rung {d} {inv} is {h_[0]['verdict']}")
            hits.append(h_[0])
        nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+|\d{4,}", row[4])]
        if nums:
            _need(nums == [h_["states"] for h_ in hits], f"§7 row {row[0][:40]!r}: states {nums} are not the file's")
        used.update(h_["name"] for h_ in hits)
        return "agrees: " + ", ".join(f"`{h_['name']}`" for h_ in hits) + (" (states too)" if nums else "")
    return compare


ROLES = {
    "NoRecs": "The empty records are of their types.", "VerdictValues": "A verdict is one of three.",
    "InitTypeOK": "Typing, at the start.", "NextTypeOK": "Typing is kept.",
    "InitInvC": "`InvC`, the containment invariant, at the start.",
    "TamperKills": "Unless `M_HOST` or `M_HW`, tampering kills the guest.",
    "NextInvC": "`InvC` is kept unless one of the five mutations that break containment.",
    "ContainedMeansConfinedAlways": "ADR-0034 §4, for every behaviour, under those exclusions.",
    "InitInvD": "`InvD`, the rung invariant, at the start.",
    "NextInvD": "`InvD` is kept unless `M_DOWNGRADE` or `M_RENEWLOW`.",
    "NoSilentDowngradeAlways": "ADR-0034 §3 and ADR-0031 A1, unless `M_DOWNGRADE` or `M_RENEWLOW`.",
    "InitInvS": "`InvS` at the start.", "NextInvS": "`InvS` is kept unless `M_CONTESTED`.",
    "ContestedStoppedAlways": "ADR-0034 §3, unless `M_CONTESTED`.",
    "InitInvF": "`InvF` at the start.", "NextInvF": "`InvF` is kept unless `M_STALE`.",
    "FreshAppraisalAlways": "ADR-0034 §3, unless `M_STALE`.",
    "SafeAlways": "All four, unmutated.",
    "MutHostLaunchesRogue": "Why `M_HOST` must fail: the host may launch a rogue image.",
    "MutHwTamperSwaps": "Why `M_HW` must fail: at rung 3 tampering swaps the image.",
    "MutContestedHeld": "Why `M_CONTESTED` must fail: a Contested verdict is held as Attested.",
    "MutUnboundIgnoresGeneration": "Why `M_UNBOUND` must fail: the guest instance is not checked.",
    "MutProfileIgnored": "Why `M_PROFILE` must fail: any profile is counted Contained.",
    "MutDowngradeHolds": "Why `M_DOWNGRADE` must fail: an Unattestable verdict is kept.",
    "UnattestableGrantsRung0": "And is granted at rung 0.",
    "MutRenewLowers": "Why `M_RENEWLOW` must fail: an Unattestable renewal lowers the rung.",
    "MutStaleAccepted": "Why `M_STALE` must fail: any epoch is fresh.",
}


def band_picture(c, X0, y, WW, mod, rung_lines, evidence_words, third_card):
    # ---- the picture
    ap, gr, ct, ac, rn, er = (M.definition(mod, n_)[0] for n_ in ("Appraise", "Grant", "Contained", "Act", "Renew",
                                                                   "EndRound"))
    y = P.band(c, X0, y, "The mechanism, as the module states it: a guest is appraised before it is granted, at the "
                         "declared rung, and every effect is recorded with the image that was really running")
    y = P.flow_picture(
        c, X0, y, WW,
        ("A host, trusted as far as the rung says", ["`Launch`, `Kill` and `Tamper`: the host launches guests and "
                                                      "misbehaves wherever the declared rung does not trust it"],
         "brown"),
        (f"Appraisal, then the grant (`Appraise`, line {ap}; `Grant`, line {gr})", [
            "**①** the evidence: " + evidence_words + " (`Evidence`). `M_HOST` [[red|lets the host launch a rogue image or alter a guest]] where the rung "
            "trusts it; `M_HW` [[red|removes the hardware's protection]] at rung 3.",
            "**②** the verdict: `Attested`, `Unattestable` (rung 3 with the verifier down) or `Contested`, which "
            "revokes the principal (ADR-0034 §3). `M_CONTESTED` [[red|treats it as]] `Attested`.",
            "**③** the grant, at the declared rung, on a fresh epoch and the same guest. `M_STALE` and `M_UNBOUND` "
            "[[red|drop those checks]]; `M_DOWNGRADE` [[red|grants an Unattestable verdict at rung 0]]."], "teal"),
        ("Refused, or revoked", ["`Unattestable`: refused. `Contested`: the principal is revoked."], "red"),
        ("`lease`: one record per principal", "teal", [
            ("A live lease, at the declared rung", ["its rung, profile, epoch and the guest instance it is bound "
                                                    "to (`gen`)"], "teal"),
            (f"Counted Contained (line {ct})", ["live, at rung 1 or above, on the archetype profile. `M_PROFILE` "
                                                "[[red|drops the profile]]."], "green"),
            (f"Renewal (`Renew`, line {rn})", ["re-attests: `Attested` renews at the rung, `Unattestable` lapses, "
                                              "`Contested` revokes. `M_RENEWLOW` [[red|renews at rung 0]]."],
             "teal")]),
        ("The record of effects: `acted`", ["one per admitted effect: whether it was counted `Contained`, and the "
                                            "image really running"], "grey"),
        [("ADR-0034 §4, read on `acted`", ["`ContainedMeansConfined`: an effect counted `Contained` ran the "
                                           "archetype image"], "record"),
         ("ADR-0034 §3, read on `lease`", ["`NoSilentDowngrade`, `ContestedStopped`, `FreshAppraisal`"], "state")],
        {"ask": "launches", "write": "④ a lease", "act": f"⑤ `Act(p)`, line {ac}",
         "end": f"⑥ `EndRound(p)`, line {er}: the lease and the guest end"},
        "**Key.** ① to ③ are the appraisal and the grant; ④ the lease; ⑤ an admitted effect, recorded with what was "
        "really running, so the check compares the claim with the fact (ADR-0034 §7); ⑥ ends the round and the guest. "
        "Red marks where each mutation acts. The picture is the diagram's own drawing of the definitions below.") + 24
    y += P.row_cards(c, X0, y, WW, 30, [
        ("What each rung trusts the host with (the module's header)", rung_lines,
         "brown", {"bullets": False}),
        ("What the module does not model", [
            "**The criterion conjunct**: \"one deployment-wide fact, taken as holding. With it false, `Contained` is "
            "empty and `NeverContainedEffect` holds trivially\" (ADR-0034 §7).",
            "**A running guest altered after launch**: \"rungs 2 and 3 measure what was launched, and neither "
            "detects a running guest being altered\" (the header; ADR-0034 §2, §5)."], "red", {}),
        third_card,
    ], size=13.5) + 50
    return y


def band_machine(c, X0, y, WW, mod, name):
    # ---- the machine
    y = P.band(c, X0, y, "The machine: the host, the verifier, the mechanism's appraisal, grant, effects, renewal "
                         "and fence (`" + name + ".tla`)")
    y = P.machine(c, X0, y, WW, mod, [
        [("Constants and the empty records", ["Principals", "Promoted", "Arch", "NoGuest", "NoPending", "NoLease"],
          [f"`CONSTANTS Mut, Declared, MaxEpoch, MaxIdx, MaxGen` (line {M.line_of(mod, r'^CONSTANTS Mut, Declared')}): "
           f"the mutation, the declared rung and three bounds"], "grey"),
         ("The host launches and kills", ["HostMayLaunchRogue", "Launch", "Kill"], [], "brown"),
         (None, ["Tamper"], [], "brown"),
         ("The verifier, the evidence and the verdict", ["VerifierFlip", "Evidence", "Verdict"], [], "teal")],
        [(None, ["Appraise"], [], "teal"),
         ("A pending appraisal, and the grant's checks", ["Discard", "FreshEpoch", "SameGuest"], [], "teal"),
         (None, ["Grant"], [], "teal"),
         ("Counted `Contained`, and an admitted effect", ["Contained", "Act"], ["ADR-0034 §4: membership."],
          "green")],
        [(None, ["Renew"], ["ADR-0034 §3.6 with ADR-0031 A1."], "teal"),
         ("The round, the fence, and `Next`", ["EndRound", "Fence", "Next", "Spec"], ["No fairness: safety only."],
          "grey")],
    ]) + 50
    return y


def band_mutations(c, X0, y, WW, ev, mod, head_muts):
    # ---- mutations
    y = P.band(c, X0, y, "The mutations: what each does and where it acts")
    mrows = []
    lines = M.text(mod).split("\n")
    for mt, words in head_muts[1:]:
        at = M.code_lines_with(mod, f'"{mt}"')
        lem = [s for s in ev["statements"] if s["kind"] == "LEMMA" and f'Mut = "{mt}"' in (s["assume"] or "")]
        mrows.append([f"`{mt}`", words, "; ".join(f"`{M.enclosing(mod, ln)}`, line {ln}" for ln in at),
                      "; ".join(f"`{s['name']}` (line {s['line']}): `{s['prove']}`" for s in lem) or "—"])
    y += c.table(X0, y, [("Mutation", 210, {}), ("What it does (the module's header)", 1100), ("Where it acts", 700),
                         ("Why it must fail (the proof module's lemma)", WW - 2010)], mrows, size=13.5, accent="red",
                 anchor="mutations") + 50
    return y


def band_matrix(c, X0, y, WW, rows, res, nrows, other_reading, title):
    # ---- the matrix, by rung
    y = P.band(c, X0, y, title)
    muts = ["none"] + M.mutations(res)
    mrows = []
    for mt in muts:
        r_ = [f"`{mt}`"]
        for p in PROPS:
            hits = sorted([r for r in rows if r["mut"] == mt and r["prop"] == p], key=rung)
            r_.append("\n".join(f"rung {rung(h_)}: {P.verdict(h_)}" for h_ in hits) or "[[grey|not run]]")
        mrows.append({"cells": r_, "accent": "grey" if mt == "none" else "red"})
    pw = (WW - 210) / len(PROPS)
    y += c.table(X0, y, [("Mutation", 210, {})] + [(f"`{p}`", pw) for p in PROPS], mrows, size=12.5,
                 anchor="matrix") + 14
    y += c.para(X0, y, WW, f"Every row's verdict is held by the diagram ({nrows} rows) and compared with "
                "the files both ways. \"The `M_HOST` rows are the rung ladder, checked. The same mutation breaks "
                "containment at rungs 1 and 2 and changes nothing at rung 3\" (ADR-0034 §7).", 13.5, "muted") + 24
    other = [r for r in rows if r["mut"] != "none" and r["prop"].startswith("Never")]
    if not other:
        return y - 24 + 50
    y += c.table(X0, y, [("Row", 200, {}), ("Rung", 90), ("Under", 200), ("Property", 330), ("TLC", 520),
                         ("What it shows (the diagram's reading)", WW - 1340)],
                 [[f"`{r['name']}`", str(rung(r)), f"`{r['mut']}`", f"`{r['prop']}`", P.verdict(r),
                   other_reading[r["name"]]] for r in other], size=13.5, accent="amber") + 50
    return y


def band_witnesses(c, X0, y, WW, mod, rows, witnesses, title, readings=None):
    # ---- witnesses, by rung
    y = P.band(c, X0, y, title)
    _readings = {
        "NeverContainedEffect": "A `Contained` principal takes an admitted effect: the ratification witness at rungs "
                                "1 to 3. At rung 0 it **holds**: D-0034-4, \"checked rather than declared\".",
        "NeverMediatedEffect": "A `Mediated` principal acts too: discrimination.",
        "NeverContested": "A rogue launch is detected at rungs 2 and 3. At rungs 0 and 1 it **holds**: \"Rung 1 cannot "
                          "detect one\", \"as §2 says\".",
        "NeverRefused": "An unreachable verifier refuses (rung 3).",
        "NeverTamperKilled": "Tampering becomes the guest's death, a subtraction (rung 3).",
        "NeverRenewed": "A renewal re-attests and keeps the lease.",
        "NeverLapsed": "An unreachable verifier at renewal lets the lease lapse (rung 3).",
        "NeverRenewContested": "**Holds** at every rung: a renewal never turns `Contested` (§7 finding 5).",
    }
    readings = readings or _readings
    ws = [r for r in rows if r["mut"] == "none" and r["prop"].startswith("Never")]
    _need(sorted({r["prop"] for r in ws}) == sorted(witnesses), "the witnesses are not the diagram's")
    wrows = []
    for w in witnesses:
        ln, src = M.definition(mod, w)
        cells = [f"`{w}`", " ".join(P.code_lines(src))]
        for d in range(4):
            h_ = [r for r in ws if r["prop"] == w and rung(r) == d]
            cells.append(P.verdict(h_[0]) if h_ else "[[grey|not run]]")
        cells.append(readings[w])
        wrows.append(cells)
    y += c.table(X0, y, [("Witness", 260, {}), ("Its definition", 460)] + [(f"Rung {d}", 330) for d in range(4)] +
                 [("What it shows (the diagram's reading)", WW - 2040)], wrows, size=12.5, anchor="witnesses") + 50
    return y


def band_proofs(c, X0, y, WW, ev, other_card):
    # ---- the proofs
    prf = ev["files"]["proof"]
    ce = ev["cert"]
    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, the run that proved it, and the certified run "
                         f"that refused it")
    y = P.proofs(c, X0, y, WW, ev, ROLES, assumptions_note="the declared rung is 0 to 3") + 24
    fails = [r for r in ce["routes"] if r[0].startswith("failed")]
    y += P.row_cards(c, X0, y, WW, 30, [
        ("[[red|Proved, and not certified]]", [
            f"The proof run: \"All {ev['proof']['obligations']} obligations proved.\"",
            f"The certified run: {fails[0][1]} obligations failed, last backend tried Isabelle; its last line: "
            f"\"{ce['last']}\" The file names no obligation by number.",
            "One of the three modules that do not certify; restructuring them is deferred by the custodian (G10 item "
            "74). **Proved is not certified.**"], "red", {}),
        other_card,
    ], size=13.5) + 50
    return y


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    rows = res["rows"]
    got = {r["name"]: r["verdict"] for r in rows}
    _need(got == EXPECT_ROWS, f"the files' rows are not the diagram's: "
                              f"{sorted(set(got.items()) ^ set(EXPECT_ROWS.items()))[:6]}")
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts][1:] == M.mutations(res), "the header's mutations are not the files'")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == PROPS[1:], "the header's properties")
    _need(ev["proof"]["assumptions"] == "DeclaredRung == Declared \\in 0..3", "the proof's assumption")
    ce = ev["cert"]
    _need(not ce["certified"] and ce["last"] == "NOT CERTIFIED: 3 obligation(s) failed (last backend tried: isabelle).",
          f"the certified run's last line is {ce['last']!r}")
    rec = M.text(REC)
    _need("digest `d0dcf21ce9774885`" in rec and M.sha16(mod) == "d0dcf21ce9774885", "ADR-0034 §7's digest")
    _need(F6_SAYS in re.sub(r"\s+", " ", rec) and [r["states"] for r in rows if r["name"] == "hx0"] == [159],
          "ADR-0034 finding 6 no longer says what the diagram reads of hx0")
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
    _need(len(rung_lines) == 3, f"the header's rung table has {len(rung_lines)} entries")
    used = set()

    c = Canvas(ID,
               "`Confinement.tla`: an effect counted `Contained` ran inside the archetype profile, at every rung a "
               "deployment may declare, and what each rung trusts the host with. Four invariants: checked by TLC at "
               "rungs 0 to 3, proved by TLAPS and in Lean, and **not certified**",
               "The module ADR-0034 §7 reports, drawn from its own text and the two results files that section "
               "cites, all read at build time: the host and the mechanism, the four properties and the section each "
               "states, every mutation by every property at every rung, the witnesses by rung, ADR-0034 §7's two "
               "tables compared row by row, every theorem and lemma, the proof run and the certified run that "
               "refused it, and the Lean re-encoding. **What is checked or proved here is of the module, at its "
               "constants or by its proofs, and not of the reference; the criterion conjunct is not modelled** "
               "(ADR-0034 §7). **The proofs are proved and not certified.** The module is frozen, cited by digest "
               "(ADR-0034 §7); its successor, carrying finding 6, is `Confinement_A1.tla` (I8).",
               W,
               f"spec/Confinement.tla (its header, every definition); spec/Confinement_proof.tla (every THEOREM and "
               f"LEMMA); {res['file']}; {ev['files']['proof_results']}; {ev['files']['cert']}; {M.LEAN_RESULTS} "
               f"(compared with {M.LEAN_LATER[10:]}); spec/lean/TopakSpec/Confinement.lean; {P.PREMISES} (the four "
               f"rows and invariant(Confinement)); ADR-0034 §2–§4, §7 (both tables and their notes), A1; G10 item 74. "
               f"Every file read at the pin its links open, and checked equal to the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0034", "accepted", "C2, C4")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    y = band_picture(c, X0, y, WW, mod, rung_lines, "at rung 1 the profile the launcher was asked for, else the "
                     "launch measurement", ("What it is and is not", [
                         "\"This is a separate module. It does not refine `Lease.tla`, and it shares that module's "
                         "rung-0 rule by construction\" (ADR-0034 §7).", "Rung 0 is in the second file (2026.09.30, "
                         "A1): D-0034-4's deployment, every principal `Mediated`."], "grey", {}))

    y = band_machine(c, X0, y, WW, mod, NAME)

    # ---- the properties
    y = P.band(c, X0, y, "The four properties, the section of ADR-0034 each states, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, f"ADR-0034 {s}", w) for p, s, w in hp],
                     key=lambda r: f"{r['mut']} at rung {rung(r)}") + 14
    y += c.para(X0, y, WW, "\"Two clauses are about honest declaration, not containment\": under `M_STALE`, "
                "`M_DOWNGRADE` and `M_RENEWLOW` `ContainedMeansConfined` still holds, and what fails is the "
                "deployment's claim about itself (ADR-0034 §7). Each theorem excludes every mutation that breaks its "
                "property at some rung, so `ContainedMeansConfinedAlways` excludes `M_HOST` though it changes nothing "
                "at rung 3 (the diagram's reading).", 13.5, "muted") + 50

    y = band_mutations(c, X0, y, WW, ev, mod, head_muts)

    y = band_matrix(c, X0, y, WW, rows, res, len(EXPECT_ROWS), {"hx0": HX0_READING},
                    "Every mutation by every property, at every rung it is run, read from the two files")

    y = band_witnesses(c, X0, y, WW, mod, rows, WITNESSES,
                       "Witnesses, by rung: most must be violated, and three hold where the record says they do")

    # ---- the record's tables
    y = P.band(c, X0, y, "ADR-0034 §7's two tables, every row and column, each compared with the files")
    t7 = P.md_table(REC, S7_HEAD, occurrence=0)
    ta1 = P.md_table(REC, S7_HEAD, occurrence=1)
    cmp_ = s7_compare(rows, used)
    for title, tab in (("§7, the run of 2026.09.28 (rungs 1 to 3)", t7), ("§7 A1, the run of 2026.09.30 (rung 0)", ta1)):
        c.text(X0, y + 16, title, 16, "blue", bold=True)
        y += 30
        y += c.table(X0, y, [(h_, w_) for h_, w_ in zip(S7_HEAD, (560, 140, 200, 520, 560))] +
                     [("Against the files (compared at build time)", WW - 1980)],
                     [[P.strike(x_) for x_ in r] + [cmp_(r)] for r in tab], size=13, accent="blue") + 24
    left = sorted(set(EXPECT_ROWS) - used)
    y += c.para(X0, y, WW, f"Of the files' {len(EXPECT_ROWS)} rows, {len(used)} are matched by a row of the two tables. "
                f"Not in either: {', '.join(f'`{n_}`' for n_ in left)}. A1 carries \"only the three [rung-0 mutation "
                f"rows] whose result the discrepancy does not affect\", so `hx0` is the file's and not the record's.",
                13.5, "muted") + 50

    y = band_proofs(c, X0, y, WW, ev, ("The successor", ["`Confinement_A1.tla` (I8) carries finding 6, and fails "
                                                       "to certify in the same way."], "grey", {}))

    # ---- Lean
    y = P.band(c, X0, y, "In Lean: the module re-encoded and its theorems proved again")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.Confinement",
               extra_card="\"`Confinement.lean` covers `Confinement.tla` and `Confinement_A1.tla` under one flag\" "
                          "(the results file). The Lean proofs are a second proof, of the re-encoding, and not a "
                          "certification of the TLAPS ones.") + 50

    # ---- premises
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, PROPS[1:], ["invariant(Confinement)"]) + 50

    # ---- where else
    y = P.band(c, X0, y, "Where else `Confinement.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50

    # ---- digests
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, note="ADR-0034 §7 cites the module as `d0dcf21ce9774885`.")
    return c
