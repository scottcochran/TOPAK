# Self review of 2026.11.11: reader G's findings in full

Reader G read workflows and user scope. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

33 reported: 26 confirmed, 7 confirmed with a correction, 0 dropped.

### G-1: `covered` is an attribute that changes after the round ends, and towards enabled, while §4 says `found` is the only one that changes and that a guard can move only towards disabled
- Against: decisions/ADR-0054.md:156-166 and :187-188 (and spec/Workflow.tla:232-235; mechanism/crates/topak-core/src/workflow.rs:265-274, :315, :1331-1334; decisions/ADR-0047.md:207-208)
- Basis: Proposed
- Claim: "When a node's round ends, the mechanism lifts its **attributes** in one log entry." and "Because every attribute but `found` is written once, and `found` only subtracts, **a guard's value cannot change after it is first evaluable except towards disabled.**"
- Why wrong: The same table lists `covered` (ADR-0054.md:165: "| `covered` | Observed | Its cell Observer has reported coverage to the seal (§7) |") beside `found` (:166: "**The one attribute that changes after the end, and only from false to true**"). Coverage cannot be in the entry that ends the round: Workflow.tla:24-25 says "node's cell Observer reports coverage to its seal at some moment after it ends", and `Cover(n)` (Workflow.tla:232-234) requires `status[n] = "ended" /\ ~covered[n]` and sets it TRUE. The reference agrees with the module and not with the record: `Attributes` (workflow.rs:265-274) holds `end`, `actuates`, `label`, `outcome`, `output` only; `covered` is a field of the `Activation` (:315) set in a later apply (:1331-1334). So `covered` is a second attribute that changes after the end, from false to true. The reference's `Guard` (workflow.rs:193-202) has no atom for `covered` or `found`, which is what keeps guards settled there; the record does not say a guard may not read them, and under D-0054-2 (coverage waived, ADR-0054.md:283) a guard that read `covered` would flip towards enabled after it was first evaluable. ADR-0047 A1 repeats the claim (ADR-0047.md:207-208: "each lifted by the mechanism when the node's round ends").
- Fix belongs in: ADR-0054 §4 (and with it ADR-0047 A1 and the glossary's *Attributes* entry)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:156 and :187-188 quoted exactly; :165-166 lists `covered` beside `found`, "the one attribute that changes after the end". spec/Workflow.tla:23-25 and :232-235 (Cover needs status "ended" and sets covered TRUE). mechanism/crates/topak-core/src/workflow.rs:265-274 (Attributes has no covered), :315, :1333 (set in a later apply), :193-202 (no guard atom over covered or found). decisions/ADR-0047.md:207-208 and narrative/glossary.md:278-279 repeat "lifted when the round ends". No qualifier in §7 (:231-237).

### G-2: The routing rule the record states is over what the guard reads; the module and the reference apply it to the source's label whatever the guard reads
- Against: decisions/ADR-0054.md:203-205 (and spec/Workflow.tla:153-159; mechanism/crates/topak-core/src/workflow.rs:676-688)
- Basis: Proposed
- Claim: "An edge whose target's lease reaches an outward entry (ADR-0049 §5) or receives `restricted` input is **disabled** when any attribute its guard reads is labelled `untrusted`."
- Why wrong: In the module the edge into the outward node, e2, has a guard that reads nothing (Workflow.tla:154: `[] e = "e2" -> TRUE`), yet it is disabled by its source's label (Workflow.tla:159: `TaintOK(e) == Mut = "M_NOTAINT" \/ ~(Dst[e] \in Outward /\ attr[Src[e]].lbl = "untrusted")`). The comment above it, "Every guard here reads the attributes of its source" (Workflow.tla:158), is false of e2, e3 and e4. The reference says outright that it adds the source: workflow.rs:678-679 "An attribute carries its node's label; the source's is always read, since the edge delivers its output", and :683-684 `let mut reads = e.guard.reads(); reads.insert(e.from.clone());`. Read as written, the record's rule would leave e2 enabled from an untrusted `s`, which is the state `TaintedNeverOutward` forbids in the module. So `TaintedNeverOutward` is checked of a stricter rule than the record states. Separately, the rule's second arm ("or receives `restricted` input") is in no module: `TaintOK` tests `Outward` only, and ADR-0054 §12's "Not met" list (ADR-0054.md:323-324) does not name it. The reference narrows that arm to clear delivery from this edge's source (workflow.rs:680-681), which the record does not say.
- Fix belongs in: ADR-0054 §5 (and ADR-0047 A1's wording of the rule), or spec/Workflow.tla and workflow.rs if the record is right
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no (mechanism/GAPS-AND-ASSUMPTIONS.md I49 (i) is about which label an attribute carries, not about the read set)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:203-205 quoted exactly. spec/Workflow.tla:154 (e2 guard TRUE), :158-159 (TaintOK on attr[Src[e]].lbl whatever the guard), :190 and :338 (routedOnTaint is the source's label). workflow.rs:678-684 (reads.insert(e.from)), :680-681 (restricted arm narrowed to clear delivery from this source). `grep -n -i "restricted" spec/Workflow.tla spec/Mesh.tla` returns nothing; ADR-0054.md:323-324 does not list it. mechanism/GAPS-AND-ASSUMPTIONS.md:108 I49 (i) is about the label, not the read set.

### G-3: What a lapsed worker lease does differs three ways: the record makes `expired` a value a guard reads, the module fails the node, the reference ends it with attributes
- Against: decisions/ADR-0054.md:162 and :272-273 (and spec/Workflow.tla:225-229; mechanism/crates/topak-core/src/workflow.rs:1270-1287)
- Basis: Proposed
- Claim: "| `end` | Observed | How the round ended: `outcome`, `expired`, `fenced`, `revoked` |" and "It **fails** when a node fails, a decision point fails, a grant is refused, the epoch is fenced, or `T_wf` or the step bound passes."
- Why wrong: The record never says which ends make "a node fail". The module says a lapse does: Workflow.tla:225 "A worker's round ends without an end: its lease lapsed." sets `status` to `"failed"` (:228), lifts no attributes, and `Settle` then fails the workflow (:308-310). The reference says a lapse does not: workflow.rs:1273-1276 fails the activation only for `EndKind::Fenced | EndKind::Revoked`, and otherwise (outcome or expired) sets `ActStatus::Ended`, lifts attributes with `end` = expired and lets edges fire. So the module's properties are checked of a workflow in which no edge ever leaves a lapsed round, and the reference runs one in which it does. Two of the four `end` values the record lists can never reach a guard in the reference: a fenced or revoked round has no `Attributes`, and an atom over a node without them is false (workflow.rs:230-231, :241). A further difference on the same sentence: the record and the reference fail the workflow on a fence (workflow.rs:1307-1313), and the module does not always; after `Fence` with the decision consumed and no node ready or running, `Enabled` is false for good (Workflow.tla:169) and `Settle` (:305-310) is never enabled, so `wf` stays `"running"`.
- Fix belongs in: ADR-0054 §4 and §9 (to say which ends fail a node), then spec/Workflow.tla or workflow.rs
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:162 and :272-273 quoted exactly; `grep -n -i "fail" decisions/ADR-0054.md` finds no sentence saying which end of a running round fails its node (:112, :116 are refused and unissued grants). spec/Workflow.tla:225-229 (Fail: lapse, status failed, attr unchanged), :305-310 (Settle fails on a failed node). workflow.rs:1270-1287 (only Fenced or Revoked fail; Expired ends with attributes), :149-166, :230-241 (no attributes, atom false), :1302-1313 (a fence fails the run). Fence case rechecked: Workflow.tla:167-169, :284-285, :296-310, with the decision consumed and no node ready, running or failed, Settle is never enabled.

### G-4: §8 closes an edge on a finding against "any ancestor"; the reference closes it only on a finding in the activation's causal history, which at an `any` join leaves out the branch that did not trigger; neither module can tell the two apart
- Against: decisions/ADR-0054.md:247-249 (and mechanism/crates/topak-core/src/workflow.rs:669, :701-713; spec/Workflow.tla:80-88)
- Basis: Proposed
- Claim: "the edge enabled: its source ended and covered, its guard true, the routing rule satisfied, no finding against its source or any ancestor"
- Why wrong: The reference tests `a.hist.iter().any(|j| self.acts[*j].found)` (workflow.rs:669). In a dag, when a second edge reaches an `any` join that is already entered, `enter` returns without extending the join's history (workflow.rs:701-713: "An `any` join already entered: the edge is taken and changes nothing"). So with two parallel branches b and c into an `any` join j, entered first from b, a finding against c closes nothing out of j, though c is an ancestor of j. The module takes the record's reading in its constants (Workflow.tla:87-88: `n = "j" -> {"s", "b", "c"}`) and never uses it: no edge has j as its source (:81), only one of b and c ever runs, and `Anc` of every edge source that exists is `{}` or `{"s"}`. So nothing checked or tested distinguishes "ancestor" from "causal history" in a dag, and the reference implements the weaker one. I49 states the reference's rule ("no finding in the causal history") without marking it as a departure.
- Fix belongs in: ADR-0054 §8 (say which is meant), then workflow.rs or the record; spec/Workflow.tla for a graph that discriminates
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:247-249 quoted exactly; `grep -n -i "ancestor" decisions/ADR-0054.md` gives only :249, no definition. workflow.rs:669 (hist only), :701-713 (an `any` join already entered: hist not extended), :720-726. spec/Workflow.tla:81-88 (no edge has j as source; Anc of s, b, c is {} or {"s"}), :83 (both chosen edges leave s). mechanism/GAPS-AND-ASSUMPTIONS.md:108 "no finding in the causal history", not among (a) to (i).

### G-5: A grant refused because the principal still holds a live lease fails the node in the records, and waits in the reference and in ADR-0055
- Against: decisions/ADR-0054.md:111-113 and decisions/ADR-0031.md:106-109 (and mechanism/crates/topak-core/src/workflow.rs:1027-1048; decisions/ADR-0055.md:117-119; decisions/ADR-0031.md:112-113)
- Basis: Proposed (ADR-0054 §2), pending (ADR-0031 A4)
- Claim: ADR-0054: "the grant refuses as any grant does. A refused grant fails the node; nothing grants it lower and no other seating stands in." ADR-0031 A4: "the grant is refused as any grant is: while the principal holds a live lease, when a revocation names its principal, Persona or confinement profile, or when the rules epoch is no longer the tally's. A refused grant fails the node."
- Why wrong: The same pending amendment's last bullet says the opposite for the same cause (ADR-0031.md:112: "A principal seated at more than one node still holds one live lease, so its rounds are granted in log order"), as does ADR-0055 §3 (ADR-0055.md:118-119: "a node's next activation waits until its previous one has ended"). The reference implements the wait and says so: workflow.rs:1027-1028 "Waits, not failures: the seat holds a live lease (one per principal and seat; a node has one live activation, ADR-0055 §3), or its last round is not yet read to the seal", returning `Applied::Rejected(... "the slot waits")` without failing the slot (:1036-1047). The register describes the wait (I49: "a slot whose seat holds a live lease or whose last round is unread waits") but does not list it among the reference's own choices (a) to (i).
- Fix belongs in: ADR-0054 §2 and ADR-0031 A4 (which refusals fail a node and which make it wait)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:111-113 and decisions/ADR-0031.md:106-109 quoted exactly; ADR-0031.md:112-113 ("granted in log order") and decisions/ADR-0055.md:117-119 ("waits"). workflow.rs:1027-1048 ("Waits, not failures", Rejected without failing the slot). mechanism/GAPS-AND-ASSUMPTIONS.md:108 states the wait and lists it under none of (a) to (i). No text in either record separates a refusal that fails from one that waits.

### G-6: ADR-0056 says the subject assertion is in no record's payload (§5) and that its bytes are in the round's payload (§7)
- Against: decisions/ADR-0056.md:167-168 (and decisions/ADR-0056.md:185-186)
- Basis: Proposed
- Claim: "**Neither the assertion nor the credential is ingress.** The Listener never delivers them. They are not in the round payload a Thinker reads, and they are not in any record's payload."
- Why wrong: ADR-0056.md:185-186, two sections later: "The assertion's bytes are in the round's payload, inside the unit of erasure (ADR-0003)." The two sentences cannot both hold of the assertion. Which one holds decides whether a provider-signed assertion naming a user is erasable evidence on the round topic (§7's reading, and §7 adds that "An Observer and the correlator read the subject's digest"), or is kept off the record altogether (§5's reading).
- Fix belongs in: ADR-0056 §5 or §7
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0056.md:167-168 and :185-186 quoted exactly, both about the assertion. `grep -n -i "payload" decisions/ADR-0056.md` returns only these two lines, so nothing reconciles them. :15-16: C2 applies to §5, the section the first sentence is in, which supports the reader's severity.

### G-7: "A budget that charged only workers would ... leave the orchestrator's leases unbounded" is not what `M_ORCHFREE` shows, and not what the record's own rules allow
- Against: decisions/ADR-0055.md:81-82 (and spec/Mesh.tla:149-154, :169-177, :201-212; decisions/ADR-0055.md:151)
- Basis: Proposed
- Claim: "A budget that charged only workers would bound workers and leave the orchestrator's leases unbounded. `M_ORCHFREE` is that."
- Why wrong: The record gives the orchestrator "One orchestrator round per decision event" (ADR-0055.md:151), and a decision event is the end of a worker activation. In the module an orchestrator round is granted only for an event not yet served (Mesh.tla:203: `ELSE ev \notin served`), events are ended activations of `s` (:149-150), and worker grants stay charged under `M_ORCHFREE` (:171, `CanCharge`). So with workers bounded by N the orchestrator's rounds are bounded by N too; the mutation breaks `BudgetBound` (`nAll <= N`) by a bounded overrun. The record's own History says the bounded thing (ADR-0055.md:316: "frees worker rounds"), and its unconstrained `M_ORCHFREE` run is described as large, not infinite (:213-214). The stronger wording recurs in finding 2 (:279-280), the Options row (:238), G11 finding 10 (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:232-233) and the narrative (narrative/theory-of-operation.md:649-650: "a budget that does not charge the orchestrator leaves it unbounded").
- Fix belongs in: ADR-0055 §2 and finding 2 (the narrative follows)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0055.md:81-82 quoted exactly; :151 (one round per decision event), :238, :279-280, :316 ("frees worker rounds"), :211-214. spec/Mesh.tla:149-150 (events are ended activations of s), :171 (worker grants charged under every mutation), :203-208 (under M_ORCHFREE a round only for an unserved event), so rounds are at most the charged worker leases and nAll at most 2N. checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:232-233; narrative/theory-of-operation.md:649-650.

### G-8: `FindingPrecedesNoRoute` holds vacuously in its "or an ancestor" half, and no property or mutation covers a computed edge fired after a finding
- Against: spec/Workflow.tla:330-332 (and spec/Workflow.tla:83, :87, :165, :270-274; decisions/ADR-0054.md:312-318)
- Basis: evidence
- Claim: "\A r \in applied : \A a \in Anc[Src[r.edge]] \cup {Src[r.edge]} :" (the property the module header describes as "no Route applies after a finding against its source or an ancestor has been ordered", Workflow.tla:32-33), counted by ADR-0054 §12 among "The ten properties hold together (106,199 states)"
- Why wrong: Every route's edge is chosen, both chosen edges leave `s` (Workflow.tla:81, :83), and `Anc["s"] = {}` (:87). The quantifier over ancestors therefore ranges over nothing in every reachable state; the property is checked for the source only. For computed edges, `Fire` (:270-274) does consult `Unfound` through `Enabled`, but no invariant reads it (the ten are over `applied`, `activatedBy`, `uncoveredAct`, `routedOnTaint`, `grantEpoch`, `seatOK`, `wf`) and no mutation removes it, so by ADR-0046's method nothing shows that conjunct matters. The record's "Not met" list names "more than one decision point" (ADR-0054.md:323) but not that the one decision point is the root.
- Fix belongs in: spec/Workflow.tla (a graph with a decision point below the root, and a property over computed activations); ADR-0054 §12's "Not met"
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 101 lists what the module owes and does not list this)
- **Verifier:** confirmed
- **Verifier's evidence:** spec/Workflow.tla:330-332 quoted exactly; :32-33 header; :81-83 and :87 (every chosen edge leaves s, Anc["s"] = {}), :165 (Unfound has no Mut branch), :270-274, :326-349 (no invariant reads a computed activation against a finding). decisions/ADR-0054.md:313 ("ten properties hold together"), :323. checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:348 (item 101) does not list it.

### G-9: §10 lists two TLC-checked invariants of an unproved, Proposed module under "Theorems voided"
- Against: decisions/ADR-0054.md:280-283 (and decisions/ADR-0054.md:323; decisions/ADR-0047.md:355; decisions/ADR-0050.md:239)
- Basis: Proposed
- Claim: "| Id | Kind | Parameter → deployed value | Premises falsified | Theorems voided | Type changes (ADR-0023 §6b) |" with the cells "`PromotedAlternates`" and "`EdgeAfterCoverage`"
- Why wrong: Both are invariants of `spec/Workflow.tla` that are checked and not proved (ADR-0054.md:323: "**Not met:** proofs"; G11 line 179: "**`Workflow.tla` and `Mesh.tla` have no proof.**"), in a module with no row in the binding table (G11 item 90). The sibling records fill the same column honestly for the same situation: ADR-0047.md:355 "**None today**: no theorem in force reads a label", ADR-0050.md:239 "**None in force**". The corpus keeps *checked* and *proved* apart; this table does not.
- Fix belongs in: ADR-0054 §10
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:280-283 (cells `PromotedAlternates`, `EdgeAfterCoverage` under "Theorems voided"), :323 ("Not met: proofs"). Siblings: decisions/ADR-0047.md:355, ADR-0050.md:239, ADR-0051.md:286, ADR-0052.md:171 all write "None" and "properties are lost". G11:179; narrative/glossary.md:1214 (checked and proved are two words). ADOPTERS_GUIDE_README.md:145 puts `PromotedAlternates` under premises and "No safety theorem" under theorems.

### G-10: The reference the two records point to is not the reference in the corpus; ADR-0054 R6 cites A16 for a change A17 carries
- Against: decisions/ADR-0054.md:340 and :459 (and decisions/ADR-0055.md:223; decisions/ADR-0033.md:955-962; manifests/SHA256SUMS-REF-2026.10.08:44, manifests/SHA256SUMS-REF-2026.10.09:44)
- Basis: Proposed
- Claim: "**Met in part** ⟨R5⟩: ADR-0033 A16 (pending), the reference at `11aaf6a` (`SHA256SUMS-REF-2026.10.08`)." and, in R6, "The reference follows (`mechanism/` finding 22, A16)"
- Why wrong: `sha256sum mechanism/crates/topak-core/src/workflow.rs` gives `6f3ec5a3401e92e9…`, which is the line in `manifests/SHA256SUMS-REF-2026.10.09` (commit `749d54f`, ADR-0033 A17) and not the `7ac93259469d770c…` of `SHA256SUMS-REF-2026.10.08`. ADR-0033 says so itself: A16's manifest stops matching `workflow.rs` because of "the `denials` attribute ADR-0054 R6 dropped on 2026.10.09 ... after the manifest was cut" (ADR-0033.md:897-899), and A17 is the addendum that "measures the tree that A16 says moved" (:955-957). Neither ADR-0054 nor ADR-0055 mentions A17 or `749d54f`. At `11aaf6a` the reference still lifted `denials`, which §4 as revised by R6 forbids, so the tree §12 cites does not follow the record that cites it.
- Fix belongs in: ADR-0054 §12 and R6; ADR-0055 §11
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 lists both reference cuts at lines 202-203; the records' pointers are not on the open list)
- **Verifier:** confirmed
- **Verifier's evidence:** `sha256sum mechanism/crates/topak-core/src/workflow.rs` = 6f3ec5a3401e92e9..., which is manifests/SHA256SUMS-REF-2026.10.09:44 and not manifests/SHA256SUMS-REF-2026.10.08:44 (7ac93259469d770c...). decisions/ADR-0054.md:340 and :459, decisions/ADR-0055.md:223. decisions/ADR-0033.md:897-899 and :955-962. `grep -n "A17\|749d54f" decisions/ADR-0054.md decisions/ADR-0055.md` returns nothing. G11:202-203 lists both cuts.

### G-11: ADR-0054 treats ADR-0024 A3, ADR-0050 and ADR-0047 as not yet in force; all three were ratified two days before it was authored, and the condition that waits on them has no state
- Against: decisions/ADR-0054.md:7-8, :305 and :398 (and decisions/ADR-0024.md:11; decisions/ADR-0050.md:20; decisions/ADR-0047.md:19)
- Basis: Proposed
- Claim: "ADR-0024 A3 (Proposed with ADR-0050: a promotion seats)"; "**ADR-0050 and ADR-0024 A3 are ratified first**: this record is a promotion that seats, and stands on them."; "**It rests on four Proposed or provisional records**: ADR-0035, ADR-0050, ADR-0024 A3 and ADR-0047's attributes."
- Why wrong: ADR-0054 is authored 2026.10.07 (ADR-0054.md:2). ADR-0024.md:11: "A3, drafted 2026.10.04, with ADR-0050: a promotion seats (§1), ratified 2026.10.05 (Batch 34) and applied inline". ADR-0050.md:20: "**Status:** Accepted (genesis) · provisional · 2026.10.05". ADR-0047.md:19: "**Status:** Accepted (genesis) · 2026.10.05 · confirmation required", with no provisional marking, so the "four" are three at most. §12's second bullet is the only ratification condition in the record besides the reader bullet that carries neither "Met" nor "Not met", and by the two status lines it was met before the record existed. ADR-0050 is also named under "Relates to" (ADR-0054.md:35-36) and not under "Depends on", though §12 says the record "stands on" it.
- Fix belongs in: ADR-0054 (provenance note, §12, Consequences, Depends on)
- Severity: Low-Medium
- Confidence: medium (the phrase "Proposed with ADR-0050" could be read as history; :305 and :398 cannot)
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. At :398 "Proposed or provisional" is accurate of ADR-0050 and of ADR-0024 A3: both are provisional, in force and subject to redesign (ADR-0050.md:20-21; ADR-0024.md:326), which the finding does not say of A3. Only ADR-0047 is mislabelled there, so the "four" are three. The "not yet ratified" reading holds of the provenance note (:7-8) and of §12's unmarked condition (:305) only, not of :398.
- **Verifier's evidence:** decisions/ADR-0054.md:2, :7-8, :305, :398 quoted exactly; :30-36 (ADR-0050 under Relates to). decisions/ADR-0024.md:11 and :326 (A3 ratified 2026.10.05, provisional); decisions/ADR-0050.md:20-21; decisions/ADR-0047.md:19 (no provisional marking). §12 bullets at ADR-0054.md:296-346: only :305 and the reader bullet carry no state.

### G-12: Both records carry a debt against ADR-0045 that no ratification condition names and no dependent entry discharges
- Against: decisions/ADR-0054.md:46 and :296-304 (and decisions/ADR-0055.md:33-34, :199-200; decisions/ADR-0045.md:25)
- Basis: Proposed
- Claim: "**Carries a debt against:** ... ADR-0045 (the interpreter's row, §11)" against §12's "**The dependent entries are drafted**: ADR-0024 A3 ... ADR-0015 (`Route` as an emission). **Met** ⟨R3⟩"
- Why wrong: The header lists thirteen debts; §12's list of dependent entries has eleven (ADR-0033 is the reference item; ADR-0045 is nowhere), and R3's "Ten pending amendments and one revision in place" (ADR-0054.md:456) matches the eleven. ADR-0045's Pending line names only A5, for ADR-0057 (ADR-0045.md:25), and `grep -n -i "interpreter\|workflow\|0054" decisions/ADR-0045.md` returns nothing. §11 says the interpreter enters "under ADR-0045's existing mechanism row, not as a new row", which may mean no entry is owed, but then the debt line ("the interpreter's row") says something else, and the condition is marked Met with the debt neither discharged nor withdrawn. ADR-0055 repeats the pattern: debt "ADR-0045 (the interpreter's row grows, §10)" (ADR-0055.md:33-34), absent from §11's dependent entries (:199-200). The sibling records name theirs: ADR-0050 §10 lists "ADR-0045 A2 (two rows)" (ADR-0050.md:248), and ADR-0056 §11 lists ADR-0045 (ADR-0056.md:228).
- Fix belongs in: ADR-0054 header or §12; ADR-0055 header or §11; possibly ADR-0045
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 line 153 notes only that the growth "is Proposed")
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:41-46 (thirteen debts, ADR-0045 last), :296-304 (eleven entries, no ADR-0045), :289-291, :456. decisions/ADR-0055.md:33-34, :199-200, :190-192. decisions/ADR-0045.md:25; `grep -n -i "interpreter\|workflow\|0054" decisions/ADR-0045.md` returns nothing. decisions/ADR-0050.md:248 and decisions/ADR-0056.md:228 name theirs. G11:153.

### G-13: Four of ADR-0055's six ratification conditions have no state, and the one G11 says is unmet is not marked so in the record, while the reference already runs the kind
- Against: decisions/ADR-0055.md:198-200 and :217-218 (and decisions/ADR-0054.md:27; mechanism/crates/topak-core/src/workflow.rs:45-51, :517-526; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:67-68)
- Basis: Proposed
- Claim: "**The dependent entries are drafted**: ADR-0054 §1, §2, §4, §8 and §9, read per activation and with the kind and the budget; ADR-0035 §5 (the 2-colour check)." and "**The gate** computes the reachable activations within `N` and the edges with identically true guards, as evidence (§2), and refuses a mesh without a budget and one whose clear edges cannot be 2-coloured."
- Why wrong: Neither bullet says Met or Not met, where the module and reference bullets beside them do (:207, :215, :223). They are not met: G11 states "**ADR-0055's dependent entries are not drafted** (its §11)", ADR-0054 says "**Pending:** none." (ADR-0054.md:27) and nowhere mentions a kind, a mesh or a budget (`grep -n -i "mesh\|0055" decisions/ADR-0054.md` returns nothing), ADR-0035 R8 (ADR-0035.md:229-235) is ADR-0054's alternation and not a 2-colour check for a mesh, and the register lists "the gate's evidence for a mesh's vote" as not built (I49). Meanwhile the reference implements `Kind::Mesh` and the budget (workflow.rs:45-51, :517-526), so a reader of ADR-0054 alone would find the reference running a `kind` field the record it follows does not define. The first bullet (:198, "**ADR-0054 is ratified first**, or with this record.") and the last (the reader) also carry no state.
- Fix belongs in: ADR-0055 §11 (states); ADR-0054 (a revision in place carrying the kind and the budget, or a note that it is owed)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 101 ("ADR-0055's dependent entries"; "The gate's evidence for a mesh's vote"); the missing states in the record are not
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** decisions/ADR-0055.md:198-227: six bullets, four with no state (:198, :199-200, :217-218, :227). G11:67-68 and :348 (item 101) already record the entries and the gate's evidence as owed, and GAPS-AND-ASSUMPTIONS.md:108 discloses that one engine runs both kinds, so what is new is the missing marks: no claim is wrong, hence the lower severity. `grep -n -i "mesh\|0055" decisions/ADR-0054.md` returns nothing; ADR-0054.md:27. `grep -n -i "mesh\|2-colour\|0055" decisions/ADR-0035.md` returns nothing (:229-235 is R8). workflow.rs:45-51, :517-526.

### G-14: ADR-0055 changes ADR-0054 §3 and §6 without carrying a debt against them, and says Run's ingress "gain[s] nothing here" while §6 gives the orchestrator a new delivery
- Against: decisions/ADR-0055.md:30-34 and :18-19 (and decisions/ADR-0055.md:110-111, :130-131, :151-157, :164-165; decisions/ADR-0054.md:143-145)
- Basis: Proposed
- Claim: "**Carries a debt against:** ADR-0054 §1 ..., §2 ..., §4 ..., §8 ..., §9 ..." and "C2 does not apply: Run's ingress and alphabet are ADR-0054's and gain nothing here."
- Why wrong: ADR-0055 §6 rewrites two rows of ADR-0054 §3's table. Rounds: ADR-0054.md:144 "One round per decision point, granted by the promotion when the decision point is ready" becomes "One orchestrator round per decision event, granted from the budget when the event opens" (ADR-0055.md:151). Ingress: ADR-0054.md:145 lists the task, the enabled chosen edges, the attributes its guards read and a handle per output; ADR-0055.md:154-157 delivers "the track: the activation history that bears on the event, as typed facts with their labels, the triggers that link them, and handles for every output" and writes it "to the round topic as the round's opening record, as ADR-0048 §2 does for the tool list". §5 rewrites ADR-0054 §6's rule (ADR-0055.md:130-131). §3 and §6 say a route "names the activation it was decided for" and "names both its activation and its round" (:110-111, :164-165) against ADR-0054.md:143 "No other argument ⟨K8⟩". None of ADR-0054 §3, §6, ADR-0043 A3 (the orchestrator's closed list) or ADR-0048 §2 (the opening record) is in the debt list or in §11's dependent entries. Whether a new closed list for the orchestrator's Listener is "nothing" for C2 is the reviewer's call; the status note does not put the question.
- Fix belongs in: ADR-0055 (status note, debt list, §11)
- Severity: Low-Medium
- Confidence: medium (the reference stamps activation and round from the lease, workflow.rs:393-401, so "names" may not mean an argument; the debt-list omission stands either way)
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0055.md:17-19 and :30-34 quoted; §6 at :151-157 against decisions/ADR-0054.md:144-145; :130-131 against ADR-0054 §6; :110-111 and :163-165 against ADR-0054.md:143. The debt list (:30-34) and §11 (:199-200) name neither ADR-0054 §3 nor §6, nor ADR-0043 A3, nor ADR-0048 §2 (which is only under Relates to, :27).

### G-15: "The module's mesh" is not what the reference tests run, and the first behaviour §11 lists is outside what the module reaches
- Against: decisions/ADR-0055.md:219-220 and :224 (and spec/Mesh.tla:20, :67; mechanism/crates/topak-core/tests/workflow.rs:316, :331-332, :338; mechanism/crates/topak-core/tests/support/wf.rs:96-98, :112-113)
- Basis: Proposed
- Claim: "**The reference**, with an ADR-0033 addendum: the module's mesh run by scripted cells. **Behaviours, each seen:** the loop turns twice and exits" and "Every behaviour is seen as a test of the replicated state named after `Mesh.tla`'s properties, on the module's mesh."
- Why wrong: The module's budget is fixed at six, which its header glosses as "The budget N is 6: one loop and the exit" (Mesh.tla:20; `N == 6` at :67). Two turns and the exit cost nine leases, as the test says: `Log::started(&mesh(10))` (tests/workflow.rs:316) and "Nine leases, each charged: three of s, two of w, one of x, three orchestrator rounds" (:331-332). The budget test uses `mesh(4)` (:338). So the graph is the module's and the budget never is, and "the loop turns twice and exits" is a behaviour TLC did not check (the witness `NeverCompletedAfterLoop` is one turn). The same looseness is in the dag harness: wf.rs:96 says "as `spec/Workflow.tla` has it" and gives e3 the guard that `b` reports `done` (:112-113), where the module's e3 is `TRUE` (Workflow.tla:155).
- Fix belongs in: ADR-0055 §11 (the behaviour or the phrase); mechanism/crates/topak-core/tests/support/wf.rs comments
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0055.md:219-224 quoted exactly. spec/Mesh.tla:20 and :67 (N == 6), :320-322 (the witness is one turn). mechanism/crates/topak-core/tests/workflow.rs:316 (mesh(10)), :331-332 (nine leases), :338 (mesh(4)); no test uses mesh(6) (`grep -n "mesh(" tests/workflow.rs`). tests/support/wf.rs:96-98 and :112-113 against spec/Workflow.tla:155.

### G-16: Open obligations in ADR-0054 and ADR-0055 still list what their own ratification conditions mark Met and what the narrative has since done
- Against: decisions/ADR-0054.md:433 and :442-443; decisions/ADR-0055.md:296 and :304-305 (and decisions/ADR-0054.md:301, :328; decisions/ADR-0055.md:207-208; narrative/glossary.md:19-21; narrative/theory-of-operation.md:582)
- Basis: Proposed
- Claim: ADR-0054: "**The dependent entries, the module, the floor and the reference** (§12)." and "**Narrative.** ToO §2.8, §2.9, §2.10 and §7.1 and the glossary owe *workflow*, *node*, *edge*, *guard*, *decision point*, *orchestrator*, *input* and *route* at the next checkpoint." ADR-0055: "**The dependent entries, the module rows not yet run, the gate and the reference** (§11)." and "**Narrative.** ToO and the glossary owe *mesh*, *activation*, *causal history*, *decision event*, *budget* and *track* at the next checkpoint."
- Why wrong: ADR-0054 §12 marks the dependent entries "**Met** ⟨R3⟩" (:301) and the floor "**Met** ⟨R4⟩" (:328). ADR-0055 §11 reports all 23 rows run (:207-208: "23 rows from `spec/Mesh-rows.txt`"), so there are no "module rows not yet run". The glossary records the terms as added (glossary.md:19-21: "From ADR-0054, Proposed: *workflow*, *node*, *edge*, *guard*, *decision point*, *orchestrator*, *input* and *route*. From ADR-0055, Proposed: *mesh*, *activation*, *causal history*, *decision event*, *budget* and *track*"), and the ToO has §2.11 for both records (theory-of-operation.md:582). The History rows that marked the conditions Met (R3, R4; R1) each say "No decision text changes" and left the lists as drafted.
- Fix belongs in: ADR-0054 and ADR-0055, Open obligations
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 100 lists the narrative terms as owed at G11; that they are now done and still listed in the records is not on a list
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:433 and :442-443, decisions/ADR-0055.md:296 and :304-305 quoted exactly. ADR-0054.md:301 (Met, R3), :328 (Met, R4); ADR-0055.md:207-208 (23 rows run). narrative/glossary.md:19-21 and entries at :257-328; narrative/theory-of-operation.md:582. ADR-0054.md:454-458 and ADR-0055.md:316-317: every row says "No decision text changes".

### G-17: D-0054-2's Kind is "Deployment", which is not one of the two kinds ADR-0023 §6a defines
- Against: decisions/ADR-0054.md:283 (and decisions/ADR-0023.md:47)
- Basis: Proposed
- Claim: "| **D-0054-2** | Deployment | Coverage at the edge: required → waived"
- Why wrong: ADR-0023.md:47, in force: "**6a. Kind.** ⟨R4⟩ Two values. A **mechanism degeneracy** changes a value inside the verified object ... A **declaration degeneracy** changes something outside it". Waiving a check the mechanism makes when it enables an edge reads as the first kind, which "reopens the proofs that quantify over it; it ships as a mechanism release", and the row's own "Theorems voided" cell names a property. `grep -n -i "deployment degenerac" decisions/*.md narrative/glossary.md` returns nothing, so the third value is defined nowhere. ADR-0050 (D-0050-2, D-0050-3) and ADR-0051 (D-0051-2) use it too, so this is a precedent followed and not a slip of this record alone.
- Fix belongs in: ADR-0054 §10, or ADR-0023 §6a if a third kind is meant
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:283; decisions/ADR-0023.md:47 ("Two values"); narrative/glossary.md:1031-1032. `grep -n -i "deployment degenerac" decisions/*.md narrative/glossary.md` returns nothing. Same value at decisions/ADR-0050.md:240-241 and decisions/ADR-0051.md:287.

### G-18: ADR-0056's degeneracy table and trusted-base rows do not carry the fixed schemas the records in force require
- Against: decisions/ADR-0056.md:207-211 and :194-198 (and decisions/ADR-0023.md:45; decisions/ADR-0045.md:82-94; decisions/ADR-0054.md:280)
- Basis: Proposed
- Claim: "| Id | Degeneracy | What it costs |" and "| Row | Component | Class | Failure can produce | Identity fixed by |"
- Why wrong: ADR-0023.md:45: "**Every degeneracy carries a declaration record** with fixed schema: **kind** ⟨R4⟩, parameter, archetype value, deployed value, premises falsified, theorems voided, **type changes** ⟨R4⟩". ADR-0056 §9 gives none of kind, premises falsified, theorems voided or type changes, though D-0056-2 changes the trusted base by its own account ("The store becomes part of T-0045-25"), which is what §6b's field exists to state. Every sibling I opened uses the full table (ADR-0054.md:280; ADR-0050.md:239-241; ADR-0047.md:355). ADR-0045.md:82: "The schema is fixed", with eight fields; §8's rows omit Layer, Trusted for (the row's premise node), Rungs and Residual ("Never empty", ADR-0045.md:94).
- Fix belongs in: ADR-0056 §8 and §9
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0056.md:194-198 (five columns) and :207-211 (three columns), quoted exactly. decisions/ADR-0023.md:45; decisions/ADR-0045.md:82-94 (eight fields, Residual never empty). Full forms at decisions/ADR-0054.md:280, ADR-0050.md:237-241, ADR-0047.md:353-355 and, for a row, decisions/ADR-0053.md:162.

### G-19: None of ADR-0056's six ratification conditions has a state, nothing they ask for exists, and its Open obligations omit all of them
- Against: decisions/ADR-0056.md:225-242 and :306-313 (and decisions/ADR-0054.md:433; decisions/ADR-0049.md:21; decisions/ADR-0050.md:25; decisions/ADR-0048.md:21)
- Basis: Proposed
- Claim: "**The dependent entries are drafted**: ADR-0049 (§3's fields; W11 to W13), ADR-0050 §5, ADR-0031 A3, ADR-0041 (`R10`, `R11`, the `RunCtx` attributes), ADR-0042 §6, ADR-0045 (T-0045-38, T-0045-39, T-0045-25's premise), ADR-0025 A2 (the provider list), ADR-0048 §2, ToO §13 (§6's assumption of use), and ADR-0054 §2 if it is ratified first." (and the module, floor, reference and reader bullets after it)
- Why wrong: No bullet says Met or Not met. None is met: the Pending lines of ADR-0049, ADR-0050 and ADR-0048 read "none" (:21, :25, :21) and those of ADR-0031, 0041, 0042 and 0045 name only amendments for ADR-0054 or ADR-0057; `ls floor/proposed | grep -i subj` and `ls spec | grep -i "subj\|credential"` return nothing; among `.md`, `.tla`, `.rs`, `.cedar`, `.json` and `.py` files the only ones that mention ADR-0056 are the record, the index row, one diagram source and a derived proposal. The record's Open obligations (:306-313) list six design questions and not one of §11's items, where the sibling records open that list with them (ADR-0054.md:433: "**The dependent entries, the module, the floor and the reference** (§12)"). A reader cannot tell from the record that it is a draft with nothing behind it; the index (decisions/README.md:69) does not say either.
- Fix belongs in: ADR-0056 §11 and Open obligations
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (ADR-0056 postdates G11)
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** Scope. The last open obligation (:313, "ADR-0054's activation carrying one subject") is §11's "ADR-0054 §2 if it is ratified first" (:229-230), so the list omits all but one of §11's items, not all. Unmarked conditions are also how a draft stands before work is done (every Met in ADR-0054 §12 carries an R tag), so the defect is the omission from Open obligations, not the absence of marks; no claim in the record is wrong, hence Low.
- **Verifier's evidence:** decisions/ADR-0056.md:225-242 (no Met or Not met), :304-313. `ls floor/proposed | grep -i subj` and `ls spec | grep -i "subj\|credential"` return nothing. `grep -rl "ADR-0056" --include=*.md --include=*.tla --include=*.rs --include=*.cedar --include=*.json --include=*.py .` gives the record, decisions/README.md, one diagram source and one derived proposal. Pending lines: ADR-0049.md:21, ADR-0050.md:25, ADR-0048.md:21, ADR-0031.md:13, ADR-0041.md:19, ADR-0042.md:19, ADR-0045.md:25.

### G-20: ADR-0056 bounds a subject's authority by the lease's `ttl` and refreshes nothing in a round, but a round is renewable past its `ttl` at a new fence
- Against: decisions/ADR-0056.md:111-112 (and decisions/ADR-0056.md:99-101; decisions/ADR-0031.md:150-162; decisions/ADR-0042.md:167; decisions/ADR-0050.md:123-127)
- Basis: Proposed
- Claim: "**The subject's authority ends with the round.** The lease's `ttl` bounds it (ADR-0031 A2). Nothing is refreshed inside a round."
- Why wrong: In force, a round outlives a `ttl` by renewal: ADR-0031.md:153 "A renewal keeps `round` and `role` unchanged", :160-161 "its new `ttl` is again at most `T_persona`", and ADR-0042.md:167 "| Renewal at a new fence | **No** | The round continues". So the `ttl` does not bound the round, and the subject's authority runs as long as the round is renewed. The assertion "names ... **the fence of the grant it is presented for**" and "freshness is the fence" (ADR-0056.md:99-101); after a renewal the lease has a new fence and the assertion names the old one, which is the state the record's own mutation `M_STALE_ASSERTION` (:235) is about. The model the record says it follows re-checks at renewal (ADR-0050.md:123: "it is read only when a lease is granted or renewed"); ADR-0056 says "It is checked at grant" and is silent on renewal.
- Fix belongs in: ADR-0056 §2 (renewal: re-evidenced, refused, or the bound restated)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0056.md:111-112 quoted exactly; :99-101 (the assertion names the grant's fence), :235. `grep -n -i "renew" decisions/ADR-0056.md` returns nothing. decisions/ADR-0031.md:152-154 and :160-161 (a renewal keeps the round and takes a new ttl); decisions/ADR-0042.md:167 ("The round continues"); decisions/ADR-0050.md:123-127 (read at grant and renewal).

### G-21: ADR-0056 refers to "ADR-0054's pending amendment" and "ADR-0054's activation"; ADR-0054 has neither
- Against: decisions/ADR-0056.md:296-298, :313 and :36 (and decisions/ADR-0054.md:27; decisions/ADR-0055.md:99-100)
- Basis: Proposed
- Claim: "Across rounds, a workflow edge (ADR-0054) could carry one user's data into another's round unless the activation is per subject. ADR-0054's pending amendment should say so." and "**ADR-0054's activation** carrying one subject, if ADR-0054 is ratified first." and "ADR-0054 §2 (Proposed: a workflow activation carries one subject)"
- Why wrong: ADR-0054.md:27: "**Pending:** none."; it is a Proposed record and is revised in place, not amended. The activation is ADR-0055's unit, introduced there (ADR-0055.md:99-100: "ADR-0054's per-node rules are restated per **activation**, a pair (node, *k*)"); ADR-0054 §2 speaks of nodes. So the debt names a clause of the wrong record or a term that record does not have, and §11 inherits it ("ADR-0054 §2 if it is ratified first", ADR-0056.md:229-230).
- Fix belongs in: ADR-0056 (header debt, finding 4, Open obligations, §11)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0056.md:36, :229-230, :296-298, :313 quoted exactly. decisions/ADR-0054.md:27 ("Pending: none."); `grep -n -i -o "activation" decisions/ADR-0054.md` returns nothing. decisions/ADR-0055.md:99-100 introduces the term.

### G-22: The narrative says the `workflow` stage adds "two forbids"; it adds one permit and one forbid
- Against: narrative/theory-of-operation.md:759-760 (and floor/proposed/workflow-floor.cedar:208-209, :218-219; floor/proposed/README.md:80)
- Basis: living document
- Claim: "`workflow` adds the action `Route` and two forbids, one keeping it to the `orchestrator` kind and one to that seat's own decision point"
- Why wrong: workflow-floor.cedar:208-209: `@id("R8-route-own-decision")` / `permit (principal, action == Topak::Action::"Route", resource)`. Only R9 is a forbid (:218-219). floor/proposed/README.md:80: "One permit and one forbid over a new action". The difference is not cosmetic: `Route` has no other permit, so R8 is what admits a route at all, and a route out of another decision point is denied for want of a permit, not by a forbid.
- Fix belongs in: narrative/theory-of-operation.md §3.1
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** narrative/theory-of-operation.md:759-760 quoted exactly. floor/proposed/workflow-floor.cedar:208-209 (R8 is a permit, the only permit on `Route` by `grep -n "Route"`), :218-219 (R9, the one forbid). floor/proposed/README.md:80; decisions/ADR-0041.md:112-113.

### G-23: `floor/proposed/README.md` says the reference's lift supplies none of the floor's inputs, and reads as if nothing in the directory were in force
- Against: floor/proposed/README.md:123-125, :3 and :5 (and mechanism/crates/topak-core/src/lift.rs:183-189, :402; mechanism/GAPS-AND-ASSUMPTIONS.md:49; decisions/ADR-0033.md:893-894)
- Basis: evidence
- Claim: "`clearSet`, `destLiteral`, `peerLive` and the rest are facts the lift supplies. ... The reference's lift supplies none of them today." and "DRAFT · not ratified" and "This directory holds the floor as it would read if the records drafted on 2026.10.03 and 2026.10.04 were in force."
- Why wrong: lift.rs:185-189 writes `"clearSet": rec.labels.clear_set`, `"inputLabels"`, `"destLiteral"`, `"destLabels"` and `"decisionPoint"`, and :402 `"peerLive": facts.peer_live`. The same README says at :3 that "**the reference links the `workflow` stage**" and at :81-82 that "every Run request it lifts carries `decisionPoint`", and ADR-0054 §12's R5 behaviour depends on the lifted `clearSet`. On force: the records of 2026.10.03 and 10.04 were ratified on 2026.10.05, and the `emergency` stage in this directory is the floor in force (GAPS-AND-ASSUMPTIONS.md:49: "**It is still the floor in force**"; ADR-0033.md:893-894: "A12's `emergency` stage, which stays the floor in force"). The README's only statement about force is "Nothing here is in force" in the Workflow paragraph (:81). A reader of this file alone would take three in-force stages for drafts, or the `workflow` stage for one of them.
- Fix belongs in: floor/proposed/README.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 91 is the stage files' opening comment, not this README)
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** Two statements need changing. "The README's only statement about force is ... (:81)" is not so: :8 says the `workflow` stage is "not in force" and :34 that `floor/lean` "states the floor in force" from `emergency-tests.json`. And "not ratified" at :3 is accurate of the stage in force, which the register calls genesis-provisional, enforced and not yet ratified (GAPS-AND-ASSUMPTIONS.md:49). What stands: :125 is false, and :5 is a stale conditional. A stale README sentence that the same file's header contradicts, so Low-Medium.
- **Verifier's evidence:** floor/proposed/README.md:3, :5, :8, :34, :81, :123-125. mechanism/crates/topak-core/src/lift.rs:185-189 and :402. mechanism/GAPS-AND-ASSUMPTIONS.md:49; decisions/ADR-0033.md:893-894; decisions/ADR-0047.md:19 and decisions/ADR-0050.md:20 (ratified 2026.10.05).

### G-24: The `workflow` stage's files carry stale comments beyond the opening one the corpus already lists
- Against: floor/proposed/workflow-floor.cedar:4 and :118; floor/proposed/workflow.cedarschema:144 and :154 (and decisions/ADR-0040.md:15; decisions/ADR-0041.md:12; decisions/ADR-0050.md:20)
- Basis: evidence
- Claim: "not ratified · schema: genesis.cedarschema"; "Run envelopes : ADR-0040 §1, stated as ADR-0041 §1 (both Proposed)"; "Run's alphabet (ADR-0040 §1, Proposed)"; "the control alphabet (ADR-0050 §4, Proposed)"
- Why wrong: The stage's schema is `workflow.cedarschema` (the gate header: "schema workflow.cedarschema (sha256 fd394bb8c074eec2)"). ADR-0040.md:15 and ADR-0041.md:12: "**Status:** Accepted (genesis) · 2026.09.30"; ADR-0050.md:20: "Accepted (genesis) · provisional · 2026.10.05". The lines are the genesis text carried through `build.py`'s string edits. The first two lines of the floor, the schema and the gate results ("not what the reference follows") are the known case.
- Fix belongs in: floor/proposed/build.py (at the stage's next gate run, as the README says of the opening comment)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 91 and the register's §1.1 row for the stage cover the opening comment only; these lines are not listed
- **Verifier:** confirmed
- **Verifier's evidence:** floor/proposed/workflow-floor.cedar:4 and :118, floor/proposed/workflow.cedarschema:144 and :154 quoted exactly. floor/proposed/workflow-gates-results-2026.10.08.txt:5 (schema workflow.cedarschema). decisions/ADR-0040.md:15, ADR-0041.md:12, ADR-0050.md:20. G11:339 (item 91) and floor/proposed/README.md:8-10 cover the opening comment only.

### G-25: ADR-0047's History row for A1 still counts eight workflow attributes; the amendment's text has seven
- Against: decisions/ADR-0047.md:581 (and decisions/ADR-0047.md:207-208; decisions/ADR-0054.md:459)
- Basis: pending
- Claim: "§4: the fixed set of mechanism-computed attributes gains a workflow node's eight"
- Why wrong: The inline text reads "`end`, `actuates`, ~~`denials`,~~ (ADR-0054 R6) `label`, `covered`, `found`, `outcome` and `output`" (ADR-0047.md:207-208), which is seven. ADR-0054 R6 says "ADR-0047 A1's list drops the word" (ADR-0054.md:459); the row's count was not changed and no row records the edit to the pending text.
- Fix belongs in: ADR-0047 History (a revision row to pending A1, as ADR-0041 R3 is for A4)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:581 ("a workflow node's eight") against :207-208 (seven after the struck `denials`); decisions/ADR-0054.md:459. :581 is the last line of the file (`wc -l` gives 581), so no later row records the edit.

### G-26: The index gives confirmation criteria for ADR-0056 and later Proposed records and none for ADR-0054 or ADR-0055
- Against: decisions/README.md:67-68 (and decisions/README.md:69; decisions/ADR-0054.md:21-25; decisions/ADR-0055.md:17)
- Basis: living document
- Claim: "Proposed (drafted 2026.10.07, after G10)" (both rows)
- Why wrong: The next row reads "Proposed (drafted 2026.11.06, after G11); confirmation required: C1, with C2 applying to §5" and the rows after it carry theirs. ADR-0054's status note claims four (ADR-0054.md:21-25: "Confirmation required under **C1** ... **C2** ... **C3** ... and **C4**") and ADR-0055's one (:17). The column is also headed "Status at G8" under a sentence that says "Status is as of Genesis Checkpoint G11".
- Fix belongs in: decisions/README.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** "The rows after it carry theirs" is wrong. decisions/README.md:70-71 (ADR-0057, ADR-0058) carry no criteria though both status notes say C2 (ADR-0057.md:19, ADR-0058.md:12), and the older Proposed rows at :48, :49 and :64 (ADR-0035, ADR-0036, ADR-0051, all confirmation-required) carry none either. Only :69, :72 and :73 give criteria. The defect is index-wide: seven Proposed rows omit them, ADR-0054 and ADR-0055 among them.
- **Verifier's evidence:** decisions/README.md:3-4 against :12 ("Status at G8"); :48-49, :64, :67-73. decisions/ADR-0054.md:21-25; decisions/ADR-0055.md:17; ADR-0035.md:12, ADR-0036.md:12, ADR-0051.md:15, ADR-0057.md:19, ADR-0058.md:12.

### G-27: Each module lists abstractions its record's "Not met" does not, and each record lists gaps its module's header does not
- Against: decisions/ADR-0054.md:323-324 and decisions/ADR-0055.md:215-216 (and spec/Workflow.tla:50-54; spec/Mesh.tla:42-48)
- Basis: Proposed
- Claim: "**Not met:** proofs; more than one decision point; multi-select; `all` joins and skips; the orchestrator's own rounds; the step and time bounds." and "**Not met:** fan-out, scoped joins and pools; serialisation per node; a self-loop with seatings by parity; the static 2-colour check, which belongs to the gate; proofs."
- Why wrong: Workflow.tla:50-54 also leaves out "Run admits inside a node's round", "attestation at grant", "lineage beyond two values" and "erasure". The first means §5's "An item delivered clear joins the receiver's `clearSet`" is in no module: `End(n, s, l)` (Workflow.tla:213-217) takes any label and does not derive it from an input. The second is §2's "Confinement is appraised at that grant". The module's own list in turn omits the step and time bounds the record names. Mesh.tla:44-47 leaves out "Observer lineage; epochs and fences; the track the orchestrator is delivered", and coverage (:42-44), none of which is in ADR-0055's list; nor is `N(v)`, the per-node bound of §2, which is in neither.
- Fix belongs in: ADR-0054 §12 and ADR-0055 §11 (or the module headers)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 101 names "Fan-out, scoped joins, pools and parity seatings in a module" only
- **Verifier:** confirmed with correction
- **Verifier's correction:** "is in no module" is wrong of §5's clear-input rule. spec/Mesh.tla models it: :128-131 (NewAct, "A clear edge carries the source's label ... (ADR-0054 §5)"), :61 (M_FORGETTAINT), :298 (LabelCoversTruth). It is absent from spec/Workflow.tla only (:213-217). The rest stands.
- **Verifier's evidence:** decisions/ADR-0054.md:323-324 and decisions/ADR-0055.md:215-216 quoted exactly. spec/Workflow.tla:50-54; `grep -n "step\|T_wf\|time bound" spec/Workflow.tla` returns nothing. spec/Mesh.tla:42-48. `grep -n "N(v)" spec/Mesh.tla` returns nothing; ADR-0055.md:76.

### G-28: The register's table of TLA+ properties and the tests that restate them has no row for `Workflow.tla` or `Mesh.tla`
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:294-296 (and mechanism/crates/topak-core/tests/workflow.rs:1-3; mechanism/GAPS-AND-ASSUMPTIONS.md:3)
- Basis: evidence
- Claim: "## 6. TLA+ properties and the tests that restate them" and "**Since 2026.09.30 the restatement is checked, not asserted, on every path a test takes**"
- Why wrong: tests/workflow.rs:1-3: "The properties are `spec/Workflow.tla`'s and `spec/Mesh.tla`'s; each test names the property it shows and the mutation whose state it shows is refused." §6 has rows for every other module the tests restate and none for these two (a grep for `Workflow` or `Mesh` matches nothing from line 294 on), though the header says the register was "brought current ... for workflows 2026.10.08" (:3). §6's opening sentence is also untrue of these eighteen tests: I49 says "`spec/Mechanism.tla` does not model workflows ... and trace validation was not rerun".
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §6
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 56 (trace validation behind the tree); the missing rows are not listed
- **Verifier:** confirmed with correction
- **Verifier's correction:** "§6 has rows for every other module the tests restate" is wrong. From line 294 on there is no row for `Operators.tla`, `Emergency.tla` or `Labels.tla` either, though tests/operators.rs:4, tests/emergency.rs:2 and tests/mutations.rs:913-918 say they restate them. The table stops at the modules of 2026.10.02 and before; `Workflow.tla` and `Mesh.tla` are two of five missing.
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:3, :294-301, :308 on. `awk 'NR>=294' mechanism/GAPS-AND-ASSUMPTIONS.md | grep -n -i "workflow\|mesh"` returns nothing; the same with "Operators\|Emergency\|Labels" returns nothing. mechanism/crates/topak-core/tests/workflow.rs:1-3. GAPS-AND-ASSUMPTIONS.md:108 ("trace validation was not rerun").

### G-29: §5 cites ADR-0049 §5 for "an outward entry"; that section declares the channel, and "outward" is defined at the end of §4
- Against: decisions/ADR-0054.md:204 (and decisions/ADR-0049.md:139-140, :142-144)
- Basis: Proposed
- Claim: "An edge whose target's lease reaches an outward entry (ADR-0049 §5)"
- Why wrong: ADR-0049.md:139-140, in §4: "**\"Outward\" is derived and never declared.** An entry is outward when it has a channel whose target the issued rules do not list as inside the deployment (ADR-0047 §7)." §5 (:142-144) is "One declaration of the channel" and does not use the word. ADR-0047 A1's statement of the same rule gives no citation.
- Fix belongs in: ADR-0054 §5
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:204. decisions/ADR-0049.md:139-140 (the definition, in §4, which starts at :122); §5 is :142-154 and `grep -n -i "outward" decisions/ADR-0049.md` has no hit in that range. decisions/ADR-0047.md:211-212 gives no citation.

### G-30: ADR-0031's in-force A3 text, which the pending A4 extends, still calls ADR-0050 Proposed
- Against: decisions/ADR-0031.md:84-85 (and decisions/ADR-0050.md:20)
- Basis: in force
- Claim: "This record says what a grant is and never who makes one. ADR-0050 (Proposed) does."
- Why wrong: The sentence is marked "⟨A3⟩ ⟨B34⟩", applied at Batch 34, the batch that ratified ADR-0050 (ADR-0050.md:20: "**Status:** Accepted (genesis) · provisional · 2026.10.05 ... ⟨B34⟩"). The pending A4 begins a few lines later (:100) with "ADR-0054 (Proposed) adds one beside the first lease on a quorum and the successor grant", so the same passage uses "(Proposed)" once correctly and once not, and a reader of the grant paths cannot tell the two apart by the marking.
- Fix belongs in: ADR-0031 (an erratum to the applied A3 text)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:84-85 quoted exactly, marked A3 and B34; :423 ("the text marked A3 is in force as written"); :100 (the correct "(Proposed)" for ADR-0054). decisions/ADR-0050.md:20. `grep -n -i "speaks as of\|as of its drafting" decisions/ADR-0031.md` returns nothing.

### G-31: A Proposed record says what "every deployment today" declares
- Against: decisions/ADR-0054.md:28-29 and :282 (and checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:130-131)
- Basis: Proposed
- Claim: "Lineage alternation (§6) cannot be enforced until ADR-0035 is in force, so every deployment today declares D-0054-1." and "**Every deployment today**, since ADR-0035 is Proposed"
- Why wrong: ADR-0054 is "**Status:** Proposed" (:20) and its own floor item says "it is in force only with this record" (:332). A degeneracy on a record not in force binds no deployment today; a deployment today has no workflow to declare it of. The state of record repeats the sentence without the qualifier (G11:130-131: "Until ADR-0035 is in force that is declared and not enforced, so every deployment declares D-0054-1"), and the adopter's guide lists D-0054-1 beside D-0035-1 in its table of declarations (ADOPTERS_GUIDE_README.md:145). What is meant, that a deployment of a workflow would have to declare it until ADR-0035 is ratified, is conditional twice over and is written as a present fact.
- Fix belongs in: ADR-0054 (Deployment position, §6, §10)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** "A deployment today has no workflow to declare it of" is wrong of the one deployment that exists. The reference has run workflows on the Proposed record since ADR-0033 A16 and declares lineage as a tag (GAPS-AND-ASSUMPTIONS.md:108, I49 (b), "D-0054-1"), and ADOPTERS_GUIDE_README.md:145 is that reference's declaration (:124-131), with its source marked ADR-0054 Proposed, so the guide is not an instance of the defect. What stands: :28-29, :228-229 and :282, and G11:130-131, state without condition what holds only of a deployment that runs a workflow, and only as an obligation once the record is in force.
- **Verifier's evidence:** decisions/ADR-0054.md:20, :28-29, :228-229, :282, :332. checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:129-131. ADOPTERS_GUIDE_README.md:124-131 and :145. mechanism/GAPS-AND-ASSUMPTIONS.md:108.

### G-32: "The workflow the lease names" and "the lease's decision point" have no field in the lease, whose field set A4 says is unchanged
- Against: decisions/ADR-0054.md:143 and :331 (and decisions/ADR-0040.md:82; decisions/ADR-0041.md:112; floor/proposed/workflow.cedarschema:108; decisions/ADR-0031.md:70-71, :424; mechanism/crates/topak-core/src/workflow.rs:377-380)
- Basis: Proposed
- Claim: "`edge` names a chosen edge of the workflow the lease names, out of the decision point the round was granted for." and "The lease's decision point is a set in `RunCtx`"
- Why wrong: ADR-0031.md:70-71, in force: "**Every field is an authority claim, and the set is closed.** A capability not expressible as one of these fields is not carried by the lease". The field table (:54-68) has no workflow and no decision point, and the pending A4's History row says "§1's field set and §4's monotonicity are unchanged" (:424). ADR-0031 A3 and ADR-0056 both take care to say what travels "beside the lease" (ADR-0031.md:97-98; ADR-0056.md:96-97); no text says that of a workflow lease's binding. The reference keeps it beside the lease, in a map keyed by fence (workflow.rs:377-380, `Binding { workflow, slot, ... }`), which is the reading the records should state. As written, three records and the schema comment describe a lease that names things §1 says a lease cannot carry.
- Fix belongs in: ADR-0031 A4 (say where the binding travels); ADR-0054 §3, ADR-0040 A2 and ADR-0041 A4 wording
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:143 and :331 quoted exactly. decisions/ADR-0031.md:54-71 (twelve fields, no workflow or decision point; the set is closed), :97-98, :424 ("§1's field set ... unchanged"). decisions/ADR-0040.md:82; decisions/ADR-0041.md:112; floor/proposed/workflow.cedarschema:108. workflow.rs:377-380. `grep -n -i "beside the lease\|lease field" decisions/ADR-0054.md decisions/ADR-0055.md decisions/ADR-0040.md decisions/ADR-0041.md decisions/ADR-0024.md decisions/ADR-0043.md` finds nothing about a workflow's binding.

### G-33: §12's floor item says "Nothing loads the stage"; the reference has linked it since 2026.10.08, as the next item of the same list says
- Against: decisions/ADR-0054.md:332 (and decisions/ADR-0054.md:340-342, :458; floor/proposed/README.md:3; mechanism/README.md:29)
- Basis: Proposed
- Claim: "Nothing loads the stage, and it is in force only with this record and ADR-0041 A4."
- Why wrong: Ten lines on, the reference item reads "Every behaviour is seen ... and the one that needs the floor through the linked `workflow` stage" (:341-342), and R5 says the reference "links the `workflow` floor stage" (:458). floor/proposed/README.md:3: "**the reference links the `workflow` stage** (since 2026.10.08". mechanism/README.md:29: "Cedar engine with the proposed floor's `workflow` stage compiled in". The sentence was true at R4, and R5 did not touch it ("No decision text changes").
- Fix belongs in: ADR-0054 §12
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 102 records the linking; the stale sentence in the record is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0054.md:332 quoted exactly, against :340-342 and :458 in the same record; :457-458 (R4 and R5: "No decision text changes"). floor/proposed/README.md:3; mechanism/README.md:29. G11:349 (item 102) records the linking.

