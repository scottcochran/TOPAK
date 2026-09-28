# Security Policy

## What this repository is

TOPAK is a design corpus: architecture decision records, TLA+ specifications
and model-checker results, a draft Cedar policy floor, Rego bundle policies,
diagrams, and a reference implementation of the admit path. It is in its
genesis phase.

**Nothing here is deployable.** There is no release, no packaged artifact, no
service, and no supported configuration. The reference implementation under
`mechanism/` exists to check that the design is buildable and that the
specifications say what we think they say. Its own
[gaps and assumptions](mechanism/GAPS-AND-ASSUMPTIONS.md) list what it does
not do. Do not run it against anything you care about.

Because the repository is design only, the usual notion of a security
vulnerability (an exploitable defect in software people are running) mostly
does not apply. What can go wrong here is different, and more important.

## What we most want to hear about: safety findings

The corpus makes safety claims. It states guarantees against an agent's action
alphabet, treats every agent as Byzantine, and argues that models stay out of
the trusted computing base. If any of those claims is wrong, an implementer
who trusts the corpus inherits the flaw.

A **safety finding** is any of the following:

- A guarantee stated in a checkpoint, the Theory of Operation, or an ADR that
  the specification does not actually establish, or that a TLC run does not
  actually check.
- A TLA+ specification whose invariants or fairness assumptions are weaker
  than the prose claims, or whose model configuration excludes the states
  that matter.
- A Cedar floor or Rego bundle policy that admits an action the design says
  is denied, or that can be bypassed by a request the tests do not cover.
- A confinement, lease, break-glass, or anchor argument with a gap: a step
  that assumes an honest agent, a trusted model output, or a channel the
  design says is untrusted.
- A place where the reference implementation diverges from the specification
  in a way that a reader would not notice from the documents.
- An inconsistency between documents where the state of record
  (the latest genesis checkpoint) and another document disagree on a
  safety-relevant point.

These are the findings we treat as security reports. They get the same
private handling, the same acknowledgement window, and the same credit as a
conventional vulnerability would in a shipping project.

Conventional software defects in the reference implementation, tooling, or
scripts are welcome too. Unless they bear on a safety claim, please open an
ordinary issue for them.

## How to report

Please do not open a public issue for a safety finding until we have had a
chance to look at it. A wrong safety claim that is publicly known but not yet
corrected is the worst state for the corpus to be in.

1. **Preferred:** use GitHub's private vulnerability reporting for this
   repository (the "Report a vulnerability" button under the Security tab).
   This opens a private advisory thread that only you and the maintainer can
   see.
2. **Fallback:** email **topak.security@gmail.com**. Encrypted mail
   is available on request; ask for a key in your first message.

In either channel, please include:

- Which document, specification, policy, or source file the finding is
  against, with the digest manifest (`SHA256SUMS-*`) or commit it was read at.
- The claim you believe is wrong, quoted or closely paraphrased.
- Why it is wrong: a counterexample trace, a failing TLC configuration, a
  policy request that should be denied and is not, or a written argument.
- Whether you believe the fix is to the claim, to the specification, or to
  the implementation.

## What to expect

- Acknowledgement within **5 business days**.
- An initial assessment (agree, disagree, need more) within **15 business
  days** of acknowledgement.
- If the finding is confirmed, it will be recorded in a decision record or
  checkpoint amendment, the affected documents will be corrected, and the
  digest manifests will be re-cut. You will be credited unless you ask not
  to be.
- If we disagree, you will get a written reason. You are free to publish
  after the assessment window closes, whatever the outcome. We ask that you
  link the decision record if one exists.

This is a single-maintainer project. The windows above are what can be met
honestly, not aspirations.

## Scope

In scope: everything tracked in this repository at the current default branch
and at any tagged checkpoint.

Out of scope: third-party reference material (not part of this repository,
see [NOTICE](NOTICE)); the upstream tools the design uses at its reference
