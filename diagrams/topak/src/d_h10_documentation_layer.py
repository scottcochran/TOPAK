"""H10 — User documentation is a derived layer (ADR-0071, ADR-0072, ADR-0073; all Proposed, 2026.11.16, R1 the
same day). The corpus and its revisions as the source, the projection that can be rebuilt, the document set per
role, and the reader over the public API alone; then each record's sections, every table whole, dependent entries
and ratification conditions item by item. Nothing here is modelled, checked or built."""
from lib import Canvas, STATE_G12, STATUS, text_width

ID, SLUG = "H10", "documentation-layer"
RECORDS = ('ADR-0071', 'ADR-0072', 'ADR-0073',)   # the records this diagram draws in full: a name of one opens it

W = 3600
S = 13.5   # body size in the picture's cards and most tables
NM = "[[red|Not met]]"


# ---------------------------------------------------------------- helpers (copied, as AUTHORING.md asks)

def row_cards(c, x, y, widths, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs);
    widths: one per card. Returns the height."""
    h = max(c.card(0, 0, w_, t, b, draw=False, size=size, status=k.get("status"), bullets=k.get("bullets", True))
            for (t, b, _, k), w_ in zip(specs, widths))
    xx = x
    for (t, b, acc, k), w_ in zip(specs, widths):
        c.card(xx, y, w_, t, b, accent=acc, h=h, size=size, **k)
        xx += w_ + gap
    return h


def stack(c, x, y, w, specs, gap=16, size=14):
    """Cards one under another. specs: (title, body, accent, kwargs). Returns the bottom."""
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, **k) + gap
    return y - gap


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def sub(c, x, y, title, size=16):
    c.text(x, y + size, title, size, "ink")
    return y + size + 14


def strip(c, x0, x1, y, items):
    """A status strip: (label, key, extra). key is a library status, or a (label, accent) custom pill."""
    c.text(x0, y + 15, "Status", 15, "faint", bold=True)
    px0 = x0 + 80
    px = px0
    for lab, key, extra in items:
        lw = text_width(lab, 13.5, True) + 8
        if isinstance(key, tuple):
            pw = text_width(key[0], 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > x1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if isinstance(key, tuple):
            px += c.pill(px, y, key[0], key[1], 11.5, dash="2 3") + 26
        else:
            px += c.status(px, y, key, extra) + 26
    return y + 42


def columns(c, x, y, w, gap, blocks, size=14):
    """Equal-width columns of stacked cards. blocks: list of specs lists. Returns the lowest bottom."""
    n = len(blocks)
    cw = (w - (n - 1) * gap) / n
    bottom = y
    for i, specs in enumerate(blocks):
        bottom = max(bottom, stack(c, x + i * (cw + gap), y, cw, specs, size=size))
    return bottom


NOTW = ("Not written", "red")
NOTD = ("Not drafted", "red")
NOTC = ("Not cut", "red")
NORD = ("No reader exists", "red")


def build():
    c = Canvas(ID, "User documentation is a derived layer: a document set for every role, a projection rebuilt "
               "from every revision, and a reader over the public API alone",
               "Three records drafted on one day answer one request of the custodian. **ADR-0071** makes user "
               "documentation a derived layer that decides nothing: twenty-one readers in three positions, "
               "forty-three documents (the diagram's count) across Build, Run, governance, external, every reader "
               "and the overlay, each "
               "unit read at three levels (MI, SI, DI) where a level may leave out and never add, every DI "
               "statement bound by digest to the clause, module, policy and code it describes, and a release cut "
               "under seven mechanical gates. **ADR-0072** serves it as a projection of the corpus at a commit "
               "that can be dropped and rebuilt to the same digests: every revision immutable and addressed by "
               "SHA-256, every checkpoint and release a view equal to `latest`, one table with a composite key "
               "behind the DynamoDB interface, GraphQL and REST generated from one model and read-only. "
               "**ADR-0073** is the reference reader, React with Material UI, a client of that API and nothing "
               "more, with reflow, two colour schemes, a reading mode that never hides a mark, assistive access, "
               "and WCAG 2.2 AA as a dated audit a person signs. **All three are Proposed and nothing in them is "
               "modelled, checked or built**: no unit is written, no gate is a program, no service, store, API or "
               "reader exists, and no dependent entry is drafted.",
               W,
               "ADR-0071 provenance (⟨K1⟩ to ⟨K4⟩, ⟨R1⟩), Status note, Context, Decision §1 to §12 (§2's table, §3's "
               "table, §4's table, §5's two tables, §6's table, §8's table), Options, Consequences, Open obligations, "
               "Annex A, History (initial, R1); ADR-0072 provenance (⟨K5⟩ to ⟨K7⟩, ⟨K10⟩, ⟨R1⟩), Status note, Context, "
               "Decision §1 to §12 (§3's table, §4's table, §7 A-5's table), Options (the engine table, Other "
               "choices), Consequences, Open obligations, Annex A (three tables), History; ADR-0073 provenance "
               "(⟨K7⟩ to ⟨K9⟩, ⟨R1⟩), Status note, Context, Decision §1 to §9, Options (two tables), Consequences, "
               "Open obligations, History; decisions/README.md rows for ADR-0071 to ADR-0073; G12 §1.1 (the "
               "Proposed count, the renumbering) and §7 item 116; ADR-0029 §3, A2, A4; ADR-0005 §1; ADR-0045 §2; "
               "ADR-0057 §2, §3, §7, §8 (Proposed); ADR-0069 §1 P-1, §3 I-5, §6 G-1, §9 C-2, C-5, §10.2, §10.3 "
               "(Proposed); ADR-0074 §2 (Proposed); ADR-0007; ADR-0049 §4; ADR-0050 §4 (provisional); "
               "narrative/README.md, diagrams/README.md, checkpoints/README.md, derived/README.md, manifests/README.md "
               "as the records quote them",
               state=STATE_G12)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    y = strip(c, X0, X1, y, [
        ("ADR-0071, the layer", "proposed", "C2 · drafted 2026.11.16, R1 the same day"),
        ("ADR-0072, the service", "proposed", "C2 on the drafter's reading · 2026.11.16, R1"),
        ("ADR-0073, the reader", "proposed", "no marker on the drafter's reading · 2026.11.16, R1"),
        ("the units, every document of §3", NOTW, ""),
        ("the gates DG-1 to DG-7", "notbuilt", ""),
        ("a manifest of kind `documentation`", NOTC, ""),
        ("the service: ingest, store, API, search", "notbuilt", ""),
        ("the reference reader", NORD, ""),
        ("a conformance report (ADR-0073 §7)", NOTW, ""),
        ("ADR-0071 Annex A's dependent entries", NOTD, ""),
        ("rests on ADR-0057, ADR-0069, ADR-0074 to ADR-0076", "proposed", "none ratified"),
        ("rests on ADR-0050, ADR-0052", "provisional", "Batch 34"),
    ])
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian's request of 2026.11.16, one "
                "message and not a discussion, settled twelve things across ADR-0071 to ADR-0076, numbered ⟨K1⟩ to "
                "⟨K12⟩ once for the six records; these three use ⟨K1⟩ to ⟨K10⟩. **Every other choice is the "
                "drafter's**, marked *(drafter's choice)*, *(drafter's recommendation)* or *(drafter's reading)* in "
                "the records, and each ratification condition ends with the custodian's reading of them. Each "
                "record was **renumbered up by one on 2026.11.16 (R1)** because ADR-0070 was taken by a record in "
                "flight on another branch; no decision text changed. G12 counts the three among its 27 Proposed "
                "records and lists them at item 116: \"Nothing built, no module, no dependent entry drafted.\" One "
                "author, one day, no reader other than the drafter.", 14.5, "muted") + 34

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "The three records as one picture: the corpus is the source, the service projects it, the "
             "reader shows it, the people read it (ADR-0072 §1, §9; ADR-0071 §2, §3; ADR-0073 §1)",
             status="proposed", extra="nothing here is built")
    top = y + 40
    gap = 120
    cw = [470, 470, 560, 470, 480]
    cw.append(WW - sum(cw) - 5 * gap)
    cx = [X0]
    for w_ in cw[:-1]:
        cx.append(cx[-1] + w_ + gap)

    lane_specs = [
        ("The corpus at a commit: the sources", [
            "**The unit files, the records, modules and policies they bind to, and the manifests** (ADR-0072 §1 "
            "P-1). Units live in one tree, one file to a unit; the tree's name and the file's form are not fixed "
            "(ADR-0071 §9). [[red|No unit is written]] (ADR-0071 Status note).",
            "**The archive of record keeps them** (ADR-0074 §2, class C; Proposed). The service is a system of "
            "record for nothing, in ADR-0005 §1's sense (P-1).",
            "**Where a unit and a record disagree, the record wins**, and the state of record is the latest "
            "checkpoint (ADR-0071 §1 D-1).",
        ], "blue", {}),
        ("Gates first, then ingest", [
            "**DG-1 to DG-7 run first**, and nothing is written for a unit that fails one (ADR-0072 §9 I-4; "
            "ADR-0071 §8). Each gate is a program named by digest, mechanical as ADR-0007 requires.",
            "**Ingest is the only way in, and it starts on a digest**: given a commit it resolves a tree and "
            "records its digests; a cut is given the checkpoint's or release's manifest and refuses a tree that "
            "does not verify (I-1, I-2). Run twice on one commit it writes nothing the second time (I-3). A "
            "carrier's merge moves `latest` and is not a cut (I-5).",
            "[[red|Not built]]: no gate is a program (ADR-0071 §12).",
        ], "amber", {"status": "proposed"}),
        ("The store: revisions by digest, views as manifests, one table", [
            "**A revision is the SHA-256 of a unit's canonical bytes, written once** (ADR-0072 §2 L-1, L-2); "
            "reachable by digest, by number from 1 with no gaps, and by time (L-3); nothing ages out (L-5).",
            "**A view is a named manifest**: `latest` moves; `G12` and `DOC-<date>` are cut once and never "
            "change; every operation takes a view and none is defined for `latest` alone (§4 V-1).",
            "**One table, a composite key, two global and one local index; no operation scans; an overwrite "
            "fails at the store** (§5; Annex A). The reference's engine is ExtendDB on PostgreSQL (§6, drafter's "
            "recommendation): [[red|nothing in this corpus has run it]].",
        ], "amber", {"status": "proposed"}),
        ("One model, two generated interfaces", [
            "**The GraphQL schema and the OpenAPI description are generated from one model file** by a pinned "
            "tool, neither edited by hand (§7 A-1); equal, under a parity test (A-2); **read-only**: no "
            "mutation, no method but `GET` and `HEAD` (A-3).",
            "**Every response names its view and its revision digests** (A-4, V-6); a cut view's response is "
            "immutable and cached without limit. Seven operations (A-5, drawn below). Search is a second "
            "projection, built per view (A-8).",
            "[[red|Not built]]: there is no service, no store and no API (Status note).",
        ], "amber", {"status": "proposed"}),
        ("The reference reader, and any other client", [
            "**React with Material UI, a client of the public API and nothing more** (ADR-0073 §1 R-1, §2): no "
            "credential a third party's reader could not hold, no content of its own (R-2), nothing said of its "
            "own but navigation, labels and its accessibility statement (R-3), one code path for every view (R-4).",
            "**None is privileged**: a page, an application, a terminal, a program, an embeddable element "
            "(ADR-0072 §8 U-1, U-5). Content comes as a typed tree, marks and bindings as data (U-2, U-4).",
            "[[red|No reader exists]] (ADR-0073 Status note). The corpus is read today as Markdown that a carrier "
            "renders.",
        ], "amber", {"status": "proposed"}),
        ("The people: twenty-one readers, three positions", [
            "**Inside the proofs, holding a seat**: AU-1 to AU-5, the operator, a grant seat, an author in Build, "
            "the person seated in an emergency, the overlay seats (ADR-0071 §2).",
            "**At the gate, or a trust root**: AU-6 to AU-12, the anchor key-holder, the break-glass and erasure "
            "rosters, the custodian, pipeline keys, trust roots outside the mechanism, the responder.",
            "**Outside the deployment**: AU-13 to AU-21, reviewer, audit authority, adopter, agent developer, "
            "supplier, acquirer, a person acted for, the reporter, a vehicle builder.",
            "**Forty-three documents** for them (the diagram's count of §3's rows: Build 9, Run 8, governance 9, "
            "external 9, every reader 7, the overlay 1). [[red|Unwritten]], except two drafts (Ex-1, Ex-2) and one "
            "file (Ex-8) (S-2).",
        ], "brown", {}),
    ]
    h_lane = row_cards(c, X0, top, cw, gap, lane_specs, size=S)
    lane = top + h_lane / 2
    for i, lab in enumerate(["①", "②", "③", "④", "⑤"]):
        acc = "blue" if i == 0 else ("amber" if i < 4 else "brown")
        c.arrow([(cx[i] + cw[i], lane), (cx[i + 1], lane)], acc, sw=2.6, label=lab, lpos=0.5, lsize=15)

    # second row under the lane, per column
    y2 = top + h_lane + 40
    stacks = [
        [("A binding points back here (ADR-0071 §5)", [
            "**Node**: a record's clause; a module and a named property; a proof module or a Lean file; a floor "
            "stage or a policy; a Rego rule; a crate or a function; a schema; a results file; a trusted-base row; a "
            "degeneracy; a glossary entry; a checkpoint item.",
            "**Pin**: the node's digest when the unit was read against it, a clause's once ADR-0057 §7's clause "
            "pins exist and the file's until then. **Relation**: decides, states, enforces, implements, evidences, "
            "assumes, defines. **Reader**: who read the unit against the node.",
            "**A binding is a pinned citation and not an edge** (B-5; ADR-0057 §3): a unit discharges nothing and "
            "moves no theorem's grade.",
        ], "blue", {"tint": False}),
         ("Staleness (ADR-0071 §7)", [
             "**A binding whose pin no longer matches its node is stale**, and so is the unit (ST-1). It is served "
             "and says so, naming the node that moved (ST-2). **Only a reading clears it; no program re-pins** "
             "(ST-3). A cut view keeps the pins it was cut with (ST-4; ADR-0072 §4 V-2).",
         ], "red", {"tint": False})],
        [("A release is a manifest (ADR-0071 §8)", [
            "**A fifth manifest kind, `documentation`**, over the unit files at a commit, cut with each checkpoint "
            "and whenever the custodian cuts one between *(drafter's choice)*; ADR-0072 §4 makes a view of it.",
            "**What no gate checks: that a unit says what its clause says.** DG-2 finds a binding and cannot read "
            "it. So each unit names who read it against its bindings (RL-1); during genesis a release promotes "
            "nothing and is cut by the custodian (RL-2); after bootstrap, open (RL-3).",
            "[[red|Not cut]]; `manifests/README.md` lists four kinds (§12).",
        ], "amber", {"tint": False, "status": "proposed"})],
        [("A unit's life, and the three views (ADR-0072 §3, §4)", [
            "**drafted, released, superseded, withdrawn**: computed from revisions and views, never stored on the "
            "immutable revision (LC-1). Withdrawal is a revision, not a removal (LC-2). Disposal is not a state: a "
            "unit holds no cognitive payload (LC-4; §10 H-1).",
            "**`latest`** follows the newest ingest of the default branch and is the only view that changes; "
            "**`G12`** is cut with each Genesis Checkpoint against its manifest; **`DOC-<date>`** with each "
            "documentation release. Cut views are written once and never removed (V-3, V-4).",
            "**Rebuild** ⑥: dropping the store and ingesting again yields the same digests, checked by comparing "
            "them (P-2; ADR-0069 §10.2's `results` rule).",
        ], "amber", {"tint": False, "status": "proposed"})],
        [("What the API never does (ADR-0072 §7)", [
            "**It never writes** (A-3): content enters by ingest and by no request. **A version only grows** "
            "(A-6): a field is added or deprecated with a date, never repurposed. **A request cannot exhaust it "
            "by its shape** (A-7): paged by cursor, bounded in depth and cost; this protects availability and "
            "nothing else.",
            "**Who may read is the deployment's rule** (§8 U-6): the archetype's units are public under "
            "`LICENSE-DOCS`; a deployment's own may be restricted, which hides a unit and changes none.",
        ], "amber", {"tint": False, "status": "proposed"})],
        [("What the reader must show (ADR-0073 §3 to §7)", [
            "**One document that reflows** from 320 CSS pixels and at 400% zoom (RD-1). **Two schemes**, the "
            "first visit following the device, both at the same contrast (LD-1, LD-2). **Reading mode is the page "
            "as the server sends it**, needing no script, and it may hide navigation and never a mark or a "
            "binding (RM-1, RM-4; ADR-0029 §3). **Assistive access** as nine requirements AA-1 to AA-9.",
            "**Conformance is WCAG 2.2 Level AA as a dated audit**: a computed part that refuses and never admits, "
            "and an examined part by a person who did not write the reader; a release says *checked* or *claimed* "
            "(WC-1 to WC-3). [[red|No report, no auditor]] (§9).",
        ], "amber", {"tint": False, "status": "proposed"})],
        [("Three levels, and the record wins (ADR-0071 §4, §1, §11)", [
            "**MI**: what is this, and what may I do and not do? **SI**: how does it work, and how do I do it? "
            "**DI**: exactly what, and on whose authority? **A level may leave out, and it never adds** (LV-2). "
            "**A limit travels with the guarantee it limits** (LV-3): a reader who stops at MI has read less, not "
            "something more favourable.",
            "**The documentation decides nothing** ⑦. A wrong document subtracts, or moves a person within a "
            "bound a theorem already assumes: an operator still signs one of six admitted actions; the anchor is "
            "already a havoc issuer (§11). No degeneracy, no trusted-base row. **It does not make its readers "
            "right**: A5 stays an assumption of use.",
        ], "brown", {"tint": False})],
    ]
    bottoms = []
    for i, specs in enumerate(stacks):
        bottoms.append(stack(c, cx[i], y2, cw[i], specs, size=S))
    sbot = max(bottoms)

    # regions
    rtop = top - 50
    rbot = sbot + 30
    c.region(cx[0] - 24, rtop, cw[0] + 48, rbot - rtop, "The sources: the corpus at a commit (ADR-0072 §1 P-1)",
             "blue", dash="10 6")
    c.region(cx[1] - 24, rtop, cx[3] + cw[3] - cx[1] + 48, rbot - rtop,
             "The service: a projection that can be rebuilt, and a system of record for nothing (ADR-0072)", "amber",
             dash="10 6")
    c.region(cx[4] - 24, rtop, cw[4] + 48, rbot - rtop, "Clients: none privileged (ADR-0072 §8; ADR-0073)", "amber",
             dash="10 6")
    c.region(cx[5] - 24, rtop, cw[5] + 48, rbot - rtop, "The readers (ADR-0071 §2)", "brown", dash="10 6")

    # ⑥ rebuild: store -> corpus, below the regions; ⑦ the record wins: readers -> corpus
    y6 = rbot + 50
    y7 = rbot + 100
    x1a = cx[0] + cw[0] * 0.62   # ⑥ enters to the right, ⑦ to the left, so the two never cross
    x1b = cx[0] + cw[0] * 0.38
    c.arrow([(cx[2] + cw[2] / 2, rbot), (cx[2] + cw[2] / 2, y6), (x1a, y6), (x1a, rbot)], "teal", sw=2.2,
            label="⑥", lpos=0.5, lsize=15)
    c.arrow([(cx[5] + cw[5] / 2, rbot), (cx[5] + cw[5] / 2, y7), (x1b, y7), (x1b, rbot)], "grey", sw=2.2,
            dash="7 5", label="⑦", lpos=0.5, lsize=15)
    y = y7 + 40

    # the key to the arrows
    y = sub(c, X0, y, "**The arrows**, each with its clause")
    cols = [("Arrow", 90, {"bold": True}), ("Carries", 1500), ("Clause", WW - 1590)]
    t = c.table(X0, y, cols, [
        ["①", "**The corpus at one commit, read by ingest**: a commit resolved to a tree and its digests; for a cut, the "
         "checkpoint's or the release's manifest, and a tree that does not verify against it is refused",
         "ADR-0072 §9 I-1, I-2; ADR-0069 §1 P-1"],
        ["②", "**Revisions, bindings and, for `latest`, a manifest, written once**: a revision and a cut view's entries "
         "are put with a condition that the key does not exist, and a second, different write of a cut view is refused",
         "ADR-0072 §9 I-1; §5 S-4; §4 V-3"],
        ["③", "**Reads that are key conditions**: every operation is a `GetItem` or a `Query` on the table or one index, "
         "and no operation scans", "ADR-0072 §5 S-2; Annex A"],
        ["④", "**`GET` and `HEAD`, and GraphQL without a mutation**, with cross-origin reads allowed for the public "
         "units; the reader calls this and nothing else", "ADR-0072 §7 A-3, §8 U-5; ADR-0073 §1 R-1"],
        ["⑤", "**A unit at MI, SI or DI with its marks and bindings**, in whichever view the address names, the view "
         "named on the page, every mark a word", "ADR-0071 §4, §5 B-6; ADR-0073 §1 R-2, R-4, §5 RM-4"],
        ["⑥", "**Rebuild**: the store is dropped and ingested again from the corpus, and the rebuild is checked by "
         "comparing digests and not by trust in the rebuild", "ADR-0072 §1 P-2"],
        {"cells": ["⑦", "**The record wins, and the documentation decides nothing**: the service admits no action, counts no "
                   "vote and issues nothing; the reader states nothing of its own; where a unit and a record disagree, "
                   "the record wins and the disagreement is a finding against the unit. Dashed: this path carries no "
                   "authority", "ADR-0071 §1 D-1, D-2; ADR-0072 §1 P-3; ADR-0073 §1 R-3"], "accent": "grey"},
    ], size=S, accent="grey")
    y += t + 16
    lg = c.legend(X0, y, [
        ("box", "blue", "the corpus: records and what they cite"),
        ("box", "amber", "Proposed: the service and the reader, not built"),
        ("box", "brown", "the people who read"),
        ("arrow", "teal", "a rebuild, checked by digest"),
        ("arrow", "grey", "no authority: the record wins", "7 5"),
        ("box", "red", "what does not exist"),
    ])
    y += lg + 80

    # ================================================================== band 2: headers side by side
    y = band(c, X0, y, "The three records' status lines and header fields, side by side (the diagram's "
             "arrangement; each cell is the record's own text, in effect)", status="proposed")
    cols = [("Field", 300, {"bold": True}), ("ADR-0071 · the layer", (WW - 300) / 3),
            ("ADR-0072 · the service", (WW - 300) / 3), ("ADR-0073 · the reader", (WW - 300) / 3)]
    t = c.table(X0, y, cols, [
        ["Status", "[[amber|Proposed]] · 2026.11.16", "[[amber|Proposed]] · 2026.11.16", "[[amber|Proposed]] · 2026.11.16"],
        ["Status note: markers",
         "**C2** attaches and no other: §2 and §3 claim every role has a document and every document a role. C1: "
         "documents about privileged paths are listed (Rn-3, Rn-8, Gv-2), and a document is not a proof obligation "
         "over one. C3: nothing accepted is reversed. C4: no debt is resolved; a document cannot supply what no "
         "record decides (§1 D-4)",
         "**C2** attaches and no other: §2 and §4 claim no revision and no cut view is unreachable, about a derived "
         "layer and not the admit path; a reviewer may read C2 as not reaching that far. C1: no privileged path. "
         "C3: nothing reversed. C4: no accepted record owes this service",
         "**No confirmation criterion attaches** on the drafter's reading. C1: no privileged path is touched. C2: §7 "
         "claims conformance of a set of pages a release names, by audit. C3: nothing reversed. C4: no accepted "
         "record owes a reader"],
        ["Status note: what exists",
         "[[red|Nothing here is modelled, checked or built.]] No unit is written. Two guides exist as drafts, measured "
         "by no manifest, and the word \"runbook\" appears in no record, in neither guide and in no README",
         "[[red|Nothing here is modelled, checked or built.]] There is no service, no store and no API. Documentation "
         "is files in a repository, read through a carrier",
         "[[red|Nothing here is modelled, checked or built.]] No reader exists. The corpus is read today as Markdown "
         "that a carrier renders"],
        ["Pending", "none", "none", "none"],
        ["Deployment position",
         "Archetype. A method declaration, as ADR-0046 and ADR-0057 are. A deployment's own documentation is an "
         "overlay (ADR-0072 §10 H-3)",
         "Archetype for §1 to §5 and §7 to §10, as requirements on any service that claims to serve TOPAK's "
         "documentation. §6 and Annex A are the reference's choices, substitutable as §6 says",
         "Archetype for §1 and §3 to §7, as requirements on any reader that claims them. §2 is the reference's choice "
         "of libraries; a deployment that makes another makes no declaration by doing so (§8)"],
        ["Depends on",
         "ADR-0029 §3; ADR-0045 Annex A (the people rows); ADR-0050 (operators; provisional); ADR-0024 and ADR-0025 "
         "(grant seats; the anchor)",
         "ADR-0071 (units, levels, bindings, releases; Proposed); ADR-0005 §1 (what a system of record is, and that a "
         "store which is not one says so)",
         "ADR-0072 (the service and its API; Proposed); ADR-0071 (the units, levels, bindings and marks a reader "
         "shows; Proposed)"],
        ["Relates to",
         "ADR-0072, ADR-0073, ADR-0074 to ADR-0076 (Proposed); ADR-0057 §1, §3, §7, §8 (Proposed); ADR-0058 §1 "
         "(Proposed); ADR-0069 §3a, §6, §10.3 (Proposed); ADR-0007",
         "ADR-0073, ADR-0074 to ADR-0076 (Proposed); ADR-0069 §1 P-1, §3 I-5, §8, §9 (Proposed); ADR-0057 §8 "
         "(Proposed); ADR-0045 §2; ADR-0033 §2 (the substitution rule)",
         "ADR-0069 §9 C-2 and §10.2 (Proposed); ADR-0029 §3; ADR-0045 §2"],
        ["Closes · Carries a debt against", "nothing · nothing. Annex A lists what other records would owe",
         "nothing · nothing", "nothing · nothing"],
        ["What the custodian settled, used here",
         "⟨K1⟩ documentation \"targeting operators, anchors, principals at the gate, etc.\"; ⟨K2⟩ \"exhausively list "
         "for: build, run, external, governance, etc.\"; ⟨K3⟩ \"follow a c4 progressive disclosure pattern: "
         "MI,SI,DI\"; ⟨K4⟩ \"Must map back to ADRs, formal specs, policy as code, etc at the DI level, and as "
         "appropriate at SI and MI levels\"",
         "⟨K5⟩ a store that is \"an open source alternative for Dynamodb which supports single table composite primary "
         "secondary key design\", with alternatives listed; ⟨K6⟩ \"server side must support for a graphql API and "
         "rest API\"; ⟨K7⟩ \"must support arbitrary UI integration\"; ⟨K10⟩ \"Must support full information "
         "lifecycle, every revision must be accessible, every checkpoint/release must be accessible equal to the "
         "latest\"",
         "⟨K7⟩ \"must support arbitrary UI integration\"; ⟨K8⟩ the \"ui should be react and material UI, listing "
         "alternatives\"; ⟨K9⟩ \"must support responsive display must support light and dark modes. must support "
         "minimalist reading mode and assistive access. WCAG Compliance\""],
        ["Two readings put to the custodian (ADR-0071 provenance); outside sources (ADR-0072, ADR-0073)",
         "The letters MI, SI and DI are not expanded in the request and appear nowhere in the corpus as a "
         "documentation term (§4 reads them as main, supporting, detailed). \"Principals at the gate\" joins two "
         "things the corpus keeps apart (§2 reads it as two groups)",
         "Outside sources read 2026.11.16, none run: ExtendDB (AWS's announcement of 2026.05.20, README, releases, "
         "`docs/differences-from-dynamodb.md`, partly as a fetch agent's summary); ScyllaDB's Alternator page and "
         "FAQ; three pages of Cassandra 5.0's documentation. Every other product from the drafter's knowledge, "
         "licences unchecked",
         "The W3C's announcement that WCAG 2.2 is ISO/IEC 40500:2025 and its WCAG 3.0 Working Draft page, read as "
         "search summaries; success criteria cited from the drafter's knowledge and not re-read; EN 301 549 V4.1.1's "
         "date from one secondary source, not relied on. No library installed or run. The custodian named no WCAG "
         "version and no level"],
        ["⟨R1⟩ numbering", "First drafted as ADR-0070; ADR-0070 is *The lifecycle is secured at its boundaries*, in "
         "flight on branch `ccr-dd716f39-ywh7ud` at `593af40` (pull request #51), not merged, not read beyond its "
         "header", "First drafted as ADR-0071; the same", "First drafted as ADR-0072; the same"],
    ], size=S, accent="amber")
    y += t + 80

    # ================================================================== ADR-0071
    y = band(c, X0, y, "ADR-0071 · User documentation is a derived layer with a document set for every role "
             "(Context; §1)", status="proposed", extra="C2 · drafted 2026.11.16, R1")
    y = columns(c, X0, y, WW, 40, [
        [("Context: written for the people who judge it, not yet for the people who would act under it", [
            "A Reviewer's Guide and an Adopter's Guide, both drafts; a Theory of Operation, a glossary and an "
            "architecture description whose stakeholder table names eight readers. **No document for an operator, a "
            "key-holder, a grant seat, a break-glass roster or the person seated by one, an erasure roster, or an "
            "auditor.**",
            "ToO assumption A5: \"A trained, authorized human is present\". **No record says what the training is, "
            "and nothing exists to train from.**",
        ], "grey", {"tint": False}),
         ("Three things in the corpus shape the answer", [
             "**A document that restates a guarantee can misstate it.** \"Where the narrative and the current "
             "checkpoint disagree, the checkpoint wins\" (`narrative/README.md`); \"Where a diagram and a record "
             "disagree, the record wins\" (`diagrams/README.md`). The Adopter's Guide: \"Every **must** cites the "
             "record clause it comes from\", \"Every **should** is advice the records do not contain\".",
             "**A summary is where a caveat is lost.** Progressive disclosure, done carelessly, discloses the "
             "guarantee first and the limit three clicks later.",
             "**Some readers are inside the proofs and some are not.** \"A principal is anything evictable by an "
             "authority other than itself. Whatever is not is at the gate.\" An operator is bounded by the admit "
             "path; a key-holder at archetype custody only by the rules floor (§11).",
         ], "grey", {"tint": False})],
        [("§1 · Derived, and it decides nothing", [
            "**D-1.** A unit states what records, modules, policies and code already state, for a named reader. "
            "Where a unit and a record disagree, the record wins; the disagreement is a finding against the unit, "
            "\"whichever layer is right\".",
            "**D-2. Documentation ranks last.** In the Reviewer's Guide's order (state of record, decisions, "
            "narrative, evidence, derived) it sits with the derived layer and below the narrative, which it may "
            "cite and never overrides.",
            "**D-3. Three kinds of sentence, and each says which it is**: a **must** (*cannot*, *never*) restates a "
            "clause and is bound to it (§5); a **should** is advice the records do not contain, marked *advice*, "
            "and binds nobody; where the corpus supplies nothing and a deployment has to, the unit says \"the "
            "deployment writes this\" and names the open item.",
            "**D-4. A unit does not supply what no record decides.** It says that no record decides it and cites "
            "the open obligation; it does not invent the procedure. §3's last column lists where this bites.",
            "**D-5. A unit carries the status of what it describes** (§5 B-6), at every level it speaks at.",
        ], "amber", {"status": "proposed"}),
         ("§2's rules beside its table", [
             "**A-1.** The list is every person or organization the corpus names as acting on a deployment or "
             "judging it; a role a record names that has no row is a finding against this record.",
             "**A-2.** A record that adds a role owes a row, as a record that adds a term owes the narrative its "
             "definition.",
             "**A-3.** One person may be several readers: \"A person who operates and also votes holds two seats and "
             "is two principals\" (ADR-0037), and the documents follow the seats.",
             "**A-4. The assistant is not a reader of user documentation.** Its documents are the skills; a model "
             "at a seat learns its tools from the mechanism (ADR-0048), never from a unit.",
         ], "amber", {"status": "proposed"})],
        [("§2 · \"principals at the gate\" read as two groups (drafter's reading)", [
            "The corpus defines each against the other, so no reader is both at once. The table adds a third group "
            "the request's \"etc.\" covers: readers outside the deployment.",
        ], "amber", {"tint": False}),
         ("§3's rules beside its table", [
             "**S-1.** Every reader of §2 appears in at least one row, and every row names at least one reader; "
             "DG-6 computes both.",
             "**S-2. The set is a list of what is owed, not of what exists.** Two rows have a draft today (Ex-1, "
             "Ex-2) and one has a file (Ex-8). [[red|The rest are unwritten.]]",
             "**S-3.** A document whose records are all Proposed may be written and is marked (§5 B-6): it "
             "describes a design not in force, and says so at its head.",
             "**S-4.** Operators have one document in each domain (Bd-1, Rn-1), because the seat is \"declared in "
             "the issued rules with a domain\" (ADR-0050 §1). The corpus names no \"Build operator\" role, and "
             "this record adds none.",
         ], "amber", {"status": "proposed"}),
         ("The request's domains and the drafter's two more (§3)", [
             "Build, Run, external and governance are the request's ⟨K2⟩. Its \"etc.\" is read as **what every "
             "reader needs** (Cx) and **the Proposed command-chain overlay** (Ov) *(drafter's reading)*.",
         ], "amber", {"tint": False})],
    ], size=14) + 50

    # §2 table
    y = sub(c, X0, y, "**§2 · The readers ⟨K1⟩, whole** (AU-1 to AU-21)")
    cols = [("Id", 90, {"bold": True}), ("Reader", 1150), ("Where the corpus names it", 1050),
            ("Position", WW - 2290)]
    t = c.table(X0, y, cols, [
        {"group": "Inside the proofs: people who hold a seat", "accent": "teal"},
        ["AU-1", "**Operator**, a seat of kind `operator` in one domain", "ADR-0050 §1, §4 (provisional)",
         "Principal, `Mediated`"],
        ["AU-2", "**Grant seat**: a promotion voter, and after bootstrap a voter on confirmation promotions",
         "ADR-0024; ADR-0029 §6", "Principal on every rung (ToO §7.5)"],
        ["AU-3", "**Author in Build**: a person at a `thinker` seat, recused from the vote on what they submit; a "
         "bundle author", "ADR-0024 §6; ADR-0037; ADR-0048", "Principal"],
        ["AU-4", "**The person seated in an emergency**", "ADR-0052 (provisional)",
         "Holds a seat for one round, `Mediated`"],
        ["AU-5", "**Overlay seats**: a commander, a person at a `release` seat, a person at an `orchestrator` seat",
         "ADR-0060, ADR-0066 (Proposed)", "Principals, if those records are ratified"],
        {"group": "At the gate, or a trust root: people the proofs assume", "accent": "brown"},
        ["AU-6", "**Anchor key-holder**", "ADR-0025; T-0045-9",
         "At the gate at archetype custody; a principal at degenerate custody (ToO §7.5)"],
        ["AU-7", "**Break-glass roster member**", "ADR-0052; ADR-0013; T-0045-12",
         "Trust-root row; not classed by a record"],
        ["AU-8", "**Erasure roster member**", "ADR-0025 §1 (b); ADR-0013",
         "Not stated. No roster is issued at genesis (ADR-0029 §5)"],
        ["AU-9", "**Genesis custodian**", "ADR-0029 §1; T-0045-11", "Trust-root row"],
        ["AU-10", "**Keeper of a pipeline key**: the bundle signer; whoever keeps the gate runner",
         "T-0045-27; T-0045-13 (excluded)", "Trust-root row; excluded row"],
        ["AU-11", "**Operator of a trust root outside the mechanism**: the host operator, an identity provider's "
         "administrator, the independent verifier", "T-0045-19; T-0045-35; T-0045-17", "Trust-root rows"],
        ["AU-12", "**The responder**: the person who answers a finding within `D` and releases a quarantine",
         "ToO A5; ADR-0032", "Unmodelled. No record names the role"],
        {"group": "Outside the deployment", "accent": "grey"},
        ["AU-13", "**Bootstrap reviewer**, and any reviewer", "ADR-0029 A2", "Outside; \"an environment event\""],
        ["AU-14", "**Audit authority**, including the external auditor", "ADR-0028 §3",
         "Not stated. The role is an open obligation of ADR-0028"],
        ["AU-15", "**Adopter**: the platform engineer who declares and builds a deployment", "The Adopter's Guide §1",
         "Outside"],
        ["AU-16", "**Agent developer**, building what sits behind a seat's alphabet",
         "The architecture description, S7", "Outside"],
        ["AU-17", "**Supplier** of a tool, a Persona, a policy library or a mechanism", "ADR-0058 §7 (Proposed)",
         "Outside"],
        ["AU-18", "**Acquirer or assessor**", "The architecture description, S8", "Outside"],
        ["AU-19", "**A person a deployment acts for or holds data about**: the subject of a call; someone asking for "
         "erasure; the owner of a downstream system", "ADR-0056 (Proposed); ADR-0003; ADR-0006",
         "Outside. \"A subject is not a principal\" (ADR-0056)"],
        ["AU-20", "**Reporter of a safety finding**", "`SECURITY.md`", "Outside"],
        ["AU-21", "**Builder of a vehicle** under the command-chain overlay", "ADR-0068 (Proposed)", "Outside"],
    ], size=S, accent="brown")
    y += t + 50

    # §3 table
    y = sub(c, X0, y, "**§3 · The document set ⟨K2⟩, whole** (forty-three rows, the diagram's count; the last column is "
            "what D-4 obliges a document to say and not to fill)")
    cols = [("Id", 90, {"bold": True}), ("Document", 980), ("Readers", 250), ("Rests on", 900),
            ("Not yet decidable from the records", WW - 2220)]
    t = c.table(X0, y, cols, [
        {"group": "Build", "accent": "blue"},
        ["Bd-1", "Operating Build: `Regrant`, `Renew` and `AttestGates`; the denies; working with a peer", "AU-1",
         "ADR-0050 §4, §6; ADR-0024 A3", "\"What a peer must have read before an add proceeds\" (ADR-0050 §8)"],
        ["Bd-2", "Voting on a promotion: what a vote binds to, the gate evidence, recusal, independence", "AU-2",
         "ADR-0024; ADR-0021 §4; ToO A4",
         "How independence is shown. Gates for some classes (ADR-0069 §6 G-4, Proposed)"],
        ["Bd-3", "Authoring in Build: the alphabet, the corpus root, `Submit` and the seal, what the Observer reads",
         "AU-3", "ADR-0022; ADR-0021; ADR-0039", "—"],
        ["Bd-4", "Writing a bundle and an allowlist entry: purpose text, labels, channels, what is checked and what "
         "is claimed", "AU-3, AU-17", "ADR-0030; ADR-0044; ADR-0047; ADR-0048; ADR-0049", "—"],
        ["Bd-5", "Running the gates and keeping their evidence", "AU-10, AU-1", "ADR-0007; ADR-0030 §5; T-0045-13",
         "Who the gate runner is, and its key (ADR-0069 §6 G-2, Proposed)"],
        ["Bd-6", "Intake: admitting to a corpus root, and what returns from Run", "AU-1, AU-2, AU-3",
         "ADR-0069 §3 to §5 (Proposed)", "All of it is Proposed"],
        ["Bd-7", "Training and verifying a Persona; lineage and independence", "AU-3, AU-2",
         "ADR-0016; ADR-0017; ADR-0035 (Proposed)", "The Adopter's Guide excludes operating this pipeline"],
        ["Bd-8", "Signing, publishing and rolling out", "AU-10, AU-1", "ADR-0044 §4; ADR-0031; ADR-0069 §7, §8 (Proposed)",
         "Who holds the bundle key (ADR-0044)"],
        ["Bd-9", "The pipeline on a carrier: what git and a CI runner may and may not decide", "AU-15, AU-1",
         "ADR-0069 §9, §10 (Proposed)", "—"],
        {"group": "Run", "accent": "green"},
        ["Rn-1", "Operating Run: leases, tasks, renewing, ending a round, revoking, fencing an epoch", "AU-1",
         "ADR-0050 §4, §5; ADR-0031; ADR-0042", "—"],
        ["Rn-2", "Answering a finding: Observer and correlator output, stalls, the interval `D`, quarantine",
         "AU-1, AU-12", "ADR-0038; ADR-0039; ADR-0032; ADR-0051 (Proposed)",
         "The responder's role. What a quarantine hold means (ADR-0005 §3)"],
        ["Rn-3", "Emergency seating: for the roster, and for the person seated; the drill; the review afterwards",
         "AU-7, AU-4", "ADR-0052; ADR-0009; ADR-0013", "Who reviews \"Whether the reason was good\" (ADR-0052 §7)"],
        ["Rn-4", "What a seat is delivered: tools, labels and handles", "AU-16, AU-1, AU-4",
         "ADR-0043; ADR-0047; ADR-0048", "—"],
        ["Rn-5", "Workflows: a promoted graph of cells", "AU-1, AU-15", "ADR-0054; ADR-0055 (Proposed)",
         "All of it is Proposed"],
        ["Rn-6", "Calls on a user's behalf", "AU-15, AU-19", "ADR-0056 (Proposed)", "All of it is Proposed"],
        ["Rn-7", "Withdrawing authority, and how fast: lease expiry, revocation, the fence, `deny=all`", "AU-1, AU-6",
         "ADR-0031; ADR-0032; ADR-0050 §4", "The values are a deployment's to measure and declare"],
        ["Rn-8", "Erasure: asking for it, authorizing it, what it removes and what survives", "AU-8, AU-19, AU-14",
         "ADR-0006; ADR-0013; ADR-0028; ADR-0075 (Proposed)", "No roster exists. No record names who may ask"],
        {"group": "Governance", "accent": "blue"},
        ["Gv-1", "The custodian's work: drafting, ratifying in batches, cutting checkpoints and manifests, the debt "
         "ledger", "AU-9", "ADR-0029; `checkpoints/README.md`; `manifests/README.md`", "—"],
        ["Gv-2", "The bootstrap ceremony", "AU-6, AU-9, AU-13", "ADR-0029 §5; ADR-0025; ADR-0027",
         "\"Genesis and key-ceremony procedure\" (ADR-0025, Open obligations)"],
        ["Gv-3", "Issuing rules: what an issuance may change and what bounds it", "AU-6", "ADR-0025 §1; ADR-0026",
         "\"A named owner and organizational role for every custody declaration\" (ADR-0025, Open obligations)"],
        ["Gv-4", "Confirmation promotions after bootstrap", "AU-2, AU-9", "ADR-0029 §6", "—"],
        ["Gv-5", "Changing the policy floor: tightening, relaxing, exceptions", "AU-6, AU-2",
         "ADR-0010; ADR-0012; ADR-0013; ADR-0030", "How floor fitness is tested (ADR-0029 §5, step 6)"],
        ["Gv-6", "Rosters and first seatings: promotion, break-glass, erasure; seating operators", "AU-6",
         "ADR-0025 §1 (a), (b); ADR-0050 §2", "—"],
        ["Gv-7", "Losing the anchor: re-genesis and what a successor inherits", "AU-6, AU-14",
         "ADR-0027 §4; ADR-0028, Open obligations", "The successor's read access to forensic classes (ADR-0028)"],
        ["Gv-8", "Keys the mechanism accepts in place of its own check, and their custody", "AU-6, AU-10, AU-11",
         "ADR-0025 §1 (f); ADR-0044; ADR-0034 §2", "Custody rows are undeclared"],
        ["Gv-9", "Declaring the trusted base and a deployment's position", "AU-6, AU-15", "ADR-0045; ADR-0023",
         "A declaration template (ADR-0045, Open obligations)"],
        {"group": "External", "accent": "grey"},
        ["Ex-1", "The adopter's guide", "AU-15", "`ADOPTERS_GUIDE_README.md`, a draft", "As that guide marks"],
        ["Ex-2", "The reviewer's guide", "AU-13", "`REVIEWERS_GUIDE_README.md`, a draft", "A test of floor fitness"],
        ["Ex-3", "The auditor's guide: reading the forensic classes and the archive", "AU-14",
         "ADR-0028; ADR-0074 to ADR-0076 (Proposed)",
         "\"Define the external auditor role\" (ADR-0028, Open obligations)"],
        ["Ex-4", "Building an agent behind a seat", "AU-16", "ADR-0022; ADR-0040; ADR-0043", "—"],
        ["Ex-5", "Supplying a component: publishing what it discharges", "AU-17", "ADR-0058 §7 (Proposed); ADR-0049",
         "All of §7 is Proposed"],
        ["Ex-6", "Assurance for an acquirer: each claim with its mechanism, its evidence and its residual", "AU-18",
         "ADR-0045 Annex A; the residual-risk statement in force", "No independent reader exists"],
        ["Ex-7", "For a person a deployment acts for: what is recorded, what can be erased, what cannot", "AU-19",
         "ADR-0004; ADR-0006; ADR-0028; ADR-0056 (Proposed)", "Who may ask for erasure"],
        ["Ex-8", "Reporting a safety finding", "AU-20", "`SECURITY.md`", "—"],
        ["Ex-9", "Running a trust root for a deployment: a host, an identity provider, a verifier, a downstream "
         "system", "AU-11, AU-19", "ADR-0034; ADR-0050 §3; ADR-0056 (Proposed)", "—"],
        {"group": "For every reader", "accent": "brown"},
        ["Cx-1", "Orientation: what TOPAK is, principals and the gate, and which documents are yours", "All",
         "ToO §1, §7.5", "—"],
        ["Cx-2", "Vocabulary", "All", "`narrative/glossary.md`", "—"],
        ["Cx-3", "Reading a status mark and an evidence word", "All", "ADR-0029 §3, §4; ADR-0046", "—"],
        ["Cx-4", "Formats: the lease, the allowlist entry, the alphabets, the floor's policies, the bundle's input",
         "AU-15, AU-16, AU-1", "The records that define each; the format inventory",
         "Formats defined only in `mechanism/`"],
        ["Cx-5", "The reference implementation: running it, and its gaps", "AU-15, AU-13",
         "`mechanism/README.md`; `mechanism/GAPS-AND-ASSUMPTIONS.md`", "—"],
        ["Cx-6", "Assumptions of use and residual risk", "All who act", "ToO §13; ADR-0045 Annex A", "—"],
        {"cells": ["Cx-7", "What being trained and authorized consists of, role by role",
                   "AU-1, AU-4, AU-6, AU-7, AU-12", "ToO A5",
                   "**All of it.** No record says. The deployment writes this"], "accent": "red"},
        {"group": "The command-chain overlay", "accent": "amber"},
        ["Ov-1", "Commanding a plane, holding a `release` seat, routing a mission, building a vehicle", "AU-5, AU-21",
         "ADR-0059 to ADR-0068 (Proposed)",
         "\"What a person at a release seat must be shown\" (ADR-0066, Open obligations)"],
    ], size=S, accent="brown")
    y += t + 50

    # §4 levels and §5 bindings
    y = sub(c, X0, y, "**§4 · Three levels of disclosure ⟨K3⟩** (the letters are the custodian's; *main*, *supporting*, "
            "*detailed* is the drafter's reading; the pattern is C4's, taken as follows, drafter's choice)")
    cols = [("Level", 110, {"bold": True}), ("The reader's question", 600), ("Holds", 1700),
            ("Diagram, at C4's level", WW - 2410)]
    t = c.table(X0, y, cols, [
        ["MI", "What is this, and what may I do and not do?",
         "The subject in one screen: what the reader's role is here, what the system guarantees them, what it does "
         "not, and what they must never do", "1, context: the reader and what they touch"],
        ["SI", "How does it work, and how do I do it?",
         "The parts the subject passes through and the procedure: steps, preconditions, what is recorded, what cannot "
         "be undone", "2 and 3, containers and components; a sequence where order matters"],
        ["DI", "Exactly what, and on whose authority?",
         "Every action, field, rule, bound and error, each bound to its sources (§5)",
         "4, code: the clause, the property, the policy rule, the function. A table, not a drawing"],
    ], size=S, accent="amber")
    y += t + 24
    y = columns(c, X0, y, WW, 40, [
        [("LV-1 to LV-6", [
            "**LV-1.** A unit has all three, and neither MI nor DI is empty.",
            "**LV-2. A level may leave out, and it never adds.** Every statement at MI is made at SI, and every one "
            "at SI is made at DI, where it is bound. MI is a selection from DI and has no claim of its own.",
            "**LV-3. A limit travels with the guarantee it limits**: the same level states its status mark, what it "
            "assumes, and the residual a record declares. A reader who stops at MI has read less, not something "
            "more favourable.",
            "**LV-4.** Each level answers its own question without the next. MI is not a teaser for SI.",
            "**LV-5.** A diagram depicts and decides nothing; each carries a short text alternative and a long "
            "description (ADR-0072 §8 U-3).",
            "**LV-6.** MI fits one screen *(advice)*: about 150 words and one diagram.",
        ], "amber", {"status": "proposed"})],
        [("§5 · Bindings ⟨K4⟩: B-1 to B-7", [
            "**B-1. At DI every statement is bound**: the clause that *decides* it, and beside it what *states* it "
            "in a model, *enforces* it in policy, *implements* it and *evidences* it. **Where one does not exist, "
            "the unit says so**: \"no module states this\", \"not built\". An absence is written and never left "
            "blank (ADR-0057 §2's \"none yet\", \"stated as a claim\").",
            "**B-2.** At SI every must, cannot and never is bound to its clause, and every control step names the "
            "action and the clause that gives its preconditions.",
            "**B-3.** At MI a binding is owed wherever MI states a guarantee or a limit, and each unit's MI binds at "
            "least the record that defines its subject.",
            "**B-4.** A should is bound to nothing and says *advice*.",
            "**B-5. A binding is a pinned citation and not an edge**: it discharges nothing, contributes no premise "
            "and moves no theorem's grade; it uses the specification graph's node ids where the graph has the "
            "node, so the graph's checker can report stale bindings beside stale edges (ADR-0057 §3, §8). The "
            "graph today has no node for a narrative file or a guide.",
            "**B-6.** Every bound record's status is shown in the corpus's own words, at each level (table at "
            "right). Evidence is named only of what ran: proved (TLAPS), checked (TLC, with the constants), proved "
            "in Lean, tested, built at the reference, not built.",
            "**B-7.** A bound overlay record is marked as an overlay.",
        ], "amber", {"status": "proposed"})],
        [("§5's first table, whole: the four parts of a binding", [
            "**Node**: one of a record's clause (by record, section and amendment tags); a module and a named "
            "property; a proof module or a Lean file; a floor stage or a policy in it; a Rego policy or rule; a "
            "crate or a function; a format's schema; a results file; a trusted-base row; a degeneracy; a glossary "
            "entry; a checkpoint item.",
            "**Pin**: the digest of the node's content when the unit was read against it: a clause's digest once "
            "ADR-0057 §7's clause pins exist, and the file's until then.",
            "**Relation**: *decides* (a record clause), *states* (a model), *enforces* (a policy), *implements* "
            "(code), *evidences* (a result), *assumes* (a row), *defines* (a glossary entry).",
            "**Reader**: who read the unit against the node, and whether that person drafted the unit.",
        ], "blue", {"tint": False})],
    ], size=14) + 24
    cols = [("B-6 · The record is", 700), ("The unit says", WW - 700)]
    t = c.table(X0, y, cols, [
        ["Accepted (genesis), no confirmation marker", "Nothing more"],
        ["Accepted (genesis) · confirmation required", "\"author-ratified\" (ADR-0029 §3)"],
        ["Accepted (genesis) · provisional", "\"author-ratified, provisional\" (ADR-0029 §3)"],
        {"cells": ["Proposed", "⟨Proposed⟩: drafted and not in force"], "accent": "amber"},
        {"cells": ["Bound through a pending amendment", "⟨pending⟩: drafted and not ratified"], "accent": "amber"},
    ], size=S, accent="blue")
    y += t + 50

    # §6 unit, §7 staleness, §8 gates
    y = sub(c, X0, y, "**§6 · A unit, whole**, with U-1 to U-3; **§7 · Staleness**; **§8 · A release, and what its "
            "gates can and cannot check**")
    g = 40
    wl = 1500
    wr = WW - wl - g
    xr = X0 + wl + g
    cols = [("Field", 260, {"bold": True}), ("Content", wl - 260)]
    t = c.table(X0, y, cols, [
        ["Id", "Stable, and never reused. The document's id and a short name: `Rn-1/revoke`"],
        ["Kind", "*concept*, *task*, *reference* or *troubleshooting* *(drafter's choice)*"],
        ["Readers, domain", "From §2 and §3"],
        ["MI, SI, DI", "§4"],
        ["Bindings", "§5, each attached to the statement it supports"],
        ["Language", "Declared, with any passage in another marked"],
    ], size=S, accent="amber")
    bl = stack(c, X0, y + t + 18, wl, [
        ("U-1 to U-3", [
            "**U-1. A task's steps are numbered, and each control action says four things**: what it needs (a lease, "
            "a peer), what the log records of it, whether it adds or denies, and whether it can be undone. For the "
            "six operator actions these are ADR-0050 §4's columns, bound and not paraphrased.",
            "**U-2.** A unit is the smallest thing revised, released and withdrawn (ADR-0072 §2, §3).",
            "**U-3.** A unit holds no example taken from a round (ADR-0072 §10 H-1).",
        ], "amber", {"status": "proposed"}),
        ("§7 · Staleness: ST-1 to ST-4", [
            "**ST-1.** A binding whose pin no longer matches its node is stale, and so is the unit, at each level the "
            "binding supports.",
            "**ST-2. A stale unit is served and says it is stale**, naming the node that moved. Not hidden, because "
            "the procedure it holds may be the only one; not shown as current.",
            "**ST-3. Only a reading clears it.** A person reads the changed node, brings the unit into line or "
            "records why it already is, and re-pins. **No program re-pins.** This is the review ADR-0057 §3 asks of "
            "a stale edge.",
            "**ST-4.** A cut view keeps the pins it was cut with (ADR-0072 §4 V-2). Staleness is a fact about "
            "`latest`, and about a past view only as a note beside it.",
        ], "red", {"tint": False}),
    ], gap=18, size=14)
    cols = [("Gate", 190, {"bold": True}), ("Passes when", wr - 190 - 220), ("Enforces", 220)]
    t2 = c.table(xr, y, cols, [
        ["DG-1 Resolve", "Every binding's node exists at the commit, and the gate has computed which pins match. A "
         "release may contain a stale unit only marked as one", "§7"],
        ["DG-2 Bound", "Every DI statement row has a *decides* binding, and each of its other relations has a binding "
         "or a written absence. Every SI sentence with must, cannot or never has a binding", "§5 B-1, B-2"],
        ["DG-3 Marked", "Each bound record's status, read from its Status and Pending lines at the commit, appears at "
         "each level that binds it", "§5 B-6; §4 LV-3"],
        ["DG-4 Levelled", "Every unit has MI, SI and DI, and MI and DI are not empty", "§4 LV-1"],
        ["DG-5 Describable", "Every figure has both descriptions, every table its headers, every unit its language",
         "ADR-0072 §8 U-3"],
        ["DG-6 Covered", "The coverage report exists: for each reader of §2 and each document of §3, its units, or the "
         "word *unwritten*. The gate passes once the report is written, as ADR-0069 §3a's IG-7 does", "§3 S-1"],
        ["DG-7 Own text", "No unit includes a file from outside the documentation tree", "§6 U-3"],
    ], size=S, accent="amber")
    br = stack(c, xr, y + t2 + 18, wr, [
        ("§8 · The release, and RL-1 to RL-3", [
            "**A documentation release is a manifest over the unit files at a commit**, cut with each checkpoint and "
            "whenever the custodian cuts one between *(drafter's choice: the narrative's rhythm)*. A fifth kind, "
            "`documentation`, beside the four `manifests/README.md` lists. The gates are programs named by digest "
            "(ADR-0069 §6 G-1), each mechanical (ADR-0007). [[red|Not built]], [[red|not cut]].",
            "**What no gate checks: that a unit says what its clause says.** Whether MI left out a limit, whether a "
            "step restates a precondition rightly, and whether a should is really advice are a person's to judge.",
            "**RL-1.** Each unit names who read it against its bindings; a unit read only by its drafter says so, in "
            "ADR-0029 A2's words.",
            "**RL-2.** During genesis a release promotes nothing (ADR-0069 §10.3); it is cut by the custodian.",
            "**RL-3.** After bootstrap, whether a release is promoted is open *(drafter's recommendation: not a class "
            "under ADR-0024 §1, because the mechanism loads none of it; a unit of Rn-3, Rn-8, Gv-2, Gv-3 or Gv-6 is "
            "read before release by a member of the roster or key set it instructs)*.",
        ], "amber", {"status": "proposed"}),
    ], size=14)
    y = max(bl, br) + 50

    # §9, §10, §11, §12
    y = sub(c, X0, y, "**§9 · What exists today**; **§10 · A deployment's documentation**; **§11 · Degeneracy and the "
            "trusted base**; **§12 · Ratification condition**, item by item")
    g3 = 40
    w3 = (WW - 2 * g3) / 3
    xs = [X0, X0 + w3 + g3, X0 + 2 * (w3 + g3)]
    b1 = stack(c, xs[0], y, w3, [
        ("§9 · What exists today (drafter's choice throughout). No file is moved or changed by this record", [
            "The two guides become Ex-1 and Ex-2 when they are next rewritten, as units; until then they stand as "
            "drafts that `manifests/EXCLUDE` leaves unmeasured.",
            "The Theory of Operation and the glossary stay the narrative; units bind to them (Cx-1, Cx-2) and do not "
            "replace them. The architecture description stays an index.",
            "The READMEs' instructions for running things are the source of Cx-5.",
            "Units live in one tree, one file to a unit. **The tree's name and the unit file's form are not fixed "
            "here** (Open obligations).",
        ], "grey", {"tint": False}),
        ("§10 · A deployment's documentation", [
            "**An overlay on these**: it keeps, replaces, adds or omits by unit id (ADR-0072 §10 H-3). Where §3's "
            "last column says *the deployment writes this*, the overlay is where it is written. A replacement "
            "carries its own reader (RL-1) and inherits no reading from the archetype's.",
        ], "amber", {"tint": False}),
    ], gap=18, size=14)
    b2 = stack(c, xs[1], y, w3, [
        ("§11 · No degeneracy is declared, and no row is added", [
            "**A reader inside the proofs can be misled only as far as the mechanism admits.** An operator who "
            "follows a wrong step still signs one of six actions, each admitted or refused on the lease, the peer and "
            "the floor (ADR-0050 §4). A grant seat who misreads casts a vote the tally counts as any other. The "
            "theorems take these principals as `Mediated` and attributable, not as correct.",
            "**A reader at the gate is already assumed to do anything the rules floor allows.** The anchor is \"a "
            "havoc issuer\" (ADR-0025's title), and a document cannot widen what havoc reaches.",
            "**So a wrong document subtracts, or moves a person within a bound a theorem already assumes.** By "
            "ADR-0045 §2's test it is not a trust root.",
            "**What this does not make harmless**: a revocation that should have been made, an emergency seating "
            "that should not have been, an issuance the floor permits and nobody wanted. Inside the bounds, and "
            "still harms. **A5 stays an assumption of use**; this record gives it something to point at and does "
            "not discharge it.",
        ], "green", {}),
    ], size=14)
    cols = [("§12 · Condition", w3 - 330), ("State", 330)]
    t = c.table(xs[2], y, cols, [
        ["**The readers of §2 are checked against the corpus by someone who is not the drafter**, and every role a "
         "record names has a row", NM + ". The inventory was made by a delegated reader for this draft and was not "
         "re-read against every record"],
        ["**At least one document in each of Build, Run, governance and external is written at three levels**, one "
         "for a reader at the gate and one for a principal", NM + ": no unit is written"],
        ["**The gates DG-1 to DG-7 are programs in the repository**, and a release has been cut under them, with its "
         "coverage report", NM],
        ["**LV-2 and LV-3 have been tested by a person on the written units**", NM],
        ["**Bindings resolve against the specification graph's node ids** where the graph has the node (B-5)",
         NM + ": ADR-0057 is Proposed, and its graph holds no documentation"],
        ["**A manifest of kind `documentation` is cut**, and `manifests/README.md` lists the kind", NM],
        ["**The dependent entries of Annex A are drafted**", NM + ": none is drafted"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NM],
        ["**The custodian's reading of every drafter's choice, recommendation and reading**, the expansion of MI, SI "
         "and DI and the reading of \"principals at the gate\" among them", NM],
    ], size=S, accent="red")
    b3 = y + t
    y = max(b1, b2, b3) + 50

    # Options, consequences, open obligations, Annex A
    y = sub(c, X0, y, "**Options considered, whole**; **Consequences**; **Open obligations**; **Annex A · dependent "
            "entries this record would owe** (none is drafted)")
    wl = 2000
    wr = WW - wl - g
    xr = X0 + wl + g
    cols = [("Option", 640, {"bold": True}), ("Disposition", wl - 640)]
    t = c.table(X0, y, cols, [
        ["Documents by role only, with the domain inside each", "[[grey|Not taken]] ⟨K2⟩. The request lists by domain. "
         "An operator in Build and an operator in Run hold different seats (S-4)"],
        ["Documents by record: one explanation for each ADR", "[[red|Rejected.]] It is the corpus's own order and not a "
         "reader's. The architecture description already indexes that way"],
        ["Two levels, a summary and a reference", "[[grey|Not taken]] ⟨K3⟩"],
        ["Four levels, one for each of C4's", "[[grey|Not taken]] ⟨K3⟩. The request names three. §4 folds C4's second "
         "and third into SI, since a procedure usually crosses both"],
        ["Levels as separate documents: a quick-start, a guide, a reference", "[[red|Rejected.]] Three documents drift "
         "apart, and LV-2 could not be checked across them. One unit with three levels has one set of bindings"],
        ["Bindings at DI only", "[[grey|Not taken]] ⟨K4⟩. The request asks for them \"as appropriate\" above DI. B-2 "
         "and B-3 say where that is"],
        ["Every sentence bound, at every level", "[[grey|Not taken.]] Prose that explains needs no clause, and a binding "
         "on everything is read by nobody"],
        ["A binding as an edge of the specification graph, of type *read*", "[[grey|Not taken]] *(drafter's choice)*. "
         "An edge discharges the node above it and contributes a premise (ADR-0057 §4). A runbook discharges "
         "nothing, and a stale runbook must not void a theorem"],
        ["Generate DI from the records and the code", "[[amber|Open]], and attractive for Cx-4. A generated table would "
         "have an exact binding. The prose of DI would still be written. Nothing here prevents it"],
        ["Hide a stale unit until it is re-read", "[[red|Rejected]] (ST-2). The stale procedure may be the only one "
         "there is"],
        ["Let the marks sit at DI only, to keep MI clean", "[[red|Rejected]] (LV-3; ADR-0029 §3). MI is what most "
         "readers will read"],
        ["Documentation as a promoted artifact class, voted like a bundle", "[[amber|Open]] (RL-3). It would put a "
         "quorum behind every runbook, and nothing the mechanism loads would change"],
        ["Kinds by the Diátaxis scheme (tutorial, how-to, reference, explanation)", "Close to what §6 takes. "
         "*Tutorial* is left out because nothing here can yet be practised on, and *troubleshooting* is added "
         "because refusals are most of what an operator sees"],
        ["Write the missing procedures here: the key ceremony, the peer's reading, the auditor's role",
         "[[red|Rejected]] (D-4). Each is a decision a record owes, and a runbook that settled it would be a record "
         "nobody ratified"],
        ["The assistant as a reader, with skills as its documents in this set", "[[grey|Not taken]] (A-4). A skill "
         "tells a drafter how to work on the corpus. It is not documentation of the system"],
    ], size=S, accent="grey")
    bl = y + t
    br = stack(c, xr, y, wr, [
        ("Consequences · positive", [
            "**Every role the corpus relies on has a named document**, and the gaps are a list a person can read.",
            "**A summary cannot promise more than its reference** (LV-2, LV-3).",
            "**Where the corpus has not decided, the documentation says so** and points at the obligation.",
            "**The status of a design not yet confirmed follows it onto every page** (ADR-0029 §3).",
            "**A5 has an object.** \"Trained\" can come to mean \"has read these units at this view\".",
        ], "green", {}),
        ("Consequences · negative", [
            "**It is a great deal of writing**, and nearly none of it exists.",
            "**Three levels for every unit triples the surface that can go stale.**",
            "**The gates check form.** A unit can pass all seven and be wrong.",
            "**Much of the set would describe Proposed or provisional records**, marked from head to foot.",
            "**Honest documents will read as unfinished.** Gv-2 will say that no record decides the ceremony.",
            "**The inventory dates.** Nothing but a reviewer enforces A-2 until DG-6 reads the records for roles, "
            "which it does not.",
        ], "red", {"tint": False}),
        ("Open obligations", [
            "**The custodian's expansion of MI, SI and DI**, and the reading of \"principals at the gate\".",
            "**The unit file's form and the tree's name** (§9), and an extension of `tools/check-refs.py`.",
            "**The first documents**: Cx-1, Rn-1 and Gv-3 *(drafter's recommendation)*.",
            "**The seven gates as programs.** **Clause pins** (ADR-0057 §7, Proposed).",
            "**Whether documentation is promoted after bootstrap** (RL-3).",
            "**The role of the responder** (AU-12) and **the external auditor's** (AU-14).",
            "**ADR-0057 §2's four parts for a clause**: if it is ratified first, §4, §5 and §8 are the clauses "
            "whose guarantees would be numbered.",
            "**Narrative**: the ToO and the glossary owe *unit*, *level*, *binding*, *stale* and *view* at the "
            "next revision, if ratified.",
        ], "red", {"tint": False, "status": "open"}),
        ("Annex A · dependent entries this record would owe", [
            "**1. `manifests/README.md`.** A fifth kind, `documentation`, and its row. Not a record; changed with "
            "the first cut. [[red|Not drafted.]]",
            "**2. ADR-0057 §1 (Proposed). R-revision (dependent on ADR-0071, Proposed)**, only if the custodian "
            "wants documentation named as a layer. B-5 does not need it. [[red|Not drafted.]]",
            "**3. The Adopter's Guide and the Reviewer's Guide.** No entry. They are not records, and §9 leaves "
            "them as they are.",
            "**4. ADR-0029 §3.** No entry. B-6 restates its two phrases and changes neither.",
            "**ADR-0072 and ADR-0073 list no dependent entry**: each carries a debt against nothing and closes "
            "nothing.",
        ], "amber", {"status": "proposed"}),
    ], gap=18, size=14)
    y = max(bl, br) + 80

    # ================================================================== ADR-0072
    y = band(c, X0, y, "ADR-0072 · The documentation service is a projection that can be rebuilt (Context; §1, §2, "
             "§3, §4)", status="proposed", extra="C2 on the drafter's reading · drafted 2026.11.16, R1")
    y = columns(c, X0, y, WW, 40, [
        [("Context", [
            "**The corpus already keeps every revision of everything, and offers a reader one of them.** A record "
            "changes only by a typed History row; a checkpoint is \"one cut, never revised\"; a derived document "
            "\"is never revised, a new one is written\"; a manifest is verified \"against the tree it measured, not "
            "against today's\". What a reader is given is the head of a branch on a carrier; to read the ToO at "
            "G9 one runs `git diff` between two tags.",
            "**\"Equal to the latest\" is the hard word** ⟨K10⟩. A system that keeps old versions as downloads "
            "beside a live site has kept them and has not made them equal.",
            "**A store of documentation must not become a second record.** ADR-0005 §1 makes the archive the "
            "system of record. A store that held the only copy of a revision would be a record nobody decided to "
            "keep.",
        ], "grey", {"tint": False}),
         ("§1 · The service is a projection, and it can be rebuilt", [
             "**P-1. The store holds nothing that is not derived from the corpus at a commit, by a pinned program.** "
             "The unit files, the records, modules and policies they bind to, and the manifests are the sources; the "
             "archive of record keeps them (ADR-0074 §2, class C; Proposed). Not a system of record for anything.",
             "**P-2. Dropping the store and ingesting again yields the same digests**, checked by comparing digests "
             "and not by trust in the rebuild (ADR-0069 §10.2's `results` rule, applied to a store).",
             "**P-3. The service decides nothing.** It admits no action, counts no vote and issues nothing. Where a "
             "unit and a record disagree, the record wins (ADR-0071 §1).",
         ], "amber", {"status": "proposed"})],
        [("§2 · A revision is immutable and is addressed by its digest ⟨K10⟩", [
            "**L-1. A unit's revision is the SHA-256 of its canonical bytes**: three levels, bindings and metadata "
            "in a fixed serialization. The digest identifies; a number, a date and a commit locate (ADR-0069 §9 "
            "C-5).",
            "**L-2. A revision is written once.** No operation edits or deletes one. A correction is a new revision.",
            "**L-3. Every revision of every unit is reachable three ways**: by digest; by unit and revision number, "
            "from 1 with no gaps; by unit and a time, which returns the revision in force then.",
            "**L-4.** Two revisions can be compared, level by level and binding by binding, through the API (§7).",
            "**L-5. Nothing ages out**: no expiry, no tiering a reader cannot reach, no limit on revisions kept. "
            "How long the sources are kept is ADR-0075's schedule, class C.",
        ], "amber", {"status": "proposed"}),
         ("§3's rules: LC-1 to LC-4", [
             "**LC-1.** The states are computed from revisions and views, not stored on the immutable revision. A "
             "revision released at G12 and superseded since is both, and each view shows it as that view saw it.",
             "**LC-2. Withdrawal is a revision, not a removal.** An old link reaches the old text under a line saying "
             "it was withdrawn, when, and by which revision.",
             "**LC-3.** Staleness is separate from state (ADR-0071 §7); a stale revision may be drafted, released or "
             "superseded as well.",
             "**LC-4. Disposal is not a state.** No cognitive payload (§10 H-1), so no erasure under ADR-0006 reaches "
             "a unit, and the service has no path that destroys a revision.",
         ], "amber", {"status": "proposed"})],
        [("§4's rules: V-1 to V-7", [
            "**V-1. Every operation takes a view, and none is defined for `latest` alone.** The contract tests run "
            "once against `latest` and once against a cut view, and a difference fails them.",
            "**V-2. A cut view answers from the corpus as it stood**: a binding in `G12` pins the digest its node "
            "had at that cut, and the service shows that text, saying separately whether the node has changed "
            "since. It never rewrites a cut view to agree with today.",
            "**V-3.** A cut view is written once, under its manifest's digest; a second write that differs is "
            "refused.",
            "**V-4. Views are never removed.** A view of a checkpoint later known to be wrong stays, carrying that "
            "statement as a notice (`checkpoints/README.md`'s own rule).",
            "**V-5.** Two views compare by set difference on digests: added, removed, changed (ADR-0069 §3 I-5).",
            "**V-6. `latest` always says what it resolved to**, so a reader can cite what they read and reach it "
            "again.",
            "**V-7. Checkpoints cut before the service exists get backfilled views** *(drafter's choice)*: the "
            "narrative, the two guides and the READMEs as each manifest measured them, one level, no bindings, "
            "marked backfilled; G1 and G2 as far as `manifests/index.tsv` says they verify.",
        ], "amber", {"status": "proposed"})],
    ], size=14) + 24
    wl = (WW - g) * 0.42
    wr = WW - g - wl
    xr = X0 + wl + g
    c.text(X0, y + 16, "**§3 · A unit has a life, whole** ⟨K10⟩", 16, "ink")
    cols = [("State", 150, {"bold": True}), ("Meaning", wl * 0.5), ("How a revision enters it", wl - 150 - wl * 0.5)]
    t1 = c.table(X0, y + 32, cols, [
        ["drafted", "Ingested from a commit and in no cut view. Shown in `latest` with the word *draft*", "Ingest (§9)"],
        ["released", "Named by the manifest of a checkpoint view or a release view", "The cut (§4)"],
        ["superseded", "A later revision of the same unit exists",
         "The later revision's ingest. The earlier one is unchanged"],
        ["withdrawn", "The unit's newest revision says the unit is withdrawn, why, and what replaces it",
         "A withdrawing revision. Earlier revisions and the views naming them are unchanged"],
    ], size=S, accent="amber")
    c.text(xr, y + 16, "**§4 · A view is a manifest, whole** ⟨K10⟩: for each unit one revision digest, with the corpus "
           "commit and the corpus manifest it was cut against", 16, "ink")
    cols = [("Kind", 130, {"bold": True}), ("Named", 330), ("Cut when", wr - 130 - 330 - 420),
            ("Changes afterwards", 420)]
    t2 = c.table(xr, y + 32, cols, [
        {"cells": ["latest", "`latest`", "Never cut. It follows the newest ingest of the default branch",
                   "**Yes.** It is the only view that does"], "accent": "amber"},
        ["checkpoint", "`G12`, and so on", "With each Genesis Checkpoint, against the checkpoint's own manifest",
         "Never"],
        ["release", "`DOC-<date>`, or a promoted release's digest",
         "With each documentation release (ADR-0071 §8); after bootstrap, with each publication under ADR-0069 §8",
         "Never"],
    ], size=S, accent="amber")
    y += 32 + max(t1, t2) + 50

    y = sub(c, X0, y, "**§5 · The store** ⟨K5⟩; **§6 · The reference's engine**; **§7 · One model, two generated "
            "interfaces** ⟨K6⟩; **§8 · Any reader may integrate** ⟨K7⟩")
    y = columns(c, X0, y, WW, 40, [
        [("§5 · One table with a composite primary key and secondary indexes, reached only through the DynamoDB data "
          "model and API", [
            "**S-1. One table.** Every item has a partition key and a sort key, and its type is read from the two "
            "together; items read together share a partition.",
            "**S-2. Every access pattern is a key condition**: a `GetItem` or a `Query` with a partition key and a "
            "range of the sort key. **No operation scans.** A pattern that cannot be listed in Annex A is not "
            "offered.",
            "**S-3.** Secondary indexes carry the other readings: two global, one local (Annex A).",
            "**S-4. Immutability is a conditional write**: put with a condition that the key does not exist; an "
            "overwrite fails at the store, not in the service's code.",
            "**S-5. A view is cut in one transaction, or under a marker**: the head item is written last, and a view "
            "without its head is not served.",
            "**S-6. The engine is open source**: an OSI-approved licence, the reference's build pinned by digest.",
        ], "amber", {"status": "proposed"}),
         ("§6 · ExtendDB on PostgreSQL, and the interface is what is fixed (drafter's recommendation)", [
             "**What supports it**: it implements §5's interface with composite keys, both index kinds, conditional "
             "writes and transactions, as its README and differences document state; Apache-2.0 on PostgreSQL's "
             "licence; written in Rust, as the reference mechanism is.",
             "**What does not: it is new.** AWS calls it \"a v0.1 release for development, testing, and "
             "experimentation\"; its README scopes 1.0 to \"Local development and continuous integration (CI) test "
             "runs\" and not \"A multi-server deployment\". [[red|Nothing in this corpus has run it.]]",
             "**Why that is tolerable here**: the store is a projection; an engine that loses data costs the "
             "service its availability until a rebuild, and the record nothing. Under the archive's index it is "
             "argued separately (ADR-0076 §4).",
             "**Substitution**: any engine behind §5's interface, declared as ADR-0033 §2's rule has a deployment "
             "declare a substrate; one that is not open source meets §5 except S-6, and says so.",
         ], "amber", {"tint": False})],
        [("§7 · A-1 to A-8", [
            "**A-1. The API is described once**, in a model file; the GraphQL schema and the OpenAPI description are "
            "generated by a pinned tool, neither edited by hand.",
            "**A-2. The two interfaces are equal**; a generated parity test fails the build when one offers what the "
            "other does not.",
            "**A-3. The API reads and never writes**: no mutation, no method but `GET` and `HEAD`. Content enters by "
            "ingest (§9) and by no request.",
            "**A-4. Every response names its view and its revision digests** (V-6); a cut view's or a digest's "
            "response is immutable, its entity tag the digest, cached without limit; `latest` briefly.",
            "**A-5.** The operations (table below), in both interfaces.",
            "**A-6. The interface is versioned, and a version only grows**; a breaking change is a new version "
            "served beside the old.",
            "**A-7.** Lists paged by cursor; a GraphQL query bounded in depth and cost, the bounds in the schema's "
            "description. This protects availability and nothing else.",
            "**A-8. Search is a second projection, built per view**, immutable with a cut view, rebuilt from the "
            "store as the store is from the corpus (P-2).",
        ], "amber", {"status": "proposed"})],
        [("§8 · Any reader may integrate, and none is privileged ⟨K7⟩", [
            "**U-1. The reference reader has no interface of its own.** It uses §7 and nothing else (ADR-0073 §1 "
            "R-1). What it can show, any client can show.",
            "**U-2. Content is returned as a tree and not as markup**: headings, paragraphs, lists, tables, code, "
            "figures, notes and binding references; a rendered HTML fragment is offered beside it, and the tree is "
            "the contract.",
            "**U-3. The fields accessibility needs are mandatory in the tree**: a figure's short alternative and "
            "long description, a table's header cells and caption, a heading's level, the language of the unit and "
            "of any passage, an abbreviation's expansion on first use. Ingest refuses a unit that lacks one "
            "(ADR-0071 §8).",
            "**U-4. Marks and bindings are data, not decoration**: a unit's status marks and each binding's node, "
            "clause, digest and freshness are fields.",
            "**U-5.** A client may be a page, an application, a terminal or a program; cross-origin reads are "
            "allowed for the public units; an embeddable element is one such client (ADR-0073, Options).",
            "**U-6. Who may read is the deployment's rule.** The archetype's units are public under `LICENSE-DOCS`; "
            "a deployment's own may be restricted through its identity provider. A restriction hides a unit and "
            "changes none.",
        ], "amber", {"status": "proposed"})],
    ], size=14) + 24
    y = sub(c, X0, y, "**§7 A-5 · The operations, whole**, in both interfaces")
    cols = [("Operation", 1400), ("Returns", WW - 1400)]
    t = c.table(X0, y, cols, [
        ["List views; read a view's head", "Kind, cut date, commit, manifest digest, counts"],
        ["List a view's units, filtered by audience, domain and kind (ADR-0071 §2, §3, §6)",
         "Unit heads with their state in that view"],
        ["Read a unit in a view at a level", "The content tree of MI, SI or DI, its marks, its bindings, its staleness"],
        ["List a unit's revisions; read one by number, digest or time", "L-3"],
        ["Compare two revisions, or two views", "L-4, V-5"],
        ["From a node of the specification graph, list the units bound to it in a view",
         "ADR-0071 §5's bindings, read backwards"],
        ["Search a view", "Units, with the level and passage matched"],
    ], size=S, accent="amber")
    y += t + 50

    y = sub(c, X0, y, "**§9 · Ingest is the only way in**; **§10 · What the service does not hold**; **§11 · Degeneracy "
            "and the trusted base**; **§12 · Ratification condition**, item by item")
    b1 = stack(c, xs[0], y, w3, [
        ("§9 · I-1 to I-5", [
            "**I-1.** Ingest reads the corpus at one commit and writes revisions, bindings and, for `latest`, a "
            "manifest. A program in the repository, named by digest, that runs the same way by hand and on a "
            "carrier (ADR-0069 §6 G-1).",
            "**I-2. Ingest refuses a name.** It is given a commit, resolves it to a tree, and records the tree's "
            "digests. A cut is given the checkpoint's or the release's manifest and refuses a tree that does not "
            "verify against it (ADR-0069 §1 P-1).",
            "**I-3. Ingest is idempotent.** Run twice on one commit, it writes nothing the second time (S-4).",
            "**I-4.** Ingest runs the gates of ADR-0071 §8 first, and writes nothing for a unit that fails one.",
            "**I-5. A carrier's merge is not a cut.** Merging to the default branch moves `latest`; a checkpoint view "
            "is cut when the custodian cuts the checkpoint, and after bootstrap a release view when a promotion's "
            "publication names it (ADR-0069 §8, §9 C-1).",
        ], "amber", {"status": "proposed"}),
        ("§10 · What the service does not hold, and a deployment's own units", [
            "**H-1. No cognitive payload and no labelled item** (ADR-0004; ADR-0047 §1). An example in a unit is "
            "written for it and is not taken from a round.",
            "**H-2. No secret and no deployment value** in the archetype's units: \"the deployment writes this\".",
            "**H-3. A deployment's documentation is an overlay on the archetype's** *(drafter's choice)*: keeps, "
            "replaces, adds or omits units by id, as ADR-0058 §1 (Proposed) has a deployment's graph relate to the "
            "archetype's. A replaced unit names the archetype revision it replaces, so an upstream change shows as "
            "stale.",
        ], "amber", {"tint": False}),
    ], gap=18, size=14)
    b2 = stack(c, xs[1], y, w3, [
        ("§11 · No degeneracy is declared, and no row is added", [
            "**No theorem takes a premise from the service.** By ADR-0045 §2's test, its failure produces no admit, "
            "promotion or issuance. It can show a reader a wrong or missing page, and ADR-0071 §11 says what bounds "
            "a reader who acts on one.",
            "**A deployment that serves its documentation some other way has made no declaration under ADR-0023** "
            "by doing so. It has only not met this record.",
        ], "green", {}),
    ], size=14)
    cols = [("§12 · Condition", w3 - 330), ("State", 330)]
    t = c.table(xs[2], y, cols, [
        ["**The service exists**: ingest, store, both interfaces and search, with `latest` and at least two cut "
         "views", NM + ": nothing is built"],
        ["**P-2 is seen**: the store is dropped and rebuilt, and every revision and view digest is the same", NM],
        ["**§2 and §4 are seen**: an overwrite refused at the store (S-4); a second, different write of a cut view "
         "refused (V-3); the contract tests identical against `latest` and a cut view (V-1); a binding in a cut view "
         "returning the node's text at that cut after the node has changed (V-2)", NM],
        ["**A-2's parity test exists and passes**, and both descriptions are generated from one model with no hand "
         "edits", NM],
        ["**Annex A covers §7**: every operation of A-5 is a row with a key condition, and no operation scans (S-2)",
         NM + ": Annex A lists them, and nothing has run a query"],
        ["**The engine of §6 is run under the service's load and a rebuild**, and its build is pinned",
         NM + ". Nothing in the corpus has run ExtendDB"],
        ["**A second client that is not the reference reader renders a unit from the API** (U-1)", NM],
        ["**ADR-0071 is ratified, or this record is ratified with it**", NM + ": it is Proposed"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NM],
        ["**The custodian's reading of every drafter's choice and recommendation**, the engine among them", NM],
    ], size=S, accent="red")
    y = max(b1, b2, y + t) + 50

    y = sub(c, X0, y, "**Options considered, whole: the store's engine ⟨K5⟩** (\"open source\" read as an OSI-approved "
            "licence on the releases a deployment would run today; except where the provenance note says a page was "
            "read, each row is the drafter's understanding and was not checked)")
    cols = [("Engine", 560, {"bold": True}), ("Licence", 420), ("Composite key and secondary indexes", 760),
            ("DynamoDB API", 180), ("Disposition", WW - 1920)]
    t = c.table(X0, y, cols, [
        {"cells": ["ExtendDB on PostgreSQL", "Apache-2.0, on PostgreSQL's licence",
                   "Both, with global and local indexes and transactions", "Yes",
                   "**Recommended for the reference** (§6). New, and scoped by its own README to development and CI"],
         "accent": "amber"},
        ["ExtendDB on SQLite", "Apache-2.0; SQLite is public domain", "As above; one node", "Yes",
         "The reference's test and single-machine configuration *(drafter's recommendation)*"],
        ["ScyllaDB Alternator", "Source-available from 2025.1. AGPL releases ended at 6.2.x",
         "Both. No multi-item transactions; index projections are not honoured", "Yes",
         "Not taken as the reference: current releases do not meet S-6. The most mature implementation of the "
         "interface, and the first substitution a deployment would consider"],
        ["Apache Cassandra", "Apache-2.0", "A partition key with clustering columns is the composite key. "
         "Storage-attached indexes and materialized views, or index tables the service writes", "No. CQL",
         "Not taken. The data model fits and the interface does not, so §5's substitution would be lost. ExtendDB "
         "lists a Cassandra backend as experimental"],
        ["PostgreSQL directly, one table keyed `(pk, sk)` with a JSON document and one index per secondary key",
         "PostgreSQL", "Both, by ordinary indexes", "No",
         "Not taken ⟨K5⟩. The simplest thing that would work, and the fallback if ExtendDB proves unfit: the key "
         "design of Annex A carries over unchanged"],
        ["YugabyteDB (its Cassandra-compatible interface)", "Apache-2.0 core", "Both, with consistent indexes", "No",
         "Not taken. Distributed, and more than a projection needs"],
        ["FoundationDB, with its record layer", "Apache-2.0", "An ordered key-value store; the composite key is the "
         "key's encoding, and indexes are the layer's", "No",
         "Not taken. The strongest transactions of the set, and the most to build"],
        ["TiKV", "Apache-2.0", "Ordered keys; indexes are the service's to maintain", "No",
         "Not taken, for the same reason"],
        ["Apache HBase; Apache Accumulo", "Apache-2.0", "A composite row key; no native secondary index", "No",
         "Not taken here. Accumulo's cell-level visibility labels are weighed for the archive (ADR-0076, Options)"],
        ["An embedded ordered store (RocksDB, LMDB) inside the service", "Apache-2.0 or similar",
         "Ordered keys; indexes are the service's", "No",
         "Not taken. No interface another engine could stand behind"],
        ["Amazon DynamoDB", "Proprietary service", "Both", "It is the interface",
         "Not open source ⟨K5⟩. A substitution a deployment may declare (§6)"],
        ["DynamoDB Local", "Proprietary, free to use", "Both", "Yes", "Not open source, and a test tool"],
        ["MongoDB, Couchbase, CockroachDB", "Source-available licences", "Various", "No", "Not open source"],
        ["A relational schema, normalized", "—", "Not a single-table design", "—", "Not taken ⟨K5⟩"],
    ], size=S, accent="grey")
    y += t + 40
    wl = 2000
    wr = WW - wl - g
    xr = X0 + wl + g
    c.text(X0, y + 16, "**Other choices, whole**", 16, "ink")
    cols = [("Option", 640, {"bold": True}), ("Disposition", wl - 640)]
    t = c.table(X0, y + 32, cols, [
        ["The store as the record: units authored through the service and kept only there",
         "[[red|Rejected]] (§1). It would be a system of record no record decided to keep, and its engine's maturity "
         "would then matter to the corpus"],
        ["Git as the service: the carrier's API, tags as views", "[[grey|Not taken.]] It keeps every revision and "
         "makes none equal: no levels, bindings, audience listing or search in a past tag. A carrier's tag also "
         "locates and does not identify (ADR-0069 §9 C-5)"],
        ["A site generated per version, each a copy of the tree", "[[grey|Not taken.]] Fits a few releases. Every "
         "checkpoint and every revision is not a few, and a copy per view shares nothing"],
        ["A headless content system (Strapi, Directus, Payload)", "[[grey|Not taken.]] Each gives REST and GraphQL "
         "over a relational store with editing through the service, which is the first row above"],
        ["GraphQL only, or REST only", "[[grey|Not taken]] ⟨K6⟩"],
        ["One interface written by hand and the other generated from it", "[[grey|Not taken]] *(drafter's choice)*. "
         "The hand-written one becomes the real contract and the other drifts behind it"],
        ["An interface generated from the store (a GraphQL or REST layer over the tables)", "[[red|Rejected.]] It "
         "would expose Annex A's keys as the contract, and §6's substitution with them"],
        ["gRPC as a third interface", "[[grey|Not taken.]] Not asked for; the model of A-1 could generate it"],
        ["A write interface for comments, edits or review", "[[grey|Not taken]] (A-3). Review happens where the "
         "records' own review happens"],
        ["History from the first cut after the service is built, with no backfill", "[[amber|Open.]] V-7 backfills. "
         "This is cheaper and leaves G1 to G11 readable only through the carrier"],
        ["A view per commit", "[[grey|Not taken.]] `latest` records each ingest's manifest, so any ingested commit "
         "can be read by time (L-3)"],
        ["A search engine as a service (OpenSearch, Meilisearch)", "[[amber|Open.]] A-8 fixes that each view has an "
         "index and is silent on what builds it. An index library embedded in the service is the drafter's "
         "recommendation"],
    ], size=S, accent="grey")
    bl = y + 32 + t
    br = stack(c, xr, y + 32, wr, [
        ("Consequences · positive", [
            "**A link to a page in a checkpoint keeps working and keeps meaning the same thing.**",
            "**Old and new are served by one code path**, so the old cannot rot unnoticed.",
            "**The store can be lost.** A rebuild is a recomputation with a check, not a restore.",
            "**Two engines can stand behind one interface**, and the choice of the first is cheap to reverse.",
            "**A deployment's reader, a terminal client and the reference reader are peers.**",
        ], "green", {}),
        ("Consequences · negative", [
            "**Everything is kept, so the store only grows.**",
            "**A search index per view** multiplies with the number of cuts.",
            "**A single-table design fixes the access patterns in advance**: Annex A must change before the API can.",
            "**The recommended engine is months old and declares itself unfit for production.** The least proven "
            "part of this record.",
            "**Two interfaces are twice the surface to test**, and A-2's parity is a standing cost.",
            "**Backfilled views (V-7) are thinner than cut ones**, and a reader must be told so on every page.",
        ], "red", {"tint": False}),
        ("Open obligations", [
            "**The model language and generator of A-1**, pinned: TypeSpec, Smithy, Protocol Buffers are candidates.",
            "**The canonical serialization of L-1**, which must not change once a view is cut.",
            "**The service's language**: Rust is the drafter's recommendation.",
            "**The search index of A-8**, and ranking across three levels.",
            "**The backfill of V-7** for G1 to G11, or the custodian's decision not to.",
            "**The overlay of H-3**, which leans on ADR-0058 (Proposed).",
            "**Names of people in units** (an auditor's in a conformance report, ADR-0073 §7): personal data in an "
            "immutable revision. Not resolved.",
            "**Running ExtendDB** under this design, and a second engine behind the same interface.",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=18, size=14)
    y = max(bl, br) + 50

    # Annex A: three tables
    y = sub(c, X0, y, "**Annex A · The table's keys (reference design), whole.** Drafter's choice throughout: the "
            "reference's design and not a requirement; §5 is the requirement. One table; `n` is a revision number "
            "zero-padded to eight digits; `d` is a SHA-256 in hex")
    cols = [("Item", 260, {"bold": True}), ("PK", 420), ("SK", 520), ("Holds", WW - 1200)]
    t = c.table(X0, y, cols, [
        ["Unit head", "`UNIT#<unit>`", "`HEAD`",
         "Title, kind, audiences, domain; the newest `n` (the one attribute rewritten, with `latest`)"],
        ["Revision", "`UNIT#<unit>`", "`REV#<n>`", "`d`, time ingested, source commit and path, withdrawal reason if any"],
        ["Level body", "`REV#<d>`", "`LVL#<MI|SI|DI>#<part>`", "The content tree, split into parts under the item size limit"],
        ["Binding", "`REV#<d>`", "`BIND#<level>#<seq>`", "Node id, clause or path, pinned digest, relation, reader"],
        ["Node entry", "`VIEW#<view>#NODE#<node>`", "`UNIT#<unit>#<level>#<seq>`",
         "One for each binding of each revision a view names. `d`, pinned digest, relation"],
        ["View list entry", "`VIEWS`", "`<kind>#<date>#<view>`", "The view's name. Written at the cut"],
        ["View head", "`VIEW#<view>`", "`HEAD`",
         "Kind, cut date, commit, corpus manifest digest, view manifest digest. Written last (S-5)"],
        ["View entry", "`VIEW#<view>`", "`UNIT#<unit>`", "`d`, `n`, state in the view"],
        ["Catalogue entry", "`VIEW#<view>`", "`CAT#<audience>#<domain>#<kind>#<unit>`",
         "One per audience of the unit. Title and `d`"],
        ["Ingest", "`INGEST`", "`AT#<time>#<commit>`", "The manifest digest `latest` resolved to at that ingest"],
    ], size=S, accent="amber")
    y += t + 24
    wl = 1500
    wr = WW - wl - g
    xr = X0 + wl + g
    cols = [("Index", 360, {"bold": True}), ("Partition key", 420), ("Sort key", 420), ("On", wl - 1200)]
    t1 = c.table(X0, y, cols, [
        ["GSI1, domain within a view", "`VIEW#<view>#DOM#<domain>`", "`AUD#<audience>#<kind>#<unit>`",
         "Catalogue entries"],
        ["GSI2, revision to views", "`REV#<d>`", "`VIEW#<view>`", "View entries"],
        ["LSI1, a unit by time", "`UNIT#<unit>`", "`AT#<time>`", "Revisions"],
    ], size=S, accent="amber")
    c.para(X0, y + t1 + 14, wl, "Search (A-8) is not a key condition. It is its own projection and is not in this "
           "table.", 14, "muted")
    cols = [("Operation (§7 A-5)", 520), ("Key condition", wr - 520)]
    t2 = c.table(xr, y, cols, [
        ["List views", "`Query` `PK = VIEWS`"],
        ["A view's head", "`GetItem` `VIEW#<view>`, `HEAD`"],
        ["A view's units for an audience", "`Query` `PK = VIEW#<view>`, `SK begins_with CAT#<audience>#`"],
        ["A view's units for a domain, then audience",
         "`Query` GSI1 `PK = VIEW#<view>#DOM#<domain>`, `SK begins_with AUD#<audience>#`"],
        ["A unit in a view at a level", "`GetItem` `VIEW#<view>`, `UNIT#<unit>` for `d`; then `Query` `PK = REV#<d>`, "
         "`SK begins_with LVL#<level>#`; then `Query` `PK = REV#<d>`, `SK begins_with BIND#<level>#`"],
        ["A unit's revisions, newest first", "`Query` `PK = UNIT#<unit>`, `SK begins_with REV#`, descending"],
        ["A revision by number", "`GetItem` `UNIT#<unit>`, `REV#<n>`"],
        ["A revision by digest", "`Query` `PK = REV#<d>`"],
        ["A unit's revision at a time", "`Query` LSI1 `PK = UNIT#<unit>`, `SK <= AT#<time>`, descending, limit 1"],
        ["The views a revision is in", "`Query` GSI2 `PK = REV#<d>`"],
        ["Units bound to a node, in a view", "`Query` `PK = VIEW#<view>#NODE#<node>`"],
        ["Compare two views", "Two `Query` calls, `PK = VIEW#<a>` and `PK = VIEW#<b>`, `SK begins_with UNIT#`, merged "
         "by unit"],
        ["What `latest` was at a time", "`Query` `PK = INGEST`, `SK <= AT#<time>`, descending, limit 1"],
    ], size=S, accent="amber")
    y += max(t1 + 50, t2) + 80

    # ================================================================== ADR-0073
    y = band(c, X0, y, "ADR-0073 · The reference reader is React with Material UI over the public API alone "
             "(Context; §1 to §8)", status="proposed", extra="no marker on the drafter's reading · 2026.11.16, R1")
    y = columns(c, X0, y, WW, 40, [
        [("Context", [
            "**ADR-0072 serves the documentation to any client, and no client exists.** The custodian asked for one "
            "built with React and Material UI, alternatives listed ⟨K8⟩, with five properties ⟨K9⟩: responsive "
            "display, light and dark modes, a minimalist reading mode, assistive access, and WCAG compliance.",
            "**The five properties are not equally checkable.** Reflow at a width, a contrast ratio and a missing "
            "text alternative can be computed. Whether a screen-reader user can find the clause a runbook step "
            "rests on cannot. **A program that reports no failures has shown that it found none of the failures it "
            "can find.** The corpus's words: a mechanical gate (ADR-0007), a check that \"may refuse and never "
            "admit\" (ADR-0069 §9 C-2), a field \"checked or claimed\" (ADR-0049).",
            "**Part of accessibility is not the reader's to supply**: a text alternative, a heading's level, a "
            "table's header cells, the language of a passage belong to the content. ADR-0072 §8 makes those "
            "fields mandatory.",
        ], "grey", {"tint": False}),
         ("§1 · The reader is a client of the public API and nothing more ⟨K7⟩", [
             "**R-1. The reader calls only the API of ADR-0072 §7**, with no credential a third party's reader could "
             "not hold. No route to the store, no endpoint of its own.",
             "**R-2. The reader holds no content.** A page is a rendering of a unit's revision in a view, and its "
             "address names both. A link to a page in view `G11` returns that page for as long as the service runs.",
             "**R-3. The reader states nothing of its own.** Its own text is navigation, labels and its accessibility "
             "statement (§7).",
             "**R-4. Every view is rendered by the same code path.** Search, level switching, bindings and reading "
             "mode work in every view; the only difference a past view shows is a line saying which view it is.",
         ], "amber", {"status": "proposed"}),
         ("§2 · React and Material UI ⟨K8⟩", [
             "**Both MIT-licensed; versions pinned by the lockfile, cited by digest when the reader is built** "
             "(ADR-0069 §10.2).",
             "**M-1.** A component is used as the library ships it only where it passes §6; otherwise wrapped or "
             "replaced, and the audit report names it *(drafter's choice: Material UI's WAI-ARIA conformance is the "
             "library's claim, not a result this corpus holds)*.",
             "**M-2.** The two colour schemes are one theme with two schemes, as CSS variables, set in the HTML the "
             "server sends.",
             "**M-3. Material Design's look is not a requirement.** Density, elevation and motion defaults are turned "
             "down to what §5 and §6 allow.",
         ], "amber", {"status": "proposed"})],
        [("§3 · Responsive display ⟨K9⟩", [
            "**RD-1. One document, one layout that reflows.** No separate mobile site; no loss and no two-dimensional "
            "scrolling at 320 CSS pixels (WCAG 1.4.10); usable at 400% zoom.",
            "**RD-2. What cannot reflow scrolls inside its own region**: a wide table, a code block, a diagram, each "
            "in a labelled, keyboard-focusable region.",
            "**RD-3.** Orientation is not locked (1.3.4); a pointer target is at least 24 by 24 CSS pixels (2.5.8).",
            "**RD-4. Navigation collapses, and content does not.** The unit's text, its level switch, its status "
            "marks and its bindings stay on the page.",
        ], "amber", {"status": "proposed"}),
         ("§4 · Light and dark ⟨K9⟩", [
             "**LD-1. Two schemes, and the first visit follows the device** (`prefers-color-scheme`); a reader's own "
             "choice overrides it, kept on that device, never part of a page's address.",
             "**LD-2. Both schemes meet the same contrast**: 4.5 to 1 for text (1.4.3), 3 to 1 for controls and "
             "graphics (1.4.11); each scheme audited separately (§7).",
             "**LD-3. Nothing is said by colour alone** (1.4.1): a status mark is a word; a stale binding is a word "
             "and an icon with a text alternative.",
             "**LD-4. A diagram has a rendering for each scheme, or draws in the text colour.** The corpus's "
             "diagrams are generated, so the generators owe a second palette (Open obligations).",
             "**LD-5.** A user's forced colours (`forced-colors`) are respected.",
         ], "amber", {"status": "proposed"}),
         ("§5 · Reading mode ⟨K9⟩: one unit, at one level, as a single column of text, with nothing else on the page", [
             "**RM-1. It is the page as the server sends it** *(drafter's choice)*: complete HTML with its styles, "
             "readable, followable and printable with no script. Scripts add search, the level switch without a "
             "load, and the scheme control.",
             "**RM-2.** It has its own address.",
             "**RM-3.** The column is at most 80 characters wide; size, line and paragraph spacing under the "
             "reader's control with no loss (1.4.12; 1.4.8 at AAA).",
             "**RM-4. Reading mode may hide navigation and never a mark or a binding.** The view, the marks and the "
             "staleness stay at the head of the column; each binding becomes a numbered note at the foot with its "
             "clause, module or policy and its digest. A mode that dropped \"author-ratified\" to look cleaner "
             "would make every page in it a publication ADR-0029 §3 forbids.",
             "**RM-5. Print is reading mode on paper**, each link's target and each binding's digest written out.",
         ], "amber", {"status": "proposed"})],
        [("§6 · Assistive access ⟨K9⟩: AA-1 to AA-9", [
            "**AA-1. Native elements first**; ARIA only where HTML has no element for the pattern. Every control has "
            "a name, a role and a value a program can read (4.1.2).",
            "**AA-2. The page's structure is the unit's structure**: heading levels, table headers, list nesting and "
            "reading order from the content tree ADR-0072 §8 returns (1.3.1, 1.3.2).",
            "**AA-3. Everything works from a keyboard** (2.1.1), no trap (2.1.2), in reading order (2.4.3), a visible "
            "focus indicator (2.4.7) not covered by a fixed header (2.4.11); a skip link to the unit's text (2.4.1).",
            "**AA-4. The level switch is three named controls, MI, SI and DI**, each a link to an address. Nothing a "
            "reader needs appears only on hover (1.4.13).",
            "**AA-5. A change the reader did not ask for is announced**: a route change moves focus to the new "
            "unit's heading; search results and a not-latest notice are status messages (4.1.3).",
            "**AA-6.** Motion is off where the device asks (`prefers-reduced-motion`), nothing flashes, nothing "
            "times out.",
            "**AA-7. Non-text content carries the text the unit supplies** (1.1.1): a short alternative and a long "
            "description on the page. Where a unit supplies none, the reader shows \"no description supplied\"; "
            "ADR-0071 §8 refuses that unit at release, so the words mark a defect in a view cut before the gate "
            "existed.",
            "**AA-8. Language is declared** for the page (3.1.1) and for a passage (3.1.2); a glossary term links to "
            "`narrative/glossary.md` as the unit binds it.",
            "**AA-9.** Help is in the same place on every page (3.2.6), and navigation keeps its order (3.2.3).",
        ], "amber", {"status": "proposed"}),
         ("§8 · No degeneracy is declared, and no row is added", [
             "**No theorem takes a premise from a reader.** A reader that fails shows a page wrongly or not at all; "
             "what a person then does is bounded as ADR-0071 §11 says: by the admit path for a principal, by the "
             "rules floor for a key-holder. A reader that drops a status mark breaks RM-4 and ADR-0029 §3's rule, "
             "a defect in the reader and not a change in any guarantee.",
         ], "green", {})],
    ], size=14) + 50

    y = sub(c, X0, y, "**§7 · Conformance is to WCAG 2.2 at Level AA, and it is a dated audit ⟨K9⟩** (drafter's choice "
            "of version and level; the custodian said \"WCAG Compliance\"); **§9 · Ratification condition**, item by item")
    wl = 2000
    wr = WW - wl - g
    xr = X0 + wl + g
    bl = stack(c, X0, y, wl, [
        ("§7 · WC-1 to WC-6. WCAG 2.2 is the W3C Recommendation in force and is ISO/IEC 40500:2025; WCAG 3.0 is a "
         "Working Draft and is not a target", [
            "**WC-1. A release of the reader carries an accessibility conformance report**: a dated results file, "
            "cited by digest, never edited after it is written (ADR-0069 §6 G-1). It names the reader's build by "
            "digest, the views and pages examined, both schemes, reading mode, each A and AA criterion with its "
            "result, and every known failure. [[red|Not written.]]",
            "**WC-2. The report has two parts, and only the second supports a claim.** *Computed*: pinned checkers "
            "over the pages examined; **a clean run refuses nothing and establishes nothing**; a failure refuses "
            "the release by the ratchet ADR-0069 §10.2 uses. *Examined*: a person's audit against each criterion, "
            "with a keyboard alone and at least two screen readers on two platforms, named with versions; the "
            "person is named and says whether they wrote any of the reader.",
            "**WC-3. A release says *checked* or *claimed*.** *Checked*: the examined part is complete for that "
            "build and was done by someone who did not write it. *Claimed*: anything less, and the accessibility "
            "statement uses that word.",
            "**WC-4. The claim covers the reader and the content of the views named, together.** Content defects "
            "are reported against the unit (ADR-0071 §8), not waived as \"content\".",
            "**WC-5. Four AAA criteria are met in reading mode as advice**: 1.4.6, 1.4.8, 3.1.3 (by the glossary "
            "links), 3.1.4. Marked *advice*, no part of the claim.",
            "**WC-6. Another reader makes its own claim.** A deployment's or a third party's client inherits the "
            "content's fields and nothing of this reader's report.",
        ], "amber", {"status": "proposed"}),
    ], size=14)
    cols = [("§9 · Condition", wr - 330), ("State", 330)]
    t = c.table(xr, y, cols, [
        ["**The reader exists and serves every unit of ADR-0071 §3's set, in `latest` and in at least one checkpoint "
         "view**, from the service of ADR-0072", NM + ": nothing is built, and no unit is written"],
        ["**§1 is seen at the reference**: the reader runs against the public API with no other access, and a second "
         "client that is not this reader renders the same unit from the same API", NM],
        ["**§3 to §6 are seen**: reflow at 320 CSS pixels and at 400% zoom; both schemes at LD-2's ratios; reading "
         "mode read, followed and printed with scripts off; the keyboard path through a unit, its three levels and "
         "its bindings", NM],
        ["**A conformance report under §7 WC-1 exists for a named build**, its computed part reproducible from pins "
         "and its examined part by a person other than the author", NM + ": no report, no auditor"],
        ["**The diagram generators emit a rendering for each scheme, and a long description for each diagram** "
         "(LD-4, AA-7)", NM],
        ["**ADR-0071 and ADR-0072 are ratified, or this record is ratified with them**", NM + ": both are Proposed"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NM],
        ["**The custodian's reading of every drafter's choice**, the WCAG version and level among them", NM],
    ], size=S, accent="red")
    y = max(bl, y + t) + 50

    y = sub(c, X0, y, "**Options considered, whole: the reader's framework and component library ⟨K8⟩** (one row is "
            "taken; licences as the drafter understands them, none checked); **Other choices**; **Consequences**; "
            "**Open obligations**")
    cols = [("Option", 640, {"bold": True}), ("Disposition", wl - 640)]
    t = c.table(X0, y, cols, [
        {"cells": ["React with Material UI (MIT)", "**Taken** ⟨K8⟩. A large component set with theming by CSS variables "
                   "and two colour schemes. Its accessibility is the library's claim, which is why M-1 and §7 do not "
                   "rest on it"], "accent": "amber"},
        ["React with React Aria or React Spectrum (Apache-2.0)", "[[grey|Not taken]] ⟨K8⟩. Behaviour and "
         "accessibility without a visual design; the strongest record on assistive technology of the React libraries "
         "the drafter knows. The first replacement for any Material UI component that fails M-1 *(drafter's "
         "recommendation)*"],
        ["React with Radix primitives or Base UI, styled in the repository", "[[grey|Not taken.]] Unstyled, "
         "accessible primitives. More to build, and less to override"],
        ["React with Chakra UI, Mantine, Ant Design, Fluent UI or Carbon", "[[grey|Not taken.]] Comparable component "
         "sets. None was asked for, and none changes §3 to §7"],
        ["A public-sector design system: GOV.UK Design System or USWDS", "[[grey|Not taken.]] Each is built and "
         "audited for accessibility first, server-rendered HTML with little script, which is RM-1's shape. Neither "
         "is a React library, and each carries a government's look. Worth a second reading if the audits of §7 go "
         "badly *(drafter's recommendation)*"],
        ["Vue with Vuetify, Angular with Angular Material, Svelte or Solid", "[[grey|Not taken]] ⟨K8⟩. Any of them "
         "can meet §1 and §3 to §7. Nothing in those sections is React's"],
        ["Web components (Lit), published for embedding", "[[grey|Not taken as the reader.]] Kept as a way to meet "
         "ADR-0072 §8: a `<topak-unit>` element any page can host would be a second client, and would satisfy "
         "§9's second item"],
        ["Server-rendered HTML with no client framework", "[[grey|Not taken]] ⟨K8⟩. It is what RM-1 already requires "
         "of every page. A reader that was only this would meet §3 to §7 with the least code, and would lose "
         "search-as-you-type and the level switch without a load"],
        ["A documentation generator: Docusaurus, MkDocs with Material, Sphinx, Antora, Astro Starlight, VitePress",
         "[[grey|Not taken.]] Each builds a site from files at one commit. Versions are copies of the tree, which "
         "fits a few releases and does not fit ADR-0072 §2 and §4. None serves an API another client could use ⟨K7⟩"],
        ["The carrier's rendering (Markdown on GitHub), as today", "[[grey|Not taken.]] It is what exists. It has no "
         "levels, no bindings, no views, and its accessibility is the carrier's"],
        {"group": "Other choices", "accent": "grey"},
        ["WCAG 2.1 AA, which most regulation still names", "[[grey|Not taken]] *(drafter's choice)*. 2.2 contains "
         "it, and adds focus not obscured, target size and consistent help"],
        ["WCAG 2.2 AAA throughout", "[[grey|Not taken.]] The W3C does not recommend AAA as a general policy. WC-5 "
         "takes four criteria that suit reading"],
        ["Conformance by automated scan", "[[red|Rejected]] (WC-2). It would make a tool's silence an admit"],
        ["An accessibility overlay script", "[[red|Rejected.]] It changes what one reader's users get and nothing of "
         "the content, and it would be a third party's script on every page"],
        ["A client-rendered application with no HTML until scripts run", "[[red|Rejected]] (RM-1). Reading mode "
         "would depend on the largest part of the reader working"],
        ["The scheme in the address, so that a link carries light or dark", "[[grey|Not taken]] (LD-1). The choice "
         "is the reader's, not the sender's"],
        ["A dark scheme only, or a light one only", "[[grey|Not taken]] ⟨K9⟩"],
    ], size=S, accent="grey")
    bl = y + t
    br = stack(c, xr, y, wr, [
        ("Consequences · positive", [
            "**A person reads the same unit, with the same marks, on a phone, a wide screen, paper or a screen "
            "reader.**",
            "**Conformance is a file with a date, a build and a name**, and the word *claimed* is available for when "
            "it is not yet earned.",
            "**The reader can be replaced.** It holds no content and no privilege.",
            "**Reading mode costs nothing extra**, because it is the baseline the rest is added to.",
        ], "green", {}),
        ("Consequences · negative", [
            "**Two schemes, reading mode and three levels multiply what an audit must examine.**",
            "**Material UI is a large dependency with its own design language**, and M-1 expects to override parts.",
            "**A person's audit is slow and has to be repeated per release.** Between audits a release is *claimed*.",
            "**Every diagram needs a second palette and a long description**, and the corpus has many diagrams.",
            "**Server rendering is a running service**, where a generated site would have been files.",
        ], "red", {"tint": False}),
        ("Open obligations", [
            "**The server-rendering framework for React.** Not chosen.",
            "**The checkers of WC-2**, pinned, and their ratchet.",
            "**An auditor who did not write the reader** (WC-3).",
            "**A second palette and long descriptions from the diagram generators** (LD-4, AA-7), which touches "
            "`skills/generating-corpus-diagrams` and `diagrams/`.",
            "**Mathematics and TLA+ in a page**: a rendering a screen reader can speak. Not designed.",
            "**Whether EN 301 549 or Section 508 is also claimed.** Not read for this draft.",
            "**Languages other than English.** AA-8 declares language; no translation is planned.",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=18, size=14)
    y = max(bl, br) + 80

    # ================================================================== History, all three
    y = band(c, X0, y, "History, whole: two rows for each record, and R1 is the same change three times")
    R1 = ("**Renumbered from ADR-00{a} to ADR-00{b}**, with its five siblings, each up by one: the set is now ADR-0071 "
          "to ADR-0076. ADR-0070 was already taken by a record in flight on another branch, which the first draft's "
          "check of branches missed because it looked only at the branches this clone had fetched. Every "
          "cross-reference among the six, every degeneracy id and the index rows moved with the numbers. The old "
          "numbers are not shown struck at each place, since the change is the same at every one. The provenance "
          "note says which record holds ADR-0070 and that it was not read. No decision text changes")
    SRC1 = "The custodian's question of 2026.11.16; `git ls-remote`, and pull request #51"
    ST = "Drafted 2026.11.16 by the assistant at the custodian's direction, not reviewed"
    cols = [("Record", 120, {"bold": True}), ("Tag", 70), ("Kind", 200), ("Change", WW - 120 - 70 - 200 - 520 - 420),
            ("Source", 520), ("State", 420)]
    t = c.table(X0, y, cols, [
        ["ADR-0071", "—", "—", "Initial draft. User documentation is a derived layer that decides nothing and ranks "
         "below the narrative. Twenty-one readers are listed by position: holding a seat, at the gate or a trust "
         "root, and outside. The document set is listed for Build, Run, governance, external, every reader and the "
         "command-chain overlay, each row with its readers, the records it rests on and what no record yet decides. "
         "Every unit is read at three levels, MI, SI and DI, mapped to C4's four; a level may leave out and never "
         "add, and a limit travels with its guarantee. A binding ties a statement to a node by digest, with a "
         "relation and a reader: every statement at DI, every must at SI, every guarantee or limit at MI. Status "
         "marks are ADR-0029 §3's. A stale unit is served and marked, and only a reading clears it. A release is a "
         "manifest cut under seven mechanical gates that check form and not meaning. No degeneracy and no "
         "trusted-base row, because a reader is bounded by the admit path or by the rules floor",
         "The custodian's request of 2026.11.16; the role and document inventory made for this draft", ST],
        {"cells": ["ADR-0071", "R1", "Revision before ratification", R1.format(a="70", b="71"), SRC1, ST],
         "accent": "amber"},
        ["ADR-0072", "—", "—", "Initial draft. The documentation service is a projection of the corpus that can be "
         "dropped and rebuilt to the same digests, and is not a system of record. A unit's revision is immutable and "
         "addressed by digest, and every revision stays reachable. A unit is drafted, released, superseded or "
         "withdrawn, with withdrawal a revision and disposal not a state. A view is a manifest; `latest` moves and "
         "every checkpoint and release view is cut once, and every operation is defined for every view. The store "
         "is one table with a composite key and secondary indexes, reached only through the DynamoDB interface; the "
         "reference's engine is ExtendDB on PostgreSQL, recommended with its immaturity stated. GraphQL and REST "
         "are generated from one model, equal and read-only. Any reader may integrate and none is privileged; the "
         "fields accessibility needs are mandatory in the content tree. Ingest is the only write path and starts "
         "on a digest. No degeneracy and no trusted-base row. Annex A gives the keys",
         "The custodian's request of 2026.11.16", ST],
        {"cells": ["ADR-0072", "R1", "Revision before ratification", R1.format(a="71", b="72"), SRC1, ST],
         "accent": "amber"},
        ["ADR-0073", "—", "—", "Initial draft. The reference reader is a client of ADR-0072's public API with no "
         "privilege and no content of its own. It is React with Material UI, pinned. Pages arrive as complete HTML; "
         "the layout reflows from 320 CSS pixels; there is a light and a dark scheme following the device; reading "
         "mode is the scriptless page and never hides a status mark or a binding; assistive access is stated as "
         "nine requirements. Conformance is to WCAG 2.2 AA, as a dated report with a computed part that may only "
         "refuse and an examined part by a person, and a release says *checked* or *claimed*. No degeneracy and no "
         "trusted-base row. Alternatives listed", "The custodian's request of 2026.11.16", ST],
        {"cells": ["ADR-0073", "R1", "Revision before ratification", R1.format(a="72", b="73"), SRC1, ST],
         "accent": "amber"},
    ], size=S, accent="amber")
    y += t + 16
    y += c.para(X0, y, WW, "**What a reader should take from the three together.** The layer (ADR-0071) says what is "
                "written and for whom, and that none of it decides; the service (ADR-0072) says how every revision "
                "and every cut view stays reachable and equal, from a store that can be thrown away; the reader "
                "(ADR-0073) says how a page shows a unit without adding to it, and that its accessibility is a claim "
                "until a named person has examined a named build. **Every ratification condition of all three is "
                "not met**, each ends with the custodian's reading of the drafter's choices, and each depends on the "
                "one before it being ratified or ratified with it. G12 item 116 lists the set among what is owed.",
                14.5, "muted")
    return c
