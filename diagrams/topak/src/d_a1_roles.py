"""A1 — Roles map: the letters name roles, not products."""
from lib import Canvas

ID, SLUG = "A1", "roles-map"

COLS = [
    ("T", "Formal specification and model checking", "teal",
     "Specify every guarantee against what an agent's alphabet allows, and check it, with a mutation that must fail "
     "for every property.",
     "TLA+: TLC over the tracked `tools/tla2tools.jar` **checks** every mutation and witness; since 2026.10.02 the "
     "TLA+ Proof System (`tlapm`, T-0045-31) **proves** the invariants of fifteen modules, 3,036 obligations (ADR-0046; G9 §2.9). Properties "
     "restated as Rust tests with the same mutations; since 2026.09.30 every tested behaviour replayed through "
     "`spec/Mechanism.tla`, and since 2026.10.02 every replayed state read against the abstract confinement "
     "invariants",
     ["Mutations and witnesses checked at small constants; invariants proved **of the modules**, not of the code "
      "(ADR-0046 §2).",
      "The trace harness is a mechanized link, **not a refinement** (T-0045-28 stays a trust root)."]),
    ("O", "Policy as code: a verified floor and a per-request bundle", "blue",
     "Floor tier: an evaluator with a mechanized semantics, an implementation checked against it, and a decidable "
     "comparison of two policy sets. Bundle tier: per-request, signed, subtract-only.",
     "Floor: Cedar (`cedar-policy`, the Rust engine) **linked** into the replica, the gated floor compiled in by path "
     "and refused unless its digests match. Bundle: OPA/Rego sidecar with an in-process WASM fallback bound to the "
     "lease's revision.",
     ["Rego has no mechanized semantics, so it cannot hold the floor tier (D-0030-1 if it does).",
      "`admit ⟺ floor_permit ∧ ¬bundle_deny` (ADR-0030 §1)."]),
    ("P", "Consensus over the control plane", "violet",
     "Order every grant and every authority fact in one log; the log index is the fence. Consensus for grants, "
     "local for denials.",
     "Sans-IO crash-recovery Multi-Paxos (`topak-paxos`): a `Voting` ghost under message-level `Paxos`, driven by a "
     "deterministic simulation that checks `Voting`'s invariants on every durable vote.",
     ["Replicas are crash-recovery, **not Byzantine** (ADR-0033 §3).",
      "Replica set is trust-root row T-0045-1; mutual authentication unbuilt."]),
    ("A", "Agents: the principals doing the work", "pink",
     "Every agent is Byzantine at every position. It reaches the world only through a typed alphabet; models stay out "
     "of the trusted computing base.",
     "The alphabet as MCP tools and nothing else, on a front door the mechanism owns (`topak mcp`, stdio, bearer "
     "token); downstream tools reached as MCP servers. A guest the node launches is bridged on stdio and mints "
     "no token (ADR-0033 A7, pending).",
     ["The alphabet is the whole **protocol**, not the whole **channel**: a process with a shell never has to ask.",
      "The reference grants rung 0 by operator, launches rung 1 on profiles that declare P3 `fail` and rung 3 only "
      "**SIMULATED** (A7, pending): **every real principal is** `Mediated` (G9 §2.3)."]),
    ("K", "Event transport", "amber",
     "Transport with a durability window. Neither the ordering authority (that is the Paxos log) nor the system of "
     "record (that is the archive).",
     "Kafka via `rskafka` (`acks=all`), one single-partition topic per principal per round; emissions after commit, "
     "denials unordered, an `after` companion past the seal.",
     ["The K row rests on **ADR-0005, still Proposed**: carried as a debt in ADR-0033 §2.",
      "Archive and erasure: not built."]),
]


def build():
    c = Canvas(ID, "The letters name roles, not products",
               "Each letter of TOPAK carries an obligation. Any instrument that meets the obligation may be substituted "
               "for the reference's choice; the floor tier cannot change language without ADR-0030.",
               2200, "ToO rev 13 §1, §2.3, §3.1, §12, §15; ADR-0030 §1–§3; ADR-0033 §2–§3; ADR-0005; ADR-0045 T-0045-1, T-0045-28, "
               "T-0045-29, T-0045-31; ADR-0046 §1, §2; ADR-0033 A7 (pending); G9 §2.3, §2.9, §3; README.md")
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
    def measure(i, body, title=None, acc="grey", bullets=False):
        return max(c.card(0, 0, w, title, b if isinstance(b, list) else [b], accent=acc, draw=False,
                          bullets=bullets) for b in body)

    ob_h = measure(0, [col[3] for col in COLS], "Obligation")
    in_h = measure(0, [col[4] for col in COLS], "Reference instrument")
    no_h = measure(0, [col[5] for col in COLS], "What the reference does not claim", bullets=True)

    for i, (L, role, acc, obl, inst, notes) in enumerate(COLS):
        x = x0 + i * (w + gap)
        # letter tile
        c.rect(x, y, w, 150, acc, tint=True, rx=12, sw=2.2)
        c.text(x + 22, y + 92, L, 84, acc, bold=True)
        c.para(x + 100, y + 30, w - 120, role, 18, acc, bold=True)
        yy = y + 150 + 18
        c.card(x, yy, w, "Obligation (the role)", [obl], accent=acc, bullets=False, h=ob_h, tint=False)
        yy += ob_h + 14
        c.card(x, yy, w, "Reference instrument", [inst], accent="grey", bullets=False, h=in_h)
        yy += in_h + 14
        c.card(x, yy, w, "What the reference does not claim", notes, accent="red", h=no_h, tint=False, dash="6 4")
    y += 150 + 18 + ob_h + 14 + in_h + 14 + no_h + 40

    h = c.card(x0, y, (c.x1 - x0) / 2 - 12, "Substitution is by role (ADR-0033 §2)", [
        "Any row may change without amending the record, provided the replacement meets the role's obligation and the "
        "change is recorded in the reference's assumptions register.",
        "The floor row cannot change language without ADR-0030: Cedar meets the floor obligation; Rego does not.",
        "Nothing translates: a Rego→Cedar transpiler would be a Build artifact whose output becomes the enforced floor.",
    ], accent="blue")
    c.card(x0 + (c.x1 - x0) / 2 + 12, y, (c.x1 - x0) / 2 - 12, "The reference is evidence, not the verified object", [
        "`mechanism/` implements the admit path end to end for Build's six actions and Run's three (ADR-0033 §1).",
        "It has never been promoted, nothing in it is in any TCB, and it is not a deployment: it fails assumption of "
        "use A1.",
        "It is cited like a TLA+ check: by manifest digest and commit, with the claim scoped to what its tests check.",
    ], accent="teal", h=h)
    return c
