"""A6 — The lifecycle is secured at its boundaries (ADR-0070, Proposed, R1 2026.11.13): six phases, every boundary
the record names placed on the phase whose instant checks it, the §2 inventory whole, and the record whole."""
from lib import Canvas, STATUS, STATE_G12, text_width

ID, SLUG = "A6", "lifecycle-boundaries"
RECORDS = ('ADR-0070',)   # the records this diagram draws in full: a name of one opens it

W = 3600
S = 14

# Badge and card accents by boundary id. B1 to B14 are tagged as A3 tags them (B7 takes its domain's, here Run).
# B15 onward are this diagram's: red where the record's Consequences say the boundary has no instant today
# (B18, B19, B22, B24, B25, B26, B29); otherwise brown for a person or custody, teal for the mechanism, violet for
# consensus, amber for a Proposed owner, grey for what the trusted base excludes.
BACC = {"B1": "blue", "B2": "teal", "B3": "teal", "B4": "teal", "B5": "violet", "B6": "amber", "B7": "green",
        "B8": "red", "B9": "green", "B10": "brown", "B11": "grey", "B12": "red", "B13": "violet", "B14": "red",
        "B15": "violet", "B16": "brown", "B17": "teal", "B18": "red", "B19": "red", "B20": "grey", "B21": "brown",
        "B22": "red", "B23": "brown", "B24": "red", "B25": "red", "B26": "red", "B27": "amber", "B28": "amber",
        "B29": "red"}


def bid(b):
    """A boundary id as an accented bold run, for a table cell or a body line."""
    return f"[[{BACC[b]}|{b}]]"


# ---------------------------------------------------------------------------------------------- layout helpers
def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, measured over every card in the row. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), bullets=k.get("bullets", True),
                   tsize=k.get("tsize", 16)) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def stack(c, x, y, w, specs, gap=16, size=S, draw=True):
    """Cards one under another. specs: (title, body, accent, kwargs). Returns the bottom."""
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, draw=draw, **k) + gap
    return y - gap


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def status_strip(c, x0, x1, y, items):
    c.text(x0, y + 15, "Status", 15, "faint", bold=True)
    px0 = x0 + 80
    px = px0
    for lab, key, extra in items:
        lw = text_width(lab, 13.5, True) + 8
        if isinstance(key, tuple):
            plab, acc, dash = key
            pw = text_width(plab, 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > x1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if isinstance(key, tuple):
            px += c.pill(px, y, plab, acc, 11.5, dash=dash) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    return y + 42


def btag(c, x, y, b, size=13):
    """A solid boundary-id badge, as A3 draws them; returns its width."""
    return c.pill(x, y, b, BACC[b], size=size, solid=True)


def fill_cols(ww, cols):
    """Give the last column whatever width the others leave."""
    used = sum(cw for _, cw, *_ in cols[:-1])
    last = cols[-1]
    return cols[:-1] + [(last[0], ww - used) + tuple(last[2:])]


# ---------------------------------------------------------------------------------------------- the diagram
def build():
    c = Canvas(ID, "The lifecycle is secured at its boundaries: every boundary declares what crosses it, its instant, "
               "its adversary and its owner, and a boundary with no instant is a finding",
               "ADR-0070 (Proposed, 2026.11.13; revised R1 the same day on an adversarial review) reads the lifecycle "
               "in six phases the custodian settled ⟨K1⟩, examines every boundary ⟨K2⟩ and every production target "
               "artifact ⟨K3⟩, and puts both halves of the tandem developer in scope ⟨K4⟩. It gives every boundary "
               "seven declared things, keeps the register's B1 to B14 under their ids and adds B15 to B29, and applies "
               "the corpus's own rule everywhere: a crossing that adds authority has an instant at which a quorum, an "
               "issuance or a promotion decides it, and a crossing that subtracts is local. **Nothing here is modelled, "
               "checked or built**: the two modules of §13 are not written, no dependent entry of §11 is drafted, the "
               "reference does not recompute the signed digest at load (F1), and seven boundaries have no instant "
               "today. The custodian decided none of its content. The placing of boundaries on phases in the picture "
               "is this diagram's; the register's own picture is A3 and is not redrawn here.",
               W, "ADR-0070 provenance note (⟨K1⟩ to ⟨K4⟩, ⟨R1⟩), Status note, header (Depends on, Companions, Relates "
               "to), Context (its tree list and its table), Decision §1 (the seven items, orientation), §2 (2.1, 2.2, "
               "2.3, 2.4, every row), §3 (the common rule (a) to (e) and its table), §4 items 1 to 8, §5.1 (its table "
               "and further rules), §5.2, §5.3, §6 items 1 to 7, §7 items 1 to 7, §8, §9 (its table and the drills "
               "paragraph), §10 (its rows table, Moved, T-0070-2 and ADR-0069 §9, the assumptions table), §11, §12 F1 "
               "to F9, §13 item by item, Options considered, Consequences, Open obligations, the review annex, "
               "History; decisions/README.md (ADR-0070's row); G12 §9 item 115; derived/topak-boundary-register-"
               "2026.09.13.md §10 headings (10.3, 10.4, 10.5, 10.7), as A3 draws the register; ADR-0069 is cited only "
               "as ADR-0070 cites it", state=STATE_G12)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    y = status_strip(c, X0, X1, y, [
        ("ADR-0070", "proposed", "C2, C4 on the drafter's reading · 2026.11.13 · R1 2026.11.13"),
        ("ADR-0069, its companion", "proposed", "merged to main at bb76b46, which is not ratification"),
        ("the register (A3)", ("Derived and frozen; superseded by §2 for citation", "grey", "2 3"), ""),
        ("the two modules (§13)", ("Not written", "red", "2 3"), ""),
        ("the reference (§13)", "notbuilt", "F1 open"),
        ("§11's dependent entries", ("Not drafted", "red", "2 3"), ""),
        ("§5.3's gates in CI", ("Run since e1acade; four pass on a crash (F6); four gates not run", "red", "6 4"), ""),
        ("B18, B19, B22, B24, B25, B26, B29", ("No instant today (Consequences)", "red", "6 4"), ""),
        ("every §13 condition", ("Not met", "red", "6 4"), ""),
    ])
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian settled four things, ⟨K1⟩ to ⟨K4⟩, "
                "and decided none of the content: every rule is the drafter's, marked *(drafter's choice)* where an "
                "alternative was live and *(drafter's recommendation)* where the choice is left open; the boundary, "
                "row, assumption and finding ids are the drafter's (provenance note). **C2** attaches because §2 and "
                "§3 claim to inventory every boundary and every artifact and §10 claims the rows the lifecycle adds: "
                "under ADR-0045 an omission is a false claim, not a gap. **C4** attaches because the record would resolve "
                "debts accepted records carry (T-0045-30, T-0045-13 with ADR-0069 §6, G11 item 66). C1 and C3 do not "
                "attach (Status note). **R1** was made on an adversarial review by a second session of the same model, "
                "which gives independence of context and not of lineage and is not ADR-0029 A2's reader (provenance "
                "note; review annex). **G12 §9 item 115** lists what the record still owes: the custodian's decision on "
                "disclosing F1, dispositions for F1 to F9, two rows that fail ADR-0045 §2, the two §13 modules, four "
                "gates not run, signed tags, owners for tenancy and jurisdiction, §11's entries. One author, one day, "
                "one review.", 14.5, "muted") + 34

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "Six phases ⟨K1⟩, and every boundary §2 names placed on the phase whose instant checks it "
             "(the placing is this diagram's; the names are §2's)", status="proposed", extra="nothing built")
    y += c.legend(X0, y, [
        ("box", "grey", "the trusted base; what the base excludes"), ("box", "blue", "Build, promotion"),
        ("box", "green", "Run; subtraction"), ("box", "pink", "what comes back from Run"),
        ("box", "brown", "a person, custody, the gate"), ("box", "teal", "the mechanism"),
        ("box", "violet", "consensus; a draft"), ("box", "amber", "a Proposed owner"),
        ("box", "red", "no instant today, absent, or outside every theorem", "6 4"),
        ("arrow", "blue", "authority or data crosses"), ("arrow", "red", "a deny: subtraction only", "7 5"),
    ], title="Read as") + 26

    gap = 150
    pw = (WW - 3 * gap) / 4
    px = [X0 + i * (pw + gap) for i in range(4)]
    PAD = 24
    iw = pw - 2 * PAD
    PS = 13.5

    def bcard(b, name, crosses, instant, state, extra=None):
        body = [f"**Crosses:** {crosses}. **Instant:** {instant}.", f"**State:** {state}."]
        if extra:
            body.append(extra)
        return (f"{b} · {name}", body, BACC[b], {})

    phases = [
        ("Phase 1 · The trusted base for standing up Build (§4)", "grey", [
            ("Evaluated before the first round; every row identified before it runs", [
                "**A stand-up declaration precedes the first Build round** of any deployment, and of genesis. It "
                "instantiates ADR-0045 Annex A and §10's rows (§4.1).",
                "**Nothing third-party runs before its full SHA-256 is checked**; a 16-hex prefix is a label, a floating "
                "reference is refused (§4.2). **The full-digest check moves the channel from trust root to delegated**, "
                "and no further: it fixes which bytes run, not whether their publisher was honest (T-0070-9).",
                "**Order:** tools by digest; the toolchain's reproducibility check; the floor gates; the specifications "
                "and their results; the mechanism build (§4.7).",
            ], "grey", {}),
            bcard("B18", "Internet → build host", "tools, crates, images, toolchains", "fetch and install",
                  "[[red|no instant]]. The install scripts and the OPA and Kafka images check nothing; the TLC jar, "
                  "cvc5, elan's installer and the locked crates are checked by full digest (§2.2)"),
            bcard("B19", "Source → artifact (compilation)", "the build", "rebuild and compare",
                  "\"No reproducible build is declared\" (T-0045-30; §2.4)"),
            bcard("B23", "Anchor custody", "issuances", "signature by the key set",
                  "dev keys in the clear (G6; §2.2). The key ceremony comes before any key a deployment trusts exists "
                  "(§4.6)"),
            ("The build host is a Build principal's host (§4.5)", [
                "Ephemeral, built from a declared image, appraised as ADR-0034 appraises a guest. A host that outlives "
                "its round is a degeneracy. **One stands today**: the proofs' evidence is produced on the custodian's own "
                "arm64-darwin machine, under a prover pin upstream no longer serves, and CI cannot rerun it (F8).",
            ], "red", {"tint": False, "dash": "6 4"}),
        ]),
        ("Phase 2 · Development is a Build round; the tandem developer ⟨K4⟩ at a gate (§5)", "blue", [
            ("The agent half: a havoc drafter, `Mediated`, outside the trusted base (§5.1)", [
                "**The assistant is to the corpus what a Thinker is to the mechanism.** Nothing it produces takes effect "
                "except through the custodian's act. It cannot be a row of ADR-0045 §2, so it is **excluded**, as "
                "models are (T-0070-1). **The exclusion holds only as far as A-0070-1 does.**",
            ], "grey", {}),
            bcard("B20", "Assistant → corpus", "drafts and commits on a branch", "the custodian's merge (§5.1)",
                  "plan mode, and asks for commit and push; nothing else. `.claude/` is writable by the assistant and "
                  "measured by no manifest (F7; §2.4)"),
            bcard("B29", "Drafting session → provider", "everything the session reads", "[[red|none]]",
                  "[[red|no instant]]. A session can read embargoed safety findings and any key in the workspace "
                  "(A-0070-6; §2.4)"),
            bcard("B28", "Checker → gate verdict (CI)", "a pass or a refusal", "the required check",
                  "a ratcheted check passes on a crash, and every check runs from the change's own tree (F6; §2.4)"),
            ("The human half is at the gate, and the gate is hardened (§5.2)", [
                "**The custodian is not evictable, so the custodian is at the gate** (ADR-0002 A2, B14). Asked for: a "
                "hardware-backed second factor, signed commits and tags, branch protection, the custodian merging "
                "locally, **ratification as a signed tag** carrying the Batch manifest's SHA-256. **At (1, 0) one "
                "compromised account is a compromised corpus**, and nothing here removes that.",
            ], "brown", {}),
            bcard("B21", "Custodian → default branch", "ratification, merge, tag", "the merge or the tag",
                  "104 of 149 commits unsigned at `981bc77`, the 45 signed are GitHub's merges; `main` reported "
                  "protected, its rules not read; one code owner (§2.4)"),
        ]),
        ("Phase 3 · Promotion to production keeps ADR-0024's quorum (§6)", "blue", [
            bcard("B1", "Domain, `Build` → `Run`", "one artifact, by digest", "promotion",
                  "in force as specification; no promotion pipeline exists, and signing is a script step (ADR-0044; "
                  "§2.1)",
                  "**ADR-0024 stands**: a unanimous grant quorum, veto seats, author recusal, a vote bound to (artifact "
                  "digest, gate-evidence digest, rules epoch). Nothing here lowers it (§6.1)."),
            bcard("B14", "Gate approver", "a vote", "the tally",
                  "outside every theorem, as the register found (§2.4)"),
            ("Provenance is a projection; the signature binds the bytes that load; code is reproduced (§6.2 to §6.4)",
             [
                "**Provenance and the bill of materials are projected from the sealed round**, as ADR-0035 projects "
                "Persona lineage: \"a gate over manifests checks what the author claims\" (§6.2).",
                "**The mechanism recomputes the signed digest at load.** ADR-0069 §7 S-1 recomputes at signing; the "
                "recomputation at load is what this record adds, and it is where F1 is (§6.3).",
                "**Two builders that share no host, account or key build from the same pinned toolchain** and produce "
                "the same digest, or the promotion stalls (§6.4). This is the gate ADR-0069 §6 G-4 finds mechanism "
                "code lacks.",
            ], "blue", {}),
            ("Reach is staged, in rounds (§6.5) · the temporal row \"Promotion reach\"", [
                "A promotion's reach is a field of the tally; it advances ring by ring after a bake-in with no finding. "
                "**Silence is not a pass**: a round counts only with evidence the ring's Observers and correlator were "
                "live. Only rounds the operator's schedule opens count. **A finding may stop the advance, and never "
                "cause it** (ADR-0007). **Counted in rounds, not time** (ADR-0032 §2). [[red|Unbuilt]] (§2.3).",
            ], "amber", {"status": "notbuilt"}),
            bcard("B27", "Deployment ↔ archetype", "reports upstream", "declaration",
                  "Proposed (ADR-0058 §6; §2.1). **B11, the deployment rung, is unchanged**: ADR-0023 and ADR-0058 "
                  "own it (§2)"),
            ("Distribution, retreat and return (§6.6, §6.7)", [
                "**Nothing is fetched at runtime except by digest**; freshness is the rules epoch, a log position and "
                "not a clock. **Retreat is a revocation** (local, an operator's, ADR-0031 §5); **return is a "
                "promotion**, because it adds the earlier artifact's reach back.",
            ], "green", {}),
        ]),
        ("Phase 4 · The runtime secures each artifact ⟨K3⟩ for its whole life (§7)", "green", [
            ("The register's boundaries keep their place on A3 (§2; §7.1)", [
                f"{bid('B2')} membrane · {bid('B3')} typed effect · {bid('B4')} verified / parameterized · "
                f"{bid('B5')} facts / payloads · {bid('B6')} `Contained` / `Mediated` · {bid('B7')} seat · "
                f"{bid('B8')} Persona / provider · {bid('B9')} retention / erasure · {bid('B10')} human authority · "
                f"{bid('B12')} guest / host / hypervisor / hardware · {bid('B13')} epoch / lease. Each is restated in "
                "§2's tables below; A3 places them on the system.",
                "**The runtime records stand and are not restated** (§7.1): the lease (ADR-0031), attestation at grant "
                "(ADR-0034), fencing without a clock (ADR-0032), decide, order, re-check (ADR-0015 E1), Observer "
                "coupling (ADR-0039), the forensic floor (ADR-0028), break-glass (ADR-0052).",
            ], "teal", {}),
            bcard("B15", "Replica ↔ replica", "consensus messages", "every message",
                  "[[red|not built]] (G5: \"none (replica TCP)\"; §2.2). A precondition before any deployment (§7.6)"),
            bcard("B16", "Operator → mechanism", "control actions", "each action, signed",
                  "bearer token and socket mode at the reference (G5; §2.2). A precondition before any deployment "
                  "(§7.6)"),
            bcard("B17", "Tool host → external target", "`Actuate`", "channel fidelity, P4",
                  "the reference reads node configuration (I44, G19; §2.2)"),
            bcard("B26", "Measurement", "—", "—",
                  "[[red|absent]] (register §10.7; §2.3). `W` and `L` are measured in every deployment that declares a "
                  "`T_irrev`, which gives B26 an instant (§7.7)"),
            ("Every promoted artifact has a declared end; an advisory becomes a revocation (§7.2, §7.3)", [
                "An artifact with no expiry, no revocation path and no retirement event is a finding (§7.2).",
                "When an advisory names a component in a promoted artifact's SBOM, **the operator triages it and "
                "revokes the digest when the affected code is reachable**: targeted, local, no quorum, no peer "
                "(ADR-0031 §5). Each deployment declares how much one revocation may stop at once; past that bound it "
                "is staged (§7.3). The temporal row \"Advisory to revocation\": local; [[red|unbuilt]] (§2.3).",
                "**Invariant monitors** (§7.4, a recommendation): a correlator fold per proved module; its finding may "
                "only subtract (ADR-0051). **Key rotation** is an issuance; a compromise is a revocation then an "
                "issuance (§7.5).",
            ], "green", {}),
        ]),
    ]

    def measure_phase(specs):
        return stack(c, 0, 0, iw, specs, gap=14, size=PS, draw=False)

    top = y + 30
    RH = max(measure_phase(sp) for _, _, sp in phases) + 48 + PAD
    for i, (title, acc, specs) in enumerate(phases):
        c.region(px[i], top, pw, RH, title, acc, dash=None, sw=2.4, size=14)
        stack(c, px[i] + PAD, top + 48, iw, specs, gap=14, size=PS)
    # arrows between the top-row phases
    ay = top + RH * 0.5
    c.arrow([(px[0] + pw, ay), (px[1], ay)], "blue", sw=2.4, label="stood up in order (§4.7)", lpos=0.5, lw=130)
    c.arrow([(px[1] + pw, ay), (px[2], ay)], "blue", sw=2.4, label="a pull request's merge; the Batch's signed tag (§5.2)",
            lpos=0.5, lw=130)
    c.arrow([(px[2] + pw, ay), (px[3], ay)], "blue", sw=2.4, label="B1: one artifact by digest, a quorum's vote (§6)",
            lpos=0.5, lw=130)

    # ---- bottom row: Phase 6 (left, two columns) and Phase 5 (right, two columns)
    btop = top + RH + 170
    bw = 2 * pw + gap
    biw = bw - 2 * PAD
    # Phase 5
    p5_top_specs = [
        bcard("B22", "Run → Build intake", "Run's records, traces and outcomes",
              "intake, a promotion of a corpus-root revision (§8)",
              "[[red|no instant on this tree]]. ADR-0069 gives it one (IG-1 to IG-7), Proposed. ADR-0047 §9 leaves "
              "Build's `Read` unlabelled (§2.1)",
              "**Adversary:** TM1 shaping its own output; TM13; poisoning. **Owner:** ADR-0069 §3 to §5 (Proposed); "
              "this record for the removal form (§8)."),
    ]
    p5_ways = [
        ("1 · A deny", ["A Build-domain Observer or correlator finding is ground for `Vote(deny)` at a veto seat "
                        "(ADR-0038 §6, ADR-0051 §3), or for a revocation. **This is in force today** (§8.1)."],
         "green", {}),
        ("2 · Evidence", ["Recorded traces enter the specification graph's runtime layer (ADR-0057 §1, Proposed) at the "
                          "grade of their edge. **Evidence about a module and never a premise of an admit** (§8.2)."],
         "teal", {"status": "proposed"}),
        ("3 · Ingress", ["By ADR-0069's intake (§3 to §5). A corpus-root revision is promoted under ADR-0024. A "
                         "`source: run` object is computed from the log and never written; `generatedBy` is projected "
                         "(RR-1). Payloads and labelled items are admitted only once Build labels, and erasure follows "
                         "the data (LR-1 to LR-3) (§8.3)."], "amber", {"status": "proposed"}),
    ]
    p5_bottom_specs = [
        ("Nothing Run originates enables a Build act (§8)", [
            "ADR-0069 §2 says so; this record gives it ADR-0065 §1's form: **for every Build admit and every promotion, "
            "the same request with every Run-originated item removed must still be permitted.** Run intake may inform "
            "what a person drafts. It never satisfies a gate, fills a vote, or stands in for evidence.",
            "**Through the drafter** ⟨R1⟩: Run's output reaches the assistant as `untrusted` ingress and a draft from "
            "that session carries no Run provenance, so a session that has read Run-derived material **marks its "
            "drafts**, and the removal test counts a marked draft as Run-originated (§5.1, §8). Keeping such material "
            "out of drafting sessions altogether is stricter and left open.",
            "**The adversary is TM1, writing its own future training data.** ADR-0069 §4 makes that influence "
            "\"visible and attributable\" and \"Nothing in them makes it harmless\". An evaluation suite built from "
            "intake is a Build artifact with its own lineage record (ADR-0035), and it may only refute.",
        ], "pink", {}),
    ]
    # Phase 6: the loop's eight steps as a chain, then its rule
    steps = [("Detect", "the finding is recorded"), ("Register", "the row exists"),
             ("Contain", "the revocation is ordered"), ("Disposition", "the disposition is written"),
             ("Act", "a Batch, or a promotion"), ("Prove it closed", "the check is in CI"),
             ("Re-cut", "the cut is signed"), ("Re-read the boundaries", "the checkpoint")]
    sgap = 30
    sw_ = (biw - 7 * sgap) / 8
    sh = max(c.card(0, 0, sw_, t, [f"**Instant:** {i}"], draw=False, size=12.5, tsize=14, bullets=False)
             for t, i in steps)
    p6_bottom_specs = [
        ("A finding closes only when a check that would have caught it exists (§9)", [
            "**A check that fails on the defect and passes on the fix**: a TLC mutation, a planted-defect test, a floor "
            "test, a regression case. A finding with no possible check is carried as debt, not closed *(drafter's "
            "choice)*. **Each finding gets exactly one row in one register**, with a severity, an owner record and the "
            "boundary of §2 it is against: the review counts 108 findings \"carried by no list\" (CR-60).",
            "**Drills** run as ADR-0052 §6 counts them, in rounds and not in time: break-glass, the advisory-to-"
            "revocation path of §7.3, the retreat of §6.7, and a stand-up from nothing (§4) by someone other than the "
            "custodian. **A new boundary that no row names is a C2 finding against this record** (Re-read).",
        ], "brown", {}),
    ]
    # measure both bottom regions
    h5 = (stack(c, 0, 0, biw, p5_top_specs, gap=14, size=PS, draw=False) + 14
          + max(c.card(0, 0, (biw - 2 * 20) / 3, t, b, draw=False, size=PS, status=k.get("status"))
                for t, b, _, k in p5_ways) + 14
          + stack(c, 0, 0, biw, p5_bottom_specs, gap=14, size=PS, draw=False))
    h6 = sh + 14 + stack(c, 0, 0, biw, p6_bottom_specs, gap=14, size=PS, draw=False)
    BH5, BH6 = h5 + 48 + PAD, h6 + 48 + PAD
    BH = max(BH5, BH6)
    # Phase 6 region (left), sized to its own content
    c.region(px[0], btop, bw, BH6, "Phase 6 · Improvement is a loop with an instant at each step (§9)", "brown",
             dash=None, sw=2.4, size=14)
    cy = btop + 48
    for i, (t, inst) in enumerate(steps):
        sx = px[0] + PAD + i * (sw_ + sgap)
        c.card(sx, cy, sw_, t, [f"**Instant:** {inst}"], accent="brown", h=sh, size=12.5, tsize=14, bullets=False,
               tint=(i % 2 == 0))
        if i < 7:
            c.arrow([(sx + sw_, cy + sh / 2), (sx + sw_ + sgap, cy + sh / 2)], "brown", sw=1.8)
    cy += sh + 14
    stack(c, px[0] + PAD, cy, biw, p6_bottom_specs, gap=14, size=PS)
    # Phase 5 region (right)
    c.region(px[2], btop, bw, BH5, "Phase 5 · Run reaches Build in three ways, and no other (§8)", "pink",
             dash=None, sw=2.4, size=14)
    cy = btop + 48
    cy = stack(c, px[2] + PAD, cy, biw, p5_top_specs, gap=14, size=PS) + 14
    cy += row_cards(c, px[2] + PAD, cy, biw, 20, p5_ways, size=PS) + 14
    stack(c, px[2] + PAD, cy, biw, p5_bottom_specs, gap=14, size=PS)

    # vertical arrows: Run → Phase 5; Phase 5 → Phase 3 (deny, dashed); Phase 6 → Phase 2 (act); Phase 5 → Phase 6
    xa = px[3] + pw / 2
    c.arrow([(xa, top + RH), (xa, btop)], "green", sw=2.4, label="Run's records, traces and outcomes (§8)", lpos=0.5,
            lw=220)
    xd = px[2] + pw / 2
    c.arrow([(xd, btop), (xd, top + RH)], "red", dash="7 5", sw=2.4,
            label="a deny: `Vote(deny)` at a veto seat, or a revocation (§8.1)", lpos=0.5, lw=220)
    xb = px[1] + pw / 2
    c.arrow([(xb, btop), (xb, top + RH)], "brown", sw=2.4,
            label="Act: an erratum, an amendment, an R-revision, a new record, a new release (§9)", lpos=0.5, lw=220)
    my = btop + 48 + sh / 2
    c.arrow([(px[2], my), (px[1] + pw, my)], "pink", sw=2.4, label="Detect (§9)", lpos=0.5, lw=120)
    y = btop + BH + 70

    # ================================================================== band 2: §1 and the register
    y = band(c, X0, y, "Every boundary declares seven things, and a boundary with no instant is a finding (§1) ⟨K2⟩",
             status="proposed")
    wl = 1500
    xr = X0 + wl + 50
    wr = WW - wl - 50
    t1 = c.table(X0, y, [("Item", 70, {"bold": True}), ("Declared", 560), ("From", wl - 630)], [
        ["1", "**Its sides.**", "The register's columns (items 1 to 5)"],
        ["2", "**What may cross**, typed.", "The register's columns"],
        ["3", "**Its instant**: the event at which the crossing is checked. ⟨R1⟩ An instant names the predicate checked "
              "there, and the evidence that shows the check ran. An event with no predicate is not an instant.",
         "The register's columns"],
        ["4", "**Its interval of untruth**: how long the boundary's claim may be false.", "The register's columns"],
        ["5", "**What happens if the check cannot run.**", "The register's columns"],
        ["6", "**Its adversary**: who is assumed to attack it, named against TM1 to TM14 (ADR-0068) where one fits. "
              "⟨R1⟩ That includes an adversary to what crosses being read, not only to its being changed.",
         "The two its assessment found missing *(drafter's choice)*"],
        ["7", "**Its owner**: the record that decides it.", "The two its assessment found missing *(drafter's choice)*"],
    ], size=14, accent="ink")
    bl = stack(c, X0, y + t1 + 18, wl, [
        ("Orientation (§1)", [
            "**A crossing that adds authority, reach or trust has an instant at which a quorum, an issuance or a "
            "promotion decides it.** A crossing that subtracts is local, needs no quorum, and may run on a local "
            "monotonic clock (ADR-0032 §2).",
            "**A boundary with no instant is not a control. It is a finding**, entered in §12 or the review's register, "
            "and carried until an instant exists.",
            "The register (§6) calls it the orientation of every boundary: \"crossing toward more authority requires "
            "consensus, crossing toward less is local and monotone\". This record applies the corpus's own design "
            "(havoc principals, typed crossings, digests, quorums for additions, local subtraction) to the parts of the "
            "lifecycle that do not yet have it. **It invents no new kind of mechanism** (Context).",
        ], "blue", {}),
    ], size=S)
    br = stack(c, xr, y, wr, [
        ("The record's relation to the register (A3)", [
            "**The register's B1 to B14 keep their ids. B15 onward are new** (§2). \"State\" says what exists at "
            "`e1acade` ⟨R1⟩.",
            "**The register is derived and frozen. It is superseded by §2 for citation and stays as it is** (§11).",
            "The register's own assessment named the two columns it lacked, \"Weak: no per-boundary adversary, no owner "
            "column\" (ToO §10); they are items 6 and 7. Its §10 named eight categories \"absent entirely\"; records "
            "since closed parts of several (ADR-0032, ADR-0034, ADR-0031 A2). **Four are still absent**: the toolchain "
            "and supply chain (§10.3), tenancy (§10.4), jurisdiction (§10.5) and measurement (§10.7) (Context).",
            "**This diagram's reading of that list against §2**: tenancy is B24, jurisdiction B25 and measurement B26, "
            "each marked \"Absent (register §10.n)\" in its State cell; the toolchain and supply chain is B18, which "
            "the record owns itself and whose State cell cites §4.2 and not the register.",
            "**This diagram's count**: all fourteen register boundaries appear. B1 to B7 in §2.1; B12 in §2.2; B8, B9, "
            "B10, B13 in §2.3; B14 in §2.4; B11 by the note under §2.4, unchanged and owned by ADR-0023 and ADR-0058.",
            "**Owed on ratification**: ToO §10 and §13, the boundary inventory beside the register, and A-0070-1 to 6 "
            "(§11). The temporal axis keeps the register's organizing correction: **temporal is an axis that crosses "
            "every boundary**, and ADR-0032 decides which intervals may use which clock (§2.3).",
        ], "grey", {}),
    ], size=S)
    y = max(bl, br) + 70

    # ================================================================== band 3: the inventory, whole
    y = band(c, X0, y, "The boundary inventory, every row (§2) ⟨K2⟩ · Instant cells name the event; the predicate and "
             "its evidence are owed per row (Open obligations)", status="proposed")
    y += c.para(X0, y, WW, "The practice column is the drafter's assessment of what good practice asks at that boundary, "
                "and it is a requirement only where §4 to §9 make it one (§2). Ids are accented as the picture tags "
                "them. **Red** is the record's own word: no instant, absent, not built, or outside every theorem.",
                14, "muted") + 14
    cols8 = fill_cols(WW, [("Id", 90, {"bold": True}), ("Boundary", 300), ("What crosses", 360), ("Instant", 380),
                           ("Adversary", 400), ("Owner", 360), ("Practice at the boundary", 700), ("State", 0)])
    c.text(X0, y + 16, "**§2.1 Logical boundaries**", 16, "ink")
    y += 30
    y += c.table(X0, y, cols8, [
        [bid("B1"), "**Domain**, `Build` → `Run`", "One artifact, by digest", "Promotion",
         "A Byzantine Build principal; TM10", "ADR-0024, ADR-0021 §4",
         "The vote binds the artifact digest, the gate-evidence digest and the rules epoch; provenance is computed and "
         "not claimed; the signature binds the bytes that load; reach is staged (§6)",
         "In force as specification. No promotion pipeline exists, and signing is a script step (ADR-0044)"],
        [bid("B2"), "**Membrane**, `Contain`", "Typed actions in; admit or deny out", "Admit", "TM1",
         "ADR-0015, ADR-0030, ADR-0041", "Resident default-deny; decide, then order, then re-check at apply",
         "Built at the reference"],
        [bid("B3"), "**Typed effect**", "`{tool invocation, principal emission}`", "Validate", "A hostile decoder",
         "ADR-0018, ADR-0042 §1", "A total validator; any error is a deny", "Built"],
        [bid("B4"), "**Verified / parameterized**", "Refinements only",
         "Load and admit: `admit ⟺ floor_permit ∧ ¬bundle_deny`", "The bundle's author", "ADR-0030, ADR-0044",
         "Subtraction by construction; a signature over the loaded bytes", "Built, with finding F1"],
        [bid("B5"), "**Facts / payloads**", "Facts; payloads by hash and pointer", "Fact construction",
         "Exfiltration through the log", "ADR-0004", "Minimize by default", "In force"],
        [bid("B6"), "**`Contained` / `Mediated`**", "A predicate", "Grant", "—", "ADR-0034 §4",
         "Membership only by attestation", "`Contained` has no members"],
        [bid("B7"), "**Seat**", "Seat-scoped alphabets", "Grant and admit, \"enforced twice\"",
         "A principal asking past its seat", "ADR-0037", "—", "Built"],
        {"cells": [bid("B22"), "**Run → Build intake**", "Run's records, traces and outcomes",
                   "Intake, a promotion of a corpus-root revision (§8)", "TM1 shaping its own output; TM13; poisoning",
                   "ADR-0069 §3 to §5 (Proposed); this record for the removal form (§8)",
                   "Provenance, label and erasure carried across; nothing enabling",
                   "[[red|No instant on this tree.]] ADR-0069 gives it one (IG-1 to IG-7), Proposed. ADR-0047 §9 "
                   "leaves Build's `Read` unlabelled"], "accent": "red"},
        {"cells": [bid("B24"), "**Tenancy**", "—", "—", "A principal of another tenant", "—",
                   "Per-tenant roots, rosters and keys", "[[red|Absent]] (register §10.4)"], "accent": "red"},
        {"cells": [bid("B25"), "**Jurisdiction and residency**", "—", "—", "A legal demand", "ADR-0013 §5 in part",
                   "Residency declared per data class", "[[red|Absent]] (register §10.5)"], "accent": "red"},
        [bid("B27"), "**Deployment ↔ archetype**", "Reports upstream", "Declaration",
         "An overlay overstating its grade", "ADR-0058 §6 (Proposed)", "Every grade published", "Proposed"],
    ], size=13.5, accent="ink") + 30

    c.text(X0, y + 16, "**§2.2 Physical boundaries**", 16, "ink")
    y += 30
    y += c.table(X0, y, cols8, [
        [bid("B12"), "**Guest / host / hypervisor / hardware**", "One channel; no network device",
         "Appraisal at grant", "The host operator; an altered guest", "ADR-0034, T-0045-16 to 20",
         "A confidential VM appraised by an independent verifier (RFC 9334); a guest per round",
         "Specified. Rung 3 is simulated at the reference (I42)"],
        {"cells": [bid("B15"), "**Replica ↔ replica**", "Consensus messages", "Every message",
                   "TM4; anyone on the network", "ADR-0033 §3, T-0045-1",
                   "Mutual authentication; BFT where a replica is exposed (ADR-0061, Proposed)",
                   "[[red|Not built]] (G5: \"none (replica TCP)\")"], "accent": "red"},
        [bid("B16"), "**Operator → mechanism**", "Control actions", "Each action, signed", "TM7; a stolen key",
         "ADR-0050", "A hardware-held key per person (A16)", "Bearer token and socket mode at the reference (G5)"],
        [bid("B17"), "**Tool host → external target**", "`Actuate`", "Channel fidelity, P4",
         "A tool that dials elsewhere", "ADR-0034 A2, ADR-0049 §5", "The target read from the entry only",
         "The reference reads node configuration (I44, G19)"],
        {"cells": [bid("B18"), "**Internet → build host**", "Tools, crates, images, toolchains", "Fetch and install",
                   "An upstream compromise; a re-pointed tag", "**This record**; T-0045-29, 30, 31, 37",
                   "Full-digest check before first execution; no floating tags; a mirror; an SBOM (§4)",
                   "[[red|No instant.]] ⟨R1⟩ The install scripts and the OPA and Kafka images check nothing. The TLC "
                   "jar, cvc5, elan's installer and the locked crates are checked by full digest. A digest fixes what "
                   "was fetched and not whether its publisher was honest (§4.2)"], "accent": "red"},
        [bid("B23"), "**Anchor custody**", "Issuances", "Signature by the key set", "Key theft below threshold",
         "ADR-0025, T-0045-8, 9", "A ceremony; hardware-held keys; n ≥ 3", "Dev keys in the clear (G6)"],
    ], size=13.5, accent="ink") + 30

    c.text(X0, y + 16, "**§2.3 Temporal boundaries** · temporal is an axis that crosses every boundary, and ADR-0032 "
           "decides which intervals may use which clock", 16, "ink")
    y += 30
    cols7t = fill_cols(WW, [("Id", 90, {"bold": True}), ("Boundary", 330), ("Instant", 400), ("Interval", 320),
                            ("Clock, by failure direction", 800), ("Owner", 400), ("State", 0)])
    y += c.table(X0, y, cols7t, [
        [bid("B8"), "**Persona / provider**", "Promotion; grant; renewal", "`T_persona` plus drift",
         "Expiry adds if late, so it needs trusted time; A6", "ADR-0016, ADR-0031 A2, ADR-0034 §3",
         "Bounded. At the reference, attestation is an operator-supplied digest (G13)"],
        [bid("B9"), "**Retention / erasure**", "Seal", "Emit to seal", "—", "ADR-0003, ADR-0006, ADR-0028", "In force"],
        [bid("B10"), "**Human authority**", "Gate or non-refresh", "`D`", "—", "ADR-0032 §4", "`L` unmeasured"],
        [bid("B13"), "**Epoch / lease**", "Fence; expiry", "≤ `ttl`", "Local and monotonic: expiry subtracts",
         "ADR-0031, ADR-0032", "Built"],
        {"cells": [bid("B26"), "**Measurement**", "—", "`W`, `L`", "—", "ADR-0032 §4",
                   "[[red|Absent]] (register §10.7)"], "accent": "red"},
        ["—", "**Promotion reach** (§6)", "Each ring's advance", "A ring's bake-in",
         "**Counted in rounds, not time.** An advance adds reach, so ADR-0032 §2 forbids a local clock for it",
         "This record", "Unbuilt"],
        ["—", "**Advisory to revocation** (§7)", "An advisory names a digest", "Until the revocation is ordered",
         "Local. A revocation subtracts and needs no trusted time", "This record", "Unbuilt"],
        ["—", "**Artifact lifetime**", "Promotion to retirement", "Production lifetime", "—", "ADR-0021 §7",
         "In force for Build round topics"],
    ], size=13.5, accent="ink") + 30

    c.text(X0, y + 16, "**§2.4 Process boundaries: who stands at a gate**", 16, "ink")
    y += 30
    cols7p = fill_cols(WW, [("Id", 110, {"bold": True}), ("Boundary", 330), ("What crosses", 380), ("Instant", 360),
                            ("Adversary", 820), ("Owner", 480), ("State", 0)])
    y += c.table(X0, y, cols7p, [
        {"cells": [bid("B14"), "**Gate approver**", "A vote", "The tally",
                   "An approver misled, or the same reading taken twice", "ADR-0024, ADR-0050 (attribution only)",
                   "[[red|Outside every theorem]], as the register found"], "accent": "red"},
        {"cells": [bid("B19"), "**Source → artifact** (compilation)", "The build", "Rebuild and compare",
                   "A compiler or crate that inserts below the source (Thompson)", "T-0045-30; this record",
                   "[[red|\"No reproducible build is declared\"]]"], "accent": "red"},
        [bid("B20"), "**Assistant → corpus**", "Drafts and commits on a branch", "The custodian's merge (§5.1)",
         "An instruction injected through repository text, web content or tool output; a claim stated as Met that is "
         "not; a model substituted under the same name; ⟨R1⟩ Run's output relayed through what the assistant reads "
         "(with B22, §8)", "**This record**",
         "Plan mode, and asks for commit and push. Nothing else. ⟨R1⟩ The permission list, the skills and the record "
         "lint are under `.claude/`, which the assistant can write and no manifest measures (F7)"],
        [bid("B21"), "**Custodian → default branch**", "Ratification, merge, tag", "The merge or the tag",
         "Account takeover; a stolen key", "T-0045-11",
         "⟨R1⟩ 104 of 149 commits unsigned at `981bc77`, and the 45 signed are GitHub's merges. GitHub reports `main` "
         "as protected; its rules were not read. One code owner"],
        [bid("B28") + " ⟨R1⟩", "**Checker → gate verdict** (CI)", "A pass or a refusal", "The required check",
         "A change that edits the checker that grades it; a checker that crashes or prints nothing",
         "ADR-0069 §10.2 (Proposed); this record, §5.3",
         "A ratcheted check passes on a crash, and every check runs from the change's own tree (F6)"],
        {"cells": [bid("B29") + " ⟨R1⟩", "**Drafting session → provider** (what the session reads)",
                   "Everything the session reads", "**None**",
                   "The provider and its logs; an injected instruction that sends what was read elsewhere",
                   "**This record**",
                   "[[red|No instant.]] A session can read embargoed safety findings and any key in the workspace "
                   "(A-0070-6)"], "accent": "red"},
    ], size=13.5, accent="ink") + 18
    y += row_cards(c, X0, y, WW, 40, [
        ("Boundaries compose ⟨R1⟩ (§2.4)", [
            "**B22 and B20 meet in the assistant.** Run's output reaches an assistant session as `untrusted` ingress, "
            "and leaves it as a draft with no Run provenance. §5.1 and §8 close that path.",
        ], "red", {"tint": False}),
        ("B11, the deployment rung, is unchanged (§2)", [
            "ADR-0023 and ADR-0058 own it. It is the one register boundary with no row in §2's tables.",
        ], "grey", {}),
        ("What §2 still owes (Open obligations) ⟨R1⟩", [
            "**The predicate and its evidence for each row**, when a deployment instantiates §2 (§1 item 3). "
            "**Confidentiality across the inventory**: R1 names one boundary (B29) and one assumption (A-0070-6), for "
            "the drafting session only. **Tenancy (B24) and jurisdiction (B25)**, each still without an owner record.",
        ], "amber", {}),
    ], size=S) + 70

    # ================================================================== band 4: context
    y = band(c, X0, y, "Context: the corpus secures the admit path, and the lifecycle around it in pieces; ADR-0069 "
             "and this record divide the ground")
    wl = 1700
    xr = X0 + wl + 50
    wr = WW - wl - 50
    bl = stack(c, X0, y, wl, [
        ("The tree shows the same gaps (Context, at `981bc77`, with `e1acade` marked ⟨R1⟩)", [
            "⟨R1⟩ At `981bc77` there was no CI, and the review found four checkers that \"pass, or stay silent, on a "
            "failure\" (CR-57). At `e1acade`, ADR-0069 §10.2's workflows run on every pull request. Four of their seven "
            "checks run through a ratchet that passes a checker which crashes (F6).",
            "⟨R1⟩ The install scripts check no digest when they download (`tools/install-tla.sh` line 15, "
            "`tools/install-tlaps.sh` line 36, `curl -L`). The TLC jar is tracked and checked against a full digest "
            "(`tools/TLA-PIN`, `tools/check-pins.sh`). CI checks cvc5 and elan's installer by full digest. Cargo checks "
            "the SHA-256 that `mechanism/Cargo.lock` records for 435 of its 443 packages; the other eight are the "
            "workspace's own.",
            "`tools/TLAPS-PIN` says \"The release tag floats\". The pin is a 16-hex prefix, and \"The full digest is "
            "owed\".",
            "⟨R1⟩ `mechanism/docker-compose.yml` (line 9) runs `openpolicyagent/opa:latest`. "
            "`mechanism/scripts/build-bundle.sh` (line 22) compiles the bundle's Wasm with the untagged "
            "`openpolicyagent/opa`, which no Annex A row names.",
            "`manifests/EXCLUDE` keeps the install scripts and the pin-enforcing wrappers (`tools/tlapm`, `tools/tlc`) "
            "out of every checkpoint manifest. ⟨R1⟩ It keeps `.claude/` and `.github/` out too (F7).",
            "⟨R1⟩ 104 of the 149 commits on the branch carry no signature. The 45 that do are merges GitHub made. "
            "GitHub reports `main` as protected. Its rules were not read. `CODEOWNERS` names one owner for every path.",
            "T-0045-30 reads: \"**No reproducible build is declared**\".",
        ], "red", {"tint": False}),
        ("The developer is two parties (Context) ⟨K4⟩", [
            "\"Every record, specification, proof, policy, test and line of code was written or ratified by one person, "
            "working with an AI assistant\" (REVIEWERS_GUIDE). ToO §0: \"Assisted drafting is now the rule and not the "
            "exception\". ADR-0029 has no criterion for it (G11 item 66). The assistant's constraints are three lines "
            "of `.claude/settings.json`: `NotebookEdit` denied, `git commit` and `git push` asked, and plan mode by "
            "default. The rest is skill prose. The review's highest finding: \"the corpus can now be extended faster "
            "than it can be kept true\" (CR-61).",
        ], "brown", {}),
    ], size=S)
    c.text(xr, y + 16, "**Where both speak, this record defers to ADR-0069** (Context; the table whole)", 16, "ink")
    t = c.table(xr, y + 32, fill_cols(wr, [("Here", 300, {"bold": True}), ("ADR-0069", 260), ("How they meet", 0)]), [
        ["§5.3, gate evidence signed", "§6 G-1, G-2", "ADR-0069 decides it; this record cites it"],
        ["§5.3, CI", "§10.2, §10.3", "ADR-0069 repurposes f1-tla's workflows; this record asks fail-closed checkers of "
         "them. ⟨R1⟩ **They conflict**: §10.2's ratchet passes a checker that crashes, and §5.3 refuses that (F6)"],
        ["§6.3, signed bytes", "§7 S-1", "S-1 recomputes the digest at signing; this record adds a recomputation at "
         "load (F1)"],
        ["§6.4, a second builder", "§6 G-4", "G-4 finds mechanism code has no gate; this record proposes one"],
        ["§8, intake and return", "§2 to §5", "ADR-0069 decides them; this record adds the removal form of \"enables "
         "nothing\" and the evidence path"],
        ["T-0070-2, the repository host", "§9 C-1, C-2", "**They differ.** §10 reconciles them on one condition"],
    ], size=14, accent="amber")
    br = stack(c, xr, y + 32 + t + 18, wr, [
        ("The register said so on 2026.09.13 (Context)", [
            "ADR-0069 decides one ordered path from intake to rollout: its stages, intake into a corpus root, return "
            "from Run, gates as programs with signed evidence, signing after the tally, and carriers. **This record "
            "decides what every boundary declares, the inventory, each artifact's life after rollout, the tandem "
            "developer, the stand-up, staged reach, the advisory path and the improvement loop.** Companion: ADR-0069 "
            "(Proposed, merged to `main` at `bb76b46` ⟨R1⟩). Its §11, §12, Options, Annexes and History were not read "
            "(provenance note).",
            "**Depends on** ADR-0002, 0007, 0015, 0022, 0024, 0025 to 0027, 0029, 0032, 0034, 0044, 0045. **Relates "
            "to** ADR-0016, 0017, 0021, 0031, 0033, 0039, 0046, 0047, 0051, 0053; ADR-0035, 0057, 0058, 0065 (all "
            "Proposed); ADR-0068 (TM10, supply chain; Proposed); the register; ToO §10 and §13. **Closes** nothing.",
        ], "grey", {}),
    ], size=S)
    y = max(bl, br) + 70

    # ================================================================== band 5: §3 artifacts
    y = band(c, X0, y, "Every production target artifact has a build-side check, a boundary check, run checks and an "
             "end (§3) ⟨K3⟩", status="proposed", extra="the common rule is the drafter's choice")
    y += c.para(X0, y, WW, "The artifacts are the kinds the records name as crossing B1 (ADR-0024 §1 and A3; ADR-0035 §4; "
                "ADR-0054, Proposed), plus the two that reach Run without promotion (the genesis bundle and anchor "
                "issuances). **The common rule, for every row:**", 14, "muted") + 10
    y += row_cards(c, X0, y, WW, 24, [
        ("(a) Hermetic build", ["Built in a Build round from pinned inputs, by allowlisted tools only (ADR-0022 §3), so "
                                "its sealed topic-set digest is its provenance (ADR-0021 §4)."], "blue", {}),
        ("(b) The bytes are signed", ["The digest that is signed and voted on is the digest of the bytes the mechanism "
                                      "will load. Not a source digest, a revision string or a file name. **The load "
                                      "recomputes it (F1).** ⟨R1⟩ Where more than one engine evaluates the artifact, "
                                      "as the bundle's sidecar and its in-process fallback do, each is held to the "
                                      "signed digest."], "teal", {}),
        ("(c) A bill of materials", ["An SBOM the gate projects from the round's `consumed` set as ADR-0035 §1 projects "
                                     "lineage. An authored SBOM is a cross-check, and a divergence is *Contested*."],
         "blue", {}),
        ("(d) Code is rebuilt", ["⟨R1⟩ By a second, independent builder from the same pinned toolchain, and the digests "
                                 "must match (§6.4)."], "blue", {}),
        ("(e) A declared end", ["Expiry, revocation or retirement."], "green", {}),
    ], size=S) + 24
    cols6 = fill_cols(WW, [("Artifact", 520, {"bold": True}), ("Build-side check", 700), ("At B1 (promotion)", 560),
                           ("In Run: load, grant, admit", 640), ("Over its life", 440), ("End", 0)])
    y += c.table(X0, y, cols6, [
        ["**Mechanism release** (validator, floor engine, resident genesis rules)",
         "(a) to (d); `cargo test`; drift; floor gates; dependency audit", "Quorum; reproducible digest from two builders",
         "Loaded by digest; floor bytes refused unless they match the gated digest (ADR-0033 §2)",
         "Advisories against its SBOM (§7)", "Superseded by a release; revoked by digest"],
        ["**Rules floor**", "A release (ADR-0026 §4)", "As a release, two-key", "Resident", "—", "A new release"],
        ["**Policy floor and its values**", "Cedar gates; the proof checker (T-0045-14)",
         "Quorum; floor fitness at bootstrap (ADR-0029 A4)", "Resident; verified evaluator (ADR-0030 §3)",
         "Invariant monitors (§7)", "Release or issuance (ADR-0026 §5)"],
        ["**Operational bundle** (Wasm and `data.json`, with the allowlist)",
         "Rego tests; ADR-0049 W1 to W10; a compile by a pinned OPA", "Quorum; signature over the tarball's loaded bytes",
         "Load recomputes the digest (F1); `¬bundle_deny` only", "Correlator folds",
         "A new revision at the next grant (ADR-0031 §4)"],
        ["**Persona** (weights, configuration, decoder)",
         "Lineage projected (ADR-0035, Proposed); deny-only evaluation (ADR-0016 §3)", "Quorum; independence table",
         "Attested at grant and renewal; a lease field", "`T_persona`; decode observability (ADR-0019)",
         "Targeted revocation (ADR-0031 §5)"],
        ["**Independence table**", "Computed once, in Build (ADR-0035 §4)", "Promoted", "Read at the tally, never at grant",
         "—", "With either Persona"],
        ["**Seating**", "Gates attested (ADR-0050 §4)", "Quorum; seats a principal", "First lease from the quorum", "—",
         "Revocation"],
        ["**Workflow graph** (Proposed)", "ADR-0054", "Voted with its seatings", "Routes re-checked where applied", "—",
         "—"],
        ["**Guest image, Wasm runtime, confinement profile**", "(a) to (d); P1 to P7", "Promoted by digest (T-0045-20)",
         "The launch measurement covers them (ADR-0034 §2)", "Re-attestation on renewal",
         "Revoked by confinement digest"],
        ["**Run tool** (module and entry)", "Hermeticity (A2); entry schema (ADR-0049)", "In its bundle",
         "Allowlisted by name and digest", "—", "With its bundle"],
        ["**Deployment declaration** (trusted base, graph)", "ADR-0045, ADR-0058", "Read at the Build promotion gate",
         "—", "Upstream reports", "Re-declared"],
        ["**Genesis bundle**", "The full-corpus review (ADR-0029 A2)", "**Never promoted**: signed by every key-holder",
         "Epoch 0", "—", "Re-genesis"],
        ["**Anchor issuance**", "Bounded by the rules floor (ADR-0026)", "Not promoted: issued", "Rules epoch", "—",
         "A later issuance"],
        ["**Evidence** (gate evidence, results files, manifests)", "Produced by the gate runner (T-0045-13)",
         "Bound into the vote by digest", "—", "Re-run on any pin move", "Frozen, cited by digest"],
    ], size=13.5, accent="ink") + 70

    # ================================================================== band 6: §4 and §5 in full
    y = band(c, X0, y, "Phase 1 (§4) and Phase 2 (§5), item by item", status="proposed")
    g3 = 40
    w3 = (WW - 2 * g3) / 3
    xs = [X0, X0 + w3 + g3, X0 + 2 * (w3 + g3)]
    b1 = stack(c, xs[0], y, w3, [
        ("§4 · The trusted base is evaluated before the first round ⟨K1⟩", [
            "**1.** A stand-up declaration precedes the first Build round of any deployment, and of genesis *(drafter's "
            "choice)*. For each row it records how the row's identity was fixed, and how that was checked on the host "
            "where it runs.",
            "**2.** Nothing third-party runs before its full SHA-256 is checked: tools, toolchains, crates, container "
            "images and Lean and Lake dependencies. **The design argument**: before the check, the download channel is "
            "a trust root; after it, a substitution can only be refused. ⟨R1⟩ **And no further**: trust on first use "
            "pins an upstream compromise faithfully; crates run code at build time (`build.rs`, procedural macros). The "
            "publishers stay a trust-root row (T-0070-9).",
            "**3.** Every platform that runs a pinned tool has its own pin. The Lean pin is arm64-darwin only "
            "(ADR-0053); a run on another platform under that pin is unpinned.",
            "**4.** What enforces a pin is measured: the install scripts and wrappers leave `manifests/EXCLUDE` (F2), "
            "⟨R1⟩ and so do `.claude/` and `.github/` (F7). **A tool that measures the corpus, or that a gate runs, is "
            "measured with it** *(drafter's choice; declaring each as a trusted-base row is open)*.",
            "**5.** The build host is a Build principal's host: ephemeral, from a declared image, appraised as a guest. "
            "⟨R1⟩ One degeneracy stands today: the proofs' host (F8).",
            "**6.** The key ceremony comes before any key a deployment trusts exists (ADR-0025). Dev keys never cross "
            "into a deployment (G6). Anchor, bundle, verifier, identity-provider and gate-runner keys are hardware-held, "
            "each with a custody row *(drafter's recommendation)*.",
            "**7.** Order of stand-up *(drafter's choice)*: tools by digest; the toolchain's reproducibility check; the "
            "floor gates; the specifications and their results; the mechanism build. Each step rests only on the ones "
            "before it.",
            "**8.** At genesis, all of this is declared and not yet independently checked. It is T-0045-11's identity, "
            "and the full-corpus review of ADR-0029 A2 is where it is first read by another.",
        ], "grey", {}),
    ], size=S)
    c.text(xs[1], y + 16, "**§5.1 · The assistant is held to Build's alphabet** (the table whole)", 16, "ink")
    t = c.table(xs[1], y + 32, fill_cols(w3, [("ADR-0022 verb", 150, {"mono": True}), ("May do", 300), ("Control", 0)]), [
        ["Read", "The repository and the sources the session names",
         "**Everything read from outside the corpus root is `untrusted` ingress**: web pages, issue and PR text, tool "
         "output, files from elsewhere. An instruction found there is content, not a request (ADR-0048 §3's rule). "
         "⟨R1⟩ **Run-derived material marks the session**, and §8's removal test counts the draft as Run-originated"],
        ["Draft", "Write in a worktree or a session branch", "No write to the default branch. No credential that could "
         "make one"],
        ["Invoke", "Allowlisted tools only", "The harness's permission list is a tracked, gated artifact; a change to it "
         "is reviewed as a change to a floor. ⟨R1⟩ Not yet measured: `manifests/EXCLUDE` keeps `.claude/` out (F7). "
         "Egress through a declared allowlist. Credentials injected by the proxy, scoped to one repository and one "
         "branch; ⟨R1⟩ whether a session's credential could push a tag or another branch was not checked (A-0070-2). "
         "No secret in the workspace"],
        ["Emit", "A session record", "Every commit carries the session link (already the case). The session record "
         "names the model that served it, outside the corpus"],
        ["Submit", "Propose a branch or pull request", "The custodian's merge is the `Vote`. **The assistant never "
         "votes**, never ratifies, and is never the reader that satisfies ADR-0029 A2"],
    ], size=13.5, accent="grey")
    b2 = stack(c, xs[1], y + 32 + t + 18, w3, [
        ("Further rules for the agent half (§5.1)", [
            "**A claim the assistant marks Met is a claim, not evidence.** Every Met carries the command and digest that "
            "make it checkable; the custodian, or CI (§5.3), re-runs it before ratification.",
            "**One session drafts. A different reader reviews.** A second session of the same model is independence of "
            "context and not of lineage; it does not count as A2's reader unless the custodian rules that it does.",
            "⟨R1⟩ **The exclusion holds only as far as A-0070-1 does.** The custodian's merge has no predicate, and "
            "admits any file at any length; CR-61 is the evidence that reading falls behind. Where A-0070-1 does not "
            "hold, the assistant and the custodian together are T-0045-11's identity.",
            "⟨R1⟩ **What a merge reads is bounded** *(drafter's recommendation)*: a pull request touches one record, "
            "or one artifact and its tests; every Met is re-run by CI.",
            "⟨R1⟩ **The assistant does not grade itself** *(drafter's choice)*: a change to a checker, to `.claude/`, "
            "to `.github/` or to `manifests/EXCLUDE` is drafted alone and gated by the base's copy (§5.3).",
        ], "grey", {}),
    ], size=S)
    b3 = stack(c, xs[2], y, w3, [
        ("§5.2 · The human half is at the gate, and the gate is hardened", [
            "**Account and keys.** A hardware-backed second factor on the repository host; commits and tags signed with "
            "a hardware-held key; the allowed-signers file tracked. ⟨R1⟩ A signature is checked against the signers "
            "file of the tagged commit's parent, so adding a signer is itself signed by one already allowed.",
            "**Branch protection on the default branch.** No direct push, no force-push, merge only through a pull "
            "request whose required checks have passed. ⟨R1⟩ GitHub reports `main` as protected; which rules it holds "
            "was not read.",
            "⟨R1⟩ **The custodian merges, not the host.** A merge made in GitHub's interface is signed with GitHub's "
            "key. A ratifying merge is made and signed locally and then pushed, or it is not a ratification.",
            "**Ratification is a tagged act.** A Batch is a signed tag over the merge commit; the tag, not the merge, is "
            "the instant. ⟨R1⟩ Its message carries the SHA-256 of the Batch's manifest (ADR-0033). A tag signs a "
            "commit id, which is SHA-1 and locates the tree rather than identifying it (ADR-0069 §9 C-5).",
            "**The custodian's own environment is declared**: part of T-0045-11's identity.",
            "**The residual.** At (1, 0), one compromised account is a compromised corpus. The bootstrap's custody "
            "(ADR-0029, at least five humans) is what removes it, and nothing here does. ⟨R1⟩ A signature does not stop "
            "the host from withholding the newest tag, or serving an older one that is validly signed (§10).",
        ], "brown", {}),
        ("§5.3 · Gates before release run on every change and fail closed", [
            "**The gates** *(drafter's choice; the alternative, gates run by hand at each Batch, is today's practice and "
            "CR-57's finding)*: `tools/check-refs.py`, the record lint, `tools/verify-manifest.sh --all`, the drift "
            "test, `spec/proof-sync.sh`, `tools/lean-sync.sh`; the floor gates and `cargo test`; a dependency audit "
            "and a review of each new crate or version; secret scanning; SBOM generation and a reproducibility check "
            "(§6).",
            "⟨R1⟩ ADR-0069 §10.2's workflows run the pins, proof-sync, verify-manifest, drift, lean-sync, check-refs, "
            "the record lint, TLC's results, `cargo test`, the Lean builds and the floor gates. **Four are ratcheted. "
            "They run no dependency audit, no secret scan, no SBOM and no reproducibility check.**",
            "**Each checker fails closed.** A checker that passes on an empty input, or skips silently, is a defect "
            "(CR-57); each carries a planted-defect test that must fail. ⟨R1⟩ A non-zero exit, or output without the "
            "checker's own closing line, is a refusal whether or not the check is ratcheted; `tools/ratchet.py` ignores "
            "the exit status (F6). **A gate runs the base's copy of its checker** *(drafter's choice)*.",
            "**Gate evidence is signed by the gate runner** under a key issued under ADR-0025 §1 (f): the condition on "
            "which T-0045-13 stops being excluded. Until then, evidence is an operator's assertion. ADR-0069 §6 G-1 and "
            "G-2 decide this.",
            "**Pace is bounded by review** *(drafter's recommendation)*: while a checkpoint is owed, or more than an "
            "agreed number of records stand Proposed and unread by anyone but their drafter, new drafting waits. The "
            "review's first remedy for CR-61, written as a stall. The custodian's choice, and the number is open.",
        ], "blue", {}),
    ], gap=18, size=S)
    y = max(b1, b2, b3) + 70

    # ================================================================== band 7: §9 table, §10 rows, assumptions
    y = band(c, X0, y, "Phase 6, the loop, every row (§9) · the trusted base gains ten rows and moves two (§10)",
             status="proposed", extra="ADR-0045 Annex A rows owed")
    c.text(X0, y + 16, "**§9's table, whole**", 16, "ink")
    y += 32
    y += c.table(X0, y, fill_cols(WW, [("Step", 220, {"bold": True}), ("What happens", 1300), ("Instant", 420),
                                       ("Rule", 0)]), [
        ["**Detect**", "Observer and correlator findings; dependency advisories; scenarios and simulations; dated "
         "reviews; SECURITY.md reports; upstream reports (ADR-0058 §6); a checker's failure", "The finding is recorded",
         "**A finding may only subtract** wherever it acts at runtime (ADR-0007)"],
        ["**Register**", "Each finding gets exactly one row in one register, with a severity, an owner record and the "
         "boundary of §2 it is against", "The row exists",
         "The review counts 108 findings \"carried by no list\" (CR-60). A finding without a row is lost"],
        ["**Contain**", "If the finding is against something running: a revocation or an epoch fence, at once",
         "The revocation is ordered", "Subtraction needs no quorum and waits for none (§7.3)"],
        ["**Disposition**", "Applied, declined with reasons, or carried as named debt (ADR-0029 A2's three)",
         "The disposition is written", "Silence is not a disposition"],
        ["**Act**", "The typed act its status allows: an erratum, an amendment, an R-revision, a new record, a new "
         "release", "A Batch, or a promotion", "Accepted text changes only by History row"],
        ["**Prove it closed**", "**A check that fails on the defect and passes on the fix**: a TLC mutation, a "
         "planted-defect test, a floor test, a regression case", "The check is in CI",
         "**A finding closes only when such a check exists** *(drafter's choice)*. A finding with no possible check is "
         "carried as debt, not closed"],
        ["**Re-cut**", "Pins, manifests and the checkpoint", "The cut is signed", "§5.2"],
        ["**Re-read the boundaries**", "Each record names the rows of §2 it touches, and each checkpoint re-reads the "
         "inventory", "The checkpoint", "A new boundary that no row names is a C2 finding against this record"],
    ], size=14, accent="brown") + 36

    c.text(X0, y + 16, "**§10's rows, whole.** Each row is read against ADR-0045 §2: its failure can only subtract, or "
           "its identity is issued. Ids are the drafter's", 16, "ink")
    y += 32
    y += c.table(X0, y, fill_cols(WW, [("Id", 170, {"bold": True}), ("Row", 760), ("Class", 520), ("If it fails", 860),
                                       ("Identity", 0)]), [
        ["T-0070-1", "**The drafting assistant**: model, harness and provider", "**Excluded**",
         "A wrong or hostile draft, which the custodian's act must catch",
         "None. Nothing it produces is in force without the act (§5.1)"],
        {"cells": ["T-0070-2", "**The repository host's access control**: branch protection and the custodian's account",
                   "**Trust root while a merge is the ratification**. **Delegated once §5.2's signed tag is**",
                   "An unratified change on the default branch; once delegated, a refusal",
                   "[[red|Not issued: fails §2 as a trust root]] (finding F4). Folds into T-0045-11 at genesis"],
         "accent": "red"},
        {"cells": ["T-0070-3", "**Commit and tag signing keys**", "Trust root", "A forged ratification",
                   "Allowed-signers file, tracked. [[red|Not issued]] until an anchor key set exists"], "accent": "red"},
        ["T-0070-4", "**The download channel for third-party tools**", "**Delegated, once §4.2 holds**; a trust root "
         "before", "A refusal (after); anything (before)", "The tracked full digests"],
        ["T-0070-5", "**The bundle compiler** (OPA, `opa build -t wasm`)", "Trust root",
         "A Wasm that is not the Rego that was reviewed",
         "The image digest, pinned. ⟨R1⟩ §6.4 reproduces it on the same compiler only, since no second Rego-to-Wasm "
         "compiler exists"],
        ["T-0070-6", "**Container images** used to build or run (OPA, Kafka)", "Trust root for a builder; delegated for "
         "transport", "As T-0070-5; or a stall", "Image digest, never a tag"],
        ["T-0070-7", "**The second builder** (§6.4)", "Trust root, jointly with T-0045-30", "A false \"reproduced\"",
         "⟨R1⟩ The pinned toolchain's digest, and a host, account and key the first builder does not share"],
        ["T-0070-8", "**Build's labelling of admitted Run objects**, once a record decides that Build labels (ADR-0047 "
         "§9; ADR-0069 §5 LR-1)", "Trust root, reserved", "A label leak into Build", "Promotion"],
        ["T-0070-9 ⟨R1⟩", "**Upstream publishers**: crate authors, image publishers, tool releasers", "Trust root",
         "Anything the published bytes do, at build or at run",
         "The tracked full digests, which fix the bytes and not the publisher. It passes §2 only on the reading "
         "T-0070-5 takes, that a pinned digest is an identity"],
        {"cells": ["T-0070-10 ⟨R1⟩", "**What the gate runner installs untracked**: the runner image, the downloads of "
                   "`setup-java` and `setup-python`, apt packages", "Trust root for a gate's verdict, beside T-0045-13",
                   "A false pass", "[[red|None tracked: fails §2]]"], "accent": "red"},
    ], size=14, accent="ink") + 18
    y += row_cards(c, X0, y, WW, 40, [
        ("Moved (§10)", [
            "**T-0045-13**, the gate runner, moves from excluded to trust root when its key is issued (§5.3), as "
            "ADR-0045 §6 already provides.",
            "**T-0045-30** keeps its class. Its residual narrows from \"no reproducible build\" to ⟨R1⟩ the independence "
            "of the two builders and of the double-compiling (§6.4).",
            "**Models stay out of the trusted base, including the one that drafts the corpus.**",
        ], "blue", {}),
        ("T-0070-2 and ADR-0069 §9 (§10)", [
            "ADR-0069 recommends that no carrier be a trust root (C-1, C-2). This record agrees on one condition: if the "
            "ratification's instant is a signed tag that a checker verifies against tracked signers (§5.2), the host can "
            "only refuse ⟨R1⟩ *what the tag says*, and it is delegated *for that*. If the merge itself is the act, as "
            "today, the host can add, and it is a trust root that fails ADR-0045 §2.",
        ], "amber", {}),
        ("For integrity, and not for freshness ⟨R1⟩ (§10)", [
            "The host still serves the bytes every verifier reads. It can withhold the newest tag, or serve an older one "
            "that is validly signed, and by §6.7 a return adds reach back. So a signed tag leaves the host a trust root "
            "for which tag is newest, until a verifier holds the latest Batch's manifest digest from somewhere the host "
            "does not serve *(drafter's recommendation)*. **Signing the tag is necessary for ADR-0069 §9's "
            "recommendation, and not sufficient.**",
        ], "red", {"tint": False}),
    ], size=S) + 36
    c.text(X0, y + 16, "**Assumptions of use, beside ToO §13 (§10), whole**", 16, "ink")
    y += 32
    y += c.table(X0, y, fill_cols(WW, [("Id", 150, {"bold": True}), ("Assumption", 1700), ("If it does not hold", 0)]), [
        ["A-0070-1", "The custodian reads what is ratified, re-runs every Met before ratifying, and does not delegate the "
         "act to the assistant", "T-0070-1's exclusion is false: the assistant's output is in force unread, and every "
         "claim it drafted is the assistant's"],
        ["A-0070-2", "No credential that can write the default branch or a tag is reachable from an assistant session",
         "B20 has no instant"],
        ["A-0070-3", "Third-party bytes run only after a full-digest check",
         "T-0070-4 is a trust root, and every \"checked\", \"proved\" and \"built\" rests on the network"],
        ["A-0070-4", "⟨R1⟩ The two builders share no host, account or key, and the toolchain's double-compiling uses a "
         "compiler of another lineage", "§6.4 reproduces a compromise both builders share faithfully"],
        ["A-0070-5", "Run intake is admitted only through ADR-0069's intake (§8)",
         "Build reads unlabelled Run output; lineage under-approximates its generators"],
        ["A-0070-6 ⟨R1⟩", "Nothing embargoed under SECURITY.md, and no key a deployment trusts, can be read from an "
         "assistant session", "The provider and its logs hold them, and B29 has no instant"],
    ], size=14, accent="ink") + 70

    # ================================================================== band 8: findings
    y = band(c, X0, y, "Findings F1 to F9 (§12): reported, none fixed here", accent="red", status="open",
             extra="each to a disposition; F1 under SECURITY.md")
    fnd = [
        ("F1 · The bundle signature binds a source digest and not the bytes that load", [
            "`build-bundle.sh` computes the revision as a SHA-256 over the Rego sources and `data.json`, compiles the "
            "Wasm with the untagged `openpolicyagent/opa`, and signs `{\"revision\": R}`. `topak-bundle` reads R from "
            "the tarball's own `.manifest`, verifies the signature over `bundle_body(R)`, and loads `data.json` and "
            "`policy.wasm` without recomputing anything against R. **A tarball whose `.manifest` names a signed "
            "revision loads whatever Wasm and `data.json` it carries.**",
            "⟨R1⟩ **A substituted `data.json` adds reach**: it sets each hosted tool's channel target, the label "
            "delivery table, each tool's input types, the tool list and the break-glass Run entries. **The sidecar is "
            "held to less**: it runs with no verification key. **No promoted set is checked at load.** **The "
            "repository is public**; whether F1 stays here is the custodian's decision under SECURITY.md.",
        ]),
        ("F2 · What enforces the tool pins is not measured", [
            "`manifests/EXCLUDE` excludes `tools/install-*.sh`, `tools/tlapm` and `tools/tlc`, the scripts and "
            "wrappers that fetch the tools and refuse an unpinned one.",
        ]),
        ("F3 · No CI at `981bc77`; at `e1acade`, CI that tolerates what stands ⟨R1⟩", [
            "At `981bc77` every gate in §5.3 is run by hand. At this tree the drift pins fail on ADR-0054 and ADR-0055, "
            "whose bytes have moved since they were pinned, and nothing ran to say so. ⟨R1⟩ Since `bb76b46` the "
            "workflows run on `main`; the two drift pins are standing findings that the ratchet lists and passes "
            "(ADR-0069 ⟨R3⟩). Visible, and still not fixed.",
        ]),
        ("F4 · The gate's own boundary fails ADR-0045 §2", [
            "The repository host's access control (T-0070-2) can add, and its identity is issued by nothing. ⟨R1⟩ 104 "
            "of 149 commits are unsigned at `981bc77`; the 45 signed were made by GitHub, with GitHub's key and not the "
            "custodian's. At genesis this is inside T-0045-11's declaration; after bootstrap it needs an issued key "
            "(T-0070-3) or it is not a row.",
        ]),
        ("F5 · Nothing in Annex A names the bundle compiler", [
            "T-0070-5. T-0045-6 covers OPA at evaluation and not at compilation.",
        ]),
        ("F6 · A ratcheted check passes when its checker crashes ⟨R1⟩", [
            "`tools/ratchet.py` ignores the command's exit status and counts only matching output lines; run on a "
            "checker that exits with a traceback, it reported \"added 0\" and exited 0. Four checks in "
            "`.github/workflows/checks.yml` run through it: the corpus pins, `tools/lean-sync.sh`, "
            "`tools/check-refs.py` and the record lint. Every step runs the pull request's own tree, so a change that "
            "edits a checker is graded by the edited one. Against ADR-0069 §10.2 (Proposed), and §5.3 here.",
        ]),
        ("F7 · The tools that measure the corpus are not measured ⟨R1⟩", [
            "`manifests/EXCLUDE` keeps `.claude/` and `.github/` out of every manifest: `.claude/settings.json`, the "
            "skills that direct ratification and manifest cutting, the record lint CI runs, the manifest-cutting "
            "script, and the workflows. The assistant can write all of `.claude/`. F2 named only the install scripts "
            "and wrappers.",
        ]),
        ("F8 · The proofs' evidence comes from a host §4.5 would refuse ⟨R1⟩", [
            "TLAPS runs on the custodian's arm64-darwin machine under `tools/TLAPS-PIN`, whose release upstream no "
            "longer serves, and CI cannot rerun it (ADR-0069 §10.2, G-3). Declared as a degeneracy at §4.5.",
        ]),
        ("F9 · ADR-0069's Status note and §10.2 say its workflows are not on `main` ⟨R1⟩", [
            "They have been since `bb76b46`. Reported and not changed here: it is ADR-0069's to revise (§11).",
        ]),
    ]
    for i in range(0, 9, 3):
        y += row_cards(c, X0, y, WW, 30, [(t, b, "red", {"tint": False}) for t, b in fnd[i:i + 3]], size=13.5) + 18
    y += 52

    # ================================================================== band 9: §11, §13, options
    y = band(c, X0, y, "Dependent entries owed (§11), the ratification condition item by item (§13), and the options",
             status="proposed", extra="every condition Not met")
    wl = 1150
    xr = X0 + wl + 50
    wr = WW - wl - 50
    c.text(X0, y + 16, "**§11 · Owed, not drafted here**: each a pending entry drafted as its own act, after the "
           "custodian's reading", 16, "ink")
    tl = c.table(X0, y + 32, fill_cols(wl, [("Record", 230, {"bold": True}), ("Entry", 0)]), [
        ["ADR-0045, amendment", "§10's rows in Annex A, and T-0045-13's and T-0045-30's cells. The same amendment owes "
         "T-0045-6's stale Annex B cell, which still reads \"Bundle unsigned\""],
        ["ADR-0044, amendment", "§2's signed body becomes the digest of the loaded bytes and not the source revision "
         "(F1), and §3's load recomputes it. Drafted with ADR-0069's entry on the same record"],
        ["ADR-0024, amendment", "Computed provenance (§6.2), a second builder (§6.4), and reach as a tally field "
         "(§6.5). Touches the bootstrap set, as ADR-0024 A4 does"],
        ["ADR-0029, amendment", "A criterion for assisted drafting (G11 item 66), from §5.1"],
        ["ADR-0022, amendment or note", "The assistant's `Submit` and the harness permission list as an allowlist (§5.1)"],
        ["ADR-0035 and ADR-0047", "Nothing from this record. ADR-0069 owes ADR-0035 its R-revision, and its §5 LR-1 "
         "waits on the record that decides whether Build labels"],
        ["ADR-0069, R-revision ⟨R1⟩", "Since it is Proposed. §10.2's ratchet refuses on a checker's non-zero exit, and "
         "gates run the base's checkers (F6). Its Status note and §10.2's \"Not yet\" are stale since `bb76b46` (F9)"],
        ["ToO §10 and §13", "The boundary inventory beside the register, and A-0070-1 to 6 ⟨R1⟩"],
        ["The register", "Derived and frozen. Superseded by §2 for citation and stays as it is"],
    ], size=13.5, accent="amber")
    bl = y + 32 + tl
    c.text(xr, y + 16, "**§13 · Ratification condition**, item by item", 16, "ink")
    NM = "[[red|Not met]]"
    tr = c.table(xr, y + 32, [("Condition", wr - 620), ("Status", 620)], [
        ["**ADR-0069 is ratified first, or with this record**, for §8 and the parts of §5.3 and §6 that cite it. A "
         "clause here that cites an ADR-0069 clause later withdrawn is withdrawn with it",
         NM + ": ADR-0069 is Proposed. ⟨R1⟩ It is merged to `main`, which is not ratification"],
        ["**The custodian's reading of every drafter's choice and recommendation**: §1 items 6 and 7; §3's common rule; "
         "§4.1, §4.6, §4.7; §5.1's exclusion; §5.2; §5.3 including the pace bound; §6.2, §6.4, §6.5; §7.4; §8's three "
         "ways; §9's closing rule; §11's listing. ⟨R1⟩ And R1's: §4.4; §5.1's three added rules; §5.3's base-copy rule; "
         "§6.4 as rewritten; §6.5's live-monitor and round rules; §7.3's triage and bound; §8's marking; §10's "
         "freshness recommendation", NM],
        ["**Each row of §10 is read against ADR-0045 §2**",
         NM + ". T-0070-2 and T-0070-3 fail it as they stand (F4). ⟨R1⟩ T-0070-10 fails it too, and T-0070-9 passes "
         "only on the reading T-0070-5 takes"],
        ["**The inventory of §2 is read for completeness** by someone other than the drafter, since C2 attaches", NM],
        ["**A module states the two properties this record adds and its mutations break them**, by ADR-0046's method: "
         "*staged reach* (no ring is reached before its predecessor's bake-in has passed without a finding, and a "
         "finding never advances reach); *intake never enables* (ADR-0065 §1's removal property, at the Run → Build "
         "boundary)", NM + ": no module is written"],
        ["**The reference** (ADR-0033): the bundle load recomputes the signed digest from the loaded bytes (F1); ⟨R1⟩ "
         "the sidecar's bundle is held to the same signature, or its decision does not count (F1); every image used is "
         "pinned by digest; every install script checks a full digest before execution",
         NM + ": nothing is built"],
        ["**CI runs §5.3's gates on every pull request, each with a planted-defect test that fails**",
         NM + ". ⟨R1⟩ CI runs on this branch since `e1acade`. Four of its checks pass on a crash and every check runs "
         "the change's own checker (F6). None carries a planted-defect test, and four of §5.3's gates are not run"],
        ["**The default branch is protected and commits and tags are signed**",
         NM + " for signing (F4). ⟨R1⟩ GitHub reports `main` as protected. Its rules were not read, so protection is "
         "not shown to be what §5.2 asks"],
        ["⟨R1⟩ **The custodian decides F1's disclosure under SECURITY.md**", NM],
        ["**§11's dependent entries are drafted**, or this record is narrowed so that it owes fewer", NM],
        ["**A reader who is not the drafter** (ADR-0029 A2)",
         NM + ". ⟨R1⟩ The adversarial review of 2026.11.13 was a second session of the same model, and is not this "
         "reader (§5.1)"],
    ], size=13.5, accent="red")
    y = max(bl, y + 32 + tr) + 36
    c.text(X0, y + 16, "**Options considered, whole**", 16, "ink")
    y += 32
    y += c.table(X0, y, fill_cols(WW, [("Option", 760, {"bold": True}), ("Disposition", 0)]), [
        ["**A record per phase**, six records", "[[grey|Not taken for the draft]] *(drafter's recommendation, left "
         "open)*. The six phases share one rule, §1's orientation, and one inventory. **Splitting after the custodian's "
         "reading is recommended** if §5 and §8 are to be ratified before §6's staging, which needs a module"],
        ["**Fold this record into ADR-0069**", "[[grey|Not taken]] *(drafter's recommendation, left open)*. ADR-0069 "
         "decides one path and its stages; this record decides what every boundary declares, each artifact's life, the "
         "tandem developer and the loop, none a pipeline stage. Folding or splitting is the custodian's choice"],
        ["**Adopt SLSA, SSDF or in-toto wholesale**", "[[grey|Not taken.]] Each is a practice this record cites and maps "
         "to. ADR-0021 rejected an in-toto attestation chain in favour of the sealed topic set. The external levels are "
         "a vocabulary for the deployment declaration"],
        ["**The assistant as a trust-root row**", "[[red|Rejected.]] It fails ADR-0045 §2: its failure adds and its "
         "identity is not issued. Excluding it puts the weight on the custodian's act (A-0070-1)"],
        ["**The assistant as a seated principal** under a lease", "[[grey|Not taken now.]] It would need an issued "
         "identity and a mechanism around the harness: the right end state once the corpus has an anchor, left open"],
        ["**Gates run by hand at each Batch**, as today", "[[red|Rejected.]] CR-57 and F3 are what it produces"],
        ["**A bake-in measured in time**", "[[red|Rejected.]] An advance adds reach, and ADR-0032 §2 requires trusted "
         "time for such an interval, which the corpus refuses (ADR-0045 §6). Rounds are counted, as ADR-0052 counts "
         "drills"],
        ["**Run data never enters Build**", "[[grey|Not taken.]] Incidents, traces and outcomes are how §9's loop "
         "learns. They enter as `untrusted`, labelled, erasable ingress that enables nothing"],
        ["**Signing the source revision**, as ADR-0044 §2 does", "[[red|Not kept.]] It signs a name for the bytes and "
         "not the bytes (F1)"],
        ["⟨R1⟩ **A second builder on a second toolchain**, as first drafted", "[[red|Withdrawn.]] Two toolchains do not "
         "produce the same bytes, so the rule could not be met (§6.4)"],
        ["⟨R1⟩ **A ratchet that passes a checker's crash**, as ADR-0069 §10.2 builds it", "[[red|Not kept here.]] A "
         "crash that passes is CR-57's defect inside the gate (F6). A ratchet that refuses on a non-zero exit keeps what "
         "ADR-0069 wanted from it"],
        ["⟨R1⟩ **Keeping Run-derived material out of drafting sessions**", "[[grey|Left open]] *(drafter's "
         "recommendation: marking, §8)*. Stricter, and it would keep the assistant from the incidents §9's loop learns "
         "from"],
        ["⟨R1⟩ **Revoking on every advisory**, as first drafted", "[[amber|Revised]] (§7.3). It made the advisory feed "
         "a switch that could stop a fleet"],
        ["⟨R1⟩ **Declaring `.claude/` and `.github/` as trusted-base rows** instead of measuring them", "[[grey|Left "
         "open.]] Measuring is cheaper, and a row would still need an identity, which a manifest gives"],
    ], size=14, accent="grey") + 70

    # ================================================================== band 10: consequences, open obligations
    y = band(c, X0, y, "Consequences and open obligations", status="proposed")
    g3 = 40
    w3 = (WW - 2 * g3) / 3
    xs = [X0, X0 + w3 + g3, X0 + 2 * (w3 + g3)]
    b1 = stack(c, xs[0], y, w3, [
        ("Positive", [
            "**One inventory, seven columns, and every hole visible.** B18, B19, B22, B24, B25, B26 and B29 ⟨R1⟩ have no "
            "instant today, and the table says so in one place.",
            "**The tandem developer is placed on the pattern's own terms.** A-0070-1 and A-0070-2 can be checked. ⟨R1⟩ "
            "The exclusion is only as good as A-0070-1, and §5.1 now says so.",
            "**A full-digest check moves the download channel from trust root to delegated.** ⟨R1⟩ It reduces the "
            "channel, and not the publishers behind it (T-0070-9).",
            "**Every subtracting response needs no quorum and no clock.** Every adding one (promotion, a ring's "
            "advance, a return, intake) has an instant.",
            "**Findings close on a check**, which addresses CR-60 at the point where findings are lost.",
        ], "green", {}),
    ], size=S)
    b2 = stack(c, xs[1], y, w3, [
        ("Negative", [
            "**The trusted base grows by ten rows** ⟨R1⟩, three of which fail ADR-0045 §2 as they stand.",
            "⟨R1⟩ **A gate runs its checker from the base**, so a fix to a checker counts one change after it is "
            "written.",
            "**Promotion gets slower**: a second builder, a staged reach, and computed provenance, which needs "
            "ADR-0035's method in force.",
            "**Everything in §5.2 is still one person.** At (1, 0) a hardened gate is still a single gate.",
            "**The record is wide.** It cites more than thirty records and owes entries in five records and the ToO, "
            "some jointly with ADR-0069: the CR-61 pattern this record also criticizes, and why §5.3 recommends a pace "
            "bound and the Options a split.",
            "**One author, one day, and no deployment.** ⟨R1⟩ One adversarial review, by a second session of the same "
            "model.",
        ], "red", {"tint": False}),
    ], size=S)
    b3 = stack(c, xs[2], y, w3, [
        ("Open obligations", [
            "**The custodian's reading** of the drafter's choices, and whether to split (Options).",
            "**The two modules** of §13.",
            "**F1 to F9** ⟨R1⟩, each to a disposition. F1 under SECURITY.md's handling.",
            "**Branch protection on the default branch**, checked and recorded. ⟨R1⟩ Reported protected; its rules "
            "still to be read.",
            "⟨R1⟩ **The predicate and its evidence** for each row of §2 (§1 item 3).",
            "⟨R1⟩ **Confidentiality across the inventory.** R1 names B29 and A-0070-6, for the drafting session only.",
            "**The assistant as a seated principal** once an anchor exists: an issued identity, a lease over a "
            "session, and a Persona for the model that serves it.",
            "**Tenancy (B24) and jurisdiction (B25)**, each still without an owner record.",
            "**A threshold for §5.3's pace bound**, if adopted.",
            "**Run-side intake for an overlay** (ADR-0059 to ADR-0068, Proposed): a plane's reports to its peers are "
            "not Run → Build intake, and this record does not decide them.",
        ], "amber", {"status": "open"}),
    ], size=S)
    y = max(b1, b2, b3) + 70

    # ================================================================== band 11: the review annex and history
    y = band(c, X0, y, "The review of 2026.11.13, and where each finding landed (annex, whole) ⟨R1⟩ · History")
    y += c.para(X0, y, WW, "The review is not reproduced elsewhere, as the custodian directed: this table and the ⟨R1⟩ "
                "marks are its record. The ordering and severities are the review's; the dispositions are the "
                "drafter's, and **the custodian has read none of them** (annex).", 14, "muted") + 10
    y += c.table(X0, y, fill_cols(WW, [("#", 60, {"bold": True}), ("The review's finding", 1500), ("Severity", 150),
                                       ("Disposition", 900), ("Where", 0)]), [
        ["1", "F1 understated: `data.json` sets where effects go and how labels are delivered; `policy.wasm` is "
         "unsigned; the sidecar's bytes are checked against nothing; no promoted set at load; F1 stated in a public "
         "record", "[[red|Critical]]", "Applied. Disclosure left to the custodian", "§3 (b), §12 F1, §13"],
        ["2", "The merged CI's ratchet passes a crashing checker, and every check runs the change's own checker",
         "[[red|Critical]]", "Applied", "B28, §5.3, §11, §12 F6, §13, Options"],
        ["3", "The record described `981bc77`, not `main`: no-CI and no-digest claims overstated, a commit count off by "
         "one, branch protection checkable", "[[red|Critical]]", "Applied", "Context, §2, §12 F3, F4, F9"],
        ["4", "The custodian's merge has no predicate, so the exclusion rests on A-0070-1, which CR-61 contradicts",
         "[[amber|High]]", "Applied", "§5.1, Consequences"],
        ["5", "The tools that measure the corpus are excluded from its manifests and writable by the assistant",
         "[[amber|High]]", "Applied", "B20, §4.4, §5.1, §12 F7, Options"],
        ["6", "Run's output reaches Build through an assistant session, with no Run provenance on the draft",
         "[[amber|High]]", "Applied", "§2.4, §5.1, §8, Options"],
        ["7", "A signed tag leaves the host able to withhold or roll back; a tag signs a SHA-1 commit id; the signers "
         "file authorizes itself; GitHub signs its own merges", "[[amber|High]]", "Applied", "§5.2, §10"],
        ["8", "The second builder on a second toolchain could not be met, and no second Rego-to-Wasm compiler exists",
         "[[amber|High]]", "Applied", "§3 (d), §6.4, §10 T-0070-5 and T-0070-7, A-0070-4, Options"],
        ["9", "Staged reach advances on silence, and rounds can be generated by principals", "[[amber|High]]", "Applied",
         "§6.5"],
        ["10", "Revoking on every advisory makes the feed a switch that can stop a fleet", "[[amber|High]]",
         "Applied, bounded to §7.3's own trigger", "§7.3, Options"],
        ["11", "A full digest fixes identity and not trust; publishers and runner installs are unlisted", "[[amber|High]]",
         "Applied", "B18, §4.2, §10 T-0070-9 and T-0070-10, Consequences"],
        ["12", "Confidentiality is absent from the inventory", "Medium", "Applied in part: the drafting session only",
         "§1 item 6, B29, A-0070-6, Open obligations"],
        ["13", "The proofs' evidence comes from an unappraised, unreproducible host", "Medium",
         "Applied, as a declared degeneracy", "§4.5, §12 F8"],
        ["14", "An instant names an event but not the predicate checked, nor evidence that it ran", "Medium",
         "Applied to §1; owed for each row", "§1 item 3, §2, Open obligations"],
        ["15", "\"A finding closes only on a check\" invites checks written to close findings", "Medium",
         "**Not applied.** §9 already carries a finding with no possible check as debt, and §5.3's base-copy rule "
         "keeps a check from being written to pass the change it grades. Whether a check would catch the defect is "
         "left to the reader of each closure", "—"],
        ["16", "The assistant drafted the rules that contain it, from delegated summaries", "Medium",
         "Recorded. The review is not A2's reader", "§13"],
        ["—", "CI's path-citation check refused four citations, each a path with a line number joined to it", "—",
         "Applied: each now gives the line in words", "Context"],
    ], size=13.5, accent="ink") + 30
    c.text(X0, y + 16, "**History**, whole", 16, "ink")
    y += 32
    y += c.table(X0, y, fill_cols(WW, [("Tag", 70, {"bold": True}), ("Kind", 220), ("Change", 2100), ("Source", 700),
                                       ("State", 0)]), [
        {"cells": ["—", "—", "Initial draft. A seven-column boundary contract; an inventory of twenty-seven numbered "
                   "boundaries, B15 to B27 new, and three temporal ones; a build, boundary, run and end check for each "
                   "of fourteen artifact kinds; the six phases ⟨K1⟩; the assistant as an excluded havoc drafter and the "
                   "custodian at the gate ⟨K4⟩; Run → Build as a deny, evidence or labelled ingress; a finding closed "
                   "only by a check; eight trusted-base rows and five assumptions; five findings. Drafted as ADR-0069 "
                   "and renumbered ADR-0070 before it was committed, at the custodian's direction, since ADR-0069 is in "
                   "flight on its own branch; deferring to ADR-0069 where the two overlap",
                   "The custodian's request of 2026.11.13 ⟨K1⟩ to ⟨K4⟩ and direction on the number; the register; the "
                   "review; ADR-0069 at `0024532`", "**Proposed**"], "accent": "amber"},
        ["R1", "Revision before ratification", "**Revised on an adversarial review, after `main` was merged.** Four "
         "path citations given with the line in words. The Context, §2's State cells, F3 and F4 brought to `e1acade`. "
         "F1 assessed: a substituted `data.json` redirects effects and lifts delivery modes, the sidecar is held to "
         "nothing signed, no promoted set is checked at load; disclosure left to the custodian. New F6 to F9. New B28 "
         "and B29, and boundaries composing at the assistant. §1: an instant names its predicate and evidence, and an "
         "adversary may be to confidentiality. §3 (b), (d); §4.2's limit; §4.4 and §4.5 extended; §5.1 gains three "
         "rules and marks Run-derived sessions; §5.2 signs the manifest digest in the tag, checks signers against the "
         "parent, and has the custodian merge locally; §5.3 refuses on a non-zero exit and runs the base's checkers; "
         "§6.4 rewritten; §6.5 counts only live, operator-opened rounds; §7.3 triages and bounds; §8 closes the path "
         "through the drafter; §10 adds T-0070-9 and T-0070-10, qualifies T-0070-2 for freshness, and adds A-0070-6. "
         "§11 owes ADR-0069 an R-revision. §13, Options, Consequences and Open obligations follow. The review annex "
         "maps each finding to where it landed. The title and the decision's orientation are unchanged",
         "An adversarial review of 2026.11.13 by a second assistant session at the custodian's request (the review "
         "annex); the merge of `main` at `e1acade`; CI's path-citation check on the merged branch; the custodian's "
         "direction to fix the citations, revise on the findings, and note the process in this record",
         "Drafted 2026.11.13 by the assistant at the custodian's direction, not reviewed"],
    ], size=13.5, accent="ink")
    return c
