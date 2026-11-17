"""H3 — Verification map: every check the corpus runs, what it checks, what must fail, where its result lives, and
what none of it claims."""
from lib import AMENDED_G12, Canvas
from d_h7_lean_route import ENC, PKGS, read_pin, read_results
# The command-chain overlay's eight modules (ADR-0059 to ADR-0066, Proposed) are read from spec/ at build time with
# H8's readers, which name their files (…-2026.11.10.txt) and raise on anything missing or unparseable.
from d_h8_overlay_verification import MODS, SPEC, digest, read_cert, read_proof, read_record, read_rows, read_tlc

ID, SLUG = "H3", "verification-map"

CERT = "[[teal|certified]]"
NOCERT = "[[red|not certified]]"


def overlay_rows():
    """One table row per overlay module, from the module's rows, TLC, proof, certified and record files."""
    out = []
    for d in MODS:
        m = d["m"]
        rows = read_rows(m)
        tlc, prf, cert, rec = read_tlc(m), read_proof(m), read_cert(m), read_record(d["adr"])
        if tlc["rows"] != tlc["ok"] or tlc["notok"] != "none" or tlc["err"] != "none":
            raise ValueError(f"H3: {m}'s TLC results are not all as expected")
        props = ", ".join(f"`{p}`" + (" (over `ENABLED`)" if "ENABLED" in s else "") for p, _, s in d["props"])
        breaks = {}
        for name, mut, prop, exp, consts in rows:
            if mut != "none" and exp == "VIOLATED":
                breaks.setdefault(mut, []).append(prop)
        muts = []
        for mut in d["muts"]:
            b = breaks.get(mut, [])
            muts.append(f"`{mut}` (breaks " + ", ".join(f"`{p}`" for p in dict.fromkeys(b)) + ")" if b
                        else f"`{mut}` ([[red|breaks no property]], as its rows file expects)")
        wits = [prop for name, mut, prop, exp, consts in rows if mut == "none" and prop.startswith("Never")]
        wits = ", ".join(f"`{w}`" for w in dict.fromkeys(wits))
        mdig = digest(SPEC / f"{m}.tla")
        cited = rec["cites"].get(f"{m}.tla")
        cite = (f"ADR-{d['adr']} R1 ([[amber|{rec['status']}]]) cites the module (`{mdig}`), the proof and both results "
                "by digest" if cited == mdig else
                f"[[red|ADR-{d['adr']} cites `{cited}`, the module is `{mdig}`]]")
        asm = prf["asm"] if prf["asm"] != "none" else "nothing assumed"
        certcell = (CERT + f": {cert['n'] - cert['ls4']} on normalization or a checked proof, {cert['ls4']} LS4 "
                    "temporal steps no checker confirms" if cert["certified"] else NOCERT)
        out.append([f"`{m}.tla`", f"ADR-{d['adr']} {d['rc']} ([[amber|Proposed]], 2026.11.10): {d['name']}",
                    props, "; ".join(muts), wits,
                    f"`live-gen-results.sh` with `{m}-rows.txt` (`modules.tsv`, tier `pr`); `-deadlock` audited "
                    "(`deadlock-audit-results-2026.11.10.txt`)",
                    f"`{m}-results-2026.11.10.txt` ({tlc['rows']} rows, every one as expected); `{tlc['consts']}`",
                    f"`{m}_proof.tla` · **{prf['n']:,}**: " + ", ".join(f"`{t}`" for t in prf["thms"]) + f"; {asm} · "
                    + certcell + " (H8)",
                    cite + " · not frozen: freezes at ratification (G12 §3) · [[red|no floor stage, no reference]] "
                    "(G12 item 112) · no binding rows (item 90)"])
    return out


def lane(c, x0, y, w, cards, gap=56, size=14, label_fn=None):
    """A row of cards joined by arrows. cards: (title, body, accent, status, status_extra, dash, arrow_label).
    Returns the height used."""
    n = len(cards)
    cw = (w - gap * (n - 1)) / n
    h = max(c.card(0, 0, cw, t, b, accent=a, status=s, status_extra=se, draw=False, size=size, bullets=False)
            for t, b, a, s, se, d, al in cards)
    for i, (t, b, a, s, se, d, al) in enumerate(cards):
        x = x0 + i * (cw + gap)
        c.card(x, y, cw, t, b, accent=a, status=s, status_extra=se, dash=d, h=h, size=size, bullets=False)
        if i < n - 1:
            nxt = cards[i + 1]
            acc = nxt[2] if nxt[2] in ("red",) else "grey"
            dash = "7 5" if nxt[2] == "red" or (nxt[3] in ("notbuilt",)) else None
            c.arrow([(x + cw + 2, y + 40), (x + cw + gap - 3, y + 40)], acc, dash=dash)
    return h


def build():
    c = Canvas(ID, "Verification map: what is checked, what is proved, what must fail, and what neither claims",
               "Every check and proof in the corpus at G12 and Batch 40. Three methods, three words (ADR-0046 §1, A1): "
               "TLC **checks** forty-one TLA+ modules at small constants, each mutation failing the property it targets "
               "and each reachability witness violated; the TLA+ Proof System **proves** the invariants of thirty-four "
               "of them, 13,622 obligations, under named assumptions and the absence of the mutations that break each "
               "(G12 §2.9); and thirty-one of those proofs are **certified**, every SMT obligation backed by a proof an "
               "independent checker accepted (H6), by a prover known to be unsound in two ways that a rule and a scan "
               "keep proofs from (ADR-0046 A2, B37), both reported upstream (B39) and the pin unmoved (G12 §2.6). "
               "Liveness is **checked, not proved** (E4). Ten of the thirty-four proofs are of Proposed records: the two "
               "workflow modules, **proved and certified since 2026.11.11** (ADR-0054 R7, ADR-0055 R3; C9, D6), and the "
               "command-chain overlay's eight, of a design with no floor and no code (H8). The consensus log is modelled "
               "since 2026.11.14, **checked and trace-validated, not proved** (ADR-0033 A20, B40). Then the policy "
               "floor's gates, run on the genesis floor and on the proposed floor's four stages, the last of which the "
               "reference links and is not in force; the reference's 159 tests restating the properties; the trace "
               "harness that replays those tests through an operational model, which found a race no proof could and "
               "is behind the tree since the workflow build; the drift pins; and the lineage gate suite. Then the "
               "honesty layer: a proof is of the module, a certified proof is not a verified one, and what runs is "
               "neither checked nor proved. Beside them, **ratified in Batch 36** (ADR-0053; H7), a second route in "
               "Lean: fifteen proof modules' theorems proved again of re-encodings, the admit decision proved a step of "
               "`FloorComposition`, two models of `apply` replayed against the traces, and the floors' totality under "
               "Cedar's verified model; unchanged since, and stale (G12 item 103).",
               3400,
               "spec/README.md and every spec/*.tla header and results file, among them Labels-results-2026.10.03.txt and "
               "-2026.10.04.txt, ToolList-, Operators-, Emergency- and Correlator-results-2026.10.04.txt, BreakGlass_A1- "
               "and NonComposition_A1-results-2026.10.05.txt, Emergency_live- and Coupling_live-results-2026.10.07.txt, "
               "Mesh-results-2026.10.07.txt and Workflow-results-2026.10.08.txt with their rows files; "
               "Federation-, Membership-, Intent-, Alone-, Outstanding-, PlaneClock-, Peer- and Release-results-2026.11.10.txt "
               "with their rows files, proof modules, -proof-results- and -proof-cert-results-2026.11.10.txt (read at "
               "build time with H8's readers); spec/Paxos.tla and PaxosTrace.tla headers, Paxos-rows.txt, "
               "Paxos-larger-rows.txt, Paxos-kept-rows.txt, Paxos-results-, Paxos-larger-results- and "
               "Paxos-trace-results-2026.11.14.txt; spec/modules.tsv; spec/deadlock-audit-results-2026.10.07.txt and "
               "-2026.11.10.txt; spec/proof-scan-results-2026.10.08.txt, -2026.11.10.txt, -2026.11.11.txt; "
               "spec/<Module>_proof.tla, spec/<Module>-proof-results-*.txt and spec/<Module>-proof-cert-results-*.txt "
               "(34 each), among them Workflow- and Mesh-proof-results- and -proof-cert-results-2026.11.11.txt; "
               "spec/Mechanism-trace-results-2026.10.05.txt (3b1ad26dfd432d48) and its predecessors; spec/proof-method.md "
               "§1, §5a; spec/proof-certification.md §8, §9; spec/proof-sync.sh (its seven reasons), proof-results.sh, "
               "proof-cert.sh; spec/theorem-premise-binding.md; tools/TLAPS-PIN; ADR-0046 §1–§5, §7, E1, E2, A1 (B28), "
               "E4 (B37), A3 (B39); ADR-0045 A4 (B39); "
               "floor/README.md, floor/run-gates.py, floor/genesis-gates-results-2026.10.01.txt; floor/proposed/README.md, "
               "build.py, run-gates.py, labels-, control- and emergency-gates-results-2026.10.04.txt and "
               "workflow-gates-results-2026.10.08.txt; "
               "mechanism/README.md, mechanism/GAPS-AND-ASSUMPTIONS.md §6 (in full, 42 rows), I46–I49, findings 9, 19–23; "
               "mechanism/corpus-pins.sha256 (63 lines); mechanism/crates/*/tests (fifteen binaries), "
               "topak-paxos/tests/sim.rs and src/replica.rs (Mutation); "
               "slm/README.md Part B, slm/gate-suite-results-2026.09.28.txt; ADR-0029 §5 (A1, A3, A4); ADR-0030 §5 A1, "
               "A3; ADR-0033 §2 row P, §3, §7 finding 9, A5–A17, A19, R14, A20, B40; ADR-0034 finding 6, A2; ADR-0035 "
               "(Proposed); ADR-0045 §5, T-0045-3, T-0045-14, T-0045-28 to 31; ADR-0053 (B36) and the three Lean results "
               "files spec/lean/TopakSpec-, mechanism/lean/Admit- and floor/lean/TopakFloor-results-2026.10.05.txt, "
               "tools/LEAN-PIN, tools/lean-sync.sh; ADR-0047 §11; ADR-0048 §8; ADR-0050 §10; ADR-0051 §10; ADR-0052 §9, "
               "R5; ADR-0013 A1; ADR-0026 A2; ADR-0046 A2; ADR-0054 §12, R7; ADR-0055 §11, R3; ADR-0059 §9, ADR-0060 §7, "
               "ADR-0061 §7, ADR-0062 §11, ADR-0063 §8, ADR-0064 §8, ADR-0065 §9, ADR-0066 §7 (each R1, Proposed); G5 §4; "
               "G7 §2.2, §3, §4; G8 §1, §5, §8; G9 §3; G10 §3, §5; G11 §1, §2.1, §2.2, §2.6, §2.9, §3, §4, §5, §7 items 56, "
               "69, 73–75, 78, 90, 91, 96, 101–105, §8, §9; G12 §1.1, §2.1, §2.2, §2.5, §2.6, §2.9, §3, §4, §6, §7 items 56, "
               "73, 74, 90, 101, 103, 104, 107, 112, 120, §8, §9; ToO rev 16 §5.5, §11.3, §15")
    c.note = AMENDED_G12
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ================================================================ 1. the chains
    y += c.heading(X0, y, "1 · Six chains of evidence, from the record to the running code; the third is in Lean", size=22)
    y += 14
    LP = 30

    # lane A: protocol properties
    top = y
    y += 40
    hA = lane(c, X0 + LP, y, W - 2 * LP, [
        ("Records", ["The ADRs state each property against what an agent's alphabet allows. A module is cited by "
                     "digest in the accepted record it checks; a change is a successor module, suffix `_A1` (G10 §5): "
                     "`Lease_A1`, `Confinement_A1`, and since 2026.10.05 `BreakGlass_A1` and `NonComposition_A1`, "
                     "where the predecessors model X1."], "blue", None, "", None, None),
        ("41 TLA+ modules, TLC", ["Each property with a **mutation that must fail** and a `Never…` "
                                  "**witness that must be violated** (non-vacuity, G2 §3): existential claims, "
                                  "**checked**. Small constants; `tools/tla2tools.jar` 1.7.4, TLC 2.19, tracked for "
                                  "its digest (T-0045-29) and since G12 pinned in `tools/TLA-PIN` (G12 §2.6). G9's "
                                  "twenty, seven at G10, four at G11 (two liveness extensions, whose leads-to "
                                  "properties TLC checks; `Workflow` and `Mesh`), the command-chain overlay's eight "
                                  "(2026.11.10, Proposed; H8), and `Paxos` with `PaxosTrace` (2026.11.14, A20, B40). "
                                  "The invariants of 34 are also proved (lane 2); `Paxos`'s are not."],
         "teal", None, "", None, None),
        ("Rust tests restate them", ["`mechanism/`: **159 tests** (`36269bc`, ADR-0033 A20, B40: A19's 155 across "
                                     "fifteen binaries and four in `topak-paxos`'s simulation) and **38 Rego tests** "
                                     "(A15's, not rerun since), each named for the property and the mutation it "
                                     "refuses (GAPS §6; `operators.rs`, `emergency.rs` and the two `workflow.rs` named "
                                     "for the modules' properties). The workflow build is still A16's and A17's, "
                                     "pending (R14). Discrimination tests, not proofs, by the same hand."],
         "teal", "built", "", None, None),
        ("Trace validation: stage 1", ["Tests record every `apply`; `trace2tla.py` converts; `Mechanism.tla` "
                                       "replays and checks `TraceMatches`. 21 traces (09.30); 62 traces, 709 steps "
                                       "(10.02b); **82 traces, 1,007 steps, every step matching** (10.05, A14), every "
                                       "state also read against `ConfinementRefinement.tla`. Checked to discriminate; "
                                       "it found a race in lease expiry (A13). **Behind the tree since 2026.10.08**: "
                                       "`Mechanism.tla` does not model workflows, and it was not rerun at A16, A19 or "
                                       "A20; the self review's rerun matched 82 of 83 traces, the end-to-end workflow "
                                       "run excepted (G12 item 56). **The consensus log has the same since 2026.11.14**: "
                                       "`PaxosTrace.tla` replays the simulation's recorded runs, 8 traces, 3,302 "
                                       "events, every line as expected, run twice (A20, B40). Since "
                                       "2026.10.06 the same traces also run through a Lean model of `apply`'s seat "
                                       "and lease arms: 82 traces, 1,014 steps, every one a model step (ADR-0053 R4, "
                                       "B36), and through a second model that adds sequence numbers, watermarks and "
                                       "seals (R5); both [[red|stale]] since the workflow build (G12 item 103)."],
         "teal", "built", "", None, None),
        ("Tested paths only (T-0045-28)", ["What no test reaches is asserted, and the model takes more from the "
                                           "trace than it did: whether a request's signature is its seat's, whether "
                                           "a sign-on assertion verifies, which roster keys approved an activation, "
                                           "which seat a revocation was lifted on (G10 §3). The floor's decision on an "
                                           "operator's request is not modelled. T-0045-28 stays a **trust root**."],
         "red", "open", "", "6 4", None),
        ("Stage 2: a Lean model", ["With differential testing against the code (ADR-0033 open obligations; G12 "
                                   "item 56). **Not begun.** The proofs make its target precise and do nothing "
                                   "else for it (ADR-0046 §2). Two functions are proved in Lean of a transcription "
                                   "(ADR-0053, B36; lane 3): evidence for those functions, not a model of "
                                   "`apply`, and not stage 2."], "red", "notbuilt", "", None, None),
        ("Stage 3: compilation", ["The Lean model compiled; with a reproducible build (T-0045-30), the rows "
                                  "leave Annex A only on the addendum that cites the chain. **Not begun.**"],
         "red", "notbuilt", "", None, None),
    ], size=14)
    y += hA + 26
    c.region(X0, top, W, y - top, "Protocol properties: spec/ → mechanism/", "teal", dash=None, sw=2, size=15)
    y += 44

    # lane P: the proofs (ADR-0046)
    top = y
    y += 40
    hP = lane(c, X0 + LP, y, W - 2 * LP, [
        ("A frozen module", ["Cited by digest in a record. **Thirty-four** have a proof (G12 §2.9): every module but "
                             "`Mechanism.tla` (a trace replay), `ConfinementRefinement.tla` (predicates over its "
                             "replayed states), `Lease.tla` (its invariants are `Lease_A1`'s), `RulesFloorNV.tla` "
                             "(superseded by rev 5), `RulesFloorBase.tla` (definitions), and since A20 `Paxos.tla` "
                             "(its safety argument is `Voting`'s, not written as a module) and `PaxosTrace.tla` (a "
                             "trace replay): seven reasons in `proof-sync.sh`, which exits 0. `Workflow` and `Mesh` "
                             "are **proved** since 2026.11.11 (ADR-0054 R7, ADR-0055 R3), their records Proposed."],
         "blue", None, "", None, None),
        ("`spec/<Module>_proof.tla`", ["**Extends the module without editing it.** Each invariant as `Spec => []P`; "
                                       "its hypothesis is only the mutations that break it; a combined `Safe` under "
                                       "`Mut = \"none\"`; one lemma per mutation saying what it admits."],
         "teal", None, "", None, None),
        ("The prover (T-0045-31)", ["`tlapm` 1.6.0-pre at `7824dab` (binary `e150fb793fb28592…`) with Z3 4.8.9, "
                                    "Zenon 0.8.4, Isabelle2025, LS4; installed by `tools/install-tlaps.sh`, **not "
                                    "tracked**, pinned by `tools/TLAPS-PIN` and run through `tools/tlapm`, which "
                                    "refuses another digest (G10 item 73, discharged). **Known unsound in two ways** "
                                    "(ADR-0046 A2): a term under a binder; two terms with one name. A rule and "
                                    "`proof-scan.sh` keep a proof from them; [[red|no check detects the first]]. Both "
                                    "**reported upstream** (A3, ADR-0045 A4, B39) and fixed upstream in part, in "
                                    "`ff40755`; **the pin has both** (G12 §2.6, item 104)."],
         "blue", "accepted", "C2, C4 · B25, B37, B39", None, None),
        ("`*-proof-results-<date>.txt`", ["`proof-results.sh` regenerates each, printing the digest of every "
                                          "module in the EXTENDS chain and of the prover. **13,622 obligations, every "
                                          "one proved** (G12 §2.9): G11's twenty-four still sum to 5,416 (G9's fifteen "
                                          "at 10.02, five at 10.04, the two successors at 10.05, the two liveness "
                                          "extensions at 10.07 and 10.08); the overlay's eight at 11.10 (5,600) and "
                                          "`Workflow` and `Mesh` at 11.11 (1,136 and 1,470)."],
         "teal", None, "", None, None),
        ("Certified: 31 of 34 (ADR-0046 A1)", ["`proof-cert.sh` reruns each with Z3 replaced by cvc5 behind "
                                               "`smt-checked`, every `unsat` counted only on a proof `ethos` accepted, "
                                               "and Zenon checked by Isabelle. All ten new modules certify, each with "
                                               "its LS4 steps uncertified, as every module (G12 §2.9). **Three do not "
                                               "certify**, as at G11: `RulesFloorNV_rev5`, `Confinement`, "
                                               "`Confinement_A1`; restructuring deferred (item 74). Route by route: H6."],
         "teal", "accepted", "C2, C4 · B28", None, None),
        ("Frozen; kept in step", ["Thirteen cited by digest in ADR-0046 §4, two frozen from G9, six from G10, two "
                                  "from G11 (G11 §3); **frozen from G12 on: nothing new**, every module and proof "
                                  "added since cited only by Proposed or pending text (G12 §3). "
                                  "A change is a successor module with a successor proof. `proof-sync.sh` reports any "
                                  "proof whose specification moved, and any results file citing a prover other than "
                                  "the pin's; at G12 it exits 0, where at G11 it exited 1 (G12 §2.9)."],
         "teal", None, "", None, None),
        ("Of the module only", ["**Proved** holds of every behaviour of the module, for every constant its "
                                "assumptions admit. It is not a claim about `mechanism/` (T-0045-28) and replaces "
                                "no mutation row (ADR-0046 §2). Certified is not verified (G11 §8)."], "red", None, "",
         "6 4", None),
    ], size=14)
    y += hP + 26
    c.region(X0, top, W, y - top, "Proofs (ADR-0046, Batches 25 and 28): spec/<Module>.tla → spec/<Module>_proof.tla "
                                  "→ TLAPS → certified run", "teal", dash=None, sw=2, size=15)
    y += 44

    # lane L: the Lean route (ADR-0053, B36), read from the Lean results files and the pin
    lres = {pkg: read_results(pkg, g) for pkg, g, *_ in PKGS}
    pin = read_pin()
    nl = sum(r["nprint"] for r in lres.values())
    top = y
    y += 40
    hL = lane(c, X0 + LP, y, W - 2 * LP, [
        ("What is stated", ["A proved TLA+ module, a function of the reference, or the floor. The TLA+ text, its "
                            "TLAPS proof and the Rust stay canonical: Lean proves again, of what its Lean states "
                            "(ADR-0053 §1)."], "blue", None, "", None, None),
        ("`spec/lean`: re-encodings", [f"Sixteen modules as Lean transition systems; the theorems of their "
                                       f"**{len(ENC)} proof modules** by induction on the reachable states, the step "
                                       "TLAPS hands to LS4. Among them the three that do not certify, every step "
                                       "kernel-checked, of the encoding."], "teal", "accepted", "ADR-0053 · B36", None, None),
        ("`mechanism/lean`: transcriptions", ["`admit.rs`'s `floor_gate` and `compose`, their call site and the "
                                             "`topak-floor` wrapper: the whole decision **proved a `Decide` step of "
                                             "`FloorComposition`**, on Cedar's rule as the engine premise (R2). "
                                             "`clock.rs`'s subtracting interval: the margin moves expiry earlier, "
                                             "never later. Two models of `apply`, replayed against the traces. Read "
                                             "beside the Rust; pinned, not frozen; [[red|stale at G12, as at G11]] "
                                             "(item 103)."],
         "teal", "accepted", "ADR-0053 · B36", None, None),
        ("`floor/lean`: Cedar's model", ["The genesis floor, **the floor in force** (`emergency`, R3) and the stage "
                                         "the reference links (`workflow`, not in force), in cedar-spec `" + pin["cedar_spec_tag"] + "`'s "
                                         "syntax: totality as one theorem of the model's proved validator soundness; "
                                         "the 62, 107 and 123 cases under the model's authorizer; witnesses per action. "
                                         "The sync fails if the reference links a floor no file states."],
         "teal", "accepted", "ADR-0053 · B36", None, None),
        ("The kernel (T-0045-37)", [f"Lean {pin['version']}, kernel `libleanshared` "
                                              f"`{pin['libleanshared_sha256_16']}…`, pinned by `tools/LEAN-PIN`; "
                                              "installed through elan by `tools/install-lean.sh`, **not tracked**. "
                                              "In ADR-0045's Annex A since Batch 36."],
         "blue", "accepted", "B36", None, None),
        ("Results, replay, sync", [f"Each `results.sh`: a clean build, `#print axioms` of {nl} theorems, and "
                                   "`leanchecker --fresh` replaying every constant, because the axiom list alone "
                                   "misses a declaration added past the kernel. Byte for byte. `tools/lean-sync.sh` "
                                   "checks every digest against the tree and the pin; at G12, as at G11, it exits 1 "
                                   "for `mechanism/lean`'s three series, by the custodian's decision, now ratcheted "
                                   "in CI (G12 item 103). Nothing under the three packages changed since G11; proved "
                                   "modules without an encoding went from nine to nineteen (item 107)."],
         "teal", None, "", None, None),
        ("Of the encoding only", ["**Proved in Lean** holds of the encoding, transcription or statement, read against "
                                  "what it states. Not a refinement: T-0045-28 is unchanged; derived premises carry "
                                  "the second route, and no stage is discharged through Lean (ADR-0053 §5)."], "red",
         None, "", "6 4", None),
    ], size=14)
    y += hL + 26
    c.region(X0, top, W, y - top, "A second route, in Lean (ADR-0053, B36; H7): spec/lean, mechanism/lean, "
                                  "floor/lean → the Lean kernel → replay", "amber", dash="10 6", sw=2, size=15)
    y += 44

    # lane B: the floor
    top = y
    y += 40
    hB = lane(c, X0 + LP, y, W - 2 * LP, [
        ("The floor bundle", ["In force: `floor/proposed/emergency-floor.cedar`, **28 policies, 107 cases**, built by "
                              "`build.py` from `genesis-floor.cedar` (17, 62) in three gated stages, `labels` (20, 74), "
                              "`control` (29, 106), `emergency`; `genesis-values.json` (placeholders). Ratified when "
                              "the bootstrap reviewer finds it fit (ADR-0030 A3). A fourth stage, `workflow` (30, 123), "
                              "is Proposed with ADR-0054 and not in force."], "violet", "genprov", "", None,
         None),
        ("`run-gates.py`, `cedar symcc`", ["Totality, non-vacuity, discrimination, every entry matters, routing, "
                                          "four negative controls, three checker controls (ADR-0030 §5); "
                                          "`floor/proposed/run-gates.py` runs them unchanged on a stage, then routing "
                                          "controls for the stage's new entries."],
         "blue", None, "", None, None),
        ("`floor/cvc5-checked`", ["Keeps each query, runs cvc5 with proofs, binds the proof to the query's own "
                                  "declarations and assertions; forwards `unsat` only once the checker accepts. "
                                  "Anything else is `unknown`, a failure."], "blue", None, "", None, None),
        ("The checker (T-0045-14)", ["`ethos` 8dc85c4 against the CPC signature in `tools/cpc/` (from cvc5 1.4.0). "
                                     "**The solver is trusted for nothing** (ADR-0030 A1, Batch 24). Since B28 the same "
                                     "checker stands behind the certified proofs."], "blue",
         "accepted", "C1", None, None),
        ("Results, each stage", ["**RESULT: all gates pass**, in all four. `workflow`, 2026.10.08: 22 `unsat` with a "
                                            "checked proof, 44 totality checks `holds°`, tree `4ffc4fade540ab64`. "
                                            "`emergency`, 2026.10.04: 15 `unsat` with a "
                                            "checked proof, 41 totality checks `holds°` by cedar's folding (T-0045-3), "
                                            "none unchecked; evidence tree `974f339662a5289d`. A rerun reproduces each "
                                            "file byte for byte (G10 §3, G11 §3). Every stage's totality, and the "
                                            "genesis floor's, is also proved in Lean, under cedar-spec's model "
                                            "(lane 3)."], "teal",
         None, "", None, None),
        ("`topak-floor` pins it", ["Compiled in **by path**, refused at startup unless its bytes match the gated "
                                   "digests: the `emergency` stage from 2026.10.05 (A10–A12), and since 2026.10.08 the "
                                   "`workflow` stage, [[red|not in force]], at the custodian's direction (A16; item 102). "
                                   "Its 123 cases replay through the linked engine. The stage files' opening comment is "
                                   "wrong, and false of the linked stage (item 91)."],
         "teal", "built", "", None, None),
    ], size=14)
    y += hB + 26
    c.region(X0, top, W, y - top, "Policy floor: floor/ and floor/proposed/ → topak-floor", "blue", dash=None, sw=2,
             size=15)
    y += 44

    # lanes C and D side by side
    half = (W - 40) / 2
    top = y
    yy = y + 40
    hC = lane(c, X0 + LP, yy, half - 2 * LP, [
        ("Lineage records", ["`slm/` pipeline at rung 0: every record is **declared** (D-0035-1)."], "grey", None,
         "", None, None),
        ("`gate_suite.py`", ["E1–E5 and distillation cases each seen to fire alone; the §2 monotonicity check: "
                             "**holds** in `bounded` mode, 2,000 trials (09.28)."], "grey", None, "", None, None),
        ("ADR-0035", ["The independence criterion these test, with R4 to R8 (G11 §2.4). **Not in force**; "
                      "its §8 item 5 review is owed."], "amber", "proposed", "", None, None),
    ], size=14)
    hD = lane(c, X0 + half + 40 + LP, yy, half - 2 * LP, [
        ("`corpus-pins.sha256`", ["The whole-file digest of every record (42) and TLA+ module (21) the reference "
                                  "follows, as it last followed them: **63 pins** since `Paxos.tla` and "
                                  "`PaxosTrace.tla` were pinned at `7df7bb6` (ADR-0033 A20, B40); sixty-one at G12 "
                                  "(ToO rev 16 §15)."], "grey", None, "", None, None),
        ("`cargo test -p topak-core --test drift`", ["Fails when a pinned file changes, or when the code cites a "
                                                      "record that is not pinned."], "teal", "built", "", None, None),
        ("Clearing it", ["Review the change against the code; bring the code into line or register the divergence "
                         "in GAPS; replace the pin line. Whole-file pins trip on History-only edits."], "grey", None,
         "", None, None),
    ], size=14)
    hh = max(hC, hD) + 66
    c.region(X0, top, half, hh, "Lineage gate suite: slm/ (ADR-0035 §8 rehearsal)", "amber", dash="10 6", sw=2,
             size=15)
    c.region(X0 + half + 40, top, half, hh, "Drift: records and modules pinned by the reference", "grey",
             dash=None, sw=2, size=15)
    y = top + hh + 60

    # ================================================================ 2. the module table
    y += c.heading(X0, y, "2 · Every TLA+ module in `spec/`: what it checks, what must fail, what is proved and "
                          "certified, and where its result is", size=22)
    y += c.para(X0, y, W, "Forty-one modules and thirty-four proof modules (G12 §2.9, §9; ADR-0033 A20: G9's twenty and "
                "fifteen; at G10 `Labels`, `ToolList`, `Operators`, `Emergency`, `Correlator`, `BreakGlass_A1` and "
                "`NonComposition_A1`, and seven proofs; at G11 `Emergency_live` and `Coupling_live` with their proofs, "
                "and `Workflow` and `Mesh`, then unproved; since, the command-chain overlay's eight with their proofs "
                "(2026.11.10), the proofs of `Workflow` and `Mesh` (2026.11.11), and `Paxos` with `PaxosTrace` "
                "(2026.11.14), unproved; `Trace_*` files are generated and not counted). Properties are invariants "
                "checked under `Mut = \"none\"`; each "
                "mutation changes the mechanism, never the property, and must produce a counterexample; each `Never…` "
                "witness must be violated, which shows the behaviour it names is reachable. The proof column gives each "
                "proof module, its obligations (ADR-0046 §4) and whether its certified run certifies (A1; H6); its results "
                "files are `<Module>-proof-results-<date>.txt` and `<Module>-proof-cert-results-<date>.txt`. Results "
                "files are dated and never change; every proof results file, and every module added since G9, "
                "regenerates from a script (G12 item 78, in part; `spec/modules.tsv` drives CI's TLC job over fifteen). "
                "**Pinned** means listed in `mechanism/corpus-pins.sha256`. The binding table has no rows yet for "
                "eighteen modules, the overlay's eight among them (G12 item 90).",
                15, "muted") + 14
    cols = [("Module", 230, {"mono": False}), ("Record it checks", 240), ("Properties (invariants)", 420),
            ("Mutations that must fail", 400), ("Witnesses that must be violated", 380),
            ("Driver", 232), ("Results file, constants", 500), ("Proved in (ADR-0046 §4) · certified (A1)", 448),
            ("Cited by digest in · status", 438)]
    rows = [
        {"group": "The rules floor and the bootstrap modules", "accent": "blue"},
        ["`RulesFloorBase.tla`", "ADR-0029 §5 shared definitions", "— (the live definition of the floor; no property "
         "of its own)", "—", "—", "via `bootstrap-run.sh`, `a1-run.sh`", "—",
         "— (extended by `Anchor`, `BreakGlass` and `BreakGlass_A1` and their proofs)",
         "ADR-0026; **live**: ADR-0046 cites the digest proved (`cf2351de2b39cccf`) and does not freeze it (E1). "
         "[[red|Behind the records]]: still `bgScope` and R6's bound of two (G10 §2.1, item 90)"],
        ["`RulesFloorNV.tla`", "ADR-0026 §6", "`P1_AllSeatsGranted`, `P2_AtLeastTwo`, `P3_AuthorNotCounted`, "
         "`P4_NoTimeoutGrant`, `P5_AnchorNotApprover`, `P7_BGNoAuthority` (in `Safe`)",
         "drop R1, R2, R3, R4, R5, R7, under `Mech` = `param`, `as0024`, `rev4`", "`NeverPromoted`",
         "`RulesFloorNV-run.sh`", "`RulesFloorNV-results-2026.09.15.txt` (26 runs)", "[[grey|not proved]]",
         "ADR-0026 · frozen (G1)"],
        ["`RulesFloorNV_rev5.tla`", "ADR-0026 R1; ADR-0024 rev 5", "`P1_Unanimity`, `P2_TwoSeatsCounted`, "
         "`P3_AuthorNotCounted`, `P5_AnchorNotApprover`, `P7_BGNoAuthority`, `P9_NoSoloGrant`",
         "drop R1; drop R1 and R9; drop R2; `Mech = \"norecuse\"` (withdrawn R3); drop R5; drop R7",
         "`NeverPromoted`", "`RulesFloorNV_rev5-run.sh`", "`RulesFloorNV-rev5-results-2026.09.23.txt`; five humans "
         "(at four, threshold equals unanimity)", "`RulesFloorNV_rev5_proof.tla` · **262**: each property under "
         "the entry it rests on, `P9` under R2 and (R1 or R9); the three `ASSUME`s proved as lemmas · " + NOCERT +
         ": Isabelle refuses all five Zenon scripts, tlapm reporting one (ADR-0046 E4, B37)",
         "ADR-0026, ADR-0033, ADR-0046 · **pinned**"],
        ["`NonComposition.tla`", "ADR-0013 §4 (erasure, ADR-0006, with break-glass, ADR-0009, against ADR-0028)",
         "`NC1`, `NC2`", "`M1` (F1 decisions erasable), `M2` (break-glass widens erasure)",
         "`NeverErased`, `NeverBGEffect`, `NeverBGErased`", "`NonComposition-run.sh`",
         "`NonComposition-results-2026.09.23.txt`", "`NonComposition_proof.tla` · **58**: `NC1`, `NC2` not "
         "under `M1`, `M2` · " + CERT, "ADR-0013, ADR-0046 · frozen; models X1, succeeded by `NonComposition_A1`"],
        ["`NonComposition_A1.tla`", "ADR-0013 §4, A1; ADR-0052 §9, R5: break-glass as an emergency seating, a record "
         "per activation", "`NC1`, `NC2`, restated for a record per activation",
         "`M1`, `M2`, and **`M3`, new with the seating**: an activation's record kept only while its round is live. "
         "Each of the three breaks both (G10 §3)",
         "`NeverErased`, `NeverEmEffect`, `NeverEmErased`, `NeverErasedAfterRound`, `NeverSecondActivation`",
         "`a1-run.sh` with `NonComposition_A1-rows.txt`", "`NonComposition_A1-results-2026.10.05.txt` (14 rows); "
         "`MaxRound = 2`", "`NonComposition_A1_proof.tla` · **96**: `NC1`, `NC2` with none of the three mutations "
         "on; nothing assumed · " + CERT, "ADR-0013, ADR-0052 · frozen from G10"],
        ["`Anchor.tla`", "ADR-0029 §5, bootstrap module 2 of 5; ADR-0025, ADR-0026 §1", "`FloorPreserved`",
         "`M_FLOOR` (issuance accepted without the floor check)", "`NeverIssued`", "`bootstrap-run.sh`",
         "`bootstrap-results-2026.09.23.txt`", "`Anchor_proof.tla` · **40**: `FloorPreserved` under `Mut = "
         "\"none\"`, for every floor subset and epoch bound; `EpochMonotone` · " + CERT, "ADR-0029, ADR-0046"],
        ["`BreakGlass.tla`", "ADR-0029 §5, bootstrap module 5 of 5; ADR-0009, ADR-0026 R7",
         "`BreakGlassNeverChangesAuthority`", "`M_SCOPE` (mechanism ignores `bgScope`); R7 dropped from `Active`",
         "`NeverBreakGlass`", "`bootstrap-run.sh`", "`bootstrap-results-2026.09.23.txt`",
         "`BreakGlass_proof.tla` · **37**: under `Mut = \"none\"`, assuming `\"R7\" ∈ Active` · " + CERT,
         "ADR-0029, ADR-0046 · frozen; models X1, succeeded by `BreakGlass_A1`"],
        ["`BreakGlass_A1.tla`", "ADR-0029 §5; ADR-0026 A2; ADR-0052 §9, R5: the emergency seating in place of X1",
         "`EmergencyNeverChangesAuthority`", "`M_SCOPE` (the lease's alphabet ignored); `M_KIND` (the kind given an "
         "authority act), with and without R7. With the kind's alphabet as decided, **dropping R7 changes nothing** "
         "(G10 §3)", "`NeverEmergencyAct`, `NeverSecondRound`", "`a1-run.sh` with `BreakGlass_A1-rows.txt`",
         "`BreakGlass_A1-results-2026.10.05.txt` (8 rows); `MaxRound = 2`, `MaxEpoch = 2`; `Active` with and "
         "without R7", "`BreakGlass_A1_proof.tla` · **45**: under `Mut # \"M_SCOPE\"` and `Mut = \"M_KIND\" => "
         "\"R7\" ∈ Active`; unlike its predecessor it does not assume R7 · " + CERT,
         "ADR-0026, ADR-0052 · frozen from G10"],
        {"group": "The policy floor's composition and routing", "accent": "blue"},
        ["`FloorComposition.tla`", "ADR-0030 §1, §3, §4 (§9)", "`AdmitImpliesFloorPermit`, `FloorErrorIsDeny`, "
         "`BundleRefusalHonored`, `BundleCannotWriteFloorInputs`, `EnvelopeHolds`",
         "`M_OVERRIDE`, `M_ERR`, `M_FAILOPEN`, `M_WRITE` (each also breaks `EnvelopeHolds`, except `M_FAILOPEN`); "
         "`M_OVERRIDE` also breaks `FloorErrorIsDeny` and `BundleRefusalHonored`, `M_ERR` also "
         "`AdmitImpliesFloorPermit` (ADR-0046 §5; three new TLC rows)",
         "`NeverAdmitted`, `NeverNarrowed`, `NeverFloorError`", "`floor-run.sh`",
         "`FloorComposition-results-2026.09.24.txt`; `premise-corrections-results-2026.10.02.txt`",
         "`FloorComposition_proof.tla` · **171**: each property not under the mutations that break it · " + CERT,
         "ADR-0030, ADR-0033, ADR-0046 · **pinned**"],
        ["`FloorRouting.tla`", "ADR-0030 §5", "`NoWideningWithoutIssuance`, `FloorNeverVacuous`",
         "`M_ROUTE` (only a strict superset is a relaxation), `M_GATE` (non-vacuity off)",
         "`NeverIncomparable`, `NeverRelaxIssued`, `NeverTightened`", "`floor-run.sh`",
         "same file as above. Checks the routing logic, not the analyzer: it assumes the implies answers",
         "`FloorRouting_proof.tla` · **36**: both under `Mut = \"none\"`; a proof of the routing model, not "
         "of the floor's Cedar text · " + CERT, "ADR-0030, ADR-0033, ADR-0046"],
        {"group": "The lease and confinement", "accent": "teal"},
        ["`Lease.tla`", "ADR-0031 §8", "`LeaseAuthorityMonotone`, `NoActionUnderFencedEpoch`, "
         "`Rung0NeverContained`, `RevokedStaysStopped`", "`M_RENEW`, `M_FENCE`, `M_RUNG`, `M_ROLE`, `M_REVOKE`",
         "`NeverActed`, `NeverRenewed`, `NeverRevoked`, `NeverStaleLease`, `NeverSelectiveRevoke`", "`lease-run.sh`",
         "`Lease-results-2026.09.23.txt`, `-25.txt`; `MaxEpoch = 2`, `MaxFence = 3`",
         "[[grey|not proved]]: its invariants are `Lease_A1`'s at rungs 0..2",
         "ADR-0031 · frozen at `7636c6c3364bca9c` · **pinned**"],
        ["`Lease_A1.tla`", "ADR-0031 A1 (renewal keeps the rung)", "as `Lease.tla`, rungs 0..3",
         "as `Lease.tla`, and `M_LOWER` (renewal may lower the rung)", "as `Lease.tla`, and `NeverRenewedAbove0`",
         "`Lease_A1-run.sh`", "`Lease_A1-results-2026.09.28.txt`; `MaxEpoch = 2`, `MaxFence = 3`",
         "`Lease_A1_proof.tla` · **200**: each property not under its mutations · " + CERT,
         "ADR-0031, ADR-0046 · successor of the frozen module · **pinned**"],
        ["`Confinement.tla`", "ADR-0034 §7, A1", "`ContainedMeansConfined`, `NoSilentDowngrade`, `ContestedStopped`, "
         "`FreshAppraisal`", "`M_HOST` (rungs 1, 2), `M_HW` (3), `M_CONTESTED`, `M_UNBOUND`, `M_STALE`, "
         "`M_DOWNGRADE`, `M_PROFILE`, `M_RENEWLOW`", "`NeverContainedEffect`, `NeverMediatedEffect`, "
         "`NeverContested`, `NeverRefused`, `NeverTamperKilled`, `NeverRenewed`, `NeverLapsed`, per declared rung",
         "`confinement-run.sh`; `confinement-gen-results.sh`", "`Confinement-results-2026.09.25.txt`, `-28.txt`, "
         "`-30.txt` (the rung-0 row, D-0034-4); `MaxEpoch = 1`, `MaxIdx = 4`, `MaxGen = 2`, two principals",
         "`Confinement_proof.tla` · **502**: every rung at once, assuming `Declared ∈ 0..3` · " + NOCERT +
         ": three `TypeOK` steps proved by Z3 alone",
         "ADR-0034, ADR-0046 · frozen; succeeded by `Confinement_A1` (finding 6) · **pinned**"],
        ["`Confinement_A1.tla`", "ADR-0034 finding 6's successor: `Evidence` reads no measurement at rung 0 "
         "(ADR-0033 A7, Batch 29)", "as `Confinement.tla`; `Safe` holds at every rung",
         "as `Confinement.tla`; `M_HOST` breaks rungs 1 and 2 and changes nothing at 0 and 3",
         "`NeverContainedEffect` (holds at rung 0, violated at 1 and 3), `NeverMediatedEffect`, `NeverContested` "
         "(3); the rung-0 row that reached Contested under `M_HOST` now holds",
         "`confinement-run.sh`; `confinement-gen-results.sh` over `confinement-A1-rows-2026.10.02.txt`",
         "`Confinement_A1-results-2026.10.02.txt` (24 rows, rungs 0–3); constants as `Confinement.tla`",
         "`Confinement_A1_proof.tla` · **503**: `Confinement_proof` with one case split changed, `Declared <= 1` · "
         + NOCERT + ": the same three steps",
         "ADR-0033 A7 · frozen from G9 · **pinned**"],
        {"group": "Seats, Observers, coupling and the correlator (Build cells)", "accent": "pink"},
        ["`Seats.tla`", "ADR-0037 §9", "`OnlyThinkersAuthor`, `OneSeatPerPrincipal`", "`M_KIND`, `M_SEAT` (the "
         "reference before ADR-0037)", "`NeverActed`, `NeverTwoLive`, `NeverObserverVoted`", "`seats-run.sh`",
         "`Seats-results-2026.09.29.txt`; 2 principals, 3 seats, 4 actions", "`Seats_proof.tla` · **110** · " + CERT,
         "ADR-0037, ADR-0046 · **pinned**"],
        ["`Observers.tla`", "ADR-0038 §8", "`DenyByAnyOf`, `ReachIsBounded`", "`M_QUORUM`, `M_REACH`",
         "`NeverFound`, `NeverRefused`, `CorrelatorNeverFinds`", "`observers-run.sh`",
         "`Observers-results-2026.09.29.txt`; 2 cells, 1 correlator", "`Observers_proof.tla` · **65** · " + CERT,
         "ADR-0038, ADR-0046 · **pinned**"],
        ["`Correlator.tla`", "ADR-0051 §10: the correlator's detection function, its folds (G10 item 43)",
         "`CarriedCoversSplitPath`, `FindingHasEvidence`, `IngressReachIsShared`, `SilenceIsCounted`, "
         "`MissIsOnACorrelation`, `HonestNeverCharged`, `StoreWithinRecord`, `LagNeverGates` (`ENABLED`)",
         "`M_ROUNDSCOPE`, `M_ONEHOP`, `M_BARE`, `M_DOMAIN`, `M_SELF`, `M_TIERLESS`, `M_KEEP`, `M_COUPLE`",
         "`NeverSplitFound`, `NeverFoundClean`, `NeverSharedTwo`, `NeverMiss`, `NeverNamed`, `NeverLostTaint`, "
         "`NeverErasedARow`", "`correlator-run.sh`; `correlator-gen-results.sh`",
         "`Correlator-results-2026.10.04.txt` (22 rows); `Thinkers = {t1, t2}`, `Corrs = {c1, c2}`, `Honest = {c1}`, "
         "`MaxRound = 2`, one or two stores", "`Correlator_proof.tla` · **455**: all eight, `LagNeverGates` a state "
         "lemma · " + CERT, "ADR-0051, [[amber|Proposed]] · not among G10's frozen six; not built at the reference "
         "(item 97)"],
        ["`Coupling.tla`", "ADR-0039 §8", "`NoAdmitWithoutLiveObserver`, `UnreadBounded`, `CorrelatorNeverGates`",
         "`M_NOCOUPLE`, `M_MARK`, `M_ROUNDS`, `M_CORR`", "`NeverRoundTwo`, `NeverRefused`, `NeverStaleRefusal`, "
         "`NeverBacklogRefusal`", "`coupling-run.sh`", "`Coupling-results-2026.09.29.txt`; `K = 1`, `R = 3`, "
         "`MaxRound = 2`", "`Coupling_proof.tla` · **320**: for every K, R and MaxRound; `K < R` is not a "
         "premise of `UnreadBounded` (ADR-0046 §5) · " + CERT, "ADR-0039, ADR-0046 · **pinned**"],
        ["`Coupling_live.tla`", "ADR-0039 §2; ToO §13 A12 and A18; the liveness plan, Tier 1 item 1 (CR-37)",
         "`Safe` over `SpecL`, as `Coupling`'s; and **four leads-to properties**, `AdmitStallEnds`, `GrantStallEnds`, "
         "`AdmitsResume`, `NextRoundGranted`, each under the fairness it needs",
         "`M_HBLIVE`, which passes every safety row and every witness and breaks `GrantStallEnds` and "
         "`NextRoundGranted`; `M_HBCOUPLED`; and each fairness condition taken away in turn, breaking the property it "
         "is for", "`NeverRoundTwo`, `NeverRefused`, `NeverStaleRefusal`, `NeverBacklogRefusal`, "
         "`NeverRoundTwoAfterReading`, `NeverAdmitted`; `NoBehaviour` under the full fairness",
         "`live-gen-results.sh` with `Coupling_live-rows.txt`", "`Coupling_live-results-2026.10.07.txt` (69 rows, "
         "every one as expected); `K = 1`, `R = 3`, `MaxRound = 2`, and `K = 2`, `R = 4`, `MaxRound = 3`",
         "`Coupling_live_proof.tla` · **31**: `SpecL ⇒ Spec` and `Coupling`'s three for `SpecL` · " + CERT +
         "; [[red|the leads-to properties are checked, not proved]] (G11 item 105)",
         "frozen from G11 · extends `Coupling` without editing it (E4)"],
        {"group": "Run", "accent": "green"},
        ["`RunCoupling.tla`", "ADR-0042 §8; ADR-0039 §2 as ADR-0041 §2 reads it", "`NoEffectWithoutLiveObserver`, "
         "`UnreadEffectsBounded`, `ConsultNeverCoupled`, `SealCountsEffects`, `RoundBoundCountsAll`",
         "`M_EMITSEQ` (the reference before ADR-0042), `M_COUPLEALL`, `M_ROUNDS`, `M_MARK`, `M_NOCOUPLE`, "
         "`M_BOUNDEFF`", "`NeverRoundTwo`, `NeverRefused`, `NeverRefusedOnActuates`, `NeverConsultedWhileStalled`, "
         "`NeverSealedOnActuates`", "`runcoupling-run.sh`", "`RunCoupling-results-2026.09.29.txt`; `K = 1`, `R = 4`, "
         "`MaxRound = 2`", "`RunCoupling_proof.tla` · **469**: for every K, R and MaxRound; "
         "`SealCountsEffects` not under `M_EMITSEQ` (the table said `M_ROUNDS`) · " + CERT,
         "ADR-0042, ADR-0046 · **pinned**"],
        ["`RunSeats.tla`", "ADR-0043 §8; ADR-0040 §2", "`OnlyThinkersActuate`, `ObserversConsultAndReport`, "
         "`NoNameCrossesDomains`", "`M_KIND`, `M_DOMAIN` (which also breaks `ObserversConsultAndReport`); "
         "`M_OBSEMIT` is the provisional column, under which every property holds",
         "`NeverActuated`, `NeverObserverReported`, `NeverObserverConsulted`", "`runseats-run.sh`",
         "`RunSeats-results-2026.09.29.txt`; 4 seats, 6 actions", "`RunSeats_proof.tla` · **147** · " + CERT,
         "ADR-0043, ADR-0046 · **pinned**"],
        ["`RunConfinement.tla`", "ADR-0034 A2 (Batch 30), condition (ii): P4 for Run is channel fidelity",
         "`EffectsOnDeclaredChannels`, `ContainedEffectsUseHeldTools`; both also hold under D-0034-5's filter",
         "`M_CHANNEL` (the runtime does not bind the target), `M_NATIVE` (breaks both), `M_FILTER` (only where "
         "D-0034-5 is declared)", "`NeverContainedEffect`, `NeverMediatedEffect`, `NeverRefused` (with and "
         "without the filter), `NeverUndeclaredTarget`: five rows", "`runconfinement-run.sh`; "
         "`runconfinement-gen-results.sh`", "`RunConfinement-results-2026.10.02.txt` (13 rows); 2 principals; "
         "a Wasm, a filtered and a native tool; 3 targets", "`RunConfinement_proof.tla` · **116**: both invariants "
         "inductive on their own; one `ASSUME`, `FilteredBool` · " + CERT,
         "ADR-0034 A2, ADR-0033 A8 (Batches 30, 31) · frozen from G9 · **pinned**"],
        ["`Labels.tla`", "ADR-0047 §11: labels on Run's ingress, handles, the floor's minimum",
         "`LabelsCoverTruth`, `ResultLabelCoversInputs`, `FloorMinimumHolds`, `NoUnlabelledDelivery`, "
         "`OutsideResultIsUntrusted`, `ReservedReleasedOnlyIfIssued`, `ClearSetCoversGuest`, "
         "`SuppressedNeverInGuest`, `NoReadThenSend`, `NoSteeredDestination`; the step property "
         "`ClearSetOnlyGrows`",
         "`M_LITERAL`, `M_JOIN`, `M_LOAD`, `M_RESET`, `M_DELIVER`, `M_F1`, `M_F2`, `M_F3`. **It found a hole in "
         "the record**: a literal laundered through an inside tool, closed by R10's join (G10 §3)",
         "`NeverOutwardEffect`, `NeverTaintedOutward`, `NeverF1`, `NeverF2`, `NeverF3`, `NeverSuppressed`, "
         "`NeverHandleInput`, `NeverCleanLeak`, `NeverReleased`", "`labels-run.sh`; `labels-gen-results.sh`",
         "`Labels-results-2026.10.03.txt` (33 rows), `-2026.10.04.txt` (37); `MaxSeq = 3`; tools `fetch`, `send` "
         "(outward), `vault`, `echo` (inside)", "`Labels_proof.tla` · **651**: all ten and `ClearSetOnlyGrows`, for "
         "every `MaxSeq` (`MaxSeq ∈ Nat`) · " + CERT, "ADR-0047 · frozen from G10 · **pinned**"],
        ["`ToolList.tla`", "ADR-0048 §8: a Thinker learns its tools from the mechanism",
         "`ToolListIsExact`, `ToldMatchesDecided`, `ListFixedForRound`, `OpenedListIsTold`, `OpeningRecordFirst`",
         "`M_RECOMPUTE`, `M_WIDE`, `M_DECIDELATEST`, `M_LATE`, each run against all five",
         "`NeverPromotedMidRound`, `NeverNarrowed`, `NeverAdmitted`, `NeverRefused`, `NeverNewList`, "
         "`NeverRefusedNewTool`", "`toollist-run.sh`; `toollist-gen-results.sh`",
         "`ToolList-results-2026.10.04.txt` (27 rows); `Tools = {t1, t2, t3}`, two revisions, one principal",
         "`ToolList_proof.tla` · **215** · " + CERT, "ADR-0048 · frozen from G10"],
        {"group": "The operator and the emergency seating (both records provisional)", "accent": "brown"},
        ["`Operators.tla`", "ADR-0050 §10 ([[blue|provisional]]): an operator is a principal",
         "`FirstLeaseHasAQuorum`, `LeaseWithinSeating`, `SuccessorNeverWidens`, `ExpiredOperatorOnlyDenies`, "
         "`NoAddWithoutLiveLeaseAndPeer`, `NoSelfRegrant`, `OperatorLeaseWasVouched`, `NoDenyOnAStaleKey`, "
         "`NoDenyByRevoked`, `EveryStopIsAttributed`, `RevokedStaysOut`, `FleetFenceNeedsLease`, "
         "`DenyAlwaysAvailable` (`ENABLED`)",
         "`M_NOSEAT`, `M_WIDEN`, `M_PEER`, `M_LAPSEDADD`, `M_SELF`, `M_NOATTEST`, `M_STALEKEY`, `M_DENYLEASE`, "
         "`M_ANON`, `M_LAPSEDFENCE`",
         "`NeverWorkerRegrant`, `NeverNarrowed`, `NeverLapsedDeny`, `NeverStaleKey`, `NeverPeerless`, "
         "`NeverRecovered`, `NeverOperatorRenewed`, `NeverOperatorRegranted` (two and three operators), "
         "`NeverFenced`, `NeverLapsedRevoke`", "`operators-run.sh`; `operators-gen-results.sh`",
         "`Operators-results-2026.10.04.txt` (32 rows, after R5); `MaxRound = 2`, `Workers = {w}`, `Ops = {a, b}` "
         "or `{a, b, c}`", "`Operators_proof.tla` · **354**: all thirteen, for every set of operators and round "
         "bound · " + CERT, "ADR-0050 · frozen from G10 · **pinned**. Tied to the reference by tests, not a "
         "refinement (item 90)"],
        ["`Emergency.tla`", "ADR-0052 §9 ([[blue|provisional]]): break-glass is an emergency seating",
         "`EmergencyLeaseHasARosterQuorum`, `EmergencyLeaseIsOneRound`, `NoAgentHoldsAnEmergencySeat`, "
         "`CallsAreAllowlisted`, `ThinkerStillCoupled`, `ActivationIsForensic`",
         "`M_NOQUORUM`, `M_REGRANT`, `M_RENEW`, `M_AGENT`, `M_X1`, `M_UNCOUPLE`, `M_ERASE`, each run against all six",
         "`NeverActivated`, `NeverSecondRound`, `NeverUnobservedEmergencyCall`, `NeverEmergencyOnlyTool`, "
         "`NeverNewToolInEnvelope`, `NeverStaleEnvelope`, `NeverRefused`, `NeverThinkerCall`",
         "`emergency-run.sh`; `emergency-gen-results.sh`", "`Emergency-results-2026.10.04.txt` (51 rows); "
         "`MaxRound = 2`; a roster of three, quorum two; one person, one agent; tools `t1`, `t2` (promoted), `te` "
         "(emergency-only), `tx` (in no bundle)", "`Emergency_proof.tla` · **373**: all six · " + CERT,
         "ADR-0052 · frozen from G10 · **pinned**. Tied to the reference by tests, not a refinement (item 90)"],
        ["`Emergency_live.tla`", "ADR-0039 A2; ADR-0052 §9 ([[blue|provisional]]); the liveness plan, Tier 0",
         "`EmergencyNeverCoupled`, `EmergencyCallsWithoutObserver` (both over `ENABLED`: while the lease is live "
         "every tool in its envelope can be admitted; with no live Observer some call can), `EnvelopeHasT1`; `Safe`",
         "`M_EMCOUPLE`, `M_EMCOUPLE2`, each breaking both; `Emergency`'s seven, under which both still hold",
         "`NeverUnobservedEmergencyCall`", "`live-gen-results.sh` with `Emergency_live-rows.txt`",
         "`Emergency_live-results-2026.10.07.txt` (32 rows); `MaxRound = 2` and `3`",
         "`Emergency_live_proof.tla` · **160**: both through Isabelle, and `SpecL ⇒ Spec` · " + CERT,
         "frozen from G11 · extends `Emergency` without editing it (E4)"],
        {"group": "Workflows (ADR-0054 and ADR-0055, both Proposed): checked, and since 2026.11.11 proved and certified "
                  "(ADR-0054 R7, ADR-0055 R3); the records stay Proposed, and the proofs do not ratify them (G12 §8)",
         "accent": "amber"},
        ["`Workflow.tla`", "ADR-0054 §12 ([[amber|Proposed]]): a workflow is a promoted DAG (C9)",
         "`AppliedRouteEnabled`, `OneRoutePerDecision`, `FindingPrecedesNoRoute`, `ChosenOnlyByRoute`, "
         "`EdgeAfterCoverage`, `TaintedNeverOutward`, `GrantUnderPromotion`, `PromotedAlternates`, "
         "`CompletedOnlyBySink`, `BasisStable`; and `LogReach`",
         "`M_DECIDEONLY` (breaks three), `M_NOCONSUME` (two), `M_DEFAULT`, `M_UNCOVERED`, `M_NOTAINT`, "
         "`M_GRANTANYEPOCH`, `M_TIMEOUTDONE`, `M_REWRITE` (its remainder under `CapLog`), `M_NOLINEAGE`; each shown to "
         "break nothing else", "`NeverRouted`, `NeverCompleted`, `NeverVoidedByFinding`, `NeverVoidedByConsumed`, "
         "`NeverVoidedByLease`, `NeverDecisionFailed`, `NeverOutward`, `NeverComputed`, `NeverRefusedAtGrant`, "
         "`NeverLogSix`", "`workflow-run.sh`; `workflow-gen-results.sh`",
         "`Workflow-results-2026.10.08.txt` (33 rows), module `a72973b5878e9468`",
         "`Workflow_proof.tla` · **1,136**: all ten and `SafeAlways`, each under only the mutations its rows say "
         "break it; nothing assumed; no state constraint, so it covers what the `M_REWRITE` remainder row checks only "
         "under `CapLog`; writing it corrected no pairing · " + CERT + ": 1,125 on normalization or a checked proof, "
         "11 LS4 temporal steps no checker confirms, none left to Zenon or Isabelle (ADR-0054 R7; "
         "`Workflow-proof-results-2026.11.11.txt`, `-proof-cert-`; G12 §3)",
         "ADR-0054 R7 ([[amber|Proposed]]) cites module, proof and both results by digest · **pinned**, re-read at R7 "
         "(A19) · tied to the reference by tests named after its properties, and by no trace (A16, pending)"],
        ["`Mesh.tla`", "ADR-0055 §11 ([[amber|Proposed]]): a workflow may be a mesh (D6)",
         "`BudgetBound`, `CompletedOnlyBySink`, `RouteOnItsEvent`, `NoActivationAfterFinding`, `LabelCoversTruth`, "
         "`TaintedNeverOutward`, `ClearHopsAlternate`",
         "`M_OVERRUN`, `M_ORCHFREE` and `M_TRACKER` (their remainders under `CapOnePast`), `M_BUDGETDONE`, "
         "`M_SOURCEONLY`, `M_FORGETTAINT` (breaks two), `M_NOLINEAGE`; each shown to break nothing else",
         "`NeverLooped`, `NeverCompletedAfterLoop`, `NeverExhausted`, `NeverTaintAroundLoop`, `NeverExitClosedByTaint`, "
         "`NeverVoidedByHistory`, `NeverVoidedByLease`", "`mesh-run.sh`; `mesh-gen-results.sh`",
         "`Mesh-results-2026.10.07.txt` (23 rows), module `a5bc64953c38c9a9`",
         "`Mesh_proof.tla` · **1,470**: all seven and `SafeAlways`, each under only the mutations its rows say break "
         "it, at the module's own mesh and budget `N = 6`; nothing assumed; no state constraint, so it covers what the "
         "`M_ORCHFREE` and `M_TRACKER` remainder rows check only under `CapOnePast` · " + CERT + ": 1,462 on "
         "normalization or a checked proof, 8 LS4 temporal steps no checker confirms, none left to Zenon or Isabelle "
         "(ADR-0055 R3; `Mesh-proof-results-2026.11.11.txt`, `-proof-cert-`; G12 §3)",
         "ADR-0055 R3 ([[amber|Proposed]]) cites module, proof and both results by digest · **pinned**, re-read at R3 "
         "(A19) · tied to the reference by tests, and by no trace (A16, pending)"],
        {"group": "The command-chain overlay (ADR-0059 to ADR-0066, each R1, Proposed 2026.11.10): checked, proved and "
                  "certified; a design with no floor stage and no reference (G12 §8, item 112). Read from spec/ at "
                  "build time; what each property and mutation says, and the abstractions, are on H8", "accent": "amber"},
        *overlay_rows(),
        {"group": "The consensus log (ADR-0033 §2 row P, §3, §7 finding 9, closed; A20, B40): an operational model of "
                  "the replica, checked and trace-validated, not proved", "accent": "teal"},
        ["`Paxos.tla`", "ADR-0033 §2 row P, §3 (crash-recovery, not Byzantine), finding 9 (proposer retry; **closed "
         "2026.11.14** by the custodian's decision, B40); ToO §11.3's message-level module over `Voting`",
         "`OneValuePerBallot`, `ChosenUnique`, `Agreement`, `LearnerSound`, `OnlyHanded`, `NoAmplification` "
         "(finding 9: `assigned[v] <= handed[v] + duped[v]`); `Safe` their conjunction with `TypeOK`. No liveness is "
         "stated",
         "`M_IGNOREPROMISED`, `M_BELOWPROMISE` (the code's two) and `M_NOPERSIST` (a host that sends before it persists), "
         "each breaking `ChosenUnique` and `Agreement` at two values; `M_REQUEUE` (the first implementation's re-queue "
         "on step-down), breaking `NoAmplification` and no safety property. What each keeps is checked too "
         "(`KeptUnderLogMutations`, `KeptUnderRequeue`)",
         "`NeverChosen`, `NeverLearned`, `NeverSecondLeader`, `NeverAdopted`, `NeverGapFilled`, `NeverNacked`, "
         "`NeverForwarded`, `NeverCaughtUp`, `NeverTwoSlots`, `NeverDuped`",
         "`live-gen-results.sh` with `Paxos-rows.txt` (`modules.tsv`, tier `pr`, about seven minutes); "
         "`Paxos-larger-rows.txt` and `Paxos-kept-rows.txt` outside it, a row being millions of states",
         "`Paxos-results-2026.11.14.txt` (27 rows, every one as expected), module `ac26b35f368beeb8`; "
         "`Paxos-larger-results-2026.11.14.txt` (2 rows: `Safe` at two values, 4,414,419 states, and with one value "
         "handed in twice); `N = 3`, one round, replicas 1 and 3 may stand (two leaders at most), one value, each bound "
         "opened in turn. [[red|No results file for]] `Paxos-kept-rows.txt`: its first row did not finish in two hours, so "
         "what `M_BELOWPROMISE` and `M_NOPERSIST` keep is checked at one value only. Not checked: a second round, five "
         "replicas, a crash together with a second value (spec/README.md)",
         "[[grey|not proved]]: `proof-sync.sh` says why, the safety argument is `Voting`'s, which is not written as a "
         "module, and this one would refine it (A20)",
         "ADR-0033 A20 (B40) · **pinned** at `7df7bb6`, because `replica.rs` and `sim.rs` cite it · **not frozen**: "
         "moves with the code · no binding rows (item 90)"],
        ["`PaxosTrace.tla`", "ADR-0033 finding 9; ADR-0045 T-0045-28, stage one for the consensus log, as "
         "`Mechanism.tla` is for the admit path",
         "`TraceReceivable`, `TraceStateMatches` (the replica's state after each call of `handle`, field for field, "
         "and its `next_deliver`), `TraceSendsMatch` (what the call sent, the same forwards in the same order); `Safe` "
         "on every replayed state",
         "a run of mutated code, replayed under its own mutation, matches to its last event, after which the property "
         "it must break is violated; replayed under `Mut = \"none\"` it is a MISMATCH (at events 46, 70, 330, 14). "
         "**Checked to discriminate** that way, by the code's own mutations",
         "—",
         "`paxos-trace-run.sh` on runs `tests/sim.rs` records over `Replica::snapshot` with `TOPAK_TRACE_DIR` set; "
         "`paxos-trace-results.sh`; `paxos-trace2tla.py`",
         "`Paxos-trace-results-2026.11.14.txt`: **8 traces, 3,302 events, every line as expected**; four unmutated runs "
         "MATCH (three and five replicas, under loss, delay, duplication, partition and restarts), four mutated; module "
         "`63a086605dca3cad`, reference at `63e9922`, run again at `48a392c` with the same lines (A20). The host is the "
         "simulation's: `topak-node`'s driver and WAL are not traced",
         "[[grey|no proof]]: a trace replay over `Paxos`'s operators, not a transition system with invariants of its "
         "own (`proof-sync.sh`)", "ADR-0033 A20 (B40) · **pinned** at `7df7bb6`, **not frozen**: moves with the code"],
        {"group": "The operational model of the reference", "accent": "teal"},
        ["`Mechanism.tla`", "ADR-0045 T-0045-28; ADR-0033 A5, A6, A14", "`TraceMatches` (each recorded step's "
         "projected state and result equal the model's)", "a step that differs. **Checked to discriminate** (A14): "
         "five edits each removing one modelled thing (the peer rule, the activation's quorum, the gate on unsigned "
         "requests, the stale-`clearSet` comparison, the fold's clear-or-handle test) each mismatched a trace; a "
         "sixth, the label check removed, stops TLC with an **evaluation error**, reported `ERROR`", "—",
         "`mechanism-trace-run.sh` (one TLC per trace, six at a time, each its own temporary directory); "
         "`mechanism-trace-results.sh`; `trace2tla.py`",
         "`Mechanism-trace-results-2026.09.30.txt` (21 traces, 163 steps); `-10.01` (22, 168); `-10.02` (57, 642); "
         "`-10.02b` (62, 709); **`-2026.10.05.txt` (82 traces, 1,007 steps)**, module `e29dbaf0936dbae1`, at "
         "`9c57221` + working tree", "[[grey|no proof]]: a trace replay states no invariants; its target is "
         "the refinement (T-0045-28)", "pinned, **not frozen**: moves with the code"],
        ["`ConfinementRefinement.tla`", "ADR-0045 T-0045-28, stage one; ADR-0034 §3, §4 as `Confinement_A1` "
         "states them (ADR-0033 A7)", "`ConfinementRefined`: `RNoSilentDowngrade` (per seat), "
         "`RContestedStopped`, `RFreshAppraisal`, `RContainedAttested` (`Contained`'s premises; "
         "`ContainedMeansConfined` is not checkable here)", "a negative control, a broken invariant, must fire",
         "—", "`mechanism-trace-run.sh`, on every replayed state", "the trace results files from "
         "`-2026.10.02.txt` on, through `-2026.10.05.txt`: every state keeps the invariants", "[[grey|no proof]]: "
         "predicates over replayed trace states, not a specification (`proof-sync.sh`)", "pinned"],
    ]
    # ADR-0053 (B36): the proof modules spec/lean re-encodes, read from its results file, gain a Lean note
    enc_tla = {m for m, _ in ENC}
    for r in rows:
        cells = r["cells"] if isinstance(r, dict) and "cells" in r else (r if isinstance(r, list) else None)
        if not cells:
            continue
        mod = cells[0].strip("`").removesuffix(".tla")
        if mod in enc_tla:
            lf = dict(ENC)[mod]
            cells[7] += f" · [[teal|proved in Lean]]: `spec/lean/TopakSpec/{lf}.lean` (ADR-0053, B36)"
        elif mod == "RulesFloorBase":
            cells[7] += (" · [[amber|encoded in Lean]], its genesis `ASSUME` proved as a theorem: "
                         "`spec/lean/TopakSpec/RulesFloorBase.lean` (ADR-0053, B36)")
        if mod == "FloorComposition":
            cells[7] += (" · and the code's decision, wrapper and `compose`, [[amber|proved a `Decide` step]] of it: "
                         "`mechanism/lean/Topak/FloorRefinement.lean` (ADR-0053 R2)")
        if mod == "Seats":
            cells[7] += (" · and a model of `State::apply`'s seat and lease arms [[amber|proved to refine it]] at its "
                         "constants, the reference's recorded traces replayed through the model: "
                         "`mechanism/lean/Topak/SeatsModel.lean` (ADR-0053 R4)")
        if mod == "Coupling":
            cells[7] += (" · and `UnreadBounded` [[amber|proved of a model of `apply`]] at any number of seats, directly "
                         "and not by refinement, the recorded traces replayed through it: "
                         "`mechanism/lean/Topak/CouplingModel.lean` (ADR-0053 R5)")
    y += c.table(X0, y, cols, rows, size=13.5) + 50

    # ================================================================ 3. gates + bootstrap
    y += c.heading(X0, y, "3 · The floor gates, on the genesis floor and on the proposed floor's four stages; and "
                          "the bootstrap specification", size=22)
    wl = W * 0.6
    wr = W - wl - 40
    gy = y
    gc = [("Gate (ADR-0030 §5)", 220), ("What it checks", wl * 0.25), ("Genesis floor, 2026.10.01", wl * 0.13),
          ("`labels`, 10.04", wl * 0.1), ("`control`, 10.04", wl * 0.12), ("`emergency`, 10.04 (in force)", wl * 0.14)]
    gc.append(("`workflow`, 10.08 (linked)", wl - sum(x[1] for x in gc)))
    h1 = c.table(X0, gy, gc, [
        ["**Policies · cases**", "the floor text and its behavioural cases", "17 · 62 (DRAFT)", "20 · 74",
         "29 · 106", "**28 · 107**", "30 · 123"],
        ["**Totality**", "never-errors, per policy per applicable action", "23, all `holds°`", "26, `holds°`",
         "41, `holds°`", "41, `holds°`", "44, `holds°`"],
        ["**Non-vacuity**", "always-allows refuted, per action", "10 actions", "10", "16 (the six control actions)",
         "16", "17 (and `Route`)"],
        ["**Discrimination**", "always-denies refuted, per action", "10", "10", "16", "16", "17"],
        ["**Every entry matters**", "the floor minus one policy is not equivalent to the floor", "17, each differs",
         "20", "29", "28", "30"],
        ["**Routing**", "candidate revisions classified by implies both ways (ToO §3.2): a tightening, two "
                        "relaxations, an incomparable", "4, on checked proofs", "4", "4", "4", "4"],
        ["**Routing, new entries**", "a weakened entry is a relaxation, a strengthened one a tightening "
                                     "(`floor/proposed/run-gates.py`)", "—", "4 (`R5`–`R7`)",
         "9 (and `C1`, `C4`, `C5`, `C7`, `C8`)", "11 (and `B10` both ways)",
         "17 (and `R9`, `R8` twice, `R3`, a tightening, an equivalent)"],
        ["**Negative controls**", "vacuous floor (Read, Consult), erroring policy, dead entry: each gate must catch "
                                  "a defective floor", "all four caught", "4", "4", "4", "4"],
        ["**Checker controls**", "a solver that answers `unsat` with no proof, a proof of another query, a proof "
                                 "missing a step", "all three caught", "3", "3", "3", "3"],
        ["**Evidence**", "cedar calls · solver queries · `unsat` checked · `sat`; `holds` without a checked proof",
         "81 · 56 · 4 · 49; 0; tree `f8b1196a427a35ed`", "95 · 67 · 8 · 56; 0", "147 · 104 · 13 · 88; 0",
         "151 · 108 · 15 · 90; 0; tree `974f339662a5289d`", "171 · 125 · 22 · 100; 0; tree `4ffc4fade540ab64`"],
        ["**Result**", "", "all gates pass", "all gates pass", "all gates pass", "**all gates pass**",
         "all gates pass"],
        {"group": "Genesis gate runs before 2026.10.01 are D-0030-2 runs (no checked proofs)", "accent": "grey"},
        ["09.24 to 09.30", "ADR-0037, ADR-0039, ADR-0041 runs; `T_persona` in the values file", "all pass; 47, 51, "
         "62 cases", "", "", "", ""],
        ["10.01", "**proof-carrying** (ADR-0030 A1, Batch 24)", "all pass; the digests pinned until 10.05", "", "", "",
         ""],
        {"group": "The `emergency` stage is the floor in force: genesis-provisional (ADR-0030 A3), ratified when the "
                  "bootstrap reviewer finds it fit; what makes a floor fit is not written (items 2, 87). Since "
                  "2026.10.08 the reference links the `workflow` stage, Proposed with ADR-0054 and not in force (item "
                  "102). The stage files' comment \"not what the reference follows\" is wrong (item 91)",
         "accent": "violet"},
    ], size=13.5, accent="blue")
    h2 = c.table(X0 + wl + 40, gy, [("Bootstrap module (ADR-0029 §5)", wr * 0.3), ("Invariant", wr * 0.32),
                                    ("Status", wr * 0.38)], [
        ["`Genesis`", "`GenesisSatisfiesFloor`", "[[red|not drafted]]; the reference checks genesis rules at "
         "startup instead (T-0045-10). Its shape is a lemma in the `Anchor` and `BreakGlass` proofs, proved of the "
         "floor's definition and not of genesis contents, which are unwritten"],
        ["`Anchor`", "`FloorPreserved`", "[[teal|drafted and checked]] 2026.09.23; [[teal|proved]] 2026.10.02 "
         "(40 obligations); [[teal|certified]] 2026.10.04; [[teal|proved in Lean]] of its re-encoding (ADR-0053)"],
        ["`RulesFloor`", "`PromotionMeetsIssuedQuorum` (A1, replacing `NoPromotionWithoutAllGrantSeats`)",
         "[[red|not drafted]]"],
        ["`Promotion`", "`StaleVotesNeverCount`", "[[red|not drafted]]; owes decide-then-commit (G3), the ADR-0035 "
         "§5 tally condition, A2.2 and A2.3"],
        ["`BreakGlass`", "`BreakGlassNeverChangesAuthority`", "[[teal|drafted and checked]] 2026.09.23; "
         "[[teal|proved]] 2026.10.02 (37); [[teal|certified]]. Models X1: succeeded by `BreakGlass_A1`, "
         "`EmergencyNeverChangesAuthority`, 45 obligations, certified, with no assumption of R7 (2026.10.05). "
         "`BreakGlass` is also [[teal|proved in Lean]] (ADR-0053)"],
    ], size=13.5, accent="brown")
    hb = c.card(X0 + wl + 40, gy + h2 + 24, wr, "Bootstrap specification: partial (G5 §4; G12 §4, as at G11)", [
        "The anchor **may** bootstrap once a drafted TLA+ bootstrap specification exists: five modules, five "
        "invariants, each with a mutation that must fail. TLC checking is recommended, not required.",
        "Two of five exist, `Anchor` and `BreakGlass` with its successor, **proved and certified**. `Genesis`, "
        "`RulesFloor` and `Promotion` are still owed. The ceremony gains the seating of the first operators, at "
        "least three in each domain at the archetype (ADR-0029 A3, provisional), and floor fitness (A4). The trigger "
        "is unmet and remains optional; bootstrap itself is deliberately not on the open list (G12 §7).",
    ], accent="brown", size=14)
    hs = c.card(X0 + wl + 40, gy + h2 + 24 + hb + 24, wr, "Lineage gate suite: ADR-0035 §8's ratification items", [
        "1 · cases for E1–E5 and distillation, each seen to fire: **passes**.",
        "2 · monotonicity property check: **holds** in `bounded` (ADR-0035 R2, 09.28); failed as first drafted "
        "(`ratio`, E3 13/2000, distillation 241/2000).",
        "3 · E3 overlap: tool ready; first measurements at 20 MB; θ needs slices at training size.",
        "4 · a lineage projected from the reference's log matches its manifest: **done**; three tampers Contested.",
        "5 · an outside review of the bounded-share construction: [[red|owed]].",
    ], accent="amber", status="proposed", status_extra="ADR-0035", size=14)
    y = gy + max(h1, h2 + 24 + hb + 24 + hs) + 50

    # ================================================================ 4. the restatements
    y += c.heading(X0, y, "4 · The Rust tests that restate each property (`mechanism/GAPS-AND-ASSUMPTIONS.md` §6, "
                          "in full, and the tests named for the modules of G10)", size=22)
    y += c.para(X0, y, W, "Since 2026.09.30 the restatement is checked, not asserted, on every path a test takes: "
                "each state these tests build records its applied entries and `spec/mechanism-trace-run.sh` replays "
                "them through `Mechanism.tla`, and since 2026.10.02 every traced state is also read against "
                "`Confinement_A1.tla`'s invariants (`ConfinementRefinement.tla`). Since 2026.10.05 `operators.rs` and "
                "`emergency.rs` are traced too (A14). Nothing a test does not reach is checked. The same kind of "
                "evidence the TLC runs are, by the same hand. Row `SealCountsEffects, and M_ROUNDS carried over` is "
                "GAPS §6's text; the binding table says the seal breaks under `M_EMITSEQ`, not `M_ROUNDS` (ADR-0046 "
                "§5). Four rows say **proved of a model of `apply`**, **of the code's composition** or **of the code's "
                "arithmetic**: those are Lean proofs of a model or a transcription (ADR-0053, B36), not restatements by "
                "a test, and this diagram omitted them at G11. Since 2026.11.14 GAPS §6 has rows for `Paxos.tla` and "
                "`PaxosTrace.tla` (A20). GAPS §6 has no rows for the modules of G10; the table after it is from "
                "ADR-0033 A10 to A12 and A15.", 15, "muted") + 14
    t = [
        ["`Lease.tla`", "`LeaseAuthorityMonotone` / `M_RENEW`", "`mutations.rs` `lease_renewal_is_monotone_and_m_renew_is_refused`"],
        ["`Lease.tla`", "C1 one live lease", "`one_live_lease_per_principal`"],
        ["`Lease.tla`", "`NoActionUnderFencedEpoch` / `M_FENCE`", "`no_action_under_a_fenced_epoch_and_m_fence_is_refused`; e2e `FencedEpoch`"],
        ["`Lease.tla`", "`Rung0NeverContained` / `M_RUNG`", "`rung_zero_is_never_contained_and_says_why`; `confinement.rs` `contained_is_a_lookup_and_each_conjunct_matters`"],
        ["`Confinement.tla`", "`ContestedStopped` / `M_CONTESTED`; `NeverContested` at rung 1", "`confinement.rs` `a_contested_verdict_never_grants_and_revokes_the_principal`, `a_contested_verdict_ends_a_live_lease`; e2e `contain.rs` rogue image"],
        ["`Confinement.tla`", "`ContainedMeansConfined` / `M_UNBOUND` (at `Act`)", "`the_session_is_the_attested_guests_and_m_unbound_is_refused`, `renewal_re_attests_the_same_guest`; `contain.rs` `the_session_is_the_attested_guests`"],
        ["`Confinement.tla`", "`FreshAppraisal` / `M_STALE`", "`an_epoch_fence_invalidates_a_pending_appraisal`; `contain.rs` with the verifier held"],
        ["`Confinement.tla`", "`NoSilentDowngrade` / `M_DOWNGRADE`, `M_RENEWLOW`; `Lease_A1.tla` `M_LOWER`", "`no_silent_downgrade_at_grant`, `m_lower_and_m_renewlow_are_refused`; `contain.rs` renewal lapses"],
        ["`Confinement.tla`", "`ContainedMeansConfined` / `M_PROFILE`", "`contained_is_a_lookup_and_each_conjunct_matters`"],
        ["`Confinement.tla`", "`ContainedMeansConfined` / `M_HOST` at rung 1", "`contain.rs` `every_host_power_subtracts`: a lying rung-1 launcher is believed (T-0045-19)"],
        ["`Lease.tla`", "`LeaseAuthorityMonotone` / `M_ROLE` (ADR-0031 R1)", "`renewal_cannot_change_round_or_role_and_m_role_is_refused`"],
        ["`Lease.tla`", "`NeverSelectiveRevoke` witness (ADR-0031 R3)", "`a_targeted_revocation_ends_one_round_and_not_the_fleet`; e2e targeted revocation leaves a bystander live"],
        ["`Lease.tla`", "`RevokedStaysStopped` / `M_REVOKE` (ADR-0031 R3)", "`a_revoked_principal_persona_or_profile_is_not_granted_again_and_m_revoke_is_refused`"],
        ["`Seats.tla`", "`OnlyThinkersAuthor` / `M_KIND` (ADR-0037 §4)", "`alphabets_are_bounded_by_seat_kind_and_m_kind_is_refused`; `floor.rs` replays B10 and the tightened B6 (47 cases); e2e: the author's voter grant is refused"],
        ["`Seats.tla`", "`OneSeatPerPrincipal` / `M_SEAT` (ADR-0037 §1; finding 1: the reference's behavior before 2026.09.29)", "`one_seat_per_principal_and_m_seat_is_refused`"],
        ["`Coupling.tla`", "`UnreadBounded`, `NoAdmitWithoutLiveObserver`, **proved of a model of `apply`** (ADR-0039 §2)",
         "`lean/Topak/CouplingModel.lean` narrows the Seats-shaped model's oracle with the cross-round condition, round "
         "reuse, the round bound, heartbeat validity and coupling, keeping each lease's sequence, the watermarks and the "
         "seals; proves at any number of seats that a Run Thinker's live round has at most `K` effects unread by some "
         "cell Observer and its last round was read to the seal, both at once with one Observer in the cell, and that an "
         "admitted effect was covered; not a refinement of `Coupling`'s encoding; `lean/Admit-results-2026.10.06c.txt`. "
         "`lean/coupling-replay.sh`: 82 traces, all MATCH, 51 coupled admits and 34 heartbeats among them "
         "(`lean/CouplingReplay-results-2026.10.06.txt`). **Open:** with several Observers in a cell each half has its "
         "own witness, so no one Observer's unread is bounded (ADR-0053 finding 10); freshness is not checked at apply"],
        ["`Seats.tla`", "`OnlyThinkersAuthor`, `OneSeatPerPrincipal`, **proved of a model of `apply`** (ADR-0037 §1, §4)",
         "`lean/Topak/SeatsModel.lean` models `State::apply`'s grant, renewal, admit, end-of-round, revocation, fence and "
         "issuance arms on the leases, `live_by_seat` and the seat kinds, every other check an oracle that can only "
         "refuse; proves one live lease per principal and per seat, and alphabets and admitted acts within the seat's "
         "kind, at any number of seats, and the model a refinement of `spec/lean`'s `Seats` at its constants, on the "
         "premise that the log's indices increase; `lean/Admit-results-2026.10.06b.txt`. `lean/seats-replay.sh` replays "
         "the six suites' traces through the model: 82 traces, 1014 steps, all MATCH "
         "(`lean/SeatsReplay-results-2026.10.06.txt`); a copy of `state.rs` without §1's check fails it. **Open:** an "
         "issuance may change a seat's kind, which `validate_issuance` does not refuse though `types.rs` says it never "
         "changes; safe because an issuance ends every live lease (ADR-0053 finding 8)"],
        ["`Observers.tla`", "`DenyByAnyOf` / `M_QUORUM` (ADR-0038 §5)", "`a_correlator_on_the_veto_roster_vetoes_and_its_silence_does_not` (the tally is any-of over the veto roster); e2e: two veto seats silent, promotion completes"],
        ["`Observers.tla`", "`ReachIsBounded` / `M_REACH` (ADR-0038 §1)", "`a_cell_names_a_thinker_seat_in_its_domain_and_only_observers_have_one` (declared reach); **not enforced**: no topic read ACL (I8)"],
        ["`Coupling.tla`", "`NoAdmitWithoutLiveObserver` / `M_NOCOUPLE` (ADR-0039 §2)", "e2e `observer_liveness_couples_run_admits`: refused with no Observer lease, no heartbeat, and after `T_obs` (floor R3); `floor.rs` replays R3"],
        ["`Coupling.tla`", "`UnreadBounded` / `M_MARK`, `M_ROUNDS` (ADR-0039 §2)", "same e2e: refused at a backlog of `K`, refused on a fresh heartbeat with an unchanged watermark, refused a round-2 grant while round 1 is unread (`apply_grant`); `State::observer_covers` is the strict form"],
        ["`RunCoupling.tla`", "`UnreadEffectsBounded` / `M_EMITSEQ` (ADR-0042 §2; **the reference's behaviour before 2026.09.29**, D-0042-1)", "`mutations.rs` `the_sequence_counts_effects_and_m_emitseq_is_refused`; e2e `actuate_is_counted_recorded_and_sealed`: `K` invocations and no report, the next refused by R3"],
        ["`RunCoupling.tla`", "`ConsultNeverCoupled` / `M_COUPLEALL` (ADR-0041 §2)", "same two tests: a `Consult` admitted with no heartbeat at all, and again while `Actuate` and `Report` are refused for the backlog; `floor.rs` replays \"R3 does not couple Consult\""],
        ["`RunCoupling.tla`", "`SealCountsEffects`, and `M_ROUNDS` carried over (ADR-0042 §5)", "`a_run_round_seals_with_its_lease_and_a_run_seat_cannot_abstain`: a renewal does not seal, the seal is 3 after three invocations, and the round-2 grant waits on it; e2e: the grant refused with one invocation unread"],
        ["`RunCoupling.tla`", "`RoundBoundCountsAll` / `M_BOUNDEFF` (ADR-0042 §2)", "`the_round_bound_counts_consult`"],
        ["`RunSeats.tla`", "`OnlyThinkersActuate`, `ObserversConsultAndReport` / `M_KIND`; `NoNameCrossesDomains` / `M_DOMAIN` (ADR-0043 §2; ADR-0040 §2)", "`run_alphabets_are_bounded_by_seat_kind_and_domain`; `floor.rs` replays B10 over `Actuate` and R4 for an observer seat"],
        ["ADR-0042 §3, §4", "the `Actuate` record; `unknown` ahead of the seal; the late result withheld", "e2e `actuate_is_counted_recorded_and_sealed`. **Not modeled in TLA+**: `RunCoupling.tla` assumes a record at every sequence number"],
        ["ADR-0040 §1, ADR-0041 §4", "a retired name is an error, and an error is a deny", "`floor.rs` `a_retired_run_action_is_an_error_not_a_decision`"],
        ["`Coupling.tla`", "`CorrelatorNeverGates` / `M_CORR` (ADR-0039 §4)", "`Rules::cell_observers` excludes correlators from `live(o)`; e2e: the correlator is never granted a Run lease and Run admits proceed"],
        ["ADR-0039 §3 (ADR-0024 A2.3)", "coverage to the seal completes a promotion", "e2e `build_round_promotion_and_fencing`: every grant seat granted, `Tally::Stalled` until `o1` heartbeats `a1`'s seal"],
        ["`FloorComposition.tla`", "`AdmitImpliesFloorPermit` / `M_OVERRIDE`", "`admit_implies_floor_permit_and_m_override_is_refused`; e2e allow-all bundle still floor-bounded"],
        ["`FloorComposition.tla`", "`FloorErrorIsDeny` / `M_ERR`", "same test; `floor.rs` `an_incomplete_slice_is_a_deny_not_a_skipped_forbid`"],
        ["`FloorComposition.tla`", "`BundleRefusalHonored` / `M_FAILOPEN`", "`bundle_refusal_is_honored…`; `fallback.rs` (6 cases)"],
        ["`FloorComposition.tla`", "narrowing witness", "e2e: `Invoke` floor-permitted, bundle-refused"],
        ["`FloorComposition.tla`", "`AdmitImpliesFloorPermit`, `FloorErrorIsDeny`, `BundleRefusalHonored`, and §1 R4, "
         "**proved of the code's composition**",
         "`lean/Topak/Admit.lean` transcribes `admit.rs` (`floor_gate`, `compose`) and the call site in `mechanism.rs`, "
         "and proves the three properties, `admit ⟺ floor_permit ∧ ¬bundle_deny` (`admit_iff`), and that every floor "
         "deny names a reason, of the transcription; Lean 4 kernel, no Mathlib, no `sorry`, every constant replayed; "
         "`lean/Admit-results-2026.10.05.txt` (ADR-0053). The transcription's fidelity to the Rust is read, not checked "
         "(`lean/README.md`). **Since 2026.10.06 the decision refines the module**: `lean/Topak/FloorRefinement.lean` "
         "transcribes the `topak-floor` wrapper and proves the code's decision a `Decide` step of `spec/lean`'s "
         "re-encoding of the module, on Cedar's rule as the engine premise (T-0045-3), so all five of its invariants "
         "hold of every behaviour in which the code decides; the floor is the module's four policies, not the floor in "
         "force; `lean/Admit-results-2026.10.06.txt`"],
        ["ADR-0032 §2", "the subtracting interval fails closed: the margin moves expiry earlier, never later, **proved "
         "of the code's arithmetic**",
         "`lean/Topak/Clock.lean` transcribes `clock.rs` `subtracting_interval_elapsed` with `u64` saturating addition "
         "and proves it monotone in the margin and in `now`, equal to `now + margin ≥ start + len` where nothing "
         "saturates, and never elapsed before it starts when the margin is no longer than the interval; same results "
         "file. `Lease_A1.tla` abstracts time away, so no TLA+ property states this"],
        ["`RulesFloorNV_rev5.tla`", "each entry's mutation fails", "`every_rules_floor_entry_has_a_violation_it_catches`; e2e issuance rejections (R1+R9, R2, Authentic)"],
        ["`RulesFloorNV.tla`", "dropping R2 promotes with zero votes", "`without_r2_an_empty_roster_promotes_with_zero_votes`"],
        ["G2 §3", "a threshold needs ≥ 3 counted seats", "`a_threshold_needs_three_counted_seats_to_differ_from_unanimity`"],
        ["ADR-0024", "recusal, timeout ≠ grant, stale votes, veto", "four `tally` tests; e2e promotion"],
        ["`Voting` (cheat sheet)", "`OneValuePerBallot`, chosen-unique, agreement", "`topak-paxos/tests/sim.rs`, both mutations caught"],
        ["`Paxos.tla` (2026.11.14)", "`OneValuePerBallot`, `ChosenUnique`, `Agreement`, `LearnerSound`: the row above. "
         "`NoAmplification` (finding 9). Its four mutations",
         "`sim.rs`: the amplification check in `feed`; `mutation_requeue_on_step_down_is_caught` (caught by that check "
         "and no other); `a_host_that_does_not_persist_is_caught` (`M_NOPERSIST`); the two older mutation tests"],
        ["`PaxosTrace.tla` (2026.11.14)", "the replica's state after every call of `handle`, and what the call sent, "
         "are the model's",
         "`sim.rs` `traced_runs_under_faults` and `traced_runs_under_each_mutation`, recorded with `TOPAK_TRACE_DIR` "
         "set and replayed by `spec/paxos-trace-results.sh`. The host is the simulation's: `topak-node`'s driver and "
         "WAL are not traced"],
        {"group": "Named for the modules of G10, from the addenda that built them (ADR-0033 A10–A12, A15); not in "
                  "GAPS §6", "accent": "brown"},
        ["`Labels.tla` (ADR-0047 §11)", "the fold, the stale-`clearSet` refusal, `R5` to `R7`, clear and handle "
         "delivery, §11's scripted Run cell", "`mutations.rs` `the_rounds_labels_are_folded_and_a_stale_clear_set_is_refused`; "
         "e2e `labels_bound_what_a_round_may_send_after_what_it_has_read`; `floor.rs` (the stage's cases)"],
        ["ADR-0049 §6 (the allowlist entry)", "W1 to W9, each seen with a bundle built to fail it; W10 as restated "
         "at R4", "`allowlist.rs` (13): `w1_identity` … `w9_an_outward_entry_marks_a_destination_or_says_it_has_none`, "
         "`w10_a_field_the_record_does_not_define_is_refused`, the join and the delivery table; 38 Rego tests"],
        ["`ToolList.tla` (ADR-0048 §8)", "the list rendered at grant, the opening record first, the same answer "
         "all round", "e2e `the_tool_list_is_delivered_and_opens_the_round` (four of §8's five behaviours); the fifth "
         "is `w3_interface`"],
        ["`Operators.tla` (ADR-0050 §10)", "named for its properties", "`operators.rs` (6): "
         "`an_operators_lease_needs_a_sign_on_assertion`, `a_successor_grant_keeps_the_seating_and_never_widens`, "
         "`the_unsigned_path_seats_and_does_nothing_else`, `a_lapsed_operator_stops_its_own_domain_and_nothing_else`, "
         "`a_request_is_the_operators_and_is_not_replayed`, `three_operators_recover_a_lapse_and_two_cannot`; e2e "
         "`an_operator_is_a_principal_and_its_requests_are_decided`"],
        ["`Emergency.tla` (ADR-0052 §9)", "named for its properties", "`emergency.rs` (5): "
         "`an_emergency_lease_has_a_roster_quorum`, `an_emergency_lease_is_one_round`, "
         "`an_operator_ends_it_and_x1_is_retired`, `the_actions_are_the_persons`, "
         "`a_drill_is_a_real_activation_on_the_log`; e2e `break_glass_is_an_emergency_seating`"],
        ["ADR-0025 §1 (h)", "the two issued lists are read by well-formedness and admitted by the rules floor",
         "`mutations.rs` `the_two_issued_lists_are_admitted_by_the_rules_floor` (A15)"],
        {"group": "Named for the workflow modules (ADR-0033 A16, A17, both pending); **not traced**: `Mechanism.tla` "
                  "does not model workflows", "accent": "amber"},
        ["`Workflow.tla` (ADR-0054 §12, [[amber|Proposed]])", "the reference item's behaviours, each seen",
         "`topak-core` `workflow.rs`, among its 18: `a_workflow_loads_only_promoted_and_well_formed`, "
         "`a_fence_fails_a_node_not_yet_granted`, `a_route_applies_and_the_workflow_completes_by_its_sink`, "
         "`a_route_decided_before_a_finding_and_applied_after_is_void`, "
         "`a_second_route_to_a_consumed_decision_point_is_void`, `a_lapsed_orchestrator_fails_its_decision_point`, "
         "`a_computed_edge_fires_on_a_typed_attribute`, `only_the_orchestrator_routes_and_only_its_own_decision`, "
         "`an_untrusted_attribute_disables_the_edge_into_an_outward_node`, `a_clear_input_joins_the_receivers_clear_set`, "
         "`an_edge_waits_for_its_sources_coverage`; `topak-floor` `workflow.rs` (3), among them "
         "`a_clear_input_raises_the_receivers_clear_set_and_r5_then_refuses_its_outward_call`; e2e "
         "`a_workflow_is_run_by_its_promotion`"],
        ["`Mesh.tla` (ADR-0055 §11, [[amber|Proposed]])", "the reference item's behaviours, each seen at the "
         "replicated state; no mesh end to end",
         "`workflow.rs`: `a_mesh_loads_only_with_a_budget_and_two_coloured_clear_edges`, `the_loop_turns_twice_and_exits`, "
         "`the_budget_refuses_a_grant_and_the_workflow_fails`, `an_orchestrator_round_is_charged`, "
         "`a_finding_against_the_workers_round_voids_the_decision_nodes_next_route`, "
         "`a_route_decided_in_one_round_and_committed_after_it_ends_is_void`, "
         "`untrusted_content_read_on_the_loop_disables_the_exit`"],
    ]
    y += c.table(X0, y, [("Artifact", 330), ("Property / mutation", 1000), ("Rust test", W - 1330)], t,
                 size=13.5, accent="teal") + 50

    # ================================================================ 5. honesty layer
    y += c.heading(X0, y, "5 · The honesty layer: what none of the above claims", "red", size=22)
    y += 6
    y += c.para(X0, y, W, "G7 said, as every checkpoint since G3 had: \"no theorem is proved\". G8 was the first "
                "checkpoint under which a property of the corpus is **proved**, in ADR-0046 §1's sense; G10 is the "
                "first at which a proof can be **certified** (ADR-0046 A1), and it says in the same breath that a "
                "certified proof is not a verified one (G10 §8). G11 is the first at which the prover is known to be "
                "unsound, in two ways, and a second method proves the same theorems again (G11 §8). G12 is the first at "
                "which those two cases are reported upstream, and the first with ten more proof modules, every one "
                "under a Proposed record (G12, \"What G12 is\").", 15, "muted")
    y += 6
    g = 24
    w3 = (W - 2 * g) / 3
    cards = [
        ("Proved, checked, certified: three words", [
            "**Proved** names a claim TLAPS discharged and the hypotheses it was discharged under: thirty-four modules' "
            "invariants, ten of them of Proposed records (G12 §8). **Certified** names a proof whose every obligation "
            "is closed by the prover's normalization, a checked proof or LS4: thirty-one of them. **Checked** names "
            "TLC's evidence: the mutations and witnesses at small constants, since 2026.10.07 four leads-to "
            "properties, and since 2026.11.14 the consensus log's trace replay. None is used of the running reference "
            "(ADR-0046 §1, A1). A fourth, since Batch 36: **proved in Lean**, of an encoding, a transcription or a "
            "statement, never \"proved\" alone (ADR-0053 §1).",
            "Trace validation is drift detection against a model of the code: tested paths only, and it cannot check "
            "`ContainedMeansConfined`; a checked gate proof certifies an implication between two Cedar encodings, not "
            "the encoding (G8 §8). The theorem-to-premise table says what each property **assumed**."], "red"),
        ("Small constants; the prover as written", [
            "\"A property that holds at two principals and one epoch is evidence, not a proof\" (T-0045-29, G5 §8): "
            "since B25 that residual bounds the mutations and witnesses only. Model checking at practical constants: "
            "none yet (spec/README.md practice item 3; G10 §7, item 75 as at G9).",
            "TLC and the prover are trust-root rows (T-0045-29, T-0045-31), trusted as written: no mutation of either "
            "is run. **A certified proof still trusts the prover's translation of an obligation into a query, its "
            "normalization, LS4, and the checker** (G10 §3); three modules certify on nothing more than the prover as "
            "first configured (item 74). **And the translation is known to be unsound in two ways** (ADR-0046 A2): "
            "a scan and a reading say no cited result rests on either, and no check detects the first (item 104). "
            "Both are reported upstream (B39) and fixed upstream in part, in `ff40755`; **the pin has both**, and "
            "moving it is ADR-0077's open decision, Proposed (G12 §2.6, §8)."],
         "red"),
        ("The same hand", [
            "\"One record, six amendments and errata, three Lean packages, two liveness modules, two Proposed records "
            "with twelve pending amendments, two modules, a floor stage and a rebuilt reference are one hand's, "
            "drafted, built and checked across five days\" (G11 §4), as G10 said of the three days before it; and "
            "\"twenty-two Proposed records, four pending amendments, ten proof modules, a specification graph, a CI "
            "pipeline and a rung-1 run are one hand's, drafted, built and checked across five weeks, with no second "
            "reader\" (G12 §4). The certification wrapper, its driver, the scan and every result are the drafter's "
            "(B28, B37); so are the consensus log's model and its traced simulation (A20, B40, \"not reviewed by a "
            "reader other than the drafter\").",
            "The operational model was written from the code by the same hand: \"a model written from the code by the "
            "same hand agrees with the code\" (ToO §11.3). Breaking it on purpose, one modelled thing at a time, is "
            "the check that it can disagree (A14; G10 §5)."], "red"),
        ("What runs is neither checked nor proved", [
            "\"The invariants are proved, under named hypotheses, by the prover T-0045-31 ... Neither is a claim about "
            "the running reference\"; \"a Lean proof of the code is not a proof of the code\" (G11 §8, G12 §8). "
            "\"What runs is not the specification\" (ADR-0045 §5, R1): no refinement from the modules to the Rust "
            "exists and the build is asserted, not reproduced: trust-root rows T-0045-28 to 30, for every deployment.",
            "`Operators.tla` and `Emergency.tla` are tied to the reference by tests and no refinement (item 90); "
            "`Workflow.tla` and `Mesh.tla` by tests named after their properties and by no trace (A16): \"their "
            "modules are now proved; that does not ratify them\" (G12 §8). `Paxos.tla` is written from `replica.rs` "
            "and replayed against its runs: an operational model, checked and not proved, that \"does not claim a "
            "refinement of `Voting`\" (A20). The overlay's eight are of a design with no floor and no code (G12 §8)."],
         "red"),
        ("What the checks do not cover", [
            "A `holds°` is cedar's own term folding with no query to check: in the `emergency` stage's run, all 41 "
            "totality checks rest on the engine's row (T-0045-3), not the checker's (G9 item 69). For those 41, and "
            "the genesis floor's 23, a Lean proof under cedar-spec's model carries them since Batch 36 (ADR-0053 R3).",
            "The CPC signature is cvc5's own formalization, trusted as written (G7 §4). **The race in lease expiry had "
            "no property to violate**: the clock is outside every module, and it was found because a test failed one "
            "run in three under tracing, \"and no proof would have found it\" (ADR-0033 A13). Whether anything else a "
            "replica keeps is recorded after the lock is released was not audited (item 96). **No liveness property "
            "is proved**: coupling's four are checked at small constants (E4; item 105); five `ENABLED` invariants are "
            "proved, two for the emergency call and three in the overlay, under Proposed records (G12 §8). `Paxos.tla` "
            "states no liveness; delivery after the network heals is the simulation's check alone."], "red"),
        ("The chain still owed (ADR-0033)", [
            "Stage 1, trace validation: A5 (Batch 21), rerun at A6, widened at A7 and A8, not rerun at A10 to A12, and "
            "**current with the tree again at A14**; A15 changed nothing `apply` does; **behind it again since A16**, "
            "which `Mechanism.tla` does not model, and not rerun at A19 or A20 (B40). The consensus log gained its "
            "own stage one at A20, `PaxosTrace.tla`, run twice; it is of the simulation's host, not `topak-node`'s. "
            "Stage 2, a Lean model with differential testing, and stage 3, its compilation: \"the chain proper\", "
            "**not begun** (G12 item 56). "
            "\"Of the refinement chain's three items, none is discharged\" (A15). Proving two functions in Lean of a "
            "transcription (ADR-0053, B36) discharges none of them either. Since R4 a Lean model of `apply`'s "
            "seat and lease arms is proved to refine `Seats` and replayed against every recorded trace: stage 2's "
            "shape for one module, with an oracle for the rest of `apply`, and not the stage (ADR-0053 §5). R5 narrows "
            "that oracle with ADR-0039's checks and proves `Coupling`'s properties of the result; still not the stage.",
            "The reproducible build (T-0045-30) is untouched. Each addendum says which stage it discharges, and the "
            "rows leave Annex A only on that addendum."], "red"),
    ]
    hh = max(c.card(0, 0, w3, t_, b, accent=a, draw=False, size=14.5) for t_, b, a in cards)
    for i, (t_, b, a) in enumerate(cards):
        cx = X0 + (i % 3) * (w3 + g)
        cy = y + (i // 3) * (hh + g)
        c.card(cx, cy, w3, t_, b, accent=a, h=hh, size=14.5, tint=(i % 2 == 0), dash=None if i % 2 == 0 else "6 4")
    y += 2 * hh + g
    return c
