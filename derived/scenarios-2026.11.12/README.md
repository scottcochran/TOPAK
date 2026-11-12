# Scenario inventory

**2026.11.12** · derived · an inventory, not a record · basis: the tree at `dbb2b0c` (`main`) · modelled on the
incident inventory of the `f1-tla` repository (`incidents/`, 2026.11.11) · prepared by the assistant at the
custodian's request · nothing in the tree outside this directory was changed, except this directory's row in
`derived/README.md`

Episodes from telecom, networking, cloud operations, finance, control, game theory, industrial control, energy,
robotics, aviation, space, medicine and AI agents that show where a system's rules, the people and machines
that apply them, and the parties subject to them come apart. Each one is read against TOPAK's records and
modules. It bears on them in one of three ways:

- it is a trace a module can already express;
- it is a fault the fault model or a threat-model row already names;
- it shows something the records or modules cannot yet say.

The [index](INDEX.md) lists every scenario, grouped by sector, and lists the steps no module has yet and the
modules proposed. [FINDINGS_TOPAK.md](FINDINGS_TOPAK.md) consolidates what the scenarios say against the records
and modules: twenty-five findings (`SF-1` to `SF-25`), what the scenarios confirm, the existing `CR-` and `TM`
findings they bear on, the proposed modules grouped by gap, and the suggested entries by record, none made.

## What the inventory says so far

These conclusions come from 45 scenarios in thirteen sectors: 35 incidents, 4 disclosures, 2 case studies,
3 canonical problems and 1 thought experiment. Each fact was checked against the listed sources on 2026-11-12, at least two per incident,
disclosure and case study. 29 of them carry a counterfactual. Where a primary source refused automated fetching
(several `justice.gov`, `nhtsa.gov`, `fcc.gov` and `crtc.gc.ca` pages), the entry names the secondary it used and
what it could not confirm.

**Where the corpus already reaches.** Some scenarios are close to runs a module already has:

| Scenario | What the corpus already has |
|---|---|
| Knight Capital 2012 | `Intent` under `M_NOCOUNT` breaks `EveryEffectHasALease`: the order count lived in the code that failed |
| Northeast blackout 2003 | an alarm processor present and making no progress: `Coupling` under `M_MARK`, with `UnreadBounded` failing |
| Bangladesh Bank 2016 | the confirmations printer as an Observer nothing was coupled to: `M_NOCOUPLE` |
| Überlingen 2002 | ADR-0030 §1's composition (no permit overrides a refusal) and ADR-0065 §1's peer facts that "may refuse and never permit", which is ICAO's post-accident rule |
| Citibank–Revlon 2020 | ADR-0066's human-in-the-loop run as written: `SignedByPerson` and `IrreversibleIsAPersons` hold and the payment is still wrong, which is ADR-0066 §5's own "a key and not a judgment" |
| YouTube 2008, SS7 2014 | `Federation` under `M_TRUSTPLANE`, and `Peer` under `M_PEERENABLES` |
| Replit 2025 | a freeze stated in conversation is no freeze. The corpus's three real ones are a deny (`DenyAlwaysAvailable`), a narrower successor (`SuccessorNeverWidens`) and a bundle refusal (`BundleRefusalHonored`) |

The most cited records are ADR-0045 and ADR-0068 (27 scenarios each) and ADR-0062 (25). The most cited properties
are `DenyByAnyOf`, `PeerAddsNothing` and `DenyAlwaysAvailable` (9 each) and `TerminalNeverWaits` (8). The most cited
findings are CR-2, detection fails open (14), CR-17, a present and trained person presumed (12), and TM9 (10).

**What to model next, by how many scenarios need it.**

| Proposed module | Scenarios | The question it would answer |
|---|---|---|
| `StagedPromotion` | 4: AT&T 1990, Rogers 2022, CenturyLink 2020, CrowdStrike 2024 | Promotion to a declared subset first, with the rest of the domain on the prior digest |
| `SubtractionReach` | 4: AT&T 1990, Optus 2023, CenturyLink 2020, Facebook 2021 | How many cells one item, one deny or one shared dependency can stop. `Observers`' `ReachIsBounded` is the nearest property |
| `RecoveryPath` | 3: Rogers 2022, Optus 2023, Facebook 2021 | The emergency seating's channel declared, given a trusted-base row, and still enabled when what it repairs has failed |
| `Disclosure` | 2: Cruise 2023, surgical robots 2016 | A report to an overseer projected from the record, not written afterwards by people |
| `PeerFederation` | 2: SS7 2014, YouTube 2008 | Several roots, each issuing scoped credentials to the others; `Federation` assumes one root |
| `SeatHandover` | 2: Teterboro 2017, Pulkovo 2006 | Who takes the controls from whom, by one attributed act, with exactly one holder of `Actuate` at every instant |
| `VehicleEnvelope` | 2: Learjet 60 2026, its thought experiment | A grant checked against the grantee's measured margin, not only the grantor's rules |

Thirty-five other modules are each proposed once. Several of them are the same gap in different words:
`MeasuredExtent` and `ExtentGuard`; `EffectConfirmation`, `WorldObserver` and `SensedAdmit`;
`InterlockIndependence` and `SignerIndependence`; `ManualReversion` and `RecoveryPath`; `VehicleEnvelope` and
`MarginEnvelope`. The 280 `outside:` steps in the [index](INDEX.md) were named by nine writers working in parallel, and almost none is reused verbatim, so they
are best read by theme, as below, and not counted.

**Themes that recur:**

1. **Fail-closed assumes that doing less is safe.**
   - In five of the seven telecom and networking outages, every failure was a subtraction: a deny, a disconnect, a
     withdrawal, a self-isolation. TOPAK's safety properties hold throughout, and the harm is availability, which
     the formal layer does not state (CR-37).
   - In the 2003 blackout, the Ukraine grid attack and Ariane 501 (a fail-stop design on a flight sensor), the safe
     move was an act.
   - ADR-0045's class of components "whose failure can only subtract" is safe for authority. It is not safe for
     the world, and no record says so.
2. **Monitors fail in the four ways the F1 inventory found, and in two more.**
   - **Absent:** Therac-25.
   - **Defeated:** by replay (Stuxnet) or by the attacker (the Bangladesh printer).
   - **Present and unread:** Knight's 97 e-mails, MISO's state estimator.
   - **Wrong:** at TMI the light showed that the valve had been told to close, not that it had.
   - **Disabled by its own maintenance:** Buncefield's test lever, MISO's trigger left off.
   - **Silenced by design at the extreme:** AF447's stall warning below 60 kt.

   Coupling covers the dead, partitioned and starved monitor. A replayed loop advances its watermark, which is a
   case beyond ADR-0039 §5's dead and colluding Observers: an honest Observer whose input is forged upstream.
3. **Nothing checks the effect.**
   - ADR-0042 §3 records an `Actuate` as returned, failed or unknown. That is the TMI light, done honestly.
   - No clause confirms that the world changed: TMI, Buncefield, Stuxnet, Mars Climate Orbiter.
   - Under ADR-0049 §4, the orbiter's unit was a claimed field on both sides and a checked field on neither.
4. **A person in the loop is a key, not a judgment.**
   - Three Citibank approvers, the Uber safety operator, the AF447 crew and the Therac-25 proceed key were all
     present, and none was a check.
   - TOPAK's only fast path for a person is a deny, or an emergency seating that needs a quorum.
   - Teterboro 2017 shows the corpus has no rule for when the senior seat must take over.
5. **Promotion has no rings, and unanimity does not help reviewers who share one validator.**
   - CrowdStrike, AT&T, Knight's partial deployment, and Rogers' risk rating, which fell as earlier phases
     succeeded.
   - ADR-0024 already concedes correlated review failure.
6. **Redundancy fails in common mode.**
   - Examples: Ariane's two inertial units, Ronin's four signers held by one operator, AT&T's 114 switches on one
     release, and the Therac-20's hardware interlocks that the Therac-25 dropped.
   - The corpus has independence rules only for Observers and Personas (ADR-0038, ADR-0035).
7. **For AI agents, the corpus agrees by construction, and the gaps are at its edges.**
   - In Replit, EchoLeak and Air Canada, an instruction or statement stayed text and never entered the admit path.
   - EchoLeak passes through a mailbox root labelled by where content is stored, and a `Report` the client
     fetched. The Air Canada tribunal reached ADR-0056's position: the deployer owns its agent's statement.
8. **Game theory sits beside the premise, not under it.**
   - TOPAK makes no claim that its rules are incentive-compatible.
   - The FCC's 1997 code bidding is collusion through a channel the rules let every bidder use, which ADR-0065's
     open topics reproduce.
   - Axelrod's shadow of the future sustains TM11's colluding Observer in a fixed Thinker–Observer pair.
   - ADR-0061's 3f+1 follows from refusing synchronized clocks (ADR-0032), which is Lamport, Shostak and Pease's
     assumption A3. ADR-0061 does not say so.
   - Two Generals is `Release`'s own finding that a governor cannot tell the link is cut.
9. **Hindsight decides the counterfactual.**
   - The video's thought experiment replays the 2026 Learjet 60 at each decision point. With hindsight one different
     choice saves the jet; without it, the same captain may make the same ordinary calls, and each passes every
     check a TOPAK grant makes.
   - Every counterfactual in this inventory has that weakness. Where a safety argument rests on a person's judgment
     in the moment (ADR-0066 §5), its counterfactual holds only with knowledge nobody had.
   - The grants in that flight were each checked against the grantor's rules, never against the grantee's margin.
     Pulkovo 612 is the same climb into a narrowing envelope, with a valid stall warning wired to nothing.
   - TWA 841 was saved by an act far outside the normal envelope, which a range limit in the floor, with break-glass
     retired, would have refused to every seat.

**What these are not.**
- Nine writers of the same lineage as the corpus's drafter wrote the entries in parallel from one brief. That is
  independence of context, not of lineage.
- Many Analyses lean on the command-chain overlay's modules (`Intent`, `Release`, `Peer`, `Alone`, `Outstanding`),
  which are Proposed and written for vehicles. Each entry says where.
- Fault classes for crews were applied unevenly. Every crew in the control and aviation entries is `contested`,
  and the Teterboro captain is `byzantine` in the schema's sense, with a note that the NTSB found no intent.
- Four entries answer a request to include "the scenarios as described in" a YouTube video, *How the Best Captain
  Would Have Saved This Learjet* (channel Unfolded), from a transcript the custodian supplied: the Learjet 60 lost
  over South Florida on 1 November 2026, whose investigation is open and whose cause is undetermined; the video's
  own thought experiment; and the two upsets it compares, TWA 841 (1979) and Pulkovo 612 (2006). The video is cited
  for what it says, not for facts about the crash.
  [2017-AVI-TETERBORO-LEARJET](2017-AVI-TETERBORO-LEARJET.md) was first written as an inferred match before the
  transcript was available. It was the wrong accident, and it is kept on its own merits.

## One file per scenario

`<id>.md` has YAML front matter (the schema representation) and five sections, in this order:

| Section | What goes in it |
|---|---|
| **Summary** | What happened, objectively: times, values, decisions, who did what. No adjectives a party would dispute. For a canonical problem, the problem as its authors posed it |
| **Defensive position** | The case **for** the conduct, design or decision under challenge, as made by the party defending it or by those who spoke for it at the time. Attributed, not ours. For a canonical problem, the case for the protocol, strategy or mechanism the literature offers |
| **Adversarial position** | The case **against** it, as made by the critics, claimants, investigators or attackers on record. Attributed, not ours. For a canonical problem, the impossibility result, the attack or the critique |
| **Outcome** | What the competent body decided or found, when and on what basis: a court, a regulator, an investigation board, a post-incident review, or, for a canonical problem, what the literature settled. Whether the effect was reversed |
| **Analysis** | Ours. What the scenario says against TOPAK: which record, module, action, property, mutation, finding or threat row it touches, what the corpus cannot express, and what row or module it suggests |

"Defensive" and "adversarial" follow the dispute, not the merits. Where an operator was blamed, the defensive
position is the operator's; where a vendor's design was challenged, it is the vendor's.

## The schema is generic

[schema.yaml](schema.yaml) is a JSON Schema with no sector's regulator, no corpus's record and no
specification's module in it. The `f1-tla` schema is specific in five places, and each is generalised here:

| `f1-tla` field | Here | Why |
|---|---|---|
| `season`, `event`, `session` | `kind`, `sector`, `setting` | A scenario may be an incident, a disclosure, a case study, a canonical problem or a thought experiment, from any sector |
| `domains` (F1's) | `concerns` | Twenty-eight concerns that hold across sectors: authority, quorum, revocation, interlock, ingress, cascading failure |
| `regs_at_time` | `rules_at_time` | A regulation, standard, procedure or protocol, as `document`, `clause`, `paraphrase` |
| `analogue_2026` | `analogue` | Where the same question sits in the corpus's records, by record id |
| `ruling`, `result_changed` | `outcome`, `effect_reversed` | Not every sector rules; many investigate or settle. `effect_reversed` is `yes`, `no`, `partial` or `not-applicable` |

Three things are added. Actor faults gain `crash` and `omission`, the distributed-systems classes the F1 fault
model did not need. `detection` gains an optional `note`, for how a fault was found where the means alone do not
say, or the basis of the latency. And `counterfactual`, optional, is the run that would have kept the system within bounds: who
would have had to act, the steps, and the properties that would then have held. It is there for the scenarios
whose question is "what would have saved it", which for TOPAK is the question that matters.

What a reference must resolve to is set in one block of [scenarios.py](scenarios.py), `BINDINGS`. For TOPAK:

| Field | Resolves to |
|---|---|
| `trace[].step`, `counterfactual.trace[].step` | An operator defined in `spec/*.tla` (not the generated `Trace_*` modules), or `outside:<name>` |
| `model.properties`, `counterfactual.holds` | An operator defined in `spec/*.tla` |
| `model.mutations` | A mutation string used in `spec/*.tla` (`M_FENCE`, `M1`) |
| `model.modules` | A module in `spec/`, or `proposed:<Name>` |
| `model.records`, `analogue[].record` | A file `decisions/ADR-NNNN.md` |
| `model.findings` | A `CR-` id in `derived/topak-critical-review-*.md`, a `TM` row of ADR-0068's threat model, or a trusted-base or assumption row (`T-0045-28`, `A-0068-4`) in any record's tables |

The loader reads dates and clock times (`21:34:49`) as strings, so neither needs quoting; YAML 1.1 would otherwise
read the second as a base-60 integer. A bare year in `date` must still be quoted (`"1986"`).

Another corpus reuses the schema unchanged and rewrites that block.

## The main fields

| Field | Meaning |
|---|---|
| `kind` | `incident`, `disclosure`, `case-study`, `canonical` or `thought-experiment`. An incident, disclosure or case study needs two sources and at least one rule at the time |
| `rules_at_time` | The rules as they stood, paraphrased |
| `analogue` | Where the same question sits in TOPAK's records, and the clause |
| `actors[].fault` | `honest`, `honest-error`, `crash`, `omission`, `byzantine`, `contested` (the classification is the dispute) or `none-alleged`, applied to what the outcome found |
| `detection` | How the deviation came to light and how long it took: a monitor, an alarm, an interlock, a counterparty, an insider, a researcher |
| `trace` | The scenario as steps in the modules' vocabulary. The `outside:` steps are the to-do list |
| `counterfactual` | Optional: the run that would have held, in the same vocabulary |
| `model` | The modules, properties, mutations, records and findings it bears on, and a one-line fault class |
| `sources` | Read when the entry was written |
| `verified` | The date the facts were checked against those sources |

## Checking

The checker declares its own dependencies (PyYAML, jsonschema), so `uv` runs it with nothing installed:

```sh
cd derived/scenarios-2026.11.12
uv run --script scenarios.py check    # schema, sections, sector codes, and every corpus reference resolved
uv run --script scenarios.py index    # regenerate INDEX.md
uv run --script scenarios.py vocab Lease_A1 Coupling   # what a step, property or mutation may name
```

`check` fails if a trace step, property or mutation names something that is not in `spec/*.tla`, a record
that is not in `decisions/`, or a finding no review or threat model holds. A rename in a module therefore breaks
the inventory loudly. This directory is dated and frozen like the rest of `derived/`: a later tree that
breaks it gets a new inventory, not an edit to this one.

## Rules for entries

- **Facts from sources, positions attributed.** Every claim in Summary and Outcome must be supported by a
  listed source. Every claim in the two position sections must be attributed to someone who made it.
- **Short quotations only.** Words are quoted only where the words themselves are the point, and briefly.
- **No verdicts in Summary.** Words like "deliberate", "error", "negligent" and "attack" appear only where an
  outcome found them, and are attributed to it.
- **People.** These are public events, published findings and literature. Describe what the record says about
  people's roles and conduct in them, and nothing else.
- **The analysis is TOPAK's, not the sector's.** It says what the corpus would and would not have changed,
  without claiming that TOPAK would have prevented an accident it was never built for.
