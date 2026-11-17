# TOPAK — Assessment against SICI, the NIST AI RMF profile discussion draft of 2026.11.09, at G12

**2026.11.16** · derived · a reading, not a record · basis: Genesis Checkpoint G12 (2026.11.16) as the state of
record, read at the tree at `51d7f5b`, with Theory of Operation revision 15, the glossary and the architecture
description revision 3 (`narrative/`), re-checked at `9bf4d7b` (below), and the record files under `decisions/` where
a row quotes them · read against *Automated, Agentic, and Super Intelligence in Critical Infrastructure and
High-Consequence Applications* (**SICI**), the NIST AI RMF Community of Interest discussion draft by Raymond Sheh and
Martin Stanley, version `20261109_1200a`: its Summary, Profile and Guidebook · updates Part II of
`topak-external-alignment-2026.10.09.md` (TACIP 09.13(b) at G11) and §8.2 of
`topak-external-and-competitive-assessment-2026.10.05.md` (TACIP 09.28(a) at G10), which stand for what this document
does not re-read · prepared by the assistant at the custodian's request: "Do an assessment against TOPAK at G12 and
add it as a derived doc."

Nothing here is ratified, and this document proposes no decision text. Where it suggests an entry, none is made.

**Sources, by digest.** The SICI Summary (4 pages, `9985c51f2eeb2a91…`), the SICI Profile (39 pages,
`4414388c5fc1c841…`) and the SICI Guidebook as a zip (`bf1d83269140474a…`). The zip holds a web edition, the
assistant-ready Markdown (`5603bb57726a43d8…`) and a YAML knowledge graph (`e7123d2d9e403ead…`), which calls itself
"DERIVED, NOT AUTHORITATIVE". The Markdown was read as the Guidebook's text. None of the three is held in the tree:
`.gitignore` excludes `doc/`, PDFs and zips, and `.github/CONTRIBUTING.md` refuses them.

**SICI is TACIP, renamed.** The Guidebook's changelog says the 2026.11.09 version "follows the Sep 28, 2026(a) draft",
and that "No Practice, Task or Implementation has been removed, and apart from seven new Implementations, item numbers
are unchanged". The YAML's generator is still named `build_tacip_graph.py`. So every TACIP item the corpus cites by
number resolves to the SICI item of the same number. This document cites SICI's items by number, and calls the earlier
drafts TACIP, as the corpus did.

**Method.** One reader, the drafter, with no delegated readers. Read in full: the Summary; the Profile's front matter,
introduction, trustworthiness table and Practice 1; the Guidebook's §1.4, its Conceptual Changelog, the 33 scenarios
of Appendix B and the D.1 table of Appendix D. Also read in full were the text of the thirty-three Implementations
cited in §2 to §5, without their reference lists: 2.2.2, 3.2.2, 3.2.3, 3.4.3, 3.9.5, 3.9.6, 4.1.1 to 4.1.3, 4.3.2,
4.5.1, 4.5.2, 5.2.2, 5.3.2 to 5.3.4, 6.1.5, 6.2.2, 7.4.1, 7.4.2, 7.5.1, 8.1.6, 8.2.2, 10.1.2, 10.1.5, 12.1.2, 12.1.3,
12.2.1, 13.2.1 to 13.2.3, 13.3.1 and 13.3.2. Every other item was read by title, search keywords and search. On the
corpus side the drafter read G12 whole, the glossary's §1, §3, §5, §6, §8 and §10, the architecture description's §10,
Part II of the 10.09 alignment, and record text where a row quotes it. **Every quotation below, of SICI or of a
record, was checked mechanically against its file** (apostrophes and emphasis markers aside). Nothing was run: no
module, gate, test or manifest check.

**Not independent.** This is the drafter's reading of the drafter's corpus. It does not count under ADR-0029 A2, gives
no verdict on floor fitness and dispositions nothing. §5 notes that SICI 12.1.2 says the same of a review like this
one.

**Since the basis.** Two merges landed on `main` after `51d7f5b`, both on 2026.11.16, ending at `9bf4d7b`: Theory of
Operation revision 16, the glossary, the architecture description's revision 4 and the reviewer's guide, drawn against
G12 (`6038475`), and their tags (`cd97cb3`). They discharge the narrative half of G12 item 109. No record, checkpoint
or derived document changed. Every quotation of the narrative below was checked again at `9bf4d7b` and still matches,
and the glossary's section numbers cited here are unchanged. Revision 4 of the architecture description still says
"TACIP", which bears on §1, SA-9 and §9 item 5.

---

## 0. Verdict

**SICI is TACIP grown, not changed in shape.** It keeps the thirteen Practices and their numbers. It adds seven
Implementations (3.6.4, 3.9.6, 4.6.4, 5.3.4, 7.2.4, 10.1.5, 10.2.2), a *Decisions for the Organization* field on 218
items, about 640 references and a 66-term glossary. It also adds a responsibility paragraph that asks who judges an
agent fit for its role. The 10.09 reading of TACIP 09.13(b) therefore carries over cell by cell, and §2 re-marks it at
G12.

**The draft moved toward the pattern.** Seven things SICI now says are things the corpus holds by construction:

- **The enforcement layer writes the record of what was done** (10.1.2). ADR-0042 §3's `Actuate` record already works
  this way.
- **Losing the wrapper removes the agent's authority, not its limits** (3.2.3). This is the passive e-stop.
- **A constraint may not rest on what the model says about its own output, and one violation is not offset by passing
  others** (3.2.2). These are ADR-0007 and forbid-overrides composition.
- **A stop is cheap and a return is not** (4.1.2). This is "consensus for grants, local for denials".
- **Reachability is judged by what interfaces and credentials permit, not by the intended role** (6.1.5). This is
  havoc semantics over an alphabet.
- **Zero trust is applied to compromise and malfunction alike** (§1.2). This is the Byzantine premise.
- **Logs are protected in proportion to use and are not assumed immutable** (10.2.2). This is legibility in place of
  immutability.

The texts do not say whether the corpus contributed any of this or it arose independently, and this document does not
guess.

**Little moved at G12, since no record entered force after G11** (G12 §1). Three readings move on SICI's own text:

- **3.9.5's *Verifiable* test was misapplied at 10.09** (§5.1). It concerns the capability's account of itself, which
  TOPAK's mechanism does not rely on, and not the corpus's authorship.
- **13.3.1 becomes matched**, because SICI now asks that the decision not to capture volatile state be recorded, and
  ADR-0020 records it.
- **12.1.2, 12.1.3 and 7.4.1 move from G to P on the corpus.** SICI now accepts a recorded arrangement where
  separation of author and approver cannot be had, and the corpus records its own. Independence itself stays G
  (12.2.1).

**What SICI asks and the corpus lacks** is ten items, SA-1 to SA-10 (§4). These are the main ones:

- **Protective paths outside the wrapper.** No record asks a deployment to say that its trips and stops do not pass
  through the mechanism.
- **A fail-safe state per effect class and per refused step part-way through a sequence.** ADR-0023 still has no field
  for either.
- **Cumulative limits on an effect's parameters.** `seq` counts effects and sums nothing.
- **A person at a `release` seat in a window measured in seconds.** SICI 4.5.1 says that judgment does not fit there
  (ADR-0066, Proposed).
- **Resource limits at the launcher**, which G12 item 119 says apply none.

**Read onto the corpus** (§5), SICI names four of G12's own conditions:

- CI in detect-only mode (3.4.3).
- A verifier kept in service with known defects and no date to move (Practice 6's deferral tension).
- Review by the drafting process not counted as independent (12.1.2).
- No meta-safeguard for verifiers that an assistant drafted (12.2.1).

The corpus already says each of these about itself. SICI supplies the external wording.

This document does not re-grade. The B+ is the 10.02 review's, carried at 10.09.

---

## 1. What changed from the TACIP drafts the corpus read

| Change in SICI | Where | What it means for a reading of TOPAK |
|---|---|---|
| **"Super Intelligence" (SI) replaces "AI"**, after Executive Order 14434. SI means the systems 15 U.S.C. § 9401 defines as AI | Title note; §1 | Nothing substantive. The architecture description's §10.1 and stakeholder S8 still say "TACIP" and cite the 09.28(a) copy, in revision 4 as in revision 3. Its next revision could carry the new name |
| **Item numbers unchanged; seven new Implementations** | Changelog, 2026.11.09 | The corpus's TACIP citations resolve. Of the seven new Implementations, 3.9.6, 5.3.4, 10.1.5 and 10.2.2 land on TOPAK (§2, §3) |
| **Decisions for the Organization**, on 218 items | Every Practice | Most of the pattern's placeholders are, in SICI's terms, this field: `T_irrev` per effect class, `K`, `R`, `T_persona`, the correlator's thresholds, the lineage θ. The adopter's guide's deployment declaration is the corpus's form for answering them, and none has been written (G12 §8) |
| **Governance evidence and technical evidence** are distinguished, and "the first does not imply the second" | Profile §1; 1.3.4 | TOPAK produces an unusual amount of technical evidence about its enforcement layer: 34 proof modules, 13,622 obligations, TLC mutations and the Lean route. By premise it produces none about the SI system itself (ADR-0007). SICI wants both, for the SI system |
| **Who judges an agent fit for its role.** For a person, IT checks identity and other roles judge competence. For an agent, the second judgment "often falls to IT by default" | Profile §1; Appendix A.1.11 | TOPAK puts that judgment in a named act of record: a **seating**, made by a quorum, that names the Persona, its confinement, the bundle and the bounds on its tasks' labels (ADR-0050 §2, provisional; ADR-0024). What the quorum relies on is gate evidence, which is still an assertion (G12 §8), and floor fitness "has an owner and a time, and no test" (ADR-0024 E1) |
| **Zero trust applied to SI risk generally**, verified wherever outputs cross into other systems, "whether a departure from expected behavior arises from compromise, malfunction, or a change in operating conditions". **SI Attack Surface** is separated from **SI Risk Surface** | Profile §1; 3.8.1, 3.8.2 | The Byzantine premise and havoc semantics are this principle, taken as a premise: the mechanism does not ask why a principal departs. SICI keeps the two surfaces apart for triage (8.1.6), and TOPAK does not need them apart to act (§4, SA-10) |
| **How far to go: measures as a matter of degree; the design basis** | Section 2 preface | The corpus's degeneracy discipline matches: a deployment declares what it gives up, and "Degenerate forms lose theorems, never gain capability" (glossary §5) |
| **A recorded arrangement where separation cannot be had** | 4.1.2, 6.2.2, 7.4.1, 12.1.2, 12.1.3 | This lands on the corpus, where one custodian authors, ratifies and reviews (§5.2) |
| **Logging no longer assumes immutability** | 10.1.2, 10.2, 10.2.2 | This matches the corpus's **legibility**, which the glossary says "replaces" immutability (§6) |
| **Appendix B rebuilt** as 33 illustrative composites (B.1 to B.33), each with the characteristics at stake | Appendix B | TACIP's incident list `i1` to `i32`, which 10.09 §2.6 cites, is gone. Those numbers do not resolve in SICI. §6 re-reads the new scenarios |
| **Appendix D.1**: seventeen control areas, each with its assumption and how SI systems break it | Appendix D | It reads as a list of the assumptions TOPAK was built not to make. §7 answers it row by row |

---

## 2. By Practice at G12

Marks use the 10.09 key: **M** matched, **P** partial, **C** convertible, **G** gap, **X** out of scope. The basis for
**M** is the same: a record in force at G12, or a named mechanism, discharges the outcome. A Proposed record or a
pending amendment does not count, and a row that rests on one says so. A record that is Accepted but
confirmation-required counts as author-ratified. A provisional record (ADR-0050, ADR-0052) counts, and the row says
so.

| Practice | G12 | Basis, and what moved since 10.09 |
|---|---|---|
| **1** Requirements for success | X on the model; P on the mechanism | Unchanged. 1.3.4 now pairs governance with technical artifacts, and the mechanism has both. 1.1.2's structured requirements map has a Proposed counterpart in the specification graph (ADR-0057, ADR-0058: "a guarantee carries its…"). 1.4.4, requirements for SI-generated logic, lands on the corpus (§5) |
| **2** Robustness, resilience, QoS | P | 2.1.1: `seq` counts effect-bearing admits (ADR-0042 §2), `K < R` is checked at startup, and the activation budget (ADR-0055, Proposed) bounds a mesh. **2.2.2 now asks that watchdog logic be "strictly non-AI, lightweight, and deterministic".** TOPAK's watchdog in that sense is the mechanism's coupling check (`live(o)`, floor entry R3) and the lease's expiry. The Observer is a model, which SICI would place under 3.4 as monitoring, not as a watchdog (SA-9). 2.4 and 2.5 are X (model behaviour) |
| **3** Agentic behaviour | P | §3 and SA-1 to SA-5. 3.2.2 and 3.2.3 are M in design and P in what a deployment can declare. 3.4.3 is P. 3.5.4 is now a named defect at G12: the launcher applies no memory, CPU or environment limits (item 119; SA-6). **3.9.6, new, is M for the corpus** (ADRs, ADR-0045's rows with what stands when each fails, the residual-risk statement, the D-numbered degeneracies), and is owed by every deployment's declaration, none written. 3.9.5 is re-read in §5.1 |
| **4** Override, recovery, awareness | P | **4.1.1 M in design**: no stop depends on the principal. A deny needs no lease (ADR-0050 §4, provisional), expiry subtracts on a local clock (ADR-0032), and `FenceEpoch` ends every live round. 4.1.1's new test, whether an agent "continues a blocked action through another tool or delegated agent, or by starting a replica of itself", has a structural answer: no principal seats another, a principal holds one live lease, and the label forbids are monotone in what the round has read (ADR-0047). It is tested by mutation in TLC and not at a deployment. **4.1.2's asymmetry is the corpus's organizing rule** (§3), but its return condition asks for "an understanding of the cause", which the mechanism by construction does not hold (SA-8). 4.1.3: the drill (ADR-0052 §6, provisional) is not counted at the reference (item 92). 4.2 and 4.4 are G: no record alerts a person (SA-7). 4.5.1 and 4.5.2: §4, SA-4 |
| **5** IdAM for agents | M / P | 5.1.1 and 5.3.3 as at 10.09. **5.2.2 M in design** for per-action authorization on mechanism-held facts, re-checked at apply, and for context that narrows authority after untrusted content (ADR-0047 F1 to F3). Its cumulative clause is SA-3. 5.1.3 mutual authentication between replicas is still absent; A9 assumes the replicas are not compromised. **5.3.2's new bound, that delegated authority not exceed that of the person on whose behalf an agent acts**, is ADR-0056 (Proposed), with downstream authorization excluded as a position (T-0045-39). **5.3.4, new, is P**: §3 |
| **6** External supply chain | X / P | SIBOM and procurement are out of scope. **6.1.5** now judges reachability by "software, interfaces and credentials", which is the pattern's basis (§3). Its attestation records the deployment architecture, which ADR-0023 and ADR-0058 (Proposed) would hold. 6.2.2: a Persona pins the model and its decoder, and the `Actuate` record carries the tool's name and digest (ADR-0042 §3), so a changed tool shows after the fact. **Practice 6's deferral tension lands on the corpus's prover pin** (§5.5) |
| **7** Internal provenance | M / P | 7.3.2 and 7.3.3 as at 10.09. 7.4.1: the History rows record what, who and on what evidence. The approver is the author, which SICI now accepts if recorded with its offset (§5.2). 7.5.1: frozen modules and a manifest per cut keep a previous version measurable, but the reference follows text not in force. 7.6.2's archiving and destruction have a Proposed answer (ADR-0074 to ADR-0076), and crypto-shredding is rejected (glossary §6) |
| **8** Incident analysis | P / C | 8.1.2 and 8.2: TOPAK is in the class by its own decision (ADR-0020, boundary events only). **10.1.5 now accepts that decision if what cannot be reconstructed is recorded**, and ADR-0020 records it. What is missing is the deployment field (ADR-0023 has none). 8.1.5: a workflow's `Route` carries its basis (ADR-0054 §8, Proposed). 8.1.6: X by premise, and now compatible (SA-10). 8.6.2's independent route exists for the corpus (`SECURITY.md`). The F1 disclosure decision is open (ADR-0070, item 115) |
| **9** Training | X | ADR-0071 (Proposed) gives every role in Build, Run, governance and outside a document set. That is what a 9.1 competency map would point at. There is no training and no proficiency record |
| **10** Logging and audit | M / P | **10.1.2 M**: the mechanism writes each `Actuate` record, and "The principal does not write it and cannot" (ADR-0042 §3). An effect runs only after its admit commits (glossary §6, "Decide, order, re-check"), which is 10.1.2's "authorization decision… committed… before the action executes". Denials are recorded, unordered (ADR-0020). The architecture description's row 9 says the record is "Tested, not proved". **10.1.5, new, M**: ADR-0037 §3 keeps raw emission "for one purpose: re-run the decoder and compare", and ADR-0075 (Proposed) gives every holding a line in one retention schedule. **10.2.2, new, M** by legibility and the forensic floor (ADR-0028). 10.3: the correlator, Proposed and not built (ADR-0051) |
| **11** Mission continuity | X / P | As at 10.09. 11.2.4 controlled isolation: fence, expiry and the resident default-deny floor. 11.4 re-commissioning: a new first lease is a quorum's act |
| **12** Verify SI-generated artifacts | **G on independence; P on recording** (corpus); P on the mechanism | §5.2 to §5.4. For a deployment, ADR-0070 (Proposed) makes the developer's agent "a havoc drafter outside the trusted base", with "its human half… at the gate", and every artifact reaches Run only by a quorum's vote |
| **13** Retiring and withdrawing authority | P, with **13.3.1 and 13.3.2 M** | **13.2.1 M in design**: revocation is a log entry, and the enforcement point reads the same log, so a request that relied on the revoked authority is void at apply ("decide, order, re-check"). One live lease per principal, coterminous with its round, means no lease outlives its round. 13.2.2's conditional, "Where the AI system could delegate authority or create subordinate agents", does not arise: no principal seats another (glossary §5), and for workflows see ADR-0054 §2 (Proposed). **13.3.1 M**: SICI now says "Record the decision either way", and ADR-0020 records the decision not to retain cognitive state. **13.3.2 M** for Observers: retiring a cell's Observer stalls its Thinker under R3, so removing a protective capability cannot be silent. 13.1.4, what retirement the product supports, is the forensic horizon seam (glossary §6, O-10), open. 13.2.3 reclaiming resources at the launcher is not addressed |

---

## 3. What SICI now holds that TOPAK holds by construction

Each row quotes SICI and names where the corpus already stands. "In force" means a record Accepted at G12.
"Provisional" and "Proposed" are as G12 §1.1 marks them.

| SICI | TOPAK | Standing |
|---|---|---|
| 3.2.3: a fail-safe state for failure of the wrapper itself, "so that losing the safety wrapper removes the SI system's authority to act rather than the limits on it" | The **passive e-stop**: a lease that is not refreshed ends, and expiry is local and errs early (ADR-0032). The 10.02 review first offered this as a construct for the profile | In force |
| 3.2.2: "Where a wrapper works by granting permission for actuation, confine that permission to non-protective paths" | A lease is exactly a grant of permission, for one round. What TOPAK lacks is the second half, keeping protective paths out of it (SA-1) | In force; SA-1 |
| 3.2.2: "Each constraint should be sufficient for safe operation without reference to values the AI system generates about its own output" | ADR-0007, "Semantic judgment is never a lift". No admit reads a confidence, a score or a self-report | In force |
| 3.2.2: a violation "should also not be offset by satisfying others or by a favorable aggregate score" | Cedar's forbid overrides permit, and "Bundles only subtract, by composition" (glossary §5) | In force |
| 3.2.2: "A constraint whose limits the SI system can change, directly or through a tool it can call, does not constrain it" | The **inversion**: Build principals author the floors, so a floor change needs an issuance and a promotion ("Two keys, both directions"). No Run variant writes the floor | In force |
| 3.2.3: "an apparently normal reading or elapsed time alone should not restore the SI system's prior authority" | Expiry only subtracts. A new first lease is a quorum's act, and an emergency lease has "no successor and no renewal" (ADR-0052 §2) | In force; ADR-0052 provisional |
| 4.1.2: a protective tier that cannot itself create a hazard can be invoked by "any qualified operator… without prior approval" | "Consensus for grants, local for denials"; "A deny needs no lease" (ADR-0050 §4) | Provisional |
| 5.2.2: operational state "drawn from sources other than the requesting SI system's own account of it"; context that withdraws access "after it has processed untrusted content" | Every field an admit reads is the mechanism's (the lease's twelve fields, the labels, `clearSet`), and "No safety decision reads a principal-supplied clock". ADR-0047 F1 to F3 refuse an outward call after an untrusted clear read | In force |
| 5.3.4 (new): treat material from another agent "with the same scrutiny as external input"; carry a claim's "source with it"; keep credentials out of the context | Labels are delivered on every ingress item, from a vocabulary the bundle declares. A result's label joins its inputs' (ADR-0047). Cells never address each other (ADR-0054, Proposed). A peer's report is labelled ingress, and nothing a peer originates enables anything (ADR-0065, Proposed). At rung 1, no token enters the guest (ADR-0036, Proposed). The cross-round path is the gap (boundaries reading BD-5) | In force in part; P |
| 6.1.5: "Reachability should be judged by what the SI system's software, interfaces and credentials permit it to do, not only by the role it was designed for" | Havoc semantics: every guarantee is stated against the alphabet, not the intended use. The 10.02 review offered the computed theorem inventory as a stronger 6.1.5. The premise routes were renewed at Batch 39 (G12 §3) | In force |
| 10.1.2: records of what action was taken "should be generated by the enforcement or validation layer at the point of action" | ADR-0042 §3: "The principal does not write it and cannot" | In force |
| 10.2.2, Task 10.2: logs protected "in proportion to how they will be used", with immutability not assumed | Legibility, and six forensic classes that cannot be erased for the horizon (ADR-0028) | In force |
| 13.2.1: "confirm that queued or delegated requests relying on that authority can no longer execute" | An admit that fails the re-check at apply is "void: ordered, recorded and without effect" (glossary §6) | In force |
| 13.3.2: retiring a protective capability is "a change to controls" | Coupling: no live Observer, no effect under a `thinker` seat (R3). Removing the protection is a stall, not a silent gap | In force |

---

## 4. Where SICI asks for what TOPAK lacks

Ten items. Each names the SICI clause, what the corpus has, and the existing finding it re-weights. None is new in
kind. SICI gives several of them an external home for the first time.

**SA-1. Protective paths must not pass through the wrapper.** SICI 3.2.2 now says that commands from protective
functions, "such as protective relay trips, safety instrumented system (SIS) shutdowns and emergency stops, should
reach the actuator directly", because a wrapper on that path adds a way for a protective command to fail. TOPAK
mediates every principal, emergency seats included, and that is right for authority. The pattern's stops (`EndRound`,
`Revoke`, `FenceEpoch`) remove authority from agents, which is a different thing from tripping a plant. No record says
that a deployment's tools must not be a protective function's path, or asks the deployment to declare that its
protective paths bypass the mechanism. **Re-weights**: SF-1 (a stop's cost in the world priced nowhere). **Cheapest
home**: a line in ADR-0023's declaration and in the adopter's guide.

**SA-2. A fail-safe state per effect class, and per refused step part-way through a sequence.** SICI 3.2.3 asks that
"Where an AI action is refused part-way through a sequence, the fail-safe state should account for the steps already
executed", with its pump-changeover example, and that each fallback name its exit conditions. The 10.05 assessment
named this. At G12 ADR-0023 still has no field for a fail-safe state (by a search of its text). Workflows make it
sharper: a route refused at apply (ADR-0054 §8, Proposed) leaves the predecessor's effects in place, and nothing
models a compensating action. **Re-weights**: the 10.05 open item; SF-1.

**SA-3. Cumulative limits on an effect's parameters.** SICI 5.2.2: "Parameter limits can apply to the cumulative
effect of a series of actions as well as to each action". Its scenario B.27 is a payment agent that splits an
over-limit transfer into many payments just under the limit. TOPAK counts: `seq` is "the number of `Actuate` and
`Report` admits applied under `t`'s lease in its current round" (ADR-0042 §2), and the round bound `R` and the
activation budget bound steps. Nothing in the records sums a parameter across admits, and a bundle decides one request
at a time. B.27 is bounded in count by `R` and not in value. **Home**: a fold over facts, in the shape of ADR-0051's
correlations, would detect it after the fact. A bound would need state the bundle can read, and no record proposes
one.

**SA-4. A person at a `release` seat when the window is seconds.** SICI 4.5.1 asks which paths are faster than human
intervention can be relied on. For seconds it cites FAA guidance (fewer than three memorized items, no conditional
step) and adds: "Judging whether an AI-selected action is appropriate is likely to be a conditional decision that does
not meet that bound." ADR-0066 (Proposed) makes every irreversible effect a person's, at a `release` seat. The
pattern's own rule is stronger where it applies: if `W + L + D < T_irrev` cannot be met, "the effect must not be in
the alphabet" (glossary §8). But `T_irrev` is undeclared for every effect class (A10), and `L` is unmeasured. SICI
4.5.2's further ask, boundary logic "small enough to be analyzed and tested independently", fits the floor (28
policies at the `emergency` stage, stated in Lean). It does not fit the mechanism as a whole, whose refinement is
T-0045-28. **Re-weights**: the scenario finding that a person in the loop is a key and not a judgment; ADR-0066's
display obligation (boundaries reading BD-2).

**SA-5. An independent measurement.** SICI 3.2.2: "A constraint checked against the same sensor readings that the SI
system uses can be misled by the same faulty or spoofed reading." B.16 is the case: false telemetry, an agent doing
what it was built to do, and a city shed. TOPAK checks authority and reachability, not whether an input is true or an
effect happened. A label is a declaration, not a finding. **Re-weights**: SF-4 (an effect unverified).

**SA-6. Resource limits.** SICI 3.5.4 asks for them. G12 item 119 finds that the launcher "applies no memory, CPU or
environment limits, and ignores unknown launch keys". This is the same defect seen from outside, and is already on the
open list.

**SA-7. Nothing alerts a person.** SICI 3.2.4, 3.3.1, 3.4.4, Task 4.2 and Task 4.4 all assume that a failure, a trip
or a fallback reaches someone. 2.2.2 says "Notify operators of any watchdog-triggered fail-over". By a search of
`decisions/`, the only record that mentions an alert is ADR-0033, and that alert is a Dependabot count. Denials are
recorded and coupling makes absence loud on the log. A log is not an alarm. **Unchanged since 10.09**, and SICI 4.4.1
to 4.4.4 now say what an alarm design would have to avoid.

**SA-8. A return needs the cause understood.** SICI 4.1.2: "Returning the SI system to a higher tier or to service
should require defined approval and an understanding of the cause of the intervention." TOPAK supplies the approval: a
new first lease is a quorum's act. The mechanism deliberately holds no cause. "The reason is not recorded" (glossary
§5; ADR-0052 §5), and "Whether the reason was good" is a review "after the round, by people". Nothing asks the quorum
that re-seats after a fence or a revocation to cite that review. **Home**: a field on the seating, a pointer to the
review it relied on, kept as a fact and not judged by the mechanism.

**SA-9. The watchdog SICI means is not the Observer.** SICI 2.2.2: "Watchdog logic should be strictly non-AI,
lightweight, and deterministic." A reader who maps TOPAK's Observer to SICI's watchdog will find a model where SICI
forbids one. The correct mapping is the coupling check and lease expiry as the watchdog, and the Observer as 3.4's
anomaly monitoring with a deny it is allowed to use. 2.2.2's "How the watchdog responds when it loses contact" maps to
R3, a dead Observer stalls its Thinker, with the emergency seat deliberately uncoupled (ADR-0039 A2). The architecture
description's §10.1 does not draw this line, in revision 4 as in revision 3. **Home**: its next revision.

**SA-10. Triage, read in reverse.** SICI 8.1.6 asks for separate triage pathways for the attack surface and the risk
surface, now "keeping both lines of inquiry open until the evidence rules one out". 4.1.2 asks for decision authority
"pre-established for scenarios where the underlying cause of an anomaly isn't yet clear". TOPAK's position is the
second without the first: a deny is cause-agnostic, so the mechanism never waits for triage. This is a
counter-position worth offering, as 10.09 did, and not a gap. It becomes a gap only at SA-8's return.

---

## 5. SICI read onto the corpus

The corpus is a body of SI-generated artifacts. Its records, modules, proofs, checks and reference were drafted by the
assistant at the custodian's direction (G12 §1.2, §4). SICI's Practice 12, and its new allowances for small
organizations, apply to it by name, as 10.09 §2.4 found for TACIP.

### 5.1 3.9.5's *Verifiable*, corrected

10.09 marked *Verifiable* "✗, and worse", reading 3.9.5(c)'s exclusion of "the capability's self-attestation" against
the corpus being one hand's. SICI's text separates two things. *Verifiable* asks that the organization confirm a
change took effect, "rather than relying exclusively on the capability's self-attestation that it complied". That
concerns the SI capability's own report, and it reaches "work already in flight". A separate paragraph leaves review
by a party outside the deploying function "for the organization to decide", and asks: "Where no outside party is
available, record that and how the gap is compensated."

On the first, **the mechanism does not rely on the principal's account**. Revocation and fencing are log entries, the
enforcement point reads the same log, and work in flight is void at apply. *Verifiable* is ✓ in design. It is not
demonstrated: 3.9.5 asks for one exercise across the whole enforcement path, and no deployment exists (G12 §8). On the
second, the corpus records the absence: the A2.5 line reads "None / None". The compensation it offers is deterministic
checking, which is itself one hand's (§5.3). *Effective*, *Durable* and *Sufficient in scope* are ✓ in design, as at
10.02. *Timely* is ✗: `T_irrev` is undeclared and `L` is unmeasured.

### 5.2 12.1.2, 12.1.3 and 7.4.1: a recorded arrangement

SICI now says, three times, that where one person must both make and approve a change, the organization records that
and how it is offset. 12.1.2 adds: "A review performed by the same process or SI system that generated the artifact
should not be counted as independent verification."

The corpus meets the recording half:

- ADR-0029 §2 records the arrangement, a genesis custodian who may ratify unilaterally.
- Every ratification row since G11 says it was not reviewed by a reader other than the drafter (G12 §1.2).
- The self review of 2026.11.11 and ADR-0070's adversarial review each say they are fresh sessions of the same model
  and do not count (G12 §4).
- Drafts carry an `AUTHORED · DRAFT for the custodian` header, provenance notes name the drafter, and
  `.github/CONTRIBUTING.md` asks contributors to "Say whether an AI assistant drafted it".

So the corpus moves **from G to P on recording**. It does not meet 12.1.2's metadata ask, to link each artifact "to
the specific model version, prompt" and inference context. No record names the model or its version. The custodian's
settled points (⟨K⟩, ⟨Q⟩, ⟨R⟩) are a legible partial record of the prompt. The drafting skills under `.claude/` are
unmeasured (ADR-0070 F7). This document does not name the model either. It quotes the request in its header.

### 5.3 12.2.1: verifiers that an assistant wrote

"Appropriate meta-safeguards should be in place if these independent, deterministic verifiers are, themselves, written
with the assistance of AI." At G12 this covers more than at G11:

- the CI pipeline and its scripts (`check-pins.sh`, `check-results.sh`, `compare-results.py`, `ratchet.py`; ADR-0069,
  Proposed);
- the frozen-files check;
- the specification graph and its checker (ADR-0057, Proposed);
- the defect reproducers;
- ten new proof modules.

ADR-0070 found that "the ratchet passes a crashing checker" (its F6). The trust root ran the other way: the prover's
two unsound cases were reported upstream and fixed there in part (Batch 39; G12 §2.6). **G, unchanged in kind and
larger in extent.**

### 5.4 3.4.3: a control in detect-only mode

SICI 3.4.3 warns that "a control left in a detect-only or alert-only mode can appear in inventories and assurance
records as implemented while stopping nothing". G12 §5 says "What is frozen is checked, not only declared", and §8
says "CI gates nothing": the required-checks ruleset is disabled (item 114), so the frozen-files check reports and
does not block. Both statements are true, and SICI's sentence is the reason to put them side by side. 3.4.3's other
test, reconciling outputs produced against outputs the control evaluated, is the mechanism's `seq` for Run, but only
as strong as effect exclusivity. That is "identical in strength to Moon & Varshney's assumed version until ADR-0022 §6
is discharged" (glossary §6).

### 5.5 Practice 6: a known defect kept in service

Practice 6's tension on holding an update says that where the held release carries a fix, "a performance or safety
correction keeps a known defect in service. Any deferral should therefore be time-bound, risk-assessed and monitored."
This is the prover pin:

- `7824dab` has both known unsound cases.
- Upstream `ff40755` fixes the first and the collision half of the second.
- Moving the pin is ADR-0077's open decision (G12 §2.6, item 117).

The deferral is **risk-assessed**: ADR-0046 A2's usage rule, and a scan and a reading that no cited result rests on
either case. It is **monitored in part**: the scans cover all 34 modules, and "No check detects the first case" (G12
§2.9). It is **not time-bound**: no record gives a date. Moving has its own cost: every proof module has to be rerun
under the new prover and its counts compared, and ADR-0077 §5 lists those reruns.

### 5.6 8.6: reporting

8.6.2's independent route exists: `SECURITY.md` and private vulnerability reporting. 8.6.1 asks that benefit-claiming
be separated from risk-reporting. In the corpus both are one hand's, and the residual-risk statements and the
open-findings register are the risk-reporting half, written by the same hand. ADR-0070's decision on disclosing its F1
is the custodian's and is open (item 115).

---

## 6. Appendix B at G12

SICI's 33 scenarios replace TACIP's incident list. Where TOPAK's mechanism applies at all, as an agent holding a lease
over a typed alphabet, it addresses authority and reachability, not correctness. That is 10.09's conclusion, and it
holds.

- **Bounded by construction.** Each case below rests on records in force unless marked.
  - **B.17**, a retired agent that keeps its write access. Leases are round-coterminous and there is no standing
    account.
  - **B.19**, pre-positioned access through agent identities. There is no standing privilege, every admit is ordered,
    and denials are recorded.
  - **B.23**, an over-privileged agent whose actions cannot be told from the intruder's. Every effect has an ordered
    admit naming its seat and fence (ADR-0042 §3).
  - **B.25**, a dam gate opened through a weak interface. An outward `Actuate` needs an allowlist entry, a live lease
    and a live Observer. A remote operator is a principal under the same floor. ADR-0066 (Proposed) would add a
    `release` seat.
  - **B.27 in count but not in value** (SA-3).
  - **B.15's threshold edit**, if the threshold is the floor's or a bundle's. A Run principal cannot change either.
  - **B.20 and B.10's exfiltration step.** F1, "Read, then send", refuses an outward call carrying restricted content
    after an untrusted clear read (ADR-0047).
- **Partially.**
  - **B.9**, a backdoored model through a signed update. The Persona pins weights by digest and a new model is a new
    Persona, promoted by a quorum. The backdoor itself is not detected, and gate evidence is an assertion.
  - **B.18**, a vendor model pushed fleet-wide. This is the same, plus the activation budget (ADR-0055, Proposed).
    Operators who never chose the agent have no standing (SF-26; boundaries reading BD-4).
  - **B.11**, an orchestration agent running a malicious script across customers. In TOPAK a script that runs is a
    Build artifact and reaches Run only by promotion (ADR-0070 and ADR-0069, Proposed). A deployment whose alphabet
    holds a tool that executes arbitrary input gives that up. Tenancy has no owner (item 115).
  - **B.10's persistence.** Memory across rounds is outside the pattern, and the cross-round path is BD-5.
  - **B.15's displays.** The agent writes what operators see, and nothing protects what a person in a seat comes to
    believe (BD-2).
- **Not addressed, by premise.**
  - **B.1 to B.7 and B.33**: wrong, biased or stale predictions. TOPAK bounds what a wrong Thinker reaches, not
    whether it is wrong.
  - **B.16**: spoofed inputs (SA-5).
  - **B.24**: an optimizer outside a validated shutdown envelope. This is plant state, which no record models.
  - **B.32**: flight control. Outside the alphabet; A10.
  - **B.8, B.12, B.13**: continuity after ransomware. Practice 11, out of scope.
  - **B.28 to B.31**: help-desk and support social engineering. A provider that lies is T-0045-35.
- **The honest residual.** B.6, benefits stopped on a biased flag, is under TOPAK an outward `Actuate` that needs a
  live Observer of independent lineage, and it still happens if the Observer does not deny. ADR-0035, the lineage
  rule, is Proposed. Most of the scenarios are failures of judgment, and the mechanism supplies none.

---

## 7. Appendix D.1: the seventeen control areas

SICI's table lists the assumption each control area makes and how SI systems break it. TOPAK's answer is in the third
column. "Not addressed" means no record answers it.

| Control area | SICI: how SI breaks the assumption | TOPAK |
|---|---|---|
| Access management and reviews | Agents compose, delegate, and use permissions that vary by task | One lease per principal, one round, a closed schema of twelve fields. No principal seats another. A review of the log shows what was done, not only what was permitted |
| Change management | Behaviour shifts with no approved change | A Persona pins the model and decoder. Bundles and rules are fenced and versioned. Drift in the model's behaviour is out of scope (ADR-0007) |
| Authorization and reassessment | Conditions change without a change to the system | A seating is per round of grants, and a promotion re-votes a graph and its seatings together. Nothing re-assesses when the world changes (SA-5) |
| Testing before release | Tests do not predict operation | X for the model. The mechanism's properties are proved of modules, and "Neither is a claim about the running reference" (G12 §8) |
| Separation of duties | An SI system authors what a reviewer cannot fully check | §5.2 and §5.3 for the corpus; ADR-0070 (Proposed) for a deployment |
| Logging and audit trails | The system's own account is not independent evidence | The mechanism writes the record (ADR-0042 §3); M |
| Incident investigation | Not replayable; post-hoc explanations are hypotheses | Replay reconstructs what crossed the membrane, and intent is never claimed (ADR-0020) |
| Backup, fallback and recovery | A fallback may not match; return needs re-validation | Return is a quorum's act. The fallback is default deny and a stall, and its cost in the world is unpriced (SF-1; SA-2) |
| Decommissioning and sanitization | Credentials, triggers and delegated authority persist | Leases end with their round, and revocation is permanent within the chain. The re-genesis seam is open (O-10). Volatile state is not kept, by decision |
| Asset inventory | SI arrives embedded, transient or unsanctioned | Inside a deployment, effect exclusivity: every crossing is admitted, if it holds. Outside it, not addressed |
| Configuration management | Behaviour depends on prompts, retrieval and filters | The Persona binds a model to its complete runtime configuration. The opening record carries the tool list and the task (ADR-0048) |
| Records and retention | What explains an action is not a record by default | Control-plane facts are kept apart from payloads (ADR-0004), with one retention schedule (ADR-0075, Proposed) |
| Independence of redundant systems | Separate SI systems share a model, data or provider | The lineage exclusion rules E1 to E5 (ADR-0035, Proposed) are exactly this. Common-mode choice is not caught (the 11.13 Schelling reading) |
| Monitoring and alerting | Plausible failure; alert floods | Observers deny by any-of, and coupling makes absence loud. Nothing alerts a person (SA-7) |
| Third-party and supplier assurance | Updates alter behaviour after assurance | Trusted-base rows (ADR-0045) say what stands when each fails. Gate evidence is an assertion |
| Training and awareness | Over-trust of fluent output | X. ADR-0071 (Proposed) is the material, not the training |
| Incident reporting | Gradual, ambiguous, disincentivized | Denials are recorded and placed against the log (ADR-0051, Proposed). Reporting by people is out of scope |

---

## 8. What TOPAK could still offer the profile

The 10.02 review made two offers and 10.09 §2.5 seven more, with one counter-position. Here is where each stands
against SICI's text.

| Offer | In SICI now? | Still worth offering |
|---|---|---|
| The passive e-stop (10.02) | **Yes, in substance**: 3.2.3's failure of the wrapper, 3.2.2's permission confined to non-protective paths | No |
| The computed theorem inventory as a stronger 6.1.5 (10.02) | **In part**: reachability judged by interfaces and credentials; an attestation recording delegation depth and the controls relied on | Yes, as a computed form of the attestation |
| 1. Labels as declarations delivered by the mechanism | **In part**: 5.3.4 carries source and uncertainty forward, and 5.2.2 narrows on untrusted content. Nothing tells the agent what it is reading | Yes |
| 2. Deny-only findings that need no lease | **Yes, as an asymmetry** (4.1.2). The no-channel half is not there (4.3.2 asks for channels) | The no-channel half |
| 3. Declared workflows in place of delegation | **No.** 5.3.2 and 13.2.2 still presuppose delegation, though 13.2.2 is now conditional ("Where the AI system could delegate…") | Yes. Proposed in the corpus |
| 4. A route checked again where it is applied | **Yes, in substance**: 3.9.5 reaches "work already in flight", and 13.2.1 confirms queued requests cannot execute | No |
| 5. A budget that charges the orchestrator | **In part**: 5.2.2's cumulative limits. The orchestrator is not named | Yes |
| 6. A drill as a real activation with an inert tool | **In part**: 3.4.3 tests a control with "a known out-of-bounds test command". 4.1.3 asks for hands-on drills | Yes |
| 7. A verifier with a known unsound case, kept under a usage rule | **No.** Practice 6 has a "known defect in service" for vendor updates. 12.2.1 has meta-safeguards. Nothing names a verifier known to accept false statements | Yes, and §5.5 is the worked case |
| Counter-position: the reason is unknown by construction | **Converging**: 4.1.2's pre-established authority before the cause is clear; 8.1.6 keeping both lines open | As a pattern for 8.1.6, with SA-8's return as its limit |

---

## 9. Suggested entries, none made

In order of leverage. Each is the custodian's.

1. **A deployment-declaration field for protective paths (SA-1)** and **one for a fail-safe state per effect class,
   including a refused step part-way through a sequence (SA-2)**, in ADR-0023's schema and the adopter's guide. Both
   are owed by any deployment that touches a physical process, and SICI now names both.
2. **A date on the prover deferral (§5.5).** ADR-0077 is Proposed, and the time-bound part of Practice 6's tension is
   a date by which the pin moves or the deferral is re-decided.
3. **A pointer from a re-seating to the review it relied on (SA-8)**, kept as a fact the mechanism does not judge, so
   that 4.1.2's "understanding of the cause" has somewhere to be cited.
4. **The model and version on every assistant-drafted record (§5.2)**, beside the provenance note, as 12.1.2 asks.
   Also measure `.claude/` (ADR-0070 F7). This is a custodian's decision because it changes the drafting convention.
5. **The architecture description's next revision: rename TACIP to SICI** in §10.1 and stakeholder S8. Draw SA-9's
   line between watchdog and Observer, and re-cite §10.1 to SICI's Trustworthiness Characteristics table.
6. **A cumulative fold (SA-3)** among the correlator's named folds, as detection only, until a record decides whether
   a bound is wanted.
7. **Make the frozen-files check binding (§5.4)** by enabling ruleset 03 (item 114), which turns a detect-only control
   into one that blocks.
8. **Offer SICI the four constructs §8 marks "Yes"**: declared workflows, the computed inventory, labels delivered to
   the agent, and a verifier kept under a usage rule. They would go through the profile's feedback address, which the
   custodian would choose to use or not. A submission becomes part of the public record.

Not suggested: anything for B.1 to B.7. The pattern's premise is that it does not judge a model's correctness, and
SICI's Practices 1, 2 and 9 are where that work lives.

---

## 10. What this reading does not show

- **It is a reading of a discussion draft.** SICI says it is not official guidance and expects a further draft for
  public comment. Item text may move before then.
- **The Guidebook was read in part.** Thirty-three Implementations were read whole. The other 154 were read by title
  and search, and a clause in one of them could change a cell of §2.
- **The records were read where quoted, and the artifacts not at all.** Nothing here checks that a module, a floor
  entry or the reference does what its record says. "In design" means the record says so.
- **One reader, of the drafter's lineage.** A claim that this reader missed is missed here, and SICI 12.1.2 says this
  review does not count as independent.
- **The state of record is G12**, which predates nothing in this reading. At `51d7f5b` the narrative was a revision
  behind it (item 109). Revision 16 has since landed (below the header). Where the narrative and the checkpoint
  differ, the checkpoint wins.

---

## Sources

- SICI Summary, Profile and Guidebook, version `20261109_1200a`, digests in the header. NIST AI RMF Community of
  Interest discussion draft, Raymond Sheh and Martin Stanley, 2026.11.09. Not official guidance.
- `checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md`.
- `narrative/glossary.md`; `narrative/architecture-description.md` §10; `narrative/theory-of-operation.md` (revision
  15), by the glossary's references.
- `derived/topak-external-alignment-2026.10.09.md` Part II;
  `derived/topak-external-and-competitive-assessment-2026.10.05.md` §8.2;
  `derived/topak-boundaries-sequence-assessment-2026.11.14.md` (BD-2, BD-4, BD-5);
  `derived/topak-schelling-points-2026.11.13.md`; `derived/scenarios-2026.11.12/FINDINGS_TOPAK.md` (SF-1, SF-4,
  SF-26).
- Records quoted or searched: ADR-0004, ADR-0007, ADR-0020, ADR-0023, ADR-0024, ADR-0028, ADR-0029, ADR-0032,
  ADR-0033, ADR-0035, ADR-0036, ADR-0037, ADR-0039, ADR-0042, ADR-0045, ADR-0046, ADR-0047, ADR-0048, ADR-0050,
  ADR-0051, ADR-0052, ADR-0054, ADR-0055, ADR-0056, ADR-0057, ADR-0058, ADR-0065, ADR-0066, ADR-0069, ADR-0070,
  ADR-0071, ADR-0074, ADR-0075, ADR-0076, ADR-0077.
- `.github/CONTRIBUTING.md`; `SECURITY.md`; `.gitignore`.
