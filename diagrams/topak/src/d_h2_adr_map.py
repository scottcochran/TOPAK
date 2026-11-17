"""H2 — The decision record map: ADR-0001 to ADR-0077 by area, with status, markers and edges.

Amended 2026.11.17 against G12 and Batch 40: ADR-0056 to ADR-0077 added (every one Proposed), Batches 38 to 40 drawn,
and the tiles the batches and the revisions since G11 moved (0024, 0033, 0045, 0046, 0053, 0054, 0055)."""
import math

from lib import AMENDED_G12, Canvas

ID, SLUG = "H2", "adr-map"

# id -> (short title, status, status_extra, relation line, note)
#   status: accepted | provisional | proposed | superseded | tombstone | reserved
R = {
    1: ("Rename the CI domain to `Build`; adopt `Build(Contain) → Run(Contain)`", "accepted", "", "", ""),
    2: ("Apply the membrane in `Build` as well", "accepted", "", "", "A2: the evictability test"),
    3: ("Topic per principal per round, sealed on emit, as the unit of erasure", "accepted", "C1 for A2 only", "",
        ""),
    4: ("Separate control-plane facts from cognitive payloads", "accepted", "", "", ""),
    5: ("Kafka is neither the ordering authority nor the system of record", "accepted", "C4", "0003, 0004, 0015",
        "Ratified at R2 in Batch 27, alone; discharges ADR-0033's K-row debt"),
    6: ("Erasure is a privileged, modeled, consensus-ordered event", "accepted", "C1, C4 via 0013", "", ""),
    7: ("Semantic judgment is never a lift", "accepted", "", "", ""),
    8: ("Observer replicas are not colocated with the Thinker", "superseded", "by 0038", "",
        "Colocation rule carried forward by 0038 §4"),
    9: ("Break-glass is a modeled, quorum-witnessed path, not a prohibition", "accepted", "C1, C4 via 0013", "",
        "A1 (B34): an emergency seating; a grant ends with its round"),
    10: ("The verified object: the mechanism, its epoch discipline, a minimal policy floor", "accepted", "", "",
         "Amended by 0026"),
    11: ("Observer placement and fault-domain independence", "tombstone", "", "", "No decision content"),
    12: ("The default-deny bundle is the policy floor: pre-blessed, resident, verified", "accepted", "", "", ""),
    13: ("Exception mechanism for privileged paths through the floor", "accepted", "C1, C4",
          "0010, 0025, 0026, 0028", "A1 (B34): the exception count is 1"),
    14: ("— (the per-class floor question)", "reserved", "", "", "Reserved, no file; narrowed by 0024"),
    15: ("Effects are boundary crossings; every crossing authorized, ordered, auditable", "accepted", "C2", "",
         "Revised by 0025; [[amber|A1 pending]] (0054): `Route` an emission"),
    16: ("The model enters the system as a Persona", "accepted", "", "0002, 0007, 0010",
         "A1, A2 (B34): a person's Persona; the binding `emergency`"),
    17: ("Archetype admits only in-house pre-trained Personas", "accepted", "", "0008, 0016",
         "Ordering-primacy clause reversed in effect; supersession unwritten"),
    18: ("The typed lift splits: decoder in the Persona, validator in the mechanism", "accepted", "",
         "0004, 0007, 0010, 0016", "Reader scope correction reversed in effect by 0037 §3"),
    19: ("Optional decode observability", "accepted", "", "0004, 0006, 0008, 0016", "Narrow form"),
    20: ("Replay scope is boundary events only", "accepted", "", "0003, 0004, 0006", ""),
    21: ("Build emits to the effect stream; Build has an Observer", "accepted", "C4", "", ""),
    22: ("Typed action alphabet for Build principals", "accepted", "§1–§5, §7, §8 only", "",
         "§6 (confinement) stays Proposed; A3 (B34): the entry's form is 0049's"),
    23: ("Degeneracy as the deployment-variation relation; archetype as unique maximum", "accepted", "C3", "",
         "§5 reverses 0008 scoping and 0017 ordering-primacy in effect; A1 (B29): the rung per seat"),
    24: ("Promotion requires a unanimous quorum", "accepted", "bootstrap set", "0007, 0010, 0022, 0025, 0026",
         "Amends 0002; A2 in force; [[blue|A3 provisional]] (B34): a promotion seats; E1 (B38): a citation; "
         "[[amber|A4 pending]] (0054)"),
    25: ("The trust anchor is a havoc issuer; intent is the sole axiom", "accepted", "bootstrap set", "",
         "Revises 0015; A2 (B34): the two issued lists; [[blue|A3 provisional]]: the provider's key"),
    26: ("The rules floor bounds every anchor issuance", "accepted", "bootstrap set", "0007, 0010, 0025",
         "Amends 0010; A1 (R8) [[grey|withdrawn]] (W1); [[blue|A2 provisional]] (B34): R6's count, R7's subject"),
    27: ("Genesis rules are resident", "accepted", "bootstrap set", "0025, 0026", ""),
    28: ("The forensic floor: authority facts survive erasure and break-glass", "accepted", "C1",
         "0004, 0006, 0010, 0020", "Split from 0013"),
    29: ("Genesis; the custodian ratifies unilaterally; bootstrap on a drafted TLA+ spec", "accepted",
         "for A2 (C3) and A4 only", "0024, 0025, 0026, 0027",
         "A4 (B34): the provisional status; floor fitness. [[blue|A3 provisional]]: the first operators"),
    30: ("Bundles cannot add authority by construction; the floor runs on a verified evaluator", "accepted", "C1",
         "0007, 0010, 0012, 0018, 0023", "A2 (B34): labels in S, a well-formed allowlist; A3: the floor is "
         "genesis-provisional"),
    31: ("The lease is the composite credential, and its grant is the instant", "accepted", "C1; C2 for A1",
         "0003, 0007, 0016, 0022, 0026, 0032", "A3 (B34): who grants and who denies; [[amber|A4 pending]] (0054): a "
         "third grant path"),
    32: ("The clock model: intervals trusted by failure direction", "accepted", "", "0007, 0022, 0031", ""),
    33: ("The mechanism has a reference implementation: evidence, not the verified object", "accepted", "",
         "0010, 0015, 0022, 0024, 0026, 0029, 0032", "A1–A20; A7–A15 in B29, B31–B35; A19, A20 (B40, 2026.11.17): the "
         "reference measured at G12 and after `Paxos.tla`; §7 finding 9 closed; [[amber|A16, A17, A18 pending]] (0054, "
         "0055, 0057)"),
    34: ("Confinement is attested at lease grant; the archetype rung is a confidential VM", "accepted", "C2, C4",
         "0016, 0017, 0022, 0023, 0024, 0031, 0032, 0033, 0035", "Discharges 0022 §6 for Build; A2, the Run profile "
         "(B30); A3 (B29)"),
    35: ("Persona lineage is a projection of the Build log; independence is an exclusion rule", "proposed", "",
         "0015, 0016, 0017, 0022, 0024, 0034", "R4–R8: R8 a workflow's tally (G11 §2.4)"),
    36: ("At rung 1 the launcher is the channel: a principal `Mediated` by declaration", "proposed", "",
         "0017, 0022, 0031, 0033, 0034", "§6's launcher built; 0033 A7 ratified ahead of it (B29)"),
    37: ("The LTRO decomposes into principals: Thinker and Observer are seats", "accepted", "C3, C4",
         "0002, 0007, 0016, 0018, 0019, 0022, 0024, 0031", "A2–A4 (B34): labels; kinds `emergency`, `operator`; "
         "[[amber|A5 pending]]: `orchestrator`"),
    38: ("Observers are per cell; the shared group becomes the correlator", "accepted", "C3, C4",
         "0003, 0004, 0007, 0023, 0031, 0037", "Supersedes 0008"),
    39: ("Observer liveness is progress, not presence", "accepted", "C4",
         "0007, 0022, 0024, 0031, 0032, 0037, 0038", "A2 (B34): an emergency seat is not coupled; [[amber|A3 "
         "pending]]: coverage at an edge"),
    40: ("Run has its own alphabet: `Consult`, `Actuate`, `Report`", "accepted", "C3, C4",
         "0007, 0010, 0015, 0018, 0022, 0031", "Reverses in effect 0022 §5's shared `Read`/`Emit`; A1 (B34): the root's "
         "label; [[amber|A2 pending]]: `Route`"),
    41: ("Policy obligations for Run: one envelope per variant; coupling on effects only", "accepted", "C1, C4",
         "0009, 0013, 0026, 0030, 0037, 0039, 0040", "A1–A3 (B34): `R5`–`R7`; X1 retired; `C1`–`C9`; [[amber|A4 "
         "pending]]: `R8`, `R9`"),
    42: ("Mechanism obligations for Run: effects counted, every `Actuate` recorded", "accepted",
         "C4; C2 for §6", "0003, 0004, 0015, 0018, 0031, 0033, 0039, 0040",
         "Whole: §6 in B30; A1, A2 (B34): labels, opening record, `seatKind`; [[amber|A3 pending]]"),
    43: ("Cell obligations for Run: Listener, seats, what the Observer must read", "accepted", "C4",
         "0018, 0037, 0038, 0039, 0040, 0042", "A1, A2 (B34): four labelled items; the task; [[amber|A3 pending]]: "
         "`input`"),
    44: ("A bundle is trusted by its signature, not its file name", "accepted", "C1", "0025, 0030, 0031, 0033",
         "Drafted by the assistant"),
    45: ("The trusted base is declared row by row", "accepted", "C2, C4", "0015, 0023, 0025, 0029, 0031, 0034",
         "A1, A2 (B34); B36: thirty-seven rows; A3, E1 (B37): T-0045-31's two unsound cases; A4 (B39): both reported "
         "upstream; [[amber|A5 pending]] (0057)"),
    46: ("The formal layer's method is declared: TLC checks, TLAPS proves, the prover is a trusted-base row",
         "accepted", "C2, C4", "0023, 0026, 0029, 0045", "E2, A1 (B28): certified configuration; A2, E3, E4 (B37): "
         "two unsound cases; A3 (B39, C4): the upstream report made, tlapm #309, #310"),
    47: ("The Listener labels what it delivers: a label on every item, a handle for what is suppressed", "accepted",
         "C4; C2 for §3", "0007, 0030, 0037, 0040, 0041, 0042, 0043, 0044", "Batch 34; [[amber|A1 pending]] (0054): "
         "the workflow's attributes"),
    48: ("A Thinker learns its tools from the mechanism: the entry carries its interface", "accepted", "C4, C3",
         "0007, 0022, 0031, 0037, 0040, 0043, 0044", "Batch 34; drafted by the assistant"),
    49: ("The allowlist entry has one schema, each field marked checked or claimed", "accepted", "C4; C2 for §5",
         "0022, 0030, 0040, 0044", "Batch 34; drafted by the assistant"),
    50: ("An operator is a principal: seated by promotion, renewing under a lease, denying without one",
         "provisional", "C1, C3, C4", "0016, 0024, 0025, 0026, 0031, 0035, 0037, 0045",
         "Batch 34; a first lease from a quorum not built; no reader"),
    51: ("The correlator computes named folds over facts; a store that never outlives its sources", "proposed", "",
         "0003, 0004, 0007, 0037, 0038, 0039, 0042, 0043", "Drafted 10.04; `Correlator.tla` proved; not built"),
    52: ("Break-glass is an emergency seating; the floor's exception for it is retired", "provisional",
         "C1, C3, C4", "0013, 0028, 0031, 0037, 0050", "Batch 34; rests on 0050; X1 retired on this basis"),
    53: ("A second deductive method: Lean re-encodings, code transcriptions, the floor in Cedar's model; the Lean "
         "kernel a trusted-base row", "accepted", "C4 (refines(Seats))", "0030, 0033, 0045, 0046",
         "Batch 36, 10.06; T-0045-37 in Annex A; E1 (B37); dependent entries on 0030, 0032, 0033, 0037, 0039, 0045, "
         "0046; [[amber|A1 pending]] (0057)"),
    54: ("A workflow is a promoted DAG: the promotion seats every cell; an orchestrator only narrows", "proposed", "",
         "0007, 0024, 0031, 0033, 0037, 0039, 0040–0043, 0047", "Drafted 10.07; R7 (11.11): `Workflow.tla` proved by "
         "`Workflow_proof.tla`; ten dependent amendments pending; built at the reference (0033 A16, A17)"),
    55: ("A workflow may be a mesh: a budget, the activation as the unit, the mechanism as the bus", "proposed", "",
         "0005, 0031, 0047, 0054", "Drafted 10.07; widens 0054; R3 (11.11): `Mesh.tla` proved by `Mesh_proof.tla`; "
         "built at the reference (0033 A16); dependent entries not drafted"),
    # ---- drafted after G11, all Proposed (G12 §1.1). A Proposed tile's marker is the criterion its Status note claims
    #      on the drafter's reading, not a ratification. "Overlay": an overlay, not the archetype (Status note, ⟨Q11⟩).
    56: ("A call's user scope is downstream: the mechanism binds the subject from the grant; the tool decides nothing",
         "proposed", "C1; C2 for §5", "0007, 0030, 0031, 0040, 0041, 0045, 0049, 0050",
         "Drafted 11.06, after G11; Archetype; not built; carries debts against nine records, 0049 and 0050 first"),
    57: ("The corpus's specifications form a graph: typed edges; a theorem inherited at the grade of its weakest edge",
         "proposed", "C2, C4", "0023, 0033, 0045, 0046, 0053",
         "Drafted 11.06; R1 (11.07): `specification-graph.json` built, 419 nodes, 435 edges, its checker run; dependent "
         "entries pending: 0033 A18, 0045 A5, 0053 A1"),
    58: ("A deployment declares its specification graph against the archetype's: keep, replace, add or omit",
         "proposed", "C2", "0023, 0045, 0053, 0057",
         "Drafted 11.06; rests on 0057: ratified together or waits; debt against 0023 §6; not built"),
    59: ("A deployment may be a tree of planes, each seated by its parent's promotion under a charter it can only narrow",
         "proposed", "C1", "0024, 0025, 0026, 0030, 0031, 0033, 0058",
         "Overlay; R1: `Federation.tla` checked and proved; nothing built; C3 would apply on admission to the archetype"),
    60: ("Every effect is admitted at the intent boundary; below it an autonomous plane with no path that changes "
         "authority", "proposed", "C1, C2", "0015, 0050, 0054, 0055, 0058, 0059",
         "Overlay; R1: `Intent.tla` checked and proved; R2: 0032 §4's budget, three options for the custodian; nothing "
         "built"),
    61: ("An autonomous plane is seven replicas under Byzantine agreement; membership shrinks only along a voted "
         "schedule", "proposed", "C1", "0058, 0059, 0060",
         "Overlay; R1: `Membership.tla` checked and proved at five replicas, not seven; PBFT not read; nothing built"),
    62: ("The lease pre-authorizes: a governor on each vehicle permits each entry against an exact count",
         "proposed", "C1, C2", "0031, 0049, 0058, 0059, 0060, 0061, 0064",
         "Overlay; R1: `Alone.tla` checked and proved, with `Intent`, `PlaneClock`, `Release`; R2: `T_irrev` and `K` "
         "said plainly; nothing built"),
    63: ("Revocation below the intent boundary is bounded in effects: watermarks; `K_up` outstanding and no more",
         "proposed", "C1", "0032, 0058, 0059, 0060, 0062",
         "Overlay; R1: `Outstanding.tla` checked and proved; R2: `K_up` against `K`; keeps 0032's first clause, so no "
         "C3; nothing built"),
    64: ("An autonomous plane's clock is its ticks, each signed by a quorum of replicas; an interval is a count of "
         "ticks", "proposed", "", "0032, 0058, 0059, 0060, 0061",
         "Overlay; no criterion on the drafter's reading; R1: `PlaneClock.tla` checked and proved in discrete time "
         "under §4's premise, the Lean arithmetic not; nothing built"),
    65: ("Stacks report to each other on topics promoted with the mesh: a send is permitted, never ordered; nothing a "
         "peer originates enables anything", "proposed", "C2", "0043, 0047, 0055, 0058, 0062",
         "Overlay; R1: `Peer.tla` checked and proved; changes 0055 §7 (Proposed); nothing built"),
    66: ("An irreversible effect is a person's: a `release` seat at a commanded plane is the only kind that reaches it",
         "proposed", "C1", "0013, 0052, 0058, 0059, 0060, 0062, 0064",
         "Overlay; R1: `Release.tla` checked and proved; provisional while 0052 is; C3 would apply on admission (0032 "
         "§4); nothing built"),
    67: ("Rules of engagement in three places: the Cedar floor, a promoted Wasm bundle, judgments nowhere; a "
         "`federation` stage", "proposed", "C1", "0007, 0030, 0058, 0059–0066",
         "Overlay; R1: `FD10` after 0063 R1; R2: `FD15-unattended-declared`; nothing written as policy, gated, "
         "modelled or built"),
    68: ("The overlay declares its adversaries, trusted-base rows and assumptions of use: fourteen, twelve and ten",
         "proposed", "C2", "0045, 0058, 0059–0067",
         "Overlay; nothing modelled, checked or built; no row tested against a vehicle"),
    69: ("The Build-Run pipeline: one ordered path from intake to rollout, keyed by digest; git and GitHub decide "
         "nothing", "proposed", "C1, C2, C3, C4", "0004, 0006, 0015, 0021, 0024, 0025, 0028, 0031, 0035, 0044, 0045, "
         "0047", "Drafted 11.12; R1–R3; R3: stage 4's carrier (`checks`, `results`) built and runs on pull requests "
         "into its branch, not on `main`; nothing else built; C3: 0016 §1's promotion key"),
    70: ("The lifecycle is secured at its boundaries: every boundary declares what crosses, its instant, adversary and "
         "owner", "proposed", "C2, C4", "0002, 0007, 0015, 0022, 0024, 0025, 0026, 0027, 0029, 0032, 0034, 0044, 0045",
         "Drafted 11.13; R1 on an adversarial review; companion of 0069 and defers to it; nothing modelled, checked or "
         "built"),
    71: ("User documentation is a derived layer: a document set for every role, read at three levels; it decides "
         "nothing", "proposed", "C2", "0024, 0025, 0029, 0045, 0050",
         "Drafted 11.16; R1: renumbered from 0070; nothing built, no unit written"),
    72: ("The documentation service is a projection that can be rebuilt: every revision by digest; one model, GraphQL "
         "and REST", "proposed", "C2", "0005, 0071",
         "Drafted 11.16; R1: renumbered from 0071; nothing built: no service, no store, no API"),
    73: ("The reference reader is React with Material UI over the public API alone; WCAG 2.2 AA is a dated audit a "
         "person signs", "proposed", "", "0071, 0072",
         "Drafted 11.16; R1: renumbered from 0072; no criterion on the drafter's reading; nothing built: no reader"),
    74: ("The archive of record keeps what the log ordered, a round sealed, a fact cites and a manifest measured, and "
         "originates none of it", "proposed", "C2, C4", "0003, 0004, 0005, 0015, 0028, 0045",
         "Drafted 11.16; R1: renumbered from 0073; nothing built; would discharge 0034's archive debt and give "
         "T-0045-7 content"),
    75: ("Every holding has a line in one retention schedule: facts never erased; a round unit dropped whole; every "
         "absence explained", "proposed", "C1, C2, C4", "0003, 0004, 0006, 0013, 0021, 0028, 0074",
         "Drafted 11.16; R1: renumbered from 0074; R2: reconciled with 0070; nothing built; erasure not implemented "
         "at the reference"),
    76: ("The archive is two stores and an index: a lock that cannot be shortened, a store that can delete, one table "
         "rebuilt from both", "proposed", "C2, C4", "0003, 0004, 0028, 0045, 0074, 0075",
         "Drafted 11.16; R1: renumbered from 0075; nothing built; no product named has been run"),
    77: ("TLA+ checks run in the tla-kit image, pinned by its published digest; the prover pin moves only by its own "
         "pull request", "proposed", "C2, C4", "0045, 0046, 0069",
         "Drafted 11.16, two unnumbered revisions; nothing built in TOPAK; tla-kit `v0.1.0` published, §7's first "
         "condition met; the pin stays at `7824dab` (G12)"),
}

# rows of regions: (label, accent, ncols, [ids in grid order, None for an empty slot])
ROWS = [
    [("Authority and bootstrap", "brown", 5, [25, 26, 24, 27, 29]),
     ("Deployment variation", "violet", 1, [23]),
     ("Reference, trusted base and method", "teal", 2, [46, 45, 53, 33])],
    [("Domains, membrane and Build alphabet (B1–B3)", "teal", 5, [1, 2, 7, 15, 22]),
     ("Run", "green", 4, [40, 41, 42, 43])],
    [("Policy and floors", "blue", 4, [10, 12, 30, 44, 13, 6, 9, 14]),
     ("Record, transport and erasure", "grey", 3, [4, 3, 20, 28, 21, 5]),
     ("Lease, time and confinement", "amber", 2, [31, 32, 34, 36])],
    [("Seats, cells and detection", "pink", 3, [8, 38, 39, 11, 37, 51]),
     ("Persona and model", "violet", 3, [16, 17, 19, 18, 35, None])],
    [("Ingress: labels, the tool list, the entry", "teal", 3, [47, 48, 49]),
     ("People in seats: operators and break-glass", "brown", 2, [50, 52]),
     ("Workflows (Proposed)", "amber", 2, [54, 55])],
    # drafted after G11 (G12 §1.1): every tile Proposed, none in force
    [("User scope (Proposed)", "amber", 1, [56]),
     ("The specification graph (Proposed)", "amber", 2, [57, 58]),
     ("Pipeline, lifecycle and the prover's image (Proposed)", "amber", 3, [69, 70, 77])],
    [("Command-chain overlay: an overlay, not the archetype (Proposed; each Status note, ⟨Q11⟩)", "amber", 5,
      [59, 60, 61, 62, 63, 64, 65, 66, 67, 68]),
     ("User documentation and the archive of record (Proposed)", "amber", 3, [71, 72, 73, 74, 75, 76])],
]

# edges drawn under a tile row: (src, dst, kind) — kind: dep | sup | rev
UNDER = [
    (26, 25, "dep"), (24, 25, "dep"), (24, 26, "dep"), (27, 25, "dep"), (27, 26, "dep"),
    (29, 24, "dep"), (29, 25, "dep"), (29, 26, "dep"), (29, 27, "dep"), (46, 45, "dep"), (53, 33, "dep"),
    (41, 40, "dep"), (42, 40, "dep"), (43, 40, "dep"), (43, 42, "dep"),
    (30, 10, "dep"), (30, 12, "dep"), (44, 30, "dep"),
    (20, 4, "dep"), (20, 3, "dep"),
    (31, 32, "dep"), (32, 31, "dep"),
    (36, 34, "dep"),
    (38, 8, "sup"), (39, 38, "dep"),
    (17, 16, "dep"), (19, 16, "dep"),
    (37, 18, "rev"),
    (51, 37, "dep"),
    (52, 50, "dep"),
    (55, 54, "dep"),
    # drafted after G11: each record's "Depends on" line, where both sit in the same tile row
    (58, 57, "dep"), (77, 69, "dep"), (72, 71, "dep"), (73, 71, "dep"), (73, 72, "dep"),
    (75, 74, "dep"), (76, 74, "dep"), (76, 75, "dep"),
    (60, 59, "dep"), (61, 59, "dep"), (61, 60, "dep"), (62, 59, "dep"), (62, 60, "dep"), (62, 61, "dep"),
    (63, 59, "dep"), (63, 60, "dep"), (63, 62, "dep"),
    (66, 64, "dep"), (67, 64, "dep"), (67, 65, "dep"), (67, 66, "dep"),
    (68, 64, "dep"), (68, 65, "dep"), (68, 66, "dep"), (68, 67, "dep"),
]
EDGE = {"dep": ("blue", None, 1.6), "sup": ("grey", None, 3.0), "rev": ("red", "7 5", 2.4)}


def build():
    c = Canvas(ID, "The decision records, ADR-0001 to ADR-0077, by area",
               "Every record with its status and confirmation markers at G12 and Batch 40 (2026.11.17), and its "
               "amendments since G9, pending ones "
               "in amber. Solid blue "
               "edges are dependencies taken "
               "from each record's \"Depends on\" line, drawn where both records sit in the same row of tiles (every "
               "tile lists its full line); the grey edge is the one supersession; red dashed edges are the reversals "
               "in effect (ToO §8.3) and ADR-0040's. The twenty-two records drafted after G11 are the two lowest bands, "
               "every one Proposed and none in force.",
               3600, "decisions/README.md (the index at G12); G10 §1, §1.2, §5, §6; G11 §1, §1.1, §1.2, §2.4, §4, §6, §7 "
               "items 6, 34, 43, 88, 92, 97, 101; G12 §0, §1 (the Batch table), §1.1, §1.2, §6, §7 item 76; ToO rev 16 "
               "§0, §8.3, §9; ADR-0029 A4 (the provisional status); ADR-0026 W1; the History tables of every record "
               "amended since G9 (G10 §6, G11 §6, G12 §6); ADR-0024 E1, B38; ADR-0045 A4, A5, B39; ADR-0046 A3, B39; "
               "ADR-0053 A1; ADR-0033 A16 to A20, B40 and its Pending line; ADR-0054 R7; ADR-0055 R3; ADR-0057 R1; the "
               "Status, Status note, Pending, Depends on, "
               "Supersedes, Amends, Revises, Narrows and Split from lines of ADR-0001 to ADR-0077; the History rows of "
               "ADR-0056 to ADR-0077; ADR-0018 Status note on 0037 §3; ADR-0023 Status "
               "note; ADR-0038 Supersedes; ADR-0040 Status note")
    c.note = AMENDED_G12
    X0 = c.x0
    tw, ig, rp = 330, 20, 22       # tile width, inner gap, region padding
    rgap, band_gap = 60, 110
    lane = 15
    y = c.y + 30

    def tile_body(i):
        t, st, ex, dep, note = R[i]
        body = []
        if note:
            body.append(note)
        if dep:
            body.append(f"[[faint|Depends on]] {dep}")
        return t, st, ex, body

    def measure(i):
        t, st, ex, body = tile_body(i)
        key = st if st in ("accepted", "provisional", "proposed", "superseded") else None
        return c.card(0, 0, tw, f"ADR-{i:04d}", body, draw=False, sub=t, status=key, status_extra=ex, size=13,
                      bullets=False, tsize=17, pad=13, lead=17.5)
    TH = max(measure(i) for i in R)

    # lanes needed per (band, tile-row)
    pos = {}
    loc = {}
    for b, row in enumerate(ROWS):
        for label, acc, nc, ids in row:
            for k, i in enumerate(ids):
                if i is not None:
                    loc[i] = (b, k // nc)
    lanes_needed = {}
    for s, d, _ in UNDER:
        key = loc[s]
        assert key == loc[d], (s, d)
        lanes_needed[key] = lanes_needed.get(key, 0) + 1

    chx = c.x1 - 26          # the right-hand channel of the long edges

    def right_of(b):
        used = sum(nc * tw + (nc - 1) * ig + 2 * rp for _, _, nc, _ in ROWS[b]) + rgap * len(ROWS[b])
        return X0 + used, chx - 70 - (X0 + used)

    def legend_block(lx, ly, gw):
        """The tile key and the edge legend, right of the band of ADR-0047 to 0055. Returns its bottom."""
        h1 = c.card(lx, ly, gw, "Reading a tile", [
            "Tile colour is status: [[blue|blue]] Accepted (genesis), [[red|red]] Accepted with a confirmation marker "
            "(C1–C4, ADR-0029 §4), [[blue|dashed blue]] Accepted · **provisional** (ADR-0029 A4: in force, subject to "
            "redesign, confirmation required), [[amber|amber]] Proposed, [[grey|grey]] superseded, tombstone or "
            "reserved.",
            "\"bootstrap set\": ADR-0024 to 0027, which cannot carry a marker (ADR-0029 §4); three of them hold a "
            "provisional amendment, which the genesis attestation must name (G11 §1.2); ADR-0024 A4 is pending.",
            "\"§1–§5, §7, §8\": ratified in part; ADR-0022 §6 stays Proposed. ADR-0042 is whole since Batch 30.",
            "On a Proposed tile the marker is the criterion its Status note claims on the drafter's reading, not a "
            "ratification. ADR-0059 to 0068 are an overlay, not the archetype: a deployment with one plane takes "
            "nothing from them (each Status note).",
            "A note names amendments since G9 with their batch (G10 §6, G11 §6, G12 §6); [[amber|pending]] ones are "
            "ADR-0054's twelve dependent amendments (A16 also on ADR-0055) and ADR-0057's three (ADR-0033 A18, "
            "ADR-0045 A5, ADR-0053 A1), none in force (G12 §1.1, §6).",
        ], accent="grey", size=13.5, bullets=True)
        h2 = c.legend(lx, ly + h1 + 18, [("arrow", "blue", "depends on"), ("arrow", "grey", "supersedes"),
                                          ("arrow", "red", "reverses in effect", "7 5")], title="Edges", maxw=gw)
        return ly + h1 + 18 + h2

    # what sits right of a band: the key (band 4) and the batches since G11 (band 5)
    SIDE = {4: legend_block, 5: lambda lx, ly, gw: batches_block(c, lx, ly, gw)}

    band_tops, band_bottoms = [], []
    for b, row in enumerate(ROWS):
        nrows = max(math.ceil(len(ids) / nc) for _, _, nc, ids in row)
        row_y = []
        cy = y + 36
        for r in range(nrows):
            row_y.append(cy)
            cy += TH + (lanes_needed.get((b, r), 0) * lane + 24 if lanes_needed.get((b, r)) else 0) + 22
        bottom = cy + 4
        x = X0
        for label, acc, nc, ids in row:
            rw = nc * tw + (nc - 1) * ig + 2 * rp
            nr = math.ceil(len(ids) / nc)
            c.region(x, y, rw, bottom - y, label, acc, dash=None, sw=2.2, size=15)
            for k, i in enumerate(ids):
                if i is None:
                    continue
                tx = x + rp + (k % nc) * (tw + ig)
                ty = row_y[k // nc]
                pos[i] = (tx, ty)
                t, st, ex, body = tile_body(i)
                if st in ("accepted", "provisional", "proposed", "superseded"):
                    acc_t = {"accepted": "blue", "provisional": "blue", "proposed": "amber",
                             "superseded": "grey"}[st]
                    if st == "accepted" and ex and ex != "bootstrap set" and not ex.startswith("§"):
                        acc_t = "red"
                    if st == "accepted" and ex.startswith("§"):
                        acc_t = "red" if "C" in ex else "blue"
                    c.card(tx, ty, tw, f"ADR-{i:04d}", body, accent=acc_t, h=TH, sub=t, status=st, status_extra=ex,
                           size=13, bullets=False, tsize=17, pad=13, lead=17.5)
                else:
                    lab = "Tombstone" if st == "tombstone" else "Reserved, no file"
                    c.card(tx, ty, tw, f"ADR-{i:04d}", body, accent="grey", h=TH, sub=t, size=13, bullets=False,
                           tsize=17, pad=13, lead=17.5, tint=False, dash="2 3")
                    c.pill(tx + 13 + 90, ty + 12, lab, "grey", 11.5, dash="2 3")
            x += rw + rgap
        band_tops.append(y)
        band_bottoms.append(bottom)
        if b in SIDE:
            # a key or a table sits right of this band and may be taller than it: the next band starts below both
            lx, gw = right_of(b)
            bottom = max(bottom, SIDE[b](lx, y, gw))
        y = bottom + band_gap

    # ---------------------------------------------------------------- edges under tile rows
    ports = {}
    for s, d, _ in UNDER:
        ports[s] = ports.get(s, 0) + 1
        ports[d] = ports.get(d, 0) + 1
    used = {}

    def port(i):
        n = ports[i]
        k = used.get(i, 0)
        used[i] = k + 1
        x0, _ = pos[i]
        return x0 + 40 + (tw - 80) * (k + 0.5) / n

    lane_i = {}
    for s, d, kind in UNDER:
        key = loc[s]
        li = lane_i.get(key, 0)
        lane_i[key] = li + 1
        sx = port(s)
        dx = port(d)
        base = pos[s][1] + TH
        ly = base + 16 + li * lane
        acc, dash, sw = EDGE[kind]
        c.arrow([(sx, base), (sx, ly), (dx, ly), (dx, base + 1)], acc, dash=dash, sw=sw)

    # ---------------------------------------------------------------- long edges
    # 0040 -> 0022, adjacent across the region gap (same band, same tile row)
    x22, y22 = pos[22]
    x40, y40 = pos[40]
    my = y22 + TH * 0.45
    c.arrow([(x40, my), (x22 + tw, my)], "red", dash="7 5", sw=2.4)
    c.label((x40 + x22 + tw) / 2, my - 34, "reverses §5 in effect", "red", 11.5, 80)

    # 0023 -> 0008 and 0023 -> 0017, through the gutters and the right-hand channel
    x23, y23 = pos[23]
    top4 = band_tops[3]
    for n, (dst, xoff) in enumerate([(8, 0.35), (17, 0.65)]):
        sx = x23 + tw * xoff
        gy1 = band_bottoms[0] + 30 + n * 22
        gy2 = top4 - 72 + n * 22
        dx = pos[dst][0] + tw * (0.8 if dst == 8 else 0.5)
        cx = chx - n * 22
        c.arrow([(sx, y23 + TH), (sx, gy1), (cx, gy1), (cx, gy2), (dx, gy2), (dx, pos[dst][1])], "red",
                dash="7 5", sw=2.4)
    c.label(chx - 11, (band_bottoms[0] + top4) / 2, "0023 §5 reverses in effect 0008 scoping and 0017 "
            "ordering-primacy", "red", 12, 170)

    # ---------------------------------------------------------------- notes, right of the bands with room
    lx, gw = right_of(3)
    c.card(lx, band_tops[3], gw, "Counts at G12 (§1.1), with Batch 40", [
        "**47 Accepted**: 18, 27 confirmation-required and **2 provisional** (0050, 0052); 2 in part · **27 Proposed** "
        "(0035, 0036, 0051, 0054, 0055, **0056 to 0077**; and ADR-0022 §6) · **1 superseded** · **1 tombstone** · "
        "**1 reserved**: **76 files**, numbered to 0077, twenty-two added since G11, all Proposed; 0071 to 0076 "
        "renumbered from 0070 to 0075 before ratification (each one's R1).",
        "**Batches 27 to 40** since G9: ADR-0005 (B27); ADR-0047 to 0050 and 0052 and twenty-six dependent amendments "
        "in seventeen records (B34); ADR-0053 (B36); the prover's two unsound cases (B37); ADR-0024 E1 (B38); the "
        "upstream report, ADR-0046 A3 and ADR-0045 A4 (B39); ADR-0033 A19 and A20 (B40, 2026.11.17, after G12). "
        "**Sixteen amendments pending at G12**, fifteen on a Proposed record and A19 alone; A19 ratified at Batch 40, "
        "so **fifteen remain** (the diagram's count), twelve on ADR-0054 and three on ADR-0057; ADR-0026 A1 (R8) "
        "**withdrawn** (W1).",
        "**Reversals in effect** (ToO rev 16 §8.3), all by the author alone in genesis: 0008 by 0038 (superseded); "
        "0017's ordering-primacy clause (the superseding record still unwritten); 0018's Reader scope by 0037 §3 (not "
        "superseded). ADR-0069 §7 would reverse ADR-0016 §1's promotion key (its C3): Proposed, not in force, not drawn "
        "as an edge.",
    ], accent="grey", size=13.5)

    return c


def batches_block(c, lx, ly, gw):
    """The batches since G11 (G12 §1's table, whole, and Batch 40 from ADR-0033 B40), right of the band of
    ADR-0056 to 0058, 0069, 0070 and 0077. Returns its bottom."""
    ly += c.heading(lx, ly, "Batches since G11: 38 and 39 (G12 §1), 40 (ADR-0033 B40)", "ink", 19)
    cw = [136, 62, 236]
    cw.append(gw - sum(cw))
    ly += c.table(lx, ly, [("Batch", cw[0], {"bold": True}), ("Date", cw[1], {}), ("Contents", cw[2], {}),
                           ("Notes", cw[3], {})], [
        ["**38 · A citation**", "11.02", "**ADR-0024 E1**, alone",
         "The human half of correlated review failure is Knight and Leveson's, and the gate's half Moon and Varshney's "
         "(§4.6, Appendix B). Floor fitness has an owner and a time, and no test. No decision text changes. Nothing was "
         "run. ADR-0024 is in the bootstrap set, and no criterion attaches (G12 §1)"],
        ["**39 · The upstream report**", "11.03", "**ADR-0046 A3**; **ADR-0045 A4**, its dependent entry",
         "The two cases are reported upstream as `tlapm` #309 and #310 (2026.10.18). **C4 on A3**, the custodian's "
         "decision. The assistant checked through GitHub's API that the issues exist and are labelled and that a "
         "maintainer opened #314, #315 and #318; the custodian read the issues against §8. ADR-0045's pin moved, and "
         "the premise routes were renewed (`premise-routes-results-2026.11.03.txt`) (G12 §1)"],
        {"cells": ["**40 · The reference measured**, after G12", "11.17",
                   "**ADR-0033 A19** (as revised at R14) **and A20**, together, applied inline",
                   "A19: `mechanism/` and `policies/` at `d1b72db` by `SHA256SUMS-REF-2026.11.16` (116 entries), the "
                   "reference at G12; 155 tests. A20: at `36269bc` by `SHA256SUMS-REF-2026.11.16b` (116 entries), after "
                   "`spec/Paxos.tla` and `spec/PaxosTrace.tla` were added and pinned (pull request #68); 159 tests. "
                   "§7's finding 9 is closed by the custodian's decision. No decision text changes. **No confirmation "
                   "criterion attaches**, the custodian's decision: both are measurements of the reference. A16, A17 "
                   "(ADR-0054, ADR-0055) and A18 (ADR-0057) stay pending (ADR-0033 B40, Pending)"],
         "accent": "blue"},
    ], size=13.5)
    ph = c.para(lx, ly + 14, gw, "Neither Batch 38 nor 39 changes a record's status (G12 §0); Batch 40 changes none "
                "either: ADR-0033 stays Accepted (genesis), its History gains rows A19, A20 and B40 (ADR-0033 B40). The "
                "twenty-two records drafted after G11 are Proposed, none in force (G12 §1.1).", 13.5, "muted")
    return ly + 14 + ph
