"""D9 — The archive of record (ADR-0074, ADR-0075, ADR-0076; all Proposed, 2026.11.16).

ADR-0074: what the archive holds and how it is fed; ADR-0075: how long, and how a thing leaves; ADR-0076: the two
stores, the index, integrity and reading. D3 draws the four record planes; this diagram opens the archive plane
and draws nothing of D3's content again."""
from lib import Canvas, STATUS, STATE_G12, text_width

ID, SLUG = "D9", "archive-of-record"
RECORDS = ('ADR-0074', 'ADR-0075', 'ADR-0076',)   # the records this diagram draws in full: a name of one opens it

W = 3600
S = 14


# ---------------------------------------------------------------------------------------------- layout helpers
def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, measured over every card in the row. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), tsize=k.get("tsize", 16))
            for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def stack(c, x, y, w, specs, gap=16, size=S):
    """Cards one under another. specs: (title, body, accent, kwargs). Returns the bottom."""
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, **k) + gap
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


NOTWRITTEN = ("Not written", "red", "2 3")
NOTDRAFTED = ("Not drafted", "red", "2 3")
NOTRUN = ("Not run", "red", "2 3")
NOTMET = ("Not met", "red", "6 4")


def conditions(c, x, y, w, items, accent="blue"):
    """Ratification conditions item by item: (condition, state). Every state here is Not met, as the records say."""
    cols = [("Condition", w * 0.72, {}), ("State, as the record marks it", w * 0.28)]
    rows = [{"cells": [cond, f"[[red|Not met.]] {st}"], "accent": "red"} if st else
            {"cells": [cond, "[[red|Not met.]]"], "accent": "red"} for cond, st in items]
    return c.table(x, y, cols, rows, size=13.5, accent=accent)


# ---------------------------------------------------------------------------------------------- the diagram
def build():
    c = Canvas(ID, "The archive of record: what the log ordered, what a round sealed, what a build pinned, kept in "
               "two stores and an index, on one retention schedule",
               "ADR-0074 says what the archive holds and how it is fed: five holdings, each a copy from one source "
               "by a program that only reads, and a segment of the log is held before a mark the log orders says so. "
               "ADR-0075 gives every holding a line in one retention schedule: facts are never erased, a round unit "
               "ends by erasure or by period and is dropped whole, every absence is explained by a fact, and a hold "
               "may only preserve. ADR-0076 makes the archive a locked store, a governed store and an index, with "
               "the log ordering the root of every segment and nothing that decides reading the archive without a "
               "proof. **All three are Proposed (2026.11.16), unreviewed, and nothing in them is modelled, checked or "
               "built: ADR-0005 §5 still holds, \"The archive does not exist at the reference\".** D3 draws the "
               "four record planes; this diagram opens the archive plane and does not redraw D3.",
               W, "ADR-0074 provenance, Status note, Context, §1–§10 (§2's table, §6's table, §9's table), Options, "
               "Consequences, Open obligations, History (R1); ADR-0075 provenance, Status note, Context, §1–§10 (§1's "
               "table, §2's schedule, §8's table, §8a's table, §9's table), Options, Consequences, Open obligations, "
               "Annex A (its table and findings 1–13), Annex B (entries 1–8), History (R1, R2); ADR-0076 provenance, "
               "Status note, Context, §1–§11 (§1's table, §7's two tables, §9's table, §10's table), Options (three "
               "tables), Consequences, Open obligations, Annex A (three tables), Annex B (entries 1–6 and the proposed "
               "row T-0045-40), History (R1); ADR-0005 §1, §5; ADR-0003 A3; ADR-0004; ADR-0028 §1–§4; ADR-0045 Annex "
               "A T-0045-7, T-0045-11; ADR-0072 §1, §5–§7 (Proposed); ADR-0070 as ADR-0075 R2 reads it at `593af40` "
               "(Proposed, on branch `ccr-dd716f39-ywh7ud`, not in this tree); mechanism/GAPS-AND-ASSUMPTIONS G9, "
               "G11, G14; diagrams/topak/src/d_d3_record_planes.py for the plane names and accents; G12 §9",
               state=STATE_G12)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    y = status_strip(c, X0, X1, y, [
        ("ADR-0074", "proposed", "C2, C4 · R1 · 2026.11.16"),
        ("ADR-0075", "proposed", "C1, C2, C4 · R2 · 2026.11.16"),
        ("ADR-0076", "proposed", "C2, C4 · R1 · 2026.11.16"),
        ("their modules (§10, §10, §11)", NOTWRITTEN, ""),
        ("the mechanism record for the mark and compaction", NOTDRAFTED, ""),
        ("the dependent entries (ADR-0075 Annex B; ADR-0076 Annex B)", NOTDRAFTED, ""),
        ("floor entries: the hold, the readers' proviso", NOTWRITTEN, ""),
        ("the stores, the index, their products", "notbuilt", "none run"),
        ("the archive at the reference", "notbuilt", "ADR-0005 §5; G9"),
        ("erasure, the erasure roster", "notbuilt", "G11; ADR-0029 §5"),
        ("ADR-0070, read by ADR-0075 R2", "proposed", "on another branch, not here"),
        ("a reader who is not the drafter", ("None yet", "red", "6 4"), ""),
    ])
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian's request of 2026.11.16 settled "
                "three things the set uses: ⟨K10⟩ every revision and every checkpoint or release of the documentation "
                "stays reachable, equal to the latest; ⟨K11⟩ a separate set of records for the archive of record; "
                "⟨K12⟩ the set conforms to TOPAK's retention requirements, follows good practice and is informed by "
                "the documentation's design. ADR-0076 also applies ⟨K5⟩ (a single-table store behind the DynamoDB "
                "interface) and ⟨K6⟩ (GraphQL and REST), said of the documentation, on the strength of ⟨K12⟩. "
                "**Every other choice is the drafter's**, marked (drafter's choice) or (drafter's recommendation) "
                "in the records and kept so here. One author, one day; ADR-0075 R2 the same day, after reading "
                "ADR-0070. The three records cite each other and ask to be ratified together.", 14.5, "muted") + 34

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "The archive plane opened: four sources, two stores, an index, the mark, and who reads "
             "(ADR-0074 §1–§4; ADR-0076 §1, §6, §7)", status="proposed", extra="nothing here is built")
    y = _picture(c, X0, X1, y + 90)
    y = _adr_0074(c, X0, X1, y + 40)
    y = _adr_0075(c, X0, X1, y + 40)
    y = _adr_0076(c, X0, X1, y + 40)
    return c


def _picture(c, X0, X1, top):
    """Returns the y below the picture."""
    WW = X1 - X0
    S1 = 13.5
    src_w = 640
    gap1 = 150
    rx = X0 + src_w + gap1
    rw = 1700
    rpad = 24
    st_x = rx + rpad
    st_w = 760
    ix_x = st_x + st_w + 120
    ix_w = rx + rw - rpad - ix_x
    gap2 = 150
    rd_x = rx + rw + gap2
    rd_w = X1 - rd_x

    # ---- the sources (left), in D3's names and accents
    LOG = ("P · the log", [
        "**The ordering authority** (ADR-0015; D3). Every entry of every kind is a fact for holding A, read in index "
        "order (ADR-0074 §2, §3 F-1).",
        "**Orders the archive mark** for a held segment, on its own recomputation of the root (ADR-0074 §4 A-2, A-4): the "
        "roots are facts, and an auditor has them from the log (ADR-0076 §5 IN-2).",
        "**Discards no entry above the newest mark** (ADR-0074 §4 A-3). An unmarked log grows and never loses an entry (A-5).",
        "**The F6 entry** is how an erasure reaches the archive, and by no other path (ADR-0075 §3 ER-1).",
    ], "violet", {"status": "built", "status_extra": "3 replicas; nothing compacted (G14)"})
    REPO = ("The repository, at a manifest", [
        "**The corpus is a holding** (drafter's choice: no record says the corpus is archived). A cut is the files "
        "one manifest measures (ADR-0074 §2 C, H-6).",
        "The feeder is given a manifest and a commit, **refuses a tree that does not verify**, and stores each file "
        "under its digest, once (§3 F-6).",
        "Trust is T-0045-11's and no better: one person cuts the manifests (§7).",
    ], "grey", {})
    EVID = ("Where a citing fact's author put it", [
        "**Evidence**: an object a fact cites by digest that is neither payload nor corpus: attestation evidence, "
        "gate evidence, promoted artifacts and signatures, the genesis bundle, issued rules (§2 D).",
        "When a segment is ingested each cited digest is looked for; **a digest with no object is recorded as "
        "*missing*** and never passed over in silence (§3 F-7).",
    ], "grey", {})
    TRANS = ("K · transport", [
        "**Transport, not the record** (ADR-0005 §1; D3). A sealed round topic with its `after` companion is "
        "holding B's unit (ADR-0074 §2 B).",
        "**Captured after the seal**, whole, judged by nothing: no filter, redaction or summary (§3 F-2, F-9). "
        "Masking is the write path's, before the seal.",
        "**Capture does not touch the topic**: it is dropped on its own schedule; a topic that expires uncaptured is "
        "lost to the archive and its header says not captured (F-4; ADR-0003 A3).",
        "**At the archetype every unit is captured** (drafter's choice) (F-5).",
    ], "amber", {"status": "accepted", "status_extra": "ADR-0005 · C4 · Batch 27"})

    # ---- the archive (middle)
    LOCK = ("The locked store (ADR-0076 §2) · T-0045-7, delegated", [
        "**Holds A facts as segments, C the corpus, D evidence, E the journal** (§1). Duty: keep, unchanged, for each "
        "line's at least. Failure: evidence lost or damaged.",
        "**LS-1** Every object under the SHA-256 of its bytes, written once. **LS-2** Under a lock no credential can "
        "shorten or lift (compliance mode or a declared equivalent), extended before it ends, never shortened; a "
        "lock that lapses under its line is a finding. **LS-3** In every declared fault domain: at least three, under "
        "two administrations, one sharing no site with the replicas (drafter's choice). **LS-4** Bytes as written; "
        "a segment names the cut whose formats it uses. **LS-5** Ceph's object gateway (drafter's recommendation).",
        "**A segment is *held*** when its bytes are in this store in every declared fault domain and each copy hashes "
        "to its root (ADR-0074 §4 A-1).",
        "**A** facts: every log entry, in segments, complete and gapless (§3 F-1) · **C** cuts, by manifest · **D** "
        "objects, by digest · **E** the journal: ingests, marks received, fixity results, drops, reads; the one thing "
        "the archive originates (§1 K-4), with a tree of its own whose root each mark carries (ADR-0076 §5 IN-6).",
    ], "blue", {"status": "notbuilt"})
    GOV = ("The governed store (ADR-0076 §3) · D3's plaintext store · T-0045-40, proposed", [
        "**Holds B round units** and nothing else: ADR-0004's store \"built for deletion\". Duty: keep until erasure "
        "or period, and then no longer. Failure: a unit lost early; a unit not deleted.",
        "**GS-1** One container, one store, for the unit's whole time: no tiering. **GS-2** No version, no lock; a "
        "deleted object is gone from every read at once. **GS-3** Dropped when no read in any domain returns it, "
        "purged when the bytes leave the media; the deployment declares the purge interval. **GS-4** Nothing "
        "derived from a unit outside it. **GS-5** Held in the domains declared for payload, each receiving every "
        "drop. **GS-6** The same gateway, separately deployed, versioning off (drafter's recommendation).",
        "**Shares nothing with the locked store**: no bucket, volume, credential or administrator's role (§1 P-1). "
        "The only right to delete is the executor's, on an F6 entry or the end of a period.",
    ], "brown", {"status": "notbuilt"})
    IDX = ("The index (ADR-0076 §4) · no row", [
        "**One table behind the DynamoDB interface**, under ADR-0072 §5's contract ⟨K5⟩: composite key, every "
        "access a key condition, none a scan, immutability by conditional write (IX-1; Annex A).",
        "**A projection of both stores**: fields of facts, unit headers, cut manifests (§1). It is not the record: "
        "dropped and rebuilt, the rebuild checked against the roots (P-2, IX-3).",
        "**No attribute derived from a body** (IX-2; ADR-0075 §3 ER-5). A unit's item says it exists, where, its "
        "digest and its state, not what is in it.",
        "**Engine**: ExtendDB on PostgreSQL (drafter's recommendation), new and self-declared for development; "
        "tolerable here and **not for either store** (IX-4).",
    ], "grey", {"status": "notbuilt"})
    READ = ("Reading and export (ADR-0076 §7, §8) ⟨K6⟩ ⟨K10⟩", [
        "**Every read is by an identified reader under a reader set**, declared per holding and, for A, per forensic "
        "class (RD-1). Reader sets are policy in a promoted bundle (drafter's choice); the audit authority is "
        "never removed (RD-2; ADR-0028 §4).",
        "**GraphQL and REST, generated from one model, equal, read-only** (RD-3; ADR-0072 §7). Every past state is "
        "read as the newest (RD-5).",
        "**An answer about a fact carries its inclusion proof and names its mark** (RD-7): the service and the index "
        "are conveniences the reader need not trust.",
        "**Every read but a read of C is entered in the journal** (RD-6), with the reader, the set, the ask and a "
        "stated purpose nothing checks. A read writes nothing else (RD-8).",
        "**Export**: any readable range as one self-describing package (a BagIt bag, RFC 8493, drafter's choice) "
        "that verifies with no access to the archive (EX-1, EX-2). A package of units is a copy no erasure reaches "
        "(EX-3).",
    ], "teal", {"status": "notbuilt"})

    # ---- the readers (right)
    AUD = ("The audit authority", [
        "\"the anchor plus a declared external auditor role\" (ADR-0028 §3); **the role is undefined** (ADR-0076 "
        "§11; ADR-0028, Open obligations). Reads **A** always, every class, and **E**.",
    ], "brown", {})
    ACL = ("The round topic's ACL readers", [
        "Read **B**: whoever the topic's ACL named (ADR-0003 0003.3), carried to the unit (drafter's choice), and "
        "the \"Separate read-only principals for audit\". Readers of **D**: as the fact that cites the object.",
    ], "brown", {})
    ANY = ("Anyone, for the archetype's corpus", [
        "Reads **C**, which is published; a deployment's own cuts as it declares. **The documentation service "
        "(ADR-0072 §1 P-1, Proposed) reads holding C and nothing else**, and its store can be rebuilt from C "
        "(ADR-0074 §5 C-4).",
    ], "grey", {})
    GATE = ("A gate, a tally, a tool that needs a compacted entry", [
        "**Takes it only with an inclusion proof against a mark in the log** (AR-2); an entry without one is absent "
        "and the gate fails. **Absence only subtracts** (AR-3). Lineage (ADR-0035 §1) and the intake gate that "
        "reruns an extractor (ADR-0069 §3a IG-4), both Proposed, are the first two readers this binds.",
    ], "teal", {})
    ADM = ("The admit path, and anything that decides on a unit", [
        "**The admit path does not read the archive** (AR-1): true of the reference today, and kept true. **Nothing "
        "decides on a unit** (AR-4): no admit, gate or tally reads holding B. So an archive that fails in any way, "
        "lying included, produces no admit, promotion or issuance the mechanism would otherwise refuse (§6).",
    ], "red", {"tint": False, "dash": "6 4"})

    def mh(spec, w_):
        t, b, _, k = spec
        return c.card(0, 0, w_, t, b, draw=False, size=S1, status=k.get("status"))

    # heights
    h_log, h_repo, h_evid, h_trans = (mh(s, src_w) for s in (LOG, REPO, EVID, TRANS))
    h_lock, h_gov = mh(LOCK, st_w), mh(GOV, st_w)
    h_idx, h_read = mh(IDX, ix_w), mh(READ, ix_w)
    h_aud, h_acl, h_any, h_gate, h_adm = (mh(s, rd_w) for s in (AUD, ACL, ANY, GATE, ADM))

    # vertical positions: the sources stack; the locked store spans log..evidence; the governed store is level
    # with the transport, below a corridor for the erasure arrow
    sgap = 56
    y_log = top + 60
    y_repo = y_log + h_log + sgap
    y_evid = y_repo + h_repo + sgap
    lock_h = max(h_lock, y_evid + h_evid - y_log)
    y_gov = y_log + lock_h + 110
    y_trans = y_gov + (h_gov - h_trans) / 2 if h_gov > h_trans else y_gov
    if y_trans < y_evid + h_evid + sgap:
        y_trans = y_evid + h_evid + sgap
        y_gov = y_trans
    gov_h = max(h_gov, h_trans)
    bottom_stores = max(y_gov + gov_h, y_trans + h_trans)
    # the index and the read service share the right sub-column, from the locked store's top
    y_idx = y_log
    y_read = y_idx + h_idx + 110
    read_h = max(h_read, bottom_stores - y_read)
    region_top = top
    region_bot = max(bottom_stores, y_read + read_h) + rpad + 10
    # readers: stacked from the region top, aligned to the read-service band where possible
    ys_rd = []
    yy = y_log
    for h in (h_aud, h_acl, h_any, h_gate, h_adm):
        ys_rd.append(yy)
        yy += h + 44
    rd_bot = yy - 44

    # ---- regions
    c.region(rx, region_top, rw, region_bot - region_top, "the archive · the system of record (ADR-0005 §1) · "
             "not built (ADR-0005 §5; G9)", "blue", dash="2 3", size=15)
    c.region(X0 - 16, region_top, src_w + 32, max(y_trans + h_trans, y_evid + h_evid) + rpad + 10 - region_top,
             "the sources: each holding has one (ADR-0074 §2 H-2)", "grey", dash="10 6", size=15)
    c.region(rd_x - 16, region_top, rd_w + 32, max(rd_bot, region_bot - rpad - 10) + rpad + 10 - region_top,
             "the readers (ADR-0076 §7 RD-1; §6)", "brown", dash="10 6", size=15)

    # ---- cards
    c.card(X0, y_log, src_w, LOG[0], LOG[1], accent=LOG[2], size=S1, **LOG[3])
    c.card(X0, y_repo, src_w, REPO[0], REPO[1], accent=REPO[2], size=S1, tint=False, **REPO[3])
    c.card(X0, y_evid, src_w, EVID[0], EVID[1], accent=EVID[2], size=S1, tint=False, **EVID[3])
    c.card(X0, y_trans, src_w, TRANS[0], TRANS[1], accent=TRANS[2], size=S1, **TRANS[3])
    c.card(st_x, y_log, st_w, LOCK[0], LOCK[1], accent=LOCK[2], size=S1, h=lock_h, **LOCK[3])
    c.card(st_x, y_gov, st_w, GOV[0], GOV[1], accent=GOV[2], size=S1, h=gov_h, **GOV[3])
    c.card(ix_x, y_idx, ix_w, IDX[0], IDX[1], accent=IDX[2], size=S1, tint=False, **IDX[3])
    c.card(ix_x, y_read, ix_w, READ[0], READ[1], accent=READ[2], size=S1, h=read_h, **READ[3])
    for spec, yy, h in zip((AUD, ACL, ANY, GATE, ADM), ys_rd, (h_aud, h_acl, h_any, h_gate, h_adm)):
        c.card(rd_x, yy, rd_w, spec[0], spec[1], accent=spec[2], size=S1, **spec[3])

    # ---- arrows: feeders (not built: dashed 2 3, as D3 draws the unbuilt ETL)
    nb = "2 3"
    sx1 = X0 + src_w
    c.arrow([(sx1, y_log + 60), (st_x, y_log + 60)], "violet", sw=2.4, dash=nb, label="① segments, in index order",
            lpos=0.5, loff=(0, -24))
    c.arrow([(sx1, y_repo + 50), (st_x, y_repo + 50)], "grey", sw=2.4, dash=nb, label="③ a cut, by manifest",
            lpos=0.5, loff=(0, -24))
    c.arrow([(sx1, y_evid + 50), (st_x, y_evid + 50)], "grey", sw=2.4, dash=nb, label="④ objects, by digest",
            lpos=0.5, loff=(0, -24))
    c.arrow([(sx1, y_trans + 60), (st_x, y_trans + 60)], "amber", sw=2.4, dash=nb,
            label="② a sealed unit, whole", lpos=0.5, loff=(0, -24))
    # ⑤ the mark: from the locked store's top, over the region, into the log's top
    cy_top = top - 48
    mx = st_x + st_w - 40
    lx = X0 + src_w - 60
    c.arrow([(mx, y_log), (mx, cy_top), (lx, cy_top), (lx, y_log)], "violet", sw=2.4, dash=nb,
            label="⑤ the mark: the archive reports a root, a replica recomputes it, the log orders it", lpos=0.5,
            lw=900)
    # ⑥ erasure inside the archive: locked store (the F6 entry in a segment) → governed store, dashed red
    ex = st_x + st_w * 0.5
    c.arrow([(ex, y_log + lock_h), (ex, y_gov)], "red", sw=2.4, dash="7 5",
            label="⑥ an F6 entry: drop the unit whole", lpos=0.5, lw=430)
    # ⑦ headers and fields to the index; the index rebuilt from both
    c.arrow([(st_x + st_w, y_log + 120), (ix_x, y_log + 120)], "blue", sw=2.2, dash=nb,
            label="⑦ fields; manifests", lpos=0.5, loff=(0, -22))
    c.arrow([(st_x + st_w, y_gov + 70), (ix_x - 60, y_gov + 70), (ix_x - 60, y_idx + h_idx - 40),
             (ix_x, y_idx + h_idx - 40)], "brown", sw=2.2, dash=nb,
            label="⑦ the unit's header", lpos=0.08, lw=300, loff=(0, -26))
    # the read service reads the stores and the index
    c.arrow([(ix_x + ix_w * 0.5, y_idx + h_idx), (ix_x + ix_w * 0.5, y_read)], "teal", sw=2.2, dash=nb,
            label="answers", lpos=0.5)
    c.arrow([(ix_x, y_read + read_h * 0.6), (st_x + st_w, y_read + read_h * 0.6)], "teal", sw=2.2, dash=nb,
            label="a unit's records", lpos=0.5, loff=(0, -22), lw=220)
    # ⑧ readers → the read service; the admit path: no read
    rsx = rx + rw
    ry = y_read + 50
    for i, yy in enumerate(ys_rd[:4]):
        hh = (h_aud, h_acl, h_any, h_gate)[i]
        c.arrow([(rd_x, yy + hh / 2), (rsx + 60, yy + hh / 2), (rsx + 60, ry + i * 18), (ix_x + ix_w, ry + i * 18)],
                "teal", sw=2.0, dash=nb)
    c.label(rsx + 60, ys_rd[0] + 14, "⑧ reads", "teal", 12.5)
    ya = ys_rd[4] + h_adm / 2
    c.arrow([(rd_x, ya), (rsx + 20, ya)], "red", sw=2.4, dash="7 5",
            label="no read", lpos=0.5, loff=(0, 24))

    bot = max(region_bot, rd_bot + rpad + 10, y_trans + h_trans + rpad + 10)
    lg = c.legend(X0, bot + 36, [
        ("box", "violet", "P · the log"), ("box", "amber", "K · transport"), ("box", "blue", "the locked store"),
        ("box", "brown", "the governed store (D3's plaintext store); readers"), ("box", "grey", "the index: a projection"),
        ("box", "teal", "the read service"),
        ("arrow", "blue", "a feeder or a read: not built", "2 3"), ("arrow", "red", "erasure; a path denied", "7 5"),
    ])
    ky = bot + 36 + lg + 30
    c.text(X0, ky + 16, "**The arrows** (every one is a path nothing has built)", 16, "ink")
    kh = c.table(X0, ky + 30, [("", 60, {"bold": True}), ("What moves, and on whose word", WW - 60)], [
        ["①", "**The facts feeder** reads the log in index order and writes segments: complete, in order, no gap "
              "between one and the segment before (ADR-0074 §3 F-1). A feeder is a program in the repository, "
              "named by digest, that reads one source and writes one holding, holds no credential that could write "
              "to a source, and judges nothing (§1 K-3; §3 F-9). Ingest is idempotent and addressed by content (F-8)."],
        ["②", "**The round-unit feeder** reads a topic after its seal (Run: ADR-0042 §5; Build: the topic set, "
              "ADR-0021 §3) and writes the unit as one container, with the `after` companion as its second member "
              "(F-2). The header is a fact and the container is payload (F-3)."],
        ["③", "**The corpus feeder** is given a manifest and a commit, refuses a tree that does not verify, and "
              "stores each file under its digest with the manifest as the cut's index (F-6). Reads what ADR-0029's "
              "genesis bundle and corpus manifest format define, which is open."],
        ["④", "**Evidence** is looked for by each digest a segment's facts cite; found, it is written under its "
              "digest; a digest with no object is recorded as missing (F-7)."],
        ["⑤", "**The archive mark** (drafter's choice): an entry the mechanism orders for a held segment, naming "
              "its range and its root; not an admit, promotion or issuance, and it enables nothing (§4 A-2). A "
              "replica proposes it only for a root it recomputed from its own log; a wrong root is refused (A-4). "
              "Kinds: held (this record's), erased and disposed (ADR-0075's), the last two recording the "
              "archive's report, which A-4 cannot reach (A-7). The marks are facts, in the next segment (A-6). "
              "Each mark also carries the journal's root, which the mechanism cannot recompute (ADR-0076 §5 IN-6)."],
        ["⑥", "**Erasure reaches the archive as the F6 fact and by no other path** (ADR-0075 §3 ER-1): the feeder of "
              "facts sees the entry, the entry names units, the governed store drops each container whole in every "
              "fault domain. When every copy is gone the archive reports it and the mechanism orders the erased "
              "mark; between the two the erasure is ordered and not complete, and that state is listable (ER-2). "
              "Disposition at the end of a period takes the same path with a disposed mark (§5 DP-1, DP-2)."],
        ["⑦", "**The index is a projection of both stores**: fields of facts and of headers, cut manifests, and no "
              "attribute derived from a body (ADR-0076 §1, §4 IX-2). Dropped, it is rebuilt from the stores and "
              "checked against the roots (P-2)."],
        ["⑧", "**A read** is by an identified reader under a reader set (RD-1), answered through GraphQL or REST "
              "(RD-3), with the inclusion proof and the mark for any fact (RD-7), and journalled unless it reads C "
              "(RD-6). **The admit path never reads the archive** (§6 AR-1), and no admit, gate or tally reads a "
              "unit (AR-4)."],
    ], size=13.5, accent="blue", header=False)
    return ky + 30 + kh + 40


# ================================================================================================ ADR-0074
def _adr_0074(c, X0, X1, y):
    WW = X1 - X0
    y = band(c, X0, y, "ADR-0074 · The archive keeps what the log ordered, what a round sealed, what a fact cites and "
             "what a manifest measured, and originates none of it", status="proposed",
             extra="C2, C4 · R1 · drafted 2026.11.16, not reviewed")
    y += c.para(X0, y, WW, "**Context.** The corpus says where the record is kept and nothing about the place: ADR-0005 §1 "
                "names the archive as the system of record, ADR-0004 keeps the hash and a pointer in the record and "
                "plaintext in a store built for deletion, ADR-0003 A3 makes the archive \"a separate store fed by that "
                "ETL and ... not a tier of the topic\", T-0045-7 trusts it to retain what was written, and ADR-0005 §5 "
                "says it does not exist at the reference. **No record says what the ETL takes, when, or on whose "
                "word.** ADR-0005 and ADR-0024 §8 give two right answers to which store is the record: the archive "
                "keeps, the log authors. The corpus keeps itself in a repository on a carrier whose identifiers "
                "\"locate and do not identify\" (ADR-0069 §9 C-5, Proposed), and ⟨K10⟩ asks that every revision stay "
                "reachable. **Status note**: C2 (§2's exhaustiveness and §1's confinement) and C4 attach; C1 is "
                "ADR-0075's; C3: nothing accepted is reversed, and §4 A-3 adds a precondition to a compaction no "
                "record has decided. Deployment position: Archetype.", 14.5, "muted") + 30

    # ---- §1 and §2
    y = band(c, X0, y, "§1 The archive keeps and never originates ⟨K11⟩ · §2 Five holdings ⟨K12⟩, the table whole")
    y += row_cards(c, X0, y, WW, 30, [
        ("K-1 Every item is a copy", ["Of an entry the log ordered, a round topic the mechanism sealed, an object a "
                                     "fact cites by digest, or a file a manifest measured; each carries what says "
                                     "which: a log index, a round's identity and seal, a digest, a manifest line."],
         "blue", {}),
        ("K-2 The log says what happened; the archive is where that is kept",
         ["A fact is in the archive because it was in the log. **Where a copy and the log disagree, the log is right "
          "and the copy is a finding.** When the log no longer holds an entry (§4), the copy stands on the mark that "
          "covers it and on nothing else."], "violet", {}),
        ("K-3 No program in the archive writes to a source", ["The feeders read the log, the transport and the "
                                                             "repository, and hold no credential that could write to "
                                                             "any of them."], "green", {}),
        ("K-4 The one exception: the archive's account of itself", [
            "What it ingested, checked, dropped and showed to whom (holding E). A record about the archive, not a fact "
            "about any principal's action; **nothing reads it to decide anything.**",
            "This keeps T-0045-7's class: a store that only copies can lose a copy, which is \"legibility subtracted, "
            "authority untouched\". ADR-0076 §6 closes the remaining route."], "blue", {}),
    ]) + 24
    cols = [("", 50, {"bold": True}), ("Holding", 860, {}), ("Source", 300), ("Unit of ingest", 330),
            ("Erasable", 300)]
    cols.append(("Named by", WW - sum(cl[1] for cl in cols)))
    y += c.table(X0, y, cols, [
        {"cells": ["A", "**Facts**: every entry of the consensus log, whatever its kind. Admits (F1), stop "
                   "attributions (F2), votes (F3), issuances (F4), break-glass invocations (F5), erasure events (F6), "
                   "and every other entry: lease and epoch transitions, seals, and the marks of §4", "The log",
                   "A **segment**: a contiguous range of log indices", "No",
                   "ADR-0015; ADR-0028 §1; ADR-0024 §8"], "accent": "blue"},
        {"cells": ["B", "**Round units**: a sealed round topic with its `after` companion, whole. Envelopes, denials "
                   "and bodies together: raw emissions, `Actuate` records, the task, the tool list, review commentary",
                   "The transport, after the seal", "A **unit**: one principal's round in one rules-epoch chain",
                   "Yes, whole", "ADR-0003 0003.1, 0003.2, A1, A2; ADR-0037 §3; ADR-0042 §3"], "accent": "brown"},
        {"cells": ["C", "**The corpus**: records, checkpoints, manifests, modules and results, the floor, the narrative "
                   "and its revisions, derived documents, documentation releases (ADR-0071 §8), and the reference "
                   "trees", "The repository, at a manifest", "A **cut**: the files one manifest measures", "No",
                   "ADR-0029 §5; T-0045-11; the checkpoints' convention G-C1"], "accent": "blue"},
        {"cells": ["D", "**Evidence**: an object a fact cites by digest that is neither payload nor corpus. "
                   "Attestation evidence, gate-evidence files, promoted artifacts and their signatures, the genesis "
                   "bundle, issued rules, the review attestation; lineage records and corpus-root manifests if "
                   "ADR-0035 and ADR-0069 are ratified", "Where the citing fact's author put it",
                   "An **object**, by digest", "No, unless it embeds payload, when it is in B",
                   "ADR-0034 §3; ADR-0024 §3; ADR-0029 §5, A2.2"], "accent": "blue"},
        {"cells": ["E", "**The archive's journal**: ingests, marks received, fixity results, drops, and reads",
                   "The archive", "An entry", "No", "§1 K-4; ADR-0076 §5, §7"], "accent": "blue"},
    ], size=14, accent="blue") + 24
    y += row_cards(c, X0, y, WW, 30, [
        ("H-1 The list is exhaustive · H-2 One source, one feeder", [
            "A thing a record says is retained, kept or archived belongs to one holding; a record that adds such a "
            "thing names its holding or adds one here. Each holding has one source and one feeder (§3)."], "blue", {}),
        ("H-3 Payload is only ever in B · H-4 A denial is in B", [
            "A, C, D and E hold no cognitive payload (ADR-0004); evidence that carries payload goes in its unit so an "
            "erasure reaches it.",
            "A denial is a control-plane fact and **not in the log** (ADR-0005 §2: \"by the deciding replica, "
            "unordered\"); it is kept and dropped with its round."], "brown", {}),
        ("H-5 Three things are not holdings", [
            "The correlator's store, \"a cache and never a source\" (ADR-0051 §6, Proposed).",
            "A replica's security log of attempts with no session, which no record places.",
            "The live content store behind a corpus root (ADR-0069 §10.1, Proposed): Build's working store. The root's "
            "promoted manifests are in D."], "grey", {"tint": False}),
        ("H-6 The corpus is a holding (drafter's choice)", [
            "No record says the corpus is archived. A deployment's archive holds the cuts its genesis bundle and "
            "promotions cite. During genesis there is no deployment, and §7 says what holding C is then."],
         "amber", {}),
    ]) + 40

    # ---- §4, §5, §7, §8
    y = band(c, X0, y, "§4 A segment is held before a mark says so · §5 What the archive keeps for the documentation "
             "⟨K10⟩ ⟨K12⟩ · §7 During genesis · §8 The trusted base")
    g = 30
    w4 = (WW - 3 * g) / 4
    xs = [X0 + i * (w4 + g) for i in range(4)]
    b = [stack(c, xs[0], y, w4, [
        ("§4 The mark, item by item", [
            "**A-1** Held: bytes in the locked store in every declared fault domain, each copy hashing to the root.",
            "**A-2** The mechanism orders an archive mark naming range and root (drafter's choice). ADR-0063 "
            "(Proposed) orders a watermark the same way and owes \"a record that goes up in segments with a "
            "receipt\": the mark is that receipt.",
            "**A-3** No replica discards an entry above the newest mark (drafter's choice). ADR-0045 §6 leaves "
            "compaction inside the verified object and no record decides when it may run.",
            "**A-4** Checked, not believed: proposed only for a root the replica recomputed; a wrong root is refused.",
            "**A-5** An unmarked log grows: storage and, at the limit, availability; never an entry.",
            "**A-6** The marks are facts, in holding A, in the next segment.",
            "**A-7** Kinds: held here; erased and disposed are ADR-0075's and record the archive's report, which "
            "A-4 cannot reach. A false one is T-0045-7's residual with a mark that claims otherwise; ADR-0076 §5's "
            "audit looks for it."], "violet", {}),
    ]), stack(c, xs[1], y, w4, [
        ("§5 For the documentation", [
            "**C-1** Every cut is kept whole and verifies as cut: a manifest is checked \"against the tree it "
            "measured, not against today's\" (`manifests/README.md`), with no carrier.",
            "**C-2** Every revision of a file is reachable: by digest, by path in a cut, and across cuts as the "
            "sequence of digests one path has had.",
            "**C-3** A cut is never preferred for being newer; which checkpoint is the state of record is the "
            "corpus's statement (`checkpoints/README.md`), kept in the cut that makes it.",
            "**C-4** The documentation service reads holding C and nothing else (ADR-0072 §1 P-1). Its store can be "
            "rebuilt from C; C is rebuilt from nothing.",
            "**C-5** What a manifest excludes is not kept by it: `manifests/EXCLUDE` leaves the two guides, the "
            "diagrams and the READMEs unmeasured; a documentation release (ADR-0071 §8) measures the unit files."],
         "blue", {}),
    ]), stack(c, xs[2], y, w4, [
        ("§7 During genesis (drafter's recommendation)", [
            "No log, no round, no deployment: holdings A, B and D are empty at every site but the reference's tests.",
            "**Holding C can exist now**: an archive of the corpus's cuts, fed by manifest, under the custodian's "
            "custody (1, 0). It would make G1 to G11 readable as cut without a carrier and be the first thing the "
            "documentation service projects.",
            "Its trust is T-0045-11's and no better: one person cuts the manifests it is fed.",
            "[[red|Not built.]] The record names G1 to G11; G12 was cut 2026.11.16, the same day."], "amber",
         {"status": "notbuilt"}),
        ("§3 F-5, F-8: capture and idempotence", [
            "Which units are captured is declared per use case (ADR-0003 0003.4); at the archetype every unit "
            "(drafter's choice: ADR-0028's \"maximum projection\"; ADR-0037 §3 retains raw emission). Running a "
            "feeder twice writes nothing the second time."], "amber", {}),
    ]), stack(c, xs[3], y, w4, [
        ("§8 The trusted base: T-0045-7 stays delegated", [
            "Three things are new and none is a row: **the feeders** read and copy, and A-4 and F-7 make a failure "
            "visible; **the mark** is ordered by the mechanism on its own recomputation, so the archive's word is not "
            "taken; **holding C's feeder** stands behind T-0045-11 and adds nothing.",
            "ADR-0076 Annex B proposes that T-0045-7 become two rows, since the archive and the plaintext store have "
            "opposite duties."], "teal", {}),
        ("Status note, C2 and C4", [
            "On ratification and building the set would discharge ADR-0034's debt against \"archive and plaintext "
            "store (evidence retention, §3)\", give T-0045-7 the content ADR-0045 lists it as lacking, and answer "
            "part of ADR-0029's open item on the corpus manifest. **Nothing here is modelled, checked or built.**"],
         "grey", {"tint": False}),
    ])]
    y = max(b) + 40

    # ---- §6 OAIS and §9 degeneracies
    y = band(c, X0, y, "§6 The archive in OAIS's terms (ISO 14721:2025; informative, no conformance claimed) · §9 "
             "Degeneracy on this record")
    wl = 1500
    wr = WW - wl - 40
    xr = X0 + wl + 40
    t1 = c.table(X0, y, [("OAIS", 460, {"bold": True}), ("Here", wl - 460)], [
        ["Producer", "The log, the transport, the repository. Never a person"],
        ["Submission package", "A range of log entries, a sealed topic, a tree at a manifest, an object by digest"],
        ["Ingest", "The feeders (§3) and the mark (§4)"],
        ["Archival package", "A segment with its root; a unit with its header; a cut with its manifest; an object with "
                             "its digest"],
        ["Preservation description: provenance, fixity, reference, context, access rights",
         "The source position (§1 K-1); digests and roots (ADR-0076 §5); ids; chain, epoch, round and fence; reader "
         "sets (ADR-0076 §7)"],
        ["Archival storage, data management", "ADR-0076 §2 to §4"],
        ["Administration, preservation planning", "The schedule (ADR-0075 §1); fixity and format (ADR-0076 §5)"],
        ["Access; dissemination package", "The read interfaces and the export (ADR-0076 §7, §8)"],
        ["Designated community", "The audit authority (ADR-0028 §3), and the readers ADR-0071 §2 lists"],
    ], size=13.5, accent="grey")
    cols = [("ID", 130, {"bold": True}), ("Axis", 200), ("Value", 330), ("Theorems voided", 380)]
    cols.append(("Declared consequence", wr - sum(cl[1] for cl in cols)))
    t2 = c.table(xr, y, cols, [
        ["D-0074-1", "Capture → partial", "Some use cases' units are not captured", "None. No theorem reads a unit",
         "After a topic's own retention ends, nothing holds its payload. ADR-0037's D-0037-2 is the instance for raw "
         "emission"],
        {"cells": ["D-0074-2", "Mark → absent", "Segments are archived and no mark is ordered",
                   "§4 A-3, and every property of ADR-0076 §5 that reads a mark",
                   "A compacted log's entries stand on the archive's word alone, or the log is never compacted. **This "
                   "is the reference's position**, with nothing compacted"], "accent": "red"},
        {"cells": ["D-0074-3", "Corpus → not held", "Holding C is omitted", "None",
                   "The corpus is where a carrier has it. ADR-0072's service projects a repository, not a record. "
                   "**This is today's position**"], "accent": "red"},
    ], size=13.5, accent="red")
    y += max(t1, t2) + 40

    # ---- §10 ratification
    y = band(c, X0, y, "§10 Ratification condition, item by item (every item Not met, as the record marks it)")
    y += conditions(c, X0, y, WW, [
        ("**A module states §1 and §4 and its mutations break them** (ADR-0046's method). At least "
         "`ArchiveOriginatesNothing` (`M_FEEDERWRITES`), `MarkedOnlyIfHeld` (`M_EARLYMARK`), `NoDiscardAboveMark` "
         "(`M_COMPACTEARLY`), `MissingIsRecorded` (`M_SILENTSKIP`)", "No module is written"),
        ("**A mechanism record decides the archive mark and the compaction rule** (A-2, A-3)", "None is drafted"),
        ("**The reference shows**: a segment ingested, held and marked; a mark refused for a wrong root; a round unit "
         "captured after its seal with its `after` member; a cut ingested by manifest and one refused for a tree that "
         "does not verify; a cited digest recorded as missing", "Nothing is built"),
        ("**Holding C exists for G1 to G11** (§7), or the custodian decides it waits", ""),
        ("**The dependent entries of ADR-0076 Annex B are drafted**", "None is drafted"),
        ("**ADR-0075 and ADR-0076 are ratified, or this record is ratified with them**", "Both are Proposed"),
        ("**A reader who is not the drafter** (ADR-0029 A2)", ""),
        ("**The custodian's reading of every drafter's choice and recommendation**, the corpus as a holding and the "
         "mark among them", ""),
    ]) + 40

    # ---- options, consequences, open obligations, history
    y = band(c, X0, y, "Options considered, whole · Consequences · Open obligations · History")
    wo = 2100
    wc = WW - wo - 40
    xc = X0 + wo + 40
    t = c.table(X0, y, [("Option", 620, {"bold": True}), ("Disposition", wo - 620)], [
        ["One record for the whole archive", "[[grey|Not taken ⟨K11⟩.]] The request asks for a set. Holdings, lifetime "
         "and storage change for different reasons, which is ADR-0003's own lesson: four of its seven clauses turned "
         "out to be separately supersedable"],
        ["The log as the system of record, kept for ever, and no archive", "[[red|Rejected.]] ADR-0005 §1 is accepted "
         "and names the archive. A log that is never compacted is the reference's position and \"Fine for a baseline, "
         "not for a service\" (`mechanism/` G14)"],
        ["The transport as the record, with long retention", "[[red|Rejected]] by ADR-0005 §1, which names the "
         "transport as \"Not the holder\""],
        ["The archive as a tier of the topic", "[[red|Rejected]] by ADR-0003 A3"],
        ["An archive that accepts writes from principals or operators: notes, annotations, corrections",
         "[[red|Rejected]] (§1). It would originate. A correction to the record is a new fact in the log"],
        ["Facts and units in one holding", "[[red|Rejected.]] ADR-0004 separates them so that one can be destroyed and "
         "the other cannot"],
        ["The mark as the archive's signed receipt, under an archive key", "[[grey|Not taken]] (drafter's choice). "
         "The key would be a trust root for whether evidence exists, with its own issuance and custody. A-4 has the "
         "mechanism recompute, and needs no key"],
        ["No compaction rule here, leaving A-3 to a mechanism record", "[[amber|Open.]] A-3 is stated here because "
         "the archive is not the record without it. The custodian may prefer it in the record that owns the log"],
        ["The corpus not a holding, left to the repository", "[[amber|Open]] (D-0074-3). It is today's position. It "
         "leaves ⟨K10⟩ resting on a carrier"],
        ["Denials in holding A", "[[grey|Not taken.]] They are not in the log, and ordering them there \"contradicts "
         "ADR-0015\" (ADR-0003, A2 note). Whether a denial should outlive its round is a question for ADR-0003 and "
         "ADR-0020 and is not moved here"],
        ["Capture decided by the feeder: sampling, or keeping only rounds with findings", "[[red|Rejected]] (F-9). It "
         "would make a judgment about content decide what evidence exists"],
        ["The correlator's store as a holding", "[[grey|Not taken]] (H-5). ADR-0051 is Proposed and makes it a cache"],
    ], size=13.5, accent="grey")
    bc = stack(c, xc, y, wc, [
        ("Consequences", [
            "[[green|Positive]]: the store five records lean on has a description; \"the record\" has one meaning; the "
            "log can be compacted without losing the record and not before it is safe; the archive cannot be made to "
            "say something happened; the corpus has a home that is not a carrier; a missing piece of evidence is a "
            "recorded fact.",
            "[[red|Negative]]: the mechanism gains a log entry and a constraint on compaction with no module or "
            "record; replicas' storage is coupled to the archive's health (A-5); capturing every unit is large; a "
            "captured unit is a second copy of erasable data; holding C duplicates a repository during genesis; "
            "**denials die with their round**, and ADR-0020 calls them \"the only evidence containment did "
            "anything\"."], "grey", {"tint": False}),
        ("Open obligations", [
            "The mechanism record for the mark and compaction, with its module.",
            "A sequence number on denials (ADR-0005 §6; G9 item 44).",
            "The replica security log, which no record places (H-5).",
            "Whether a denial should survive its round's erasure, as a fact with no payload.",
            "Segment size and cadence: A-5's storage cost against the feeder's lag.",
            "The genesis bundle and corpus manifest format (ADR-0029), which F-6 reads.",
            "The overlay's plane records (ADR-0062, ADR-0063; Proposed), which arrive already in segments.",
            "Narrative: ToO §4 and the glossary owe holding, segment, unit, cut, feeder and archive mark "
            "if ratified."], "red", {"tint": False, "status": "open"}),
        ("History", [
            "**—** Initial draft, 2026.11.16, by the assistant at the custodian's direction, not reviewed.",
            "**R1** Revision before ratification: **renumbered from ADR-0073 to ADR-0074** with its five siblings, "
            "each up by one, because ADR-0070 was taken by a record in flight on another branch (pull request #51) "
            "that the first draft's check of fetched branches missed. No decision text changes. Not reviewed."],
         "grey", {"tint": False}),
    ], gap=18)
    y = max(y + t, bc) + 40
    return y


# ================================================================================================ ADR-0075
def _adr_0075(c, X0, X1, y):
    WW = X1 - X0
    y = band(c, X0, y, "ADR-0075 · Every holding has a line in one retention schedule; facts are never erased; a round "
             "unit is dropped whole; every absence is explained by a fact; a hold may only preserve; a closed chain's "
             "record is still kept", status="proposed", extra="C1, C2, C4 · R2 · drafted 2026.11.16, not reviewed")
    y += c.para(X0, y, WW, "**Context.** The retention rules exist clause by clause in a dozen records and have never been "
                "in one table: F1 to F6 \"non-erasable for the declared horizon\", the chain's lifetime at the "
                "archetype (ADR-0028 §1, §3); Run's topics \"per use case\" (ADR-0003 0003.4); Build's \"for the "
                "production lifetime of any artifact promoted from that round\" (ADR-0021 §7); raw emission the same "
                "(ADR-0037 §3); **no length for anything else**. The records disagree at the edges: T-0045-7 covers "
                "\"The archive and plaintext store\" with one identity, \"object lock or equivalent\", while ADR-0004 "
                "wants plaintext \"built for deletion\"; ADR-0003's Context has both \"nothing ever be removed\" and "
                "erasure \"provably\"; ADR-0006 records an erasure \"in the log it modifies\" while ADR-0003 says hash "
                "chains are never edited; ADR-0028's horizon \"does not survive re-genesis\" and lists HIPAA's six "
                "years as unresolved; CR-11 notes that who exercised authority is personal data. **No record fixes a "
                "retention length in any unit of time, and this one fixes none.** Status note: C1 (§3, §4 put a proof "
                "obligation on erasure), C2 (§1, §4), C4 (ADR-0006's required property stated; ADR-0038 finding 3; "
                "ADR-0028's re-genesis obligation in part); C3: §2's line for facts outside F1 to F6 extends "
                "ADR-0028's horizon, and a reviewer may read that as more than a restatement. **R2 reconciles the "
                "record with ADR-0070 (Proposed, on another branch)** ⟨K13⟩: §8a, HD-3 and DP-4 revised; SC-5, AS-6, "
                "AS-7, ER-8 and D-0075-4 new. Erasure is not implemented and no erasure roster exists (G11).",
                14.5, "muted") + 30

    # ---- §1 the line, and §2 the schedule
    y = band(c, X0, y, "§1 One schedule, a line for every holding ⟨K12⟩: the six fields · §2 The archetype's schedule, "
             "whole")
    wl = 1100
    wr = WW - wl - 40
    xr = X0 + wl + 40
    t1 = c.table(X0, y, [("Field", 200, {"bold": True}), ("Content", wl - 200)], [
        ["Class", "A holding of ADR-0074 §2, or a named part of one"],
        ["Starts", "The event that begins the period. Always a fact in the log or a seal. Never a date someone enters"],
        ["At least", "What the class is kept for whatever anyone asks. Shortening it is the change the line's last "
                     "field names"],
        ["At most", "When the class must be gone, if a limit applies. Empty for a class that is kept without limit"],
        ["Ends by", "never, erasure (§3), period (§5), or both"],
        ["Changed by", "What it takes to shorten at least: a floor relaxation, a declaration, or nothing"],
    ], size=13.5, accent="amber")
    bl = stack(c, X0, y + t1 + 20, wl, [
        ("SC-1 to SC-5", [
            "**SC-1** A period is counted from a fact, in the deployment's clock model (ADR-0032). Where no record "
            "supplies a value the line reads \"the deployment writes this\", and a schedule with such a line unfilled "
            "is incomplete.",
            "**SC-2** At least protects evidence; at most limits exposure. A line may carry both.",
            "**SC-3** Lengthening at least is always allowed: ADR-0028's \"more, never less\".",
            "**SC-4** The schedule is promoted with the declaration; each line states its basis *(drafter's choice; "
            "CR-11 asks for \"a legal-basis line per class\")*.",
            "**SC-5** ⟨R2⟩ A line may say where its class may be held: ADR-0070's B25 practice, \"Residency declared "
            "per data class\". **This record does not become B25's owner.**"], "amber", {}),
    ])
    cols = [("Class", 300, {"bold": True}), ("Starts", 260), ("At least", 520), ("At most", 420), ("Ends by", 200)]
    cols.append(("Changed by", wr - sum(cl[1] for cl in cols)))
    t2 = c.table(xr, y, cols, [
        ["**A-F.** Facts in F1 to F6", "The entry", "The life of the rules-epoch chain, and after it as §6 says",
         "None", "Never", "A floor relaxation: \"an anchor issuance plus a promotion\" (ADR-0028 §2)"],
        ["**A-o.** Every other log entry", "The entry", "As A-F (drafter's choice)", "None", "Never",
         "A declaration (D-0075-1). The entry's hash stays in its segment either way (ADR-0076 §5)"],
        {"cells": ["**B-r.** A Run round unit", "The seal (ADR-0042 §5)",
                   "The topic's own retention, per use case (ADR-0003 0003.4)",
                   "The period the deployment declares for the use case. **The deployment writes this**",
                   "Erasure, or period", "A declaration"], "accent": "brown"},
        {"cells": ["**B-b.** A Build round unit", "The seal of the topic set (ADR-0021 §3)",
                   "\"the production lifetime of any artifact promoted from that round\" (ADR-0021 §7). For a round "
                   "nothing was promoted from, as B-r (drafter's choice)",
                   "The period the deployment declares, counted from the end of that lifetime", "Erasure, or period",
                   "A declaration, never below ADR-0021 §7"], "accent": "brown"},
        ["**B-h.** A unit's header (ADR-0074 §3 F-3)", "The seal", "As A-F", "None", "Never", "As A-o"],
        ["**C.** A cut of the corpus", "The cut", "For as long as any chain's genesis bundle or promotions cite it. "
         "During genesis, without limit", "None", "Never", "Nothing shortens it"],
        ["**D-f.** Evidence a fact cites", "The citing entry", "As long as the citing fact", "None", "Never",
         "As the citing fact's line. A deployment that keeps a large artifact's digest and not its bytes declares it "
         "(D-0075-2)"],
        {"cells": ["**D-r.** A corpus-root object returned from Run (ADR-0069 §4, Proposed)", "Its intake",
                   "\"the production lifetime of any artifact promoted from a round that read it\" (ADR-0069 RR-4)",
                   "—", "Period; erasure under ADR-0069 §5 LR-3 if labelled", "Not in force"], "accent": "grey"},
        ["**E.** The archive's journal", "The entry", "As A-F", "None", "Never", "A declaration"],
    ], size=13.5, accent="amber")
    y = max(bl, y + t2) + 24
    y += row_cards(c, X0, y, WW, 30, [
        ("AS-1 Every log entry is kept (drafter's choice)", [
            "ADR-0028 fixes a horizon for F1 to F6 and the corpus none for the rest. Keeping all is \"The archetype "
            "log remains the maximum projection\" and what replay over \"boundary events only\" (ADR-0020) needs. "
            "⟨R2⟩ Tolerable only because a fact holds little: ADR-0070's B5 practice, \"Minimize by default\"."],
         "amber", {}),
        ("AS-2, AS-3, AS-5", [
            "**AS-2** A unit is never kept for less time than its topic.",
            "**AS-3** A header outlives its unit: ADR-0004's \"hash and a pointer\", and a fact.",
            "**AS-5** Nothing in class C has a limit; a cut holds no payload but does hold names, an open "
            "obligation here as CR-11 is for the floor."], "amber", {}),
        ("AS-4 Evidence follows the fact that cites it", [
            "Attestation evidence is cited by a grant (F1), so kept for the chain's life: the length ADR-0034 left "
            "unstated. ⟨R2⟩ ADR-0070 §3's bill of materials, second-builder evidence and projected provenance, and "
            "§4's stand-up declaration, are each on line D-f; the bill has to be kept for §7.3's advisory-to-"
            "revocation test."], "amber", {}),
        ("AS-6, AS-7 ⟨R2⟩ A production lifetime ends at a fact; a return restarts one", [
            "ADR-0021 §7 does not say what ends a lifetime; ADR-0070 §3 (e) gives every artifact \"A declared end\" "
            "(expiry, revocation or retirement), each an entry. The lifetime ends at the last such entry *(drafter's "
            "choice)*; without ADR-0070, at the entry the declaration names, and a B-b line that names none has no "
            "at most.",
            "\"return is a promotion\" (ADR-0070 §6.7): the round's line is again inside its at least. **If the "
            "unit was disposed of in between, ADR-0021 §7 cannot be met**; the header reads disposed and voters "
            "can read that (ADR-0076 §7 RD-4). A gate on such a return is not decided (Annex B, item 7)."],
         "amber", {}),
    ]) + 40

    # ---- §3, §4, §5, §6, §7
    y = band(c, X0, y, "§3 Erasure in the archive · §4 Every absence is explained · §5 Disposition · §6 A closed chain "
             "· §7 Holds")
    g = 30
    w3 = (WW - 2 * g) / 3
    xs = [X0 + i * (w3 + g) for i in range(3)]
    b = [stack(c, xs[0], y, w3, [
        ("§3 Erasure: restated, then how the event reaches the archive", [
            "**Restated.** Erasure \"is an event — consensus-ordered, modeled in TLA+, recorded in the log it "
            "modifies\" (ADR-0006), a quorum decision on an anchor-issued roster (ADR-0013 §1), by deletion of "
            "sealed topics and plaintext-store entries, crypto-shredding rejected (ADR-0028), the unit \"dropped "
            "whole\" (ADR-0003 A3).",
            "**ER-1** The archive erases on the F6 fact and on nothing else; no operator, administrator or program "
            "has another path, because \"deletion cannot be an out-of-band operator action\" (ADR-0006).",
            "**ER-2** Ordered, then complete, and the difference is visible: the erased mark is ordered when every "
            "copy is gone; between them the erasure is a listable state. **The mark records the archive's report and "
            "proves nothing more.**",
            "**ER-3** Deletion is the mechanism; a destroyed key is at most an addition and **never the evidence**: "
            "ciphertext with no key is \"a hole no auditor can distinguish from suppression\" (ADR-0003).",
            "**ER-4** No copy exists that an erasure cannot reach: no backup of the governed store unless encrypted "
            "under the units' keys and declared (D-0075-3).",
            "**ER-5** Nothing derived from a unit's payload lives outside the unit: an index, extract, embedding or "
            "summary is inside the container or dropped with it (ADR-0019's shadow; ADR-0038 finding 3). ⟨R2⟩ A trace "
            "of admits is facts; a trace that carries bodies is a derivative.",
            "**ER-6** What survives: every fact, the F6 entry among them; the header; the digests the log holds "
            "(ADR-0042 §3). Demand type 5 is not supported (ADR-0013 §5); \"the pointer is itself a disclosure\" "
            "(ADR-0004).",
            "**ER-7** An erasure of a unit not in the archive completes at once, with a mark saying not captured "
            "or disposed.",
            "**ER-8** ⟨R2⟩ A drafting session that reads a unit's body is a copy no erasure reaches, and what it "
            "drafts is a derivative that lands in the corpus, where nothing is erased. **At the archetype no body of "
            "a unit is read into a drafting session** (drafter's choice); facts may be, under ADR-0070 §5.1's "
            "mark (D-0075-4 for a provider that deletes verifiably)."], "red", {"tint": False}),
    ]), stack(c, xs[1], y, w3, [
        ("§4 Every absence is explained: ADR-0006's required property, at the archive", [
            "**AB-1** For every header exactly one holds: the container is in the governed store; an erased mark "
            "cites an F6 entry; a disposed mark cites the schedule line; or the header says not captured. **A "
            "header with none of the four is a finding**: a loss or a suppression, and the archive cannot tell which.",
            "**AB-2** A fact is never lawfully absent: an absent entry under a mark is always a finding. NC-2 "
            "(ADR-0013 §4) held at the archive, over every class of ADR-0028 §1.",
            "**AB-3** Nothing is dropped before its fact; a drop with no entry before it is a finding against the "
            "archive.",
            "**AB-4** An erasure rewrites nothing: the Merkle tree is over facts and no payload is a leaf, which is "
            "how \"recorded in the log it modifies\" and \"never edited\" both hold.",
            "**AB-5** Replay survives erasure: conformance replays admits (ADR-0005 §4). What replay loses with a "
            "unit is its denials (ADR-0074 §2 H-4)."], "blue", {}),
        ("§5 Disposition at the end of a period", [
            "**DP-1** A unit whose at most has ended is dropped whole, under ER-4 and ER-5. **DP-2** Recorded: a "
            "disposed mark naming the unit and the line. **DP-3** By the schedule in force, never by a person's "
            "choice. **DP-5** Only B and D-r are ever disposed of.",
            "**DP-4** A clock that fails must fail towards keeping (drafter's choice): disposition waits for the "
            "entry that says the period ended, and a replica's own clock disposes of nothing. ⟨R2⟩ ADR-0032 §2's rule "
            "turned round: an at most is read as elapsed late, which neither ADR-0032 nor ADR-0070 states; "
            "ADR-0070's B9 leaves its clock cell empty, and this belongs in it. **No trusted clock exists** "
            "(ADR-0045 §6), so an at most in calendar time is a limit a deployment can overrun, **not a guarantee "
            "of deletion by a date**; which clock proposes the entry is open."], "green", {}),
    ]), stack(c, xs[2], y, w3, [
        ("§6 A closed chain: so that the archive is not why the record lapses", [
            "ADR-0028's open obligation: \"The horizon does not survive re-genesis\"; \"Re-genesis (A-0025) starts a "
            "new chain, not a continuation\" (ADR-0027). The migration rule is ADR-0025's to write.",
            "**RG-1** Everything is keyed by chain; a successor never writes under a predecessor's id.",
            "**RG-2** A closed chain's holdings are kept (drafter's choice): each at least runs as if the chain "
            "had continued, down the line of succession; a chain with no successor is kept until a person with the "
            "authority to decide says otherwise, **whom no record names**.",
            "**RG-3** Who reads a closed chain is not decided here: until ADR-0025's rule, the audit authority its own "
            "chain declared, and no one under the successor's authority.",
            "**RG-4** A closed chain has no log to order an erasure in; **until the rule exists its units end by "
            "period only. This is a real gap**: an erasure duty does not lapse because an anchor was lost."],
         "violet", {}),
        ("§7 Holds: the corpus has none, and good practice requires one", [
            "**HD-1** Names units, or a class and a range, and suspends disposition by period. **HD-2** May only "
            "preserve: ends nothing, shortens nothing, gives nobody a reading.",
            "**HD-3** Also refuses erasure, as policy: a deny on the erasure envelope in a promoted bundle, since "
            "\"Bundles may only narrow erasure further\" (ADR-0028 §2). ⟨R2⟩ **Lifting is a promotion. Placing "
            "should not have to wait for a quorum** (drafter's recommendation): on ADR-0070 §1's orientation a hold "
            "subtracts, and ADR-0050 §4 makes the same split, \"adds need a lease and a peer, denies need neither\". "
            "No variant of ADR-0050's alphabet places one; until it gains one (Annex B, item 8) a hold is placed by "
            "promotion, and **an erasure or a disposition can complete while that promotion is voted**. One operator "
            "could delay an owed erasure: attribution, not prevention (HD-4).",
            "**HD-4** On the record, not secret from the audit authority. **HD-5** A regulator's duty to keep is a "
            "line's at least, not a hold."], "brown", {}),
    ])]
    y = max(b) + 40

    # ---- §8 and §9
    y = band(c, X0, y, "§8 Practice this schedule can express (informative; named from the drafter's knowledge, none "
             "read, no compliance claimed) · §9 Degeneracy, and no row added")
    wl = 1560
    wr = WW - wl - 40
    xr = X0 + wl + 40
    t1 = c.table(X0, y, [("A deployment that must", 760, {"bold": True}), ("Uses", wl - 760)], [
        ["Keep records of who did what for a fixed term (for example, HIPAA's six years for required documentation)",
         "At least on A-F, A-o and E (SC-3)"],
        ["Limit how long personal data is kept (for example, GDPR's storage limitation)", "At most on B-r and B-b (§5)"],
        ["Erase a person's data on request (GDPR's erasure)", "§3, on the round units that hold it. **Not on facts.** "
         "What F1 to F6 hold of a person is kept, and the basis for that is the deployment's to state (SC-4)"],
        ["Account for disclosures (HIPAA's accounting of disclosures)", "The journal's read entries (ADR-0076 §7), "
         "kept as class E"],
        ["Preserve material for a dispute or an inquiry", "§7"],
        ["Keep certain records on storage that cannot be rewritten (for example, the SEC's broker-dealer rule)",
         "The locked store (ADR-0076 §2), for A, C, D and E"],
        ["Show that a record is authentic, reliable, intact and usable (ISO 15489's four characteristics)",
         "K-1's source positions (ADR-0074 §1); the roots and fixity audit (ADR-0076 §5); the read interfaces "
         "(ADR-0076 §7)"],
        ["Preserve materials for forensic and regulatory review (NIST AI RMF Playbook, MANAGE 2.4)",
         "ADR-0028, which this schedule carries"],
    ], size=13.5, accent="grey")
    cols = [("ID", 120, {"bold": True}), ("Axis", 260), ("Value", 360), ("Theorems voided", 340)]
    cols.append(("Declared consequence", wr - sum(cl[1] for cl in cols)))
    t2 = c.table(xr, y, cols, [
        ["D-0075-1", "A-o's at least → shorter than the chain", "Entries outside F1 to F6 are dropped after a "
         "declared period", "None of ADR-0028's. Replay over the dropped range", "Conformance cannot be replayed over "
         "that range. The entries' hashes stay, so the classes that remain still verify"],
        ["D-0075-2", "D-f → digest only", "A large artifact's bytes are not kept", "None", "A fact cites an object "
         "nobody can produce. A promoted Persona's weights are the likely case"],
        ["D-0075-3", "ER-4 → a backup deletion cannot reach", "Offline copies of units, encrypted under their keys",
         "§3 ER-2 for those copies", "An erasure is complete for the store and rests on key destruction for the "
         "backup, which ADR-0003 calls \"a hole no auditor can distinguish from suppression\""],
        ["⟨R2⟩ D-0075-4", "ER-8 → a session reads bodies", "A drafting session, or any processor outside ADR-0076 "
         "§1's stores, is given a unit's payload", "§3 ER-2 and ER-4, for that copy", "An erasure is complete for the "
         "stores and cannot be verified for the provider. What the session drafted from the payload is in the corpus, "
         "where nothing is erased"],
        {"cells": ["—", "F1 to F6's horizon → shorter", "—", "—", "Not this record's. It is ADR-0028 §3's legibility "
                   "degeneracy, and a floor relaxation"], "accent": "grey"},
    ], size=13.5, accent="red")
    ty = y + t2 + 16
    th = c.para(xr, ty, wr, "**No row is added by this record.** The executor that drops a unit acts inside the governed "
                "store's row (ADR-0076 §9), a hold is a deny carried today in a promoted bundle (HD-3), and the "
                "schedule is part of the declaration.", 13.5, "muted")
    y = max(y + t1, ty + th) + 40

    # ---- §8a
    y = band(c, X0, y, "§8a The retention boundary in ADR-0070's terms ⟨R2⟩ ⟨K13⟩: B9 made six crossings (drafter's "
             "choice; the ids are placeholders, numbering is ADR-0070's), whole")
    cols = [("", 70, {"bold": True}), ("Crossing", 150, {"bold": True}), ("Sides, and what crosses", 360),
            ("Instant: predicate; evidence", 560), ("Interval of untruth", 400), ("If the check cannot run", 420),
            ("Adversary", 560)]
    cols.append(("Owner", WW - sum(cl[1] for cl in cols)))
    y += c.table(X0, y, cols, [
        ["B9-a", "Capture", "Transport → governed store. A sealed unit, whole", "The seal. The unit's emissions match "
         "the admits the log holds for the round (ADR-0076 §5 IN-5); the header and a journal entry", "Seal to "
         "capture, while the round's payload is only on its topic", "The topic ends on its own schedule and the "
         "header reads not captured (ADR-0074 §3 F-4)", "A principal shaping its own record, which ADR-0070 names "
         "TM1, within what IN-5 cannot reach; loss on the transport", "ADR-0074 §3"],
        ["B9-b", "Erasure", "Governed store → nothing. A unit's container", "The F6 entry. The floor's erasure entry "
         "held, on a roster's quorum, and the unit is in no forensic class (ADR-0006; ADR-0013; ADR-0028 §2); the "
         "entry, and then the erased mark", "F6 to the erased mark, and then the purge interval (ADR-0076 §3 "
         "GS-3)", "The erasure stands as ordered and not complete, and is listed (ER-2)", "ADR-0006's: \"a rogue agent "
         "or hostile insider\" who \"covers tracks\". A store that reports a drop it did not make. A reader who copied "
         "first (ER-4, ER-8)", "ADR-0006 and ADR-0013 for the act; §3 for the archive"],
        ["B9-c", "Disposition", "Governed store → nothing. A unit whose at most has ended", "The entry that says the "
         "period ended. The schedule line is in force and no hold names the unit; the entry, and then the disposed "
         "mark", "The period's end to the mark", "The unit is kept (DP-4)", "A fast clock. Anyone who wants evidence "
         "gone early", "§5"],
        {"cells": ["B9-d", "Hold", "Nothing crosses. An erasure and a disposition are refused", "Placing: an operator's "
                   "deny, or a promotion until one exists. Lifting: a promotion (HD-3). The deny is in the bundle in "
                   "force; a signed action, or the votes", "Placing by promotion: the promotion's latency, in which "
                   "B9-b or B9-c can complete", "There is no hold, and erasure and disposition proceed", "Someone "
                   "racing a hold with an erasure. Someone holding to delay an erasure that is owed", "§7; ADR-0050 "
                   "for the deny, owed"], "accent": "red"},
        {"cells": ["B9-e", "A chain closes", "A live chain's holdings → a closed chain's", "The successor's genesis. "
                   "**None is defined** for who may then read or erase", "From the close until ADR-0025's migration "
                   "rule sets readers", "The closed chain is read only by the audit authority it declared, and its "
                   "units end by period only (RG-3, RG-4)", "A captured anchor that wants its predecessor's record "
                   "read, or gone", "ADR-0025, owed; §6 for what the archive does"], "accent": "red"},
        ["B9-f", "Shortening a line", "A longer at least → a shorter one", "For F1 to F6, an issuance and a "
         "promotion (ADR-0028 §2). For other lines, the promotion of the declaration (SC-4). The schedule in force; "
         "the votes", "None, if no drop precedes the entry (AB-3)", "The longer line stands", "Whoever would have "
         "less kept", "ADR-0028 §2; §1"],
    ], size=13.5, accent="violet") + 20
    y += row_cards(c, X0, y, WW, 30, [
        ("RB-1 Four instants only on paper, two that do not do the job", [
            "B9-b's and B9-f's instants are accepted records' and nothing implements them: no roster, erasure not "
            "built (G11). B9-a's and B9-c's are Proposed. **B9-e has no instant, and B9-d's is too slow to stop "
            "what it is for**: by ADR-0070 §1, \"A boundary with no instant is not a control. It is a finding\", "
            "until ADR-0025 and ADR-0050 are amended."], "red", {"tint": False}),
        ("RB-2 The orientation holds on a second axis", [
            "ADR-0070 §1 orients by \"authority, reach or trust\"; destroying evidence subtracts none, so read alone "
            "it would make erasure local. ADR-0006 forbids that. The record's own direction is ADR-0028's: **towards "
            "less record a quorum, an issuance or a promotion decides; towards more, it is local.** B9-b, B9-c, B9-f "
            "and lifting a hold go towards less; B9-a and placing a hold towards more."], "violet", {}),
        ("RB-3 Disposition is decided when the schedule is promoted", [
            "No quorum meets to dispose of a unit: the promotion was the decision (SC-4, DP-3), the entry that ends "
            "a period carries it out. ADR-0070 §6.5: \"An advance adds nothing the vote did not.\""], "green", {}),
        ("RB-4 Being read is an adversary here too", [
            "ADR-0070 §1 counts \"an adversary to what crosses being read\". For B9-b that is the reader who copied "
            "before the drop: ER-4 and ER-8 address it, and an export does not (ADR-0076 §8 EX-3)."], "pink", {}),
    ]) + 40

    # ---- §10 ratification
    y = band(c, X0, y, "§10 Ratification condition, item by item (every item Not met, as the record marks it)")
    y += conditions(c, X0, y, WW, [
        ("**A module states §3 to §7 and its mutations break them.** At least `AbsenceExplained` (`M_SILENTDROP`), "
         "`FactsSurviveErasure` over all six classes (`M_ERASEFACT`), `NoDropBeforeFact` (`M_EARLYDROP`), "
         "`ErasureReachesEveryCopy` (`M_STRAYCOPY`), `NoShadow` (`M_INDEXEDBODY`), `HoldOnlyPreserves` "
         "(`M_HOLDDROPS`), `ClosedChainKept` (`M_LAPSEATREGENESIS`)", "No module is written"),
        ("**`spec/NonComposition_A1.tla`'s NC-2 is restated over the archive**, or a note says why ADR-0013's module "
         "already covers AB-2", ""),
        ("**The floor carries the hold as a narrowing of erasure** (HD-3): a bundle-tier deny on the erasure "
         "envelope, with a gate case showing it cannot widen", "No entry is written"),
        ("⟨R2⟩ **ADR-0050's alphabet has a deny that places a hold** (HD-3; Annex B, item 8), or the custodian "
         "decides a hold stays a promotion both ways", "No amendment is drafted"),
        ("⟨R2⟩ **ADR-0070's row B9 is reconciled with §8a** (Annex B, item 7), by an R-revision of that record; if "
         "ADR-0070 is withdrawn or narrowed, §8a stands on the accepted records it cites",
         "ADR-0070 is Proposed on another branch, and nothing in it has changed"),
        ("⟨R2⟩ **The clock that ends an at most is decided** (DP-4)", ""),
        ("**The reference shows** an erasure ordered, a unit dropped in every domain and the erased mark; an erasure "
         "left incomplete and listed; a disposition at a period's end with its mark; a hold refusing both; a header "
         "with no explanation reported as a finding", "Erasure is not implemented, and no roster exists"),
        ("**A deployment declaration carries a schedule under §1**, every line filled or marked",
         "No declaration template exists (ADR-0045, Open obligations)"),
        ("**ADR-0025's migration rule exists**, or §6's two gaps are carried on this record's face at ratification",
         "They are carried: RG-3 and RG-4"),
        ("**The dependent entries of Annex B are drafted**", "None is drafted"),
        ("**ADR-0074 and ADR-0076 are ratified, or this record is ratified with them**", "Both are Proposed"),
        ("**A reader who is not the drafter** (ADR-0029 A2)", ""),
        ("**The custodian's reading of every drafter's choice and recommendation**", ""),
    ], accent="amber") + 40
    return _adr_0075_tail(c, X0, X1, y)


def _adr_0075_tail(c, X0, X1, y):
    WW = X1 - X0
    # ---- options, consequences, open obligations
    y = band(c, X0, y, "Options considered, whole · Consequences · Open obligations")
    wo = 2150
    wc = WW - wo - 40
    xc = X0 + wo + 40
    t = c.table(X0, y, [("Option", 640, {"bold": True}), ("Disposition", wo - 640)], [
        ["Fixed lengths in the record: seven years, ten years", "[[red|Rejected.]] No record fixes one, the right number "
         "is a jurisdiction's and a use's, and ADR-0028 already makes the archetype's horizon a lifetime and not a "
         "term"],
        ["Only F1 to F6 kept for the chain's life, other entries on a shorter line", "[[grey|Not taken]] at the "
         "archetype (AS-1). It is D-0075-1, for a deployment to declare. F1 is the high-volume class anyway "
         "(ADR-0028), so the saving is smaller than it looks"],
        ["Crypto-shredding as the erasure", "[[red|Rejected]] by ADR-0028 and ADR-0021 §7, restated. Kept as an "
         "addition (ER-3)"],
        ["Erasure by an administrator's command at the store", "[[red|Rejected]] by ADR-0006: \"exactly the "
         "capability to rewrite history\""],
        ["Tombstones in the fact log", "[[grey|Not needed.]] The F6 entry is the record of an erasure, and ADR-0003 "
         "rejects tombstones for breaking \"gapless ordering\""],
        ["A unit's header erased with it, to support demand type 5", "[[red|Rejected]] by ADR-0013 §5, restated"],
        ["Row-level erasure inside a unit: one subject's lines removed from a round", "[[red|Rejected.]] The unit is "
         "\"dropped whole\" (ADR-0003 A3). ADR-0056 (Proposed) keeps one subject to a round for this reason"],
        ["Disposition on a replica's clock", "[[red|Rejected]] (DP-4). A fast clock would destroy evidence"],
        ["A hold as an operator's action, a seventh variant in ADR-0050's alphabet", "[[grey|Struck at R2:]] Not taken *(drafter's "
         "choice)*: quicker than a promotion, but it would let one operator and a peer block an erasure a roster had "
         "authority to order, and needs a change to a provisional record. ⟨R2⟩ [[amber|Recommended for placing a "
         "hold, and owed to ADR-0050]] (HD-3). On ADR-0070 §1's orientation that is a deny, which the pattern lets "
         "an operator make alone and holds them to account for. Lifting stays a promotion"],
        ["⟨R2⟩ A hold placed and lifted by promotion, as first drafted", "[[grey|Withdrawn as the end state.]] It "
         "stands as the interim, since no operator's deny exists"],
        ["⟨R2⟩ Reading ADR-0070's orientation as covering the record, so that erasure and disposition need no quorum",
         "[[red|Rejected]] (RB-2), by ADR-0006. The orientation is about authority"],
        ["⟨R2⟩ Marking a session that has read a unit's body, as ADR-0070 §5.1 marks one", "[[grey|Not enough here]] "
         "(ER-8). A mark does not recall what a provider holds"],
        ["⟨R2⟩ A retention period on trusted time", "[[grey|Not available.]] ADR-0045 §6 refuses trusted time (DP-4)"],
        ["⟨R2⟩ This record as the owner of B9 in ADR-0070's inventory, and of B25", "B9: for B9-a, B9-c and B9-d, if "
         "both records are ratified. B25: no (SC-5). Residency reaches past the archive"],
        ["A hold that does not refuse erasure, only disposition", "[[grey|Not taken.]] A preserved unit that a roster "
         "can still erase is not preserved"],
        ["Decide here who reads a closed chain", "[[grey|Not taken]] (RG-3). It is ADR-0025's, and it turns on what a "
         "successor anchor may inherit"],
        ["A closed chain's holdings dropped at re-genesis", "[[red|Rejected]] (RG-2). \"the authority record lapses "
         "exactly when it matters most\" is ADR-0025's own description of that outcome"],
        ["A named profile for each regulation", "[[red|Rejected]] by ADR-0023, restated (§8)"],
    ], size=13.5, accent="grey")
    bc = stack(c, xc, y, wc, [
        ("Consequences", [
            "[[green|Positive]]: every kept thing has a line, and the lines the corpus never wrote are marked as the "
            "deployment's; the lock and the delete stop contradicting each other; a missing payload reads as erased, "
            "disposed of, never captured, or lost, and the last is a finding; an unfinished erasure is visible; a "
            "retention duty and an erasure duty are both expressible; re-genesis no longer ends the record by "
            "default; ⟨R2⟩ the boundary is declared in ADR-0070's seven terms and its two weak crossings named.",
            "[[red|Negative]]: everything in the log is kept for the chain's life, the largest possible choice; **a "
            "person's name in a fact is kept, and no erasure reaches it**; ⟨R2⟩ until ADR-0050 gains a deny a hold is "
            "as slow as a promotion and an erasure can beat it; ⟨R2⟩ a drafting session gets what the log says of a "
            "round and not what the round said; ⟨R2⟩ an at most is not a deletion date; a closed chain's units "
            "cannot be erased until ADR-0025 says who may; no offline backup of payload; disposition waits on the "
            "log; the schedule has lines no one can fill from the corpus."], "grey", {"tint": False}),
        ("Open obligations", [
            "The migration rule (ADR-0025), for RG-3 and RG-4.",
            "Personal data in facts, headers and cuts (CR-11; ADR-0056's open question): whether a name could be "
            "replaced by a reference an erasure can sever is not asked here.",
            "Who may ask for an erasure, and what the roster is shown: no record names the requester.",
            "What the disposed and erased marks cost the log, at one entry per unit.",
            "⟨R2⟩ The operator's deny that places a hold (Annex B, item 8). ⟨R2⟩ The clock that ends an at most. "
            "⟨R2⟩ A gate on a return to an artifact whose unit is gone (AS-7). ⟨R2⟩ A provider's deletion a "
            "deployment can verify (ER-8). ⟨R2⟩ Tenancy: ADR-0070's B24 has no owner and the archive has nothing per "
            "tenant.",
            "F1's volume in the cost model, which AS-1 enlarges. The purge interval of the governed store. The "
            "findings of Annex A, each another record's to correct.",
            "Narrative: ToO §4.3, §4.4 and the glossary owe schedule, disposition, hold and closed chain if "
            "ratified."], "red", {"tint": False, "status": "open"}),
    ], gap=18)
    y = max(y + t, bc) + 40

    # ---- Annex A
    y = band(c, X0, y, "Annex A · The retention, erasure and archive clauses in force, and where this set puts each, "
             "whole (Restated = cited unchanged; a Proposed clause binds nothing)")
    cols = [("Clause", 420, {"bold": True}), ("Says", 900), ("State", 260)]
    cols.append(("Here", WW - sum(cl[1] for cl in cols)))
    rows = [
        ["ADR-0003 0003.1, 0003.2", "A topic per principal per round, sealed on emit completion", "Accepted",
         "Restated: the unit (ADR-0074 §2 B)"],
        ["ADR-0003 A1", "A topic is identified by its chain", "Accepted", "Restated, and extended to every holding (§6 "
         "RG-1)"],
        ["ADR-0003 A2", "The `after` companion is in the round's unit of erasure", "Accepted (C1)", "Restated: a "
         "unit's second member (ADR-0074 §3 F-2)"],
        ["ADR-0003 0003.3; \"Separate read-only principals for audit\"", "Access by ACL", "Accepted", "Restated "
         "(ADR-0076 §7)"],
        ["ADR-0003 0003.4", "Retention per use case", "Accepted", "Restated: lines B-r, B-b. No value supplied"],
        ["ADR-0003 0003.5", "Replay authorized or refused", "Accepted", "Not moved. ADR-0076 §7 records a replay's "
         "reads"],
        ["ADR-0003 0003.6", "Masking at write time", "Accepted", "Restated: the feeder does not mask (ADR-0074 §3 F-9)"],
        ["ADR-0003 0003.7, A3", "No tiered storage; the archive is a separate store, not a tier, and \"neither extends "
         "a topic's life nor survives its erasure\"", "Accepted", "Restated (ADR-0074 §3 F-4; §3 ER-1; ADR-0076 §3)"],
        ["ADR-0004", "Hash and pointer in the record; plaintext in a governed store built for deletion", "Accepted",
         "Restated: header and unit (ADR-0074 §3 F-3; ADR-0076 §3)"],
        ["ADR-0004, residuals", "The pointer is a disclosure; the plaintext store's readers", "Accepted", "First "
         "restated (ER-6). Second open (ADR-0076, Open obligations)"],
        ["ADR-0005 §1", "The archive is the system of record", "Accepted (C4)", "Restated (ADR-0074 §1)"],
        ["ADR-0005 §5", "\"The archive does not exist at the reference\"", "Accepted", "Still true"],
        ["ADR-0006", "Erasure is consensus-ordered, modelled, recorded; never out of band", "Accepted (C1, C4)",
         "Restated (§3). Its owed property stated (§4)"],
        ["ADR-0013 §4 NC-1, NC-2", "No composition of break-glass and erasure removes a forensic record",
         "Accepted (C1, C4)", "Restated, and held at the archive (AB-2)"],
        ["ADR-0013 §5", "Demand type 5 unsupported", "Accepted", "Restated (ER-6)"],
        ["ADR-0019", "Logprobs not in round topics; their storage is an ADR-0006 decision", "Accepted", "Restated: if "
         "stored, inside the unit (ER-5)"],
        ["ADR-0020", "Replay is over boundary events; denials are part of the record", "Accepted", "Restated (AS-1, "
         "AB-5). Denials die with the unit (ADR-0074 §2 H-4)"],
        ["ADR-0021 §7", "Build topics kept for the promoted artifact's production lifetime", "Accepted (C4)",
         "Restated: line B-b"],
        ["ADR-0024 §8", "Votes are facts, outside erasure; commentary is payload", "Accepted", "Restated: A-F, and B"],
        ["ADR-0028 §1", "F1 to F6 non-erasable for the horizon", "Accepted (C1)", "Restated: line A-F"],
        ["ADR-0028 §2", "Classes are floor denials; bundles may only narrow erasure", "Accepted", "Restated, and used "
         "for holds (HD-3)"],
        ["ADR-0028 §3", "Horizon is the chain's life; audit authority declared", "Accepted", "Restated. Its lapse at "
         "re-genesis answered in part (§6)"],
        ["ADR-0028 §4", "Compartmentation is not erasure", "Accepted", "Restated (ADR-0076 §7)"],
        ["ADR-0029 §5", "The corpus manifest is in the genesis bundle; no erasure roster at genesis", "Accepted",
         "Restated: line C; §10"],
        ["ADR-0034 §3", "The appraisal is kept beside the lease; evidence bytes \"belong in the archive\"",
         "Accepted (C2, C4)", "Placed: holding D, line D-f (AS-4). Nothing is built"],
        ["ADR-0037 §3", "Raw emission kept at the archetype, in the round's unit", "Accepted (C3, C4)", "Restated: in "
         "B, every unit captured (ADR-0074 §3 F-5)"],
        ["ADR-0038, finding 3", "The correlator's store \"crosses erasure units\"", "Accepted (a finding)", "Answered "
         "for the archive (ER-5). The correlator's own store is ADR-0051's"],
        ["ADR-0042 §3, §5", "The `Actuate` record is in the unit; its digests survive", "Accepted", "Restated (ER-6)"],
        ["ADR-0045 T-0045-7", "Delegated, \"with object lock or equivalent\"", "Accepted (C2, C4)", "Kept delegated. "
         "Split proposed (ADR-0076 Annex B)"],
        ["ADR-0052 §5", "The activation is an F5 record", "Accepted, provisional", "Restated: A-F"],
        {"cells": ["ADR-0035", "Lineage records \"belong in the archive\"", "Proposed", "Holding D, if ratified"],
         "accent": "amber"},
        {"cells": ["ADR-0051 §6", "The store \"never outlives its sources\"", "Proposed", "Not a holding (ADR-0074 §2 "
                   "H-5). ER-5 is the same rule for the archive"], "accent": "amber"},
        {"cells": ["ADR-0056 §7", "A digest of the subject's identifier is in the forensic floor", "Proposed", "A-F, "
                   "if ratified; an open obligation here"], "accent": "amber"},
        {"cells": ["ADR-0069 §4 RR-4, §5 LR-3", "Returned objects' retention; erasure follows the data", "Proposed",
                   "Line D-r, if ratified"], "accent": "amber"},
    ]
    y += c.table(X0, y, cols, rows, size=13.5, accent="blue") + 24
    g = 40
    w2 = (WW - g) / 2
    b1 = stack(c, X0, y, w2, [
        ("Findings against other records, not changed here (the inventory's, not re-derived); each is against B9 "
         "and the first record named is its owner; no register row is written", [
            "**1.** ADR-0069 §4 (Proposed) lists \"`Actuate` records, by digest\" and \"Observer and correlator "
            "findings\" among things \"None of these is erasable\"; ADR-0028 §1 has six classes and neither is one, "
            "and ADR-0042 §3 drops the `Actuate` record with its round.",
            "**2.** ADR-0018, ADR-0020 and ADR-0028 still list raw-emission retention as open; ADR-0037 §3 decided it.",
            "**3.** ADR-0028 F5 reads \"Break-glass invocations | ADR-0009\"; ADR-0052 (provisional) makes the "
            "activation the F5 record, and ADR-0028 has no entry for it.",
            "**4.** ADR-0028's bootstrap note says erasure is disabled \"until this record and ADR-0013 are "
            "ratified\", and two paragraphs on that \"Ratifying them does not by itself enable erasure\".",
            "**5.** ADR-0003's History row A3 still reads Pending in its State column, with B17 ratifying it below.",
            "**6.** \"Horizon\" means a chain's lifetime in ADR-0028, \"a count of correlation windows\" in ADR-0051 "
            "(Proposed), and is undefined in ADR-0003 A3's \"Run's horizon\"."], "red", {"tint": False}),
    ])
    b2 = stack(c, X0 + w2 + g, y, w2, [
        ("⟨R2⟩ Findings against ADR-0070, from reading it for R2; reported and not changed; ADR-0070 owns each", [
            "**7.** Its B9 row reads \"In force\". No erasure roster exists, erasure is not implemented, and there is "
            "no archive (G9, G11). Its B1 row has the form that fits: \"In force as specification\".",
            "**8.** B9 has one instant, the seal. Erasure, disposition and a chain's close are crossings of the same "
            "boundary; its Consequences name seven boundaries with no instant and B9 is not among them, though B9-e "
            "has none.",
            "**9.** Its §1 orientation and §9's \"Subtraction needs no quorum\" are written of authority; neither "
            "says that destroying evidence is not that kind of subtraction (RB-2).",
            "**10.** Its §5.1 has a session read \"an intake object, a trace or a Report\" and mark its drafts; a "
            "Report's content is payload, and the mark does nothing for an erasure (ER-8). Against B20, B22, B29.",
            "**11.** Its §8 lets recorded traces into the specification graph as evidence without saying they are "
            "traces of facts (ER-5). Against B22.",
            "**12.** Its §6.7 makes a return a promotion without asking whether the returned artifact's Build round "
            "is still held (AS-7). Against B1.",
            "**13.** Its §2.3 gives B9 no clock; a retention period's failure direction is the opposite of "
            "ADR-0032 §2's for an interval that subtracts authority (DP-4)."], "red", {"tint": False}),
    ])
    y = max(b1, b2) + 40

    # ---- Annex B and History
    y = band(c, X0, y, "Annex B · Dependent entries this record would owe (none drafted; each in its own record, "
             "pending, moving that record's pin) · History")
    wa = 2150
    wh = WW - wa - 40
    t = c.table(X0, y, [("", 50, {"bold": True}), ("Record and kind", 560, {"bold": True}), ("Entry", wa - 610)], [
        ["1", "ADR-0006, Consequences. Amendment (dependent), C4", "The safety property it requires is stated at the "
         "archive by ADR-0075 §4, and is owed a module"],
        ["2", "ADR-0028, Open obligations and Consequences. Amendment (dependent)", "\"The horizon does not survive "
         "re-genesis\": the archive keeps a closed chain's holdings (§6), and the reading rule stays ADR-0025's. "
         "\"HIPAA's six-year retention and disclosure accounting\": expressible by a line's at least and by the "
         "journal (§1 SC-3, §8). Neither is closed by the entry"],
        ["3", "ADR-0038, finding 3. Amendment (dependent)", "Answered for the archive by §3 ER-5"],
        ["4", "ADR-0034, Open obligations. Amendment (dependent), C4", "\"Evidence retention\": holding D, kept as the "
         "citing fact (§2 AS-4). ADR-0034's header debt against the archive stands until the archive is built"],
        ["5", "ADR-0025, Open obligations. Amendment (dependent)", "The migration rule gains two questions from §6: who "
         "sets a closed chain's reader sets, and whether a successor's roster may erase a predecessor's unit"],
        ["6", "ADR-0035 (Proposed). R-revision (dependent on ADR-0075, Proposed)", "\"Lineage retention\": holding D"],
        ["7", "⟨R2⟩ ADR-0070 (Proposed, on branch `ccr-dd716f39-ywh7ud`, pull request #51). R-revision (dependent "
         "on ADR-0075, Proposed). Not this session's to draft on that branch", "It would: give B9 the crossings of "
         "§8a and change B9's state to its B1 form; add B9-e to the boundaries with no instant; say in §1 that the "
         "orientation is of authority and the record's direction is ADR-0028's; limit what §5.1 has a session read "
         "to facts, or have the provider's copy declared; say in §8 that traces taken as evidence are traces of "
         "facts; put the retention clock's direction in §2.3; say in §6.7 what a return owes ADR-0021 §7. Its §10 "
         "rows and T-0045-40 (ADR-0076 Annex B) would both amend ADR-0045 Annex A"],
        ["8", "⟨R2⟩ ADR-0050 §4 (provisional). Amendment (dependent)", "A seventh variant, a deny, that places a hold "
         "on named units, with a deny's requirements under that section. Lifting is not a variant. The record's "
         "floor entries and its module would follow. Drafted only if the custodian takes HD-3's recommendation"],
    ], size=13.5, accent="red")
    bh = stack(c, X0 + wa + 40, y, wh, [
        ("History", [
            "**—** Initial draft, 2026.11.16, by the assistant at the custodian's direction, not reviewed. A hold "
            "then refused erasure \"as a promoted narrowing\"; Annex B listed six entries.",
            "**R1** Revision before ratification: **renumbered from ADR-0074 to ADR-0075** with its five siblings, "
            "since ADR-0070 was taken by a record in flight on another branch. No decision text changes.",
            "**R2** Revision before ratification, 2026.11.16 ⟨K13⟩: **reconciled with ADR-0070 (Proposed), read in "
            "full at `593af40`**. New §8a; HD-3 (placing a hold recommended as an operator's deny, promotion the "
            "interim, lifting a promotion); DP-4 (an at most read as elapsed late, not a deletion date); new ER-8, "
            "SC-5, AS-6, AS-7, D-0075-4; Annex A gains findings 7 to 13 and the owners of 1 to 6; Annex B gains "
            "entries 7 and 8. ADR-0070 is unchanged; ADR-0073 §7 WC-2 inherits a ratchet finding. Not reviewed."],
         "grey", {"tint": False}),
    ])
    return max(y + t, bh) + 40


# ================================================================================================ ADR-0076
def _adr_0076(c, X0, X1, y):
    WW = X1 - X0
    y = band(c, X0, y, "ADR-0076 · The archive is two stores and an index; the log orders the root of every segment; "
             "nothing that decides reads the archive without a proof; every reading is by a declared authority and is "
             "itself kept", status="proposed", extra="C2, C4 · R1 · drafted 2026.11.16, not reviewed")
    y += c.para(X0, y, WW, "**Context.** One row of the trusted base asks one store to do two opposite things: T-0045-7's "
                "identity is \"object lock or equivalent\" and ADR-0004's store is \"built for deletion\"; on the "
                "common object-store interface a bucket with Object Lock must keep versions, and versions keep what a "
                "delete removed. The corpus has asked for integrity without saying of what: ADR-0015's audit chain "
                "ends \"at a named axiom\", ADR-0003 recalls a Merkle root over round envelopes that never reached the "
                "record, ADR-0006 wants lawful erasure told apart from rewriting. **The archive must not become an "
                "authority by being read**: ADR-0035's lineage and ADR-0069's IG-4 (both Proposed) read log positions "
                "that a compacted log leaves in the archive. No record says who reads the archive or how: ADR-0028 "
                "§3's audit authority is \"the anchor plus a declared external auditor role\", and the role is open. "
                "**Status note**: C2 (§6's confinement claim is what keeps T-0045-7 delegated), C4 (§11's modules "
                "would be the first theorems to cite T-0045-7); C1 is ADR-0075's; C3: Annex B's split of T-0045-7 "
                "changes no class. **No product named in §2 to §4 has been run.** Deployment position: Archetype for "
                "§1, §5 to §8 and the requirements of §2 to §4; the products are the reference's choices, "
                "substitutable as ADR-0072 §6 says.", 14.5, "muted") + 30

    # ---- §1 table and P-rules; §5 integrity; §6
    y = band(c, X0, y, "§1 Two stores and an index, the table whole · §5 Integrity · §6 Nothing that decides reads the "
             "archive without a proof")
    wl = 1700
    wr = WW - wl - 40
    xr = X0 + wl + 40
    cols = [("Part", 220, {"bold": True}), ("Holds (ADR-0074 §2)", 440), ("Its duty", 520)]
    cols.append(("Its failure", wl - sum(cl[1] for cl in cols)))
    t1 = c.table(X0, y, cols, [
        {"cells": ["The locked store", "A facts, as segments; C the corpus; D evidence; E the journal",
                   "Keep, unchanged, for each line's at least (ADR-0075 §2)", "Evidence lost or damaged"],
         "accent": "blue"},
        {"cells": ["The governed store", "B round units", "Keep until erasure or period, and then no longer",
                   "A unit lost early. A unit not deleted"], "accent": "brown"},
        {"cells": ["The index", "A projection of both: fields of facts, unit headers, cut manifests", "Answer queries",
                   "Unavailable, or wrong and caught by a proof (§7 RD-7)"], "accent": "grey"},
    ], size=13.5, accent="blue")
    bl = stack(c, X0, y + t1 + 20, wl, [
        ("P-1 to P-3", [
            "**P-1** The two stores share nothing: no bucket, volume, credential or administrator's role. The feeder "
            "of facts holds no right to delete anywhere; the only right to delete in the governed store is the "
            "executor's, on an F6 entry or the end of a period.",
            "**P-2** The index is not the record: dropped and rebuilt from the two stores, the rebuild checked against "
            "the roots (§5), as ADR-0072 §1 P-2 checks its own.",
            "**P-3** Each part's interface is fixed and its product is not: S3 with Object Lock; S3 without it; the "
            "DynamoDB interface ⟨K5⟩."], "blue", {}),
        ("§6 AR-1 to AR-4: the delegated row's test, as a property", [
            "**AR-1** The admit path does not read the archive: true of the reference today, kept true.",
            "**AR-2** A gate, a tally or a tool that needs an entry the log no longer holds takes it only with an "
            "inclusion proof against a mark in the log; without one the entry is absent and the gate fails. Lineage "
            "(ADR-0035 §1) and IG-4 (ADR-0069 §3a), both Proposed, are the first two readers bound.",
            "**AR-3** Absence only subtracts: no rule lets a missing record count as a clean one.",
            "**AR-4** Nothing decides on a unit: a unit is evidence for people and for the Observer's successors in "
            "review, and \"never admits anything\" (ADR-0037 §3).",
            "**So an archive that fails in any way, lying included, produces no admit, promotion or issuance the "
            "mechanism would otherwise refuse**: ADR-0045 §2's test for a delegated row, which §11 asks for as a "
            "property."], "teal", {}),
    ])
    br = stack(c, xr, y, wr, [
        ("§5 Integrity, item by item", [
            "**IN-1** A chain's facts form one Merkle tree in log order, in RFC 9162's form (drafter's choice); a leaf "
            "is the hash of one entry's bytes; the root after a segment covers every entry so far.",
            "**IN-2** The log orders each root: the held mark names range and root, proposed only for a root the "
            "replica recomputed. An auditor has the roots from the log, not from the archive.",
            "**IN-3** Two proofs, both served: inclusion (this entry is a leaf under this root) and consistency "
            "(a later tree extends an earlier one, nothing before changed). ADR-0015's audit chain can be walked from "
            "an effect to the genesis issuance without trusting the store.",
            "**IN-4** An erasure touches no leaf (ADR-0075 §4 AB-4); a deployment keeping fewer entries (D-0075-1) "
            "keeps their leaf hashes, and every proof holds.",
            "**IN-5** A unit is checked against the log as far as the log reaches: every emission carries its admit's "
            "index and sequence number (ADR-0005 §2) and the round \"seals at the final sequence number\" (ADR-0042 "
            "§5); Build's container against the sealed topic-set digest (ADR-0021 §4). **What the log does not reach "
            "is a body's bytes where it holds no digest, and the denials.**",
            "**IN-6** The journal has a tree of its own and each mark carries its root; the mechanism cannot "
            "recompute it and does not vouch for it. Ordering it fixes what the archive said and when.",
            "**IN-7** Fixity is audited on a declared cycle: every locked object rehashed in every domain; a mismatch "
            "repaired from another domain and journalled, one that cannot be is a finding; the same audit reads the "
            "governed store for every unit an erased or disposed mark names, and a container found is a finding. "
            "Each audit writes a dated results file, never edited.",
            "**IN-8** No key of the archive's is trusted for anything; the roots are the log's. An outside witness "
            "or a timestamp authority (RFC 3161) is an addition with a carrier's standing (ADR-0069 §9 C-2): it may "
            "refuse and never admits."], "teal", {}),
    ])
    y = max(bl, br) + 40

    # ---- §7 reading: two tables; §8 export
    y = band(c, X0, y, "§7 Reading ⟨K6⟩ ⟨K10⟩ ⟨K12⟩: RD-1's reader sets and RD-4's operations, whole · §8 Export")
    wl = 1200
    wr = WW - wl - 40
    xr = X0 + wl + 40
    t1 = c.table(X0, y, [("Holding", 140, {"bold": True}), ("Readers (RD-1)", wl - 140)], [
        ["A", "The declared audit authority, always: \"the anchor plus a declared external auditor role\" (ADR-0028 §3). "
              "Others as the deployment declares. A class may be removed from a reader's set, and never from the audit "
              "authority's (ADR-0028 §4)"],
        ["B", "Whoever the round topic's ACL named (ADR-0003 0003.3), carried over to the unit (drafter's choice), and "
              "the \"Separate read-only principals for audit\" of ADR-0003"],
        ["C", "Anyone, for the archetype's corpus, which is published. A deployment's own cuts as it declares"],
        ["D", "As the fact that cites the object"],
        ["E", "The audit authority"],
    ], size=13.5, accent="brown")
    bl = stack(c, X0, y + t1 + 20, wl, [
        ("RD-2, RD-3, RD-5 to RD-9", [
            "**RD-2** Reader sets are policy, in a promoted bundle (drafter's choice); the read service holds no list "
            "of its own. ADR-0028 §4's proviso belongs in the floor: **the genesis draft floor has an erasure entry and a "
            "forensic-classes entry and none about readers.**",
            "**RD-3** GraphQL and REST, generated from one model, equal, read-only (ADR-0072 §7's A-1 to A-4, A-6, A-7 "
            "as written) ⟨K6⟩.",
            "**RD-5** Every past state is read as the newest ⟨K10⟩: a superseded revision, an earlier epoch's rules, a "
            "closed chain, an old cut, by the same operations.",
            "**RD-6** Every read but a read of C is journalled: reader, set, the ask, and a stated purpose nothing "
            "checks. This is the accounting ADR-0028 lists as a requirement its floor \"does not express\".",
            "**RD-7** An answer about a fact carries its inclusion proof and names its mark. **RD-8** A read writes "
            "nothing but its journal entry. **RD-9** How to read the archive is a document, ADR-0071's Ex-3, whose "
            "bindings point at objects in C and D by digest."], "teal", {}),
        ("§8 Export", [
            "**EX-1** Any range a reader may read, as one self-describing package: objects, a manifest of SHA-256 "
            "digests, the marks, the proofs; a BagIt bag (RFC 8493) (drafter's choice).",
            "**EX-2** Verifies with no access to the archive, against a copy of the log's marks obtained separately.",
            "**EX-3** A package of units goes only to a reader of B, is a copy ER-4 does not reach, and is journalled "
            "as such; what the recipient owes an erasure is the deployment's to bind.",
            "**EX-4** A successor chain's audit authority receives a closed chain's facts as a package once ADR-0025's "
            "rule says it may (ADR-0075 §6 RG-3)."], "teal", {}),
    ])
    t2 = c.table(xr, y, [("Operation (RD-4)", 900, {"bold": True}), ("Returns", wr - 900)], [
        ["Facts of a chain by log index range; by principal and round; by forensic class; by rules epoch",
         "Entries, each with its proof (RD-7)"],
        ["Facts that cite a digest", "Every vote on an artifact, every admit under a bundle revision, every grant that "
         "cites an appraisal"],
        ["The marks of a chain; a consistency proof between two", "§5 IN-3"],
        ["A unit's header and state: present, erased, disposed, not captured, held", "For any reader of A"],
        ["A unit's records", "For a reader of B only"],
        ["Erasures ordered and not complete; headers with no explanation", "The two lists ADR-0075 §3 ER-2 and §4 AB-1 "
         "define"],
        ["A cut; a path's digests across cuts; an object by digest", "ADR-0074 §5 C-1, C-2"],
        ["The journal: ingests, fixity results, drops, reads", "For a reader of E"],
        ["An export (§8)", "A package"],
    ], size=13.5, accent="teal")
    y = max(bl, y + t2) + 40

    # ---- §9 trusted base and §10 degeneracy
    y = band(c, X0, y, "§9 The trusted base: T-0045-7 stays delegated, and Annex B proposes it become two rows "
             "(drafter's recommendation) · §10 Degeneracy on this record")
    wl = 1500
    wr = WW - wl - 40
    xr = X0 + wl + 40
    t1 = c.table(X0, y, [("Component", 360, {"bold": True}), ("Class", 300), ("Why", wl - 660)], [
        {"cells": ["The locked store", "delegated (T-0045-7)", "Its failure loses or damages evidence. §6 keeps a "
                   "damaged entry from deciding anything"], "accent": "blue"},
        {"cells": ["The governed store", "delegated (T-0045-40, proposed)", "Its failure loses a unit early, or fails to "
                   "delete one. Neither is an admit, a promotion or an issuance. **The second is a harm to a person and "
                   "is the residual on the row's face**"], "accent": "brown"},
        ["The index, the read service, the feeders, the export", "No row", "Projections and copies. A read service that "
         "shows a class to a reader outside its set is a confidentiality failure. It is stated as a residual on "
         "T-0045-7 and adds no authority"],
        ["The fixity audit", "No row", "It reports. It decides nothing"],
    ], size=13.5, accent="teal")
    cols = [("ID", 120, {"bold": True}), ("Axis", 250), ("Value", 340), ("Theorems voided", 400)]
    cols.append(("Declared consequence", wr - sum(cl[1] for cl in cols)))
    t2 = c.table(xr, y, cols, [
        ["D-0076-1", "Lock → absent", "The locked store is an ordinary store", "None, while §5's roots are kept: "
         "tampering is detected and not prevented", "An administrator can destroy evidence. Its absence is then seen "
         "at the next audit, and not before"],
        ["D-0076-2", "Fault domains → one", "One copy, one administration", "None", "One failure loses the record"],
        {"cells": ["D-0076-3", "Roots → not ordered", "Segments archived with no root in the log", "§5 IN-2, IN-3; §6 "
                   "AR-2; §7 RD-7", "Readers trust the store. Any gate that reads the archive is void, since AR-2 has "
                   "nothing to prove against. **With D-0074-2 this is the reference's position**"], "accent": "red"},
        ["D-0076-4", "Governed store → versioned or locked", "Units in a store that keeps what it deletes", "ADR-0075 "
         "§3 ER-2, §4 AB-1", "An erasure cannot complete. This is what a single shared store produces"],
        ["D-0076-5", "Reads → not journalled", "—", "§7 RD-6", "No accounting of who read what"],
    ], size=13.5, accent="red")
    y += max(t1, t2) + 40

    # ---- §11 ratification
    y = band(c, X0, y, "§11 Ratification condition, item by item (every item Not met, as the record marks it)")
    y += conditions(c, X0, y, WW, [
        ("**A module states §5 and §6 and its mutations break them.** At least `ArchiveCannotAdd` (the archive as a "
         "havoc component that may drop, alter or invent any entry; `M_TRUSTARCHIVE`: a gate accepts an entry with no "
         "proof), `RootsAreTheLogs` (`M_ARCHIVEROOT`), `AuditAuthorityAlwaysReads` (`M_COMPARTOUT`), `ReadsAreKept` "
         "(`M_SILENTREAD`)", "No module is written"),
        ("**The floor carries ADR-0028 §4's proviso** (RD-2): a reader set that drops the audit authority is refused, "
         "with a gate case", "The genesis draft floor has no entry about readers"),
        ("**The external auditor role is defined** (ADR-0028, Open obligations), since RD-1 names it", ""),
        ("**The reference shows**: the two stores apart with no shared credential; an object refused deletion under "
         "lock; a unit dropped and absent from every read; the index dropped and rebuilt to the same answers; an "
         "entry served with a proof that verifies against the log's mark, and an altered entry whose proof fails; a "
         "gate refusing an unproved entry; a read entered in the journal; an export verified offline",
         "Nothing is built"),
        ("**Each product of §2 to §4 has been run under this design**, and its build pinned", "None has been run"),
        ("**A fixity audit has run and written its results file**", ""),
        ("**The dependent entries of Annex B are drafted**, and ADR-0045's pin moved", "None is drafted"),
        ("**ADR-0074 and ADR-0075 are ratified, or this record is ratified with them**", "Both are Proposed"),
        ("**A reader who is not the drafter** (ADR-0029 A2)", ""),
        ("**The custodian's reading of every drafter's choice and recommendation**, the products of §2 to §4 among "
         "them", ""),
    ], accent="teal") + 40
    return _adr_0076_tail(c, X0, X1, y)


def _adr_0076_tail(c, X0, X1, y):
    WW = X1 - X0
    # ---- options: three tables
    y = band(c, X0, y, "Options considered, whole: the stores (licences and features as learned by search on "
             "2026.11.16, none verified against a running system), integrity, reading")
    g = 40
    w2 = (WW - g) / 2
    xr = X0 + w2 + g
    t1 = c.table(X0, y, [("The stores: option", 560, {"bold": True}), ("Disposition", w2 - 560)], [
        {"cells": ["Ceph object gateway (LGPL): the interface with Object Lock, set at a bucket's creation",
                   "[[teal|Recommended for both stores]], as two deployments (§2 LS-5, §3 GS-6). Heavy to run"],
         "accent": "teal"},
        ["SeaweedFS (Apache-2.0): its wiki claims Object Lock, retention and legal hold", "[[grey|Not taken]] as the "
         "reference: the claim was read on a mirror of the wiki and not tested. The lighter candidate, and the first "
         "substitution to try"],
        ["MinIO (AGPL)", "[[grey|Not taken.]] Its community edition is reported to be in maintenance mode, with no new "
         "features accepted"],
        ["Garage (AGPL)", "[[grey|Not taken.]] Whether it supports Object Lock was not confirmed. A candidate for the "
         "governed store, which needs none"],
        ["Apache Ozone (Apache-2.0)", "[[grey|Not taken.]] Built for analytic workloads; its lock support was not looked "
         "up"],
        ["A filesystem with immutable snapshots and holds (ZFS, for example)", "[[grey|Not taken]] as the reference. A "
         "real equivalent under LS-2's \"or what a deployment declares\", with no interface another product could "
         "stand behind"],
        ["Write-once media: tape or optical", "Admissible for the locked store as a fault domain. Wrong for the "
         "governed store, which must delete"],
        ["A managed object service with Object Lock", "A substitution a deployment may declare, as ADR-0072 §6 allows "
         "for the index"],
        ["One store for everything, with a prefix for units", "[[red|Rejected]] (D-0076-4). The lock needs versions, "
         "and versions defeat the delete"],
        ["The transport with long retention as the archive", "[[red|Rejected]] by ADR-0005 §1 and ADR-0003 A3"],
        ["A relational database as the archive", "[[red|Rejected]] for the stores. Rows can be changed by whoever "
         "administers it, and deletion leaves the bytes in its log and its backups. PostgreSQL does sit under the "
         "index, where neither matters"],
        ["Apache Accumulo for the index, for its cell-level visibility labels", "[[grey|Not taken ⟨K5⟩.]] Its labels "
         "would put compartmentation (RD-1) in the store itself, which is attractive. It is not the DynamoDB "
         "interface, and reader sets are policy here (RD-2)"],
        ["The index's engine for the stores as well", "[[red|Rejected]] (IX-4). An engine that declares itself unfit "
         "for production may hold a projection and not a record"],
    ], size=13.5, accent="grey")
    t2 = c.table(xr, y, [("Integrity: option", 560, {"bold": True}), ("Disposition", w2 - 560)], [
        ["A hash chain, each segment naming the one before", "[[grey|Not taken.]] It shows that history was not "
         "rewritten only to someone who reads all of it. A tree gives a short proof for one entry"],
        ["A transparency-log service (Trillian or its successor) as the tree", "[[amber|Open.]] IN-1 fixes the form "
         "and not the program. A pinned library may well be the implementation"],
        ["The archive signs its roots", "[[red|Rejected]] (IN-8). The key would be a trust root for whether evidence "
         "exists. The log already orders the roots"],
        ["A public ledger or an outside timestamp as the anchor", "[[grey|Not taken]] as the anchor. Admissible as an "
         "addition (IN-8)"],
        ["A ledger database", "[[grey|Not taken.]] The ones the drafter knows are a proprietary service since "
         "withdrawn, or under a source-available licence"],
        ["Bodies as leaves of the tree", "[[red|Rejected]] (IN-4). An erasure would then leave a hole in the tree, or "
         "a hash of low-entropy content that \"can be confirmed by guessing\", which is ADR-0047's reason for not "
         "using content digests in handles"],
        ["Trust the archive for old entries, with no proof", "[[red|Rejected]] (§6). It would make the archive a trust "
         "root with no issued identity, which ADR-0045 §2 refuses"],
    ], size=13.5, accent="grey")
    t3 = c.table(xr, y + t2 + 24, [("Reading: option", 560, {"bold": True}), ("Disposition", w2 - 560)], [
        ["Direct access to the stores for auditors", "[[grey|Not taken.]] No reader sets, no journal, and for B no ACL"],
        ["Reader sets held by the archive", "[[grey|Not taken]] (RD-2). They would be a list an administrator edits. In "
         "a bundle they are promoted, and a change to them is a vote in the log"],
        ["Journal only reads of B", "[[grey|Not taken]] (drafter's choice). Who looked at the authority record is "
         "also something an audit asks"],
        ["A query language over the facts", "[[grey|Not taken.]] IX-1 has every reading a key condition. An auditor who "
         "needs more takes an export and queries their own copy"],
        ["Only GraphQL, or only REST", "[[grey|Not taken ⟨K6⟩ ⟨K12⟩]]"],
    ], size=13.5, accent="grey")
    y = max(y + t1, y + t2 + 24 + t3) + 40

    # ---- consequences, open obligations, history
    y = band(c, X0, y, "Consequences · Open obligations · History")
    g = 30
    w3 = (WW - 2 * g) / 3
    xs = [X0 + i * (w3 + g) for i in range(3)]
    b = [stack(c, xs[0], y, w3, [
        ("Consequences", [
            "[[green|Positive]]: the lock and the delete each have a store; an auditor can check one entry without "
            "reading the whole record or trusting the archive; the archive can lie and nothing is admitted on its "
            "word; a failed delete can be found; who read what is itself on the record; the documentation's design "
            "carries over nearly whole; the index's engine is the least proven part and the least trusted one.",
            "[[red|Negative]]: two object stores, an index, a tree and a read service for a deployment that has not "
            "yet run the mechanism; the lock has to be extended for ever and a lapse is silent until someone looks; "
            "three fault domains under two administrations is a cost many will declare away (D-0076-2); a body's "
            "bytes are checked only where the log holds a digest (IN-5); an export of units is a copy no erasure "
            "reaches (EX-3); reader sets as promoted policy make changing an auditor as slow as a promotion; **every "
            "product recommendation rests on reading and on none of it having been run.**"], "grey", {"tint": False}),
    ]), stack(c, xs[1], y, w3, [
        ("Open obligations", [
            "The external auditor role (ADR-0028), and the audit authority's reader set in the floor (RD-2).",
            "ADR-0004's second residual: \"the plaintext store's readers are where the replay-harness attestation "
            "requirement attaches\"; RD-1 names B's readers and does not attest them.",
            "Whether replay is a reader: ADR-0003 0003.5 and ADR-0020 do not say which governs; RD-6 records a "
            "replay's reads and settles nothing.",
            "The tree's implementation, pinned, and the canonical bytes of a leaf. A sequence number on denials "
            "(ADR-0005 §6), without which IN-5 cannot order them.",
            "The purge interval (GS-3) and the fault-domain numbers (LS-3, GS-5): the deployment writes these. "
            "Running the products of §2 to §4, and a second product behind each interface. Row T-0045-40, if the "
            "custodian takes Annex B.",
            "Narrative: ToO §4, §7.9 and the glossary owe locked store, governed store, root, inclusion proof "
            "and reader set if ratified."], "red", {"tint": False, "status": "open"}),
    ]), stack(c, xs[2], y, w3, [
        ("History", [
            "**—** Initial draft, 2026.11.16, by the assistant at the custodian's direction, not reviewed: a locked "
            "store, a governed store and an index that is a projection of both; the stores share no credential; a "
            "Merkle tree whose roots the log orders; nothing that decides reads without a proof; reading by promoted "
            "reader sets through GraphQL and REST; exports verify offline; T-0045-7 delegated with a second row "
            "proposed; five degeneracies.",
            "**R1** Revision before ratification: **renumbered from ADR-0075 to ADR-0076** with its five siblings, "
            "since ADR-0070 was taken by a record in flight on another branch (pull request #51). No decision text "
            "changes. Not reviewed."], "grey", {"tint": False}),
    ])]
    y = max(b) + 40

    # ---- Annex A: three tables
    y = band(c, X0, y, "Annex A · The index's keys, reference design (drafter's choice throughout; §4 is the "
             "requirement): one table; c is a chain id, i a zero-padded log index, s a segment number, d a "
             "SHA-256 in hex")
    wl = 1760
    wr = WW - wl - 40
    xr = X0 + wl + 40
    t1 = c.table(X0, y, [("Item", 170, {"bold": True}), ("PK", 330, {"mono": True}), ("SK", 300, {"mono": True}),
                         ("Holds", wl - 800)], [
        ["Fact", "CHAIN#<c>#SEG#<s>", "LOG#<i>", "Kind, class, epoch, principal, round, sequence number, the digests it "
         "cites, the leaf hash, the object key in the locked store"],
        ["Segment head", "CHAIN#<c>", "SEG#<s>", "Index range, root, the mark's log index, the corpus cut whose formats "
         "it uses"],
        ["Mark", "CHAIN#<c>", "MARK#<i>", "Kind (held, erased, disposed), range or unit, roots"],
        ["Unit header", "CHAIN#<c>#PRIN#<p>", "UNIT#<round>", "Fence, seal sequence number, container digest, state, "
         "schedule line, hold if any"],
        ["Cut", "CORPUS", "CUT#<date>#<name>", "Kind, commit, manifest digest, entry count"],
        ["Cut entry", "CUT#<name>", "PATH#<path>", "`d`"],
        ["Object", "OBJ#<d>", "HEAD", "Holding, size, lock term, fault domains, last fixity result"],
        ["Journal entry", "JOURNAL#<c>", "AT#<time>#<id>", "Kind (ingest, fixity, drop, read), subject, reader and "
         "reader set for a read"],
    ], size=13.5, accent="grey")
    t2 = c.table(X0, y + t1 + 24, [("Index", 340, {"bold": True}), ("Partition key", 440, {"mono": True}),
                                   ("Sort key", 500, {"mono": True}), ("On", wl - 1280)], [
        ["GSI1, a principal's facts", "CHAIN#<c>#PRIN#<p>", "ROUND#<r>#SEQ#<n>#LOG#<i>", "Facts"],
        ["GSI2, a class's facts", "CHAIN#<c>#CLASS#<class>", "LOG#<i>", "Facts"],
        ["GSI3, what cites a digest", "DIGEST#<d>", "CHAIN#<c>#LOG#<i>", "One item per digest a fact cites"],
        ["GSI4, a path across cuts", "PATH#<path>", "CUT#<date>#<name>", "Cut entries"],
        ["GSI5, units by state", "CHAIN#<c>#STATE#<state>", "PRIN#<p>#UNIT#<round>", "Unit headers"],
        ["LSI1, a chain's facts by epoch", "CHAIN#<c>#SEG#<s>", "EPOCH#<e>#LOG#<i>", "Facts"],
    ], size=13.5, accent="grey")
    t3 = c.table(xr, y, [("Operation (§7 RD-4)", 520, {"bold": True}), ("Key condition", wr - 520)], [
        ["Facts by index range", "`Query` `PK = CHAIN#<c>`, `SK between SEG#…` for the segments; then `PK = "
         "CHAIN#<c>#SEG#<s>`, `SK between LOG#<i1> and LOG#<i2>`"],
        ["Facts by principal and round", "`Query` GSI1, `SK begins_with ROUND#<r>#`"],
        ["Facts by class", "`Query` GSI2"],
        ["Facts by epoch", "`Query` LSI1 within each segment the epoch spans"],
        ["Facts that cite a digest", "`Query` GSI3 `PK = DIGEST#<d>`"],
        ["Marks; two roots for a consistency proof", "`Query` `PK = CHAIN#<c>`, `SK begins_with MARK#`"],
        ["A unit's header", "`GetItem` `CHAIN#<c>#PRIN#<p>`, `UNIT#<round>`"],
        ["Erasures not complete; unexplained headers", "`Query` GSI5 on the states that mean them"],
        ["A cut's files", "`Query` `PK = CUT#<name>`"],
        ["A path's digests across cuts", "`Query` GSI4 `PK = PATH#<path>`"],
        ["An object by digest", "`GetItem` `OBJ#<d>`, `HEAD`"],
        ["The journal; one reader's reads", "`Query` `PK = JOURNAL#<c>`, by time. A reader's own history is a further "
         "index, not drawn here"],
    ], size=13.5, accent="grey")
    ny = max(y + t1 + 24 + t2, y + t3) + 12
    y = ny + c.para(X0, ny, WW, "A unit's records are not in the table. They are read from the governed store by the "
                    "unit's container key.", 13.5, "muted") + 40

    # ---- Annex B
    y = band(c, X0, y, "Annex B · Dependent entries the archive set would owe (none drafted; ADR-0075's own are in its "
             "Annex B), and the proposed row T-0045-40, whole")
    y += c.table(X0, y, [("", 50, {"bold": True}), ("Record and kind", 600, {"bold": True}), ("Entry", WW - 650)], [
        ["1", "ADR-0045 Annex A, row T-0045-7. Amendment (dependent)", "The note goes below the table, naming the row. "
         "The row would read as the locked store only: component \"The archive's locked store (ADR-0074 A, C, D, "
         "E)\", trusted to retain what was written unchanged for each line's least period. Its residual gains the "
         "read service's confidentiality failure (§9). A new row would follow it (below)"],
        ["2", "ADR-0005 §5. No entry until the archive is built", "\"The archive does not exist at the reference\" "
         "stays true"],
        ["3", "ADR-0028, Open obligations. Amendment (dependent)", "\"Define the external auditor role\": §7 RD-1 uses "
         "the role and does not define it. The entry records the dependence and closes nothing"],
        ["4", "ADR-0015. No entry", "§5 IN-3 gives the audit chain a means of being walked, and changes no clause"],
        ["5", "ADR-0035 and ADR-0069 (both Proposed). R-revisions (dependent on ADR-0076, Proposed)", "A gate that "
         "reads log positions reads them under §6 AR-2 once the log is compacted"],
        ["6", "A mechanism record, unwritten", "The archive mark and its kinds, the journal root in a mark, and the "
         "rule on compaction (ADR-0074 §4). When the archive is built, ADR-0033 takes an addendum with the run"],
    ], size=13.5, accent="red") + 24
    cols = [("Id", 120, {"bold": True}), ("Component", 330), ("Layer", 110), ("Trusted for", 420), ("Rungs", 90),
            ("Class", 130), ("Failure can produce", 520), ("Identity fixed by", 360)]
    cols.append(("Residual", WW - sum(cl[1] for cl in cols)))
    y += c.table(X0, y, cols, [
        {"cells": ["T-0045-40", "The archive's governed store (ADR-0004; ADR-0074 B)", "substrate", "Holds a round "
                   "unit until its erasure or its period's end, and then no longer", "all", "delegated", "A unit lost "
                   "early: legibility subtracted. A unit not deleted: an erasure or a limit not honoured", "The "
                   "deployment declaration, with no lock and no versioning", "A unit that outlives its erasure harms "
                   "the person it concerns and changes no authority. The mechanism records the archive's report that it "
                   "is gone and cannot check it"], "accent": "brown"},
    ], size=13.5, accent="brown") + 16
    y += c.para(X0, y, WW, "**Proposed, not in ADR-0045.** T-0045-37 is the last row in force (ADR-0053, Batch 36); T-0045-38 "
                "and T-0045-39 are ADR-0056's proposed rows (C10), so T-0045-40 is the next id after them. The row "
                "exists only in ADR-0076 Annex B until ADR-0045 takes its amendment; the diagram shows it as the "
                "record writes it.", 13.5, "muted") + 20
    return y
