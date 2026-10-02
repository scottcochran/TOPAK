//! The launcher in the node (ADR-0036 §6), end to end: three replicas, the pinned floor, the
//! scripted occupant as the guest. Rung 1 is a real host-process launch; rung 3 is SIMULATED
//! (`topak-contain` `sim`): the platform and the verifier are keys this test made, and the
//! `contained = true` it reaches is a witness that the lookup is reachable, not a confinement claim.
//!
//! | Test                                         | What it shows                                         |
//! |----------------------------------------------|-------------------------------------------------------|
//! | `rung_1_honest_round_and_its_refusals`       | ADR-0036 §7: one honest round, `Mediated` by P3; three refusals |
//! | `a_guest_that_cannot_verify_its_bundle_...`  | ADR-0036 §7's second refusal                          |
//! | `simulated_rung_3_round_is_contained_...`    | F28: honest round, `contained = true`; rung 0 beside it |
//! | `without_the_criterion_nothing_is_contained` | ADR-0034 §4's last conjunct                            |
//! | `a_run_seat_launches_nothing`                | ADR-0034 §1: a Build profile confines no Run seat     |
//! | `a_rogue_image_is_contested_...`             | F10, F28: Contested ends in a revoked principal       |
//! | `an_unreachable_verifier_grants_nothing`     | F14, F28: PC/EC                                       |
//! | `an_epoch_fence_voids_a_pending_appraisal`   | F13, `M_STALE`                                        |
//! | `the_session_is_the_attested_guests`         | F12, `M_UNBOUND` at decide                            |
//! | `renewal_re_attests_and_lapses_...`          | F11, F13                                              |
//! | `every_host_power_subtracts`                 | F23, ADR-0034 §5; `M_HOST` at rung 1                  |
//! | `withdrawing_a_profile_fences_its_leases`    | F17                                                   |

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use serde_json::{Value, json};
use tokio::sync::{Semaphore, mpsc};
use topak_contain::BoxFuture;
use topak_contain::appraise::{Appraiser, LauncherAssertion};
use topak_contain::backend::*;
use topak_contain::guest::{GuestEvidence, GuestHello};
use topak_contain::sim::{SimCvmBackend, SimPlatform, SimVerifier};
use topak_core::action::Action;
use topak_core::admit::BundleOutcome;
use topak_core::confine::*;
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::*;
use topak_floor::Floor;
use topak_mcp::proto::{AgentOp, AgentRequest};
use topak_mcp::toolhost::ToolHost;
use topak_node::driver::Driver;
use topak_node::mechanism::{BundleDecider, Contain, Mechanism, Parts};
use topak_node::net::{ChannelNet, Hub};
use topak_node::ops::OperatorOp;
use topak_transport::{Memory, Transport};

const BUILD: &[ActionKind] = &[ActionKind::Read, ActionKind::Draft, ActionKind::Emit, ActionKind::Submit];
const LONG: u64 = 60_000;

fn guest_bin() -> PathBuf {
    // The demo guest is topak-contain's binary; cargo builds it into the same target directory.
    let me = std::env::current_exe().unwrap();
    let bin = me.parent().unwrap().parent().unwrap().join("topak-demo-guest");
    assert!(bin.exists(), "build the guest first: cargo build -p topak-contain --bins (same profile as the tests)");
    bin
}

struct Fx {
    dir: PathBuf,
    corpus_obj: Digest,
    params: Params,
    rules: Rules,
    model: PathBuf,
    corrupt_model: PathBuf,
    persona: Digest,
    verifier_secret: [u8; 32],
    chip_secret: [u8; 32],
    round: AtomicU64,
}

impl Fx {
    fn next_round(&self) -> Round {
        self.round.fetch_add(1, Ordering::SeqCst) + 1
    }
}

fn persona_bundle(dir: &Path, name: &str, corrupt: bool) -> PathBuf {
    let d = dir.join(name);
    std::fs::create_dir_all(&d).unwrap();
    let weights = b"weights of an in-house model";
    std::fs::write(d.join("weights.bin"), if corrupt { &b"swapped weights"[..] } else { &weights[..] }).unwrap();
    let model =
        json!({ "family": "demo", "params": 1000, "weights": "weights.bin", "weights_sha256": Digest::of(weights) });
    std::fs::write(d.join("model.json"), serde_json::to_vec(&model).unwrap()).unwrap();
    d.join("model.json")
}

fn fixture(name: &str, criterion: bool) -> Fx {
    let dir = std::env::temp_dir().join(format!("topak-contain-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("corpus")).unwrap();
    let content = b"---- MODULE Confinement ----\n";
    let corpus_obj = Digest::of(content);
    std::fs::write(dir.join("corpus").join(&corpus_obj.0), content).unwrap();
    let model = persona_bundle(&dir, "persona", false);
    let corrupt_model = persona_bundle(&dir, "corrupt", true);
    let persona = Digest::of(&std::fs::read(&model).unwrap());
    let verifier_secret: [u8; 32] = rand::random();
    let chip_secret: [u8; 32] = rand::random();
    let vkey = SimVerifier::new(verifier_secret, String::new()).key();
    let seat = |d: Domain, k: SeatKind, rung: u8| SeatDecl {
        domain: d,
        kind: k,
        cell: None,
        key: hex::encode(rand::random::<[u8; 32]>()),
        rung,
    };
    let rules = Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats: BTreeMap::from([
            ("w1".into(), seat(Domain::Build, SeatKind::Thinker, 0)),
            ("o1".into(), SeatDecl { cell: Some("w1".into()), ..seat(Domain::Build, SeatKind::Observer, 0) }),
            ("g1".into(), seat(Domain::Build, SeatKind::Grant, 0)),
            ("g2".into(), seat(Domain::Build, SeatKind::Grant, 0)),
            ("g3".into(), seat(Domain::Build, SeatKind::Grant, 0)),
            ("c1".into(), seat(Domain::Build, SeatKind::Thinker, 1)),
            ("c3".into(), seat(Domain::Build, SeatKind::Thinker, 3)),
            ("d3".into(), seat(Domain::Build, SeatKind::Thinker, 3)),
            ("z0".into(), seat(Domain::Build, SeatKind::Thinker, 0)),
            ("r3".into(), seat(Domain::Run, SeatKind::Thinker, 3)),
        ]),
        grant_roster: ["g1", "g2", "g3"].into_iter().map(String::from).collect(),
        veto_roster: BTreeSet::new(),
        anchor_keys: BTreeSet::from([hex::encode(rand::random::<[u8; 32]>())]),
        break_glass: None,
        erasure_roster: None,
        // ADR-0025 §1 (f): the simulated verifier counts only because the rules issue its key.
        verifier_keys: BTreeSet::from([vkey]),
        bundle_keys: BTreeSet::new(),
        personas: BTreeMap::from([(persona.clone(), topak_core::confine::Provenance::InHousePretrain)]),
        criterion: criterion.then(|| Criterion {
            record: "ADR-0035 (test: SIMULATED)".into(),
            independence_table: Digest::of(b"table"),
            floor_values: Digest::of(b"theta"),
        }),
    };
    let params = Params {
        corpus: BTreeSet::from([corpus_obj.clone()]),
        build_tools: BTreeSet::new(),
        run_tools: BTreeSet::new(),
        run_root: BTreeSet::new(),
        round_bound: 50,
        lease_margin_ms: 100,
        after_topic_limit: 3,
        run_round_bound: None,
    };
    Fx {
        dir,
        corpus_obj,
        params,
        rules,
        model,
        corrupt_model,
        persona,
        verifier_secret,
        chip_secret,
        round: AtomicU64::new(0),
    }
}

struct AllowAll;
impl BundleDecider for AllowAll {
    fn decide<'a>(&'a self, b: &'a Digest, _i: &'a Value) -> topak_node::mechanism::BoxFuture<'a, BundleOutcome> {
        Box::pin(async move { BundleOutcome::Allow { engine: BundleEngine::Sidecar, bundle: b.clone() } })
    }
    fn verified(&self, _rev: &Digest) -> bool {
        true
    }
}

/// A rung-1 backend that says it launched the profile's image whatever it ran: an untrusted host
/// where rung 1 trusts it (`Confinement.tla` `M_HOST`; ADR-0045 T-0045-19).
struct LyingBackend(ProcessBackend);
struct LyingGuest(Arc<dyn GuestHandle>, Option<Digest>);

impl Backend for LyingBackend {
    fn rung(&self) -> u8 {
        1
    }
    fn kind(&self) -> &'static str {
        "lying"
    }
    fn launch<'a>(&'a self, req: LaunchRequest<'a>) -> BoxFuture<'a, anyhow::Result<LaunchedGuest>> {
        Box::pin(async move {
            let claimed = req.profile.image.clone();
            let g = self.0.launch(req).await?;
            Ok(LaunchedGuest { handle: Arc::new(LyingGuest(g.handle, claimed)), io: g.io })
        })
    }
}

impl GuestHandle for LyingGuest {
    fn instance(&self) -> &Digest {
        self.0.instance()
    }
    fn evidence(&self, _g: &GuestEvidence, hello: &GuestHello) -> anyhow::Result<Evidence> {
        Ok(Evidence::LauncherAssertion { image: self.1.clone(), persona: hello.persona.clone() })
    }
    fn destroy(&self) -> BoxFuture<'_, ()> {
        self.0.destroy()
    }
}

#[derive(Clone, Default)]
struct Opts {
    script: &'static str,
    corrupt: bool,
    lying: bool,
}

struct Cl {
    nodes: Vec<Arc<Mechanism>>,
    hub: Arc<Hub>,
    sim: Arc<SimCvmBackend>,
    verifier: Arc<SimVerifier>,
}

fn guest_args(f: &Fx, rung: u8, o: &Opts) -> Vec<String> {
    let model = if o.corrupt { &f.corrupt_model } else { &f.model };
    let mut a = vec!["--model".into(), model.display().to_string(), "--rung".into(), rung.to_string()];
    a.extend(["--read".into(), f.corpus_obj.0.clone()]);
    if !o.script.is_empty() {
        a.extend(["--script".into(), o.script.into()]);
    }
    a
}

async fn cluster(f: &Fx, o: Opts) -> Cl {
    let hub = Arc::new(Hub::default());
    let platform = SimPlatform::new(f.chip_secret, 6);
    let sim = Arc::new(SimCvmBackend::new(guest_bin(), guest_args(f, 3, &o), f.model.clone(), platform.clone()));
    let verifier = Arc::new(SimVerifier::new(f.verifier_secret, platform.endorsement_key()));
    let process = ProcessBackend { command: guest_bin(), args: guest_args(f, 1, &o) };
    let rung1: Arc<dyn Backend> = if o.lying { Arc::new(LyingBackend(process)) } else { Arc::new(process) };
    let floor_exc = Floor::load().unwrap().exception_count();
    let mut nodes = Vec::new();
    for id in 1..=3u32 {
        let (prop_tx, prop_rx) = mpsc::channel(1024);
        let (in_tx, in_rx) = mpsc::channel(8192);
        hub.register(id, in_tx);
        let contain = Contain {
            backends: BTreeMap::from([(1, rung1.clone()), (3, sim.clone() as Arc<dyn Backend>)]),
            appraisers: BTreeMap::from([
                (1, Arc::new(LauncherAssertion) as Arc<dyn Appraiser>),
                (3, verifier.clone() as Arc<dyn Appraiser>),
            ]),
            evidence_dir: f.dir.join(format!("n{id}")).join("evidence"),
            hello_timeout: Duration::from_secs(5),
        };
        let mech = Mechanism::new(Parts {
            id,
            params: f.params.clone(),
            genesis: State::genesis(f.rules.clone(), floor_exc).unwrap(),
            floor: Floor::load().unwrap(),
            bundle: Box::new(AllowAll),
            transport: Transport::Memory(Memory::default()),
            tools: ToolHost::new(BTreeMap::new()),
            corpus_dir: f.dir.join("corpus"),
            data_dir: f.dir.join(format!("n{id}")),
            proposals: prop_tx,
            contain: Some(contain),
        })
        .unwrap();
        let mut pcfg = topak_paxos::Config::new(id, vec![1, 2, 3]);
        pcfg.heartbeat_ms = 20;
        pcfg.election_timeout_ms = 150;
        let net = Arc::new(ChannelNet { id, hub: hub.clone() });
        tokio::spawn(
            Driver { replica: topak_paxos::Replica::new(pcfg), wal: None, net, mech: mech.clone() }.run(in_rx, prop_rx),
        );
        topak_node::spawn_sweeper(mech.clone());
        nodes.push(mech);
    }
    let name = f.dir.file_name().unwrap().to_string_lossy().to_string();
    let name = name
        .strip_prefix("topak-contain-")
        .unwrap_or(&name)
        .rsplit_once('-')
        .map(|(n, _)| n.to_string())
        .unwrap_or(name);
    if let Some(t) = topak_core::trace::name_from_env(&format!("contain-{name}")) {
        nodes[0].state.write().unwrap().trace = Some(t);
    }
    Cl { nodes, hub, sim, verifier }
}

async fn until(what: &str, f: impl Fn() -> bool) {
    for _ in 0..400 {
        if f() {
            return;
        }
        tokio::time::sleep(Duration::from_millis(25)).await;
    }
    panic!("timed out waiting for {what}");
}

async fn settle(c: &Cl) {
    for _ in 0..200 {
        tokio::time::sleep(Duration::from_millis(20)).await;
        let isolated = c.hub.isolated.lock().unwrap().clone();
        let applied: BTreeSet<u64> = c
            .nodes
            .iter()
            .filter(|m| !isolated.contains(&m.id))
            .map(|m| m.state.read().unwrap().last_applied)
            .collect();
        if applied.len() == 1 {
            return;
        }
    }
}

fn profile_text(f: &Fx, image: &Digest, measurement: Option<String>, fail: &[&str]) -> String {
    let clauses: BTreeMap<String, Value> = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
        .iter()
        .map(|c| {
            let v = if fail.contains(c) {
                "fail"
            } else if *c == "P4" {
                "vacuous"
            } else {
                "pass"
            };
            (c.to_string(), json!({ "verdict": v, "why": "test" }))
        })
        .collect();
    let subtractions: BTreeMap<String, &str> = fail.iter().map(|c| (c.to_string(), "the subtraction")).collect();
    serde_json::to_string_pretty(&json!({
        "_what": "test profile",
        "image": image,
        "launch": { "kind": if measurement.is_some() { "sim-cvm" } else { "host-process" } },
        "channel": { "kind": "stdio" },
        "persona": { "model_json_sha256": f.persona },
        "reference": { "launch_measurement": measurement, "min_tcb": 5 },
        "clauses": clauses,
        "subtractions": subtractions,
    }))
    .unwrap()
}

/// ADR-0034 §1: draft the profile as the round's only file, submit, pass the gates, three grant
/// votes, register. Returns the profile digest.
async fn promote(m: &Mechanism, f: &Fx, text: &str) -> Digest {
    let grant = |seat: &str, role, alphabet: &[ActionKind]| OperatorOp::Grant {
        principal: format!("p-{seat}-{}", f.round.load(Ordering::SeqCst)),
        seat: seat.into(),
        persona: Digest::of(b"author persona"),
        bundle: Digest::of(b"bundle"),
        confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
        alphabet: alphabet.iter().copied().collect(),
        ttl_ms: LONG,
        round: f.next_round(),
        role,
    };
    let r = m.operate(grant("w1", RoundRole::Author, &[ActionKind::Draft, ActionKind::Submit])).await;
    let token = r["token"].as_str().unwrap_or_else(|| panic!("{r}")).to_string();
    let act = |op| m.act(AgentRequest { token: token.clone(), op });
    let r = act(AgentOp::Act { action: Action::Draft { target: PROFILE_FILE.into(), content: text.into() } }).await;
    assert!(r.admitted, "{}", r.detail);
    let r = act(AgentOp::SubmitWorkspace).await;
    assert!(r.admitted, "{}", r.detail);
    let artifact = Digest(r.detail["result"]["submitted"].as_str().unwrap().into());
    assert_eq!(artifact, profile_artifact(text.as_bytes()), "the round's workspace is the profile alone");
    let evidence = Digest::of(b"gates");
    m.operate(OperatorOp::GatesPassed { artifact: artifact.clone(), evidence: evidence.clone() }).await;
    for g in ["g1", "g2", "g3"] {
        let r = m.operate(grant(g, RoundRole::Voter, &[ActionKind::Vote])).await;
        let t = r["token"].as_str().unwrap().to_string();
        let vote = Action::Vote {
            verdict: Verdict::Grant,
            artifact: artifact.clone(),
            evidence: evidence.clone(),
            rules_epoch: 0,
        };
        let r = m.act(AgentRequest { token: t, op: AgentOp::Act { action: vote } }).await;
        assert!(r.admitted, "{}", r.detail);
    }
    let r = m.operate(OperatorOp::RegisterProfile { profile: text.into() }).await;
    assert_eq!(r["ok"], true, "{r}");
    Digest::of(text.as_bytes())
}

async fn launch(m: &Mechanism, f: &Fx, principal: &str, seat: &str, profile: &Digest, ttl_ms: u64) -> Value {
    m.operate(OperatorOp::Launch {
        principal: principal.into(),
        seat: seat.into(),
        profile: profile.clone(),
        bundle: Digest::of(b"bundle"),
        alphabet: BUILD.iter().copied().collect(),
        ttl_ms,
        round: f.next_round(),
        role: RoundRole::Author,
    })
    .await
}

fn because(r: &Value) -> String {
    r["because"].to_string()
}

fn launched(m: &Mechanism) -> usize {
    m.status()["launched"].as_array().unwrap().len()
}

fn live(m: &Mechanism, seat: &str) -> Option<LogIndex> {
    m.state.read().unwrap().live_by_seat.get(seat).copied()
}

fn ended(m: &Mechanism, fence: LogIndex) -> Option<EndReason> {
    m.state.read().unwrap().leases.get(&fence).and_then(|l| l.ended)
}

fn image() -> Digest {
    file_digest(&guest_bin()).unwrap()
}

// ---- rung 1 (ADR-0036 §7) ------------------------------------------------------------------------

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn rung_1_honest_round_and_its_refusals() {
    let f = fixture("r1", true);
    let c = cluster(&f, Opts { script: "read,draft,submit", ..Default::default() }).await;
    let n1 = &c.nodes[0];
    // ADR-0036 §4's honest declaration for a host process: P1, P2 and P3 fail.
    let honest = promote(n1, &f, &profile_text(&f, &image(), None, &["P1", "P2", "P3"])).await;

    let r = launch(n1, &f, "occupant-1", "c1", &honest, LONG).await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!((r["verdict"].as_str(), r["rung"].as_u64()), (Some("attested"), Some(1)));
    assert_eq!(r["lease"]["confinement"]["rung"], 1);
    assert!(r.get("token").is_none(), "no token: the bridge is the session (ADR-0036 §2)");
    // Mediated, derived from the declared P3 failure, not from the rung or the criterion.
    assert_eq!(r["contained"], false);
    assert!(because(&r).contains("P3"), "{r}");
    assert!(!because(&r).contains("criterion"), "{r}");
    let fence = r["fence"].as_u64().unwrap();
    // The round runs over the bridge and ends with Submit; the guest is destroyed (P6).
    until("the occupant's Submit", || ended(n1, fence) == Some(EndReason::Submitted)).await;
    until("the guest destroyed", || launched(n1) == 0).await;
    settle(&c).await;
    let st = n1.state.read().unwrap().clone();
    assert!(st.candidates.values().any(|c| c.author == "c1"), "the occupant's workspace was submitted");
    assert_eq!(st.leases[&fence].attestation.as_ref().unwrap().platform, PLATFORM_LAUNCHER);
    for m in &c.nodes[1..] {
        assert_eq!(m.state.read().unwrap().leases[&fence], st.leases[&fence], "every replica applied the same grant");
    }
    drop(st);

    // First refusal: the image is not the profile's. Unattestable; nothing is ordered.
    let wrong = promote(n1, &f, &profile_text(&f, &Digest::of(b"another image"), None, &["P1", "P2", "P3"])).await;
    let before = n1.state.read().unwrap().leases.len();
    let r = launch(n1, &f, "occupant-2", "c1", &wrong, LONG).await;
    assert_eq!(r["verdict"], "unattestable", "{r}");
    assert!(r["reason"].as_str().unwrap().contains("image"), "{r}");
    settle(&c).await;
    assert_eq!(n1.state.read().unwrap().leases.len(), before, "no grant was ordered");
    assert_eq!(launched(n1), 0);

    // A digest nobody promoted is not a reference value: refused before anything starts.
    let r = launch(n1, &f, "occupant-3", "c1", &Digest::of(b"unpromoted"), LONG).await;
    assert_eq!(r["verdict"], "refused", "{r}");
    assert!(r["reason"].as_str().unwrap().contains("not registered"), "{r}");
    // Rung 0 launches nothing.
    let r = launch(n1, &f, "occupant-4", "z0", &honest, LONG).await;
    assert!(r["reason"].as_str().unwrap().contains("rung 0"), "{r}");

    // Third refusal: a second process at the agent socket holds no token. Nothing names the lease.
    let r = n1.act(AgentRequest { token: String::new(), op: AgentOp::Abstain }).await;
    assert!(!r.admitted && r.detail["reason"].to_string().contains("UnknownLease"), "{}", r.detail);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn a_guest_that_cannot_verify_its_bundle_is_never_granted() {
    let f = fixture("bundle", true);
    let c = cluster(&f, Opts { script: "read", corrupt: true, ..Default::default() }).await;
    let n1 = &c.nodes[0];
    let p = promote(n1, &f, &profile_text(&f, &image(), None, &["P1", "P2", "P3"])).await;
    let r = launch(n1, &f, "occupant", "c1", &p, LONG).await;
    assert_eq!(r["verdict"], "unattestable", "{r}");
    assert!(r["reason"].as_str().unwrap().contains("closed"), "the guest exited before its identity line: {r}");
    assert_eq!(live(n1, "c1"), None);
}

// ---- rung 3, SIMULATED (F28) ---------------------------------------------------------------------

async fn rung3_profile(c: &Cl, f: &Fx, fail: &[&str]) -> Digest {
    promote(&c.nodes[0], f, &profile_text(f, &image(), Some(c.sim.expected_measurement().unwrap()), fail)).await
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn simulated_rung_3_round_is_contained_and_rung_0_beside_it_is_not() {
    let f = fixture("r3", true);
    let c = cluster(&f, Opts { script: "read,draft,emit,submit", ..Default::default() }).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;

    let r = launch(n1, &f, "occupant-3", "c3", &p, LONG).await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!(r["contained"], true, "{r}");
    assert_eq!(r["simulated"], true, "a simulated rung 3 says so");
    let fence = r["fence"].as_u64().unwrap();
    let att = n1.state.read().unwrap().leases[&fence].attestation.clone().unwrap();
    assert_eq!(att.verified_by.as_deref(), Some(c.verifier.key().as_str()), "F15: the issued verifier key");
    assert!(att.session_key.is_some(), "F12: the session is the attested guest's key");
    // Every action reached the log with the guest's proof, checked at apply on every replica.
    until("the occupant's Submit", || ended(n1, fence) == Some(EndReason::Submitted)).await;
    settle(&c).await;
    assert_eq!(n1.state.read().unwrap().leases[&fence].session_ctr, 4, "read, draft, emit, submit");
    for m in &c.nodes[1..] {
        assert_eq!(m.state.read().unwrap().leases[&fence], n1.state.read().unwrap().leases[&fence]);
    }

    // A rung-0 principal beside it: `Contained` is not everyone.
    let r = n1
        .operate(OperatorOp::Grant {
            principal: "beside".into(),
            seat: "z0".into(),
            persona: f.persona.clone(),
            bundle: Digest::of(b"bundle"),
            confinement: topak_core::lease::Confinement { digest: p.clone(), rung: 0 },
            alphabet: BUILD.iter().copied().collect(),
            ttl_ms: LONG,
            round: f.next_round(),
            role: RoundRole::Author,
        })
        .await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!(r["contained"], false);
    assert!(because(&r).contains("rung 0"), "{r}");
}

/// ADR-0034 §1: a Build profile does not confine a Run seat, and no Run profile exists
/// (ADR-0042 §6). Refused before anything starts.
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn a_run_seat_launches_nothing() {
    let f = fixture("run", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    let r = launch(n1, &f, "runner", "r3", &p, LONG).await;
    assert_eq!(r["verdict"], "refused", "{r}");
    assert!(r["reason"].as_str().unwrap().contains("domain"), "{r}");
    assert_eq!(launched(n1), 0);
    assert_eq!(live(n1, "r3"), None);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn without_the_criterion_nothing_is_contained() {
    let f = fixture("nocrit", false);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    let r = launch(n1, &f, "occupant", "c3", &p, LONG).await;
    assert_eq!((r["ok"].as_bool(), r["contained"].as_bool()), (Some(true), Some(false)), "{r}");
    assert!(because(&r).contains("criterion"), "{r}");
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn a_rogue_image_is_contested_and_the_principal_is_revoked() {
    let f = fixture("rogue", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    c.sim.rogue.store(true, Ordering::SeqCst);
    let r = launch(n1, &f, "mallory", "c3", &p, LONG).await;
    assert_eq!(r["verdict"], "contested", "{r}");
    assert_eq!(r["applied"]["Contested"]["ended"], 0, "{r}");
    settle(&c).await;
    for m in &c.nodes {
        let st = m.state.read().unwrap();
        assert!(st.contested.contains_key("mallory"), "ContestedStopped, on every replica");
        assert!(st.revoked.contains(&RevocationTarget::Principal("mallory".into())));
    }
    let evidence = r["evidence"].as_str().unwrap();
    assert!(f.dir.join("n1/evidence").join(format!("{evidence}.json")).exists(), "F18: the evidence is retained");
    assert_eq!(launched(n1), 0, "the rogue guest is destroyed");
    // The principal's next guest, honest this time, is refused; the profile is not revoked.
    c.sim.rogue.store(false, Ordering::SeqCst);
    let r = launch(n1, &f, "mallory", "c3", &p, LONG).await;
    assert!(r["reason"].as_str().unwrap().contains("revoked"), "{r}");
    let r = launch(n1, &f, "alice", "d3", &p, LONG).await;
    assert_eq!(r["ok"], true, "{r}");
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn an_unreachable_verifier_grants_nothing() {
    let f = fixture("unreach", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    // A lease granted while the verifier answered keeps running to its renewal (PC/EC).
    let r = launch(n1, &f, "alice", "d3", &p, LONG).await;
    let alive = r["fence"].as_u64().unwrap();
    c.verifier.reachable.store(false, Ordering::SeqCst);
    let r = launch(n1, &f, "bob", "c3", &p, LONG).await;
    assert_eq!(r["verdict"], "unattestable", "{r}");
    assert!(r["reason"].as_str().unwrap().contains("unreachable"), "{r}");
    settle(&c).await;
    assert_eq!(live(n1, "c3"), None, "no grant, at any rung");
    assert_eq!(live(n1, "d3"), Some(alive), "the live lease is untouched");
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn an_epoch_fence_voids_a_pending_appraisal() {
    let f = fixture("stale", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = c.nodes[0].clone();
    let p = rung3_profile(&c, &f, &[]).await;
    let gate = Arc::new(Semaphore::new(0));
    *c.verifier.gate.lock().unwrap() = Some(gate.clone());
    let round = f.next_round();
    let pending = {
        let n1 = n1.clone();
        let p = p.clone();
        tokio::spawn(async move {
            n1.operate(OperatorOp::Launch {
                principal: "alice".into(),
                seat: "c3".into(),
                profile: p,
                bundle: Digest::of(b"bundle"),
                alphabet: BUILD.iter().copied().collect(),
                ttl_ms: LONG,
                round,
                role: RoundRole::Author,
            })
            .await
        })
    };
    tokio::time::sleep(Duration::from_millis(500)).await;
    let r = n1.operate(OperatorOp::FenceEpoch { reason: "test".into(), attribution: "test".into() }).await;
    assert_eq!(r["ok"], true, "{r}");
    gate.add_permits(1);
    let r = pending.await.unwrap();
    assert_eq!(r["verdict"], "unattestable", "{r}");
    assert!(r["reason"].as_str().unwrap().contains("fenced"), "{r}");
    assert_eq!(live(&n1, "c3"), None);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn the_session_is_the_attested_guests() {
    let f = fixture("session", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    let a = launch(n1, &f, "alice", "c3", &p, LONG).await["fence"].as_u64().unwrap();
    let b = launch(n1, &f, "bob", "d3", &p, LONG).await["fence"].as_u64().unwrap();
    assert_ne!(a, b);
    let op = AgentOp::Act { action: Action::Read { object: f.corpus_obj.clone() } };
    let deny = |r: topak_mcp::proto::AgentResponse| r.detail["reason"].to_string();
    // No proof; a proof by a key that is not the attested guest's; a proof for another action.
    assert!(deny(n1.act_bound(a, op.clone(), None).await).contains("signed nothing"));
    let other: [u8; 32] = rand::random();
    let d = Digest::of_json(&op);
    let sig = topak_core::authentic::sign(AGENT_OP_PURPOSE, &session_body(a, 0, 1, &d), &other).sig;
    let forged = SessionProof { ctr: 1, op: d.clone(), sig };
    assert!(deny(n1.act_bound(a, op.clone(), Some(forged.clone())).await).contains("not the attested guest's"));
    let other_op = AgentOp::Abstain;
    assert!(deny(n1.act_bound(a, other_op, Some(forged)).await).contains("another action"));
    // An operator token cannot reach a launched lease: none was minted.
    let r = n1.act(AgentRequest { token: "guess".into(), op }).await;
    assert!(r.detail["reason"].to_string().contains("UnknownLease"));
    assert_eq!(launched(n1), 2);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn renewal_re_attests_the_same_guest_and_lapses_when_it_cannot() {
    let f = fixture("renew", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    let r = launch(n1, &f, "alice", "c3", &p, 1_500).await;
    let first = r["fence"].as_u64().unwrap();
    let instance = n1.state.read().unwrap().leases[&first].attestation.clone().unwrap().instance;
    until("a renewal", || live(n1, "c3").is_some_and(|f| f != first)).await;
    let renewed = live(n1, "c3").unwrap();
    {
        let st = n1.state.read().unwrap();
        let l = &st.leases[&renewed];
        assert_eq!(l.lease.confinement.rung, 3, "a renewal keeps the rung");
        assert_eq!(l.attestation.as_ref().unwrap().instance, instance, "the same guest");
        assert!(l.attestation.as_ref().unwrap().nonce_index >= first, "a fresh nonce");
        assert!(st.contained(renewed).contained);
    }
    // The verifier stops answering: no renewal, and the lease lapses. It is not kept lower.
    c.verifier.reachable.store(false, Ordering::SeqCst);
    until("the lease to lapse", || live(n1, "c3").is_none()).await;
    let st = n1.state.read().unwrap();
    let last = st.leases.values().filter(|l| l.lease.seat == "c3").max_by_key(|l| l.lease.fence).unwrap();
    assert_eq!(last.ended, Some(EndReason::Expired), "lost its lease, not its containment");
    assert_eq!(last.lease.confinement.rung, 3);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn every_host_power_subtracts() {
    let f = fixture("host", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    // Alter a running guest: the hardware kills it (assumed, ADR-0034 §5). The round ends.
    let a = launch(n1, &f, "alice", "c3", &p, LONG).await["fence"].as_u64().unwrap();
    c.sim.tamper();
    until("the round to end", || ended(n1, a) == Some(EndReason::Operator)).await;
    // Withhold the channel: the lease expires.
    let b = launch(n1, &f, "bob", "d3", &p, 800).await["fence"].as_u64().unwrap();
    c.verifier.reachable.store(false, Ordering::SeqCst);
    until("expiry", || ended(n1, b).is_some()).await;
    assert_eq!(ended(n1, b), Some(EndReason::Expired));
    let seen = Arc::new(Mutex::new(()));
    drop(seen);

    // M_HOST at rung 1: a host that lies about the image is believed. T-0045-19 is load-bearing.
    let g = fixture("lying", true);
    let c = cluster(&g, Opts { lying: true, ..Default::default() }).await;
    let m = &c.nodes[0];
    let claimed =
        promote(m, &g, &profile_text(&g, &Digest::of(b"the image it claims"), None, &["P1", "P2", "P3"])).await;
    let r = launch(m, &g, "occupant", "c1", &claimed, LONG).await;
    assert_eq!(r["verdict"], "attested", "rung 1 trusts the launcher: {r}");
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn withdrawing_a_profile_fences_its_leases() {
    let f = fixture("withdraw", true);
    let c = cluster(&f, Opts::default()).await;
    let n1 = &c.nodes[0];
    let p = rung3_profile(&c, &f, &[]).await;
    let a = launch(n1, &f, "alice", "c3", &p, LONG).await["fence"].as_u64().unwrap();
    // F17: the vendor withdrew a firmware version; the custodian fences by profile digest.
    let r = n1
        .operate(OperatorOp::Revoke {
            target: RevocationTarget::Confinement(p.clone()),
            reason: "minimum TCB raised".into(),
            attribution: "custodian".into(),
        })
        .await;
    assert_eq!(r["applied"]["Revoked"]["ended"], 1, "{r}");
    assert_eq!(ended(n1, a), Some(EndReason::Revoked));
    until("the guest destroyed", || launched(n1) == 0).await;
    let r = launch(n1, &f, "bob", "d3", &p, LONG).await;
    assert!(r["reason"].as_str().unwrap().contains("revoked"), "{r}");
}
