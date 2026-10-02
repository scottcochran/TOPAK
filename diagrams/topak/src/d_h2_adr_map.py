"""H2 — The decision record map: ADR-0001 to ADR-0046 by area, with status, markers and edges."""
import math

from lib import Canvas

ID, SLUG = "H2", "adr-map"

# id -> (short title, status, status_extra, relation line, note)
#   status: accepted | proposed | superseded | tombstone | reserved
R = {
    1: ("Rename the CI domain to `Build`; adopt `Build(Contain) → Run(Contain)`", "accepted", "", "", ""),
    2: ("Apply the membrane in `Build` as well", "accepted", "", "", "A2: the evictability test"),
    3: ("Topic per principal per round, sealed on emit, as the unit of erasure", "accepted", "C1 for A2 only", "",
        ""),
    4: ("Separate control-plane facts from cognitive payloads", "accepted", "", "", ""),
    5: ("Kafka is neither the ordering authority nor the system of record", "proposed", "", "",
        "Blocked on a decision; ADR-0033's K row is a debt on it"),
    6: ("Erasure is a privileged, modeled, consensus-ordered event", "accepted", "C1, C4 via 0013", "", ""),
    7: ("Semantic judgment is never a lift", "accepted", "", "", ""),
    8: ("Observer replicas are not colocated with the Thinker", "superseded", "by 0038", "",
        "Colocation rule carried forward by 0038 §4"),
    9: ("Break-glass is a modeled, quorum-witnessed path, not a prohibition", "accepted", "C1, C4 via 0013", "",
        ""),
    10: ("The verified object: the mechanism, its epoch discipline, a minimal policy floor", "accepted", "", "",
         "Amended by 0026"),
    11: ("Observer placement and fault-domain independence", "tombstone", "", "", "No decision content"),
    12: ("The default-deny bundle is the policy floor: pre-blessed, resident, verified", "accepted", "", "", ""),
    13: ("Exception mechanism for privileged paths through the floor", "accepted", "C1, C4",
          "0010, 0025, 0026, 0028", ""),
    14: ("— (the per-class floor question)", "reserved", "", "", "Reserved, no file; narrowed by 0024"),
    15: ("Effects are boundary crossings; every crossing authorized, ordered, auditable", "accepted", "C2", "",
         "Revised by 0025"),
    16: ("The model enters the system as a Persona", "accepted", "", "0002, 0007, 0010", ""),
    17: ("Archetype admits only in-house pre-trained Personas", "accepted", "", "0008, 0016",
         "Ordering-primacy clause reversed in effect; supersession unwritten"),
    18: ("The typed lift splits: decoder in the Persona, validator in the mechanism", "accepted", "",
         "0004, 0007, 0010, 0016", "Reader scope correction reversed in effect by 0037 §3"),
    19: ("Optional decode observability", "accepted", "", "0004, 0006, 0008, 0016", "Narrow form"),
    20: ("Replay scope is boundary events only", "accepted", "", "0003, 0004, 0006", ""),
    21: ("Build emits to the effect stream; Build has an Observer", "accepted", "C4", "", ""),
    22: ("Typed action alphabet for Build principals", "accepted", "§1–§5, §7, §8 only", "",
         "§6 (confinement) stays Proposed"),
    23: ("Degeneracy as the deployment-variation relation; archetype as unique maximum", "accepted", "C3", "",
         "§5 reverses 0008 scoping and 0017 ordering-primacy in effect"),
    24: ("Promotion requires a unanimous quorum", "accepted", "bootstrap set", "0007, 0010, 0022, 0025, 0026",
         "Amends 0002; A2 in force"),
    25: ("The trust anchor is a havoc issuer; intent is the sole axiom", "accepted", "bootstrap set", "",
         "Revises 0015; A1 item (f)"),
    26: ("The rules floor bounds every anchor issuance", "accepted", "bootstrap set", "0007, 0010, 0025",
         "Amends 0010; R8 (A1) pending"),
    27: ("Genesis rules are resident", "accepted", "bootstrap set", "0025, 0026", ""),
    28: ("The forensic floor: authority facts survive erasure and break-glass", "accepted", "C1",
         "0004, 0006, 0010, 0020", "Split from 0013"),
    29: ("Genesis; the custodian ratifies unilaterally; bootstrap on a drafted TLA+ spec", "accepted",
         "C3 for A2 only", "0024, 0025, 0026, 0027", ""),
    30: ("Bundles cannot add authority by construction; the floor runs on a verified evaluator", "accepted", "C1",
         "0007, 0010, 0012, 0018, 0023", "Floor text and schema S stay DRAFT; A1 (B24)"),
    31: ("The lease is the composite credential, and its grant is the instant", "accepted", "C1; C2 for A1",
         "0003, 0007, 0016, 0022, 0026, 0032", ""),
    32: ("The clock model: intervals trusted by failure direction", "accepted", "", "0007, 0022, 0031", ""),
    33: ("The mechanism has a reference implementation: evidence, not the verified object", "accepted", "",
         "0010, 0015, 0022, 0024, 0026, 0029, 0032", "A1–A6; K row a debt on 0005"),
    34: ("Confinement is attested at lease grant; the archetype rung is a confidential VM", "accepted", "C2, C4",
         "0016, 0017, 0022, 0023, 0024, 0031, 0032, 0033, 0035", "Discharges 0022 §6 for Build"),
    35: ("Persona lineage is a projection of the Build log; independence is an exclusion rule", "proposed", "",
         "0015, 0016, 0017, 0022, 0024, 0034", "R2 marked by custodian instruction"),
    36: ("At rung 1 the launcher is the channel: a principal `Mediated` by declaration", "proposed", "",
         "0017, 0022, 0031, 0033, 0034", ""),
    37: ("The LTRO decomposes into principals: Thinker and Observer are seats", "accepted", "C3, C4",
         "0002, 0007, 0016, 0018, 0019, 0022, 0024, 0031", ""),
    38: ("Observers are per cell; the shared group becomes the correlator", "accepted", "C3, C4",
         "0003, 0004, 0007, 0023, 0031, 0037", "Supersedes 0008"),
    39: ("Observer liveness is progress, not presence", "accepted", "C4",
         "0007, 0022, 0024, 0031, 0032, 0037, 0038", ""),
    40: ("Run has its own alphabet: `Consult`, `Actuate`, `Report`", "accepted", "C3, C4",
         "0007, 0010, 0015, 0018, 0022, 0031", "Reverses in effect 0022 §5's shared `Read`/`Emit`"),
    41: ("Policy obligations for Run: one envelope per variant; coupling on effects only", "accepted", "C1, C4",
         "0009, 0013, 0026, 0030, 0037, 0039, 0040", ""),
    42: ("Mechanism obligations for Run: effects counted, every `Actuate` recorded", "accepted",
         "§1–§5, §7, §8 · C4", "0003, 0004, 0015, 0018, 0031, 0033, 0039, 0040", "§6 Proposed"),
    43: ("Cell obligations for Run: Listener, seats, what the Observer must read", "accepted", "C4",
         "0018, 0037, 0038, 0039, 0040, 0042", ""),
    44: ("A bundle is trusted by its signature, not its file name", "accepted", "C1", "0025, 0030, 0031, 0033",
         "Drafted by the assistant"),
    45: ("The trusted base is declared row by row", "accepted", "C2, C4", "0015, 0023, 0025, 0029, 0031, 0034",
         "Drafted by the assistant; new at G7; T-0045-31 by B25"),
    46: ("The formal layer's method is declared: TLC checks, TLAPS proves, the prover is a trusted-base row",
         "accepted", "C2, C4", "0023, 0026, 0029, 0045", "Drafted by the assistant; new at G8 (Batch 25)"),
}

# rows of regions: (label, accent, ncols, [ids in grid order, None for an empty slot])
ROWS = [
    [("Authority and bootstrap", "brown", 5, [25, 26, 24, 27, 29]),
     ("Deployment variation", "violet", 1, [23]),
     ("Reference, trusted base and method", "teal", 3, [33, 45, 46])],
    [("Domains, membrane and Build alphabet (B1–B3)", "teal", 5, [1, 2, 7, 15, 22]),
     ("Run", "green", 4, [40, 41, 42, 43])],
    [("Policy and floors", "blue", 4, [10, 12, 30, 44, 13, 6, 9, 14]),
     ("Record, transport and erasure", "grey", 3, [4, 3, 20, 28, 21, 5]),
     ("Lease, time and confinement", "amber", 2, [31, 32, 34, 36])],
    [("Seats, cells and detection", "pink", 3, [8, 38, 39, 11, 37, None]),
     ("Persona and model", "violet", 3, [16, 17, 19, 18, 35, None])],
]

# edges drawn under a tile row: (src, dst, kind) — kind: dep | sup | rev
UNDER = [
    (26, 25, "dep"), (24, 25, "dep"), (24, 26, "dep"), (27, 25, "dep"), (27, 26, "dep"),
    (29, 24, "dep"), (29, 25, "dep"), (29, 26, "dep"), (29, 27, "dep"), (46, 45, "dep"),
    (41, 40, "dep"), (42, 40, "dep"), (43, 40, "dep"), (43, 42, "dep"),
    (30, 10, "dep"), (30, 12, "dep"), (44, 30, "dep"),
    (20, 4, "dep"), (20, 3, "dep"),
    (31, 32, "dep"), (32, 31, "dep"),
    (36, 34, "dep"),
    (38, 8, "sup"), (39, 38, "dep"),
    (17, 16, "dep"), (19, 16, "dep"),
    (37, 18, "rev"),
]
EDGE = {"dep": ("blue", None, 1.6), "sup": ("grey", None, 3.0), "rev": ("red", "7 5", 2.4)}


def build():
    c = Canvas(ID, "The decision records, ADR-0001 to ADR-0046, by area",
               "Every record with its status and confirmation markers at G8. Solid blue edges are dependencies taken "
               "from each record's \"Depends on\" line, drawn where both records sit in the same row of tiles (every "
               "tile lists its full line); the grey edge is the one supersession; red dashed edges are the reversals "
               "in effect (ToO §8.3) and ADR-0040's.",
               3600, "decisions/README.md; G8 §1, §1.1, §1.2, §4, §6; ToO rev 11 §0, §8.3, §9; the Status, Status note, "
               "Depends on, Supersedes, Amends, Revises, Narrows and Split from lines of ADR-0001 to ADR-0046; ADR-0018 "
               "Status note on 0037 §3; ADR-0023 Status note; ADR-0038 Supersedes; ADR-0040 Status note")
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
        key = st if st in ("accepted", "proposed", "superseded") else None
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
                if st in ("accepted", "proposed", "superseded"):
                    acc_t = {"accepted": "blue", "proposed": "amber", "superseded": "grey"}[st]
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
    chx = c.x1 - 26
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

    # ---------------------------------------------------------------- legend and notes, right of the last band
    last_row = ROWS[3]
    used_w = sum(nc * tw + (nc - 1) * ig + 2 * rp for _, _, nc, _ in last_row) + rgap * len(last_row)
    lx = X0 + used_w
    lw = chx - 70 - lx
    ly = band_tops[3]
    h1 = c.card(lx, ly, lw, "Reading a tile", [
        "Tile colour is status: [[blue|blue]] Accepted (genesis), [[red|red]] Accepted with a confirmation marker "
        "(C1–C4, ADR-0029 §4), [[amber|amber]] Proposed, [[grey|grey]] superseded, tombstone or reserved.",
        "\"bootstrap set\": ADR-0024 to 0027, which cannot carry a marker (ADR-0029 §4).",
        "\"§1–§5, §7, §8\": ratified in part; §6 stays Proposed (ADR-0022, ADR-0042).",
    ], accent="grey", size=13.5, bullets=True)
    ly += h1 + 18
    c.legend(lx, ly, [("arrow", "blue", "depends on"), ("arrow", "grey", "supersedes"),
                      ("arrow", "red", "reverses in effect", "7 5")], title="Edges", maxw=lw)
    ly += 60
    c.card(lx, ly, lw, "Counts at G8 (§1.1)", [
        "**40 Accepted** (18 + 22 confirmation-required), 2 in part · **3 Proposed** · **1 superseded** · "
        "**1 tombstone** · **1 reserved**: 45 files, numbered to 0046.",
        "**New at G8**: ADR-0046 (Batch 25, C2, C4). Its dependent entries (B25) landed in 0013, 0026, 0029, 0030, "
        "0031, 0034, 0037, 0038, 0039, 0041, 0042, 0043 and 0045; no decision text changed in any of them (G8 §6).",
        "**Reversals in effect** (ToO §8.3), all by the author alone in genesis: 0008 by 0038 (superseded); 0017's "
        "ordering-primacy clause (supersession unwritten, G8 item 6); 0018's Reader scope by 0037 §3 (not "
        "superseded).",
    ], accent="grey", size=13.5)
    return c
