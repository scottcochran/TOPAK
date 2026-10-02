"""H4 — The reference implementation as deployed in development."""
from lib import Canvas, text_width

ID, SLUG = "H4", "reference-deployment"

W = 3300

CRATES = [
    ("topak-node", "Replica: Paxos driver, WAL, admit pipeline, effects, the two sockets, the `topak` CLI", "all"),
    ("topak-core", "Types, lease (ADR-0031), rules floor (ADR-0026), tally (ADR-0024), lift, composition, replicated "
                   "state, trace recorder", "none"),
    ("topak-paxos", "Sans-IO crash-fault Multi-Paxos plus a `Voting` ghost", "none"),
    ("topak-floor", "Cedar engine with `floor/genesis-floor.cedar`, `genesis.cedarschema` and the values file compiled "
                    "in, pinned by digest", "none"),
    ("topak-bundle", "OPA sidecar client; local OPA WASM fallback bound to the lease's bundle; signature check "
                     "(ADR-0044)", "HTTP"),
    ("topak-transport", "Round topics over `rskafka`, or in memory", "Kafka"),
    ("topak-mcp", "The alphabet as MCP tools (`rmcp` server); downstream tool host (`rmcp` client)", "stdio"),
    ("topak-contain", "The launcher's backends (host process, Docker, SIMULATED rung 3), appraisal, bridge; the Run "
                      "tool host for Wasm modules; `topak-demo-guest`", "stdio"),
]


def build():
    c = Canvas(ID, "The reference implementation, as deployed in development",
               "`mechanism/` runs the admit path end to end for Build's six actions and Run's three: three replicas of "
               "one Rust binary, an MCP front door on stdio, an operator socket, a linked Cedar floor, an OPA sidecar "
               "with a WASM fallback, and Kafka or an in-memory transport. It carries a launcher and a Run tool host that the dev "
               "configuration does not turn on. It is evidence, not the verified object.",
               W, "mechanism/README.md; mechanism/docker-compose.yml; mechanism/scripts/dev-init.sh, build-bundle.sh, "
               "smoke.py; mechanism/crates/*/src (topak-node main.rs, lib.rs, api.rs, ops.rs, net.rs, wal.rs, config.rs, "
               "mechanism.rs, mechanism/launch.rs; topak-mcp lib.rs, server.rs, toolhost.rs; topak-bundle lib.rs; "
               "topak-transport lib.rs; topak-floor lib.rs; topak-core lib.rs, confine.rs, trace.rs; topak-contain "
               "lib.rs, wasmtool.rs); mechanism/corpus-pins.sha256; GAPS-AND-ASSUMPTIONS G1–G19, I8, I40–I44; "
               "ADR-0033 §1–§6, A5, A6, A7 and A8 (pending); ADR-0044; ToO rev 13 §15; G9 §2.3, §2.5, §7 items 34–36, "
               "52, 67, 80, 83, 84; spec/Mechanism-trace-results-2026.10.02b.txt")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---- evidence banner
    bh = c.card(X0, y, X1 - X0, "Evidence, not the verified object (ADR-0033 §1)", [
        "**Rung 0 as deployed**: the dev configuration has no `contain` section, so every lease it issues is rung 0. "
        "In its tests the launcher (ADR-0033 A7, pending) issues rung 1 on profiles that declare P3 `fail`, and rung 3 "
        "only SIMULATED under test keys: every principal it serves in earnest is `Mediated`; it fails assumption of use "
        "A1, and no containment theorem describes it. **Never promoted**: no promotion pipeline exists, "
        "and nothing in it is in any TCB. **Dev rules are not genesis rules**: `dev-init.sh` generates keys and writes "
        "their secrets to `dev/secrets/` in the clear (G6).",
        "Cited like a TLA+ check, by manifest and commit: `SHA256SUMS-REF-2026.10.02b`, digest `8fa797e317120e54`, at "
        "`c534a42` (ADR-0033 A8, pending; the last inserted addendum is A6, `48f92ab89086adce` at `dacbb0c`). **A running program invites being mistaken for the mechanism** (ToO §15).",
    ], accent="red", size=14.5, status="built", status_extra="evidence · rung 0 as deployed", tint=False, dash="6 4")
    y += bh + 50

    # ---- columns
    lx, lw = X0, 600
    gx = lx + lw + 110
    rw_ = 880
    rx = X1 - rw_
    cx_, cw = gx, rx - 210 - gx
    top = y

    # left: agent side and operator
    cy = top + 34
    ah = c.card(lx + 20, cy, lw - 40, "Agent · an MCP client", [
        "Any MCP-capable agent. **Byzantine at every position** (ADR-0007).",
        "Launches `topak mcp --socket dev/run/n1/agent.sock --token <token> --domain build|run` as its MCP server.",
        "**Not confined**: an agent process with a shell, a network stack or a filesystem bypasses the front door "
        "entirely (G1, the sandbox gap). A guest the node launches is the other way in: no token, stdio only (C5).",
    ], accent="pink", size=14)
    a_mid = cy + 60
    cy += ah + 60
    mh = c.card(lx + 20, cy, lw - 40, "`topak mcp` · the front door", [
        "One process per session; crate `topak-mcp` (`rmcp` server), inside the `topak` binary.",
        "Its tools are **exactly the seat's alphabet**: Build's six (ADR-0022 §1) or Run's three (ADR-0040 §1). Each "
        "call becomes one typed action; unknown or malformed calls are errors, never a default.",
        "It grants nothing: every call is decided by the replica.",
    ], accent="teal", size=14)
    c.arrow([(lx + 120, cy - 60 + 0 + 0), (lx + 120, cy)], "pink", sw=2.4, label="MCP over stdio", lpos=0.5,
            loff=(70, 0))
    m_mid = cy + 70
    cy += mh + 40
    agent_bot = cy
    c.region(lx, top, lw, agent_bot - top, "Agent host (no confinement · rung 0)", "pink", size=15)

    oy = agent_bot + 60
    oh = c.card(lx + 20, oy + 34, lw - 40, "Operator · `topak op`", [
        "`topak op --socket dev/run/n1/operator.sock '{\"op\": …}'`, one JSON line in, one out.",
        "**PROVISIONAL (operator authentication)**: the socket is protected by file mode 0600 only. Issuances and "
        "break-glass approvals carry their own signatures; grants, revocations and gate evidence do not (G5).",
        "Helpers: `topak keygen`, `topak sign`, `topak tool-digest`, `topak check-rules`, `topak profile-digest`.",
    ], accent="brown", size=14)
    o_mid = oy + 34 + 60
    oty = oy + 34 + oh + 16
    otw = lw - 40
    oty += c.table(lx + 20, oty, [("`op`", otw * 0.3, {"mono": True}), ("Log entry", otw * 0.27, {"mono": True}),
                                  ("Carries", otw * 0.43)], [
        ["grant", "Grant", "Unsigned; returns the session token"],
        ["renew", "Renew", "Unsigned; narrower lease, new fence"],
        ["end_round", "EndRound", "Unsigned; an e-stop (F2)"],
        ["revoke", "Revoke", "Unsigned; names a principal, Persona or confinement digest (F2)"],
        ["fence_epoch", "EpochIncrement", "Unsigned; the fleet fence (F2)"],
        ["issue", "Issue", "**Signed** by anchor keys; validated against the rules floor (F4)"],
        ["gates_passed", "GatesPassed", "Unsigned; gate evidence asserted (G8)"],
        ["break_glass_approve", "BreakGlassApprove", "**Signed** by a break-glass roster key"],
        ["register_profile", "ProfileRegister", "Unsigned; refused unless the profile is a promoted artifact"],
        ["launch", "Grant · Contested", "Unsigned; the node launches, appraises, and orders the grant with the "
                                        "appraisal in it (A7, pending; needs `contain`)"],
        ["status", "—", "Read-only; nothing ordered"],
    ], size=13, accent="brown") + 18
    op_bot = oty + 10
    c.region(lx, oy, lw, op_bot - oy, "Environment steps, not principal actions", "brown", size=15)

    # centre: three replicas
    ry = top
    n1h_body = [
        ("agent socket", "`run/n1/agent.sock`, mode 0660; a bearer token names seat, lease, epoch; a launched lease "
                         "mints none"),
        ("operator socket", "`run/n1/operator.sock`, mode 0600"),
        ("admit pipeline", "the eight steps of D1, in `topak-node` over `topak-core`"),
        ("floor", "`topak-floor`: Cedar **linked**; refuses to start unless the floor, schema and values bytes match "
                  "the gated digests"),
        ("bundle tier", "`topak-bundle`: loads `bundles_dir` **only under signatures** verifying against "
                        "`bundle_keys`; sidecar client, WASM fallback"),
        ("Paxos", "`topak-paxos` driven by `driver.rs`: persists fsynced before any send"),
        ("WAL", "`run/n1/wal.jsonl`: promises and accepted votes, durable before replies"),
        ("expiry sweeper", "every 250 ms, proposes `EndRound(Expired)` for leases this replica saw expire"),
        ("local files", "`workspaces/` (not replicated, G9); `archive.jsonl`, a projection of the log, not the archive"),
        ("launcher", "`mechanism/launch.rs` over `topak-contain`: launch, appraise, grant, bridge; renews against the "
                     "same guest; destroys it when the round ends (A7, pending). **Off in dev**: no `contain` section"),
        ("Run tool host", "`topak-contain` `wasmtool`: a Wasm module per call whose one network capability is its "
                          "declared target (A8, pending). **None in dev**: `wasm_tools` is empty"),
    ]
    tw = cw - 40
    th_title = 34
    c.text(cx_ + 20, ry + 34 + 22, "Replica n1 · `topak node --config dev/n1.json`", 20, "teal", bold=True)
    tyy = ry + 34 + th_title + 12
    tyy += c.table(cx_ + 20, tyy, [("Part", tw * 0.2, {"bold": True}), ("What it is", tw * 0.8)],
                   [list(r) for r in n1h_body], size=13.5, accent="teal") + 18
    # crates table: which process each lives in
    c.text(cx_ + 20, tyy + 18, "The eight crates, and the process each runs in", 18, "teal", bold=True)
    tyy += 32
    crows = []
    for name, what, io in CRATES:
        where = {"topak-node": "`topak node`", "topak-core": "`topak node`", "topak-paxos": "`topak node`",
                 "topak-floor": "`topak node` (linked)", "topak-bundle": "`topak node`; talks to the OPA sidecar",
                 "topak-transport": "`topak node`; talks to Kafka",
                 "topak-mcp": "server half in `topak mcp`; tool-host half in `topak node`",
                 "topak-contain": "`topak node`; each guest is its own process or container"}[name]
        crows.append([f"`{name}`", what, io, where])
    tyy += c.table(cx_ + 20, tyy, [("Crate", tw * 0.17), ("What", tw * 0.45), ("I/O", tw * 0.08),
                                   ("Runs in", tw * 0.30)], crows, size=13.5, accent="teal") + 12
    tyy += c.para(cx_ + 20, tyy, tw, "One binary, `topak`, carries every crate; `topak-demo-tool` is a second binary in "
                  "`topak-node`, the downstream tool the dev configuration allowlists; `topak-demo-guest`, in `topak-contain`, is "
                  "the scripted occupant the tests launch.", 13.5, "muted") + 14
    n1_bot = tyy + 10
    c.region(cx_, ry, cw, n1_bot - ry, "Replica n1 · one process", "teal", dash=None, size=15)
    # n2, n3
    ny = n1_bot + 50
    nw = (cw - 40) / 2
    peer_h = 0
    for i, nid in enumerate(["n2", "n3"]):
        h = c.card(cx_ + i * (nw + 40), ny, nw, f"Replica {nid} · `topak node --config dev/{nid}.json`", [
            f"Same binary, same rules, params, corpus and bundles; its own `run/{nid}/` data dir, WAL and sockets.",
            f"Paxos peer at `127.0.0.1:710{i + 2}`.",
        ], accent="teal", size=14)
        peer_h = max(peer_h, h)
    c.text(cx_ + 20, ny - 14, "n1 at 127.0.0.1:7101", 13, "faint")
    pax_y = ny + peer_h + 30
    ph = c.card(cx_, pax_y, cw, "Paxos over TCP among n1, n2, n3", [
        "Unauthenticated JSON frames over plain TCP, best-effort: Paxos tolerates loss, duplication and reordering "
        "(`net.rs`). **PROVISIONAL (replica authentication)**: mutual TLS is required before this leaves a lab (G5; "
        "T-0045-1).",
        "Fault model: **crash-recovery, not Byzantine** (ADR-0033 §3). A compromised replica could propose admits no "
        "floor evaluated.",
        "No snapshots and no compaction: the log, the `chosen` map, the dedupe set and the WAL grow without bound "
        "(G14). Every admit waits for a consensus round.",
    ], accent="violet", size=14)
    c.arrow([(cx_ + cw / 2, n1_bot), (cx_ + cw / 2, ny)], "violet", sw=2.4, both=True)
    c.arrow([(cx_ + nw / 2, ny + peer_h), (cx_ + nw / 2, pax_y)], "violet", sw=2.4, both=True)
    c.arrow([(cx_ + nw + 40 + nw / 2, ny + peer_h), (cx_ + nw + 40 + nw / 2, pax_y)], "violet", sw=2.4, both=True)
    cent_bot = pax_y + ph

    # arrows left -> n1
    c.arrow([(lx + lw - 20, m_mid), (cx_ + 20, m_mid)], "teal", sw=2.6, label="unix agent socket", lpos=0.5,
            loff=(0, -16))
    c.arrow([(lx + lw - 20, o_mid), (lx + lw + 75, o_mid), (lx + lw + 75, ry + 140), (cx_ + 20, ry + 140)], "brown",
            sw=2.4)
    c.label(lx + lw + 75, (o_mid + ry + 140) / 2 + 40, "unix operator\nsocket", "brown", 12.5)

    # right: external services
    ey = top
    cards = [
        ("OPA sidecar · `openpolicyagent/opa`", "amber", None, [
            "`docker compose up opa`: host `:18181` → container `:8181`, serving `bundles/${TOPAK_BUNDLE}.tar.gz`.",
            "Optional: `dev-init.sh --opa` points every replica at it; without it, the **local WASM engine only**.",
            "Its answer counts only from the lease's revision, and only if that revision verified (ADR-0044 §3).",
        ]),
        ("Kafka · `apache/kafka`, single-node KRaft", "amber", None, [
            "`docker compose up kafka`: `:9092`; `dev-init.sh --kafka` sets brokers `127.0.0.1:9092`, replication 1.",
            "Without it: **in-memory transport**. Round topics `topak.<chain>.<domain>.<seat>.e<epoch>.r<round>` and "
            "their `.after` companions.",
            "Transport only; ADR-0005 is **Proposed**, and the K row is carried as a debt (ADR-0033 §2).",
        ]),
        ("Downstream MCP tool · `topak-demo-tool`", "brown", None, [
            "Spawned per call by the tool host over stdio, as `wordcount@<digest>`; digest = SHA-256(binary digest ‖ "
            "canonical JSON of its MCP input schema), both halves checked on every call.",
            "Cleared environment, the workspace as working directory, **and nothing more**: hermeticity is unchecked "
            "(G4), and a native Run tool's channel is checked by nobody (G19). A Run tool hosted as Wasm reaches only "
            "its declared target (I44); dev hosts none.",
        ]),
        ("Signed bundles · `dev/bundles/`", "amber", None, [
            "`build-bundle.sh`: `policies/` → OPA WASM `bundles/<revision>.tar.gz`; revision = SHA-256 over sorted "
            "non-test `.rego` and `data.json` (today `be46c574…`).",
            "`dev-init.sh` signs a copy into `dev/bundles/` with `<revision>.sig` under a **dev bundle key** whose "
            "public half the rules carry in `bundle_keys`; the tracked tarball stays unsigned. Signing at promotion is "
            "a script step (G7 item 67).",
        ]),
    ]
    e_mids = []
    for t, acc, st, body in cards:
        h = c.card(rx + 20, ey + 34, rw_ - 40, t, body, accent=acc, size=14)
        e_mids.append(ey + 34 + 50)
        ey += h + 30
    ext_bot = ey + 14
    c.region(rx, top, rw_, ext_bot - top, "Processes outside the replica", "grey", size=15)
    # arrows n1 -> externals (route through a vertical bus left of the region)
    busx = (cx_ + cw + rx) / 2
    labs = ["HTTP · sidecar client", "Kafka · `rskafka`, `acks=all`", "stdio · MCP client", "load at startup"]
    for i, (yy, lab) in enumerate(zip(e_mids, labs)):
        acc = ["amber", "amber", "brown", "amber"][i]
        c.arrow([(cx_ + cw, yy), (rx + 20, yy)], acc, sw=2.2)
        c.label(busx, yy - 18, lab, acc, 12)

    # ---- config tables (dev rules and params)
    y = max(cent_bot, op_bot, ext_bot) + 70
    c.text(X0, y + 21, "What `scripts/dev-init.sh` generates under `mechanism/dev/`", 21, "brown", bold=True)
    y += 42
    hw = (X1 - X0 - 50) / 2
    h1 = c.table(X0, y, [("Seat", hw * 0.1, {"mono": True}), ("Domain", hw * 0.12), ("Kind", hw * 0.14),
                         ("Cell", hw * 0.09), ("Rosters and role", hw * 0.55)], [
        {"group": "`rules.json`: `rules_epoch` 0 · `quorum` \"all\" · `min_grant` 2", "accent": "brown"},
        ["a1", "build", "thinker", "—", "The Build author"],
        ["g1", "build", "grant", "—", "Grant roster"],
        ["g2", "build", "grant", "—", "Grant roster"],
        ["g3", "build", "grant", "—", "Grant roster"],
        ["o1", "build", "observer", "a1", "Veto roster; `a1`'s cell Observer"],
        ["corr", "build", "observer", "—", "Veto roster; the correlator (ADR-0038)"],
        ["r1", "run", "thinker", "—", "The Run principal"],
        ["ro1", "run", "observer", "r1", "`r1`'s cell Observer"],
        {"group": "Keys and exceptions", "accent": "brown"},
        ["—", "—", "—", "—", "`anchor_keys`: three generated keys"],
        ["—", "—", "—", "—", "`break_glass`: two roster keys, `quorum` 2, the demo tool, `actions` [\"Actuate\"]"],
        ["—", "—", "—", "—", "`erasure_roster`: **null** (as genesis rules issue none)"],
        ["—", "—", "—", "—", "`verifier_keys`: [] (read at rung 3, so none is granted) · `bundle_keys`: the dev "
                              "bundle key"],
        ["—", "—", "—", "—", "No seat declares a `rung` (0 by default); `personas` empty; `criterion` unset (G2)"],
    ], size=13.5, accent="brown")
    h2 = c.table(X0 + hw + 50, y, [("File", hw * 0.2, {"mono": True}), ("What it holds", hw * 0.8)], [
        {"group": "`params.json`", "accent": "brown"},
        ["corpus", "Every `spec/*.tla`, copied into `dev/corpus/` under its SHA-256: the content-addressed `Read` store"],
        ["build_tools", "The demo tool's allowlist id"],
        ["run_tools, run_root", "Empty"],
        ["round_bound", "200 (Build) · `run_round_bound` 64 (Run)"],
        ["lease_margin_ms", "500: the asymmetric clock margin (ADR-0032 §2)"],
        ["after_topic_limit", "64: the `after` companion's bound (ADR-0003 A2)"],
        {"group": "Per replica, and beside them", "accent": "brown"},
        ["n1.json … n3.json", "id, peers `127.0.0.1:7101–7103`, data dir, both sockets, rules, params, corpus, "
                              "bundles dir, `opa_sidecar`, `kafka`, the tool spec with its binary SHA-256"],
        [".env", "`TOPAK_BUNDLE=<revision>` for `docker compose`"],
        ["secrets/", "Every generated secret, **in the clear**"],
    ], size=13.5, accent="brown")
    y += max(h1, h2) + 14
    c.para(X0, y, X1 - X0, "`topak check-rules` validates `rules.json` against the rules floor at the end of "
           "`dev-init.sh`, and every replica refuses rules that violate it at startup: the runtime stand-in for the "
           "unwritten `GenesisSatisfiesFloor`.", 14, "muted")
    y += 50

    # ---- verification harness
    c.text(X0, y + 21, "How it is checked, and how it stays honest", 21, "violet", bold=True)
    y += 42
    w4 = (X1 - X0 - 3 * 36) / 4
    hs = [
        ("Tests: 103 across ten binaries", "violet", [
            "`mutations.rs`, `confinement.rs` (core), `sim.rs` (Paxos deterministic simulation with `Voting` "
            "invariants), `floor.rs`, `fallback.rs` (bundle tier, signatures), `e2e.rs`, `contain.rs` (the launcher in "
            "the node), `launch.rs`, `wasmtool.rs` (`topak-contain`), `drift.rs` (ADR-0033 A6).",
            "TLA+ properties restated as Rust tests with the same mutations.",
        ]),
        ("Trace recorder → `spec/Mechanism.tla`", "violet", [
            "`TOPAK_TRACE_DIR` makes every `apply` write a step: index, entry, result and a projected state "
            "(`trace.rs`). `trace2tla.py` converts; `mechanism-trace-run.sh` replays in TLC.",
            "2026.10.02: **62 traces, 709 steps, every step matching**, each state also read against "
            "`Confinement_A1`'s invariants (`ConfinementRefinement`). A mechanized link, **not a refinement**; "
            "T-0045-28 stays a trust root.",
        ]),
        ("Corpus pins and the drift test", "blue", [
            "`corpus-pins.sha256`: **49 pins**, one per record and TLA+ module the reference follows.",
            "`cargo test -p topak-core --test drift` fails when a pinned file changes, or when the code cites a record "
            "that is not pinned. `PROVISIONAL (<tag>)` marks every gap in the code.",
        ]),
        ("Live smoke run", "amber", [
            "`scripts/smoke.py`: processes, TCP, operator CLI and an MCP client, in-memory or against Kafka and the "
            "sidecar.",
            "**Not rerun since 2026.09.25** (G7 item 52).",
        ]),
    ]
    hh = max(c.card(0, 0, w4, t, b, accent=a, draw=False, size=14) for t, a, b in hs)
    for i, (t, a, b) in enumerate(hs):
        c.card(X0 + i * (w4 + 36), y, w4, t, b, accent=a, h=hh, size=14)
    y += hh + 60

    # ---- not built panel
    c.text(X0, y + 21, "What it does not show (ToO §15; ADR-0033 §6; the register, as at G9)", 21, "red", bold=True)
    c.status(X0 + 780, y + 3, "notbuilt")
    y += 42
    nb = [
        ["Confinement", "The launcher makes the alphabet the whole channel for a guest it starts; no guest it starts "
         "passes P3, no host it runs on attests (rung 3 is SIMULATED, rung 2 a seam), and an agent outside a launcher "
         "still has a shell", "G1; items 34, 36"],
        ["Tool hermeticity", "Tools are pinned by binary and schema and run in a cleared environment; their behaviour "
         "is unchecked", "G4"],
        ["Channel fidelity", "A Wasm-hosted Run tool reaches only its declared target; a native one is checked by "
         "nobody, the channel is declared twice and not checked to agree, and a P4-pass Build profile is not held to "
         "Wasm tools", "G19; items 83, 84"],
        ["The Observer as a detector", "One is seated, its heartbeats are heard and its absence stalls; the Observer that "
         "would produce a finding is an e2e fixture with nothing behind it", "G12"],
        ["`W(p)` as an ACL", "Cells are declared, not enforced", "I8; item 46"],
        ["The archive and the plaintext store", "`archive.jsonl` per replica is a projection of the log; no governed "
                                                "store, no horizon, no audit-authority read path", "G9"],
        ["Erasure", "Not implemented; no erasure roster exists, so `X2-erasure` admits nothing", "G11"],
        ["Write-time masking", "Wrapper-Rego masking (ADR-0003 0003.6) is not built", "ToO §15"],
        ["Persona attestation", "For an operator grant, `persona` is an operator-supplied digest; a launch's appraisal "
         "must name the profile's, which is all the rung detects", "G13"],
        ["Bootstrap and genesis rules", "Dev rules, not genesis rules; no anchor ceremony", "G6"],
        ["Snapshots and compaction", "None; scale and long-running behaviour are not shown", "G14"],
        ["Replica and operator authentication", "Plain TCP between replicas; socket file modes and bearer tokens", "G5"],
        ["Signing at promotion", "A script step under a dev key with custody (1, 0); no pipeline, no custody row",
         "G7 item 67"],
        ["That the floor is the right floor", "Floor fitness (MEASURE 2.13) is unowned", "G16"],
        {"cells": ["(built since G8)", "The rung-1 launcher, a SIMULATED rung 3, the session proof, `Contained` as a "
                   "lookup, and the Run tool host for Wasm modules: **built**, under addenda that are pending (A7, A8) "
                   "on records that are not ratified (ADR-0036; ADR-0034 A2)", "G9 §2.3, §2.5; items 35, 80"],
         "accent": "teal"},
    ]
    c.table(X0, y, [("Not built", (X1 - X0) * 0.2, {"bold": True}), ("What stands in, and what that leaves",
                                                                      (X1 - X0) * 0.68),
                    ("Register", (X1 - X0) * 0.12)], nb, size=13.5, accent="red")

    ly = c.ymax + 44
    c.legend(c.x0, ly, [
        ("box", "teal", "the mechanism (replica, front door)"), ("box", "violet", "consensus (P), checks"),
        ("box", "amber", "bundle tier, transport"), ("box", "brown", "operator, tools, dev config"),
        ("box", "pink", "agent"), ("box", "red", "not built, residual"),
    ])
    return c
