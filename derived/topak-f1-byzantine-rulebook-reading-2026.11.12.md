# What a Byzantine reading of the Formula 1 rulebook says about TOPAK

> How does the _byz modelling inform TOPAK?
>
> dated analysis in TOPAK's derived/

(The custodian's questions of 2026.11.12, about the f1-tla repository's `Neutralisation_byz` module.)

**2026.11.12** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
TOPAK at `dbb2b0c` and `scottcochran/f1-tla` at `dae0947`

---

## 1. What this is

f1-tla is a separate repository. It uses the published FIA Formula 1 Regulations as requirements and models them
with this corpus's method:
- the `writing-tla-specs-and-proofs` skill;
- one `Mut` constant, `Never…` witnesses, `f-…` finding rows;
- dated results files that are never edited;
- successor modules over frozen ones.

Its `Neutralisation_byz.tla` applies TOPAK's premise to a rulebook not written for it. It makes some drivers, and
then the Race Director, Byzantine, and asks what the honest parties and the mechanism still guarantee.

This document reads that result back against TOPAK. **Nothing here decides anything.**
- The F1 models are small (two or three cars, three or four laps) and only **checked** by TLC. Nothing in them is
  proved.
- They say nothing about TOPAK's mechanism. What they offer is a worked counterexample: a governed system whose rules
  are obligations on its actors rather than guards a mechanism enforces.
- The correspondences in §3 are analogies.
- Every TOPAK statement below was checked against the record or glossary entry it cites, at `dbb2b0c`. The questions
  in §4 are leads for the custodian, not findings against the corpus.

---

## 2. The external model in brief

The models take their requirements from the 2026 FIA Formula 1 Regulations, Section B [Sporting], Issue 09
(2026.10.01). They are pinned by digest in f1-tla's `rules/sources.tsv`, and no FIA text is copied.

**`Neutralisation.tla`** (`f97efc68aedc14d2`) covers:
- the Virtual Safety Car, the Safety Car, the red flag and resumption, and the end-of-session signal (B5.12 to B5.16);
- 8 properties with their articles, 10 single-guard mutations and 18 witnesses;
- 3 findings: gaps where Section B gives no rule.

Its results file (`54e222dfa9d0815f`) has 112 rows, all as expected.

**`Neutralisation_byz.tla`** (`3e369b4e9ada70d6`) extends it without editing it. With its faults off it reproduces
the base module's state counts (2,366 and 9,788). It adds two kinds of Byzantine actor:
- **Byzantine drivers** (`Byz ⊆ Cars`): they overtake in any mode, breach the minimum time under VSC or SC, and leave
  through a closed Pit Lane exit. Three monitors record what they do. The text names the monitor for only one of the
  three, the FIA ECU's minimum time.
- **A Byzantine Race Director** (`RDByz`): withdraws the SC against the lapped-car guards, sends a suspended race
  straight to green, and opens the Pit Lane exit while it should be closed.

Its results file (`5f8e55238c13c4f8`) has 54 rows, all as expected. The outcome:

| Fault | Fails | Holds |
|---|---|---|
| Byzantine drivers | `NoForbiddenPass` only. By design: the rule prohibits; nothing prevents | the other seven, and every violation stays **on record** given its monitor |
| Byzantine Race Director | `UnlapComplete`, `UnlapThenFollowingLap`, `PitExitClosed`, `RedResumesBehindSC` | honest drivers' overtaking, and all three classification properties |

f1-tla's `FINDINGS.md` (`a98dde89f4e4c215`) records two results relevant here:
- **F-4:** Section B places nothing between the Race Director and those four decisions, neither in advance nor
  while they are made.
- **C-4:** two of the three driver obligations have no monitor named in the text.

f1-tla also holds an inventory of 24 historical episodes (`incidents/`), each checked against at least two sources.
§3 and §4 draw on it by identifier.

---

## 3. Where the external result agrees with choices TOPAK has made

### 3.1 Every decision that broke a property under the Byzantine Race Director *adds* authority

The three actions `RDByz` enables are `ByzWithdrawSC`, `ByzRedToGreen` and `ByzOpenPit`. All three are
**relaxations**:
- ending a neutralisation;
- resuming racing;
- reopening an exit.

None of the Race Director's *subtractive* decisions (deploying the VSC or SC, the red flag) is in the forbidden set.
Section B lets the Race Director subtract and add alone, in real time. In F1, then, the four broken properties all
sit on the *adding* side.

TOPAK draws its line exactly there:
- **"Runtime subtraction is not promotion"** [A]: e-stop, expiry, revocation and `deny=all` need no quorum.
- **Adding authority goes through promotion.** ADR-0052 §1: "Adding authority is done by promotion." Break-glass,
  the one fast addition, is an emergency seating that the break-glass roster's quorum activates for one named person
  and one round (ADR-0052 §2).
- **A change to the rules floor needs two keys** even to tighten ("Two keys, both directions" [A]).

So in TOPAK's terms, finding F-4 describes a system with no asymmetry between adding and removing authority. Abu Dhabi
2021 (`2021-ABU-SAFETY-CAR-RESTART`) is a real instance of a fast, unilateral addition going wrong.

The F1 governance response after 2021 was:
- two Race Directors alternating;
- a virtual race control room;
- a permanent adviser.

As far as the inventory's sources describe it, that response added support and observers. It added no quorum on the
additive decisions and no power for anyone else to stop them. ADR-0052 §4 goes further on both counts: an emergency
seat's topic is read by the domain's operators, and "a finding is a deny any of them can make".

### 3.2 What survived the Byzantine Race Director was computed mechanically

The properties that hold under `RDByz` are the three classification properties. They hold because the result is a
function of facts (laps completed), whatever the Race Director decides. B5.16.2 makes an early or late chequered flag
harmless by recomputing from laps, not by preventing the error (`2014-CHN-EARLY-CHEQUERED-FLAG`). The properties that
fail rest on the Race Director's *judgment*.

That is ADR-0007's distinction found in another domain:
- semantic judgment is never a lift;
- the admit path consumes only syntactic lifts of typed fields ("Syntactic lift" and "Semantic lift" [A]).

The external result is evidence that the distinction is where Byzantine-tolerance comes from. Guarantees that rest on
an actor's judgment fail as soon as that actor is Byzantine. Guarantees computed from recorded facts don't.

### 3.3 Prohibiting is not preventing

`NoForbiddenPass` fails as soon as one driver is Byzantine, because no rule in Section B *prevents* an overtake under
the Safety Car. The regime is detection, then sanction. The inventory shows its failure modes:

| Failure mode | Episodes |
|---|---|
| Detection taking months or years | `2008-SIN-DELIBERATE-CRASH`, `2007-WMSC-SPYGATE` |
| Detection through insiders, obtained with immunity | the same two |
| Coalitions | `2010-GER-TEAM-ORDERS` and both of the above |
| A rule deleted because the act it prohibited could not be observed | team-orders ban, 2010 |

TOPAK puts containment in the admit path and treats detection as a second line, deny-only. The external record is a
long, documented case of a governance regime that has only the second line.

### 3.4 Observer findings can only deny, which is what lets the Observer itself be Byzantine

`Neutralisation_byz` had to assume its monitors honest (its C-4), because in F1 a monitor's record leads to a
penalty. A lying monitor harms an honest competitor, so the stewards and timekeepers who act on monitor records join
the trusted base.

TOPAK assumes the opposite:
- An Observer is a principal: Byzantine, with its own lease, evictable alone ("Observer" [A]; ADR-0037).
- Every finding is deny-only.
- Coupling only refuses: "the Thinker waits rather than being evicted" ("Coupling" [A·CR]; ADR-0039).

The external case shows what that choice avoids. Once a monitor's output can punish, someone honest has to stand
between the monitor and the sanction.

### 3.5 Coupling, and a monitor that kept up with detection but not with decisions

At Austria 2023 (`2023-AUT-TRACK-LIMITS`) the monitors flagged more than 1,200 track-limit reports. The stewards could
not review them during the race, which carried on. The result was revised nearly five hours later, after a
competitor's protest.

ADR-0039 rejects exactly this:
- "Presence is not progress" [A·CR].
- A Thinker's next round waits for coverage of its last.

F1 cannot stop a race to clear a backlog. TOPAK chose that it would.

### 3.6 Independent records

At Brazil 2003 (`2003-BRA-RED-FLAG-COUNTBACK`) the official timing record was wrong about which lap the leader was
on. A second record, the team's own ECU log, corrected it five days later. The correction rested on the two records
being independent.

TOPAK's counterparts:
- "Seat distinctness" [A]: an Observer's Persona differs from its Thinker's by lineage.
- ADR-0039's rejection of Kafka consumer offsets as a watermark: a Byzantine Observer "can advance them without
  reading".

Both express the same principle: a check is worth what its independence from the checked party is worth.

### 3.7 Binding a decision to the rule revision it was made under

At Racing Point 2020 (`2020-STY-BRAKE-DUCT-DESIGN`):
- design data received legitimately while brake ducts were not a listed part became non-compliant once they were
  listed;
- the stewards had to draw a line between front and rear ducts.

TOPAK's "Bundle revision binding" [A·CR] (a bundle decision counts only from the revision the lease names) is the
design that removes that kind of retroactive effect.

### 3.8 A design that met every rule and defeated the stated purpose

In 2009 (`2009-ICA-DOUBLE-DIFFUSER`), the FIA International Court of Appeal held a design legal:
- it met every technical article;
- the appellants argued it defeated the purpose stated in the preamble to the aerodynamic rules, which was to help
  overtaking;
- the court treated the preamble as unenforceable.

That is "Floor fitness" [O], the gate the corpus names as missing. The gates show that a floor is well formed. They
don't show that it is fit for its purpose. The external outcome is a caution for when that gate is written: once the
letter and the purpose part, an adjudicator holding to the letter is the expected outcome, not an exception.

### 3.9 Correcting, not replacing

Across the inventory, remedies after the race recomputed the result of the race that was run:
- `2003-BRA-RED-FLAG-COUNTBACK`;
- `2014-CHN-EARLY-CHEQUERED-FLAG`;
- `2023-AUT-TRACK-LIMITS`.

None replaced the race with a different one:
- `2021-ABU-SAFETY-CAR-RESTART`: "retrospectively shorten the race" was the stewards' stated reason for refusing;
- `2008-SIN-DELIBERATE-CRASH`;
- `1997-EUR-CHAMPIONSHIP-EXCLUSION`.

TOPAK's discipline is the same:
- an admit that fails its re-check is "void: ordered, recorded and without effect" ("Decide, order, re-check" [A]);
- revocation is permanent within the chain [A·CR].

---

## 4. Questions the external result raises for TOPAK

These are leads. Each says what was checked in the corpus and what was not found.

### 4.1 Subtraction is safe but not neutral

**The episode.** Singapore 2008 (`2008-SIN-DELIBERATE-CRASH`):
- One car crashed on its team's instruction.
- That brought out a correct, honest, field-wide subtractive response, the Safety Car.
- The response advantaged the team-mate, whose early pit stop made the neutralisation pay.
- The deviation was in the *input* to an honest decision maker. No property of `Neutralisation` or
  `Neutralisation_byz` is violated by it.

**What TOPAK says.**
- Runtime subtraction needs no quorum ("Runtime subtraction is not promotion" [A]).
- An operator is havoc ("Operator" [A·Pv]).
- An operator with a live lease may `FenceEpoch`, the fleet fence (ADR-0050, the table of operator actions; a lapsed
  operator stops only its own domain).
- Safety holds for every such stop, because a stop only removes authority.

**The question.** Can a Byzantine principal, or a coalition, provoke an honest operator into a subtraction, or can a
havoc operator perform one, that benefits a colluding principal in another cell? Examples would be:
- an e-stop;
- a targeted revocation on a shared Persona or profile;
- a fleet fence.

What would decide the benefit is where each cell stands at the moment of the stop: mid-round, between rounds, just
promoted.

**What was checked.** The glossary, ADR-0039, ADR-0050, ADR-0052 and the Theory of Operation were searched for any
treatment of the *distributional* effect of a subtraction. "Fairness" there means TLA+ fairness, as in assumption
A12. Nothing addressing who gains from a stop was found.

**Why it may matter.** TOPAK's claims are containment claims, so this sits outside them by design. Whether that
holds depends on how cells relate:
- Where cells cooperate, it may be harmless.
- Where cells serve different parties and compete for resources or deadlines, it is a way to misuse a mechanism that
  is entirely safe.

**Possible next steps:**
- an entry in the next residual-risk statement or an assumption of use;
- an adversary row of ADR-0068's kind;
- a small TLA+ module with two cells, a provoked fence, and a progress property that fails.

f1-tla has the analogous module in its plan: `Neutralisation_incident`, a deliberate incident with a hidden flag
and a coalition over a team's two cars.

### 4.2 Coalitions below the capture threshold

**What TOPAK says.**
- It names anchor capture at a threshold as its headline residual ("Anchor capture" [A]).
- It uses seat separation and lineage independence against collusion at an edge.
- ADR-0039 says "Collusion stays open". ADR-0068, Proposed, lists TM11, a colluding Observer, as bounded by
  "Nothing. Coupling cannot see collusion."

**The external record.** The gravest episodes in the inventory are all small coalitions whose gain shows only
jointly, across principals with a common owner: team orders, Singapore 2008 and Spygate 2007. `Neutralisation_byz`
could not express them, because its Byzantine actors are individuals.

**The question.** Does any TOPAK property range over a *coalition's* joint effect? For example: two Thinkers on one
Persona or one provider, the "same team", coordinating a gain that no property stated for a single cell would
detect.

**What was checked.** The corpus's own statements that collusion is open, quoted above. Whether some module already
states a property over a coalition was not checked across all modules.

### 4.3 Whether the anchor's decisions reach everyone they affect

**The episode.** At Ferrari 2020 (`2020-FIA-FERRARI-PU-SETTLEMENT`), the governing body settled a compliance
question confidentially. Seven competitors objected publicly, demanding "full and proper disclosure". Their
complaint was not that the decision was wrong, but that they, the parties it affected, could not check it.

**What TOPAK says.**
- The trust anchor is a havoc issuer: safety holds for every issuance it could make ("Trust anchor" [A]).
- The audit chain runs from an effect to the intent axiom ("Audit chain" [A·CR]).

**The question.** Is it stated anywhere that every issuance, and every lifted revocation, is *visible to every
principal it affects*, rather than only recorded?

**What was checked.** The glossary was searched for "publish", "visible", "relying part" and "transparen". The only
hit was unrelated. The records and the Theory of Operation were not searched in full, so this may be stated
elsewhere.

### 4.4 A measurement that can be anticipated

**The episode.** Ferrari 2019–2020 was reported as a suspicion that a sensor's sampling could be anticipated. The
response was more measurement: technical directives adding sensors.

**What TOPAK has already done.** ADR-0039 meets this in kind:
- it states that the Observer's heartbeat, watermark and coverage are "its own assertions";
- it rejects a transport-derived watermark that a Byzantine Observer could advance without reading.

So this is noted as convergent, not open. The general question for any future mechanism-side measurement is whether
the principal it measures can anticipate it.

### 4.5 A habit of method

f1-tla pins the exact state count on its unmutated `Safe` rows. That rule exists because a constant override was
once silently dropped, and the larger-constants row ran at the defaults without any row failing.

In TOPAK at `dbb2b0c`, the rows files `Coupling_live-rows.txt` (14 of 69 rows) and `Emergency_live-rows.txt` (20 of
32) pin `states=`. The other fifteen rows files pin none. `live-gen-results.sh` prints the constants in each
section's heading but does not compare them with anything.

Pinning the count on each module's unmutated `Safe` rows would catch the same class of error at the cost of one
field per row.

---

## 5. What not to read into this

- The external models are bounded and checked, not proved. Their constants are small.
- The analogies in §3 match structure, not mechanism. F1 has no admit path, and nothing here tests TOPAK's.
- The inventory's facts are as its sources state them. Its positions are attributed to the parties. Its analyses are
  f1-tla's own.
- Where §3 cites a TOPAK record, the citation was checked at `dbb2b0c`. Where §4 says something was not found, it
  says what was searched.
- §4.1 is the only question here that names a property class TOPAK states nowhere, the distributional effect of a
  safe action. It is also the one most worth a module.

## 6. Sources

**f1-tla at `dae0947`:**

| File | Digest |
|---|---|
| `f1-tla/spec/Neutralisation.tla` | `f97efc68aedc14d2` |
| `f1-tla/spec/Neutralisation_byz.tla` | `3e369b4e9ada70d6` |
| `f1-tla/spec/Neutralisation-results-2026.11.11.txt` | `54e222dfa9d0815f` |
| `f1-tla/spec/Neutralisation_byz-results-2026.11.11.txt` | `5f8e55238c13c4f8` |
| `f1-tla/FINDINGS.md` | `a98dde89f4e4c215` |

Also `incidents/` (24 entries, cited by identifier), `rules/sources.tsv` and `PLAN.md`.

**TOPAK at `dbb2b0c`:**
- **Records:** ADR-0007, ADR-0037, ADR-0039, ADR-0050, ADR-0052, ADR-0068 (Proposed).
- **Glossary entries:** "Runtime subtraction is not promotion", "Two keys, both directions", "Trust anchor",
  "Anchor capture", "Operator", "Observer", "Coupling", "Seat distinctness", "Syntactic lift", "Semantic lift",
  "Bundle revision binding", "Floor fitness", "Decide, order, re-check", "Audit chain".
- **Spec files:** the rows files in `spec/`.
