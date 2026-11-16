# Findings and the report

## What counts

A finding is a thing the run showed that someone would do differently knowing it. Each states what happened, with numbers from the
trace, why it follows from the configuration or a record, and what would change it. Sort them by what they would cost.

| Against | Example | Where it goes |
|---|---|---|
| The configuration | The mesh cannot deliver overlapping relief | The simulation's README, with the fix offered |
| A record | No record says what a body does between a lease and its successor | The README, as a lead for the custodian |
| The reference | `policies/*.rego` traps under `opa-wasm` on a refusal | The README. A code change is a separate request |

A finding is never applied to a record here. The custodian reads it and decides.

## Patterns to look for

The six recon-7 findings, as questions for any use case:

| Pattern | Ask of your run |
|---|---|
| One outcome per round | Does the plan need the next round before this one ends? Each relief there left about 20 minutes uncovered against 30 of planned overlap |
| An edge needs a seal | When a body or host is lost, does anything fire? A spare sat on the ground for 3 h 20 min |
| Chains through one principal | If one round is revoked, what else never happens? One revocation ended a sector for the rest of the mission |
| Rules that interact with delivery | Does a label delivered as routine make a permitted action impossible? ROE-11 nearly disabled SAR, because a routine peer report labels every stack |
| Accounting that needs a seal | What is never released? A destroyed vehicle's charge stayed against `K_up` for good |
| Undefined gaps between records | What did you have to assume? Each item in `assumptions` is a candidate, like the 4-tick wait for a successor |
| A limit on what the stack asks | Does any rule tie the requested value to the facts? A workflow's attributes do not reach a bundle, so a limit on an amount bounds only the claim made |
| Completion is not success | A refused effect can still end the round and complete the workflow. Who finds out? |
| A seat is a key | What can a stolen seat do inside every rule? The run should measure it |
| Nobody answers | A person's absence fails a decision when its lease ends. Does anything queue, retry or hand off? |

Also confirm what was declared. "`K_up` stopped a cut-off plane after 3 h 10 min, against about 3 to 4 hours declared" is a result
too. Confirmation only counts where it could have come out otherwise.

## The simulation's README

Use `assets/simulation-README.md`: what is real against what is modelled, the assumptions, a table of what happened with ticks and times,
the findings, and the replay commands. Every number comes from `--summary`, `--timeline` or `--explain`.

## The closing message

For someone who knows TOPAK and did not watch the run:

1. **First, what is modelled**, and any assumption the result leans on.
2. **What happened**: did the use case get what it was for, measured. Refusals and invariants.
3. **What was verified**: each of the four checks and its result.
4. **Corrections**: any claim in the configuration that the run disproved, stated plainly.
5. **Findings**, ordered by cost.
6. **What is uncommitted**, and the one decision that is theirs, usually whether to apply a fix and re-run.

Point to the README and the replay commands. Do not paste the timeline.
