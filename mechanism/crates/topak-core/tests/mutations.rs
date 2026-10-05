//! The TLA+ checks, restated against the Rust mechanism.
//!
//! Each property from `spec/Lease.tla`, `spec/FloorComposition.tla` and
//! `spec/RulesFloorNV_rev5.tla` gets a test that the implementation keeps it, and a test that
//! the corresponding mutation — or the state the mutation would admit — is refused. A property
//! that no test could break would be vacuous (the corpus's mutation discipline).

use std::collections::{BTreeMap, BTreeSet};

use serde_json::Value;
use topak_core::action::{Action, ActionRequest};
use topak_core::admit::*;
use topak_core::lease::{Confinement, Lease};
use topak_core::lift::{inputs_in_workspace, workspace_relative};
use topak_core::promotion::{Candidate, Tally, VoteRecord, tally};
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::*;

fn seat(d: Domain, kind: SeatKind, key: &str) -> SeatDecl {
    SeatDecl { domain: d, kind, cell: None, key: key.into(), rung: 0 }
}

fn cell_observer(d: Domain, cell: &str, key: &str) -> SeatDecl {
    SeatDecl { domain: d, kind: SeatKind::Observer, cell: Some(cell.into()), key: key.into(), rung: 0 }
}

fn rules() -> Rules {
    Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats: BTreeMap::from([
            ("a1".into(), seat(Domain::Build, SeatKind::Thinker, "ka1")),
            ("g1".into(), seat(Domain::Build, SeatKind::Grant, "kg1")),
            ("g2".into(), seat(Domain::Build, SeatKind::Grant, "kg2")),
            ("g3".into(), seat(Domain::Build, SeatKind::Grant, "kg3")),
            ("o1".into(), cell_observer(Domain::Build, "a1", "ko1")),
            ("r1".into(), seat(Domain::Run, SeatKind::Thinker, "kr1")),
        ]),
        grant_roster: ["a1", "g1", "g2", "g3"].into_iter().map(String::from).collect(),
        veto_roster: BTreeSet::from(["o1".into()]),
        anchor_keys: BTreeSet::from(["kA".into(), "kB".into(), "kC".into()]),
        break_glass: None,
        erasure_roster: None,
        verifier_keys: BTreeSet::new(),
        bundle_keys: BTreeSet::new(),
        inside_targets: BTreeSet::new(),
        releasers: BTreeSet::new(),
        personas: BTreeMap::new(),
        criterion: None,
    }
}

fn params() -> Params {
    Params {
        corpus: BTreeSet::new(),
        build_tools: BTreeSet::new(),
        run_tools: BTreeSet::new(),
        run_root: BTreeSet::new(),
        wasm_tools: BTreeSet::new(),
        round_bound: 3,
        lease_margin_ms: 0,
        after_topic_limit: 3,
        run_round_bound: None,
    }
}

fn grant_req(seat: &str, alphabet: &[ActionKind]) -> GrantRequest {
    GrantRequest {
        principal: format!("p-{seat}"),
        seat: seat.into(),
        persona: Digest::of(b"persona"),
        bundle: Digest::of(b"bundle"),
        // Rung 0: a grant at rung 1 or above rests on an appraisal (`tests/confinement.rs`).
        confinement: Confinement { digest: Digest::of(b"profile"), rung: 0 },
        alphabet: alphabet.iter().copied().collect(),
        ttl_ms: 1000,
        round: 1,
        role: RoundRole::Author,
        task_label: None,
    }
}

fn state() -> State {
    let mut s = State::genesis(rules(), 2).unwrap();
    s.trace = topak_core::trace::name_from_env("mut");
    s
}

fn read(seat: &str, lease: LogIndex, epoch: Epoch) -> ActionRequest {
    ActionRequest { seat: seat.into(), lease, epoch, action: Action::Read { object: Digest::of(b"x") } }
}

// ---- Lease.tla ------------------------------------------------------------------------------

#[test]
fn lease_renewal_is_monotone_and_m_renew_is_refused() {
    let p = params();
    let mut s = state();
    assert_eq!(
        s.apply(
            1,
            &Entry::Grant {
                id: "g".into(),
                req: grant_req("a1", &[ActionKind::Read, ActionKind::Emit]),
                appraisal: None
            },
            &p
        ),
        Applied::LeaseGranted { fence: 1 }
    );
    let renew = |alphabet: &[ActionKind], rung, ttl| RenewRequest {
        seat: "a1".into(),
        fence: 1,
        alphabet: alphabet.iter().copied().collect(),
        rung,
        ttl_ms: ttl,
    };

    // M_RENEW: every widening is refused, a higher rung among them.
    for (i, r) in [
        renew(&[ActionKind::Read, ActionKind::Emit, ActionKind::Draft], 0, 1000),
        renew(&[ActionKind::Read], 1, 1000),
        renew(&[ActionKind::Read], 0, 2000),
    ]
    .into_iter()
    .enumerate()
    {
        let a = s.apply(10 + i as u64, &Entry::Renew { id: format!("w{i}"), req: r, appraisal: None }, &p);
        assert!(matches!(a, Applied::Rejected(_)), "widening {i} accepted: {a:?}");
    }
    // Lease_A1.tla `M_LOWER` (a lower rung) needs a lease above rung 0, which needs an appraisal:
    // `tests/confinement.rs` `m_lower_and_m_renewlow_are_refused`.
    assert_eq!(s.live_by_seat["a1"], 1, "a refused renewal leaves the lease as it was");
    // Narrowing is accepted at the same rung, at a new fence, and the old lease stops being live.
    let a = s.apply(20, &Entry::Renew { id: "n".into(), req: renew(&[ActionKind::Read], 0, 500), appraisal: None }, &p);
    assert_eq!(a, Applied::Renewed { fence: 20 });
    assert_eq!(s.live_by_seat["a1"], 20);
    assert!(s.check_live(&read("a1", 1, 0), &p).is_err());
    assert!(s.check_live(&read("a1", 20, 0), &p).is_ok());
}

#[test]
fn renewal_cannot_swap_the_bundle() {
    let old = Lease {
        principal: "p".into(),
        seat: "a1".into(),
        persona: Digest::of(b"p"),
        epoch: 0,
        fence: 1,
        rules_epoch: 0,
        bundle: Digest::of(b"b1"),
        confinement: Confinement { digest: Digest::of(b"c"), rung: 1 },
        alphabet: BTreeSet::from([ActionKind::Read]),
        round: 1,
        role: RoundRole::Voter,
        ttl_ms: 10,
    };
    let mut new = old.clone();
    new.bundle = Digest::of(b"b2");
    assert!(old.check_renewal(&new).is_err(), "ADR-0031 R2: renewal keeps the bundle, so a swap is refused");
}

/// Lease.tla `M_ROLE`: round and role are lease fields (ADR-0031 R1), fixed across renewal. A
/// voter renewed as an author would gain `Draft` under the floor's role rule without a grant.
#[test]
fn renewal_cannot_change_round_or_role_and_m_role_is_refused() {
    let p = params();
    let mut s = state();
    let mut req = grant_req("a1", &[ActionKind::Read]);
    req.role = RoundRole::Voter;
    s.apply(1, &Entry::Grant { id: "g".into(), req, appraisal: None }, &p);
    let old = s.leases[&1].lease.clone();
    assert_eq!((old.round, old.role), (1, RoundRole::Voter), "the grant's round and role are in the lease");

    let mut as_author = old.clone();
    as_author.role = RoundRole::Author;
    assert!(old.check_renewal(&as_author).is_err(), "M_ROLE: a renewal changed the role");
    let mut next_round = old.clone();
    next_round.round = 2;
    assert!(old.check_renewal(&next_round).is_err(), "a renewal moved the lease to another round");
    assert!(old.check_renewal(&old.clone()).is_ok(), "reachability: an unchanged renewal is accepted");
}

/// ADR-0031 C1, the finding the check bought: a grant must not replace a live lease, or §4's
/// monotonicity is bypassed by never renewing.
#[test]
fn one_live_lease_per_principal() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g1".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None }, &p);
    let mut wide = grant_req("a1", &[ActionKind::Read, ActionKind::Draft, ActionKind::Invoke]);
    wide.round = 2;
    let a = s.apply(2, &Entry::Grant { id: "g2".into(), req: wide, appraisal: None }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("live lease")), "{a:?}");
}

#[test]
fn no_action_under_a_fenced_epoch_and_m_fence_is_refused() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None }, &p);
    assert!(s.check_live(&read("a1", 1, 0), &p).is_ok(), "reachability: an action is admissible");
    s.apply(2, &Entry::EpochIncrement { id: "e".into(), reason: "revoke".into(), attribution: "t".into() }, &p);
    // The fence is checked first, so the reason is the fence, not the lease's end.
    assert_eq!(s.check_live(&read("a1", 1, 0), &p).unwrap_err(), MechanismDeny::FencedEpoch { lease: 0, current: 1 });
    // A request that claims the current epoch under the stale lease is refused as well.
    assert!(s.check_live(&read("a1", 1, 1), &p).is_err());
}

/// Finding 5, ADR-0031 R3: a targeted revocation ends the matching principal's lease and leaves
/// every other lease live at the same epoch (`Lease.tla` `NeverSelectiveRevoke`, reachable).
#[test]
fn a_targeted_revocation_ends_one_round_and_not_the_fleet() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g1".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None }, &p);
    let mut other = grant_req("g1", &[ActionKind::Read]);
    other.persona = Digest::of(b"another persona");
    s.apply(2, &Entry::Grant { id: "g2".into(), req: other, appraisal: None }, &p);
    s.break_glass.entry("a1".into()).or_default().entry(0).or_default().insert("kA".into());

    let revoke = Entry::Revoke {
        id: "r".into(),
        target: RevocationTarget::Persona(Digest::of(b"persona")),
        reason: "persona revoked".into(),
        attribution: "t".into(),
    };
    assert_eq!(s.apply(3, &revoke, &p), Applied::Revoked { ended: 1 });
    assert_eq!(s.check_live(&read("a1", 1, 0), &p).unwrap_err(), MechanismDeny::LeaseEnded(EndReason::Revoked));
    assert!(s.check_live(&read("g1", 2, 0), &p).is_ok(), "another principal's round survives");
    assert_eq!(s.epoch, 0, "the epoch is untouched");
    assert!(!s.break_glass.contains_key("a1"), "break-glass approvals lapse with the revoked lease");
}

/// `Lease.tla` `M_REVOKE`: every target kind bars a later grant that it matches.
#[test]
fn a_revoked_principal_persona_or_profile_is_not_granted_again_and_m_revoke_is_refused() {
    let p = params();
    for (i, target) in [
        RevocationTarget::Principal("p-a1".into()),
        RevocationTarget::Persona(Digest::of(b"persona")),
        RevocationTarget::Confinement(Digest::of(b"profile")),
    ]
    .into_iter()
    .enumerate()
    {
        let mut s = state();
        let r = Entry::Revoke { id: "r".into(), target, reason: "t".into(), attribution: "t".into() };
        assert_eq!(s.apply(1, &r, &p), Applied::Revoked { ended: 0 }, "a revocation needs no live lease");
        let a = s.apply(
            2,
            &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None },
            &p,
        );
        assert!(matches!(a, Applied::Rejected(ref m) if m.contains("revoked")), "target {i} re-granted: {a:?}");
        // Reachability: a principal the target does not match is still granted.
        let mut other = grant_req("g1", &[ActionKind::Read]);
        other.principal = "p-other".into();
        other.persona = Digest::of(b"another persona");
        other.confinement.digest = Digest::of(b"another profile");
        assert_eq!(
            s.apply(3, &Entry::Grant { id: "o".into(), req: other, appraisal: None }, &p),
            Applied::LeaseGranted { fence: 3 }
        );
    }
}

/// ADR-0030 §1 R4 (ADR-0033 finding 10): every floor deny names its reason. A deny with no
/// determining forbid is `FloorNoPermit`, not an empty list.
#[test]
fn every_floor_deny_names_a_reason() {
    let none = FloorOutcome::Deny { reasons: vec![] };
    assert_eq!(floor_gate(&none), Some(DenyReason::FloorNoPermit));
    let forbid = FloorOutcome::Deny { reasons: vec!["B7-author-recused".into()] };
    assert_eq!(floor_gate(&forbid), Some(DenyReason::Floor(vec!["B7-author-recused".into()])));
    assert_eq!(floor_gate(&FloorOutcome::Permit { reasons: vec![] }), None);
}

/// ADR-0034 §4 as a lookup: rung 0 is `Mediated`, always, and says why. The conjuncts above
/// rung 0 are `tests/confinement.rs`.
#[test]
fn rung_zero_is_never_contained_and_says_why() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None }, &p);
    let c = s.contained(1);
    assert!(!c.contained);
    assert!(c.because.iter().any(|r| r.contains("rung 0")), "{c:?}");
    assert!(c.because.iter().any(|r| r.contains("criterion")), "{c:?}");
    assert!(!s.contained(99).contained, "no lease is not contained");
}

#[test]
fn the_round_bound_terminates_a_round() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None }, &p);
    for i in 0..p.round_bound {
        s.leases.get_mut(&1).unwrap().actions = i;
        assert!(s.check_live(&read("a1", 1, 0), &p).is_ok());
    }
    s.leases.get_mut(&1).unwrap().actions = p.round_bound;
    assert_eq!(s.check_live(&read("a1", 1, 0), &p).unwrap_err(), MechanismDeny::RoundBoundReached(3));
}

// ---- FloorComposition.tla -------------------------------------------------------------------

fn allow() -> BundleOutcome {
    BundleOutcome::Allow { engine: BundleEngine::LocalWasm, bundle: Digest::of(b"b") }
}

fn refuse() -> BundleOutcome {
    BundleOutcome::Refuse { engine: None, reason: "unreachable".into() }
}

#[test]
fn admit_implies_floor_permit_and_m_override_is_refused() {
    let permit = FloorOutcome::Permit { reasons: vec!["B1".into()] };
    let deny = FloorOutcome::Deny { reasons: vec![] };
    let error = FloorOutcome::Error { diagnostics: vec!["skipped forbid".into()] };
    assert!(matches!(compose(&permit, &allow()), Decision::Admit { .. }), "reachability: something is admitted");
    // M_OVERRIDE: a bundle allow never admits what the floor did not permit.
    assert!(matches!(compose(&deny, &allow()), Decision::Deny(DenyReason::Floor(_) | DenyReason::FloorNoPermit)));
    // M_ERR: a floor error is a deny, whatever the engine decided.
    assert!(matches!(compose(&error, &allow()), Decision::Deny(DenyReason::FloorError(_))));
}

#[test]
fn bundle_refusal_is_honored_and_m_failopen_is_refused() {
    let permit = FloorOutcome::Permit { reasons: vec!["B1".into()] };
    // Reachability: a bundle narrows what the floor permits.
    assert!(matches!(compose(&permit, &refuse()), Decision::Deny(DenyReason::Bundle(_))));
}

#[test]
fn break_glass_is_recognized_only_when_x1_alone_permits() {
    assert!(via_break_glass(&["X1-break-glass".into()]));
    assert!(!via_break_glass(&["X1-break-glass".into(), "R1-actuate-allowlisted".into()]));
    assert!(!via_break_glass(&["R1-actuate-allowlisted".into()]));
}

// ---- RulesFloorNV_rev5.tla ------------------------------------------------------------------

#[test]
fn genesis_rules_satisfy_the_floor() {
    assert!(check_rules_floor(&rules(), 2).is_empty());
    assert!(check_well_formed(&rules()).is_empty());
}

#[test]
fn every_rules_floor_entry_has_a_violation_it_catches() {
    let entry = |r: &Rules, exc: usize| -> BTreeSet<&'static str> {
        check_rules_floor(r, exc).into_iter().map(|v| v.entry).collect()
    };
    let mut r1 = rules();
    r1.quorum = Quorum::Threshold(3);
    assert_eq!(entry(&r1, 2), BTreeSet::from(["R1"]));

    let mut r2 = rules();
    r2.min_grant = 1;
    assert_eq!(entry(&r2, 2), BTreeSet::from(["R2"]));

    let mut r5 = rules();
    r5.anchor_keys.insert("kg1".into());
    assert_eq!(entry(&r5, 2), BTreeSet::from(["R5"]));

    assert_eq!(entry(&rules(), 3), BTreeSet::from(["R6"]));

    let mut r7 = rules();
    r7.break_glass = Some(BreakGlassRules {
        roster: BTreeSet::from(["kx".into()]),
        quorum: 1,
        tools: BTreeSet::new(),
        actions: BTreeSet::from(["Actuate".into(), "Vote".into()]),
    });
    assert_eq!(entry(&r7, 2), BTreeSet::from(["R7"]));

    // R9 is conditional: it binds only once R1 is relaxed, so it fires alongside R1.
    let mut r9 = rules();
    r9.quorum = Quorum::Threshold(1);
    assert_eq!(entry(&r9, 2), BTreeSet::from(["R1", "R9"]));
}

#[test]
fn quorum_any_is_withdrawn() {
    assert!(serde_json::from_value::<Quorum>(Value::String("any".into())).is_err());
    assert_eq!(serde_json::from_value::<Quorum>(Value::String("all".into())).unwrap(), Quorum::All);
    assert_eq!(serde_json::from_value::<Quorum>(serde_json::json!(3)).unwrap(), Quorum::Threshold(3));
}

#[test]
fn genesis_refuses_floor_violating_rules() {
    let mut r = rules();
    r.min_grant = 0;
    assert!(State::genesis(r, 2).is_err());
}

// ---- ADR-0024 tally --------------------------------------------------------------------------

fn candidate(author: &str, votes: &[(&str, Verdict)], ev: &Digest, re: RulesEpoch) -> Candidate {
    Candidate {
        artifact: Digest::of(b"art"),
        author: author.into(),
        votes: votes
            .iter()
            .map(|(s, v)| (s.to_string(), VoteRecord { verdict: *v, evidence: ev.clone(), rules_epoch: re }))
            .collect(),
        promoted_at: None,
    }
}

#[test]
fn unanimity_over_counted_seats_with_the_author_recused() {
    let ev = Digest::of(b"ev");
    let r = rules();
    let all = [("g1", Verdict::Grant), ("g2", Verdict::Grant), ("g3", Verdict::Grant)];
    assert_eq!(tally(&candidate("a1", &all, &ev, 0), &r, Some(&ev)), Tally::Promoted);
    // The author's own grant is not counted; the three others still must all grant.
    let two = [("a1", Verdict::Grant), ("g1", Verdict::Grant), ("g2", Verdict::Grant)];
    assert!(matches!(tally(&candidate("a1", &two, &ev, 0), &r, Some(&ev)), Tally::Pending { granted: 2, counted: 3 }));
}

#[test]
fn a_timeout_is_never_a_grant() {
    let ev = Digest::of(b"ev");
    let some = [("g1", Verdict::Grant), ("g2", Verdict::Grant)];
    assert!(matches!(tally(&candidate("a1", &some, &ev, 0), &rules(), Some(&ev)), Tally::Pending { .. }));
}

#[test]
fn stale_votes_never_count() {
    let ev = Digest::of(b"ev");
    let all = [("g1", Verdict::Grant), ("g2", Verdict::Grant), ("g3", Verdict::Grant)];
    let mut r = rules();
    r.rules_epoch = 1;
    assert!(matches!(tally(&candidate("a1", &all, &ev, 0), &r, Some(&ev)), Tally::Pending { granted: 0, .. }));
    // Votes bound to other evidence do not count either.
    assert!(matches!(
        tally(&candidate("a1", &all, &ev, 0), &rules(), Some(&Digest::of(b"new"))),
        Tally::Pending { granted: 0, .. }
    ));
}

#[test]
fn veto_deny_denies_and_veto_silence_does_not() {
    let ev = Digest::of(b"ev");
    let mut votes = vec![("g1", Verdict::Grant), ("g2", Verdict::Grant), ("g3", Verdict::Grant)];
    assert_eq!(tally(&candidate("a1", &votes, &ev, 0), &rules(), Some(&ev)), Tally::Promoted);
    votes.push(("o1", Verdict::Deny));
    assert!(matches!(tally(&candidate("a1", &votes, &ev, 0), &rules(), Some(&ev)), Tally::Denied(_)));
}

#[test]
fn no_gate_evidence_no_promotion() {
    let ev = Digest::of(b"ev");
    let all = [("g1", Verdict::Grant), ("g2", Verdict::Grant), ("g3", Verdict::Grant)];
    assert!(matches!(tally(&candidate("a1", &all, &ev, 0), &rules(), None), Tally::Pending { .. }));
}

/// The vacuous-roster failure R2 exists for (ADR-0026 §6, finding 3): without R2 a havoc
/// issuance sets an empty roster and unanimity over the empty set promotes with zero votes.
/// The tally reproduces it — which is exactly why R2 is checked on every issuance.
#[test]
fn without_r2_an_empty_roster_promotes_with_zero_votes() {
    let ev = Digest::of(b"ev");
    let mut r = rules();
    r.grant_roster.clear();
    r.veto_roster.clear();
    r.min_grant = 0;
    assert_eq!(tally(&candidate("a1", &[], &ev, 0), &r, Some(&ev)), Tally::Promoted);
    assert!(check_rules_floor(&r, 2).iter().any(|v| v.entry == "R2"), "and R2 refuses those rules");
}

/// The too-small-model finding (G2 §3): with two counted seats, k ≥ 2 *is* unanimity, so a
/// threshold property means nothing below three counted seats.
#[test]
fn a_threshold_needs_three_counted_seats_to_differ_from_unanimity() {
    let ev = Digest::of(b"ev");
    let mut r = rules();
    r.quorum = Quorum::Threshold(2);
    let two = [("g1", Verdict::Grant), ("g2", Verdict::Grant)];
    assert_eq!(tally(&candidate("a1", &two, &ev, 0), &r, Some(&ev)), Tally::Promoted, "2 of 3 counted seats");
    r.grant_roster = ["a1", "g1", "g2"].into_iter().map(String::from).collect();
    let one = [("g1", Verdict::Grant)];
    assert!(
        matches!(tally(&candidate("a1", &one, &ev, 0), &r, Some(&ev)), Tally::Pending { .. }),
        "2 of 2 is unanimity"
    );
}

// ---- the lift --------------------------------------------------------------------------------

#[test]
fn workspace_paths_are_syntactic_and_fail_closed() {
    assert_eq!(workspace_relative("spec/Lease.tla").as_deref(), Some("spec/Lease.tla"));
    assert_eq!(workspace_relative("./a//b").as_deref(), Some("a/b"));
    for bad in ["", "/etc/passwd", "../x", "a/../../b", "a\\b", "http://x", ".", "a/.."] {
        assert_eq!(workspace_relative(bad), None, "{bad:?}");
    }
    assert!(inputs_in_workspace(&serde_json::json!({ "spec": "Lease.tla", "workers": 4 })));
    assert!(!inputs_in_workspace(&serde_json::json!({ "spec": "/abs" })));
    assert!(!inputs_in_workspace(&serde_json::json!({ "nested": ["ok", "../no"] })));
}

// ---- Seats.tla (ADR-0037) ------------------------------------------------------------------

/// Seats.tla `OnlyThinkersAuthor` / `M_KIND`: the grant path issues nothing outside the kind's
/// bound (ADR-0037 §4), so an observer seat never holds `Draft` and a thinker seat never holds
/// `Vote`. The floor (B10, B6) is the second enforcement; this is the first.
#[test]
fn alphabets_are_bounded_by_seat_kind_and_m_kind_is_refused() {
    let p = params();
    let mut s = state();
    let a = s.apply(
        1,
        &Entry::Grant {
            id: "g1".into(),
            req: grant_req("o1", &[ActionKind::Read, ActionKind::Draft]),
            appraisal: None,
        },
        &p,
    );
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("observer alphabet")), "{a:?}");
    let a = s.apply(
        2,
        &Entry::Grant { id: "g2".into(), req: grant_req("a1", &[ActionKind::Read, ActionKind::Vote]), appraisal: None },
        &p,
    );
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("thinker alphabet")), "{a:?}");
    let a =
        s.apply(3, &Entry::Grant { id: "g3".into(), req: grant_req("g1", &[ActionKind::Submit]), appraisal: None }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("grant alphabet")), "{a:?}");
    // Reachability: each kind is granted what it may hold.
    for (seat, alpha) in [
        ("o1", vec![ActionKind::Read, ActionKind::Emit, ActionKind::Vote]),
        ("a1", vec![ActionKind::Read, ActionKind::Draft]),
        ("g1", vec![ActionKind::Vote]),
    ] {
        let mut req = grant_req(seat, &alpha);
        req.role = if seat == "a1" { RoundRole::Author } else { RoundRole::Voter };
        let a = s.apply(
            10 + seat.len() as u64 + alpha.len() as u64,
            &Entry::Grant { id: format!("ok-{seat}"), req, appraisal: None },
            &p,
        );
        assert!(matches!(a, Applied::LeaseGranted { .. }), "{seat}: {a:?}");
    }
}

/// Seats.tla `OneSeatPerPrincipal` / `M_SEAT`: a principal holds exactly one seat (ADR-0037 §1).
/// Before ADR-0037 the reference keyed the one-live-lease rule by seat only (finding 1), which is
/// exactly M_SEAT: the same principal could be granted a second seat.
#[test]
fn one_seat_per_principal_and_m_seat_is_refused() {
    let p = params();
    let mut s = state();
    let mut first = grant_req("a1", &[ActionKind::Read]);
    first.principal = "p-shared".into();
    assert!(matches!(
        s.apply(1, &Entry::Grant { id: "g1".into(), req: first, appraisal: None }, &p),
        Applied::LeaseGranted { .. }
    ));
    let mut second = grant_req("g1", &[ActionKind::Read]);
    second.principal = "p-shared".into();
    second.role = RoundRole::Voter;
    let a = s.apply(2, &Entry::Grant { id: "g2".into(), req: second, appraisal: None }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("holds a live lease on seat a1")), "M_SEAT: {a:?}");
    // Reachability: another principal takes g1; and after a1's round ends, p-shared may take g1.
    let mut other = grant_req("g1", &[ActionKind::Read]);
    other.principal = "p-other".into();
    other.role = RoundRole::Voter;
    assert!(matches!(
        s.apply(3, &Entry::Grant { id: "g3".into(), req: other, appraisal: None }, &p),
        Applied::LeaseGranted { .. }
    ));
}

// ---- Observers.tla (ADR-0038) --------------------------------------------------------------

/// ADR-0038 §6 / ADR-0024 A2.1: a correlator, an observer seat with no cell, holds a veto seat
/// like a cell Observer. Its `Vote(deny)` denies; its silence is not a veto (ADR-0024 §2). Its
/// `Vote(grant)` is the floor's B8 to refuse, replayed in `floor.rs`.
#[test]
fn a_correlator_on_the_veto_roster_vetoes_and_its_silence_does_not() {
    use topak_core::promotion::{Candidate, Tally, VoteRecord, tally};
    let mut r = rules();
    r.seats.insert("corr".into(), seat(Domain::Build, SeatKind::Observer, "kcorr"));
    r.veto_roster.insert("corr".into());
    assert!(check_well_formed(&r).is_empty(), "{:?}", check_well_formed(&r));
    let ev = Digest::of(b"evidence");
    let vote = |v: Verdict| VoteRecord { verdict: v, evidence: ev.clone(), rules_epoch: 0 };
    let mut votes: BTreeMap<SeatId, VoteRecord> =
        ["g1", "g2", "g3"].into_iter().map(|s| (s.to_string(), vote(Verdict::Grant))).collect();
    let cand = |votes: &BTreeMap<SeatId, VoteRecord>| Candidate {
        artifact: Digest::of(b"art"),
        author: "a1".into(),
        votes: votes.clone(),
        promoted_at: None,
    };
    assert_eq!(tally(&cand(&votes), &r, Some(&ev)), Tally::Promoted, "a silent correlator does not veto");
    votes.insert("corr".into(), vote(Verdict::Deny));
    assert!(matches!(tally(&cand(&votes), &r, Some(&ev)), Tally::Denied(ref d) if d.contains("veto seat corr")));
}

/// ADR-0038 §1: a cell names a declared thinker seat in the observer's domain, and only an
/// observer seat has one. The rules are refused otherwise.
#[test]
fn a_cell_names_a_thinker_seat_in_its_domain_and_only_observers_have_one() {
    let mut r = rules();
    r.seats.insert("ox".into(), cell_observer(Domain::Build, "r1", "kox")); // r1 is a Run seat
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("not a thinker seat in its domain")));
    let mut r = rules();
    r.seats.insert("ox".into(), cell_observer(Domain::Build, "g1", "kox")); // g1 is a grant seat
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("not a thinker seat")));
    let mut r = rules();
    r.seats.insert("ox".into(), cell_observer(Domain::Build, "nobody", "kox"));
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("not declared")));
    let mut r = rules();
    r.seats.insert(
        "gx".into(),
        SeatDecl { domain: Domain::Build, kind: SeatKind::Grant, cell: Some("a1".into()), key: "kgx".into(), rung: 0 },
    );
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("cannot have a cell")));
}

// ---- RunCoupling.tla and RunSeats.tla (ADR-0042 §2, §5; ADR-0043 §2; all Proposed) -----------

fn run_rules() -> Rules {
    let mut r = rules();
    r.seats.insert("ro1".into(), cell_observer(Domain::Run, "r1", "kro1"));
    r
}

fn run_state() -> State {
    let mut s = State::genesis(run_rules(), 2).unwrap();
    s.trace = topak_core::trace::name_from_env("mut");
    s
}

const RUN_THINKER: &[ActionKind] = &[ActionKind::Consult, ActionKind::Actuate, ActionKind::Report];
const RUN_OBSERVER: &[ActionKind] = &[ActionKind::Consult, ActionKind::Report];

fn admit(id: &str, seat: &str, lease: LogIndex, action: Admitted, p: &Params) -> Entry {
    Entry::Admit {
        id: id.into(),
        rec: AdmitRecord {
            seat: seat.into(),
            lease,
            epoch: 0,
            action,
            input: Digest::of(b"input"),
            floor: Digest::of(b"floor"),
            schema: Digest::of(b"schema"),
            floor_reasons: vec![],
            bundle: Digest::of(b"bundle"),
            engine: BundleEngine::LocalWasm,
            params: p.digest(),
            decided_by: 1,
            session: None,
            labels: Some(Default::default()),
        },
    }
}

fn actuate() -> Admitted {
    Admitted::Actuate { tool: "valve@d4".into(), inputs: Digest::of(b"inputs"), break_glass: false }
}

fn consult() -> Admitted {
    Admitted::Consult { object: Digest::of(b"x") }
}

/// RunCoupling.tla `UnreadEffectsBounded` / `M_EMITSEQ`, and `ConsultNeverCoupled`. The sequence an
/// Observer's watermark is over counts every effect-bearing admit (ADR-0042 §2). Before ADR-0042
/// the reference counted emissions only, which is exactly M_EMITSEQ: a Thinker that never
/// reported could invoke up to the round bound with its Observer's mark standing still.
#[test]
fn the_sequence_counts_effects_and_m_emitseq_is_refused() {
    let mut p = params();
    p.round_bound = 40;
    let mut s = run_state();
    let k = s.observer.k;
    assert!(k < p.round_bound, "K < R, or the check is vacuous (ADR-0039 §1)");
    s.apply(1, &Entry::Grant { id: "gt".into(), req: grant_req("r1", RUN_THINKER), appraisal: None }, &p);
    s.apply(2, &Entry::Grant { id: "go".into(), req: grant_req("ro1", RUN_OBSERVER), appraisal: None }, &p);

    // Three invocations, two reads, one report: four effects, six admits.
    let mut at = 10;
    let mut step = |s: &mut State, a: Admitted| {
        at += 1;
        s.apply(at, &admit(&format!("a{at}"), "r1", 1, a, &p), &p)
    };
    for n in 1..=3 {
        assert_eq!(step(&mut s, actuate()), Applied::Admitted { seq: Some(n), promoted: None });
    }
    for _ in 0..2 {
        assert_eq!(step(&mut s, consult()), Applied::Admitted { seq: None, promoted: None });
    }
    let report = Admitted::Report { record: Digest::of(b"r") };
    assert_eq!(step(&mut s, report), Applied::Admitted { seq: Some(4), promoted: None });
    assert_eq!((s.leases[&1].seq, s.leases[&1].actions), (4, 6));

    // Invocations alone fill the backlog to K. Under M_EMITSEQ the sequence would still read 1.
    while s.leases[&1].seq < k {
        assert!(matches!(step(&mut s, actuate()), Applied::Admitted { .. }));
    }
    let a = step(&mut s, actuate());
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("no cell Observer covers")), "M_EMITSEQ: {a:?}");

    // `Consult` is not coupled: a Thinker whose Observer lags can read and cannot act.
    assert_eq!(step(&mut s, consult()), Applied::Admitted { seq: None, promoted: None });
    assert_eq!(s.leases[&1].seq, k, "a read does not advance the sequence");

    // The Observer reads to K, and effects resume.
    let topic = topak_core::lift::topic_name(&s.chain, Domain::Run, "r1", 0, 1);
    let beat = Admitted::Heartbeat { via: ActionKind::Report, topic, watermark: k };
    let a = s.apply(5, &admit("hb", "ro1", 2, beat, &p), &p);
    assert!(matches!(a, Applied::Admitted { .. }), "{a:?}");
    assert_eq!(step(&mut s, actuate()), Applied::Admitted { seq: Some(k + 1), promoted: None });
}

/// RunCoupling.tla `RoundBoundCountsAll`: `R` is a termination bound and a read is a step
/// (ADR-0042 §2), so `Consult` counts toward it though it does not advance the sequence.
#[test]
fn the_round_bound_counts_consult() {
    let p = params();
    let mut s = run_state();
    s.apply(1, &Entry::Grant { id: "gt".into(), req: grant_req("r1", &[ActionKind::Consult]), appraisal: None }, &p);
    for i in 0..p.round_bound {
        let a = s.apply(10 + i, &admit(&format!("c{i}"), "r1", 1, consult(), &p), &p);
        assert_eq!(a, Applied::Admitted { seq: None, promoted: None });
    }
    let a = s.apply(20, &admit("over", "r1", 1, consult(), &p), &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("RoundBoundReached")), "{a:?}");
    assert_eq!((s.leases[&1].seq, s.leases[&1].actions), (0, p.round_bound));
}

/// RunCoupling.tla `SealCountsEffects`, and ADR-0042 §5: a Run round ends when its lease ends. The
/// principal cannot end it, a renewal does not seal it, and the seal is the final sequence.
#[test]
fn a_run_round_seals_with_its_lease_and_a_run_seat_cannot_abstain() {
    let mut p = params();
    p.round_bound = 40;
    let mut s = run_state();
    s.apply(1, &Entry::Grant { id: "gt".into(), req: grant_req("r1", RUN_THINKER), appraisal: None }, &p);
    s.apply(2, &Entry::Grant { id: "go".into(), req: grant_req("ro1", RUN_OBSERVER), appraisal: None }, &p);
    for i in 0..2 {
        s.apply(10 + i, &admit(&format!("a{i}"), "r1", 1, actuate(), &p), &p);
    }

    let end = |fence, reason| Entry::EndRound {
        id: format!("end-{fence}-{reason:?}"),
        seat: "r1".into(),
        fence,
        reason,
        attribution: "test".into(),
    };
    let a = s.apply(20, &end(1, EndReason::Abstained), &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("cannot abstain")), "{a:?}");
    assert!(s.leases[&1].live() && !s.seals.contains_key("r1"));

    // A renewal continues the round under a new fence: no seal, and the counters carry over.
    let renew = RenewRequest {
        seat: "r1".into(),
        fence: 1,
        alphabet: RUN_THINKER.iter().copied().collect(),
        rung: 0,
        ttl_ms: 500,
    };
    assert_eq!(
        s.apply(21, &Entry::Renew { id: "rn".into(), req: renew, appraisal: None }, &p),
        Applied::Renewed { fence: 21 }
    );
    assert!(!s.seals.contains_key("r1"), "a renewal does not seal");
    assert_eq!((s.leases[&21].seq, s.leases[&21].actions), (2, 2));
    s.apply(22, &admit("a2", "r1", 21, actuate(), &p), &p);

    // Expiry is the ordinary end. The seal counts the invocations: there were no reports.
    assert_eq!(s.apply(23, &end(21, EndReason::Expired), &p), Applied::RoundEnded);
    assert_eq!(s.seals["r1"].seq, 3);

    // Cross-round coverage now means something for invocations (ADR-0039 §2).
    let mut next = grant_req("r1", RUN_THINKER);
    next.round = 2;
    let a = s.apply(24, &Entry::Grant { id: "g2".into(), req: next.clone(), appraisal: None }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("unread")), "M_EMITSEQ would seal at 0: {a:?}");
    let beat = Admitted::Heartbeat { via: ActionKind::Report, topic: s.seals["r1"].topic.clone(), watermark: 3 };
    assert!(matches!(s.apply(25, &admit("hb", "ro1", 2, beat, &p), &p), Applied::Admitted { .. }));
    assert!(matches!(
        s.apply(26, &Entry::Grant { id: "g3".into(), req: next, appraisal: None }, &p),
        Applied::LeaseGranted { .. }
    ));

    // Abstention is Build's, and stays Build's.
    let mut b = state();
    b.apply(1, &Entry::Grant { id: "ga".into(), req: grant_req("a1", &[ActionKind::Read]), appraisal: None }, &p);
    let abstain = Entry::EndRound {
        id: "ab".into(),
        seat: "a1".into(),
        fence: 1,
        reason: EndReason::Abstained,
        attribution: "test".into(),
    };
    assert_eq!(b.apply(2, &abstain, &p), Applied::RoundEnded);
}

/// RunSeats.tla `OnlyThinkersActuate` / `M_KIND`: ADR-0043 §2's Run row. An observer seat holds
/// `Consult` and `Report`; only a thinker seat holds `Actuate`; no name crosses the domains.
#[test]
fn run_alphabets_are_bounded_by_seat_kind_and_domain() {
    let p = params();
    let mut s = run_state();
    let a = s.apply(
        1,
        &Entry::Grant { id: "g1".into(), req: grant_req("ro1", &[ActionKind::Actuate]), appraisal: None },
        &p,
    );
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("observer alphabet")), "M_KIND: {a:?}");
    let a =
        s.apply(2, &Entry::Grant { id: "g2".into(), req: grant_req("r1", &[ActionKind::Read]), appraisal: None }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("outside the run alphabet")), "{a:?}");
    let a = s.apply(
        3,
        &Entry::Grant { id: "g3".into(), req: grant_req("a1", &[ActionKind::Consult]), appraisal: None },
        &p,
    );
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("outside the build alphabet")), "{a:?}");
    let a = s.apply(4, &Entry::Grant { id: "g4".into(), req: grant_req("ro1", RUN_OBSERVER), appraisal: None }, &p);
    assert!(matches!(a, Applied::LeaseGranted { .. }), "{a:?}");
    let a = s.apply(5, &Entry::Grant { id: "g5".into(), req: grant_req("r1", RUN_THINKER), appraisal: None }, &p);
    assert!(matches!(a, Applied::LeaseGranted { .. }), "{a:?}");
    assert!(ActionKind::RUN.iter().all(|k| k.domain() == Domain::Run));
    assert!(ActionKind::BUILD.iter().all(|k| k.domain() == Domain::Build));
    assert!(ActionKind::Actuate.is_run_effect() && ActionKind::Report.is_run_effect());
    assert!(!ActionKind::Consult.is_run_effect());
}

/// ADR-0031 A2: a lease's ttl is at most T_persona at grant and at renewal, refused by the
/// mechanism and not by policy; the bound is on the declared value (ADR-0045 finding 2).
/// The bound is a floor constant, so it never moves within a trace: a renewal over it is also a
/// renewal over the lease's own ttl, which §4 refuses first. The renewal check exists for a bound
/// that moves by release, and is shown here at the bound's edge.
#[test]
fn a_ttl_over_t_persona_is_refused_at_grant_and_at_renewal() {
    let mut s = state();
    s.persona.t_persona_ms = 5_000;
    let p = params();
    let mut over = grant_req("a1", &[ActionKind::Read]);
    over.ttl_ms = 5_001;
    assert!(matches!(
        s.apply(1, &Entry::Grant { id: "g-over".into(), req: over, appraisal: None }, &p),
        Applied::Rejected(_)
    ));
    let mut at = grant_req("a1", &[ActionKind::Read]);
    at.ttl_ms = 5_000;
    assert_eq!(
        s.apply(2, &Entry::Grant { id: "g-at".into(), req: at, appraisal: None }, &p),
        Applied::LeaseGranted { fence: 2 }
    );
    let renew = |fence: LogIndex, ttl_ms: u64| Entry::Renew {
        id: format!("r-{fence}-{ttl_ms}"),
        req: RenewRequest {
            seat: "a1".into(),
            fence,
            alphabet: [ActionKind::Read].into_iter().collect(),
            rung: 0,
            ttl_ms,
        },
        appraisal: None,
    };
    assert!(matches!(s.apply(3, &renew(2, 5_001), &p), Applied::Rejected(_)), "over the bound, and over the lease");
    assert_eq!(s.apply(4, &renew(2, 5_000), &p), Applied::Renewed { fence: 4 }, "at the bound");
    assert_eq!(s.apply(5, &renew(4, 1_000), &p), Applied::Renewed { fence: 5 }, "shorter");
}

/// ADR-0025 §1 (f): the keys that vouch for artifacts are issued like every other key, and must
/// be keys.
#[test]
fn vouching_keys_are_issued_and_must_be_keys() {
    let mut r = rules();
    r.bundle_keys.insert("not-a-key".into());
    assert!(check_well_formed(&r).iter().any(|v| v.entry == "WF" && v.detail.contains("bundle key")));
    let mut r = rules();
    r.verifier_keys.insert("ab".repeat(32));
    r.bundle_keys.insert("cd".repeat(32));
    assert!(check_well_formed(&r).is_empty());
}
