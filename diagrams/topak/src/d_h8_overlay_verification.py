"""H8 — The command-chain overlay's evidence: eight TLA+ modules, checked and proved, and what each says against its
record (ADR-0059 to ADR-0066, Proposed; ADR-0067 and ADR-0068 have none). Every count and digest is read from the
module, rows, results, proof and scan files at build time, and every digest is compared with the one the record's
ratification condition cites; a missing file or an unparseable number is an error, not a blank."""
import hashlib
import pathlib
import re

from lib import Canvas, STATE_CC, STATUS, text_width

ID, SLUG = "H8", "overlay-verification"

W = 3600
DAY = "2026.11.10"

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "spec" / "Federation.tla").exists() and (p / "decisions").is_dir()), _HERE.parents[3])
SPEC = ROOT / "spec"
DEC = ROOT / "decisions"
PROPOSAL = ROOT / "derived" / "topak-federated-c2-design-proposal-2026.11.10b.md"


# ------------------------------------------------------------------------------------------------- the eight modules
# Hand-written: what each property and mutation says, from each module's header; the record and section it states.
# Everything numeric, and which mutation breaks which property, is read from the files below.
MODS = [
    dict(m="Federation", adr="0059", rc="§9", sections="ADR-0059 §1, §4–§6, §9", name="a tree of planes",
         props=[
             ("CharterNarrows", "§1", "A charter seated by an honest parent is the parent's or narrower, field by field"),
             ("LeaseWithinChain", "§4, §5", "Every lease a verifier accepts is within every charter on its chain"),
             ("HavocPlaneBounded", "§4", "Whatever the captured planes sign, no verifier permits an entry the root's "
                                         "tally did not vote"),
             ("BudgetConserved", "§1", "Leases under a charter and every charter below it never exceed its budget, "
                                       "**for a subtree with no captured plane**"),
             ("AnyPlaneFences", "§6", "No verifier that has heard an epoch permits under a chain carrying an older "
                                      "epoch of that plane"),
         ],
         muts={
             "M_WIDEN": "A seating by an honest parent may widen the alphabet",
             "M_LASTLINK": "A verifier checks only the granting plane's charter",
             "M_TRUSTPLANE": "A verifier takes a captured plane's word for its own chain and checks no charter",
             "M_NODEBIT": "A child's budget is not debited from its parent's",
             "M_STALEEPOCH": "A check compares only the granting plane's epoch",
         },
         abstr="One chain of three planes, `r` → `a` → `b`, the root honest (`ASSUME CapturedNotRoot`). Four of §1's "
               "fields: `seated`, `alphabet` (a set), `budget` (a number) and `fence`; `labels`, `bundles`, `ttlMax`, "
               "`countMax` and `expiry` have the shape of the first two. One fence value per link. A commit certificate "
               "is unforgeable; verifiers are honest; a presented lease is any entry at any epoch. No re-seating. "
               "Membership is `Membership.tla`'s"),
    dict(m="Intent", adr="0060", rc="§7", sections="ADR-0060 §1–§3, §7; ADR-0062 §2", name="the intent boundary",
         props=[
             ("EveryEffectHasAnIntent", "0060 §1", "Every reversible effect has an intent ordered at the commanded "
                                                   "plane before it, live when the effect's lease was granted"),
             ("EveryEffectHasALease", "0062 §2", "Every reversible effect has a lease ordered at its plane before it, "
                                                 "and is within that lease's count"),
             ("IntentNarrows", "0060 §2", "Every intent is within the promoted seating, and not merely within the last "
                                          "intent ⟨Q4⟩"),
             ("AutonomousAddsNothing", "0060 §3", "The autonomous plane's log holds no promotion, seating, issuance, "
                                                  "bundle change or operator's grant, and no membership change off its "
                                                  "schedule"),
         ],
         muts={
             "M_NOINTENT": "The autonomous plane grants a lease with no live intent",
             "M_NOCOUNT": "The governor does not count",
             "M_WIDEINTENT": "A successor widens the envelope past the seating",
             "M_LASTINTENT": "ADR-0050's rule, which ⟨Q4⟩ declined: a successor is bounded by the last intent",
             "M_LITEPROMOTES": "The autonomous plane orders a promotion",
         },
         abstr="Every effect is reversible: an irreversible one is `Release.tla`'s. Time is nondeterminism: an intent "
               "ends by `EndIntent`, whichever of expiry, revocation and a fence it was. An intent has `envelope` and "
               "`budget`; `expiry` and `task` have their shape. ADR-0050's live lease and live peer are not modelled. "
               "**The autonomous plane is honest**: a captured one is `Federation`'s and `Outstanding`'s"),
    dict(m="Membership", adr="0061", rc="§7", sections="ADR-0061 §1, §3, §4, §7", name="the shrink schedule",
         props=[
             ("StepInSchedule", "§3, §4", "Every step is to a size the charter's schedule names"),
             ("StepAtFloor", "§4", "Every step leaves at least the capture floor tolerated"),
             ("StepByQuorum", "§3", "Every step is signed by a certificate of the membership it replaces"),
             ("AtMostOneSuccessor", "§3", "No membership has two successors: two certificates of one membership share "
                                          "an honest replica, and it signed one step"),
             ("OneSuccessor", "§7", "The four together, as §7 states it"),
         ],
         muts={
             "M_MINORITYSTEP": "A step is ordered by one signer fewer than a certificate",
             "M_BELOWFLOOR": "A step may go below the capture floor",
             "M_OFFSCHEDULE": "A step need not be in the schedule",
             "M_TWOVOTES": "An honest replica may sign several steps of one membership: §3's signing rule with no "
                           "agreement behind it",
         },
         abstr="**Five replicas, one plane, and not §1's seven.** The captured are within the floor (`ASSUME "
               "CapturedWithinFloor`). PBFT is abstracted to its certificate: no view change, primary or message "
               "delivery. Whether a replica has \"not heard\" another is not modelled: an honest "
               "replica may sign any drop but its own, more than §3 allows. A step's ticks and a smaller membership's "
               "budget are not modelled. No action adds a replica"),
    dict(m="Alone", adr="0062", rc="§11", sections="ADR-0062 §5, §7, §11", name="a vehicle alone",
         props=[
             ("AlonePermitsNothing", "§5", "A governor whose vehicle is alone permits nothing but the beacon, and the "
                                           "beacon within its count"),
             ("ExpiryGrantsNothing", "§7", "After a lease ends no entry is permitted, and the only terminal act is hold "
                                           "or the seating's terminal behaviour, which the stack does not select"),
             ("LocalNeverWaits", "§11", "**Over `ENABLED`**: while a lease is live and the vehicle hears its plane, a "
                                        "`local` entry within its count can be permitted, whatever the primary, any "
                                        "other vehicle or any Observer does (⟨21⟩)"),
             ("TerminalNeverWaits", "§11", "**Over `ENABLED`**: with a lease ended, the terminal behaviour is enabled "
                                           "whatever the stack does"),
         ],
         muts={
             "M_ALONEACTS": "Going alone does not end the lease, so the vehicle goes on permitting within its count",
             "M_BEACONUNCOUNTED": "The beacon's count is one higher than declared",
             "M_STACKCHOOSES": "The stack selects the terminal act",
             "M_ENTRYAFTEREND": "An entry is permitted under an ended lease",
             "M_WAITPRIMARY": "A `local` permit waits for the primary",
             "M_WAITPEER": "A `local` permit waits for another vehicle",
             "M_WAITOBSERVER": "A `local` permit waits for a live Observer: R3 kept mid-lease, which §8 moves to the "
                               "grant",
             "M_STACKGATED": "The terminal behaviour waits for the stack",
         },
         abstr="One vehicle, one governor, one stack. \"Hears its plane\" is a flag and `GoAlone` is free: the clock is "
               "`PlaneClock.tla`'s. One `local` and one `ordered` entry; the count is a constant. `EndLease` stands for "
               "every ending but going alone and a fence. Reports are `Peer.tla`'s. Reaching a safe state is physics"),
    dict(m="Outstanding", adr="0063", rc="§8", sections="ADR-0063 §3, §4, §8", name="revocation bounded in effects",
         props=[
             ("EffectsAfterHonest", "§4", "After the intent boundary orders a revocation, an honest plane's vehicles "
                                          "produce fewer than `KUp` further effects"),
             ("EffectsAfterPerGovernor", "§4", "Under any plane, each honest governor produces fewer than `KUp` further "
                                               "effects"),
             ("EffectsAfterRevocationBounded", "§8", "The two together, as §8 names it, **with no premise about time**"),
             ("HavocPlaneBoundedInEffects", "§3", "Each honest governor has permitted fewer than `KUp` effects that no "
                                                  "watermark covers, the plane signing anything"),
             ("SealedIsSpent", "§4", "A lease a watermark covers produces no further effect"),
             ("CountExact", "§4", "No lease permits more entries than its count"),
         ],
         muts={
             "M_NOCHARGE": "A lease is granted without charging the plane",
             "M_ATMOST": "The bound is \"at most `KUp`\", which lets one more through: ADR-0039's finding about K",
             "M_TRUSTMARK": "A governor takes a captured plane's word for what has been read",
             "M_EARLYRELEASE": "A watermark may cover a lease not yet sealed",
             "M_NOSTOP": "A plane or governor that hears the moved fence does not stop",
             "M_ORDEREDFREE": "§3's governor rule read literally: only leases are charged",
         },
         abstr="**No clock: no variable or guard is a time**, so a cut link, a late watermark and one never delivered "
               "are the same actions taken or not. Three lease slots, reclaimed, so leases over a behaviour are "
               "unbounded and at most three outstanding. Two honest governors. A watermark is one lease's coverage. A "
               "fence ahead of a watermark subtracts and is not modelled. Reports and ticks are not charged"),
    dict(m="PlaneClock", adr="0064", rc="§8", sections="ADR-0064 §2, §4, §5, §8; ADR-0062 §4", name="the plane's clock",
         props=[
             ("NoGrantPastExpiry", "0064 §4", "No grant under an intent one tick period or more past its `expiry`, as "
                                              "real time. **Rests on `ClockPremise`: a declared bound, not a safety "
                                              "theorem**"),
             ("EntryEndsAtExtent", "0062 §4; 0064 §5", "A running entry is short of its extent, counted in ticks applied, "
                                                       "and its governor's own clock has not passed the next tick's due "
                                                       "time"),
             ("NoStretchUnlessSlow", "0064 §5", "A governor whose clock is not slow runs no entry past one overdue tick "
                                                "in real time"),
         ],
         muts={
             "M_ONECLOCK": "One replica's clock decides a certificate",
             "M_RECEIPT": "An intent's interval starts at receipt, not at the tick it names: the NATO reading's F1",
             "M_RELATIVETICK": "A tick is measured from the tick before, so a stall hides its length: §2's first draft "
                               "(ADR-0064 Findings, 1)",
             "M_TOOSLOW": "The premise is waived: captured and slow make a certificate",
             "M_NOEXTENT": "An entry with no extent loads",
             "M_NOWATCHDOG": "An overdue tick ends nothing",
         },
         abstr="**Discrete time**: `now` in whole units, `P` units a tick period. **No clock rates and no margins** "
               "(folded into each clock's class: sound, slow, fast, captured), and **nothing of a real clock's drift**; "
               "ADR-0032 defers a timed automaton. A certificate is one atomic step, with no ballot, primary or view. "
               "One intent, one governor, one lease flag, one entry at a time; the lease's `ttl` is not modelled. "
               "Going alone is urgent. An extent is a number of ticks"),
    dict(m="Peer", adr="0065", rc="§9", sections="ADR-0065 §1–§4, §9", name="stacks report to peers",
         props=[
             ("PeerAddsNothing", "§1", "Every request permitted is still permitted with every item received from peers "
                                       "removed"),
             ("NarrowsInReceived", "§1", "… and with any subset of them: receipt only narrows, the monotonicity "
                                         "ADR-0067 §7 asks the stage to show"),
             ("ReceivedIsUntrusted", "§3", "A delivered report's label holds `untrusted` and its topic's name, whatever "
                                           "its sender declared"),
             ("SendWithinTopics", "§2, §4", "Every report an honest governor sends is to a topic the mesh declares for "
                                            "the seat"),
         ],
         muts={
             "M_PEERENABLES": "A report enables one entry, `gated`",
             "M_SENDERLABEL": "The sender's label is taken as given",
             "M_ANYTOPIC": "A governor sends a report to an undeclared topic",
         },
         abstr="One receiving governor, its lease, and one honest sender. **The radio is the adversary's**: any report on "
               "any topic with any labels can arrive. Three requests (`act`, `egress`, `gated`) and three topics. Sends "
               "recorded by digest, and the lease's end, are not modelled: `live` only rises. Whether a report is read "
               "is not modelled. `Mesh.tla` is neither edited nor extended"),
    dict(m="Release", adr="0066", rc="§7", sections="ADR-0066 §4, §7; ADR-0062 §6", name="an irreversible effect",
         props=[
             ("SignedByPerson", "0066 §7", "Every irreversible effect has a person's key on it"),
             ("OrderedAtCommand", "0066 §4", "… and was ordered at a commanded plane"),
             ("UsedOnce", "0066 §4", "An act produces at most one effect, anywhere"),
             ("NoOlderThanDeclared", "0066 §4", "An effect is no more than `FreshT` ticks past the tick its act names: "
                                                "**ticks, not duration**"),
             ("IrreversibleIsAPersons", "0066 §7", "The four together"),
             ("ConflictIsAFinding", "0062 §6", "A check failing at a seal or above subtracts, and voids nothing a "
                                               "governor permitted"),
             ("OrderedInContact", "0066 §4", "An act is admitted only in contact with the intent boundary"),
             ("ReleaseNeverCoupled", "0066 §7", "**Over `ENABLED`**: while the seat is live and the plane in contact, a "
                                                "release can be admitted whatever any agent or Observer is doing"),
         ],
         muts={
             "M_AGENTRELEASE": "The interlock does not check the person's key",
             "M_LITERELEASE": "The interlock accepts the autonomous plane's certificate",
             "M_REPLAY": "The interlock does not check that the act is unused",
             "M_ANYVEHICLE": "The interlock does not check the act's vehicle",
             "M_LATEFIRST": "A first delivery after the ticks have run is accepted, as an interval from receipt would be",
             "M_VOID": "A failed check voids an effect that happened",
             "M_NOCONTACT": "A release is admitted with no link",
             "M_OBSCOUPLE": "A release waits for a live Observer",
             "M_AGENTPROPOSES": "A release waits for an agent's proposal, the design §3 rejects",
         },
         abstr="One commanded plane, one autonomous plane, two vehicles, one person, one agent, one irreversible entry. "
               "Ticks are numbers in the log, not a clock. **The interlock is the only check relied on**: an agent's act "
               "may be ordered and the autonomous plane may originate any act, so `FD5`, `FD6` and `FD9` are not "
               "assumed. The roster's quorum is one action; a void before the effect is not modelled"),
]

# A property whose theorem is not `<Property>Always`.
THM_OVERRIDE = {
    "OneSuccessor": (["SafeAlways"], "`Safe == OneSuccessor`"),
    "EffectsAfterRevocationBounded": (["EffectsAfterHonestAlways", "EffectsAfterPerGovernorAlways"],
                                      "its two conjuncts' theorems"),
}


# ------------------------------------------------------------------------------------------------- readers
def _read(path):
    if not path.exists():
        raise FileNotFoundError(f"H8 needs {path}")
    return path.read_bytes()


def _need(pat, text, what, flags=0):
    m = re.search(pat, text, flags)
    if not m:
        raise ValueError(f"H8: cannot parse {what}: /{pat}/")
    return m


def digest(path):
    return hashlib.sha256(_read(path)).hexdigest()[:16]


def read_rows(mod):
    """-> list of (name, mut, prop, expected, consts) from <M>-rows.txt."""
    t = _read(SPEC / f"{mod}-rows.txt").decode("utf-8")
    out = []
    for ln in t.splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) < 6 or p[3] != "INVARIANT" or p[5] not in ("HOLDS", "VIOLATED"):
            raise ValueError(f"H8: cannot parse row of {mod}-rows.txt: {ln!r}")
        out.append((p[0], p[1], p[4], p[5], " ".join(p[6:])))
    if not out:
        raise ValueError(f"H8: no rows in {mod}-rows.txt")
    return out


def read_tlc(mod):
    t = _read(SPEC / f"{mod}-results-{DAY}.txt").decode("utf-8")
    m = _need(r"Rows: (\d+) · as expected: (\d+) · not as expected: (\w+) · ERROR: (\w+)", t, f"{mod} TLC summary")
    consts = _need(r"rows: \S+ \(sha256 [0-9a-f]+\) · (.*?) unless the row says otherwise", t, f"{mod} constants")
    mdig = _need(rf"Module: {mod}\.tla \(sha256 ([0-9a-f]+)\)", t, f"{mod} module digest in TLC results")
    rdig = _need(rf"rows: {mod}-rows\.txt \(sha256 ([0-9a-f]+)\)", t, f"{mod} rows digest in TLC results")
    return {"rows": int(m.group(1)), "ok": int(m.group(2)), "notok": m.group(3), "err": m.group(4),
            "consts": consts.group(1), "mdig": mdig.group(1), "rdig": rdig.group(1)}


def read_proof(mod):
    t = _read(SPEC / f"{mod}-proof-results-2026.11.10.txt").decode("utf-8")
    thms = _need(r"^Theorems: (.*)$", t, f"{mod} theorems", re.M).group(1).split(" · ")
    asm = _need(r"^Assumptions: (.*)$", t, f"{mod} assumptions", re.M).group(1)
    n = int(_need(r"All (\d+) obligations proved", t, f"{mod} proof summary").group(1))
    return {"thms": [x.strip() for x in thms], "asm": asm, "n": n}


def read_cert(mod):
    t = _read(SPEC / f"{mod}-proof-cert-results-2026.11.10.txt").decode("utf-8")

    def num(pat, what):
        return int(_need(pat, t, f"{mod} cert {what}").group(1))
    last = [ln for ln in t.strip().splitlines() if ln.startswith("All ") or ln.startswith("NOT CERTIFIED")]
    if not last:
        raise ValueError(f"H8: no verdict in {mod}-proof-cert-results")
    return {"n": num(r"Obligations: (\d+)", "obligations"),
            "triv": num(r"trivial, closed by tlapm with no backend\s+(\d+)", "trivial"),
            "smt": num(r"SMT, proof accepted by ethos\s+(\d+)", "SMT"),
            "zen": num(r"Zenon, proof checked by Isabelle\s+(\d+)", "Zenon"),
            "isa": num(r"\n  Isabelle\s+(\d+)", "Isabelle"),
            "ls4": num(r"LS4, temporal step, NOT certified\s+(\d+)", "LS4"),
            "certified": last[-1].startswith("All "), "last": last[-1]}


def read_theorems(mod):
    """-> {theorem: (conclusion, [excluded mutations], unmutated?)} from <M>_proof.tla."""
    t = _read(SPEC / f"{mod}_proof.tla").decode("utf-8")
    out = {}
    for m in re.finditer(r"^THEOREM (\w+) ==(.*?)Spec => \[\](\w+)", t, re.M | re.S):
        body = m.group(2)
        out[m.group(1)] = (m.group(3), re.findall(r'Mut # "(M_\w+)"', body), 'Mut = "none"' in body)
    if not out:
        raise ValueError(f"H8: no theorems in {mod}_proof.tla")
    return out


def read_assumes(mod):
    t = _read(SPEC / f"{mod}.tla").decode("utf-8")
    return re.findall(r"^ASSUME (\w+)\s*==", t, re.M)


def read_scan():
    t = _read(SPEC / "proof-scan-results-2026.11.10.txt").decode("utf-8")
    per = {}
    for m in re.finditer(r"^== (\w+)_proof\.tla: (\d+) obligations printed normalized, of the (\d+) sent to a backend · "
                         r"(no capture|[^·]+) · SANY: (\w+)", t, re.M):
        per.setdefault(m.group(1), {}).update(sent=int(m.group(3)), cap=m.group(4), sany=m.group(5))
    for m in re.finditer(r"^== (\w+)_proof\.tla: SMT .*? · renamed run: each of (\d+) obligations by the same route, "
                         r"(no difference|.+)$", t, re.M):
        per.setdefault(m.group(1), {}).update(renamed=m.group(3))
    for m in re.finditer(r"^== (\w+)_proof\.tla \(sha256 [0-9a-f]+\): .*?· (this run certifies|.+?)\n"
                         r"   SMT queries with an opaque constant under a binder: (\d+)", t, re.M):
        per.setdefault(m.group(1), {}).update(binder=int(m.group(3)), runcert=m.group(2))
    tot = {
        "caps": int(_need(r"captures: (\d+)", t, "scan captures").group(1)),
        "sany": _need(r"modules SANY parses: (\d+) of (\d+)", t, "scan SANY").groups(),
        "differs": int(_need(r"modules whose renamed run differs: (\d+)", t, "scan renamed").group(1)),
        "run": _need(r"Modules run: (\d+), of which this run certifies: (\d+)", t, "scan runs").groups(),
        "binder": int(_need(r"SMT queries with an opaque constant under a binder: (\d+) ·", t, "scan binder").group(1)),
        "zi": int(_need(r"obligations Zenon or Isabelle closed: (\d+)\n", t, "scan Zenon/Isabelle").group(1)),
        "sent": int(_need(r"obligations sent to a backend: (\d+)", t, "scan sent").group(1)),
        "renamed_ids": int(_need(r"(\d+) identifiers renamed", t, "scan renamed ids").group(1)),
        "expect": _need(r"so ([0-9.]+) collisions to expect by accident", t, "scan collisions").group(1),
        "untrans": int(_need(r"lines with an untranslated operator, outside comments: (\d+)", t, "scan lines").group(1)),
        "digest": digest(SPEC / "proof-scan-results-2026.11.10.txt"),
    }
    return per, tot


def read_deadlock():
    t = _read(SPEC / "deadlock-audit-results-2026.11.10.txt").decode("utf-8")
    per = {}
    for m in re.finditer(r"^(\w+) \| Mut = \"none\" · (.*?) \| (\d+) distinct states \| (.+)$", t, re.M):
        per[m.group(1)] = {"states": int(m.group(3)), "verdict": m.group(4)}
    tot = _need(r"Lines: (\d+) · no terminal state: (\d+) · every terminal state at the bound: (\d+) · "
                r"STRAY DEADLOCK: (\d+) · ERROR: (\d+)", t, "deadlock totals").groups()
    return per, [int(x) for x in tot], digest(SPEC / "deadlock-audit-results-2026.11.10.txt")


def read_record(adr):
    """The record's status line, its cited spec digests and its stated figures."""
    t = _read(DEC / f"ADR-{adr}.md").decode("utf-8")
    flat = re.sub(r"\s+", " ", t)   # the records wrap at 120 columns, inside a citation as anywhere
    cites = dict(re.findall(r"`spec/([\w.-]+)` \(`([0-9a-f]{16})`\)", flat))
    status = _need(r"^\*\*Status:\*\* (\w+)", t, f"ADR-{adr} status", re.M).group(1)
    hist = t.split("## History")[1]
    r1 = re.search(r"^\| R1 \| [^|]+\| (.*?) \|", hist, re.M)
    return {"text": flat, "raw": t, "cites": cites, "status": status, "r1": bool(r1)}


def proposal_muts():
    t = _read(PROPOSAL).decode("utf-8")
    sec = _need(r"\n## 10\. What would be checked\n(.*?)\n## 11\.", t, "proposal §10", re.S).group(1)
    return set(re.findall(r"`(M_[A-Z]+)`", sec)), set(re.findall(r"^\| (?:`\w+`[^|]*)?\| `(\w+)`:", sec, re.M))


# ------------------------------------------------------------------------------------------------- helpers from C10
def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), sub=k.get("sub"))
            for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def at_list(rows, witness_word=False):
    """Rows as `Prop` at `consts`; a row at the defaults says so where the same property also runs at others."""
    with_c = {r[2] for r in rows if r[4]}
    out = []
    for r in rows:
        lab = (f"witness `{r[2]}`" if witness_word and r[2].startswith("Never") else f"`{r[2]}`")
        lab += f" at `{r[4]}`" if r[4] else (" at the defaults" if r[2] in with_c else "")
        if lab not in out:
            out.append(lab)
    return out


def thm_cell(prop, thms, proved):
    names, note = THM_OVERRIDE.get(prop, ([f"{prop}Always"], None))
    parts = []
    for n in names:
        if n not in thms or n not in proved:
            return f"[[red|no theorem found for {prop}]]"
        concl, excl, unmut = thms[n]
        if unmut:
            hyp = "unmutated"
        elif excl:
            hyp = "excluding " + ", ".join(f"`{x}`" for x in excl)
        else:
            hyp = "under every mutation"
        parts.append(f"`{n}`, {hyp}")
    s = "; ".join(parts)
    if note:
        s += f" ({note})"
    return s


def build():
    # ------------------------------------------------------------------ read everything first
    data = {}
    for d in MODS:
        m = d["m"]
        rows = read_rows(m)
        tlc = read_tlc(m)
        prf = read_proof(m)
        crt = read_cert(m)
        thm = read_theorems(m)
        if tlc["rows"] != len(rows):
            raise ValueError(f"H8: {m}: results file has {tlc['rows']} rows, rows file {len(rows)}")
        if crt["n"] != prf["n"]:
            raise ValueError(f"H8: {m}: certified run has {crt['n']} obligations, ordinary run {prf['n']}")
        files = {"module": f"{m}.tla", "proof": f"{m}_proof.tla", "tlc": f"{m}-results-2026.11.10.txt",
                 "presults": f"{m}-proof-results-2026.11.10.txt", "cert": f"{m}-proof-cert-results-2026.11.10.txt",
                 "rowsf": f"{m}-rows.txt"}
        dig = {k: digest(SPEC / f) for k, f in files.items()}
        if tlc["mdig"] != dig["module"]:
            raise ValueError(f"H8: {m}: the TLC results file was run on another module text")
        rec = read_record(d["adr"])
        data[m] = dict(rows=rows, tlc=tlc, prf=prf, crt=crt, thm=thm, files=files, dig=dig, rec=rec,
                       asm=read_assumes(m))
    for mod, name in (("PlaneClock", "ClockPremise"), ("Federation", "CapturedNotRoot"),
                      ("Membership", "CapturedWithinFloor")):
        if name not in data[mod]["asm"]:
            raise ValueError(f"H8: {mod}.tla no longer assumes {name}: redraw what rests on it")
    scan, stot = read_scan()
    dl, dtot, ddig = read_deadlock()
    p10_muts, _ = proposal_muts()
    recs = {a: read_record(a) for a in ("0059", "0060", "0061", "0062", "0063", "0064", "0065", "0066", "0067",
                                        "0068")}

    n_mod = len(MODS)
    T_rows = sum(v["tlc"]["rows"] for v in data.values())
    T_ok = sum(v["tlc"]["ok"] for v in data.values())
    T_obl = sum(v["crt"]["n"] for v in data.values())
    T_ls4 = sum(v["crt"]["ls4"] for v in data.values())
    T_cert = sum(1 for v in data.values() if v["crt"]["certified"])
    all_ok = T_rows == T_ok and all(v["tlc"]["notok"] == "none" and v["tlc"]["err"] == "none" for v in data.values())

    def kinds(rows):
        s = sum(1 for r in rows if r[1] == "none" and not r[2].startswith("Never"))
        w = sum(1 for r in rows if r[1] == "none" and r[2].startswith("Never"))
        return s, w, len(rows) - s - w

    c = Canvas(ID, "The command-chain overlay's evidence: eight TLA+ modules, checked and proved, and what each says "
                   "against its record",
               "ADR-0059 to ADR-0066 each ask, in their ratification condition, for **a module that states the "
               "properties and mutations that break them** (ADR-0046's method). On 2026.11.10 eight were written from "
               "those conditions and proposal §10 of `derived/topak-federated-c2-design-proposal-2026.11.10b.md`, "
               f"model-checked by TLC ({T_rows} rows, all as expected), proved by the TLA+ Proof System ({T_obl:,} "
               f"obligations) and certified, **with {T_ls4} LS4 temporal steps that no checker confirms**. Each header "
               "states findings against its record, and the same day **R1 revised ADR-0059 to ADR-0067 to take them**: "
               "the module items of ADR-0059 to ADR-0066 now read \"Met for TLC and TLAPS\" and cite every file by "
               "digest. **Every record is "
               "Proposed, an overlay and not the archetype, and nothing here is built**: no floor stage is written, the "
               "reference has no addendum, and **none of these words is a claim about running code**. Every count and "
               "digest on this page is read from the files when the diagram is generated.",
               W,
               "spec/Federation.tla, Membership.tla, Intent.tla, Alone.tla, Outstanding.tla, PlaneClock.tla, Peer.tla, "
               "Release.tla (headers, ASSUMEs); their -rows.txt, -results-2026.11.10.txt, _proof.tla (THEOREMs), "
               "-proof-results-2026.11.10.txt and -proof-cert-results-2026.11.10.txt, all read at build time; "
               "spec/proof-scan-results-2026.11.10.txt; spec/deadlock-audit-results-2026.11.10.txt; spec/README.md (the "
               "eight module rows, the eight proof rows, the paragraph on the overlay; method steps 2–4); ADR-0059 "
               "Status note, §1, §4, §9, History R1; ADR-0060 Status note, §1, §3, §7, R1; ADR-0061 Status note, §1, §3, "
               "§4, §7, Negative, Open obligations, R1; ADR-0062 Status note, §5, §11, R1; ADR-0063 Status note, §3, §4, "
               "§8, R1; ADR-0064 Status note, §2, §4, §5, §8, R1; ADR-0065 Status note, §1, §3, §9, R1; ADR-0066 Status "
               "note, §4, §7, Negative, R1; ADR-0067 Status note, §3's table (FD1–FD14), §5, §7, R1; ADR-0068 Status "
               "note, §6, Findings 1, History; proposal §10 (its table and \"What the modules could not show\"), read at "
               "build time for its mutation names; ADR-0046 §1, A1, A2 (B37); ADR-0045 T-0045-28; ADR-0029 A2; ADR-0053; "
               "ADR-0058 (Proposed); G11 §8, as proposal §10 cites it; ToO §11.3; ADR-0032; "
               "diagrams H3 and H6 for the evidence conventions",
               state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    def strip(label, items, y):
        c.text(X0, y + 15, label, 15, "faint", bold=True)
        px0 = X0 + 120
        px = px0
        for lab, kind, extra in items:
            lw = text_width(lab, 13.5, True) + 8 if lab else 0
            if kind in STATUS:
                pl = STATUS[kind][0] + (f" · {extra}" if extra else "")
            else:
                pl = extra
            pw = text_width(pl, 11.5, True) + 18
            if px + lw + pw > X1:
                px = px0
                y += 34
            if lab:
                c.text(px, y + 15, lab, 13.5, "ink", bold=True)
                px += lw
            if kind in STATUS:
                px += c.status(px, y, kind, extra) + 24
            else:
                acc, dash = kind
                px += c.pill(px, y, pl, acc, 11.5, dash=dash) + 24
        return y + 38

    marks = {"0059": "C1", "0060": "C1, C2", "0061": "C1", "0062": "C1, C2", "0063": "C1", "0064": "no criterion",
             "0065": "C2", "0066": "C1 · provisional while ADR-0052 is", "0067": "C1", "0068": "C2"}
    for a, r in recs.items():
        if r["status"] != "Proposed":
            raise ValueError(f"H8: ADR-{a} is {r['status']}, not Proposed: redraw")
    y = strip("Records", [(f"ADR-{a}", "proposed", marks[a] + (" · R1" if recs[a]["r1"] else " · not revised"))
                          for a in recs] + [("", ("grey", "6 4"), "every one an overlay, not the archetype ⟨Q11⟩")], y)
    y = strip("Evidence", [
        (f"{n_mod} modules", ("teal", None), f"checked: {T_rows} TLC rows, "
                                             f"{'all as expected' if all_ok else 'NOT all as expected'}"),
        ("", ("teal", None), f"proved: {T_obl:,} obligations"),
        ("", ("teal", "6 4"), f"certified, {T_cert} of {n_mod}, with {T_ls4} LS4 temporal steps no checker confirms"),
        ("", ("teal", None), f"proof scan: {stot['caps']} captures · renamed runs differ in {stot['differs']} of "
                             f"{stot['run'][0]} · SANY parses {stot['sany'][0]} of {stot['sany'][1]}"),
        ("", ("teal", None), f"deadlock audit: {dtot[0]} lines, {dtot[3]} stray deadlocks"),
    ], y)
    y = strip("Not", [
        ("floor stage federation, FD1–FD14", ("red", "2 3"), "Not written"),
        ("the reference, ADR-0033 addendum", "notbuilt", ""),
        ("", ("red", "2 3"), "no record ratified · nothing in force"),
        ("", ("red", "2 3"), "nothing here is checked, proved or certified of running code (T-0045-28)"),
    ], y)
    y += c.para(X0, y, WW, "**Three words, kept apart** (ADR-0046 §1, A1). TLC **checks** each module at small "
                "constants: every mutation fails the property it targets and holds the rest, every `Never…` witness is "
                "violated, `Safe` holds. The prover **proves** each invariant under its named hypotheses (the mutations "
                "it excludes and the module's `ASSUME`s) for every constant they admit. A proof module is **certified** "
                "when every obligation is closed by tlapm's normalization or a checked proof, **except its LS4 temporal "
                "steps, which no checker confirms**; and a certified proof is not a verified one (ADR-0046 A2, B37). "
                "**Proposed means nothing here is in force.** The modules and the revision are the drafter's, one "
                "author, one day; every record's last condition, a reader who is not the drafter, is not met.",
                14.5, "muted") + 50

    # ================================================================== 1. the map
    y = band(c, X0, y, "1 · Which module states which record: eight modules for eight records, and two records with "
                       "none", status="proposed", extra="ADR-0059 to ADR-0068")
    top = y + 40
    wl, wm, gx = 960, 1080, 230
    wr = WW - wl - wm - 2 * gx
    xl, xm, xr = X0, X0 + wl + gx, X0 + wl + gx + wm + gx
    S = 14

    def rec_card(a, title, body, st_extra):
        return (f"ADR-{a} · {title}", body, "amber", {"status": "proposed", "status_extra": st_extra, "tint": False})

    def modline(m):
        v = data[m]
        return (f"**{v['tlc']['rows']} rows**, {'all as expected' if v['tlc']['ok'] == v['tlc']['rows'] else 'NOT'} · "
                f"**{v['crt']['n']:,} obligations** proved · certified, **{v['crt']['ls4']} LS4**")

    def mod_card(d):
        m = d["m"]
        props = ", ".join(f"`{p[0]}`" for p in d["props"])
        return (f"`{m}.tla` · `{m}_proof.tla`", [modline(m), props], "teal", {"tint": True})

    recrow = {
        "Federation": rec_card("0059", "a tree of planes", [
            "**§9's module item: Met for TLC and TLAPS** ⟨R1⟩, with `BudgetConserved` for a subtree with no captured "
            "plane.", "Not met: the `federation` stage's `FD1`–`FD3`; the reference; a second reader."], marks["0059"]),
        "Intent": rec_card("0060", "the intent boundary", [
            "**§7's module item: Met for TLC and TLAPS** ⟨R1⟩. The plane is honest (§3); the intent was live at the "
            "grant (§1).", "Not met: `FD4`; the reference; a second reader. Waits on ADR-0050, -0054, -0055."],
            marks["0060"]),
        "Membership": rec_card("0061", "the membership of an autonomous plane", [
            "**§7: Met for TLC and TLAPS at five replicas, and not at §1's seven** ⟨R1⟩.",
            "Not met: **PBFT is read**; **a measured round** among seven over a deployment's radios; the reference; a "
            "second reader."], marks["0061"]),
        "Alone": None,
        "Outstanding": rec_card("0063", "revocation bounded in effects", [
            "**§8: Met for TLC and TLAPS** ⟨R1⟩, **with no premise about time**, and §4's argument as corrected.",
            "Not met: `FD10`; the reference; a second reader."], marks["0063"]),
        "PlaneClock": rec_card("0064", "the plane's clock is its ticks", [
            "**§8: Met for TLC and TLAPS, in discrete time** ⟨R1⟩, under §4's premise: a declared bound, not a safety "
            "theorem.", "Not met: **the two rules' arithmetic in Lean**; the reference; a second reader."], marks["0064"]),
        "Peer": rec_card("0065", "stacks report to peers", [
            "**§9: Met for TLC and TLAPS** ⟨R1⟩; `NarrowsInReceived` added.",
            "Not met: `FD12`, and the stage shown monotone in what was received; the reference; a second reader."],
            marks["0065"]),
        "Release": rec_card("0066", "an irreversible effect is a person's", [
            "**§7: Met for TLC and TLAPS** ⟨R1⟩. The interlock is the only check the module relies on.",
            "Not met: `FD5`, `FD6`, `FD9`, and `B10`'s relaxation routed; the reference; a second reader; ADR-0052 "
            "still provisional."], marks["0066"]),
    }
    to62 = {"Intent": "§2 · `EveryEffectHasALease`, `M_NOCOUNT`",
            "Alone": "§5, §7, §11 · the four properties",
            "PlaneClock": "§4 · `EntryEndsAtExtent`, `M_NOEXTENT`, `M_NOWATCHDOG`",
            "Release": "§6 · `ConflictIsAFinding`, `M_VOID`"}
    tolabel = {"Federation": "states §1, §4–§6, §9", "Intent": "states §1–§3, §7", "Membership": "states §1, §3, §4, §7",
               "Outstanding": "states §3, §4, §8", "PlaneClock": "states §2, §4, §5, §8", "Peer": "states §1–§4, §9",
               "Release": "states §4, §7"}
    alone_note = ("ADR-0062 is drawn on the right", [
        "Four modules state it, and `Alone.tla` states only it."], "grey", {"tint": False})
    rows_map = []
    yy = top
    for d in MODS:
        m = d["m"]
        rc = recrow[m] or alone_note
        mc = mod_card(d)
        hl = c.card(0, 0, wl, rc[0], rc[1], draw=False, size=S, status=rc[3].get("status"))
        hm = c.card(0, 0, wm, mc[0], mc[1], draw=False, size=S)
        h = max(hl, hm)
        rows_map.append((m, yy, h, rc, mc))
        yy += h + 34
    # the two with none
    none67 = ("ADR-0067 · rules of engagement; the `federation` floor stage", [
        "**Its condition asks for Cedar, not TLA+**: `FD1`–`FD14` written and passing the three gates (§7). **\"Nothing "
        "here is written as policy, gated, modelled or built\"** (Status note).",
        "**R1 changed one entry**: `FD10`'s governor clause follows ADR-0063 R1."], "amber",
        {"status": "proposed", "status_extra": marks["0067"], "tint": False})
    none67m = ("No module: the stage is not written", [
        "Each `FD` entry cites the record whose property it enforces (§3's table). **The modules state those "
        "properties; no gate shows that the entries enforce them.**"], "red", {"tint": False, "dash": "6 4"})
    none68 = ("ADR-0068 · adversaries, trusted-base rows, assumptions", [
        "**A declaration**: fourteen adversaries, twelve rows, ten assumptions. Its §6 asks that **each bound name a "
        "property of a module that exists**, and still says **\"Not met: no module is written\"**.",
        "**Not revised**: no R1 row."], "amber",
        {"status": "proposed", "status_extra": marks["0068"] + " · not revised", "tint": False})
    none68m = ("No module, and the record not revised", [
        "Eight modules now exist and its §6 is unchanged. **Which property each §1 bound names is not yet "
        "recorded.**"], "red", {"tint": False, "dash": "6 4"})
    for rc, mc in ((none67, none67m), (none68, none68m)):
        hl = c.card(0, 0, wl, rc[0], rc[1], draw=False, size=S, status="proposed")
        hm = c.card(0, 0, wm, mc[0], mc[1], draw=False, size=S)
        h = max(hl, hm)
        rows_map.append((None, yy, h, rc, mc))
        yy += h + 34
    bot = yy - 34

    c.region(xl - 24, top - 46, wl + 48, bot - top + 46 + 28, "decisions/ · Proposed 2026.11.10 · ADR-0059 to "
             "ADR-0067 revised R1 the same day", "amber", dash="10 6")
    c.region(xm - 24, top - 46, wm + 48, bot - top + 46 + 28, "spec/ · checked, proved, certified with LS4 · "
             "no running code", "teal", dash=None)
    # ADR-0062, tall, on the right
    r_top = [r for r in rows_map if r[0] == "Intent"][0][1]
    r_bot = [r for r in rows_map if r[0] == "Release"]
    r_bot = r_bot[0][1] + r_bot[0][2]
    body62 = [
        "**§11's module item: Met for TLC and TLAPS, across four modules** ⟨R1⟩: `Alone.tla`, with `Intent.tla`, "
        "`PlaneClock.tla` and `Release.tla`, each for the sections in the table below.",
        "**Two of them are the custodian's decision of 2026.11.10**, beyond §11 as drafted: `TerminalNeverWaits`, and "
        "`ConflictIsAFinding` with `M_VOID`, §6 as a property.",
        "**R1 places the beacon**: it is an effect (§5); proposal §10's \"the only effects are hold and the seating's "
        "terminal behaviour\" is true of actuation.",
    ]
    rcc = [("§11's ratification condition, item by item", wr - 330, {}), ("State", 330)]
    rcr = [
        ["**ADR-0059 to ADR-0061, and ADR-0064, ratified first**, or with this record", "[[red|Not met]]: all Proposed"],
        ["**A module** stating `EveryEffectHasALease`, `AlonePermitsNothing`, `ExpiryGrantsNothing`, "
         "`EntryEndsAtExtent`, their mutations, and one invariant over `ENABLED` (⟨21⟩)",
         "[[teal|Met for TLC and TLAPS]], across four modules ⟨R1⟩"],
        ["**The floor** carries `FD7`, `FD8`, `FD11` and `FD14` (ADR-0067)", "[[red|Not met]]: not written"],
        ["**The reference** shows a lease spent to its count with no round between; an entry with no extent refused at "
         "load; a lease ended on a missed tick; a failed check at a seal recorded as a finding", "[[red|Not met]]: "
         "nothing is built"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", "[[red|Not met]]"],
    ]
    h62r = c.table(0, 0, rcc, rcr, size=13.5, draw=False)
    heads62 = re.findall(r"^### (\d+)\. (.+)$", recs["0062"]["raw"], re.M)
    if len(heads62) < 11:
        raise ValueError("H8: cannot read ADR-0062's section headings")
    by62 = {
        "2": "`Intent.tla`: `EveryEffectHasALease` · `M_NOCOUNT`",
        "4": "`PlaneClock.tla`: `EntryEndsAtExtent` · `M_NOEXTENT`, `M_NOWATCHDOG`",
        "5": "`Alone.tla`: `AlonePermitsNothing` · `M_ALONEACTS`, `M_BEACONUNCOUNTED`",
        "6": "`Release.tla`: `ConflictIsAFinding` · `M_VOID` ([[brown|the custodian, 2026.11.10]])",
        "7": "`Alone.tla`: `ExpiryGrantsNothing` · `M_STACKCHOOSES`",
        "11": "`Alone.tla`: `LocalNeverWaits` (⟨21⟩) and `TerminalNeverWaits` ([[brown|the custodian]]), over `ENABLED`",
    }
    none62 = {"1": "a claim about hardware: the governor as the only path (C2; proposal §10)",
              "3": "the floor's `FD7`, not written", "8": "`Alone.tla`'s `M_WAITOBSERVER` is R3 kept mid-lease, which §8 moves to the grant",
              "9": "a degeneracy", "10": "overlay position"}
    t62c = [("§", 60, {}), ("ADR-0062's heading, read from the record", wr - 60 - 640), ("Stated by", 640)]
    t62r = []
    for num, head in heads62:
        head = re.sub(r"\s*⟨[^⟩]+⟩", "", head)
        if num in by62:
            t62r.append([f"§{num}", head, by62[num]])
        else:
            lab = "[[grey|in part]]: " if num == "8" else "[[grey|no module]]: "
            t62r.append({"cells": [f"§{num}", head, lab + none62.get(num, "")], "accent": "grey"})
    h62t = c.table(0, 0, t62c, t62r, size=13.5, draw=False)
    h62c = c.card(0, 0, wr, "ADR-0062 · the lease pre-authorizes", body62, draw=False, size=S, status="proposed")
    span = r_bot - r_top
    h62c = max(h62c, span - h62t - 50 - h62r - 30)
    r_end = max(r_bot, r_top + h62c + 30 + h62r + 44 + h62t)
    c.region(xr - 24, r_top - 46, wr + 48, r_end - r_top + 46 + 28, "decisions/ADR-0062", "amber", dash="10 6")
    c.card(xr, r_top, wr, "ADR-0062 · the lease pre-authorizes: a governor and a stack on each vehicle", body62,
           accent="amber", status="proposed", status_extra=marks["0062"], size=S, tint=False, h=h62c)
    c.table(xr, r_top + h62c + 30, rcc, rcr, size=13.5, accent="amber")
    c.text(xr, r_top + h62c + 30 + h62r + 32, "**The record, section by section, and the module that states each**",
           15, "ink")
    c.table(xr, r_top + h62c + 30 + h62r + 44, t62c, t62r, size=13.5, accent="amber")
    for m, ry, h, rc, mc in rows_map:
        c.card(xl, ry, wl, rc[0], rc[1], accent=rc[2], size=S, h=h, **rc[3])
        c.card(xm, ry, wm, mc[0], mc[1], accent=mc[2], size=S, h=h, **mc[3])
        mid = ry + 44
        if m and recrow.get(m):
            c.arrow([(xm - 2, mid), (xl + wl + 4, mid)], "teal", sw=2.2, label=tolabel[m], lpos=0.5)
        if m in to62:
            c.arrow([(xm + wm + 2, mid), (xr - 4, mid)], "teal", sw=2.2, label=to62[m], lpos=0.5, lw=200)
    y = bot + 28 + 30
    lg = c.legend(X0, y, [
        ("box", "amber", "a Proposed record (dashed: not ratified)", "6 4"),
        ("box", "teal", "a module and its proof: checked, proved, certified with LS4"),
        ("arrow", "teal", "the module states that record's sections"),
        ("box", "red", "nothing states it: no module, or not written", "6 4"),
    ])
    y += lg + 70

    # ================================================================== 2. the numbers
    y = band(c, X0, y, "2 · What was run, and what each run reports, read from the results files")
    cols = [("Module · record", 290, {}), ("TLC rows: safety · witness · mutation", 250), ("Result", 170),
            ("Obligations", 120), ("Trivial", 90), ("SMT, accepted by `ethos`", 125), ("Zenon, checked by Isabelle", 130),
            ("Isabelle", 90), ("LS4, not certified", 110), ("Certified run", 470),
            ("Proof scan: sent to a backend · capture · renamed run · SANY", 560)]
    cols.append(("Deadlock audit, unmutated, at the results file's constants", WW - sum(cl[1] for cl in cols)))
    trs = []
    for d in MODS:
        m = d["m"]
        v = data[m]
        s, w_, mu = kinds(v["rows"])
        sc = scan.get(m)
        if not sc or not {"sent", "cap", "sany", "renamed"} <= set(sc):
            raise ValueError(f"H8: the proof scan has no full entry for {m}")
        dd = dl.get(m)
        if not dd:
            raise ValueError(f"H8: the deadlock audit has no line for {m}")
        ok = v["tlc"]["ok"] == v["tlc"]["rows"] and v["tlc"]["notok"] == "none"
        cr = v["crt"]
        cert = (f"[[teal|Certified]]: {cr['n'] - cr['ls4']:,} on normalization or a checked proof; {cr['ls4']} on LS4"
                if cr["certified"] else f"[[red|{cr['last']}]]")
        trs.append([f"**`{m}`** · ADR-{d['adr']} {d['rc']}", f"{s} · {w_} · {mu} = **{v['tlc']['rows']}**",
                    "[[teal|all as expected]]" if ok else "[[red|NOT all as expected]]", f"**{cr['n']:,}**",
                    str(cr["triv"]), str(cr["smt"]), str(cr["zen"]), str(cr["isa"]), f"**{cr['ls4']}**", cert,
                    f"{sc['sent']} · {sc['cap']} · {sc['renamed']} · SANY {sc['sany']}",
                    f"{dd['states']:,} states · " + re.sub(r"^(every terminal state at the bound): (.+)$", r"\1: `\2`",
                                                             dd["verdict"])])
    sums = {k: sum(data[d['m']]["crt"][k] for d in MODS) for k in ("triv", "smt", "zen", "isa")}
    S_s = sum(kinds(data[d["m"]]["rows"])[0] for d in MODS)
    S_w = sum(kinds(data[d["m"]]["rows"])[1] for d in MODS)
    trs.append({"cells": [f"**All {n_mod}**", f"{S_s} · {S_w} · {T_rows - S_s - S_w} = **{T_rows}**",
                          "[[teal|all as expected]]" if all_ok else "[[red|NOT all]]", f"**{T_obl:,}**",
                          f"{sums['triv']:,}", f"{sums['smt']:,}", str(sums["zen"]), str(sums["isa"]), f"**{T_ls4}**",
                          f"{T_cert} of {n_mod} certified; {T_obl - T_ls4:,} on normalization or a checked proof",
                          f"{stot['sent']:,} sent · captures {stot['caps']} · renamed runs that differ "
                          f"{stot['differs']} · SANY {stot['sany'][0]} of {stot['sany'][1]}",
                          f"{dtot[0]} lines: {dtot[1]} with no terminal state, {dtot[2]} with every terminal state at "
                          f"the bound; stray deadlocks {dtot[3]}; errors {dtot[4]}"], "accent": "blue"})
    y += c.table(X0, y, cols, trs, size=13.5, accent="blue") + 16
    y += c.para(X0, y, WW, "**Obligation counts equal the ordinary runs'** (`<M>-proof-results-2026.11.10.txt`, each "
                "ending \"All N obligations proved\", under Z3); the certified run adds none and removes none. Each "
                "proof is **for every value of the constants its assumptions admit**: \"the prover, not the constants, "
                "bounds the claim\" (every proof results file). **Mutations and witnesses are behaviours and stay with "
                "TLC.** A deadlock line claims only that at its constants every terminal state is at the module's own "
                "bound, so `-deadlock` hides nothing else; it claims nothing under a mutation or at other constants.",
                14, "muted") + 30

    # the digests, against the record's citations
    c.text(X0, y + 16, "**Every file by digest** (SHA-256, first 16 hex, computed here) **against the digest the "
                       "record's ratification condition cites** ⟨R1⟩", 16, "ink")
    y += 32
    dcols = [("Module", 190, {})] + [(lab, 375) for lab in ("`<M>.tla`", "`<M>_proof.tla`", "TLC results",
                                                           "proof results", "certified results")]
    dcols += [("rows file", 395), ("The record's own figures", WW - 190 - 5 * 375 - 395)]
    drs = []
    mism = []
    for d in MODS:
        m = d["m"]
        v = data[m]
        rec = v["rec"]
        cells = [f"**`{m}`**"]
        for k in ("module", "proof", "tlc", "presults", "cert"):
            f, h = v["files"][k], v["dig"][k]
            cited = rec["cites"].get(f)
            if cited == h:
                cells.append(f"`{h}` [[green|as ADR-{d['adr']} {d['rc']} cites]]")
            elif cited:
                cells.append(f"`{h}` [[red|ADR-{d['adr']} cites {cited}]]")
                mism.append(f"{m} {k}")
            else:
                cells.append(f"`{h}` [[red|not cited]]")
                mism.append(f"{m} {k}")
        cells.append(f"`{v['dig']['rowsf']}` " + ("[[green|as the TLC results print]]" if v["dig"]["rowsf"] ==
                                                   v["tlc"]["rdig"] else "[[red|the TLC results print another]]"))
        if v["dig"]["rowsf"] != v["tlc"]["rdig"]:
            mism.append(f"{m} rows file")
        t = rec["text"]
        mr = re.search(rf"(\d[\d,]*) rows from `spec/{m}-rows\.txt`, all as expected", t)
        mo = re.search(r"([\d,]+) obligations proved, (\d+) of them LS4", t)
        if not mr or not mo:
            raise ValueError(f"H8: ADR-{d['adr']} states no row or obligation count for {m}")
        fr, fo, fl = int(mr.group(1).replace(",", "")), int(mo.group(1).replace(",", "")), int(mo.group(2))
        same = (fr, fo, fl) == (v["tlc"]["rows"], v["crt"]["n"], v["crt"]["ls4"])
        cells.append(f"{fr} rows · {fo:,} obligations · {fl} LS4: " +
                     ("[[green|as the files]]" if same else "[[red|the files differ]]"))
        if not same:
            mism.append(f"{m} figures")
        drs.append(cells)
    y += c.table(X0, y, dcols, drs, size=13, accent="teal") + 16
    y += c.para(X0, y, WW, ("**Every digest is the one the record cites, and every figure the record states is the "
                            "files'.** " if not mism else f"[[red|Differences: {', '.join(mism)}.]] ") +
                "Each TLC results file also names its module by digest, and each matches. The R1 module items cite them "
                "(ADR-0059 §9 to ADR-0066 §7), and spec/README.md says so.", 14, "muted") + 26

    # the scan and the audit, and what they look for
    run_muts = {mu for d in MODS for mu in d["muts"]}
    n_muts = len(run_muts)
    n_beyond = len(run_muts - p10_muts)
    p10_missing = p10_muts - run_muts
    ga = 36
    h_sa = row_cards(c, X0, y, WW, ga, [
        (f"The proof scan · `proof-scan-results-2026.11.10.txt` (`{stot['digest']}`)", [
            "**Why**: the pinned prover is **known to be unsound in two ways** (ADR-0046 A2, B37): a term under a "
            "binder, and two terms that share a name. **The scan looks; it does not prove absence.**",
            f"**Runs**: {stot['run'][0]} proof modules rerun, **{stot['run'][1]} certify**. "
            f"**{stot['binder']} SMT queries hold an opaque constant under a binder**, listed by line; the scan's rule "
            "is that this is the binder case only when the hidden term mentions a variable bound around it, and the "
            f"step at each line says which. {stot['zi']} obligations were closed by Zenon or Isabelle.",
            f"**Names**: a second run over sources with {stot['renamed_ids']:,} identifiers renamed: **"
            f"{stot['differs']} of {stot['run'][0]} differ** ({stot['expect']} collisions expected by accident).",
            f"**Capture**: {stot['sent']:,} obligations printed normalized: **{stot['caps']} captures**; SANY parses "
            f"**{stot['sany'][0]} of {stot['sany'][1]}**.",
        ], "teal", {"tint": False}),
        (f"The deadlock audit · `deadlock-audit-results-2026.11.10.txt` (`{ddig}`)", [
            "**Why**: every run passes TLC's `-deadlock`, which turns off the report of a state with no successor. The "
            "audit asks whether that hides anything.",
            f"**{dtot[0]} lines, one per module, unmutated, at the results files' constants**: {dtot[1]} have no "
            f"terminal state; {dtot[2]} (`Membership`, `Outstanding`) have terminal states only at the module's own "
            f"bound; **{dtot[3]} stray deadlocks**.",
            "`Membership`'s bound is every honest replica having voted from every reached membership: **a vote that "
            "splits stalls the schedule**, which R1 put in ADR-0061 §3, its Negatives and its open obligations.",
            "**It does not claim** the module never stalls: a state whose only step leaves it unchanged has a "
            "successor, and neither TLC's check nor `ENABLED` sees it.",
        ], "teal", {"tint": False}),
        ("Beyond proposal §10, read from its table", [
            f"Proposal §10 names {len(p10_muts)} mutations. **The modules run {n_muts}, of which {n_beyond} §10 does "
            f"not name**; each is marked in section 3, and every one §10 names is run"
            f"{'' if not p10_missing else ' [[red|except ' + ', '.join(sorted(p10_missing)) + ']]'}.",
            "Headers call some **added**: `M_OFFSCHEDULE`, `M_TWOVOTES` (\"beyond §7's two\"), `M_LASTINTENT` (\"an "
            "addition to proposal §10's table\"), `M_NOSTOP`, `M_ORDEREDFREE` (\"Added: finding 3\", \"finding 1\"). "
            "Records call others added: `M_TOOSLOW` and `NoStretchUnlessSlow` (ADR-0064 §8); `NarrowsInReceived` "
            "(ADR-0065 §9); `OrderedInContact`, `M_ANYVEHICLE`, `M_NOCONTACT`, `M_OBSCOUPLE`, `M_AGENTPROPOSES` "
            "(ADR-0066 §7).",
            "`OneSuccessor` is in `Membership.tla` where §10 puts it under `Federation`: it rests on quorum "
            "intersection and shares no state with the charter chain (spec/README.md).",
        ], "grey", {"tint": False}),
    ], size=14)
    y += h_sa + 80

    # ================================================================== 3. each module whole
    y = band(c, X0, y, "3 · Each module whole: every property with the theorem that proves it, every mutation with the "
                       "rows it breaks, every witness")
    y += c.para(X0, y, WW, "**Breaks** lists the rows a mutation must make VIOLATED, with any constants the row sets; "
                "**holds** lists the properties it must leave holding, which is what \"breaks it and nothing else\" "
                "means. A theorem's hypotheses are its `ASSUME` clause, read from the proof module: the mutations it "
                "excludes. **§10?** marks a mutation proposal §10 does not name.", 14.5, "muted") + 20
    for d in MODS:
        m = d["m"]
        v = data[m]
        rows = v["rows"]
        pad = 22
        wp = 1500
        wmu = WW - 2 * pad - wp - 30
        ws = wp
        px, mx_, sx = X0 + pad, X0 + pad + wp + 30, X0 + pad
        pcols = [("Property", 290, {}), ("Record", 125), ("What it says (the header)", 620),
                 ("Theorem, and its hypotheses", wp - 1035)]
        prow = []
        for p, sec, desc in d["props"]:
            prow.append([f"**`{p}`**", sec, desc, thm_cell(p, v["thm"], v["prf"]["thms"])])
        mcols = [("Mutation", 235, {}), ("What it does (the header)", 520), ("Breaks: VIOLATED rows", 400),
                 ("Holds under it", wmu - 235 - 520 - 400 - 115), ("§10?", 115)]
        mrow = []
        for mu, desc in d["muts"].items():
            mr = [r for r in rows if r[1] == mu]
            if not mr:
                raise ValueError(f"H8: {m}: no row runs {mu}")
            br = [f"`{r[2]}`" + (f" at `{r[4]}`" if r[4] else "") for r in mr if r[3] == "VIOLATED"]
            ho = at_list([r for r in mr if r[3] == "HOLDS"], witness_word=True)
            beyond = mu not in p10_muts
            mrow.append({"cells": [f"**`{mu}`**", desc, "; ".join(br) if br else "[[amber|no property]]",
                                   ", ".join(ho) or "—", "[[amber|not in §10]]" if beyond else "in §10"],
                         "accent": "amber"} if beyond else
                        [f"**`{mu}`**", desc, "; ".join(br) if br else "[[amber|no property]]", ", ".join(ho) or "—",
                         "in §10"])
        unk = sorted({r[1] for r in rows if r[1] != "none"} - set(d["muts"]))
        if unk:
            raise ValueError(f"H8: {m}: rows run mutations the diagram does not describe: {unk}")
        s_, w_, mu_ = kinds(rows)
        wit = [r for r in rows if r[1] == "none" and r[2].startswith("Never")]
        wv = [f"`{r[2]}`" + (f" at `{r[4]}`" if r[4] else "") for r in wit if r[3] == "VIOLATED"]
        wh = at_list([r for r in wit if r[3] == "HOLDS"])
        safe = [r for r in rows if r[1] == "none" and not r[2].startswith("Never")]
        sv = sorted({r[2] for r in safe})
        cr = v["crt"]
        side = [
            f"**{v['tlc']['rows']} rows**, all as expected: {s_} safety, {w_} witness, {mu_} mutation.",
            f"**Safety rows**: {', '.join(f'`{x}`' for x in sv)} HOLD at {len(safe)} sets of constants.",
            f"**Witnesses, each VIOLATED** ({len(wv)}): " + ", ".join(wv) + ".",
        ]
        if wh:
            side.append("**Witness rows that must HOLD**: " + ", ".join(wh) + ".")
        side += [
            f"**{cr['n']:,} obligations proved**: {cr['triv']} trivial, {cr['smt']} SMT, {cr['zen']} Zenon, "
            f"{cr['isa']} Isabelle, **{cr['ls4']} LS4, not certified**.",
            "**Named assumptions**: " + (", ".join(f"`{a}`" for a in v["asm"]) or "none") + " in the module; "
            + (", ".join(f"`{a.split(' == ')[0].strip()}`" for a in v["prf"]["asm"].split(" · "))
               if v["prf"]["asm"] != "none" else "none") + " in the proof.",
        ]
        hp = c.table(0, 0, pcols, prow, size=13.5, draw=False)
        hmu = c.table(0, 0, mcols, mrow, size=13.5, draw=False)
        hs = c.card(0, 0, ws, "Rows, witnesses, obligations", side, draw=False, size=13.5)
        inner = max(hp + 20 + hs, hmu)
        hs = inner - hp - 20
        rtop = y + 30
        c.region(X0, rtop, WW, inner + 2 * pad + 20,
                 f"{m}.tla · {d['name']} · states {d['sections']}", "teal", dash=None, size=15)
        c.table(px, rtop + pad + 20, pcols, prow, size=13.5, accent="teal")
        c.table(mx_, rtop + pad + 20, mcols, mrow, size=13.5, accent="red")
        c.card(sx, rtop + pad + 20 + hp + 20, ws, "Rows, witnesses, obligations", side, accent="teal", size=13.5,
               tint=False, h=hs)
        y = rtop + inner + 2 * pad + 20 + 40
    y += 40

    # ================================================================== 4. findings and R1
    y = band(c, X0, y, "4 · What each header found against its record, and how R1 took it", status="proposed",
             extra="R1, 2026.11.10, on the custodian's instruction to revise")
    fcols = [("The finding, as the module's header states it", 1330, {}), ("Shown by, in the rows", 600),
             ("How R1 took it", 1150)]
    fcols.append(("Where, in the record", WW - sum(cl[1] for cl in fcols)))
    F = [
        {"group": "Federation.tla → ADR-0059", "accent": "teal"},
        ["`Federation`", "**`BudgetConserved` is stated for an honest subtree, and that is a finding.** §1 said the debit "
         "makes \"the root's tally bounds the whole tree\". The debit bounds what is allocated: **a captured plane can "
         "sign more leases than its budget, each to a different vehicle, and no single verifier sees more than its "
         "own.** What survives capture is the honest parent's account and ADR-0063's per-governor bound",
         "Every `BudgetConserved` row runs at `Captured={}`; `M_NODEBIT` breaks it there",
         "[[green|Narrowed.]] §1: the debit bounds what is allocated across the tree, and what is issued in any subtree "
         "with no captured plane. §4: **the chain check bounds what each lease may carry, and not how many a captured "
         "plane signs**; the Consequences say the same", "ADR-0059 §1, §4, Consequences, §9; R1"],
        ["`Federation`", "**Two mutations break two properties each.** Proposal §10 says each property has a mutation "
         "that breaks it and nothing else. `M_LASTLINK` and `M_TRUSTPLANE` each break `LeaseWithinChain` and "
         "`HavocPlaneBounded`: under capture, a lease outside the chain is, or can be, outside what the root voted",
         "`m-last-chain`, `m-last-root`, `m-trust-chain`, `m-trust-root`: VIOLATED", "[[green|Recorded]] in §9's module "
         "item", "ADR-0059 §9"],
        {"group": "Intent.tla → ADR-0060, ADR-0062 §2", "accent": "teal"},
        ["`Intent`", "**The autonomous plane is honest here.** A captured plane is a havoc issuer (ADR-0059 §4): it can "
         "sign a lease under an intent that has ended, and no log of its own is evidence. So \"live when its lease was "
         "granted\" is a claim about an honest plane, and **§3's is a claim about the log of an honest one**",
         "The module's plane has no capture; a captured one is bounded by `Federation`'s chain check and "
         "`Outstanding`", "[[green|Narrowed.]] §3: \"This is a claim about an honest plane's log\"; what bounds a "
         "captured one is the chain check and ADR-0063", "ADR-0060 §3, §7; R1"],
        ["`Intent`", "**An effect can follow its intent's end.** `EndLease` is free, so a lease may outlive its intent. "
         "§1's predecessor is ordered before the effect, **not live at it**; ADR-0063 bounds how many follow",
         "`w-afterend`: `NeverEffectAfterIntentEnded` VIOLATED", "[[green|Narrowed.]] §1: \"The predecessor is ordered "
         "before the effect and need not be live at it\"", "ADR-0060 §1; R1"],
        ["`Intent`", "**`M_LASTINTENT`, an addition to proposal §10's table**: ADR-0050's rule, which ⟨Q4⟩ declined. It "
         "breaks no property. Its effect is that **a commander who narrows cannot restore**",
         "`m-last-restored`: `NeverRestored` HOLDS; `m-last-safe`: `Safe` HOLDS", "[[green|Recorded]] in §7 as ⟨Q4⟩'s "
         "reason", "ADR-0060 §7"],
        {"group": "Membership.tla → ADR-0061", "accent": "teal"},
        ["`Membership`", "**The one-vote rule is not in §3.** §3's only rule on signing is that a replica signs a drop "
         "only if it has not heard that replica either. **An honest replica that has heard neither of two others could "
         "sign both, and two successors follow.** What forbids it is §2's agreement: one entry at one log index, a step "
         "naming the membership it replaces", "`M_TWOVOTES` breaks `AtMostOneSuccessor` (`m-twovotes-amo`, at "
         "`MaxBallots=6`); the deadlock audit's bound for `Membership`", "[[green|Taken.]] §3 gains it: an honest "
         "replica signs at most one step of a membership. Read as one vote with no second ballot, **a split vote stalls "
         "the schedule for good: safe, and not live**. A Negative follows, and an open obligation: whether a split vote "
         "may be retried, **which `Membership.tla` (no ballot, no view change) neither designs nor checks**",
         "ADR-0061 §3, Negative, Open obligations; R1"],
        ["`Membership`", "**At the archetype the floor is redundant with the schedule.** 7, 6, 5, 4 ends at the last size "
         "whose f is one, so removing the floor's guard changes nothing while the schedule stands. The floor binds a "
         "charter whose schedule runs past it", "`m-below-archetype`: `Safe` HOLDS under `M_BELOWFLOOR`; its breaking "
         "rows set `Schedule={5,4,3}` and `{5,4,3,2}`", "[[green|Taken.]] §4: at this schedule the floor adds nothing "
         "the schedule does not", "ADR-0061 §4; R1"],
        ["`Membership`", "**Five replicas, not seven.** The module runs one plane of five; §1's archetype is seven, "
         "tolerating two captured", "Every row's constants; `Schedule={5,4}` by default", "[[amber|Recorded, not "
         "closed.]] §7: \"Met for TLC and TLAPS at five replicas, and not at §1's seven\"", "ADR-0061 Status note, §7"],
        {"group": "Alone.tla → ADR-0062 §5, §7, §11", "accent": "teal"},
        ["`Alone`", "**Proposal §10 and ADR-0062 §5 cannot both be read literally.** §10: after a lease ends \"the only "
         "effects are hold and the seating's terminal behaviour\". §5 keeps a beacon, and ADR-0065 §2 with ADR-0015 "
         "counts a transmission as an effect. The module states `ExpiryGrantsNothing` of entries and terminal acts, and "
         "bounds the beacon in `AlonePermitsNothing`: **\"It permits no actuation\"**", "`w-beacon`: `NeverBeacon` "
         "VIOLATED; `M_BEACONUNCOUNTED` breaks `AlonePermitsNothing`", "[[green|Taken.]] §5: **the beacon is an "
         "effect**; §10's sentence is true of actuation and is read that way", "ADR-0062 §5; R1"],
        ["`Alone`", "**`M_ALONEACTS` is drawn otherwise than proposal §10 draws it.** §10 has the alone governor permit "
         "one `local` entry. Since a permit needs a live lease, the guard that stops it is the ending, and the mutation "
         "removes that: going alone does not end the lease", "`m-alone-alone`: `AlonePermitsNothing` VIOLATED",
         "[[grey|Not a finding against the record.]] §11 names `M_ALONEACTS` among what `Alone.tla` meets",
         "ADR-0062 §11"],
        {"group": "Outstanding.tla → ADR-0063 (and ADR-0067 R1)", "accent": "teal"},
        ["`Outstanding`", "**1. §3's governor rule names only leases.** Read literally, a captured plane can admit "
         "`ordered` entries without limit and an honest governor carries them out unaccounted",
         "`M_ORDEREDFREE` breaks both per-governor properties under a captured plane, neither under an honest one",
         "[[green|Taken.]] §3: the governor's account charges `ordered` entries as well as leases. **ADR-0067 R1**: "
         "`FD10`'s governor clause follows", "ADR-0063 §3; R1; ADR-0067 R1"],
        ["`Outstanding`", "**2. §4's argument names the last watermark before the revocation.** A watermark covers one "
         "segment and is not cumulative, so it must read: that **no watermark ordered before the revocation** covers",
         "The property as stated and proved: a charge is released by a pre-revocation watermark only",
         "[[green|Taken.]] §4's argument reads so", "ADR-0063 §4; R1"],
        ["`Outstanding`", "**3. The stop is load-bearing.** A watermark ordered after the revocation releases a charge "
         "whose lease may have produced effects since; a hearer that released it and went on granting breaks the "
         "bound. The same watermark carries the fence", "`M_NOSTOP` breaks both effects bounds, and "
         "`HavocPlaneBoundedInEffects` holds", "[[green|Taken.]] §4: \"That stop carries the bound\"",
         "ADR-0063 §4; R1"],
        ["`Outstanding`", "**4. The strict form makes `KUp` a capacity of `KUp` − 1.** `KUp` = 1 grants nothing, and a "
         "lease whose count is `KUp` or more can never be granted. Neither is stated",
         "`w-k1-nogrant`: `NeverGranted` HOLDS at `KUp=1 MaxCount=1`", "[[green|Taken.]] §3: **`kUp` is at least 2**, "
         "and a lease of count `K_up` or more is never granted", "ADR-0063 §3; R1"],
        {"group": "PlaneClock.tla → ADR-0064, ADR-0062 §4", "accent": "teal"},
        ["`PlaneClock`", "**The premise and what this is not.** `NoGrantPastExpiry` rests on the named `ASSUME "
         "ClockPremise`: captured and slow replicas together are fewer than a certificate. **A declared bound with a "
         "premise about time, not a safety theorem**; `Outstanding` carries the bound with no such premise",
         "`m-tooslow-grant`: VIOLATED at `Slow={\"r2\",\"r3\"}`; `m-tooslow-nofail` HOLDS with the premise true",
         "[[green|Taken.]] §4: with the premise false this bound fails (`M_TOOSLOW`), and ADR-0063's still holds",
         "ADR-0064 Status note, §4; R1"],
        ["`PlaneClock`", "**The residual.** Overdue is by the governor's own clock, so `EntryEndsAtExtent`'s third "
         "clause is about `gclock` and not `now`. **A slow governor clock can stretch the entry in progress**, only "
         "when the plane's ticks have also stopped reaching it", "`w-stretched-slow`: `NeverStretched` VIOLATED at "
         "`GovClass=\"slow\"`; HOLDS sound and fast", "[[green|Taken]], on the custodian's decision of 2026.11.10: §5 "
         "defines overdue by the governor's own clock and shows the residual; `NoStretchUnlessSlow` says nothing else "
         "reaches it", "ADR-0064 §5; R1"],
        ["`PlaneClock`", "**A finding on §2.** The first rule on a vote (never sign a tick ahead of your clock) carries "
         "no property: a tick ahead only subtracts. The second (no grant while the next tick is due) carries "
         "`NoGrantPastExpiry`. **The first is availability**, ADR-0032's side", "The module's header",
         "[[green|Taken.]] §2: \"The second rule carries §4's bound, and the first carries availability\"",
         "ADR-0064 §2; R1"],
        {"group": "Peer.tla → ADR-0065", "accent": "teal"},
        ["`Peer`", "**§1's sentence is false read literally.** A peer relays certified facts, leases among them: **a "
         "vehicle whose lease reached it by relay is permitted because of an item received from a peer.** "
         "`PeerAddsNothing` ranges over what a peer originates; a certified lease is the plane's act",
         "`w-relayedlease`: `NeverPermitUnderRelayedLease` VIOLATED", "[[green|Corrected.]] §1 ranges over what a peer "
         "originates, and adds \"so is the same request with any subset of those items\" (`NarrowsInReceived`)",
         "ADR-0065 §1, §9; R1"],
        ["`Peer`", "**What the labels guarantee.** The receiver adds `untrusted` and the topic's name, so those two "
         "survive a captured sender. §3's \"cannot remove any\" holds of an honest governor, and a captured one is the "
         "case in which it matters", "`M_SENDERLABEL` breaks `ReceivedIsUntrusted`; `w-labellow`: "
         "`NeverSenderLabelledLow` VIOLATED", "[[green|Corrected.]] §3: an honest sender's governor adds names and "
         "removes none; **what survives capture is the two names the receiver adds**", "ADR-0065 §3; R1"],
        {"group": "Release.tla → ADR-0066, ADR-0062 §6", "accent": "teal"},
        ["`Release`", "**1. §4's interlock omits that the act names this vehicle.** Without it, one act fires once on "
         "each vehicle, since `unused` is each governor's own record", "`M_ANYVEHICLE` breaks `UsedOnce` (and the "
         "conjunction)", "[[green|Taken.]] §4: the interlock checks **that the act names this vehicle**",
         "ADR-0066 §4; R1"],
        ["`Release`", "**2. \"With no link there is no irreversible effect\" is true of the order, not the effect.** An "
         "act that crossed the link before it was cut is still delivered and fires inside `FreshT`, and **a governor "
         "cannot know the link is cut**. Freshness bounds it", "`w-aftercut`: `NeverFiredAfterCut` VIOLATED; "
         "`M_NOCONTACT` breaks `OrderedInContact`", "[[green|Taken.]] §4: an act is ordered only while the plane is in "
         "contact; Negative: with no link no irreversible effect can be **ordered**", "ADR-0066 §4, Negative; R1"],
        ["`Release`", "**3. \"Aged\" is measured in the plane's ticks, and a captured plane can stop ticking.** "
         "`NoOlderThanDeclared` is a statement about ticks and says nothing of duration, which is the watchdog's",
         "`M_LATEFIRST` breaks `NoOlderThanDeclared`", "[[green|Taken.]] §4: \"Aged is a count of the plane's ticks\"; "
         "duration is ADR-0064 §5's", "ADR-0066 §4; R1"],
    ]
    F = [r if isinstance(r, dict) else r[1:] for r in F]   # the group row names the module
    y += c.table(X0, y, fcols, F, size=13.5, accent="teal") + 80

    # ================================================================== 5. abstraction
    y = band(c, X0, y, "5 · What each module abstracts, and the constants TLC ran it at")
    acols = [("Module", 170, {}), ("Default constants, from the results file (rows may set others)", 700),
             ("What is abstracted, from the header", WW - 870)]
    ars = []
    for d in MODS:
        ars.append([f"**`{d['m']}`**", f"`{data[d['m']]['tlc']['consts']}`", d["abstr"]])
    y += c.table(X0, y, acols, ars, size=13.5, accent="grey") + 80

    # ================================================================== 6. what is not verified
    y = band(c, X0, y, "6 · What none of this verifies", "red")
    specs1 = [
        ("TLC is bounded, and no larger run exists", [
            "Every row runs at the small constants of section 5. **No `-medium` run** at the records' placeholder "
            "values exists for any module (spec/README.md, method step 3), and no simulation at larger bounds.",
            "The proofs are not bounded by constants, but they are **of the modules**, and every module abstracts "
            "(section 5).",
        ], "red", {"tint": False, "dash": "6 4"}),
        (f"{T_ls4} LS4 steps, and a prover with two known unsound cases", [
            f"**{T_ls4} temporal steps** ({', '.join(str(data[d['m']]['crt']['ls4']) for d in MODS)}) rest on LS4, "
            "\"whose answer no checker confirms\". None of the eight is re-encoded in Lean (ADR-0053's route).",
            "The scan looks for the prover's two unsound cases and finds no capture and no renamed difference; it "
            "lists the binder-case candidates for reading. **A certified proof is not a verified one.**",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("Nothing of running code", [
            "**No reference addendum**: every record's reference item is \"Not met\". No test restates these properties "
            "and no trace is replayed through them.",
            "\"A proof of these modules would be of the modules: no refinement to running code exists anywhere in the "
            "corpus\" (proposal §10; G11 §8; T-0045-28).",
        ], "red", {"status": "notbuilt"}),
        ("The `federation` floor stage, `FD1`–`FD14`, is not written", [
            "ADR-0067 §7: \"Not met: no entry is written\". No gate runs; the stage is not shown monotone in what a "
            "vehicle received from peers (`NarrowsInReceived` is the module's, not the stage's).",
            "**No floor is ratified, so nothing here can be in force** (ADR-0067 §5).",
        ], "red", {"tint": False, "dash": "2 3"}),
    ]
    h1 = row_cards(c, X0, y, WW, 30, specs1, size=14)
    y += h1 + 26
    specs2 = [
        ("ADR-0061: PBFT not read, a round not measured", [
            "**\"PBFT is read\"**, and §2's three recalled statements sourced or corrected: **not met**. PBFT is "
            "abstracted to its certificate.",
            "**A measured round among seven** over a deployment's radios: **not met**; the only figure is a simulated "
            "412.3 ms among 20.",
            "**Five replicas modelled, not seven**; a split vote's retry is neither designed nor checked.",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("ADR-0064: the arithmetic not in Lean, and time is discrete", [
            "**The two rules' arithmetic, transcribed and proved** as `mechanism/lean/Topak/Clock.lean` does for the "
            "subtracting interval: **not met** (R1).",
            "No clock rates, no margins, no drift. \"The timing budget is only partly expressible in TLA+\" (ToO "
            "§11.3); ADR-0032 defers a timed automaton.",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("ADR-0068: not revised", [
            "**No R1 row.** §6 still reads \"Each bound in §1 names a property of a module that exists. **Not met: no "
            "module is written**\", though eight now exist.",
            "\"Each row is read against ADR-0045's test\": **not met**. Four rows are trust roots whose identity "
            "nothing issues (its Findings, 1).",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("No reader but the drafter; nothing ratified", [
            "Every record's last condition, **a reader who is not the drafter** (ADR-0029 A2), is not met. ADR-0063: "
            "§4's argument as corrected \"has been read by its author only\".",
            "**Every record is Proposed and an overlay** ⟨Q11⟩; each waits on records before it, and ADR-0058 itself is "
            "Proposed.",
        ], "red", {"tint": False, "dash": "6 4"}),
    ]
    h2 = row_cards(c, X0, y, WW, 30, specs2, size=14)
    y += h2 + 40
    c.legend(X0, y, [
        ("box", "teal", "checked, proved, certified with LS4 (the modules)"),
        ("box", "amber", "Proposed; or a mutation proposal §10 does not name", "6 4"),
        ("box", "red", "not written, not built, not met, residual", "6 4"),
        ("box", "blue", "totals, read from the files"),
        ("box", "green", "taken by R1; matches the record"),
    ])
    return c
