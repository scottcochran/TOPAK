//! `spec/Confinement.tla`, restated against the Rust mechanism (ADR-0034 §3, §4, §7).
//!
//! Each invariant gets a test that the implementation keeps it, and each mutation of §7 a test
//! that the state it would admit is refused at apply. The appraisal here is built by hand: what a
//! replica believes is only what `State::apply` checks, whoever produced the entry.
//!
//! | `Confinement.tla`        | here                                                          |
//! |--------------------------|---------------------------------------------------------------|
//! | `M_CONTESTED`            | `a_contested_verdict_never_grants_and_revokes_the_principal`  |
//! | `M_UNBOUND`              | `the_session_is_the_attested_guests_and_m_unbound_is_refused` |
//! | `M_STALE`                | `an_epoch_fence_invalidates_a_pending_appraisal`              |
//! | `M_DOWNGRADE`            | `no_silent_downgrade_at_grant`                                |
//! | `M_RENEWLOW`, `M_LOWER`  | `m_lower_and_m_renewlow_are_refused`                          |
//! | `M_PROFILE`              | `contained_is_a_lookup_and_each_conjunct_matters`             |
//! | ADR-0034 §1 (domain)     | `a_run_seat_is_never_granted_on_a_build_profile`              |
//! | `NeverContested` at 1    | `a_contested_verdict_never_grants_and_revokes_the_principal`  |

use std::collections::{BTreeMap, BTreeSet};

use serde_json::{Value, json};
use topak_core::authentic::{self, KeyHex};
use topak_core::confine::*;
use topak_core::lease::Confinement;
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::*;

const VERIFIER: [u8; 32] = [7; 32];
const ROGUE: [u8; 32] = [9; 32];
const GUEST_A: [u8; 32] = [11; 32];
const GUEST_B: [u8; 32] = [12; 32];

fn pubkey(secret: &[u8; 32]) -> KeyHex {
    authentic::sign("key", &Value::Null, secret).key
}

fn persona() -> Digest {
    Digest::of(b"model.json")
}

fn seat(d: Domain, kind: SeatKind, key: &str, rung: u8) -> SeatDecl {
    SeatDecl { domain: d, kind, cell: None, key: key.into(), rung }
}

/// `w1` authors profiles at rung 0 and `o1` covers it, so a profile can be promoted. `c1` is
/// declared at rung 1, `c3` and `d3` at rung 3, `r3` is a Run seat at rung 3, `z0` is rung 0.
fn rules() -> Rules {
    Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats: BTreeMap::from([
            ("w1".into(), seat(Domain::Build, SeatKind::Thinker, "kw1", 0)),
            ("o1".into(), SeatDecl { cell: Some("w1".into()), ..seat(Domain::Build, SeatKind::Observer, "ko1", 0) }),
            ("g1".into(), seat(Domain::Build, SeatKind::Grant, "kg1", 0)),
            ("g2".into(), seat(Domain::Build, SeatKind::Grant, "kg2", 0)),
            ("g3".into(), seat(Domain::Build, SeatKind::Grant, "kg3", 0)),
            ("c1".into(), seat(Domain::Build, SeatKind::Thinker, "kc1", 1)),
            ("c3".into(), seat(Domain::Build, SeatKind::Thinker, "kc3", 3)),
            ("d3".into(), seat(Domain::Build, SeatKind::Thinker, "kd3", 3)),
            ("r3".into(), seat(Domain::Run, SeatKind::Thinker, "kr3", 3)),
            ("ro3".into(), SeatDecl { cell: Some("r3".into()), ..seat(Domain::Run, SeatKind::Observer, "kro3", 3) }),
            ("rz".into(), SeatDecl { cell: Some("r3".into()), ..seat(Domain::Run, SeatKind::Observer, "krz", 0) }),
            ("z0".into(), seat(Domain::Build, SeatKind::Thinker, "kz0", 0)),
        ]),
        grant_roster: ["g1", "g2", "g3"].into_iter().map(String::from).collect(),
        veto_roster: BTreeSet::new(),
        anchor_keys: BTreeSet::from(["kA".into()]),
        break_glass: None,
        erasure_roster: None,
        verifier_keys: BTreeSet::from([pubkey(&VERIFIER)]),
        bundle_keys: BTreeSet::new(),
        provider_keys: BTreeSet::new(),
        inside_targets: BTreeSet::new(),
        releasers: BTreeSet::new(),
        personas: BTreeMap::from([(persona(), Provenance::InHousePretrain)]),
        criterion: Some(Criterion {
            record: "ADR-0035 (test)".into(),
            independence_table: Digest::of(b"table"),
            floor_values: Digest::of(b"theta"),
        }),
    }
}

fn params() -> Params {
    Params {
        corpus: BTreeSet::new(),
        build_tools: BTreeSet::new(),
        run_tools: BTreeSet::new(),
        run_root: BTreeSet::new(),
        wasm_tools: BTreeSet::from([WASM_TOOL.to_string()]),
        round_bound: 8,
        lease_margin_ms: 0,
        after_topic_limit: 3,
        run_round_bound: None,
    }
}

fn state_with(r: Rules) -> State {
    let mut s = State::genesis(r, 2).unwrap();
    s.trace = topak_core::trace::name_from_env("conf");
    s
}

/// A profile file: every clause passes unless `fail` names one, with P7's values.
const WASM_TOOL: &str = "valve@wasm";
const NATIVE_TOOL: &str = "valve@native";

/// A Run profile (ADR-0034 A2, pending): every clause passes but P4, which is `p4`.
fn run_profile_text(p4: ClauseVerdict) -> String {
    let mut v: Value = serde_json::from_str(&profile_text(&[], p4)).unwrap();
    v["domain"] = json!("run");
    serde_json::to_string_pretty(&v).unwrap()
}

fn profile_text(fail: &[Clause], p4: ClauseVerdict) -> String {
    let clauses: BTreeMap<String, Value> = Clause::ALL
        .iter()
        .map(|c| {
            let v = if fail.contains(c) {
                "fail"
            } else if *c == Clause::P4 {
                p4.as_str()
            } else {
                "pass"
            };
            (format!("{c:?}"), json!({ "verdict": v, "why": "test" }))
        })
        .collect();
    let subtractions: BTreeMap<String, &str> = fail.iter().map(|c| (format!("{c:?}"), "remove it")).collect();
    serde_json::to_string_pretty(&json!({
        "_what": "test profile",
        "image": Digest::of(b"image"),
        "launch": { "kind": "sim-cvm" },
        "channel": { "kind": "stdio" },
        "persona": { "model_json_sha256": persona() },
        "reference": { "launch_measurement": "m-good", "min_tcb": 5 },
        "clauses": clauses,
        "subtractions": subtractions,
    }))
    .unwrap()
}

fn admit_entry(id: &str, seat: &str, lease: LogIndex, action: Admitted, session: Option<SessionProof>) -> Entry {
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
            params: params().digest(),
            decided_by: 1,
            session,
            labels: Some(Default::default()),
        },
    }
}

/// A log the test writes into, one index per entry.
struct Log {
    s: State,
    at: LogIndex,
    round: Round,
}

impl Log {
    fn new(r: Rules) -> Self {
        Log { s: state_with(r), at: 0, round: 0 }
    }

    fn apply(&mut self, e: Entry) -> Applied {
        self.at += 1;
        self.s.apply(self.at, &e, &params())
    }

    fn id(&self, what: &str) -> String {
        format!("{what}-{}", self.at + 1)
    }

    fn grant_plain(&mut self, seat: &str, role: RoundRole, alphabet: &[ActionKind]) -> LogIndex {
        self.round += 1;
        let req = GrantRequest {
            principal: format!("p-{seat}-{}", self.round),
            seat: seat.into(),
            persona: Digest::of(b"author persona"),
            bundle: Digest::of(b"bundle"),
            confinement: Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: alphabet.iter().copied().collect(),
            ttl_ms: 1000,
            round: self.round,
            role,
            task_label: None,
            task_labels_allowed: None,
            sign_on: None,
        };
        let id = self.id("g");
        match self.apply(Entry::Grant { id, req, appraisal: None }) {
            Applied::LeaseGranted { fence } => fence,
            a => panic!("grant refused: {a:?}"),
        }
    }

    /// ADR-0034 §1: submit the single-file workspace, pass the gates, three grants, and register.
    fn promote_and_register(&mut self, text: &str) -> (Digest, Applied) {
        let artifact = profile_artifact(text.as_bytes());
        let f = self.grant_plain("w1", RoundRole::Author, &[ActionKind::Submit]);
        let id = self.id("submit");
        let a = self.apply(admit_entry(&id, "w1", f, Admitted::Submit { artifact: artifact.clone() }, None));
        assert!(matches!(a, Applied::Admitted { .. }), "{a:?}");
        let evidence = Digest::of(b"gates");
        let id = self.id("gates");
        self.apply(Entry::GatesPassed { id, artifact: artifact.clone(), evidence: evidence.clone() });
        for g in ["g1", "g2", "g3"] {
            let f = self.grant_plain(g, RoundRole::Voter, &[ActionKind::Vote]);
            let vote = Admitted::Vote {
                verdict: Verdict::Grant,
                artifact: artifact.clone(),
                evidence: evidence.clone(),
                rules_epoch: 0,
            };
            let id = self.id("vote");
            self.apply(admit_entry(&id, g, f, vote, None));
        }
        assert!(self.s.candidates[&artifact].promoted_at.is_some(), "the profile's artifact promotes");
        self.register(text)
    }

    fn register(&mut self, text: &str) -> (Digest, Applied) {
        let id = self.id("reg");
        (Digest::of(text.as_bytes()), self.apply(Entry::ProfileRegister { id, profile: text.into() }))
    }
}

/// What a grant at `rung` for `principal` on `profile` asks the appraiser to attest.
struct Ask {
    rung: u8,
    principal: String,
    round: Round,
    profile: Digest,
    nonce_epoch: Epoch,
    nonce_index: LogIndex,
    verdict: Appraised,
    session: Option<[u8; 32]>,
    measurement: Option<String>,
    tcb: Option<u64>,
    instance: Digest,
    signer: Option<[u8; 32]>,
}

impl Ask {
    fn new(log: &Log, rung: u8, principal: &str, profile: &Digest) -> Self {
        Ask {
            rung,
            principal: principal.into(),
            round: 1,
            profile: profile.clone(),
            nonce_epoch: log.s.epoch,
            nonce_index: log.s.last_applied,
            verdict: Appraised::Attested,
            session: (rung >= 2).then_some(GUEST_A),
            measurement: (rung >= 2).then(|| "m-good".into()),
            tcb: (rung >= 2).then_some(5),
            instance: Digest::of(b"guest-a"),
            signer: (rung == 3).then_some(VERIFIER),
        }
    }

    fn appraisal(&self) -> Appraisal {
        let statement = AppraisalStatement {
            nonce: NonceInput {
                epoch: self.nonce_epoch,
                index: self.nonce_index,
                principal: self.principal.clone(),
                round: self.round,
            },
            profile: self.profile.clone(),
            persona: persona(),
            rung: self.rung,
            verdict: self.verdict,
            evidence: Digest::of(b"evidence"),
            session_key: self.session.as_ref().map(pubkey),
            measurement: self.measurement.clone(),
            tcb: self.tcb,
            platform: if self.rung == 1 { PLATFORM_LAUNCHER.into() } else { PLATFORM_SIM_SNP.into() },
        };
        let body = serde_json::to_value(&statement).unwrap();
        let signature = self.signer.map(|k| authentic::sign(APPRAISAL_PURPOSE, &body, &k));
        Appraisal { statement, instance: self.instance.clone(), signature }
    }

    fn grant_req(&self, seat: &str, alphabet: &[ActionKind]) -> GrantRequest {
        GrantRequest {
            principal: self.principal.clone(),
            seat: seat.into(),
            persona: persona(),
            bundle: Digest::of(b"bundle"),
            confinement: Confinement { digest: self.profile.clone(), rung: self.rung },
            alphabet: alphabet.iter().copied().collect(),
            ttl_ms: 1000,
            round: self.round,
            role: RoundRole::Author,
            task_label: None,
            task_labels_allowed: None,
            sign_on: None,
        }
    }

    fn grant(&self, log: &mut Log, seat: &str, alphabet: &[ActionKind]) -> Applied {
        let id = log.id("cg");
        log.apply(Entry::Grant { id, req: self.grant_req(seat, alphabet), appraisal: Some(self.appraisal()) })
    }
}

const BUILD: &[ActionKind] = &[ActionKind::Read, ActionKind::Draft, ActionKind::Emit, ActionKind::Submit];

fn rejected(a: &Applied, needle: &str) -> bool {
    matches!(a, Applied::Rejected(r) if r.contains(needle))
}

fn proof(secret: &[u8; 32], fence: LogIndex, ctr: u64) -> SessionProof {
    let op = Digest::of(format!("op-{ctr}").as_bytes());
    let s = authentic::sign(AGENT_OP_PURPOSE, &session_body(fence, 0, ctr, &op), secret);
    SessionProof { ctr, op, sig: s.sig }
}

fn read() -> Admitted {
    Admitted::Read { object: Digest::of(b"x") }
}

// ---- the profile is a promoted artifact (ADR-0034 §1) ------------------------------------------

#[test]
fn only_a_promoted_well_formed_build_profile_is_a_reference_value() {
    let mut log = Log::new(rules());
    let text = profile_text(&[], ClauseVerdict::Vacuous);
    let (_, a) = log.register(&text);
    assert!(rejected(&a, "not promoted"), "a digest nobody promoted is not a reference value: {a:?}");
    let (d, a) = log.promote_and_register(&text);
    assert_eq!(a, Applied::ProfileRegistered { digest: d.clone() });
    // A grant naming an unregistered profile is refused at apply.
    let ask = Ask::new(&log, 3, "p-c3", &Digest::of(b"unregistered"));
    assert!(rejected(&ask.grant(&mut log, "c3", BUILD), "not registered"));

    // Malformed: a missing clause, or a failure with no subtraction.
    let mut v: Value = serde_json::from_str(&text).unwrap();
    v["clauses"].as_object_mut().unwrap().remove("P6");
    let missing = serde_json::to_string(&v).unwrap();
    assert!(rejected(&log.promote_and_register(&missing).1, "P6 is missing"));
    let mut v: Value = serde_json::from_str(&profile_text(&[Clause::P3], ClauseVerdict::Vacuous)).unwrap();
    v["subtractions"] = json!({});
    let silent = serde_json::to_string(&v).unwrap();
    assert!(rejected(&log.promote_and_register(&silent).1, "names no subtraction"));
    // A Run profile registers (ADR-0034 A2, pending; PROVISIONAL run-profile).
    let run = run_profile_text(ClauseVerdict::Pass);
    let (d, a) = log.promote_and_register(&run);
    assert_eq!(a, Applied::ProfileRegistered { digest: d });
}

#[test]
fn the_reference_profile_on_disk_parses_and_declares_its_failures() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../../slm/serve/profile-host-rung0.json");
    let text = std::fs::read_to_string(path).unwrap();
    let p = Profile::parse(&text).unwrap();
    assert!(p.check_well_formed().is_empty(), "{:?}", p.check_well_formed());
    assert!(p.check_for_rung(1).is_err(), "a host process has no image to appraise at rung 1");
    let fails = p.meets_p3_p5(&BTreeSet::new());
    assert_eq!(fails.len(), 1, "P3 fails; P4 is vacuous without Invoke; P5 passes: {fails:?}");
}

// ---- appraisal at grant (ADR-0034 §3) --------------------------------------------------------

#[test]
fn an_attested_rung_3_grant_binds_the_guest_and_is_contained() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log, 3, "p-c3", &d);
    let a = ask.grant(&mut log, "c3", BUILD);
    let Applied::LeaseGranted { fence } = a else { panic!("{a:?}") };
    let att = log.s.leases[&fence].attestation.clone().unwrap();
    assert_eq!(att.verified_by, Some(pubkey(&VERIFIER)), "item 15: the issued verifier key is read");
    assert_eq!(att.session_key, Some(pubkey(&GUEST_A)));
    let c = log.s.contained(fence);
    assert!(c.contained && c.simulated, "{c:?}");
}

#[test]
fn a_rung_1_grant_is_the_launchers_assertion() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let mut ask = Ask::new(&log, 1, "p-c1", &d);
    ask.signer = Some(VERIFIER);
    let Applied::LeaseGranted { fence } = ask.grant(&mut log, "c1", BUILD) else { panic!() };
    let c = log.s.contained(fence);
    assert!(c.contained && !c.simulated, "ADR-0034 §4: rung ≥ 1 at the declared rung: {c:?}");
}

#[test]
fn a_contested_verdict_never_grants_and_revokes_the_principal() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let mut ask = Ask::new(&log, 3, "p-c3", &d);
    ask.verdict = Appraised::Contested;
    ask.measurement = Some("m-rogue".into());
    // M_CONTESTED: Contested treated as Attested.
    assert!(rejected(&ask.grant(&mut log, "c3", BUILD), "only Attested"));
    // Unsigned, or signed by a key the rules do not issue: refused, and nobody is revoked.
    let unsigned = Appraisal { signature: None, ..ask.appraisal() };
    let id = log.id("ct");
    let a = log.apply(Entry::Contested { id, appraisal: unsigned, attribution: "test".into() });
    assert!(rejected(&a, "issued verifier key"), "{a:?}");
    ask.signer = Some(ROGUE);
    let id = log.id("ct");
    assert!(rejected(
        &log.apply(Entry::Contested { id, appraisal: ask.appraisal(), attribution: "t".into() }),
        "issued"
    ));
    // NeverContested at rung 1: the launcher has no measurement to diverge from.
    let mut one = Ask::new(&log, 1, "p-c1", &d);
    one.verdict = Appraised::Contested;
    let id = log.id("ct");
    assert!(rejected(
        &log.apply(Entry::Contested { id, appraisal: one.appraisal(), attribution: "t".into() }),
        "rungs 0 and 1"
    ));
    assert!(log.s.contested.is_empty() && log.s.revoked.is_empty());

    // ContestedStopped: the principal is revoked, permanently, with the evidence; not the profile.
    ask.signer = Some(VERIFIER);
    let id = log.id("ct");
    let a = log.apply(Entry::Contested { id, appraisal: ask.appraisal(), attribution: "verifier".into() });
    assert_eq!(a, Applied::Contested { ended: 0 });
    assert_eq!(log.s.contested.get("p-c3"), Some(&Digest::of(b"evidence")));
    let honest = Ask::new(&log, 3, "p-c3", &d);
    assert!(rejected(&honest.grant(&mut log, "c3", BUILD), "revoked"), "the principal's next guest too");
    let other = Ask::new(&log, 3, "p-d3", &d);
    assert!(matches!(other.grant(&mut log, "d3", BUILD), Applied::LeaseGranted { .. }), "the profile is not revoked");
}

#[test]
fn a_contested_verdict_ends_a_live_lease() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log, 3, "p-c3", &d);
    let Applied::LeaseGranted { fence } = ask.grant(&mut log, "c3", BUILD) else { panic!() };
    let mut renewal = Ask::new(&log, 3, "p-c3", &d);
    renewal.verdict = Appraised::Contested;
    let id = log.id("ct");
    let a = log.apply(Entry::Contested { id, appraisal: renewal.appraisal(), attribution: "renewal".into() });
    assert_eq!(a, Applied::Contested { ended: 1 });
    assert_eq!(log.s.leases[&fence].ended, Some(EndReason::Revoked));
}

#[test]
fn no_silent_downgrade_at_grant() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    // M_DOWNGRADE: an Unattestable principal granted at rung 0 on a seat declared rung 3.
    let mut low = Ask::new(&log, 3, "p-c3", &d).grant_req("c3", BUILD);
    low.confinement.rung = 0;
    let id = log.id("g");
    assert!(rejected(&log.apply(Entry::Grant { id, req: low, appraisal: None }), "declared rung"));
    // At the declared rung, no appraisal and an Unattestable one are both refused.
    let ask = Ask::new(&log, 3, "p-c3", &d);
    let id = log.id("g");
    let a = log.apply(Entry::Grant { id, req: ask.grant_req("c3", BUILD), appraisal: None });
    assert!(rejected(&a, "carries its appraisal"));
    let mut un = Ask::new(&log, 3, "p-c3", &d);
    un.verdict = Appraised::Unattestable;
    assert!(rejected(&un.grant(&mut log, "c3", BUILD), "only Attested"));
    // A rung-0 grant rests on nothing.
    let mut z = Ask::new(&log, 0, "p-z0", &d);
    z.signer = None;
    assert!(rejected(&z.grant(&mut log, "z0", BUILD), "rung-0 grant"));
}

#[test]
fn rung_3_is_appraised_by_an_issued_verifier_against_the_profile() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    type Alter = Box<dyn Fn(&mut Ask)>;
    let cases: Vec<(&str, Alter)> = vec![
        ("issued verifier key", Box::new(|a: &mut Ask| a.signer = Some(ROGUE))),
        ("issued verifier key", Box::new(|a: &mut Ask| a.signer = None)),
        ("reference value", Box::new(|a: &mut Ask| a.measurement = Some("m-other".into()))),
        ("below the profile's minimum", Box::new(|a: &mut Ask| a.tcb = Some(4))),
        ("bind a session key", Box::new(|a: &mut Ask| a.session = None)),
        ("another principal", Box::new(|a: &mut Ask| a.principal = "p-else".into())),
        ("another profile", Box::new(|a: &mut Ask| a.profile = Digest::of(b"other"))),
    ];
    for (needle, f) in cases {
        let mut ask = Ask::new(&log, 3, "p-c3", &d);
        f(&mut ask);
        // The request names the honest principal and profile; only the appraisal is altered.
        let honest = Ask::new(&log, 3, "p-c3", &d);
        let id = log.id("g");
        let a = log.apply(Entry::Grant { id, req: honest.grant_req("c3", BUILD), appraisal: Some(ask.appraisal()) });
        assert!(rejected(&a, needle), "{needle}: {a:?}");
    }
    // The nonce is from the log before this entry.
    let mut ask = Ask::new(&log, 3, "p-c3", &d);
    ask.nonce_index = log.at + 1;
    assert!(rejected(&ask.grant(&mut log, "c3", BUILD), "not from the log"));
    // Rung 2 is a seam.
    let mut r2 = rules();
    r2.seats.get_mut("c1").unwrap().rung = 2;
    let mut log2 = Log::new(r2);
    let (d2, _) = log2.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log2, 2, "p-c1", &d2);
    assert!(rejected(&ask.grant(&mut log2, "c1", BUILD), "rung 2"));
}

#[test]
fn a_rung_3_seat_needs_an_issued_verifier() {
    let mut r = rules();
    r.verifier_keys.clear();
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("no verifier key")));
    let mut r = rules();
    r.seats.get_mut("c3").unwrap().rung = 4;
    assert!(check_well_formed(&r).iter().any(|v| v.detail.contains("above 3")));
}

// ---- freshness, binding, renewal (ADR-0034 §3.5, §3.6) -----------------------------------------

#[test]
fn an_epoch_fence_invalidates_a_pending_appraisal() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    // Appraised at epoch 0; the fleet fence lands before the grant commits. M_STALE.
    let ask = Ask::new(&log, 3, "p-c3", &d);
    let id = log.id("fence");
    log.apply(Entry::EpochIncrement { id, reason: "test".into(), attribution: "test".into() });
    assert!(rejected(&ask.grant(&mut log, "c3", BUILD), "fenced"));
    let fresh = Ask::new(&log, 3, "p-c3", &d);
    assert!(matches!(fresh.grant(&mut log, "c3", BUILD), Applied::LeaseGranted { .. }));
}

#[test]
fn the_session_is_the_attested_guests_and_m_unbound_is_refused() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log, 3, "p-c3", &d);
    let Applied::LeaseGranted { fence } = ask.grant(&mut log, "c3", BUILD) else { panic!() };
    let id = log.id("a");
    assert!(rejected(&log.apply(admit_entry(&id, "c3", fence, read(), None)), "signed nothing"), "no proof");
    let id = log.id("a");
    let a = log.apply(admit_entry(&id, "c3", fence, read(), Some(proof(&GUEST_B, fence, 1))));
    assert!(rejected(&a, "not the attested guest's"), "another guest's key: {a:?}");
    let id = log.id("a");
    assert!(matches!(
        log.apply(admit_entry(&id, "c3", fence, read(), Some(proof(&GUEST_A, fence, 1)))),
        Applied::Admitted { .. }
    ));
    let id = log.id("a");
    assert!(rejected(&log.apply(admit_entry(&id, "c3", fence, read(), Some(proof(&GUEST_A, fence, 1)))), "replayed"));
    assert_eq!(log.s.leases[&fence].session_ctr, 1);
}

#[test]
fn renewal_re_attests_the_same_guest() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log, 3, "p-c3", &d);
    let Applied::LeaseGranted { fence } = ask.grant(&mut log, "c3", BUILD) else { panic!() };
    let id = log.id("a");
    log.apply(admit_entry(&id, "c3", fence, read(), Some(proof(&GUEST_A, fence, 1))));
    let req =
        |rung| RenewRequest { seat: "c3".into(), fence, alphabet: BUILD.iter().copied().collect(), rung, ttl_ms: 900 };
    let renew = |log: &mut Log, a: Option<Appraisal>, rung| {
        let id = log.id("r");
        log.apply(Entry::Renew { id, req: req(rung), appraisal: a })
    };
    // Every renewal re-attests: a token-only renewal of an attested lease is refused.
    assert!(rejected(&renew(&mut log, None, 3), "fresh appraisal"));
    // The grant's nonce is older than the lease: not fresh.
    assert!(rejected(&renew(&mut log, Some(ask.appraisal()), 3), "not from the log"));
    // Another guest, under its own key or under a new instance: not the lease's.
    let mut b = Ask::new(&log, 3, "p-c3", &d);
    b.session = Some(GUEST_B);
    assert!(rejected(&renew(&mut log, Some(b.appraisal()), 3), "another guest"));
    let mut b = Ask::new(&log, 3, "p-c3", &d);
    b.instance = Digest::of(b"guest-b");
    assert!(rejected(&renew(&mut log, Some(b.appraisal()), 3), "another guest"));
    // Same guest, fresh nonce: renewed at the same rung, the counter carried.
    let same = Ask::new(&log, 3, "p-c3", &d);
    let Applied::Renewed { fence: f2 } = renew(&mut log, Some(same.appraisal()), 3) else { panic!() };
    assert_eq!(log.s.leases[&f2].lease.confinement.rung, 3);
    assert_eq!(log.s.leases[&f2].session_ctr, 1);
    assert_eq!(log.s.leases[&f2].attestation.as_ref().unwrap().nonce_index, same.nonce_index);
    let id = log.id("a");
    assert!(rejected(&log.apply(admit_entry(&id, "c3", f2, read(), Some(proof(&GUEST_A, f2, 1)))), "replayed"));
}

#[test]
fn m_lower_and_m_renewlow_are_refused() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log, 1, "p-c1", &d);
    let Applied::LeaseGranted { fence } = ask.grant(&mut log, "c1", BUILD) else { panic!() };
    let req =
        |rung| RenewRequest { seat: "c1".into(), fence, alphabet: BUILD.iter().copied().collect(), rung, ttl_ms: 900 };
    // Lease_A1.tla M_LOWER: a lower rung, with or without an appraisal.
    let id = log.id("r");
    assert!(rejected(&log.apply(Entry::Renew { id, req: req(0), appraisal: None }), "confinement rung"));
    let id = log.id("r");
    let fresh = Ask::new(&log, 1, "p-c1", &d);
    assert!(rejected(&log.apply(Entry::Renew { id, req: req(0), appraisal: Some(fresh.appraisal()) }), "rung"));
    // M_RENEWLOW: an Unattestable renewal is not kept at any rung. The lease lapses instead.
    let mut un = Ask::new(&log, 1, "p-c1", &d);
    un.verdict = Appraised::Unattestable;
    let id = log.id("r");
    assert!(rejected(&log.apply(Entry::Renew { id, req: req(1), appraisal: Some(un.appraisal()) }), "only Attested"));
    assert_eq!(log.s.live_by_seat["c1"], fence);
    let fresh = Ask::new(&log, 1, "p-c1", &d);
    let id = log.id("r");
    assert!(matches!(
        log.apply(Entry::Renew { id, req: req(1), appraisal: Some(fresh.appraisal()) }),
        Applied::Renewed { .. }
    ));
}

// ---- Contained(p) (ADR-0034 §4) ----------------------------------------------------------------

#[test]
fn contained_is_a_lookup_and_each_conjunct_matters() {
    // M_PROFILE: `Contained` ignoring the profile. Each failing conjunct alone is enough.
    let contained = |r: Rules, fail: &[Clause], p4, seat: &str, alphabet: &[ActionKind]| {
        let mut log = Log::new(r);
        let (d, _) = log.promote_and_register(&profile_text(fail, p4));
        let ask = Ask::new(&log, 3, &format!("p-{seat}"), &d);
        let a = ask.grant(&mut log, seat, alphabet);
        let Applied::LeaseGranted { fence } = a else { panic!("{a:?}") };
        log.s.contained(fence)
    };
    let with_invoke = &[ActionKind::Read, ActionKind::Invoke, ActionKind::Submit];
    assert!(contained(rules(), &[], ClauseVerdict::Vacuous, "c3", BUILD).contained);
    assert!(contained(rules(), &[], ClauseVerdict::Pass, "c3", with_invoke).contained);
    let mediated = |c: Containment, why: &str| {
        assert!(!c.contained && c.because.iter().any(|r| r.contains(why)), "{why}: {c:?}");
    };
    mediated(contained(rules(), &[Clause::P3], ClauseVerdict::Vacuous, "c3", BUILD), "P3");
    mediated(contained(rules(), &[], ClauseVerdict::Vacuous, "c3", with_invoke), "holds Invoke");
    mediated(contained(rules(), &[Clause::P5], ClauseVerdict::Vacuous, "c3", BUILD), "P5");
    let mut external = rules();
    external.personas.insert(persona(), Provenance::AttestedExternal);
    mediated(contained(external, &[], ClauseVerdict::Vacuous, "c3", BUILD), "in house");
    let mut no_criterion = rules();
    no_criterion.criterion = None;
    mediated(contained(no_criterion, &[], ClauseVerdict::Vacuous, "c3", BUILD), "criterion");
}

/// ADR-0034 §1: Build and Run share the schema, not the profile. A Run seat is refused a grant
/// on a Build profile at apply, and no Run profile can be registered (ADR-0042 §6, Proposed): so
/// a Run principal is never granted above rung 0, and `contained`'s Run conjunct is a second
/// guard that apply leaves unreachable.
#[test]
fn a_run_seat_is_never_granted_on_a_build_profile() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let ask = Ask::new(&log, 3, "p-r3", &d);
    let a = ask.grant(&mut log, "r3", &[ActionKind::Consult, ActionKind::Report]);
    assert!(rejected(&a, "does not confine a run seat"), "{a:?}");
    assert!(!log.s.live_by_seat.contains_key("r3"));
}

#[test]
fn a_contained_lease_stops_being_contained_when_it_ends() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&profile_text(&[], ClauseVerdict::Vacuous));
    let Applied::LeaseGranted { fence } = Ask::new(&log, 3, "p-c3", &d).grant(&mut log, "c3", BUILD) else { panic!() };
    assert!(log.s.contained(fence).contained);
    // Item 17: a withdrawn reference value fences live leases by profile digest.
    let id = log.id("w");
    let a = log.apply(Entry::Revoke {
        id,
        target: RevocationTarget::Confinement(d.clone()),
        reason: "firmware withdrawn".into(),
        attribution: "custodian".into(),
    });
    assert_eq!(a, Applied::Revoked { ended: 1 });
    assert!(!log.s.contained(fence).contained);
    let again = Ask::new(&log, 3, "p-d3", &d);
    assert!(rejected(&again.grant(&mut log, "d3", BUILD), "revoked"), "the profile is barred");
}

#[test]
fn rules_without_the_new_fields_keep_their_bytes() {
    // A rules file written before confinement serializes as it did: chain digests and issuance
    // signatures over it do not move.
    let mut r = rules();
    r.personas.clear();
    r.criterion = None;
    for d in r.seats.values_mut() {
        d.rung = 0;
    }
    let v = serde_json::to_value(&r).unwrap();
    assert!(v.get("personas").is_none() && v.get("criterion").is_none());
    assert!(v["seats"]["c3"].get("rung").is_none());
    let back: Rules = serde_json::from_value(v).unwrap();
    assert_eq!(back, r);
}

// ---- Run (ADR-0034 A2, pending: P4 for Run is channel fidelity) ---------------------------------

const RUN_THINKER: &[ActionKind] = &[ActionKind::Consult, ActionKind::Actuate, ActionKind::Report];
const RUN_OBSERVER: &[ActionKind] = &[ActionKind::Consult, ActionKind::Report];

#[test]
fn a_run_seat_on_a_run_profile_is_contained_with_p4_as_channel_fidelity() {
    let mut log = Log::new(rules());
    let (pass, _) = log.promote_and_register(&run_profile_text(ClauseVerdict::Pass));
    let Applied::LeaseGranted { fence } = Ask::new(&log, 3, "p-r3", &pass).grant(&mut log, "r3", RUN_THINKER) else {
        panic!()
    };
    let c = log.s.contained(fence);
    assert!(c.contained, "{c:?}");

    // A Run profile that declares P4 vacuous does not cover a seat that can `Actuate`: D-0034-6.
    let mut log = Log::new(rules());
    let (vac, _) = log.promote_and_register(&run_profile_text(ClauseVerdict::Vacuous));
    let Applied::LeaseGranted { fence } = Ask::new(&log, 3, "p-r3", &vac).grant(&mut log, "r3", RUN_THINKER) else {
        panic!()
    };
    let c = log.s.contained(fence);
    assert!(!c.contained && c.because.iter().any(|r| r.contains("holds Actuate")), "{c:?}");
    // An Observer reaches no tool: P4 holds vacuously, as for a Build seat without `Invoke`.
    let Applied::LeaseGranted { fence } = Ask::new(&log, 3, "p-ro3", &vac).grant(&mut log, "ro3", RUN_OBSERVER) else {
        panic!()
    };
    assert!(log.s.contained(fence).contained);
    // And a Build seat is not granted on a Run profile (ADR-0034 §1).
    assert!(rejected(&Ask::new(&log, 3, "p-c3", &vac).grant(&mut log, "c3", BUILD), "does not confine a build seat"));
}

/// The Run counterpart of `M_PROFILE`: a native tool under a lease whose Run profile says P4
/// passes (A2's `M_NATIVE`). Refused at apply, on every replica, so the claim is not a declaration.
#[test]
fn channel_fidelity_is_checked_at_apply() {
    let mut log = Log::new(rules());
    let (d, _) = log.promote_and_register(&run_profile_text(ClauseVerdict::Pass));
    let Applied::LeaseGranted { fence } = Ask::new(&log, 3, "p-r3", &d).grant(&mut log, "r3", RUN_THINKER) else {
        panic!()
    };
    // The cell Observer holds a live lease, so the coupling at apply (ADR-0039 §2) is met.
    log.grant_plain("rz", RoundRole::Author, RUN_OBSERVER);
    let actuate = |tool: &str| Admitted::Actuate { tool: tool.into(), inputs: Digest::of(b"in"), break_glass: false };
    let id = log.id("a");
    let a = log.apply(admit_entry(&id, "r3", fence, actuate(NATIVE_TOOL), Some(proof(&GUEST_A, fence, 1))));
    assert!(rejected(&a, "not held to its declared channel"), "M_NATIVE: {a:?}");
    let id = log.id("a");
    let a = log.apply(admit_entry(&id, "r3", fence, actuate(WASM_TOOL), Some(proof(&GUEST_A, fence, 1))));
    assert!(matches!(a, Applied::Admitted { .. }), "{a:?}");
    // A Run profile that declares P4 `fail` claims nothing: a native tool is admitted, and the
    // principal is `Mediated` (D-0034-6).
    let mut log = Log::new(rules());
    let (f, _) = log.promote_and_register(&{
        let mut v: Value = serde_json::from_str(&profile_text(&[Clause::P4], ClauseVerdict::Pass)).unwrap();
        v["domain"] = json!("run");
        serde_json::to_string(&v).unwrap()
    });
    let Applied::LeaseGranted { fence } = Ask::new(&log, 3, "p-r3", &f).grant(&mut log, "r3", RUN_THINKER) else {
        panic!()
    };
    log.grant_plain("rz", RoundRole::Author, RUN_OBSERVER);
    let id = log.id("a");
    let a = log.apply(admit_entry(&id, "r3", fence, actuate(NATIVE_TOOL), Some(proof(&GUEST_A, fence, 1))));
    assert!(matches!(a, Applied::Admitted { .. }), "{a:?}");
    assert!(!log.s.contained(fence).contained);
}
