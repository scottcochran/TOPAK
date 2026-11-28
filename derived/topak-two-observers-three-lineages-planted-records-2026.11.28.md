# Two Observers per cell, three lineages and planted records: a design sketch against the colluding Observer

**2026.11.28** · a design sketch, not a record · prepared at the custodian's request · read against the tree at
`231ca68` (G12 the state of record; ToO revision 16), with Proposed records cited as Proposed

**The custodian's choices, taken as given.** Five, from the session of 2026.11.28: two cell Observers in every cell;
two correlators in every domain; three lineages, so that a Thinker and its two Observers are pairwise independent;
admission coupled to both cell Observers and not to either; and planted records in Run. This document works those
choices through the records. It does not argue for them against alternatives, and where it found a choice inside
one of them it lists the choice in §8 and does not make it.

**Sources.** In the corpus: ADR-0007, ADR-0016 §5, ADR-0017, ADR-0035 §§2 to 7 and 9, ADR-0037 D-0037-1, ADR-0038
§§2 to 7, ADR-0039 §§1 to 8, ADR-0043 §4, ADR-0051 §§1 to 3, 6 to 10, Consequences and Findings; `derived/`'s
Schelling reading of 2026.11.13 (§§3, 4 and 8) and the scenario inventory's SF-17. Outside the corpus: nothing was
fetched. Greenblatt et al. is cited through the 11.13 reading's §4 and was not re-read. Nothing was modelled, checked
or built. Nothing in the tree changed except this file and its row in `derived/README.md`.

**Not independent.** The drafter is of the corpus drafter's lineage. The 11.13 reading's head says why that is the
correlation in question, and it applies here unchanged.

---

## 1. What is proposed, against what stands

| Element | What stands | Proposed here | Record, and its standing |
|---|---|---|---|
| Cell Observers | "One cell Observer per cell is the archetype value"; more is a deployment choice | **Two in every cell** | ADR-0038 §5, Accepted |
| Lineages | "two lineages with separate corpora and separate architecture ancestry" | **Three**, pairwise independent | ADR-0017, Accepted; the criterion is ADR-0035 §3, Proposed |
| Coupling in Run | An admit "requires `live(o)` for at least one cell Observer `o` in its cell" | **`live(o)` for every cell Observer seat declared for the cell** | ADR-0039 §2, Accepted |
| Correlators | Two or more; one is the degeneracy D-0051-2 | **Two, of different lineages** where they hold a model | ADR-0051 §9, Proposed |
| Planted records | "Honeypot validation at seat admission (LP-4) is not decided anywhere" | **Planted in Run, all the time**, with a fold `planted-past` | ADR-0039 §5; no record decides it |

The watched-by relation of a Thinker `p` becomes `W(p) = {o1, o2, c1, c2}` (ADR-0038 §2). Findings still combine by
any-of (ADR-0038 §5), still only subtract (ADR-0007), and no correlator is coupled (ADR-0039 §4). None of that
changes.

## 2. What a colluder now has to do

ADR-0039 §5 states the open case: "A colluding Observer sends heartbeats, reports a watermark, and finds nothing,
and all three are its own assertions." The table reads each form of it against the design.

| Case | Today | Under this design | What decides it |
|---|---|---|---|
| One cell Observer silent, the other honest and able | Open: there is one | **Closed.** The honest finding blocks the next admit by any-of, and the silent seat has a miss | ADR-0038 §5; ADR-0051 `marked-past` |
| The honest Observer is killed, partitioned or starved, the colluder stays live | Not a case: there is one | **Closed only by coupling to both** (§4). Under "at least one" the colluder's own heartbeat keeps the cell admitting | ADR-0039 §2 as amended here |
| Both cell Observers silent, on everything | Open | **Caught by planting**: each marks past a planted record with no finding | `planted-past` (§5) |
| Every watcher silent on a real defect, each flagging what is planted | Open | **Open.** It needs a way to tell planted from real: a signal from the Thinker, or a tell in the plant | §6; the 11.13 reading §4 |
| All three lineages let the same class of defect pass, with no message | Open | **Open, and narrower.** Three lineages must share the focal point, and the suite must lack the class | ADR-0035 §7; the 11.13 reading §3.1 |
| A Byzantine watcher raises false findings | A false denial in its reach | **Worse.** Four seats can deny where two could | ADR-0038 §5; ADR-0051, Consequences |

Each of the three parts closes a row that the other two leave open. Two Observers give a second opinion and nothing
against a starved honest seat. Coupling to both closes that and nothing against two silent seats. Planting checks
silence against ground truth and needs no second opinion.

## 3. Three lineages

### 3.1 Three pairs, and one the criterion does not name

ADR-0035 §3's relation is "not transitive, since A ⊥ B and B ⊥ C say nothing about A and C, so every seat pair is
checked on its own." A cell with Thinker `t` and Observers `o1` and `o2` therefore has three pairs to check:
(`t`, `o1`), (`t`, `o2`) and (`o1`, `o2`).

**The third pair is in no rule today.**

- ADR-0016 §5's seat distinctness is between the Observer's Persona and the Thinker's.
- ADR-0035 §5's declaration condition is over "every (Thinker, Observer) seat pair".
- Neither asks anything of two Observers in one cell. As the records stand, a second Observer of the first's lineage
  satisfies every rule.
- ADR-0051 §7 says what that is worth: "where the only other watcher is of the same lineage and misses the same
  things, there is no finding to miss against."

So the design needs seat distinctness and the declaration condition extended to every pair of seats in a cell.
ADR-0038 §5 already makes the benefit conditional on it: an added seat "can raise detection if its lineage is
independent".

### 3.2 What three costs under E1 to E5

- **E4** asks for "different `family` tags and different tokenizer digests". Three lineages need three architecture
  families and three tokenizers. ADR-0035 §8's rehearsal names a Llama-style model and "SSM or RWKV", so three
  families exist at rehearsal size. Whether three exist at a size where any is a usable Observer is not known here.
- **E3** asks for three corpora whose pairwise overlaps are each under θ. The θ values are unset.
- **ADR-0035 §6**'s correlated-miss test runs on three pairs, and its suite "must satisfy E3 against both lineages
  under test", which becomes all three.
- The 11.13 reading's suggestion 3, a focal-agreement measure, would also run on three pairs.

### 3.3 A workflow with three lineages

ADR-0035 §5 ⟨R8⟩ asks that Thinkers along a workflow's clear edges be independent, and notes: "With two lineages the
Thinkers along clear edges alternate, which a workflow whose clear edges are not bipartite cannot meet." With three
lineages the condition is that the clear-edge graph can be coloured with three colours, which admits odd cycles.
Each cell then takes its two Observers from the two lineages its Thinker is not. That rule is Proposed
(ADR-0054), and this reading did not re-read ADR-0054.

### 3.4 The correlators add a view, not a lineage

Take a cell with a Thinker of lineage A and Observers of B and C. Two correlators drawn from three lineages share a
lineage with at least one seat already in `W(p)`. Four watchers hold at most three lineages, and two if the
correlators are B and C. What the correlators add against collusion is therefore:

- **The cross-cell view**, which no cell Observer has (ADR-0038 §1).
- **The fixed folds**, which need no judgment, so one correlator's silence on a correlation is a miss the other
  counts whatever their lineages (ADR-0051 §2).
- **For any Thinker, a correlator not of its lineage**, wherever Thinkers are of more than one lineage (§3.3): two
  correlators of different lineages cannot both share the Thinker's.

**A facts-only correlator has no lineage to compare.** ADR-0051 finding 5: "A facts-tier correlator is a program
holding an `observer` seat", and no record says what a Persona with no model is. For such a seat E2 to E5 have
nothing to measure, as ADR-0035 §1 ⟨R7⟩ found for an operator. "Two independent correlators" then means two
implementations of the folds, and what makes two implementations independent is not written anywhere (§8, item 6).

### 3.5 What three lineages do not buy

ADR-0035 §7's residuals are untouched: unlabeled model text, shared human feedback, shared priors, and a shared
training stack. The 11.13 reading §3.1 reads the second and third as a coordination capacity. A third lineage makes
a common focal point less likely and does not remove it. No record measures by how much.

## 4. Coupling to both

### 4.1 The rule

Three clauses of ADR-0039 would read differently. Each is given as it stands and as it would read.

| Clause | As accepted | As it would read |
|---|---|---|
| §2, the admit | "requires `live(o)` for at least one cell Observer `o` in its cell" | requires `live(o)` for **every cell Observer seat declared for its cell** |
| §2, coverage across rounds | "granted only if a cell Observer's `mark(o, r)` is at or beyond the seal" | granted only if **every** cell Observer's mark is |
| §3, Build's promotion | "the author's cell Observer has a watermark at or beyond the seal" | **every** cell Observer of the author's cell has |

- **The quantifier is over declared seats, not leased ones.** If it ranged over the Observers that hold a lease, a
  seat whose lease lapsed would drop out and the rule would be "at least one" again. `live(o)`'s first condition,
  "`o` holds a live lease" (ADR-0039 §1), already makes an unleased declared seat not live.
- **The floor's text need not change.** `R3-observer-live` forbids when `!context.observerLive`. What changes is the
  lift that computes the field, from an exists to a for-all. It stays a syntactic lift over mechanism state
  (ADR-0007).
- **The pending workflow clause (ADR-0039 ⟨A3⟩) would follow**: an edge is enabled when every cell Observer of the
  node's cell has read to the seal.
- **The emergency seat is untouched.** It is not a `thinker` seat and is not coupled (ADR-0039 §2 ⟨A2⟩).

### 4.2 What it closes

Under "at least one", `UnreadBounded` reads: at most `K` of a Thinker's emissions are unread "by an Observer that
has reported in within `T_obs`". With two Observers that is satisfied by whichever is further ahead. An adversary
who holds one Observer and can starve the other leaves the bound true and the honest seat arbitrarily far behind.
With coupling to both, the bound holds **for each** cell Observer: at most `K` unread by the slower one.

The same reasoning is why Build's coverage should follow (§4.1's third row). A promotion that needs one Observer's
coverage can be met by the colluder's.

### 4.3 What it costs, and one accepted sentence it reverses

ADR-0039 §6 says of availability: "The cell's availability is the product of its Thinker's and its Observer's.
ADR-0038 §5's extra Observers raise it, because any one live Observer is enough (§2)." Coupling to both reverses
the second sentence.

- **Availability** is the product of three: the Thinker's and both Observers'.
- **Latency** is set by the slower Observer. `K` has to cover the slower seat's ordinary lag, and it is still below
  `R` (ADR-0039 §1).
- **Throughput:** two heartbeats per `T_obs` per cell on the log, where there was one.
- **A Byzantine Observer can stop its own cell** by withholding heartbeats (ADR-0039 §5). Either of two can now.
  It is still one cell, and still the direction that fails closed.
- **Eviction needs a spare.** With a dead Observer the cell stalls until the seat is leased again. The replacement
  must be independent of the Thinker and of the surviving Observer, so with exactly three lineages it is another
  instance of the lost seat's lineage.

ADR-0038 §5's "More Observers never lower safety and may lower availability" stays true. Under the accepted
coupling the availability cost of an extra Observer was false denials only. Here it is also every stall.

### 4.4 What the modules can and cannot say about it

ADR-0039 §8 asks for a module "with one Thinker, one cell Observer and one correlator", and `spec/Coupling.tla` and
`spec/RunCoupling.tla` are that. With one Observer, "at least one" and "every" are the same predicate, so neither
module tells the two rules apart. A successor would need two cell Observers and, at least:

- **`NoAdmitWithoutEveryObserver`**: no effect-bearing Run admit while `live(o)` is false for any declared cell
  Observer. A mutation in which any one live Observer suffices must break it, with a trace in which one Observer is
  starved and the Thinker goes on. **That mutation is ADR-0039 §2 as accepted.**
- **`UnreadBoundedEach`**: `UnreadBounded`, for each honest cell Observer separately.
- **`CorrelatorNeverGates`**, unchanged, with two correlators.

These names are sketches. Nothing was written.

## 5. Planted records

### 5.1 What a planted record is

A **planted record** is a record the mechanism puts in what a watcher reads, drawn from a suite promoted in Build,
that carries a defect the suite's authors put there. The mechanism knows which records it planted. No effect ever
follows from one. This is the 11.13 reading's suggestion 4, and ADR-0035 §6's planted defects carried from Build
onto live traffic.

**The fold, `planted-past`.** A watcher `o` whose `mark(o, r)` is at or beyond a planted record `n`, and which has
reported no finding citing `n` by the time its mark is `g` records past `n`, has a **planted miss**. It fires,
naming `o`, when `o`'s planted misses in the window reach `m_plant`. `g` and `m_plant` would be values, and like
every value in ADR-0039 §1 and ADR-0051 §2 they would be placeholders until measured.

**How it differs from `marked-past`.** ADR-0051 §2 draws the line: "a planted defect is a defect, and another
watcher's finding may be false."

| | `marked-past` | `planted-past` |
|---|---|---|
| Silence is compared with | Another watcher's finding | Ground truth the mechanism holds |
| Needs a second opinion | Yes | No |
| Works when every watcher is silent | No | Yes |
| A Byzantine watcher can manufacture a miss for another | Yes (ADR-0051, Consequences) | No |
| Covers defects | Whatever some watcher finds | Only the classes the suite holds |

**The arithmetic of catching total silence.** If one record in `1/ρ` is planted, a watcher that finds nothing has
`m_plant` planted misses after about `m_plant / ρ` records. For illustration only: at one plant in sixteen and
`m_plant` = 2, that is about 32 records, half of Run's placeholder round bound `R` = 64. These are not proposed
values.

### 5.2 Five things the design has to get right

1. **A finding on a planted record must not stop the Thinker.** Under any-of, a finding citing record `n` blocks the
   Thinker's next admit. If `n` is planted, that is a false denial on every correct catch. The mechanism knows `n`
   is planted, so the finding has to be absorbed: recorded, credited to the watcher, and without effect on the
   Thinker. For the same reason `shared-ingress` and `marked-past` must not fire on a planted record.
2. **A watcher must not learn that a record was planted before its own grace has run.** If `o2` can see that `o1`'s
   finding on `n` blocked nothing, it knows `n` is planted and can copy the finding. Either each cell Observer gets
   different plants, or the plants are common and neither Observer can see the other's finding, or what became of
   it, until both marks are past `n + g`. Common plants also give ADR-0035 §6's joint miss rate for the pair on
   live traffic. Whether a cell Observer can read another cell Observer's findings today was not established here.
3. **The watcher's read has to be something the mechanism delivers.** `W(p)` is "the set of `observer` seats whose
   lease holds a read authorization on `p`'s current round topic" (ADR-0038 §2): as the records read, a watcher
   reads the topic. A planted record cannot go into the topic itself without also going to everything else that
   reads it. So planting needs a mechanism-side stage between the topic and the watcher. The 11.13 reading's
   suggestion 5, a canonicalizer, needs the same stage. No record has one (the 11.13 reading §3.4).
4. **Sequence numbers have to hide the plant and keep the bound.** `live(o)`'s third condition is
   `seq(t) − mark(o, r) < K`, with `seq(t)` counting the Thinker's effect-bearing admits. If plants are numbered
   apart, the watcher sees which they are. If they are numbered in line, the watcher's mark is in a numbering the
   Thinker's `seq` is not. The mechanism would keep the map between the two, and the record would say whether a
   plant counts against `K`.
5. **A plant has to pass for a real record of this round.** This is the hardest part and it is not solved here.
   - A defect the floor would refuse is no test: the watcher knows the floor refuses it, so the record cannot be
     real. A plant has to be a defect the floor admits, which makes it a semantic one.
   - A plant drawn unchanged from a static suite will not fit the round it lands in. One alternative is a pinned,
     deterministic transformation of a real record of the round, promoted with the bundle.
   - The suite is a Build artifact, and its authors are Build's Byzantine parties. As in ADR-0035 §6 it would carry
     its own lineage record and satisfy E3 against all three lineages.

### 5.3 Who computes the fold

Two shapes, and this reading does not choose (§8, item 3).

- **The mechanism computes it.** It holds the planted set, and the fold reads only marks and findings, which are
  already in its state. It is per watcher, so it puts no cross-principal state on the admit path, which was
  ADR-0051 §1's ground for keeping the five correlations out of the mechanism. It does put the planted set and the
  fold in the trusted base.
- **The mechanism reveals, and a correlator computes it.** Once every watcher's mark is `g` past `n`, the mechanism
  writes a fact saying `n` was planted. `planted-past` is then a sixth fold over facts, and any reader can recompute
  it, as ADR-0051 §3 wants of a correlation. With two correlators, one's silence on it is a miss the other counts.

### 5.4 What planting does not do

- **It plants, and it does not jam.** The 11.13 reading §4, from Greenblatt et al.: "Planting without jamming
  leaves the signal in place." A colluding Observer that can tell a plant from a real record flags the first and
  passes the second, and a Thinker that marks its real defects gives it the means. The custodian's choices here do
  not include a canonicalizer (§8, item 7).
- **It covers only what the suite holds.** A class of defect no plant carries is never tested.
- **An honest, weak Observer is charged like a colluding one.** A planted miss is a finding against the watcher. With
  coupling to both, removing a watcher stalls its cell. The false-finding rate of `planted-past` is availability.
- **It says nothing of the correlators' folds.** Those are fixed and are covered by `marked-past` between two
  correlators. A correlator that reads payloads and judges (ADR-0051 §4) would be tested by plants as a cell
  Observer is.

## 6. What stays open, and what the statement would say

| Residual | Why the design does not reach it | Nearest cover, and its standing |
|---|---|---|
| A watcher tells planted from real | No stage removes a Thinker's signal, and a plant may have a tell | The 11.13 reading's suggestions 5 and 6; no record |
| A defect class outside the suite, passed by all | Planting tests only its suite, and three lineages share priors | ADR-0035 §7, declared; the 11.13 reading's suggestion 3 |
| False findings | Any-of over four seats; a second correlator "bounds its silence on correlations and not its false findings" | ADR-0051 §3: a correlation finding can be recomputed. A judgment finding cannot |
| The correlators are absent together | Never coupled, by design | ADR-0039 §4; the 11.13 reading §6 |
| The suite is captured | Its authors are Build's Byzantine parties | The suite's lineage record and Build's gate |
| No lineage is projected | ADR-0035 is Proposed, and "Until then, every lineage is declared" (§2) | ADR-0035's ratification condition |

**The sentence on the statement would change.** ADR-0039 §5 has the residual-risk statement say "detection fails
open against a colluding Observer", and ToO §13's A13 is that the cell Observer is not colluding with its Thinker.
Under this design the assumption would be narrower, and it would have two parts:

- Not every watcher of a record colludes.
- A colluding watcher cannot tell a planted record from a real one.

The first is what two Observers, three lineages and coupling to both are for. The second is what planting leans on,
and nothing in this design establishes it.

## 7. What it would touch

As far as this reading went. The lists are not complete, and every entry is a suggestion with none made.

| Record | Standing | What would change |
|---|---|---|
| ADR-0038 §5 | Accepted | The archetype value of cell Observers, one to two (§8, item 1) |
| ADR-0037 | Accepted | D-0037-1 counts "Observer seats per cell: 1 or more → 0"; a row for two to one |
| ADR-0039 §§2, 3, 6 to 8 | Accepted | §4.1's three clauses; §6's availability sentence; a degeneracy for "every" to "at least one", which is the rule accepted today; §5's LP-4 sentence |
| ADR-0017 | Accepted | "two lineages" to three |
| ADR-0016 §5 | Accepted | Seat distinctness between two Observers of one cell |
| ADR-0035 §§5, 6 | Proposed | The declaration condition over every pair in a cell; the suite against three lineages |
| ADR-0051 §§2, 9 | Proposed | `planted-past`, if it is a fold; `shared-ingress` and `marked-past` set aside for planted records |
| ADR-0043 §4 | Accepted | What a finding citing a planted record does |
| A new record | None | Planting: the stage, the suite, the numbering, the fold, the values. It would decide LP-4 |
| ADR-0068 §1 (TM11); ToO §13 (A13); the residual-risk statement §1.3 | Proposed; narrative; derived | The assumption as §6 restates it |

**Modules.** A successor to `spec/Coupling.tla` and `spec/RunCoupling.tla` with two cell Observers (§4.4).
`spec/Correlator.tla` already has two correlators; it has no planted record. A module for planting would state at
least that no planted record is followed by an effect, that a finding on one never blocks a Thinker, and that a
watcher silent on everything is named within a bound.

**The reference.** ADR-0038 §8 has the dev rules "seat one cell Observer per author seat and one correlator". The
lift for `observerLive`, a second cell Observer seat and a second correlator would follow the records.

## 8. Choices this reading found and did not make

1. **Is two the archetype value, or a deployment choice above one?** ADR-0038 §5 allows more than one today as a
   deployment choice. Making two the archetype makes every one-Observer deployment a declared degeneracy.
2. **Does Build's coverage follow Run's coupling** (§4.1, third row)? §4.2 argues that it should.
3. **Who computes `planted-past`**: the mechanism, or a correlator after a reveal (§5.3).
4. **Common plants or separate ones** for the two cell Observers (§5.2, item 2).
5. **The values**: the planting rate, `g`, `m_plant`, and whether a plant counts against `K`.
6. **What makes two facts-only correlators independent** (§3.4), with ADR-0051 finding 5's open question of what a
   Persona with no model is.
7. **Whether jamming belongs in the same record as planting.** §5.4's first point says planting alone leaves the
   known way round it in place. It was not among the choices given.
8. **One record or several.** The planting part has no record to amend. The rest is amendments to six accepted
   records and revisions to two Proposed ones.

## 9. What this reading did not do

- Nothing was modelled, checked, measured or built. Every rule, fold, property and mutation named here is a sketch.
- The records were read in the sections listed at the head, not whole. ADR-0054, ADR-0062 and ADR-0068 were read
  only in the lines other records quote.
- No paper was read. Greenblatt et al. is cited as the 11.13 reading reports it.
- Whether a cell Observer can read another's findings, and how a watcher's read of a round topic is delivered in the
  reference, were not established. §5.2's items 2 and 3 rest on the records' text.
- Whether three architecture families exist at a size where each is a usable Observer was not examined.
- The cost in instances, hardware (ADR-0038 §4: no two `observer` seats in `W(p)` share a device) and training was
  not estimated.
- The drafter is of the corpus drafter's lineage (see the head of this document).

## Sources

**Corpus**, at `231ca68`:

- Records: `decisions/ADR-0007.md`, `decisions/ADR-0016.md`, `decisions/ADR-0017.md`, `decisions/ADR-0035.md`,
  `decisions/ADR-0037.md`, `decisions/ADR-0038.md`, `decisions/ADR-0039.md`, `decisions/ADR-0043.md`,
  `decisions/ADR-0051.md`.
- Modules, by their constants only: `spec/Coupling.tla`, `spec/RunCoupling.tla`, `spec/Correlator.tla`,
  `spec/Observers.tla`.
- Derived: `derived/topak-schelling-points-2026.11.13.md`, `derived/scenarios-2026.11.12/FINDINGS_TOPAK.md` (SF-17),
  `derived/topak-residual-risk-statement-2026.11.11.md` (§1.3, A13 and TM11 rows), `derived/topak-glossary-2026.09.17.md`
  (LP-4).

**Outside**: none fetched.
