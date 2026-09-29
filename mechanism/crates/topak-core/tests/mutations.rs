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
    SeatDecl { domain: d, kind, cell: None, key: key.into() }
}

fn cell_observer(d: Domain, cell: &str, key: &str) -> SeatDecl {
    SeatDecl { domain: d, kind: SeatKind::Observer, cell: Some(cell.into()), key: key.into() }
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
    }
}

fn params() -> Params {
    Params {
        corpus: BTreeSet::new(),
        build_tools: BTreeSet::new(),
        run_tools: BTreeSet::new(),
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
        confinement: Confinement { digest: Digest::of(b"profile"), rung: 1 },
        alphabet: alphabet.iter().copied().collect(),
        ttl_ms: 1000,
        round: 1,
        role: RoundRole::Author,
    }
}

fn state() -> State {
    State::genesis(rules(), 2).unwrap()
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
        s.apply(1, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read, ActionKind::Emit]) }, &p),
        Applied::LeaseGranted { fence: 1 }
    );
    let renew = |alphabet: &[ActionKind], rung, ttl| RenewRequest {
        seat: "a1".into(),
        fence: 1,
        alphabet: alphabet.iter().copied().collect(),
        rung,
        ttl_ms: ttl,
    };

    // M_RENEW: every widening is refused.
    for (i, r) in [
        renew(&[ActionKind::Read, ActionKind::Emit, ActionKind::Draft], 1, 1000),
        renew(&[ActionKind::Read], 2, 1000),
        renew(&[ActionKind::Read], 1, 2000),
    ]
    .into_iter()
    .enumerate()
    {
        let a = s.apply(10 + i as u64, &Entry::Renew { id: format!("w{i}"), req: r }, &p);
        assert!(matches!(a, Applied::Rejected(_)), "widening {i} accepted: {a:?}");
    }
    // Lease_A1.tla `M_LOWER`: a lower rung is refused too (ADR-0031 A1, ADR-0034 §3.4). The
    // lease stays live at its rung; a principal that cannot re-attest lets it lapse instead.
    let a = s.apply(15, &Entry::Renew { id: "l".into(), req: renew(&[ActionKind::Read], 0, 500) }, &p);
    assert!(matches!(a, Applied::Rejected(_)), "M_LOWER: a renewal lowered the rung: {a:?}");
    assert_eq!(s.live_by_seat["a1"], 1, "a refused renewal leaves the lease as it was");
    // Narrowing is accepted at the same rung, at a new fence, and the old lease stops being live.
    let a = s.apply(20, &Entry::Renew { id: "n".into(), req: renew(&[ActionKind::Read], 1, 500) }, &p);
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
    s.apply(1, &Entry::Grant { id: "g".into(), req }, &p);
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
    s.apply(1, &Entry::Grant { id: "g1".into(), req: grant_req("a1", &[ActionKind::Read]) }, &p);
    let mut wide = grant_req("a1", &[ActionKind::Read, ActionKind::Draft, ActionKind::Invoke]);
    wide.round = 2;
    let a = s.apply(2, &Entry::Grant { id: "g2".into(), req: wide }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("live lease")), "{a:?}");
}

#[test]
fn no_action_under_a_fenced_epoch_and_m_fence_is_refused() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]) }, &p);
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
    s.apply(1, &Entry::Grant { id: "g1".into(), req: grant_req("a1", &[ActionKind::Read]) }, &p);
    let mut other = grant_req("g1", &[ActionKind::Read]);
    other.persona = Digest::of(b"another persona");
    s.apply(2, &Entry::Grant { id: "g2".into(), req: other }, &p);
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
        let a = s.apply(2, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]) }, &p);
        assert!(matches!(a, Applied::Rejected(ref m) if m.contains("revoked")), "target {i} re-granted: {a:?}");
        // Reachability: a principal the target does not match is still granted.
        let mut other = grant_req("g1", &[ActionKind::Read]);
        other.principal = "p-other".into();
        other.persona = Digest::of(b"another persona");
        other.confinement.digest = Digest::of(b"another profile");
        assert_eq!(s.apply(3, &Entry::Grant { id: "o".into(), req: other }, &p), Applied::LeaseGranted { fence: 3 });
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

#[test]
fn rung_zero_is_never_contained_and_nothing_is_contained_yet() {
    let mut l = Lease {
        principal: "p".into(),
        seat: "a1".into(),
        persona: Digest::of(b"p"),
        epoch: 0,
        fence: 1,
        rules_epoch: 0,
        bundle: Digest::of(b"b"),
        confinement: Confinement { digest: Digest::of(b"c"), rung: 0 },
        alphabet: BTreeSet::new(),
        round: 1,
        role: RoundRole::Author,
        ttl_ms: 1,
    };
    assert!(!l.is_contained());
    l.confinement.rung = 3;
    assert!(!l.is_contained(), "the provenance criterion is unwritten, so no rung suffices");
}

#[test]
fn the_round_bound_terminates_a_round() {
    let p = params();
    let mut s = state();
    s.apply(1, &Entry::Grant { id: "g".into(), req: grant_req("a1", &[ActionKind::Read]) }, &p);
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
    assert!(!via_break_glass(&["X1-break-glass".into(), "R1-run-invoke-allowlisted".into()]));
    assert!(!via_break_glass(&["R1-run-invoke-allowlisted".into()]));
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
        actions: BTreeSet::from(["RunInvoke".into(), "Vote".into()]),
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
    let a =
        s.apply(1, &Entry::Grant { id: "g1".into(), req: grant_req("o1", &[ActionKind::Read, ActionKind::Draft]) }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("observer alphabet")), "{a:?}");
    let a =
        s.apply(2, &Entry::Grant { id: "g2".into(), req: grant_req("a1", &[ActionKind::Read, ActionKind::Vote]) }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("thinker alphabet")), "{a:?}");
    let a = s.apply(3, &Entry::Grant { id: "g3".into(), req: grant_req("g1", &[ActionKind::Submit]) }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("grant alphabet")), "{a:?}");
    // Reachability: each kind is granted what it may hold.
    for (seat, alpha) in [
        ("o1", vec![ActionKind::Read, ActionKind::Emit, ActionKind::Vote]),
        ("a1", vec![ActionKind::Read, ActionKind::Draft]),
        ("g1", vec![ActionKind::Vote]),
    ] {
        let mut req = grant_req(seat, &alpha);
        req.role = if seat == "a1" { RoundRole::Author } else { RoundRole::Voter };
        let a =
            s.apply(10 + seat.len() as u64 + alpha.len() as u64, &Entry::Grant { id: format!("ok-{seat}"), req }, &p);
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
    assert!(matches!(s.apply(1, &Entry::Grant { id: "g1".into(), req: first }, &p), Applied::LeaseGranted { .. }));
    let mut second = grant_req("g1", &[ActionKind::Read]);
    second.principal = "p-shared".into();
    second.role = RoundRole::Voter;
    let a = s.apply(2, &Entry::Grant { id: "g2".into(), req: second }, &p);
    assert!(matches!(a, Applied::Rejected(ref r) if r.contains("holds a live lease on seat a1")), "M_SEAT: {a:?}");
    // Reachability: another principal takes g1; and after a1's round ends, p-shared may take g1.
    let mut other = grant_req("g1", &[ActionKind::Read]);
    other.principal = "p-other".into();
    other.role = RoundRole::Voter;
    assert!(matches!(s.apply(3, &Entry::Grant { id: "g3".into(), req: other }, &p), Applied::LeaseGranted { .. }));
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
        SeatDecl { domain: Domain::Build, kind: SeatKind::Grant, cell: Some("a1".into()), key: "kgx".into() },
    );
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("cannot have a cell")));
}
