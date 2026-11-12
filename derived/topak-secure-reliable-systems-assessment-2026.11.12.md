# TOPAK read against *Building Secure and Reliable Systems* (Google, 2020)

> Assess TOPAK against the standards of this book:
> https://google.github.io/building-secure-and-reliable-systems/raw/toc.html

(The custodian's prompt of 2026.11.12.)

**2026.11.12** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
the tree at `981bc77`: Genesis Checkpoint G11 (`ce8f460`) and the ninety-eight commits after it, which carry
Batches 38 and 39, thirteen records Proposed since G11, the self review of 2026.11.11 and the scenario inventory
of 2026.11.12 · nothing in the tree changed but this file and its index row

**The book.** Heather Adkins, Betsy Beyer, Paul Blankinship, Piotr Lewandowski, Ana Oprea and Adam Stubblefield,
*Building Secure and Reliable Systems: Best Practices for Designing, Implementing, and Maintaining Systems*
(O'Reilly, 2020), read from the HTML at the address above on 2026.11.12: the preface, twenty-one chapters, the
conclusion and the appendix, 174,782 words. It is cited by chapter number and by section heading, in italics. The
forewords, the index and the figures were not read.

**Three words collide with the corpus.**

- **Breakglass.** In the book, a mechanism that goes round the authorization system when it has failed. In the
  corpus since ADR-0052, an emergency seating inside it. The difference is rows 5.5 and 14.11.
- **Fail safe.** The book uses *fail safe* for failing open and *fail secure* for failing closed. The corpus's
  "safe direction" is the book's *fail secure*.
- **C.** Here a plane, the corpus as a project (§1.1). In the corpus, a confirmation criterion (C1 to C4) and a
  floor entry. The Playbook alignment's mark *C*, convertible, is not used in this document for that reason.

**Not independent.** The reading is Claude's, of a corpus Claude's lineage drafted most of, for the custodian who
ratified it. §11 says what that leaves out.

---

## 0. In one page

The book asks for three kinds of thing: a design in which failure and attack can be survived, code and a path to
production that are disciplined, and people organized to respond. TOPAK answers the first kind and is close to
silent on the third, and the line between them runs through the middle of the design.

**Where the book says *do not*, the design is stricter than the book.** No ambient authority, no general
interface, no policy that can widen by being pushed, no security decision that fails open, no clock a safety
decision reads, no reliance on what a client intends. On these the book's standards are met by construction, with
invariants stated and proved to a depth the book calls rarely practical (chapters 3, 5, 6, 9, 13).

**Where the book asks *what then*, the design mostly has no answer.** The pattern's response to every fault is to
stop. The book treats a stop as the beginning of a list: what it costs, who can cause one on purpose, how a fix
is tried and rolled out and undone, how state is restored, who is told, who decides it is over. On that list the
pattern has the first hour (an ordered record, an immediate stop, evidence nobody can erase) and little of the
second (chapters 7, 8, 9, 10, 16, 17, 18). The scenario inventory of 2026.11.12 found the same line from
incidents; SF-1, SF-2, SF-3, SF-6 and SF-7 are the book's chapters 8 and 9 in the corpus's own words.

**The reference is graded as evidence, and holds up as that with four exceptions.** It is small, memory-safe,
tested against the mutations the specifications name, and labelled wherever it stands in for something. Reading
it against the chapters on recovery, logging and deployment found four places where it departs from the record
it follows. One was reproduced: a bundle is accepted under its signature with its contents changed (SRS-12), an
attack ADR-0044 was written to close and a gap the reference's own register strikes as retired.

**The project does every day what the pattern forbids a deployment to do**, and says so. One person is the
quorum; the author votes on the artifact; the lineage that drafts is the lineage that reviews. That much is
ADR-0029, tracked as debt. What the book adds is two things the corpus has not named. Nothing runs unless a
person runs it, so the reference's own drift test is failing on the default branch with eight merges over it
(SRS-16). And the root every digest in the corpus resolves to is unsigned (SRS-17).

### 0.1 Marks by chapter

Counts of marks in the tables of §2 to §6, by plane: **D** the design, **R** the reference, **C** the corpus as a
project (§1.1); **M** matched, **P** partial, **G** gap, **X** out of scope by declaration (§1.2). A row marks a
plane only where the standard lands on it.

| Chapter | Rows | D | R | C |
|---|---|---|---|---|
| 1. The intersection of security and reliability | 8 | M1 P5 | P4 | M2 |
| 2. Understanding adversaries | 8 | M1 P3 G1 | P2 G3 | M1 P3 G1 |
| 3. Case study: safe proxies | 9 | M3 P5 G1 | P7 G2 | G1 |
| 4. Design tradeoffs | 6 | M3 P1 G1 | P2 X1 | M2 P1 G1 |
| 5. Design for least privilege | 16 | M6 P8 G2 | P11 G4 | P5 G2 |
| 6. Design for understandability | 10 | M2 P8 | P7 G3 | P5 G2 |
| 7. Design for a changing landscape | 13 | M2 P7 G4 | P7 G3 X3 | P8 G3 |
| 8. Design for resilience | 13 | M2 P8 G3 | M2 P8 G3 | P4 G4 |
| 9. Design for recovery | 10 | M1 P8 G1 | P6 G4 | M2 P3 G2 |
| 10. Mitigating denial-of-service attacks | 6 | P3 G3 | P3 G3 | P1 |
| 11. Case study: a publicly trusted certificate authority | 7 | M4 P2 | M1 P3 G3 | P3 G2 |
| 12. Writing code | 8 | M5 P2 | P8 | M1 P4 G1 |
| 13. Testing code | 8 | M3 P1 | P6 G2 | M1 P1 G3 |
| 14. Deploying code | 11 | M3 P5 X2 | P6 G4 | M2 P3 G5 |
| 15. Investigating systems | 10 | M2 P5 G2 | M1 P3 G4 X1 | M2 P5 G1 |
| 16. Disaster planning | 8 | M2 P5 G1 | P3 G2 | M2 P5 G1 |
| 17. Crisis management | 9 | M1 P4 G4 | P1 | M2 P5 G1 |
| 18. Recovery and aftermath | 8 | M2 P5 G1 | P5 G3 | M2 P4 |
| 19. Case study: the Chrome security team | 5 | P4 | – | P2 X1 |
| 20. Understanding roles and responsibilities | 5 | M1 G2 X1 | – | M1 P1 G2 |
| 21. Building a culture of security and reliability | 9 | M3 P3 G1 X1 | – | M4 P2 G2 X1 |
| **All** | **187** | **M47 P92 G27 X4** | **M4 P92 G43 X5** | **M24 P65 G34 X2** |

Read down the columns. On the design, gaps cluster in chapters 7, 8, 10 and 17: change, load and response. On the
reference almost nothing is matched outright, which is what "the reference is not the mechanism" predicts, and
most of its gaps are the unbuilt parts the corpus lists itself. On the project the gaps are review, automation and
continuity, in every chapter that asks for them.

### 0.2 What is carried already, and what is new

Most of what the book exposes is on one of the corpus's lists, and each row's last column says where. §7.1 maps
the book's fifteen larger points to the identifiers that carry them. Nineteen findings are carried by no list
(`SRS-1` to `SRS-19`, §7.2 to §7.4), eleven on the design, four on the reference and four on the project, with
sixteen smaller observations beside them (§7.5). Five matter most.

| | Finding | Why first |
|---|---|---|
| 1 | **SRS-12.** The bundle signature authenticates a revision's name, and not the bytes that load | Reproduced. A record in force reads as if it were closed |
| 2 | **SRS-16.** Nothing runs unless a person runs it, and the default branch is failing its own check | Hours of work, and every other check depends on it. The 11.11 review found the symptoms; this is the cause |
| 3 | **SRS-6 and SRS-7.** A deployment that conforms to every row has no incident response, and the way back from each of five stops is open or unwritten | The pattern assumes a present, trained person (A5) and gives them nothing to work from |
| 4 | **SRS-3**, beside SF-6. A promoted change cannot be staged, tried or taken back | The design's one fast direction is down |
| 5 | **SRS-2.** Availability has no adversary | Every agent is hostile by premise, and no record asks what a hostile agent can do to a stall |

**The plain statement.** Measured against this book, TOPAK is a strong answer to the question of what an agent
may do, and an unfinished answer to the question of what people do when it has stopped one. In two places the book
asks for what a decision in force declines: a breakglass that goes round authorization, and a recorded reason for
using it (ADR-0052 §2, §5). Both are marked as decisions and not as gaps. Most of the rest of what the book asks
and the pattern lacks could be asked of a deployment in a few rows of the declaration. The corpus's own plan of
2026.11.11 is right about what comes first, a reader and a cut. This reading adds one thing to the front of it:
the checks that exist, made to run.

---

## 1. How the book applies, and how this was made

### 1.1 Three planes

The book is written for an organization that builds and operates production systems. TOPAK is a design pattern, a
reference implementation of one path through it, and a repository run by one person. A standard of the book can
land on any of three things, and a mark that does not say which is not a mark.

| Plane | What is judged | Evidence that counts |
|---|---|---|
| **D**, the design | What the pattern, as recorded, gives a conforming deployment or requires of it | A record that is Accepted (genesis), read as author-ratified (ToO A8); a provisional record counts and the row says so (A17). Proposed records and pending amendments do not count, and are named where they would move a mark |
| **R**, the reference | What is built and tested under `mechanism/`, `floor/`, `policies/`, `spec/` and `slm/` | The code, tests, scripts and results files, read or run. A document's description of code is not evidence about the code |
| **C**, the corpus as a project | How this repository is engineered and run: review, change control, testing, verification, release, the handling of findings | The tree, its history, and the repository's settings as GitHub reports them |

### 1.2 Marks

The marks are the ones the corpus uses for the Playbook (`derived/topak-external-alignment-2026.10.09.md`), on
the same basis, less one: *convertible* is not used, because its letter is a plane's here.

| Mark | Meaning |
|---|---|
| **M** | Matched: a record in force or a built mechanism discharges what the book asks |
| **P** | Partial: something exists and half the outcome is discharged |
| **G** | Gap: the book asks for it, TOPAK's own argument needs it, and it is not there |
| **X** | Out of scope, by a declaration that can be cited |
| **–** | The standard does not land on this plane |

A gap the corpus admits is still marked G. The last column of every table says where the corpus already carries
the point, by its own identifiers: `SF-n` (the scenario findings of 2026.11.12), `CR-n` (the critical reviews),
G11 items, ToO §12 items, `mechanism/` gaps and assumptions (`Gn`, `In`), design-gap rows. Where nothing carries
it, the column gives this document's identifier, `SRS-n`, and §7 has the finding.

### 1.3 Method

- **The book.** All twenty-one chapters, the conclusion and the appendix were fetched from the official site on
  2026.11.12 and converted to text (174,782 words). Standards were extracted from the text, each with the section
  heading it comes from, and not from memory of the book. The case-study chapters (3, 11, 19) yield fewer.
- **The corpus.** The tree at `981bc77`: G11 (`ce8f460`) plus ninety-eight commits, which carry Batches 38 and 39,
  thirteen records Proposed since G11 and the documents of the 2026.11.11 self review and the 2026.11.12 scenario
  inventory. Where the frozen checkpoint and a later ratified amendment disagree, the amendment was followed and
  the row says so.
- **Readers.** Chapters 3 and 5 to 18 were each read against the tree by one of five readers working from one
  brief, in five groups; each returned a report with a citation for every claim. Chapters 1, 2, 4 and 19 to 21 were
  read by the lead. The lead merged the reports, re-read the cited text behind every `SRS-n` and behind the marks a
  finding rests on, and ran the checks in §9. The other marks rest on the readers' citations.
- **Known findings first.** Before a gap was called new it was searched for in ToO §12 and §13, G11 §7 and §8,
  `mechanism/GAPS-AND-ASSUMPTIONS.md`, the 11.11 critical review and its register (460 rows), the 11.11
  residual-risk statement and the scenario findings. Most of what the book exposes is already there.

---

## 2. Part I: Introductory material

### Chapter 1. The intersection of security and reliability

The chapter's own example is a password manager whose recovery needed a smart card, in a safe, whose combination
was in the password manager. Its standards are the ones the rest of the book works out, so most rows point forward.

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 1.1 | Decide for each failure whether it fails open or closed, with an adversary present (*Reliability Versus Security: Design Considerations*) | P | P | – | The corpus has a rule and not a case-by-case choice: a component or an interval is trusted by the direction its failure takes (ADR-0045 §2; ADR-0032 §2), and the posture everywhere is "stall, not proceed" (Adopter's Guide §7). The reference keeps it on every path read but one: `K < R` is refused at startup and the lease interval errs early, except after a restart. The book's other half, that failing closed has a cost somebody must weigh, is priced nowhere in force | SF-1; ToO §10 ("fail-closed uniformity presented as costless"); SRS-13 |
| 1.2 | Weigh every redundant path against the attack surface it adds (*Tradeoff: Redundancy*) | M | P | – | Redundancy is admitted only where it subtracts: any one Observer may deny, and "More Observers never lower safety and may lower availability" (ADR-0038 §5). The second door the book warns of, an exception through the floor for break-glass, was retired for a seating held to the ordinary allowlist (ADR-0052 §2, provisional). The retirement is not carried through the reference's `rules.rs` and four other places | CR-45 |
| 1.3 | A security control must not stand between responders and recovery, and recovery must not depend on what failed (*On Passwords and Power Drills*; *Recovery*) | P | P | – | ADR-0052 §1 keeps the emergency key off single sign-on for this reason, and §6 asks for a drill in each domain in each epoch. Nothing requires the channel, the consoles or the roster's reach to survive the failure being repaired, and a path around the mechanism is out of scope (§7). At the reference no drill is counted | SF-3; residual-risk §3 (A5) |
| 1.4 | Treat confidentiality, integrity and availability each with and without an adversary (*Confidentiality, Integrity, Availability*) | P | P | – | Integrity is the design's centre: authority changes are ordered and every artifact is named by digest. Confidentiality is by label and by topic read set, and the read set is declared and not enforced at the reference (`mechanism/` I8). Availability is given up by position: the pattern does not "scale, or promise latency" (Adopter's Guide §8.1 o), and no stall is proved to end | ToO §12 items 18, 21; I8 |
| 1.5 | Design security and reliability in from the start; they are emergent and cannot be bolted on (*Reliability and Security: Commonalities*) | P | – | M | Security was designed in before any code existed, and the code was built to check the design. Reliability came second: liveness was first stated at G11, as two extension modules, and is checked and not proved | CR-37; G11 item 105 |
| 1.6 | Assess risk, and say plainly what is left (*Assessment*; *Invisibility*) | P | – | M | A residual-risk statement exists and is current to `bbda621`, ordered by severity and row by row over the trusted base. It is qualitative: every number is a placeholder, nothing is measured, and "no adversarial exercise has been run" (residual-risk §4) | CR-36 |
| 1.7 | Keep the design simple enough to assess (*Simplicity*) | → 6 | → 6 | → 6 | Chapter 6 | |
| 1.8 | Expect the system to change, and small changes to have large effects (*Evolution*) | → 7 | → 7 | → 7 | Chapter 7 | |

**Reading.** The corpus answers the chapter's question, which way a failure should fall, with more rigour than the
book asks: the direction of every trusted component's failure is a field in a table, and a component whose failure
can add authority is refused or named a trust root. What it does not do is the thing the chapter's opening story is
about. The password manager failed because a protection sat in the path of its own recovery, and nobody had asked
what the protection cost when the system was down. The scenario inventory reached the same place from forty-five
incidents (SF-1, SF-3), so this is confirmation from a second source, not a new finding.

### Chapter 2. Understanding adversaries

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 2.1 | Know who would attack you and why: profiles and motivations (*Attacker Motivations*; *Attacker Profiles*) | P | – | – | The archetype has one adversary, stated by capability: an agent that "may do anything its alphabet allows" (ToO §1; ADR-0007). Every other party enters as a trusted-base row with a failure direction and a residual (ADR-0045 Annex A), which is a threat model by component and not by actor. Only the command-chain overlay lists adversaries (ADR-0068 §1, fourteen, Proposed). The boundary register's own assessment says "no per-boundary adversary" (ToO §10), an item first listed at G1 | ToO §10; G1 ("Declarations unwritten"); SRS-1 |
| 2.2 | Design for insiders, first-party, third-party and related, malicious or mistaken (*Insiders*) | P | G | P | The design's inversion puts the Byzantine threat in Build, among the authors of policy (ToO §1), and bounds operators, key-holders and grant seats by peers, quorums and disjoint rosters (ADR-0050; ADR-0024; ADR-0026 R5). What is left is stated: "The mechanism cannot tell a person from a program holding the person's key" (ADR-0050 §1), a coalition at the anchor's threshold issues anything the rules floor allows (A3), and third parties are bounded by declaration (tool entries, ADR-0049) or by a record not in force (model lineage, ADR-0035). At the reference the insider needs no key: the operator socket is unsigned and custody is (1, 0). For the project, the insider is the custodian and the assistant together | ToO §12 items 3, 4, 17; A16; TM7 |
| 2.3 | Of the book's six controls for insider risk: least privilege, zero trust, multi-party authorization, business justification, auditing and detection, recoverability (*Designing for insider risk*) | P | P | – | Four are the pattern's spine (chapters 3 and 5). **Business justification is declined by decision**: "The reason is unknown to the mechanism, by construction" (ADR-0052 §5). **Recoverability** is the thinnest (chapter 9) | ADR-0052 finding 5; chapter 9 |
| 2.4 | Expect automated and AI-driven attackers, and make the defence resilient by default (*Automation and Artificial Intelligence*) | M | P | – | This is the premise. The book treats a self-directed machine attacker as a prediction; the corpus treats every model as one, at every position, and keeps it out of the trusted base | ADR-0007 |
| 2.5 | Study how attackers work: tactics, techniques and procedures, and current intelligence (*Attacker Methods*) | – | – | P | Done as dated one-shots and well: OWASP's agentic top ten and TACIP's incident appendix read against the mechanism (the 10.05 and 10.09 assessments), and forty-five incidents each replayed as a trace in the corpus's vocabulary (scenarios, 11.12). No kill-chain reading of the admit path itself, and no standing process: each reading is frozen on its date | CR-60 (findings have no path into the open list) |
| 2.6 | Cover the simple attacks before the exotic ones (*Risk Assessment Considerations*) | – | G | P | The corpus proves its modules' invariants in two provers while the reference's replica channel is unauthenticated, its operator socket unsigned and its keys in the clear in `dev/secrets/`. Each is declared (T-0045-1, T-0045-8; D-0050-1) and none is hidden. The order is the reverse of the book's | ToO §12 items 9, 17; residual-risk §2 |
| 2.7 | Do not assume you are not a target (*Risk Assessment Considerations*) | – | – | M | `SECURITY.md` names the corpus's own exposure exactly: a wrong safety claim is inherited by whoever builds on it, and is handled as a vulnerability | |
| 2.8 | Test against a defined adversary (*Assessment*, chapter 1; chapter 20 on Red Teams) | G | G | G | None has been run, at any plane. The mutation method is adversarial toward the specification, not toward a system | residual-risk §4; CR-36 |

**Reading.** A reader coming from this chapter will look for the page that says who the attackers are. For the
archetype there is no such page. The corpus's answer, that naming actors is unnecessary when every agent is assumed
hostile and every other party is a row with a failure direction, is a strong one for the agent and a weaker one for
people. The book's insider table (actor, motive, action, target) has a use the row table does not: it makes a
designer ask what an operator who is tired, coerced or wrong will do with a key that verifies. ADR-0068 does this
for the overlay and lists two adversaries that nothing in the design bounds (TM8, TM11). Nobody has done it for the
archetype.

---

## 3. Part II: Designing systems

### Chapter 3. Case study: safe proxies

In the book the proxy stands between administrators who are trusted and fallible, and production. In TOPAK the
admit path stands between agents assumed hostile and every effect, and the administrators reach the same mechanism
by other doors. Each row is read for both.

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 3.1 | Clients reach the target only through the proxy, and the target accepts only the proxy (*Safe Proxies in Production Environments*) | P | G | – | "A Run principal's only route to an effect is an `Actuate` admitted at the front door" (ADR-0034). The design enforces that at the client's cage, and the cage has no member: "`Contained` is still unreachable at every rung today" (ToO §2.3). The book enforces at the target. No record asks a target to refuse a caller that is not the tool host, and a person outside the mechanism is out of scope (ADR-0050 §8; ADR-0052 §7) | ToO §12 item 1; A1; G1. Target side: SRS-11 |
| 3.2 | The proxy decides each call against a policy of which roles may make which calls | M | P | – | Typed alphabets by domain and seat kind, a closed lease, a floor and a bundle that can only refuse. At the reference a lease cannot be narrowed to particular tools (I45), the bundle is a placeholder, and the floor linked is a stage not in force | I45; ToO §12 items 8, 20 |
| 3.3 | Every request is logged, refused ones included, with who and when | P | P | – | For agents, yes, by rule: "Denials are part of the record" (ADR-0020). For operators the record speaks of actions taken (ADR-0050 §6), and the reference keeps nothing of a control request refused at decide. First seatings are ordered with no author | I47 (a); SRS-8 |
| 3.4 | Changes take effect gradually, so a mistake's reach is limited | G | P | – | Counts exist per round (`R`, `K`, the bounded `after` topic). Nothing bounds the size of one act, stages a promotion, or bounds what one stop takes out | SF-6; SF-8; SF-2 |
| 3.5 | The proxy is not a single point of failure, and its dependencies are known (*pitfalls*) | P | P | – | The mechanism is replicated, the floor and genesis rules are resident, and a failed bundle engine falls back to the same revision. The chosen direction on every other failure is to stall | ToO §12 item 21 |
| 3.6 | Access configuration is secure by default, generated from templates, and tested | P | P | – | Absence denies at every level. The one document a deployment must write has a schema and a worked example in a draft guide, and no fixed format or template (Adopter's Guide §2.2). The reference's only rules generator writes the least protected configuration, one with no operator seat (`mechanism/README.md`; D-0050-1) | G10 item 64; I47 (b); G6 |
| 3.7 | The proxy acts as the client and holds no privileged role of its own | P | G | – | Inside the mechanism every admit is the principal's. Toward the target no record in force says what credential a tool presents; ADR-0056 would, and is Proposed and "has nothing behind it". At the reference the target sees the tool host | CR-51 |
| 3.8 | Production is touched only by automation, by prevalidated change, or through an audited breakglass (*Zero Touch Prod*) | M | P | G | For agents and operators this is the design: six typed operator requests and no shell, even in an emergency. "Prevalidated" rests on gate evidence an operator asserts (G8). The corpus's own agent, the assistant, works through a shell behind a permission prompt, which by the corpus's definition is `Mediated` | G8; T-0045-13; SRS-17 |
| 3.9 | A tool call names a pinned version and is governed by a per-tool policy (*Google Tool Proxy*) | M | P | – | An allowlist entry is keyed `name@digest` and re-checked on every call (ADR-0049 §2). The book's own example pins "latest" | I13; I46 |

**Reading.** The admit path is a safe proxy in the book's sense and a stricter one: it assumes its clients are
adversaries, pins what it calls by content, and re-checks every decision at its place in the log. Two things the
book's proxy has, TOPAK's does not. The book's target refuses everyone but the proxy, so the proxy cannot be walked
around; TOPAK relies on confining the client, which nothing yet does. And the book's proxy exists to audit
administrators, whereas the one class of request that leaves no trace at the reference is an administrator's failed
attempt.

### Chapter 4. Design tradeoffs

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 4.1 | State requirements explicitly, and say which are critical (*Feature Requirements*; *Nonfunctional Requirements*) | M | – | M | Every decision is a numbered clause in a record; what a deployment owes is a table of "You must" rows with what is unmet and what checks it (Adopter's Guide §3, §4); the critical set is the eighteen assumptions of use (ToO §13). Author-ratified | |
| 4.2 | State reliability requirements as objectives: availability, latency, behaviour above a load threshold (*Nonfunctional Requirements*) | G | X | – | None is stated. Scale and latency are declined by position (ADR-0033 §6; Adopter's Guide §8.1 o), which discharges the reference. For the design it does not: the pattern's answer to every fault is a stall, and how long a stall a deployment may accept, per effect class, is a number with no field. `T_irrev` has a form and no declared value for any class (§6.6) | SF-1; CR-36; ToO §12 item 21 |
| 4.3 | A design document answers for scaling, data loss and restore, dependencies that are down or circular, corruption, and worst-case attack (*Example: Google Design Document*) | P | – | P | Dependencies and worst case are answered better than the template asks: every boundary has a "when the check cannot run" entry (Adopter's Guide §5), and every trusted component a failure direction and a residual (ADR-0045 Annex A). Scaling, and the loss or corruption of the log, are not: the log grows without bound, no record says what a snapshot must preserve, no record supplies the archive, and re-genesis migration is left to the deployment (§7.12, §7.13, §5.13). The record form has no standing prompt for any of these (Context, Decision, Options considered, Consequences, Open obligations) | design-gap 1.10, 1.11; G17; chapter 9 |
| 4.4 | Make tradeoffs on purpose, and write down what was given up (*Balancing Requirements*) | M | – | M | Every record has an "Options considered" table with dispositions; the Adopter's Guide separates fifteen *positions* (trades made on purpose) from open design (§8); a deployment's departures from the archetype are declared as degeneracies with the theorems each one voids (ADR-0023) | |
| 4.5 | Prefer a framework that takes responsibility for a security property over asking each application to get it right (*Managing Tensions and Aligning Goals*) | M | P | – | This is the pattern's shape. The mechanism holds the invariants and an agent cannot opt out: "Semantic judgment is never a lift" (ADR-0007), and a Thinker's own defences earn nothing (ADR-0047 §6). At the reference the framework can be walked around, since no principal is confined | ToO §12 item 1 |
| 4.6 | Do not buy initial velocity with sustained velocity: pay early for automated tests, a reliable pipeline, and exercised rollout and rollback (*Initial Velocity Versus Sustained Velocity*) | – | P | G | The corpus paid early, and heavily, for specification, proof and digest discipline, which the book does not ask for. It did not pay for the thing the book does ask for. There is no pipeline: no check runs on any change (chapter 14), every checker is run by hand, and since G11 mostly not run. The last review's verdict is the book's sentence in other words: "the corpus can now be extended faster than it can be kept true" | CR-61; CR-41; CR-57; SRS-16 |

**Reading.** The chapter's argument is that security and reliability are emergent, so they must be designed in
together and early, and that the team which skips the early investment is slower by its third release. The corpus is
the rare project that took the first half of that to its limit: there is no feature here that is not a security
decision. The second half caught it anyway, from the other side. The investment that was skipped is the cheap one
(a pipeline that runs the checks that already exist), and the cost showed up where the book says it would, as a
state of record seventy-one commits behind its tree at the last review, and further now.

### Chapter 5. Design for least privilege

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 5.1 | No actor, person or machine, holds ambient authority (*Least Privilege*; *Zero Touch*) | M | P | P | The lease is a closed credential for one round: a capability that is not a field is not carried, renewal only narrows, and a bundle cannot add. At the reference the operator socket is ambient authority for whoever can open the file, an agent's session is a bearer token, and tools run with the node's own OS authority. In the project the custodian holds every authority | G5; I14; I47 (a); G4 |
| 5.2 | Network position grants nothing; access rests on user and device credentials (*Zero Trust Networking*) | P | G | – | Operators are authenticated by key and a provider's assertion. Replicas are trusted and their mutual authentication is an assumption of use (A9), unbuilt: "Anyone who can reach a socket can act" (G5). No record speaks of the device an operator, a roster member or a key-holder acts from | G5; A9; T-0045-1 |
| 5.3 | Access is classed by risk, read access included, and the controls differ by class (*Classifying Access Based on Risk*) | P | P | P | There are classes and they are in the types: add against deny, Build against Run, labels, six forensic classes, `T_irrev` per effect class. The ranking is by effect on authority, not on the world, so a stop is the lowest class whatever it stops. The read set `W(p)` is designed and not enforced at the reference | SF-1; SF-8; I8 |
| 5.4 | Interfaces are small, typed and non-interactive, the administrative and emergency ones too (*Small Functional APIs*) | M | P | P | Six Build variants, three Run variants, six control actions, and for an emergency "A shell, or a client that reaches any address, is not an entry the corpus admits anywhere" (ADR-0052 §2). Where the rules declare an operator, the reference still takes several requests unsigned, a first grant and the preparation of an emergency seating among them. The project's own administrative interface is a general shell and git | I47 (a); I19 |
| 5.5 | A breakglass exists that works when the authorization system is what failed, is tightly restricted, and is watched (*Breakglass*; *Graceful Failure and Breakglass Mechanisms*) | P | P | – | The emergency seating is restricted (a roster's quorum, one named person, one round) and recorded. It is inside the policy and not around it: "a bad bundle can disable an emergency seat's tools" (ToO §3.1), Build has no emergency seat, and a path outside the mechanism is out of scope. Nothing raises a signal when it is used. The rules floor does not bound the roster's quorum, and the reference accepts one | SF-3; SF-24; ADR-0052 open obligations; 10.02 review §3 ("no alarm path at all") |
| 5.6 | The breakglass is exercised regularly by the people who would use it | M | P | – | "A drill is a real activation", at least once in each domain in each epoch, counted in rounds and read from the log (ADR-0052 §6, provisional). At the reference a drill is marked and "nothing counts it or reports it" | I48; SF-3 (a drill names no failure) |
| 5.7 | Audit logs say what, where, who, when and why, for every decision made or bypassed (*Auditing*) | P | P | P | What, where, who and when are the alphabet, the seat and lease, and a position in one log. *Why* is on the log for a round (its task, by digest) and withheld by decision for an emergency: "The reason is unknown to the mechanism, by construction" (ADR-0052 §5). The book's use of a justification is narrower than what that decision answers: a ticket need not be believed to let software check that one exists | ADR-0052 finding 5 (a decision); SRS-8 for the unrecorded refusals |
| 5.8 | Named reviewers with the right context inspect the logs, and signals are raised (*Choosing an auditor*) | P | G | G | The structure is the book's: a cell Observer with one Thinker's context and a correlator with the cross-cell view. The people are not chosen. "Define the external auditor role" is an open obligation of ADR-0028, the anchor audits its own issuances until then, and the review after an emergency is "by people" unnamed. At the reference no Observer or correlator judges anything | ADR-0028 open obligations; G12; G9; ToO §12 item 14 |
| 5.9 | Least privilege is tested: profiles and scenarios with expected results, run before a policy change, with test credentials (*Testing and Least Privilege*) | M | P | – | The floor's gates are this method made mandatory: totality, non-vacuity, discrimination, with "a case that allows and at least one that denies" for every permit (`floor/gen-tests.py`). The reference's test keys and rules are labelled as such and a simulated attester is refused unless built for. Nothing runs any of it before a change | CR-57; SRS-16 |
| 5.10 | A denied caller is told an amount graded by its privilege, and a wrong denial can be diagnosed (*Diagnosing Access Denials*) | G | P | – | One sentence governs: "A floor deny names its reason." No record says what a denied principal may be told. At the reference the grading runs the wrong way by accident: the agent is given the forbids that fired, its own Observer's liveness among them, and an unknown caller a blind answer. A refusal by the bundle, the tier where a deployment's fine policy lives, says "bundle did not allow" and nothing else; the policies compute their reasons "for the decision log" and nothing reads them | I22 (reference only); SRS-10 |
| 5.11 | Policy is distributed versioned, reviewed, signed apart from what pushes it, and gradually (*Worked Example: Configuration Distribution*) | P | G | P | A bundle is trusted by a signature under an anchor-issued key, made at promotion. Nothing is gradual. At the reference the signature covers the revision's name and not the bytes that load | SF-6; SRS-12 |
| 5.12 | One authorization framework, apart from business logic, in a language neither too simple nor too general (*Authorization Decisions*; *Avoiding Potential Pitfalls*) | M | P | – | One admit path, two tiers, a fixed and proved composition, and a floor that "must fit PARC. No aggregation, no regex, no computed data" (ADR-0030). At the reference authorization is also written in Rust beside the policy, the book's first pitfall: the operator envelope "is stated twice, in Cedar for the decision and in Rust for apply; nothing checks the two agree but the tests" | I47 (e); I20; CR-46 |
| 5.13 | Sensitive actions need a second party who sees exactly what they approve, can refuse, and leaves a record (*Multi-Party Authorization*) | P | P | G | A promotion vote binds to the artifact's digest, the gate evidence's digest and the rules epoch; any counted deny denies; a timeout is never a grant. Below that the design is single-party on purpose: an operator's add needs a peer's presence and not its reading, and every stop is unilateral. At the reference a roster member's approval names a seat, a person and a round, and not the seating it activates. In the project one person is every party | ADR-0050 finding 6; A4; SF-2; SRS-9 |
| 5.14 | The riskiest approvals come from a second, hardened platform (*Three-Factor Authorization*) | G | G | – | No record speaks of the platform an approval is made on, for operators, the roster, voters or key-holders. The Adopter's Guide says so of keys: "How private keys are stored and who can reach them, which no record addresses" | SF-7 and A16 in part; SRS-5 |
| 5.15 | Access is temporary (*Temporary Access*) | M | P | – | Every lease is one round with a `ttl` of at most `T_persona`; an emergency lease has no renewal and no successor; a lapsed operator can only stop. At the reference a restarted replica starts every live lease's clock again | I47 (d); CR-46; SRS-13 |
| 5.16 | The cost to the people who must use the controls is managed (*Tradeoffs and Tensions*) | P | – | – | Costs are stated record by record, and the operator's load is argued and not measured. Nothing addresses approval fatigue or routine use of the emergency path, which is the book's warning: without reinforcement "breakglass use can become an everyday occurrence" | CR-17; fatigue uncarried, low |

**Reading.** On the agent's side this chapter is met about as fully as a design can meet it: there is no ambient
authority to hold, no general interface to misuse, and no way for policy pushed at the bundle tier to widen
anything. The gaps are all on the side of the people. The book's advanced controls exist to answer one question,
who administers the administrators, and the corpus answers it for votes and leaves it open for approvals: what an
approver is shown, what device they approve from, where their key lives, and who reads the record afterwards. Two
deliberate divergences from the book should be weighed as such and not counted as lapses. Break-glass here does not
bypass authorization, which is safer and means a broken policy has no way round it. And no reason is recorded for
using it, which keeps the mechanism from seeming to know what it cannot, and gives the auditor nothing to search.

### Chapter 6. Design for understandability

The chapter treats understandability as a security property: a system nobody can hold in their head is one nobody
can change or defend safely. Plane C here is the corpus's own legibility.

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 6.1 | A person with the right background can reason about the system's behaviour and invariants, when changing it and during an incident (*Why Is Understandability Important?*) | P | P | G | An operator has thirteen operating situations, each with what the design does and what they do (Adopter's Guide §7). The reference's decision is small: the composition is 87 lines. The corpus is 524 Markdown files and 1.28 million words, its glossary lists thirty-eight naming collisions as "live", and its own process asks one reviewer to read all of it at one digest. The last review found what the chapter predicts: text in force that contradicts its amended neighbours | CR-47; CR-56; CR-58; cause: SRS-19 |
| 6.2 | Properties are stated as invariants the system upholds whatever its environment does, and the confidence each method gives is stated (*System Invariants*; *Analyzing Invariants*) | M | P | P | This is the corpus's strongest ground. Every property is named, with the mutation that breaks it and the premises it rests on, and *checked*, *proved*, *proved in Lean* and *certified* are kept apart, "none of them means reviewed". The chapter sets formal proof aside as usually impractical. The limit is stated as exactly: the proofs are of modules, not of the code | ToO §12 items 7, 16; T-0045-28 |
| 6.3 | The design keeps people's mental models predictive under attack, overload and failure (*Mental Models*) | P | P | P | A few rules predict behaviour in exactly the unusual cases: failure subtracts, stalls do not proceed, a refusal names its reason. The names work against it. The floor-policy ids an operator sees in a denial collide with other things: "R5, R6 and R7 are each a rules-floor entry and a label forbid" (glossary §13). For the corpus, the rule "the checkpoint wins" now makes a frozen sentence outrank a ratified amendment | glossary §13; CR-41; SRS-19 |
| 6.4 | Complexity is contained in small parts whose properties compose, and cross-cutting requirements are met once, centrally (*Breaking Down Complexity*; *Centralized Responsibility*) | M | P | G | Mechanism constants, a small verified floor, and a bundle that can only subtract; authorization, ordering and audit belong to the mechanism and nobody else. At the reference some rules are held twice (5.12). In the corpus no property can be established from one component: a change travels as dependent entries across records, and findings have no central list | I47 (e); CR-60 |
| 6.5 | Interfaces are narrow, typed, specified, and have a defined way to evolve (*Understandable Interface Specifications*) | P | P | P | Two closed alphabets and one allowlist-entry schema with each field marked checked or claimed (ADR-0049). No record gives the wire, log or record formats a version, or says how a deployment moves from one mechanism release to the next | versioning uncarried, low; SRS-3 |
| 6.6 | Operations are idempotent, or made so with request identifiers, and retries behave as callers will assume (*Pay attention to idempotent operations*) | P | P | – | Log entries carry an id, so a second apply is a duplicate. For effects the question is open: `unknown` is a typed outcome of an `Actuate`, and no record says whether the call may be repeated or gives the tool a key to recognise a repeat by | uncarried, medium; §7.5 |
| 6.7 | Every active entity has one identity, hard to spoof and never reused, and every action traces to an accountable person (*Identities*) | P | G | P | A principal holds exactly one seat, and a person who operates and votes is two principals. An operator's identity is its seat's key, "with no record behind it", and the mechanism cannot tell the person from a program holding the key. No record forbids issuing a seat or principal name again to someone else. At the reference whoever reaches the socket can seat | ToO §12 item 17; I47 (c); reuse uncarried, low |
| 6.8 | Authentication and transport security come from infrastructure, behind one abstraction (*Authentication and transport security*) | P | G | – | Each channel has its own answer, and the replica channel's is an assumption a deployment must build | G5; A9; Adopter's Guide §4.4 |
| 6.9 | The trusted computing base is identified from the threat model and kept small, and requests carry the end user's context (*Security Boundaries*) | P | G | P | Identified more thoroughly than the chapter asks: thirty-seven rows, the verifiers and the people among them, each with a class, a failure direction and a residual, and an *excluded* class so that a theorem resting on an untrusted component is computed void. Small it is not, by position: the pattern does not "keep the trusted base small by hiding rows". End-user context has its only counterpart in ADR-0056, Proposed. At the reference every remaining theorem "rests on T-0045-28 to 30", the implementation, the checker and the toolchain | CR-54; CR-51; CR-3 |
| 6.10 | Security properties of values are carried by types whose constructors enforce them (*Understanding Complex Data Flows*) | P | P | – | Labels on ingress, and handles in place of suppressed bytes, are a taint discipline the mechanism enforces. A label is a declaration and traces no value. In the reference epochs, rounds and log indexes are interchangeable integer aliases, and a digest is an unvalidated public string that reaches a filesystem join, protected by checks made earlier | ToO §12 item 18; SF-9; aliases uncarried, low; §7.5 |

**Reading.** The design is understandable in the way the chapter means: a small number of invariants, stated
exactly, each with what breaks it. On that measure it exceeds the book. The corpus that carries the design is
understandable in no ordinary sense, and the corpus is what a reviewer, an adopter and an incident responder will
actually meet. The chapter's claim is that this matters for security and not only for comfort: when a system
outgrows its readers, changes start to conflict with requirements the person making them did not know of. The
11.11 review counted that happening (CR-45, CR-47, CR-56) and named its rate (CR-61). No list names the property
whose absence causes it, and nothing measures it.

### Chapter 7. Design for a changing landscape

The chapter's frame is three changes at three speeds: a zero-day, a posture improvement, an externally demanded
migration. Plane D asks how a deployment of the pattern would change; plane C, how the corpus does.

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 7.1 | A change is small and standalone, and is documented with its why (*Designing Your Change*: incremental, documented) | P | P | P | Every change of authority is one promoted artifact, ordered and kept. One artifact carries much: the mechanism release holds the floor, its schema, the engine and the genesis rules, so they queue behind one another ("Rotation cannot outrun release cadence", ADR-0027). The corpus documents every change as a typed row with its reason; in practice a batch is wide and a commit can be 36 files and 101,876 lines | ADR-0027 consequences; CR-61 |
| 7.2 | A change is tested and peer-reviewed before it is relied on (*tested*) | M | P | G | In the design, gates before votes and a unanimous quorum with the author recused. In the project, none (21.2) | ToO §12 item 3 |
| 7.3 | A change can be carried switched off, and tried without effect before it is enforced (*isolated*; *Medium-Term Change*: dry run) | G | G | P | No record provides for a promoted and inert behaviour, a flag, or a report-only evaluation of a candidate floor or bundle against live traffic. The reference follows two Proposed records with no switch. The corpus does isolate unratified text, by marking it pending in place | SRS-3 |
| 7.4 | A change is rolled out in stages, with instrumentation that shows before and after (*qualified, staged*) | G | X | P | Qualification exists (the gates, then the tally). Staging does not: "no record or module has a canary, a ring or a fraction of the domain left on the prior digest" | SF-6 |
| 7.5 | A rollout can be sped up, slowed or rolled back (*Complications: When Plans Change*) | G | X | P | There is no defined return to a prior promoted artifact, and the routing rule works against one: reverting a floor tightening is a relaxation, which needs an anchor issuance and a promotion (ADR-0030 §5). The corpus itself moves forward only, by design | SRS-3 |
| 7.6 | Dependencies are kept current and the system is rebuilt often, so a critical patch applies directly (*Keep Dependencies Up to Date and Rebuild Frequently*) | P | P | G | The design has a staleness argument for policy ("Stale bundles are monotone-safe") and none for software: nothing bounds the age of a mechanism release. The reference's lockfile was brought current once, on 2026.11.03, in answer to eighteen hosted alerts, with no addendum; ADR-0033 still names the older versions. The verification toolchain cannot follow upstream at all: the pinned prover is a build upstream has since replaced, for one platform, with two known unsound cases, and a fix reopens every proof | CR-55; G11 items 73, 104, 107; SRS-16 |
| 7.7 | Releases are frequent and their validation is automated, so a bad one is stopped without a person noticing (*Release Frequently Using Automated Testing*) | P | G | G | Gates are automated in the design and their evidence is an assertion. In the repository nothing runs unless a person runs it | T-0045-13; SRS-16 |
| 7.8 | What runs is immutable and content-addressed, and old artifacts age out (*Use Containers*) | P | P | P | Content addressing is everywhere: a lease names its bundle, Persona and profile by digest. Nothing ages out: a superseded revision stays in the verified set | SF-6; SRS-12 |
| 7.9 | Units change independently with no trust between them, and security functions sit in few simple services (*Use Microservices*) | M | P | – | Cells do not address each other, control-plane facts are apart from payloads, and the security function is one mechanism | |
| 7.10 | The speed of a change follows from its severity, and a critical fix does not wait behind other work (*Different Changes: Different Speeds*) | P | X | P | Speed follows direction, by rule, which is better than the book asks for stopping: a subtraction is immediate and needs no quorum. Everything that adds has one speed, a unanimous promotion | SRS-4 |
| 7.11 | For a zero-day: triage it, know what runs the affected version, get a verified patch out fast and gradually, and mitigate by restriction where no patch exists (*Short-Term Change*; *Example: Shellshock*) | P | P | P | Mitigation by restriction is the design's strength: revoke by principal, Persona or profile digest, or fence the fleet. What runs which revision can be read from the log. The fix is the slow part. It needs every grant seat ("Liveness equals the availability of every grant seat. This includes Persona and incident-driven bundle promotions"), cannot use break-glass (R7), and reaches a live principal only when its round is ended. The fast path for strictly subtractive bundles was "Deferred" in ADR-0024's options and is on no open list. The corpus has had its own zero-day, the prover's unsoundness, and handled it by the book: triaged in a day, reproducers kept, every proof scanned, reported upstream | SRS-4; ADR-0046 A2, A3 |
| 7.12 | A long change has a goal, automated measures of progress, and documentation that survives a change of people (*Long-Term Change*) | P | P | P | How the archetype itself evolves is deferred to a record not written (ToO §8.2). The drift test is an automated measure of whether code still follows the text it cites. The corpus's long change is genesis to bootstrap: the goal is defined, the progress is a debt ledger, and there is no date ("No forcing function") | ToO §12 item 6; ADR-0029 |
| 7.13 | Keys and secrets are rotated regularly and the rotation is practised (*Example: Heartbleed*) | G | G | – | Leases are short by rule. For every issued key, replacement is defined and regular rotation is not: no interval, no exercise | SRS-5 |

**Reading.** The corpus is strongest where the chapter is weakest and weakest where it is strongest. The chapter
has nothing like a computed classification of a policy change, in which neither the author nor the solver can pass
a relaxation off as a tightening, or an authority to change that scales with the direction of the change. The
corpus has almost nothing of what fills the chapter: staging, flags, dry runs, rollback, a rebuild cadence. SF-6
already carries the absence of rings. What it does not carry is that the design's one fast direction is down. A
deployment can stop anything at once, and can fix, try or undo nothing faster than its slowest voter.

### Chapter 8. Design for resilience

One fact governs most of chapters 8 to 10. The design's stated answer to failure is to stop. The book treats
stopping as one option, whose cost has to be weighed, bounded and recovered from. TOPAK therefore does well
wherever the book says *do not fail open*, and poorly wherever it asks what a stop costs, how load is shed, or how
the system comes back.

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 8.1 | Layers of defence are independent, and each assumes the one before it has failed (*Defense in Depth*) | P | P | P | Six layers, each with a declared job, and the strongest habit in the corpus: every trusted component has a row saying what its failure yields, and every property a mutation that must break it. Independence is required of Observers and Personas only, and the layer that makes the rest exhaustive, confinement, is empty | SF-7; ToO §12 items 1, 12 |
| 8.2 | Probing is detected, and outsiders are asked to find what the builders missed (*Google App Engine Analysis*) | P | G | G | Refused attempts are part of the record. Nothing reads them at the reference, and no outsider has looked at any of it | G12; G11 §4 |
| 8.3 | What is kept and what is dropped under failure is decided in advance, by criticality (*Controlling Degradation*) | P | P | – | The choices are specific: reads continue while effects stop, a dead Observer stalls its own cell and nothing else, an emergency call is never coupled to detection. They are made by rule and not by ranking what matters | SF-1; CR-37 |
| 8.4 | The cost of each failure is known, including the time to recover from it (*Differentiate Costs of Failures*) | G | P | – | "ADR-0045's rows record what a component's failure does to authority, and they have no column for what its stop does to the process it controls" (SF-1). The reference does fail early and cheaply, in the order fence, lease, lift, floor, bundle, consensus, though no record gives cost as the reason | SF-1; SF-2; CR-36 |
| 8.5 | Under excess load the system sheds by priority, and security-critical requests come first (*Load shedding*; *Throttling*) | G | G | – | No record defines a priority, a request cost, a shedding rule or a throttle. At the reference a revocation and a fence wait in the same queue and the same log as every ordinary admit | SRS-2 |
| 8.6 | A security-critical operation never fails open, and a substitute is at least as strict (*Failing safe versus failing secure*) | M | M | – | A floor error is a deny, every non-affirmative bundle answer is a deny, and the fallback engine is bound to the lease's own revision. This is the chapter's rule, kept without exception and partly proved | |
| 8.7 | Automation leaves people a foothold and makes no unsupervised change of large scope (*A foothold for humans*) | P | P | P | The footholds are real: a deny needs no lease, and an emergency seat cannot be blocked by an Observer. Scope is unbounded in the stopping direction: "Any one operator can stop a domain, and any one with a live lease the fleet" (ADR-0050). In the project nothing bounds how much is ratified in a day | SF-2; SF-12; CR-61 |
| 8.8 | Compartments follow role, location and time, with boundaries that are enforced and tested (*Controlling the Blast Radius*) | P | P | G | Role: one seat per principal, alphabets by kind, proved. Time: a lease is one round. Location: one device rule for Observers, and "placement, which no record checks" (Adopter's Guide §3.4). At the reference the three replicas are one process tree. In the project one person holds every role | I8; G5; SF-2 |
| 8.9 | Failure domains are independent, are never all changed at once, and critical functions have alternatives that are exercised (*Failure Domains and Redundancies*) | P | P | G | Consensus replicas are the redundancy, crash-fault by position. A promotion reaches the whole domain at once. Only the bundle engine has an alternative. The project's failure domain is one person and one hosting account | SF-6; SF-7; ToO §12 item 9; SRS-18 |
| 8.10 | Nothing enters a failure domain unvalidated, and the last known good configuration is kept locally (*Data isolation*) | M | M | P | Everything that changes behaviour enters through a check, and what is resident (floor, genesis rules) needs no fetch to fail closed. The reference refuses to start on a digest mismatch | G11 §8 (no floor ratified) |
| 8.11 | Validators exist for each known failure and run continually, and the validation is itself audited (*Continuous Validation*) | P | P | G | In the design confinement is appraised again at every renewal and gates run before every vote. In the repository a validator exists for nearly everything, the validators were themselves audited by planting defects, and none runs unless someone runs it | CR-57; CR-55; SRS-16 |
| 8.12 | Failures are injected on purpose, and emergency components are used in normal operation so they are known to work (*Validation in Practice*) | P | P | P | The emergency path has a required drill. The fleet fence and re-seating, an operator's lapse, loss of the transport and replacement of a key have none. The reference's consensus tests inject drop, duplication, partition and crash | SF-3; G11 item 105 |
| 8.13 | Keys are rotated when nothing requires it, the time a rotation takes is measured, and the old key is shown to fail (*Measure key rotation cycles*) | G | G | – | Replacement of a key is defined as an issuance. No record asks for a period, a measurement or the check | SRS-5 |

**Reading.** The chapter's first two sections could have been written from the corpus: assume every layer fails,
never fail open, give people a foothold automation cannot remove. Its middle is the scenario findings' territory,
and SF-1, SF-2, SF-6 and SF-7 reached from incidents what the chapter reaches from principle. What is left for
this reading to add is small and specific: nothing says a revocation goes ahead of ordinary work when the system
is busy, and no key is ever rotated on purpose.

### Chapter 9. Design for recovery

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 9.1 | Recovery is planned for random, accidental, software and malicious errors alike (*What Are We Recovering From?*) | P | P | M | Malicious and software errors are the premise. Random and accidental ones are thinner: the replica model is crash-recovery and "does not lie", and nothing says what a replica with a damaged log is. The reference's acceptor log has no checksum and stops replaying, silently, at the first line it cannot parse. The corpus has itself been recovered once, record by record from session history, under a stated rule (`process/RECOVERY-REGISTRY-2026.09.15.md`) | ToO §12 item 9; A9; SRS-14 |
| 9.2 | The change mechanism can go as fast as will ever be needed, with its speed set by a separate, simple, testable policy (*Design to Go as Quickly as Possible (Guarded by Policy)*) | P | G | G | A subtraction is as fast as one consensus round and needs nobody's approval. An addition has one speed. Nothing sets a rate: no limiter exists, and the nearest object, a mesh's activation budget, is a count. The reference has "no promotion pipeline". The project is fast with no policy on it | SF-6 in part; SRS-3; CR-61 |
| 9.3 | Nothing depends on wall-clock time; rates, epochs and validity lists are used, and repair needs no clock (*Limit Your Dependencies on External Notions of Time*) | M | P | – | ADR-0032 is this section stated as a rule: "clocks buy liveness, never safety", an interval is trusted by the direction its failure takes, and "No safety decision reads a clock a principal supplies." Epochs carry safety and only move forward. The margin arithmetic is proved in Lean of a transcription. One interval still needs trusted time (Persona expiry, A6). The reference departs from the rule on one path, a restart | ADR-0045 finding 2; A6; SRS-13 |
| 9.4 | A rollback to the last good state is quick, a rollback to a known-bad version is impossible, and updates are signed over their contents and version (*Rollbacks Represent a Tradeoff*) | P | G | M | For bundles the floor is the fence: an old bundle can only refuse. Neither half of the book's tradeoff is otherwise decided. There is no quick return (7.5) and no bar on an old revision: "no clause found takes a superseded revision out of the verified set" | SF-6; SRS-3; SRS-12 |
| 9.5 | Known-bad versions go on a deny list kept outside the component, and an ordered security version with a low-water mark stops the system running anything older (*Deny lists*; *Minimum Acceptable Security Version Numbers*) | P | G | – | The revocation set is such a list, in replicated state, checked at every grant. It can name a principal, a Persona digest or a profile digest. It cannot name a bundle revision, a tool or a mechanism release. A bundle revision is a content digest with no order, so there is no version to set a mark on. A profile does carry a minimum platform version (P7), and whether moving it fences live leases is "answered in the design record and decided nowhere" (Adopter's Guide §7.7) | SF-6; ordered-version framing uncarried |
| 9.6 | Revocation is explicit, from one source of truth, never fails open and needs no clock; emergencies use the same mechanism; and it is safeguarded so a partial compromise cannot revoke everything (*Use an Explicit Revocation Mechanism*) | P | P | – | The first three are met in full and proved of the modules: targeted revocation and the epoch fence, ordered, attributed, enforced by the mechanism ahead of the floor. The fourth is not: one operator with a live lease fences the fleet, a revocation is "permanent within the rules-epoch chain", and recovery from a fence is "a quorum's work" | SF-2; SF-12; TM7 |
| 9.7 | The intended state is known to the byte, the deployed state can be read, and deviations are found and repaired (*Know Your Intended State, Down to the Bytes*) | P | P | P | Intended state is content-addressed almost everywhere and every admit records the digests it was decided under. Nothing reads a running deployment back against its declaration ("nothing checks the rows against the running system", Adopter's Guide §4.1). At the reference the loaded bundle's bytes are not what its signature covers, and the values-file digest is recorded nowhere. The corpus has a digest manifest for every cut, all thirty of which verify, and at the last review 190 files measured by none | CR-41; CR-55; format inventory finding 12; SRS-12 |
| 9.8 | Backups are protected like the data, restores are validated, and a second instance of any singleton can be built from captured state (*Persistent data*; *Global services*) | G | G | P | No record mentions a backup or a restore of the log, the archive or the plaintext store, or what to do when a quorum of replicas is lost. The archive itself is supplied by no record, the log has no snapshot, and the fallback is re-genesis, whose migration "the deployment writes" and which inherits no forensic read of the old chain. The corpus's backup is git and its hosting account | G9; G14; G17; design-gap 1.10, 1.11; SRS-7 |
| 9.9 | Recovery is tested, including by people following the written steps (*Design for Testing and Continuous Validation*) | P | P | P | The emergency drill is the one recovery test a deployment owes. That a stall ends is checked at small constants for coupling and proved for nothing | SF-3; CR-37; G11 item 105 |
| 9.10 | Emergency access has the fewest dependencies, shares none with what it rescues, keeps controls as strong, and is exercised on a schedule; responders can talk when normal channels are down (*Emergency Access*) | P | P | G | ADR-0052 applies the book's argument to one dependency and stops: the emergency key is off single sign-on because "An emergency path that needs the identity provider fails when the provider does." The same holds of the network, the consoles, the bundle (5.5) and the replicas, and no record says so. Communications are out of scope. The exercise period is required and is the deployment's to declare. In the project nothing can be ratified, and no report answered, without one person | SF-3; SF-24; SRS-18 |

**Reading.** The chapter and the corpus agree, almost sentence for sentence, on time and on revocation. They part
on everything that comes after the stop. The book's recovery is a return: roll back, restore, rotate, rebuild a
second instance. The pattern's recovery is a further subtraction, and the way back from each one is open in a
different record: after a fleet fence, a quorum's work with the mechanics an open obligation; after a revocation,
nobody may lift it; after a quarantine hold, undecided (G12); after a bad promotion, nothing retires it (SF-6);
after the loss of the log or the anchor, re-genesis, unwritten (G17). Each of the five is carried somewhere. No list
puts them side by side, and together they are the least designed part of the pattern.

### Chapter 10. Mitigating denial-of-service attacks

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 10.1 | Denial of service is modelled against every dependency of a request, and the weakest link is found by what it costs an attacker to disrupt (*Strategies for Attack and Defense*) | G | G | – | Every agent is hostile by premise, and no record asks what a hostile agent can do to availability. The words *denial of service*, *flood*, *throttle*, *rate limit* and *backoff* occur in no record, in neither guide and nowhere in the narrative. Loss of availability is counted as the safe residual. Nobody has ranked who can induce a designed stall: a cell Observer its cell, a correlator or one operator a domain, the transport or one operator with a lease the fleet | SRS-2; SF-2 for reach |
| 10.2 | Each constrained resource is protected, in layers that turn attack traffic away as early and as cheaply as possible (*Designing for Defense*) | P | P | – | The shape is right: "Consensus for grants, local for denials", so a refused request never reaches the replicated log, and admitted work is bounded per lease (`R`, `K`). Refused work is not. ADR-0003 A2 capped denial records written after a round is sealed, because "A misbehaving agent could otherwise turn its own revocation into an unbounded write", and left the open round uncapped; at the reference every refusal in an open round is one more record on its topic. Both sockets read a line of any length | SRS-2; G5 |
| 10.3 | Demand and saturation are monitored, and a person is alerted when action is needed (*Monitoring and Alerting*) | G | G | P | Nothing in a record. At the reference "No telemetry, metrics, dashboards or token accounting" (10.09 alignment) | register row "§12 row 17" ("nothing alerts a person") |
| 10.4 | Under attack the service degrades by priority, never crashes, and its control system fails static and does not depend on what is attacked (*Graceful Degradation*; *A DoS Mitigation System*) | P | P | – | Fail-static is met: when a policy source fails, the policy in force does not change. There is no reduced mode and no priority. The response to an offending principal is a finding that revokes for good, with no recourse for a false positive | SF-12; G12; SRS-2 |
| 10.5 | Synchronized legitimate demand is expected (*Dealing with Self-Inflicted Attacks: User Behavior*) | P | G | – | Two events synchronize by design and their cost is stated in prose only: a fleet fence and an issuance each end every round at once, and every principal then asks to be regranted. "A fence storm is an availability event" (ADR-0031) | SF-1 |
| 10.6 | Clients retry with exponential backoff and jitter, and servers stay healthy enough to let them stop (*Client Retry Behavior*) | G | P | – | The design requires retries and does not shape them: assumption A18 makes "A refused Thinker asks again" a premise of liveness, with no backoff asked of an honest client and no bound on the others. The reference's own proposal retry is a fixed 750 ms interval to a deadline | SRS-2 |

**Reading.** This is the chapter with the least to hold on to in the corpus, and the reason is a single early
choice. A pattern that treats a stall as the safe outcome has no cause to ask who can produce one. The book's
point is that availability has an adversary too, and here the adversary is already inside the premise: an agent
that "may do anything its alphabet allows" may also ask ten thousand times for what it will be refused. The
position in the Adopter's Guide, that the pattern does not "scale, or promise latency", discharges throughput. It
does not discharge this.

---

## 4. Part III: Implementing systems

These four chapters are about code and the path from source to production. Plane R carries most of them, read as
what it is: `SECURITY.md` says nothing here is deployable, and "the reference is not the mechanism" (ADR-0033 §1).
A standard the reference does not meet is marked G or P all the same, because the reference is the evidence the
records cite. Plane D is the `Build` domain, the pattern's own model of a supply chain.

### Chapter 11. Case study: a publicly trusted certificate authority

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 11.1 | Untrusted input is parsed in a memory-safe language, away from critical operations, by parts of limited function (*Programming Language Choice*; *Design, Implementation, and Maintenance Considerations*) | M | M | – | The model is outside the trusted base and reaches the mechanism through a typed alphabet. The reference is Rust with no `unsafe` anywhere in its eight crates, and three of them do no I/O. Nothing keeps it so (no `forbid(unsafe_code)`) | T-0045-30 |
| 11.2 | Where two components judge the same input, their answers are compared and a disagreement stops the work | M | P | P | The floor gate accepts a solver's `unsat` only with a proof a second, pinned checker accepts, and three lying-solver controls are part of the gate run. Tested paths are replayed through a TLA+ model and two Lean models. The two bundle engines, whose divergence ADR-0045 names as a residual, are never compared on common inputs | T-0045-6; CR-55 (82 of 83 traces) |
| 11.3 | Access checks are centralized so that an entry point cannot be added without one (*Complexity Versus Understandability*) | M | P | – | One admit path for every agent action. For operator requests the reference's gate is a list of what to refuse ending in a wildcard (`state.rs`, `_ => None`): a new kind of log entry is accepted unsigned unless someone remembers to add it | I47 (a) for the paths; the shape uncarried; §7.5 |
| 11.4 | Third-party code is reviewed, isolated, tested like one's own, and its defects reported upstream (*Securing Third-Party and Open Source Components*) | P | G | P | Third-party components are rows of the trusted base, which is a declaration and not a review: one row trusts "every crate in `Cargo.lock`". The replica reaches 409 packages; no audit or vetting tool is configured. For the prover the corpus did exactly what the chapter describes: found two unsound cases, kept reproducers in `spec/defects/`, and reported both (tlaplus/tlapm#309, #310) | T-0045-30; CR-55 |
| 11.5 | Good practice is enforced before submission, and tests, static analysis, sanitizers and fuzzing run continuously (*Testing*) | – | G | G | Chapters 13 and 14 | SRS-16 |
| 11.6 | Root keys are offline under multi-party control, daily work uses intermediates, and replacement material is matured before it is needed (*Resiliency for the CA Key Material*) | P | G | G | Multi-party control of the root is the archetype: unanimity of at least three anchor keys, with issued keys doing the daily work. Recovery is where it departs: "At the archetype, **loss freezes the rules**", and the exit is re-genesis. No alternate is prepared and the ceremony is an open obligation. The reference's keys are files in the clear. The corpus's own root is one account, with unsigned manifests in the repository they measure | ADR-0025 open obligations; G6; SRS-17 |
| 11.7 | Validation admits no human discretion, outputs are checked at several stages, and independent logs are reconciled (*Data Validation*) | M | P | P | "Gates enable voting; they do not vote", and semantic judgment may deny and never enable. The reconciling parties, an Observer and an archive, are not built | G12; G9 |

### Chapter 12. Writing code

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 12.1 | Invariants are enforced by a shared framework whose interfaces make the unsafe construction impossible, not by reviewing each change (*Frameworks to Enforce Security and Reliability*) | M | P | P | The membrane is such a framework, and the composition of its two policy tiers is fixed in one function and proved of a transcription of it. Other invariants in the reference are held by convention across call sites (12.5). The project's skills carry lint scripts for the record process; they bind the assistant and not a commit | I47 (e); I46 (a) |
| 12.2 | Every request passes logging, authentication, authorization and throttling steps supplied once; deadlines are tracked and retries back off (*Example: Framework for RPC Backends*) | P | P | – | Authorization and logging are central. Authentication is a bearer token, a file mode, and nothing between replicas. Throttling: none, and a native tool call has no deadline | G5; I14; SRS-2 |
| 12.3 | Cryptography comes from established libraries, and secrets have types that restrict where they go (*Benefits of Using Frameworks*; *Common Security Vulnerabilities*) | M | P | M | Primitives are library code (`ed25519-dalek`, `sha2`). The signed-statement format is the reference's own, and its canonicalization has failed once (`mechanism/` finding 15). Secrets are hex strings in configuration and on the command line, and a request type derives `Debug` with its token in it. No secret is tracked in the repository | G6; I7; argv and `Debug` uncarried, low |
| 12.4 | Defaults are secure, and debug features cannot be turned on in production (*security misconfiguration*) | M | P | P | Absence denies everywhere, and the simulated attester is behind a build feature and an issued key. Two test instruments are not: the consensus replica's configuration carries a public `mutation` field that switches safety checks off, compiled in unconditionally | uncarried, low; §7.5 |
| 12.5 | Values cannot reach an interpreted context except through types whose constructors establish the contract; identifiers and units are distinct types (*TrustedSqlString*; *SafeHtml*; *Use Strong Types*) | P | P | – | Requests deserialize into closed enums, and a handle cannot be mistaken for a literal. But epochs, rules epochs, rounds and log indexes are aliases of one integer type, and a digest is a public string with no shape check that is joined to a directory path in three places; what stops `../` is an earlier membership check and not the type | SF-9 (design); the reference's types uncarried, low; §7.5 |
| 12.6 | Bypasses of a safe interface are explicit, few, and collected where they can be reviewed (*Legacy conversions*) | M | P | P | In the design every exception is an enumerated floor entry and every departure a numbered degeneracy with what it voids. In the reference every stand-in is tagged `PROVISIONAL`, `BOOTSTRAP` or `SIMULATED` and listed in a register, which is the book's advice exactly; the register and the tags have drifted apart | register, inventory finding 8; CR-41 |
| 12.7 | Risky patterns are rejected at compile time or on every commit; dynamic languages are statically checked; sanitizers run automatically (*Lessons for Evaluating and Building Frameworks*; *Sanitize Your Code*) | – | P | G | Rust's enums give compile-time feedback through most of the state machine. Nothing is configured to fail a build: no lint table, no pinned compiler, no checker for the 129 Python files (the gate runner among them) or the 66 shell scripts, eight of which set `-euo pipefail`. The one data race on record was found by chance | `mechanism/` finding 19; SRS-16 |
| 12.8 | Debt is marked, measured and repaid; refactoring and functional change never share a commit (*Repay Technical Debt*; *Refactoring*) | M | P | P | Marking is the corpus's habit at every plane: a genesis debt ledger, open obligations on every record, a tagged register in the code. Repayment has no mechanism: a derived document's findings have "no path" into the open list. Commits mix records, policy, code and tests | CR-60; CR-59 |

### Chapter 13. Testing code

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 13.1 | Unit tests exist, are fast and hermetic, cover malformed and boundary input, and run before a change merges (*Unit Testing*) | P | P | G | 155 tests in fifteen files, most of them against a pure state machine with no I/O. They gate nothing: at `981bc77` one fails and eight pull requests have merged over it. The design's version of *before merge* is that votes open only after gates pass, on evidence an operator asserts | G8; T-0045-13; SRS-16 |
| 13.2 | A test that still passes when the code is removed is a defect (*When to Write Unit Tests*: mutation testing) | M | P | M | This is the corpus's own founding rule, non-vacuity, applied at every layer: a mutation per TLA+ property, a broken variant per consensus check ("otherwise the checks are vacuous"), lying-solver controls in the gates, and defects planted in the corpus's own checkers. It is done by hand, property by property; no coverage or mutation tool measures what no test reaches | CR-57; `mechanism/` §6 |
| 13.3 | Code is built to be tested, flaky tests are fixed, and a defect found by review gets a regression test (*How Unit Testing Affects Code*) | – | P | – | The consensus core is free of I/O, and the clock, transport, network and bundle decider are traits with in-memory forms. Flaky tests were diagnosed when found. Some defects were fixed with repeated runs and no named test | CR-39; `mechanism/` findings 15, 19, 20 |
| 13.4 | Integration tests use real dependencies (*Integration Testing*) | – | P | – | The end-to-end tests run three replicas, the linked floor and the compiled bundle in one process. The run against a real Kafka and a real policy sidecar was last made on 2026.09.25, and its script no longer completes | G11 item 52; CR-55 |
| 13.5 | Code that handles untrusted input is fuzzed, continuously, and crashes become tests (*Fuzz Testing*) | – | G | – | No generated-input test exists for any parser of untrusted bytes: replica frames, agent requests, guest messages, bundle tarballs, allowlists, profiles, workflow text. The apply path, which every replica runs on every ordered entry, contains `expect` calls, each guarded by an earlier check that nothing but reading confirms | uncarried; §7.5 |
| 13.6 | Linters run by default, fast static analysis blocks a failing push, and deeper analysis runs on a schedule (*Static Program Analysis*) | M | P | G | For the policy floor, deeper analysis is a gate: symbolic over its schema, with a candidate change routed by its computed meaning. For the Rust, Clippy is nearly clean when run (three warnings) and nothing runs it | SRS-16 |
| 13.7 | Safety and liveness properties are specified and verified, of the system or a model of it (*Formal Methods*) | M | P | P | The chapter gives this two pages and calls it rarely practical. The corpus has thirty-four proof modules, a second prover, and a declared method. Its limits are stated more exactly than any outside reader would state them: "Neither is a claim about the running reference"; "A Lean proof of the code is not a proof of the code"; "The pinned prover can prove false statements"; "No liveness is proved." Trace validation, the one mechanical link from code to model, is behind the code | G11 §8; G11 items 56, 103, 104, 105 |
| 13.8 | All of it is part of the engineering workflow and runs without being asked (*Conclusion*) | – | G | G | None of it is | SRS-16 |

### Chapter 14. Deploying code

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 14.1 | The supply chain's adversaries are named and mapped to mitigations, with each mitigation's limit (*Threat Model*) | P | – | G | "Build is the hostile domain. One coerced or compromised approver can promote alone" is the chapter's insider, and ADR-0045 gives the limits row by row. The mechanism's own supply chain is three rows (T-0045-28 to 30) and not a list of threats. The corpus has no threat model of its own path from author and assistant through merge, tool install and manifest cut | T-0045-28 to 30; SRS-17 |
| 14.2 | A second person must review every change, and nobody can submit alone (*Require Code Reviews*) | M | P | G | The design is stricter than the book: no strict subset of grant seats can promote, the author is recused by the mechanism, and "Correlated review failure is untouched" is stated as the limit. At the reference the independent veto seat is not enforced (G18). In the project one account authored, merged and cut everything | G18; ToO §12 item 3; SRS-16 |
| 14.3 | Build, test and deploy are run by a locked-down automated system, and nobody can go around it unchecked (*Rely on Automation*; *Deployment Choke Points*) | P | P | G | Effects pass the admit path and artifacts pass the tally. Who runs the gates, on what machine, is unowned. At the reference signing "is still a script step, since no promotion pipeline exists", and two paths go round the choke point: a process outside a launcher, and the unsigned operator socket. The repository has no gate at all | G8; G1; design-gap 1.7; SRS-16 |
| 14.4 | The deployment point verifies the artifact and not the person: the provenance is authentic, applies to this artifact by hash, and meets the policy (*Verify Artifacts, Not Just People*; *Implementing policy decisions*) | P | G | P | Identity is a digest everywhere, and a vote binds to (artifact digest, gate-evidence digest, rules epoch). The second of the book's three checks is missing for bundles. ADR-0044 §2 has the key sign the content revision, a digest of the policy sources; the reference's loader takes the revision from the tarball's own manifest and checks the signature over that name. A tarball with other contents, the same manifest and the genuine signature loads as verified. Reproduced (§9) | SRS-12; inventory finding 11 for the build side |
| 14.5 | Configuration is code: versioned, reviewed, tested (*Treat Configuration as Code*) | M | P | M | Everything that defines authority is an issued or promoted artifact. A node's own configuration is a local file nobody promotes | I21 |
| 14.6 | No secret is in version control (*Don't Check In Secrets!*) | X | G | M | None is tracked. The reference has no secret manager; custody is the deployment's to declare | G6 |
| 14.7 | Every build emits signed provenance (sources, dependencies, command, environment), and the builder is one a single workstation cannot subvert (*Binary Provenance*; *Verifiable Builds*) | P | G | G | For artifacts authored inside Build the log is the provenance. For compiled artifacts there is none, and the record says so: "No reproducible build is declared." The only provenance object in the reference is a signature over a revision's name. The corpus's evidence is produced on one machine and signed by nobody | T-0045-30; ToO §12 item 16; G11 item 56; SRS-17 |
| 14.8 | A deployment policy is matched against provenance: reviewed, tested, from the right source, recent, free of known vulnerabilities (*Provenance-Based Deployment Policies*) | P | P | G | The promotion tally is such a policy for *reviewed* and *allowed here*. *Tested* is a rule whose evidence is asserted. *Recent* and *free of known vulnerabilities* are absent | T-0045-13; SF-6 |
| 14.9 | Build inputs are pinned by version or hash, and every fetched input is authenticated before use (*Hermetic, Reproducible, or Verifiable?*) | – | P | P | Pinned by hash: crates, the Python sets, the `slm/` image, Lean dependencies, the TLC jar. Not pinned: the compiler, the policy compiler image (`openpolicyagent/opa`, untagged, in the script that builds what gets signed), `cedar-policy-cli`. The installers compare a sixteen-digit prefix of one binary after installing it, and the prover's own pin says a fresh install "no longer yields the pinned binary" | inventory finding 11; G11 item 73; `tools/TLAPS-PIN` |
| 14.10 | Enough is logged to judge a deployment decision afterwards, and a rejection says what failed and how to fix it (*Post-Deployment Verification*; *Provide Actionable Error Messages*) | M | P | P | Each admit records the digests it was decided under. Start-up and load failures name the clause and print both digests; the drift test prints its own repair steps. Two of the corpus's checkers report failure with exit status 0, and on a shallow clone the manifest verifier fails with a `tar` error | CR-57; inventory finding 12 |
| 14.11 | A deployment breakglass exists, raises an alarm and is rare (*Include a Deployment Breakglass*) | X | G | – | Declined by position: there is no way round a promotion, and the fast path once considered is "Deferred". The reference has a standing one all the same, the `BOOTSTRAP` socket, with no alarm | SRS-4; I47 (a) |

**Reading.** The `Build` domain is a better supply-chain design than the chapter's. Promotion is a
consensus-ordered, unanimous, digest-bound grant with the author recused by construction, where the book has an
approval count on a change. The repository that holds the design has none of the chapter's first three practices:
nobody else reviews, nothing is automated, and nothing verifies an artifact before it lands. The corpus is candid
about the first. The other two it has not named, and they are cheap. They are also where its own tools already
point: the drift test is a deployment policy with nothing to enforce it, and the test that would have caught the
bundle finding is one case away from a test that exists.

---

## 5. Part IV: Maintaining systems

These chapters are about defending a system that is running, and nothing here runs. On plane D the question is
what the pattern gives an investigator or a responder and what it asks a deployment to have. The pattern assumes
"a trained, authorized human is present" (A5), so where it is silent about that human, the silence is a finding
about the pattern. On plane C the corpus's declared equivalent of an incident is a wrong safety claim
(`SECURITY.md`), and its findings, errata and amendments are its postmortems.

### Chapter 15. Investigating systems

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 15.1 | How the system is meant to work is knowable by someone other than its builder (*Debugging Techniques*) | – | P | P | The knowledge is on the page, at a length that defeats the purpose (6.1). Twenty-one recovered records cite as their source private chat sessions the repository excludes, so a second reader cannot check "verbatim from session history" | SRS-19; provenance uncarried, low |
| 15.2 | An issue can be reproduced outside production, and the system emits enough joinable output to tell what it did (*Reproduce the bug*; *Improve observability*) | P | P | M | One causal frame: every admit has a log index, every emission carries it, and each admit records the input's digest and the digests of the floor, schema, bundle and parameters it was decided under. Replay is of boundary events only, by position: root cause past the boundary "is a deployment's to supply". In the corpus every results file regenerates from a script and is cited by digest | ADR-0020; CR-38 |
| 15.3 | A baseline of normal exists, so that deviation is noticed (*Know what's normal for your system*) | P | G | P | At the boundary normal is exact: the alphabet, the allowlist, the envelope. Noticing a deviation inside them is the Observer's and the correlator's work, and neither is built | G12; ToO §12 item 14 |
| 15.4 | Writers to production state are few, human access is justified, and investigators' own access is logged (*Improve access and authorization controls*) | P | G | P | Writers are bounded by seat kind and a responder's acts through the mechanism are attributed. The audit read path is supplied by no record | Adopter's Guide §5.13; G9 |
| 15.5 | Compromise is investigated by trained people, with stated signs of compromise and a point at which an incident is declared (*How Security Investigations and Debugging Differ*) | G | – | G | Assumed in one sentence (A5) and specified nowhere. In the project no reader independent of the author exists | CR-17; SRS-6 |
| 15.6 | Log entries are hard to alter, any alteration leaves a trail, and logs go off-host to a hardened store (*Design Your Logging to Be Immutable*) | P | G | P | What the design gives: one consensus-ordered log across replicas, erasure only as an ordered and modelled event, and six forensic classes that erasure cannot reach. What it does not: any tamper-evidence of its own. A sealing certificate and a Merkle root over round envelopes were designed in the originating session and "None appear in this record" (ADR-0003, recovery finding), so integrity rests on the replicas (a trust root) and on an archive no record supplies. At the reference denial, seal and control records are dropped with a warning when a write fails | ToO §12 item 9; T-0045-1; T-0045-7; G9; SRS-15 |
| 15.7 | Logging design fixes depth, retention, access and the handling of sensitive content (*Take Privacy into Consideration*) | M | X | – | Each has a decision in force: boundary events only; control-plane facts apart from payloads, by hash and pointer; erasure as a privileged, ordered event with its own roster; a read set per topic; retention per domain. The reference declares the archive, masking and erasure out of scope | ADR-0003, 0004, 0006, 0028; residual-risk §1.12 |
| 15.8 | The sources to retain are chosen deliberately, storage is budgeted, retention covers the time it takes to discover a compromise, and logging degrades gracefully when storage runs out (*Determine Which Security Logs to Retain*; *Budget for Logging*) | P | G | – | At the membrane the choice is deliberate and exhaustive. Below it (hosts, the network, the tool host, the transport) no record asks for anything. Cost is admitted and unbudgeted: "Retention cost grows with principals × rounds for F1." Nothing relates payload retention to detection latency, though collusion is the declared case detection cannot see and retention is all a later investigation would have. The log grows without bound | ADR-0028 open obligations; G14; retention against discovery time uncarried, medium |
| 15.9 | Integrity checks have a scope wide enough to catch the right value in the wrong place (*Data Corruption and Checksums*) | M | P | P | Digests bind to their context throughout: a vote to its triple, a lease to its revision. The reference's durable log is the exception (9.1) | SRS-14 |
| 15.10 | Investigation skill is practised, and each investigation ends by adding what would have helped (*Practice!*; *Conclusion*) | G | M | M | Building the reference found what reading had missed, and the records were changed: "a record that nothing executes is checked only by the person who wrote it." The scenario inventory is practice of the same kind. No practice is asked of a deployment | ToO §9, §15 |

### Chapter 16. Disaster planning

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 16.1 | Critical systems and their dependencies are identified, disaster scenarios are ranked, and the analysis is revisited (*Disaster Risk Analysis*) | P | – | P | The pattern analyses its own failure: every boundary has its behaviour when unavailable, every trusted row a residual. A deployment is asked to declare what it gives up and is not asked for a risk analysis of its own. The corpus ranks the risks to its claims (ToO §12; the residual-risk statement) on no schedule | CR-36 |
| 16.2 | The people and roles who respond are identified, with a charter, a severity model, response plans and playbooks (*Setting Up an Incident Response Team*; *Develop Response Plans*; *Create Detailed Playbooks*) | G | – | P | The pattern names who may act (an operator, an emergency-seat holder, two rosters) and nobody who responds. The declaration and the conformance checklist ask for no response roles, severity model, reporting path or playbook. The nearest thing is thirteen operating postures (Adopter's Guide §7). A finding is a deny with no class. The project has routine playbooks for its own operations, as skills, and a five-point scale for findings | CR-17 for proficiency only; SRS-6 |
| 16.3 | No one person's absence blocks a response (*Avoid Single Points of Failure*) | P | G | G | For stopping, nobody is needed but one operator. For everything else in the project, one person is | SRS-18 |
| 16.4 | Time to first response and to triage are stated (*Define Operating Parameters for Engaging the IR Team*) | P | – | M | The pattern puts response time inside the safety argument, which the book does not: `W + L + D < T_irrev` per effect class, and where no budget fits "the effect must not be expressible in the alphabet at all". `D` is declared for no class, and nothing starts its clock, because nothing turns a stall, a finding or an activation into a signal to a person. `SECURITY.md` states five and fifteen business days | register row "§12 row 17"; A10 |
| 16.5 | Before an incident: retention is set, responder access exists, fallbacks exist, backups are restore-tested, responders are trained (*Prestaging Systems and People Before an Incident*) | P | G | P | Emergency access is prestaged by promotion and retention is a declared value. The conformance checklist (V1 to V4) omits three values the guide's own §6 says must be declared: the drill period, the forensic horizon and topic retention. No backup (9.8), no training (20.3) | CR-17; checklist omission uncarried, low |
| 16.6 | Evidence is preserved during an incident and cannot be overwritten (*Processes and Procedures*) | M | P | M | This is the forensic floor's purpose: admit decisions, stop attribution, votes, issuances, activations and erasure events survive erasure and break-glass, as floor denials on the erasure envelope, proved not to compose away (NC-1, NC-2) | I40 |
| 16.7 | Automated systems are audited, and every alert rule is shown to fire (*Auditing Automated Systems*) | M | P | P | The mutation method is alert validation applied to properties: each check is shown to fail on the defect it is for. The corpus audited its own checkers the same way and found four that stay silent | CR-57 |
| 16.8 | Response is exercised: tabletops, faults injected in production, the absence of key people, and a red team (*Testing Systems and Response Plans*) | P | P | P | One real exercise is required, the emergency drill, and it is a better one than the book's example: a real activation, on the same log, countable without a clock. Nothing else is asked. The scenario inventory is a tabletop of the design against forty-five incidents. The absence of the project's one key person has never been exercised, and nothing has ever been attacked | SF-3; residual-risk §4 |

### Chapter 17. Crisis management

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 17.1 | Criteria fixed in advance say what an incident is, and triage sorts a report (*Is It a Crisis or Not?*) | G | – | M | Any Observer's finding takes effect by any-of, as a revocation that is permanent, with no severity and no release. `SECURITY.md` defines six kinds of safety finding in advance and three outcomes of assessment | SF-12; G12; ADR-0039 finding 1 |
| 17.2 | A severe vulnerability is handled as an incident, with an urgent route for the fix and coordinated disclosure in both directions (*Compromises Versus Bugs*) | P | – | P | Stopping is urgent; fixing is not (7.11). Inbound disclosure has a policy. Outbound happened once and well (the prover). The frozen checkpoint still says those defects are unreported, against a ratified amendment that says they were | SRS-4; CR-41 |
| 17.3 | An incident is declared, and one named person takes command (*Taking Command of Your Incident*) | G | – | – | No declaration and no commander. A fleet fence is the nearest act: single, attributed, ordered | SRS-6 |
| 17.4 | Responders do not tip off the adversary, and evidence is gathered without exposing them (*Operational Security*) | P | – | P | A watched principal has no read on its Observer's topic. But the pattern ejects on a finding and has no way to watch quietly, a refusal returns its reason to the principal refused, and no record states either as a choice against the alternative | SF-12 nearby; I22; otherwise uncarried, low |
| 17.5 | A chronological forensic timeline can be built (*The Investigative Process*) | M | P | M | One log index orders every admit, grant, revocation, fence, vote, issuance and activation. Dated History rows, numbered batches and tags do the same for the corpus | G9 |
| 17.6 | Work passes between responders by explicit handover; shifts are bounded and heroics are rare (*Handovers*; *Morale*) | P | – | G | Authority changes hands only by an ordered, attributed grant. The corpus is built to be picked up cold, with a state of record, a debt ledger and an open list. It has only ever been worked in bursts by one person | CR-61; SRS-18 |
| 17.7 | Communication is explicit: terms mean one thing, and what is and is not known is said exactly (*Communications*) | P | – | P | What is not known is said more exactly here than anywhere the reader is likely to have seen (G11 §8; ToO §12). Terms do not mean one thing (6.3) | glossary §13 |
| 17.8 | Who is told what, by whom, is planned: leadership, customers, regulators, those affected (*Keeping the Right People Informed*) | G | – | P | No notification of anyone is in any record. "The record survives; the report to an overseer is still composed by people", and the people an effect lands on "have no standing in the pattern". A reporter to the project gets a written answer; a reader who relied on a claim since corrected gets no advisory | SF-14; SF-26 |
| 17.9 | The incident is closed explicitly, after remediation (*Closure*) | G | – | P | Stopping is defined and ending is not (reading of chapter 9). In the corpus a single finding closes by a ratified erratum; the aggregate does not close | CR-60 |

### Chapter 18. Recovery and aftermath

| # | The book asks (section) | D | R | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|---|
| 18.1 | The full list of what was affected can be produced, including whatever a compromised distribution point pushed downstream (*Scoping the Recovery*) | M | P | P | Scope can be computed from the record: each admit names the lease's bundle revision, rules epoch and Persona, and a promotion names every artifact by digest. The reference keeps the fields and has no tool to query them | G9 |
| 18.2 | Recovery assumes the attacker is watching, and the tools recovery depends on are checked first (*Recovery Considerations*) | P | G | P | Against an agent a revocation is immediate and what the agent tries next is recorded. Against a compromised mechanism the named response is the fence, which the mechanism itself orders, and after that re-genesis. The corpus has lived this once: a trust root of its own evidence, the prover, was found defective and is kept in use under a rule and a scan | ToO §12 items 4, 19; G17 |
| 18.3 | The same weakness is looked for everywhere, and recovery does not reintroduce it: compromised images and configurations are retired (*What variants of the attack exist?*; *Will your recovery reintroduce attack vectors?*) | P | P | M | A revocation by Persona or profile digest reaches every principal on it and bars it from any later grant, which is the book's point made mechanical. A bundle revision or a tool cannot be named the same way, and no rule says what happens to revisions verified under a bundle key that is later replaced | SF-6; SRS-5 |
| 18.4 | A short-term mitigation is marked as debt, with an owner and a condition for removing it (*What are your mitigation options?*) | M | P | P | The pattern's temporary grant expires by construction, and a record may be *provisional* with its exit written down. The debt is, in the corpus's words, "visible, not bounded" | ADR-0029 A4 |
| 18.5 | Compromised assets are isolated and marked so that nobody returns them to service by mistake (*Isolating Assets (Quarantine)*) | P | P | – | The book warns that a newcomer may release a quarantined resource. Here lifting a revocation is not an act anyone has. The softer hold, quarantine with a release, is named and its gate's semantics decided by no record | G12; SF-12 |
| 18.6 | Systems are rebuilt from verified known-good images, and data from integrity-protected backups (*System Rebuilds and Software Upgrades*; *Recovery Data*) | P | G | M | For a guest this is the normal case and not the recovery: one guest per round, from a promoted and measured profile, appraised again at each renewal. For the control plane's own state there is nothing to rebuild from (9.8) | SRS-7 |
| 18.7 | Every credential that may have been exposed is rotated, in a planned order (*Credential and Secret Rotation*) | P | G | – | Exposure of a lease is short by construction. Every issued key can be replaced by an issuance. At archetype custody the anchor's own key cannot: a loss freezes the rules. There is no ceremony, no storage rule and no order | ADR-0025 open obligations; SRS-5 |
| 18.8 | Every incident ends in a written postmortem with causes, how it was found, and action items with owners; the lessons are implemented (*Postmortems*; *After the Recovery*) | G | P | P | No record asks a deployment for one, though the forensic floor holds what one would be written from. The corpus does something larger than a postmortem and stops short of one: 493 findings reported in its last review, each checked by a reader who did not find it and 485 standing, 252 earlier ones still open, and no owner or disposition for any. The book says of an exercise whose lessons are not implemented that it "is merely entertainment" (chapter 16), which is harsher than this work deserves and accurate about its effect | SF-14; CR-60; gaps-prioritization item 13 |

**Reading.** Read against these four chapters the pattern is a machine for the first hour of an incident. It
records what happened in an order nobody can dispute, it stops what must be stopped at once and without a quorum,
and it keeps the evidence from the people most likely to want it gone. For the second hour it assumes a person and
says nothing to them. Nothing tells that person a stall has begun. No record says who they are, what they were
taught, how bad the thing in front of them is, what they should do first, or when they may say it is over. The
corpus carries the single sentence this hangs from (A5) and one finding about it (CR-17, on proficiency). The rest
is a blank in the deployment declaration, where a deployment that conforms to every row would still have no
incident response.

---

## 6. Part V: Organization and culture

These three chapters are about people, and the corpus has one person and an assistant. Plane C is therefore
the project as run, and plane D is the organization the pattern requires of a deployment: its seats, rosters and
the people assumed to fill them. The reference has no organization, and its column is left out.

### Chapter 19. Case study: the Chrome security team

| # | The book asks (section) | D | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|
| 19.1 | Security is everybody's job, with nobody able to disown it (*Security Is a Team Responsibility*) | P | X | The pattern names its roles and separates them: operators, grant seats, anchor key-holders, the break-glass and erasure rosters, an audit authority, and no key both in the anchor set and on a promotion roster (ADR-0026 R5). Two duties have no owner: who runs the gates and signs their evidence, and who says the floor is the right floor. For the project there is no team | design-gap 1.7, 1.8; Adopter's Guide §4.12 |
| 19.2 | Make the safe path the one users are on without trying (*Help Users Safely Navigate the Web*) | P | – | Default-deny is resident and cannot be relaxed by a bundle (ADR-0012; ADR-0030), and the Adopter's Guide's advice runs in the safe direction (start every label at `handle`). But the theorems are inherited only by a deployment that makes eighteen assumptions true and declares sixteen values, none of which ships with a usable default. The safe configuration is the one nobody runs | ToO §12 item 5 |
| 19.3 | Be able to ship a fix fast, on a cadence that is exercised (*Speed Matters*) | P | P | A bundle fix needs a unanimous promotion and then does not reach a live lease: the round is ended and regranted, or the fleet is fenced (Adopter's Guide §7.4). A floor fix is an issuance and a promotion. Neither path has a declared time, and nothing stages either (chapter 7). For the project, fixes land in minutes, and that speed is the absence of a gate | SF-6; SRS-4 |
| 19.4 | Layer defences so that one failure is not a compromise (*Design for Defense in Depth*) | P | – | Fence, lease, lift, floor, bundle, consensus order and an apply-time re-check, with the Observer behind them (Adopter's Guide §5.1). The layer that would make the others exhaustive, confinement, has no member | ToO §12 item 1 |
| 19.5 | Work in the open and engage the people who can find your faults (*Be Transparent and Engage the Community*) | – | P | The repository is public, with its own critical reviews, residual-risk statement and non-claims in it. `SECURITY.md` treats a wrong safety claim as a vulnerability, gives two private channels and response windows, credits the finder and leaves them free to publish. The corpus reported the prover's two unsound cases upstream (tlaplus/tlapm#309 and #310; ADR-0045 A4). The engagement has so far run one way: no outside reader has reported anything, and none is engaged | G11 §4 (A2.5 line) |

### Chapter 20. Understanding roles and responsibilities

| # | The book asks (section) | D | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|
| 20.1 | Those who build the system own its security and reliability; specialists advise and do not absolve (*Who Is Responsible for Security and Reliability?*) | M | M | The pattern puts the duty where the authority is (a seat, a roster, a key). The project's author owns its claims and says so on every page | |
| 20.2 | Bring independent security expertise in at design time (*The Roles of Specialists*; *Integrating Security into the Organization*) | – | G | None has been. The corpus makes it a precondition of bootstrap and not of design: "an independent review of the entire corpus" before the anchor may bootstrap (ADR-0029 A2). The field for a reviewer engaged reads "None" | CR-61; CR-21; gaps-prioritization item 1 |
| 20.3 | Say what the people in each role must know and be able to do (*Understanding Security Expertise*) | G | – | Assumption A5 needs "a trained, authorized human" at the emergency seat, at operation, at quarantine release and across the interval `D`. No record says what the training is, what the person is shown, or how proficiency is kept | CR-17; SF-15 |
| 20.4 | Run offensive exercises against yourself, with rules of engagement (*Special Teams: Blue and Red Teams*) | G | G | None. The mutation method attacks a specification and the scenario inventory replays other people's incidents; neither is an attack on a running system by someone trying to win | residual-risk §4 |
| 20.5 | Give outside researchers a way in, with intake, triage and a disclosure policy (*External Researchers*) | X | P | The policy exists and is better scoped than most (19.5). There is no reward, which the book treats as optional, and one maintainer behind both channels with no stand-in | SRS-18 |

### Chapter 21. Building a culture of security and reliability

| # | The book asks (section) | D | C | What the corpus has, and what is missing | Carried by |
|---|---|---|---|---|---|
| 21.1 | Security and reliability by default, from the design stage on (*Culture of Security and Reliability by Default*) | M | M | See 4.5 and 1.5 | |
| 21.2 | Review is mandatory, documented, and nobody, owners included, can opt out (*Culture of Review*) | M | G | In the pattern a promotion is a unanimous quorum with the author recused, and no one votes on their own artifact (ADR-0024). In the project all 45 pull requests were opened by the custodian's account; 44 were merged, half of them within 71 seconds, with no review on the four sampled and no check run on the two sampled. This is the declared process and not a lapse: "the custodian may ratify unilaterally" (ADR-0029), with the unreviewed part tracked as debt. The book's sentence is that a review works only if it is mandatory, and here the one mandatory review is deferred to a gate with no date | ToO §12 item 3; CR-5; CR-61 |
| 21.3 | Teach people what they are responsible for, and keep reference documentation they can find (*Culture of Awareness*) | G | P | For the project: two guides, a glossary, and the methods written down as skills. For a deployment: 20.3 | CR-17; CR-58 (both guides are behind the tree) |
| 21.4 | Say yes safely: accept risk on purpose, with a budget, instead of refusing by reflex (*Culture of Yes*) | P | M | The project has a device for exactly this, and it is unusual: a record may be ratified *provisional*, in force and subject to redesign, with its exit stated (ADR-0029 A4), and a deployment may depart from the archetype by declared degeneracy. The design itself has no budget for refusal: it says no at no stated cost | SF-1 |
| 21.5 | Assume failure, prepare for it, and write blameless postmortems, your own and other people's (*Culture of Inevitably*) | M | M | Every checkpoint ends with what it does not claim. Findings are numbered, re-graded and never deleted; errata are typed History rows; forty-five public incidents were read as traces against the records, which is the book's own advice (*Using Related Case Studies*) carried further than the book takes it | |
| 21.6 | Make the work sustainable: staff it, spread it, and do not rest it on one person's endurance (*Culture of Sustainability*) | P | G | The pattern asks an archetype bootstrap for "at least 5 humans" and says "a solo bootstrap is not a bootstrap" (ADR-0029). The project is one person at custody (1, 0): loss tolerance zero. Ninety-eight commits and 748 changed files since the last checkpoint, eleven ratification batches in five days before it, ten records drafted in one day after it. No document says what happens to the corpus, its security channel or its response windows if the custodian is unavailable | SRS-18; CR-61 for the pace only |
| 21.7 | Lower the cost of doing the right thing: safety nets, staged change, tools that make the secure path the easy one (*Changing Culture Through Good Practice*) | P | P | The skills under `.claude/skills/` and `skills/` are this for the assistant's work: they make the ratification sequence and the manifest cut the easy path. The safety net under them, checks that run without being asked, is missing (chapter 14) | SRS-16 |
| 21.8 | Be transparent, and overcommunicate (*Overcommunicate and Be Transparent*) | – | M | See 19.5 and 21.5. The risk the book does not anticipate is the one the last review named: so much is disclosed, in so many dated documents, that what is in force "cannot be read off the page" | CR-47; CR-60 |
| 21.9 | Win leadership's support (*Convincing Leadership*) | X | X | Nothing to apply it to | |

**Reading.** The corpus has two of the book's six cultures to a degree the book does not describe (inevitability,
and security by default) and lacks two outright (review, sustainability). The design knows this about itself:
it forbids in a deployment exactly what the project does every day. An author votes on their own artifact, one
person is the quorum, and the lineage that drafts is the lineage that reviews. ADR-0029 names that as genesis and
tracks it as debt. The book's contribution is to say what the debt costs while it is carried. A
review culture is a habit, built by doing it on small changes, and a project that has merged forty-four pull
requests, most of them within minutes of opening them, has no such habit to hand to the reviewer it is waiting for.

---

## 7. What the book adds

### 7.1 What it confirms, and where that is already carried

Most of what the book asks and the corpus lacks is on a list already. These are the book's larger points that
need no new entry.

| The book's point | Chapters | Carried as |
|---|---|---|
| Failing closed has a cost someone must weigh | 1, 8 | SF-1; CR-37 |
| One stop must not take out everything | 8, 9 | SF-2; SF-12 |
| Emergency access must survive what it is there to repair | 1, 9 | SF-3; SF-24 |
| Change is rolled out in stages, and old versions are retired | 7, 9, 14 | SF-6 |
| Failure domains are independent | 8 | SF-7 |
| Review is mandatory and by someone else | 14, 21 | ToO §12 item 3; CR-5; CR-21; CR-61; ADR-0029 A2 |
| Responders are trained | 16, 20 | CR-17; SF-15 |
| Internal channels are authenticated | 5, 6 | G5; A9; ToO §12 item 9 |
| Builds are verifiable | 14 | T-0045-30; ToO §12 item 16; G11 item 56 |
| What runs is what was verified | 13 | T-0045-28; ToO §12 item 16 |
| Checks fail loudly | 13, 14 | CR-57 |
| A person is alerted | 10, 15, 16 | register row "§12 row 17" |
| Defences are attacked on purpose | 2, 16, 20 | residual-risk §4; CR-36 |
| The people affected are told | 17 | SF-14; SF-26 |
| Lessons are implemented | 16, 18 | CR-60 |

The scenario inventory of 2026.11.12 reached the first five rows from forty-five incidents. The book states them
as practice, and was written six years before either. Two sources that share nothing arriving at the same five
gaps is better evidence than either gives alone.

### 7.2 The design

Each finding gives its weight on the scenario findings' scale, the planes it lands on, and the book section. *Near*
names the closest thing the corpus already carries. Nothing here is dispositioned.

**SRS-1. No adversary is named for the archetype.** Medium · D · chapter 2, *Attacker Profiles*, *Insiders*.
The archetype has one adversary, the agent, stated by capability, and a trusted base stated by component. Nobody
has asked the book's question of the people in it: what does an operator who is coerced, tired or wrong do with a
key that verifies, and what does a key-holder's household have access to. ADR-0068 asks it for the overlay and
found two adversaries nothing bounds. *Near:* ToO §10 ("no per-boundary adversary"), listed at G1 as a declaration
unwritten and on no open list since; TM7 in the overlay.

**SRS-2. Availability has no adversary.** High · D, R · chapter 10, all of it; chapter 8, *Load shedding*.
Every agent is hostile by premise and no record asks what a hostile agent can do to availability. Four things
follow, each checkable. (a) Nobody has listed who can induce a designed stall and how far it reaches. (b) Refused
requests are unbounded, and at the reference each one in an open round is a record on its topic
(`topak-node/src/mechanism.rs`, `record_denial`); ADR-0003 A2 bounded the same writes after the seal for this
reason. (c) Assumption A18 makes a client's retry a premise of liveness and asks no backoff of it. (d) No record
says a revocation or a fence goes ahead of ordinary admits; at the reference they share one queue. *Near:* SF-2
(reach of a stop, by fault); the position that the pattern does not "scale, or promise latency", which discharges
throughput and not this.

**SRS-3. A promoted change cannot be tried, and cannot be taken back.** High · D · chapter 7, *Designing Your
Change*, *When Plans Change*; chapter 9, *Rollbacks*. SF-6 carries the absence of rings and of retirement. Three
things beside it are carried nowhere. No candidate floor or bundle can be evaluated against live requests without
effect. No promoted artifact has a defined return to its predecessor, and for the floor the routing rule forbids a
cheap one: a revert of a tightening is a relaxation and needs the anchor (ADR-0030 §5). And no record says how the
replicas of one deployment move from one mechanism release to the next; the reference's `apply` checks the
parameter digest an admit was decided under and not the floor's. *Near:* SF-6; ADR-0027's consequence that
rotation cannot outrun release cadence.

**SRS-4. A vulnerability in a trust-root dependency has only the slow path.** Medium · D · chapter 7,
*Short-Term Change: Zero-Day Vulnerability*. Restriction is immediate. The fix needs every grant seat, cannot use
the emergency path, and reaches a live principal only when its round is ended. ADR-0024 names the cost
("incident-driven bundle promotions") and deferred the one mitigation it considered, a fast path for strictly
subtractive bundles, in its options table. It is on no open list, and no guide walks the case through. *Near:*
ADR-0024 consequences; SF-6.

**SRS-5. Keys have no life cycle.** Medium · D · chapter 8, *Measure key rotation cycles*; chapter 9, *Rotating
signing keys*; chapter 5, *Three-Factor Authorization*; chapter 18, *Credential and Secret Rotation*. Replacement
of an issued key is defined. Nothing asks for a rotation interval, a rehearsal, or a check that the old key now
fails. Nothing says what becomes of bundle revisions verified under a key since replaced. No record says where a
private key is kept or from what device an approval is given, which the Adopter's Guide states in so many words.
At archetype custody the anchor's own key cannot be rotated at all: a loss freezes the rules. *Near:* ADR-0025
open obligations; design-gap 5.4; SF-7; A16.

**SRS-6. A deployment that conforms to every row has no incident response.** High · D · chapters 16 and 17.
Assumption A5 needs a trained, authorized human. The declaration and the conformance checklist ask for no response
role, severity model, reporting path, playbook, exercise other than the emergency drill, or postmortem, and the
checklist's own values (V1 to V4) omit the drill period, the forensic horizon and retention that the guide's §6
says must be declared. Nothing turns a stall, a finding or an activation into a signal to a person, so the human
budget `D` has no starting point. *Near:* CR-17 (proficiency); the register's row on alerting; SF-14; SF-15.

**SRS-7. The control plane's own state has no way back.** Medium · D, R · chapter 9, *Persistent data*; chapter
18, *Recovery Data*. No record mentions a backup or a restore of the log, the archive or the plaintext store, or
what a deployment does when it loses a quorum of replicas. The pieces are carried one by one (no archive, G9; no
snapshot, G14 and design-gap 1.11; re-genesis migration unwritten, G17 and design-gap 1.10). The whole is the fifth
of five unwritten return paths (reading of chapter 9), and no list sets the five side by side.

**SRS-8. An operator's refused request leaves no record.** Medium · D, R · chapter 3; chapter 5, *Auditing*.
ADR-0020 makes an agent's denied attempts part of the record, because "Without them the trail shows a clean
system". ADR-0050 §6 writes an operator's control actions to its topic and is silent on the ones refused. At the
reference a control request refused for a bad signature or by the floor returns an answer to the caller and is
written nowhere (`mechanism.rs`, `control`; `api.rs`, `serve_operator`). An operator's failed attempt to widen a
grant is what a peer or a correlator would most want to read. *Near:* I47 (a).

**SRS-9. A break-glass approval names who and when, and not what.** Medium · D, R · chapter 5, *Multi-Party
Authorization*. The book wants an approver to have "confidence in precisely what they are authorizing". ADR-0052 §2
says "Several seatings may exist; the roster's quorum activates one", and §5 that the activation record names the
seating. At the reference what a roster member signs is a seat, a person, an epoch, a round, a `ttl` and a task
(`topak-core/src/control.rs`, `Activation`); the seating's envelope, bundle and drill mark are not in it, and a
seating is replaced by plain insertion (`state.rs`). Between signing and activation the thing activated can
change, from a drill to the domain's whole envelope. In the design that takes a promotion; at the reference, one
unsigned request. *Near:* I48 (a), (b).

**SRS-10. A refusal by the bundle carries no reason, and nothing says what a denied principal is told.**
Low-Medium · D, R · chapter 5, *Diagnosing Access Denials*. See row 5.10. *Near:* I22.

**SRS-11. Nothing asks a target to accept only the tool host.** Medium · D · chapter 3. Effect exclusivity rests
on confining the client. The book's proxy rests on the target refusing everyone else, which needs no cage. For a
deployment whose principals are `Mediated`, which today is every deployment, a target that accepts only the tool
host is the one control that would make the front door the only door. It is asked for nowhere. *Near:* A1; A2;
A-0068-1 in the overlay.

### 7.3 The reference

Four defects in the reference, found by reading it against the book's chapters on recovery, logging and
deployment. Each is a place where the code departs from the record it follows, which `SECURITY.md` counts as a
safety finding. The first was reproduced. The other three were read and not run, and should be reproduced before
anything is built on them.

**SRS-12. The bundle signature authenticates a revision's name, and not the bytes that load.** High · R, with a
design half · chapter 14, *Implementing policy decisions*. ADR-0044 was written to close one attack, named in its
Context: "A swapped tarball whose manifest names the expected revision is loaded." It is still open. The loader
takes the revision from the tarball's own `.manifest`, requires the file name to match, and verifies the
signature over `{"revision": …}` (`topak-bundle/src/lib.rs`, `bundle_body`, `load_dir_issued`). Nothing hashes
`policy.wasm` or `data.json`. **Reproduced** outside the tree against the tracked bundle: with the genuine
signature left beside it, a tarball whose `data.json` gives the `search@d3` tool the channel target
`elsewhere.example:443` in place of `search.internal:443` loads and reads as verified, and so does one with an
altered `policy.wasm`. What the swap reaches is everything a bundle carries: the policy that can only refuse, and
the allowlist, with each tool's channel target and labels. It needs write access to a replica's bundle directory
and no key. The existing test covers a tarball renamed to a revision nobody signed, and not this.
`mechanism/GAPS-AND-ASSUMPTIONS.md` strikes G7 as "Retired 2026.10.01", ADR-0044 says D-0044-1 is "no longer its
position", and the 11.11 review grades CR-24 partly addressed on the same footing. The design half: §2 signs a
digest of the policy *sources*, and what loads is the compiler's *output*. *Near:* format inventory finding 11
("another OPA can give another module under one revision"), open and carried by nowhere, which is the same root
seen from the build.

**SRS-13. A restarted replica starts every live lease's clock again, and every Observer's.** Medium · R · chapter
9, *Limit Your Dependencies on External Notions of Time*. Each replica notes on its own clock when it applied a
grant or a heartbeat (`mechanism.rs`, `apply_committed`), and a lease with no such note reads as expired, which is
the fail-closed default. A restarted replica is delivered the log again from the first slot (`topak-paxos`,
`Replica::recover`) and notes each replayed grant and heartbeat at the time of replay. So after a restart a live
lease has a full `ttl` ahead of it and an Observer reads as fresh, on that replica. Where another replica kept
running, it still ends the round on time. Where all restart together, which at the reference is one process tree,
every lease outlives the outage by up to its `ttl`, and each further restart extends it again. ADR-0032 §2
admits a local clock for a subtracting interval on condition that it errs early. *Near:* I27; nothing on restart.

**SRS-14. The acceptor's log stops replaying at the first line it cannot parse, and then appends after it.**
Medium · R · chapter 9, *Random Errors*; chapter 15, *Data Corruption and Checksums*. `wal.rs` treats an
unparsable line as a torn tail from a crash and stops there, which is right once. It then opens the file for
append without removing the tail. The next record written joins the torn fragment on one line; at the following
restart replay stops at that line and every promise and accept made since the first crash is forgotten. A replica
that forgets a promise is outside the crash-recovery model the records assume ("It does not lie"). There is no
checksum, and no test opens the log. *Near:* nothing.

**SRS-15. Evidence writes fail open.** Low-Medium · R · chapter 15, *Design Your Logging to Be Immutable*. The
ordering log refuses to speak when it cannot write. The records beside it do not: a denial, a seal's `unknown`
record and a control record are each dropped with a warning when the transport refuses them (`mechanism.rs`). No
record says which kinds are best-effort, or whether an admit should be refused when its round topic cannot be
written. *Near:* G9 (the archive); ADR-0020 on why denials matter.

### 7.4 The project

**SRS-16. Nothing runs unless a person runs it, and the default branch is failing its own check.** High · C ·
chapter 4, *Initial Velocity Versus Sustained Velocity*; chapter 13, *Conclusion*; chapter 14, *Rely on
Automation*. The repository has no workflow, hook or scheduled job, and the pull requests sampled have no check
run. The reference's drift test fails at `981bc77`, because ADR-0054 and ADR-0055 were revised in `fec5c44` and
`mechanism/corpus-pins.sha256` was not, and eight pull requests have merged over it. `tools/check-refs.py` exits 1.
The 11.11 review found the symptoms one by one: a state of record behind its tree (CR-41), a reference no manifest
measures (CR-55), checkers that pass on a failure (CR-57), and its verdict, that "The machinery for catching drift
works wherever it is run, and since G11 the corpus has mostly stopped running it on itself." Neither it nor the
plan that followed names the cause or the remedy. The remedy was named once, in the reorganization proposal of
2026.09.30: "A GitHub Action running `verify-manifest.sh --all`, `check-refs.py`, `cargo test` and `opa test
policies/` would be natural and is one file under `.github/workflows/`. It is a separate decision from layout and
is left out here." The decision was not taken up. `manifests/EXCLUDE` already has a line for the directory. *Near:*
gaps-prioritization item 8, which makes the checkers fail honestly and does not make anything run them.

**SRS-17. The corpus's own root of integrity is unsigned, and its own change path has no threat model.** Medium · C
· chapter 14, *Threat Model*, *Verify Artifacts, Not Just People*; chapter 11, *Resiliency for the CA Key
Material*. Every citation in the corpus is by digest, and the digests resolve to manifests that are plain
`SHA256SUMS` files in the repository they measure, cut by scripts that no manifest measures. No commit the
custodian authored carries a signature, and `G11` is a lightweight tag. The integrity of every citation therefore
rests on one hosting account. The pattern forbids this in a deployment by name: an artifact is trusted by its
signature, under a key whose custody is declared. The corpus has also never written down its own chain (author,
assistant, merge, tool install, manifest cut) with the adversary at each link, though `SECURITY.md` identifies the
asset exactly. One link is a principal by the corpus's own definition: the assistant, which authored twenty-three
commits and acts through a shell behind a permission prompt. *Near:* custody (1, 0), declared in ADR-0029; G11 item
66 (no criterion for assisted drafting).

**SRS-18. One custodian, loss tolerance zero, and no word on what happens without them.** Medium · C · chapter
16, *Avoid Single Points of Failure*; chapter 21, *Culture of Sustainability*. Custody (1, 0) is declared and
`SECURITY.md` says plainly that this is a single-maintainer project. No document says what a reporter should do,
and after how long, if nothing is heard; who may ratify, cut or answer if the custodian cannot; or where a second
copy of the excluded session history, and of the pinned prover that upstream no longer serves, is kept. *Near:*
CR-61 (the pace); ADR-0029 (the headcount a bootstrap needs).

**SRS-19. Legibility is not managed as a property of the corpus.** Medium · C · chapter 6, *Why Is
Understandability Important?*. See row 6.1 and its reading. Nothing budgets, measures or tests whether a person
who is not the drafter can find out what is in force. *Near:* CR-47; CR-58; glossary §13.

### 7.5 Smaller observations

Uncarried, and low or narrow. Listed so that they are on a list.

- **D.** No record says whether an `Actuate` whose outcome is `unknown` may be repeated, and a tool is given no key
  to recognise a repeat by (row 6.6).
- **D.** No record forbids issuing a seat or principal name again to a different entity (row 6.7).
- **D.** Wire, log and record formats carry no version (row 6.5).
- **D.** Nothing relates how long payloads are kept to how long a compromise may take to find (row 15.8), and no
  log is asked for below the membrane.
- **D.** The pattern ejects on a finding and cannot watch quietly; no record states that as a choice (row 17.4).
- **D.** Approval fatigue and routine use of the emergency path are not weighed (row 5.16).
- **D.** A deny list that can name a bundle revision, a tool or a release, and an ordered security version, are not
  considered and declined; they are absent (row 9.5).
- **R.** The gate on unsigned operator requests is a list of what to refuse, ending in a wildcard (row 11.3).
- **R.** The consensus replica's `mutation` switch is compiled in unconditionally (row 12.4).
- **R.** Epochs, rounds and log indexes are one integer type under four names, and a digest is an unvalidated
  public string that reaches a path join (row 12.5).
- **R.** No generated-input test of any parser, with `expect` calls in the path every replica applies (row 13.5).
- **R.** Secrets travel on the command line and in a `Debug` form (row 12.3); the compiler, the policy compiler
  image and `cedar-policy-cli` are unpinned (row 14.9).
- **R.** The two bundle engines are never run against the same inputs (row 11.2).
- **C.** Twenty-one recovered records cite private sessions that the repository excludes (row 15.1).
- **C.** The conformance checklist omits three values the guide says must be declared (row 16.5).
- **C.** On a shallow clone `tools/verify-manifest.sh --all` fails with a `tar` error and no hint (§9).

---

## 8. Where TOPAK goes beyond the book, and where the book stops

### 8.1 Beyond

Places where the corpus does more than the book asks, each with the chapter it outruns. Status is as the rows
above give it: author-ratified, and for the operator and the emergency seating, provisional.

| What | Against | Where |
|---|---|---|
| **The adversary is inside by premise.** The book's insider is trusted and fallible, and its AI attacker is a prediction. Here every agent is hostile at every position and no guarantee depends on what a model means | 2, 3, 5 | ADR-0007; ToO §1 |
| **Failure direction is an admission rule.** A component whose failure can add authority, and whose identity nothing fixes, is refused entry to the trusted base; one relied on and trusted for nothing gets a row so that what rests on it is computed void | 6, 8 | ADR-0045 §2, §3 |
| **The trusted base includes the verifiers and the people**, and a known defect in the prover is written against the prover's row and stated as a non-claim | 6, 11, 13 | ADR-0045 Annex A; ADR-0046 A2 |
| **The direction of a policy change is computed, and the computation is checked.** Neither the author nor the solver can pass a relaxation off as a tightening | 5, 7, 14 | ADR-0030 §5, A1 |
| **Non-vacuity at every layer.** Every property has a mutation that must break it, in the specifications, the consensus tests, the gates and the corpus's own checkers | 13, 16 | ADR-0046; CR-57 |
| **Proof, twice, with its limits stated.** The book gives formal methods two pages | 6, 13 | ADR-0046; ADR-0053; G11 §8 |
| **A deployment's guarantees are computed from what it declares.** A departure from the archetype names the theorems it loses | 4, 8 | ADR-0023; `spec/inventory.py` |
| **Clocks buy liveness and never safety**, stated as a rule, with the arithmetic proved of a transcription | 9 | ADR-0032 |
| **Response time is a term of the safety argument**, and where no budget fits the effect is removed from the alphabet | 16 | ADR-0032 §4 |
| **A stop that is ordered before it acts.** An admit decided before a revocation and committed after it is void | 3, 17 | ToO §4.1; ADR-0015 |
| **A quarantine nobody can lift by mistake**, and a temporary privilege with no renewal | 18 | ADR-0031 §5; ADR-0052 §3 |
| **A drill that is a real activation**, on the same log, counted without a clock | 9, 16 | ADR-0052 §6 |
| **Refusals are evidence by rule**, including what a principal goes on trying after it is stopped | 5, 15 | ADR-0020; ADR-0003 A2 |
| **Erasure is a modelled, ordered event**, proved not to combine with the emergency path into an act nobody answers for | 15 | ADR-0006; ADR-0028; NC-1, NC-2 |
| **Non-claims as a standing section.** Every checkpoint ends with what it does not claim, and the residual-risk statement is written for the acquirer | 1, 17, 21 | G11 §8; residual-risk statement |

### 8.2 Where the book stops

The book was published in 2020 by a company that operates its own systems at scale. Four things follow for anyone
using it as a measure of TOPAK.

- **It has no principal that is a model.** Nothing in it bears on the corpus's central decisions: that semantic
  judgment never admits, that labels bound what an injection can reach, that a monitor may collude with what it
  watches. Chapters 3 and 5 are the nearest, and they assume the client means well.
- **It assumes an organization.** Teams, an on-call rotation, a security function, leadership to persuade. Much of
  Part V has nothing to land on in a project of one, and the marks there say so. They would change the day a
  second person joined, without a line of the corpus changing.
- **It measures practice, and the corpus is mostly argument.** The book's standards are met by doing something
  repeatedly. A design can only require them, and most of the G marks on plane D are places where the pattern
  could ask a deployment for a practice and does not.
- **It does not ask whether a guarantee is true.** Nothing in the book would have found the questions the
  critical reviews spend most of their length on: whether a proved property says what its record says. The two
  kinds of reading find different things and neither replaces the other.

---

## 9. What was verified, and how

Run by the lead on 2026.11.12 against the tree at `981bc77`, on Linux x86_64, in a fresh clone. Nothing in the
tree was changed by any of it.

| Check | Command | Result |
|---|---|---|
| Every manifest at the commit it measured | `tools/verify-manifest.sh --all` | **30 of 30 OK** (`SHA256SUMS-G1` to `-G11`, eighteen reference cuts, one rehearsal cut), with full history fetched. On the shallow clone a cloud session starts with, the script prints `fatal: not a valid object name` and a `tar` error for the first commit it cannot find, and stops |
| Every cited path | `python3 tools/check-refs.py` | **Exit 1: 34 missing paths, 113 date tokens.** Most of the 34 are tool directories that are installed and not tracked, and four are in the skills' reference files. One is G11 citing a file it says was removed. The checker has an allowlist for known stale citations, and it has not been kept at zero since the last cut |
| The reference's tests | `cargo test --workspace --release --no-fail-fast` (rustc 1.97.0), without rebuilding the bundle | **154 of 155 pass. `pinned_records_have_not_drifted` fails**: `decisions/ADR-0054.md` and `decisions/ADR-0055.md` no longer match `mechanism/corpus-pins.sha256`. Both were revised in `fec5c44` (2026.11.11, R7 and R3, citing the new proofs by digest), after the pin the 11.11 review read (`bbda621`), where all 155 passed. The test did what it was written to do. Nothing ran it |
| Static analysis of the reference | `cargo clippy --workspace --all-targets --release` | Exit 0, **three warnings** in the workspace's own code (a complex type, a large enum variant, a field assigned after `Default`) |
| One module's model check | `spec/coupling-run.sh` for `Safe` with no mutation, and for `M_NOCOUPLE` and `M_MARK` | Holds at 1,124 distinct states, as `Coupling-results-2026.09.29.txt` records; both mutations give a counterexample. The state count at a counterexample differs from the results file for `M_MARK` (71 against 84), which is the run's worker count and not the verdict |
| The bundle loader against a swapped tarball (SRS-12) | A scratch program outside the tree, linking `topak-bundle` and `topak-core` by path, on the tracked bundle `3e98ed17…`: sign the revision as the tests do, load; replace the tarball with one whose `data.json` or `policy.wasm` differs and whose `.manifest` is unchanged, leave the signature, load again | **Accepted both times.** `1. genuine tarball: verified=true search@d3 target=Some("search.internal:443")` · `2. swapped data.json: verified=true search@d3 target=Some("elsewhere.example:443")` · `3. altered policy.wasm: verified=true` |
| Review and checks on pull requests | The GitHub API, for `scottcochran/TOPAK` | 45 pull requests, all opened by the custodian's account; 44 merged, half within 71 seconds of opening and none open longer than 52 minutes. Four sampled (8, 12, 22, 37) have no review; two sampled (37, 45) have no check run. The repository has no `.github/` directory |
| Whether the repository is public | The session's repository listing | Public |

**Not run.** The TLAPS proofs, the proof scan, the Lean packages, the Cedar gates and the Rego tests (none of
`tlapm`, `lean`, `cedar`, `cvc5` or `opa` is installed here, and the pinned prover binary is not obtainable from
upstream by the pin file's own account); the other TLA+ modules; trace validation; the lineage rehearsal;
`cargo audit` or any other dependency scan. What is said of those rests on the results files and on the 11.11
review, which ran the manifests, the sync checks, TLC over ten modules, the tests, trace validation, the Rego
tests and the Cedar gates at `bbda621`.

---

## 10. Suggested entries, none made

In the order the 11.11 gaps prioritization would take them: what costs hours and is checked by a machine first,
decisions next, design last. "With" names the item of that plan an entry would sit beside. Every entry is the
custodian's to take, change or decline.

| # | Entry | Where | For | With |
|---|---|---|---|---|
| 1 | **Re-pin or register.** Read `fec5c44`'s changes to ADR-0054 and ADR-0055 against the reference, then re-pin, as the failing test's own message says | `mechanism/corpus-pins.sha256`; an ADR-0033 addendum, which CR-55 already owes for `8ec1a34` | SRS-16 | item 2 (the cut) |
| 2 | **One workflow file.** On every push: the manifests, the cited paths, the reference's tests with the drift test, the Rego tests, the two sync checks and the small-constant TLC runs, each failing with a non-zero status. The 09.30 proposal's sentence, taken up | `.github/workflows/`; `tools/check-refs.py`'s allowlist brought to zero first | SRS-16; CR-57; CR-41 | item 8, widened |
| 3 | **Bind the bundle's bytes.** The signature covers a digest of what loads (the tarball, or `policy.wasm` and `data.json`); the loader recomputes it; one more case in `fallback.rs`, a swapped tarball under the genuine signature, refused. G7 reopened until then, and D-0044-1's "no longer its position" struck | ADR-0044 §2, an amendment; `topak-bundle`; `mechanism/GAPS-AND-ASSUMPTIONS.md` | SRS-12; inventory finding 11 | item 4 (an erratum batch) |
| 4 | **Three reference defects, each with the test that shows it.** A restart that must not refresh a lease or a heartbeat; a log that truncates its torn tail before appending, with a two-restart test; a row saying which records are best-effort | `mechanism/`; `GAPS-AND-ASSUMPTIONS.md` | SRS-13; SRS-14; SRS-15 | after item 2 |
| 5 | **A sentence in `SECURITY.md`**: what a reporter does, and after how long, if nothing is heard; and where a second copy of the session history and the pinned prover is kept | `SECURITY.md`; `process/README.md` | SRS-18 | item 1 (the reader) |
| 6 | **Sign the cut.** Manifests and checkpoint tags signed under a key whose custody is declared, as the pattern asks of a bundle. A page on the corpus's own change path, link by link | `manifests/README.md`; ADR-0029 | SRS-17 | item 2 |
| 7 | **Record the refusals, and bind the approval.** A control request refused at decide is written to the operator's topic or its companion; an activation names its seating by digest | ADR-0050 §6; ADR-0052 §2, §5; `mechanism/` I47, I48 | SRS-8; SRS-9 | the exits from provisional |
| 8 | **An incident-response block in the declaration.** Who is told by what signal; `D` per effect class; severity classes for a finding; the drill and exercise periods; a named investigator and auditor; a postmortem owed. The checklist gains the three values it omits | Adopter's Guide §9; ToO A5, split into items that can be checked | SRS-6; CR-17 | a decision |
| 9 | **The return path from each stop**, as one open-list item naming the five: after a fence, a revocation, a quarantine hold, a bad promotion, and the loss of the log or the anchor | the next checkpoint's open list | SRS-7; SF-6; SF-12; G12; G17 | item 2 |
| 10 | **A position on availability's adversary.** Who can stall what, for how long; a bound on refusals in an open round, as ADR-0003 A2 bounds them after the seal; a retry discipline beside A18; whether a subtraction is ordered ahead of an admit | an ADR-0045 annex or a record of its own; ADR-0003 A2; ToO A18 | SRS-2 | a decision |
| 11 | **Try and undo.** A candidate floor or bundle may be evaluated in report-only mode; a promotion may name its predecessor, and returning to it within a declared window is not a relaxation | beside SF-6's `proposed:StagedPromotion`; ADR-0030 §5 | SRS-3; SRS-4 | a decision |
| 12 | **A life cycle for keys.** A rotation interval and a rehearsal per issued key, in epochs; what an issuance that replaces a bundle key does to revisions verified under the old one; a trusted-base row for where each key is held and approved from | ADR-0025 open obligations; ADR-0044; ADR-0045 Annex A | SRS-5 | a decision |
| 13 | **Name the adversaries of the archetype**, as ADR-0068 does for the overlay, people included | a record, or an annex to ADR-0045 | SRS-1 | after item 3 of the plan |
| 14 | **A reader test.** A person who is not the drafter answers a fixed set of what-is-in-force questions from the guides alone; a generated page, *in force at this cut*; no new identifier family reuses a letter | the next checkpoint's conventions | SRS-19; CR-47 | item 1 |
| 15 | **Ask the target.** Each target a Run entry's channel names accepts connections from the tool host only; where it does not, effect exclusivity holds for confined principals only | ToO §13, an assumption of use; Adopter's Guide §4.7 | SRS-11 | a decision |

Entries 1 to 6 add no design and are days of work between them. Entry 3 is the only one that changes what a
record in force says is closed.

---

## 11. What this does not claim

- **It is not a record, and nothing in it is ratified.** A mark is a reading. A finding is suggested, and none is
  dispositioned. `SRS-n` is minted here and continues no other series.
- **It is not the review ADR-0029 A2 asks for**, and it changes nothing on the A2.5 line. It was prepared by Claude
  at the custodian's request, with five readers of the same lineage, which is the lineage that drafted most of
  what it reads. A finding here was looked for in the corpus's lists by the lineage that wrote the lists.
- **It does not say the book is the right measure.** The book describes one large operator's practice in 2020. A G
  on plane D means the book asks for something and the pattern does not; whether the pattern should is a decision.
  §8.2 says where the book has nothing to offer.
- **It does not grade the corpus.** The tallies in §0 count rows this document chose to write. They are a map of
  where the gaps are, by plane, and not a score.
- **The reference's defects were read, and one was run.** SRS-12 was reproduced as §9 describes. SRS-13, SRS-14 and
  SRS-15 are from reading the code and were not exercised; §7.5's observations likewise.
- **It did not read everything.** The lead read in full: the README, both guides' cited sections, `SECURITY.md`,
  ToO §0, §1, §9, §10, §12 and §13, G11 §4 to §8, ADR-0052's decision, ADR-0045 §1 to §3, the residual-risk
  statement's first part, the gaps prioritization, and SF-1, SF-2, SF-3 and SF-6. The rest was read by the five
  readers and reaches this document through their citations, of which the lead re-read those behind every `SRS-n`
  and the marks a finding rests on. The glossary and the architecture description were searched and not read. The
  command-chain overlay (ADR-0059 to ADR-0068) was read only where a row cites it.
- **It says nothing about the hosting service's settings** beyond what §9 lists: whether the default branch is
  protected, whether private vulnerability reporting is switched on, or whether any report has been received.
- **Nothing in the tree was changed** but this file and its row in `derived/README.md`. The failing drift test was
  left failing: re-pinning is the review's record, and the review is the custodian's.
