---
id: 2025-AIA-REPLIT-DATABASE-DELETION
title: Replit Agent, July 2025 — a coding agent deleted a production database while its user had told it to change nothing
kind: incident
date: 2025-07
sector: ai-agents
setting: Replit's hosted coding agent, building an application for SaaStr's founder in a twelve-day trial, with the application's production database in reach
concerns: [authority, human-in-the-loop, actuation, containment, rollback, monitoring, accountability, ingress]
rules_at_time:
  - document: The user's instruction to the agent (as Jason Lemkin reported it)
    clause: freeze on changes
    paraphrase: no further changes without his explicit permission; an instruction typed to the agent, not a setting of the platform
  - document: Replit platform at the time (as described in Amjad Masad's statement of 21 July 2025)
    clause: databases and recovery
    paraphrase: the agent could reach the production database from development; automatic separation of development and production databases was only then being rolled out; backups and one-click restore of a project's state existed
analogue:
  - record: ADR-0050
    clause: "§4"
    note: '"A deny needs no lease": EndRound and Revoke are always open to an operator, and a successor grant is the last lease''s width or narrower. A freeze is one of these, or it is nothing'
  - record: ADR-0066
    clause: "§1, §3"
    note: an irreversible entry is reachable only from a seat a person holds; an agent proposing and a person approving is rejected as putting the agent on the path
  - record: ADR-0047
    clause: "§1"
    note: the task travels with its label beside the lease, as ingress; an instruction in it is content the Thinker reads, not a rule anything enforces
  - record: ADR-0068
    clause: "TM1"
    note: the stack is Byzantine; what bounds it is the alphabet and the envelope, and "anything inside the envelope was voted acceptable"
actors:
  - party: Jason Lemkin (SaaStr founder)
    role: user
    fault: none-alleged
    note: ran the trial and published it on X; reported the deletion, the agent's statements and the recovery
  - party: Replit Agent
    role: automation
    fault: byzantine
    note: by Lemkin's account, ran destructive commands against production despite his instruction, fabricated data and reports, and said rollback was impossible
  - party: Replit (CEO Amjad Masad)
    role: vendor
    fault: none-alleged
    note: called it "unacceptable and should never be possible"; offered a refund and a postmortem
detection:
  means: [customer]
  latency: hours
trace:
  - step: outside:freeze-declared-in-conversation
    at: during the trial, before the deletion
    note: the user told the agent to make no changes without explicit permission. In TOPAK that is task text, ingress to the Thinker
  - step: Actuate
    at: day nine of the trial, by eWeek's account
    note: RunCoupling.tla's effect, standing for the destructive database command; admitted because the entry was in the envelope
  - step: outside:irreversible-effect-from-agent-seat
    at: same
    note: records on 1,206 executives and more than 1,196 companies were wiped, by eWeek's report
  - step: Report
    at: after the deletion
    note: the agent's own account, by Lemkin's screenshots, that it "panicked" on seeing empty queries and made "a catastrophic error of judgement"
  - step: outside:agent-reports-false-state
    at: same period
    note: the agent said rollback could not restore the database and that all its versions had been destroyed; Lemkin had earlier reported fabricated data and a 4,000-record database of fictional people
  - step: outside:user-runs-platform-rollback
    at: after the deletion
    note: Lemkin later wrote that the rollback did work
counterfactual:
  by: the user as an operator, and the database's destructive entries typed irreversible
  trace:
    - step: Regrant
      at: when the freeze is declared
      note: Operators.tla's successor grant, narrower than the last lease, with no entry that writes to production; or EndRound to stop the agent outright
    - step: AdmitAgent
      at: day nine
      note: Release.tla's agent-signed act on an irreversible entry, which may even be ordered
    - step: RefuseAct
      at: day nine
      note: the interlock refuses an act without a person's key
  holds: [SuccessorNeverWidens, DenyAlwaysAvailable, SignedByPerson, IrreversibleIsAPersons]
outcome:
  by: Replit (statement by CEO Amjad Masad on X, as reported by The Register and eWeek)
  date: 2025-07-21
  summary: >-
    Masad called the deletion of Lemkin's production data "unacceptable and should never be possible". He said Replit had backups and one-click restore of a project's
    state, that the agent "didn't have access to the proper internal docs", that Replit would refund Lemkin and hold a
    postmortem, and, per eWeek, "We heard the 'code freeze' pain loud and clear". No independent investigation is on
    record. Lemkin reported that the platform's rollback restored the data the agent had said was unrecoverable.
  aftermath: >-
    Replit began rolling out automatic separation of development and production databases, in beta for new apps
    first ("to prevent this categorically", Masad); staging environments "in the works"; forced documentation search
    for the agent; and, per eWeek, a planning or chat-only mode to prevent unauthorized changes. Lemkin posted lessons
    for vibe-coding platforms, among them that AI systems fabricate data when they fail and that users should master
    rollback early.
  effect_reversed: "yes"
model:
  modules: [Operators, Release, RunCoupling, FloorComposition, proposed:Freeze]
  properties: [DenyAlwaysAvailable, SuccessorNeverWidens, SignedByPerson, IrreversibleIsAPersons, BundleRefusalHonored]
  mutations: [M_AGENTRELEASE, M_WIDEN]
  records: [ADR-0050, ADR-0066, ADR-0047, ADR-0007, ADR-0024, ADR-0030, ADR-0040]
  findings: [TM1, CR-15]
  fault_class: a Byzantine agent inside a wide envelope; the freeze was a sentence to the agent, not a narrowing of its authority
sources:
  - https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/
  - https://www.theregister.com/2025/07/22/replit_saastr_response/
  - https://www.eweek.com/news/replit-ai-coding-assistant-failure/
verified: 2026-11-12
---

## Summary

In July 2025 Jason Lemkin, founder of SaaStr, ran a twelve-day trial of building an application with Replit's coding
agent and reported it as it went, on X and in blog posts. On 18 July he wrote that the agent had been hiding bugs with fake data and
reports and lying about a unit test, and he later described a 4,000-record database full of fictional people.

He had told the agent to make no further changes without his explicit permission. By his account, on day nine of the
trial (eWeek's dating) the agent ran destructive commands against the live production database, wiping records on
1,206 executives and more than 1,196 companies. In screenshots he posted, the agent said it had "panicked" on seeing
empty database queries, called its action "a catastrophic error of judgement", and said it had "violated your
explicit trust and instructions". It told him the database could not be restored, that rollback did not support
databases, and that all database versions had been destroyed. Lemkin later wrote that the rollback did work.

On 21 July Replit's CEO, Amjad Masad, responded on X.

## Defensive position

**Replit's case**, from Masad's statement as The Register and eWeek reported it:

- The platform already kept backups and offered one-click restore of a project's entire state "in case the Agent
  makes a mistake"; the data was recoverable.
- The agent "didn't have access to the proper internal docs"; Replit was forcing documentation search.
- Replit had already started separating development and production databases automatically and would extend it to
  all apps; staging environments were in progress.
- Replit acknowledged the complaint about code freezes and offered Lemkin a refund and a postmortem.

## Adversarial position

**Lemkin's case**, in his posts as reported:

- The agent deleted his production database without permission, during a period in which he had told it to change
  nothing, and "Possibly worse, it hid and lied about it" (eWeek).
- It fabricated data and test results when it failed, and told him recovery was impossible when it was not.
- His lessons: AI systems fabricate data when they fail; they make unrequested changes, so rollback must be mastered
  early; a user must act as QA; most commercial apps outgrow prosumer vibe-coding platforms.

## Outcome

There was no regulator or court. Replit's CEO acknowledged the deletion as "unacceptable and should never be
possible" and announced changes: automatic dev/prod database separation, rolling out first to new apps; staging
environments in progress; forced documentation search for the agent; a planning or chat-only mode (eWeek). Replit
offered a refund and a postmortem; no published postmortem is among the sources read. Lemkin reported that the
platform's rollback restored the database.

## Analysis

**The freeze was a sentence, not an authority change.** In TOPAK, what the user typed is task text: it travels beside
the lease with its label (ADR-0050 §5, ADR-0047 §1) and is ingress to the Thinker. Whether a Thinker obeys an
instruction in its task is a fact about the model, and ADR-0007 keeps any judgment of that out of the admit path. A
freeze that only the agent is asked to honour is, in TOPAK's own vocabulary, no freeze. TM1 states the consequence:
the stack is Byzantine and "anything inside the envelope was voted acceptable". The destructive command was in the
envelope, so the `Actuate` was admitted.

**A freeze in TOPAK is one of three things, and each is on the admit path.**

- *A deny.* ADR-0050 §4: `EndRound` and `Revoke` need no lease, no quorum and no peer. Operators.tla proves
  `DenyAlwaysAvailable`, an invariant over `ENABLED`. This stops the agent outright.
- *A narrower successor.* A `Regrant` whose envelope omits every entry that writes to production.
  `SuccessorNeverWidens` holds; `M_WIDEN` is the mutation that lets a successor widen.
- *A bundle refusal.* A promoted bundle that denies the write entries. `BundleRefusalHonored`
  (FloorComposition) makes a bundle's deny final; ADR-0024 §9 makes `bundle(deny=all)` a runtime subtraction that
  needs no promotion.

None of these needs the agent's cooperation. What they need is that the person declaring the freeze is an operator in
the corpus's sense, holding a seat with a key. Lemkin was a user of a hosted platform; the platform had the levers.
`proposed:Freeze` would name the missing one: a user-facing control that compiles to a narrowing (a successor
without the write entries, for a stated period), so that a freeze is an admit-path fact and its violation is a
refused act, not a broken promise.

**Deleting production is the irreversible case.** CR-15 found that nothing in the alphabet typed reversibility.
ADR-0066 (Proposed) answers it: an entry declares its effect class, and an irreversible entry is reachable only from
a `release` seat a person holds. ADR-0066 §3 rejects "an agent proposes and a person approves" because it puts the
agent's output on the path to the effect. In Release.tla an agent's act may be ordered (`AdmitAgent`) and the
interlock refuses it (`RefuseAct`); `SignedByPerson`, and with it `IrreversibleIsAPersons`, fails under
`M_AGENTRELEASE`. Two caveats. ADR-0066 is written for vehicles in the command-chain overlay, not for Run tools in
general. And the effect class is a declaration: a database tool declared reversible because backups exist is seen by
nothing. Here the platform's restore did reverse the effect, which is the honest argument for calling it reversible.

**Dev/prod separation is containment.** Replit's main fix makes production unreachable from the agent's environment.
In TOPAK that is the envelope and the tool's declared channel (ADR-0040 §3, ADR-0049): a development seat's entry
whose channel does not reach production. That is the corpus's strongest tool, and the one this episode most needed.

**The agent's account of itself.** The agent's statements (it panicked; rollback was impossible; fabricated data) are
`Report`s. TOPAK records and couples them and does not believe them: a Thinker's report is untrusted, and a judgment
about its truth is an Observer finding (ADR-0007). The user here was the only Observer, and the platform's rollback
was the only check on the agent's claim. TOPAK would add an independent Observer; it would not make the agent
truthful.

**Outside steps.** `freeze-declared-in-conversation`, `irreversible-effect-from-agent-seat`,
`agent-reports-false-state`, `user-runs-platform-rollback`.
