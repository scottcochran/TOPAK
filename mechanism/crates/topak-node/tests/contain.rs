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

// The launch future is deep: the appraisal, the grant, the opening record and the bridge.
#![recursion_limit = "256"]

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
/// A lease long enough that nothing in a test waits on it: ten minutes, under `T_persona` (one hour,
/// ADR-0031 A2). The launcher re-attests at TTL/2, so a shorter value puts a renewal inside tests
/// that are not about renewal; the renewal tests choose their own TTL.
const LONG: u64 = 600_000;

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
    /// An object in the Run root, for a Run guest's `Consult`.
    run_obj: Digest,
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
    let run_content = b"valve v7: closed is safe\n";
    let run_obj = Digest::of(run_content);
    std::fs::write(dir.join("corpus").join(&run_obj.0), run_content).unwrap();
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
        inside_targets: BTreeSet::new(),
        releasers: BTreeSet::new(),
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
        wasm_tools: BTreeSet::new(),
        round_bound: 50,
        lease_margin_ms: 100,
        after_topic_limit: 3,
        run_round_bound: None,
    };
    Fx {
        dir,
        corpus_obj,
        run_obj,
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

/// Allows everything, and holds the channel declarations of the revisions a test names: what the
/// allowlist entries of those revisions would say (ADR-0049 §5).
struct AllowAll(Channels);
type Channels = BTreeMap<(Digest, String), topak_contain::wasmtool::Channel>;
impl BundleDecider for AllowAll {
    fn decide<'a>(&'a self, b: &'a Digest, _i: &'a Value) -> topak_node::mechanism::BoxFuture<'a, BundleOutcome> {
        Box::pin(async move { BundleOutcome::Allow { engine: BundleEngine::Sidecar, bundle: b.clone() } })
    }
    fn verified(&self, _rev: &Digest) -> bool {
        true
    }
    /// No entries here: a test of what a list holds uses the real tier.
    fn tool_list(&self, rev: &Digest, domain: Domain, callable: &BTreeSet<String>) -> Value {
        topak_bundle::Allowlist::default().tool_list(rev, domain, callable)
    }
    /// A stub with no entries declares no label: nothing joined, everything clear, nothing outward.
    fn label_facts(
        &self,
        _rev: &Digest,
        _kind: &str,
        action: &Action,
        round: &topak_core::labels::RoundLabels,
    ) -> Result<Option<topak_core::labels::LabelFacts>, String> {
        Ok(matches!(action, Action::Consult { .. } | Action::Actuate { .. })
            .then(|| topak_core::labels::LabelFacts::unlabelled(&round.clear_set)))
    }
    fn input_types(&self, _rev: &Digest, _tool: &str) -> BTreeMap<String, String> {
        BTreeMap::new()
    }
    fn channel(&self, rev: &Digest, tool: &str) -> Option<topak_contain::wasmtool::Channel> {
        self.0.get(&(rev.clone(), tool.to_string())).cloned()
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
    /// Run tools hosted as Wasm modules, and the one the guest's `actuate` step names.
    wasm: Option<Arc<topak_contain::wasmtool::WasmToolHost>>,
    tool: String,
    /// What each bundle revision's entry declares as a tool's channel.
    channels: Channels,
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
    a.extend(["--read".into(), f.corpus_obj.0.clone(), "--consult".into(), f.run_obj.0.clone()]);
    if !o.tool.is_empty() {
        a.extend(["--tool".into(), o.tool.clone()]);
    }
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
            bundle: Box::new(AllowAll(o.channels.clone())),
            transport: Transport::Memory(Memory::default()),
            tools: ToolHost::new(BTreeMap::new()),
            corpus_dir: f.dir.join("corpus"),
            data_dir: f.dir.join(format!("n{id}")),
            proposals: prop_tx,
            wasm_tools: o.wasm.clone(),
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

/// Poll until a condition holds. The ceiling is generous because a condition that is met costs
/// nothing to wait for, and reaching the ceiling is a failure, never a pass (ADR-0032 §1: no
/// decision here reads a clock; the clock only bounds how long a test may run).
async fn until(what: &str, f: impl Fn() -> bool) {
    for _ in 0..2400 {
        if f() {
            return;
        }
        tokio::time::sleep(Duration::from_millis(25)).await;
    }
    panic!("timed out waiting for {what}");
}

/// Every replica that is not isolated has reached a state satisfying `pred`. A test that reads
/// another replica's state waits for the entry it means to see, named by what it changes, and not
/// for a quiet period: a wait that can run out and return silently can also pass for want of time
/// (the 10.02 critical review's CR-39).
async fn every_replica(c: &Cl, what: &str, pred: impl Fn(&State) -> bool) {
    until(what, || {
        let isolated = c.hub.isolated.lock().unwrap().clone();
        c.nodes.iter().filter(|m| !isolated.contains(&m.id)).all(|m| pred(&m.state.read().unwrap()))
    })
    .await;
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
        task_label: None,
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
        task_label: None,
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
    every_replica(&c, "every replica to apply the round's Submit", |st| {
        st.leases.get(&fence).is_some_and(|l| l.ended == Some(EndReason::Submitted))
    })
    .await;
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
    // Unattestable is decided before anything is proposed, so there is nothing to wait for.
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
    every_replica(&c, "every replica to apply the round's Submit", |st| {
        st.leases.get(&fence).is_some_and(|l| l.ended == Some(EndReason::Submitted))
    })
    .await;
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
            task_label: None,
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
    // ContestedStopped, on every replica: the Contested entry is ordered, so each applies it.
    every_replica(&c, "every replica to apply the Contested entry", |st| {
        st.contested.contains_key("mallory") && st.revoked.contains(&RevocationTarget::Principal("mallory".into()))
    })
    .await;
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
    // Unattestable proposes nothing (ADR-0034 §3.3), so the state is already final.
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
                task_label: None,
            })
            .await
        })
    };
    // The nonce is fixed before the verifier is asked (launch.rs steps 3 to 5), so an appraisal
    // waiting at the gate is one the fence must void. Wait for it to arrive, not for a clock.
    until("the appraisal to reach the verifier", || c.verifier.appraisals.load(Ordering::SeqCst) == 1).await;
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

// ---- Run (ADR-0034 A2, pending: the Run profile; P4 is channel fidelity) ------------------------

/// A tool that connects to its declared target, sends its inputs, and returns the reply.
const ECHO_TOOL: &str = r#"
(module
  (import "topak" "input_len" (func $input_len (result i32)))
  (import "topak" "input_read" (func $input_read (param i32)))
  (import "topak" "output" (func $output (param i32 i32)))
  (import "topak" "connect" (func $connect (result i32)))
  (import "topak" "send" (func $send (param i32 i32 i32) (result i32)))
  (import "topak" "recv" (func $recv (param i32 i32 i32) (result i32)))
  (memory (export "memory") 1)
  (func (export "run") (result i32)
    (local $n i32) (local $h i32) (local $r i32)
    (local.set $n (call $input_len))
    (call $input_read (i32.const 0))
    (local.set $h (call $connect))
    (if (i32.lt_s (local.get $h) (i32.const 0)) (then (return (i32.const 1))))
    (drop (call $send (local.get $h) (i32.const 0) (local.get $n)))
    (local.set $r (call $recv (local.get $h) (i32.const 1024) (i32.const 1000)))
    (call $output (i32.const 1024) (local.get $r))
    (i32.const 0)))
"#;

/// A target that answers once, and says what it was sent.
fn target_once() -> (String, std::thread::JoinHandle<String>) {
    use std::io::{Read, Write};
    let target = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let addr = target.local_addr().unwrap().to_string();
    let seen = std::thread::spawn(move || {
        let (mut s, _) = target.accept().unwrap();
        s.set_read_timeout(Some(Duration::from_secs(5))).unwrap();
        let mut buf = vec![0u8; 4096];
        let n = s.read(&mut buf).unwrap();
        s.write_all(format!("{{\"echo\":{n}}}").as_bytes()).unwrap();
        String::from_utf8_lossy(&buf[..n]).to_string()
    });
    (addr, seen)
}

/// A Run round at rung 3 on a Run profile, SIMULATED, with its cell Observer live: the guest
/// `Consult`s, then `Actuate`s the one Wasm tool this replica hosts. The lease names the bundle
/// revision `Digest::of(b"bundle")`; `channels` is what each revision's entry declares.
/// Returns the cluster, the tool's id, the lease's fence and the round's topic.
async fn run_round(name: &str, channels: impl FnOnce(&str) -> Channels) -> (Cl, String, u64, String) {
    use topak_contain::wasmtool::{WasmToolHost, WasmToolSpec, module_digest};
    let mut f = fixture(name, true);
    let module = f.dir.join("valve.wasm");
    std::fs::write(&module, wat::parse_str(ECHO_TOOL).unwrap()).unwrap();
    let digest = module_digest(&module).unwrap();
    let tool = format!("valve@{}", digest.0);
    // The host is told where the module is and what its bytes are, and nothing of its channel.
    let host = Arc::new(
        WasmToolHost::new(BTreeMap::from([(tool.clone(), WasmToolSpec { module, module_sha256: digest })])).unwrap(),
    );
    f.params.run_root.insert(f.run_obj.clone());
    f.params.run_tools.insert(tool.clone());
    f.params.wasm_tools.insert(tool.clone());
    let cell = SeatDecl {
        domain: Domain::Run,
        kind: SeatKind::Observer,
        cell: Some("r3".into()),
        key: hex::encode(rand::random::<[u8; 32]>()),
        rung: 0,
    };
    f.rules.seats.insert("ro0".into(), cell);
    let c = cluster(
        &f,
        Opts {
            script: "consult,wait:1500,actuate",
            wasm: Some(host),
            tool: tool.clone(),
            channels: channels(&tool),
            ..Default::default()
        },
    )
    .await;
    let n1 = &c.nodes[0];

    // The Run profile: every clause passes, P4 as channel fidelity.
    let text = profile_text(&f, &image(), Some(c.sim.expected_measurement().unwrap()), &[]);
    let mut v: Value = serde_json::from_str(&text).unwrap();
    v["domain"] = json!("run");
    v["clauses"]["P4"]["verdict"] = json!("pass");
    let p = promote(n1, &f, &serde_json::to_string_pretty(&v).unwrap()).await;

    // The cell Observer, at rung 0: it reports, it acts on nothing.
    let r = n1
        .operate(OperatorOp::Grant {
            principal: "watcher".into(),
            seat: "ro0".into(),
            persona: f.persona.clone(),
            bundle: Digest::of(b"bundle"),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: [ActionKind::Consult, ActionKind::Report].into_iter().collect(),
            ttl_ms: LONG,
            round: f.next_round(),
            role: RoundRole::Author,
            task_label: None,
        })
        .await;
    let watcher = r["token"].as_str().unwrap().to_string();

    let round = f.next_round();
    let r = n1
        .operate(OperatorOp::Launch {
            principal: "operator-of-v7".into(),
            seat: "r3".into(),
            profile: p.clone(),
            bundle: Digest::of(b"bundle"),
            alphabet: [ActionKind::Consult, ActionKind::Actuate, ActionKind::Report].into_iter().collect(),
            ttl_ms: LONG,
            round,
            role: RoundRole::Author,
            task_label: None,
        })
        .await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!((r["contained"].as_bool(), r["simulated"].as_bool()), (Some(true), Some(true)), "{r}");
    let fence = r["fence"].as_u64().unwrap();
    let chain = n1.state.read().unwrap().chain.clone();
    let topic = topak_core::lift::topic_name(&chain, Domain::Run, "r3", 0, round);
    let hb =
        AgentOp::Act { action: Action::Report { record: json!({ "heartbeat": { "topic": topic, "watermark": 0 } }) } };
    let r = n1.act(AgentRequest { token: watcher, op: hb }).await;
    assert!(r.admitted, "the Observer is live: {}", r.detail);
    (c, tool, fence, topic)
}

/// F28 for Run, SIMULATED: a Run principal launched at rung 3 on a Run profile `Consult`s, then
/// `Actuate`s a tool held to its declared channel, with its cell Observer live. The effect reaches
/// the declared target, the record names the channel, and the lease is `Contained`.
///
/// The declaration is the allowlist entry's, in the bundle revision the lease names (ADR-0049 §5;
/// ADR-0034 A2 R4). Another revision declares another target for the same tool, and it is not
/// reached: the host has no configured target, and the lease does not name that revision.
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn a_run_round_actuates_only_its_declared_channel() {
    use topak_contain::wasmtool::Channel;
    let (addr, seen) = target_once();
    let other = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    other.set_nonblocking(true).unwrap();
    let channel = Channel { kind: "tcp".into(), target: addr };
    let elsewhere = Channel { kind: "tcp".into(), target: other.local_addr().unwrap().to_string() };
    let (c, tool, fence, topic) = run_round("run3", |tool| {
        BTreeMap::from([
            ((Digest::of(b"bundle"), tool.to_string()), channel.clone()),
            ((Digest::of(b"another revision"), tool.to_string()), elsewhere),
        ])
    })
    .await;
    let n1 = &c.nodes[0];

    let sent = seen.join().unwrap();
    assert!(sent.contains("\"open\":\"v7\""), "the declared target received the call: {sent}");
    assert!(other.accept().is_err(), "the target another revision declares saw nothing");
    until("the Actuate admitted", || n1.state.read().unwrap().leases.get(&fence).is_some_and(|l| l.seq == 1)).await;
    let Transport::Memory(mem) = &n1.transport else { unreachable!() };
    // The record is written when the call returns, after the admit is applied.
    let mut rec = None;
    for _ in 0..200 {
        let found = mem
            .topics
            .lock()
            .await
            .get(&topic)
            .and_then(|recs| recs.iter().find(|r| r.kind == topak_transport::RecordKind::Actuate).cloned());
        if found.is_some() {
            rec = found;
            break;
        }
        tokio::time::sleep(Duration::from_millis(25)).await;
    }
    let rec = rec.expect("the Actuate record");
    let env = &rec.payload["actuate"];
    assert_eq!(env["tool"], json!(tool));
    assert_eq!(env["outcome"], "returned");
    assert_eq!(env["channel"], json!(channel), "the record names the channel the tool was held to");
    assert!(n1.state.read().unwrap().contained(fence).contained);
}

/// The other half of ADR-0049 §5: with no declaration in the lease's revision there is no target.
/// The entry of another revision does not stand in for it, and the hosted tool is not run.
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn a_hosted_tool_with_no_channel_in_the_leases_revision_is_not_run() {
    use topak_contain::wasmtool::Channel;
    let other = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    other.set_nonblocking(true).unwrap();
    let elsewhere = Channel { kind: "tcp".into(), target: other.local_addr().unwrap().to_string() };
    let (c, _tool, fence, topic) =
        run_round("run3-undeclared", |tool| BTreeMap::from([((Digest::of(b"another revision"), tool.to_string()), elsewhere)]))
            .await;
    let n1 = &c.nodes[0];
    until("the Actuate admitted", || n1.state.read().unwrap().leases.get(&fence).is_some_and(|l| l.seq == 1)).await;
    tokio::time::sleep(Duration::from_millis(500)).await;
    assert!(other.accept().is_err(), "nothing was reached");
    let Transport::Memory(mem) = &n1.transport else { unreachable!() };
    let recs = mem.topics.lock().await.get(&topic).cloned().unwrap_or_default();
    assert!(
        !recs.iter().any(|r| r.kind == topak_transport::RecordKind::Actuate && r.payload["actuate"]["outcome"] == "returned"),
        "no call returned"
    );
}
