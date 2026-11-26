"""I12 — `Lease_A1.tla`, the successor to `Lease.tla` that carries ADR-0031 A1: a renewal keeps the confinement rung,
and rungs run 0 to 3. Drawn whole from the module's own text and every results file about it: checked by TLC, proved
and certified by TLAPS, and proved in Lean.

Built on I11's bands (d_i11_lease), which draw the same machine; what A1 changes is drawn as such, every definition
compared with the frozen module's."""
import re

import modules as M
import modpage as P
from lib import Canvas
from d_i11_lease import WITNESS_READINGS, band_machine, band_picture, band_record

ID, SLUG = "I12", "lease-a1"
NAME = "Lease_A1"
MODULE_FILES = ("spec/Lease_A1.tla", "spec/Lease_A1_proof.tla")
W = 3400

REC = "decisions/ADR-0031.md"
PRED = "spec/Lease.tla"
H, X = "HOLDS", "COUNTEREXAMPLE"
PROPS = ["Safe", "LeaseAuthorityMonotone", "NoActionUnderFencedEpoch", "Rung0NeverContained", "RevokedStaysStopped"]
EXPECT = {("none", "Safe"): H, ("M_RENEW", "LeaseAuthorityMonotone"): X, ("M_FENCE", "NoActionUnderFencedEpoch"): X,
          ("M_RUNG", "Rung0NeverContained"): X, ("M_ROLE", "LeaseAuthorityMonotone"): X,
          ("M_REVOKE", "RevokedStaysStopped"): X, ("M_LOWER", "LeaseAuthorityMonotone"): X}
A1_SAYS = "at rungs 0–3; `Safe` holds over 2,136,720 distinct states. `M_LOWER` grants at rung 1 and renews at rung 0"
ELSEWHERE = ["C3", "G3", "H3", "H5"]


def _need(cond, what):
    if not cond:
        raise M.CorpusError(f"{ID}: {what}")


def code_only(src):
    src = re.sub(r"\(\*.*?\*\)", " ", src, flags=re.S)
    src = re.sub(r"\\\*[^\n]*", " ", src)
    return re.sub(r"\s+", " ", src).strip()


def build():
    ev = M.evidence(NAME)
    mod, prf = ev["files"]["module"], ev["files"]["proof"]
    res = ev["tlc"]
    head_muts = M.header_mutations(mod)
    _need([m for m, _ in head_muts] == ["none"] + M.mutations(res), "the header's mutations are not the file's")
    hp = M.header_properties(mod)
    _need([p for p, _, _ in hp] == ["LeaseAuthorityMonotone", "NoActionUnderFencedEpoch", "RevokedStaysStopped",
                                    "Rung0NeverContained"], "the header's properties")
    rec = re.sub(r"\s+", " ", M.text(REC))
    base = [r for r in res["rows"] if r["name"] == "base"][0]
    _need(A1_SAYS in rec and base["states"] == 2136720, "ADR-0031 §8's A1 sentence, or the file's base row")
    _need("`spec/Lease_A1.tla` · digest `0b5eac7a7309be2f`" in rec, "ADR-0031 §8's digest of the module")
    _need("**A1 ratified 2026.09.28** by the genesis custodian" in rec, "ADR-0031 B10")
    _need(M.header_comment(mod)[0].strip().startswith("Properties for ADR-0031, the lease schema, as amended by A1 "
                                                     "(pending)."), "the header's first line")
    # what A1 changed: every definition of the two modules, comments aside
    mt, pt = M.text(mod), M.text(PRED)
    dn = lambda t: re.findall(r"^([A-Za-z_]\w*)\s*(?:\([^)]*\))?\s*==", t, re.M)  # noqa: E731
    a_defs, p_defs = dn(mt), dn(pt)
    added = [n_ for n_ in a_defs if n_ not in p_defs]
    _need(not [n_ for n_ in p_defs if n_ not in a_defs], "a definition of the frozen module is gone")
    changed = [n_ for n_ in a_defs if n_ in p_defs and code_only(M.definition(mod, n_)[1]) !=
               code_only(M.definition(PRED, n_)[1])]
    _need(changed == ["Rungs", "Narrows", "Refines", "RenewalAllowed"] and added == ["LowerOrSame",
                                                                                     "NeverRenewedAbove0"],
          f"A1 changed {changed} and added {added}")
    shared = {(r["mut"], r["prop"]): r for r in M.evidence("Lease")["tlc"]["rows"]}
    same = [r for r in res["rows"] if (r["mut"], r["prop"]) in shared]
    _need(all(shared[(r["mut"], r["prop"])]["verdict"] == r["verdict"] for r in same),
          "a check both runs share has another verdict: \"repeated every row with its result unchanged\"")
    new = [r for r in res["rows"] if (r["mut"], r["prop"]) not in shared]
    _need(sorted(r["name"] for r in new) == ["mut-lower", "reach-renew-above0"], "the A1 rows")

    c = Canvas(ID,
               "`Lease_A1.tla`: the lease schema as amended by A1. A renewal keeps the confinement rung, so a principal "
               "never leaves `Contained` silently. Four invariants, each broken by its mutation: checked by TLC at "
               "rungs 0 to 3, proved and certified by TLAPS, and proved in Lean",
               "The successor to `Lease.tla` (I11), drawn from its own text and every results file about it, all read "
               "at build time: what A1 changed, every definition compared with the frozen module's; the mechanism; the "
               "four properties; the mutation matrix, with A1's `M_LOWER`; the witnesses, with A1's rung-1 renewal; "
               "ADR-0031 §8's table compared row by row; every theorem and lemma, the certified run and the Lean "
               "re-encoding. **What is checked or proved here is of the module, not of the reference.** A1 was "
               "ratified on 2026.09.28 in Batch 10; the module's header, written before, calls it pending.",
               W,
               f"spec/Lease_A1.tla (its header, every definition); spec/Lease.tla (every definition, for the comparison); "
               f"spec/Lease_A1_proof.tla (every THEOREM and LEMMA); {res['file']}; "
               f"{M.MODULES['Lease']['tlc']} (the checks both run); {ev['files']['proof_results']}; "
               f"{ev['files']['cert']}; {M.LEAN_RESULTS} (compared with {M.LEAN_LATER[10:]}); "
               f"spec/lean/TopakSpec/Lease_A1.lean; {P.PREMISES} (the four rows and invariant(Lease_A1)); ADR-0031 "
               f"§2–§5, §8, A1, B10; ADR-0034 §3.4. Every file read at the pin its links open, and checked equal to "
               f"the tree",
               state=P.STATE)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y
    y = P.status_strip(c, X0, X1, y, P.status_items(ev, [("ADR-0031", "accepted", "C1; C2 for A1")]))
    y += c.para(X0, y, WW, P.WORDS, 14.5, "muted") + 34

    # ---- what A1 changed
    y = P.band(c, X0, y, "What A1 changed: four definitions, two added, every other one the same as the frozen module's")
    specs = []
    for n_ in changed:
        lp, sp = M.definition(PRED, n_)
        la, sa = M.definition(mod, n_)
        specs.append((f"`{n_}` · `Lease.tla` line {lp} · `Lease_A1.tla` line {la}",
                      ["**Frozen:**"] + P.code_lines(sp) + ["**A1:**"] + P.code_lines(sa), "amber", {"bullets": False}))
    y += P.row_cards(c, X0, y, WW, 30, specs, size=13) + 24
    hc = [ln.strip() for ln in M.header_comment(mod)[:9] if ln.strip()]
    y += P.row_cards(c, X0, y, WW, 30, [
        ("Added", [f"`{n_}` (line {M.definition(mod, n_)[0]}): " + " ".join(P.code_lines(M.definition(mod, n_)[1]))
                   for n_ in added], "teal", {}),
        ("Why (the module's header)", [" ".join(hc[1:])], "grey", {}),
        ("What did not move", [f"Every other definition is the same, comments aside, and every check both runs share "
                               f"has the same verdict ({len(same)} rows): ADR-0031 §8's \"repeated every row with its "
                               f"result unchanged\". The A1 rows are `mut-lower` and `reach-renew-above0`."],
         "teal", {}),
    ], size=13.5) + 50

    y = band_picture(c, X0, y, WW, mod, a1=True)
    y = band_machine(c, X0, y, WW, mod, NAME, a1=True)

    y = P.band(c, X0, y, "The four properties, the section of ADR-0031 each states, and how each is shown")
    y = P.properties(c, X0, y, WW, ev, [(p, f"ADR-0031 {s}" + (", A1" if p == "LeaseAuthorityMonotone" else ""), w)
                                        for p, s, w in hp]) + 50
    y = P.band(c, X0, y, "The mutations: what each does, where it acts, and what it must break")
    y = P.mutations(c, X0, y, WW, ev, head_muts) + 50
    y = P.band(c, X0, y, f"Every mutation by every property, read from `{res['file'][5:]}`")
    y += P.matrix_table(c, X0, y, WW, ev, PROPS, EXPECT, dict(head_muts)) + 50
    y = P.band(c, X0, y, "Witnesses: each `Never…` property must be violated unmutated")
    y += P.witnesses_table(c, X0, y, WW, ev, {w: WITNESS_READINGS[w] for w in
                                              [r["prop"] for r in M.witnesses(res)]}) + 50
    y = band_record(c, X0, y, WW, res["rows"], True, "`Lease_A1.tla`",
                    "\"The A1 run (2026.09.28) repeated every row with its result unchanged, at rungs 0–3; `Safe` holds "
                    "over 2,136,720 distinct states\" (ADR-0031 §8): the file's `base` row, compared.")

    y = P.band(c, X0, y, f"The proofs: every statement of `{prf[5:]}`, and the run that discharged it")
    y = P.proofs(c, X0, y, WW, ev, {
        "NoLeaseRec": "The empty lease is a lease record.", "InitTypeOK": "Typing, at the start.",
        "NextTypeOK": "Typing is kept, under every mutation.",
        "RenewRefines": "Unless `M_RENEW`, `M_ROLE` or `M_LOWER`, an allowed renewal refines.",
        "NextMonotone": "`LeaseAuthorityMonotone` is kept under those exclusions.",
        "LeaseAuthorityMonotoneAlways": "ADR-0031 §4 and A1, for every behaviour, unless `M_RENEW`, `M_ROLE` or "
                                        "`M_LOWER`.",
        "NextFenced": "`NoActionUnderFencedEpoch` is kept unless `M_FENCE`.",
        "NoActionUnderFencedEpochAlways": "ADR-0031 §5, unless `M_FENCE`.",
        "Rung0Valid": "Unless `M_RUNG`, a rung-0 lease is never `Contained`, in every state.",
        "Rung0NeverContainedAlways": "ADR-0031 §3, unless `M_RUNG`.",
        "NextRevoked": "`RevokedStaysStopped` is kept unless `M_REVOKE`.",
        "RevokedStaysStoppedAlways": "ADR-0031 §5 R3, unless `M_REVOKE`.",
        "SafeAlways": "All four, unmutated.",
        "MutRenewAllowsAll": "Why `M_RENEW` must fail: any renewal is allowed.",
        "MutRoleIgnored": "Why `M_ROLE` must fail: a renewal that changes the role is allowed.",
        "MutLowerAccepted": "Why `M_LOWER` must fail: a renewal that lowers the rung is allowed.",
        "MutFenceIgnoresEpoch": "Why `M_FENCE` must fail: any epoch is current.",
        "MutRungContainsAll": "Why `M_RUNG` must fail: every live lease is `Contained`.",
        "MutRevokeGrantsAgain": "Why `M_REVOKE` must fail: a revoked principal can be granted again.",
    }) + 50

    y = P.band(c, X0, y, "In Lean: the module re-encoded and its theorems proved again")
    y = P.lean(c, X0, y, WW, ev, "Topak.Spec.Lease_A1") + 50
    y = P.band(c, X0, y, "What a theorem about the module rests on")
    y = P.premises(c, X0, y, WW, ev, PROPS[1:], ["invariant(Lease_A1)"]) + 50
    y = P.band(c, X0, y, "Where else `Lease_A1.tla` is drawn")
    y = P.elsewhere(c, X0, y, WW, ev, ELSEWHERE) + 50
    y = P.band(c, X0, y, "The digests: every file drawn whose digest is cited, and every place that cites it")
    P.digests(c, X0, y, WW, ev, note="ADR-0031 §8 cites the module as `0b5eac7a7309be2f`.")
    return c
