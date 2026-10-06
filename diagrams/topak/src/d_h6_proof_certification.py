"""H6 — A certified proof: every obligation of a proof module accounted for by the route that closed it (ADR-0046 E2,
A1; spec/proof-certification.md). The per-module table is read from the certified results files themselves, and the
two trusted-base rows from ADR-0045, so neither can drift from the record."""
import hashlib
import pathlib
import re

from lib import Canvas, strip_external

ID, SLUG = "H6", "proof-certification"

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "spec" / "proof-certification.md").exists()), _HERE.parents[3])
SPEC = ROOT / "spec"
ADR45 = ROOT / "decisions" / "ADR-0045.md"

# Which record each proof module answers to, and its status at G10 (G10 §1.1, §3; spec/README.md). Grouped as
# ADR-0046 A1 groups them: its thirteen; the three its note names; and the six certified after it was drafted.
GROUPS = [
    ("ADR-0046 §4's thirteen, each cited by digest; A1 lists eleven as certified and two as not (Batch 28, "
     "2026.10.04)", "blue", [
        ("Anchor", "ADR-0029 §5, bootstrap module 2 of 5"),
        ("BreakGlass", "ADR-0029 §5; ADR-0026 R7 · frozen, succeeded by `BreakGlass_A1` where it models X1"),
        ("FloorRouting", "ADR-0030 §9"),
        ("FloorComposition", "ADR-0030 §1, §4, §5"),
        ("Seats", "ADR-0037 §9"),
        ("Observers", "ADR-0038 §8"),
        ("RunSeats", "ADR-0043 §8"),
        ("Lease_A1", "ADR-0031 A1"),
        ("NonComposition", "ADR-0013 §4 · frozen, succeeded by `NonComposition_A1`"),
        ("Coupling", "ADR-0039 §8"),
        ("RunCoupling", "ADR-0042 §8"),
        ("RulesFloorNV_rev5", "ADR-0026 R1; ADR-0024 rev 5"),
        ("Confinement", "ADR-0034 §7, A1 · frozen, succeeded by `Confinement_A1`"),
    ]),
    ("Outside the thirteen, named in A1's own note: two certify and one does not", "teal", [
        ("RunConfinement", "ADR-0034 A2 (Batch 30), condition (ii)"),
        ("Operators", "ADR-0050 §10 · [[blue|provisional]]"),
        ("Confinement_A1", "ADR-0034 finding 6's successor; ADR-0033 A7 (Batch 29)"),
    ]),
    ("Certified after A1 was drafted: four on 2026.10.04, two on 2026.10.05 (spec/README.md; G10 §2.9, §3)",
     "green", [
        ("Labels", "ADR-0047 §11"),
        ("ToolList", "ADR-0048 §8"),
        ("Emergency", "ADR-0052 §9 · [[blue|provisional]]"),
        ("Correlator", "ADR-0051 §10 · [[amber|Proposed]]; not among G10 §3's frozen six"),
        ("BreakGlass_A1", "ADR-0052 R5; ADR-0026 A2; ADR-0029 §5"),
        ("NonComposition_A1", "ADR-0052 R5; ADR-0013 A1"),
    ]),
]


def _num(pat, t):
    m = re.search(pat, t)
    return int(m.group(1)) if m else 0


def read_cert(mod):
    """-> dict of one module's certified results file, as printed (spec/proof-certification.md §5)."""
    f = sorted(SPEC.glob(f"{mod}-proof-cert-results-*.txt"))[-1]
    raw = f.read_bytes()
    t = raw.decode("utf-8")
    last = [ln for ln in t.strip().splitlines() if ln.startswith("All ") or ln.startswith("NOT CERTIFIED")][-1]
    zen_note = re.search(r"Zenon, proof checked by Isabelle\s+\d+\s+\((.+?)\)", t)
    return {
        "file": f.name, "digest": hashlib.sha256(raw).hexdigest()[:16],
        "n": _num(r"Obligations: (\d+)", t),
        "triv": _num(r"trivial, closed by tlapm with no backend\s+(\d+)", t),
        "smt": _num(r"SMT, proof accepted by ethos\s+(\d+)", t),
        "zen": _num(r"Zenon, proof checked by Isabelle\s+(\d+)", t),
        "zen_note": zen_note.group(1) if zen_note else "",
        "isa": _num(r"\n  Isabelle\s+(\d+)", t),
        "ls4": _num(r"LS4, temporal step, NOT certified\s+(\d+)", t),
        "fail": _num(r"failed / \w+: (\d+)", t),
        "stretch": re.search(r"Backend timeouts (x\d+)", t).group(1),
        "evidence": re.search(r"evidence digest ([0-9a-f]+)", t).group(1),
        "certified": last.startswith("All "),
        "last": last,
    }


def _row45(text, rid, annex):
    """The T-0045-nn row of Annex A or Annex B, as cells, with struck text dropped and batch marks kept."""
    part = text.split("## Annex A")[1].split("## Annex B")[0] if annex == "A" else \
        text.split("## Annex B")[1].split("## History")[0]
    for line in part.splitlines():
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if line.startswith("|") and re.sub(r"[*]", "", cells[0]) == rid:
            return [_clean(x) for x in cells]
    raise KeyError(rid)


def _clean(s):
    s = re.sub(r"~~(.+?)~~\s*", "", s)
    s = re.sub(r"⟨(B\d+|A\d+)⟩", r"(\1)", s)
    # a bold span holding code cannot nest in lib's markup: keep the code and drop the bold there
    s = re.sub(r"\*\*([^*]*`[^*]*)\*\*", r"\1", s)
    s = re.sub(r"(?<![*\w])\*(?!\*)([^*]+?)(?<!\*)\*(?![*\w])", r"\1", s)
    return s.strip()


def build():
    c = Canvas(ID, "A certified proof: every obligation accounted for by the route that closed it",
               "\"All N obligations proved\" is the word of whichever backend discharged each obligation. A **certified** "
               "run (ADR-0046 A1, Batch 28) takes the same proof again and does not take that word: Z3 is not run, cvc5 "
               "stands behind `spec/smt-checked` and an SMT obligation counts only with a proof of false that the `ethos` "
               "checker accepted; every Zenon proof is re-checked by Isabelle; and `spec/proof-cert.sh` puts every "
               "obligation on exactly one route. **Nineteen of the twenty-two proof modules certify; three do not** "
               "(G10 §2.9). Three words, kept apart (ADR-0046 §1, A1): TLC **checks** mutations and witnesses; the prover "
               "**proves** invariants under named hypotheses; a proof is **certified** when every obligation is closed "
               "by the prover's normalization, by a checked proof, or by LS4. **A certified proof is not a verified one** "
               "(G10 §8), and none of it is a claim about the running reference (T-0045-28). **Beside it, proposed**: twelve of "
               "these modules' theorems proved again in Lean, of re-encodings, with the temporal step a kernel-checked "
               "induction and no SMT solver; the three that do not certify among them (ADR-0053; H7).",
               3200,
               "spec/proof-certification.md §1–§12 (DRAFT, 2026.10.04; 61346a4237a85c94); spec/proof-cert.sh "
               "(315fa3d07b7a42de); spec/smt-checked (bb86642633822ae5); spec/smt-checked-selftest.sh; the twenty-two "
               "spec/*-proof-cert-results-2026.10.04.txt and -2026.10.05.txt files, read at build time; "
               "spec/proof-method.md §5a; spec/README.md (TLAPS proofs, certified runs); ADR-0046 §1, §3 with A1, "
               "open obligations, E2, A1, B28; ADR-0045 Annex A and Annex B rows T-0045-14 and T-0045-31 (read at "
               "build time), B24, B25, B28; ADR-0053 (Proposed) §2, §5 and spec/lean/TopakSpec-results-2026.10.05.txt; "
               "proof-certification.md §8, §12 as amended 2026.10.05; ADR-0030 §5 A1 and floor/cvc5-checked; G10 §1 (Batch 28), §2.6, §2.9, "
               "§3 (results 9; \"What these checks are\"), §5, §7 items 73, 74, §8; ToO rev 14 §7.9, §11.3")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y
    from d_h7_lean_route import ENC  # ADR-0053 (Proposed): the proof modules spec/lean re-encodes
    in_lean = {m for m, _ in ENC}

    # ---- status band
    sx = X0
    sx += c.status(sx, y, "accepted", "C2, C4 · ADR-0046 E2 and A1, Batch 28, 2026.10.04") + 14
    c.text(sx, y + 16, "The method is adopted by **ADR-0046 A1**; `spec/proof-certification.md`, which describes it, is "
                       "itself a draft and not a record. Its wrapper, driver, method and every result are the drafter's, "
                       "regenerated at ratification by the assistant at the custodian's direction (B28).", 14.5, "muted")
    y += 52

    # ================================================================ 1 · why
    y += c.heading(X0, y, "1 · Why a second run: whose word is \"All N obligations proved\"?", size=22)
    y += 4
    lw = W * 0.5
    rw = W - lw - 40
    h1 = c.table(X0, y, [("Backend, in an ordinary run (`proof-results.sh`)", lw * 0.3),
                         ("What it returns", lw * 0.36), ("Who checks the answer", lw * 0.34)], [
        ["tlapm itself", "\"trivial\": the obligation is closed by normalization, with no backend", "[[red|Nobody]]"],
        ["Z3 4.8.9, the default SMT solver", "`unsat`", "[[red|Nobody]]. Z3 4.8.9 emits no proof the prover reads"],
        ["Zenon 0.8.4", "A proof script in Isabelle's language", "[[red|Nobody]], unless asked (`-C`)"],
        ["Isabelle2025", "A proof, checked by Isabelle's kernel as it is made", "Isabelle"],
        ["LS4", "`unsat`, for a step of temporal logic", "[[red|Nobody]]"],
    ], size=14, accent="grey")
    h1 += 10
    h1 += c.para(X0, y + h1, lw, "The prover stops at the first backend that answers. In the sixteen proof modules of "
                 "2026.10.04 about a third of all obligations were SMT's, \"so a third of every 'proved' was Z3's "
                 "unsupported word\" (proof-certification.md §1).", 14, "muted")
    e2 = [
        "ADR-0046 as ratified at B25 said `tlapm` \"can hand every SMT-proved obligation to Isabelle for checking "
        "(`-C`)\". **It cannot.** `-C` checks the scripts Zenon emits and nothing else. For a module whose obligations "
        "are all SMT's it hands Isabelle a theory with no lemmas, and Isabelle reports \"No errors found\": true, and "
        "says nothing.",
        "Seen by reading the generated theory for `RunConfinement_proof`: fourteen lines, no lemma. Run over every "
        "proof module on 2026.10.04 (proof-method.md §5a: thirteen of sixteen were in that position or close to it).",
        "**E2 corrects the sentence** and says `-C` does not move T-0045-31's residual. A checked SMT route does: A1. "
        "G10 lists it among the results the drafting did not anticipate (§3, result 9); the sentence was the "
        "drafter's and was not checked before B25.",
    ]
    he = c.card(X0 + lw + 40, y, rw, "`tlapm -C` checks Zenon's proofs, and nothing else (ADR-0046 E2)", e2,
                accent="red", status="accepted", status_extra="erratum E2 · Batch 28", size=14.5)
    y += max(h1, he) + 56

    # ================================================================ 2 · the routes
    y += c.heading(X0, y, "2 · The certified run: every obligation on exactly one route (proof-certification.md §2, §4)",
                   size=22)
    y += c.para(X0, y, W, "`spec/proof-cert.sh <Module>_proof > <Module>-proof-cert-results-<date>.txt` runs "
                "`tlapm -C --cleanfp --strict --toolbox 0 0 --solver '<smt-checked> \"$file\"'`, then reads the "
                "prover's per-obligation messages, which name the backend that discharged each one, and the wrapper's "
                "verdicts. **A module is certified when every obligation is on one of the first five rows.** The counts "
                "are the sums over the twenty-two certified results files (§3 below).", 15, "muted") + 18

    cert = {m: read_cert(m) for _, _, mods in GROUPS for m, _ in mods}
    tot = {k: sum(r[k] for r in cert.values()) for k in ("n", "triv", "smt", "zen", "isa", "ls4", "fail")}
    zen_refused = sum(int(re.search(r"REJECTED (\d+)", r["zen_note"]).group(1))
                      for r in cert.values() if "REJECTED" in r["zen_note"])

    LWc, RTc, CKc, CNc, RSc = 430, 720, 640, 520, W - 430 - 720 - 640 - 520 - 4 * 70
    xs = [X0]
    for w_ in (LWc, RTc, CKc, CNc):
        xs.append(xs[-1] + w_ + 70)
    routes = [
        ("Trivial: closed by tlapm's own normalization, with no backend", "grey", None,
         ["About two obligations in three. Nothing is sent anywhere: the prover's front end closes it."],
         "Nothing beyond tlapm", ["Trusted as written: tlapm's normalization is a premise (§8)."], "grey",
         f"**Counts.** On trust in tlapm.\n**{tot['triv']:,}** of {tot['n']:,}", "grey"),
        ("SMT: cvc5 1.4.0 behind `spec/smt-checked`", "teal", None,
         ["The prover writes one SMT-LIB query per obligation it sends to SMT and runs the configured solver on it. "
          "The wrapper forwards `unsat` only on a proof the checker accepted; otherwise `unknown`, and the obligation "
          "passes on to Zenon and then Isabelle."],
         "`ethos` 8dc85c4, against the CPC signature in `tools/cpc/`",
         ["The floor's checker (T-0045-14), with a wrapper of its own binding the proof to the prover's query, as "
          "`floor/cvc5-checked` binds one to `cedar symcc`'s (ADR-0030 §5 A1)."], "teal",
         f"**Counts.** A proof of false from the query's own declarations and assertions.\n**{tot['smt']:,}**", "teal"),
        ("Zenon, its script checked by Isabelle (`-C`)", "teal", None,
         ["What no SMT answer closed goes on to Zenon. `Operators_proof` has two `ENABLED` goals there that "
          "Isabelle accepted; `RulesFloorNV_rev5_proof` has five, the cases of `BaseNext`, under Z3 as under cvc5, "
          "and Isabelle refuses one."],
         "Isabelle2025 reconstructs the script", ["A script Isabelle refuses, or cannot check, is not a checked "
                                                   "proof: the module does not certify."], "teal",
         f"**Counts** when Isabelle confirms it.\n**{tot['zen']}**: {tot['zen'] - zen_refused} accepted, "
         f"[[red|{zen_refused} refused]]", "teal"),
        ("Isabelle, directly", "teal", None, ["The prover's last backend, tried after SMT and Zenon."],
         "Isabelle's kernel, as the proof is made", ["Isabelle is still trusted, for its own proofs and for "
                                                     "checking Zenon's (§8)."], "teal",
         f"**Counts.**\n**{tot['isa']}**", "teal"),
        ("LS4: the temporal step of each theorem", "grey", "6 4",
         ["One to three per theorem, of one fixed shape: \"the invariant holds initially and every step keeps it, so "
          "it holds always\" (`PTL`)."],
         "[[red|Nothing.]] No route checks a temporal step", ["Reported separately in every results file's last "
                                                              "sentence: \"N rest on LS4, whose answer no checker "
                                                              "confirms\"."], "red",
         f"**Counts**, and is reported as **not certified**.\n**{tot['ls4']}**", "grey"),
        ("Anything else: failed under the checked backends, an SMT answer with no accepted proof, a Zenon proof "
         "Isabelle refused or could not check", "red", "6 4",
         ["`unknown` from the wrapper reads as \"this backend did not prove it\". An obligation no checked route "
          "closes is a missing check, **not a counterexample**."],
         "—", ["The run is refused as a whole: `proof-cert.sh` exits non-zero and the file ends `NOT CERTIFIED: "
               "<reason>`."], "red",
         f"[[red|The module is not certified.]]\n**{tot['fail']}** failed, in two modules; and the "
         f"{zen_refused} refused Zenon proof above", "red"),
    ]
    rows_h = []
    for rt, ra, rd, rb, ck, cb, ca, cn, cna in routes:
        rows_h.append(max(c.card(0, 0, RTc, rt, rb, accent=ra, size=14, draw=False, bullets=False),
                          c.card(0, 0, CKc, ck, cb, accent=ca, size=14, draw=False, bullets=False),
                          c.para(0, 0, CNc - 32, cn, 15, draw=False) + 34))
    gap = 22
    total_h = sum(rows_h) + gap * (len(rows_h) - 1)
    # left: the run; right: the results file
    lb = ["`tlapm -C --cleanfp --strict --toolbox 0 0 --solver '<smt-checked> \"$file\"'`",
          "`--cleanfp`: nothing is carried over from an earlier run, an uncertified one least of all.",
          "Within the run the prover reuses a result for an obligation identical to one just proved; the driver "
          "counts those, so SMT obligations less the reused ones never exceed the calls forwarded on an accepted "
          "proof.",
          "`STRETCH=n` multiplies the backend timeouts; the file states it. `CVC5=` and `ETHOS=` default to the "
          "floor gates' binaries under `tools/`.",
          "Exit status non-zero unless the module is certified."]
    c.card(xs[0], y, LWc, "`spec/proof-cert.sh <M>_proof`", lb, accent="blue", size=14, h=total_h,
           sub="the driver (proof-certification.md §4)")
    rb_ = ["**Certified:** \"All N obligations proved. X of them rest on tlapm's own normalization or on a checked "
           "proof; Y rest on LS4, whose answer no checker confirms.\"",
           "**Not certified:** \"NOT CERTIFIED: <reason>\".",
           "The header fixes the modules of the `EXTENDS` chain, the prover, and the wrapper, solver, checker and "
           "signature, each by digest: a change to any is a different certification.",
           "**Evidence not tracked**: one query and one proof per SMT obligation, about 30 KB an obligation. The file "
           "carries a digest of the sorted (query, proof) digest pairs, which a rerun reproduces (the custodian's "
           "decision, 2026.10.04).",
           "Dated, never edited; a changed module or proof gets a new run.",
           "**Reproduced by** `./proof-cert.sh Anchor_proof | cmp - Anchor-proof-cert-results-2026.10.04.txt`: a "
           "difference in any line is a difference in the module, the proof, the prover, the solver, the checker, the "
           "signature or the wrapper, and the header says which (§6)."]
    c.card(xs[4], y, RSc, "`<M>-proof-cert-results-<date>.txt`", rb_, accent="blue", size=14, h=total_h,
           sub="every obligation on exactly one row (§5)")
    ry = y
    for (rt, ra, rd, rb, ck, cb, ca, cn, cna), rh in zip(routes, rows_h):
        mid = ry + 36
        bad = ra == "red"
        c.arrow([(xs[0] + LWc + 2, mid), (xs[1] - 4, mid)], "red" if bad else "grey", dash="7 5" if bad else None)
        c.card(xs[1], ry, RTc, rt, rb, accent=ra, dash=rd, size=14, h=rh, bullets=False)
        c.arrow([(xs[1] + RTc + 2, mid), (xs[2] - 4, mid)], ca, dash="7 5" if ca == "red" else None)
        c.card(xs[2], ry, CKc, ck, cb, accent=ca, size=14, h=rh, bullets=False, tint=ca != "red",
               dash="6 4" if ca == "red" else None)
        c.arrow([(xs[2] + CKc + 2, mid), (xs[3] - 4, mid)], cna, dash="7 5" if cna == "red" else None)
        c.rect(xs[3], ry, CNc, rh, cna, tint=True, dash="6 4" if cna in ("red", "grey") and rd else None)
        c.blocks.append((xs[3], ry, xs[3] + CNc, ry + rh, "count " + rt[:20]))
        c.para(xs[3] + 16, ry + 12, CNc - 32, cn, 15)
        c.arrow([(xs[3] + CNc + 2, mid), (xs[4] - 4, mid)], cna, dash="7 5" if cna == "red" else None)
        ry += rh + gap
    for x_, lab in [(xs[1], "Route (§2)"), (xs[2], "Checked by"), (xs[3], "Counts toward certification · "
                                                                         "obligations, all 22")]:
        c.text(x_, y - 10, lab, 13, "faint", bold=True)
    y += total_h + 50

    # ---- the wrapper
    y += c.heading(X0, y, "The checked SMT route: what `spec/smt-checked` does with each query (§3)", "teal", 19)
    steps = [
        ("1 · Keep the query", ["Under the digest of its text: `q-<digest>.smt2`."]),
        ("2 · Run cvc5 as written", ["Adding only `--produce-proofs --dump-proofs --proof-format-mode=cpc "
                                     "--proof-granularity=dsl-rewrite`."]),
        ("3 · Substitute the query's declarations", ["cvc5's proof begins by restating them; the wrapper drops those "
                                                    "and writes declarations derived from the query. A proof about "
                                                    "other symbols would no longer type-check."]),
        ("4 · Every assumption is an assertion", ["Each `assume` step, its abbreviations expanded, must equal one of "
                                                  "the query's assertions structurally. Anything else is refused."]),
        ("5 · `ethos --require-proof-of-false`", ["Against the CPC signature in `tools/cpc/`. Only `correct` makes the "
                                                  "wrapper print `unsat`; anything else, its own errors included, "
                                                  "prints `unknown`."]),
    ]
    sg = 50
    sw_ = (W - 4 * sg) / 5
    sh = max(c.card(0, 0, sw_, t, b, accent="teal", size=14, draw=False, bullets=False) for t, b in steps)
    for i, (t, b) in enumerate(steps):
        x_ = X0 + i * (sw_ + sg)
        c.card(x_, y, sw_, t, b, accent="teal", size=14, h=sh, bullets=False)
        if i < 4:
            c.arrow([(x_ + sw_ + 3, y + sh / 2), (x_ + sw_ + sg - 4, y + sh / 2)], "teal")
    y += sh + 30

    w3 = (W - 2 * 40) / 3
    ta = c.table(X0, y, [("In the query", w3 * 0.33), ("In the proof", w3 * 0.3),
                         ("Why the two are the same formula", w3 * 0.37)], [
        ["`(! φ :named N)`, `(! φ :pattern (…))`", "`φ`", "A name is a label; a pattern is an instantiation hint and "
                                                          "no part of what the formula says"],
        ["`(forall ((x S)) φ)`, `x` in `φ`", "`(forall (@list (@var \"x\" S)) φ′)`",
         "The proof format's bound variable. The wrapper rewrites the query into this form, scope by scope, and "
         "compares exactly; never the other way, so a bound variable and a constant of one name cannot be confused"],
    ], size=13.5, accent="teal")
    ta += 16
    ta += c.card(X0, y + ta, w3, "What it refuses, and what it writes", [
        "A query form it does not carry into a proof (anything but `set-logic`, `set-option`, `set-info`, "
        "`declare-sort`, `declare-fun`, `declare-const`, `assert`, `check-sat`, `exit`); a `let`; a binder it does not "
        "read; a proof step other than an abbreviation, `assume`, `assume-push`, `step`, `step-pop`; a proof that "
        "assumes nothing. Each refusal recorded with its reason.",
        "Per query: `q-<digest>.smt2`, the proof as checked `.cpc`, and a verdict `.json` with the digests of query, "
        "proof, solver and checker; one line per call in `calls.log`.",
        "A solver's `sat` or `unknown` needs no certificate: it can only pass the obligation on or fail the proof.",
    ], accent="teal", size=13.5)
    tb = c.table(X0 + w3 + 40, y, [("Stand-in solver (§7)", w3 * 0.2), ("What it does", w3 * 0.32),
                                   ("The wrapper must", w3 * 0.18), ("Reason it gives", w3 * 0.3)], [
        ["honest", "Runs cvc5", "Forward `unsat`", "checker accepted the proof"],
        ["other", "Proves the query with `(assert false)` added", "Forward `unknown`",
         "an `assume` is not one of the query's assertions"],
        ["empty", "Says `unsat`, prints an empty proof", "Forward `unknown`", "proof assumes nothing"],
        ["cut", "An honest proof with its last step removed", "Forward `unknown`",
         "checker refused: the last step did not prove false"],
    ], size=13.5, accent="teal")
    tb += 12
    tb += c.para(X0 + w3 + 40, y + tb, w3, "`spec/smt-checked-selftest.sh`, against any query the prover wrote "
                 "(`tlapm --debug tempfiles` keeps them). All four behave as required: the second is the case step 4 "
                 "exists for; the fourth shows the checker doing work. The wrapper is the one new piece of code the "
                 "method trusts, so it is the one with a test that tries to make it accept what it should not.",
                 13.5, "muted")
    sample = (SPEC / "ToolList-proof-cert-results-2026.10.04.txt").read_text(encoding="utf-8").strip().splitlines()
    samp = [f"`{ln.strip()}`" if ln.strip() else "" for ln in sample]
    samp = [s for s in samp if s]
    tcx = X0 + 2 * (w3 + 40)
    tcard = c.card(tcx, y, w3, "Reading one: `ToolList-proof-cert-results-2026.10.04.txt`, verbatim", samp,
                   accent="blue", size=12.5, bullets=False, lead=17)
    tcard += 14
    tcard += c.table(tcx, y + tcard, [("Line (§5)", w3 * 0.26), ("What it fixes", w3 * 0.74)], [
        ["Modules", "Exactly which text was proved: every module in the `EXTENDS` chain, by digest"],
        ["Prover", "The prover binary and its other backends, as `proof-results.sh` prints them"],
        ["Checked SMT route", "The wrapper, the solver, the checker and its signature, each by digest"],
        ["Obligations", "Every obligation, on exactly one row"],
        ["The last line", "`All N obligations proved…`, or `NOT CERTIFIED: …` with the reason"],
    ], size=13.5, accent="blue")
    y += max(ta, tb, tcard) + 56

    # ================================================================ 3 · the table
    y += c.heading(X0, y, f"3 · Every proof module, by the route that closed each obligation: "
                          f"{sum(1 for r in cert.values() if r['certified'])} of {len(cert)} certified", size=22)
    y += c.para(X0, y, W, "Read from the certified results files at build time (`spec/*-proof-cert-results-*.txt`). "
                "**Deterministic**: on 2026.10.04 the eleven files ADR-0046 A1 cites were regenerated on the custodian's "
                "machine and each was byte-identical, evidence digest included, which was A1's ratification condition "
                "with the self-test (B28). The digest column is each results file's SHA-256 (16), as A1 cites them. "
                "**Obligation counts equal the uncertified runs'** (`<M>-proof-results-*.txt`), every one of which ends "
                "\"All N obligations proved\"; certification adds no obligation and removes none.", 15, "muted") + 14
    cols = [("Proof module", 270), ("Over the record · status at G10", 490), ("Obligations", 120),
            ("Trivial", 100), ("SMT, accepted by `ethos`", 150), ("Zenon, checked by Isabelle", 230),
            ("Isabelle", 100), ("LS4, not certified", 120), ("Failed", 90), ("Time-outs", 100),
            ("Evidence digest", 170), ("Results file (SHA-256, 16)", 410), ("Result", W - 2350)]
    rows = []
    for glabel, gacc, mods in GROUPS:
        rows.append({"group": glabel, "accent": gacc})
        for m, rec in mods:
            r = cert[m]
            zen = str(r["zen"]) + (f": {r['zen_note']}" if r["zen_note"] else "")
            if "REJECTED" in zen:
                zen = f"[[red|{zen}]]"
            res = ("[[teal|Certified]]" if r["certified"] else f"[[red|NOT CERTIFIED]]: {r['last'][15:]}")
            if m in in_lean:
                res += " · [[amber|also proved in Lean]] (ADR-0053, Proposed)"
            elif m == "FloorComposition":
                res += " · three properties [[amber|proved in Lean]] of `admit.rs`'s transcription (ADR-0053, Proposed)"
            cells = [f"`{m}_proof`", rec, f"**{r['n']}**", str(r["triv"]), str(r["smt"]), zen, str(r["isa"]),
                     str(r["ls4"]), f"[[red|{r['fail']}]]" if r["fail"] else "0",
                     ("[[red|×10]]" if r["stretch"] == "x10" else "×1"), f"`{r['evidence']}`",
                     f"`{r['file']}` (`{r['digest']}`)", res]
            rows.append({"cells": cells, "accent": "red"} if not r["certified"] else cells)
    cc = [r for r in cert.values() if r["certified"]]
    sub = {k: sum(r[k] for r in cc) for k in ("n", "triv", "smt", "zen", "isa", "ls4", "fail")}
    rows.append({"cells": ["**All twenty-two**", "5,225 obligations, every one proved (G10 §2.9)",
                           f"**{tot['n']:,}**", f"{tot['triv']:,}", f"{tot['smt']:,}",
                           f"{tot['zen']} ({zen_refused} refused)", str(tot["isa"]), str(tot["ls4"]),
                           f"[[red|{tot['fail']}]]", "", "", "", "19 certified, 3 not"], "accent": "blue"})
    rows.append({"cells": ["**The nineteen certified**", "the certified configuration of T-0045-31",
                           f"**{sub['n']:,}**", f"{sub['triv']:,}", f"{sub['smt']:,}", str(sub["zen"]),
                           str(sub["isa"]), str(sub["ls4"]), "0", "", "", "",
                           f"{sub['n'] - sub['ls4']:,} rest on normalization or a checked proof; {sub['ls4']} on LS4"],
                 "accent": "teal"})
    y += c.table(X0, y, cols, rows, size=13.5, accent="blue") + 14
    y += c.para(X0, y, W, "proof-certification.md §9 reports twenty modules and 5,084 obligations on 2026.10.04 (trivial "
                "3,330; SMT 1,621; Zenon 10, nine accepted and one refused; Isabelle 2; LS4 115; failed 6); the two "
                "successors certified on 2026.10.05 add 141 and make the totals above. Time-outs ×10 is `STRETCH=10`: "
                "it recovered one obligation in `Confinement` and none elsewhere (§10).", 14, "muted") + 50

    # ================================================================ 4 · the three
    y += c.heading(X0, y, "4 · The three that do not certify, and why restructuring them is deferred", "red", 22)
    y += 4
    g = 40
    w3b = (W - 3 * g) / 4
    three = [
        ("`RulesFloorNV_rev5_proof`", [
            f"**{cert['RulesFloorNV_rev5']['n']} obligations**: five are Zenon's (the cases of `BaseNext`, lines 115 to "
            "126), under Z3 as under cvc5, and **Isabelle refuses the script for one** (obligation 55). The 10.02 "
            "results never ran the check.",
            "**What it would take:** smaller steps for those cases, so that SMT proves them or Zenon's script "
            "reconstructs.",
            "Cited by ADR-0026, ADR-0033 and ADR-0046 §4."]),
        ("`Confinement_proof`", [
            f"**{cert['Confinement']['n']} obligations**: three, large type-invariant steps (`TypeOK` at lines 97, 102 "
            "and 190), are proved by Z3 and by nothing else. cvc5 does not prove them at ten times the timeout or "
            "under five instantiation strategies.",
            "**What it would take:** the steps split, by field or by action, in a successor module.",
            "Frozen; cited by ADR-0034 and ADR-0046 §4."]),
        ("`Confinement_A1_proof`", [
            f"**{cert['Confinement_A1']['n']} obligations**: the same three. Its proof is its predecessor's with one "
            "case split changed (`Declared <= 1`), so it inherits the steps cvc5 cannot do.",
            "**What it would take:** the same.",
            "Frozen from G9; ADR-0033 A7 cites it."]),
    ]
    deferred = [
        "All three are cited by digest in accepted records, so restructuring means **successor modules**; the "
        "custodian deferred that on 2026.10.04 (ADR-0046 A1; G10 §7 item 74).",
        "**A refused script and an unproved obligation are missing checks, not counterexamples.** The uncertified "
        "results stand as they did: every obligation proved under the prover as first configured, on the residual "
        "of T-0045-31 as first written, the SMT solver's soundness included.",
        "Item 74, \"the SMT backends' proofs checked\", is discharged for nineteen of twenty-two, **by cvc5 and the "
        "`ethos` checker and not by Isabelle**, the checker it named.",
        "**Proposed, a second route** (ADR-0053; H7): all three are also proved in Lean, every step kernel-checked, of "
        "a re-encoding (`RulesFloorNV_rev5.lean`, `Confinement.lean` under a flag). That does not certify them; it "
        "proves the same theorems again, on the encoding.",
        ]
    th = max([c.card(0, 0, w3b, t, b, accent="red", status="open", size=14, draw=False) for t, b in three] +
             [c.card(0, 0, w3b, "Deferred, and still proved", deferred, accent="brown", size=14, draw=False)])
    for i, (t, b) in enumerate(three):
        c.card(X0 + i * (w3b + g), y, w3b, t, b, accent="red", status="open",
               status_extra="item 74", size=14, h=th)
    c.card(X0 + 3 * (w3b + g), y, w3b, "Deferred, and still proved", deferred, accent="brown", size=14, h=th)
    y += th + 56

    # ================================================================ 5 · what is still trusted
    y += c.heading(X0, y, "5 · What a certified proof still trusts", "red", 22)
    lw5 = W * 0.42
    rw5 = W - lw5 - 40
    t8 = c.table(X0, y, [("Trusted before (proof-certification.md §8)", lw5 * 0.36), ("After certification",
                                                                                       lw5 * 0.64)], [
        ["The SMT solver's soundness", "[[green|No longer trusted.]] Its answer counts only with a proof the checker "
                                       "accepted"],
        ["Zenon's soundness", "[[green|No longer trusted.]] Its script is checked by Isabelle"],
        ["—", "[[red|The checker, its signature and the wrapper]] are trusted in the solver's place. These are the "
              "floor's T-0045-14, and the wrapper has the test of §7"],
        ["Isabelle", "[[red|Still trusted]], for its own proofs and for checking Zenon's"],
        ["**LS4**", "[[red|Still trusted.]] One to three obligations per theorem: the step from \"holds initially and "
                    "every step keeps it\" to \"holds always\". No checker confirms it. For twelve modules a Lean "
                    "re-encoding does that step as a kernel-checked induction ([[amber|ADR-0053, Proposed]]); it does "
                    "not change what this run certifies"],
        ["**tlapm's translation** of an obligation into an SMT query", "[[red|Still trusted]], as `cedar symcc`'s "
         "encoding is for the floor. The checker certifies that the query is unsatisfiable; that the query says what "
         "the obligation says is the prover's"],
        ["**tlapm's normalization**", "[[red|Still trusted.]] About two obligations in three are closed by it with "
                                      "no backend"],
        ["The prover's expansion of definitions, of `ENABLED`, and of primes", "[[red|Still trusted]]; part of the "
                                                                                "translation"],
    ], size=13.5, accent="red")
    t8 += 12
    t8 += c.para(X0, y + t8, lw5, "\"So certification removes the largest unexamined premise, the SMT solver, and leaves "
                 "three: the prover's front end, its temporal backend, and the checker\" (§8).", 14, "muted")
    tA1 = c.table(X0 + lw5 + 40, y, [("Row (ADR-0046 §3, A1)", rw5 * 0.14),
                                     ("Uncertified, as run at B25", rw5 * 0.36), ("Certified", rw5 * 0.5)], [
        ["**Component**", "`tlapm` with Z3, Zenon, Isabelle and LS4", "`tlapm` with cvc5 behind `spec/smt-checked` and "
         "the checker of T-0045-14, Zenon checked by Isabelle, Isabelle, and LS4. Z3 is not run"],
        ["**Trusted for**", "\"All N obligations proved\" means every obligation is a theorem under the module's "
                            "assumptions", "The same, and of every obligation discharged by SMT: a proof of false from "
                                           "the query's own declarations and assertions was accepted by the checker"],
        ["**Residual**", "The prover's and each backend's soundness are unexamined; no backend's answer is checked",
         "The prover's translation of an obligation into a query, and its normalization; LS4, for the temporal step "
         "of each theorem; the checker and its signature, which are T-0045-14's. The SMT solver's soundness is no "
         "longer a premise, as it stopped being one for the floor at Batch 24"],
        ["**Identity fixed by**", "The prover's digest, in every proof results file", "That, and the digests of the "
         "solver, the checker, the signature and the wrapper, in every certified results file"],
    ], size=13.5, accent="blue")
    tA1 += 18
    qw = (rw5 - 30) / 2
    q1 = [
        "\"A certified proof still trusts the prover's translation of an obligation into a query, its normalization, "
        "LS4, and the checker\" (G10 §3, what these checks are).",
        "\"Twenty-two modules' invariants are proved, nineteen with checked proofs, and nothing about the running "
        "reference is. A matching trace is drift detection on tested paths; T-0045-28 stands\" (G10 §8).",
    ]
    q2 = [
        "\"**A certified proof is not a verified one.** The prover's translation, its normalization, LS4 and the "
        "checker are trusted as written\" (G10 §8).",
        "\"Nothing here is independently reviewed\" (G10 §8): the method document, the wrapper, the driver and the "
        "results are the drafter's; B28 was not reviewed by a reader other than the drafter (ADR-0029 A2.5).",
    ]
    hq = max(c.card(0, 0, qw, "What these checks are", q1, accent="red", size=14, draw=False),
             c.card(0, 0, qw, "What G10 does not claim", q2, accent="red", size=14, draw=False))
    c.card(X0 + lw5 + 40, y + tA1, qw, "What these checks are", q1, accent="red", size=14, h=hq, tint=False,
           dash="6 4")
    c.card(X0 + lw5 + 40 + qw + 30, y + tA1, qw, "What G10 does not claim", q2, accent="red", size=14, h=hq,
           tint=False, dash="6 4")
    y += max(t8, tA1 + hq) + 44

    # the two trusted-base rows, as ADR-0045 has them
    text45 = strip_external(ADR45.read_text(encoding="utf-8"))
    y += c.heading(X0, y, "The two trusted-base rows certification rests on: ADR-0045 Annex A and Annex B, as amended "
                          "(B24, B25, B28)", "blue", 19)
    a14, a31 = _row45(text45, "T-0045-14", "A"), _row45(text45, "T-0045-31", "A")
    colsA = [("Id", 120), ("Component", 300), ("Layer", 100), ("Trusted for", 330), ("Rungs", 110), ("Class", 110),
             ("Failure can produce", 280), ("Identity fixed by", 360), ("Residual", W - 1710)]
    y += c.table(X0, y, colsA, [a14, a31], size=13, accent="blue") + 16
    b14, b31 = _row45(text45, "T-0045-14", "B"), _row45(text45, "T-0045-31", "B")
    y += c.table(X0, y, [("Row (Annex B)", 140), ("Instance at the reference", 1100), ("Class here", 140),
                         ("Note", W - 1380)], [b14, b31], size=13, accent="blue") + 50

    # ================================================================ 6 · practice and open
    y += c.heading(X0, y, "6 · Writing proofs that certify, and what is still open", size=22)
    w2 = (W - 40) / 2
    p10 = [
        "**Most proofs certify unchanged**: thirteen of the sixteen that existed when the method was first run, at "
        "the default timeouts. cvc5 proves what Z3 proved in the great majority of steps.",
        "**cvc5 is weaker than Z3 on very large single steps**: the three failures in `Confinement` expand a type "
        "invariant with many record fields in one `BY`. Split such a step by field or by action.",
        "**Name the parts of a large action.** `Labels_proof` states one lemma on the shapes a step can have, with the "
        "action's `LET` named part by part; all 216 of its SMT obligations certified at the default timeout.",
        "**Give the case split explicitly** when an obligation quantifies over a set that has just grown. Both failures "
        "met writing `Labels_proof` and `Emergency_proof` were of this kind, and each was a real gap in the argument.",
        "**An `ENABLED` goal may go to Zenon**, whose script may not reconstruct. A lemma that cannot be certified "
        "should not sit in a certified module: `Emergency_proof`'s was removed and its fact left to a TLC witness.",
        "**A longer timeout rarely helps**; **run `proof-results.sh` first**, then `proof-cert.sh`.",
        "G10 §5 makes it a convention: **a proof is certified or its results file says why not.**",
    ]
    p12 = [
        "**LS4.** No route checks a temporal step. The steps are few and of one shape; a small fixed lemma library "
        "proved once in Isabelle could replace them. Since 2026.10.05 the Lean re-encodings are a route beside this "
        "one in which the step is an induction the Lean kernel checks, at the price of the encoding (ADR-0053, "
        "Proposed).",
        "**The translation.** Nothing here examines how the prover turns an obligation into a query.",
        "**One solver, one version.** cvc5 1.4.0 is pinned by digest because the floor pins it. A newer cvc5 may prove "
        "the six obligations that fail, and would be a different certification.",
        "**The three modules that do not certify** (section 4). Still uncertified here; also proved in Lean of a "
        "re-encoding (ADR-0053, Proposed).",
        "**The evidence is not kept.** A digest and a deterministic rerun stand in for it.",
        "**The prover itself**: pinned by `tools/TLAPS-PIN` (2026.10.03, G10 item 73 discharged), the full binary digest "
        "still owed; the `1.6.0-pre` tag is rebuilt upstream, so a fresh install does not yield the pinned prover.",
        "**This document is the drafter's**, as the wrapper, the driver and the results are.",
    ]
    hp = max(c.card(0, 0, w2, "What the first twenty modules taught (§10)", p10, accent="teal", size=14, draw=False),
             c.card(0, 0, w2, "Open (§12)", p12, accent="red", size=14, draw=False))
    c.card(X0, y, w2, "What the first twenty modules taught (§10)", p10, accent="teal", size=14, h=hp)
    c.card(X0 + w2 + 40, y, w2, "Open (§12)", p12, accent="red", size=14, h=hp, status="open")
    y += hp + 40
    c.legend(X0, y, [("box", "teal", "a checked route, a checker"), ("box", "grey", "trusted as written, unchecked"),
                     ("box", "red", "not certified, residual"), ("box", "blue", "the driver, the record, the results"),
                     ("box", "brown", "the custodian's decision")])
    return c
