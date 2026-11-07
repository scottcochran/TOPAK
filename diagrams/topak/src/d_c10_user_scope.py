"""C10 — A call's user scope is downstream (ADR-0056, Proposed). The mechanism binds the subject from the grant, the
policy decides whether a call may use it, the downstream system decides what it permits, and the tool decides
nothing."""
from lib import Canvas, STATUS, text_width

ID, SLUG = "C10", "user-scope"

W = 3400
STATE_56 = ("State of record: Genesis Checkpoint G11 (2026.10.09), with Batches 38 and 39 · narrative: Theory of "
            "Operation rev 15 · drawn 2026.11.06 for ADR-0056 (Proposed, 2026.11.06)")


def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
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


def build():
    c = Canvas(ID, "A call's user scope is downstream: the mechanism binds the subject, the policy decides whether, "
               "the downstream system decides what, and the tool decides nothing",
               "A Run tool that reads \"the current user's documents\" reaches a system that authorizes by user, and "
               "**the corpus has no record of whose scope a call uses**. The entry declares where a tool connects "
               "(ADR-0049 §5) and nothing about the credential it presents. ADR-0056 answers OWASP LLM06:2025's "
               "mitigation 5 and example 5. **Carrying the user's scope in the lease would be wrong ⟨U1⟩. Leaving the "
               "binding to the model would be worse ⟨U2⟩.** A subject travels with the grant, beside the lease, "
               "evidenced by its provider and fixed for the round. **ADR-0056 is Proposed and nothing here is in "
               "force or built**: no dependent entry is drafted, and no module, floor stage or reference addendum "
               "exists.",
               W, "ADR-0056 provenance (⟨U1⟩, ⟨U2⟩), Status note, Context, Decision §1–§11 (§1's table, §3's two "
               "tables, §4's table, §8's table, §9's table), Options, Consequences, Findings 1–5, Open obligations, "
               "History; OWASP LLM06:2025 Excessive Agency (mitigations 5 and 7, common example 5), as ADR-0056 "
               "cites them; ADR-0045 Annex A T-0045-25, T-0045-35; ADR-0049 §1, §5, §6 (W1–W10); ADR-0050 §3, §5 "
               "(provisional, B34); ADR-0031 §1, A2, A3; ADR-0047 §1, F2; ADR-0048 §2; ADR-0025 §1 (f), A3; "
               "ADR-0030 (`bundle ⊑ floor`); ADR-0007; ADR-0003; ADR-0028; ADR-0037; ADR-0054 §2 (Proposed); "
               "floor/proposed/README.md (the `workflow` stage's `R8`, `R9`); ToO rev 15 §13; A3's boundary register "
               "(B2)", state=STATE_56)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    for lab, key, extra in [
            ("ADR-0056", "proposed", "C1, C2 · drafted 2026.11.06"),
            ("its dependent entries (§11)", "notdrafted", ""),
            ("rests on ADR-0050 §3, §5", "provisional", "Batch 34"),
            ("ADR-0054 §2's activation", "proposed", "if ratified first"),
            ("the module (§11)", "notwritten", ""),
            ("floor stage `subjects`", "notbuilt", ""),
            ("the reference, ADR-0033 addendum", "notbuilt", "")]:
        lw = text_width(lab, 13.5, True) + 8
        plab = {"notdrafted": "Not drafted", "notwritten": "Not written"}.get(key)
        if plab:
            pw = text_width(plab, 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if plab:
            px += c.pill(px, y, plab, "red", 11.5, dash="2 3") + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian settled two things: **a user's "
                "scope is enforced downstream and not carried in the lease ⟨U1⟩**, and **which user a call acts for is "
                "decided by the mechanism and the policy, not by the model ⟨U2⟩**. The custodian asked whether the tool "
                "should decide. That the tool decides nothing is the drafter's answer (§1), and so is every other "
                "choice. **C1** applies because a subject-bound credential is a new route by which an admitted call "
                "carries authority that is not the deployment's own. **C2** applies to §5: the tool host's premise "
                "widens. **Every clause the mechanism applies subtracts, except binding a subject at grant**, whose "
                "authority is the subject's provider's. One author, one day.", 14.5, "muted") + 34

    # ================================================================== band 1: the problem, and four owners
    y = band(c, X0, y, "Four questions, four owners (Context; §1)", status="proposed")
    top = y
    g = 50
    wl = 900
    wr = WW - wl - g
    xr = X0 + wl + g

    bot_l = stack(c, X0, top, wl, [
        ("Today, a deployment has two choices, and both are bad", [
            "**One service identity that can reach every user's data.** This is LLM06's example 5, a generic "
            "high-privileged identity standing in for the user.",
            "**The tool picks a user's credential from something it was given**, usually an input the Thinker wrote. "
            "**This is the worse failure, and the admit path cannot see it.** An injected Thinker names another user, "
            "and the downstream system honours it. ADR-0047's F2 refuses a literal destination after untrusted "
            "reads. **A subject is not a destination, and nothing marks it.**",
        ], "red", {"tint": False}),
        ("Where the scope is enforced is not the problem ⟨U1⟩", [
            "The membrane decides what crosses. What the downstream system does with a call it receives is **its own "
            "authorization**, as LLM06's mitigation 7 asks.",
            "**A per-user credential can only make an admitted call do less.** It weakens no theorem, and none needs "
            "to rest on it.",
            "**Not in the lease**: every lease field is authority the mechanism grants and can check (ADR-0031 §1). "
            "A user's rights in a third-party system are neither.",
        ], "green", {}),
        ("The problem is the binding: who decides which user ⟨U2⟩", [
            "**A wrong binding adds authority**: another user's. By ADR-0045 §2's test, whatever decides it must be "
            "checked, or be a trust root with an issued identity.",
            "**A model is neither**, and a tool's behaviour is a claim (ADR-0049 §4). So the binding is **a syntactic "
            "lift from something on the record** (ADR-0007).",
            "**The corpus already has the shape**: ADR-0050 §3 binds an operator to a provider's assertion naming the "
            "fence; ADR-0050 §5 carries the task and its label with the grant, beside the lease.",
        ], "amber", {"tint": False}),
    ], gap=18, size=14)

    cols = [("Question", wr * 0.2, {"bold": True}), ("Decided by", wr * 0.22), ("How", wr * 0.36),
            ("Class", wr * 0.22)]
    rows = [
        {"cells": ["**Which user** does this round act for?", "**The mechanism**",
                   "A syntactic lift from a provider-signed assertion carried with the grant (§2). Fixed for the round",
                   "[[teal|Checked at grant]]"], "accent": "teal"},
        {"cells": ["**May** this call use that user's credential?", "**The policy**",
                   "The floor's minimum (§4), and the bundle may narrow on the subject's attributes. It never widens "
                   "(ADR-0030)", "[[teal|Checked at admit]]"], "accent": "teal"},
        {"cells": ["**What** may the credential do downstream?", "**The downstream system**",
                   "Its own authorization, on the subject the credential names",
                   "[[grey|Outside the pattern, by position ⟨U1⟩]]"], "accent": "grey"},
        {"cells": ["**Which credential** does the tool present?",
                   "**Nobody**: the tool host injects the one credential for the round's subject (§5)",
                   "The tool is handed exactly one credential and has no means to obtain another",
                   "[[brown|The tool host's premise (T-0045-25, widened)]]"], "accent": "brown"},
    ]
    c.text(xr, top + 16, "**§1's table, whole**", 16, "ink")
    t1 = c.table(xr, top + 32, cols, rows, size=14.5, accent="teal")
    ty = top + 32 + t1 + 30
    h_tool = row_cards(c, xr, ty + 32, wr, 24, [
        ("A tool that chooses must hold every subject's credential", [
            "That is the generic high-privileged identity of LLM06's example 5, **moved from the network to the tool's "
            "memory**.",
        ], "red", {"tint": False}),
        ("A tool's behaviour is a claim", [
            "The digest pins its code, not what it does with its inputs (ADR-0049 §2, §4). **A choice made inside it "
            "is made past the membrane, off the record.**",
        ], "red", {"tint": False}),
        ("A tool's choice is steered by its inputs", [
            "Its inputs are the Thinker's. **Letting the tool choose is letting the model choose, one step removed.**",
        ], "red", {"tint": False}),
    ], size=14)
    c.text(xr, ty + 16, "**The tool decides nothing** (drafter's choice; the custodian asked): three reasons", 15,
           "ink")
    y = max(bot_l, ty + 32 + h_tool) + 80

    # ================================================================== band 2: the flow
    y = band(c, X0, y, "A round that acts for a user, end to end (§2, §4–§7)", status="proposed",
             extra="nothing here is built")
    ftop = y + 30
    gap = 170
    cw = [400, 400, 600, 470, 330]
    cw.append(WW - sum(cw) - 5 * gap)
    cx = [X0]
    for w_ in cw[:-1]:
        cx.append(cx[-1] + w_ + gap)
    S = 13.5

    # ---- column 1: the user's side (row A and below)
    U = ("The user: a subject, not a principal", [
        "**No seat, no lease, no alphabet**, and never promoted (§2). ADR-0037's one-seat-per-principal rule is "
        "untouched.",
        "The party whose downstream authority a round's calls may use.",
        "**Must be present at grant**: a user who is not cannot be acted for (finding 2).",
    ], "grey")
    P = ("A subject provider · T-0045-38", [
        "**Its key is on the issued rules' list of subject providers** (ADR-0025 §1 (f); A2, owed).",
        "**A trust root for the subjects it vouches for, and for no others**, as an operator's provider is "
        "(T-0045-35). One provider may serve both.",
    ], "brown")
    A = ("The subject assertion", [
        "Names **the subject**, **the provider** and **the fence of the grant it is presented for**.",
        "**No wall clock is read: freshness is the fence.**",
        "Its form is open: an OIDC ID token with a nonce bound to the fence, or a token-exchange request (Open "
        "obligations).",
    ], "amber")

    # ---- column 2: who submits; the Thinker
    SUB = ("Whoever submits the grant", [
        "A seating's quorum, or an operator's `Regrant` (ADR-0050 §5).",
        "**Cannot name a subject without that subject's assertion.** So an operator cannot act as an arbitrary user, "
        "and the subject is attributed to its provider's signature, not to the operator's word.",
    ], "brown")
    TH = ("The Thinker", [
        "**Sees the tool list**, which shows each entry's `credential.mode` and `scope`, so it knows a call acts as "
        "its user. **It does not show the subject** (ADR-0048 §2, owed).",
        "**Never sees the assertion or the credential**: neither is ingress, and the Listener never delivers them.",
        "**The task may name the user. That is content.** So may any input.",
    ], "amber")

    # ---- column 3: the mechanism
    GR_L = ("The lease", ["**Closed field set, unchanged** (ADR-0031 §1). No thirteenth field ⟨U1⟩."], "teal")
    GR_T = ("The task and its label", ["Beside the lease (ADR-0050 §5; ADR-0031 A3)."], "blue")
    GR_S = ("The subject: at most one", ["Beside the lease, as the task is (§2; ADR-0031 A3, owed)."], "amber")
    CG = ("[[green|①]] Checked at grant", [
        "The assertion **verifies under a listed provider key** and **names this grant's fence**. Otherwise the grant "
        "is [[red|refused]].",
        "**The seating bounds it**: whether its rounds may carry a subject, and from which providers. A grant outside "
        "that bound is [[red|refused]]. **A quorum decides that a seat acts for users. One operator cannot.**",
        "**Fixed for the round**: not added, changed or dropped inside it. Two users are two rounds.",
        "**Ends with the round**: the lease's `ttl` bounds it (ADR-0031 A2). Nothing is refreshed inside a round.",
    ], "teal")
    CA = ("Checked at admit (§4)", [
        "**The lift adds to `RunCtx`**, from the grant: `subject.present`, `subject.provider`, `subject.attributes`; "
        "**to the tool**: `credentialMode`, `subjectProviders`. Mechanical and total (ADR-0007).",
        "**`R10`** forbids a `subject` call in a round with no subject. **`R11`** forbids one whose provider the entry "
        "does not accept.",
        "**The bundle may narrow on `subject.attributes`**. By `bundle ⊑ floor` it only denies more: **a provider's "
        "claim can subtract authority, and never add it.**",
        "**No floor entry looks for a subject in the inputs.** Telling whether free text names a user is a judgment.",
    ], "teal")
    RC = ("What reaches the record (§7)", [
        "**The grant record**: the subject's provider and **a digest of its identifier**. An authority fact, so it is "
        "**in the forensic floor and survives erasure** (ADR-0028).",
        "**The assertion's bytes** are in the round's payload, **inside the unit of erasure** (ADR-0003).",
        "**Every `Actuate` on a `subject` entry is attributable to the subject** through its round's grant. The admit "
        "record gains no field.",
        "**An Observer and the correlator read the digest**, as they read every grant fact.",
    ], "teal")

    # ---- column 4: the tool host
    TS = ("A token service that mints for the downstream system", [
        "Part of **T-0045-39**: excluded. No theorem rests on it.",
    ], "grey")
    HO = ("[[green|②]] The tool host · T-0045-25, widened", [
        "**At each `Actuate` on a `subject` entry**, obtains the credential for **the round's subject** and presents "
        "it on the tool's one channel.",
        "**Exchange, not storage** (drafter's choice): the round's assertion is exchanged for a credential scoped to "
        "that subject, so **no standing per-user credential exists at rest**.",
        "For `service`, it injects the entry's service credential. For `none`, nothing.",
        "**Newly trusted to present only the round's subject's credential**, beside running only the allowlisted "
        "binary and binding its socket (ADR-0034 A2).",
    ], "brown")

    # ---- column 5: the tool
    TO = ("The tool", [
        "**Receives exactly one credential** and **no means to obtain another**.",
        "**Decides nothing.** Its behaviour is a claim; the digest pins its code (ADR-0049 §4).",
        "A Thinker's input naming another user reaches it as content.",
    ], "grey")

    # ---- column 6: downstream
    DS = ("[[green|③]] The downstream system", [
        "**Authorizes on the subject its credential names, and never on a subject named in the request.**",
        "**An assumption of use, stated as one** (§6; ToO §13, owed). It closes the free-text path that §4 leaves open.",
        "**A Thinker may write any user's name into an input. The downstream system acts for the user in the token.**",
        "What it permits is its own: **T-0045-39, excluded** ⟨U1⟩.",
    ], "grey")

    def mh(spec, w_, **k):
        return c.card(0, 0, w_, spec[0], spec[1], draw=False, size=S, **k)

    # Row A: user/provider/assertion | submitter | the grant | token service
    # The grant is a region holding three small cards.
    gpad = 20
    giw = cw[2] - 2 * gpad
    hgl, hgt, hgs = mh(GR_L, giw), mh(GR_T, giw, status="provisional"), mh(GR_S, giw, status="proposed")
    hgrant = 52 + hgl + 12 + hgt + 12 + hgs + gpad
    hu, hp_, ha = mh(U, cw[0]), mh(P, cw[0]), mh(A, cw[0], status="proposed")
    hsub = mh(SUB, cw[1])
    # rows: user (A0) above the provider (A1) above the assertion (A2); the grant sits level with the provider
    yu = ftop + 60
    yp = yu + hu + 70
    ya = yp + hp_ + 70
    yg = yp
    ycg = max(yg + hgrant + 70, ya)
    hcg = mh(CG, cw[2])
    hca = mh(CA, cw[2])
    hrc = mh(RC, cw[2])
    yca = ycg + hcg + 70
    yrc = yca + hca + 70
    # the call lane is level with the admit card
    hth, hho, hto, hds = mh(TH, cw[1], status="proposed"), mh(HO, cw[3], status="proposed"), mh(TO, cw[4]), mh(DS, cw[5])
    lane = yca + hca / 2
    yth = lane - hth / 2
    yho = yca
    yto = lane - hto / 2
    yds = lane - hds / 2
    hts = mh(TS, cw[5])
    yts = yg
    ysub = yg

    # regions
    c.region(cx[0] - 24, yu - 50, cw[0] + 48, ya + ha - yu + 50 + 30, "The user's side", "brown", dash="10 6")
    mreg_top = yg - 50
    mreg_bot = yrc + hrc + 30
    c.region(cx[2] - 24, mreg_top, cw[2] + 48, mreg_bot - mreg_top, "B2 · The mechanism: grant and admit", "teal",
             dash=None)
    ds_top = yts - 50
    ds_bot = max(yds + hds, yts + hts) + 30
    c.region(cx[5] - 24, ds_top, cw[5] + 48, ds_bot - ds_top, "Outside the pattern ⟨U1⟩ · T-0045-39", "grey")

    c.card(cx[0], yu, cw[0], U[0], U[1], accent=U[2], size=S, tint=False)
    c.card(cx[0], yp, cw[0], P[0], P[1], accent=P[2], size=S)
    c.card(cx[0], ya, cw[0], A[0], A[1], accent=A[2], size=S, status="proposed")
    c.card(cx[1], ysub, cw[1], SUB[0], SUB[1], accent=SUB[2], size=S, tint=False)
    # the grant
    gx = cx[2]
    c.rect(gx, yg, cw[2], hgrant, "teal", tint=False, sw=2)
    c.text(gx + gpad, yg + 32, "**The grant** carries, beside the lease:", 16, "teal")
    gy = yg + 52
    c.card(gx + gpad, gy, giw, GR_L[0], GR_L[1], accent=GR_L[2], size=S)
    gy += hgl + 12
    c.card(gx + gpad, gy, giw, GR_T[0], GR_T[1], accent=GR_T[2], size=S, status="provisional")
    gy += hgt + 12
    c.card(gx + gpad, gy, giw, GR_S[0], GR_S[1], accent=GR_S[2], size=S, status="proposed")
    ys_card = gy
    c.card(cx[2], ycg, cw[2], CG[0], CG[1], accent=CG[2], size=S)
    c.card(cx[2], yca, cw[2], CA[0], CA[1], accent=CA[2], size=S)
    c.card(cx[2], yrc, cw[2], RC[0], RC[1], accent=RC[2], size=S, tint=False)
    c.card(cx[1], yth, cw[1], TH[0], TH[1], accent=TH[2], size=S, status="proposed", tint=False)
    c.card(cx[3], yho, cw[3], HO[0], HO[1], accent=HO[2], size=S, status="proposed")
    c.card(cx[4], yto, cw[4], TO[0], TO[1], accent=TO[2], size=S, tint=False)
    c.card(cx[5], yts, cw[5], TS[0], TS[1], accent=TS[2], size=S, tint=False)
    c.card(cx[5], yds, cw[5], DS[0], DS[1], accent=DS[2], size=S)


    # arrows: authority lane
    ux = cx[0] + cw[0] / 2
    c.arrow([(ux, yu + hu), (ux, yp)], "brown", label="signs in", lpos=0.5)
    c.arrow([(ux, yp + hp_), (ux, ya)], "brown", label="signs", lpos=0.5)
    # assertion -> submitter -> grant's subject card
    am = ya + ha / 2
    sx_mid = cx[1] + cw[1] / 2
    c.arrow([(cx[0] + cw[0] + 24, am), (sx_mid, am), (sx_mid, ysub + hsub)], "amber", sw=2.4,
            label="the assertion", lpos=0.3)
    sm = ys_card + hgs / 2
    c.arrow([(cx[1] + cw[1], sm if sm < ysub + hsub - 10 else ysub + hsub / 2), (gx + gpad, sm if sm < ysub + hsub - 10
             else ysub + hsub / 2)], "brown", sw=2.4, label="submits", lpos=0.5)
    # grant -> checked at grant -> admit
    mx_ = cx[2] + cw[2] / 2
    c.arrow([(mx_, yg + hgrant), (mx_, ycg)], "teal", sw=2.4, label="verified at the fence", lpos=0.5)
    c.arrow([(mx_, ycg + hcg), (mx_, yca)], "teal", sw=2.4, label="`RunCtx` lifted from the grant", lpos=0.5)
    c.arrow([(mx_, yca + hca), (mx_, yrc)], "teal", sw=2.4, label="recorded", lpos=0.5)
    # call lane
    c.arrow([(cx[1] + cw[1], lane), (cx[2], lane)], "amber", sw=2.6, label="`Actuate`", lpos=0.5)
    c.arrow([(cx[2] + cw[2], lane), (cx[3], lane)], "teal", sw=2.6, label="admitted", lpos=0.5)
    c.arrow([(cx[3] + cw[3], lane), (cx[4], lane)], "brown", sw=2.6, label="one credential", lpos=0.5)
    c.arrow([(cx[4] + cw[4], lane), (cx[5], lane)], "grey", sw=2.6, label="call + token", lpos=0.5)
    # refusals at admit, and at grant
    c.arrow([(cx[2] + cw[2], ycg + hcg / 2), (cx[2] + cw[2] + 110, ycg + hcg / 2)], "red", dash="7 5",
            label="refused", lpos=1.0, loff=(20, -22))
    c.arrow([(cx[2] + cw[2] + 24, yca + 60), (cx[2] + cw[2] + 110, yca + 60)], "red", dash="7 5")
    c.label(cx[2] + cw[2] + 120, yca + 30, "`R10`, `R11`: refused", "red", 12.5)
    # the round's subject, from the grant, to the host's exchange
    hx = cx[3] + cw[3] / 2
    c.arrow([(gx + cw[2] - gpad, sm), (hx, sm), (hx, yho)], "amber", sw=2.2, dash="7 5",
            label="the round's assertion, never ingress", lpos=0.25, lw=260)
    # the exchange with the token service
    tsm = yts + hts / 2
    c.arrow([(hx + 130, yho), (hx + 130, tsm), (cx[5], tsm)], "grey", both=True, label="exchange", lpos=0.8)

    fbot = max(mreg_bot, ds_bot, yrc + hrc) + 40
    lg = c.legend(X0, fbot, [
        ("arrow", "brown", "a human or a trust root acts"),
        ("arrow", "amber", "Proposed: the subject's path"),
        ("arrow", "teal", "the mechanism"),
        ("arrow", "red", "refused", "7 5"),
        ("box", "green", "①②③: the three closure points (Consequences; band 3)"),
    ])
    y = fbot + lg + 70

    # ================================================================== band 3: the confused deputy
    y = band(c, X0, y, "The confused deputy is closed at three points, and each degeneracy reopens one (Consequences; "
             "§9)", status="proposed")
    cols = [("Point", 110, {"bold": True}), ("Where", 300), ("What closes it", 700), ("Fails toward", 300),
            ("The degeneracy that reopens it", 520)]
    cols.append(("What it costs (§9)", WW - sum(cl[1] for cl in cols)))
    rows = [
        ["[[green|① At grant]]", "**The mechanism** (§2)", "**No subject without its assertion**: signed under a "
         "listed key, naming this grant's fence, within the seating's bound", "[[red|refusing the grant]]",
         "**D-0056-1 Declared subject**: the subject is named by the operator's signed grant, with no provider "
         "assertion", "Attribution moves from the subject's provider to the operator. **A havoc operator can act for "
         "any subject the seating admits.** §2's bound still holds"],
        ["[[green|② At the host]]", "**The tool host** (§5)", "**One credential per round**: the round's subject's, "
         "obtained by exchange, and the tool has no means to obtain another", "[[red|no credential]]",
         "**D-0056-2 Stored credentials**: the host selects a per-user credential from a store rather than exchanging "
         "the round's assertion", "The host's failure reaches **every stored subject**, not only the round's. **The "
         "store becomes part of T-0045-25**"],
        ["[[green|③ Downstream]]", "**The downstream system** (§6)", "**It takes the subject from the credential**, "
         "never from the request. An assumption of use, not a check", "[[red|serving only the token's subject]]",
         "**D-0056-3 Request-named subject downstream**: the downstream system reads the subject from the request",
         "**A Thinker's input names the user. The confused deputy is open**, and only the bundle and the Observer stand "
         "against it"],
    ]
    t = c.table(X0, y, cols, rows, size=14, accent="green")
    y += t + 16
    y += c.para(X0, y, WW, "**Deployment position: Archetype**, with three degeneracies. Only ① is the mechanism's "
                "own check; ② rests on a trust root and ③ on an assumption of use. **Finding 5**: §6 carries the "
                "weight for free text, because the floor cannot find a user named in an input. The design moves that "
                "path to a system TOPAK does not verify, which is the position ⟨U1⟩, recorded as one.", 14, "muted")
    y += 70

    # ================================================================== band 4: the entry and the floor
    y = band(c, X0, y, "The entry declares its credential, and the floor carries a minimum (§3, §4)",
             status="proposed", extra="ADR-0049, ADR-0041: owed")
    top = y
    g = 50
    wa = (WW - g) * 0.52
    wb = WW - g - wa
    xb = X0 + wa + g
    c.text(X0, top + 16, "**§3: `channel.credential`**, added to the channel part of a Run entry (ADR-0049 §1)", 16,
           "ink")
    cols = [("Field", wa * 0.27, {"mono": True}), ("Values", wa * 0.38), ("Checked or claimed", wa * 0.35)]
    t1 = c.table(X0, top + 32, cols, [
        ["channel.credential.mode", "`none` · `service` · `subject`",
         "[[teal|Checked]]: the tool host injects by it (§5), and the floor reads it (§4)"],
        ["channel.credential.providers", "For `subject`: the subject providers whose assertions this entry accepts",
         "[[teal|Checked]]: against the issued list at load (W12) and the round's subject at admit (`R11`)"],
        ["channel.credential.scope", "Text: what the credential permits downstream",
         "[[red|Claimed]]. What the downstream system enforces is its own"],
    ], size=14, accent="teal")
    ty = top + 32 + t1 + 22
    c.text(X0, ty + 16, "**Load checks, added to ADR-0049 §6 after W1–W10.** The bundle is refused when:", 16, "ink")
    cols = [("Check", 90, {"bold": True}), ("Refused when", wa - 90)]
    t2 = c.table(X0, ty + 32, cols, [
        ["W11", "A Run entry's channel has no `credential.mode`, or a mode outside the three"],
        ["W12", "A `subject` entry names no provider, or a provider the issued rules do not list, or has empty `scope` "
                "text"],
        ["W13", "A `none` or `service` entry carries `providers`"],
    ], size=14, accent="red")
    ty2 = ty + 32 + t2 + 18
    bl = stack(c, X0, ty2, wa, [
        (None, [
            "**The mode is required, with no default** (drafter's choice), by the totality rule ADR-0047 §1 and "
            "ADR-0049 W4 apply. **A Run entry without it does not load**, so every Run entry changes form, and a "
            "bundle and policy change together.",
            "**`service` is permitted and is not the default**: the deployment's own identity, right for a tool that "
            "reaches nothing per-user. **Finding 3: `service` is where LLM06's example 5 survives.** Whether a "
            "`service` entry reaches per-user data is a claim nothing checks; `scope` and promotion are the only "
            "defence, as for `purpose`.",
            "**A Build entry has no channel, so it has no credential.** ADR-0049 W5 already refuses one.",
        ], "grey", {"tint": False}),
    ], size=14)

    c.text(xb, top + 16, "**§4: two floor entries**, ADR-0041's next free ids after the `workflow` stage's `R8`, `R9`",
           16, "ink")
    cols = [("Id", wb * 0.33, {"mono": True}), ("Kind", wb * 0.1), ("Action", wb * 0.12, {"mono": True}),
            ("Holds when", wb * 0.45)]
    t3 = c.table(xb, top + 32, cols, [
        ["R10-subject-entry-needs-subject", "[[red|forbid]]", "Actuate",
         "the tool's `credentialMode` is `subject` and `subject.present` is false"],
        ["R11-subject-provider-accepted", "[[red|forbid]]", "Actuate",
         "the tool's `credentialMode` is `subject` and `subject.provider` is not in the tool's `subjectProviders`"],
    ], size=14, accent="teal")
    by = top + 32 + t3 + 22
    br = stack(c, xb, by, wb, [
        ("Why the floor stops there", [
            "**`R11` duplicates what the tool host would fail anyway**, and is kept so that the refusal is **an admit "
            "decision on the record, not a failed call past the membrane** (drafter's choice).",
            "**The bundle may narrow on `subject.attributes`**, for example to allow an entry only for subjects in a "
            "named group. Such a rule can only deny more.",
            "**No floor entry looks for a subject in the inputs.** That is a judgment, and ③ closes the path "
            "downstream instead.",
            "**Not taken: a floor forbid on `service` entries in a subject round.** A `service` entry that reaches "
            "nothing per-user is legitimate, and the floor cannot tell which kind it is. The bundle may forbid it.",
        ], "teal", {"tint": False}),
        ("The floor stage that would carry them", [
            "**`subjects`, in `floor/proposed/`**, built on the stage in force at ratification, with `R10` and `R11`: "
            "validated, tested and gated, **each entry shown to fire and none shown vacuous** (§11). "
            "[[red|Not built.]]",
        ], "violet", {"status": "notbuilt"}),
    ], gap=18, size=14)
    y = max(bl, br) + 80

    # ================================================================== band 5: trusted base and options
    y = band(c, X0, y, "The trusted base gains a root, a widened premise and an excluded row (§8)", status="proposed",
             extra="ADR-0045 rows owed")
    cols = [("Row", 230, {"bold": True}), ("Component", 480), ("Class", 170),
            ("Failure can produce", 900), ("Identity fixed by", 620)]
    cols.append(("", WW - sum(cl[1] for cl in cols)))
    cols[-1] = ("Note", cols[-1][1])
    t = c.table(X0, y, cols, [
        {"cells": ["T-0045-38 · new", "A subject provider", "trust root",
                   "A round that acts for a subject who did not ask, **within what the seating and floor allow**",
                   "Issued (ADR-0025 §1 (f)), on the list of subject providers",
                   "A trust root for the subjects it vouches for, and no others"], "accent": "amber"},
        {"cells": ["T-0045-25 · widened", "The tool host", "trust root",
                   "As before, **and a call presented with another subject's credential**",
                   "Promotion: part of the release", "Under D-0056-2 the credential store joins this row"],
         "accent": "brown"},
        {"cells": ["T-0045-39 · new", "A downstream system's authorization, and any token service that mints for it",
                   "[[grey|excluded]]", "Whatever the credential permits, done for the subject it names",
                   "Nothing. **No theorem rests on it** ⟨U1⟩",
                   "**The position, not a gap**: a reader computing a deployment's guarantees sees that per-user scope "
                   "is the downstream system's"], "accent": "grey"},
    ], size=14, accent="brown")
    y += t + 16
    y += c.para(X0, y, WW, "T-0045-37 is the last row in force (ADR-0053, B36), so these are the next two ids. They join G1 "
                "at ratification. Every theorem stays about the "
                "membrane.", 14, "muted") + 70

    y = band(c, X0, y, "Options considered, whole", status="proposed")
    cols = [("Option", 760, {"bold": True}), ("Disposition", WW - 760)]
    t = c.table(X0, y, cols, [
        {"cells": ["The subject in the lease, as a thirteenth field", "[[red|Rejected ⟨U1⟩.]] Every lease field is "
                   "authority the mechanism grants (ADR-0031 §1). A subject's authority is its provider's, and it "
                   "travels beside the lease as the task does"], "accent": "red"},
        {"cells": ["The subject as a Thinker input, checked by policy", "[[red|Rejected ⟨U2⟩.]] Whether the named user "
                   "is the right one is a judgment about content (ADR-0007)"], "accent": "red"},
        {"cells": ["The tool chooses the credential", "[[red|Rejected]] (§1). It needs every credential, its choice is "
                   "a claim, and its inputs are the model's"], "accent": "red"},
        {"cells": ["A subject input marked as a `destination`, so F2 and F3 apply", "[[grey|Not taken.]] It stretches "
                   "what a destination is, and it still lets a Thinker that has read only trusted content name any "
                   "user"], "accent": "grey"},
        {"cells": ["A seat per user", "[[red|Rejected.]] A user is not promoted and holds no Persona, and a quorum per "
                   "user does not scale. One entry or seating per tenant remains possible and is syntactic, so it "
                   "needs no degeneracy"], "accent": "red"},
        {"cells": ["The operator declares the subject", "[[grey|Not taken at the archetype.]] It is D-0056-1"],
         "accent": "grey"},
        {"cells": ["Several subjects per round", "[[grey|Not taken]] (drafter's choice). It mixes two users' content "
                   "in one round topic and one `clearSet`, and needs a per-call subject, which is a choice someone must "
                   "make"], "accent": "grey"},
        {"cells": ["A floor forbid on `service` entries in a subject round", "[[grey|Not taken.]] A `service` entry "
                   "that reaches nothing per-user is legitimate, and the floor cannot tell which kind it is (finding "
                   "3). The bundle may forbid it"], "accent": "grey"},
        {"cells": ["No record: leave per-user scope to deployments", "[[red|Rejected.]] The scope can be left to "
                   "deployments, and §6 does. **The binding cannot, because its failure adds authority**"],
         "accent": "red"},
    ], size=14, accent="grey")
    y += t + 80

    # ================================================================== band 6: findings, gaps, ratification
    y = band(c, X0, y, "What is open, and what ratification needs (Findings; Open obligations; §10, §11)")
    g = 40
    w3 = (WW - 2 * g) / 3
    xs = [X0, X0 + w3 + g, X0 + 2 * (w3 + g)]
    b1 = stack(c, xs[0], y, w3, [
        ("Findings", [
            "**1. The task path is the larger gap.** Grants come from a quorum or an operator, and ADR-0050 §2's \"the "
            "rate problem does not arise\" assumed one operator acting per round. **A deployment serving users at "
            "volume reopens that rate problem.**",
            "**2. Freshness by fence asks the user's session to be live at grant.** The right failure direction, but "
            "it excludes scheduled or long-running work for a user.",
            "**3. `service` is where LLM06's example 5 survives** (band 4).",
            "**4. Results from a `subject` call are that user's data, and nothing labels them so.** A workflow edge "
            "(ADR-0054) could carry one user's data into another's round unless the activation is per subject.",
            "**5. §6 is an assumption, and it carries the weight for free text** (band 3).",
        ], "red", {"tint": False}),
    ], size=14)
    b2 = stack(c, xs[1], y, w3, [
        ("Not covered (§10)", [
            "**How a user's request becomes a task.** A round for a user today needs an operator to act. A separate "
            "record (finding 1).",
            "**Long-running or offline action for a user**: refresh tokens, a scheduled job for an absent user.",
            "**Delegation between principals**, which ADR-0054 decides by seating every cell.",
            "**A subject's consent**, beyond its provider having signed an assertion naming the grant's fence.",
        ], "grey", {"tint": False}),
        ("Open obligations", [
            "**The form of the subject assertion**, and whether an existing token format carries it unchanged.",
            "**The size and form of `subject.attributes`**, and which provider claims may be lifted.",
            "**A task path for end users**: a record of its own.",
            "**Whether a digest of a personal identifier in the forensic floor** meets a deployment's data obligations.",
            "**The label of a `subject` call's result**: a per-subject sensitivity name in ADR-0047's vocabulary, or "
            "one the bundle declares.",
            "**ADR-0054's activation carrying one subject**, if ADR-0054 is ratified first.",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=18, size=14)
    b3 = stack(c, xs[2], y, w3, [
        ("Ratification condition (§11)", [
            "**ADR-0050 confirmed first**, or this record ratified provisionally with it.",
            "**The dependent entries drafted**: ADR-0049 (§3's fields; W11–W13), ADR-0050 §5, ADR-0031 A3, ADR-0041 "
            "(`R10`, `R11`, the `RunCtx` attributes), ADR-0042 §6, ADR-0045 (T-0045-38, T-0045-39, T-0045-25's "
            "premise), ADR-0025 A2, ADR-0048 §2, ToO §13, and ADR-0054 §2 if ratified first.",
            "**A module, by ADR-0046's method**, whose mutations break its properties: `SubjectFixedForRound`, "
            "`SubjectEvidenced`, `InjectedIsRoundSubject`, `SubjectEntryNeedsSubject`; `M_INPUT_SUBJECT`, "
            "`M_RESUBJECT`, `M_STALE_ASSERTION`, `M_NO_R10`.",
            "**The floor stage `subjects`** (band 4).",
            "**The reference, with an ADR-0033 addendum**: one `subject` entry over a stub downstream that authorizes "
            "by token. **Each behaviour seen**: a valid assertion binds; one naming another fence is refused; a "
            "`subject` call in a subjectless round is refused by `R10`; **a Thinker input naming another user is "
            "served for the token's subject, not the input's**; the tool list shows the mode and not the subject.",
            "**A reader who is not the drafter** (ADR-0029 A2).",
        ], "blue", {"tint": False, "status": "proposed"}),
        ("On ratification it closes", [
            "**On-behalf-of attribution for an end user**, which ADR-0037 lists as not owed, in one form: one subject "
            "per round, evidenced at grant. Delegation between principals stays as ADR-0054 leaves it.",
        ], "green", {}),
    ], gap=18, size=14)
    c.ymax = max(c.ymax, b1, b2, b3)
    return c
