// PROPOSED · built by floor/proposed/build.py from the genesis floor · stage: emergency · not ratified,
// and not what the reference follows. Edit build.py, not this file.
// TOPAK genesis policy floor (ADR-0030).
// DRAFT · 2026.09.24, revised 2026.09.29 (ADR-0040, ADR-0041) · not ratified · schema: genesis.cedarschema
//
// The floor is an upper bound, not the policy. It states what the system may NEVER exceed;
// fine-grained rules belong in the bundle tier, which can only subtract (ADR-0030 §1).
// Every permit below is an envelope from a ratified record; every forbid is a carve-out that
// the permits alone would not make, so each one discriminates (ADR-0030 §5).
//
// Not in the floor, and why:
//   - epoch fencing        — the mechanism, ahead of the floor (ADR-0022 §2)
//   - round bound          — a count; mechanism-checked (ADR-0022 §3)
//   - the rules floor      — bounds issuances, not admits (ADR-0030 §7)
//   - Invoke hermeticity   — an obligation on each allowlist entry, not a request property
//
// Evaluation: any satisfied forbid denies; else any satisfied permit allows; else deny.
// The mechanism treats ANY evaluation error as a deny (ADR-0030 §1), because Cedar skips a
// policy that errors and a skipped forbid would otherwise let a permit through.

// ============================================================================================
// Build envelopes — ADR-0022 §1
// ============================================================================================

@id("B1-read-corpus")
permit (principal, action == Topak::Action::"Read", resource)
when {
  principal.domain == "build" &&
  context.lease.alphabet.contains("Read") &&
  resource in context.corpusRoot
};

@id("B2-draft-workspace")
permit (principal, action == Topak::Action::"Draft", resource)
when {
  principal.domain == "build" &&
  context.lease.alphabet.contains("Draft") &&
  resource in context.workspace
};

@id("B3-invoke-allowlisted")
permit (principal, action == Topak::Action::"Invoke", resource)
when {
  principal.domain == "build" &&
  context.lease.alphabet.contains("Invoke") &&
  resource in context.toolAllowlist &&
  context.inputsInWorkspace
};

@id("B4-emit-own-topic")
permit (principal, action == Topak::Action::"Emit", resource)
when {
  principal.domain == "build" &&
  context.lease.alphabet.contains("Emit") &&
  resource.owner == principal &&
  resource.epoch == context.epoch &&
  resource.round == context.round &&
  !resource.sealed
};

@id("B5-submit-own-artifact")
permit (principal, action == Topak::Action::"Submit", resource)
when {
  principal.domain == "build" &&
  context.lease.alphabet.contains("Submit") &&
  resource.author == principal
};

// ADR-0037 §4: a vote is permitted from the grant roster only for a `grant` seat and from the veto
// roster only for an `observer` seat. A roster issued with the wrong kind of seat on it cannot vote.
@id("B6-vote-seated")
permit (principal, action == Topak::Action::"Vote", resource)
when {
  principal.domain == "build" &&
  context.lease.alphabet.contains("Vote") &&
  context.voteRulesEpoch == context.rulesEpoch &&
  ((principal in context.grantRoster && principal.kind == "grant") ||
   (principal in context.vetoRoster && principal.kind == "observer"))
};

// ---- carve-outs on the Build envelopes ------------------------------------------------------

// ADR-0022 §7, ADR-0024 §6: the author is recused. A mechanism constant, stated in the floor;
// relaxing it is a floor relaxation shipped as a mechanism release.
@id("B7-author-recused")
forbid (principal, action == Topak::Action::"Vote", resource)
when { resource.author == principal };

// ADR-0024 §5: a veto seat's alphabet lacks grant.
@id("B8-grant-only-from-grant-seat")
forbid (principal, action == Topak::Action::"Vote", resource)
when { context.verdict == "grant" && !(principal in context.grantRoster) };

// ADR-0022 §7: within a promotion round, voters review; they do not author.
@id("B9-voters-do-not-author")
forbid (
  principal,
  action in [Topak::Action::"Draft", Topak::Action::"Invoke", Topak::Action::"Submit"],
  resource
)
when { context.roundRole == "voter" };

// ADR-0037 §4: only a `thinker` seat holds a variant that writes, runs or offers. An Observer or a
// grant seat never authors, in either domain; a Reader with Draft authority cannot arise.
@id("B10-only-thinkers-author")
forbid (
  principal,
  action in [Topak::Action::"Draft", Topak::Action::"Invoke", Topak::Action::"Submit", Topak::Action::"Actuate"],
  resource
)
// ADR-0052 §1: an `emergency` seat, held by a person for one round, may Actuate and nothing else here.
when {
  principal.kind != "thinker" &&
  !(principal.kind == "emergency" && action == Topak::Action::"Actuate")
};

// ============================================================================================
// Run envelopes — ADR-0040 §1, stated as ADR-0041 §1 (both Proposed)
// ============================================================================================

@id("R1-actuate-allowlisted")
permit (principal, action == Topak::Action::"Actuate", resource)
when {
  principal.domain == "run" &&
  context.lease.alphabet.contains("Actuate") &&
  resource in context.toolAllowlist
};

@id("R2-report-own-topic")
permit (principal, action == Topak::Action::"Report", resource)
when {
  principal.domain == "run" &&
  context.lease.alphabet.contains("Report") &&
  resource.owner == principal &&
  resource.epoch == context.epoch &&
  resource.round == context.round &&
  !resource.sealed
};

// ADR-0040 §1: `Consult` resolves a content-addressed object inside the pinned Run root. It is
// ingress, not an effect. A read of anything live is an `Actuate` of a tool, never a `Consult`.
@id("R4-consult-pinned")
permit (principal, action == Topak::Action::"Consult", resource)
when {
  principal.domain == "run" &&
  context.lease.alphabet.contains("Consult") &&
  resource in context.runRoot
};

// ADR-0039 §2, as ADR-0041 §2 reads it: every *effect-bearing* Run admit under a Thinker's lease
// needs a live cell Observer. `Consult` is not named: it emits nothing, nothing crosses outward,
// and what was read can be reconstructed from the digest. The exemption rests on R4's pinning;
// the gate run carries a control that a floor without it is classed a relaxation. `observerLive`
// is the lift's `live(o)`: a live Observer lease, a heartbeat within T_obs on the mechanism's clock,
// and a watermark within K of the Thinker's sequence (`genesis-values.json`). Deny-only, and it
// applies to break-glass too: a dead, partitioned or starved Observer stops its own cell and nothing
// else. An observer seat's own emissions, its heartbeats among them, are not coupled: nothing
// watches the watcher's liveness but the Thinker it stalls.
@id("R3-observer-live")
forbid (principal, action in [Topak::Action::"Actuate", Topak::Action::"Report"], resource)
when { principal.kind == "thinker" && !context.observerLive };

// ---- carve-outs on Run's effects by label — ADR-0047 §7 (F1 to F3), named by ADR-0041 A1 ---------
// Each is a set-membership test on attributes the mechanism computed. `untrusted` and `restricted`
// are the two names the floor reserves. `outward` is derived, never declared. They are forbids, so
// they deny whatever permit is satisfied, a break-glass permit included.

// F1, read then send: a principal that has read untrusted content in the clear makes an outward
// call while holding restricted content, read in the clear or passed by handle.
@id("R5-no-read-then-send")
forbid (principal, action == Topak::Action::"Actuate", resource)
when {
  resource.outward &&
  context.clearSet.contains("untrusted") &&
  (context.clearSet.contains("restricted") || context.inputLabels.contains("restricted"))
};

// F2, steered destination: a principal that has read untrusted content in the clear types the
// destination of an outward call. A literal carries anything the principal has read.
@id("R6-no-steered-destination")
forbid (principal, action == Topak::Action::"Actuate", resource)
when {
  resource.outward &&
  context.clearSet.contains("untrusted") &&
  context.destLiteral
};

// F3, replayed content: the destination of an outward call is a handle to untrusted content,
// whatever the principal has read.
@id("R7-no-replayed-destination")
forbid (principal, action == Topak::Action::"Actuate", resource)
when {
  resource.outward &&
  context.destLabels.contains("untrusted")
};

// ============================================================================================
// Floor exceptions — ADR-0013 §2. Count: 1, bounded by ADR-0026 R6.
// ============================================================================================

// X1 break-glass is retired (ADR-0052 §2). Break-glass is an emergency seating: the break-glass
// roster's quorum seats a named person on a seat of kind `emergency` for one round, and that seat's
// calls are admitted by R1 over an envelope computed at activation.

// X2 erasure (ADR-0006). Destroys evidence, so it lives in the floor, not a bundle. Authorized
// only by a quorum on the erasure roster; genesis rules issue no erasure roster (ADR-0029 §5),
// so `erasureQuorum` is FALSE from epoch 0 and this entry admits nothing until bootstrap.
@id("X2-erasure")
permit (principal, action == Topak::Action::"Erase", resource)
when { context.erasureQuorum };

// ============================================================================================
// The forensic floor — ADR-0028. Each class is a denial on the erasure envelope.
// Removing a class is a floor relaxation.
// ============================================================================================

@id("F-forensic-classes")
forbid (principal, action == Topak::Action::"Erase", resource)
when { ["F1", "F2", "F3", "F4", "F5", "F6"].contains(resource.class) };

// ============================================================================================
// The control entries — ADR-0050 §4, named by ADR-0041 A3. An `operator` seat's requests.
// A first lease is not here: the mechanism grants one when a quorum completes (ADR-0050 §2).
// ============================================================================================

// A successor grant: the target's next round, with nothing wider. The binding and the round are
// compared by the lift; the alphabet is compared here.
@id("C1-regrant-successor")
permit (principal, action == Topak::Action::"Regrant", resource)
when {
  principal.kind == "operator" &&
  resource.domain == principal.domain &&
  context.targetSeated &&
  !context.targetLive &&
  context.sameBinding &&
  context.nextRound &&
  context.lastAlphabet.containsAll(context.newAlphabet)
};

@id("C2-renew")
permit (principal, action == Topak::Action::"Renew", resource)
when {
  principal.kind == "operator" &&
  resource.domain == principal.domain &&
  context.targetLive
};

@id("C3-attest-gates")
permit (principal, action == Topak::Action::"AttestGates", resource)
when { principal.kind == "operator" && principal.domain == "build" };

// A deny needs no lease: a Persona in force, and a credential that is fresh, by the lease or by a
// sign-on assertion (ADR-0050 §4, R1).
@id("C4-deny")
permit (
  principal,
  action in [Topak::Action::"EndRound", Topak::Action::"Revoke", Topak::Action::"FenceEpoch"],
  resource
)
when {
  principal.kind == "operator" &&
  context.personaInForce &&
  (context.hasLease || context.freshAssertion)
};

// An add needs a live lease and a live peer.
@id("C5-add-needs-lease-and-peer")
forbid (
  principal,
  action in [Topak::Action::"Regrant", Topak::Action::"Renew", Topak::Action::"AttestGates"],
  resource
)
when { !context.hasLease || !context.peerLive };

@id("C6-no-self")
forbid (principal, action in [Topak::Action::"Regrant", Topak::Action::"Renew"], resource)
when { resource == principal };

// The fleet fence is the one deny that needs a live lease (ADR-0050 §4, R5).
@id("C7-fence-needs-lease")
forbid (principal, action == Topak::Action::"FenceEpoch", resource)
when { !context.hasLease };

// The round's task carries a label, and one its seating allows (ADR-0047 §1, R9; ADR-0050 §5).
@id("C8-task-label-in-bounds")
forbid (principal, action == Topak::Action::"Regrant", resource)
when { !context.taskLabelled || !context.taskLabelsAllowed.containsAll(context.taskLabel) };

// An operator ends rounds and revokes in its own domain. Across domains the tool is the fence.
@id("C9-stop-in-own-domain")
forbid (principal, action in [Topak::Action::"EndRound", Topak::Action::"Revoke"], resource)
when { resource.domain != principal.domain };
