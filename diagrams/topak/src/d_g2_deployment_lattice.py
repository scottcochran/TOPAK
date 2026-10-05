"""G2 — The deployment lattice: degeneracy per axis, the archetype at the top of each, every declared record placed."""
import re

import lib
from lib import Canvas

ID, SLUG = "G2", "deployment-lattice"


def _boldfix(s):
    """Split a **bold** span that holds `code` into bold runs around the code (lib cannot nest them)."""
    segs = s.split("**")
    if len(segs) % 2 == 0:
        return s
    out = []
    for k, seg in enumerate(segs):
        if k % 2 == 0:
            out.append(seg)
        elif "`" in seg:
            parts = re.split(r"(`[^`]+`)", seg)
            out.append("".join(p if p.startswith("`") else (f"**{p}**" if p.strip() else p) for p in parts))
        else:
            out.append(f"**{seg}**")
    return "".join(out)


def build():
    orig = lib.parse
    lib.parse = lambda s: orig(_boldfix(s))
    try:
        return _build()
    finally:
        lib.parse = orig


# ---------------------------------------------------------------------------------------------
# Axes. Each: (axis name, source record + status line, archetype (title, body), nodes)
# node: dict(id, title, status, extra, body, parent: "prev" | "arch", accent, dash, sub)

def N(id_, title, status, extra, body, parent="prev", accent="red", dash=None, sub=None):
    return dict(id=id_, title=title, status=status, extra=extra, body=body, parent=parent, accent=accent, dash=dash,
                sub=sub)


TIER1 = [
    ("Approver fault tolerance", "ADR-0024 · Accepted (genesis), bootstrap set",
     ("`quorum` = every counted grant seat", ["At the archetype a promotion needs a grant vote from **every** grant seat "
                                              "on the roster (§2; ADR-0026 R1, R9)."]),
     [N("D-0024-1", "k-of-n grant seats", "accepted", "mechanism",
        ["**Deployed**: `quorum = k`, 1 < k < |counted grant seats|; relaxes R1.",
         "**Premise falsified**: no promotion without every grant seat.",
         "**Sacrificed**: tolerance of n−k Byzantine approvers. **Gained**: liveness under n−k absent approvers.",
         "Reachable since `quorum` takes a threshold; R9 keeps it ≥ 2 (the admission test working)."]),
      N("D-0024-2", "Single signer", "accepted", "mechanism",
        ["**Deployed**: `quorum = 1` with a single-seat roster; relaxes R1, R9 and R2. The pre-0024 status quo.",
         "**Premise falsified**: grants need consensus.",
         "**Sacrificed**: all approver fault tolerance; reintroduces a privileged human grant. **Gained**: throughput."]),
      ]),
    ("Anchor recoverability", "ADR-0025 annex · Accepted (genesis), bootstrap set",
     ("A-0025: strict unanimity, (n, 0)", ["`Authentic` = signed by every anchor key; n ≥ 3 `Mediated` key-holders, "
                                          "**at the gate**. Any permanent loss freezes the rules; exit is re-genesis. "
                                          "Ordered by capture threshold."]),
     [N("D-0025-2", "n−1 eviction with replacement, (n−1, 1)", "accepted", "declaration",
        ["**Premise falsified**: no key-holder is removed without their own consent.",
         "**Type change**: key-holders become **principals**; the gate moves to the genesis-declared eviction rule "
         "(ADR-0023 §4a).",
         "**Gained**: a compromised key-holder's permanent veto ends. One eviction per anchor epoch.",
         "Theorems voided: none stated (the §4a case)."]),
      N("D-0025-1", "TUF-style threshold with recovery, (k, n−k)", "accepted", "declaration",
        ["**Premise falsified**: rule changes carry unanimous consent.",
         "**Type change**: key-holders become **principals**; the gate moves to the genesis threshold-and-recovery rule.",
         "**Sacrificed**: a k-coalition can issue rules over n−k objections. **Gained**: liveness under n−k losses."]),
      N("(1, 0)", "Single custodian: no record", None, "",
        ["The annex lists the row with a dash. Genesis custody, which ADR-0029 names **not a degeneracy**; the corpus's "
         "own custody row is T-0045-11. The reference's dev keys and bundle key are also (1, 0) (G10 §7 items 11, 67)."],
        accent="grey", dash="2 3"),
      ]),
    ("Floor verification", "ADR-0030 §8 · Accepted (genesis), C1",
     ("A-0030: the floor on a verified evaluator", ["Cedar, linked, with a mechanized semantics (§2); monotone "
                                                    "composition `admit ⟺ floor_permit ∧ ¬bundle_deny` (§1). The "
                                                    "floor's text is **genesis-provisional** (A3): the proposed "
                                                    "floor's `emergency` stage, 28 policies, gated and not ratified "
                                                    "(G10 §2.2)."]),
     [N("D-0030-2", "Routing verdicts unchecked (A1)", "accepted", "declaration",
        ["**Deployed**: a `holds` from the solver is taken on trust.",
         "**Premise falsified**: a routing verdict is checked.",
         "**Voided**: none. **Lost**: §5's classification as a checked result; a wrong `holds` lets a relaxation reach a "
         "promotion without an issuance.",
         "**Every gate run before 2026.10.01**; not the reference's position since (B24)."], parent="arch"),
      N("D-0030-1", "A floor in Rego", "accepted", "mechanism",
        ["**Deployed**: Rego, with tests over a bounded schema and `RulesFloorNV`-style witnesses.",
         "**Premise falsified**: the floor's evaluator is faithful to a mechanized semantics.",
         "**Voided**: no containment theorem; `bundle ⊑ floor` survives. **Lost**: non-vacuity, never-errors and "
         "revision classification as **proven**; they become **measured**.",
         "Composition with D-0030-2: the gate is a reviewer's reading end to end."], parent="arch"),
      ]),
    ("Confinement rung", "ADR-0034 §8 · Accepted (genesis), C2, C4 · numbers ascend with strength",
     ("Rung 3: a confidential VM", ["Hardware report covering firmware, kernel, initrd, root hash, profile and Persona "
                                    "digests, appraised by an **independent verifier** (§2). The only rung where every "
                                    "residual host power is excluded (`M_HOST` holds). The reference reaches it only "
                                    "**SIMULATED**, under test keys (ADR-0033 A7, B29)."]),
     [N("D-0034-1", "Rung 2: measured boot", "accepted", "declaration",
        ["Premises falsified: none. Theorems voided: none.",
         "**Type change / TCB**: the hypervisor and host firmware enter the trusted base (T-0045-18). `M_HOST` at rung "
         "2 is a counterexample: launch-time only.",
         "At the reference rung 2 is a seam: `apply_grant` refuses it."]),
      N("D-0034-2", "Rung 1: a launcher asserts", "accepted", "declaration",
        ["Premises falsified: none. Theorems voided: none.",
         "**TCB**: the host operator and orchestrator enter (T-0045-19); Contested becomes unreachable.",
         "The reference's launcher issues it for real, on profiles that declare P3 `fail` (ADR-0033 A7, B29; "
         "G10 §2.3)."]),
      N("D-0034-4", "Rung 0: no attestation", "accepted", "declaration",
        ["**Premise falsified**: A1. **Voided**: every `Contained` theorem; every principal is `Mediated`.",
         "**At the reference** the rung is declared per seat (ADR-0023 §6c, B29): rung 1 real, rung 3 SIMULATED, "
         "rung 2 a seam; **no real principal is `Contained`** (G10 §2.3). An operator and an emergency seat are "
         "`Mediated` by design (ADR-0050 §1; ADR-0052 §1). `NeverContainedEffect` holds at rung 0, the declared "
         "vacuity."]),
      ]),
    ("Confinement profile clauses", "ADR-0034 §8, A2 (B30) · Accepted (genesis), C2, C4 · ADR-0036 §8 (Proposed)",
     ("Profile P1–P7 all hold", ["At the archetype the promoted profile fixes P1–P7, among them P3 (no interpreter "
                                 "reachable) and P4 (tools are Wasm, hermetic by construction). For Run, P4 is "
                                 "**channel fidelity** (A2, B30): each tool a Wasm component whose one network "
                                 "capability is its declared target, read from its allowlist entry."]),
     [N("D-0034-3", "Profile admits a native tool", "accepted", "declaration",
        ["**Premise falsified**: P4. **Voided**: every `Contained` theorem, for principals whose alphabet reaches that "
         "tool; they become `Mediated` (T-0045-23 excluded).",
         "The reference: every tool it runs in dev is native (`topak-demo-tool`, the MLX trainer); a Build profile "
         "that says P4 passes is not yet held to Wasm tools (G10 §7 item 83)."], parent="arch"),
      N("D-0036-1", "Profile has a reachable interpreter", "proposed", "as D-0034-3",
        ["**Premise falsified**: P3. **Voided**: every `Contained` theorem, for principals under that profile; they are "
         "`Mediated` (ADR-0034 §4). No participant changes type.",
         "D-0034-2 (rung 1) is inherited, not restated."], parent="arch", accent="amber"),
      N("D-0034-5", "A native Run tool behind an egress filter", "accepted", "declaration · A2, B30",
        ["**Deployed**: a native Run tool, under an egress filter in the tool host that admits only its declared "
         "target.",
         "**Premise falsified**: P4 (Run), as stated: channel fidelity moves from a check to a **trust**. **Voided**: "
         "none.",
         "**TCB**: the tool host enters for channel fidelity (T-0045-25 widens; T-0045-24 delegated on trust). "
         "`RunConfinement`'s invariants hold under it."], parent="arch"),
      N("D-0034-6", "A native Run tool, unfiltered", "accepted", "declaration · A2, B30",
        ["**Premise falsified**: P4 (Run). **Voided**: every `Contained` theorem, for Run principals whose alphabet "
         "reaches that tool; they become `Mediated`.",
         "The Run counterpart of D-0034-3. **The reference today for a native tool** (the record's words), "
         "T-0045-24 excluded for it; a Wasm Run tool is held to the target its entry declares (ADR-0033 A8, A9)."]),
      ]),
    ("Lineage strength", "ADR-0035 §9 · Proposed, R7",
     ("Projected", ["The lineage record is computed by the gate from the log, every round ingress-bounded (rung ≥ 1, "
                    "Attested, P1 and P2)."]),
     [N("D-0035-1", "Declared", "proposed", "kind not stated",
        ["**Deployed**: a rung-0 round in the DAG, an external base, an unbounded ingress or an empty consumed set.",
         "**Premise falsified**: §2's bound.",
         "**Voided**: no theorem (detection carries none); voids declaring archetype provenance. The tally condition is "
         "met by declared entries resting on the author's claim.",
         "Every lineage is declared today (the trainer runs outside the guest). **An operator's lineage is always "
         "declared**, rooted in its identity provider (R7)."], accent="amber"),
      ]),
]

TIER3 = [
    ("Labels and delivery", "ADR-0047 §10 · Accepted (genesis), C4; C2 for §3 · a parameter not on ToO §8.2's axis list",
     ("Every item labelled; delivered clear, or as a handle", [
         "Each admitted item of Run's ingress carries its source's label; the bundle's delivery table puts it in the "
         "clear, its label then in `clearSet`, or delivers a handle with no bytes. The floor's `R5` to `R7` forbid "
         "over labels (ADR-0047 §1–§3; ADR-0041 A1; ToO §2.10)."]),
     [N("D-0047-1", "No labels", "accepted", "mechanism",
        ["**Deployed**: labels and delivery modes → none: every admitted item delivered clear and unlabelled.",
         "**Premises falsified**: every item of ingress carries a label; a suppressed item's bytes do not enter the "
         "guest.",
         "**Voided**: none today: no theorem in force reads a label. Every property of `Labels.tla` is lost; F1 to F6 "
         "have nothing to read.",
         "**The reference before 10.05** (ToO §8.2; ADR-0033 A10). A table that delivers every label clear is not "
         "degenerate."]),
      ]),
    ("Tool list", "ADR-0048 §7 · Accepted (genesis), C4, C3 · a parameter not on ToO §8.2's axis list",
     ("The tool list, delivered by the mechanism", [
         "At the start of a round the Listener delivers the interface of every tool the lease may call, and the "
         "mechanism writes it to the round topic as the round's opening record (ADR-0048 §2; ToO §2.10)."]),
     [N("D-0048-1", "No tool list", "accepted", "mechanism",
        ["**Deployed**: the tool list not delivered: entries carry no interface, and a Thinker learns its tools from "
         "its Persona, its task or a consulted object.",
         "**Premise falsified**: a Thinker's description of a tool is bound to the entry's name and digest.",
         "**Voided**: none: no theorem reads a description."]),
      ]),
    ("Operators", "ADR-0050 §9 · Accepted (genesis) · provisional, C1, C3, C4 · parameters not on ToO §8.2's axis list",
     ("Signed, floored requests; first leases from a quorum; three or more operators per domain", [
         "Six control actions signed with the Persona's key and decided by `C1` to `C9` (§4); a first lease from a "
         "promotion, or for the first operators an anchor issuance (§2); **at least three operators in a domain** "
         "(§6 R5; ADR-0029 A3), each peer behind a **different identity provider** (§3, §6)."]),
     [N("D-0050-1", "The socket", "provisional", "mechanism",
        ["**Deployed**: operator requests unsigned, from whoever reaches the socket; grants at any time; no task "
         "carried.",
         "**Premises falsified**: every lease on the log was put there by a quorum or by an operator inside a "
         "quorum's grant; every stop is attributed.",
         "**Voided**: none in force: no theorem takes the operator as a premise. §10's properties are lost.",
         "**The reference before 10.05, and still its BOOTSTRAP path for a first seating** (ToO §8.2; ADR-0033 "
         "A11): whoever reaches the socket can seat (G10 §8)."], parent="arch"),
      N("D-0050-3", "Two operators in a domain", "provisional", "Deployment (the record's word)",
        ["**Deployed**: operators in a domain → two.",
         "**Premise falsified**: a lapsed operator's lease can be regranted by a peer.",
         "**Voided**: none. A lapse by either stalls the domain until a quorum seats it again (`Operators.tla` rows "
         "w8, w9)."], parent="arch"),
      N("D-0050-2", "One identity provider", "provisional", "Deployment (the record's word)",
        ["**Deployed**: operators' identity providers → one.",
         "**Premise falsified**: a peer is independent of the operator it watches.",
         "**Voided**: none; the peer rule holds in letter, and one provider can produce both.",
         "At the reference nothing compares two operators' providers, so it is not told from the archetype "
         "(ADR-0045 Annex B, A2)."], parent="arch"),
      ]),
    ("Emergency path", "ADR-0052 §8 · Accepted (genesis) · provisional, C1, C3, C4 · a parameter not on ToO §8.2's "
     "axis list",
     ("Break-glass is an emergency seating", [
         "A seat of kind `emergency`, held by a person, activated by the break-glass roster's quorum for one person "
         "and one round; no successor and no renewal; the activation is a forensic record (ADR-0052 §1; ADR-0033 "
         "A12). **X1 is retired**, on this provisional record (G10 §1.2, §8). A seating prepared by promotion is not "
         "built (G10 §1.2)."]),
     [N("D-0052-1", "X1-break-glass", "provisional", "mechanism",
        ["**Deployed**: the emergency path → `X1-break-glass`: an approval scoped to a seat and an epoch lets that "
         "seat, an agent's included, `Actuate` inside an issued envelope until the epoch ends.",
         "**Premises falsified**: a break-glass grant ends with its round; the actor under it is a person.",
         "**Voided**: none in force. §9's properties are lost.",
         "**The reference before 10.05** (ToO §8.2; ADR-0033 A12)."]),
      ]),
    ("Correlations computed", "ADR-0051 §9 · Proposed, not built (G10 §7 item 97)",
     ("A correlator computes the correlations of its table", [
         "ADR-0051 (Proposed) states the correlator's detection function; the deployed value below is \"the five → "
         "none\". A table that turns a correlation `off` is declared in the bundle and is not a degeneracy."]),
     [N("D-0051-1", "Heartbeats only", "proposed", "declaration",
        ["**Deployed**: correlations computed, the five → none. The seat exists and reports nothing but heartbeats.",
         "**Premise falsified**: a correlator computes the correlations of its table.",
         "**Voided**: none; §10's properties are lost. D-0038-2 with a seat filled.",
         "**The reference today** (the record's words)."], accent="amber"),
      ]),
]

TIER2 = [
    ("Observer scoping", "ADR-0038 §7 · Accepted (genesis), C3, C4",
     ("One `observer` seat per cell, plus a correlator", ["The cell Observer reads its Thinker's round topic in full; the "
                                                         "correlator watches every cell in its domain."]),
     [N("D-0038-1", "The shared group only (ADR-0008 as ratified)", "accepted", "declaration",
        ["**Deployed**: cell Observers one per cell → none, correlator kept.",
         "**Voided**: no safety theorem. **Lost**: bounded injection blast radius; one compromised correlator blinds "
         "every cell. In Run, usable only with D-0039-1."], parent="arch"),
      N("D-0038-2", "No correlator", "accepted", "declaration",
        ["**Deployed**: correlators 1 or more → 0. **Mitigation**: a facts-only correlator is the narrowing recorded "
         "here.",
         "**Voided**: no safety theorem. **Lost**: cross-principal detection (fragmentation, multi-agent coordination)."],
        parent="arch"),
      N("D-0051-2", "Correlators in a domain: two or more → one", "proposed", "Deployment (the record's word)",
        ["**ADR-0051 §9, Proposed**: it would put two or more correlators in a domain.",
         "**Premise falsified**: a correlator's silence on a correlation is a miss some other correlator counts.",
         "**Voided**: none. `marked-past` still covers cell Observers."], parent="arch", accent="amber"),
      ]),
    ("Observers per cell", "ADR-0037 §8 · Accepted (genesis), C3, C4 · a parameter not on ToO §8.2's list",
     ("1 or more `observer` seats per cell", ["Every cell has a leased `observer` seat (ADR-0037 §2)."]),
     [N("D-0037-1", "No Observer in a cell", "accepted", "declaration",
        ["**Deployed**: 1 or more → 0.",
         "**Voided**: no safety theorem. **Lost**: the cell's detection claims (`L`); in Build its artifacts cannot "
         "promote (ADR-0035 §5).",
         "In Run, usable only with D-0039-1: under coupling the cell never acts."]),
      ]),
    ("Emission retention", "ADR-0037 §8 · Accepted (genesis), C3, C4",
     ("Raw emission retained", ["The Thinker's raw emission is written to its round topic beside its typed action."]),
     [N("D-0037-2", "Raw emission not retained", "accepted", "declaration",
        ["**Voided**: no safety theorem. **Lost**: decoder faithfulness auditable after the fact; the record falls back "
         "to ADR-0018's concession (the typed action, not what the model emitted).",
         "Composes with nothing in ADR-0037."]),
      ]),
    ("Observer coupling", "ADR-0039 §7 · Accepted (genesis), C4",
     ("Run coupled", ["`R3-observer-live` and the cross-round grant condition in force. **`R3` is a Thinker's**: "
                      "an emergency seat is not coupled, by design (A2, B34; provisional with ADR-0052)."]),
     [N("D-0039-1", "Run uncoupled", "accepted", "mechanism",
        ["**Voided**: none. **Lost**: `UnreadBounded`, `UnreadEffectsBounded` (A1): the in-round bound loosens from `K` "
         "to `R`; across rounds, unbounded.",
         "Detection fails open against a dead, partitioned or starved Observer."]),
      ]),
    ("Effects counted", "ADR-0042 §7 · Accepted (genesis), C4 · a parameter not on ToO §8.2's list",
     ("`Actuate` and `Report` counted and recorded", ["Every effect-bearing admit advances `seq` and leaves a record an "
                                                     "Observer can mark."]),
     [N("D-0042-1", "Reports only", "accepted", "mechanism",
        ["**Voided**: none. **Lost**: `UnreadBounded` for invocations (`R`, not `K`, in a round; unbounded across).",
         "**The reference before 09.29** (closed at `1e6c0c4`, ADR-0033 A3). No loss beyond the union with D-0039-1."]),
      ]),
    ("Bundle signing", "ADR-0044 §5 · Accepted (genesis), C1 · a parameter not on ToO §8.2's list",
     ("Bundles signed under an issued key", ["A bundle is signed when its signature over the content revision verifies "
                                            "under a bundle key in the rules in force (§1)."]),
     [N("D-0044-1", "Signing off", "accepted", "kind not stated",
        ["**Deployed**: empty key set, unsigned load. **Voided**: ADR-0030 §2's \"Signed\".",
         "A swapped tarball with a matching manifest is trusted.",
         "**The reference before 10.01**; not since ADR-0033 A6 (B23): an empty key set now loads nothing."]),
      ]),
    ("Trusted base", "ADR-0045 §8 · Accepted (genesis), C2, C4",
     ("Annex A declared, row by row", ["Every row a deployment relies on is declared with its class; an undeclared "
                                       "row is false (§3 rule 1)."]),
     [N("D-0045-1", "No trusted-base declaration", "accepted", "declaration",
        ["**Premises falsified**: every row. **Voided**: every theorem with a premise node: **the bottom of every "
         "axis**, holding the mechanism constants and nothing else.",
         "The reference before Annex B; every deployment before it declares."], accent="red"),
      ]),
]


def _column(c, x, y, w, axis, src, arch, nodes):
    """Draw one axis column, archetype at the top. Returns bottom y."""
    gut = 26
    cx = x + gut
    cw = w - gut
    c.text(x, y + 18, axis, 18, "ink", bold=True)
    yy = y + 28
    yy += c.para(x, yy, w, src, 13, "muted") + 10
    ah = c.card(cx, yy, cw, "Archetype · top: " + arch[0], arch[1], "blue", size=13.5, bullets=False)
    arch_bottom = yy + ah
    prev_bottom = arch_bottom
    yy += ah + 46
    for nd in nodes:
        title = (nd["id"] + " · " + nd["title"]) if nd["id"] else nd["title"]
        h = c.card(cx, yy, cw, title, nd["body"], nd["accent"], status=nd["status"], status_extra=nd["extra"],
                   size=13.5, dash=nd["dash"], sub=nd["sub"])
        if nd["parent"] == "prev" or prev_bottom == arch_bottom:
            if nd["accent"] == "grey":
                c.arrow([(cx + cw / 2, prev_bottom), (cx + cw / 2, yy)], "grey", dash="2 3")
            else:
                c.arrow([(cx + cw / 2, prev_bottom), (cx + cw / 2, yy)], "red", dash="7 5")
        else:
            c.arrow([(x + 11, arch_bottom - 20), (x + 11, yy + 26), (cx, yy + 26)], "red", dash="7 5")
            c.line(cx, arch_bottom - 20, x + 11, arch_bottom - 20, "red", 2, "7 5")
        prev_bottom = yy + h
        yy += h + 46
    # every chain ends at D-0045-1
    yy -= 20
    if nodes[-1]["id"] == "D-0045-1":
        return yy
    c.arrow([(cx + cw / 2, prev_bottom), (cx + cw / 2, yy + 6)], "grey", dash="2 3")
    c.pill(cx + cw / 2, yy + 8, "⊥ D-0045-1: no trusted-base declaration", "red", 12, dash="4 3", anchor="middle")
    return yy + 34


def _build():
    c = Canvas(ID, "The deployment lattice: degeneracy per axis, the archetype at the top of each, every declared record "
                   "placed",
               "ADR-0023 (Accepted (genesis) 2026.09.23, confirmation required C3; A1, Batch 29: the declared rung is "
               "per seat, §6c) replaces the ladder: a deployment is the archetype with named parameters driven to "
               "limiting values, the effect is premise loss, and rungs are per axis. Below, every axis ToO rev 14 §8.2 "
               "names, and every record-level degeneracy entry placed on its axis with its deployed value and what it "
               "voids, among them the six of Batch 34's records (two of those records provisional) and two of ADR-0051 "
               "(Proposed). Arrows point down the lattice, toward degeneracy.",
               3600, "ADR-0023 §1–§7, A1 §6c and carried scope (B3, R3, R4, B13, B29); ADR-0024 Degeneracies; ADR-0025 "
               "Annex; ADR-0029 A3, A4; ADR-0030 §8, A3; ADR-0034 §2, §8, A2 (B30); ADR-0033 A7 (B29), A8 (B31), A9 "
               "(B32), A10 to A12 (B34); ADR-0035 §1 R7, §9 (Proposed); ADR-0036 §8 (Proposed); ADR-0037 §8; ADR-0038 "
               "§7; ADR-0039 §7, A2; ADR-0041 A1; ADR-0042 §7; ADR-0044 §5; ADR-0045 §8, Annex B (A2); ADR-0047 §1–§3, "
               "§10; ADR-0048 §2, §7; ADR-0050 §1–§4, §6, §9 (provisional); ADR-0051 §9 (Proposed); ADR-0052 §1, §8 "
               "(provisional); ADR-0017; ADR-0028 §3; ADR-0005 (B27); ToO rev 14 §2.10, §8.1–§8.3; "
               "derived/topak-rungs-axes-degeneracies-accounting-2026.09.26.md; "
               "mechanism/GAPS-AND-ASSUMPTIONS.md G19; G10 §1.1, §1.2, §2.2, §2.3, §2.5, §8, §7 items 5, 6, 7, 11, 38, "
               "40, 64, 67, 80, 83, 85, 97")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y
    sx = X0
    sx += c.status(sx, y, "accepted", "C3 · Batch 3, 2026.09.23") + 14
    c.text(sx, y + 16, "C3 because §5 reversed ADR-0008's Observer scoping (now superseded by ADR-0038) and ADR-0017's "
                       "ordering-primacy clause (supersession unwritten) in effect. **Nobody ships the archetype.** No "
                       "deployment declaration has been written (G10 §8).", 14.5, "muted")
    y += 52

    # ======================================================================== the relation
    w4 = (W - 3 * 24) / 4
    specs = [
        ("§1–§3 · Degeneracy, premise loss, a unique maximum", [
            "**Degeneracy**: D is a degenerate form of archetype A iff D is obtained from A by driving one or more named "
            "mechanism parameters to a limiting value. “degenerate” is the formal register, “reduced” the operational.",
            "**The effect is premise loss, not weakening**: each limit is bound to the premises it falsifies; the "
            "inventory is A's minus every theorem whose premises are no longer discharged. No partial credit.",
            "**The archetype is the unique maximum** of the parameter lattice: a reference point, not required to be "
            "shippable. Precedent: ISO 26262's safety element out of context (SEooC).",
        ], "blue"),
        ("§4, §4a · The admission test, with type changes", [
            "A variation is a rung only if it is **reachable from A by parameter limit**. If it holds a capability A "
            "lacks, A is incomplete and must be extended first: **a rejection is a finding about the archetype**.",
            "**Type changes are admission conditions too**: a variation that changes a participant's type (key-holders "
            "from the gate to principals under D-0025-1, D-0025-2) can void no theorem at all while moving what the "
            "theorems are about. It must declare the change, the gate's new place and the trusted-base effect.",
        ], "blue"),
        ("§5, §7 · Rungs per axis; composition owned here", [
            "**Rungs are per-axis**: a deployment's position is a tuple; the unqualified phrase \"rung demotion\" is "
            "barred.",
            "**Composition is not assumed monotone**: two limits may jointly falsify a premise neither falsifies alone. "
            "Above one parameter the **composition note names the delta**; an empty delta is a claim; **a missing note "
            "is not an empty delta** and fails at the Build promotion gate (§7b).",
            "The gate can check the note exists, not that its delta is correct.",
        ], "blue"),
        ("Deferred: the archetype-evolution record (unwritten)", [
            "**Archetype versioning**: conformance binds to (archetype version, rung tuple); published versions freeze.",
            "**Dominance rule**: on a paired axis the archetype moves only to Pareto-dominating values.",
            "**Non-increasing TCB** across versions (now checkable row set against row set, ADR-0045 §4).",
            "**Until it exists, nothing bounds how the archetype grows** under §4 (ToO §8.2; G10 §7 item 7). Also open: the "
            "axis set is not enumerated; finiteness of each chain is unproven.",
        ], "red"),
    ]
    hs = [c.card(0, 0, w4, t, b, a, draw=False, size=14) for t, b, a in specs]
    hh = max(hs)
    for i, (t, b, a) in enumerate(specs):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, a, h=hh, size=14, dash="6 4" if a == "red" else None,
               tint=a != "red")
    y += hh + 40

    # schema + rung orderings
    sw = 1700
    sth = c.table(X0, y, [("§6 declaration field", 330, {"bold": True}), ("Content", sw - 330)], [
        ["Kind (§6a)", "**Mechanism** degeneracy: changes a value inside the verified object, reopens the proofs that "
         "quantify over it, ships as a mechanism release. **Declaration** degeneracy: changes something outside it, "
         "reopens nothing"],
        ["Parameter", "The named mechanism parameter driven to a limit"],
        ["Archetype value", "Its value at the unique maximum"],
        ["Deployed value", "Its limiting value in this deployment"],
        ["Premises falsified", "The theorem premises the limit falsifies"],
        ["Theorems voided", "The inventory loss. No field exists for a checkable property that is not a safety theorem: "
         "a properties-lost field is proposed (ADR-0037 finding 6; G10 §7 item 40)"],
        ["Type changes (§6b)", "For each participant whose type changes: archetype type, deployed type, where the gate "
         "sits, what enters or leaves the trusted base. Empty is a claim: \"no participant changes type\". To be stated "
         "as ADR-0045 row ids: the §6b amendment and the declaration template are still owed (G10 §7 item 64)"],
        ["Declared rung per seat (§6c, A1, B29)", "For every seat the issued rules declare, the confinement rung its "
         "leases are granted at and the ADR-0045 Annex A rows that rung rests on. Rung 0 is `Mediated`; rung ≥ 1 is "
         "granted only on an Attested appraisal at that rung, and any other rung is refused. **Changing a seat's rung "
         "is an issuance.** The reference carries it as `SeatDecl.rung` (I37)"],
        ["Mitigation", "Optional"],
        ["Composition note", "Mandatory above one parameter (§7a)"],
    ], size=13.5, accent="blue")
    ox = X0 + sw + 30
    ow = X1 - ox
    oth = c.table(ox, y, [("\"Rung\" carries four orderings (09.26 accounting; ToO §8.2)", 560, {"bold": True}),
                          ("Source", 420), ("Direction", ow - 980)], [
        ["Position on one axis; a deployment is a tuple", "ADR-0023 §5 (Accepted, C3)", "Abstract, per axis"],
        ["Provenance: archetype, 1 fine-tune, 2 attested external, 3 asserted external", "ADR-0017 (ordering-primacy "
         "reversed in effect)", "Numbers ascend with **weakness**; the archetype is unnumbered"],
        ["Confinement attestation: 0 none, 1 launcher, 2 measured boot, 3 confidential VM", "ADR-0031 §3, ADR-0034 §2",
         "Numbers ascend with **strength**; the archetype is 3"],
        ["Custody: A-0025, D-0025-2, D-0025-1, (1, 0)", "ADR-0025 annex", "Ordered by capture threshold"],
    ], size=13.5, accent="grey")
    c.para(ox, y + oth + 14, ow, "**Always qualify \"rung\".** The 09.17 glossary said rename one; the 09.26 glossary "
           "downgraded that to \"always qualify\". Record-level entries are not deployment declarations, and the 09.26 "
           "accounting notes that no record yet says how the two differ (ToO §8.2).", 14)
    y += max(sth, oth + 90) + 56

    # ======================================================================== the lattice
    y += c.heading(X0, y, "The lattice, axis by axis: archetype at the top, each declared record below it, every chain "
                          "ending at D-0045-1", "ink", 22)
    y += c.legend(X0, y, [("box", "blue", "archetype value (the top of the axis)"),
                          ("arrow", "red", "degeneracy: a parameter driven toward its limit", "7 5"),
                          ("box", "red", "record-level entry (Accepted)"),
                          ("box", "red", "entry in a provisional record (ADR-0050, ADR-0052): in force, subject to "
                           "redesign", "4 3"),
                          ("box", "amber", "entry in a Proposed record, not in force", "6 4"),
                          ("box", "grey", "a position with no record", "2 3")], title="Reading") + 20
    for tier in (TIER1, TIER2, TIER3):
        n = len(tier)
        gap = 28
        cw = (W - gap * (n - 1)) / n
        bottoms = []
        for i, (axis, src, arch, nodes) in enumerate(tier):
            bottoms.append(_column(c, X0 + i * (cw + gap), y, cw, axis, src, arch, nodes))
        y = max(bottoms) + 60

    # ======================================================================== named axes with no declared record
    y += c.heading(X0, y, "Axes named in ToO §8.2 with no declared record yet", "ink", 19)
    w4 = (W - 3 * 24) / 4
    specs = [
        ("Persona provenance (ADR-0017)", [
            "**Archetype**: in-house pre-train, two independent lineages. Rungs 1 to 3 (fine-tune, attested external, "
            "asserted external) are positions in ADR-0017's table, not D-records.",
            "Its claim to be the axis is reversed in effect by ADR-0023 §5; supersession unwritten (G10 §7 item 6). "
            "ADR-0035 (Proposed) adds distillation at rung 1.",
        ]),
        ("Event-log legibility (ADR-0028 §3)", [
            "**Archetype**: horizon = the lifetime of the rules-epoch chain; audit authority = the anchor plus a declared "
            "external auditor role.",
            "**Shortening either** is a legibility degeneracy; none is declared. The forensic horizon and audit "
            "authority are folded into this axis (09.26 accounting).",
        ]),
        ("Effect-stream role (ADR-0005, Accepted (genesis), C4, B27)", [
            "At the archetype Kafka is a transport with a durability window, and the archive is the system of record "
            "(the Paxos log orders); lower profiles may subtract toward native-log ordering (09.12 review note).",
            "**Deployment position** (ADR-0005): a deployment that reads order from the transport, or keeps the "
            "transport as its record, is a degeneracy of its own declaration; **none is declared**. Ratified, "
            "discharging G9 item 5 (G10 §1, §7).",
        ]),
        ("HITL / HOTL / HOOTL posture (\"arguably\")", [
            "Named as a candidate parameter by ADR-0023's obligations and ToO §8.2 (\"arguably\"). Build's gate is a "
            "quorum of `Mediated` grant seats; Run is human-on-the-loop.",
            "No record states an archetype value for it as an axis, and no entry is declared.",
        ]),
    ]
    hs = [c.card(0, 0, w4, t, b, "grey", draw=False, size=14) for t, b in specs]
    hh = max(hs)
    for i, (t, b) in enumerate(specs):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, "grey", h=hh, size=14, dash="2 3")
    y += hh + 30
    c.para(X0, y, W, "**The five Observer and retention entries** (D-0037-1, D-0037-2, D-0038-1, D-0038-2, D-0039-1) "
           "**void no safety theorem**, because the Observer is deny-only, and state their losses in prose; so do D-0042-1 "
           "and D-0030-2. Confinement rungs 1 and 2 void no theorem and move what the theorems rest on, as D-0034-5 "
           "does. **None of the eight entries of ADR-0047 to ADR-0052 voids a theorem in force.** D-0047-1, D-0050-1, "
           "D-0051-1 and D-0052-1 lose the properties their record's ratification condition states, and the binding "
           "table has no rows for those modules yet (G10 §2.6, item 90); under D-0050-3 every safety property holds. Three of them, D-0050-1, "
           "D-0052-1 and D-0047-1, were the reference's position until 2026.10.05; D-0050-1 still is for a first "
           "seating. **No deployment declaration has been written, and no deployment conforms** (G10 §8).", 14.5)
    return c
