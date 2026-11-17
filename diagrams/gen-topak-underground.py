#!/usr/bin/env python3
"""The TOPAK line diagram: the pattern drawn as a 1930s-style pocket railway map.

    python3 diagrams/gen-topak-underground.py                  # writes diagrams/underground/
    python3 diagrams/gen-topak-underground.py --fragment PATH  # also the page without its document skeleton

Writes one HTML page (the network map, four line diagrams and an index to stations) and each drawing as a
standalone SVG. Standard library only. The stations, their text and their marks are data in this file, read by hand
from the documents diagrams/README.md lists for it; nothing is read from the corpus at build time, so the drawing
does not follow a record that moves. Layout is hand-placed on a grid of 20 px units and checked by eye."""
import html
import math
import os
import sys

U = 20                      # one grid unit in px
GW, GH = 88, 54             # grid size
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "underground")
SRC = os.path.join(OUT, "src")
DATE = "2026.11.14"         # the day the diagram was drawn; its state of record is Genesis Checkpoint G11


def tc(s):
    """Title case for a station name, small words kept small."""
    out = []
    for i, w in enumerate(s.replace("\n", " ").split(" ")):
        lw = w.lower()
        out.append(lw if i and lw in ("and", "or", "in", "of") else lw[:1].upper() + lw[1:])
    return " ".join(out)


def esc(s):
    return html.escape(s, quote=True)


def rpath(points, r=0.9):
    """Rounded orthogonal/diagonal polyline through grid points."""
    pts = [(x * U, y * U) for x, y in points]
    if len(pts) < 2:
        return ""
    d = ["M%.1f %.1f" % pts[0]]
    for i in range(1, len(pts) - 1):
        ax, ay = pts[i - 1]
        bx, by = pts[i]
        cx, cy = pts[i + 1]
        lab = math.hypot(ax - bx, ay - by)
        lbc = math.hypot(cx - bx, cy - by)
        cut = min(r * U, lab / 2, lbc / 2)
        p1 = (bx + (ax - bx) / lab * cut, by + (ay - by) / lab * cut)
        p2 = (bx + (cx - bx) / lbc * cut, by + (cy - by) / lbc * cut)
        d.append("L%.1f %.1f Q%.1f %.1f %.1f %.1f" % (p1[0], p1[1], bx, by, p2[0], p2[1]))
    d.append("L%.1f %.1f" % pts[-1])
    return " ".join(d)


# ------------------------------------------------------------------ lines
# status: solid (accepted), prov (provisional: in force, subject to redesign), prop (Proposed)
LINES = [
    ("admit", "Admit", "The membrane, to an effect", "solid", [
        [(6, 24), (79, 24)],
        [(61.5, 24), (63, 24), (67, 20), (76, 20)],
        [(42.5, 24), (44, 24), (47, 21)],
    ]),
    ("authority", "Authority", "From intent to the tally", "solid", [
        [(46.5, 5), (73, 5), (76, 8), (76, 10)],
    ]),
    ("promotion", "Promotion", "The only way from Build to Run", "solid", [
        [(76, 20), (76, 10), (30, 10), (26, 14), (26, 24)],
    ]),
    ("record", "Record", "Topics, archive, audit", "solid", [
        [(61, 24), (61, 43)],
    ]),
    ("detection", "Detection", "Observers, deny-only", "solid", [
        [(61, 28), (56, 33), (44.25, 33), (36, 24.75)],
    ]),
    ("ingress", "Ingress", "What the Listener delivers", "solid", [
        [(71, 48), (10, 48), (6, 44), (6, 24)],
        [(71, 24), (71, 44), (67, 48), (65.5, 48)],
    ]),
    ("operator", "Operator", "Six signed control actions", "prov", [
        [(10.5, 36), (24, 36), (35.25, 24.75), (55, 24.75)],
    ]),
    ("emergency", "Emergency", "Break-glass, as a seating", "prov", [
        [(9, 30), (20, 30), (26, 24)],
    ]),
    ("workflow", "Workflow", "A promoted graph of cells", "prop", [
        [(76, 10), (74, 8), (20, 8), (16, 12), (16, 24)],
    ]),
    ("shuttle", "Appraisal shuttle", "Rung 3 evidence and verdict", "solid", [
        [(11, 24), (11, 19)],
    ]),
]
# extra segments drawn in another status than their line's
EXTRA = [
    ("detection", "prop", [(52, 33), (52, 38)]),
]
LINE_NAME = {l[0]: l[1] for l in LINES}
LINE_STATUS = {l[0]: l[3] for l in LINES}

# ------------------------------------------------------------------ stations
# id, label (\n breaks), x, y, kind, label dir, lines, tick colour line
#   kind: tick | ring | cap (capsule, two parallel lines) | term (terminus bar)
# then: what, record, reference
S = []


def st(sid, label, x, y, kind, ldir, lines, what, record, ref, y2=None):
    S.append(dict(id=sid, label=label, x=x, y=y, kind=kind, ldir=ldir, lines=lines, what=what, record=record,
                  ref=ref, y2=y2))


# Admit line
st("thinker", "THINKER SEAT", 6, 24, "ring", "N", ["admit", "ingress"],
   "A Persona in a confined guest, Byzantine by premise. It speaks one typed alphabet: six variants in Build, "
   "three in Run.",
   "ADR-0007, ADR-0022, ADR-0037, ADR-0040",
   "An agent process with a shell, or a launched guest: Mediated. No attested Persona.")
st("launcher", "LAUNCHER", 11, 24, "ring", "S", ["admit", "shuttle"],
   "Starts a guest from a promoted profile, appraises it, grants, and bridges its channel.",
   "ADR-0034, ADR-0036 (Proposed), ADR-0033 A7",
   "Rung 1 built, under the launcher's own assertion. Rung 2 is a seam.")
st("verifier", "VERIFIER ‡", 11, 19, "term", "E", ["shuttle"],
   "An independent verifier appraises rung-3 evidence under an issued key and returns a signed verdict.",
   "ADR-0034",
   "Simulated, under test keys.")
st("frontdoor", "FRONT DOOR", 16, 24, "ring", "S", ["admit", "workflow"],
   "Exposes the alphabet and nothing else.",
   "ADR-0022, ADR-0040, ADR-0033 §2",
   "Built: MCP tools over stdio, proxied to the agent socket.")
st("fence", "EPOCH FENCE", 21, 24, "tick", "N", ["admit"],
   "Local expiry, then the epoch fence. An action under a fenced epoch is rejected by the mechanism, not by policy.",
   "ADR-0010, ADR-0022",
   "Built.")
st("lease", "LEASE", 26, 24, "ring", "SE", ["admit", "promotion", "emergency"],
   "The one composite credential, twelve fields. It ends with its round, renewal only narrows it, and revoking it "
   "needs no quorum.",
   "ADR-0031, ADR-0032",
   "Built.")
st("lift", "LIFT", 31, 24, "tick", "N", ["admit"],
   "Syntactic lift to one frozen input. Semantic judgment is never a lift.",
   "ADR-0007, ADR-0018",
   "Built.")
st("floor", "POLICY FLOOR *", 36, 24, "cap", "N", ["admit", "operator", "detection"],
   "Permits only what the floor allows, over schema S, and any error is a deny. It decides control requests "
   "alone, and entry R3 refuses a Thinker's effect without a live cell Observer.",
   "ADR-0010, ADR-0012, ADR-0030, ADR-0041",
   "Built in Cedar, of the gated workflow stage, which is not in force. The floor in force is the emergency "
   "stage, 28 policies, genesis-provisional.", y2=24.75)
st("bundle", "BUNDLE", 42, 24, "tick", "N", ["admit"],
   "A signed bundle, evaluated at the lease's revision. It can refuse and can never grant: "
   "admit ⟺ floor_permit ∧ ¬bundle_deny.",
   "ADR-0030, ADR-0044, ADR-0049 §6",
   "Built: an OPA sidecar or in-process Wasm. Dev key.")
st("denied", "DENIED", 47, 21, "term", "E", ["admit"],
   "A denial is recorded, unordered, with digests only. It never crosses the log.",
   "ADR-0020, ADR-0042 A1",
   "Built: on the round topic, or its companion after the seal.")
st("apply", "APPLY", 55, 24, "cap", "N", ["admit", "operator"],
   "At its log position every entry is checked again: fence, lease, alphabet. If one has moved the admit is void: "
   "ordered, recorded, no effect.",
   "ADR-0033 §4",
   "Built. The floor and bundle are not re-run; their decision is recorded with the input digest.", y2=24.75)
st("effect", "EFFECT", 61, 24, "ring", "N", ["admit", "record"],
   "The effect executor performs an effect only after its admit commits.",
   "ADR-0015, ADR-0042",
   "Built: read, draft, tool, emit.")
st("toolhost", "TOOL HOST", 71, 24, "ring", "SE", ["admit", "ingress"],
   "Gives a tool its workspace or its one declared channel, and nothing else. Handles are resolved on the "
   "mechanism's side.",
   "ADR-0034 P4, ADR-0047 §3, ADR-0049 §5",
   "Wasm built, on a provisional ABI. Native tools are unchecked.")
st("world", "THE WORLD", 79, 24, "term", "E", ["admit"],
   "The tools' targets: what Run acts on. Reached only by Actuate, on the allowlist entry's declared channel.",
   "ADR-0040, ADR-0042",
   "External.")
st("workspace", "WORKSPACE", 70, 20, "tick", "N", ["admit"],
   "Build's round-scoped workspace, where Draft writes.",
   "ADR-0022",
   "Built, in the effect executor.")
st("submit", "SUBMIT & SEAL", 76, 20, "ring", "E", ["admit", "promotion"],
   "Submit(digest) seals the workspace and the topic set. It is Build's sole egress.",
   "ADR-0021, ADR-0022",
   "Built.")
# Authority line
st("intent", "INTENT", 46.5, 5, "term", "N", ["authority"],
   "The sole axiom. Everything below it is issued, voted or derived.",
   "ADR-0025",
   "An assumption, not a block.")
st("anchor", "ANCHOR †", 52.5, 5, "tick", "N", ["authority"],
   "A havoc issuer. Its key-holders sign the rules and stand at the gate, outside the proofs.",
   "ADR-0025, ADR-0029",
   "Issuances are validated. No ceremony; one custodian, custody (1, 0).")
st("rulesfloor", "RULES FLOOR", 58.5, 5, "tick", "N", ["authority"],
   "Bounds every anchor issuance, R1 to R9 (R8 withdrawn). An issuance outside it is rejected.",
   "ADR-0026",
   "Built.")
st("rules", "RULES", 64.5, 5, "tick", "N", ["authority"],
   "Rosters, seat declarations, quorum, keys and the two lists the load checks read. Genesis rules are resident.",
   "ADR-0025, ADR-0027",
   "Built, with dev rules. No genesis rules.")
st("grantseats", "GRANT SEATS", 70.5, 5, "tick", "N", ["authority"],
   "Human voters, Mediated. Each vote is bound to the artifact, the evidence and the rules epoch, and the author "
   "is recused.",
   "ADR-0024",
   "Votes are counted. The veto seat's independence is unchecked.")
st("tally", "PROMOTION TALLY §", 76, 10, "ring", "E", ["authority", "promotion", "workflow"],
   "Promotion is a unanimous quorum grant, counted at apply: Promoted, Pending, Stalled or Denied. A timeout never "
   "grants.",
   "ADR-0024, ADR-0039 §3",
   "Partial. No pipeline; gate evidence is an operator's assertion.")
# Promotion line
st("gates", "GATES §", 76, 17, "tick", "E", ["promotion"],
   "Totality, non-vacuity, discrimination. Each vote covers the evidence digest.",
   "ADR-0007, ADR-0030 A1",
   "Partial: floor/run-gates.py, outside the mechanism. Evidence unsigned.")
st("sign", "SIGN §", 62, 10, "tick", "S", ["promotion"],
   "The bundle key signs after the tally and never before.",
   "ADR-0044 §4",
   "Dev key. Signing is a script step.")
st("rollout", "ROLL OUT †", 26, 18, "tick", "E", ["promotion"],
   "A promoted revision reaches a live principal when its round ends: the next lease names it. A promotion seats.",
   "ADR-0031; ADR-0024 A3 (provisional)",
   "Not built. A promotion does not seat; the unsigned BOOTSTRAP socket stands in for the quorum.")
# Workflow line (Proposed)
st("wfengine", "WORKFLOW ENGINE", 56, 8, "tick", "N", ["workflow"],
   "Loads a workflow only from a promoted artifact, grants each slot under the promotion's authority, evaluates "
   "guards over settled attributes, and checks a route at decide and again at apply.",
   "ADR-0054, ADR-0055 (Proposed)",
   "Built for each record's listed behaviours, on a floor stage that is not in force.")
st("orchestrator", "ORCHESTRATOR", 38, 8, "tick", "N", ["workflow"],
   "Chooses one enabled edge with Route(edge). It is given handles, never bytes. It can stall a workflow and "
   "cannot misroute it.",
   "ADR-0054 §3 (Proposed)",
   "Built; driven by the tests' scripted cells.")
# Operator line (provisional)
st("idp", "IDENTITY\nPROVIDER ‡", 10.5, 36, "term", "S", ["operator"],
   "Vouches for the person behind an operator's key: a sign-on assertion naming the key and a fence.",
   "ADR-0050 §3 (provisional)",
   "Simulated: test keys.")
st("operator", "OPERATOR\nSEAT", 16.5, 36, "tick", "S", ["operator"],
   "A person and a principal. One operator keeps a quorum's grant going and may only narrow it.",
   "ADR-0050 (provisional)",
   "Signed requests are built. A first lease from a quorum is not: the BOOTSTRAP socket seats.")
st("control", "CONTROL", 22, 36, "tick", "S", ["operator"],
   "Six signed actions. Three add: Regrant, Renew, AttestGates. Three deny: EndRound, Revoke, FenceEpoch. Floor "
   "entries C1 to C9 decide them with no bundle, and a deny needs no lease.",
   "ADR-0050 (provisional), ADR-0031 A3",
   "Built.")
# Emergency line (provisional)
st("roster", "ROSTER", 9, 30, "term", "S", ["emergency"],
   "The break-glass roster. Its quorum signs an activation.",
   "ADR-0052 (provisional)",
   "Roster keys sign on the operator socket.")
st("activation", "ACTIVATION", 14, 30, "tick", "S", ["emergency"],
   "One person, one seating, one round, with the task. The Activate entry is forensic class F5.",
   "ADR-0052 (provisional), ADR-0028",
   "Built. The seating is prepared by the BOOTSTRAP path, not by a promotion.")
st("emseat", "EMERGENCY\nSEAT", 19, 30, "tick", "S", ["emergency"],
   "One lease, no successor and no renewal, on an ordinary allowlist with no floor exception. It is not coupled "
   "to an Observer, so no Observer can block the call.",
   "ADR-0052 (provisional), ADR-0039 A2",
   "Built. Nothing counts the drill.")
# Record line
st("topic", "ROUND TOPIC", 61, 28, "ring", "E", ["record", "detection"],
   "One topic per principal per round, opened by the mechanism's record and sealed on emit: the unit of erasure. "
   "Kafka is neither the ordering authority nor the system of record.",
   "ADR-0003, ADR-0005",
   "Built: Kafka, or in memory.")
st("archive", "ARCHIVE †", 61, 31, "tick", "E", ["record"],
   "The system of record for control-plane facts.",
   "ADR-0004, ADR-0005",
   "Absent.")
st("payload", "PAYLOAD STORE †", 61, 34, "tick", "E", ["record"],
   "Cognitive payloads, kept apart from the facts and built for deletion.",
   "ADR-0004",
   "Absent.")
st("erasure", "ERASURE †", 61, 37, "tick", "E", ["record"],
   "A privileged, modeled, consensus-ordered event, and the floor's one exception.",
   "ADR-0006, ADR-0013, ADR-0028",
   "Absent. Genesis issues no erasure roster.")
st("forensic", "FORENSIC FLOOR", 61, 40, "tick", "E", ["record"],
   "Six classes survive erasure: F1 admit decisions, F2 stop attribution, F3 promotion votes, F4 anchor "
   "issuances, F5 activations, F6 erasure events.",
   "ADR-0028",
   "Archetype. Erasure is not built.")
st("audit", "AUDIT AUTHORITY", 61, 43, "term", "E", ["record"],
   "Reads the record: replay of boundary events, for the declared horizon.",
   "ADR-0020, ADR-0028",
   "No reader other than the author has verified any of it.")
# Detection line
st("observer", "CELL OBSERVER", 52, 33, "tick", "N", ["detection"],
   "One per cell, deny-only. It reads the cell's round topics, and sends heartbeats, findings and Vote(deny).",
   "ADR-0038, ADR-0039",
   "The seat is built. No detector sits behind it, and the read ACL W(p) is not enforced.")
st("heartbeat", "HEARTBEAT", 40, 28.75, "tick", "SW", ["detection"],
   "Liveness is progress, not presence: heard within T_obs, and seq − mark < K. Run couples every effect to it; "
   "Build couples the gate.",
   "ADR-0039",
   "Built: floor entry R3-observer-live. T_obs and K are placeholders.")
st("correlator", "CORRELATOR †", 52, 38, "term", "E", ["detection"],
   "Named folds over facts: five correlations a second reader can recompute. Never coupled.",
   "ADR-0038, ADR-0051 (Proposed)",
   "Absent as a detector. The seat only.")
# Ingress line
st("pinned", "PINNED CONTENT", 71, 48, "term", "S", ["ingress"],
   "The corpus root in Build and the Run root: content-addressed, reached by Read and Consult.",
   "ADR-0022, ADR-0040",
   "External.")
st("listener", "LISTENER", 62, 48, "tick", "N", ["ingress"],
   "A stage, not a seat. It delivers the task, admitted reads and results, and makes no choice.",
   "ADR-0037, ADR-0043",
   "Built for results, consulted content and the tool list.")
st("labels", "LABELS", 52, 48, "tick", "N", ["ingress"],
   "Every item of Run's ingress carries a label: a function of its source, and no judgment about content.",
   "ADR-0047",
   "Built since 2026.10.05. No task at a first seating.")
st("handles", "CLEAR OR HANDLE", 42, 48, "tick", "N", ["ingress"],
   "An item arrives clear, and joins clearSet, or as a handle: a name and no bytes. Forbids R5 to R7 tighten "
   "with what was read.",
   "ADR-0047",
   "Built. Handles resolve to scalars only.")
st("toollist", "TOOL LIST", 30, 48, "tick", "N", ["ingress"],
   "A Thinker learns its tools from the mechanism. The list is the round's opening record.",
   "ADR-0048, ADR-0049",
   "Built.")


def grid_ref(s):
    col = "ABCDEFGH"[min(7, int(s["x"] // 11))]
    row = min(6, int(s["y"] // 9) + 1)
    return "%s%d" % (col, row)


# ------------------------------------------------------------------ main map SVG
DIRV = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0),
        "NE": (0.7071, -0.7071), "SE": (0.7071, 0.7071), "SW": (-0.7071, 0.7071), "NW": (-0.7071, -0.7071)}
LH = 12.5                      # label line height, px


def label_svg(s):
    lines = s["label"].split("\n")
    x, y = s["x"] * U, s["y"] * U
    if s.get("y2"):
        ymid = (s["y"] + s["y2"]) / 2 * U
    else:
        ymid = y
    d = s["ldir"]
    ix = " ix" if s["kind"] in ("ring", "cap") else ""
    off = 13 if s["kind"] in ("ring", "cap") else 12
    n = len(lines)
    if d == "N":
        tx, ty, anchor = x, y - off - (n - 1) * LH, "middle"
    elif d == "S":
        yb = (s["y2"] * U if s.get("y2") else y)
        tx, ty, anchor = x, yb + off + 9, "middle"
    elif d == "E":
        tx, ty, anchor = x + off, ymid + 4 - (n - 1) * LH / 2, "start"
    elif d == "W":
        tx, ty, anchor = x - off, ymid + 4 - (n - 1) * LH / 2, "end"
    elif d == "SE":
        tx, ty, anchor = x + 9, y + 21, "start"
    elif d == "NE":
        tx, ty, anchor = x + 9, y - 11, "start"
    elif d == "SW":
        tx, ty, anchor = x - 10, y + 15, "end"
    else:  # NW
        tx, ty, anchor = x - 9, y - 11, "end"
    out = ['<text class="st%s" x="%.1f" y="%.1f" text-anchor="%s">' % (ix, tx, ty, anchor)]
    for i, ln in enumerate(lines):
        out.append('<tspan x="%.1f" dy="%s">%s</tspan>' % (tx, "0" if i == 0 else "%.1f" % LH, esc(ln)))
    out.append("</text>")
    return "".join(out)


def station_svg(s):
    x, y = s["x"] * U, s["y"] * U
    cls = " ".join("s-" + l for l in s["lines"])
    g = ['<g class="stn %s" data-id="%s"><title>%s (%s). %s</title>' % (
        cls, s["id"], esc(s["label"].replace("\n", " ")), grid_ref(s), esc(s["what"]))]
    col = "var(--l-%s)" % s["lines"][0]
    dx, dy = DIRV[s["ldir"]]
    if s["kind"] == "tick":
        g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5"/>' % (
            x, y, x + dx * 9.5, y + dy * 9.5, col))
    elif s["kind"] == "term":
        # bar across the line end, perpendicular to the line: the label dir tells which way the line runs
        tdir = TERM_AXIS[s["id"]]
        px, py = tdir
        g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5.5"/>' % (
            x - px * 9, y - py * 9, x + px * 9, y + py * 9, col))
    elif s["kind"] == "ring":
        g.append('<circle cx="%.1f" cy="%.1f" r="6.6" class="ring"/>' % (x, y))
    elif s["kind"] == "cap":
        y2 = s["y2"] * U
        g.append('<rect x="%.1f" y="%.1f" width="13.2" height="%.1f" rx="6.6" class="ring"/>' % (
            x - 6.6, y - 6.6, (y2 - y) + 13.2))
    g.append(label_svg(s))
    g.append("</g>")
    return "".join(g)


# terminus bars: unit vector along the bar
TERM_AXIS = {
    "verifier": (1, 0), "denied": (0.7071, 0.7071), "world": (0, 1), "intent": (0, 1), "idp": (0, 1),
    "roster": (0, 1), "audit": (1, 0), "correlator": (1, 0), "pinned": (0, 1),
}


def line_svg(lid, status, pts, extra_cls=""):
    d = rpath(pts)
    out = []
    if status == "prop":
        out.append('<path d="%s" class="ln ln-%s prop %s"/>' % (d, lid, extra_cls))
    else:
        out.append('<path d="%s" class="ln ln-%s %s"/>' % (d, lid, extra_cls))
        if status == "prov":
            out.append('<path d="%s" class="ln-stripe ln-%s %s"/>' % (d, lid, extra_cls))
    return "".join(out)


def frame_svg():
    W, H = GW * U, GH * U
    o = []
    o.append('<rect x="6" y="6" width="%d" height="%d" class="frame-o"/>' % (W - 12, H - 12))
    o.append('<rect x="26" y="26" width="%d" height="%d" class="frame-i"/>' % (W - 52, H - 52))
    for i, ch in enumerate("ABCDEFGH"):
        cx = (i * 11 + 5.5) * U
        o.append('<text class="grid" x="%.0f" y="20.5" text-anchor="middle">%s</text>' % (cx, ch))
        o.append('<text class="grid" x="%.0f" y="%d" text-anchor="middle">%s</text>' % (cx, H - 11.5, ch))
        if i:
            xx = i * 11 * U
            o.append('<line class="gridtick" x1="%d" y1="8" x2="%d" y2="26"/>' % (xx, xx))
            o.append('<line class="gridtick" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (xx, H - 26, xx, H - 8))
    for j in range(6):
        cy = (j * 9 + 4.5) * U + 4
        o.append('<text class="grid" x="16" y="%.0f" text-anchor="middle">%d</text>' % (cy, j + 1))
        o.append('<text class="grid" x="%d" y="%.0f" text-anchor="middle">%d</text>' % (W - 16, cy, j + 1))
        if j:
            yy = j * 9 * U
            o.append('<line class="gridtick" x1="8" y1="%d" x2="26" y2="%d"/>' % (yy, yy))
            o.append('<line class="gridtick" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (W - 26, yy, W - 8, yy))
    return "".join(o)


def cartouche_svg():
    x0, y0, w, h = 2.0 * U, 2.0 * U, 12.6 * U, 10.6 * U
    o = ['<g class="cartouche">']
    o.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" class="box"/>' % (x0, y0, w, h))
    o.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" class="box-in"/>' % (x0 + 4, y0 + 4, w - 8, h - 8))
    cx = x0 + w / 2
    o.append('<text class="ct-name" x="%.0f" y="%.0f" text-anchor="middle">TOPAK</text>' % (cx, y0 + 58))
    o.append('<text class="ct-sub" x="%.0f" y="%.0f" text-anchor="middle">DIAGRAM OF LINES</text>' % (cx, y0 + 82))
    o.append('<line class="ct-rule" x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f"/>' % (x0 + 24, y0 + 94, x0 + w - 24, y0 + 94))
    roles = [("T", "the survey: TLA+, TLC, proofs"), ("O", "Policy Floor and Bundle"),
             ("P", "the river: the consensus log"), ("A", "the seats: agents, as principals"),
             ("K", "the Record line: transport")]
    yy = y0 + 114
    for k, v in roles:
        o.append('<text class="ct-role" x="%.0f" y="%.0f"><tspan class="ct-letter">%s</tspan>'
                 '<tspan dx="8">%s</tspan></text>' % (x0 + 22, yy, k, esc(v)))
        yy += 16.5
    o.append('<text class="ct-foot" x="%.0f" y="%.0f" text-anchor="middle">The archetype, as the records draw it.</text>'
             % (cx, y0 + h - 14))
    o.append("</g>")
    return "".join(o)


def key_svg():
    x0, y0, w, h = 75.4 * U, 27.6 * U, 10.8 * U, 24.6 * U
    o = ['<g class="key">']
    o.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" class="box"/>' % (x0, y0, w, h))
    o.append('<text class="key-h" x="%.0f" y="%.0f" text-anchor="middle">REFERENCE</text>' % (x0 + w / 2, y0 + 24))
    yy = y0 + 46
    for lid, name, sub, status, _ in LINES:
        xa, xb = x0 + 12, x0 + 50
        d = "M%.0f %.0f L%.0f %.0f" % (xa, yy, xb, yy)
        if status == "prop":
            o.append('<path d="%s" class="ln ln-%s prop"/>' % (d, lid))
        else:
            o.append('<path d="%s" class="ln ln-%s"/>' % (d, lid))
            if status == "prov":
                o.append('<path d="%s" class="ln-stripe"/>' % d)
        o.append('<text class="key-l" x="%.0f" y="%.0f">%s</text>' % (xb + 9, yy - 1, esc(name.upper())))
        o.append('<text class="key-s" x="%.0f" y="%.0f">%s</text>' % (xb + 9, yy + 10.5, esc(sub)))
        yy += 28
    yy += 2
    o.append('<line class="ct-rule" x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f"/>' % (x0 + 12, yy - 12, x0 + w - 12, yy - 12))
    # symbols
    sx = x0 + 31
    o.append('<path d="M%.0f %.0f L%.0f %.0f" class="ln ln-admit"/>' % (x0 + 12, yy + 3, x0 + 50, yy + 3))
    o.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="var(--l-admit)" stroke-width="5"/>' % (sx, yy + 3, sx, yy - 6.5))
    o.append('<text class="key-t" x="%.0f" y="%.0f">Station</text>' % (x0 + 59, yy + 7))
    yy += 21
    o.append('<path d="M%.0f %.0f L%.0f %.0f" class="ln ln-admit"/>' % (x0 + 12, yy + 3, x0 + 50, yy + 3))
    o.append('<circle cx="%.0f" cy="%.0f" r="6.6" class="ring"/>' % (sx, yy + 3))
    o.append('<text class="key-t" x="%.0f" y="%.0f">Interchange</text>' % (x0 + 59, yy + 7))
    yy += 21
    o.append('<path d="M%.0f %.0f L%.0f %.0f" class="ln ln-operator"/>' % (x0 + 12, yy + 3, x0 + 50, yy + 3))
    o.append('<path d="M%.0f %.0f L%.0f %.0f" class="ln-stripe"/>' % (x0 + 12, yy + 3, x0 + 50, yy + 3))
    o.append('<text class="key-t" x="%.0f" y="%.0f">Provisional: in force,</text>' % (x0 + 59, yy + 2))
    o.append('<text class="key-t" x="%.0f" y="%.0f">subject to redesign</text>' % (x0 + 59, yy + 13))
    yy += 27
    o.append('<path d="M%.0f %.0f L%.0f %.0f" class="ln ln-workflow prop"/>' % (x0 + 12, yy + 3, x0 + 50, yy + 3))
    o.append('<text class="key-t" x="%.0f" y="%.0f">Proposed: under</text>' % (x0 + 59, yy + 2))
    o.append('<text class="key-t" x="%.0f" y="%.0f">construction</text>' % (x0 + 59, yy + 13))
    yy += 30
    notes = ["At the reference implementation:", "†  not built", "‡  simulated", "§  partial",
             "*  genesis-provisional"]
    for i, n in enumerate(notes):
        o.append('<text class="key-t%s" x="%.0f" y="%.0f">%s</text>' % (" key-b" if i == 0 else "", x0 + 12, yy, esc(n)))
        yy += 13.5
    o.append("</g>")
    return "".join(o)


def map_svg():
    W, H = GW * U, GH * U
    o = ['<svg id="map" viewBox="0 0 %d %d" role="img" aria-labelledby="map-t map-d" xmlns="http://www.w3.org/2000/svg">' % (W, H)]
    o.append('<title id="map-t">TOPAK drawn as a railway line diagram</title>')
    o.append('<desc id="map-d">Ten coloured lines and forty-seven stations. The consensus log is drawn as a river: '
             'lines decide on its north bank and take effect on its south bank. Every station is listed in the index '
             'below the map.</desc>')
    o.append('<rect width="%d" height="%d" class="paper"/>' % (W, H))
    # river
    river = [(-1, 42), (32, 42), (60, 14), (89, 14)]
    rd = rpath(river, r=3)
    o.append('<clipPath id="inner"><rect x="26" y="26" width="%d" height="%d"/></clipPath>' % (W - 52, H - 52))
    o.append('<g clip-path="url(#inner)"><path d="%s" class="river-e"/><path d="%s" class="river"/></g>' % (rd, rd))
    o.append('<text class="river-t" x="%.0f" y="%.0f" text-anchor="middle">THE CONSENSUS LOG</text>' % (19.5 * U, 42 * U + 4))
    o.append('<text class="river-t" x="%.0f" y="%.0f" text-anchor="middle">THE LOG</text>' % (67.5 * U, 14 * U + 4))
    o.append('<text class="bank" x="%.0f" y="%.0f" text-anchor="middle">NORTH BANK · DECIDE</text>' % (36 * U, 16.5 * U))
    o.append('<text class="bank" x="%.0f" y="%.0f" text-anchor="middle">SOUTH BANK · EFFECT</text>' % (44.5 * U, 44.4 * U))
    # branch names
    o.append('<text class="branch" x="%.0f" y="%.0f">Build branch</text>' % (64.2 * U, 19.2 * U))
    o.append('<text class="branch" x="%.0f" y="%.0f" text-anchor="middle">Run branch</text>' % (75.2 * U, 23.35 * U))
    # crossings: the log entry a line is ordered as
    for (x, y, t, a) in [(50.9, 23.3, "Admit", "start"), (50.2, 26.6, "Control", "start"),
                         (76.7, 13.3, "votes", "start"), ]:
        o.append('<text class="xing" x="%.0f" y="%.0f" text-anchor="%s">%s</text>' % (x * U, y * U, a, t))
    # lines, proposed first so solid lines overprint
    order = sorted(LINES, key=lambda l: {"prop": 0, "prov": 1, "solid": 2}[l[3]])
    for lid, name, sub, status, paths in order:
        o.append('<g class="lg lg-%s">' % lid)
        for pts in paths:
            o.append(line_svg(lid, status, pts))
        for (xl, xs, pts) in EXTRA:
            if xl == lid:
                o.append(line_svg(lid, xs, pts))
        o.append("</g>")
    for s in S:
        o.append(station_svg(s))
    o.append(cartouche_svg())
    o.append(key_svg())
    o.append(frame_svg())
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ strip (carriage line) diagrams
def strip_svg(sid, lid, status, stops, river_after=None, loop=None, river_label="THE LOG"):
    """stops: list of (name, ring?) ; names are drawn at 38 degrees above the line."""
    n = len(stops)
    W = 1180
    x0, x1 = 70, W - 150
    step = (x1 - x0) / (n - 1)
    yl = 112
    H = 160 if not loop else 204
    o = ['<svg class="strip" viewBox="0 0 %d %d" role="img" aria-label="%s line diagram" xmlns="http://www.w3.org/2000/svg">'
         % (W, H, esc(sid))]
    o.append('<rect width="%d" height="%d" class="paper"/>' % (W, H))
    o.append('<rect x="3" y="3" width="%d" height="%d" class="strip-frame"/>' % (W - 6, H - 6))
    if river_after is not None:
        rx = x0 + step * (river_after + 0.5)
        o.append('<rect x="%.0f" y="3" width="26" height="%d" class="river-band"/>' % (rx - 13, H - 6))
        o.append('<text class="river-t" transform="translate(%.0f %.0f) rotate(-90)" text-anchor="middle">%s</text>'
                 % (rx + 4, 48, river_label))
    d = "M%.0f %d L%.0f %d" % (x0 - 34, yl, x1 + 34, yl)
    if status == "prop":
        o.append('<path d="%s" class="ln ln-%s prop"/>' % (d, lid))
    else:
        o.append('<path d="%s" class="ln ln-%s"/>' % (d, lid))
        if status == "prov":
            o.append('<path d="%s" class="ln-stripe"/>' % d)
    if loop:
        ly = yl + 46
        ld = "M%.0f %d L%.0f %d Q%.0f %d %.0f %d L%.0f %d Q%.0f %d %.0f %d L%.0f %d" % (
            x1 + 24, yl, x1 + 24, ly - 14, x1 + 24, ly, x1 + 10, ly, x0 - 10, ly, x0 - 24, ly, x0 - 24, ly - 14, x0 - 24, yl)
        o.append('<path d="%s" class="ln ln-%s prop thin"/>' % (ld, lid))
        o.append('<text class="loop-t" x="%.0f" y="%d" text-anchor="middle">%s</text>' % ((x0 + x1) / 2, ly + 20, esc(loop)))
    for i, (name, ring) in enumerate(stops):
        x = x0 + i * step
        if ring:
            o.append('<circle cx="%.0f" cy="%d" r="6.6" class="ring"/>' % (x, yl))
        else:
            o.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d" stroke="var(--l-%s)" stroke-width="5"/>' % (x, yl, x, yl - 9.5, lid))
        o.append('<text class="st%s" transform="translate(%.0f %d) rotate(-38)">%s</text>' % (
            " ix" if ring else "", x + 3, yl - 15, esc(name)))
        o.append('<text class="stop-n" x="%.0f" y="%d" text-anchor="middle">%d</text>' % (x, yl + 24, i + (0 if sid == "pipeline" else 1)))
    o.append("</svg>")
    return "\n".join(o)


STRIPS = [
    dict(
        id="admit", line="admit", status="solid", name="Admit line",
        tag="In force · the reference builds it",
        lede="Decide, then order, then effect. An action that is refused leaves the line before the log, and "
             "nothing reaches the south bank without crossing it.",
        src="ADR-0033 §4; Architecture Description §6.1",
        river_after=5,
        stops=[
            ("FRONT DOOR", True, "One action of the alphabet arrives, with its epoch and its lease."),
            ("EPOCH FENCE", False, "Local expiry, then the fence. A fenced epoch is refused by the mechanism, not by policy."),
            ("LEASE", True, "The lease is live, and the action is in the alphabet it names."),
            ("LIFT", False, "A syntactic lift to one frozen input. What the model meant is not consulted."),
            ("POLICY FLOOR", True, "Cedar answers Allow, the forbids that fired, or no permit matched. An error is a deny."),
            ("BUNDLE", False, "Evaluated at the lease's bundle revision. Anything other than allow is a refusal. "
                              "Refused here or earlier: denied, recorded unordered, digests only."),
            ("APPLY", True, "Across the log as an Admit entry carrying the input digest and both decisions. Fence, "
                            "lease and alphabet are checked again; if one moved, the admit is void and has no effect."),
            ("EFFECT", True, "Performed only now. A crash between commit and effect leaves no effect."),
            ("ROUND TOPIC", True, "The emission, with log index, fence and sequence. The Observer reads to the new sequence number."),
        ]),
    dict(
        id="pipeline", line="promotion", status="prop", name="Build-Run pipeline",
        tag="ADR-0069 · Proposed · under construction",
        lede="One ordered path from intake to rollout, keyed by digest. No stage starts on a name, the stages are "
             "not reordered, and an artifact that stops at any stage has no egress. Stage 4's carrier for this "
             "repository is built and runs. Nothing else on this line is modelled, checked or built.",
        src="ADR-0069 §1 to §8",
        loop="Run's output re-enters only through intake, as data, and enables nothing",
        stops=[
            ("INTAKE", False, "Takes objects with their sources. Produces a corpus-root revision, promoted. The only way into a corpus root."),
            ("ROUND", False, "Takes a corpus-root revision, a seating and a tool list. Produces leases at a fresh fence."),
            ("AUTHOR", False, "Read, Draft, Invoke, Emit. Produces a workspace and round topics."),
            ("SUBMIT AND SEAL", False, "Takes the workspace. Produces the artifact digest and the sealed topic-set digest."),
            ("GATES", False, "Takes the artifact digest. Produces gate evidence and its digest, counted once an issued key signs it."),
            ("TALLY", True, "Takes artifact, evidence and epoch. Produces the promotion entry in the log. The tally is the log's."),
            ("SIGN", False, "Takes the promotion entry. Produces a signature over the artifact digest."),
            ("PUBLISH", False, "Takes the artifact and its signature. Produces a content-addressed copy. Publishing locates."),
            ("ROLL OUT", False, "Takes a promoted, signed revision. Produces leases naming it. Rollout ends rounds."),
        ]),
    dict(
        id="overlay", line="overlay", status="prop", name="Command-chain extension",
        tag="ADR-0059 to ADR-0068 · Proposed · an overlay, not the archetype",
        lede="What follows if TOPAK is the top tier of a command chain. Planes are seated down a tree under charters "
             "that only narrow. Nothing here is in force or built, and a deployment with one plane takes nothing "
             "from it.",
        src="ADR-0059 to ADR-0066; diagram A5",
        stops=[
            ("ROOT PLANE", True, "The anchor's key and the root's tally, which seats each child plane by voting its charter. One floor, in Cedar. (ADR-0059)"),
            ("COMMANDED PLANES", False, "Any number, and where people are seated. Every field of a charter is the parent's or narrower. (ADR-0059 §3)"),
            ("INTENT BOUNDARY", True, "The last commanded plane above a group of vehicles. Every effect's authorizing admit is ordered here. A release seat, held by a person, is the only kind that reaches an irreversible entry. (ADR-0060, ADR-0066)"),
            ("AUTONOMOUS PLANE", False, "Seven replicas under Byzantine agreement, on the vehicles' governors. It grants leases and changes no authority, and its clock is its ticks. (ADR-0060, ADR-0061, ADR-0064)"),
            ("GOVERNOR", True, "The trusted part of a vehicle. It permits each entry under the lease against an exact count, with no further round. A vehicle that stops hearing its plane loses its lease at once. (ADR-0062)"),
            ("STACK", False, "Planning, perception, any model: Byzantine. It chooses which permitted entry, never whether. Nothing a peer originates enables anything. (ADR-0062, ADR-0065)"),
        ]),
    dict(
        id="survey", line="authority", status="solid", name="Survey line",
        tag="T · counts as of Genesis Checkpoint G11",
        lede="How the corpus says a claim was established. The four words are kept apart, and none of them is said "
             "of the running reference.",
        src="ADR-0046 §1, A1; ADR-0053 §1; diagrams/README.md (G11 counts)",
        stops=[
            ("SPECIFIED", False, "Written in TLA+. Thirty-one modules at G11."),
            ("CHECKED", False, "TLC ran mutations and witnesses at small constants. Also said of the floor's gates and of trace validation, 82 traces."),
            ("PROVED", False, "The TLA+ Proof System discharged the obligations: twenty-four proof modules, 5,416 obligations."),
            ("CERTIFIED", False, "Every obligation of a proof module is accounted for by a route an independent checker accepted. Twenty-one of the twenty-four."),
            ("PROVED IN LEAN", False, "The Lean kernel discharged it, of the encoding, transcription or statement it names. Never shortened to proved."),
        ]),
]


def strips_html():
    out = []
    for sp in STRIPS:
        svg = strip_svg(sp["id"], sp["line"], sp["status"], [(a, b) for a, b, _ in sp["stops"]],
                        river_after=sp.get("river_after"), loop=sp.get("loop"))
        start = 0 if sp["id"] == "pipeline" else 1
        items = "".join(
            '<li><span class="n">%d</span><div><b>%s</b><p>%s</p></div></li>' % (i + start, esc(tc(a)), esc(c))
            for i, (a, b, c) in enumerate(sp["stops"]))
        out.append("""
<article class="linecard" id="line-%s">
  <header>
    <span class="swatch sw-%s %s"></span>
    <h3>%s</h3>
    <span class="tag">%s</span>
  </header>
  <p class="lede">%s</p>
  <div class="scroller" tabindex="0" role="group" aria-label="%s, scrollable diagram">%s</div>
  <ol class="stops" start="%d">%s</ol>
  <p class="src">Read from %s.</p>
</article>""" % (sp["id"], sp["line"], sp["status"], esc(sp["name"]), esc(sp["tag"]), esc(sp["lede"]), esc(sp["name"]),
                 svg, start, items, esc(sp["src"])))
    return "\n".join(out)


def index_html():
    rows = []
    for lid, name, sub, status, _ in LINES:
        members = [s for s in S if s["lines"][0] == lid]
        if not members:
            continue
        stat = {"solid": "", "prov": " · provisional", "prop": " · Proposed"}[status]
        rows.append('<tr class="grp"><th colspan="5" scope="colgroup"><span class="swatch sw-%s %s"></span>%s line%s</th></tr>'
                    % (lid, status, esc(name), stat))
        for s in members:
            others = [LINE_NAME[l] for l in s["lines"][1:]]
            ch = (' <span class="chg">change for %s</span>' % esc(", ".join(others))) if others else ""
            rows.append('<tr id="ix-%s"><th scope="row">%s%s</th><td class="sq">%s</td><td>%s</td><td class="rec">%s</td><td>%s</td></tr>' % (
                s["id"], esc(tc(s["label"])), ch, grid_ref(s),
                esc(s["what"]), esc(s["record"]), esc(s["ref"])))
    return "\n".join(rows)


def chips_html():
    o = ['<button type="button" class="chip on" data-line="" id="chip-all">All lines</button>']
    for lid, name, sub, status, _ in LINES:
        o.append('<button type="button" class="chip" data-line="%s" id="chip-%s"><span class="swatch sw-%s %s"></span>%s</button>'
                 % (lid, lid, lid, status, esc(name)))
    return "\n".join(o)


# ------------------------------------------------------------------ outputs
def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote %s (%d bytes)" % (os.path.relpath(path, os.path.dirname(HERE)), len(text.encode("utf-8"))))


def standalone(svg, css):
    """An SVG that carries its own stylesheet. A viewer that loads no web font draws it in the fallback stack."""
    head, rest = svg.split(">", 1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n%s>\n<style>\n%s</style>%s\n' % (head, css, rest)


def main(argv):
    css = read("map.css")
    page = (read("page.tmpl.html").replace("{{MAPCSS}}", css.rstrip())
            .replace("{{MAP}}", map_svg())
            .replace("{{STRIPS}}", strips_html())
            .replace("{{INDEX}}", index_html())
            .replace("{{CHIPS}}", chips_html())
            .replace("{{NSTATIONS}}", str(len(S))))
    skeleton = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    write(os.path.join(OUT, "topak-diagram-of-lines-%s.html" % DATE), skeleton + page)
    write(os.path.join(OUT, "network-%s.svg" % DATE), standalone(map_svg(), css))
    for sp in STRIPS:
        svg = strip_svg(sp["id"], sp["line"], sp["status"], [(a, b) for a, b, _ in sp["stops"]],
                        river_after=sp.get("river_after"), loop=sp.get("loop"))
        write(os.path.join(OUT, "line-%s-%s.svg" % (sp["id"], DATE)), standalone(svg, css))
    if "--fragment" in argv:
        write(argv[argv.index("--fragment") + 1], page)


if __name__ == "__main__":
    main(sys.argv[1:])
