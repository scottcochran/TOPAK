"""A1 — Roles map: the letters name roles, not products."""
from lib import AMENDED_G12, Canvas

ID, SLUG = "A1", "roles-map"

# (letter, role, accent, obligation, reference instrument, (status, extra) for the instrument or None, not-claimed)
COLS = [
    ("T", "Formal specification, model checking and proof", "teal",
     "Specify every guarantee against what an agent's alphabet allows, and check it, with a mutation that must fail "
     "for every property.",
     "TLA+: TLC over the pinned `tools/tla2tools.jar` (`tools/TLA-PIN`) **checks** every mutation and witness. The TLA+ "
     "Proof System (`tlapm`, T-0045-31) **proves** the invariants of **thirty-four** modules, **13,622 obligations**, "
     "every one proved; ten of the thirty-four are under Proposed records (ADR-0046; G12 §2.9). **Thirty-one certify**: "
     "every SMT obligation closed by a proof the `ethos` checker accepted, cvc5 behind `spec/smt-checked` (ADR-0046 "
     "E2, A1). **Lean 4** proves fifteen modules' theorems again, of re-encodings, on its own kernel (T-0045-37; "
     "ADR-0053; G12 §2.9). Properties restated as Rust tests with the same mutations, and every tested behaviour "
     "replayed through `spec/Mechanism.tla`: **82 traces, 1,007 steps**, every one matching (ADR-0033 A14), behind "
     "the tree since the workflow build. Since 2026.11.14 the consensus log too: `spec/Paxos.tla` **checked** in TLC "
     "and the simulation's runs replayed through `spec/PaxosTrace.tla`, **8 traces, 3,302 events**, every line as "
     "expected (ADR-0033 A20, Batch 40)",
     None,
     ["Mutations and witnesses checked at small constants; invariants proved **of the modules**, not of the code "
      "(ADR-0046 §2).",
      "**A certified proof is not a verified one**: the prover's translation, its normalization, LS4 and the checker "
      "are trusted, and the translation is **known to be unsound in two ways** (ADR-0046 A2), reported upstream "
      "(A3, Batch 39) and fixed there in part; **the pin, `7824dab`, has both** (G12 §2.6). Three modules do not "
      "certify: `RulesFloorNV_rev5`, `Confinement`, `Confinement_A1` (G12 §2.9, §8).",
      "No liveness property is proved: coupling's are checked by TLC; five `ENABLED` invariants are proved, three of "
      "them under Proposed records (G12 §8).",
      "`Paxos.tla` is **checked, not proved**, at three replicas and one round; `Voting` is not written as a module "
      "(ADR-0033 A20).",
      "A matching trace is drift detection, **not a refinement** (T-0045-28 stays a trust root)."]),
    ("O", "Policy as code: a verified floor and a per-request bundle", "blue",
     "Floor tier: an evaluator with a mechanized semantics, an implementation checked against it, and a decidable "
     "comparison of two policy sets. Bundle tier: per-request, signed, subtract-only.",
     "Floor: Cedar (`cedar-policy`, the Rust engine) **linked** into the replica, the gated floor compiled in by path "
     "and refused unless its digests match: since 2026.10.08 the proposed floor's `workflow` **stage** (30 policies, "
     "123 cases), **Proposed and not in force**; the floor in force is the `emergency` stage (28, 107; G12 §2.2; "
     "ADR-0033 A12, A16). Bundle: OPA/Rego sidecar with an in-process WASM fallback bound to the lease's revision, loading only "
     "a bundle signed under an issued key (ADR-0044) whose allowlist is well-formed (ADR-0049)",
     ("genprov", "the floor, ADR-0030 A3"),
     ["Rego has no mechanized semantics, so it cannot hold the floor tier (D-0030-1 if it does).",
      "`admit ⟺ floor_permit ∧ ¬bundle_deny` (ADR-0030 §1).",
      "**No floor is ratified**: the bootstrap reviewer establishes fitness, and nothing written says what fit "
      "means (G12 §8; item 87).",
      "The floor the reference follows is not the floor in force (G12 §2.2, item 102)."]),
    ("P", "Consensus over the control plane", "violet",
     "Order every grant and every authority fact in one log; the log index is the fence. Consensus for grants, "
     "local for denials.",
     "Sans-IO crash-recovery Multi-Paxos (`topak-paxos`): a `Voting` ghost under message-level `Paxos`, driven by a "
     "deterministic simulation that checks `Voting`'s invariants on every durable vote. Since 2026.11.14 the log is "
     "**modelled**: `spec/Paxos.tla`, one operator per function of `replica.rs`, four mutations and ten witnesses, "
     "**checked** in TLC (29 rows, every one as expected); its recorded runs replay through `spec/PaxosTrace.tla` "
     "(8 traces, 3,302 events). ADR-0033 finding 9 is closed (A20, Batch 40)",
     None,
     ["Replicas are crash-recovery, **not Byzantine** (ADR-0033 §3).",
      "Replica set is trust-root row T-0045-1; mutual authentication between replicas is unbuilt (ADR-0045 "
      "Annex B).",
      "`Paxos.tla` is checked at three replicas, one round and two leaders, **not proved**; the host replayed is the "
      "simulation's, not `topak-node`'s driver and WAL (ADR-0033 A20)."]),
    ("A", "Agents: the principals doing the work", "pink",
     "Every agent is Byzantine at every position. It reaches the world only through a typed alphabet; models stay out "
     "of the trusted computing base.",
     "The alphabet as MCP tools and nothing else, on a front door the mechanism owns (`topak mcp`, stdio, bearer "
     "token); downstream tools reached as MCP servers. A guest the node launches is bridged on stdio and mints no "
     "token (ADR-0033 A7). In Run every item delivered carries a **label**, clear or as a **handle**, and the round "
     "opens with the **tool list** (ADR-0047, ADR-0048; A10). **Operators** send signed requests the floor's `C1`–`C9` "
     "decide (ADR-0050; A11); an **emergency seat** is activated by the roster's quorum and signs each action "
     "(ADR-0052; A12). An `orchestrator` seat chooses among a workflow's enabled edges with `Route` (ADR-0054, "
     "Proposed, its module proved at R7; A16 pending)",
     ("provisional", "ADR-0050, ADR-0052"),
     ["The alphabet is the whole **protocol**, not the whole **channel**: a process with a shell never has to ask.",
      "Leases at rung 0, rung 1 on profiles that declare P3 `fail`, rung 3 only **SIMULATED**: **every real "
      "principal is** `Mediated`; an operator and an emergency seat by design. One compiled occupant passes P3 at "
      "rung 1 on DEV rules, outside the reference's tests and with no criterion in force; **no real principal is** "
      "`Contained` (G12 §2.3, §8).",
      "[[red|BOOTSTRAP]]: the unsigned operator socket seats and does nothing else; a first lease from a quorum is "
      "**not built** (G12 §8; item 88).",
      "A label is one replica's computation, a declaration and not a finding (G12 §8; item 93)."]),
    ("K", "Event transport", "amber",
     "Transport with a durability window. Neither the ordering authority (that is the Paxos log) nor the system of "
     "record (that is the archive).",
     "Kafka via `rskafka` (`acks=all`), one single-partition topic per principal per round, opening with the tool "
     "list (ADR-0042 A1); emissions after commit, denials unordered, an `after` companion past the seal.",
     ("accepted", "ADR-0005 · C4"),
     ["The K row rests on **ADR-0005, ratified in Batch 27**: the debt ADR-0033 §2 carried since Batch 7 is "
      "discharged; author-ratified until confirmed (C4).",
      "Archive and erasure: not built; the archive's records, ADR-0071 to ADR-0076, are Proposed and nothing is "
      "built (G12 item 116)."]),
]


def build():
    c = Canvas(ID, "The letters name roles, not products",
               "Each letter of TOPAK carries an obligation. Any instrument that meets the obligation may be substituted "
               "for the reference's choice; the floor tier cannot change language without ADR-0030.",
               2200, "ToO rev 16 §1, §2.3, §2.10, §2.11, §3.1, §4.2, §5.5, §7.10, §7.11, §11.3, §12, §15; ADR-0030 §1–§3, A3; "
               "ADR-0033 §1–§3, §7 finding 9, A7, A10–A12, A14, A16, A17, A19, A20, B40; ADR-0053; ADR-0054 (Proposed, R7); "
               "ADR-0046 A2, A3; ADR-0005 (Batch 27); ADR-0042 A1; ADR-0044; ADR-0045 T-0045-1, T-0045-28, T-0045-29, "
               "T-0045-31, Annex B; ADR-0046 §1, §2, E2, A1; ADR-0047; ADR-0048; ADR-0049; ADR-0050 and ADR-0052 "
               "(provisional); ADR-0071 to ADR-0076 (Proposed); G12 §1, §2.2, §2.3, §2.6, §2.9, §3, §8, §7 items 87, 88, "
               "93, 102, 116; spec/Paxos.tla, spec/PaxosTrace.tla, spec/Paxos-results-2026.11.14.txt, "
               "spec/Paxos-trace-results-2026.11.14.txt; mechanism/README.md; mechanism/corpus-pins.sha256; README.md")
    c.note = AMENDED_G12
    x0, gap = c.x0, 24
    n = len(COLS)
    w = (c.x1 - x0 - gap * (n - 1)) / n
    y = c.y

    # premise band
    h = c.card(x0, y, c.x1 - x0, "The premise every column serves", [
        "An agent is **Byzantine at every deployment position**. Safety cannot depend on what a model means or intends, "
        "so models stay out of the trusted computing base and every guarantee is stated against an agent that may do "
        "anything its alphabet allows (ADR-0007).",
    ], accent="red", bullets=False, size=15)
    y += h + 40

    # measure rows so each band lines up across columns
    ob_h = max(c.card(0, 0, w, "Obligation (the role)", [col[3]], draw=False, bullets=False) for col in COLS)
    in_h = max(c.card(0, 0, w, "Reference instrument", [col[4]], draw=False, bullets=False,
                      status=col[5][0] if col[5] else None, status_extra=col[5][1] if col[5] else "")
               for col in COLS)
    no_h = max(c.card(0, 0, w, "What the reference does not claim", col[6], draw=False) for col in COLS)

    for i, (L, role, acc, obl, inst, st, notes) in enumerate(COLS):
        x = x0 + i * (w + gap)
        # letter tile
        c.rect(x, y, w, 150, acc, tint=True, rx=12, sw=2.2)
        c.text(x + 22, y + 92, L, 84, acc, bold=True)
        c.para(x + 100, y + 30, w - 120, role, 18, acc, bold=True)
        yy = y + 150 + 18
        c.card(x, yy, w, "Obligation (the role)", [obl], accent=acc, bullets=False, h=ob_h, tint=False)
        yy += ob_h + 14
        c.card(x, yy, w, "Reference instrument", [inst], accent="grey", bullets=False, h=in_h,
               status=st[0] if st else None, status_extra=st[1] if st else "", dash=None)
        yy += in_h + 14
        c.card(x, yy, w, "What the reference does not claim", notes, accent="red", h=no_h, tint=False, dash="6 4")
    y += 150 + 18 + ob_h + 14 + in_h + 14 + no_h + 40

    sub_body = [
        "Any row may change without amending the record, provided the replacement meets the role's obligation and the "
        "change is recorded in the reference's assumptions register.",
        "The floor row cannot change language without ADR-0030: Cedar meets the floor obligation; Rego does not.",
        "Nothing translates: a Rego→Cedar transpiler would be a Build artifact whose output becomes the enforced floor.",
    ]
    ref_body = [
        "`mechanism/` implements the admit path end to end for Build's six actions and Run's three (ADR-0033 §1), an "
        "operator's six control requests and an emergency seating, rebuilt in five stages on 2026.10.05; since "
        "2026.10.08 workflows and meshes, built to records that are Proposed (A16, A17 pending); measured for G12 at "
        "`d1b72db` (A19) and after the consensus log's model at `36269bc` (A20), both ratified in Batch 40, "
        "2026.11.17: **159 tests across fifteen binaries** and 38 Rego tests (ADR-0033 A9–A20; G12 §3).",
        "It has never been promoted, nothing in it is in any TCB, and it is not a deployment: it fails assumption of "
        "use A1.",
        "It is cited like a TLA+ check: by manifest digest and commit, with the claim scoped to what its tests check.",
    ]
    hw = (c.x1 - x0) / 2 - 12
    h = max(c.card(0, 0, hw, "Substitution is by role (ADR-0033 §2)", sub_body, draw=False),
            c.card(0, 0, hw, "The reference is evidence, not the verified object", ref_body, draw=False))
    c.card(x0, y, hw, "Substitution is by role (ADR-0033 §2)", sub_body, accent="blue", h=h)
    c.card(x0 + hw + 24, y, hw, "The reference is evidence, not the verified object", ref_body, accent="teal", h=h)
    return c
