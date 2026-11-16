# What drawing the command-chain overlay found, and why a diagram is worth generating when nobody looks at it

> Write up the findings as a derived doc and explain how these findings were surfaced and the usefulness of the
> diagrams even if they are never viewed by a human.

(The custodian's prompt of 2026.11.10, after nine diagrams of the overlay were drawn.)

**2026.11.10** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
`baddd63` (ADR-0059 to ADR-0068, with the R1 revisions of ADR-0059 to ADR-0067, and the eight TLA+ modules of
2026.11.10) and the nine diagrams A5, B9, B10, C11, D7, D8, E5, G4 and H8 on branch `diagrams-command-chain`, which
were uncommitted when this was written

---

## 1. What this is

On 2026.11.10 the custodian asked for diagrams of the command-chain overlay, ADR-0059 to ADR-0068. Nine were drawn,
in the TOPAK family's style and under its rules (`diagrams/topak/src/AUTHORING.md`). Drawing them turned up
inconsistencies in the records, between the records and their modules, and in other corpus artifacts. §2 lists
them. §3 says which part of the drawing found each. §4 argues that the generated diagrams are worth having for
these checks alone, whether or not a person ever looks at them, and says where that argument stops.

**Nothing here decides anything.** Each finding is a lead for the custodian. Every one was checked against the
files before it was written down, and two that the drawing agents reported did not survive that check (§3.6). The
records named are Proposed, and none is ratified.

This is the second pass over these records in one day. The first was the TLA+ modules, whose findings the records
took as R1. This pass found what R1 left behind, and some things no module could see.

---

## 2. The findings

### 2.1 Against the records

| # | Finding | Where | Found by |
|---|---|---|---|
| R-1 | **ADR-0068 was not revised when the modules arrived.** Its Status note still says "Nothing here is modelled, checked or built", §6 says "Not met: no module is written", and §3 speaks of what the modules "would prove". The eight modules exist, and ADR-0059 to ADR-0066 cite them by digest in their R1 rows. | ADR-0068 Status note, §3, §6 | G4, A5, H8 |
| R-2 | **ADR-0068's Consequences count three adversaries bounded by "nothing"; the table has two.** TM8 ("Nothing in this design") and TM11 ("Nothing. Coupling cannot see collusion") are. TM13's cell begins "Nothing a peer originates enables anything", which is a bound, not its absence. | ADR-0068 §1, Consequences | G4 |
| R-3 | **"Received" and "originates" disagree after R1.** ADR-0065 §1 now ranges over items a peer originates, because a relayed lease is received from a peer and does enable a permit. ADR-0065 §9 and ADR-0067 §7 still ask for the floor stage to be "monotone in what was received from peers". Read literally, that asks for something §1 now says is false. | ADR-0065 §1, §9; ADR-0067 §7 | D8 and B10, each independently |
| R-4 | **"Arrives a day old" assumes the plane keeps ticking.** ADR-0064 §3 says "Anything withheld for a day arrives a day old." ADR-0066 §4 ⟨R1⟩ says aged is a count of the plane's ticks, which a captured plane can stop, so no act then ages. Both are true of an honest plane, and only the second says what happens under capture. | ADR-0064 §3; ADR-0066 §4 | C11 |
| R-5 | **ADR-0062 §8 quotes `R3-observer-live` short.** It says R3 "refuses `Actuate`". ADR-0041's table has R3 forbid `Actuate` and `Report`. §8 moves coupling to the grant for a `local` entry, so what happens to a `Report` under R3 is the part left unsaid. | ADR-0062 §8; ADR-0041 table | D7 |
| R-6 | **ADR-0065 counts a pending amendment as in force.** §3 calls a peer's report "a sixth item on the Listener's list, after ADR-0054's `input`". The fifth item is ADR-0043 A3, which is Pending and takes force only when ADR-0054 is ratified. | ADR-0065 §3; ADR-0043 A3 | D8 |
| R-7 | **ADR-0061 names floor entries and has no floor condition.** §3 cites `FD13` and `FD4`. §7, unlike the ratification conditions of its siblings, has no item for the floor. | ADR-0061 §3, §7 | B9 |
| R-8 | **Unmet conditions are marked unevenly.** In ADR-0059 to ADR-0066 the module and reference items say "Met" or "Not met". Every floor item ("The floor carries …") and every reader item ("A reader who is not the drafter") says neither. None of them is met. | Ratification conditions of ADR-0059 to ADR-0066 | B9, D7 |
| R-9 | **ADR-0067 alone has no overlay-position section.** The other nine records each say what they report upstream under ADR-0058 §6 and what the archetype's records would owe. ADR-0067 says it is an overlay and carries no debt, and stops there, although its §4 relaxes two entries of the archetype's floor. | ADR-0067 | A5 |
| R-10 | **ADR-0067 paraphrases ADR-0007.** It gives ADR-0007 as "no semantic judgment is an enabling condition". ADR-0007's words are "Semantic judgment is never a lift" and "Semantic lift is prohibited in the admit path". The paraphrase is faithful in effect. It is not a quotation. | ADR-0067 §1, §6; ADR-0007 | B10 |

### 2.2 Between the records and their modules

| # | Finding | Where | Found by |
|---|---|---|---|
| M-1 | **One interlock check is not modelled.** ADR-0066 §4 lists five checks plus, after R1, that the act names this vehicle; one of them is that the entry is in the seat's envelope. `Release.tla` abstracts "an act's entry, inputs and envelope" as the floor's business. It also says the interlock is the only check its properties rest on. So no property rests on the envelope check, and the module would not notice its absence. | ADR-0066 §4; `spec/Release.tla` header | C11 |
| M-2 | **Hold when an extent ends ⟨Q14⟩ is stated by no module.** ADR-0062 §4: when an extent ends and no entry follows, the governor holds and the lease stays live. `Alone.tla` hands this to `PlaneClock.tla`. `PlaneClock.tla` ends an entry at its extent (`EntryEndsAtExtent`) and says nothing of holding. ADR-0062 §11 does not ask for it either. | ADR-0062 §4, §11; `spec/Alone.tla`, `spec/PlaneClock.tla` headers | D7 |
| M-3 | **The module states a stronger bound than its record.** ADR-0064 §4: no grant "more than one tick period past its `expiry`". `PlaneClock.tla`'s `NoGrantPastExpiry`: no grant "one tick period or more" past it. The module is in discrete time, so the two may differ only at the boundary. The record could state what was proved. | ADR-0064 §4; `spec/PlaneClock.tla` | E5 |
| M-4 | **Module headers describe their records as drafted.** `Release.tla`'s "three findings against ADR-0066" and `Outstanding.tla`'s "Mut = none: ADR-0063 as drafted" were written before R1. `Outstanding.tla` already charges `ordered` entries to the governor, which is R1's reading. A module cited by digest is frozen, so its header cannot follow the record. The R1 rows are where the current reading is. A reader of a header should know that. | `spec/Release.tla`, `spec/Outstanding.tla` headers; R1 rows | C11, E5 |
| M-5 | **The archetype's numbers are not the module's.** ADR-0061 §4 and ADR-0068 TM12 count losses at seven replicas. `Membership.tla` is checked and proved at five. ADR-0061 R1 says so. ADR-0068 does not. | ADR-0061 §4, R1; ADR-0068 TM12 | G4, B9 |

### 2.3 In other artifacts

| # | Finding | Where | Found by |
|---|---|---|---|
| A-1 | **`spec/README.md` said no record cites the overlay's modules by digest.** That was true when written and false after R1. **Fixed** on the diagram branch. | `spec/README.md`, the overlay paragraph | H8, comparing every digest the records cite with the files |
| A-2 | **G1 and G3 have not drawn Batch 39.** Regenerated, G1 takes ADR-0045 A4's text, the upstream report of the prover's two unsound cases, and G3 takes the premise routes of 2026.11.03. Neither was regenerated at Batch 39. | `diagrams/topak/G1-…`, `G3-…` | Regenerating the whole family |
| A-3 | **H6 would now draw the wrong scan.** H6 reads the newest `spec/proof-scan-results-*.txt` by file name. Since 2026.11.10 that file is the overlay's eight-module scan, not the corpus's. Regenerated, H6's counts change to the overlay's. H6 should name its file, or select by the modules it draws. | `diagrams/topak/src/d_h6_proof_certification.py` | Regenerating the whole family |

G1, G3 and H6 were left as drawn. Each wants an amendment made on purpose, not as a side effect of drawing
something else.

### 2.4 In the diagrams themselves

Review of the nine found one defect, now fixed. B9's picture of a captured plane gave it a budget of 2 and three
leases, numbers the record does not state, without saying so. It now says they are illustrative. Two diagrams add
columns the records do not have: B10 relates floor entries to module properties, and G4 relates adversaries to
module properties. Both columns are headed as the diagram's own. G4's mapping of T-0068-10 to ADR-0045's T-0045-3
(the Cedar engine) and T-0045-6 (the bundle-tier engines) was checked against Annex A.

---

## 3. How the findings were surfaced

Nine agents drew the nine diagrams in parallel. Each started with a fresh context, the family's authoring rules,
its records and its modules, and no draft to agree with. Each had to finish with a generator run that printed no
overlap warnings and a look at both themes. Their reports were then checked against the files, and the whole family
was regenerated. Each finding in §2 traces to one of six mechanisms.

### 3.1 Full tables leave nothing unplaced

The rules say: "When a record has a table, draw all of it." A summary can skip a row. A drawn table cannot: every
cell is set, measured and wrapped. Drawing ADR-0068 §1 whole put TM8, TM11 and TM13's bounding cells side by
side, and the Consequences' "three" no longer matched (R-2). Drawing every ratification condition item by item,
each needing a pill, showed that the floor and reader items have no state at all (R-8).

### 3.2 Every statement traces to a record, by section

A diagram may not say anything its records do not, and each card cites its source by section. So the drawer reads
both records wherever two of them meet. That is how the quotations of R3 (R-5) and ADR-0007 (R-10) were compared with
their sources, and how ADR-0065's count of ingress items was traced to a pending amendment (R-6). A prose reader
takes "ADR-0041" on trust. A drawer has to put R3's row on the page.

### 3.3 Two records on one page

When two records are drawn together, a sentence in one meets a sentence in the other. D8 and B10, drawn separately
and from different records, each found the "received" against "originates" split (R-3). C11 drew ADR-0066's
freshness check next to ADR-0064's tick rules and found that "a day old" assumes an honest clock (R-4). A5's table of
ten records, one row each, showed ADR-0067's missing section (R-9) only because every other row had something in
that column.

### 3.4 Joins between records and modules

Several diagrams set a record's claim beside the module property that states it: the interlock's checks beside
`Release`'s (M-1), ADR-0062's sections beside the four modules that state them (M-2), ADR-0064's bound beside
`PlaneClock`'s (M-3), ADR-0068's adversaries beside module properties (R-1, M-5). A join shows its empty cells. The
empty cell for hold ⟨Q14⟩ is M-2. The envelope check, drawn as the one dashed box in a row of solid ones, is M-1.

### 3.5 Generators that read the corpus and regenerate byte for byte

The family's generator is deterministic. An unamended diagram regenerates byte for byte, and several diagrams read
records and results files when they are built. H8 computes every digest and compares it with what the records cite,
and so caught the stale README sentence (A-1). Regenerating all 52 diagrams to confirm that only the nine new ones
changed showed three that should not have: G1 and G3 had fallen behind Batch 39 (A-2), and H6 had started reading the
wrong file (A-3). No one was looking for either.

### 3.6 Checking the drawers

The agents' reports were leads too. Each finding above was checked in the records or the modules before it was
written down. Two reported inconsistencies were dropped:
- `Alone.tla` credits `TerminalNeverWaits` to proposal §10, while ADR-0062 §11 calls it the custodian's decision.
  Both are true: the proposal stated it, and the custodian chose to include it.
- `M_NOEXTENT` runs in `PlaneClock`'s rows but is absent from ADR-0064 §8. It belongs to ADR-0062 §11, and the
  module covers both records.

The one defect in a diagram (§2.4) was found the same way: by reading the diagram against its record.

---

## 4. Why the diagrams are worth generating when nobody looks at them

### 4.1 A diagram generator is a second compiler for the corpus

The records are prose, and prose tolerates a stale sentence, a miscounted list, a quotation that has drifted, a
section that one record has and its siblings lack. The generator does not. It has a fixed vocabulary: a status is one
of a fixed set of pills, and *proved*, *certified* and *checked* are distinct words. It sets every table cell, and it
requires a source for every card. Writing a diagram therefore compiles the records into a form where those faults
show, as empty cells, mismatched counts, or two sentences that cannot share a page. Thirteen of the eighteen
findings in §2 are of that kind (R-1 to R-10 and M-1 to M-3). None of them needed a person to look at a picture.
They needed something to try to draw one.

### 4.2 Regeneration is a regression test over the corpus

Because the family is deterministic, a full regeneration is a test: every diagram whose inputs have not moved
comes out byte for byte, and any diff is either an intended amendment or a finding. Today it found two diagrams a
batch behind and one reading the wrong file (A-2, A-3). The diagrams that read the corpus at build time (G1, G3, H6,
H7, H8) are the strongest form of this. A missing file or a number that no longer parses is an error, as a gate's
is. H8 goes further and checks that the records' digest citations match the files.

### 4.3 Drawing is a structured reading by someone who did not draft

Each agent read its records cold, with a brief that required it to place every claim and report what it could not
place. That is a reading the drafter cannot give their own text. It found things the drafter, who also wrote the
modules and the R1 revisions, had read past the same day (R-1, R-3, M-1, M-2).

It is not the reader ADR-0029 A2 asks for. The drawing agents are the same kind of model as the drafter, so their
blind spots are correlated with the drafter's, which is the failure ADR-0035 is about. They are independent in
context, not in lineage. Every ratification condition's reader item stays unmet.

### 4.4 It is cheap enough to repeat

Nine diagrams took nine agents working in parallel, nine to seventeen minutes each, and about 2.3 million tokens in all.
Regenerating the family takes seconds. The drawing can be repeated after every revision of these records, and the
regeneration after every batch.

### 4.5 Where the argument stops

- **A diagram decides nothing.** "Where a diagram and a record disagree, the record wins" (`diagrams/README.md`).
  A finding from drawing is a lead until someone reads the record.
- **A diagram can add an error as well as find one.** B9's unlabelled numbers are the instance here (§2.4). The
  diagrams' own cross-reference columns (B10, G4) are claims the records do not make, and must stay labelled as
  such.
- **The overlap checker is a layout check, and has a known blind spot.** It does not catch a card that outgrows a
  row height computed over other cards. It says nothing about content.
- **Nothing here is verification.** The modules are checked and proved under their own abstractions (H8 draws
  them). The diagrams only show where a record, a module and a file disagree.
- **A finding not drawn is not found.** Each diagram covered its records' tables and decisions in full, but
  nothing measures what a drawer read past.

---

## 5. What the custodian may decide

1. **Revise ADR-0068** (R-1, R-2, M-5). It is the only record of the ten with no R1.
2. **Settle the wording of the monotonicity condition** in ADR-0065 §9 and ADR-0067 §7 against ADR-0065 §1 (R-3).
3. **Decide whether hold ⟨Q14⟩ and the envelope check need module properties** (M-2, M-1). Each would be a successor
   module, since the current ones are frozen by digest.
4. **Make the ratification conditions say "Not met" wherever they are not met** (R-8), and give ADR-0061 §7 a floor
   item (R-7) and ADR-0067 an overlay-position section (R-9).
5. **Correct the smaller items** in a pass of their own: R-4, R-5, R-6, R-10, M-3.
6. **Amend G1, G3 and H6** (A-2, A-3), with H6 told which scan file it draws.
7. **Make regeneration a routine check.** Run the full family after every batch, and treat any diff that is not a
   declared amendment as a finding.
