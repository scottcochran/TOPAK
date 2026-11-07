# The AI use cases that carry 80% of usage, and how each would manifest in a TOPAK deployment

**2026.11.05** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
Genesis Checkpoint G11 (`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`), Theory of Operation revision 15
(`narrative/theory-of-operation.md`) and the Adopter's Guide draft of 2026.10.09, at the tree after `147bc72`
(Batch 39). Nothing in Batches 38 and 39 bears on what follows

**The question.** Which AI use cases make up the top-p nucleus at p = 0.8, the smallest set of use cases whose
combined share of usage reaches 80%? And what would each look like as a TOPAK deployment: which domain, which
alphabet variants, which floor forbids apply, and what the pattern does and does not add?

**The answer, in one paragraph.** At p = 0.8 the nucleus is four things: **practical guidance, information seeking,
writing and coding**. The first three make up the consumer nucleus, and coding dominates professional and API use.
TOPAK states its guarantees over effects, not over content (`narrative/architecture-description.md` §10.1: *Valid*
and *Accurate* are out of scope by premise). So the three consumer use cases, about 78% of consumer traffic, meet the
pattern mostly as `Consult` and `Report`, and gain attribution and a record. The pattern's machinery does its work in
two places: **coding, which is Build**, where the corpus places the Byzantine threat (ToO §1, "the inversion"), and
**office and administrative automation, which is Run with outward `Actuate`s**, where the label forbids R5 to R7 are
built for exactly the injection-and-exfiltration path that automation creates.

**Basis.** Every claim about the pattern below cites the record or narrative section it comes from, and adds no
design. Status words are the corpus's own: ADR-0054 and ADR-0055 (workflows) and ADR-0035 (lineage) are **Proposed**,
and nothing resting on them binds a deployment; ADR-0040, ADR-0047, ADR-0048 and ADR-0049 are Accepted (genesis) and
author-ratified (ToO §0).

---

## 1. The nucleus

### 1.1 Method

The use cases are ranked by share of usage and accumulated until the running total first reaches 0.8, the
nucleus-sampling rule borrowed as an analogy. Two populations are kept apart because their published taxonomies differ
and cannot be added together: consumer chat, classified by conversation topic, and professional use, classified by
O\*NET occupational group.

### 1.2 Consumer chat

Source: Chatterji et al., *How People Use ChatGPT*, NBER Working Paper 34255, September 2025. The abstract states
that the three most common topics together account for nearly 80% of conversations. The per-topic shares below come
from secondary coverage of the paper and are approximate.

| Rank | Use case | Share | Running total |
|---|---|---|---|
| 1 | Practical guidance: how-to, tutoring, advice, ideation | ~29% | ~29% |
| 2 | Seeking information: a close substitute for web search | ~24% | ~53% |
| 3 | Writing: mostly editing, critiquing, summarizing and translating text the user supplies | ~24% | **~78%** |
| 4 | Multimedia | ~7% | ~85% |

The three-topic cut is the nucleus in all but rounding; multimedia carries the total past 0.8. Coding is a small share
of consumer chat, around 4%.

### 1.3 Professional use

Source: Anthropic Economic Index reports, 2025 to early 2026, by O\*NET group on Claude.ai. Figures move between
reports and are approximate; the per-group shares here were read through secondary summaries in this session, not
from the reports themselves.

| Rank | Domain | Share | Running total |
|---|---|---|---|
| 1 | Computer and mathematical: software development and debugging | ~34–37% | ~37% |
| 2 | Educational instruction and tutoring | ~9–15% | ~50% |
| 3 | Arts, design, media and writing | ~8–10% | ~59% |
| 4 | Office and administrative support | ~8% | ~67% |
| 5 | Life, physical and social science | ~7% | ~74% |
| 6 | Business and financial operations | ~6% | **~80%** |

On the first-party API, computer and mathematical tasks reach the mid-40s by themselves, and coding work has been
moving from chat to the API as agentic coding tools split it into many smaller calls.

### 1.4 The combined nucleus

| Use case | Consumer nucleus | Professional nucleus |
|---|---|---|
| Guidance and tutoring | Rank 1 | Rank 2 (education) |
| Information seeking and research | Rank 2 | Rank 5 (science) |
| Writing and editing | Rank 3 | Rank 3 (arts, media) |
| Coding | Outside | Rank 1 |
| Office and administrative automation | Outside | Rank 4 |
| Business and financial analysis | Outside | Rank 6 |

§3 reads all six, because the professional nucleus is where agents, rather than chat, are deployed.

---

## 2. The vocabulary the mapping needs

- **Two domains.** `Build` produces artifacts; `Run` operates them (ToO §1). No alphabet variant name is shared
  between them (ADR-0022 A2; ToO §2.9).
- **Build's alphabet** (ADR-0022; ToO §2.4): `Read` inside the pinned corpus root, `Draft` into a round-scoped
  workspace, `Invoke` a tool allowlisted by name and digest, `Emit` to the round topic, `Submit` the sealed workspace
  or abstain, and `Vote`. A Build artifact leaves only by promotion, and the author cannot vote on it. No shell, no
  network, no package installation, no git.
- **Run's alphabet** (ADR-0040; ToO §2.9): `Consult(ref)` is ingress from the pinned, content-addressed Run root, with
  no effect. `Actuate(tool, inputs)` invokes an allowlisted tool whose entry declares the channel it opens.
  `Report(record)` emits to the principal's own round topic. **A read of live state is an `Actuate`**, however
  read-only it is.
- **The cell** (ADR-0037; ToO §2.8): the principals seated around one Thinker for a round. Every Thinker is coupled
  to an Observer, which may deny, quarantine or evict and may never admit (ADR-0007).
- **Labels and handles** (ADR-0047; ToO §2.10): every ingress item is labelled by its source, with `untrusted` and
  `restricted` reserved. An item is delivered **clear**, as bytes with their label, or as a **handle**, a name with no
  bytes that the Thinker can pass to a tool without reading it. `clearSet`, the join of the labels delivered clear
  this round, only grows.
- **The three label forbids**, on an `Actuate` of an **outward** entry, one whose channel reaches a target the issued
  rules do not list as inside the deployment:
  - **R5**, read then send: `clearSet` holds `untrusted`, and `restricted` is in `clearSet` or in an input handle.
  - **R6**, steered destination: `clearSet` holds `untrusted`, and a destination input is a literal.
  - **R7**, replayed content: a destination input is a handle labelled `untrusted`.
- **Tool interfaces** (ADR-0048, ADR-0049): a Thinker learns its tools from the mechanism. Each allowlist entry's
  purpose text passed promotion and is the round topic's opening record. An outward entry's result must be labelled
  `untrusted`, or the bundle does not load.

---

## 3. Each use case as a deployment

Every row below is a configuration of the pattern as the records state it, not a new design.

### 3.1 Practical guidance and tutoring

**Shape.** A Run cell whose task is the learner's or user's question. The Thinker `Consult`s a pinned knowledge base
(course material, a policy handbook, product documentation) in the Run root and answers with `Report`. No `Actuate`
is needed, so the allowlist can be empty.

**What the pattern adds.** Attribution per lease, a sealed per-round topic with its erasure unit (ADR-0003, ADR-0005),
and an Observer reading what was delivered and what was said. A tutoring session that spans turns is a sequence of
rounds, not one persistent agent: a lease is one round (ADR-0031 §2).

**What it does not add.** Whether the advice is right. *Valid* and *Accurate* are out of scope by premise
(`narrative/architecture-description.md` §10.1). An injection that only changes what a `Report` says is not covered
(ToO §2.10, "What this does not cover"). A judgment that an answer is wrong can only be an Observer finding, which may
subtract authority and never add it (ADR-0007).

**Reading.** This is the largest use case and the one where the pattern contributes least. A deployment would adopt
TOPAK for guidance only as one face of a deployment that also acts.

### 3.2 Information seeking and research

**Shape.** Two forms, and the difference matters.
- **Pinned retrieval.** The corpus is content-addressed in advance in the Run root and reached by `Consult`. Its label
  is whatever the root's declaration says, and nothing outward is touched.
- **Live search, live databases, live APIs.** Each is an `Actuate`, because a read of live state leaves the membrane
  (ToO §2.9). A web search entry is outward, and its result must be labelled `untrusted` (ADR-0049).

**What the pattern adds.** Once a search result is delivered clear, `clearSet` holds `untrusted` for the rest of the
round. From then on, R6 refuses any outward call whose destination the Thinker typed as a literal, and R5 refuses any
outward call while `restricted` content is in play. A research deployment that keeps outward options open delivers
search results as **handles**: the Thinker can route them to a summarizer or a store without reading them, and the
round stays narrow only where it read (ToO §2.10, "delivering more in the clear buys a narrower round").

**Research over sensitive data** (science, business and financial analysis). Datasets labelled `restricted` in the
Run root, or query results from an inside `Actuate` entry labelled `restricted`, cannot flow to an outward entry in a
round that has also read untrusted content (R5). The Observer reads every fact, including suppressed bytes, and the
`Actuate` record holds inputs, result, labels, delivery mode and `clearSet` as it stood (ADR-0042; ToO §2.10).

**What it does not add.** Whether a source is truthful. A label is a declaration, and an inside source wrongly
labelled trusted that carries an attacker's text is seen by nothing (ADR-0047 §9; Adopter's Guide §8.1 k).

### 3.3 Writing and editing

**Shape.** Three cases, by where the writing goes.
- **Drafting for a person.** The user's text arrives as the task, labelled by whoever issues the grant, or by
  `Consult`. The result is a `Report`. This is §3.1's shape.
- **Writing that becomes a governed artifact:** a policy, a specification, a published document, a bundle's tool
  description. This is **Build**: `Read` the pinned corpus, `Draft` into the workspace, `Submit`, and a quorum `Vote`
  in which the author is refused by the `Vote` envelope (floor forbid B7; ToO §2.4). This corpus's own records are
  written this way, under ADR-0029.
- **Writing that is sent:** an email, a post, a reply in a ticket. The send is an outward `Actuate` and falls under
  R5 to R7 (§3.5).

**Arts, design and media.** Image or video generation is an `Actuate` on an entry whose channel is declared and,
under a Wasm tool, bound by the tool host to that one target (ADR-0034 A2; ADR-0049 §5). Nothing judges the content.

**What it adds.** For the promoted case, separation of duties between author and approver, which is per seat and
does not see through a person who holds two (ToO §2.8). For the sent case, the label forbids. For pure drafting,
attribution only.

### 3.4 Coding

**Shape.** Code that ships is **Build**.
- The Thinker `Read`s a content-addressed snapshot of the repository inside the pinned corpus root, `Draft`s changes
  into the round-scoped workspace, and `Invoke`s compilers, linters and test runners allowlisted by name and digest.
  Packaged as Wasm components, they are hermetic by construction (ADR-0034 P4). A native tool is a declared
  degeneracy (D-0034-3).
- It `Submit`s the sealed workspace, or abstains with `Submit(⊥)`, and a quorum of `grant` seats votes with evidence
  under a rules epoch. The author cannot vote.
- **Deploying the result is Run**, an `Actuate` on a deployment tool, in a separate domain with a separate alphabet.
- A plan, implement, review and test pipeline is a promoted **workflow** (ADR-0054, Proposed): a node per round of one
  cell, edges with guards over settled attributes, and an orchestrator that may only choose among edges the mechanism
  has already enabled. A loop that runs until the tests pass is a **mesh** under an activation budget (ADR-0055,
  Proposed).

**What it adds.** The most of any use case. The corpus places the Byzantine threat in Build, because Build agents
author what Run is later judged against (ToO §1). Moon & Varshney's failure, silent abstention, a vacuously true
predicate and green gates, is a Build failure, and the totality, non-vacuity and discrimination gates exist for it
(ToO §2.2). A coding agent under TOPAK cannot install a package, reach the network or push to a remote. Its only exit
is promotion.

**What it costs.** The corpus says it plainly: "This is not how agents write code today: no shell, no package
installation, no network, no git" (ToO §2.4). Dependencies must be inside the pinned corpus root before the round
starts. A crashed round loses its work (Adopter's Guide §7.11). A coding harness that gives the agent a shell makes the
agent `Mediated`: attributed and authorized, not contained, and outside every containment theorem (ToO §2.3). Every
principal at the reference is `Mediated` today, because the lineage criterion (ADR-0035) is Proposed.

### 3.5 Office and administrative automation

**Shape.** Run cells whose `Actuate` entries reach email, calendar, ticketing, CRM and document stores. Each entry
declares its one channel target, read from the allowlist entry in the bundle revision the lease names (ADR-0049 §5).
Reading a mailbox is an outward `Actuate` whose result is labelled `untrusted`, and the mailbox's own contents may
also carry `restricted`.

**What it adds.** This is the case the label forbids were built for. The canonical agent injection is a message in
the inbox that tells the agent to forward something sensitive somewhere.
- If the agent read the message clear and then calls an outward send while `restricted` content is in its `clearSet`
  or among its input handles, **R5** refuses.
- If the message named the destination and the agent typed it as a literal, **R6** refuses.
- If the agent passed the message's own handle as the destination, **R7** refuses.

None of this depends on the model resisting the injection. A defence inside the Thinker lowers how often an
injection succeeds, and the labels bound what a successful one can reach (ToO §2.10; Adopter's Guide §8.1 l). The
Observer is handed the same tool list its Thinker was handed and can judge a call against the tool's stated purpose
(ADR-0048).

**Irreversible effects.** A payment, a contract signature or a mass send may be irreversible on emission. ADR-0032's
budget, `W + L + D < T_irrev`, is declared per effect class, and where no budget fits, **the effect must not be
expressible in the alphabet at all** (ToO §10; assumption A10, ToO §13). An office deployment would either put such
an effect behind a promoted workflow edge or a human seat, or leave it out of the allowlist.

**What it does not add.** Protection against a wrong declaration: a source that is outward but declared inside, or an
entry whose channel is misdeclared for a native tool (D-0034-5, D-0034-6). Flow traced value by value: `clearSet`
bounds the round, not a value. Protection between cells that no workflow joins (ADR-0051 finding 2).

---

## 4. What every one of them costs

These follow from the records whatever the use case, and an adopter should state them before a user meets them.

| Cost | Consequence for the use cases | Source |
|---|---|---|
| A lease is one round | No agent memory across rounds. A tutoring or coding session is a sequence of rounds or a workflow | ADR-0031 §2; Adopter's Guide §8.1 g |
| No delegation | No agent spawns another. Sub-agents are seated only by promoting a workflow | ADR-0054 §2 ⟨Proposed⟩; Adopter's Guide §8.1 h |
| No choreography | Agents never address each other; the mechanism is the bus | ADR-0055 §7 ⟨Proposed⟩ |
| A crashed round ends | Work is lost; size rounds to what can be lost | Adopter's Guide §7.11 |
| Every admit is a consensus round, with no compaction | Interactive, low-latency chat is not a design goal | ADR-0033 §6; Adopter's Guide §8.1 o |
| Stall, not proceed | An Observer that is dead or behind stops its Thinker's effects | Adopter's Guide §7.1 |
| People are seats | Reviewers, operators and break-glass users each hold one seat, and the human budget `D` must be staffed | ToO §2.8, §7.10; Adopter's Guide §7.9 |
| Not deployable today | No release, and no principal is `Contained` | `derived/topak-residual-risk-statement-2026.10.09.md` §6 |

---

## 5. Where the pattern's value concentrates

| Use case | Domain | Outward `Actuate` | R5–R7 apply | Build promotion | Value of the pattern |
|---|---|---|---|---|---|
| Guidance and tutoring | Run | Rarely | Rarely | No | Low: attribution and record |
| Information, pinned | Run | No | No | No | Low |
| Information, live | Run | Yes (search) | Yes, via `untrusted` | No | Medium: bounds what a poisoned result can steer |
| Writing for a person | Run | No | No | No | Low |
| Writing as an artifact | Build | — | — | Yes | High: separation of duties |
| Writing that is sent | Run | Yes | Yes | No | High |
| Coding | Build, then Run to deploy | At deploy | At deploy | Yes | **Highest**, and costliest |
| Office and admin | Run | Yes | Yes | Workflows ⟨Proposed⟩ | **High**: the injection path the forbids were built for |
| Analysis over sensitive data | Run | Sometimes | Yes, via `restricted` | No | High |

**Reading.** The usage nucleus and the pattern's value nucleus barely overlap. By traffic, most AI use is reading and
answering, and TOPAK's guarantees there are nearly empty, by design, because they are stated over effects. By risk, the
use cases that matter are the ones that author what is later trusted (coding, governed writing) and the ones that act
outward on content an attacker can write (office automation, live research). Those are a minority of traffic and the
majority of what the pattern is for.

---

## 6. Suggested entries, none made

1. **Adopter's Guide, a second worked example:** an office-automation Run cell (mailbox read, outward send, a
   `restricted` document store), with its allowlist entries, its label table and the R5 to R7 refusals walked
   through. The guide's only worked example today is the reference's declaration (§2.3).
2. **Adopter's Guide §8.1, a position row:** that a deployment adopting the pattern for `Consult`-and-`Report` use
   alone inherits attribution and a record and nothing that bounds content, citing
   `narrative/architecture-description.md` §10.1.
3. **A Build-domain note on dependencies for coding:** where a coding round's package set comes from when `Read` is
   bounded by the pinned corpus root and there is no network. No record states the pinning workflow for third-party
   code. It is the first question a reader who has used a coding harness will ask.
4. **The next external-alignment document** (`derived/`): a row reading usage-share data as context for which
   assumptions of use matter most in practice, beside the Playbook's MAP subcategories.

---

## Sources

- Chatterji, A., et al., *How People Use ChatGPT*, NBER Working Paper 34255, September 2025:
  https://www.nber.org/papers/w34255 (abstract read; per-topic shares from secondary coverage)
- Entrepreneur, *Here's How People Are Actually Using ChatGPT, According to OpenAI*:
  https://www.entrepreneur.com/business-news/heres-how-people-are-using-chatgpt-openai-study/497193
- Gizmodo, coverage of the NBER paper: https://gizmodo.com/openai-how-people-use-ChatGPT-2000658906
- Anthropic Economic Index reports (September 2025; January 2026), read through secondary summaries:
  - eWeek, *Anthropic's AI Usage Study: Coding Still Dominates*: https://www.eweek.com/news/anthropic-economic-index-claude-ai-usage/
  - Business Data Solutions AI wiki, Q4 2025 summary: https://businessdatasolutions.github.io/ai-wiki/sources/2026-04-28-anthropic-economic-index-q4-2025
  - Business Data Solutions AI wiki, report 5 (March 2026): https://businessdatasolutions.github.io/ai-wiki/sources/2026-05-07-anthropic-economic-index-5-learning-curves
- Corpus: `narrative/theory-of-operation.md` §0–§2.11, §10, §13; `narrative/architecture-description.md` §10.1;
  `derived/topak-residual-risk-statement-2026.10.09.md`; the Adopter's Guide (2026.10.09 draft) §1, §3, §7, §8;
  ADR-0007, ADR-0022, ADR-0031, ADR-0032, ADR-0034, ADR-0037, ADR-0040, ADR-0042, ADR-0047, ADR-0048, ADR-0049, ADR-0054,
  ADR-0055
