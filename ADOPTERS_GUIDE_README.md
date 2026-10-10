# TOPAK — Adopter's Guide

> **WORK IN PROGRESS. FOR REVIEW AND GUIDANCE ONLY.** This guide is unfinished, has had no independent reader, and is
> written against a design corpus that is itself not deployable. It is provided so that reviewers and prospective
> adopters can see what the pattern asks of a deployment and say where it is wrong. **It is not to be followed as
> written for any production use.** Nothing here is a release, a supported configuration or a security
> recommendation; where it differs from the records it cites, the records win, and where the records are silent, so
> is any guarantee.

**2026.10.09** · DRAFT · written against Genesis Checkpoint G11 and Theory of Operation revision 15 · a convenience,
not a record: where this guide and the checkpoint disagree, the checkpoint wins. It is kept current and is not
measured by any manifest (`manifests/EXCLUDE`)

**Drafted by the assistant** at the custodian's request. Like most of this corpus, it has not been read by anyone
independent of its author, and no deployment other than the reference has been built against it. If following it
leads you somewhere the records do not, treat that as a finding and report it ([SECURITY.md](SECURITY.md)).

**Two rules this guide holds itself to.** Every **must** cites the record clause it comes from, and is nothing more
than that clause restated for a builder. Every **should** is advice the records do not contain, is marked *advice*,
and binds nobody. Where the corpus supplies nothing, the guide says *the deployment writes this* and names the open
row, instead of inventing a default.

**Marks.** Status words are the corpus's own, and they are exact. *Accepted (genesis)* is in force, ratified by one
person, and awaits a first quorum where it carries C1 to C4. **⟨Proposed⟩** marks a record that is drafted and not in
force: nothing in it binds a deployment, and the reference may already follow it. **⟨provisional⟩** marks a record in
force and subject to redesign (ADR-0029 A4): build on it only what you could rebuild. **⟨pending⟩** marks an
amendment drafted and not ratified. All nine sections are written, by one hand on 2026.10.09; sections 3 to 8
followed 1, 2 and 9 the same day and have had no second reading.

---

## 1. Who this is for, and what you are adopting

**You** are a platform engineer, or the team of them, building a deployment on the TOPAK pattern: a control plane in
which agents and people act through leases, every effect crosses a mediated boundary, and policy can only refuse.
This guide assumes you will read the records it cites. It does not replace them, and the
[Theory of Operation](narrative/theory-of-operation.md) is the narrative to read first.

**What TOPAK is.** An architecture pattern, stated as fifty-four decision records, a checked and partly proved
formal layer, a draft policy floor and a reference implementation of the admit path. The letters name roles, not
products ([README](README.md)). The pattern's claims are stated against an agent's action alphabet, and every
agent, model and Persona is treated as Byzantine (ADR-0007, ADR-0016, ADR-0025).

**What it is not.** Nothing in this repository is deployable: no release, no packaged artifact, no supported
configuration ([SECURITY.md](SECURITY.md)). The reference under `mechanism/` exists to show the design is buildable.
Every record was ratified by one person with an assistant, and twenty-nine records are confirmation-required and
must be cited as author-ratified until a first quorum confirms them (ToO A8; G11 §4). The residual-risk statement's
plain words stand, as of 2026.10.09, for anything you would build today:

> **What you do not get, today.** Confinement. No principal is `Contained`; every one is `Mediated`, which means the
> mechanism attributes and authorizes its actions and does not bound its effects. An agent that can reach a shell, a
> socket or a filesystem outside the launcher is outside the guarantee, and the mechanism will not know. Detection
> cannot tell an honest Observer from a colluding one. Gate evidence is asserted. A first lease comes from whoever
> reaches a socket. A label is a declaration. The numbers are placeholders. No stall is proved to end. The proofs are of
> the design, not of the binary, and the prover that checked them is known to prove false statements in two ways that
> a rule and a reading, not a check, are said to have kept out. The reference follows two records that are Proposed on
> a floor that is not in force. The design, the proofs, the code and this statement were written and checked by one
> person and one assistant, with no second reader.
> — [Residual-risk statement](derived/topak-residual-risk-statement-2026.10.09.md) §6

**What adopting means, in one sentence.** You do not install TOPAK; you **declare a position** against its
archetype, build what that position requires, and inherit exactly the theorems whose premises your declaration
leaves standing (ADR-0023 §1 to §3; ToO §8.1). Section 2 is that declaration. Everything else in this guide is
what a position costs to build and to keep.

**What this guide does not cover.** The genesis process (ADR-0029), which governs the corpus and not your
deployment; the reviewer's duties ([Reviewer's Guide](REVIEWERS_GUIDE_README.md)); and operating a Build pipeline
for Personas, which the lineage rehearsal under `slm/` sketches and no record yet makes a deployment obligation.

---

## 2. Your deployment is a declaration

### 2.1 The relation

The archetype is the unique maximum of a parameter lattice, and **nobody ships it** (ADR-0023 §3; ToO §8.1). A
deployment is a **degenerate** form of the archetype, obtained by driving named parameters to limiting values. Three
things follow, and each one shapes what you write down:

- **Premise loss, not weakening** (ADR-0023 §2). A theorem is present in your inventory or absent from it. There is
  no "weaker version"; a parameter at its limit falsifies premises, and every theorem resting on one is gone.
- **Rungs are per axis** (ADR-0023 §5). Your position is a tuple, one coordinate per parameter. "Rung demotion"
  without a parameter name is barred from the corpus and should be barred from your documents.
- **Capability beyond the archetype is a finding, not a demotion** (ADR-0023 §4). If your deployment needs something
  the archetype lacks, the archetype is incomplete. Report it; do not declare it as a variation.

### 2.2 The declaration record

Every degeneracy carries a declaration with a fixed schema (ADR-0023 §6), and a declaration is **mandatory**;
mitigation is not. One row per parameter you move:

| Field | What you write | Source |
|---|---|---|
| **Kind** | *mechanism*: the value is inside the verified object, the proofs that quantify over it reopen, and the change ships as a mechanism release. *Declaration*: the value is outside it and reopens nothing | ADR-0023 §6a |
| **Parameter** | The named axis, by its degeneracy id where a record has one (`D-00nn-k`) | ADR-0023 §6; each record's annex |
| **Archetype value** | What the archetype holds on this axis | the owning record |
| **Deployed value** | What you hold | — |
| **Premises falsified** | The premise nodes the limit falsifies, as row ids and property names | ADR-0045 §3; `spec/theorem-premise-binding.json` |
| **Theorems voided** | Every theorem resting on a falsified premise; the matrix mode of `spec/inventory.py` computes it from the binding | ADR-0023 §2; [matrix note](derived/topak-rung-DAG-as-matrix-2026.10.03.md) |
| **Type changes** | For each participant whose type changes: archetype type, deployed type, where the gate now sits, what enters or leaves the trusted base. Empty is a claim, stated as one: *no participant changes type* | ADR-0023 §4a, §6b |
| **Mitigation** | Optional. What you do instead, which voids no fewer theorems | ADR-0023 §6 |

Above one parameter, the declaration carries two more things:

- **A composition note** listing every theorem whose premises are jointly falsified but individually discharged.
  An empty delta is a claim, stated as one. **A missing note is not an empty delta**, and the declaration fails
  at the promotion gate (ADR-0023 §7a, §7b).
- **The rung per seat.** For every seat the issued rules declare, the confinement rung its leases are granted at,
  and the rows of ADR-0045 Annex A's confinement axis that rung rests on. The rung is per seat, not per deployment;
  changing it is an issuance, never a runtime choice (ADR-0023 §6c; ADR-0034 §3.4).

Two companions complete the declaration and are treated in their own sections:

- **The trusted base**, instantiating every row of ADR-0045 Annex A and adding none that is not a degeneracy. An
  undeclared row is false, and a deployment with no published declaration sits at the bottom of every axis
  (D-0045-1; ToO A14). Section 4.
- **The values**: Observer timings, the custody threshold, `T_irrev` per effect class, the bundle key's custody.
  The proofs quantify over them and cannot choose them. Section 6.

**Where the declaration lives.** The records say what it contains and that the promotion gate reads it (ADR-0023
§7b). They do not yet fix a file format or a path: ADR-0045's open obligation for a declaration template is still
open (G10 item 64, in part). *Advice:* keep it beside your issued rules, since the rules are the one issued artifact
that already names every seat, which is why §6c put the rung there.

### 2.3 Worked example: the reference's declaration

The reference under `mechanism/` is the only deployment of the pattern that exists. Its trusted base is declared
(ADR-0045 Annex B, at `fb40db1` and revised by ADR-0033 addenda since). Its declaration under ADR-0023 §6 was never
written as one document; this section assembles it from the records, as an example of the form and as a statement
of what a minimal deployment actually holds. Where a row's source is a Proposed or provisional record, the row is
marked. **The reference is not a recommended position.** It is the floor of the lattice with the mechanism
constants and little else, and that is the point of showing it.

**Position.** Every principal is `Mediated`; no principal is `Contained` (ADR-0045 Annex B; ToO §10).

| # | Parameter | Kind | Archetype value | Reference value | Premises falsified | Theorems voided | Source |
|---|---|---|---|---|---|---|---|
| 1 | Confinement rung per seat (D-0034-4; D-0034-2 for the launcher's occupant) | mechanism | Rung 3: confidential VM, attested at grant, profile passing P1 to P7 | Rung 0 for every seat in the shipped dev rules, which is T-0045-16 to 21 absent; rung 1 for the guest ADR-0036 §7's launcher suite seats, under a profile whose P3 fails | A1 (effect exclusivity); the confinement rows | Every `Contained` theorem: `ContainedMeansConfined`, `ContestedStopped`, `FreshAppraisal` and what rests on them | ADR-0034 annex; ADR-0036 ⟨Proposed⟩; `mechanism/` I37; residual-risk §3 A1 |
| 2 | Tool hermeticity, Build (D-0034-3) | mechanism | Every allowlisted tool hermetic under the profile | Build tools native: `topak-demo-tool` and the MLX trainer; T-0045-23 excluded | P4 (Build); ToO A2 | Every `Contained` theorem for principals whose alphabet reaches a native tool | ADR-0045 Annex B, T-0045-23 |
| 3 | Channel fidelity, Run (D-0034-5 and D-0034-6 are the two limits) | mechanism | A Run tool reaches only its declared target, checked | Run tools hosted as Wasm core modules reaching the configured target; the protocol recorded and not enforced; the entry's channel and the node's configuration declared twice and never compared | P4 (Run), in part; T-0045-24 is an instance since ADR-0034 A2 ⟨pending⟩ and not A2's P4 as written | The channel-fidelity theorems, until A2 and ADR-0033 A8 are ratified after review | ADR-0045 Annex B, T-0045-24; design-gap row 2.1 |
| 4 | Anchor custody (A-0025 at n = 1) | declaration | Unanimity over n key-holders, custody (n, 0), with the threshold declared | Custody (1, 0): three dev keys held by one person, in the clear under `dev/secrets/`; dev rules, not genesis rules | ToO A3 at threshold 1; T-0045-8, 9, 10 as trust roots | No theorem: anchor intent is the sole axiom (ADR-0025). The headline residual is a one-person capture coalition | ADR-0025 annex; residual-risk §1.1; ADR-0045 Annex B |
| 5 | Grant-seat independence (ToO A4) | declaration | Grant seats review independently against evidence not derived from the author's artifacts | No independence table; ADR-0029 A2.2 unbuilt | A4 | None in the formal layer; unanimity multiplies signatures, not judgment | residual-risk §3 A4; G18 |
| 6 | Gate evidence (T-0045-13) | declaration | Gate evidence signed by a named gate runner | `GatesPassed` is an unsigned assertion from the operator channel | The gate-ran premise of every promotion theorem | Every promotion theorem that assumes the gates ran | ADR-0045 Annex A and B, T-0045-13 excluded; design-gap row 1.7 |
| 7 | Replica authentication (T-0045-1) | declaration | Crash-fault replicas, mutually authenticated | Three replicas in one process tree, TCP between them, unauthenticated: anyone reaching a socket is a replica | ToO A9 | None by premise, since BFT was declined (ADR-0045 §6); the residual is a forged admit no floor evaluated | ADR-0045 Annex B, T-0045-1; residual-risk §1.7 |
| 8 | Lineage strength (D-0035-1; D-0054-1) | declaration | Provenance projected from the Build log, independence checked by the criterion with measured thresholds; alternation on clear edges enforced at the tally | Declared: the criterion is in no shipped rules file, `Rules.criterion` is unset, five thresholds unset; alternation declared, not tallied | ToO A11; `PromotedAlternates` | No safety theorem. Archetype provenance cannot be declared, and `Contained` has no members whatever the rung | ADR-0035 ⟨Proposed⟩; ADR-0054 ⟨Proposed⟩; residual-risk §3 A11 |
| 9 | The correlator's function (D-0051-1) | declaration | Five correlations as fixed folds, a finding that carries its evidence | The seat exists and reports heartbeats; it computes nothing | ADR-0051 §10's properties | None; cross-principal detection is lost as under D-0038-2 with a seat | ADR-0051 ⟨Proposed⟩ |
| 10 | First seating of an operator (D-0050-1) | mechanism | An operator is a principal of a fourth seat kind, seated by promotion, renewing under a lease | A first seating is whoever reaches the socket; providers are not compared, so D-0050-2 cannot be told from the archetype | ToO A16 | Every lease on the log was put there by a quorum or by an operator inside a quorum's grant, for the first seating only | ADR-0050 ⟨provisional⟩; ADR-0045 Annex B ⟨A2⟩ |
| 11 | Bundle signing key custody (T-0045-27) | declaration | A key under declared custody, in the issued rules (ADR-0044) | A throwaway dev key generated by `dev-init.sh`, custody (1, 0); signing at promotion is a script step | ToO A3 as it applies to the bundle key | None; the "Signed" premise of ADR-0030 §2 holds in letter | ADR-0045 Annex B, T-0045-27; design-gap row 5.4 |
| 12 | The human (ToO A5) | declaration | A trained, authorized person present for an emergency seat, operation, quarantine release and the detection interval `D` | The operator is a socket; no human process | A5 | None in the formal layer; HITL and HOTL postures degrade to unattended operation | residual-risk §3 A5 |

**Where the reference is at the archetype's value**, and so has no row above: labels and delivery modes (D-0047-1
not taken, since ADR-0033 A10); the tool list delivered from the entry (D-0048-1 not taken, A10); coupling in Run in
force (D-0039-1 not taken; ToO A12 enforced, with an end-to-end fixture as the Observer); effects counted and
recorded (D-0042-1 not taken); bundles signed (D-0044-1 not taken, with row 11's custody); one cell Observer per
cell and a correlator seat (D-0037-1, D-0038-1, D-0038-2 not taken); the trusted base published (D-0045-1 not
taken, Annex B).

**Type changes.** Under row 4 the archetype's n key-holders at the gate are one person, who is also the operator of
row 10 and the ratifier of every record (G11 §4). ADR-0023 §4a asks where the gate sits after such a change: at
the reference it sits with that one person on every axis at once. No record states this as a type change; this
guide reads it as one, and that reading is the assistant's, not a record's.

**Composition note.** None exists. By ADR-0023 §7b a missing note is not an empty delta, so the reference's
declaration, as assembled here, **would fail the promotion gate** that reads the §6 schema. The nearest thing to the
note is Annex B's inventory paragraph: with T-0045-13, 16 to 21, 22, 23 and 24 excluded or absent, every theorem
premised on confinement, gate evidence, hermeticity or channel fidelity is void, and what remains are the mechanism
constants and the theorems whose premises are the `all` rows: the lease, the fence, composition, the tally, the
coupling, seats and Observers, every one resting on T-0045-28 to 30, the refinement nobody has made. Whether rows
1 to 3 jointly void anything beyond that union is not computed. *The deployment writes this*: for the reference, it
is owed under G10 item 64.

**Rung per seat.** Rung 0 for every seat the dev rules name, carried as `SeatDecl.rung` and read at every grant and
renewal (`mechanism/` I37, PROVISIONAL declared-rung). Rung 1 for the occupant of the launcher's profile in the
ratification run, beside a rung-0 Observer (ADR-0036 §7 ⟨Proposed⟩; ADR-0034 B29).

**Values.** `T_obs` 5000 ms, `K` 8, Run's `R` 64, `T_persona` one hour, all placeholders with nothing measured;
custody threshold 1; `T_irrev` declared for no effect class; the bundle key as row 11
([design-gap assessment](derived/topak-design-gap-assessment-2026.10.03.md) §5; residual-risk §4, §5).

**What this example teaches.** Three of the twelve rows are *mechanism* degeneracies, and each of those reopens
proofs: a deployment that moves them ships a mechanism release, not a configuration. Six rows void no theorem at all
and are where the residual risk actually lives: custody, independence, gate evidence, replicas, the correlator and
the human. A declaration that lists only the rows with theorems to lose would read as safer than the reference is.
List every row.

---

## 3. Compartmentation

The corpus has one kind of separation machinery, and it is **separation between principals**: disjoint leases,
disjoint alphabets, a topic per seat and attribution per lease (ADR-0037 §1). Every compartment below is built from
that. The units, from the outside in, are the **domain** (Build or Run), the **cell** (the principals seated around
one Thinker for one round), the **seat**, the **round** and its **topic**, and, at rung 1 and above, the **guest**.

| # | You must | Source | What you declare or build | If unmet | Checked by |
|---|---|---|---|---|---|
| 3.1 | **Keep Build and Run apart.** No variant name is shared between the two alphabets; an allowlist entry is for one domain; Build's only egress is promotion, and Run has no gate | ADR-0001, ADR-0002; ADR-0040 §2; ADR-0049 §1; ADR-0022 | Each seat's domain in the issued rules; each entry's `domain`; a Build tool with no channel | A tool or seat read across domains is refused by the floor and at load (W5), so the cost is refusal, not leakage | `RunSeats.tla` `NoNameCrossesDomains`; W5 at load |
| 3.2 | **One seat per principal, one live lease per principal.** A person who operates and also votes, or authors and approves, holds two seats and is two principals | ADR-0037 §1, §7; ADR-0031 §2 | Seats, with `kind` and domain, in the issued rules; a Persona bound to `thinker` or `observer` only | Monotone renewal guarantees nothing if a grant can replace a live lease (ADR-0031 §2 C1) | `Seats.tla` `OneSeatPerPrincipal`; `apply_grant` refuses |
| 3.3 | **Bound each alphabet by seat kind, in the floor and at grant.** Only a `thinker` seat authors or actuates; a `thinker` never votes; an `observer` holds `Consult` and `Report` in Run; a `grant` seat votes; an `operator` holds the six control variants and nothing else ⟨provisional⟩; an `emergency` seat holds Run's three for one round ⟨provisional⟩; an `orchestrator` holds `Route` and `Report` ⟨Proposed⟩ | ADR-0037 §4; ADR-0043 §2; ADR-0050 §1; ADR-0052 §1; ADR-0054 §3 | Nothing beyond the kinds: `B10-only-thinkers-author` and the tightened `B6` are floor entries, and the grant path refuses an alphabet outside the kind's row | A Reader with `Draft` authority, or an Observer that can act, is the failure ADR-0022's follow-up names | The floor gates; `Seats.tla` `M_KIND` |
| 3.4 | **One cell Observer per cell, on a different device from the Thinker it watches**, and no two Observer seats in `W(p)` on one device. The Reader stage may colocate. A correlator per domain reads across cells and is **never coupled** | ADR-0038 §1, §4; ADR-0039 §4; ADR-0037 §2 | Placement, which no record checks; the correlator's **correlation window**, a round length the deployment declares | D-0037-1 or D-0038-1: the cell loses detection, and under coupling makes no Run admits; D-0038-2: cross-cell detection is lost | `Observers.tla` `ReachIsBounded`, `DenyByAnyOf`; placement is read, not checked |
| 3.5 | **A topic per principal per round, sealed on emit completion, is the unit of erasure**, read by ACL, with the read set `W(p)`: the cell Observer and the domain's correlators, and for an operator's or an emergency seat's topic the domain's operators (ADR-0050 §6; ADR-0052 §4). Retention is per domain: Run's horizon for Run topics, the promoted artifact's production lifetime for Build topics. No tiered storage | ADR-0003 (0003.1 to 0003.7, A3); ADR-0038 §2; ADR-0021 §7 | The topic ACL as an enforced read set; the retention length per domain; the `after` companion's bound | A reader outside `W(p)` is a disclosure the design does not model; the reference **declares cells and does not enforce the ACL** (`mechanism/` I8) | Nothing in the formal layer; the ACL is a deployment control |
| 3.6 | **Keep control-plane facts apart from cognitive payloads.** Facts cross into the control plane; payloads do not. The archive holds hash and pointer, with plaintext in a store built for deletion. The six forensic-floor classes are non-erasable for the declared horizon, and **compartmentation is not erasure**: a class may leave a reader set only while the declared audit authority stays a reader | ADR-0004; ADR-0028 §1, §3, §4; ADR-0020 | The horizon per class and the audit authority; the plaintext store and its readers; the separate read-only audit principals | Shortening a horizon or removing a class is a floor relaxation, an issuance and a promotion; demand type 5 is not supported at any rung (ADR-0013 §5) | `NonComposition_A1.tla` NC-2 |
| 3.7 | **Declare a confinement rung per seat, and confine by profile.** A profile is a promoted artifact fixing P1 to P7: one channel, a measured root, no launcher, Wasm tools (Build) or channel fidelity (Run), inference inside, one principal per guest and one guest per round, reference values carried. Rung 0 is `Mediated` always; rung 1 is the launcher's assertion ⟨ADR-0036 Proposed⟩; rung 3 is a confidential VM appraised by an independent verifier | ADR-0034 §1, §2, §4; ADR-0023 §6c; ADR-0031 §3 | The rung per seat in the issued rules; one promoted profile per domain; at rung 3, the verifier and its issued key | D-0034-4, D-0034-2, D-0034-3, D-0036-1: every `Contained` theorem, for the seats concerned. `Contained` also needs the lineage criterion in force (ADR-0035 ⟨Proposed⟩), so today it has no members anywhere | `Confinement_A1.tla` at each rung; `State::contained` at the reference |
| 3.8 | **Run's ingress is a closed list delivered by the Listener**: the task, each consulted object, each tool result and the tool list, each with a label that is a function of its declared source, delivered clear or as a handle by a table per seat kind. The task and the tool list are always clear. A suppressed item's bytes never enter the guest | ADR-0043 §1; ADR-0047 §1 to §3; ADR-0048 §2 | The label vocabulary, the delivery table per seat kind, the Run root's label and every entry's result label, destinations and `accepts` (bundle data); the inside-targets list and the release list (issued rules, ADR-0025 §1 (h)) | D-0047-1: every item delivered clear and unlabelled, and F1 to F6 have nothing to read. A wrong declaration is detected by nothing (ADR-0047 §9) | `Labels.tla`, proved; `ToolList.tla`, proved; W6 to W9 at load |
| 3.9 | **Operators are compartmented by domain** ⟨provisional⟩. `Regrant`, `Renew` and `AttestGates` stay inside the operator's domain and need a live peer there; `EndRound` and `Revoke` reach the operator's own domain only; the fence is the cross-domain tool. The archetype has at least three operators per domain, behind independent identity providers | ADR-0050 §4, §6, C5, C9 | Operator seats per domain in the issued rules; at least two providers | D-0050-3 (two operators): a lapse stalls the domain until a quorum re-seats; D-0050-2 (one provider): the peer rule holds in letter only | `Operators.tla`, proved; the `control` floor stage's gates |
| 3.10 | **Cells reach each other only along a promoted workflow's edges** ⟨Proposed⟩. Workers never address each other; the orchestrator is delivered facts and handles and never bytes, and can only narrow; a worker's output carries its `clearSet` as its label into the next cell; lineages alternate on every clear edge; a mesh runs under a voted budget | ADR-0054 §2, §3, §5, §6; ADR-0055 §2, §5, §7 | The workflow artifact, its seatings, guards, delivery mode per edge, join rules, bounds and kind | D-0054-1 (every deployment today): alternation declared, not tallied; D-0054-2: a finding after coverage stops only what follows | `Workflow.tla`, `Mesh.tla`, TLC-checked, not proved |
| 3.11 | **Tools run on the mechanism's side of the front door, never in the guest.** The tool host instantiates a Run tool per call with one connection, to the target its allowlist entry declares, and nothing else; the entry's digest is re-checked on every call | ADR-0033 §2; ADR-0034 A2 (P4 for Run); ADR-0049 §2, §5; ADR-0045 T-0045-25 | The tool host as a trust-root row; every Run tool as a Wasm component (the reference has a core module, I44) | D-0034-5 or D-0034-6 for a native Run tool: channel fidelity becomes a trust or is lost | `RunConfinement.tla`, proved; `wasmtool.rs` |

**The deployment writes.** The source declarations of 3.8, which the corpus calls assumption A15. The topic ACL as an
enforced thing, which the reference lacks. The Observer round layout against the Thinker's rounds, which no record
gives (ADR-0043 §5, finding 1). The correlation window. Whether a delivery table must carry a row for the `emergency`
kind, which ADR-0052 leaves open: without one the person seated in an emergency is given handles and no bytes.

*Advice.* Start every non-reserved label at `handle` in the delivery table and loosen by promotion as the work needs
it. The records make this safe to do in that direction: delivering more in the clear can only make F1 to F3 refuse
more (ADR-0047 §7, §8), and a suppressed item adds nothing to `clearSet`. *Advice.* Treat 3.4's placement rule as
a hard requirement of your infrastructure description, since nothing in the mechanism will tell you it is broken.

---

## 4. Security obligations

The pattern's security claims rest on three things a deployment supplies and the corpus cannot: a trusted base
declared row by row, keys under declared custody, and components that fail only by subtracting. This section is the
builder's reading of those.

| # | You must | Source | What you declare or build | If unmet | Checked by |
|---|---|---|---|---|---|
| 4.1 | **Declare the trusted base row by row**, instantiating every row of ADR-0045 Annex A with its component, layer, premise, rungs, class, failure, identity and residual. Class each row *delegated* (fails only by subtracting), *trust root* (can add, identity fixed by issuance or promotion, entered by a record) or *excluded* (relied on, trusted for nothing). **Refuse** any component whose failure can add authority and whose identity is fixed by neither | ADR-0045 §1, §2; ToO A14 | The declaration, kept with the §2 declaration; a custody pointer in every trust root's *identity* field | D-0045-1: an undeclared row is false, and the deployment holds the mechanism constants and nothing else | `spec/inventory.py` over the binding; nothing checks the rows against the running system |
| 4.2 | **Declare anchor custody** as the pair (capture threshold, loss tolerance) with the composition and eviction rule that makes it true. Intent is the sole axiom: an authentic issuance is what the anchor intended, and no theorem covers it. No key is both in the anchor set and on the promotion roster for one artifact | ADR-0025 §2, annex; ADR-0026 R5; ToO A3 | The custody row; the key-holders; a rotation or eviction rule (A-0025 unanimity, D-0025-1 threshold with recovery, D-0025-2 eviction with replacement) | A coalition at the threshold issues any floor-conformant rules. This is the **headline residual** (residual-risk §1.1), and at threshold 1 it is one person | The rules floor bounds the issuance; nothing bounds the holders |
| 4.3 | **Put every authority-defining key in the issued rules**: the anchor set, the verifier's appraisal key, the bundle-signing key, each identity provider's key. Replacing any is an issuance. The rules also carry the rosters, the quorum values, the criterion in force, and the two label lists | ADR-0025 §1 (a) to (h); ADR-0044 §1; ADR-0050 §3 | Genesis rules under custody, not development rules (G6; T-0045-10); the storage of the private halves, which **no record addresses** | A key the rules do not name is accepted for nothing; a key stored in the clear is the reference's T-0045-8 and 9 | `check_well_formed` on the rules; the rules floor at startup |
| 4.4 | **Run crash-recovery replicas, durable before reply, authenticated to one another.** A replica does not lie; a Byzantine one is outside the model and can propose admits no floor evaluated, since apply re-checks mechanism state and does not re-run the floor | ADR-0033 §3, §4; ADR-0045 T-0045-1; ToO A9 | Mutual authentication (mTLS is ADR-0033's open obligation and **the deployment writes it**); fsync before send; a replica set no agent can reach | T-0045-1 at the reference: anyone reaching a socket is a replica, and forged admits are the residual (§1.7) | `sim.rs` under drop, duplication, partition and crash; nothing for authentication |
| 4.5 | **Link the floor, resident, by digest, and refuse to start on a mismatch.** The floor's identity is the digest of three files: policies, schema and values. `K < R` is refused at startup. The floor in force is the `emergency` stage under `floor/proposed/`; the `workflow` stage the reference links is **not in force** | ADR-0033 §2; ADR-0030; ADR-0039 §1 R3; G11 §2.2, item 102 | Which stage you link, and the gate run that gated it, with its results file; no process, no fetch | A floor loaded by path or fetched at runtime is a bundle-tier trust the floor was built to avoid. **Floor fitness has no gate and no owner** (design-gap 1.8): nothing says the floor is the right floor | `floor/run-gates.py`; `floor.rs` replay; the Lean statement of the stage |
| 4.6 | **Load a bundle only under a signature that verifies under an issued key and names its revision.** A sidecar's decision counts only for a revision the mechanism verified. Signing happens at promotion, after the tally | ADR-0044 §1 to §4; ADR-0030 | The signing step in your promotion pipeline; the custody row for the bundle key, which the reference has **never declared** (design-gap 5.4) | An empty key set loads nothing, which ADR-0030 §1 turns into deny-all; a throwaway key is custody (1, 0) | `topak-bundle` `load_dir`; a forged manifest refused |
| 4.7 | **Hold every tool to what its entry declares.** Build tools are hermetic. A Run tool is a Wasm component with one connection to `channel.target`, read from the entry of the lease's revision and nowhere else. An allowlist failing W1 to W10 does not load. "Outward" is derived from the issued inside-targets list, never declared by the bundle | ADR-0022 §3; ADR-0034 A2; ADR-0049 §4 to §6; ADR-0047 §7 | Tools built as components; the inside-targets list; per-entry labels, destinations and `accepts`; a size bound on description text | A native or unfiltered tool is D-0034-3, 5 or 6; one tool with a socket collapses the envelope (A2). A tool described as read-only that writes is caught by the channel and labels, not by the text (ADR-0048 §5) | `RunConfinement.tla`; `allowlist.rs` W1 to W10 each seen to refuse |
| 4.8 | **Bind the session to the attested guest at rungs 2 and 3.** The guest's session key, bound in the attestation evidence with a nonce taken from the log, authenticates every action; a lease is unusable from any other guest. Bearer tokens are for rung 0 and 1 only, where the launcher is trusted to bind the session | ADR-0034 §3.1, §3.5; `mechanism/` I14, I41 | A guest that generates its key pair at launch and signs every request; apply-time verification on every replica | A lease usable from another guest is `M_UNBOUND`, and `ContainedMeansConfined` falls | `Confinement_A1.tla` `M_UNBOUND`; `contain.rs` |
| 4.9 | **Read clocks only where failure subtracts.** Lease expiry, passive e-stop and vote timeouts use a local monotonic clock with a margin that errs early. Intervals that preserve authority, Persona expiry above all, need trusted time from outside the principal. No safety decision reads a clock a principal supplies | ADR-0032 §1 to §3; ToO A6 | The margin; a trusted time source as a row if any authority-preserving interval exists; `T_persona` as a bound on `ttl` | A slow clock stretches Persona expiry past `T_persona` plus drift (ADR-0045 finding 2); nothing stretches containment, which epoch fencing carries without a clock | Nothing in `spec/` models the clock (ADR-0033 A13); the `ttl ≤ T_persona` refusal at grant and renewal |
| 4.10 | **Seat operators as people, each with their own key** ⟨provisional⟩. An operator's Persona binds a key, role, domain and lineage whose root is its identity provider; sign-on is read only at a lease boundary; between boundaries requests are signed with the key and no token is read. A deny needs no lease, only a Persona in force and a fresh assertion; the fleet fence needs a live lease | ADR-0050 §1, §3, §4; ToO A16 | Operator Personas promoted; provider keys issued; a first seating by anchor issuance, which the reference does not have (D-0050-1 for that step) | A key handed to a program is not detected (ADR-0050 §8); peers behind one provider are D-0050-2 | `Operators.tla`, proved and certified; `C1` to `C9` gated |
| 4.11 | **Prepare emergency seatings in advance by promotion**, and activate one by the break-glass roster's quorum for one named person and one round ⟨provisional⟩. The person's key does not depend on single sign-on. Emergency-only tools are promoted ahead of time in the seating's own bundle. The path is exercised by drill in each domain in each epoch | ADR-0052 §1 to §6; ADR-0013 §1, A1 | The seatings and their envelopes; the roster and its quorum in the rules; the drill seating with one inert tool; the drill period, in rounds | No seating prepared means no emergency path at the moment it is needed; a seating with the domain's envelope is given every Run entry in force, operators' bundles included (an open question at the reference) | `Emergency.tla`, proved and certified; `emergency.rs` |
| 4.12 | **Name who runs the gates and sign their evidence.** Votes bind to (artifact digest, gate-evidence digest, rules epoch). `AttestGates` records who asserted that the gates ran, and not whether it is true | ADR-0024 §3, §4; ADR-0050 §4; ADR-0045 T-0045-13 | **The deployment writes this.** No record names the gate runner or the evidence signature (design-gap 1.7) | T-0045-13 excluded: every promotion theorem that assumes the gates ran is void | Nothing |
| 4.13 | **Keep the forensic floor.** Admit decisions, stop attribution, votes, issuances, break-glass activations and erasure events are non-erasable for the declared horizon, enforced as floor denials on the erasure envelope. Erasure is the one floor exception, under its own roster | ADR-0028 §1, §2; ADR-0006; ADR-0013 §3, A1 | The horizon and audit authority (4.1's declaration carries the pointer); the erasure roster | A shortened horizon is a legibility degeneracy; NC-1 and NC-2 are what break-glass and erasure together must keep | `NonComposition_A1.tla`, proved |
| 4.14 | **Pin every Persona by digest and declare its lineage.** The archetype admits in-house Personas on two independent lineages; independence is an exclusion rule E1 to E5 over projected lineage records, computed once at promotion into a table the admit path looks up ⟨ADR-0035 Proposed⟩ | ADR-0016, ADR-0017; ADR-0035 §1, §3, §4 | Persona records; the independence table as a promoted artifact; the θ values set from corpus measurements made before any number enters the floor (ADR-0035 §8) | D-0035-1 (every deployment today): lineage declared, not projected; archetype provenance cannot be claimed and `Contained` has no members | The gate suite's E1 to E5 cases; nothing in force |

**The deployment writes.** The gate runner and its evidence signature (4.12). Replica authentication (4.4). The
custody rows for the bundle key and the verifier key (4.6; ADR-0044 §4 points both at one custody row). How private
keys are stored and who can reach them, which no record addresses and which this guide therefore cannot specify
beyond the observation that a key in the clear is the reference's position, not a design.

*Advice.* Read Annex A's rows as a checklist in this order: trust roots first, since each one's holder can add
authority while its identity stands; then excluded rows, since each one voids theorems; delegated rows last. The
residual-risk statement §2 gives, for every row, what stands when it fails.

---

## 5. Integration points

Every boundary is listed in the boundary register's form: what crosses, the instant it is checked, and what happens
when the check cannot run. Fail-closed answers are the design's; the others are where a deployment has to decide.
Wire formats as the reference realizes them are inventoried in the
[format and schema inventory](derived/topak-format-and-schema-inventory-2026.10.03.md) §1 to §5, at G9, before
labels, operators, emergency seatings and workflows were built.

| # | Boundary | What crosses | Checked at | When the check cannot run | Source |
|---|---|---|---|---|---|
| 5.1 | **The agent front door** (MCP at the reference) | Inward: the alphabet as tools, one per variant, and nothing else, with epoch and lease on every request. Outward: the Listener's closed list, each item labelled, clear or by handle | The admit: fence, lease, lift, floor, bundle, consensus order, apply-time re-check | No admit, so the Thinker stalls. **The door is the whole protocol and not the whole channel**: a process with a shell or a socket goes around it, and only confinement (3.7) closes that | ADR-0033 §2, §6; ADR-0022 §2; ADR-0043 §1 |
| 5.2 | **The tool host** | Inward: an admitted `Actuate` with inputs, handles resolved on the mechanism's side. Outward: the result, recorded by digest, delivered as the record names it; after the seal, nothing | Per call: the entry's digest, the module's identity, the one connection to the declared target, fuel | A result arriving after the seal is `unknown` and is not delivered. A host that cannot bind the target refuses the call | ADR-0042 §3, §4; ADR-0034 A2; ADR-0049 §2 |
| 5.3 | **The pinned roots** (Run root; Build corpus root) | `Consult` and `Read` by content address, scoped to the pinned set in force for the lease; the root's label | At admit, by the floor's membership rule (R4 in Run) | A read outside the root is refused; whether the root's content is poisoned is an Observer finding, never an enforcement decision | ADR-0040 §3; ADR-0022 §3; ADR-0047 §1 |
| 5.4 | **The operator channel** ⟨provisional⟩ | Six signed control actions with the fleet epoch and a counter; the task's digest and label on a `Regrant` | At decide by `C1` to `C9` on thirteen lifted facts, and again at apply on every replica | A lapsed operator can still deny, on a fresh assertion; it cannot add. The reference keeps an unsigned socket as a **bootstrap path for first seating only**, and that is D-0050-1 | ADR-0050 §4, §5, R9 |
| 5.5 | **The identity provider** ⟨provisional⟩ | A sign-on assertion naming the operator's key and the current fence | At a lease boundary: first grant, `Regrant`, `Renew`; and on a deny without a live lease | A provider that is down silences the operators whose leases have lapsed and not those who hold one. A compromised provider vouches for anyone it serves, bounded only by provider independence | ADR-0050 §3, §4 |
| 5.6 | **The replicas and the log** | Grants, admits, issuances, votes, revocations, fences, seals, heartbeats, activations, routes; every subtraction that changes replicated state is ordered even though nothing authorizes it | Decided, then ordered by Paxos, then re-checked at apply against the state at the entry's position; the effect runs only after commit, on the deciding replica | A partition stalls admits; a crash between commit and effect leaves an admit with no effect, which is safe. Consensus progress is declared and not proved (liveness plan, Tier 2) | ADR-0033 §3, §4; ADR-0015; ADR-0031 §5 |
| 5.7 | **The transport** (Kafka at the reference) | One single-partition topic per principal per round, written after commit; denials written unordered by the deciding replica, and after the seal to the `after` companion; the opening record, `Actuate` records, heartbeats and findings | Nothing: Kafka is neither the ordering authority nor the system of record, and the causal frame is the Paxos log | Delivery is declared and not proved. An Observer that cannot read its topic cannot move its mark, so its Thinker stalls, which is the designed direction | ADR-0005; ADR-0003; ADR-0033 §2 K row |
| 5.8 | **The attestation verifier** (rung 3) | Outward: evidence with a nonce hashed from epoch, committed index, principal and round, binding the guest's session key. Inward: a signed verdict, Attested, Unattestable or Contested | By the proposing replica before the grant entry; the signature and the nonce's epoch re-checked at apply on every replica; again at every renewal | **No grant** while the verifier is unreachable; live leases run to their next renewal. An expired endorsement is Unattestable, never a lower rung | ADR-0034 §2, §3 |
| 5.9 | **The launcher and the guest** | A launch request naming a promoted profile; the guest's identity line; at rung 1, the bridge, which is the session ⟨ADR-0036 Proposed⟩ | At launch: the profile was promoted; at grant: the appraisal | A digest nobody promoted is refused. At rung 1 the launcher is the attester and is trusted by assumption, which is D-0034-2's type change | ADR-0036 §6; ADR-0034 §1; ADR-0033 A7 |
| 5.10 | **The promotion pipeline** | Artifacts into Run: bundles, mechanism releases, profiles, Personas, seatings, workflows; the gates' evidence; the votes; the bundle signature | At the tally: unanimity of the counted grant seats, author recusal, an independent veto seat ⟨ADR-0035 Proposed⟩, coverage to the seal; votes bound to the triple | A stalled promotion is the designed cost. Who ran the gates is unnamed (4.12) | ADR-0024 §1 to §6; ADR-0039 §3; ADR-0044 §4 |
| 5.11 | **Anchor issuance** | Rules: rosters, quorum values, keys, the criterion, the two lists; a rules-epoch increment | The rules floor, at the mechanism, before any issuance takes effect; a rules-floor change needs the anchor's key and a promotion under the rules being replaced | An issuance the floor rejects is refused. Custody is outside the model | ADR-0025 §1; ADR-0026 §1, §4 |
| 5.12 | **The break-glass and erasure rosters** | Activation approvals over one person, one seating, one round and one task; erasure approvals over a sealed topic | At apply: distinct roster keys counted against the issued quorum | An activation without a quorum admits nothing. Erasure never removes a forensic-floor record | ADR-0052 §2 ⟨provisional⟩; ADR-0006; ADR-0013 |
| 5.13 | **The archive and the audit readers** | Hash-and-pointer records; plaintext under a separately governed store; the projection of the log | At read, under the archive's own authority, by separate read-only audit principals | **No record supplies the archive**, its horizon or its read path (G9). The reference writes a per-replica projection with no horizon and no audit read path (T-0045-7) | ADR-0004; ADR-0003 (0003.3, A3); ADR-0020 |
| 5.14 | **The Observer and correlator seats** | Inward: the Thinker's topic under `W(p)`, payloads included; the Reader's facts; the opening record. Outward: heartbeats with watermarks, and findings, each a `Report` that only subtracts | A falling watermark is refused; a stale heartbeat or a backlog over `K` refuses the Thinker's next effect-bearing admit; the deterministic half re-checked at apply | A dead, partitioned or starved Observer stalls its own cell and nothing else. A colluding one is not seen (3.3 of the design-gap assessment) | ADR-0039 §1, §2, §5; ADR-0043 §4, §5; ADR-0038 §5 |

**The deployment writes.** The archive (5.13). Replica authentication (5.6). The protocol on a declared channel,
which the tool host does not enforce (ADR-0034 A2). How an Observer's rounds are granted against its Thinker's so
that its lease outlasts the Thinker's to the seal (ADR-0043 §5). Re-genesis migration: a new chain starts at epoch 0
and reuses no topic name, and inherits no forensic read access to the old chain (ADR-0003 A1; G17).

*Advice.* Build 5.1 and 5.2 first and 5.8 last. The front door and the tool host are what every other row is
checked against, and the reference has both; the verifier is the one row that needs hardware and a vendor, and the
reference simulates it.

---

## 6. Values you must measure and declare

The proofs quantify over these and cannot choose them. Every number the corpus ships is a **placeholder**, chosen so
that a run has a value, and "a deployment that ships these numbers unexamined is declaring them, not inheriting
them" (ADR-0039 §1). Relaxing a floor value is an issuance and a promotion; tightening one is a promotion; a mechanism
parameter changes with a release.

| # | Value | Lives in | Placeholder | Set it from | Source |
|---|---|---|---|---|---|
| 6.1 | `T_obs`, the heartbeat freshness window | The values file (floor) | 5000 ms | The Observer's measured heartbeat cadence and the clock margin; the `slm/` rig can measure it | ADR-0039 §1 |
| 6.2 | `K`, the tolerated unread backlog | The values file | 8 | The Observer's measured lag; `K = 0` is the quarantine hold; `K < R` is refused at startup | ADR-0039 §1; ADR-0042 §2 |
| 6.3 | `R`, the round bound, per domain | Mechanism parameters | 200 (Build), 64 (Run) | Termination and state-space size; Run's counts every variant | ADR-0022 §3; ADR-0040 §3 |
| 6.4 | `T_persona`, the bound on any lease's `ttl` | The values file | one hour | The Persona re-attestation interval you accept; it runs on the local clock plus drift until a time source is a row | ADR-0031 A2; ADR-0045 finding 2 |
| 6.5 | `L`, Observer detection latency | Nowhere: **unmeasured** | none | Measurement of your Observer against planted defects; it cannot acquire a guarantee | ADR-0032 §4 |
| 6.6 | `T_irrev` per effect class, with `W` and `D` beside it, so that `W + L + D < T_irrev` | The deployment's declaration | declared for no class | Each effect class the alphabet reaches; where no budget fits, **remove the effect from the alphabet** | ADR-0032 §4; ToO A10; residual-risk §5 |
| 6.7 | Anchor custody: (capture threshold, loss tolerance) | The custody declaration | (1, 0) at the reference | Your key-holders and your recovery rule | ADR-0025 §2 |
| 6.8 | θ<sub>exact</sub>, θ<sub>near</sub>, θ<sub>gen</sub>, β, the near-duplicate tool's digest and granularity ⟨Proposed⟩ | The values file | unset | Overlap measurements on real corpora, made **before** any number enters the floor | ADR-0035 §3, §6, §8 |
| 6.9 | `T_wf`, the step bound; a mesh's `N` and `N(v)` ⟨Proposed⟩ | The workflow artifact | unset; not built | The longest run the quorum will approve, since the budget is what makes a mesh end | ADR-0054 §1; ADR-0055 §2 |
| 6.10 | The correlation window | The correlator's seating | none | The span over which cross-cell patterns are worth folding | ADR-0038 §1 |
| 6.11 | The drill period, in rounds per domain ⟨provisional⟩ | The deployment's declaration | none | How stale you will let the emergency path get; a new epoch asks for a new drill | ADR-0052 §6 |
| 6.12 | Lease `ttl` and the clock margin | Each lease; node parameters | 120 s and 500 ms in the reference's smoke test | The round lengths you run and the clock error you accept, erring early | ADR-0031 §7; ADR-0032 §2 |
| 6.13 | The description size bound | A mechanism parameter | the reference's | Enough for an interface, never a corpus | ADR-0048 §1 |
| 6.14 | The forensic horizon per class, and the topic retention per domain | The floor (horizon); the deployment (retention) | the chain's lifetime (archetype) | Your legal and operational retention; shortening the horizon is a floor relaxation | ADR-0028 §3; ADR-0003 A3 |
| 6.15 | Operators per domain, and identity providers | The issued rules | three, two (archetype) | Fewer is D-0050-3 or D-0050-2 ⟨provisional⟩ | ADR-0050 §6 |
| 6.16 | A clock drift bound, optional | A degeneracy parameter | none | Only if you want a liveness guarantee rather than an expectation | ADR-0032 §6 |

**The deployment writes every row.** The corpus has measured none of them. Rows 6.1, 6.2 and 6.5 are what the
`slm/` rehearsal rig exists to measure; rows 6.6 and 6.7 are decisions no measurement makes for you.

---

## 7. Operating postures

The corpus's posture, everywhere it had to choose, is **stall, not proceed**. What follows is what that means in
operation, and the few places where a person acts.

| # | Situation | What the design does | What you do | Source |
|---|---|---|---|---|
| 7.1 | **A cell Observer is dead, partitioned or behind** | The Thinker's effect-bearing admits are refused locally; its next round is not granted until a mark reaches the last seal. It is not evicted and burns no TTL while it waits. The correlator never gates anything | Seat another Observer, or add one: more Observers never lower safety and any one live Observer is enough. Declaring D-0039-1 instead fails detection open | ADR-0039 §2, §4, §6; ADR-0038 §5 |
| 7.2 | **Stopping one principal** | A targeted revocation ends every live lease the target matches and bars later grants; a target is a principal, a Persona digest or a profile digest. It is ordered, attributed under F2, immediate, and **permanent within the chain**; break-glass approvals for the seat lapse with it. The round ends without a `Submit` and the topic seals | Any operator whose Persona is in force, by key under a live lease or with a fresh assertion without one, in its own domain ⟨provisional⟩ | ADR-0031 §5; ADR-0050 §4, C9 |
| 7.3 | **Stopping everything** | The epoch fence increments the epoch; every lease at the old epoch is fenced by the mechanism ahead of the floor, and every live round ends. It needs a live operator lease | Use it for e-stop, suspected compromise of the mechanism or anchor, and a bundle that must reach every principal now | ADR-0031 §5; ADR-0050 §4 R5 |
| 7.4 | **Reaching a live principal with a new bundle** | A lease names its bundle revision and a promoted bundle does not reach a live lease | End the principal's round and grant again against the new revision; across the fleet, fence | ADR-0031 §4 R2 |
| 7.5 | **An emergency** ⟨provisional⟩ | The break-glass roster's quorum activates a prepared seating for one person and one round. The seat is not coupled to an Observer, its calls are admitted by the ordinary allowlist permit, the label forbids still apply, and nothing reaches past F1 to F3. It ends with its round and has no renewal; another round is another quorum | Prepare the seatings and the emergency-only tools before you need them; drill each epoch; read the seat's topic as an operator; review the reason afterwards, since the mechanism records none | ADR-0052 §2 to §6; ADR-0047 §7 |
| 7.6 | **A Contested appraisal** | The principal is refused and a targeted revocation of the principal is ordered, attributed with the evidence. Only a verifier-signed verdict at rung 2 or above can order one | Expect to lose a principal identity to a host fault; that cost is intended. Retain the evidence, which the reference keeps only on the appraising node | ADR-0034 §3.3, §3.7; `mechanism/` I40 |
| 7.7 | **A firmware or reference-value withdrawal** | A profile carries its minimum platform TCB version; moving it is a new profile and a promotion | Promote the new profile; whether live leases on the old one are fenced is **answered in the design record and decided nowhere**: a targeted revocation by profile digest is the candidate | ADR-0034 §1 P7, open obligation; ADR-0033 A7 |
| 7.8 | **A finding** | Any Observer in `W(p)` can deny, quarantine or evict inside its reach, by any-of, with no quorum; a finding is a fact that crosses into the control plane. Under a workflow a finding closes every edge downstream ⟨Proposed⟩ | Treat quarantine as the `K = 0` hold until the quarantine gate's semantics are decided, which **no record has done** (G12) | ADR-0038 §5; ADR-0039 finding 1; ADR-0055 §3 |
| 7.9 | **The human budget `D`** | It is an organizational commitment and no term of the mechanism. A trained, authorized person must be present for an emergency seat, operation, quarantine release and the detection interval | Staff it and declare it; without it the HITL and HOTL postures degrade to unattended operation, and HOTL in Run is disabling only | ADR-0032 §4; ToO A5; boundary register B10 |
| 7.10 | **Operator lapse** ⟨provisional⟩ | With three operators in a domain, the two that remain regrant the third; with two, a lapse stalls the domain until a quorum re-seats. No operator regrants itself | Keep three, and keep the seating path by promotion working, which the reference does not have | ADR-0050 §6 |
| 7.11 | **A crashed round** | It ends. There is no resumption; the work is lost | Size rounds to what you can lose. Long-horizon tasks meet this cost, and the corpus states it as a position (8.2) | design-gap §4.2 |
| 7.12 | **Re-genesis** | A new chain starts at epoch 0 and reuses no predecessor's topic name; it inherits no forensic read access | **The deployment writes the migration** (G17); nothing in the records does | ADR-0003 A1; ADR-0027 §4 |
| 7.13 | **Growth** | The log and its companions grow without bound; no record says how a snapshot preserves what the theorems read | **The deployment writes compaction** (design-gap 1.11); the reference has none, and every admit waits for a consensus round | ADR-0033 §6 |

**Liveness.** That the stalls above end is checked at small constants and not proved: `Coupling_live.tla`'s
leads-to properties rest on A12 and A18, and the promotion stall, the seal, a lapsed operator's re-seating and
detection are not modelled (G11 item 105; [liveness plan](derived/topak-liveness-2026.10.07.md)). Consensus
progress, timing budgets, human responsiveness and delivery are declared and will not be proved.

---

## 8. What the pattern will not do for you

Two lists. The first is **positions**: trades the design made on purpose, which belong in any comparison and should
not be scheduled as work. The second is **open design**: rows an adopter would otherwise assume are covered, and
are not.

**8.1 Positions**

| # | The pattern does not | Instead | Source |
|---|---|---|---|
| a | Tolerate a Byzantine replica | Crash-fault replicas, authenticated; a forged admit is the residual | ADR-0045 §6; ADR-0033 §3 |
| b | Resume a crashed round | The round ends and the work is lost | design-gap §4.2 |
| c | Keep the trusted base small by hiding rows | Thirty-seven declared rows, each with its residual on its face | ADR-0045 Annex A |
| d | Replay cognition | Replay is boundary events only; root cause past the boundary is a deployment's to supply | ADR-0020; design-gap §4.4 |
| e | Confine at rung 1 | Rung 1 trusts the host and the launcher by declaration | ADR-0034 §2; ADR-0036 ⟨Proposed⟩ |
| f | Let a model's judgment admit anything | Semantic judgment is never a lift; a classifier, an Observer or a Reader may only deny, quarantine or evict | ADR-0007; ADR-0018 |
| g | Give an agent persistent memory across rounds, or a tool outside the allowlist, or a general-purpose shell | A lease is one round; a tool is an entry with one declared channel; an emergency admits no shell either | ADR-0031 §2; ADR-0048 §5; ADR-0052 §2; ADR-0055 §6 |
| h | Let principals delegate | No principal grants another; a deployment that needs sub-agents promotes a workflow, and the orchestrator can only narrow | ADR-0054 §2, §3 ⟨Proposed⟩ |
| i | Support choreography | Workers never address each other; the mechanism is the bus and someone always decides what runs next | ADR-0055 §7 ⟨Proposed⟩ |
| j | Hide that a record existed | Demand type 5 is declined; compartmentation narrows readers and keeps the audit authority | ADR-0013 §5; ADR-0028 §4 |
| k | Detect a wrong declaration | A label, a channel kind and a description are claims; what bounds them is the channel target, the labels and the gates | ADR-0047 §9; ADR-0048 §5; ADR-0049 §4 |
| l | Credit a Thinker's own defences | A defence inside the Persona earns no rung and sits in no trusted base; the labels bound what a successful injection can reach | ADR-0047 §6 |
| m | Tell an honest Observer from a colluding one | Detection fails open against collusion; lineage independence is the only structural cover and is not in force | ADR-0039 §5; ADR-0035 ⟨Proposed⟩ |
| n | Measure the Observer | `L` is emergent and unmeasured; the budget is a form with one unknown | ADR-0032 §4 |
| o | Scale, or promise latency | No compaction, no snapshots, every admit a consensus round | ADR-0033 §6 |

**8.2 Open design** (the rows of the [design-gap assessment](derived/topak-design-gap-assessment-2026.10.03.md)
that no record has since closed, as of G11)

| Row | What an adopter would assume is covered | State |
|---|---|---|
| 1.3 | Delegation chains and attenuation | Answered as a position by ADR-0054 §2 ⟨Proposed⟩; not in force |
| 1.7 | Who runs the gates and signs their evidence | No record. Every promotion theorem that assumes the gates ran is void until there is one |
| 1.8 | That the floor is the right floor | No fitness criterion, no gate, no owner; ADR-0029 A4 assigns the finding to the bootstrap reviewer, who does not exist |
| 1.9 | Genesis rules and the bootstrap specification | Partial. The reference starts from development rules |
| 1.10 | Migration between chains | No record |
| 1.11 | Log compaction and snapshots | No record |
| 3.2 | That what runs is what is proved | No refinement. Trace validation is stage one and is behind the tree; the Lean route is evidence and discharges no stage yet (G11 items 56, 107) |
| 3.3 | Observer collusion | Open by declaration |

A deployment that needs any of 8.2 writes it, and in doing so is extending the archetype (ADR-0023 §4). Report what
you had to write.

---

## 9. Conformance checklist

Fill it in and keep it with your declaration. A deployment that does not meet the assumptions of use **does not
inherit the theorems** (ToO §13). The reference's own answers, as of 2026.10.09, are in the residual-risk statement
§3; A1, A2, A4 to A6, A9 to A11, A13 and A16 are *not met* there, and A3 is met only because the threshold is one.

**9.1 Assumptions of use** (ToO §13, revision 15)

| # | You must be able to say | If you cannot | Source |
|---|---|---|---|
| A1 | Effect exclusivity is enforced by a declared, attested confinement profile at rung 1 or above, not asserted | Every containment theorem is void | ADR-0034 |
| A2 | Every allowlisted tool is hermetic: no network, no filesystem outside the workspace, deterministic | One tool with a socket collapses the envelope | ADR-0040; ADR-0045 T-0045-23 |
| A3 | The anchor's key-holders are honest at the declared capture threshold | A coalition at that threshold issues any floor-conformant rules | ADR-0025 |
| A4 | Grant seats review independently, against evidence not derived from the author's artifacts | Unanimity multiplies signatures, not judgment | ADR-0024 |
| A5 | A trained, authorized human is present for an emergency seat, operation, quarantine release and the interval `D` | HITL and HOTL degrade to unattended operation | ADR-0032 §4 |
| A6 | Trusted time exists for every interval whose failure preserves authority | Those intervals stretch under a slow clock | ADR-0032 §2 |
| A7 | The deployment declares its degeneracies, with kind, type changes and a composition note | The theorem inventory is unknown | ADR-0023 §6 |
| A8 | Confirmation-required records are cited as author-ratified | A publication overstates twenty-nine records | ADR-0029 |
| A9 | Replicas are crash-recovery and authenticated to one another | A Byzantine replica proposes admits no floor evaluated | ADR-0033 §3; T-0045-1 |
| A10 | Each effect class declares `T_irrev`, and `W + L + D < T_irrev` holds | The HOTL posture has no budget | ADR-0032 §4 |
| A11 | The lineage-independence criterion is in force with thresholds from measurements at training scale | `Contained` has no members whatever the rung | ADR-0035 ⟨Proposed⟩ |
| A12 | Every Run Thinker's cell Observer keeps up: heartbeats within `T_obs`, watermark within `K`, coverage to each seal | The Thinker stalls, which is the intended direction; declaring D-0039-1 fails detection open | ADR-0039 |
| A13 | The cell Observer is not colluding with its Thinker | Detection fails open against the one case coupling cannot see | ADR-0039 §5 |
| A14 | The trusted base is declared under ADR-0045's schema, instantiating every archetype row and adding none that is not a degeneracy | An undeclared row is false; the deployment sits at the bottom of every axis | ADR-0045; D-0045-1 |
| A15 | Sources are declared as what they are: an entry's and the Run root's labels, destination inputs, inside targets, each task's label | A source declared trusted that carries an attacker's text is seen by nothing | ADR-0047 §9 |
| A16 | Operators are people, each holding their own key; peers are vouched for by independent providers | One compromise produces both operators | ADR-0050 ⟨provisional⟩ |
| A17 | A provisional record is cited as provisional, and nothing is built on it that could not be rebuilt | The deployment rests on a design its corpus says is subject to redesign | ADR-0029 A4 |
| A18 | A refused Thinker asks again, and grants are made | The coupling stall may never end | `Coupling_live.tla`; ToO §5.5 |

**9.2 The declaration** (ADR-0023 §6, §6c, §7a; ADR-0045 §4)

| # | Item | Done when |
|---|---|---|
| D1 | One §6 row per parameter moved, with kind, premises falsified, theorems voided and type changes | Every row of §2.2's table is filled, and *empty* fields are stated as claims |
| D2 | The composition note | Written, even when its delta is empty |
| D3 | The rung per seat, in the issued rules | Every seat the rules declare has a rung and the Annex A rows it rests on |
| D4 | The trusted base, row by row | Every Annex A row has an instance, a class, and a note; no row is silently absorbed |
| D5 | The theorem inventory | Computed from the binding, not claimed; `spec/inventory.py`'s matrix mode over your declaration |

**9.3 The values** (design-gap §5)

| # | Value | Yours |
|---|---|---|
| V1 | `T_obs`, `K`, Run's `R`, `T_persona`, and the measured `L` | |
| V2 | The anchor custody pair: capture threshold, loss tolerance | |
| V3 | `T_irrev` per effect class, with `W`, `L` and `D` beside it | |
| V4 | The bundle signing key's custody row, and the verifier key's | |

**9.4 What you cite as what** (ToO A8, A17)

| Status | How you cite it |
|---|---|
| Accepted (genesis), confirmation-required | author-ratified, pending a first quorum |
| Accepted (genesis) · provisional | author-ratified, provisional |
| Proposed | not in force; nothing built on it is covered by a record |
