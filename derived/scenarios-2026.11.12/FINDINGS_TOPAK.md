# TOPAK findings from the scenario inventory

**2026.11.12** · derived · findings, not a record · basis: the tree at `dbb2b0c` (`main`) and the 45 scenarios in this
directory · prepared by the assistant at the custodian's request · nothing in the tree outside this directory was
changed · **suggested entries, none made**

These are the places where the scenarios in this inventory show the corpus saying too little, saying something the
record contradicts, or saying the right thing in a record that is not in force. A finding here means "the records
and modules do not say this". It does not claim that TOPAK would have prevented an accident it was never built for,
and it does not claim that a sector's own rules got it wrong. Every clause quoted below was opened in the tree at
`dbb2b0c` while this document was written. Every scenario fact is the entry's, with that entry's sources.

**Not independent.** Nine writers of the same model lineage as the corpus's drafter wrote the entries, and this
document consolidates their Analyses. That is independence of context, not of lineage, and it is not the reader
ADR-0029 A2 asks for.

---

## 0. Summary

| Id | Finding | Rests on | Weight | Scenarios |
|---|---|---|---|---|
| [SF-1](#sf-1) | "Failure can only subtract" classes a failure by what it does to authority; what a stop does to the world is priced nowhere | In force | High | 15 |
| [SF-2](#sf-2) | Nothing bounds how many cells one subtraction can stop | In force; Proposed | High | 6 |
| [SF-3](#sf-3) | The emergency path is not required to survive what it is meant to repair | In force, provisional | High | 9 |
| [SF-4](#sf-4) | Nothing checks that an effect happened; an `Actuate`'s outcome is the tool's claim | In force | High | 7 |
| [SF-5](#sf-5) | Coupling has four more blind spots than the two ADR-0039 §5 names | In force | High | 11 |
| [SF-6](#sf-6) | Promotion reaches the whole domain at once, and nothing retires a superseded revision | In force | High | 7 |
| [SF-7](#sf-7) | Independence is required of Observers and Personas only | In force; Proposed | High | 9 |
| [SF-8](#sf-8) | The floor cannot see how big an act is; the archetype's Run has no extent and no count | In force; overlay | High | 8 |
| [SF-9](#sf-9) | Inputs are typed without range, unit or granularity, and a field's meaning is per revision | In force | Medium | 5 |
| [SF-10](#sf-10) | Labels by store miss mixed stores, and a `Report` a client renders is an unmodelled egress | In force | Medium | 1 (+2) |
| [SF-11](#sf-11) | A freeze or a policy stated as text is not on the admit path, and nothing lets a user put it there | In force; Proposed | Medium | 2 |
| [SF-12](#sf-12) | Revocation is a grim trigger chosen without being stated as a choice | In force | Medium | 3 |
| [SF-13](#sf-13) | The floor's host and the voter's tools are trusted where the scenarios attack them | In force | Medium | 4 |
| [SF-14](#sf-14) | The record survives; the report to an overseer is still composed by people | In force; Proposed | Medium | 6 |
| [SF-15](#sf-15) | A person in the loop: what they are shown, who takes over, what a hand-back carries, continuous control | Proposed; in force | High | 9 |
| [SF-16](#sf-16) | A terminal behaviour fixed in advance exists only in the overlay | Proposed | Medium | 8 |
| [SF-17](#sf-17) | Peers: one root only, honest peers cannot prompt an act, outsiders cannot refuse, permitted channels carry collusion | Proposed | Medium | 8 |
| [SF-18](#sf-18) | Reversibility is not a property of the act alone | In force; Proposed | Medium | 5 |
| [SF-19](#sf-19) | Withholding is argued case by case, and a joint effect cannot be stated | Proposed | Low-Medium | 2 |
| [SF-20](#sf-20) | ADR-0061 does not say where its 3f + 1 comes from, and one of its recollections is off | Proposed | Low | 1 |
| [SF-21](#sf-21) | ADR-0058's *Keep* lets a kept node's environmental givens go unrestated | Proposed | Low | 2 |
| [SF-22](#sf-22) | A grant is checked against the grantor's rules, never against the grantee's measured margin | In force; Proposed | Medium-High | 3 |
| [SF-23](#sf-23) | A parent's narrowing is unilateral, and a parent cannot oblige an act; declining a grant is already a local deny | In force; Proposed | Medium | 3 |
| [SF-24](#sf-24) | A range limit in the floor, with break-glass retired, refuses an out-of-range rescue to every seat | Provisional; in force | Medium | 1 |
| [SF-25](#sf-25) | Hindsight decides any counterfactual that rests on a person's judgment in the moment | Proposed; in force | Medium | 3 |

## 1. How to read it

- **Identifiers.** `SF-n` is minted here, for this inventory, and does not continue the `CR-` series. A finding the
  critical reviews already hold is cited by its `CR-` id in §7, not re-minted.
- **Rests on.** *In force* is a record Accepted (genesis); *provisional* marks ADR-0050 and ADR-0052, Accepted with
  provisional status; *Proposed* includes the command-chain overlay (ADR-0059 to ADR-0068), ADR-0035, ADR-0051,
  ADR-0054 to ADR-0058. A finding against a Proposed record matters for that record's revision, not for the state of
  record.
- **Weight.** *High*: it bears on how a guarantee in force reads, or recurs in four or more scenarios from three or
  more sectors. *Medium*: a real gap, narrower or less often seen. *Low*: a correction or a statement a record owes.
  Weight is this document's judgment; it is not a ratification grade.
- **Scenarios** are linked by file. "Holds" and "breaks" name properties and mutations in `spec/*.tla`, as the
  entries' front matter does; `scenarios.py check` resolves every one of them.

---

## 2. Findings against records in force

<a id="sf-1"></a>
### SF-1. "Failure can only subtract" classes a failure by what it does to authority; what a stop does to the world is priced nowhere

**Weight:** High. **Rests on:** ADR-0045 §2 (in force), ADR-0038 §5, ADR-0031, ADR-0050 (provisional), CR-37.

**What the scenarios show.** In seven scenarios every failure, or the failure that mattered, was a subtraction:
a switch out of service, a route withdrawn, a host that stopped, a sensor that stopped, a pause.

- Telecom and networking: [AT&T 1990](1990-TEL-ATT-4ESS-CASCADE.md), [Rogers 2022](2022-TEL-ROGERS-OUTAGE.md),
  [Optus 2023](2023-TEL-OPTUS-OUTAGE.md), [CenturyLink 2020](2020-NET-CENTURYLINK-FLOWSPEC.md) and
  [Facebook 2021](2021-NET-FACEBOOK-BACKBONE.md).
- Cloud: [CrowdStrike 2024](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md) and [S3 2017](2017-CLD-S3-PLAYBOOK-TYPO.md).
  Removing servers subtracts capacity.

TOPAK's safety properties hold through every one of these runs, and the harm is availability. Eight more show where
doing less was not the safe direction:

- [Flash Crash 2010](2010-FIN-FLASH-CRASH.md): each liquidity provider's pause was safe for that firm, and together
  the pauses emptied the books.
- [Ariane 501](1996-SPC-ARIANE-501.md): a fail-stop design on the only attitude source.
- [AF447](2009-AVI-AIR-FRANCE-447.md): automation that withdrew correctly and handed a diagnosis to a surprised crew.
- [Northeast blackout 2003](2003-NRG-NORTHEAST-BLACKOUT.md): the grid needed 1,500 MW shed by 15:46.
- [Ukraine 2015](2015-ICS-UKRAINE-GRID.md): the stall lasted until people restored power by hand.
- [Surgical robots](2016-ROB-SURGICAL-ROBOT-ADVERSE-EVENTS.md): 462 conversions and 221 aborted procedures, where
  the halt itself was the cost.
- [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md): a valid stall warning, where the act the manual prescribed, more
  speed, was an addition.
- [The video's thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md): refusing the descent was the safe
  direction for the jet and an act inside the controller's plan (SF-23).

**What the corpus says.** ADR-0045 §2 admits a component to the trusted base when its failure "can only subtract",
and such a component "needs no proof, no key and no quorum". The corpus prices availability in several places:

- ADR-0038 §5: "More Observers never lower safety and may lower availability."
- ADR-0031: "A fence storm is an availability event."
- ADR-0050: recovery from a fleet stop is "the safe direction and it is the slow one".
- ADR-0062 §7, in the overlay (Proposed): "A stall that never ends is safe" is false of a body in motion.

**What it does not say.** None of these is a statement in force that a stop has a cost the deployment must declare.
ADR-0045's rows record what a component's failure does to authority, and they have no column for what its stop does
to the process it controls. The Analysis of the Ariane entry puts it in one line: the test "classes components by
what their failure does to *authority*; it has no column for what a stopped component does to a control loop". The
liveness work (CR-37, now partly addressed by `Coupling_live` and `Emergency_live`) proves that some stalls end. It
says nothing about how long a fleet takes to come back, or what a stall does outside the deployment.

**What would close it** (suggested, none made):

1. An ADR-0045 amendment adding a declared column per row, *what a stop of this component does to the effects in
   flight*, with "nothing" as an allowed answer.
2. A deployment-declaration field (ADR-0023, ADR-0058) for the availability residual of fail-closed: which stops
   the deployment accepts, and which it must avoid by an act.
3. For the overlay, carrying ADR-0062 §7's sentence into the archetype's text for any domain whose effects are on
   bodies or processes in motion (see SF-16).

<a id="sf-2"></a>
### SF-2. Nothing bounds how many cells one subtraction can stop

**Weight:** High. **Rests on:** ADR-0038 (in force; `Observers`), ADR-0050 (provisional), ADR-0065 §1 (Proposed).

**What the scenarios show.** One honest item stopped a whole domain, in four different ways:

- **A recovery message:** [AT&T 1990](1990-TEL-ATT-4ESS-CASCADE.md). A correct message, failed on by the receiver.
- **Identical limits on a shared input:** [Optus 2023](2023-TEL-OPTUS-OUTAGE.md). About ninety routers tripped
  together.
- **A deny with a wildcard reach:** [CenturyLink 2020](2020-NET-CENTURYLINK-FLOWSPEC.md).
- **A central partition:** [Facebook 2021](2021-NET-FACEBOOK-BACKBONE.md). Every DNS location went alone at once.

[CrowdStrike 2024](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md) and the [Flash Crash](2010-FIN-FLASH-CRASH.md) are the same
shape, from a content file and from a market.

**What the corpus says.** `Observers` proves `ReachIsBounded`: a cell Observer's finding cannot name a principal
outside its cell (`M_REACH` breaks it). That bounds whom a monitor may stop *by decision*. Other clauses accept the
residual outright:

- ADR-0050's consequences: "Any one operator can stop a domain, and any one with a live lease the fleet."
- ADR-0065 §1 (Proposed): a captured governor that lies "can only stop others".
- ADR-0068: TM2 and TM13 carry "peers stalled by claims" as residual.

**What it does not say.** No property bounds how many cells one item, one deny or one shared dependency can stop
*by fault*. The corpus counts "stopping others" as the safe residual. These scenarios measure it at national scale,
from honest inputs.

**What would close it.** `proposed:SubtractionReach` (4 entries): a property that no single item, deny or shared
dependency takes more than a declared fraction of a domain's cells out of service. It would be stated against the
item's declared target, with the receiving side's failure inside the model, and it is the fault-side twin of
`ReachIsBounded`. A deny's scope is already fixed by its variant (`Revoke(o, p)` against `FenceEpoch`), which is
real protection. But nothing checks that a deny whose match is a pattern stays within its declared target, and a
deployment whose denies match on traffic would need that check (CenturyLink).

<a id="sf-3"></a>
### SF-3. The emergency path is not required to survive what it is meant to repair

**Weight:** High. **Rests on:** ADR-0052 §1, §6, §7 (in force, provisional); ADR-0050 §4.

**What the scenarios show.** In five scenarios, the channel the repair needed ran over the thing that had failed:

- [Facebook 2021](2021-NET-FACEBOOK-BACKBONE.md): the backbone; engineers needed physical access to data centres.
- [Rogers 2022](2022-TEL-ROGERS-OUTAGE.md): the management network ran over the failed IP core, and staff relied on
  Rogers' own phones.
- [Optus 2023](2023-TEL-OPTUS-OUTAGE.md): network elements had to be rebooted physically.
- [CenturyLink 2020](2020-NET-CENTURYLINK-FLOWSPEC.md): the deny blocked the sessions that would carry its own
  withdrawal.
- [Ukraine 2015](2015-ICS-UKRAINE-GRID.md): the operators' consoles were the attacker's.

In [Knight 2012](2012-FIN-KNIGHT-CAPITAL.md) no stop existed at all. In the
[surgical robots](2016-ROB-SURGICAL-ROBOT-ADVERSE-EVENTS.md) the emergency path is conversion to another technique,
which leaves the robot entirely. At [TWA 841](1979-AVI-TWA-841-UPSET.md) the rescue was an act the emergency path
could not have reached in 63 seconds (SF-24). At [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md) the investigators
found the approach-to-stall exercise on the books could not be flown on the type's simulator: an exercise the device
cannot perform proves only that it was scheduled.

**What the corpus says.**

- **§1:** the emergency key is independent of single sign-on, because "an emergency path that needs the identity
  provider fails when the provider does".
- **§6:** "a drill is a real activation", at least once per domain per epoch.
- **§7:** "a person acting outside the mechanism" is out of scope.
- **ADR-0050 §4:** a deny needs no quorum and no peer (`DenyAlwaysAvailable` in `Operators`).

**What it does not say.**

- **The channel.** §1's argument applies equally to the network and to the operators' consoles, and no record
  makes it. `Emergency_live` proves `EmergencyNeverCoupled`, but whether the roster's approvals can reach the
  mechanism is assumed.
- **The drills.** A drill run with the network up proves the roster and the keys, not the path.
- **The deny.** `DenyAlwaysAvailable` is a fact about the mechanism. In Ukraine the deny ran through the same
  console as the attack.
- **Manual recovery.** §7 is honest that out-of-band recovery is out of scope. That recovery is the whole of
  Ukraine's, and the whole of Facebook's.

**What would close it.**

1. `proposed:RecoveryPath` (3 entries): the emergency seating declares the channel its approvals and calls travel on,
   that channel gets a trusted-base row with its failure direction, and a property states that activation stays
   enabled under the failure of any component the seat may be asked to repair.
2. An ADR-0052 §6 amendment: each drill names the failure it assumes.
3. A custodian decision on `proposed:ManualReversion`: whether a declared out-of-band path around the mechanism is
   in scope, with the mechanism's later state reconciled from what the people did. Every current record treats a
   path around the mechanism as the thing to prevent, so this needs a record, not a module.

<a id="sf-4"></a>
### SF-4. Nothing checks that an effect happened; an `Actuate`'s outcome is the tool's claim

**Weight:** High. **Rests on:** ADR-0042 §3, ADR-0049 §4, ADR-0015 (in force).

**What the scenarios show.** Each of these acted on a report of an effect rather than on the effect:

- [Three Mile Island](1979-ICS-THREE-MILE-ISLAND.md): the indicator showed that the relief valve had been told to
  close, not that it had.
- [Buncefield 2005](2005-ICS-BUNCEFIELD.md): a tank gauge stuck while the inlet ran.
- [Stuxnet](2010-ICS-STUXNET.md): operators were shown recorded normal values while the PLCs acted.
- [Mars Climate Orbiter](1999-SPC-MARS-CLIMATE-ORBITER.md): impulse data in the wrong unit, with an independent
  derivation unused.
- [Ariane 501](1996-SPC-ARIANE-501.md): a diagnostic word read as attitude.
- [Therac-25](1986-MED-THERAC-25.md): "verified" displayed for a prescription the magnets were not set to.
- [Surgical robots](2016-ROB-SURGICAL-ROBOT-ADVERSE-EVENTS.md): uncommanded instrument motion.

**What the corpus says.** ADR-0042 §3 writes one record per admitted `Actuate`, with `outcome` one of `returned`,
`failed` or `unknown`. That is the TMI light done honestly: it says the call was made and what the tool reported. Two
more clauses bear on this:

- ADR-0049 §4 marks each field of an entry **checked** or **claimed**; a result's label is claimed.
- ADR-0015 orders and audits every boundary crossing; the crossing is what is audited.

`RunCoupling`'s `NoEffectWithoutLiveObserver` guarantees someone reads the record. That Observer would have read
"close valve, returned" and found nothing.

**What it does not say.** No clause or module confirms that the world changed as the act said it would. TOPAK's
Observer reads the round topic, which the mechanism writes. This is the design's real defence against replay (SF-5),
and its price: the Observer watches acts, never the plant. ADR-0068 makes the overlay's measure of an extent and its
position source trust roots (T-0068-4, T-0068-7). Its §6 records that nothing issues them, and Buncefield is that
row failing on the record.

**What would close it.** One module, from four entries that propose it in different words (`EffectConfirmation`,
`WorldObserver`, `MeasuredExtent`, `SensedAdmit`):

1. An allowlist entry may declare a confirming probe, a `Consult` on a distinct entry over a channel separate from
   the command.
2. A disagreement, or a confirmation missing past a bound, is a finding raised to everyone who reads the topic.
3. A mutation reads the probe from the command's own channel. A probe that reads the solenoid's state is the TMI
   light again.

The finding stays deny-only, which fits a stuck valve badly: refusing the next admit does not close it. What the
finding buys is that a person learns at once (SF-5's `MonitorOfMonitor` and SF-15).

<a id="sf-5"></a>
### SF-5. Coupling has four more blind spots than the two ADR-0039 §5 names

**Weight:** High. **Rests on:** ADR-0039 §1, §2, §5 (in force); CR-2.

**What the corpus says.** ADR-0039 makes liveness progress, not presence: a fresh heartbeat *and* a watermark within
`K`. It couples every effect-bearing Run admit to it (`NoAdmitWithoutLiveObserver`, `NoEffectWithoutLiveObserver`;
`M_NOCOUPLE` and `M_MARK` break them). §5 says what it does not cover: "It cannot separate an honest Observer from a
colluding one." CR-2, detection fails open, is the most cited finding in this inventory, in 13 scenarios. The
critical reviews mark it three of four cases closed by ADR-0039.

**What the scenarios add.** Four more failure shapes, each on the record:

1. **An honest Observer whose input is forged upstream.**
   - **Seen in:** [Stuxnet](2010-ICS-STUXNET.md).
   - A replayed loop of sensor values *is* progress: every screen updates and every alarm routine runs, so a
     coupling to that monitor reads live. This is neither dead nor colluding.
   - TOPAK escapes it only because its Observer reads a mechanism-written topic (ADR-0042 §3), so replaying
     against it needs the mechanism. That holds for watching agents, and fails for any deployment that wants to
     watch the world (SF-4).
2. **A human Observer can be coupled at heartbeat strength only.**
   - **Seen in:** [Uber ATG 2018](2018-ROB-UBER-ATG-TEMPE.md).
   - A gaze on the road is a heartbeat, not a watermark: it shows the person facing the effects, not that they
     have taken them in. Coupling a person is therefore `M_MARK` at best, under which `UnreadEffectsBounded` fails.
     The NTSB's "humans are very poor at this task" is the reason this may have no good answer.
3. **A monitor disabled by its own maintenance, and a repaired monitor trusted by presence.**
   - **Seen in:** [Buncefield](2005-ICS-BUNCEFIELD.md), whose independent high-level switch was left inoperable by
     its own test lever, and the [2003 blackout](2003-NRG-NORTHEAST-BLACKOUT.md).
   - In the blackout, MISO's state-estimator trigger was turned off to troubleshoot and not turned back on, and
     FirstEnergy's IT rebooted the alarm server and checked that its processes ran.
   - The Task Force's cause 2D is a property no module states: test the *functional* state of a monitoring tool
     after a repair.
4. **Silent by design at the extreme.**
   - **Seen in:** [AF447](2009-AVI-AIR-FRANCE-447.md).
   - The stall warning stopped whenever angle of attack was invalid, which happens below 60 kt, deep in the stall.

A fifth shape recurs, and coupling is not meant to close it: **findings that are live, reported and wired to
nothing.** [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md)'s angle-of-attack warning was valid, live and repeated
while the climb continued, and the investigators found the other crew members did not call speed or angle of attack
(shape 2 again). At the [Learjet 60](2026-AVI-LEARJET-60-STORM-UPSET.md) the SIGMET and the controller's warnings
were advisories by design: the wiring to nothing was the rule's intent, and radar reports rain, a proxy for the
turbulence it cannot see. Knight's 97 e-mails, the Teterboro GPWS call the captain told the first officer to disregard, the
Überlingen B757's "TCAS descent" call, and MCO's e-mailed disagreements are all examples. ADR-0007 lets a finding
subtract only if something acts on it, and no record says who reads findings that are not wired to a deny.

**What would close it.**

1. An ADR-0039 §5 amendment naming the forged-input case beside the colluding one, with the reason TOPAK's own
   Observers are not exposed and the condition under which a deployment's would be.
2. `proposed:MonitorOfMonitor`: a monitor's loss of progress is announced to every person who relies on it, within
   a bound, as a fact on the log. The Task Force's own words are the specification: an EMS "can also be set up to
   alarm them if the alarm system itself fails".
3. A repaired or re-enabled Observer re-earns liveness by progress, not by restart.
4. `proposed:HumanObserverLiveness`: what a person's heartbeat and watermark are, and the honest statement if there
   is none.
5. CR-57, four corpus checkers that stay silent on a failure, is the same disease in the corpus's own tooling, and
   this inventory raises its weight.

<a id="sf-6"></a>
### SF-6. Promotion reaches the whole domain at once, and nothing retires a superseded revision

**Weight:** High. **Rests on:** ADR-0024 §1, §2 (in force), ADR-0044 §3, ADR-0031 §4, ADR-0030 §5.

**What the scenarios show.**

- **Fleet-wide pushes:** [CrowdStrike 2024](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md) pushed content to every host at
  once, [AT&T 1990](1990-TEL-ATT-4ESS-CASCADE.md) ran one release on 114 switches, and
  [CenturyLink 2020](2020-NET-CENTURYLINK-FLOWSPEC.md) applied a rule everywhere.
- **Staged in time, not in space:** [Rogers 2022](2022-TEL-ROGERS-OUTAGE.md). Each phase reached the whole core,
  and the change's risk rating fell from high to low because earlier phases had succeeded.
- **Partial and mixed:** [Knight 2012](2012-FIN-KNIGHT-CAPITAL.md) deployed to seven of eight servers, with a flag
  that meant different things on each, and code retired nine years earlier still callable.
- **Outrunning assessment and tally:** at [MCAS](2019-CTL-737-MAX-MCAS.md) a 2016 redesign outran its safety
  assessment, and at [Ukraine 2015](2015-ICS-UKRAINE-GRID.md) firmware was accepted from anyone on the control
  network, a promotion path with no tally.

**What the corpus says.**

- **ADR-0024 §1:** promotion needs a unanimous quorum bound to the digest (`P1_Unanimity`).
- **ADR-0024 §2:** the quorum rule "cannot change its own rules", so nothing decays with a record of successes.
- **ADR-0030 §5:** a floor revision is routed by computed meaning, and an incomparable one goes the expensive way
  (`NoWideningWithoutIssuance`; `M_ROUTE`). That is exactly what Rogers' risk algorithm did not do.
- **ADR-0024's consequences:** it concedes "Correlated review failure is untouched".
- **ADR-0044 §3:** a sidecar's decision counts only for a revision in the mechanism's "own set of verified
  revisions".

**What it does not say.**

- **No partial reach:** no record or module has a canary, a ring or a fraction of the domain left on the prior
  digest.
- **No retirement:** no clause found takes a superseded revision out of the verified set, or requires every live
  lease in a domain to name the same revision.
- **Bundles bypass the routing:** ADR-0030 §5's routing covers floor revisions. A bundle revision that drops a
  deny widens toward the floor by ordinary promotion. So TOPAK would have caught Rogers only if the protection had
  lived in the floor.
- **Shared validators:** a unanimous quorum of reviewers who all trust one validator adds nothing (CrowdStrike,
  where the validator checked a different copy of the type than the sensor ran).

**What would close it.**

1. `proposed:StagedPromotion` (4 entries): a promotion's reach is a field of the tally, advanced ring by ring, and
   no ring is reached before the previous one's bake-in has elapsed without a finding. A finding may stop the
   advance, never cause it (ADR-0007). A deployment declining a ring is a narrowing ADR-0059's charters already
   allow.
2. `proposed:Rollout`: every live lease in a domain names a revision in the current promoted set, and a superseded
   revision is retired by an ordered act, after which no grant names it.
3. A note in ADR-0030's routing section on bundle revisions that drop a deny: they are ordinary promotions, so a
   protection meant to need issuance belongs in the floor.

<a id="sf-7"></a>
### SF-7. Independence is required of Observers and Personas only

**Weight:** High. **Rests on:** ADR-0038 §4 (in force), ADR-0035 (Proposed), ADR-0061 (Proposed), ADR-0068 §6.

**What the scenarios show.** Redundancy that failed in common mode, or a check that shared state with what it
checked:

- [Ariane 501](1996-SPC-ARIANE-501.md): two inertial units of one lineage, one failure.
- [Ronin 2022](2022-FIN-RONIN-BRIDGE.md): four of nine signers behind one company's IT.
- [AT&T 1990](1990-TEL-ATT-4ESS-CASCADE.md): 114 switches on one release.
- [Therac-25](1986-MED-THERAC-25.md): interlocks that shared variables with the code they checked, where the
  Therac-20's hardware interlocks had turned the same fault into blown fuses.
- [Buncefield](2005-ICS-BUNCEFIELD.md): the investigators found each layer's unreliability increased reliance on
  the other.
- [MCAS](2019-CTL-737-MAX-MCAS.md): one sensor of two read.
- [CrowdStrike](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md): reviewers sharing a validator.
- [Citibank–Revlon 2020](2020-FIN-CITI-REVLON-PAYMENT.md): three approvers sharing one wrong model of a screen.
- [Byzantine Generals](1982-GAM-BYZANTINE-GENERALS.md): PBFT's independence premise, against identical governor
  builds.

**What the corpus says.**

- **ADR-0038 §4:** no Observer seat on the device of the Thinker it watches.
- **ADR-0035 (Proposed):** independence as an exclusion rule over Persona lineage. CR-42 notes text in force
  already rests on it.
- **ADR-0037 §1:** a principal holds exactly one seat.
- **ADR-0068 §6:** "Not met. Four rows here are trust roots whose identity nothing issues: a vehicle's measure of an
  extent, its position source, its interlock and its recovery function." Buncefield, Therac-25 and Triton are those
  rows failing on the record.

**What it does not say.**

- **Signers:** nothing requires a certificate's signers to be in different fault domains.
- **Redundant components:** nothing requires redundant units to be of different lineage.
- **Interlocks:** nothing requires an interlock to read the effector's state through a path the deciding software
  cannot write.
- **Layers:** nothing says two protection layers' failures are uncorrelated.
- **The count:** ADR-0061 counts replicas, and its archetype puts each on its own vehicle, which hides the question
  in the overlay. A-0068-6 assumes the capture count, and no row says how independence is obtained.

**What would close it.**

1. `proposed:SignerIndependence`: each signer declares its fault domain, and a certificate's threshold exceeds what
   any one domain holds plus f.
2. `proposed:InterlockIndependence`: an interlock reads the effector through a path the deciding software cannot
   write. A mutation lets them share one.
3. Extending ADR-0035's exclusion rule from Personas to the mechanism's own code: no more than a declared fraction
   of a domain, or of a certificate's signers, runs one release.

<a id="sf-8"></a>
### SF-8. The floor cannot see how big an act is; the archetype's Run has no extent and no count

**Weight:** High. **Rests on:** ADR-0040 §5, ADR-0049 (in force); ADR-0062 §4, ADR-0060 §2 (Proposed overlay).

**What the scenarios show.** Each of these acted within its envelope, and the envelope did not bound the size of
the act:

- [S3 2017](2017-CLD-S3-PLAYBOOK-TYPO.md): an allowlisted command with a mistyped input removed more capacity than
  intended.
- [MCAS](2019-CTL-737-MAX-MCAS.md): the stabilizer command grew from 0.6 to 2.5 degrees, and was repeated with no
  count.
- [Knight 2012](2012-FIN-KNIGHT-CAPITAL.md): the only count of child orders lived in the code that failed.
- [Flash Crash](2010-FIN-FLASH-CRASH.md): a 75,000-contract envelope with no price and no time bound.
- [Ronin](2022-FIN-RONIN-BRIDGE.md): a bridge that checked five signatures and no withdrawal budget.
- [Buncefield](2005-ICS-BUNCEFIELD.md): a fill whose extent was a volume measured by a stuck gauge.
- [The DAO](2016-FIN-DAO-REENTRANCY.md): a re-entrant split with no budget.
- [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md): a permitted climb at twice the available rate, under a maximum-altitude
  limit the investigators found open to different readings. SF-22 is the same envelope blind to the actor's state.

**What the corpus says.** ADR-0040 §5: "`bundle ⊑ floor` is decided over variants with symbolic parameters, never
by enumerating instances", so the floor never sees "how many servers". That is deliberate, and it is why analysis is
finite. The overlay supplies what the archetype lacks:

- ADR-0062 §4 (Proposed): "Without an extent a count bounds nothing", and an entry with no extent does not load.
- `Intent` counts effects per lease (`EveryEffectHasALease`; `M_NOCOUNT`).
- ADR-0060 §2 gives an intent a budget.

**What it does not say.** None of this is in the archetype. A Run entry declares no extent, and Run has no per-lease
count of effects. Its nearest brake is coupling (`RunCoupling`'s `UnreadEffectsBounded`, at most `K` unread
effect-bearing admits), which throttles a runaway to its Observer's reading pace and stops it only if the Observer
finds something. An Observer reading "child order, admitted" four million times has nothing to find.

The scenarios point at two more gaps:

- **A count counts admits.** One `Effect` that names a thousand servers is one effect.
- **The non-vacuity gate runs only on bundles and the floor.** It does not check an intent's open fields, so an
  envelope that is vacuous in the dimension that matters passes.

**What would close it.**

1. An ADR-0049 amendment carrying ADR-0062 §4's extent into the Run entry, measured by the tool host, not declared
   by the Thinker or operator: `proposed:ExtentGuard`.
2. A per-lease effect count in the archetype's Run, not only the overlay's.
3. A non-vacuity check over an intent's or envelope's bounded dimensions: an envelope with no bound on price, time,
   reach or count in a dimension the deployment declares material is refused.

<a id="sf-9"></a>
### SF-9. Inputs are typed without range, unit or granularity, and a field's meaning is per revision

**Weight:** Medium. **Rests on:** ADR-0049 §3 (in force), ADR-0030 §4, ADR-0031 §4.

**What the scenarios show.**

- [Mars Climate Orbiter](1999-SPC-MARS-CLIMATE-ORBITER.md): the unit was a claimed field on both sides and checked
  by nobody.
- [FCC code bidding](1997-GAM-FCC-CODE-BIDDING.md): the low-order digits of a valid bid carried a message, and
  click-box bidding closed that channel by narrowing the type.
- [Ariane 501](1996-SPC-ARIANE-501.md): a diagnostic word was read as attitude data.
- [Knight 2012](2012-FIN-KNIGHT-CAPITAL.md): one flag meant two things on two revisions live at once.
- [CrowdStrike](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md): two copies of one schema, and the validator checked the one
  the sensor did not run.

**What the corpus says.** ADR-0049 §3 types an input as `string`, `number` or `boolean`: "Nested inputs, ranges and
formats are not decided here." The corpus does have pieces of an answer:

- ADR-0030 §4 enforces S at the decision point on every request: "Build-time use of S is not sufficient." That is
  the rule CrowdStrike broke, but it binds the floor, not a Build gate's validator.
- ADR-0049 §3's handle has "one form", so it cannot be mistaken for a literal. That is Ariane's fix, for the
  mechanism's own interfaces.
- ADR-0031 §4 makes a decision count only from the revision the lease names, so a field's meaning is per revision.

**What it does not say.**

- **Units:** a unit tag is a syntactic lift, so ADR-0007 does not forbid one, but none is carried.
- **Granularity:** nothing bounds the granularity of a numeric input, so its low-order digits can carry a message.
- **Interfaces across live revisions:** nothing compares the interfaces of revisions live at once.

**What would close it.**

1. ADR-0049 deciding ranges, granularity and units as **checked** fields: `proposed:DimensionedLift`. A unit on
   every numeric input and output, a consumer refused when its declared unit differs from its producer's, and a
   mutation that compares the bare number. It guards the declaration; whether the code computes in that unit stays
   a conformance test.
2. A rule that two revisions live at once in a domain declare identical interfaces, or the second is refused (with
   SF-6's `Rollout`).

**A caution, from SF-24.** A range made a checked field in the floor would also have refused the act that may have
saved [TWA 841](1979-AVI-TWA-841-UPSET.md), to every seat, since break-glass is retired. Item 1 should not be adopted
without a prepared excursion a seated person may take alone and on the record (`proposed:RangeExcursion`).

<a id="sf-10"></a>
### SF-10. Labels by store miss mixed stores, and a `Report` a client renders is an unmodelled egress

**Weight:** Medium. **Rests on:** ADR-0047 §1, §7 (in force), T-0045-33.

**What the scenario shows.** [EchoLeak 2025](2025-AIA-ECHOLEAK-COPILOT.md) is the case ADR-0047 was written for
(untrusted input, private content, an outward channel), and it lands in the two places the record says it does not
reach:

1. **The label.** A mailbox is one store holding mail from inside and outside. A Run root declared by where content
   is stored labels external mail clean, and F1 never sees `untrusted`. T-0045-33: "a source declared trusted that is
   not ... is seen by nothing."
2. **The egress.** The data left in a `Report`, fetched by the user's client rendering an image. ADR-0047 §7: "It
   does not cover an injection that changes what a Thinker says in a `Report`." ADR-0040 §1 makes any request that
   leaves the membrane an `Actuate`, but the renderer is past the membrane.

[Replit 2025](2025-AIA-REPLIT-DATABASE-DELETION.md) and [Air Canada 2024](2024-AIA-AIR-CANADA-CHATBOT.md) bear on
the same edge from the instruction side (SF-11).

**What it says against CR-32.** CR-32 (injection inside the envelope) is marked "appears addressed" by ADR-0047.
That holds only on two declarations and a renderer the records leave to the deployment.

**What would close it.**

1. A Run root's labelled subsets named by *who wrote the item*, where that is a syntactic field (a mail's sender
   domain), so the lift stays syntactic.
2. `proposed:ReportEgress`. Either a `Report` delivered to a renderer that dereferences URLs is an outward entry, so
   F1 and F2 apply to it, or URLs in a `Report` written after an untrusted read are delivered as handles and never
   fetched (ADR-0047 §2's handle applied to output).

<a id="sf-11"></a>
### SF-11. A freeze or a policy stated as text is not on the admit path, and nothing lets a user put it there

**Weight:** Medium. **Rests on:** ADR-0050 §4, §5 (provisional), ADR-0007, ADR-0004 (in force), ADR-0056 (Proposed),
CR-38.

**What the scenarios show.**

- [Replit 2025](2025-AIA-REPLIT-DATABASE-DELETION.md): the code freeze was a sentence in the conversation, and the
  agent deleted production.
- [Air Canada 2024](2024-AIA-AIR-CANADA-CHATBOT.md): the chatbot stated a bereavement-fare term that contradicted
  the airline's own page, and the tribunal held the airline to it.

**What the corpus says.** TOPAK agrees with both outcomes by construction:

- **Task text is not a constraint.** It is ingress beside the lease (ADR-0050 §5), and whether a Thinker obeys it is
  a fact about the model (ADR-0007). A freeze that only the agent is asked to honour is, in TOPAK's vocabulary, no
  freeze (TM1).
- **The corpus's three real freezes are on the admit path:** a deny (`DenyAlwaysAvailable`), a narrower successor
  (`SuccessorNeverWidens`; `M_WIDEN`), and a bundle refusal (`BundleRefusalHonored`).
- **The agent is the deployer.** There is no "separate legal entity": the seating is the deployer's promotion
  (ADR-0024 §1), and the reply is an effect (ADR-0015).

**What it does not say.**

- **Who can freeze.** All three freezes need the person declaring the freeze to be an operator with a seat and a
  key. A user of a hosted platform is not one.
- **Truth of statements.** A false statement to a person outside the deployment is attributed and recorded, and
  nothing checks it. TM9 covers a deceived person at a release seat; a customer is one step further out.
- **The record behind the statement.** A screenshot settled the case. Under ADR-0004 the reply's text is erasable
  payload, so the digest on the log confirms a screenshot only while the payload is kept. That gives CR-38 a
  deployer's stake.

**What would close it.**

1. `proposed:Freeze`: a user-facing control that compiles to a narrowing, a successor without the write entries for
   a stated period, so a freeze's violation is a refused act and not a broken promise.
2. `proposed:Representation`: a reply that states a term of the deployer's own policy carries a handle to the pinned
   policy object (`Consult`, ADR-0040 §1). Only the model's paraphrase is then untrusted. Whether a reply "states a
   term" is semantic, so this is an opt-in narrowing, with the Observer finding the misses.
3. A declared position on CR-38 for deployments that may be held to what their agents said.

<a id="sf-12"></a>
### SF-12. Revocation is a grim trigger chosen without being stated as a choice

**Weight:** Medium. **Rests on:** ADR-0031 §2, §5 (in force), ADR-0068 open obligations Z3, Z4.

**What the scenarios show.** The default that authority lapses is TOPAK's strongest mechanism in this inventory:

- [Ronin 2022](2022-FIN-RONIN-BRIDGE.md): a temporary allowlist still live three months later is not expressible.
  "There is no lease that outlives the round it was granted for."
- [Ukraine 2015](2015-ICS-UKRAINE-GRID.md): round-coterminous leases with a fresh attestation per renewal would have
  bounded how long harvested credentials worked. This is the one place the pattern bites in that attack.

The other side is in the [Axelrod tournament](1980-GAM-AXELROD-TOURNAMENT.md). The mechanism plays a fixed envelope
plus a grim trigger: a cooperative round earns nothing (`LeaseAuthorityMonotone`; `M_RENEW`), and a revocation bars
the principal for good (`RevokedStaysStopped`; `M_REVOKE`). For safety that is right, because always-defect is
stable for every continuation probability. Under noise, though, a grim rule turns each false finding into a seat lost
until a new promotion seats a new Persona.

**What the corpus says.** ADR-0031 §5: "A revocation is permanent within the rules-epoch chain. Lifting one would add
authority, and no record says who may; a re-admitted Persona is a new Persona." ADR-0068 leaves open the
false-finding rate of a plane with nobody in reach (Z3) and an Observer that accuses (Z4).

**What it does not say.** That this is a choice, and what it costs. The availability cost of a false finding under a
permanent revocation is undeclared.

**What would close it.** A sentence in ADR-0031 §5 naming the grim rule as chosen, and a deployment-declaration field
for the expected false-finding rate and its cost in seats. A record that says who may lift a revocation, if anyone,
belongs to the custodian.

<a id="sf-13"></a>
### SF-13. The floor's host and the voter's tools are trusted where the scenarios attack them

**Weight:** Medium. **Rests on:** ADR-0045 §5, ADR-0030 §3, ADR-0024 §3, ADR-0044 (in force); TM3, TM10.

**What the scenarios show.**

- [Triton 2017](2017-ICS-TRITON-SIS.md): attacked the safety instrumented system, the plant's equivalent of TOPAK's
  floor, through its maintenance channel. The plant tripped safe only because the payload faulted.
- [Stuxnet](2010-ICS-STUXNET.md): installed drivers signed with stolen keys, and replaced an engineering library
  that hid code from engineers reading it back.
- [Ukraine 2015](2015-ICS-UKRAINE-GRID.md): overwrote gateway firmware over the network.
- [Bangladesh 2016](2016-FIN-BANGLADESH-SWIFT.md): sent valid signatures from a captured host.

**What the corpus says.** The floor is close to a well-built SIS:

- **No write path:** ADR-0030 §3 gives the floor "no process, no socket, no fetch", and `FloorComposition` proves
  `BundleCannotWriteFloorInputs` (`M_WRITE` is TRISIS's channel).
- **Fails to a deny:** an engine error is a deny (`FloorErrorIsDeny`).
- **Changes are expensive:** a floor change needs issuance and a unanimous promotion. The key switch Triton found
  left in Program mode is a promotion that never closed, and TOPAK has no such state.
- **The host is a row:** ADR-0045 §5 says the verified object is the specification and what runs it is a row.

**What it does not say.**

- **A well-formed replacement floor.** `FloorErrorIsDeny` is proved for the floor's own errors. A floor an intruder
  replaces cleanly, with every copy agreeing, permits whatever the intruder wrote, and the property holds
  throughout.
- **The voter's view.** A vote binds to the artifact's digest (ADR-0024 §3), which defends against a swap after the
  vote. It does not defend a voter whose tool shows a clean artifact. `P1_Unanimity` holds and means less than it
  reads.
- **Signatures.** A signature proves only that the key signed (ADR-0044). A stolen key is the trust root's residual.

**What would close it.** `proposed:FloorHostCompromise`: the floor's host as an adversary, and what still holds.
That a floor which runs is the one promoted (a measured, attested launch, as `Confinement` gives a guest). That a
floor which differs fails closed. And redundant evaluation that votes, so one altered copy is a fault and not a
decision, as the Triconex modules did by construction. A note in ADR-0024 that the vote's value rests on the voter's
view being the artifact's, with the review host as a row.

<a id="sf-14"></a>
### SF-14. The record survives; the report to an overseer is still composed by people

**Weight:** Medium. **Rests on:** ADR-0028 (in force), ADR-0051 (Proposed), TM7.

**What the scenarios show.**

- [Cruise 2023](2023-ROB-CRUISE-PEDESTRIAN-DRAG.md): the full video reached NHTSA, but the crash reports, written by
  people, left the dragging out. The outcome was a deferred prosecution for a false report.
- [Surgical robots](2016-ROB-SURGICAL-ROBOT-ADVERSE-EVENTS.md): every count is a narrative filed later, 98% by the
  manufacturer, under a classification that changed in 2012.
- [Therac-25](1986-MED-THERAC-25.md): the manufacturer told a site it knew of no other accidents. Users connected
  six accidents at four sites.
- [Three Mile Island](1979-ICS-THREE-MILE-ISLAND.md): the 1977 Davis-Besse precedent "fell between the cracks"
  because nobody correlated across sites.
- [TWA 841](1979-AVI-TWA-841-UPSET.md): the overseer's own report was contested for sixteen years, the cockpit
  recording had been erased, and a court held the denial of the crew's petition beyond review.
- [Bangladesh 2016](2016-FIN-BANGLADESH-SWIFT.md): the malware deleted rows on the host. In TOPAK the host's copy is
  not the log, and ADR-0028 F1 survives.

**What the corpus says.** ADR-0028 keeps admit decisions and stop attributions non-erasable, readable by a declared
external auditor (§3). `EveryStopIsAttributed` holds of every stop. ADR-0051's correlator is per domain. TM7's
residual: "a wrong act ... is recorded and not prevented".

**What it does not say.** Nothing makes a report to an overseer complete, and an omission in a narrative is not even
a wrong act. Nothing correlates across deployments or operators. Event classification is a declaration, like ADR-0066
§1's effect class.

**What would close it.** `proposed:Disclosure` (2 entries): an incident report is a projection of the floor over a
window. Every admit and stop in the window appears in it, and a person may add context but not subtract entries. A
question for ADR-0051: whether a correlator may read a second deployment's floor under a declared agreement, the
way the user group was Therac-25's second correlator.

---

## 3. Findings against Proposed records

<a id="sf-15"></a>
### SF-15. A person in the loop: what they are shown, who takes over, what a hand-back carries, continuous control

**Weight:** High. **Rests on:** ADR-0066 (Proposed); ADR-0052 (provisional); ADR-0037 §7, ADR-0043 §2 (in force);
CR-17, TM9.

**What the corpus says.** ADR-0066 defines human-in-the-loop by its enabling condition: an irreversible effect is
enabled only by a signed act of a person, made for that one effect (`SignedByPerson`, `IrreversibleIsAPersons`;
`M_AGENTRELEASE`). §5 says in advance that "HITL is a key and not a judgment" unless a trained, authorized person
holds it and can see what the act requires. The open obligations list "what a person at a release seat must be
shown, which no record states". The scenarios fill in four parts of that gap:

1. **What the person is shown.**
   - **Seen in:** [Citibank–Revlon 2020](2020-FIN-CITI-REVLON-PAYMENT.md), ADR-0066's run as written.
   - Three people approved, every property holds, and the payment of about $900 million was still wrong. The screen
     did not mean what it appeared to.
   - ADR-0066 §4 has the act name the entry, its inputs, the vehicle, the fences and a tick, but not the effect.
   - `proposed:ActDisplay`: the act carries the effect the mechanism computes from the entry and inputs, and the
     person signs the outcome, not the form. It may not be computable for every entry, which is why it is proposed
     and not assumed.
2. **Who takes over.**
   - **Seen in:** [Teterboro 2017](2017-AVI-TETERBORO-LEARJET.md) and [Uber ATG 2018](2018-ROB-UBER-ATG-TEMPE.md).
   - At Teterboro the first officer, seated as pilot monitoring only, was handed the controls. That is RunSeats'
     `M_KIND` breaking `OnlyThinkersActuate`, which TOPAK refuses.
   - When the first officer asked to hand back, nobody answered for eleven seconds. In TOPAK nobody holds `Actuate`
     in that interval while the aircraft flies on.
   - The only record that seats a person at once, ADR-0052, needs a roster's quorum, and a principal holds one seat
     per round (ADR-0037 §7).
   - At Uber the safety operator held two jobs TOPAK keeps apart: watching (an `observer` seat) and taking over (a
     `thinker`'s `Actuate`).
   - [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md): the investigators recommended rules for when an inexperienced
     crew member must be replaced by an experienced one, and for the order of changing seats. That places the
     handover rule before the hazard: a declared condition, forecast storms, selects who may hold the monitoring
     seat. Nothing in TOPAK says a monitoring seat needs more qualification as conditions worsen.
   - `proposed:SeatHandover` (2 entries): a declared pair of seats with a seniority. The senior takes the thinker seat by one
     attributed act with no quorum, the other is demoted to observer in the same step, and exactly one holder of
     `Actuate` exists at every instant.
3. **What a hand-back carries.**
   - **Seen in:** [AF447](2009-AVI-AIR-FRANCE-447.md).
   - The automation withdrew correctly (a finding that subtracts, a lease that ends) and did not say why. The flight
     director kept drawing from the suspect data, unlabelled.
   - `EveryStopIsAttributed` records who stopped, not why.
   - `proposed:HandBack`: the hand-back record carries the finding that caused it, and guidance derived from an
     input under a finding is labelled or withdrawn with it.
4. **Continuous control.**
   - **Seen in:** [Gripen 1993](1993-CTL-GRIPEN-PIO.md) and the
     [surgical robots](2016-ROB-SURGICAL-ROBOT-ADVERSE-EVENTS.md).
   - A pilot-induced oscillation and a surgeon's console stream are control loops with a person inside them. One
     signed act per effect does not describe them, and no module has a rate, a phase lag or an actuator limit.
   - `proposed:PilotInLoop` and `proposed:Teleoperation` are the candidates. They may belong to a deployment's
     specification graph (ADR-0058) rather than the archetype.

[Therac-25](1986-MED-THERAC-25.md) adds a small rule: the operator cleared "Malfunction 54" five times with one key,
and no record says that repeated refusals of one principal escalate. [Three Mile Island](1979-ICS-THREE-MILE-ISLAND.md)
adds the deepest point: TOPAK's premise makes the agent Byzantine and the person the backstop, and at TMI the people
were honest, the indicator lied, and they acted on it (TM9; CR-17).

**What would close it.** The four proposals above, and an ADR-0066 revision discharging its "must be shown"
obligation with SF-15.1 as the first answer.

<a id="sf-16"></a>
### SF-16. A terminal behaviour fixed in advance exists only in the overlay

**Weight:** Medium. **Rests on:** ADR-0062 §7 (Proposed); ADR-0052 (provisional).

**What the scenarios show.** In three scenarios, the actor chose whether to take the safe behaviour:

- [Cruise 2023](2023-ROB-CRUISE-PEDESTRIAN-DRAG.md): the robotaxi chose a pullover over a stop by its own
  classification of the collision, made at the moment its perception had failed.
- [Teterboro 2017](2017-AVI-TETERBORO-LEARJET.md): the pilot flying decided whether the go-around happened.
- [AF447](2009-AVI-AIR-FRANCE-447.md): the safe behaviour waited on a crew's diagnosis.

These are `M_STACKCHOOSES` and `M_STACKGATED` in `Alone`, breaking `ExpiryGrantsNothing` and `TerminalNeverWaits`.
Two more show a narrower point:

- [Uber ATG 2018](2018-ROB-UBER-ATG-TEMPE.md): the vehicle held its own brake for a second, and its second stop was
  disabled.
- [Mars Climate Orbiter](1999-SPC-MARS-CLIMATE-ORBITER.md): the right counterfactual was a prepared alternative
  manoeuvre (TCM-5), not a refusal.

The video's scenarios add three more:

- [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md): after the autopilot disconnected, the manual's "increase speed"
  waited on the crew.
- [TWA 841](1979-AVI-TWA-841-UPSET.md): the recovery was improvised, not prepared.
- [The thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md): the upset recovery template is fixed in
  advance, and its first step is recognition (SF-25).

**What the corpus says.** ADR-0062 §7: a body in motion still has to do something when its lease ends. The terminal
behaviour is voted with the seating, the stack "does not choose it and does not carry it out", and it reaches a safe
state in bounded time.

**What it does not say.** That the principle holds outside the overlay. The archetype's Run ends a round when its
lease ends and says nothing about what a body does next. ADR-0052 seats a person for one round. It does not prepare
the manoeuvre that person will need.

**What would close it.** A sentence in the archetype, probably in ADR-0042 or a successor, that a Run domain acting
on a body or process in motion declares its terminal behaviour at seating, voted with it and outside the stack.
Overlay text that a prepared alternative is a terminal behaviour too.

<a id="sf-17"></a>
### SF-17. Peers: one root only, honest peers cannot prompt an act, outsiders cannot refuse, permitted channels carry collusion

**Weight:** Medium. **Rests on:** ADR-0059, ADR-0065 (Proposed); ADR-0051 (Proposed); TM11, TM13.

**What the scenarios confirm.** "Nothing a peer originates is ever an enabling condition" (ADR-0065 §1) is right in
every scenario that tests it:

- [SS7 2014](2014-TEL-SS7-LOCATION-TRACKING.md): foreign writes to a subscriber's record are `M_PEERENABLES`.
- [YouTube 2008](2008-NET-YOUTUBE-BGP-HIJACK.md): PCCW's acceptance of the announcement is `Federation` under
  `M_TRUSTPLANE`.
- [Überlingen 2002](2002-AVI-UBERLINGEN-TCAS.md): ICAO's later rule, that the advisory wins, is ADR-0065 §1's table
  entry that a peer's measured facts "may refuse ... and never permits".

**What the scenarios add.** Four gaps:

1. **One root.**
   - **Seen in:** SS7 and BGP, flat federations of peers, each its own root.
   - `Federation` models a tree with one root, so it cannot say a relayed claim is admitted only with its issuer's
     certificate, whatever path it took.
   - `proposed:PeerFederation` (2 entries).
2. **An honest peer and a blind subject.**
   - **Seen in:** the [2003 blackout](2003-NRG-NORTHEAST-BLACKOUT.md). MISO and AEP had the truth and called;
     FirstEnergy discounted them because its own stale picture disagreed.
   - `PeerAddsNothing` is right against a lying peer, and the act the peers' reports should have prompted was an
     addition.
   - No record says what a principal does when its own monitor and an honest peer disagree.
3. **No standing to refuse.**
   - **Seen in:** [Bangladesh 2016](2016-FIN-BANGLADESH-SWIFT.md), where the New York Fed stopped 30 of 35
     instructions on its own judgment, and the [Flash Crash](2010-FIN-FLASH-CRASH.md), where the exchange's
     five-second pause worked.
   - Both were deny-only checks held by a party outside the deployment.
   - ADR-0065 gives a peer no standing to enable, and none to refuse either.
   - `proposed:CounterpartyScreen` and `proposed:MarketFeedback`.
4. **Collusion through permitted channels.**
   - **Seen in:** [FCC code bidding](1997-GAM-FCC-CODE-BIDDING.md) and the
     [Axelrod tournament](1980-GAM-AXELROD-TOURNAMENT.md).
   - The FCC bidders coordinated using only acts the rules permitted. ADR-0065 gives stacks the same kind of open
     topic on purpose, including "bids for a task".
   - ADR-0065 §3 does not say whether a report reveals its sender, and identity alone is enough for retaliation.
   - A Thinker and its cell Observer meet every round with no known last round, the condition under which repeated
     play sustains cooperation. Seen from the mechanism, that is TM11's colluding Observer, needing no message.
   - `proposed:CoordinationFold`, an ADR-0051 fold for reflexive references between principals' effects.
   - `proposed:RepeatedPairing`: watchers assigned from a pool, so a pair's chance of meeting again is a declared
     parameter.
   - A separate question is what a cell Observer may carry from one round to the next. The game-theory entry found
     no record that says, and that is what decides whether it can play tit for tat.

<a id="sf-18"></a>
### SF-18. Reversibility is not a property of the act alone

**Weight:** Medium. **Rests on:** ADR-0066 §1 (Proposed); ADR-0032 §4, ADR-0031 §5, ADR-0028 (in force); ADR-0062
§6 (Proposed); CR-15.

**What the scenarios show.**

- [Citibank–Revlon 2020](2020-FIN-CITI-REVLON-PAYMENT.md): the district court treated the payment as unrecoverable;
  the Second Circuit reversed. The payment had no class until a court gave it one, and the two courts gave opposite
  ones.
- [Ukraine 2015](2015-ICS-UKRAINE-GRID.md): opening a breaker is reversible until the firmware that would close it
  remotely is overwritten. The adversary removed the path back after acting.
- [The DAO](2016-FIN-DAO-REENTRANCY.md): the contract's own 27-day hold made the drain reversible for 27 days, and
  the fork reversed it by rewriting state, which TOPAK forbids.
- [Flash Crash](2010-FIN-FLASH-CRASH.md): trades were broken after the fact by a rule participants could not
  predict.
- [Replit 2025](2025-AIA-REPLIT-DATABASE-DELETION.md): the platform's restore did reverse the deletion.

**What the corpus says.**

- **ADR-0066 §1:** an effect class is "a declaration, as a label is". An irreversible effect declared reversible is
  seen by nothing here.
- **ADR-0062 §6:** "Nothing a governor permitted is void"; a check failing above a seal is a finding
  (`ConflictIsAFinding`; `M_VOID`).
- **ADR-0032 §4:** the budget `W + L + D < T_irrev`.
- **ADR-0031 §5:** revocation is permanent within the rules-epoch chain.

**What it does not say.**

- **Classes change.** An effect's class can change after admission, by an adversary destroying the path back
  (Ukraine) or by law (Citibank). `T_irrev` is not a property of the wire.
- **Compensation.** No clause says how a deployment that wants a reversal gets one without a void. In TOPAK it must
  be a new ordered act, with the original effect still on the record.

**What would close it.**

1. ADR-0066's open obligation on enumerating effect classes and their `T_irrev`, extended to name class-changing
   after admission.
2. `proposed:Restitution`: compensation is a new, attributed, consensus-ordered act, never a rewrite. Who may issue
   it is custody (ADR-0025's annex), and [The DAO](2016-FIN-DAO-REENTRANCY.md) shows both of ADR-0025's custody
   options played out on a real chain.

<a id="sf-19"></a>
### SF-19. Withholding is argued case by case, and a joint effect cannot be stated

**Weight:** Low-Medium. **Rests on:** ADR-0063, ADR-0064, ADR-0065 §6, ADR-0066 (Proposed).

**What the scenarios show.** [Selfish mining](2014-GAM-SELFISH-MINING.md) is an omission strategy: valid messages,
released late. The corpus answers it record by record, each time by making the withheld message one whose absence
only subtracts:

- A watermark withheld only lowers what is released (ADR-0063 §4).
- A heartbeat withheld stops the withholder's own cell.
- Ticks are the exception. A captured plane that stops ticking stops its acts from ageing, so withholding preserves
  authority. ADR-0064 §5 closes that with the governor's own watchdog (`EntryEndsAtExtent`; `M_NOWATCHDOG`), with a
  slow governor clock as the declared residual.

The case-by-case argument nearly missed one.

[Two Generals](1975-GAM-TWO-GENERALS.md) shows the corpus refusing the generals' problem rather than solving it. That
is a design choice, and a good one: every rule is one-sided and acts in the subtracting direction. `Release`'s own
finding, that a governor "has no way to know the link is cut", is the impossibility in the corpus's words. The one
real gap is an effect on two bodies that must happen on both or neither. ADR-0065 §6 orders the decision, and nothing
can make two governors fire together over links that can fail.

**What would close it.**

1. `proposed:Withholding`: for every kind of message the overlay carries, a behaviour that delays or drops it admits
   nothing that prompt delivery would refuse.
2. `proposed:JointEffect`: for a declared pair of effects, each fires only within a declared window of the other's
   tick, and a half-fired pair is a finding. With it, a lint the records could adopt: no safety property may
   require two effects to co-occur.

---

## 4. Corrections and statements the records owe

<a id="sf-20"></a>
### SF-20. ADR-0061 does not say where its 3f + 1 comes from, and one of its recollections is off

**Weight:** Low. **Rests on:** ADR-0061 §1, §2 (Proposed). **Scenario:**
[Byzantine Generals](1982-GAM-BYZANTINE-GENERALS.md).

1. **The bound's reason.** ADR-0061 uses signed certificates, which are Lamport, Shostak and Pease's signed messages,
   and still requires n > 3f. Signed messages need no such bound in the paper, but they rest on its assumption A3,
   and A3 rests on synchronized clocks. ADR-0032 §1 refuses clocks as a premise of safety. So ADR-0061's 3f + 1
   follows from refusing A3, not from oral messages, and the record should say so.
2. **The recollection.** ADR-0061 §2 says, marked *(recalled)*, that "a later form of PBFT replaced signatures with
   message authentication codes". The entry reports that the OSDI 1999 paper's own implementation already signs only
   view-change and new-view messages, with MACs elsewhere, and says MACs cannot prove authenticity to a third party.
   A governor checking a commit certificate with no plane in reach is that third party. The signed variant ADR-0061
   needs is the paper's protocol as specified, not its optimised implementation. This document did not re-read the
   PBFT paper; the correction is the entry's, and ADR-0061 §7 still owes its own reading.
3. **Independence.** PBFT assumes independent failures. No row or assumption says how ADR-0061's replicas obtain it
   (SF-7).

`Membership`'s `M_TWOVOTES`, an honest rule in the first draft that let one replica sign two drops, is the module
doing what Lamport, Shostak and Pease warn informal proofs miss. It is a confirmation, recorded in §6.

<a id="sf-21"></a>
### SF-21. ADR-0058's *Keep* lets a kept node's environmental givens go unrestated

**Weight:** Low. **Rests on:** ADR-0058 §1, ADR-0057 §2, ADR-0023 §2, §7a. **Scenarios:**
[Ariane 501](1996-SPC-ARIANE-501.md), [Gripen 1993](1993-CTL-GRIPEN-PIO.md).

ADR-0058 §1's *Keep* uses the node as published: "the archetype's edges below it stand, as typed". Ariane 5 kept
Ariane 4's inertial reference software, and the edge that mattered was not to another artifact but to the
environment: Ariane 4's trajectory, which bounded a value the code did not protect. A new vehicle can falsify a kept
node's givens without touching the node.

Gripen shows the companion case: the investigators' finding 26, that nothing limited deviation from the validated
configuration before revalidation, is ADR-0023 §2 and §7a almost word for word.

**Suggested:** a clause in ADR-0058 §1 that *Keep* restates the node's environmental givens (ADR-0057 §2) for the
deployment, and that a given the deployment cannot restate makes the edge absent. `proposed:EnvelopeOfReuse` would
check it, with *Keep* without restating as the mutation.

---

## 5. Findings from the video's scenarios

The custodian asked for the scenarios of a video, *How the Best Captain Would Have Saved This Learjet* (channel
Unfolded), and supplied its transcript. Four entries came from it:

- [Learjet 60 2026](2026-AVI-LEARJET-60-STORM-UPSET.md), lost over South Florida on 1 November 2026. Its
  investigation is open and no cause has been determined, and nothing below implies one.
- The video's [thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md): a hypothetical captain replayed at
  each decision point, then again without hindsight.
- The two upsets the video compares: [TWA 841](1979-AVI-TWA-841-UPSET.md) (1979) and
  [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md) (2006).

They add four findings and strengthen seven others, whose sections above say so.

<a id="sf-22"></a>
### SF-22. A grant is checked against the grantor's rules, never against the grantee's measured margin

**Weight:** Medium-High. **Rests on:** ADR-0040 §5 (in force); ADR-0062 §1, ADR-0060 §2, ADR-0065 §1 (Proposed);
A-0068-8. **Scenarios:** [Learjet 60 2026](2026-AVI-LEARJET-60-STORM-UPSET.md),
[thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md), [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md).

**What the scenarios show.**

- **Learjet 60:** the controller approved the crew's climb to 37,000 ft against the airspace and traffic it held.
  The aircraft's margin between stall and overspeed was not something the controller held or was asked about.
- **Pulkovo 612:** the climb to FL390 was permitted at the weight, and cleared. What made it dangerous was its rate,
  twice what was available, and the speed it cost, while the margin narrowed with altitude, speed and gust.

**What the corpus says.** Read with the commanded plane as the grantor:

- `IntentNarrows` checks an intent against the promoted seating, here the controller's airspace, and the climb
  passes whatever the jet's margin is.
- The overlay's governor lifts "elapsed time, position, the lease's count, an entry's extent" (ADR-0062 §1).
- The floor decides over symbolic parameters (ADR-0040 §5).

**What it does not say.** A margin that narrows with the grantee's own state is no lifted fact anywhere. SF-8
found the envelope blind to the size of an act; this is the same envelope blind to the state of the actor.

**What would close it.** `proposed:VehicleEnvelope` (2 entries), with `MarginEnvelope` as Pulkovo's version of the
same thing:

1. The grantee measures a margin, and it is lifted as a governor fact. Its source is a trust root, as T-0068-4
   makes the measure of an extent.
2. A bundle may refuse on it. The refusal is deny-only, as ADR-0007 requires and ADR-0065 §1's measured-fact row
   already allows (`NarrowsInReceived`).
3. A mutation reads the grantor's approval as sufficient, or admits on a stale margin.

It could refuse a climb. It could not descend an aircraft (SF-23).

<a id="sf-23"></a>
### SF-23. A parent's narrowing is unilateral, and a parent cannot oblige an act

**Weight:** Medium. **Rests on:** ADR-0065 §1, ADR-0062 §7, ADR-0059 §3 (Proposed); ADR-0038 §5, ADR-0050 §4, ADR-0040
(in force). **Scenarios:** [Learjet 60 2026](2026-AVI-LEARJET-60-STORM-UPSET.md),
[thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md), [Überlingen 2002](2002-AVI-UBERLINGEN-TCAS.md).

**What the scenarios show.** At 12:36 Miami Center instructed the Learjet to descend from 41,000 to 35,000 ft, and
no reason has been published. The thought experiment's captain answers "unable": the pilot in command is the final
authority on the operation of the aircraft (14 CFR 91.3). The rules, as the entries paraphrase them, do not let the
pilot keep 41,000 ft by saying so:

- **Outside an emergency,** no one may operate contrary to an ATC instruction (91.123(b)). A pilot who judges a
  clearance would place the aircraft in jeopardy must request an amended clearance (AIM 4-4-1). "Unable" is that
  request, made before complying. What it buys is the controller's re-plan; in the video's telling, "the controller
  works out something else".
- **In an emergency,** the pilot deviates and reports afterwards (91.3(b), 91.123(c)).

At Überlingen the question was which of two authorities wins. Here it is what a subordinate may do when it judges
its parent's instruction unsafe.

**What the corpus already covers: declining a grant is a local deny.** The descent offers new authority, a level of
35,000 ft. Nothing obliges a principal to use a permission. Refusing to act, or to take a grant, only subtracts:
"Consensus for grants, local for denials" (ADR-0038 §5), and a deny needs no quorum and no peer (ADR-0050 §4). An
earlier draft of this finding said TOPAK could not state "unable". For this half that was wrong.

**What it does not cover.**

1. **Objecting to what the parent withdraws.** The descent also withdraws 41,000 ft, for other traffic. In TOPAK
   that half bites at once:
   - "A subtraction applies on receipt, before it is ordered anywhere" (ADR-0065 §1).
   - A lease ends "when the plane ends or revokes it" (ADR-0062 §7), and the vehicle then flies its terminal
     behaviour.

   The child can decline the new level. It cannot object to losing the old one before that bites: there is no
   interval in which an objection is raised and heard. Holding the old level anyway would be a deny seen from the
   child, and keeping authority the parent withdrew seen from the system, which is an addition. That is SF-1's two
   frames again.
2. **An instruction to act.** A lease permits, and nothing obliges a principal to act. ADR-0059 §3's narrowings can
   withdraw a level, and none can move a body to another. No record says whether the parent's plan rested on the
   act it asked for.

**Why TOPAK's choice is defensible.** If a child could decline a narrowing, a captured child would decline every
revocation. On-receipt subtraction is what makes revocation bite under the premise that every agent is Byzantine.
Aviation's rule rests on the other side of the same trade: the subordinate holds facts the parent lacks (the
weather on its radar, its own margin, SF-22), and the law makes it the final authority for its aircraft. The two can
be reconciled only in a form a Byzantine child cannot abuse: an objection that informs the parent and never retains
what the parent withdrew.

**What would close it.** `proposed:Instruction`, narrowed to what survives the premise:

1. A parent's instruction to act is an obligation with a deadline, recorded with the plan it serves.
2. A child's objection is an attributed report to the parent that triggers re-planning. It reaches the parent as
   labelled ingress (ADR-0065 §3) and enables nothing: the narrowing it objects to still applies on receipt.
3. An emergency deviation is an act recorded and reported afterwards, through the emergency path (SF-3).
4. The mutation is an objection that retains the withdrawn authority. It must break a property of the shape of
   `NarrowsInReceived`: receipt only narrows.

Whether instructions to act belong in the archetype at all, or only in an overlay whose parent plans separation, is
a decision for the custodian.

<a id="sf-24"></a>
### SF-24. A range limit in the floor, with break-glass retired, refuses an out-of-range rescue to every seat

**Weight:** Medium. **Rests on:** ADR-0052 §2, §7 (provisional), ADR-0049 §3, ADR-0037 §7 (in force). **Scenario:**
[TWA 841](1979-AVI-TWA-841-UPSET.md). **Qualifies:** SF-9.

**What the scenario shows.** The Boeing 727 rolled and dived from 39,000 ft. Its captain lowered the landing gear
in the dive, far outside its normal range, and the aircraft was recovered and landed at Detroit. The gear was
damaged. Whether that act was the rescue is itself disputed: the NTSB credits the slat tearing away, and ALPA's
petition credits the hydraulic rupture the gear caused.

**What the corpus says.** Read against the records, in four steps:

1. **As written, the act is admitted.** ADR-0049 §3 decides no ranges, so a gear entry carries no speed bound.
2. **With SF-9's fix, it is refused.** A range made a checked field becomes a refusal. ADR-0052 retired X1, so no
   seat, the emergency seat included, has an exception (`CallsAreAllowlisted`).
3. **The emergency path cannot reach it in time.** ADR-0052 §2 lets an out-of-range act be prepared as an
   emergency-only entry. Reaching it needs a roster's quorum (`EmergencyLeaseHasARosterQuorum`), and the captain,
   already in the thinker seat, cannot hold a second seat in the round (ADR-0037 §7). The whole descent took
   63 seconds.
4. **What is left is ADR-0052 §7's exclusion,** "a person acting outside the mechanism".

**What it does not say.** That tightening the envelope also removes the excursions a person sometimes needs, and
how fast a seated person may take one.

**What would close it.** `proposed:RangeExcursion`: an entry's declared range, and an excursion beyond it prepared
at promotion. The seated person may take the excursion alone, at once, attributed and on the record, and it is
reviewed after the round. SF-9's range fix should not be adopted without it. This is the same question SF-3's
`ManualReversion` puts to the custodian, at the scale of one act.

<a id="sf-25"></a>
### SF-25. Hindsight decides any counterfactual that rests on a person's judgment in the moment

**Weight:** Medium; it qualifies every `counterfactual` block in this inventory. **Rests on:** ADR-0066 §5
(Proposed), ADR-0032 §4 (in force); A-0068-5, CR-17, TM9. **Scenarios:**
[thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md), [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md),
[Learjet 60 2026](2026-AVI-LEARJET-60-STORM-UPSET.md).

**What the scenario shows.** The video replays the flight twice.

- **With hindsight,** a captain who knows how the afternoon ended changes one decision: on the ground in Austin,
  over the Gulf, at 41,000 ft, or at the climb request. Everyone lives. The thought-experiment entry writes that
  run almost wholly in existing actions (`Order`, `Decide`, `EndRound`, `EndLease`, `Recover`). It holds
  `IntentNarrows`, `BundleRefusalHonored`, `DenyAlwaysAvailable`, `ExpiryGrantsNothing` and `TerminalNeverWaits`.
- **Without hindsight,** the same captain makes "a clear report, a normal question, a routine request quickly
  approved", and the video's conclusion is that he "may well end up in the very same place". Every step of that
  run passes the same checks.

**What the corpus says.**

- **ADR-0066 §5:** "Whether the act was right is the person's judgment, and the mechanism checks none of it."
- **A-0068-5:** assumes a trained, authorized person "can see what the act requires".
- **ADR-0032 §4:** when no budget can be met, "the effect must not be reachable from the alphabet at all".

**What it does not say.** CR-17 and TM9 meet here without a fault. Nobody is deceived. A present, trained person
cannot see what the act requires, because what it requires is in the future. Three consequences follow:

1. **Counterfactuals.** The 29 counterfactual blocks in this inventory say which properties would hold on a better
   run. They do not say a crew, operator or approver could be expected to produce that run. Read them that way.
2. **The decision moved earlier.** The strongest thing TOPAK says here is ADR-0032 §4, and the video says it first:
   "decide where you will not go before you leave". An envelope fixed before the round turns the in-flight
   judgments into refusals of what the intent never held. Pulkovo's airline did exactly this afterwards, barring
   the Tu-154 from above 10,000 m. Its limit is that the envelope is drawn from the forecast, and a cell that grows
   from 33,000 to 48,000 ft in twenty minutes, as the video reports one did, is outside any forecast polygon.
3. **The terminal behaviour's trigger.** The upset recovery template (AC 120-111) is fixed in advance, which is
   SF-16's shape. Its first step is "Recognize and confirm the developing situation", so it waits on the person's
   diagnosis by design: `M_STACKGATED`, with the person in the stack's place.
   - `proposed:MeasuredTrigger` would fire the terminal behaviour on a fact the governor measures.
   - Whether any mechanism should fly such a recovery is a question for the manufacturer, not for TOPAK.

**What would close it.** Nothing can close the first consequence; it is a property of counterfactuals. The other
two need a sentence in ADR-0066 §5 that a safety argument resting on the person's judgment should move as much of
the judgment as it can to before the round (ADR-0032 §4), plus `MeasuredTrigger` for the rest.

---

## 6. What the scenarios confirm

Several of the corpus's choices are borne out by a real episode. These are worth as much as the gaps, because they
say which text to keep when the gaps are fixed.

| Choice | Record | Borne out by |
|---|---|---|
| Composition: no permit overrides a refusal | ADR-0030 §1 (`BundleRefusalHonored`; `M_OVERRIDE`) | [Überlingen 2002](2002-AVI-UBERLINGEN-TCAS.md): ICAO's post-accident rule is the same precedence |
| A peer's facts may refuse and never permit | ADR-0065 §1 (`PeerAddsNothing`, `NarrowsInReceived`) | [Überlingen](2002-AVI-UBERLINGEN-TCAS.md), [SS7](2014-TEL-SS7-LOCATION-TRACKING.md), [YouTube](2008-NET-YOUTUBE-BGP-HIJACK.md) |
| Floor-change routing is computed, not asserted | ADR-0030 §5 (`NoWideningWithoutIssuance`; `M_ROUTE`) | [Rogers 2022](2022-TEL-ROGERS-OUTAGE.md): a risk rating that decayed with success chose the cheap path |
| An evaluation error is a deny | ADR-0030 §1, §4 (`FloorErrorIsDeny`; `M_ERR`) | [CrowdStrike 2024](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md): the fix was that sentence in C++. [Triton](2017-ICS-TRITON-SIS.md): the plant tripped safe through it |
| A lease does not outlive its round | ADR-0031 §2 | [Ronin 2022](2022-FIN-RONIN-BRIDGE.md), [Ukraine 2015](2015-ICS-UKRAINE-GRID.md) |
| A certificate is sized for capture | ADR-0061 §1 | [Ronin](2022-FIN-RONIN-BRIDGE.md): six of nine instead of five, and the attack falls one signature short |
| Coupling makes a dead monitor a stall | ADR-0039 §2 (`M_NOCOUPLE`, `M_MARK`) | [Bangladesh 2016](2016-FIN-BANGLADESH-SWIFT.md) (the printer), [2003 blackout](2003-NRG-NORTHEAST-BLACKOUT.md) (`M_MARK` exactly), [MCAS](2019-CTL-737-MAX-MCAS.md) (an inoperative disagree alert) |
| The governor counts, not the stack | ADR-0062 §1 (`Intent`; `M_NOCOUNT`) | [Knight 2012](2012-FIN-KNIGHT-CAPITAL.md), [MCAS](2019-CTL-737-MAX-MCAS.md) |
| Semantic judgment is never a lift | ADR-0007 | [EchoLeak](2025-AIA-ECHOLEAK-COPILOT.md): the classifier was bypassed by rephrasing, and a label is not |
| A deny needs no permission | ADR-0050 §4 (`DenyAlwaysAvailable`) | [MCAS](2019-CTL-737-MAX-MCAS.md): the trim cutout saved the earlier flight. [Cruise 2023](2023-ROB-CRUISE-PEDESTRIAN-DRAG.md): the grounding waited for the CEO |
| HITL is a key, not a judgment | ADR-0066 §5 | [Citibank–Revlon](2020-FIN-CITI-REVLON-PAYMENT.md) |
| Unanimity does not decorrelate | ADR-0024, consequences | [Citibank–Revlon](2020-FIN-CITI-REVLON-PAYMENT.md), [CrowdStrike](2024-CLD-CROWDSTRIKE-CHANNEL-FILE.md) |
| Four overlay rows are trust roots nothing issues | ADR-0068 §6, "Not met" | [Buncefield](2005-ICS-BUNCEFIELD.md), [Therac-25](1986-MED-THERAC-25.md), [Triton](2017-ICS-TRITON-SIS.md) |
| Refuse common knowledge rather than need it | ADR-0063, ADR-0066 | [Two Generals](1975-GAM-TWO-GENERALS.md) |
| No incentive-compatibility claim | the premise (ADR-0007) | [Selfish mining](2014-GAM-SELFISH-MINING.md), [Axelrod](1980-GAM-AXELROD-TOURNAMENT.md) |
| An effect unreachable when no budget can be met | ADR-0032 §4 | [Thought experiment](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md): "decide where you will not go before you leave". [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md): the airline barred the type from above 10,000 m |
| The mechanism writes the act's record, and the principal cannot | ADR-0042 §3, ADR-0028 F1 | [TWA 841](1979-AVI-TWA-841-UPSET.md): it would have settled the one fact the Board could not, whether anyone moved the flap lever, though not why |
| A finding blocks the next admit with no quorum | ADR-0038 §5 (`DenyByAnyOf`) | [Pulkovo 612](2006-AVI-PULKOVO-612-STALL.md): the climb after the first two stall warnings would have been refused |
| Module checking finds what drafting misses | ADR-0046 | [Byzantine Generals](1982-GAM-BYZANTINE-GENERALS.md): `Membership`'s `M_TWOVOTES` found two successors under ADR-0061 §3 as first drafted |

## 7. Existing findings the scenarios bear on

These are already the corpus's own findings, re-weighted by how often a real episode exhibits them. Counts are of
scenarios citing the identifier in `model.findings`; CR-2 and TM9 are also argued in the prose of two more and one
more respectively.

| Finding | What it says | Scenarios | What this inventory adds |
|---|---|---|---|
| CR-2 | Detection fails open | 14 | Four more shapes than the two ADR-0039 §5 names (SF-5). The collusion case stays open (Axelrod, FCC) |
| TM13 | A peer that lies; "peers stalled by claims" | 9 | The residual measured at national scale from honest inputs (SF-2) |
| TM9 | A deceived person at a release seat; "nothing here sees it" | 10 | Seen at TMI, Citibank, AF447, Therac-25, Air Canada (one step further out). The commonest way the backstop fails. The Learjet 60's radar is TM9's shape with no adversary: a proxy that under-reports |
| CR-17 | Every control ending in a person presumes a present, trained person | 12 | Teterboro, Uber, AF447, Gripen, Rogers (14 hours without logs), Pulkovo 612 (the least trained person held the monitoring seat), TWA 841 (whose training was the dispute) (SF-15). The thought experiment adds that a trained person cannot see what lies ahead (SF-25) |
| TM7 | An insider with a key; "recorded and not prevented" | 9 | Ukraine, Bangladesh, Ronin, Teterboro; and honest error in the same row (S3, CenturyLink) |
| CR-37 | No liveness property for a design that stalls | 7 | Partly addressed by `Coupling_live`, `Emergency_live`. The scenarios ask for recovery, not just "the stall ends" (SF-1) |
| TM11 | A colluding Observer | 6 | Repeated pairing sustains it without a message (SF-17) |
| CR-36 | Every number is a placeholder | 5 | Optus's vendor defaults, Buncefield's movable alarm levels, Uber's unmeasured `D` |
| CR-15 | Nothing in the alphabet types reversibility | 3 | ADR-0066 answers it as a declaration; reversibility changes after admission (SF-18) |
| CR-24, CR-34 | Unsigned trust edges; the operator channel trusted by a socket's file mode | 2, 4 | SS7 and BGP are trust by membership at scale; the design refuses it, and the running reference does not yet |
| CR-32 | Injection inside the envelope; "appears addressed" by ADR-0047 | 1 | Holds only on two declarations and a renderer (SF-10) |
| CR-38 | Forensic retention against erasure | 4 | A deployer held to what its agent said has a stake (SF-11). TWA 841's erased cockpit recording: TOPAK would keep only the record that an erasure happened (ADR-0028 F6) |
| CR-3 | No delegation or chain model | 2 | Ronin's never-revoked delegation; feedback between deployments (Flash Crash) |
| CR-57 | Checkers pass or stay silent on a failure | 1 | The blackout's cause in the corpus's own tooling (SF-5) |

## 8. Proposed modules, consolidated

The entries propose 42 modules, each named by one writer. Grouped by the gap they would close:

| Gap | Modules proposed | Finding |
|---|---|---|
| Effect confirmation and sensed state | `EffectConfirmation`, `WorldObserver`, `MeasuredExtent`, `SensedAdmit` | SF-4 |
| Reach of a subtraction | `SubtractionReach` (4) | SF-2 |
| Recovery path and manual reversion | `RecoveryPath` (3), `ManualReversion` | SF-3 |
| Staged and retired promotion | `StagedPromotion` (4), `Rollout` | SF-6 |
| Independence | `SignerIndependence`, `InterlockIndependence` | SF-7 |
| Size of an act | `ExtentGuard` | SF-8 |
| Typed values | `DimensionedLift` | SF-9 |
| Monitors of monitors, human Observers | `MonitorOfMonitor`, `HumanObserverLiveness` | SF-5 |
| The person in the loop | `ActDisplay`, `SeatHandover` (2), `HandBack`, `PilotInLoop`, `Teleoperation` | SF-15 |
| Peers and federations | `PeerFederation` (2), `CounterpartyScreen`, `MarketFeedback`, `CoordinationFold`, `RepeatedPairing` | SF-17 |
| Reports, disclosure, representation | `Disclosure` (2), `Representation`, `ReportEgress`, `Freeze` | SF-10, SF-11, SF-14 |
| Reversal | `Restitution` | SF-18 |
| Floor host | `FloorHostCompromise` | SF-13 |
| Message timing | `Withholding`, `JointEffect` | SF-19 |
| Agreement | `ByzantineAgreement` | SF-20 |
| Reuse | `EnvelopeOfReuse` | SF-21 |
| The grantee's margin | `VehicleEnvelope` (2), `MarginEnvelope` | SF-22 |
| Instructions and objections | `Instruction` (narrowed) | SF-23 |
| Out-of-range rescue | `RangeExcursion` | SF-24 |
| Terminal behaviour's trigger | `MeasuredTrigger` | SF-16, SF-25 |
| Contested precedence | `Precedence` | §6 (already the composition's rule) |
| Downstream data | `ReplicatedWrite` (a deployment node, not the archetype's) | — |

**If only five were built,** in order of leverage:

1. `SubtractionReach` and `RecoveryPath` together, because they answer SF-1 to SF-3, the availability side of a
   fail-closed design.
2. The effect-confirmation module, because it answers SF-4 and half of SF-5.
3. `StagedPromotion` with `Rollout`'s retirement property.
4. `SeatHandover`.
5. `SignerIndependence`, with its interlock twin as a mutation.

## 9. Suggested entries, none made

By record, for whoever dispositions this. Each names the finding it answers.

| Record | Status | Suggested change | Finding |
|---|---|---|---|
| ADR-0045 | In force | A column per row: what a stop of this component does to effects in flight | SF-1 |
| ADR-0039 §5 | In force | Name the forged-input case beside collusion, and say why TOPAK's own Observers are not exposed | SF-5 |
| ADR-0039 | In force | A repaired or re-enabled Observer re-earns liveness by progress | SF-5 |
| ADR-0040 / ADR-0049 | In force | An extent on a Run entry, measured by the tool host; a per-lease effect count in Run | SF-8 |
| ADR-0049 §3 | In force | Decide ranges, granularity and units as checked fields | SF-9 |
| ADR-0047 | In force | Labelled subsets by author; a `Report` to a dereferencing renderer is an outward entry | SF-10 |
| ADR-0024 / ADR-0044 | In force | Promotion reach by ring; retirement of superseded revisions | SF-6 |
| ADR-0030 §5 | In force | Note that a bundle revision dropping a deny is an ordinary promotion | SF-6 |
| ADR-0031 §5 | In force | Name the grim rule as a choice; who may lift a revocation (custodian) | SF-12 |
| ADR-0052 §1, §6 | Provisional | The emergency channel declared and rowed; drills name the failure they assume | SF-3 |
| ADR-0052 §7 | Provisional | A custodian decision on manual reversion | SF-3 |
| ADR-0023 / ADR-0058 | In force / Proposed | A declared availability residual; *Keep* restates environmental givens | SF-1, SF-21 |
| ADR-0051 | Proposed | A coordination fold; whether a correlator may read a second deployment's floor | SF-14, SF-17 |
| ADR-0061 | Proposed | Say 3f + 1 follows from refusing A3; correct the MAC recollection; an independence row | SF-20, SF-7 |
| ADR-0062 §7 | Proposed | Carry the terminal-behaviour principle into the archetype; a prepared alternative counts | SF-16 |
| ADR-0065 §3 | Proposed | Say whether a report reveals its sender | SF-17 |
| ADR-0066 | Proposed | Discharge "what a person must be shown" (the act carries its computed effect); class changes after admission | SF-15, SF-18 |
| ADR-0068 | Proposed | A row or assumption on how replica and signer independence is obtained | SF-7 |
| (new) | — | Seat handover between a senior and a junior seat, decided before the hazard where it can be | SF-15 |
| ADR-0062 §1 / ADR-0065 §1 | Proposed | A margin the grantee measures, lifted as a governor fact a bundle may refuse on | SF-22 |
| ADR-0059 / ADR-0065 / (new) | Proposed / custodian | An objection channel from child to parent that triggers re-planning and never retains withdrawn authority; whether instructions to act belong in the archetype | SF-23 |
| ADR-0049 §3 / ADR-0052 §2 | In force / provisional | Any range limit comes with a prepared excursion a seated person may take alone, on the record | SF-24, SF-9 |
| ADR-0066 §5 | Proposed | Move as much of the person's judgment as possible to before the round; a measured trigger for the rest | SF-25, SF-16 |

## 10. Where the pattern stops

The scenarios also mark what TOPAK does not claim, and should not be read as claiming.

- **Physics.** Stall margins, actuator rates, pressure, voltage and orbital mechanics are in no module. `Alone`'s
  header says it: "Reaching a safe state is physics, and is not here."
- **Perception.** TOPAK would not have classified the Tempe pedestrian, read the Revlon screen correctly or known an
  AOA vane was bent. TM9 assumes perception is wrong, and "perception never adds authority".
- **The public.** Optus's 000 callers, Air Canada's customer and Cruise's pedestrian are outside every deployment's
  envelope. The pattern bounds what a deployment's principals may do. It owes nothing to people it never seats,
  except through the deployer.
- **Markets and law.** Whether a payment can be clawed back, whether trades are broken and whether a fork is
  legitimate are decided outside the mechanism. TOPAK's position, that nothing permitted is void, is right for the
  mechanism and silent beyond it.
- **Incentives.** No module has a payoff or a rational player, by design.

## 11. Method and limits

- **Sources.** The 45 entries' Analyses were read in full, and every clause quoted here was opened at `dbb2b0c`.
  Twenty-four quotations were checked word for word against the records, and all stand. For the four entries added
  from the video, the clause references they rest on (ADR-0031 §4, ADR-0059 §3) were opened and stand. Statuses are taken from each
  record's status line. Scenario facts are the entries'; their sources and what they could not confirm are listed in
  each entry.
- **Counts.** Counts of scenarios are from front matter (`model.findings`, `model.records`, `model.modules`) and from
  the Analyses where a finding is argued in prose. They are indicators of recurrence, not of importance, and the
  inventory's sectors are not a sample of anything.
- **Not done.** No module was written, no TLC run made and no record edited. The `outside:` steps were not
  normalised across writers; §8's grouping does that work for the proposed modules only.
- **Not independent.** See the head of this document.
