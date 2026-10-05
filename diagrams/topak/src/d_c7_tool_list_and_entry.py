"""C7 — A Thinker learns its tools from the mechanism, and the allowlist entry has one schema (ADR-0048, ADR-0049)."""
from lib import Canvas

ID, SLUG = "C7", "tool-list-and-entry"

H = "[[green|holds]]"
CE = "[[red|counterexample]] ✓"


def build():
    c = Canvas(ID, "A Thinker learns its tools from the mechanism, and the allowlist entry has one schema",
               "ADR-0049 states the allowlist entry once: **five parts**, keyed `name@digest`, each field marked "
               "**checked or claimed**, with ten load checks a bundle must pass to load at all. The entry is the **one "
               "statement of a Run tool's channel**: the tool host reads the target there (ADR-0034 A2, R4; ADR-0033 "
               "A9). ADR-0048 makes every entry carry an **interface**, and at grant the mechanism **renders the tool "
               "list** of the lease's revision, delivers it to the Thinker and **opens the round's topic with it**, so an "
               "Observer is given what its Thinker was told. The list is **the only description with standing**, and "
               "Run's ingress becomes a **closed list of four**. Both ratified in Batch 34; two conditions were restated "
               "first, W10 (G10 result 3) and a list narrowed to one tool, which a lease cannot carry (result 4).",
               3400, "ADR-0049 §1–§9, Findings 1–4, Options, R1–R4, B34; ADR-0048 §1–§8, Findings 1–6, Options, R1–R6, "
                     "B34; ADR-0022 §3, A3; ADR-0040 §3, A1; ADR-0043 §1, A1; ADR-0042 §3, §4, A1; ADR-0037 §2, A2; "
                     "ADR-0035 §1, R6 (Proposed); ADR-0034 §1 A2 (P4 for Run), R3, R4, §8; ADR-0042 §6; ADR-0025 §1 "
                     "(h), A2; ADR-0030 §4, A2; ADR-0031 §1, §4, R2; ADR-0047 §1, §3, §7; ADR-0045 Annex A T-0045-24, "
                     "T-0045-25, T-0045-34, Annex B, A1; ADR-0033 A8, A9, A10, A15; spec/ToolList.tla (7c0a18b897e6cb98), "
                     "ToolList-results-2026.10.04.txt (2875c9159cac8027), ToolList_proof.tla (c6b7ac1be332dfd6), "
                     "ToolList-proof-results-2026.10.04.txt, ToolList-proof-cert-results-2026.10.04.txt "
                     "(1397c5d11022cd96); policies/data.json; mechanism/crates/topak-bundle/src/allowlist.rs (check, "
                     "check_labels, tool_list, listed); topak-node/src/mechanism.rs (tool_list, open_round), "
                     "mechanism/launch.rs; topak-mcp/src/server.rs; topak-contain wasmtool; "
                     "mechanism/GAPS-AND-ASSUMPTIONS.md I13, I33, I44, I45, I46, G19; ToO rev 14 §2.9, §2.10; "
                     "G10 §2.5, §2.6, §3 (results 3, 4), §7 items 59, 84, 89, 90, 94, 95, §8")
    X0, X1 = c.x0, c.x1
    TW = X1 - X0
    y = c.y

    # ------------------------------------------------------------------ status line
    sx = X0
    c.text(sx, y + 16, "ADR-0048", 16, "ink", bold=True)
    sx += 92
    sx += c.status(sx, y, "accepted", "C4, C3 · Batch 34, at R6") + 20
    c.text(sx, y + 16, "ADR-0049", 16, "ink", bold=True)
    sx += 92
    sx += c.status(sx, y, "accepted", "C4; C2 for §5 · Batch 34, at R4") + 12
    sx += c.status(sx, y, "accepted", "dependent: ADR-0022 A3, 0025 A2, 0030 A2, 0037 A2, 0040 A1, 0042 A1, 0043 A1, "
                                      "0045 A1 · B34") + 12
    sx += c.status(sx, y, "built", "ADR-0033 A9 (B32), A10 (B34), A15 (B35)") + 14
    c.text(sx, y + 16, "No seat gains a variant. G10 item 59 discharged; item 84 closed.", 14, "muted")
    y += 56

    # ------------------------------------------------------------------ the flow
    c.heading(X0, y, "One entry, read three ways: by the tool host, by the renderer, and by the admit path", size=21)
    y += 48
    top = y
    aw, bw, cw, dw = 560, 520, 470, 640
    g = 90
    ax, bx = X0, X0 + 560 + g
    cx = bx + bw + g
    dx = cx + cw + g
    ex = dx + dw + g
    ew = X1 - ex
    a1 = c.card(ax, top, aw, "Bundle data, at `topak.tools`", [
        "Entries keyed `name@digest`, each for one domain, signed with the bundle (ADR-0044) and promoted with it.",
        "Beside them (ADR-0049 §7): `labels.vocabulary`, `labels.delivery` per seat kind, `labels.root`.",
        "**Every bundle was in the old form**: the move was a bundle change and a policy change together "
        "(`policies/data.json`, A10).",
    ], accent="violet", size=13.5)
    a2y = top + a1 + 30
    a2 = c.card(ax, a2y, aw, "The issued rules: two lists (ADR-0025 §1 (h), A2)", [
        "**Targets inside the deployment**: an entry reaching one is not outward.",
        "**Entries allowed to release a reserved label**, by name and digest.",
        "Each widens what a bundle may declare, so adding to either **is an issuance**. With neither issued, every "
        "entry with a channel is outward and none may release a reserved name.",
        "Since A15 the rules' well-formedness reads them (a releaser named by name and digest; an inside target not "
        "empty); **the rules floor bounds neither** (ADR-0026 is not amended).",
    ], accent="blue", size=13.5)
    a_bot = a2y + a2
    fh = a_bot - top
    c.card(bx, top, bw, "At load: W1 to W10, or the bundle does not load", [
        "Made **by the mechanism at load**, after the signature and before any decision counts (ADR-0030 A2).",
        "Checks on the data's shape; **no judgment**. Each refusal names its check (`allowlist.rs` `check`).",
        "**A bundle cannot waive them**, an issuance does not change them: a mechanism constant, changed only by a "
        "release. They are harder to change than the floor.",
        "W7 and W9 read the inside-target list; W8 reads the releasers. The full table is below.",
    ], accent="red", size=13.5, h=fh, tint=False)
    c.arrow([(ax + aw, top + a1 / 2), (bx, top + a1 / 2)], "violet", sw=2.4)
    c.arrow([(ax + aw, a2y + a2 / 2), (bx, a2y + a2 / 2)], "blue", sw=2.2, label="read once, at load", lpos=0.5,
            loff=(0, -18))
    c.card(cx, top, cw, "The allowlist of one revision", [
        "Kept per bundle revision; **a grant names the revision**, so a call is decided against the revision its "
        "lease names and the key it carries (ADR-0049 §2).",
        "`outward` is **derived and never declared**: a channel whose target the issued rules do not list as inside "
        "(§4). A bundle cannot mark its own entry as inside.",
        "A new bundle reaches a principal **at its next grant** (ADR-0031 R2): the list and the decisions cannot "
        "change inside a round.",
    ], accent="teal", size=13.5, h=fh)
    c.arrow([(bx + bw, top + fh / 2), (cx, top + fh / 2)], "teal", sw=2.4, label="well-formed", lpos=0.5,
            loff=(0, -18))
    c.label(bx + bw / 2, top + fh + 26, "not well-formed: refused, every reason named", "red", 13)

    readers = [
        ("1 · The tool host reads `channel.target` from the entry", "green", ("accepted", "ADR-0034 A2, R4"), [
            "Of the bundle revision the lease names, and **from nowhere else**. Node configuration says where a "
            "module is and what its bytes are, and **states no channel**: one declaration, nothing to disagree with it.",
            "A hosted tool whose entry declares no channel in that revision **is not run** (ADR-0033 A9, B32).",
        ]),
        ("2 · At grant, the mechanism renders the tool list", "blue", None, [
            "Every entry of the revision **for the seat's domain that the lease may call, and no other**, in one fixed "
            "form, mechanical and total: a syntactic lift (ADR-0007). No admit.",
        ]),
        ("3 · The admit path", "teal", None, [
            "`name` and `digest` **checked on every call**; `domain` (an `Invoke` of a Run entry, an `Actuate` of a "
            "Build entry, refused); `type` and `required` in the bundle tier; a handle's label against `accepts`.",
        ]),
    ]
    rh = [c.card(0, 0, dw, t, b, size=13.5, status=st[0] if st else None, status_extra=st[1] if st else "",
                 draw=False) for t, _, st, b in readers]
    rg = (fh - sum(rh)) / 2
    ry = top
    rpos = []
    for (t, a, st, b), h in zip(readers, rh):
        c.card(dx, ry, dw, t, b, accent=a, size=13.5, status=st[0] if st else None,
               status_extra=st[1] if st else "", h=h)
        rpos.append((ry, h))
        ry += h + rg
    spine = cx + cw + g / 2
    c.arrow([(cx + cw, top + fh / 2), (spine, top + fh / 2)], "teal", sw=2.4, head=False)
    c.line(spine, rpos[0][0] + rpos[0][1] / 2, spine, rpos[2][0] + rpos[2][1] / 2, "teal", sw=2.4)
    for (yy, h) in rpos:
        c.arrow([(spine, yy + h / 2), (dx, yy + h / 2)], "teal", sw=2.4)

    outs = [
        ("A Wasm tool with **one network capability**: a connection to that target", "green", [
            "No other socket; any other import refused before it runs. The capability binds the target; the "
            "protocol (`kind`) is recorded and not enforced. At the reference a **core module**, not a component "
            "(PROVISIONAL tool-abi, I44). A native tool's target stays an assertion (G19).",
        ]),
        ("The round topic's opening record, and the Thinker", "blue", [
            "Written **before any other record**, before the session exists: kind `open`, the list's digest and the "
            "bundle revision in its envelope, the list in its payload; **no admit and no sequence number** "
            "(ADR-0042 A1; I45). If it cannot be written no session is opened; a launched guest is destroyed.",
            "The Thinker gets the same list with its token; `topak mcp` passes it in its instructions; a session may "
            "ask again (`ToolList`), with no admit and the same answer all round. **An Observer reads it under** "
            "`W(p)`; its mark does not assert it read it.",
        ]),
        ("Admitted, or refused and recorded", "teal", [
            "A call the list did not name is refused at the allowlist, and every attempt is an ordinary admit "
            "(`ToldMatchesDecided`, below).",
        ]),
    ]
    oh = [c.card(0, 0, ew, t, b, size=13.5, draw=False) for t, _, b in outs]
    og = 24
    oy = top
    obot = top
    for i, ((t, a, b), h, (yy, rhh)) in enumerate(zip(outs, oh, rpos)):
        c.card(ex, oy, ew, t, b, accent=a, size=13.5, h=h)
        ry0, ry1 = yy + rhh / 2, oy + min(h / 2, 40)
        mid = dx + dw + g / 2 + (i - 1) * 14
        c.arrow([(dx + dw, ry0), (mid, ry0), (mid, ry1), (ex, ry1)], a, sw=2.4)
        oy += h + og
        obot = oy - og
    y = max(top + fh, obot, max(rp[0] + rp[1] for rp in rpos)) + 70

    # ------------------------------------------------------------------ the entry's schema
    half = (TW - 50) / 2
    c.heading(X0, y, "§1: one entry, five parts, stated here and nowhere else")
    c.heading(X0 + half + 50, y, "§4: each field is checked or claimed, and the entry says which")
    y += 42
    cols = [("Part", half * 0.14, {"bold": True}), ("Fields", half * 0.36, {"mono": False}),
            ("Domain", half * 0.1), ("Asked for by", half * 0.4)]
    t1 = c.table(X0, y, cols, [
        ["Identity", "`name`, `digest`, `domain`", "Both", "ADR-0022 §3; ADR-0040 §3"],
        ["Inputs", "For each input: `type`, `required`", "Both", "The bundle tier (ADR-0041 §5)"],
        ["Interface", "`purpose`; for each input, `note`", "Both", "ADR-0048 §1"],
        ["Labels", "`result.label`, `result.releases`; for each input, `destination`, `accepts`; `destinations: none`",
         "Run", "ADR-0047 §1, §3, §7"],
        ["Channel", "`channel.kind`, `channel.target`", "Run", "ADR-0040 §3; ADR-0034 A2"],
    ], size=13.5, accent="blue")
    ly = y + t1 + 14
    ly += c.para(X0, ly, half,
                 "**This record governs** where another describes a field, a form or a load check differently, whichever "
                 "was ratified first (R1). An entry is for one domain. **A Build entry has no channel and no labels**: "
                 "a channel on it contradicts hermeticity and the bundle does not load (ADR-0022 A3). Inputs are flat: "
                 "`string`, `number` or `boolean`; an unknown input is refused.", 13.5, "muted") + 16
    hcols = [("A handle names (§3)", half * 0.45), ("Form", half * 0.55, {"mono": True})]
    ly += c.table(X0, ly, hcols, [
        ["The result of an earlier `Actuate` in this round", '{"handle": {"actuate": <seq>}}'],
        ["A consulted object", '{"handle": {"consult": "<digest>"}}'],
    ], size=13.5, accent="amber") + 12
    ly += c.para(X0, ly, half,
                 "Told from a literal by shape, since every literal is a scalar. An input takes a handle only if its "
                 "`accepts` is not empty and the handle's label is within it; same round, same principal (C6).", 13.5,
                 "muted") + 16
    scols = [("Sibling data (§7)", half * 0.26, {"mono": True}), ("What it holds", half * 0.5),
             ("Decided by", half * 0.24)]
    ly += c.table(X0, ly, scols, [
        ["labels.vocabulary", "The finite set of names; the two reserved names are always in it", "ADR-0047 §1, §7"],
        ["labels.delivery", "For each seat kind, the table from label to `clear` or `handle`, total over the "
                            "vocabulary", "ADR-0047 §2"],
        ["labels.root", "The Run root's label, for the root or a named subset", "ADR-0047 §1"],
    ], size=13.5, accent="violet")
    rx = X0 + half + 50
    kcols = [("Field", half * 0.2, {"mono": True}), ("Read by", half * 0.32), ("Checked or claimed", half * 0.48)]
    t2 = c.table(rx, y, kcols, [
        {"cells": ["name, digest", "The admit path; the tool host", "**Checked** on every call"], "accent": "teal"},
        {"cells": ["domain", "The admit path", "**Checked** at admit"], "accent": "teal"},
        {"cells": ["type, required", "The bundle tier", "**Checked** at admit"], "accent": "teal"},
        {"cells": ["purpose, note", "The Listener, which renders them into the tool list",
                   "**Claimed.** Prose that passed promotion"], "accent": "amber"},
        {"cells": ["result.label", "The Listener, at delivery", "**Claimed**, and bounded: an outward entry must carry "
                                                                "`untrusted` (F4, W7)"], "accent": "amber"},
        {"cells": ["result.releases", "The label join (ADR-0047 §1)", "**Claimed**, and bounded: a reserved name needs "
                                                                     "the issued rules to name the entry (F5, W8)"],
         "accent": "amber"},
        {"cells": ["destination", "The lift, for F2 and F3", "**Claimed.** An input that carries a destination and is "
                                                             "not marked is not seen: **the weakest field** (finding 3)"],
         "accent": "red"},
        {"cells": ["accepts", "The admit path", "**Checked** at admit, against the handle's label"], "accent": "teal"},
        {"cells": ["channel.kind", "The tool list; the record", "**Claimed.** Recorded and not enforced (ADR-0034 A2)"],
         "accent": "amber"},
        {"cells": ["channel.target", "The tool host", "**Checked** where the host binds a Wasm tool's one socket to it; "
                                                      "**claimed** for a native tool (G19)"], "accent": "green"},
    ], size=13.5, accent="teal")
    ry2 = y + t2 + 16
    dg = c.card(rx, ry2, half, "§2: the digest, and what it does not cover", [
        "**An entry's** `digest` **is the SHA-256 of the tool artifact's digest joined with the canonical form of the "
        "entry's inputs part**, re-checked on every call: a change to the artifact or to an input is a new key.",
        "It does **not** cover the interface, the labels or the channel: declarations about the tool, fixed by the "
        "bundle's revision and signature. A corrected description is a promotion, not a new tool.",
        "[[red|Not followed at the reference]] (R4; G10 item 94; I13): it digests the schema the tool's own MCP "
        "server reports, and a Wasm tool's digest is its module's bytes alone. Nothing compares either with the "
        "entry's `inputs`. Carried as a debt; not among §9's conditions.",
    ], accent="red", size=13.5, tint=False)
    y = max(ly, ry2 + dg) + 60

    # ------------------------------------------------------------------ W1 to W10
    c.heading(X0, y, "§6: what makes a bundle's allowlist well-formed (the full table); at the reference each is seen "
                     "with a bundle built to fail it", size=21)
    c.status(X1, y + 3, "built", "allowlist.rs, 13 tests (A10)", anchor="end")
    y += 48
    wcols = [("", TW * 0.045, {"bold": True}), ("The bundle is refused when", TW * 0.42), ("From", TW * 0.12),
             ("Note", TW * 0.415)]
    y += c.table(X0, y, wcols, [
        ["W1", "An entry's key is not its `name` and `digest`, or its `domain` is missing", "§1", ""],
        ["W2", "An input lacks `type` or `required`, or the type is not one of the three", "§3", ""],
        ["W3", "`purpose` is empty, an input has no `note`, or either is over the size bound", "ADR-0048 §1",
         "The bound is a mechanism parameter; **its values are the reference's**: 1,024 bytes for `purpose`, 256 for "
         "a `note` (I33)"],
        ["W4", "A Run entry has no `channel`, or a `channel` lacks `kind` or `target`", "ADR-0040 §3; I33", ""],
        ["W5", "A Build entry has a `channel`", "§1", "ADR-0022 §3's hermeticity obligation as a check on the data (A3)"],
        ["W6", "A Run entry has no `result.label`, or any label name is outside the bundle's vocabulary",
         "ADR-0047 §1, F6", "The reference applies it to the root, `accepts` and the delivery table too"],
        ["W7", "An outward entry's `result.label` lacks `untrusted`", "ADR-0047 F4", "Reads the inside-target list"],
        ["W8", "`result.releases` holds a reserved name and the issued rules do not name the entry", "ADR-0047 F5",
         "Reads the releaser list"],
        ["W9", "An outward entry takes inputs and marks none as a `destination`, without saying it has none",
         "ADR-0047 F6", "`destinations: none` at the entry's top level, so an omission and a decision look different"],
        {"cells": ["W10", "**An entry or an input carries a field this record does not define, or a Build entry "
                          "carries any of the labels part** (R4). First written: `accepts` or `destination` on an input "
                          "the entry does not have", "§1, §3",
                   "**Restated before ratification** (G10 §3, result 3): in the entry's own form `accepts` and "
                   "`destination` sit inside the input they describe, so the first W10 **could not be failed**. A "
                   "misspelt or misplaced field is now not silently dropped"], "accent": "amber"},
        {"group": "Also refused at load at the reference, for ADR-0047 §1 and §2 (`check_labels`)", "accent": "violet"},
        ["—", "The Run root declares no label (`labels.root.label`)", "ADR-0047 F6", ""],
        ["—", "The delivery table has no row for `thinker` or for `observer`, or a row is not total over the "
              "vocabulary", "ADR-0047 §2",
         "**No row is asked for** `emergency`: a person on an emergency seat is then given handles (G10 result 6; "
         "item 92)"],
    ], size=13.5, accent="red") + 14
    y += c.para(X0, y, TW, "**W7 to W9 are how ADR-0047's F4 to F6 are checked** (R1): ADR-0047 §7 says what must be "
                "refused and why; this table is the definitive form. Seven of the entry's fields are claims, bounded in "
                "three places by these checks (finding 1): the allowlist is where a deployment's honesty is "
                "concentrated.", 13.5, "muted") + 50

    # ------------------------------------------------------------------ the tool list
    c.heading(X0, y, "ADR-0048: the interface, the list, and Run's closed list of four")
    y += 42
    w3 = (TW - 2 * 40) / 3
    icols = [("Part", w3 * 0.22, {"bold": True}), ("What it is", w3 * 0.44), ("Checked by anything?", w3 * 0.34)]
    i1 = c.table(X0, y, icols, [
        ["Name and digest", "As before (ADR-0022 §3; ADR-0040 §3)", "Yes: the admit path"],
        ["Inputs", "Each input's name and type", "Yes: the bundle tier"],
        ["Purpose", "One text field: what the tool does and what it returns", "**No.** A claim, as a channel "
                                                                              "declaration is"],
        ["Input notes", "One text field per input: what it means", "**No**"],
        ["Channel, in Run", "Its kind, and whether the entry is outward", "The channel's owner (ADR-0034 A2)"],
        ["Labels", "Result label, destination inputs, what each input accepts by handle", "The load checks (F4 to F6)"],
    ], size=13.5, accent="blue")
    iy = y + i1 + 12
    iy += c.para(X0, iy, w3,
                 "**§1**: the text is in the bundle, not behind a reference: one signature covers the entry and its "
                 "text. It is bounded in size; an entry with no purpose does not load (W3). **The interface has no "
                 "digest of its own**: it is fixed by the bundle revision every grant names.", 13.5, "muted")
    qx = X0 + w3 + 40
    qcols = [("Item", w3 * 0.24, {"bold": True}), ("Source", w3 * 0.26), ("Delivered", w3 * 0.24),
             ("On the record", w3 * 0.26)]
    q1 = c.table(qx, y, qcols, [
        ["The task", "The grant (a seating, a `Regrant`)", "**Always clear**, with its label",
         "Digest and label on the log; bytes in the opening record"],
        ["Consulted content", "The Run root", "Clear or a handle, by its label", "The `Consult` admit"],
        ["Tool results", "The allowlist entry", "Clear or a handle, by its label", "The `Actuate` record"],
        {"cells": ["**The tool list**", "The bundle revision, narrowed by the lease", "**Always clear**; neither "
                   "reserved name", "**The opening record**"], "accent": "blue"},
    ], size=13.5, accent="teal")
    qy = y + q1 + 12
    qy += c.para(qx, qy, w3,
                 "**Run's ingress is a closed list of four** (ADR-0043 A1; ADR-0042 A1). Two ratified records had said "
                 "three, and \"nothing else\": the list stays closed and the sentence changes, which is why ADR-0048 "
                 "is **C3** on the drafter's reading. In Build the list is the task, the admitted `Read` content and the "
                 "tool list (ADR-0037 A2), and **a Build round's list is** `ingress` **and** `consumed` for lineage "
                 "(ADR-0035 R6, Proposed). Labels on each: C6.", 13.5, "muted")
    zx = X0 + 2 * (w3 + 40)
    z1 = c.card(zx, y, w3, "§3: the mechanism's list is the only description with standing", [
        "**A Thinker's tools are the ones on its list**, named as the list names them; the list supplies the name and "
        "digest an `Actuate` or `Invoke` must carry.",
        "**What a Persona, a task or a consulted object says about a tool is content**: the mechanism does not read "
        "it and no admit turns on it. A task says what to do; the list says what there is to do it with.",
        "**No tool supplies text at run time**, so the MCP \"rug-pull\" cannot happen; a description carrying an "
        "injection now has to **pass promotion**. Promoting a tool no longer makes a Persona stale.",
        "Purpose text is still **a claim**: a tool described as read-only that writes is detected by nothing here "
        "(§5).",
    ], accent="blue", size=13.5)
    y = max(iy, qy, y + z1) + 36

    lcols = [("What the rendered list holds, per entry (I45)", w3 * 0.5), ("Not in it", w3 * 0.5)]
    l1 = c.table(X0, y, lcols, [
        ["`name`, `digest`, `purpose`, each input's `type`, `required`, `note`",
         "Entries of another domain, or that the lease may not call"],
        ["In Run: the labels part, and the channel as `{kind, outward}`", "**The channel's target**: a Thinker needs to "
                                                                          "know a call leaves the deployment, not where "
                                                                          "to (drafter's choice)"],
        ["`{bundle, domain, tools}`, tools in key order; its digest over the canonical JSON",
         "Anything a principal wrote: it cannot write the record"],
    ], size=13.5, accent="blue")
    l1y = y + l1 + 12
    l1y += c.para(X0, l1y, w3, "**The rendering's form is the reference's** (I45; ADR-0048's open obligation). It is not "
                  "an effect and is not counted against `R`.", 13.5, "muted")
    ccols = [("What changes", w3 * 0.36), ("Where", w3 * 0.18), ("How", w3 * 0.24), ("When", w3 * 0.22)]
    c1 = c.table(qx, y, ccols, [
        ["An entry's purpose text or input notes", "Bundle data", "Bundle promotion, signed", "At a principal's next "
                                                                                             "grant"],
        ["Which entries a lease may call", "The lease", "Per grant", "That round"],
        ["The rendering; the size bound", "Mechanism", "A mechanism release", "At deployment"],
    ], size=13.5, accent="blue")
    c1y = y + c1 + 12
    c1y += c.para(qx, c1y, w3, "**§4: how it changes.** Promotion is as strong as its gates, and at the reference gate "
                  "evidence is an operator's assertion (G10 §8).", 13.5, "muted")
    n1 = c.card(zx, y, w3, "A lease cannot be narrowed to a tool (R6; G10 result 4, item 95)", [
        "§2 says the list is the allowlist \"narrowed by that lease\". **ADR-0031 §1's lease schema is closed and "
        "carries no tool set**, so the behaviour first asked for, \"a lease narrowed to one tool is given a list of "
        "one\", could not be shown.",
        "What is shown: a lease whose alphabet lacks the variant that names a tool is given **a list of none**, and a "
        "list holds only entries the deployment's allowlist admits. At the reference the narrowing is the parameters' "
        "tools for the domain when the alphabet holds `Invoke` or `Actuate` (I45).",
        "**Whether a lease should carry a tool set is ADR-0031's question, left open.**",
    ], accent="red", size=13.5, status="open", status_extra="item 95", tint=False)
    y = max(l1y, c1y, y + n1) + 60

    # ------------------------------------------------------------------ ToolList.tla
    c.heading(X0, y, "§8: `spec/ToolList.tla` (`7c0a18b897e6cb98`): 27 TLC rows; five properties proved, 215 "
                     "obligations, certified", size=21)
    c.status(X1, y + 3, "accepted", "ADR-0046 · ADR-0048 R4", anchor="end")
    y += 48
    pw = 0.36 * TW
    pcols = [("Property", pw * 0.36, {"mono": True}), ("Over", pw * 0.64)]
    pt = c.table(X0, y, pcols, [
        ["ToolListIsExact", "Under a live lease the Thinker was told the allowlist of the granted revision, narrowed "
                            "by the lease: no more and no fewer"],
        ["ToldMatchesDecided", "No admitted call names a tool the Thinker was not told of, and no call is refused for "
                               "one it was told of: **over what it was actually told** (ghost)"],
        ["ListFixedForRound", "Under a live lease, what the Thinker was told is what it was told at the grant"],
        ["OpeningRecordFirst", "No effect is recorded on a round's topic before its opening record"],
        ["OpenedListIsTold", "The list in the opening record is the list the Thinker was told: the Observer reads "
                             "what the Thinker was given"],
    ], size=13.5, accent="teal")
    py = y + pt + 14
    py += c.para(X0, py, pw,
                 "Two bundle revisions with different allowlists (revision 1 allows `t1`, `t2`; revision 2 allows "
                 "`t2`, `t3`), so that **a promotion in the middle of a round** changes which tools exist. The Thinker "
                 "is havoc: it calls any tool, told or not. One principal, any number of rounds. The lease's narrowing "
                 "is modelled as any set of tools, which ADR-0031's lease does not carry (R6). **Not modelled**: the "
                 "rendering and its size bound; purpose text; every reason for refusal other than the allowlist.",
                 13.5, "muted") + 16
    pr = c.card(X0, py, pw, "The proof: `ToolList_proof.tla` (`c6b7ac1be332dfd6`)", [
        "All five **proved**, with **no assumption**: 215 obligations (ADR-0048 R4).",
        "**Certified** (ADR-0046 A1): 133 closed by the prover's normalization, 75 by SMT with a proof the `ethos` "
        "checker accepted, **7 temporal steps by LS4, which no checker confirms**.",
        "The module **found no fault in the record**. `ToolListIsExact` alone is a function of the grant; what a model "
        "can test is a round in which a bundle is promoted.",
        "**A certified proof is not a verified one.** At the reference the module is tied by tests (e2e "
        "`the_tool_list_is_delivered_and_opens_the_round`), by no trace; the binding table has no row for it (G10 "
        "item 90).",
    ], accent="teal", size=13.5, status="accepted", status_extra="certified")
    left_bot = py + pr
    ky = left_bot + 24
    for t, a, st, b in [
        ("What the reference does not follow, of records in force (G10 item 94)", "red", None, [
            "**ADR-0049 §2's digest** over the entry's inputs: the reference digests what the tool's own server "
            "reports, or a Wasm module's bytes (I13).",
            "**The two issued lists are read once**, from the genesis rules, when bundles load: an issuance that changes "
            "them does not re-check a bundle already loaded (I46; ADR-0033 A15).",
            "Also open: two comments under `policies/` still call ADR-0049 Proposed, and a comment there is part of "
            "the bundle's revision (item 98).",
        ]),
        ("Degeneracies", "grey", None, [
            "**D-0048-1**: the tool list not delivered; a Thinker learns its tools from its Persona, its task or a "
            "consulted object. Falsifies: a Thinker's description of a tool is bound to the entry's name and digest. "
            "**Voids no theorem**; no type change. The reference until 2026.10.05.",
            "**ADR-0049 adds none**: an entry that lacks a part is the degeneracy of the record that asks for it "
            "(D-0047-1, D-0048-1, D-0034-5, D-0034-6).",
        ]),
    ]:
        ky += c.card(X0, ky, pw, t, b, accent=a, size=13.5, tint=(a == "grey")) + 20
    left_bot = ky - 20
    tx = X0 + pw + 40
    tw = X1 - tx
    tcols = [("Row", tw * 0.07, {"mono": True}), ("Mutation", tw * 0.16, {"mono": True}),
             ("Property", tw * 0.2, {"mono": True}), ("Result", tw * 0.16), ("What it shows", tw * 0.41)]
    rows = [
        {"group": "ADR-0048 as revised at R4", "accent": "teal"},
        ["safe", "none", "Safe", H + " (514 states)", "All five at once"],
        {"group": "`M_RECOMPUTE`: a promotion re-delivers the list from the new revision to a live round",
         "accent": "red"},
        ["rc1", "M_RECOMPUTE", "ToolListIsExact", CE, ""],
        ["rc2", "M_RECOMPUTE", "ToldMatchesDecided", CE, "The Thinker is told of a tool its calls are not decided "
                                                         "against"],
        ["rc3", "M_RECOMPUTE", "ListFixedForRound", CE, ""],
        ["rc4", "M_RECOMPUTE", "OpenedListIsTold", CE, "The Observer's list is no longer the Thinker's"],
        ["rc5", "M_RECOMPUTE", "OpeningRecordFirst", H, "…and nothing else breaks"],
        {"group": "`M_WIDE`: the list ignores the lease's narrowing", "accent": "grey"},
        ["wd1", "M_WIDE", "ToolListIsExact", CE, ""],
        ["wd2", "M_WIDE", "ToldMatchesDecided", CE, "A Thinker told of tools another lease holds"],
        ["wd3–wd5", "M_WIDE", "ListFixedForRound · OpenedListIsTold · OpeningRecordFirst", H + " each", ""],
        {"group": "`M_DECIDELATEST`: a call is decided against the latest revision, not the lease's", "accent": "grey"},
        ["dl1", "M_DECIDELATEST", "ToldMatchesDecided", CE, "**Breaks this one and nothing else**, as the module "
                                                            "says it must"],
        ["dl2–dl5", "M_DECIDELATEST", "ToolListIsExact · ListFixedForRound · OpenedListIsTold · OpeningRecordFirst",
         H + " each", ""],
        {"group": "`M_LATE`: the opening record is written when the mechanism gets to it, not at the grant",
         "accent": "grey"},
        ["lt1", "M_LATE", "OpeningRecordFirst", CE, "An effect on the topic before the list: **this one and nothing "
                                                    "else**"],
        ["lt2–lt5", "M_LATE", "ToolListIsExact · ToldMatchesDecided · ListFixedForRound · OpenedListIsTold",
         H + " each", ""],
        {"group": "Witnesses, each of which must be violated", "accent": "green"},
        ["w1", "none", "NeverPromotedMidRound", CE, "A bundle is promoted in the middle of a round: the case the "
                                                    "properties are about"],
        ["w2", "none", "NeverNarrowed", CE, "A lease narrows its allowlist"],
        ["w3", "none", "NeverAdmitted", CE, "A call is admitted"],
        ["w4", "none", "NeverRefused", CE, "A call is refused"],
        ["w5", "none", "NeverNewList", CE, "The next round is told the new revision's tools"],
        ["w6", "none", "NeverRefusedNewTool", CE, "A tool in the latest revision is refused under a lease on the old "
                                                  "one: a promotion does not reach a live round"],
    ]
    tt = c.table(tx, y, tcols, rows, size=13.5, accent="teal")
    y = max(left_bot, y + tt + 12) + 60

    # ------------------------------------------------------------------ the trusted base
    c.heading(X0, y, "The trusted base: who holds a tool to its channel, and who renders the list (ADR-0045 Annex A, "
                     "with B30 and A1)", size=21)
    y += 48
    kcols = [("Id", TW * 0.065, {"bold": True}), ("Component", TW * 0.15), ("Layer", TW * 0.075),
             ("Trusted for", TW * 0.17), ("Class", TW * 0.1), ("Failure can produce", TW * 0.14),
             ("Identity fixed by", TW * 0.1), ("Residual", TW * 0.2)]
    y += c.table(X0, y, kcols, [
        ["T-0045-24", "A Run tool's declared effect channel (ADR-0040 §3; G19)", "toolchain", "Nothing",
         "**delegated** to T-0045-25 for a Wasm tool; excluded for a native one (B30)", "—",
         "The entry, in the granted revision (ADR-0049 §5)",
         "The target is an address and the protocol on it is unchecked. A native Run tool is D-0034-5 or D-0034-6"],
        ["T-0045-25", "The tool host (ADR-0042 §6)", "mechanism-boundary", "Runs the allowlisted binary at the pinned "
                                                                            "digest, and nothing else; **since B30, holds "
                                                                            "a Run tool to its declared channel**",
         "trust root", "A tool run that is not the allowlisted one: the envelope collapses (ToO A2)",
         "Promotion: part of the release", "For Run, where the effect channels open"],
        {"cells": ["T-0045-34", "Handle resolution in the tool host, and **the rendering of the tool list** (ADR-0048 "
                                "§2)", "mechanism-boundary", "A handle resolves to the item the record names; **the list "
                                                             "rendered is the allowlist of the granted revision narrowed "
                                                             "by the lease**", "trust root",
                   "Suppressed bytes reaching the wrong tool; **a Thinker told of a tool it may not call, or not told "
                   "of one it may**", "Promotion: part of the release, with T-0045-25",
                   "**Purpose text is prose that passed promotion and nothing checks it** (ADR-0048 §5)"],
         "accent": "blue"},
    ], size=13, accent="blue") + 14
    c.para(X0, y, TW, "**At the reference** (Annex B): T-0045-34 has an instance since 2026.10.05, and **the list's "
           "rendering is the reference's own** (I45). **T-0045-24 is still excluded there**, for a reason that ended "
           "with ADR-0033 A9: the target is now read from the entry, not from node configuration, and moving the row "
           "is ADR-0045's to do (G10 item 89). A Wasm tool there is a core module, not a component (I44). **One hand**: "
           "both records drafted 2026.10.03, built and ratified 2026.10.05; **not reviewed by a reader other than the "
           "drafter** (ADR-0029 A2.5; G10 §8).", 13.5, "muted")
    return c
