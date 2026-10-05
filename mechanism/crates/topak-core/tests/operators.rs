//! The operator as a principal (ADR-0050, provisional), at the state: what every replica holds an
//! operator's signed request to when it applies it. The floor's control entries decide a request
//! on the deciding replica; `apply` verifies the signature, recomputes the facts and restates the
//! envelope, and these tests are of that half. The properties are `spec/Operators.tla`'s.
//!
//! | Test | What it shows |
//! |---|---|
//! | `an_operators_lease_needs_a_sign_on_assertion` | §3: read at the lease boundary; the provider's key is issued |
//! | `a_successor_grant_keeps_the_seating_and_never_widens` | §2: `C1`, `C5`, `C6`, `C8` |
//! | `the_unsigned_path_seats_and_does_nothing_else` | §2, §4: the BOOTSTRAP path, where the rules declare an operator |
//! | `a_lapsed_operator_stops_its_own_domain_and_nothing_else` | §4: `C4`, `C7`, `C9`, on a fresh assertion |
//! | `a_request_is_the_operators_and_is_not_replayed` | §3: the signature, the counter, the facts |
//! | `three_operators_recover_a_lapse_and_two_cannot` | §6 |

use std::collections::{BTreeMap, BTreeSet};

use topak_core::authentic::{self, Signed};
use topak_core::control::*;
use topak_core::lease::Confinement;
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::*;

fn secret(name: &str) -> [u8; 32] {
    let d = hex::decode(Digest::of(name.as_bytes()).0).unwrap();
    d.try_into().unwrap()
}

fn public(name: &str) -> String {
    authentic::sign("key", &serde_json::json!(null), &secret(name)).key
}

fn seat(d: Domain, kind: SeatKind, name: &str) -> SeatDecl {
    SeatDecl { domain: d, kind, cell: None, key: public(name), rung: 0 }
}

fn rules(build_operators: &[&str]) -> Rules {
    let mut seats = BTreeMap::from([
        ("a1".to_string(), seat(Domain::Build, SeatKind::Thinker, "a1")),
        ("r1".to_string(), seat(Domain::Run, SeatKind::Thinker, "r1")),
        ("opr1".to_string(), seat(Domain::Run, SeatKind::Operator, "opr1")),
        ("opr2".to_string(), seat(Domain::Run, SeatKind::Operator, "opr2")),
    ]);
    for op in build_operators {
        seats.insert(op.to_string(), seat(Domain::Build, SeatKind::Operator, op));
    }
    Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats,
        grant_roster: BTreeSet::new(),
        veto_roster: BTreeSet::new(),
        anchor_keys: BTreeSet::from(["kA".into(), "kB".into(), "kC".into()]),
        break_glass: None,
        erasure_roster: None,
        verifier_keys: BTreeSet::new(),
        bundle_keys: BTreeSet::new(),
        provider_keys: BTreeSet::from([public("idp")]),
        inside_targets: BTreeSet::new(),
        releasers: BTreeSet::new(),
        personas: BTreeMap::new(),
        criterion: None,
    }
}

/// With `TOPAK_TRACE_DIR` set, every `apply` is recorded for `spec/Mechanism.tla` (`trace.rs`).
fn traced(mut s: State) -> State {
    s.trace = topak_core::trace::name_from_env("op");
    s
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

/// A sign-on assertion for `seat` from provider `idp`, naming the seat's key and its current fence.
fn sign_on_from(s: &State, seat: &str, idp: &str) -> Signed {
    let last = s.last_lease.get(seat).copied().unwrap_or(0);
    authentic::sign(SIGN_ON_PURPOSE, &sign_on_body(&s.chain, &public(seat), s.epoch, last), &secret(idp))
}

fn sign_on(s: &State, seat: &str) -> Signed {
    sign_on_from(s, seat, "idp")
}

const AUTHOR: [ActionKind; 2] = [ActionKind::Read, ActionKind::Emit];

fn seating(s: &State, seat: &str, round: Round) -> GrantRequest {
    let operator = s.rules.seat_kind(seat) == Some(SeatKind::Operator);
    let build = s.rules.seat_domain(seat) == Some(Domain::Build);
    GrantRequest {
        principal: format!("p-{seat}"),
        seat: seat.into(),
        persona: Digest::of(format!("persona-{seat}").as_bytes()),
        bundle: Digest::of(b"bundle"),
        confinement: Confinement { digest: Digest::of(b"none"), rung: 0 },
        alphabet: if operator || !build { BTreeSet::new() } else { AUTHOR.into_iter().collect() },
        ttl_ms: 1000,
        round,
        role: RoundRole::Author,
        task_label: None,
        task_labels_allowed: Some(BTreeSet::from(["internal".to_string()])),
        sign_on: operator.then(|| sign_on(s, seat)),
    }
}

struct Log {
    s: State,
    at: LogIndex,
    ctr: u64,
}

impl Log {
    /// Every seat seated by the BOOTSTRAP path, each with its first lease.
    fn seated(build_operators: &[&str]) -> Log {
        let mut log = Log { s: traced(State::genesis(rules(build_operators), 2).unwrap()), at: 0, ctr: 0 };
        let seats: Vec<String> = log.s.rules.seats.keys().cloned().collect();
        for seat in seats {
            let req = seating(&log.s, &seat, 1);
            let a = log.apply(Entry::Grant { id: format!("seat-{seat}"), req, appraisal: None });
            assert!(matches!(a, Applied::LeaseGranted { .. }), "{seat}: {a:?}");
        }
        log
    }

    fn apply(&mut self, e: Entry) -> Applied {
        self.at += 1;
        self.s.apply(self.at, &e, &params())
    }

    /// A request signed by `op`'s key, with the facts this state gives it: what a replica that
    /// asked no floor would order. `apply` is what stands between it and the log.
    fn request(&mut self, op: &str, action: ControlAction, assertion: Option<Signed>) -> Entry {
        self.signed_by(op, op, action, assertion)
    }

    fn signed_by(&mut self, op: &str, key: &str, action: ControlAction, assertion: Option<Signed>) -> Entry {
        self.ctr += 1;
        let request = ControlRequest { operator: op.into(), epoch: self.s.epoch, ctr: self.ctr, action };
        let facts = self.s.control_facts(&request, assertion.as_ref()).expect("facts");
        let sig = authentic::sign(CONTROL_PURPOSE, &request.body(&self.s.chain), &secret(key));
        let grant = match &request.action {
            ControlAction::Regrant { target, round, alphabet, ttl_ms, task_label, sign_on, .. } => {
                let s = &self.s.seatings[target];
                Some(GrantRequest {
                    principal: s.principal.clone(),
                    seat: target.clone(),
                    persona: s.persona.clone(),
                    bundle: s.bundle.clone(),
                    confinement: s.confinement.clone(),
                    alphabet: alphabet.clone(),
                    ttl_ms: *ttl_ms,
                    round: *round,
                    role: s.role,
                    task_label: task_label.clone(),
                    task_labels_allowed: None,
                    sign_on: sign_on.clone(),
                })
            }
            _ => None,
        };
        let renew = match &request.action {
            ControlAction::Renew { target, alphabet, ttl_ms, .. } => Some(RenewRequest {
                seat: target.clone(),
                fence: self.s.live_by_seat[target],
                alphabet: alphabet.clone(),
                rung: 0,
                ttl_ms: *ttl_ms,
            }),
            _ => None,
        };
        let control = Control { request, sig, assertion, facts };
        Entry::Control { id: format!("c{}", self.ctr), control, grant, renew, appraisal: None }
    }

    fn act(&mut self, op: &str, action: ControlAction, assertion: Option<Signed>) -> Applied {
        let e = self.request(op, action, assertion);
        self.apply(e)
    }

    fn end(&mut self, op: &str, target: &str) {
        let a = self.act(op, ControlAction::EndRound { target: target.into() }, None);
        assert_eq!(a, Applied::RoundEnded, "{op} ends {target}");
    }
}

fn regrant(target: &str, round: Round, alphabet: &[ActionKind], label: Option<&[&str]>) -> ControlAction {
    ControlAction::Regrant {
        target: target.into(),
        round,
        alphabet: alphabet.iter().copied().collect(),
        ttl_ms: 1000,
        task: Some(Digest::of(b"the round's task")),
        task_label: label.map(|l| l.iter().map(|s| s.to_string()).collect()),
        sign_on: None,
    }
}

fn refused_by(a: &Applied, entry: &str) -> bool {
    matches!(a, Applied::Rejected(why) if why.contains(entry))
}

#[test]
fn an_operators_lease_needs_a_sign_on_assertion() {
    let mut log = Log { s: traced(State::genesis(rules(&["op1", "op2"]), 2).unwrap()), at: 0, ctr: 0 };
    let grant = |req| Entry::Grant { id: Digest::of_json(&req).0, req, appraisal: None };
    // No assertion: no lease.
    let mut req = seating(&log.s, "op1", 1);
    req.sign_on = None;
    assert!(refused_by(&log.apply(grant(req)), "sign-on assertion"));
    // An assertion from a provider whose key the rules do not issue.
    let mut req = seating(&log.s, "op1", 1);
    req.sign_on = Some(sign_on_from(&log.s, "op1", "another idp"));
    assert!(refused_by(&log.apply(grant(req)), "sign-on assertion"));
    // An assertion for another operator's key.
    let mut req = seating(&log.s, "op1", 1);
    req.sign_on = Some(sign_on(&log.s, "op2"));
    assert!(refused_by(&log.apply(grant(req)), "sign-on assertion"));
    // The provider's, for this key and this fence: seated.
    let req = seating(&log.s, "op1", 1);
    let used = req.sign_on.clone();
    assert!(matches!(log.apply(grant(req)), Applied::LeaseGranted { .. }));
    let req = seating(&log.s, "op2", 1);
    assert!(matches!(log.apply(grant(req)), Applied::LeaseGranted { .. }));
    // It is fresh because of the fence it names, not a clock: op1 now holds a lease, and the
    // assertion that seated it names the fence before. A renewal on it is refused.
    let renew = |sign_on| ControlAction::Renew { target: "op1".into(), alphabet: BTreeSet::new(), ttl_ms: 500, sign_on };
    assert!(refused_by(&log.act("op2", renew(used), None), "fresh sign-on assertion"));
    let fresh = sign_on(&log.s, "op1");
    assert!(matches!(log.act("op2", renew(Some(fresh)), None), Applied::Renewed { .. }));
    // A principal that is not an operator is asked for none.
    let req = seating(&log.s, "a1", 1);
    assert!(matches!(log.apply(grant(req)), Applied::LeaseGranted { .. }));
}

#[test]
fn a_successor_grant_keeps_the_seating_and_never_widens() {
    let mut log = Log::seated(&["op1", "op2", "op3"]);
    // A live lease is not regranted over: the round must have ended.
    assert!(refused_by(&log.act("op1", regrant("a1", 2, &AUTHOR, Some(&[])), None), "C1-regrant-successor"));
    log.end("op1", "a1");
    // No label on the task (ADR-0047 §1), and a label the seating does not allow (§5).
    assert!(refused_by(&log.act("op1", regrant("a1", 2, &AUTHOR, None), None), "C8-task-label-in-bounds"));
    assert!(refused_by(&log.act("op1", regrant("a1", 2, &AUTHOR, Some(&["untrusted"])), None), "C8-task-label"));
    // Wider than the last lease, and a round that is not the next one.
    let wider = [ActionKind::Read, ActionKind::Emit, ActionKind::Submit];
    assert!(refused_by(&log.act("op1", regrant("a1", 2, &wider, Some(&[])), None), "C1-regrant-successor"));
    assert!(refused_by(&log.act("op1", regrant("a1", 3, &AUTHOR, Some(&[])), None), "C1-regrant-successor"));
    // Another domain's principal.
    log.end("opr1", "r1");
    assert!(refused_by(&log.act("op1", regrant("r1", 2, &[], Some(&[])), None), "C1-regrant-successor"));
    // The next round, narrower, labelled within the seating: granted, with the seating's binding.
    let a = log.act("op1", regrant("a1", 2, &[ActionKind::Read], Some(&["internal"])), None);
    let Applied::LeaseGranted { fence } = a else { panic!("{a:?}") };
    let lease = &log.s.leases[&fence];
    assert_eq!((lease.lease.round, lease.lease.principal.as_str()), (2, "p-a1"));
    assert_eq!(lease.lease.persona, Digest::of(b"persona-a1"));
    assert_eq!(lease.labels.clear_set, BTreeSet::from(["internal".to_string()]), "clearSet starts from the task's label");
    // Narrowing is kept: the round after may not take back what round 2 gave up.
    log.end("op2", "a1");
    assert!(refused_by(&log.act("op2", regrant("a1", 3, &AUTHOR, Some(&[])), None), "C1-regrant-successor"));
    // An operator neither renews nor regrants itself (`C6`).
    let own = ControlAction::Renew { target: "op1".into(), alphabet: BTreeSet::new(), ttl_ms: 500, sign_on: None };
    assert!(refused_by(&log.act("op1", own, None), "C6-no-self"));
    // An operator's own successor lease is a peer's to grant.
    log.end("op2", "op1");
    assert!(refused_by(&log.act("op1", regrant("op1", 2, &[], Some(&[])), None), "C5-add-needs-lease-and-peer"));
}

#[test]
fn the_unsigned_path_seats_and_does_nothing_else() {
    let mut log = Log::seated(&["op1", "op2", "op3"]);
    let live = log.s.live_by_seat["a1"];
    let unsigned = [
        Entry::EndRound { id: "e".into(), seat: "a1".into(), fence: live, reason: EndReason::Operator, attribution: "socket".into() },
        Entry::Revoke { id: "r".into(), target: RevocationTarget::Principal("p-a1".into()), reason: "x".into(), attribution: "socket".into() },
        Entry::EpochIncrement { id: "f".into(), reason: "x".into(), attribution: "socket".into() },
        Entry::GatesPassed { id: "g".into(), artifact: Digest::of(b"a"), evidence: Digest::of(b"e") },
        Entry::Renew {
            id: "n".into(),
            req: RenewRequest { seat: "a1".into(), fence: live, alphabet: AUTHOR.into_iter().collect(), rung: 0, ttl_ms: 500 },
            appraisal: None,
        },
    ];
    for e in unsigned {
        assert!(refused_by(&log.apply(e.clone()), "an operator's signed request"), "{e:?}");
    }
    assert_eq!(log.s.epoch, 0, "nothing was fenced");
    // What the mechanism orders for itself is not an operator's request: an expiry still ends a round.
    let e = Entry::EndRound { id: "x".into(), seat: "a1".into(), fence: live, reason: EndReason::Expired, attribution: "clock".into() };
    assert_eq!(log.apply(e), Applied::RoundEnded);
    // The seat's next round, asked for on the unsigned path: a successor, and so an operator's.
    let req = seating(&log.s, "a1", 2);
    assert!(refused_by(&log.apply(Entry::Grant { id: "s".into(), req, appraisal: None }), "an operator's Regrant"));
    // A different binding is a first lease (§2), and the path that stands in for a quorum seats it.
    let mut req = seating(&log.s, "a1", 2);
    req.persona = Digest::of(b"another persona");
    assert!(matches!(log.apply(Entry::Grant { id: "s2".into(), req, appraisal: None }), Applied::LeaseGranted { .. }));
    assert_eq!(log.s.seatings["a1"].persona, Digest::of(b"another persona"));
}

#[test]
fn a_lapsed_operator_stops_its_own_domain_and_nothing_else() {
    let mut log = Log::seated(&["op1", "op2", "op3"]);
    log.end("op1", "op3");
    let revoke = || ControlAction::Revoke { target: RevocationTarget::Principal("p-a1".into()), reason: "seen".into() };
    let fence = || ControlAction::FenceEpoch { reason: "stop".into() };
    // By its key alone: a key is not a standing lever.
    assert!(refused_by(&log.act("op3", revoke(), None), "C4-deny"));
    // An assertion that names an older fence is not fresh: the one that seated it.
    let stale = authentic::sign(SIGN_ON_PURPOSE, &sign_on_body(&log.s.chain, &public("op3"), 0, 0), &secret("idp"));
    assert!(refused_by(&log.act("op3", revoke(), Some(stale)), "C4-deny"));
    // The widest stop needs a live lease, assertion or not.
    let fresh = sign_on(&log.s, "op3");
    assert!(refused_by(&log.act("op3", fence(), Some(fresh.clone())), "C7-fence-needs-lease"));
    // An add needs a lease.
    assert!(refused_by(&log.act("op3", regrant("a1", 2, &AUTHOR, Some(&[])), Some(fresh.clone())), "C5-add-needs-lease"));
    // Another domain's principal is not its to stop, lapsed or live.
    let other = || ControlAction::EndRound { target: "r1".into() };
    assert!(refused_by(&log.act("op3", other(), Some(fresh.clone())), "C9-stop-in-own-domain"));
    assert!(refused_by(&log.act("op1", other(), None), "C9-stop-in-own-domain"));
    let across = ControlAction::Revoke { target: RevocationTarget::Principal("p-r1".into()), reason: "x".into() };
    assert!(refused_by(&log.act("op1", across, None), "C9-stop-in-own-domain"));
    // In its own domain, on a fresh assertion: admitted, and attributed by its signature.
    assert_eq!(log.act("op3", revoke(), Some(fresh)), Applied::Revoked { ended: 1 });
    assert!(!log.s.live_by_seat.contains_key("a1"));
    // A revoked principal is not seated, so nobody regrants it.
    assert!(refused_by(&log.act("op1", regrant("a1", 2, &AUTHOR, Some(&[])), None), "C1-regrant-successor"));
    // A live operator fences the fleet by its key alone.
    assert_eq!(log.act("op1", fence(), None), Applied::EpochIncremented { epoch: 1 });
    assert!(log.s.live_by_seat.is_empty(), "every lease is fenced, the operators' with them");
    // An operator whose own principal is revoked has no Persona in force, and stops nothing.
    let mut log = Log::seated(&["op1", "op2", "op3"]);
    let a = log.act("op1", ControlAction::Revoke { target: RevocationTarget::Principal("p-op3".into()), reason: "left".into() }, None);
    assert_eq!(a, Applied::Revoked { ended: 1 });
    let fresh = sign_on(&log.s, "op3");
    assert!(refused_by(&log.act("op3", revoke(), Some(fresh)), "C4-deny"));
}

#[test]
fn a_request_is_the_operators_and_is_not_replayed() {
    let mut log = Log::seated(&["op1", "op2", "op3"]);
    let end = || ControlAction::EndRound { target: "a1".into() };
    // Signed by another seat's key.
    let forged = log.signed_by("op1", "op2", end(), None);
    assert!(refused_by(&log.apply(forged), "not signed by the operator seat's key"));
    // A seat that is not an operator's has no control alphabet.
    let request = ControlRequest { operator: "a1".into(), epoch: 0, ctr: 99, action: end() };
    let sig = authentic::sign(CONTROL_PURPOSE, &request.body(&log.s.chain), &secret("a1"));
    let e = Entry::Control {
        id: "x".into(),
        control: Control { request, sig, assertion: None, facts: ControlFacts::default() },
        grant: None,
        renew: None,
        appraisal: None,
    };
    assert!(refused_by(&log.apply(e), "not an operator seat"));
    // Facts that are not this state's: the floor was asked about something else.
    let Entry::Control { id, mut control, .. } = log.request("op1", regrant("a1", 2, &AUTHOR, Some(&[])), None) else {
        unreachable!()
    };
    control.facts.target_live = false;
    let e = Entry::Control { id, control, grant: None, renew: None, appraisal: None };
    assert!(refused_by(&log.apply(e), "facts that no longer hold"));
    // The same signed request, ordered twice under two ids: once.
    let Entry::Control { control, .. } = log.request("op1", end(), None) else { unreachable!() };
    let again = |id: &str| Entry::Control { id: id.into(), control: control.clone(), grant: None, renew: None, appraisal: None };
    assert_eq!(log.apply(again("first")), Applied::RoundEnded);
    assert!(refused_by(&log.apply(again("second")), "counter is replayed"));
    // A request signed before a fence is for a fenced epoch.
    let old = log.request("op2", ControlAction::EndRound { target: "op3".into() }, None);
    assert_eq!(log.act("op1", ControlAction::FenceEpoch { reason: "stop".into() }, None), Applied::EpochIncremented { epoch: 1 });
    assert!(refused_by(&log.apply(old), "fenced"));
}

#[test]
fn three_operators_recover_a_lapse_and_two_cannot() {
    let again = |log: &Log| ControlAction::Regrant {
        target: "op3".into(),
        round: 2,
        alphabet: BTreeSet::new(),
        ttl_ms: 1000,
        task: None,
        task_label: Some(BTreeSet::new()),
        sign_on: Some(sign_on(&log.s, "op3")),
    };
    // Three: one lapses, the two that remain are each other's peers, and one regrants the third.
    let mut log = Log::seated(&["op1", "op2", "op3"]);
    log.end("op1", "op3");
    let action = again(&log);
    assert!(matches!(log.act("op1", action, None), Applied::LeaseGranted { .. }));
    assert_eq!(log.s.live_operators(Domain::Build).len(), 3);
    // Two: one lapses, the other has no live peer and adds nothing, the lapsed one included.
    let mut log = Log::seated(&["op1", "op3"]);
    log.end("op1", "op3");
    let action = again(&log);
    assert!(refused_by(&log.act("op1", action, None), "C5-add-needs-lease-and-peer"));
    assert!(refused_by(&log.act("op1", regrant("a1", 2, &AUTHOR, Some(&[])), None), "C5-add-needs-lease-and-peer"));
    // It can still stop. And only a quorum seats the lapsed one again: here, the path that stands in.
    log.end("op1", "a1");
    let req = seating(&log.s, "op3", 2);
    assert!(matches!(log.apply(Entry::Grant { id: "reseat".into(), req, appraisal: None }), Applied::LeaseGranted { .. }));
}
