//! The emergency seating (ADR-0052, Proposed), at the state: break-glass as a seating, in place
//! of the floor's X1. The properties are `spec/Emergency.tla`'s.
//!
//! | Test | What it shows |
//! |---|---|
//! | `an_emergency_lease_has_a_roster_quorum` | §2: `EmergencyLeaseHasARosterQuorum`; the person is one the seating names; the reason is no field |
//! | `an_emergency_lease_is_one_round` | §3: `EmergencyLeaseIsOneRound`: no successor, no renewal; another round is another quorum |
//! | `an_operator_ends_it_and_x1_is_retired` | §3, §2: any operator of the domain may stop it; the X1 approval is refused |
//! | `the_actions_are_the_persons` | §1: every action under the lease is signed with the person's key |
//! | `a_drill_is_a_real_activation_on_the_log` | §5, §6: `ActivationIsForensic`; a drill is marked by its seating |

use std::collections::{BTreeMap, BTreeSet};

use topak_core::authentic::{self, Signed};
use topak_core::confine::{AGENT_OP_PURPOSE, SessionProof, session_body};
use topak_core::control::*;
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::*;

fn secret(name: &str) -> [u8; 32] {
    hex::decode(Digest::of(name.as_bytes()).0).unwrap().try_into().unwrap()
}

fn public(name: &str) -> String {
    authentic::sign("key", &serde_json::json!(null), &secret(name)).key
}

fn seat(d: Domain, kind: SeatKind, name: &str) -> SeatDecl {
    SeatDecl { domain: d, kind, cell: None, key: public(name), rung: 0 }
}

fn rules() -> Rules {
    let seats = [
        ("r1", SeatKind::Thinker),
        ("em1", SeatKind::Emergency),
        ("drill", SeatKind::Emergency),
        ("opr1", SeatKind::Operator),
        ("opr2", SeatKind::Operator),
    ];
    Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats: seats.iter().map(|(s, k)| (s.to_string(), seat(Domain::Run, *k, s))).collect(),
        grant_roster: BTreeSet::new(),
        veto_roster: BTreeSet::new(),
        anchor_keys: BTreeSet::from(["kA".into(), "kB".into(), "kC".into()]),
        break_glass: Some(BreakGlassRules {
            roster: ["bg1", "bg2", "bg3"].into_iter().map(public).collect(),
            quorum: 2,
            tools: BTreeSet::new(),
            actions: BTreeSet::from(["Actuate".to_string()]),
        }),
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

struct Log {
    s: State,
    at: LogIndex,
}

fn envelope() -> BTreeMap<String, Digest> {
    BTreeMap::from([("isolate@d7".to_string(), Digest::of(b"emergency bundle"))])
}

impl Log {
    /// Two operators seated, and two emergency seatings prepared: one real, one a drill.
    fn prepared() -> Log {
        let mut log = Log { s: State::genesis(rules(), 2).unwrap(), at: 0 };
        for op in ["opr1", "opr2"] {
            let body = sign_on_body(&log.s.chain, &public(op), 0, 0);
            let req = GrantRequest {
                principal: format!("p-{op}"),
                seat: op.into(),
                persona: Digest::of(op.as_bytes()),
                bundle: Digest::of(b"bundle"),
                confinement: lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
                alphabet: BTreeSet::new(),
                ttl_ms: 1000,
                round: 1,
                role: RoundRole::Author,
                task_label: None,
                task_labels_allowed: None,
                sign_on: Some(authentic::sign(SIGN_ON_PURPOSE, &body, &secret("idp"))),
            };
            assert!(matches!(log.apply(Entry::Grant { id: op.into(), req, appraisal: None }), Applied::LeaseGranted { .. }));
        }
        for (seat, drill) in [("em1", false), ("drill", true)] {
            let seating = EmergencySeating {
                persons: BTreeSet::from([public("alice"), public("bob")]),
                bundle: Digest::of(b"emergency bundle"),
                envelope: Envelope::Named(BTreeSet::from(["isolate@d7".to_string()])),
                task_labels: BTreeSet::from(["internal".to_string()]),
                drill,
            };
            let e = Entry::EmergencySeating { id: format!("prepare-{seat}"), seat: seat.into(), seating };
            assert_eq!(log.apply(e), Applied::EmergencyPrepared);
        }
        log
    }

    fn apply(&mut self, e: Entry) -> Applied {
        self.at += 1;
        self.s.apply(self.at, &e, &params())
    }

    fn activation(&self, seat: &str, person: &str, round: Round) -> Activation {
        Activation {
            seat: seat.into(),
            person: public(person),
            epoch: self.s.epoch,
            round,
            ttl_ms: 1000,
            task: Some(Digest::of(b"isolate the west cell")),
            task_label: Some(BTreeSet::from(["internal".to_string()])),
        }
    }

    fn approve(&self, a: &Activation, by: &[&str]) -> Vec<Signed> {
        by.iter().map(|k| authentic::sign(ACTIVATION_PURPOSE, &a.body(&self.s.chain), &secret(k))).collect()
    }

    fn activate(&mut self, a: Activation, by: &[&str]) -> Applied {
        let approvals = self.approve(&a, by);
        self.apply(Entry::Activate { id: format!("act-{}", self.at), activation: a, approvals, envelope: envelope() })
    }

    fn control(&mut self, op: &str, ctr: u64, action: ControlAction) -> Applied {
        let request = ControlRequest { operator: op.into(), epoch: self.s.epoch, ctr, action };
        let facts = match self.s.control_facts(&request, None) {
            Ok(f) => f,
            Err(e) => return Applied::Rejected(e),
        };
        let sig = authentic::sign(CONTROL_PURPOSE, &request.body(&self.s.chain), &secret(op));
        let control = Control { request, sig, assertion: None, facts };
        self.apply(Entry::Control { id: format!("c{ctr}"), control, grant: None, renew: None, appraisal: None })
    }
}

fn refused(a: &Applied, why: &str) -> bool {
    matches!(a, Applied::Rejected(r) if r.contains(why))
}

#[test]
fn an_emergency_lease_has_a_roster_quorum() {
    let mut log = Log::prepared();
    let a = log.activation("em1", "alice", 1);
    // One approval, the same member twice, and a key that is not on the roster: no quorum.
    assert!(refused(&log.activate(a.clone(), &["bg1"]), "the quorum is 2"));
    assert!(refused(&log.activate(a.clone(), &["bg1", "bg1"]), "the quorum is 2"));
    assert!(refused(&log.activate(a.clone(), &["bg1", "mallory"]), "the quorum is 2"));
    // Approvals of another activation do not carry over: another person, another round.
    let other = log.approve(&log.activation("em1", "bob", 1), &["bg1", "bg2"]);
    let e = Entry::Activate { id: "x".into(), activation: a.clone(), approvals: other, envelope: envelope() };
    assert!(refused(&log.apply(e), "the quorum is 2"));
    // A person the seating does not name, and a seat that is not an emergency seat.
    let stranger = log.activation("em1", "mallory", 1);
    assert!(refused(&log.activate(stranger, &["bg1", "bg2"]), "not one the seating says may hold the seat"));
    let wrong = log.activation("r1", "alice", 1);
    assert!(refused(&log.activate(wrong, &["bg1", "bg2"]), "not an emergency seat"));
    // A task with no label, and a label outside the seating's.
    let mut unlabelled = a.clone();
    unlabelled.task_label = None;
    assert!(refused(&log.activate(unlabelled, &["bg1", "bg2"]), "no label"));
    let mut outside = a.clone();
    outside.task_label = Some(BTreeSet::from(["untrusted".to_string()]));
    assert!(refused(&log.activate(outside, &["bg1", "bg2"]), "outside what the seating allows"));
    // An envelope that is not the one the seating names.
    let approvals = log.approve(&a, &["bg1", "bg2"]);
    let wider = BTreeMap::from([("shell@d0".to_string(), Digest::of(b"emergency bundle"))]);
    let e = Entry::Activate { id: "w".into(), activation: a.clone(), approvals, envelope: wider };
    assert!(refused(&log.apply(e), "not the one the seating names"));
    // The roster's quorum, and nothing else: no operator's request, no tally, no gate.
    let Applied::LeaseGranted { fence } = log.activate(a, &["bg1", "bg2"]) else { panic!("not activated") };
    let lr = &log.s.leases[&fence];
    assert_eq!(lr.person, Some(public("alice")));
    assert_eq!(lr.envelope, Some(envelope()));
    assert_eq!(lr.lease.alphabet, [ActionKind::Consult, ActionKind::Actuate, ActionKind::Report].into_iter().collect());
    assert_eq!(lr.labels.clear_set, BTreeSet::from(["internal".to_string()]));
    // The unsigned path does not lease an emergency seat.
    let mut log = Log::prepared();
    let req = GrantRequest {
        principal: public("alice"),
        seat: "em1".into(),
        persona: Digest::of(b"p"),
        bundle: Digest::of(b"emergency bundle"),
        confinement: lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
        alphabet: BTreeSet::from([ActionKind::Actuate]),
        ttl_ms: 1000,
        round: 1,
        role: RoundRole::Author,
        task_label: None,
        task_labels_allowed: None,
        sign_on: None,
    };
    assert!(refused(&log.apply(Entry::Grant { id: "g".into(), req, appraisal: None }), "only by an activation"));
}

#[test]
fn an_emergency_lease_is_one_round() {
    let mut log = Log::prepared();
    let a = log.activation("em1", "alice", 1);
    assert!(matches!(log.activate(a, &["bg1", "bg2"]), Applied::LeaseGranted { .. }));
    // No renewal: an operator's, and the unsigned one.
    let renew = ControlAction::Renew { target: "em1".into(), alphabet: BTreeSet::new(), ttl_ms: 500, sign_on: None };
    assert!(refused(&log.control("opr1", 1, renew), "neither regranted nor renewed"));
    // While the round is live there is no second one.
    let again = log.activation("em1", "alice", 2);
    assert!(refused(&log.activate(again.clone(), &["bg1", "bg2"]), "a live lease exists"));
    // The round ends: at its lease's ttl, here.
    let fence = log.s.live_by_seat["em1"];
    let e = Entry::EndRound { id: "x".into(), seat: "em1".into(), fence, reason: EndReason::Expired, attribution: "clock".into() };
    assert_eq!(log.apply(e), Applied::RoundEnded);
    // No successor: an operator's Regrant of the emergency seat is refused.
    let regrant = ControlAction::Regrant {
        target: "em1".into(),
        round: 2,
        alphabet: BTreeSet::from([ActionKind::Actuate]),
        ttl_ms: 1000,
        task: None,
        task_label: Some(BTreeSet::new()),
        sign_on: None,
    };
    assert!(refused(&log.control("opr1", 2, regrant), "neither regranted nor renewed"));
    // The approvals of round 1 are for round 1.
    let stale = log.approve(&log.activation("em1", "alice", 1), &["bg1", "bg2"]);
    let e = Entry::Activate { id: "s".into(), activation: again.clone(), approvals: stale, envelope: envelope() };
    assert!(refused(&log.apply(e), "the quorum is 2"));
    // Another round is another quorum.
    assert!(matches!(log.activate(again, &["bg2", "bg3"]), Applied::LeaseGranted { .. }));
    assert_eq!(log.s.activations.len(), 2);
}

#[test]
fn an_operator_ends_it_and_x1_is_retired() {
    let mut log = Log::prepared();
    let a = log.activation("em1", "alice", 1);
    assert!(matches!(log.activate(a, &["bg1", "bg2"]), Applied::LeaseGranted { .. }));
    // Any operator of the domain may revoke it (ADR-0050 §4), by its key under a live lease.
    let revoke = ControlAction::Revoke { target: RevocationTarget::Principal(public("alice")), reason: "seen".into() };
    assert_eq!(log.control("opr2", 1, revoke), Applied::Revoked { ended: 1 });
    assert!(!log.s.live_by_seat.contains_key("em1"));
    // Revoked is revoked: the roster's quorum does not seat that person again.
    let again = log.activation("em1", "alice", 2);
    assert!(refused(&log.activate(again, &["bg1", "bg2"]), "revoked"));
    // An epoch increment fences an emergency lease like any other.
    let b = log.activation("em1", "bob", 2);
    assert!(matches!(log.activate(b.clone(), &["bg1", "bg2"]), Applied::LeaseGranted { .. }));
    assert_eq!(log.control("opr1", 2, ControlAction::FenceEpoch { reason: "stop".into() }), Applied::EpochIncremented { epoch: 1 });
    assert!(!log.s.live_by_seat.contains_key("em1"));
    // Approvals for the old epoch seat nobody in the new one.
    let mut next = b;
    next.round = 3;
    assert!(refused(&log.activate(next, &["bg1", "bg2"]), "fenced epoch"));
    // X1's approval, scoped to a seat and an epoch, is refused: there is no exception to approve.
    let approval = authentic::sign("break-glass", &serde_json::json!({ "seat": "r1", "epoch": 1 }), &secret("bg1"));
    let e = Entry::BreakGlassApprove { id: "bg".into(), seat: "r1".into(), epoch: 1, approval };
    assert!(refused(&log.apply(e), "X1 break-glass is retired"));
}

#[test]
fn the_actions_are_the_persons() {
    let mut log = Log::prepared();
    let a = log.activation("em1", "alice", 1);
    let Applied::LeaseGranted { fence } = log.activate(a, &["bg1", "bg2"]) else { panic!() };
    let admit = |log: &mut Log, id: &str, session: Option<SessionProof>| {
        let rec = AdmitRecord {
            seat: "em1".into(),
            lease: fence,
            epoch: 0,
            action: Admitted::Actuate { tool: "isolate@d7".into(), inputs: Digest::of(b"in"), emergency: true },
            input: Digest::of(b"input"),
            floor: Digest::of(b"floor"),
            schema: Digest::of(b"schema"),
            floor_reasons: vec!["R1-actuate-allowlisted".into()],
            bundle: Digest::of(b"emergency bundle"),
            engine: BundleEngine::LocalWasm,
            params: params().digest(),
            decided_by: 1,
            session,
            labels: Some(labels::LabelFacts::unlabelled(&BTreeSet::from(["internal".to_string()]))),
        };
        log.apply(Entry::Admit { id: id.into(), rec })
    };
    let proof = |who: &str, ctr: u64| {
        let op = Digest::of(b"the action");
        let sig = authentic::sign(AGENT_OP_PURPOSE, &session_body(fence, 0, ctr, &op), &secret(who)).sig;
        SessionProof { ctr, op, sig }
    };
    // Unsigned, and signed by somebody else: not the person's.
    assert!(refused(&admit(&mut log, "a", None), "signed nothing"));
    assert!(refused(&admit(&mut log, "b", Some(proof("bob", 1))), "session proof"));
    // Signed by the person seated. No cell Observer is asked for: R3 is a Thinker's (§4).
    assert!(matches!(admit(&mut log, "c", Some(proof("alice", 1))), Applied::Admitted { .. }));
    assert!(refused(&admit(&mut log, "d", Some(proof("alice", 1))), "replayed"));
}

#[test]
fn a_drill_is_a_real_activation_on_the_log() {
    let mut log = Log::prepared();
    let d = log.activation("drill", "bob", 1);
    assert!(refused(&log.activate(d.clone(), &["bg1"]), "the quorum is 2"), "a drill takes the real quorum");
    assert!(matches!(log.activate(d, &["bg1", "bg3"]), Applied::LeaseGranted { .. }));
    let a = log.activation("em1", "alice", 1);
    assert!(matches!(log.activate(a, &["bg2", "bg3"]), Applied::LeaseGranted { .. }));
    // The forensic record: who approved, whom, on which seating, for which round, with the
    // task's digest and label. There is no field for the reason.
    let recs = &log.s.activations;
    assert_eq!(recs.iter().map(|r| (r.activation.seat.as_str(), r.drill)).collect::<Vec<_>>(), [("drill", true), ("em1", false)]);
    assert_eq!(recs[0].approvers, BTreeSet::from([public("bg1"), public("bg3")]));
    assert_eq!(recs[1].activation.person, public("alice"));
    assert_eq!(recs[1].activation.task, Some(Digest::of(b"isolate the west cell")));
    let fields: BTreeSet<String> =
        serde_json::to_value(&recs[1].activation).unwrap().as_object().unwrap().keys().cloned().collect();
    assert!(!fields.iter().any(|f| f.contains("reason")), "{fields:?}");
    // Whether the obligation of §6 was met is read from the log: drills in this epoch, with no clock.
    assert_eq!(recs.iter().filter(|r| r.drill && r.activation.epoch == log.s.epoch).count(), 1);
}
