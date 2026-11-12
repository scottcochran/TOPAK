# TOPAK — The scenario findings and the controls in force, against published standards

**2026.11.12** · derived · a comparison, not a record · basis: the tree at `981bc77`; the scenario inventory's
findings (`derived/scenarios-2026.11.12/FINDINGS_TOPAK.md`, SF-1 to SF-26); the 2026.10.09 alignment and §8 of the
2026.10.05 assessment, whose marks are carried and not re-made; the 2026.11.11 feature list (§14 to §16) and
residual-risk statement · prepared by the assistant at the custodian's request · nothing in the tree outside this
file was changed, except this file's row in `derived/README.md` · **suggested entries, none made**

The custodian asked how the scenario findings, and the controls TOPAK already has, compare with three bodies of
outside text: the sector standards of the industries the scenarios come from, the standards and research of AI
safety, and the aggregate catalogues that roll many standards into one control set. This document answers in that
order, after one table that places each finding.

**Not a conformance claim.** Nothing here says TOPAK conforms to any standard. A standard "requires" something of
whoever is bound by it, which is an operator, a manufacturer, a provider or a deployer. TOPAK is a design pattern
with a reference implementation that "is not a deployable system" (`README.md`). The comparison is between what a
text asks for and what the records say.

**Not independent.** The findings, the alignment, this comparison and the four readers that checked its outside
references are all of one model lineage. That is not the reader ADR-0029 A2 asks for.

**How each outside text was read.** Every outside clause below carries one of five marks. Only **O** means the
words were compared with the text.

| Mark | Meaning |
|---|---|
| **O** | Opened. The issuing body's own file or page was read for this document |
| **E** | Extract. A search engine's extract of the issuing body's page, or of a faithful copy of an official text, was read. The page was not opened |
| **S** | Secondary. A named third party's account was read, as a search extract |
| **C** | Carried. An earlier derived document of this corpus read the primary text; it was not re-read |
| **R** | Recalled. From the assistant's memory, not checked |

EUR-Lex returned no content to an automated client and ISO's site refused one, and neither was pressed, so the EU
regulations and every ISO text are **E** or **S**. IEC, RTCA, SAE and UL texts are sold, and are **E** or
**S** from tables of contents and explainers. §7 lists what was opened, by digest.

---

## 0. Summary

1. **Most of the findings restate requirements that already exist.** Of the twenty-six, twelve are stated in a
   standard read here, four are stated in an AI-specific text and are scoped out or conceded by the corpus, four are
   partly stated, five were found in no text read, and one is not a standards matter (§1).
2. **The findings document does not say so.** The only outside rules it cites by designation are the NIST AI RMF,
   once, and US aviation rules and guidance (14 CFR 91.3 and 91.123, AIM 4-4-1, AC 120-111). It names no
   functional-safety, security-control or AI-security text. Of the 45 entries, one cites a functional-safety
   standard by number, at second hand.
3. **Weight follows familiarity.** Nine of the ten findings weighted High are stated in a text read here. All five
   that were found nowhere are weighted Medium or lower.
4. **Nine findings restate deltas the corpus's own alignments already hold** (§1.5). The inventory re-found them
   from incidents, which is corroboration, and it did not connect them.
5. **Against AI governance texts TOPAK is deep and narrow, and the findings do not change the tally.** The
   alignment's marks stand at M 11 · P 27 · C 3 · G 3 · X 28 of 72. The findings would move none up. If SF-26 is
   accepted, five X rows meet the alignment's own definition of a gap (§3.1).
6. **Against the AI-safety research the premise is shared and the method is opposite.** The AI-control literature
   assumes an agent that subverts on purpose, as TOPAK does. It puts a monitor's judgment in the action path and
   measures the result by adversarial evaluation. TOPAK forbids the first and has never done the second (§3.5).
7. **Against SP 800-53 TOPAK reads as deep in three of twenty families, partial in six, thin in five and silent
   in six** (§4.1). Seventeen findings have a home family; thirteen of those land in a partial, thin or silent
   one.
8. **One earlier claim of the corpus needs a qualification.** The 10.05 assessment found that no text it read asks
   who may change an enforced policy or how many must agree. SP 800-53, which it did not read, asks for approval of
   changes, separation of duties, dual authorization and consent by "multiple authorized entities". What remains
   TOPAK's own is narrower (§5).

## 1. The findings against the texts

"Relation" is this document's reading:

- **Stated**: a text read here requires what the finding says the corpus lacks.
- **Stated for AI**: an AI-specific text asks for it, and the corpus marks it out of scope, as a gap, or concedes
  it in a record.
- **Partly**: the hazard or the principle is named, and the control the finding asks for is not.
- **Not found**: no text read here asks for it. That is a statement about what was read.

| Finding | What it asks for | Nearest published requirement, and how it was read | Relation |
|---|---|---|---|
| [SF-1](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-1) | A stop has a cost: record what a stopped component does to effects in flight | IEC 61508-4 safe state **S** · ISO 26262-1 fault reaction ends in "a safe state or … emergency operation" **E** · IEC 62443-3-3 §4.2 **E** · EU AI Act Art. 14(4)(e), 15(4) **E** · SP 800-53 SC-24, CP-2, SI-17 **O** · STPA, first unsafe-control-action type **E** · TACIP 3.2.3 **C** · AI RMF MEASURE 2.6 **O** | Stated |
| [SF-2](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-2) | A bound on how many cells one item, one deny or one dependency can stop | SP 800-160 Vol. 2 Segmentation, Coordinated Protection **O** · SP 800-53 RA-9, CP-2(8) **O** · OWASP ASI08 **C** | Partly: the principle, no bound |
| [SF-3](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-3) | An emergency channel that survives what it repairs; drills that name the failure assumed | SP 800-53 CP-13, SC-37, CP-11, CP-4 **O** · IEC 62443-3-3 §4.2 **S** · ISO/IEC 27001:2022 A.5.29, A.5.30 **S** | Stated |
| [SF-4](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-4) | Confirm the world changed, by a channel separate from the command | TACIP 3.9.5(c) **C** · IEC 61508-2 Table A.14, IEC 61511-1 §11.7.2.4 **E**, **S**: diagnostics and status, no confirmation clause found | Stated in TACIP; partly in functional safety |
| [SF-5](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-5) | Monitors that are fed forged input, human, disabled by maintenance or silent at the extreme; findings wired to nothing | NERC TOP-010-1(i) R4 **O** · SP 800-53 SI-6 **O** · IEC 61511-1 cl. 16 (proof testing 16.3 **E**; bypass 16.2.4 **S**) · TACIP 2.2.2, 3.4.3, 3.2.4 **C** · AI-control untrusted monitoring **O** | Stated for the monitor of the monitor and re-verification; partly for the rest |
| [SF-6](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-6) | Promotion staged by reach; superseded revisions retired | MiFID II RTS 6 Art. 8 **E** · SP 800-53 CM-3(2), CM-4(1) **O** · DORA Art. 9(4)(e) **E** · ISO/IEC 27001:2022 A.8.32 **S** · OWASP ASI08 **C** | Stated for staging; partly for retirement |
| [SF-7](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-7) | Independence of signers, redundant units, interlocks and layers | IEC 61508-6 Annex D **E** · IEC 61511-1 §9.4 **E** · Buncefield board, Recommendation 3 **E** · ARP4761 common mode analysis **S** · SP 800-53 SC-29, PL-8(2) **O** · SP 800-160 Vol. 2 Diversity **O** · EU AI Act Art. 15(4) **E** | Stated |
| [SF-8](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-8) | An extent and a count on a Run entry; no vacuous envelope | MiFID II RTS 6 Art. 15 **E** · SEC Rule 15c3-5(c)(1) **E** · OWASP LLM06:2025, LLM10:2025 **O** · SP 800-53 SC-6 **O** · TACIP 2.1.1, 3.5.4 **C** | Stated |
| [SF-9](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-9) | Range, unit and granularity as checked fields; interfaces compared across live revisions | SP 800-53 SI-10, SC-31 **O** | Stated for validation and covert channels; units not found |
| [SF-10](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-10) | Labels by author; a rendered `Report` treated as egress | OWASP LLM01:2025, LLM05:2025, LLM02:2025 **O** · OWASP ASI01 **C** · SP 800-53 AC-4 **O** | Stated for AI; conceded by ADR-0047 §7 |
| [SF-11](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-11) | A freeze a user can put on the admit path; a statement that carries its policy | OWASP LLM06:2025, LLM09:2025 **O** · Five Eyes guidance **C**, which supports TOPAK's position | Partly: the hazard, not the control |
| [SF-12](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-12) | Permanent revocation named as a choice, with its cost | None | Not found |
| [SF-13](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-13) | The floor's host as an adversary; the voter's view of what is voted | SP 800-53 AC-25, SI-7, CM-14, SR-4 **O** · Five Eyes attestation **C** | Stated for the host; the voter's view not found |
| [SF-14](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-14) | A report to an overseer projected from the record | EU AI Act Art. 73, 72 **E** · ISO/IEC 42001 B.8.4 **O** (title, from NIST's crosswalk) · SP 800-53 IR-6, IR-6(1) **O** · AI RMF MANAGE 4.3 **O** | Stated for AI as a duty; the projection not found |
| [SF-15](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-15) | What a person is shown; who takes over; what a hand-back carries; continuous control | EU AI Act Art. 14(4), 26(2) **E** · AI RMF MAP 3.4, 3.5 **O** · NIST AI 600-1 Human-AI Configuration **O** · OWASP ASI09 **C** · SP 800-53 SA-8(27), AT-3 **O** | Stated for AI; MAP 3.4 is already a G |
| [SF-16](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-16) | A terminal behaviour declared at seating, outside the stack | SAE J3016 minimal risk condition **S** · UL 4600 **E** · ISO 26262-1 **E** · SP 800-53 CP-12, SI-17 **O** · EU AI Act Art. 14(4)(e) **E** · TACIP 3.2.3 **C** | Stated |
| [SF-17](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-17) | Several roots; an honest peer against a blind subject; refusal by an outsider; collusion through permitted channels | OWASP ASI07 **C** · Motwani et al., arXiv:2402.07510 **O** · AI-control collusion countermeasures **O** · SP 800-53 SC-31 **O** | Not found as a requirement; research only |
| [SF-18](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-18) | Reversibility that changes after admission; compensation as a new act | None | Not found |
| [SF-19](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-19) | Withholding as one property; a joint effect | None | Not found |
| [SF-20](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-20) | Where ADR-0061's 3f + 1 comes from; a recollection corrected | The literature the record cites | Not a standards matter |
| [SF-21](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-21) | *Keep* restates a kept node's environmental givens | ISO 26262-10 cl. 9 (SEooC) **E** · RTCA DO-178C §12.1 **S** · IEC 61508-2 §7.4.10 **E** | Stated, by the precedent ADR-0023 cites |
| [SF-22](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-22) | The grantee's measured margin as a fact a bundle may refuse on | ISO 21448 **E**, **S** · UL 4600 **E** | Partly |
| [SF-23](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-23) | An objection that never retains withdrawn authority; an instruction to act | The entries' own aviation rules only | Not found outside sector law |
| [SF-24](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-24) | A prepared excursion a seated person may take alone, on the record | SP 800-53 AC-3(10) **O** · IEC 62443-3-3 §4.2 **S** | Stated |
| [SF-25](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-25) | Counterfactuals qualified by hindsight; judgment moved to before the round | ISO 21448 **S**, for a hazard with no fault | Partly |
| [SF-26](scenarios-2026.11.12/FINDINGS_TOPAK.md#sf-26) | Standing for the people an effect lands on | AI RMF MAP 5.1, 5.2, GOVERN 5.1, MEASURE 3.3, MANAGE 4.3 **O** · ISO/IEC 42001 B.5.4, B.5.5, B.8.3 **O** (titles, from NIST's crosswalk) · EU AI Act Art. 27, 85, 86, 9(9) **E** · ISO 14971 **S** · UL 4600 **E** | Stated for AI; scoped out by the corpus |

**Counts.** Stated: 12 (SF-1, 3, 4, 5, 6, 7, 8, 9, 13, 16, 21, 24). Stated for AI: 4 (SF-10, 14, 15, 26). Partly: 4
(SF-2, 11, 22, 25). Not found: 5 (SF-12, 17, 18, 19, 23). Not a standards matter: 1 (SF-20).

### 1.1 The twelve that are stated

The wording that matters most, where it was opened or extracted:

- **A stop is safe only if the stopped state is.** IEC 61508-4 defines a safe state as the "state of the EUC when
  safety is achieved" (**S**): it is a state of the equipment under control, not of the controller. ISO 26262-1's
  fault reaction time interval runs "from the detection of a fault to reaching a safe state or to reaching emergency
  operation" (**E**). The EU AI Act's stop control is one "that allows the system to come to a halt in a safe state"
  (Art. 14(4)(e), **E**). SP 800-53 SC-24's discussion says "Failure in a known safe state helps to prevent systems
  from failing to a state that may cause injury to individuals or destruction to property" (**O**). ADR-0045 §2
  classes a component by what its failure does to authority. Each of these texts classes it by what the stop does to
  the thing controlled, which is SF-1's sentence. IEC 62443-3-3 §4.2 carries the availability half: essential
  functions "shall be maintained if zone boundary protection goes into fail-close and/or island mode" (**S**, with
  the clause heading **E**).
- **An alternative when the primary is what failed.** SP 800-53 CP-13: "Employ [alternative or supplemental
  security mechanisms] for satisfying [security functions] when the primary means of implementing the security
  function is unavailable or compromised" (**O**). SC-37 is "Out-of-band Channels" and CP-11 "Alternate
  Communications Protocols" (**O**). ADR-0052 §1 makes that argument for the identity provider only, which is SF-3.
- **A monitor of the monitor is a binding requirement in the sector SF-5 took it from.** NERC TOP-010-1(i) R4:
  "Each Transmission Operator and Balancing Authority shall have an alarm process monitor that provides
  notification(s) to its System Operators when a failure of its Real-time monitoring alarm processor has occurred"
  (**O**). SF-5 quotes the 2003 Task Force and proposes `MonitorOfMonitor` from it; the standard that followed is
  the same sentence. SP 800-53 SI-6 asks that the correct operation of security functions be verified at
  system transitional states, on command or at a set frequency, and that failed tests raise an alert; its
  discussion says "Transitional states for systems include system startup, restart, shutdown, and abort" (**O**).
  That is SF-5's "A repaired or re-enabled Observer re-earns liveness by progress, not by restart".
- **Staged deployment is law for trading algorithms.** RTS 6 Art. 8, "Controlled deployment of algorithms":
  "Before deployment of a trading algorithm, an investment firm shall set predefined limits on" the number of
  instruments traded, "the price, value and numbers of orders", the strategy positions, and the number of venues
  (**E**). Those four limits are a ring's reach. SP 800-53 has testing before a change (CM-3(2), CM-4(1), **O**), and
  the words "staged", "phased", "canary" and "rollout" occur nowhere in its catalogue (**O**).
- **Independence is asked of redundant parts in general.** IEC 61508-6 Annex D is "A methodology for quantifying
  the effect of hardware-related common cause failures" (**E**), and IEC 61511-1 §9.4 is "Requirements for
  preventing common cause, common mode and dependent failures" (**E**). The Buncefield board's Recommendation 3
  asks for an overfill prevention system "physically and electrically separate and independent from the tank
  gauging system" (**E**). SP 800-160 Vol. 2 defines Diversity as "Use heterogeneity to minimize common mode
  failures" (**O**), and SP 800-53 SC-29's discussion says "Such diversity protects against common mode failures"
  (**O**). The corpus asks it of Observers (ADR-0038 §4) and, in a Proposed record, of Personas (ADR-0035).
- **Limits on the size of an act.** RTS 6 Art. 15 requires "price collars", "maximum order values", "maximum order
  volumes" and "maximum messages limits" (**E**). OWASP's LLM06:2025 gives the cause from the agent side: "The root
  cause of Excessive Agency is typically one or more of: excessive functionality; excessive permissions; excessive
  autonomy" (**O**). SF-8 is the first two as the archetype's Run has them.
- **An audited override is a catalogue control.** SP 800-53 AC-3(10): "Employ an audited override of automated
  access control mechanisms under [conditions] by [roles]", and its discussion: "when there is a threat to human
  life … an override capability for access control mechanisms may be needed" (**O**). ADR-0052 retired the floor's
  break-glass exception and replaced it with a seating that needs a roster's quorum. SF-24 asks for the catalogue's
  control back, for one seated person, in a prepared form.
- **Reuse restates its assumptions.** ISO 26262's safety element out of context is the precedent ADR-0023 cites for
  the archetype. Its guidance is ISO 26262-10 clause 9 (**E**). DO-178C §12.1 is "Use of Previously Developed
  Software" (**S**) and IEC 61508-2 §7.4.10 "Requirements for proven in use elements" (**E**). SF-21 asks ADR-0058's
  *Keep* to do what the cited precedent already expects of an integrator. The clause text was not read, so that
  last step is **R**.
- **Effect confirmation is the weakest of the twelve.** No functional-safety clause was found that requires an
  actuation to be confirmed as having happened. What was found is diagnostic technique for final elements (IEC
  61508-2 Table A.14, **E**) and a requirement that SIS status critical to the function be at the operator
  interface (IEC 61511-1 §11.7.2.4, **S**). The requirement in SF-4's form is the profile's: the organization "can
  confirm the change actually took effect, rather than relying exclusively on the capability's self-attestation"
  (TACIP 3.9.5(c), **C**).

### 1.2 The four stated for AI

- **SF-26.** The AI RMF's MAP 5 is "Impacts to individuals, groups, communities, organizations, and society are
  characterized" (**O**). MEASURE 3.3: "Feedback processes for end users and impacted communities to report
  problems and appeal system outcomes are established and integrated into AI system evaluation metrics" (**O**).
  MANAGE 4.3: "Incidents and errors are communicated to relevant AI actors, including affected communities" (**O**).
  The EU AI Act gives affected persons a complaint (Art. 85) and an explanation of "the role of the AI system in the
  decision-making procedure" (Art. 86), and asks some deployers for a fundamental rights impact assessment before
  first use (Art. 27) (all **E**). The alignment marks MAP 5.1, MAP 5.2, GOVERN 5.1, GOVERN 5.2 and MEASURE 3.3
  out of scope. SF-26's reciprocity table is, row for row, what these texts ask.
- **SF-15.** EU AI Act Art. 14(4)(b) asks that an overseer be able "to remain aware of the possible tendency of
  automatically relying or over-relying on the output" (**E**), and Art. 26(2) that oversight go to people "who
  have the necessary competence, training and authority" (**E**). AI RMF MAP 3.4 asks that operator proficiency be
  "defined, assessed, and documented" (**O**). The alignment already marks MAP 3.4 a gap. SF-15 adds what the
  texts do not have: which seat takes over, and what a hand-back must carry.
- **SF-14.** EU AI Act Art. 73 sets deadlines for reporting a serious incident: 15 days in general, two days for a
  widespread infringement or a critical-infrastructure incident, ten days after a death (**E**). No text read asks
  that the report be a projection of the record that a person may add to and not subtract from. That part is the
  finding's own.
- **SF-10.** Prompt injection and improper output handling are LLM01:2025 and LLM05:2025 (**O**). ADR-0047 §7
  already says what it does not cover, and EchoLeak lands there.

### 1.3 The four partly stated

SF-2's bound, SF-11's user-settable freeze, SF-22's measured margin and SF-25's hindsight each have a named
hazard and no requirement in the finding's form. SP 800-160 Vol. 2's Coordinated Protection comes closest to SF-2:
"ensure that the use of any given protection mechanism does not create adverse, unintended consequences by
interfering with other protection mechanisms" (**O**). CenturyLink's deny that blocked its own withdrawal is that
sentence. ISO 21448 is the standard for a hazard with no fault, "due to a hazard caused by functional
insufficiencies" (**E**), which is where SF-22, SF-25 and TM9 without an adversary would sit.

### 1.4 The five found nowhere

SF-12 (revocation as a grim trigger), SF-17 (peers), SF-18 (reversibility after admission), SF-19 (withholding and
joint effects) and SF-23 (objection without retention) were found in no standard read. SF-17's collusion half has
research behind it and no requirement: Motwani et al. formalise "secret collusion in systems of generative AI
agents" (**O**), and the AI-control literature treats collusion between a policy and its monitor (§3.5). These five
are the inventory's original contribution, as far as this reading reaches. All five are weighted Medium or lower
by the findings document.

### 1.5 Nine findings the corpus's alignments already hold

FINDINGS_TOPAK.md §7 lists the `CR-` and `TM` findings the scenarios bear on. It does not list the rows of the
10.05 assessment and the 10.09 alignment that say the same thing:

| Finding | Already held as | Where |
|---|---|---|
| SF-1 | TACIP 3.2.3: a refused action needs its own fail-safe state; "ADR-0023's schema has no field for it" | 10.05 §8.2; 10.09 §2.2 |
| SF-4 | TACIP 3.9.5(c): *Verifiable* fails, since evidence is self-attested | 10.05 §8.2; 10.09 §2.2 |
| SF-5 | TACIP 2.2.2 "a watchdog may itself be part of the attack surface"; 3.2.4 and 3.3.1 marked G: "nothing alerts a person" | 10.05 §8.2; 10.09 §2.2 |
| SF-6 | "no SLOs, canaries, flags"; "no semver, deprecation, retirement" | 10.09 Part IV |
| SF-8 | "Absent: per-tool rate limits and kill switch"; history-dependent policy is a fixed set of folds | 10.09 Part IV; feature list §14 item 5 |
| SF-10 | Output sanitization excluded by ADR-0007; "A label is a declaration, not a finding" | 10.09 Part IV |
| SF-14 | MANAGE 4.3 partial: communication "to affected communities" not addressed | 10.09 §1.9 |
| SF-15 | MAP 3.4, a gap: "nothing about skill" | 10.09 §1.7 |
| SF-26 | Twenty-eight rows out of scope, among them MAP 5.1, 5.2, GOVERN 5.1, 5.2, MEASURE 3.3; MANAGE 4.1's appeal half | 10.09 §1.10, §1.9 |

The scenarios add the evidence that these deltas cause harm. They do not add the deltas.

---

## 2. Sector standards and the controls

TOPAK already uses three sector ideas, and says so for two:

| Sector idea | Text | In TOPAK | What differs |
|---|---|---|---|
| A time budget from fault to safe state | ISO 26262-1: the fault handling time interval is the "sum of fault detection time interval and the fault reaction time interval", and must be shorter than the fault tolerant time interval **E** | ADR-0032 §4: "`W + L + D < T_irrev` is the property" | ISO's reaction ends in a safe state or emergency operation. TOPAK's ends when the admit is refused. The gap between the two is SF-1 and SF-16 |
| A component developed out of context | ISO 26262-10 cl. 9 **E** | ADR-0023 and the Theory of Operation cite it as the archetype's precedent | SF-21 |
| The monitor is a controller | STPA **E**; cited in the Theory of Operation | "the Observer is a controller, not a probe" | STPA's four unsafe control actions start with "Not providing the control action leads to a hazard" (**E**). The premise covers the second, providing, in depth, and the first barely |

Where the sector texts have a construct and TOPAK has a partial counterpart:

| Sector construct | Text | TOPAK's counterpart | Finding |
|---|---|---|---|
| Safe state, defined of the equipment under control | IEC 61508-4 **S** | Fail closed, defined of authority (ADR-0045 §2) | SF-1 |
| Proof test: a "periodic test performed to detect dangerous hidden failures" | IEC 61508-4 **S**; IEC 61511-1 §16.3 **E** | A drill "is a real activation" (ADR-0052 §6), for the emergency path only | SF-3, SF-5 |
| Common cause analysis | IEC 61508-6 Annex D **E**; ARP4761 **S** | Observer placement (ADR-0038 §4); Persona lineage (ADR-0035, Proposed) | SF-7 |
| Independent protection layer | IEC 61511-1 §9.4 **E**; Buncefield Recommendation 3 **E** | The floor has "no process, no socket, no fetch" (ADR-0030 §3) | SF-7, SF-13 |
| Essential functions survive the security measure | IEC 62443-3-3 §4.2 **E**, **S** | A deny needs no quorum (ADR-0050 §4); nothing on what a stop interrupts | SF-1, SF-3 |
| Alarm process monitor | NERC TOP-010-1(i) R4 **O** | Coupling stalls on a starved Observer (ADR-0039); nothing tells a person | SF-5 |
| Kill functionality: cancel "any or all of its unexecuted orders" at once | RTS 6 Art. 12 **E** | The epoch fence; `DenyAlwaysAvailable` | None; FINDINGS §6 lists the deny as confirmed |
| Controlled deployment; pre-trade limits | RTS 6 Art. 8, 15 **E** | Unanimous promotion (ADR-0024); a count in the overlay only (ADR-0062, Proposed) | SF-6, SF-8 |
| Minimal risk condition | SAE J3016 **S**; UL 4600 **E** | A voted terminal behaviour, in the overlay (ADR-0062 §7, Proposed) | SF-16 |
| Previously developed software | DO-178C §12.1 **S**; IEC 61508-2 §7.4.10 **E** | *Keep* (ADR-0058 §1, Proposed) | SF-21 |
| Harm to people, property or the environment | ISO 14971 **S**; UL 4600's scope includes "humans who are not operating the item (e.g., pedestrians)" **E** | Impacts on people marked out of scope | SF-26 |

**What the sector texts have that neither TOPAK nor the inventory has.**

- **A hazard analysis of the system itself.** IEC 61508's lifecycle, ISO 14971 and STPA each start from the system
  and derive its hazards. The inventory reads forty-five other systems' accidents against TOPAK. That found real
  gaps, and it is an analysis by analogy. No record derives TOPAK's own unsafe control actions.
- **Graded integrity.** The sector texts scale the rigour required to the consequence. ADR-0045's test has two
  outcomes, and ADR-0057 (Proposed) would add a grade.
- **Functional safety for AI is itself unsettled.** ISO/IEC TR 5469:2024 is a technical report on functional safety
  and AI systems (**E**), and its requirements successor, ISO/IEC TS 22440, is still a committee draft (**E**).
  TOPAK's placement of the model outside the trusted base is consistent with supervising an AI component by
  non-AI means, which is as far as that comparison can go without the text (**R**).

---

## 3. AI governance, security and safety

### 3.1 The NIST AI RMF

The alignment's tally at G11 is carried: **M 11 · P 27 · C 3 · G 3 · X 28** of 72. The findings land on these
rows, with the alignment's marks:

| Row | Mark | Finding | Row text **O** |
|---|---|---|---|
| MAP 5.1 | X | SF-26 | "Likelihood and magnitude of each identified impact (both potentially beneficial and harmful) … are identified and documented" |
| MAP 5.2 | X | SF-26 | "Practices and personnel for supporting regular engagement with relevant AI actors and integrating feedback about positive, negative, and unanticipated impacts are in place and documented" |
| GOVERN 5.1 | X | SF-26 | "… collect, consider, prioritize, and integrate feedback from those external to the team … regarding the potential individual and societal impacts related to AI risks" |
| GOVERN 5.2 | X | SF-26 | "Mechanisms are established to enable the team … to regularly incorporate adjudicated feedback from relevant AI actors into system design and implementation" |
| MEASURE 3.3 | X | SF-26 | Quoted in §1.2 |
| MANAGE 4.1 | P | SF-26, SF-6 | "… appeal and override, decommissioning, incident response, recovery, and change management" |
| MANAGE 4.3 | P | SF-14, SF-26 | Quoted in §1.2 |
| MAP 3.4 | G | SF-15 | Quoted in §1.2 |
| MAP 3.5 | P | SF-15 | "Processes for human oversight are defined, assessed, and documented" |
| MEASURE 2.6 | P | SF-1, SF-16 | "… it can fail safely, particularly if made to operate beyond its knowledge limits" |
| MEASURE 2.4 | P | SF-5 | Not re-read; the alignment's wording stands **C** |

**No mark moves up.** The findings are gaps, and a gap discharges nothing.

**Five marks are put in question.** The alignment's key defines X as "legitimately absent, discharged by a scope
declaration" and G as "TOPAK's own safety argument needs this and does not have it". SF-26 argues that the scope
line does not follow from the premise. If the custodian accepts that, MAP 5.1, MAP 5.2, GOVERN 5.1, GOVERN 5.2 and
MEASURE 3.3 are G by the key's own words, and the tally reads M 11 · P 27 · C 3 · G 8 · X 23. This document
re-makes no mark; that is a new alignment's work.

**Status.** The AI RMF is still 1.0, of January 2023 (**O**). NIST says it is being revised and has posted no
draft (**E**; the 10.05 assessment found the same, **C**). NIST AI 600-1 names twelve risks; the one the scenarios
exercise most is "Human-AI Configuration", whose definition includes "automation bias, over-reliance" (**O**).

### 3.2 ISO/IEC 42001

The corpus has no mapping to ISO/IEC 42001. The standard was not opened. NIST's own crosswalk from the AI RMF to
the final draft of 42001 was (**O**), and it gives a route from the alignment's marks:

| AI RMF row | Alignment | NIST maps it to (42001 FDIS) **O** |
|---|---|---|
| MAP 5.1 | X | 6.1.2 AI risk assessment; B.5.2 AI system impact assessment process |
| MAP 5.2 | X | B.6.1.3; B.6.2.6 AI system operation and monitoring; B.8.3 External reporting |
| GOVERN 5.1 | X | B.5.3; B.5.4 Assessing AI system impact on individuals and groups of individuals; B.8.3; B.10.4 |
| MEASURE 3.3 | X | B.8.2; B.8.3 External reporting; B.8.4 Communication of incidents |
| MANAGE 4.3 | P | 9.3.2; B.6.2.6; B.8.5 Information for interested parties |
| MAP 3.4 | G | 7.2 Competence; B.4.6 Human resources |

Annex B's guidance carries the numbers of the Annex A controls it implements (**S**). So SF-26 lands on A.5
(assessing impacts) and A.8.3, SF-14 on A.8.4, and SF-15 on clause 7.2. Annex A has 38 controls in nine areas, A.2
to A.10 (**S**), and none is titled for human oversight, which sits in the B.9.3 guidance (**S**). ISO/IEC
42001 is a management-system standard: nearly all of it binds an adopter's organization, and TOPAK's records could
discharge little of it directly. No ISO/IEC deliverable on AI agents was found published (**S**; the 10.05
assessment found the same, **C**).

### 3.3 The EU AI Act

Every article is **E**: read as extracts of the Commission's AI Act Service Desk and of EUR-Lex.

| Article | What it asks | TOPAK | Finding |
|---|---|---|---|
| 12 | High-risk systems "shall technically allow for the automatic recording of events (logs) over the lifetime of the system" | Every admit and denial ordered and recorded (ADR-0015, ADR-0028, ADR-0042 §3). The reply's text is erasable payload (ADR-0004; CR-38) | SF-11, SF-14 |
| 14(4)(b) | Awareness of automation bias | Nothing. ADR-0066 §5 (Proposed): "HITL is a key and not a judgment" | SF-15 |
| 14(4)(e) | A stop "that allows the system to come to a halt in a safe state" | A deny with no quorum (ADR-0050 §4, provisional). The stop is there; the safe state is not declared | SF-1, SF-16 |
| 15(4) | "as resilient as possible regarding errors, faults or inconsistencies"; "technical redundancy solutions, which may include backup or fail-safe plans" | Fail closed, proved of the modules. Redundancy without an independence rule | SF-1, SF-7 |
| 26(2) | Oversight by people with "the necessary competence, training and authority" | Authority only (ADR-0050). MAP 3.4 is a gap | SF-15 |
| 27 | A fundamental rights impact assessment before first use, for some deployers | Out of scope | SF-26 |
| 73 | Serious-incident reports within 15, 2 or 10 days | The record exists; no report is derived from it | SF-14 |
| 85, 86 | A complaint to an authority; an explanation to an affected person | Nothing | SF-26 |
| 9(9) | Consider adverse impact on "persons under the age of 18 and, as appropriate, other vulnerable groups" | Out of scope | SF-26 |

**Status.** Regulation (EU) 2026/1744 amended the Act and has been in force since 27 July 2026. The obligations
for Annex III high-risk systems apply from 2 December 2027 (**E**; the 10.05 assessment has the same dates, **C**).
It also replaced Article 4, which now asks for "measures to support the development of AI literacy" (**E**). Whether
it changed the articles in the table was not confirmed. The harmonised standards for logging and human oversight,
prEN 18229-1 and -3, are drafts and are cited nowhere in the Official Journal (**S**). The Act binds providers and
deployers of a system. An adopter of TOPAK would meet Article 12 largely by construction, and Articles 14, 26, 27,
73, 85 and 86 not at all.

### 3.4 OWASP's lists and MITRE ATLAS

The 10.05 assessment maps the Top 10 for Agentic Applications row by row (§8.4), and that mapping is carried.
Against it, the findings add:

- **ASI08 Cascading Failures** is where SF-2 and SF-6 land. Its "governance drift cascade: human oversight weakens
  after repeated success" (**C**) is Rogers's risk rating that fell as earlier phases succeeded.
- **ASI09 Human-Agent Trust Exploitation** is SF-15, and **ASI07 Insecure Inter-Agent Communication** is where
  SF-17 would sit, though TOPAK has no agent-to-agent protocol to secure.
- **LLM06 Excessive Agency** is Replit, and **LLM09 Misinformation** is Air Canada (**O**, 2025 edition).

A 2026 edition of the LLM list was announced on 1 September 2026, in which, in OWASP's words, "Excessive Agency,
now number three" (**O**). The rest of the new order was not opened, so this document cites the 2025 numbers with
their year. The same announcement says an "Agent Control Standard (ACS) has been donated to the OWASP GenAI
Security Project", "extending that guidance toward practical runtime enforcement" (**O**). That is the nearest
outside text to TOPAK's admit path, and it was not read.

MITRE ATLAS is a knowledge base of adversary tactics and techniques against AI systems, with mitigations, at
release v2026.10 with 16 tactics and 129 techniques (**E**). It is not a control catalogue. ADR-0068's threat model
is organised by where an adversary sits, and ATLAS by what it does. No mapping between them exists.

### 3.5 AI-control research

The 10.05 assessment set this literature aside, as one "whose monitors escalate rather than deny". It is the
closest outside work to TOPAK's premise, and it is research and not a standard.

| | AI-control literature | TOPAK |
|---|---|---|
| Premise | Protocols "robust to intentional subversion", against "a powerful but untrusted model" (arXiv:2312.06942, **O**) | Every agent is Byzantine at every position (principle P1) |
| The monitor | A weaker trusted model, or another instance of the untrusted one | An Observer off the Thinker's fault domain (ADR-0038); independent lineage is Proposed (ADR-0035) |
| Collusion | "upfront evaluation of the monitor on synthetic inputs", and redaction "to avoid collusion" (**O**) | The declared gap: coupling "cannot separate an honest Observer from a colluding one" (ADR-0039 §5; TM11). SF-17's `RepeatedPairing` is the same instinct |
| A person | "limited access to high-quality trusted labor", budgeted at 2% of problems (**O**) | A person is a backstop with no budget (CR-17). SF-5 notes a human Observer couples at heartbeat strength only |
| What a finding does | Defer, edit, resample or audit. Resample protocols work by "selectively blocking the AI agent from executing suspicious code and incriminating the agent" (arXiv:2504.10374, **O**) | Deny only, out of the admit path. "Semantic judgment is never a lift" (ADR-0007) |
| The safety claim | A measured rate. In live multi-service environments a strong attacker reached "roughly a 23% undetected sabotage success rate" against a trusted monitor at a 1% false positive rate (arXiv:2604.15384, **O**) | A theorem about what the alphabet allows. It says nothing about a detection rate |
| How it is tested | Control evaluations by a red team | Proofs and mutations of modules. "Evaluation and red-teaming exist nowhere, even as evidence" (feature list §14 item 22) |

Three things follow.

1. **The two are complements.** TOPAK bounds what a subverted agent can reach. Control protocols estimate how
   often subversion inside that bound is caught. Neither does the other's work.
2. **The literature measures TOPAK's declared gap.** Detection that "fails open against a colluding Observer" is
   residual 1.3 of the residual-risk statement. A 23% miss rate under favourable conditions is an outside number
   for how much weight an Observer's silence can bear.
3. **The corpus could be tested the literature's way.** The control settings are public. A control evaluation of
   the reference would discharge the half of MEASURE 2.7 the alignment holds against it: "no adversarial exercise
   against the system has been run".

### 3.6 Frontier-developer frameworks

Anthropic's Responsible Scaling Policy (v3.4, July 2026), OpenAI's Preparedness Framework (v2, April 2025), Google
DeepMind's Frontier Safety Framework (v3.1, April 2026), the EU's General-Purpose AI Code of Practice (July 2025)
and the International AI Safety Report (February 2026) were read as extracts only (**E**). They govern a model
developer: capability thresholds, evaluations, safeguards including the security of weights, and reporting. None
is a control catalogue for a deployer's agent runtime. TOPAK declares the model layer out of scope by its premise;
the alignment marks MEASURE 2.2, 2.5, 2.9 and 2.11 X for that reason. No scenario finding touches these texts. The
nearest overlap is language in the first about "monitoring and/or restricting AI behavior and usage internally"
(**E**), which is a mitigation named and not a control specified.

### 3.7 Agent-specific standards

Nothing from a standards body was found published for agents (**E**, **S**). NIST's control overlays for single
and multi-agent systems are listed and unpublished, and its agent security guidelines are upcoming (**E**; **C**
from 10.05 §8.3). ETSI opened a work item for agentic baseline requirements on 1 October 2026 (**E**). Outside the
standards bodies there are AIUC-1, a certification standard for agents with six principle areas (**E**), Singapore's
Model AI Governance Framework for Agentic AI of January 2026 (**E**), and OWASP's donated ACS (§3.4). None was
opened. The Five Eyes guidance the 10.05 assessment reads (§8.5) remains the government text nearest to the
records.

---

## 4. Aggregate catalogues

### 4.1 NIST SP 800-53 Rev. 5.2.0, by family

The catalogue was read from NIST's machine-readable file (**O**; 20 families, 324 base control entries). The corpus
has no mapping to it. What follows is **a reading at the level of the family, from the corpus's own derived
documents. No control was assessed**, and "deep" is not "conforms". Deep: the family's central controls have a
mechanism in a record in force, with a proved or checked property. Partial: some do. Thin: little. Silent: no record
addresses the family.

| Family | Reading | What TOPAK has | What it lacks at this tree | Findings |
|---|---|---|---|---|
| AC Access Control | Deep | The admit path as reference monitor (AC-25: "tamperproof, always invoked, and small enough to be subject to analysis"); least privilege by typed alphabet and round-bound lease (AC-6); seats and recusal (AC-5); labels (AC-4); unanimous promotion, beyond AC-3(2) dual authorization | "the first lease still comes from a socket" (residual 1.4). The audited override is a quorum seating (AC-3(10)) | SF-8, SF-10, SF-24 |
| AT Awareness and Training | Silent | Nothing; MAP 3.4 is a gap | Proficiency of operators and release seats | SF-15 |
| AU Audit and Accountability | Deep | Every admit, denial and stop ordered and attributed; six forensic classes survive erasure (ADR-0028); a principal writes nothing to the record (ADR-0020) | No archive; erasure unbuilt; gate evidence unsigned (residual 1.12, 1.4) | — |
| CA Assessment, Authorization, Monitoring | Thin | A reviewer's guide; the corpus's own reviews | Independent assessors (CA-2(1)): none engaged. Penetration and red-team exercises (CA-8, CA-8(2)): none | — |
| CM Configuration Management | Partial | Change control by unanimous quorum bound to a digest (CM-3, CM-5); a closed alphabet (CM-7); signed bundles (CM-14), under a throwaway key | Staged reach; retirement; "no SLOs, canaries, flags" | SF-6 |
| CP Contingency Planning | Thin | Fail closed and stall (CP-12 in part); an emergency seating, drilled (CP-4 in part) | Continuity "is out of scope" (10.09 §2.6). A crashed round loses its work. No alternative mechanism (CP-13) | SF-1, SF-2, SF-3, SF-16 |
| IA Identification and Authentication | Partial | One key per seat; the lease as the only credential; operators with providers (ADR-0050, provisional) | Replicas unauthenticated (residual 1.7); one root only | — |
| IR Incident Response | Thin | Fence, revocation, quarantine (MANAGE 2.3, M); `SECURITY.md` | "A stall replaces escalation, and nothing alerts a person" (feature list §14 item 17). No reporting (IR-6) | SF-14 |
| MA Maintenance | Silent | — | — | — |
| MP Media Protection | Silent | Erasure by topic is adjacent (ADR-0003, ADR-0006) | — | — |
| PE Physical and Environmental | Silent | — | — | — |
| PL Planning | Partial | The architecture is the corpus (PL-8) | "no deployment declaration has been written" (10.09 §1.1) | — |
| PM Program Management | Silent | — | — | — |
| PS Personnel Security | Silent | — | — | — |
| PT PII Processing and Transparency | Thin | Erasure machinery, "no privacy framing" (MEASURE 2.10, C) | Notice, consent; ADR-0056 §10 leaves a subject's consent out | — |
| RA Risk Assessment | Partial | Thirty-seven trusted-base rows with residuals (ADR-0045); a residual-risk statement; a threat model (ADR-0068, Proposed) | Impacts on people; a deployment's assessment | SF-26 |
| SA System and Services Acquisition | Deep | A formal policy model with proofs (SA-17(1)); the design principles of §4.2 | SA-17(3)(d), that the specification "is an accurate description of the implemented" system: no refinement to code (T-0045-28) | SF-21 |
| SC System and Communications Protection | Partial | Security function isolation (SC-3); fail in a known state (SC-24), proved; isolation rungs (ADR-0034) | No principal is `Contained`. Transport is "unauthenticated JSON over plain TCP". Heterogeneity for Observers only (SC-29) | SF-7 |
| SI System and Information Integrity | Partial | Coupled Observers, designed and unbuilt (SI-4); digests, pins and manifests (SI-7); typed inputs (SI-10) | Function verification after a restart (SI-6); ranges and formats, "not decided here" (ADR-0049 §3) | SF-4, SF-5, SF-9, SF-13 |
| SR Supply Chain Risk Management | Thin | Components as rows; pinned tools; a model provider is a row | "no SBOM, no reproducible build declared"; a throwaway signing key (feature list §14 item 21) | — |

**Tally of the reading.** Deep 3 (AC, AU, SA); partial 6 (CM, IA, PL, RA, SC, SI); thin 5 (CA, CP, IR, PT, SR);
silent 6 (AT, MA, MP, PE, PM, PS).

**Where the findings land.** Seventeen findings have a home family; each is listed once above. Four are in a deep
family (AC 3, SA 1), seven in a partial one (SI 4, CM 1, SC 1, RA 1), and six in a thin or silent one (CP 4, IR 1,
AT 1). Nine have no home in the catalogue (SF-11, 12, 17, 18, 19, 20, 22, 23, 25).

**The catalogue's own crosswalk for agents does not exist yet.** NIST's overlays for agent systems are unpublished
(§3.7), so a control-level reading would be premature.

### 4.2 The design principles TOPAK is a worked example of

SP 800-53 SA-8 lists thirty-three engineering principles as enhancements (**O**). Several read as descriptions of
records in force:

| Principle | Text **O** | In TOPAK |
|---|---|---|
| SA-8(15) Predicate Permission | "requiring multiple authorized entities to provide consent before a highly critical operation"; "no single accident, deception, or breach of trust is sufficient" | Promotion by unanimous quorum (ADR-0024) |
| SA-8(23) Secure Defaults | Title only | The resident default-deny floor (ADR-0012, ADR-0030) |
| SA-8(24) Secure Failure and Recovery | "neither a failure in a system function or mechanism nor any recovery action in response to failure leads to a violation of security policy" | "every failure lands on deny or stall" (principle P2) |
| SA-8(14) Least Privilege; SA-8(13) Minimized Security Elements | Titles only | Typed alphabets; the floor as the verified object (ADR-0010) |

And three name what the findings found missing:

| Principle | Text **O** | Finding |
|---|---|---|
| SA-8(2) Least Common Mechanism | "Every shared mechanism (especially a mechanism involving shared variables) represents a potential information path" | SF-7: Therac-25's interlocks shared variables with the code they checked |
| SA-8(27) Human Factored Security | Enforcement mechanisms "provide the user with meaningful, clear, and relevant feedback and warnings" | SF-15: what a person at a release seat is shown |
| SA-8(17) Secure Distributed Composition | "the composition of distributed components that enforce the same system security policy result in a system that enforces that policy at least as well as the individual components do" | The modules are proved one at a time, and the inventory's counterfactuals combine their actions |

SA-8(24) deserves a second look. It is satisfied by TOPAK's direction of failure, and it is silent on SF-1: a
failure that violates no policy can still stop a process someone depends on. The catalogue puts that under
contingency planning, which is the family where TOPAK is thin.

### 4.3 SP 800-160 Vol. 2 Rev. 1

It "identifies 14 cyber resiliency techniques and 50 cyber resiliency implementation approaches" (**O**). Read
against the records and the findings:

- **Privilege Restriction, Non-Persistence, Substantiated Integrity.** In force. Non-Persistence, "Generate and
  retain resources as needed or for a limited time", is the round-bound lease.
- **Analytic Monitoring.** Designed, coupled, and not built.
- **Diversity, Redundancy, Segmentation, Coordinated Protection.** SF-7, SF-3, SF-2 and SF-1 respectively.
- **Adaptive Response, Dynamic Positioning, Deception, Unpredictability, Contextual Awareness, Realignment.** No
  record addresses them. SF-17's `RepeatedPairing`, watchers assigned from a pool, would be the first use of
  Unpredictability.

### 4.4 The catalogues not read

None of these was opened, and the corpus maps to none:

| Catalogue | What it is, as extracted **E** | Route to a mapping |
|---|---|---|
| ISO/IEC 27001:2022 Annex A | 5.3 Segregation of duties; 5.29 and 5.30 on disruption and continuity; 8.14 Redundancy; 8.16 Monitoring; 8.32 Change management (**S**) | The SP 800-53 reading, through published crosswalks |
| CSA AI Controls Matrix v1.1 | 247 control objectives in 18 domains, mapped to ISO/IEC 42001, the AI RMF and AI 600-1, the EU AI Act, BSI AIC4 and AIUC-1. No agent domain | The Playbook marks, through its AI RMF mapping |
| HITRUST CSF v11.9 | A harmonised framework with an AI security assessment of 44 requirement statements and a separate AI risk management assessment | Not attempted |
| Secure Controls Framework 2026.3 | 34 domains, one of them "Artificial Intelligence & Autonomous Technologies" | Not attempted |
| CIS Controls v8.1 | Companion guides for AI agents and for MCP, issued April 2026, which map existing Controls and add none | Not attempted |

Because these catalogues are themselves crosswalked to the AI RMF or to ISO/IEC 42001, the cheapest honest mapping
goes through the 72 Playbook marks the corpus already keeps, and not through a fresh reading of each.

---

## 5. Where TOPAK and the findings go beyond the texts read

**A qualification first.** The 10.05 assessment (§8.5) concluded that across the AI and agent texts it read,
"separation of duties between the author of a policy and its approver is stated nowhere", and that no text asks
"which human, how many, or what bounds them". That holds of those texts. The general catalogue, which it did not
read, does ask: SP 800-53 CM-3 requires that proposed changes be reviewed and approved or disapproved, AC-5 is
"Separation of Duties", AC-3(2) is "Dual Authorization", CM-5 restricts who may change the system, and SA-8(15)
asks for consent from "multiple authorized entities" (all **O**). An external draft should not say that nobody
asks the question. What it can say is narrower, and still true as far as this reading reaches:

1. **A quorum rule that cannot change itself**, with votes bound to the artifact's digest, the author recused, and
   a proof that no path grants without it (ADR-0024; `P1_Unanimity`). The catalogue leaves the number and the
   binding to the organization.
2. **Monotone authority.** Findings subtract and never add (ADR-0007, ADR-0038 §5). The Five Eyes guidance lowers
   trust on anomaly and does not say whether it may rise (**C**). This reading found no text that forbids it.
3. **The agent as adversary by premise.** TACIP's scope is "a legitimate, uncompromised AI system that is not
   behaving as intended" (**C**). Only the research of §3.5 starts where TOPAK does.
4. **The model outside the trusted base, with the base enumerated row by row**, and a verifier's known defects
   recorded against its row (ADR-0045, ADR-0046 A2). The alignment's reverse deltas (§1.11) stand.
5. **Liveness as a stated property.** The texts say "fails safely". None distinguishes a stall that is safe from
   a stall that ends.
6. **The five findings of §1.4.** They ask questions no text read asks.

---

## 6. What follows

Suggested, none made. Each is for whoever dispositions the inventory.

1. **Cite the published requirement beside each finding.** For the twelve stated findings the wording exists. A
   successor to FINDINGS_TOPAK.md could carry one line per finding from §1. It would also change how the findings
   read to an outside reviewer: twelve of them say that TOPAK has not yet done what a neighbouring field requires,
   which is a different claim from having discovered something.
2. **Borrow vocabulary before proposing modules.**
   - SF-1 and SF-16: a safe state defined of the thing controlled, and ISO 26262's "safe state or emergency
     operation", for the column SF-1 suggests in ADR-0045 and the field the 10.05 assessment already found missing
     in ADR-0023.
   - SF-5: TOP-010-1(i) R4's sentence as `MonitorOfMonitor`'s property, and SI-6's transitional states for a
     repaired Observer.
   - SF-6: RTS 6 Article 8's four limits as the fields of a promotion's reach.
   - SF-7: common cause and Diversity as the terms; Recommendation 3's "physically and electrically separate" as
     the interlock mutation's negation.
   - SF-24: AC-3(10)'s two parameters, the conditions and the roles, as the shape of a prepared excursion.
3. **Put the modelling effort where the texts are silent.** SF-12, SF-17, SF-18, SF-19 and SF-23.
4. **SF-26 has texts behind it.** The decision is the custodian's. The AI RMF's MAP 5, ISO/IEC 42001's A.5 and
   A.8.3 as NIST maps them, and Articles 27, 85 and 86 of the EU AI Act all ask for what the scope line excludes.
5. **A control evaluation of the reference.** It is the corpus's own listed exposure, and §3.5 gives the method.
6. **Mapping debts, in order of cost.** ISO/IEC 42001 through NIST's crosswalk from the existing marks; an
   article table of the EU AI Act for an adopter, against the December 2027 date; SP 800-53 at control level once
   NIST publishes its agent overlays; OWASP's 2026 LLM edition and ACS, unread here.
7. **Qualify the 10.05 sentence** before any external draft (§5).
8. **A hazard analysis of TOPAK itself** (§2), of which the scenario inventory is the analogue and not the
   substitute.

---

## 7. Method and limits

- **TOPAK's side.** Every record clause quoted was opened at `981bc77`. The alignment's marks, the Playbook
  wording it abridges, the TACIP clauses, the OWASP agentic mapping, the Five Eyes table and the IBM comparison are
  carried from the 10.05 and 10.09 documents, which read them from primary text. They were not re-read, and the
  marks are those documents' and are at G11, not at this tree.
- **Opened for this document**, with the first sixteen digits of each file's SHA-256:
  - NIST SP 800-53 Rev. 5.2.0, the OSCAL catalogue, last modified 2026-10-22 (`64ca6b4161de51ab`). Every control
    statement and discussion quoted was read from it.
  - NIST AI 100-1, the AI RMF 1.0 (`7576edb531d98488`); NIST AI 600-1 (`6e73620ab6b64e90`); NIST SP 800-160 Vol. 2
    Rev. 1 (`d3e9830faadfd1e7`); NIST's AI RMF to ISO/IEC FDIS 42001 crosswalk (`170efdf7be08a988`).
  - NERC TOP-010-1(i) (`b62bb846a7b365ed`).
  - OWASP's LLM Top 10 list page, its LLM06:2025 page, the agentic list's resource page and the announcement of
    1 September 2026, as served on 2026-11-12.
  - arXiv abstracts 2312.06942 (and its body, v5), 2504.10374, 2604.15384 and 2402.07510.
- **Not opened.**
  - EUR-Lex returned an empty response (HTTP 202) to an automated client, and ISO's site refused one (HTTP 403).
    Neither was worked around.
  - The STPA handbook's own host failed certificate verification.
  - IEC, RTCA, SAE and UL texts are sold.
  - For all of these, four reader agents returned sixty-seven checks from search extracts. Every one is marked
    **E** or **S** here, and none is treated as compared with its text.
- **An extract can be wrong.** One was: an extract gave the LinuxArena result as 34%, and the abstract, opened,
  says "roughly a 23%". Every **E** and **S** above carries that risk. The clause numbers of IEC 61511-1 are the
  most exposed, since two editions number them differently.
- **Not checked.** Whether Regulation (EU) 2026/1744 changed the articles tabled in §3.3. The agentic list's PDF.
  The 2026 order of OWASP's LLM list. Any clause of ISO/IEC 42001, 27001, 26262, 21448 or 14971 beyond a title or
  a definition. The frontier frameworks. Whether a later edition of any text exists than the one named.
- **Scope of "not found".** It means not found in the texts listed here. Sector law outside the scenarios' own
  rules, human-factors standards and national guidance were not searched.
- **Counts.** Findings by relation and by family are this document's reading. The family reading of §4.1 rests on
  the corpus's derived documents and assesses no control.
- **Not done.** No mark of the alignment was re-made, no record was edited, and no mapping to any catalogue was
  written.
- **Not independent.** See the head of this document.

## Sources

- `derived/scenarios-2026.11.12/FINDINGS_TOPAK.md`, `README.md` and the 45 entries' front matter, at `981bc77`.
- `derived/topak-external-alignment-2026.10.09.md` (Parts I, II and IV);
  `derived/topak-external-and-competitive-assessment-2026.10.05.md` §8 and §12;
  `derived/topak-feature-list-2026.11.11.md` Part I and §14 to §16;
  `derived/topak-residual-risk-statement-2026.11.11.md` §0, §1 and §8.
- Records cited by number, at `981bc77`; `README.md`.
- NIST: SP 800-53 Rev. 5.2.0 (OSCAL catalogue, `usnistgov/oscal-content`); AI 100-1; AI 600-1; SP 800-160 Vol. 2
  Rev. 1; "NIST AI RMF to ISO/IEC FDIS 42001 AI Management system Crosswalk".
- NERC, TOP-010-1(i), "Real-time Reliability Monitoring and Analysis Capabilities".
- OWASP GenAI Security Project: `genai.owasp.org/llm-top-10/`; the LLM06:2025 page; "OWASP Top 10 for Agentic
  Applications for 2026" (resource page, 9 December 2025); the announcement of 1 September 2026.
- Greenblatt, Shlegeris, Sachan and Roger, "AI Control: Improving Safety Despite Intentional Subversion",
  arXiv:2312.06942. Bhatt et al., "Ctrl-Z: Controlling AI Agents via Resampling", arXiv:2504.10374. Tracy et al.,
  "LinuxArena", arXiv:2604.15384. Motwani et al., "Secret Collusion among AI Agents", arXiv:2402.07510.
- Read as extracts or at second hand, and named where used: Regulation (EU) 2024/1689 as amended by Regulation
  (EU) 2026/1744; Commission Delegated Regulation (EU) 2017/589; Regulation (EU) 2022/2554; 17 CFR 240.15c3-5;
  IEC 61508-2, -4 and -6 (2010); IEC 61511-1 (2016); IEC 62443-3-3 (2013); ISO 26262-1 and -10 (2018); ISO 21448
  (2022); ISO 14971 (2019); ISO/IEC 42001 (2023); ISO/IEC 27001 (2022); ISO/IEC TR 5469 (2024); RTCA DO-178C; SAE
  ARP4761 and J3016; UL 4600 Edition 3; the STPA Handbook (Leveson and Thomas, 2018); the Buncefield Major Incident
  Investigation Board's recommendations on design and operation (2007); MITRE ATLAS v2026.10; CSA AICM v1.1;
  HITRUST CSF v11.9; SCF 2026.3; CIS Controls v8.1 companion guides; the frontier frameworks of §3.6; AIUC-1; the
  IMDA framework; ETSI EN 304 223.
