# What code is easiest to refine to, and what else can be externalized

**2026.11.18** · derived · an answer, not a record · basis: the tree at `6588bce` (after G12), ADR-0018, ADR-0030
(§1 to §5, A2), ADR-0037, ADR-0049, ADR-0053, ADR-0054 (Proposed), `mechanism/GAPS-AND-ASSUMPTIONS.md`,
`mechanism/lean/`, `policies/tool_schema.rego`, `floor/genesis-values.json`, and
`derived/topak-refinement-verification-options-2026.11.04.md` · written by the assistant in answer to the
custodian's four questions of the day, quoted below · the companion of
`derived/topak-policy-externalization-and-refinement-2026.11.18.md`, which it follows · nothing here is built or
ratified.

> what programming paradigms and patterns are the easiest to refine to? I assume procedural with bounded recursion
> and no go-to's. also, how can the externalization pattern be applied to other aspects of code configuration?

> Doesn't strict data typing and bounding at the schema/vocab level externalize a lot?

> And floor/bundle policy can perform data validation externally?

The first is given as the custodian clarified it.

**Short answer.** The assumption is right, with one condition added: structured control flow and bounded recursion
make code easy to refine only when mutation is not aliased. Externalization transfers to any configuration that can
be held as restricted data, checked at load by the mechanism, and named by digest. Typing and bounding the
vocabulary is the highest-yield case, because it removes cases instead of deciding them. Policy can validate data,
and the bundle tier already does; only the floor's validation can carry a proof. Put together, the four answers
sort every fact about a request into one of four places (§5), and only the last of them still costs a refinement.

---

## 1. What code is easiest to refine to

What makes code easy to refine is how little of its behaviour lives outside a function's inputs and outputs. From
easiest to hardest:

| | Shape | Why | In the tree |
|---|---|---|---|
| 1 | Pure, total functions over enums and records, written as pattern matching | A model of the code is nearly a transcription of it | `compose` and `floor_gate` in `mechanism/crates/topak-core/src/admit.rs`, stated directly in `mechanism/lean/Topak/Admit.lean` |
| 2 | An explicit state machine, `step(state, event) → state`, with no I/O inside | It is the shape a TLA+ action already has, so a code step maps to a spec step | `topak-paxos`, sans-IO; `State::apply(index, entry, params)` |
| 3 | Bounded loops and bounded or structural recursion | Termination needs no invariant | — |
| 4 | Mutation of what a procedure owns or is handed, and nothing else | Ownership is what lets a translator turn mutation into pure functions | The premise Aeneas rests on (the 11.04 options document, §2.3) |

**On recursion.** Recursion bounded by a depth counter still owes a proof that the bound is never reached, or a
defined behaviour when it is. Recursion on a strictly smaller piece of the input owes neither. Where there is a
choice, the second is cheaper.

**On go-tos.** An unstructured jump breaks the property that a block can be reasoned about from its entry and its
exit. The disciplined form is row 2: a program counter held as an explicit field of the state.

**On "procedural".** It is the word that needs the condition. Procedural code with perfect control flow is still
hard to refine when two references reach the same record, or several places write one global. That, more than
loops or recursion, separates `admit.rs` from `State::apply`.

The profile that results (no go-tos, bounded loops, bounded recursion, no aliasing, no I/O in the logic) is close
to the safety-critical C rule sets. Holzmann's "Power of Ten" goes further and bans recursion outright. That is
cited from general knowledge and was not read for this document.

**What the 11.04 options document found would block a mechanical translation of this crate**, each still in the
tree at `6588bce`:

- Dynamic dispatch: four `dyn Fn` parameters, two in `state.rs` and two in `workflow.rs`.
- One labelled `break 'find` in `workflow.rs`.
- `BTreeMap` and `BTreeSet`, which have no shipped model and would be modelled by hand.
- Integer arithmetic, modelled with panic-on-overflow, so what is verified is the debug build's semantics.

Its estimate: days for `admit.rs`, `clock.rs` and `lift.rs`; for `State::apply`, "two to six weeks of refactoring
and modelling, then proofs."

Hidden behaviour of the same kind has already cost the reference once. `canonical_json` was not canonical in any
build that linked the floor, because a dependency's feature flag changed map ordering across the whole build
(`mechanism/GAPS-AND-ASSUMPTIONS.md` finding 15).

**One pattern the tree adds: guards that can only refuse.** `mechanism/lean/Topak/SeatsModel.lean` models every
check it does not state as one Boolean, `ok`, "that can only refuse". That is sound because a refusal breaks no
safety invariant. Code written so that most branches subtract can be modelled with most of its detail left out.

## 2. Externalization as a pattern, beyond policy

The pattern has four parts. It transfers wherever all four can hold.

1. The variable part is **data in a restricted language**, not code.
2. A **well-formedness check at load** is fixed in the mechanism, and the data cannot waive it.
3. The mechanism is proved **once, for every well-formed input**.
4. The data is **named by digest in each decision**, so which one was in force is on the record.

The tree already applies it to more than policy:

| What is externalized | Where | The check the mechanism holds |
|---|---|---|
| Numeric thresholds | `floor/genesis-values.json` | "Relaxing a value is an anchor issuance and a promotion; tightening is an ordinary promotion" |
| Tool allowlists | `policies/data.json` | W1 to W10 of ADR-0049 §6, refused at load (ADR-0030 A2) |
| Workflow shape | `workflow.json` (ADR-0054, Proposed) | A `dag` is acyclic, a `mesh` carries a budget (`mechanism/GAPS-AND-ASSUMPTIONS.md` I49) |
| Seats, kinds and domains | The issued rules | `rules::validate_issuance` (I8) |
| The request's type | Schema S | Enforced on every request (ADR-0030 §4) |

The same shape fits state-transition tables, routing and topology, resource limits and timeouts, wire formats
generated from a schema, and feature flags. None of those is proposed here.

It stops paying in three cases.

- **The configuration becomes a program.** Once it has loops or computed values, the mechanism is an interpreter
  and the configuration needs a semantics of its own, which is the original problem again.
- **The configuration can add as well as subtract.** A proof for every well-formed input is cheap when a bad input
  can only refuse more. If a value can widen authority, the proof must reason about its content. The values file
  treats relaxing and tightening differently for this reason.
- **Proof and deployment name different inputs.** ADR-0053 finding 6 again, and the exposure grows with each
  external file.

## 3. Typing and bounding the vocabulary

This is externalization that works earlier than policy does.

- **Malformed inputs stop being cases.** Once a value is parsed into a type that holds only valid values, no code
  downstream checks it and no proof considers it.
- **A closed vocabulary makes checks exhaustive.** A compiler can check a pattern match for completeness, and a
  model checker can enumerate every variant. ADR-0030 §4 maps Cedar's action to Build's six variants or Run's typed
  alphabet, "finite in variants".
- **It gives proofs their domain.** The floor's analyses "quantify over all requests and all entity stores
  satisfying schema S." The tighter S is, the smaller that set.
- **It moves authority into the vocabulary.** A seat's kind bounds the alphabet a grant may issue (ADR-0037 §2,
  §4; I8). That an observer cannot author is then a fact about which values exist, not a rule evaluated per
  request.

One sentence of the chat answer is narrowed here. It said the analyses are decidable because S is finite and
bounded. The schema gives the analyses their domain and their types. Decidability comes from the floor language's
restrictions, which is why ADR-0030 §2 writes "a decidable comparison of two policy sets ... over a declared
schema" as an obligation on the floor's evaluator and not on the schema.

Where typing stops:

- **A type describes one value at one moment.** Ordering, freshness, one live lease per principal and what a round
  has already read are relations across time. "History enters S only so: as one of a fixed, named set of
  attributes the mechanism defines" (ADR-0030 §4, A2).
- **The boundary has to be enforced where decisions are made.** "Build-time use of S is not sufficient"; an input
  that does not conform is a deny (ADR-0030 §4, by ADR-0018's validator).
- **The enforcer joins the trusted code.** ADR-0030 carried decoder–alphabet compatibility on its face as a debt
  at ratification (its History, B6).
- **The schema is one more thing to keep in step.** "S changes only with a mechanism release", and an analysis is
  evidence only for the version it names.

## 4. Validation by policy

`policies/tool_schema.rego` is data validation written as policy. It refuses a tool call with a missing required
input, an unknown input, a wrong type, a handle the input does not accept, or an entry of the other domain, each
with a named reason for the decision log. The schema it checks against is data inside the signed bundle.

Policy suits validation for three reasons.

- **Validation is refusal, and a bundle can only refuse.** Under `admit ⟺ floor_permit ∧ ¬bundle_deny` a
  validation rule cannot widen anything. A wrong one over-denies, which ADR-0030 §1 calls "a modeled, attributed
  local event".
- **It changes without a release.** A new tool digest needs a new allowlist entry, not new mechanism code.
- **It can use context a type cannot.** Whether an input accepts a handle depends on the entry, the tool and the
  round's labels together.

| Tier | What it validates well | Its limit |
|---|---|---|
| **Schema S**, in the mechanism | The shape and type of the request | It must come before policy: a policy cannot judge what does not parse |
| **Floor**, Cedar | What the gates can analyse over S | Only facts the lift supplies; and a `forbid` that errors is skipped, so any floor error is a deny (§1) |
| **Bundle**, Rego | Per-tool and per-deployment input checks | Nothing is proved of its text, so no theorem may rest on it |

Three things policy cannot validate.

- **Itself.** A bundle's allowlist is checked by the mechanism at load, "and a bundle cannot waive" the checks
  (ADR-0030 A2).
- **A fact about the request it was not given.** The bundle tier may not re-fetch; "a rule that needs one gets it
  through the lift, which then supplies it to both tiers" (ADR-0030 §4).
- **Anything that is not a request-time fact.** Whether a tool opens the channel it declares "is a fact about the
  tool, not the request" (`mechanism/GAPS-AND-ASSUMPTIONS.md` finding 14).

## 5. Where each kind of fact lives

The four answers give one sorting. It is the drafter's summary and no record states it in this form.

| Kind of fact | Where it lives | What it costs the refinement |
|---|---|---|
| **Shape and range** of one value | Schema S and the typed alphabet | Nothing per request; the validator and decoder as trusted code |
| **Context**: this request against tables and the current store | Floor for what must be proved, bundle for what need only refuse | The engine row (T-0045-3) and the lift |
| **Well-formedness of configuration** | A load check that is a mechanism constant | One check per kind of file, proved or tested once |
| **History and order** | The state machine | The whole of T-0045-28 |

The first three rows are what externalization reaches. The fourth is what §1 is about: it is made cheaper only by
how the state machine is written.

## 6. What follows

Nothing here asks for a record. Two observations:

- **The refactors that would make `State::apply` translatable are known and small in number**: the four `dyn Fn`
  parameters, the labelled break, and a decision on the collections. The 11.04 options document carries them.
- **Each new external file should arrive with its load check and its digest in the decision record.** The five
  rows of §2's table each have the first; whether each has the second was not checked for this document.
