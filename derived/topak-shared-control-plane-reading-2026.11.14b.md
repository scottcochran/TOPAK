# A shared control plane fails together: follow-up, after the officials' account

**2026.11.14** · derived · a follow-up note, not a record · basis: the tree at commit `7f0e765`, which is `bb76b46`
with `topak-shared-control-plane-reading-2026.11.14.md` added; that document; and press coverage of 2026.11.14, found
by web search · one further suggested entry for the open-findings register, none made · nothing was changed in the
tree but this file and the index · prepared by the assistant at the custodian's request

Nothing here is ratified, and this note proposes no decision text. The first document is frozen and is not edited.
This note says where the reporting has moved under it, what that does to its three entries, and adds a fourth.

**Not independent**, as the first document says of itself.

**The reporting is still not evidence.** No post-mortem is published. What follows is officials' statements as the
press carried them a day after the event, some through unnamed sources, and it may move again.

---

## 1. What is now reported

| | The first document's source (a Gemini conversation of 2026.11.13) | Officials' account, as reported 2026.11.14 |
|---|---|---|
| Trigger | A software or configuration update pushed to a node, a reboot and a crash | A contractor's crew moving a remote site from copper to fiber and replacing a router. The replaced router began flooding other routers |
| Mechanism | Bad routing state propagated to every peer; traffic drawn to one link | A flood of connection attempts, put at more than 1,000 every four to five seconds, overloading other routers |
| Diagnosis | Not discussed | The source of the instability was not found for about 45 minutes, and departures were then halted as a precaution |
| Mitigation | Roll back the update and let routing converge | The function at fault disabled on about 60 routers of the same type nationwide; further testing |
| Open | The routing protocol | Whether the router was defective, or installed or configured wrongly |
| Precedent | A 2009 outage from a dormant routing-table error at an upgrade | A 2009 outage from a router misconfigured during a move to fiber, by an inspector general's review |

Less firm: one outlet, on unnamed sources, limits the problem to one vendor's routers made between 2001 and 2006
and says its sources disagree on the cause. The origin at Chicago Midway comes through secondary outlets, and the
officials' account as carried says a remote site. Officials say there is no sign of an attack.

## 2. What it does to the first document

The first document said its entries "stand or fall on the lines of the tree they cite". They stand. Its §1 does
not all stand, and one sentence of its §3 is now wrong about the source.

| First document | As it reads | Now |
|---|---|---|
| §1, S2: control, data and administration in-band; load on one starves the others | The source's claim | **Supported, and sharper.** One participant's flood on a shared path is what officials describe |
| §1, S3: an update pushed with no staging | The source's claim | **Not supported.** No pushed update is reported. A change was made at one site, by hand, and its effect was not contained. The general point, that a change at one place reached every place, survives; "unstaged rollout" does not describe this event |
| §1, S4: recovery as a load | The source's claim | **Neither.** The reporting says nothing about how service came back |
| §3, E1 | Medium | **Stands, and is the entry the event bears on.** See §3 below |
| §3, E2, "Why it ranks first of the three": "S3 is the source's root cause" | The reason given for ranking E2 first | **The reason is withdrawn.** E2 is still true of the tree, on the lines it cites. It no longer has this event as its outside example, and its rank is the custodian's to set without it |
| §3, E3 | Medium, partly addressed | **Unchanged.** The event neither supports nor weakens it |
| §4, S1 at the replica set, not made an entry | A row "would restate" A9 and E2 | **Unchanged, with a note.** The mitigation was applied to every router of one type at once, which is the common-mode case. It is still E2's subject |

**On E1.** The first document found that every kind of entry shares one path into the log, and listed what bounds
the load a principal can add: the round bound, denials not ordered, and the limit after a seal. The event is a case
those three do not obviously cover: a participant that floods *attempts*, not admitted entries. In the corpus's
terms that is a principal, or something that can reach the front door, sending requests that are refused. The first
document said such requests cost "the deciding replica and not the log" and that nobody has run the loop. That is
the open part, and the event says it is the part that matters.

## 3. One further suggested entry

In the register's columns, graded at `7f0e765`. Severity is the drafter's.

| Id | Statement | Against | At the pin | Carried by |
|---|---|---|---|---|
| E4 | **Nothing counts refusals.** None of the correlator's five named folds is a count of refused requests by principal, by seat or by deciding replica, and no operator view is specified that would rank who is asking most. A participant flooding refused requests is recorded one denial at a time and summed nowhere. The time to name it is unmeasured, and no document asks for the measure | ADR-0051 §2, §5; ADR-0005 §2; ADR-0015; ADR-0039 §1 | **partly addressed** | G11 item 44 and CR-7 (the order of denials only); ADR-0051 §5, Proposed (placing a denial against the log) |

### E4. Nothing counts refusals · Low-Medium

**What the tree holds.**

- A denial is recorded and not ordered: it "is written by the deciding replica, unordered, while the topic is open
  and to the `after` companion once it is sealed" (`decisions/ADR-0005.md`, §2). After a seal the records stop at a
  limit and one overflow marker (`after_topic_limit`, 64 at the reference).
- ADR-0051, Proposed, places a denial against the log: at the reference a denial record carries `at`, "the log index
  the deciding replica had applied, and `decided_by`". So a reader can say roughly when a refusal happened and which
  replica made it.
- The five correlations are `carried-label`, `shared-ingress`, `probe-then-use`, `marked-past` and `distance-drift`
  (`decisions/ADR-0051.md`, §2). `probe-then-use` reads refusals, to find a call admitted where others were refused.
  It is about which entry, not how many.
- Coupling counts the other direction. `seq − mark < K` bounds what a Thinker has emitted unread (ADR-0039 §1). It
  is a count of effects admitted, and a refused request does not move it.

**What it does not hold.**

- A count. No fold, no floor value and no reference metric is a number of refusals over a window for a principal, a
  seat, a cell or a replica.
- A threshold or a consequence. Nothing says that a principal refused some number of times is reported, slowed or
  has its round ended. Every Observer output "is a denial or a trigger for one" (ToO §5.1), so the instrument
  exists; no input of this kind reaches it.
- Where a refusal goes when there is no open topic to write it on, before any seal: a request under no lease, or to
  no seat. The first document did not check this and neither does this note. It is listed as a question.
- A measure of time to attribution. The event's 45 minutes were spent finding which one of many participants was
  the source. The corpus's timing budget has `L`, the Observer's latency, "unmeasured", and `L` is about content
  read, not about volume.

**Why it is a separate entry and not part of E1.** E1 is about whether a stop is ordered while the path is loaded.
E4 is about whether anyone can tell whom to stop. An operator with a reserved lane and no name to put in the
revocation has a fence and nothing narrower, and the fence is E3's subject.

**Why it is only Low-Medium.** A refused request is refused. The corpus's safety claims are untouched, and a
targeted revocation of the wrong principal costs a round. What is at stake is how long a deployment stays degraded,
and whether the first tool reached for is the fleet fence.

**Kinds of answer.** A sixth correlation, a count of refusals in the window by principal and by deciding replica,
which is a fold over facts and fits ADR-0051's first tier as it stands. A per-seat bound on refused requests at the
front door, as a parameter beside the round bound, with its own denial reason. A statement in ADR-0005 or ADR-0020
of what a refusal with no topic leaves. The first is a line in a Proposed record; the second touches ADR-0022 §3 and
ADR-0042 §2.

## What this does not claim

It does not claim the officials' account is final, or that E4 would have shortened the event. It does not re-grade
E1 to E3: their statuses and severities are as the first document gave them, and only the reason for E2's rank is
withdrawn. It does not claim the question under E4 about a refusal with no topic has an answer in the tree or lacks
one. Nothing was run.

## Sources

Press, opened through search summaries on 2026.11.14 and not read in full:

- NPR, "FAA blames Friday's ground stop on 'equipment issue' during telecoms network upgrade", 2026.11.14.
- Yahoo News, live coverage, "Duffy blames contractor L3Harris; thousands more flights canceled Saturday; no sign of
  cyberattack".
- CBS News, "Travelers stranded and thousands of flights canceled after FAA ground stop. Here's what we know", and
  "FAA lifts nationwide ground stop that disrupted thousands of flights".
- NBC News, "Thousands of flights canceled or delayed Saturday after FAA's nationwide ground stop".
- Scripps stations, "What caused the FAA ground stop? Officials point to router failure".
- The Air Current, "U.S. ends halt on flight departures after nationwide air traffic communications outage".

The tree at `7f0e765`: `derived/topak-shared-control-plane-reading-2026.11.14.md`; `decisions/ADR-0005.md`,
`decisions/ADR-0015.md`, `decisions/ADR-0039.md`, `decisions/ADR-0051.md`;
`mechanism/crates/topak-node/src/mechanism.rs`; `derived/topak-open-findings-register-2026.11.11.md` (rows CR-3 and
CR-7, which name G11 item 44); `narrative/theory-of-operation.md` (§5.1); `narrative/glossary.md` (the open list's
row for item 44, "Sequence numbers on denials").
