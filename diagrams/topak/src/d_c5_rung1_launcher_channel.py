"""C5 — At rung 1 the launcher is the channel: ADR-0036's launch → appraise → grant → bridge (Proposed)."""
from lib import Canvas

ID, SLUG = "C5", "rung1-launcher-channel"

P, F, V = "[[green|pass]]", "[[red|fail]]", "[[grey|vacuous]]"


def build():
    c = Canvas(ID, "At rung 1 the launcher is the channel: launch, appraise, grant, bridge",
               "ADR-0036 (**Proposed**, not ratified; revised R1–R6) designs the reference's first step toward "
               "confinement. Its second step, the launcher in the node, is **built**, and its addendum, ADR-0033 A7, was "
               "**ratified in Batch 29 ahead of ADR-0036**; rung-1 leases are issued in the reference's tests. The guest "
               "has one channel, stdio; a launcher on the host starts it, appraises it, asks the node for a grant at "
               "`[profile digest, 1]`, and bridges every action line to the node's agent socket. **The token never "
               "enters the guest.** Every principal it launches is `Mediated`, by a declared profile clause rather than "
               "by the absence of a profile: **no guest passes P3** (G10 item 1). Under ADR-0050 (**provisional**) a "
               "launch is the mechanism's part of a first lease or of a `Regrant` at rung 1 or above, and **the second "
               "is not built** (G10 item 88).",
               3000, "ADR-0036 §1–§8, Findings, Options, R1–R6 (Proposed); ADR-0034 §1–§4, §6, §8, A2, A3; ADR-0031 §1, "
                     "§7, A1; ADR-0023 §6c (A1); ADR-0033 §2, I14, A7 (B29), A8 (B31), A9 (B32); ADR-0035 R4 (Proposed); "
                     "ADR-0048 §2, R6; ADR-0037 A2; ADR-0050 §4, §10 (provisional); ADR-0045 T-0045-19, T-0045-20, "
                     "T-0045-22; slm/serve/profile-host-rung0.json (DRAFT 2026.09.29, not a corpus record); "
                     "slm/serve/README.md; slm/serve/serve.py; mechanism/README.md; mechanism/GAPS-AND-ASSUMPTIONS.md G1, "
                     "G5, I14, I38, I40, I41, I43, I44, I45, I47; mechanism/crates/topak-contain, topak-node "
                     "mechanism/launch.rs; topak-contain/src/guest.rs (`GuestMsg`, `HostMsg`); "
                     "topak-core/src/confine.rs (`Profile`, `check_for_rung`); topak-mcp/src/server.rs; ToO rev 14 §2.7, "
                     "§7.10; G10 §1, §2.3, §7 items 1, 34, 35, 81, 85, 88; "
                     "derived/topak-format-and-schema-inventory-2026.10.03.md §1.7, §4.4")
    X0, X1 = c.x0, c.x1
    y = c.y
    sx = X0
    c.text(sx, y + 16, "ADR-0036", 16, "ink", bold=True)
    sx += 92
    sx += c.status(sx, y, "proposed", "C2, C4 on ratification · revised R1–R6") + 12
    sx += c.status(sx, y, "built", "in the node, ADR-0033 A7 ratified B29 ahead of ADR-0036 (G10 items 35, 81); "
                              "item 34 open") + 14
    c.text(sx, y + 16, "Deployment position: rung 1 (D-0034-2); the first profile fails P3 (D-0036-1).", 14, "muted")
    y += 54

    # ------------------------------------------------------------------ the sequence diagram
    SW = 2060
    lanes = [
        ("Guest container", "grey", "Persona inside (P5) · stdio only · `--network none` · read-only root · `--rm`"),
        ("Host: the launcher", "amber", "A script beside the rehearsal, holding the operator socket; trusted at rung 1 "
                                        "(T-0045-19)"),
        ("Node replica (`topak-node`)", "teal", "Operator socket (grants) and agent socket (actions); mints and checks "
                                                "the bearer token (I14)"),
    ]
    lg = 40
    lw = (SW - 2 * lg) / 3
    top = y + 14
    hh = max(c.card(0, 0, lw - 40, t, [b], size=13.5, bullets=False, draw=False) for t, _, b in lanes)
    lx = [X0 + i * (lw + lg) + lw / 2 for i in range(3)]
    hy = top + 40
    for i, (t, a, b) in enumerate(lanes):
        c.card(X0 + i * (lw + lg) + 20, hy, lw - 40, t, [b], accent=a, size=13.5, bullets=False, h=hh)
    sy = hy + hh + 30

    steps = []  # (kind, from, to, text, accent, dash)

    def msg(yy, a, b, num, text, acc, dash=None, lpos=0.5, lwid=None):
        xa, xb = lx[a], lx[b]
        off = 8 if xb > xa else -8
        c.arrow([(xa + off, yy), (xb - off, yy)], acc, sw=2.4, dash=dash)
        mx = (xa + xb) / 2
        c.label(mx, yy - 30, text, acc, 13.5, lwid or abs(xb - xa) - 70)
        if num:
            c.pill(min(xa, xb) + 14, yy + 8, num, acc, 12, solid=True)

    def note(yy, lane, title, body, acc, w=None):
        w = w or lw - 60
        x = lx[lane] - w / 2
        h = c.card(x, yy, w, title, body, accent=acc, size=13.5, bullets=False)
        return h

    n0 = len(c.out)
    yy = sy + 60
    msg(yy, 1, 0, "1 Launch", "start the profile's **image by digest** with the profile's `launch` constraints; hold "
                              "its stdin and stdout", "amber")
    yy += 76
    h = note(yy, 0, "Guest verifies its Persona bundle", [
        "Checks weights and tokenizer digests against `model.json`. **A guest that cannot verify its bundle exits "
        "without writing its first line**: no grant."], "grey")
    yy += h + 54
    msg(yy, 0, 1, "", "first stdout line: **identity** (`model.json` digest, family, parameter count, `root`)", "grey")
    yy += 30
    h = note(yy, 1, "2 Appraise (P7)", [
        "Compare the running image's digest and the reported `model.json` digest with the profile's reference values.",
        "[[green|Both match]]: **Attested**, by the launcher's own assertion, which is what rung 1 means. "
        "[[amber|Either differs, or the guest did not start]]: **Unattestable**, no grant. Contested is unreachable: "
        "nothing is measured."], "amber")
    yy += h + 70
    msg(yy, 1, 2, "3 Grant", "operator socket: `grant` with `confinement: [profile digest, 1]`, the Persona digest, "
                             "seat, round and role, and **an alphabet without** `Invoke`", "blue")
    yy += 78
    msg(yy, 2, 1, "", "the **session token** (I14's bearer token, still minted and checked by the node)", "teal")
    yy += 70
    loop_top = yy
    yy += 50
    msg(yy, 0, 1, "4 Bridge", "an `AgentOp` line on stdout, **without a token** (`Read`, `Draft`, `Emit`, `Submit`)",
        "grey")
    yy += 76
    msg(yy, 1, 2, "", "the same line **+ token**, forwarded to the agent socket", "amber")
    yy += 76
    msg(yy, 2, 1, "", "the response (for `Read`: the admitted content; the guest mounts no corpus root)", "teal")
    yy += 76
    msg(yy, 1, 0, "", "the response, on the guest's stdin: ingress = exactly the admitted `Read`s (ADR-0035 `consumed`)",
        "amber")
    yy += 40
    c.region(X0 + 10, loop_top, SW - 20, yy - loop_top, "for every action line, until the round ends", "amber",
             dash="6 5", size=13.5)
    yy += 60
    msg(yy, 1, 2, "5 End", "guest closes stdout, or the round's terminal action is admitted: **end the round** (an "
                           "ordered subtraction, attributed under F2)", "red", dash="7 5")
    yy += 64
    msg(yy, 1, 0, "", "**destroy the guest** (P6: one guest per round)", "red", dash="7 5")
    seq_bot = yy + 40
    n1 = len(c.out)
    for i, (t, a, b) in enumerate(lanes):
        c.line(lx[i], hy + hh, lx[i], seq_bot, a, sw=1.6, dash="4 6")
    # token zone markers
    c.region(X0, top, lw, seq_bot - top + 20, "Trust zone 1 · the guest: no token, ever", "grey", dash=None, size=14)
    c.region(X0 + lw + lg, top, lw, seq_bot - top + 20, "Trust zone 2 · the host: token's only holder", "amber",
             dash=None, size=14)
    c.region(X0 + 2 * (lw + lg), top, lw, seq_bot - top + 20, "Trust zone 3 · the mechanism", "teal", dash=None,
             size=14)
    seq_end = seq_bot + 20
    # draw the zones and lifelines under the messages: move them in front of the messages in paint order
    c.out[:] = c.out[:n0] + c.out[n1:] + c.out[n0:n1]


    # ------------------------------------------------------------------ sidebar
    bx = X0 + SW + 50
    bw = X1 - bx
    sy2 = top
    side = [
        ("The token never enters the guest (§2)", "teal", None, [
            "That is ADR-0034 §3.5's session binding at rung 1: **the session is the pipe**, the pipe belongs to one "
            "launched instance, and no other process can use the lease, because no other process holds the token.",
            "It replaces nothing in the node. At rungs 2 and 3 the attested session key replaces it.",
            "Mounting the socket and running `topak mcp` inside was rejected: the token would be in the guest (and "
            "Docker Desktop cannot carry a Unix socket into a container, finding 2).",
        ]),
        ("Every failure subtracts (§2)", "green", None, [
            "**No attestation, no grant.**",
            "**A dead guest** closes the pipe; the launcher ends the round (F2).",
            "**A dead launcher** takes the token with it; the lease expires on its TTL (ADR-0031 §7), and the guest, "
            "with no reader on its stdout, blocks and is destroyed at round end.",
            "Nothing in this list adds authority: the delegation test ADR-0034 applied to the host.",
        ]),
        ("Renewal re-asserts the same instance", "amber", None, [
            "The launcher renews only while the guest it launched is still on the other end of the pipe. Nothing to "
            "re-measure at rung 1; a renewal never changes the rung (ADR-0031 A1). Not yet exercised (open "
            "obligation).",
        ]),
        ("The occupant is a scripted round with the Persona inside (§3)", "grey", None, [
            "A fixed script that plays one Build round through the front door, using the Persona for the content of "
            "what it drafts. Its alphabet is `Read`, `Draft`, `Emit`, `Submit`; it never `Invoke`s, so D-0034-3 does "
            "not arise and P4 is vacuous.",
            "It mounts no corpus root: a `Read` is admitted node-side and its content comes back on stdin, so ingress "
            "is exactly the admitted `Read`s, ADR-0035's `consumed` set, beside the task and the round's tool list "
            "(ADR-0037 A2), which for an alphabet without `Invoke` lists nothing (ADR-0048 R6). Per ADR-0035 R4 the "
            "bound covers the guest's reads, not a tool's (the trainer runs in the node's toolhost).",
            "Byzantine by premise; at 1–50M parameters it cannot follow an instruction, which is enough for the cage "
            "and says nothing about capability.",
        ]),
        ("Stderr is a second channel, outward (finding 3)", "grey", None, [
            "It reaches the launcher's log and nothing else, carries no protocol and is read by nothing; listed in the "
            "profile so P1's \"one channel\" means one channel **for actions**.",
        ]),
        ("The second step: the launcher moves into the node (§6)", "blue", ("built", "A7, ratified B29"), [
            "A `launch` request: the node starts the guest, appraises, grants to itself and bridges. **The "
            "attester becomes the mechanism** (its assertion recorded in the grant entry); **the profile becomes a "
            "promoted artifact**, a one-file workspace (R4), and the node refuses an unpromoted digest.",
            "**Built**, under ADR-0033 A7 (ratified 2026.10.04, Batch 29, ahead of this record; `c536e21`): backends "
            "a host process (it declares P1–P3 `fail`), this container, and a SIMULATED rung 3; a launched lease "
            "mints **no token**, the bridge is the session; §7's three refusals are seen in tests with a scripted "
            "guest on a host process (R5). Rung 2 is not on this path: a container has no launch measurement "
            "(Firecracker or Kata, the rung-2 record's problem). The seat's rung is declared per seat (ADR-0023 "
            "§6c, A1) and a grant at any other rung is refused.",
        ]),
        ("Under ADR-0050, a launch is the mechanism's, not an operator's (R6)", "blue", ("provisional", "ADR-0050"), [
            "`Launch` and profile registration stop being an operator's requests: the node launches as its part of a "
            "**first lease** or of an operator's `Regrant` **at rung 1 or above**, and registers a profile when its "
            "promotion's tally completes (ADR-0050 §4).",
            "[[red|Not built]]: a `Regrant` at rung 1 or above, **which has to launch a guest**, is part of ADR-0050's "
            "exit from provisional (G10 item 88; `mechanism/` I47). Where the rules declare an operator, `Grant` "
            "and `Launch` arrive on the unsigned socket, a **BOOTSTRAP** path that seats and stands in for the quorum; "
            "the launcher's tests declare no operator (D-0050-1).",
        ]),
    ]
    for t, a, s, b in side:
        st, se = s if s else (None, "")
        h = c.card(bx, sy2, bw, t, b, accent=a, status=st, status_extra=se, size=14,
                   tint=(a in ("teal", "green")))
        sy2 += h + 20
    y = max(seq_end, sy2) + 50

    # ------------------------------------------------------------------ contrast: the reference path today
    c.heading(X0, y, "For contrast: the reference's front door today (ADR-0033 §2; `mechanism/README.md`)", size=21)
    c.status(X1, y + 3, "built", "socket grants: rung 0; BOOTSTRAP where the rules declare an operator",
             anchor="end")
    y += 50
    bxw = 420
    gap = 170
    chain = [
        ("Agent process", "grey", ["Holds the token: `topak mcp --socket … --token <token>`.",
                                   "**With a shell it never has to ask** (G1)."]),
        ("`topak mcp`", "teal", ["A stdio MCP server the agent runs; the alphabet as MCP tools and nothing else, "
                                 "and the round's **tool list** in its instructions (ADR-0048 §2; I45)."]),
        ("Unix agent socket", "teal", ["JSON lines carrying a **bearer token** minted at grant by the granting "
                                       "replica, not replicated (I14)."]),
        ("Replica admit path", "teal", ["session → lease, epoch, alphabet → lift (with Run's label facts) → floor "
                                        "(Cedar, the `emergency` stage, genesis-provisional) → bundle (OPA) → "
                                        "Paxos → apply → effect."]),
    ]
    chh = max(c.card(0, 0, bxw, t, b, size=14, draw=False) for t, _, b in chain)
    for i, (t, a, b) in enumerate(chain):
        x = X0 + i * (bxw + gap)
        c.card(x, y, bxw, t, b, accent=a, size=14, h=chh, tint=(i > 0))
        if i < 3:
            c.arrow([(x + bxw, y + chh / 2), (x + bxw + gap, y + chh / 2)], "teal", sw=2.4,
                    label=["MCP / stdio", "unix socket", "ActionRequest"][i], lpos=0.5, loff=(0, -22))
    ex = X0 + 4 * (bxw + gap) - gap + 40
    c.card(ex, y, X1 - ex, "What changes at rung 1", [
        "The token moves **out of the agent process** into the launcher; the agent becomes a guest whose only channel "
        "is stdio.",
        "The rung-0 host-run occupant keeps the token **inside** the occupant (its profile says so), since there is no "
        "launcher to hold it.",
        "In the node, a launched lease has **no token at all**: the bridge is the session (ADR-0033 A7, ratified "
        "B29).",
    ], accent="amber", size=14, h=chh, tint=False)
    y += chh + 60

    # ------------------------------------------------------------------ the guest channel as the node speaks it
    c.heading(X0, y, "What crosses the pipe in the node's launcher (`topak-contain/src/guest.rs`): one JSON object per "
                     "line, tagged `msg`; no token, ever", size=21)
    c.status(X1, y + 3, "built", "ADR-0033 A7, ratified B29; no record defines the wire form", anchor="end")
    y += 50
    gw = X1 - X0
    gcols = [("Direction", gw * 0.1, {"bold": True}), ("`msg`", gw * 0.08, {"mono": True}), ("Fields", gw * 0.34),
             ("When, and what it means", gw * 0.48)]
    y += c.table(X0, y, gcols, [
        ["guest → host", "hello", "`persona` (the `model.json` digest), `family`, `params`, `root`, `session_key?`",
         "The guest writes first, exactly once, within `hello_timeout_ms` (10 s): the identity line of step 1. A "
         "second hello is a protocol error, and a guest that cannot verify its bundle never writes one"],
        ["host → guest", "attest", "`nonce`", "Rungs 2 and 3: bind this nonce before the grant and at every renewal "
                                               "(ADR-0034 §3.1, §3.6). Rung 1 has nothing to measure and skips it"],
        ["guest → host", "evidence", "`report_data`", "In answer to `attest`, over `{nonce, sessionKey}`; unsolicited "
                                                       "evidence is a protocol error"],
        ["host → guest", "granted", "`fence`, `epoch`", "At grant and after every renewal: the lease the guest acts "
                                                         "under. At rungs 2 and 3 the guest signs `(fence, epoch, ctr, "
                                                         "op)` over it (I41). **Before the first one** the node writes "
                                                         "the round's opening record, the tool list (ADR-0048 §2); if "
                                                         "it cannot, the guest is destroyed and not bridged (I45)"],
        ["guest → host", "op", "`op`: an `AgentOp`; `proof?`: `{ctr, op, sig}`",
         "Every action line of step 4. The bridge hands it to the admit path as the launched lease's session: **a "
         "launched lease mints no token** (I14); at rungs 2 and 3 the proof is checked against the action at decide "
         "and its counter at apply. `ToolList` asks for the list again: no admit, the same answer all round"],
        ["host → guest", "response", "`response`: `{admitted, detail}`", "One per `op`: the admit path's answer, on "
                                                                           "the guest's stdin"],
        ["host → guest", "shutdown", "—", "At round end, before the guest is destroyed (P6)"],
    ], size=14, accent="teal") + 14
    y += c.para(X0, y, gw, "The guest-io buffer holds 64 lines; the bridge ending while the lease is live proposes "
                "`EndRound(operator)`. Evidence the node appraises is retained at `<data_dir>/evidence/<digest>.json` "
                "(I40), written non-canonically under a canonical name. Nothing in this table is a record's: the "
                "message set is the reference's, and ADR-0036's ratification would fix or change it.", 14, "muted") + 50

    # ------------------------------------------------------------------ the profiles: schema and the two declared ones
    half = (X1 - X0 - 40) / 2
    c.heading(X0, y, "§1: the profile is a file whose digest is the lease's confinement digest")
    c.heading(X0 + half + 40, y, "§5: what the launcher trusts, named (rung 1 adds them)")
    y += 40
    cols = [("Part", half * 0.18, {"mono": True}), ("Content", half * 0.82)]
    t1 = c.table(X0, y, cols, [
        ["image", "The guest image, by content digest. Not a tag"],
        ["launch", "The exact runtime constraints the launcher applies: network, root filesystem, capabilities, user, "
                   "IPC, process and resource limits, the mounts and their modes. The launcher applies these and "
                   "nothing else"],
        ["channel", "The one channel, and its protocol (§2)"],
        ["persona", "The Persona bundle's reference values: the digest of `model.json`, which pins the weights and "
                    "tokenizer (P5, P7)"],
        ["clauses", "**P1–P7, each** `pass`**,** `fail` **or** `vacuous`**, with a one-line reason.** A profile that omits a clause "
                    "is malformed"],
        ["subtractions", "For each `fail`: what would have to be removed for it to pass"],
        {"cells": ["reference", "**At the reference, not in ADR-0036 §1**: P7's reference values as a part of their own, "
                   "`launch_measurement?` and `min_tcb?` (`ReferenceValues`, confine.rs). `check_for_rung`: rung ≥ 1 "
                   "needs `image` and `persona`; rung ≥ 2 the launch measurement; rung 3 `min_tcb`"], "accent": "amber"},
        {"cells": ["domain", "**At the reference, not in ADR-0036 §1**: `build` or `run`, default `build`. The Run "
                   "profile is ADR-0034 A2, in force since Batch 30: Run profiles register, and a Run seat's tools are "
                   "**held to their channel** by the Wasm tool host, the target read from the entry (ADR-0033 A8, A9)"],
         "accent": "amber"},
    ], size=14, accent="blue")
    cols = [("Trusted for guest integrity at rung 1", half * 0.42, {"bold": True}), ("Why", half * 0.58)]
    t2 = c.table(X0 + half + 40, y, cols, [
        ["The person who runs the launcher", "Holds the operator socket, which is the grant authority in the reference "
                                             "(`mechanism/` G5); since ADR-0050, a BOOTSTRAP path where the rules "
                                             "declare an operator (I47)"],
        ["The launcher script", "Applies the profile's constraints, appraises, and holds the token"],
        ["The container runtime and its daemon", "Enforce the constraints the launcher asked for"],
        ["On Docker Desktop, the Linux VM", "The boundary between the container and the host"],
        ["The image, by digest", "What runs"],
    ], size=14, accent="amber")
    y += max(t1, t2) + 14
    c.para(X0, y - max(t1, t2) + t1, half,
           "The profile's identity is the digest of the file's bytes; a missing clause is malformed. The promotion "
           "artifact is a one-file workspace, `profile.json`, keyed by that digest (R4; PROVISIONAL (profile-artifact), "
           "I38); `register_profile` carries the text verbatim into the log.", 14, "muted")
    c.para(X0 + half + 40, y - max(t1, t2) + t2, half,
           "D-0034-2's type changes made concrete; ADR-0045 Annex B instantiates them under **T-0045-19** and "
           "**T-0045-20** (R3). On a Linux host Docker is not a VM boundary; gVisor (`SLM_RUNTIME=runsc`) is the nearest "
           "substitute, and the `launch` part must say which.", 14, "muted")
    y += 90

    c.heading(X0, y, "Two declared profiles, clause by clause: every failure is a subtraction still owed", size=21)
    y += 46
    TW = X1 - X0
    cols = [("Clause", TW * 0.12, {"bold": True}),
            ("SLM inference image under the launcher · rung 1 · ADR-0036 §4 (Proposed; the file is not written yet)",
             TW * 0.44),
            ("Host-run `serve.py`, no container · rung 0 · `profile-host-rung0.json` (DRAFT, declared, verified by "
             "nobody)", TW * 0.44)]
    rows = [
        ["P1 one channel", P + ": `--network none`; stdio is the only I/O the launcher connects. Stderr is "
                                "outward-only and listed",
         F + ": more than one channel: the host network and every host IPC path are reachable from the process"],
        ["P2 filesystem", P + ": read-only root, a 16 MB non-executable tmpfs, the three bundle files read-only. "
                               "**Nothing else is mounted**, not even the workspace: it lives node-side",
         F + ": the host filesystem is reachable; nothing is read-only and nothing is bounded to the bundle and "
             "workspace"],
        {"cells": ["P3 no launcher for the principal", F + ": the image carries a Python interpreter, which the "
                   "occupant is written in, and the base image's `/bin/sh`. The clause is about what is **reachable**, "
                   "not what the Persona intends", F + ": a Python interpreter runs the occupant and a shell is "
                                                       "reachable from it"], "accent": "red"},
        ["P4 tools are Wasm components", V + ": the occupant's alphabet has no `Invoke`",
         V + ": the occupant's alphabet has no `Invoke`"],
        ["P5 inference is inside", P + ": weights and tokenizer in the guest, digest-checked against `model.json` "
                                        "at start; that digest is a reference value the launcher appraises",
         P + ": weights and tokenizer loaded from the bundle and digest-checked against `model.json` at start"],
        ["P6 one principal per guest, one guest per round", P + ": `--rm`; one launch per grant; destroyed at round "
                                                                 "end",
         P + ": one occupant process per grant, exiting at round end. **Declared, not enforced**: nothing stops the "
             "operator starting two"],
        ["P7 reference values", P + ": the image digest and the `model.json` digest. Changing either is a new profile",
         P + ": the `model.json` digest and the `serve.py` and `model.py` digests in the results file (there is no "
             "image)"],
        ["Occupant", "A fixed script playing one Build round through the front door, `Read`, `Draft`, `Emit`, "
                     "`Submit`, with the Persona supplying the drafted text (§3). Not yet written",
         "`python3 -I slm/serve/serve.py --occupant`; `serve.py` has no `--occupant` option yet (it serves MCP or runs "
         "`--prompt`)"],
        {"cells": ["Token", "Held by the launcher only", "**Inside the occupant**: no launcher to hold it (§2 does not "
                                                          "apply at rung 0)"], "accent": "amber"},
        {"cells": ["Subtractions owed", "**One**: an image with no shell and no interpreter reachable from the "
                   "occupant (a compiled occupant on a `scratch` base, or the hermetic-shell record). G7 item 36",
                   "P1 and P2: run under ADR-0036's launcher (that is rung 1, the same schema). P3: a compiled occupant "
                   "on a scratch image"], "accent": "green"},
        {"cells": ["Verdict", "`Mediated`, **derived** from P3 (and the criterion conjunct, ADR-0035 Proposed); the "
                   "lease reports `contained = false`", "`Mediated`, derived from declared clauses; a results file "
                   "prints `[digest, 0]` and \"declared\"; the trusted base at rung 0 stays empty (T-0045-22 excluded)"],
         "accent": "red"},
    ]
    y += c.table(X0, y, cols, rows, size=14, accent="violet") + 30

    # ------------------------------------------------------------------ the ladder from the profile file, D-0036-1, ratification
    c.heading(X0, y, "The ladder the profile file lists (`_ladder`, profile-host-rung0.json): the profile is the "
                     "constant, the rung the variable")
    y += 46
    steps = [
        ("rung 0 · this profile", "grey", "P1 P2 P3 fail, P5 pass · **declared**"),
        ("rung 1 · ADR-0036 §4's profile", "amber", "P1 P2 pass, P3 fail · **asserted** by the launcher"),
        ("rung 1 · P3-passing image", "amber", "every clause passes · asserted by the launcher"),
        ("rung 2", "violet", "the same profile, **launch measurement** (Firecracker or Kata)"),
        ("rung 3 · archetype", "teal", "the same profile, **hardware attestation** (confidential VM; accelerator "
                                       "attestation, G4 item 29)"),
    ]
    sg = 60
    sw = (X1 - X0 - 4 * sg) / 5
    shh = max(c.card(0, 0, sw, t, [b], size=14, bullets=False, draw=False) for t, _, b in steps)
    for i, (t, a, b) in enumerate(steps):
        x = X0 + i * (sw + sg)
        c.card(x, y + (4 - i) * 14, sw, t, [b], accent=a, size=14, bullets=False, h=shh)
        if i < 4:
            yy = y + (4 - i) * 14 + shh / 2
            c.arrow([(x + sw, yy), (x + sw + sg, yy)], a, sw=2.2)
    y += shh + 4 * 14 + 16
    c.para(X0, y, X1 - X0,
           "The file's note: \"Each step changes one thing: a clause verdict, or the rung. Elevation is a fresh grant "
           "naming the same digest at a higher rung (ADR-0031 A1). Nothing on this ladder adds capability; what it "
           "adds is claims.\" **As drawn, the first step changes three clause verdicts and the rung together, and "
           "names a different profile file**, so it is not the single-change step ADR-0036 R1 describes.", 14, "muted")
    y += 70

    half = (X1 - X0 - 40) / 2
    c.heading(X0, y, "§8: degeneracy on this record")
    c.heading(X0 + half + 40, y, "§7: the ratification condition (G10 item 34, open)")
    y += 40
    cols = [("Id", half * 0.13, {"bold": True}), ("Parameter → deployed value", half * 0.27),
            ("Premises falsified", half * 0.14), ("Theorems voided", half * 0.24), ("Type changes", half * 0.22)]
    t1 = c.table(X0, y, cols, [
        ["D-0036-1", "Profile has an interpreter reachable from the principal", "P3",
         "Every `Contained` theorem, for principals under that profile", "Those principals are `Mediated` (ADR-0034 "
                                                                          "§4). No participant changes type"],
    ], size=14, accent="amber")
    c.para(X0, y + t1 + 14, half, "D-0034-2 (rung 1) is inherited and not restated. D-0036-1 is the same kind of entry "
           "as D-0034-3, for P3 instead of P4.", 14, "muted")
    c.card(X0 + half + 40, y, half, None, [
        "The profile file for `slm/serve/`'s image exists, every clause as §4 declares it, its digest recorded.",
        "**One honest round**: Attested, a grant at `[profile digest, 1]` with no `Invoke`, a bridged `Read` → `Draft` → "
        "`Submit` round with the Persona's text, the guest destroyed; the lease reports `contained = false`.",
        "**Three refusals seen to fire**: image digest differs (no grant); bundle does not match `model.json` (the guest "
        "exits, no grant); a second process on the agent socket without the token (refused).",
        "A rung-0 principal beside it, so `Mediated` at rung 1 is seen to come from P3, not from the rung. Results in a "
        "dated file under `slm/`.",
        "[[red|Not met at G10]] (R5): no profile file for `slm/serve`'s image, no round whose drafted content is the "
        "Persona's output, no results file under `slm/`. The reference's tests show the honest round and the three "
        "refusals with a scripted guest on a host process; A7 was ratified on those.",
    ], accent="amber", size=14, status="proposed")
    return c
