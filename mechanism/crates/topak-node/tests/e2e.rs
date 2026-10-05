//! End to end: three replicas in one process, the pinned Cedar floor, the real compiled bundle
//! (WASM, no sidecar), the in-memory transport, and the demo tool over MCP.
//!
//! Requires `scripts/build-bundle.sh` to have produced a bundle in `mechanism/bundles/`.

use std::collections::{BTreeMap, BTreeSet};
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;

use ed25519_dalek::{Signer, SigningKey};
use serde_json::{Value, json};
use tokio::sync::mpsc;
use topak_bundle::{BundleTier, LocalBundles};
use topak_core::action::{Action, tool_id};
use topak_core::admit::BundleOutcome;
use topak_core::authentic::{Signed, signing_bytes};
use topak_core::control::{CONTROL_PURPOSE, ControlAction, ControlRequest};
use topak_core::rules::*;
use topak_core::state::*;
use topak_core::*;
use topak_floor::Floor;
use topak_mcp::proto::{AgentOp, AgentRequest, AgentResponse};
use topak_mcp::toolhost::{ToolHost, ToolSpec};
use topak_node::driver::Driver;
use topak_node::mechanism::{BoxFuture, BundleDecider, Mechanism, Parts};
use topak_node::net::{ChannelNet, Hub};
use topak_node::ops::OperatorOp;
use topak_transport::{Memory, RecordKind, Transport};

// ---- fixture ---------------------------------------------------------------------------------

struct Keys {
    anchors: Vec<SigningKey>,
    bg: Vec<SigningKey>,
    /// The bundle key (ADR-0044 §1): the fixture signs its copy of the bundle with it.
    bundle: SigningKey,
    /// The operator seats' keys, by seat (ADR-0050 §3): three in Build and three in Run.
    ops: BTreeMap<String, SigningKey>,
    /// The identity provider that vouches for them. Its key is issued in the rules.
    idp: SigningKey,
}

const OPERATORS: [(&str, Domain); 6] = [
    ("op1", Domain::Build),
    ("op2", Domain::Build),
    ("op3", Domain::Build),
    ("opr1", Domain::Run),
    ("opr2", Domain::Run),
    ("opr3", Domain::Run),
];

fn key() -> SigningKey {
    SigningKey::generate(&mut rand::rngs::OsRng)
}

fn pubhex(k: &SigningKey) -> String {
    hex::encode(k.verifying_key().to_bytes())
}

fn sign(k: &SigningKey, purpose: &str, body: &Value) -> Signed {
    Signed { key: pubhex(k), sig: hex::encode(k.sign(&signing_bytes(purpose, body)).to_bytes()) }
}

struct Fixture {
    dir: PathBuf,
    corpus_obj: Digest,
    /// An object in Run's root and not in Build's (ADR-0040 §3).
    run_obj: Digest,
    tool: String,
    /// The demo binary's `sleep`, on Run's allowlist. `tool` is not: it is break-glass's.
    run_tool: String,
    tools: BTreeMap<String, ToolSpec>,
    params: Params,
    rules: Rules,
    keys: Keys,
    bundle_rev: Digest,
    /// Further revisions the real tier holds: the built bundle's policy with this data, under
    /// this revision name. They stand for revisions promoted and signed beside the built one.
    extra_bundles: Vec<(String, Value)>,
    /// Run tools hosted as Wasm modules, for the tests that pass a result by handle.
    wasm: Option<Arc<topak_contain::wasmtool::WasmToolHost>>,
}

async fn fixture(name: &str) -> Fixture {
    let dir = std::env::temp_dir().join(format!("topak-e2e-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("corpus")).unwrap();
    let content = b"---- MODULE Lease ----\n";
    let corpus_obj = Digest::of(content);
    std::fs::write(dir.join("corpus").join(&corpus_obj.0), content).unwrap();

    let bin = PathBuf::from(env!("CARGO_BIN_EXE_topak-demo-tool"));
    let (bin_digest, tdigest) = ToolHost::digest_of(&bin, &[], "wordcount").await.unwrap();
    let tool = tool_id("wordcount", &tdigest);
    let (_, sdigest) = ToolHost::digest_of(&bin, &[], "sleep").await.unwrap();
    let run_tool = tool_id("sleep", &sdigest);
    let spec = |mcp_tool: &str| ToolSpec {
        command: bin.clone(),
        args: vec![],
        binary_sha256: bin_digest.clone(),
        mcp_tool: mcp_tool.into(),
    };
    let tools = BTreeMap::from([(tool.clone(), spec("wordcount")), (run_tool.clone(), spec("sleep"))]);
    let run_content = b"valve v7: closed is safe\n";
    let run_obj = Digest::of(run_content);
    std::fs::write(dir.join("corpus").join(&run_obj.0), run_content).unwrap();

    let params = Params {
        corpus: BTreeSet::from([corpus_obj.clone()]),
        build_tools: BTreeSet::from([tool.clone()]),
        run_tools: BTreeSet::from([run_tool.clone()]),
        run_root: BTreeSet::from([run_obj.clone()]),
        wasm_tools: BTreeSet::new(),
        round_bound: 50,
        lease_margin_ms: 100,
        after_topic_limit: 3,
        run_round_bound: None,
    };

    let keys = Keys {
        anchors: (0..3).map(|_| key()).collect(),
        bg: (0..2).map(|_| key()).collect(),
        bundle: key(),
        ops: OPERATORS.iter().map(|(s, _)| (s.to_string(), key())).collect(),
        idp: key(),
    };
    let seat =
        |d: Domain, k: topak_core::SeatKind| SeatDecl { domain: d, kind: k, cell: None, key: pubhex(&key()), rung: 0 };
    let rules = Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats: BTreeMap::from([
            ("a1".into(), seat(Domain::Build, topak_core::SeatKind::Thinker)),
            ("g1".into(), seat(Domain::Build, topak_core::SeatKind::Grant)),
            ("g2".into(), seat(Domain::Build, topak_core::SeatKind::Grant)),
            ("g3".into(), seat(Domain::Build, topak_core::SeatKind::Grant)),
            ("o1".into(), SeatDecl { cell: Some("a1".into()), ..seat(Domain::Build, topak_core::SeatKind::Observer) }),
            ("corr".into(), seat(Domain::Build, topak_core::SeatKind::Observer)), // a correlator: no cell
            ("r1".into(), seat(Domain::Run, topak_core::SeatKind::Thinker)),
            ("ro1".into(), SeatDecl { cell: Some("r1".into()), ..seat(Domain::Run, topak_core::SeatKind::Observer) }),
        ]),
        // a1 authors and also holds a grant seat, so recusal has something to refuse.
        grant_roster: ["a1", "g1", "g2", "g3"].into_iter().map(String::from).collect(),
        veto_roster: BTreeSet::from(["o1".to_string(), "corr".to_string()]),
        anchor_keys: keys.anchors.iter().map(pubhex).collect(),
        break_glass: Some(BreakGlassRules {
            roster: keys.bg.iter().map(pubhex).collect(),
            quorum: 2,
            tools: BTreeSet::from([tool.clone()]),
            actions: BTreeSet::from(["Actuate".to_string()]),
        }),
        erasure_roster: None,
        verifier_keys: BTreeSet::new(),
        bundle_keys: BTreeSet::from([pubhex(&keys.bundle)]),
        provider_keys: BTreeSet::from([pubhex(&keys.idp)]),
        inside_targets: BTreeSet::new(),
        releasers: BTreeSet::new(),
        personas: BTreeMap::new(),
        criterion: None,
    };

    // ADR-0050 §1: the operators. Each seat's key is its holder's.
    let mut rules = rules;
    for (name, domain) in OPERATORS {
        let decl = SeatDecl { domain, kind: topak_core::SeatKind::Operator, cell: None, key: pubhex(&keys.ops[name]), rung: 0 };
        rules.seats.insert(name.to_string(), decl);
    }

    // ADR-0044: the fixture's bundle key signs a copy of the built bundle into its own bundles
    // directory; the rules above carry the key.
    let built = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../bundles");
    let tarball = std::fs::read_dir(&built)
        .expect("run scripts/build-bundle.sh first")
        .filter_map(|e| e.ok().map(|e| e.path()))
        .find(|p| p.extension().is_some_and(|x| x == "gz"))
        .expect("run scripts/build-bundle.sh first");
    let rev = tarball.file_name().unwrap().to_string_lossy().trim_end_matches(".tar.gz").to_string();
    std::fs::create_dir_all(dir.join("bundles")).unwrap();
    std::fs::copy(&tarball, dir.join("bundles").join(format!("{rev}.tar.gz"))).unwrap();
    let sig = topak_core::authentic::sign(
        topak_bundle::BUNDLE_PURPOSE,
        &topak_bundle::bundle_body(&rev),
        &keys.bundle.to_bytes(),
    );
    std::fs::write(dir.join("bundles").join(format!("{rev}.sig")), serde_json::to_vec(&sig).unwrap()).unwrap();
    let l = LocalBundles::load_dir(&dir.join("bundles"), &rules.bundle_keys).await.unwrap();
    let bundle_rev = l.revisions().next().expect("the signed copy loads").clone();

    Fixture { dir, corpus_obj, run_obj, tool, run_tool, tools, params, rules, keys, bundle_rev, extra_bundles: vec![], wasm: None }
}

/// A bundle that allows everything, to exercise effects the real placeholder bundle refuses.
/// It cannot widen anything: composition bounds it by the floor.
struct AllowAll;
impl BundleDecider for AllowAll {
    fn decide<'a>(&'a self, b: &'a Digest, _i: &'a Value) -> BoxFuture<'a, BundleOutcome> {
        Box::pin(async move { BundleOutcome::Allow { engine: BundleEngine::Sidecar, bundle: b.clone() } })
    }
    /// A test stub: every revision counts as verified, so grants are not refused for it.
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
    /// No test here hosts a Wasm tool.
    fn channel(&self, _rev: &Digest, _tool: &str) -> Option<topak_contain::wasmtool::Channel> {
        None
    }
}

struct Cluster {
    nodes: Vec<Arc<Mechanism>>,
    hub: Arc<Hub>,
}

async fn cluster(f: &Fixture, real_bundle: bool) -> Cluster {
    let hub = Arc::new(Hub::default());
    let floor_exc = Floor::load().unwrap().exception_count();
    let mut nodes = Vec::new();
    for id in 1..=3u32 {
        let (prop_tx, prop_rx) = mpsc::channel(1024);
        let (in_tx, in_rx) = mpsc::channel(8192);
        hub.register(id, in_tx);
        let bundle: Box<dyn BundleDecider> = if real_bundle {
            let bundles = f.dir.join("bundles");
            let mut local = LocalBundles::load_dir(&bundles, &f.rules.bundle_keys).await.unwrap();
            let built = std::fs::read(bundles.join(format!("{}.tar.gz", f.bundle_rev.0))).unwrap();
            for (revision, data) in &f.extra_bundles {
                let wasm = topak_bundle::read_bundle_tarball(&built).unwrap().wasm;
                let files = topak_bundle::BundleFiles { revision: revision.clone(), wasm, data: data.clone() };
                let issued = topak_bundle::Issued {
                    inside_targets: f.rules.inside_targets.clone(),
                    releasers: f.rules.releasers.clone(),
                };
                local.insert_issued(files, &issued).await.expect("the revision's allowlist is well-formed");
            }
            Box::new(BundleTier::new(None, local))
        } else {
            Box::new(AllowAll)
        };
        let mech = Mechanism::new(Parts {
            id,
            params: f.params.clone(),
            genesis: State::genesis(f.rules.clone(), floor_exc).unwrap(),
            floor: Floor::load().unwrap(),
            bundle,
            transport: Transport::Memory(Memory::default()),
            tools: ToolHost::new(f.tools.clone()),
            corpus_dir: f.dir.join("corpus"),
            data_dir: f.dir.join(format!("n{id}")),
            proposals: prop_tx,
            wasm_tools: f.wasm.clone(),
            contain: None,
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
    // Trace validation (ADR-0045 T-0045-28, stage 1): with TOPAK_TRACE_DIR set, replica 1's
    // every `apply` is recorded for `spec/Mechanism.tla`; the others converge to the same state.
    let fixture = f.dir.file_name().unwrap().to_string_lossy().to_string();
    let fixture = fixture
        .strip_prefix("topak-e2e-")
        .unwrap_or(&fixture)
        .rsplit_once('-')
        .map(|(n, _pid)| n.to_string())
        .unwrap_or(fixture);
    if let Some(name) = topak_core::trace::name_from_env(&format!("e2e-{fixture}")) {
        nodes[0].state.write().unwrap().trace = Some(name);
    }
    let c = Cluster { nodes, hub };
    seat_operators(&c.nodes[0], f).await;
    c
}

/// A sign-on assertion for an operator seat (ADR-0050 §3): the provider's signature over the
/// seat's key and its current fence, as this replica's state has it.
fn sign_on(m: &Mechanism, f: &Fixture, seat: &str) -> Signed {
    let st = m.state.read().unwrap();
    let last = st.last_lease.get(seat).copied().unwrap_or(0);
    let body = topak_core::control::sign_on_body(&st.chain, &pubhex(&f.keys.ops[seat]), st.epoch, last);
    sign(&f.keys.idp, topak_core::control::SIGN_ON_PURPOSE, &body)
}

/// The BOOTSTRAP path's one use (ADR-0050 §2): a first seating. Every operator seat that holds no
/// live lease is seated, each on a sign-on assertion, standing in for the quorum that would.
async fn seat_operators(m: &Mechanism, f: &Fixture) {
    for (name, _) in OPERATORS {
        let (live, round, bundle) = {
            let st = m.state.read().unwrap();
            (st.live_by_seat.contains_key(name), st.last_round.get(name).copied().unwrap_or(0) + 1, f.bundle_rev.clone())
        };
        if live {
            continue;
        }
        let r = m
            .operate(OperatorOp::Grant {
                principal: format!("person-{name}"),
                seat: name.into(),
                persona: Digest::of(format!("persona of {name}").as_bytes()),
                bundle,
                confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
                alphabet: BTreeSet::new(),
                ttl_ms: 3_600_000,
                round,
                role: RoundRole::Author,
                task_label: None,
                task_labels_allowed: None,
                sign_on: Some(sign_on(m, f, name)),
            })
            .await;
        assert_eq!(r["ok"], true, "seating {name}: {r}");
    }
}

/// One signed request from an operator seat (ADR-0050 §4), as its holder would send it.
async fn control(m: &Mechanism, f: &Fixture, op: &str, action: ControlAction) -> Value {
    control_with(m, f, op, action, None, None).await
}

async fn control_with(
    m: &Mechanism,
    f: &Fixture,
    op: &str,
    action: ControlAction,
    assertion: Option<Signed>,
    task: Option<String>,
) -> Value {
    static CTR: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    let ctr = CTR.fetch_add(1, std::sync::atomic::Ordering::SeqCst) + 1;
    let (chain, epoch) = {
        let st = m.state.read().unwrap();
        (st.chain.clone(), st.epoch)
    };
    let request = ControlRequest { operator: op.into(), epoch, ctr, action };
    let sig = sign(&f.keys.ops[op], CONTROL_PURPOSE, &request.body(&chain));
    m.operate(OperatorOp::Control { request, sig, assertion, task }).await
}

/// The first operator of a seat's domain: who a test asks to act on that seat.
fn operator_of(m: &Mechanism, seat: &str) -> &'static str {
    match m.state.read().unwrap().rules.seat_domain(seat) {
        Some(Domain::Run) => "opr1",
        _ => "op1",
    }
}

/// An operator ends a seat's round: a deny, local and attributed.
async fn end_round(m: &Mechanism, f: &Fixture, seat: &str) -> Value {
    control(m, f, operator_of(m, seat), ControlAction::EndRound { target: seat.into() }).await
}

async fn grant(
    m: &Mechanism,
    f: &Fixture,
    seat: &str,
    round: Round,
    role: RoundRole,
    alphabet: &[ActionKind],
    ttl_ms: u64,
) -> String {
    // ADR-0050 §2: a seat's first lease is a seating, and its next round is an operator's.
    if is_successor(m, f, seat) {
        let r = control(m, f, operator_of(m, seat), regrant(seat, round, alphabet, ttl_ms)).await;
        assert_eq!(r["ok"], true, "regrant {seat}: {r}");
        return r["token"].as_str().unwrap().to_string();
    }
    let r = m
        .operate(OperatorOp::Grant {
            principal: format!("principal-{seat}"),
            seat: seat.into(),
            persona: Digest::of(b"persona"),
            bundle: f.bundle_rev.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: alphabet.iter().copied().collect(),
            ttl_ms,
            round,
            role,
            task_label: None,
            task_labels_allowed: None,
            sign_on: None,
        })
        .await;
    assert_eq!(r["ok"], true, "grant {seat}: {r}");
    assert_eq!(r["contained"], false, "rung 0 is Mediated, always");
    r["token"].as_str().unwrap().to_string()
}

/// Whether a lease for `seat` under the fixture's one binding is a successor grant: the seat is
/// seated with that binding, and two operators of its domain are live to make it.
fn is_successor(m: &Mechanism, f: &Fixture, seat: &str) -> bool {
    let st = m.state.read().unwrap();
    let Some(domain) = st.rules.seat_domain(seat) else { return false };
    st.seatings.get(seat).is_some_and(|s| {
        s.principal == format!("principal-{seat}") && s.persona == Digest::of(b"persona") && s.bundle == f.bundle_rev
    }) && st.live_operators(domain).len() >= 2
}

/// A successor grant with no task: its label is declared, and is the empty one.
fn regrant(seat: &str, round: Round, alphabet: &[ActionKind], ttl_ms: u64) -> ControlAction {
    ControlAction::Regrant {
        target: seat.into(),
        round,
        alphabet: alphabet.iter().copied().collect(),
        ttl_ms,
        task: None,
        task_label: Some(BTreeSet::new()),
        sign_on: None,
    }
}

async fn act(m: &Mechanism, token: &str, action: Action) -> AgentResponse {
    m.act(AgentRequest { token: token.into(), op: AgentOp::Act { action } }).await
}

fn deny_reason(r: &AgentResponse) -> String {
    assert!(!r.admitted, "expected a deny, got {}", r.detail);
    r.detail["reason"].to_string()
}

const AUTHOR: &[ActionKind] =
    &[ActionKind::Read, ActionKind::Draft, ActionKind::Invoke, ActionKind::Emit, ActionKind::Submit];
const VOTER: &[ActionKind] = &[ActionKind::Read, ActionKind::Emit, ActionKind::Vote];
const RUN: &[ActionKind] = &[ActionKind::Consult, ActionKind::Actuate, ActionKind::Report];
const RUN_OBS: &[ActionKind] = &[ActionKind::Consult, ActionKind::Report];

fn heartbeat(topic: &str, watermark: u64) -> Value {
    json!({ "heartbeat": { "topic": topic, "watermark": watermark } })
}

async fn settle(c: &Cluster) {
    // Wait until every live replica has applied the same prefix.
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

fn state_json(m: &Mechanism) -> Value {
    serde_json::to_value(&*m.state.read().unwrap()).unwrap()
}

fn memory(m: &Mechanism) -> &Memory {
    match &m.transport {
        Transport::Memory(mem) => mem,
        _ => unreachable!(),
    }
}

fn ws_file(f: &Fixture, node: u32, seat: &str, epoch: Epoch, round: Round, rel: &str) -> PathBuf {
    f.dir.join(format!("n{node}")).join("workspaces").join(format!("ws-{seat}-e{epoch}-r{round}")).join(rel)
}

// ---- the build round, promotion, fencing -----------------------------------------------------

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn build_round_promotion_and_fencing() {
    let f = fixture("build").await;
    let c = cluster(&f, true).await;
    let n1 = &c.nodes[0];

    // ---- an authoring round ----
    let a1 = grant(n1, &f, "a1", 1, RoundRole::Author, AUTHOR, 60_000).await;

    let r = act(n1, &a1, Action::Read { object: f.corpus_obj.clone() }).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["floor"], json!(["B1-read-corpus"]));
    assert_eq!(r.detail["engine"], "local_wasm", "no sidecar: the lease's bundle ran locally");
    assert!(r.detail["result"]["content"].as_str().unwrap().contains("MODULE Lease"));

    let r = act(n1, &a1, Action::Read { object: Digest::of(b"not in the corpus") }).await;
    assert!(deny_reason(&r).contains("FloorNoPermit"), "outside the corpus root, and no forbid fired: {}", r.detail);

    let r = act(n1, &a1, Action::Draft { target: "spec/Lease.tla".into(), content: "VARIABLES lease\n".into() }).await;
    assert!(r.admitted, "{}", r.detail);
    assert!(ws_file(&f, 1, "a1", 0, 1, "spec/Lease.tla").exists());

    let r = act(n1, &a1, Action::Draft { target: "../escape.txt".into(), content: "x".into() }).await;
    assert!(deny_reason(&r).contains("Floor"), "{}", r.detail);

    let r = act(n1, &a1, Action::Emit { record: json!({ "note": "drafted the lease spec" }) }).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["result"]["seq"], 1);

    // Floor permits (allowlisted, inputs workspace-relative) but the bundle has no schema for
    // this tool digest and refuses: the narrowing witness, on the real bundle.
    let (name, digest) = f.tool.split_once('@').unwrap();
    let r = act(
        n1,
        &a1,
        Action::Invoke {
            tool: name.into(),
            digest: Digest(digest.into()),
            inputs: json!({ "path": "spec/Lease.tla" }).as_object().unwrap().clone(),
        },
    )
    .await;
    assert!(deny_reason(&r).contains("Bundle"), "bundle narrows what the floor permits: {}", r.detail);

    // A digest not on the allowlist: the floor refuses.
    let r = act(
        n1,
        &a1,
        Action::Invoke {
            tool: name.into(),
            digest: Digest::of(b"other build"),
            inputs: json!({ "path": "spec/Lease.tla" }).as_object().unwrap().clone(),
        },
    )
    .await;
    assert!(deny_reason(&r).contains("Floor"), "{}", r.detail);

    // Submit the workspace. Terminal for the round: the lease ends and the topic seals.
    let r = n1.act(AgentRequest { token: a1.clone(), op: AgentOp::SubmitWorkspace }).await;
    assert!(r.admitted, "{}", r.detail);
    let artifact = Digest(r.detail["result"]["submitted"].as_str().unwrap().into());
    let r = act(n1, &a1, Action::Emit { record: json!({ "late": true }) }).await;
    assert!(deny_reason(&r).contains("LeaseEnded"), "{}", r.detail);
    settle(&c).await;
    let chain = n1.state.read().unwrap().chain.clone();
    let topic = topak_core::lift::topic_name(&chain, Domain::Build, "a1", 0, 1);
    assert!(memory(n1).sealed.lock().await.contains_key(&topic));
    let records = memory(n1).topics.lock().await[&topic].clone();
    let count = |k| records.iter().filter(|r| r.kind == k).count();
    assert_eq!(count(RecordKind::Emit), 1, "one emission, one emit record");
    // ADR-0020: the four denials under the live lease are in the round's record. The late Emit
    // after Submit found the topic sealed, so it is in the round's `after` companion (ADR-0003 A2).
    assert_eq!(count(RecordKind::Deny), 4, "denials are part of the replayable record");
    let after =
        memory(n1).topics.lock().await[&topak_core::lift::after_topic_name(&chain, Domain::Build, "a1", 0, 1)].clone();
    assert_eq!(after.len(), 1, "the late Emit, and nothing else: {after:?}");
    assert_eq!(after[0].kind, RecordKind::Deny);
    assert!(after[0].payload["reason"].to_string().contains("LeaseEnded"), "{}", after[0].payload);
    assert!(!memory(n1).sealed.lock().await.contains_key(&topak_core::lift::after_topic_name(
        &chain,
        Domain::Build,
        "a1",
        0,
        1
    )));
    for d in records.iter().filter(|r| r.kind == RecordKind::Deny) {
        assert_eq!((d.admit, d.seq), (None, None), "a denial is never ordered");
    }
    let escape = records.iter().find(|r| r.payload["denied"]["target"] == "../escape.txt").expect("escape denial");
    assert_eq!(escape.payload["denied"]["content"], json!(Digest::of(b"x")), "ADR-0004: digests, not payloads");
    assert!(escape.payload["reason"].to_string().contains("Floor"), "{}", escape.payload);

    // ---- promotion ----
    let evidence = Digest::of(b"gate evidence: totality, non-vacuity, discrimination");
    let g1 = grant(n1, &f, "g1", 1, RoundRole::Voter, VOTER, 60_000).await;
    let vote = |v: Verdict, e: &Digest| Action::Vote {
        verdict: v,
        artifact: artifact.clone(),
        evidence: e.clone(),
        rules_epoch: 0,
    };

    // Gates enable voting (ADR-0024 §4): no evidence recorded yet.
    let r = act(n1, &g1, vote(Verdict::Grant, &evidence)).await;
    assert!(deny_reason(&r).contains("GatesNotPassed"), "{}", r.detail);
    let attest = ControlAction::AttestGates { artifact: artifact.clone(), evidence: evidence.clone() };
    let r = control(n1, &f, "op1", attest).await;
    assert_eq!(r["ok"], true, "{r}");
    let r = act(n1, &g1, vote(Verdict::Grant, &Digest::of(b"other evidence"))).await;
    assert!(deny_reason(&r).contains("EvidenceMismatch"), "{}", r.detail);

    // The author is recused. Since ADR-0037 §4 this holds at the grant: a1 is a thinker seat and
    // cannot be issued `Vote` at all, so the B7 envelope (still in the floor) is never reached
    // through the mechanism. The refusal is the grant's, not the admit's. It is asked for as a
    // new seating, under another Persona: as a1's next round it would be an operator's Regrant,
    // which no control entry permits, because it widens (`C1`).
    let r = control(n1, &f, "op1", regrant("a1", 2, VOTER, 60_000)).await;
    assert_eq!((&r["ok"], &r["denied"]), (&json!(false), &json!("floor")), "no control entry permits a wider successor: {r}");
    let r = n1
        .operate(OperatorOp::Grant {
            principal: "principal-a1".into(),
            seat: "a1".into(),
            persona: Digest::of(b"another persona"),
            bundle: f.bundle_rev.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: VOTER.iter().copied().collect(),
            ttl_ms: 60_000,
            round: 2,
            role: RoundRole::Voter,
            task_label: None,
            task_labels_allowed: None,
            sign_on: None,
        })
        .await;
    assert_eq!(r["ok"], false, "a thinker seat is never issued Vote: {r}");
    assert!(r.to_string().contains("thinker alphabet"), "{r}");

    // A veto seat cannot grant (floor B8): neither the cell Observer nor the correlator (ADR-0038 §6).
    let o1 = grant(n1, &f, "o1", 1, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(n1, &o1, vote(Verdict::Grant, &evidence)).await;
    assert!(deny_reason(&r).contains("B8-grant-only-from-grant-seat"), "{}", r.detail);
    let corr = grant(n1, &f, "corr", 1, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(n1, &corr, vote(Verdict::Grant, &evidence)).await;
    assert!(deny_reason(&r).contains("B8-grant-only-from-grant-seat"), "{}", r.detail);

    // Unanimity over counted grant seats {g1, g2, g3}; a1 is not counted.
    let r = act(n1, &g1, vote(Verdict::Grant, &evidence)).await;
    assert!(r.admitted && r.detail["result"]["promoted"] == false, "{}", r.detail);
    // Voting from another replica works the same: the log orders it.
    let n2 = &c.nodes[1];
    let g2 = grant(n2, &f, "g2", 1, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(n2, &g2, vote(Verdict::Grant, &evidence)).await;
    assert!(r.admitted && r.detail["result"]["promoted"] == false, "{}", r.detail);
    let g3 = grant(n1, &f, "g3", 1, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(n1, &g3, vote(Verdict::Grant, &evidence)).await;
    assert!(r.admitted, "{}", r.detail);
    // Every counted grant seat granted and veto silence is not a veto, but the author's round is
    // not yet covered by its cell Observer (ADR-0039 §3; ADR-0024 A2.3 pending): the promotion stalls.
    assert_eq!(r.detail["result"]["promoted"], false, "stalled for coverage: {}", r.detail);
    let seal = n1.state.read().unwrap().seals["a1"].clone();
    assert!(seal.seq >= 1, "a1 emitted in its round: {seal:?}");
    let r = act(n1, &o1, Action::Emit { record: heartbeat(&seal.topic, seal.seq - 1) }).await;
    assert!(r.admitted, "a heartbeat short of the seal is a fact, not coverage: {}", r.detail);
    assert!(n1.state.read().unwrap().candidates[&artifact].promoted_at.is_none(), "still uncovered");
    let r = act(n1, &o1, Action::Emit { record: heartbeat(&seal.topic, seal.seq) }).await;
    assert!(r.admitted, "{}", r.detail);
    settle(&c).await;
    assert!(
        n1.state.read().unwrap().candidates[&artifact].promoted_at.is_some(),
        "coverage to the seal completes the promotion"
    );

    // ---- a targeted revocation ends one principal's round, not the fleet's (ADR-0031 §5 R3) ----
    let r1 = grant(n1, &f, "r1", 1, RoundRole::Author, RUN, 60_000).await;
    // ADR-0039 §2: nothing in Run is admitted until r1's cell Observer is live.
    let r = act(n1, &r1, Action::Report { record: json!({ "valve": "open" }) }).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "{}", r.detail);
    let ro1 = grant(n1, &f, "ro1", 1, RoundRole::Author, RUN_OBS, 60_000).await;
    let r1_topic = topak_core::lift::topic_name(&chain, Domain::Run, "r1", 0, 1);
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&r1_topic, 0) }).await;
    assert!(r.admitted, "{}", r.detail);
    // o1, the veto seat's lease, is still live: the bystander.
    let r = act(n1, &r1, Action::Report { record: json!({ "valve": "open" }) }).await;
    assert!(r.admitted, "{}", r.detail);
    // Every fixture principal shares one Persona digest, so the target here is the principal.
    let revoke =
        ControlAction::Revoke { target: RevocationTarget::Principal("principal-r1".into()), reason: "principal revoked".into() };
    let r = control(n1, &f, "opr1", revoke).await;
    assert_eq!(r["ok"], true, "{r}");
    let r = act(n1, &r1, Action::Report { record: json!({ "valve": "close" }) }).await;
    assert!(
        deny_reason(&r).contains(r#"{"LeaseEnded":"revoked"}"#),
        "rejected by the mechanism, not policy: {}",
        r.detail
    );
    let r = act(n1, &o1, Action::Emit { record: json!({ "unaffected": true }) }).await;
    assert!(r.admitted, "another principal's round survives a targeted revocation: {}", r.detail);
    // The revoked principal keeps trying. Each attempt is in its round's `after` topic, up to the
    // bound (3 in this fixture), then one overflow marker, then nothing (ADR-0003 A2).
    for i in 0..5 {
        let r = act(n1, &r1, Action::Report { record: json!({ "retry": i }) }).await;
        assert!(!r.admitted);
    }
    let run_after = topak_core::lift::after_topic_name(&chain, Domain::Run, "r1", 0, 1);
    let recs = memory(n1).topics.lock().await[&run_after].clone();
    let kinds: Vec<RecordKind> = recs.iter().map(|r| r.kind).collect();
    assert_eq!(kinds, [RecordKind::Deny, RecordKind::Deny, RecordKind::Deny, RecordKind::Overflow], "{recs:?}");
    assert!(recs[0].payload["reason"].to_string().contains(r#"{"LeaseEnded":"revoked"}"#), "{}", recs[0].payload);
    assert_eq!(c.nodes[0].state.read().unwrap().epoch, 0, "a targeted revocation leaves the epoch");

    // ---- the fleet fence ends every live round ----
    let r = control(n1, &f, "op1", ControlAction::FenceEpoch { reason: "e-stop".into() }).await;
    assert_eq!(r["ok"], true, "{r}");
    let r = act(n1, &o1, Action::Emit { record: json!({ "after": "fence" }) }).await;
    assert!(deny_reason(&r).contains("FencedEpoch"), "rejected by the mechanism, not policy: {}", r.detail);

    // ---- every replica holds the same state ----
    settle(&c).await;
    let s1 = state_json(&c.nodes[0]);
    for m in &c.nodes[1..] {
        assert_eq!(state_json(m), s1, "replica {} diverged", m.id);
    }
    assert_eq!(s1["epoch"], 1);
}

// ---- effects through the tool host, break-glass, issuance, partitions -----------------------

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn tools_break_glass_issuance_and_partition() {
    let f = fixture("tools").await;
    let c = cluster(&f, false).await;
    let n1 = &c.nodes[0];
    let (name, digest) = f.tool.split_once('@').unwrap();
    let inputs = json!({ "path": "notes.txt" }).as_object().unwrap().clone();

    // Invoke through rmcp: the tool is spawned, pinned by binary and schema digest, and run in
    // the workspace.
    let a1 = grant(n1, &f, "a1", 1, RoundRole::Author, AUTHOR, 60_000).await;
    let r = act(n1, &a1, Action::Draft { target: "notes.txt".into(), content: "one two\nthree\n".into() }).await;
    assert!(r.admitted, "{}", r.detail);
    let r =
        act(n1, &a1, Action::Invoke { tool: name.into(), digest: Digest(digest.into()), inputs: inputs.clone() }).await;
    assert!(r.admitted, "{}", r.detail);
    let text = r.detail["result"]["content"][0]["text"].as_str().unwrap();
    assert_eq!(serde_json::from_str::<Value>(text).unwrap()["words"], 3);

    // An allow-all bundle still cannot widen the floor: inputs outside the workspace.
    let r = act(
        n1,
        &a1,
        Action::Invoke {
            tool: name.into(),
            digest: Digest(digest.into()),
            inputs: json!({ "path": "/etc/passwd" }).as_object().unwrap().clone(),
        },
    )
    .await;
    assert!(deny_reason(&r).contains("Floor"), "composition bounds the bundle: {}", r.detail);

    // ---- break-glass (X1): a Run tool outside the Run allowlist, inside the envelope ----
    let r1 = grant(n1, &f, "r1", 1, RoundRole::Author, RUN, 60_000).await;
    let ro1 = grant(n1, &f, "ro1", 1, RoundRole::Author, RUN_OBS, 60_000).await;
    let chain = n1.state.read().unwrap().chain.clone();
    let r1_topic = topak_core::lift::topic_name(&chain, Domain::Run, "r1", 0, 1);
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&r1_topic, 0) }).await;
    assert!(r.admitted, "{}", r.detail);
    let run = Action::Actuate { tool: name.into(), digest: Digest(digest.into()), inputs: inputs.clone() };
    let r = act(n1, &r1, run.clone()).await;
    assert!(deny_reason(&r).contains("Floor"), "no quorum yet: {}", r.detail);
    let body = json!({ "seat": "r1", "epoch": 0 });
    for (i, k) in f.keys.bg.iter().enumerate() {
        let r = n1
            .operate(OperatorOp::BreakGlassApprove {
                seat: "r1".into(),
                epoch: 0,
                approval: sign(k, BREAK_GLASS_PURPOSE, &body),
            })
            .await;
        assert_eq!(r["applied"]["BreakGlassApproved"]["approvals"], i + 1, "{r}");
    }
    let foreign = n1
        .operate(OperatorOp::BreakGlassApprove {
            seat: "r1".into(),
            epoch: 0,
            approval: sign(&key(), BREAK_GLASS_PURPOSE, &body),
        })
        .await;
    assert_eq!(foreign["ok"], false, "a key off the roster: {foreign}");
    let r = act(n1, &r1, run.clone()).await;
    // Admitted under X1; the tool runs in an empty Run directory, so the effect itself fails.
    assert_eq!(r.detail["decision"], "admit", "{}", r.detail);
    assert_eq!(r.detail["floor"], json!(["X1-break-glass"]));
    settle(&c).await;
    let archive = std::fs::read_to_string(f.dir.join("n2/archive.jsonl")).unwrap();
    assert!(archive.contains("\"break_glass\":true"), "F5: the break-glass invocation is on every replica's record");

    // ---- anchor issuance, bounded by the rules floor ----
    let sign_all = |rules: &Rules| -> Issuance {
        let body = serde_json::to_value(rules).unwrap();
        Issuance {
            rules: rules.clone(),
            signatures: f.keys.anchors.iter().map(|k| sign(k, ISSUANCE_PURPOSE, &body)).collect(),
        }
    };
    let mut single_signer = f.rules.clone();
    single_signer.rules_epoch = 1;
    single_signer.quorum = Quorum::Threshold(1);
    let r = n1.operate(OperatorOp::Issue { issuance: sign_all(&single_signer) }).await;
    let why = r["applied"]["Rejected"].as_str().unwrap_or_default().to_string();
    assert!(why.contains("R1") && why.contains("R9"), "authentic but floor-violating: {r}");

    let mut empty_roster = f.rules.clone();
    empty_roster.rules_epoch = 1;
    empty_roster.min_grant = 0;
    let r = n1.operate(OperatorOp::Issue { issuance: sign_all(&empty_roster) }).await;
    assert!(r["applied"]["Rejected"].as_str().unwrap_or_default().contains("R2"), "{r}");

    let mut good = f.rules.clone();
    good.rules_epoch = 1;
    good.seats.insert(
        "g4".into(),
        SeatDecl { domain: Domain::Build, kind: topak_core::SeatKind::Grant, cell: None, key: pubhex(&key()), rung: 0 },
    );
    let mut unsigned = sign_all(&good);
    unsigned.signatures.pop();
    let r = n1.operate(OperatorOp::Issue { issuance: unsigned }).await;
    assert!(r["applied"]["Rejected"].as_str().unwrap_or_default().contains("Authentic"), "{r}");

    let r = n1.operate(OperatorOp::Issue { issuance: sign_all(&good) }).await;
    assert_eq!(r["applied"]["Issued"]["rules_epoch"], 1, "{r}");
    let r = act(n1, &a1, Action::Emit { record: json!({}) }).await;
    assert!(deny_reason(&r).contains("RulesChanged") || deny_reason(&r).contains("FencedRulesEpoch"), "{}", r.detail);

    // ---- a partition: isolate the leader; the majority carries on ----
    settle(&c).await;
    let leader = c.nodes.iter().find(|m| m.leader.load(std::sync::atomic::Ordering::Relaxed)).map(|m| m.id).unwrap();
    c.hub.isolated.lock().unwrap().insert(leader);
    let other = c.nodes.iter().find(|m| m.id != leader).unwrap();
    let g1 = grant(other, &f, "g1", 1, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(other, &g1, Action::Emit { record: json!({ "during": "partition" }) }).await;
    assert!(r.admitted, "{}", r.detail);
    // The isolated replica cannot commit anything.
    let isolated = c.nodes.iter().find(|m| m.id == leader).unwrap();
    let r = control(isolated, &f, "op1", ControlAction::FenceEpoch { reason: "from the minority".into() }).await;
    assert_eq!(r["ok"], false, "a minority must not commit: {r}");
    // Heal: the isolated replica catches up to the same state.
    c.hub.isolated.lock().unwrap().clear();
    let mut same = false;
    for _ in 0..200 {
        tokio::time::sleep(Duration::from_millis(25)).await;
        let s: Vec<Value> = c.nodes.iter().map(|m| state_json(m)).collect();
        if s.windows(2).all(|w| w[0] == w[1]) {
            same = true;
            break;
        }
    }
    assert!(same, "replicas did not converge after the partition healed");
    // The minority's fence was re-proposed until its deadline; whether it landed after the
    // heal is timing. Either way every replica agrees on the epoch.
}

// ---- lease expiry is local and subtracting ---------------------------------------------------

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn an_expired_lease_is_ended_and_refused() {
    let f = fixture("expiry").await;
    let c = cluster(&f, true).await;
    let n1 = &c.nodes[0];
    // TTL 400 ms, margin 100 ms: expires at 300 ms on this replica's clock.
    let a1 = grant(n1, &f, "a1", 1, RoundRole::Author, AUTHOR, 400).await;
    let r = act(n1, &a1, Action::Read { object: f.corpus_obj.clone() }).await;
    assert!(r.admitted, "{}", r.detail);
    tokio::time::sleep(Duration::from_millis(700)).await;
    let r = act(n1, &a1, Action::Read { object: f.corpus_obj.clone() }).await;
    let why = deny_reason(&r);
    assert!(why.contains("Expired") || why.contains("LeaseEnded"), "{why}");
    settle(&c).await;
    let st = n1.state.read().unwrap();
    assert!(!st.live_by_seat.contains_key("a1"), "the sweeper ordered EndRound(Expired)");
}

// ---- ADR-0039: Observer liveness couples Run admits ------------------------------------------

/// Coupling.tla restated: `NoAdmitWithoutLiveObserver`, `UnreadBounded` (strict form) and the
/// cross-round grant condition, each refusal seen to fire (ADR-0039 §8). K = 8, T_obs = 5 s are
/// the placeholders in `floor/genesis-values.json`. This test reports and never invokes; the
/// backlog made of invocations is `actuate_is_counted_recorded_and_sealed`.
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn observer_liveness_couples_run_admits() {
    let f = fixture("coupling").await;
    let c = cluster(&f, true).await;
    let n1 = &c.nodes[0];
    let chain = n1.state.read().unwrap().chain.clone();
    let k = n1.state.read().unwrap().observer.k;
    assert_eq!(k, 8, "the placeholder");
    let emit = |i: u64| Action::Report { record: json!({ "i": i }) };

    // No cell Observer lease at all: refused by the floor's R3, with the reason on its face.
    let r1 = grant(n1, &f, "r1", 1, RoundRole::Author, RUN, 60_000).await;
    let r = act(n1, &r1, emit(0)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "no observer lease: {}", r.detail);

    // A lease but no heartbeat: still not live.
    let ro1 = grant(n1, &f, "ro1", 1, RoundRole::Author, RUN_OBS, 60_000).await;
    let r = act(n1, &r1, emit(0)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "no heartbeat yet: {}", r.detail);

    // Dishonest or malformed heartbeats are the mechanism's to refuse (ADR-0039 §1).
    let t1 = topak_core::lift::topic_name(&chain, Domain::Run, "r1", 0, 1);
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, 5) }).await;
    assert!(deny_reason(&r).contains("BadHeartbeat"), "above what exists: {}", r.detail);
    let r = act(n1, &ro1, Action::Report { record: heartbeat("topak.nobody", 0) }).await;
    assert!(deny_reason(&r).contains("BadHeartbeat"), "no such round: {}", r.detail);
    let r = act(n1, &r1, Action::Report { record: heartbeat(&t1, 0) }).await;
    assert!(!r.admitted, "a Thinker does not report liveness: {}", r.detail);

    // An honest heartbeat: live. K admits go through; the K+1th is refused for the backlog.
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, 0) }).await;
    assert!(r.admitted, "{}", r.detail);
    for i in 0..k {
        let r = act(n1, &r1, emit(i)).await;
        assert!(r.admitted, "admit {i} of {k}: {}", r.detail);
    }
    let r = act(n1, &r1, emit(k)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "backlog of {k} unread: {}", r.detail);
    // Presence is not progress (Coupling.tla M_MARK): a fresh heartbeat with the same watermark
    // renews T_obs and nothing else, and the Thinker stays refused for its backlog.
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, 0) }).await;
    assert!(r.admitted, "{}", r.detail);
    let r = act(n1, &r1, emit(k)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "presence is not progress: {}", r.detail);
    // One emission read frees one slot; the next admit refills it.
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, 1) }).await;
    assert!(r.admitted, "{}", r.detail);
    let r = act(n1, &r1, emit(k)).await;
    assert!(r.admitted, "{} unread, one below K: {}", k - 1, r.detail);
    let r = act(n1, &r1, emit(k + 10)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "back at {k} unread: {}", r.detail);
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, 0) }).await;
    assert!(deny_reason(&r).contains("BadHeartbeat"), "a watermark never falls: {}", r.detail);
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, k + 1) }).await;
    assert!(r.admitted, "{}", r.detail);
    let r = act(n1, &r1, emit(k + 10)).await;
    assert!(r.admitted, "caught up: {}", r.detail);

    // A stale heartbeat: T_obs elapses on this replica's clock (with the margin, early).
    let t_obs = n1.state.read().unwrap().observer.t_obs_ms;
    tokio::time::sleep(Duration::from_millis(t_obs + 200)).await;
    let r = act(n1, &r1, emit(k + 1)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "stale: {}", r.detail);
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, k + 1) }).await;
    assert!(r.admitted, "{}", r.detail);
    let r = act(n1, &r1, emit(k + 1)).await;
    assert!(r.admitted, "fresh again: {}", r.detail);

    // Coverage carries across rounds (ADR-0039 §2): round 2 waits until round 1 is read to its seal.
    let r = end_round(n1, &f, "r1").await;
    assert_eq!(r["ok"], true, "{r}");
    let seal = n1.state.read().unwrap().seals["r1"].clone();
    assert_eq!(seal.topic, t1);
    let refused = control(n1, &f, "opr1", regrant("r1", 2, RUN, 60_000)).await;
    assert_eq!(refused["ok"], false, "round 1 is unread past its seal: {refused}");
    assert!(refused.to_string().contains("unread"), "{refused}");
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, seal.seq) }).await;
    assert!(r.admitted, "{}", r.detail);
    let r1b = grant(n1, &f, "r1", 2, RoundRole::Author, RUN, 60_000).await;
    let r = act(n1, &r1b, emit(100)).await;
    assert!(r.admitted, "round 2, fresh Observer, nothing unread: {}", r.detail);

    settle(&c).await;
    let s1 = state_json(&c.nodes[0]);
    for m in &c.nodes[1..] {
        assert_eq!(state_json(m), s1, "marks and seals are replicated; heard is not: replica {} diverged", m.id);
    }
}

// ---- ADR-0042: the sequence counts effects, every Actuate leaves a record, the lease seals ----

/// RunCoupling.tla restated against the running mechanism (ADR-0042 §8, Proposed). The three
/// behaviours the record asks to see: a backlog made of invocations alone is refused past `K`; a
/// `Consult` is admitted while it is; and the next round waits until the invocations are read.
/// Then the record itself (§3), the `unknown` record written ahead of the seal with its result
/// withheld (§3, §4), and the abstain a Run seat may not make (§5).
///
/// On an allow-all bundle: the compiled bundle has no schema, and so no declared channel, for the
/// demo binary's `sleep`, and `actuate.rego` refuses a tool that declares none.
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn actuate_is_counted_recorded_and_sealed() {
    let f = fixture("actuate").await;
    let c = cluster(&f, false).await;
    let n1 = &c.nodes[0];
    let chain = n1.state.read().unwrap().chain.clone();
    let k = n1.state.read().unwrap().observer.k;
    let (name, digest) = f.run_tool.split_once('@').unwrap();
    let sleep = |ms: u64| Action::Actuate {
        tool: name.into(),
        digest: Digest(digest.into()),
        inputs: json!({ "ms": ms }).as_object().unwrap().clone(),
    };
    let seq_of = |m: &Mechanism, seat: &str| m.state.read().unwrap().live_lease(seat).map(|r| (r.seq, r.actions));

    let r1 = grant(n1, &f, "r1", 1, RoundRole::Author, RUN, 60_000).await;
    let ro1 = grant(n1, &f, "ro1", 1, RoundRole::Author, RUN_OBS, 60_000).await;
    let t1 = topak_core::lift::topic_name(&chain, Domain::Run, "r1", 0, 1);

    // Consult is not coupled: admitted before the Observer has said anything at all.
    let r = act(n1, &r1, Action::Consult { object: f.run_obj.clone() }).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["floor"], json!(["R4-consult-pinned"]));
    assert!(r.detail["result"]["content"].as_str().unwrap().contains("closed is safe"));
    // The Run root is its own set: an object in Build's corpus root is not in it.
    let r = act(n1, &r1, Action::Consult { object: f.corpus_obj.clone() }).await;
    assert!(deny_reason(&r).contains("FloorNoPermit"), "outside the Run root: {}", r.detail);
    // An Actuate is an effect, and is coupled.
    let r = act(n1, &r1, sleep(0)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "no heartbeat yet: {}", r.detail);

    // Live. K invocations go through, and nothing else is emitted: the backlog is invocations alone.
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, 0) }).await;
    assert!(r.admitted, "{}", r.detail);
    for i in 1..=k {
        let r = act(n1, &r1, sleep(0)).await;
        assert!(r.admitted, "actuate {i} of {k}: {}", r.detail);
        assert_eq!(r.detail["result"]["seq"], i, "the sequence counts invocations: {}", r.detail);
        assert_eq!(r.detail["result"]["outcome"], "returned");
    }
    assert_eq!(seq_of(n1, "r1"), Some((k, k + 1)), "K effects; K + 1 admits, the Consult among them");
    let r = act(n1, &r1, sleep(0)).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "M_EMITSEQ: {k} invocations unread: {}", r.detail);
    let r = act(n1, &r1, Action::Report { record: json!({ "done": false }) }).await;
    assert!(deny_reason(&r).contains("R3-observer-live"), "a report is an effect too: {}", r.detail);
    // A Thinker whose Observer lags can read and cannot act (ADR-0041 §2).
    let r = act(n1, &r1, Action::Consult { object: f.run_obj.clone() }).await;
    assert!(r.admitted, "Consult while effects are refused: {}", r.detail);
    assert_eq!(seq_of(n1, "r1"), Some((k, k + 2)), "a read is a step and not an effect");

    // The record (ADR-0042 §3): one for each call, written by the mechanism, at the call's sequence.
    {
        let topics = memory(n1).topics.lock().await;
        let recs: Vec<_> = topics[&t1].iter().filter(|r| r.kind == RecordKind::Actuate).collect();
        assert_eq!(recs.len() as u64, k);
        for (i, rec) in recs.iter().enumerate() {
            let env = &rec.payload["actuate"];
            assert_eq!(rec.seq, Some(i as u64 + 1));
            assert!(rec.admit.is_some(), "the admit's log index");
            assert_eq!(rec.digest, Digest::of_json(env), "the record's digest is over its envelope");
            assert_eq!(env["tool"], json!(f.run_tool));
            assert_eq!(env["breakGlass"], false);
            assert_eq!(env["outcome"], "returned");
            assert_eq!(env["inputs"], json!(Digest::of_json(&rec.payload["body"]["inputs"])));
            assert_eq!(env["result"], json!(Digest::of_json(&rec.payload["body"]["result"])));
        }
    }

    // The Observer reads them, and a slow call goes out. The round ends while it is in flight.
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, k) }).await;
    assert!(r.admitted, "{}", r.detail);
    let (node, token, slow) = (n1.clone(), r1.clone(), sleep(1_500));
    let call = tokio::spawn(async move { act(&node, &token, slow).await });
    for _ in 0..200 {
        if seq_of(n1, "r1") == Some((k + 1, k + 3)) {
            break;
        }
        tokio::time::sleep(Duration::from_millis(10)).await;
    }
    assert_eq!(seq_of(n1, "r1"), Some((k + 1, k + 3)), "the slow call's admit has committed");
    // A Run seat cannot abstain (§5). Its round ends with its lease; here the operator ends it.
    let r = n1.act(AgentRequest { token: r1.clone(), op: AgentOp::Abstain }).await;
    assert!(deny_reason(&r).contains("cannot abstain"), "{}", r.detail);
    assert!(seq_of(n1, "r1").is_some(), "the refused abstain ended nothing");
    let r = end_round(n1, &f, "r1").await;
    assert_eq!(r["ok"], true, "{r}");

    // The call returns to a sealed round: its record says `unknown`, and its result is withheld.
    let r = call.await.unwrap();
    assert_eq!(r.detail["result"]["outcome"], "unknown", "{}", r.detail);
    assert!(r.detail["result"].get("result").is_none(), "what was not recorded is not delivered: {}", r.detail);
    {
        let topics = memory(n1).topics.lock().await;
        let last = topics[&t1].iter().rfind(|r| r.kind == RecordKind::Actuate).unwrap();
        assert_eq!(last.seq, Some(k + 1));
        assert_eq!(last.payload["actuate"]["outcome"], "unknown");
        assert_eq!(last.payload["actuate"]["result"], Value::Null);
        assert!(memory(n1).sealed.lock().await.contains_key(&t1), "and the seal marker followed it");
    }

    // The seal counts the invocations, so round 2 waits until they are read (ADR-0039 §2).
    let seal = n1.state.read().unwrap().seals["r1"].clone();
    assert_eq!((seal.topic.as_str(), seal.seq), (t1.as_str(), k + 1));
    let refused = control(n1, &f, "opr1", regrant("r1", 2, RUN, 60_000)).await;
    assert_eq!(refused["ok"], false, "one invocation is unread past the mark: {refused}");
    assert!(refused.to_string().contains("unread"), "{refused}");
    let r = act(n1, &ro1, Action::Report { record: heartbeat(&t1, seal.seq) }).await;
    assert!(r.admitted, "{}", r.detail);
    let r1b = grant(n1, &f, "r1", 2, RoundRole::Author, RUN, 60_000).await;
    let r = act(n1, &r1b, sleep(0)).await;
    assert!(r.admitted, "round 2: {}", r.detail);
    assert_eq!(r.detail["result"]["seq"], 1, "the sequence restarts with the round");

    settle(&c).await;
    let s1 = state_json(&c.nodes[0]);
    for m in &c.nodes[1..] {
        assert_eq!(state_json(m), s1, "the sequence and the seal are replicated: replica {} diverged", m.id);
    }
}

// ---- the tool list (ADR-0048) -----------------------------------------------------------------

/// An allowlist in ADR-0049's form holding the fixture's two real tools, and the built bundle's
/// two entries, which no parameter allowlists. `build` is the Build tool's key and purpose.
fn allowlist(f: &Fixture, build: (&str, &str)) -> Value {
    let (name, digest) = build.0.split_once('@').unwrap();
    let (rname, rdigest) = f.run_tool.split_once('@').unwrap();
    json!({ "topak": { "labels": {
        "vocabulary": ["untrusted", "restricted"],
        "delivery": { "thinker": { "untrusted": "clear", "restricted": "handle" },
                      "observer": { "untrusted": "clear", "restricted": "clear" } },
        "root": { "label": [] },
    }, "tools": {
        build.0: {
            "name": name, "digest": digest, "domain": "build", "purpose": build.1,
            "inputs": { "path": { "type": "string", "required": true, "note": "Workspace-relative path of the file." } },
        },
        f.run_tool.clone(): {
            "name": rname, "digest": rdigest, "domain": "run", "purpose": "Wait, then return.",
            "inputs": { "ms": { "type": "number", "required": true, "note": "Milliseconds to wait.",
                                "destination": false, "accepts": [] } },
            "destinations": "none",
            "result": { "label": ["untrusted"], "releases": [] },
            "channel": { "kind": "none", "target": "timer.internal:0" },
        },
        "tlc@d1": {
            "name": "tlc", "digest": "d1", "domain": "build", "purpose": "Model-check a specification.",
            "inputs": { "spec": { "type": "string", "required": true, "note": "The module." } },
        },
    } } })
}

async fn grant_on(m: &Mechanism, seat: &str, round: Round, bundle: &Digest, alphabet: &[ActionKind]) -> Value {
    let r = m
        .operate(OperatorOp::Grant {
            principal: format!("principal-{seat}"),
            seat: seat.into(),
            persona: Digest::of(b"persona"),
            bundle: bundle.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: alphabet.iter().copied().collect(),
            ttl_ms: 60_000,
            round,
            role: RoundRole::Author,
            task_label: None,
            task_labels_allowed: None,
            sign_on: None,
        })
        .await;
    assert_eq!(r["ok"], true, "grant {seat}: {r}");
    r
}

async fn told(m: &Mechanism, token: &str) -> Value {
    let r = m.act(AgentRequest { token: token.into(), op: AgentOp::ToolList }).await;
    assert!(r.admitted, "{}", r.detail);
    r.detail["tool_list"].clone()
}

/// ADR-0048 §8's behaviours, on the real bundle tier. Two revisions are held: `rev_a`, and
/// `rev_b`, in which the Build tool is promoted under a new digest with new text.
///
/// | Behaviour | Where |
/// |---|---|
/// | The list is the granted revision's allowlist narrowed by the lease, exactly | 1, 5 |
/// | The round's topic opens with the list, which is how an Observer is given it | 2 |
/// | A Thinker calls a tool by the name and digest the list supplied, and is admitted | 3 |
/// | The list does not change inside a round | 4 |
/// | A tool promoted under a new digest reaches the Thinker at its next grant, not before | 4, 6 |
///
/// The fifth, that a bundle with an entry that has no purpose text does not load, is
/// `topak-bundle`'s `w3_interface`.
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn the_tool_list_is_delivered_and_opens_the_round() {
    let mut f = fixture("toollist").await;
    let old = f.tool.clone();
    let new = format!("wordcount@{}", Digest::of(b"the next build of wordcount").0);
    let (rev_a, rev_b) = (Digest("a".repeat(64)), Digest("b".repeat(64)));
    f.extra_bundles = vec![
        (rev_a.0.clone(), allowlist(&f, (&old, "Count the lines, words and bytes of a workspace file."))),
        (rev_b.0.clone(), allowlist(&f, (&new, "Count lines, words, bytes and characters of a workspace file."))),
    ];
    // The floor's allowlist names both builds; which one a lease may call is its revision's.
    f.params.build_tools.insert(new.clone());
    let c = cluster(&f, true).await;
    let n1 = &c.nodes[0];

    // 1. Exact: every entry the lease may call and no other. The revision holds three entries;
    //    `tlc@d1` is on no parameter allowlist and the Run entry is not Build's.
    let g = grant_on(n1, "a1", 1, &rev_a, AUTHOR).await;
    let a1 = g["token"].as_str().unwrap().to_string();
    let given = g["tool_list"].clone();
    let tools = given["list"]["tools"].as_array().unwrap();
    assert_eq!(tools.len(), 1, "{given}");
    assert_eq!(given["list"]["bundle"], json!(rev_a));
    let (name, digest) = (tools[0]["name"].as_str().unwrap(), tools[0]["digest"].as_str().unwrap());
    assert_eq!(tool_id(name, &Digest(digest.into())), old);
    assert_eq!(tools[0]["purpose"], "Count the lines, words and bytes of a workspace file.");
    assert_eq!(tools[0]["inputs"]["path"], json!({ "type": "string", "required": true, "note": "Workspace-relative path of the file." }));
    assert_eq!(given["digest"], json!(Digest::of_json(&given["list"])), "the digest is of the rendered list");

    // 2. The opening record: first on the topic, before anything the principal did, carrying the
    //    list the Thinker was given. An Observer reads it there under W(p), as the correlator does.
    let chain = n1.state.read().unwrap().chain.clone();
    let topic = lift::topic_name(&chain, Domain::Build, "a1", 0, 1);
    let opening = memory(n1).topics.lock().await[&topic][0].clone();
    assert_eq!(opening.kind, RecordKind::Open);
    assert_eq!((opening.seq, opening.admit), (None, None), "not an effect: no sequence number, no admit");
    assert_eq!(json!(opening.digest), given["digest"]);
    assert_eq!(opening.payload["tool_list"], given["list"], "the Observer reads the list the Thinker was given");

    // 3. The Thinker calls the tool by the name and digest the list supplied, with the input the
    //    list describes, and the real bundle admits it. Nothing else told it either.
    let r = act(n1, &a1, Action::Draft { target: "notes.txt".into(), content: "one two\nthree\n".into() }).await;
    assert!(r.admitted, "{}", r.detail);
    let call = |name: &str, digest: &str| Action::Invoke {
        tool: name.into(),
        digest: Digest(digest.into()),
        inputs: json!({ "path": "notes.txt" }).as_object().unwrap().clone(),
    };
    let r = act(n1, &a1, call(name, digest)).await;
    assert!(r.admitted, "a tool on the list, called as the list names it: {}", r.detail);
    assert!(r.detail["result"].to_string().contains("words"), "{}", r.detail);

    // 4. The list is fixed for the round. Revision B is held and verified, and promotes the tool
    //    under a new digest; this lease is told what it was told, and its admits are decided
    //    against that: the new build is not callable under it.
    assert_eq!(told(n1, &a1).await, given);
    let (new_name, new_digest) = new.split_once('@').unwrap();
    let r = act(n1, &a1, call(new_name, new_digest)).await;
    assert!(deny_reason(&r).contains("Bundle"), "not told of it, and refused it: {}", r.detail);
    let r = act(n1, &a1, Action::Emit { record: json!({ "note": "counted" }) }).await;
    assert!(r.admitted, "{}", r.detail);
    {
        let topics = memory(n1).topics.lock().await;
        let recs = &topics[&topic];
        assert_eq!(recs.iter().filter(|r| r.kind == RecordKind::Open).count(), 1, "delivered once");
        assert_eq!(recs[0].kind, RecordKind::Open, "and still first");
    }

    // 5. The lease narrows the list. A Run lease whose alphabet holds no `Actuate` may call
    //    nothing and is given a list of none; one that holds it is given Run's one entry, with
    //    the channel by kind and by whether it is outward, and without its target.
    let g = grant_on(n1, "ro1", 1, &rev_a, &[ActionKind::Consult, ActionKind::Report]).await;
    assert_eq!(g["tool_list"]["list"]["tools"], json!([]), "{g}");
    let g = grant_on(n1, "r1", 1, &rev_a, &[ActionKind::Consult, ActionKind::Actuate, ActionKind::Report]).await;
    let run = g["tool_list"]["list"]["tools"].as_array().unwrap();
    assert_eq!(run.len(), 1, "{g}");
    assert_eq!(tool_id(run[0]["name"].as_str().unwrap(), &Digest(run[0]["digest"].as_str().unwrap().into())), f.run_tool);
    assert_eq!(run[0]["channel"], json!({ "kind": "none", "outward": true }));
    assert_eq!(run[0]["result"]["label"], json!(["untrusted"]));
    assert!(!g["tool_list"].to_string().contains("timer.internal"), "the target is not delivered");

    // 6. The next grant names revision B, and delivers the promoted entry: new digest, new text.
    let r = end_round(n1, &f, "a1").await;
    assert_eq!(r["ok"], true, "{r}");
    let g = grant_on(n1, "a1", 2, &rev_b, AUTHOR).await;
    let a1 = g["token"].as_str().unwrap().to_string();
    let tools = g["tool_list"]["list"]["tools"].as_array().unwrap();
    assert_eq!(tools.len(), 1, "{g}");
    assert_eq!((tools[0]["name"].as_str(), tools[0]["digest"].as_str()), (Some(new_name), Some(new_digest)));
    assert_eq!(tools[0]["purpose"], "Count lines, words, bytes and characters of a workspace file.");
    assert_ne!(g["tool_list"]["digest"], given["digest"]);
    // And the old build, which this revision does not list, is refused under it.
    let r = act(n1, &a1, call(name, digest)).await;
    assert!(deny_reason(&r).contains("Bundle"), "{}", r.detail);
}

// ---- labels and handles (ADR-0047) ------------------------------------------------------------

/// A tool that returns one fixed JSON string, whatever it is given.
const SECRET_TOOL: &str = r#"
(module
  (import "topak" "output" (func $output (param i32 i32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "\"the vault's secret\"")
  (func (export "run") (result i32)
    (call $output (i32.const 0) (i32.const 20))
    (i32.const 0)))
"#;

/// A tool that returns its inputs as it received them: what the tool host handed it.
const INPUTS_TOOL: &str = r#"
(module
  (import "topak" "input_len" (func $input_len (result i32)))
  (import "topak" "input_read" (func $input_read (param i32)))
  (import "topak" "output" (func $output (param i32 i32)))
  (memory (export "memory") 1)
  (func (export "run") (result i32)
    (call $input_read (i32.const 0))
    (call $output (i32.const 0) (call $input_len))
    (i32.const 0)))
"#;

/// ADR-0047 §11's scripted Run cell, on the linked floor (`R5` to `R7`) and the real bundle tier.
/// Six Run tools, hosted as Wasm modules: `web` and `vault` are sources, outside and inside;
/// `summarize` and `archive` are inside tools that take a handle; `post` and `send` are outward.
/// Three bundle revisions differ only in the Thinker's delivery table.
///
/// | Round | Table | What it shows |
/// |---|---|---|
/// | 1 | `untrusted` clear, `restricted` handle | One result clear and another a handle; a handle admitted where its label is accepted and refused where it is not; `R5` and `R6` |
/// | 2 | Both as handles | The outward call `R5` refused is admitted when nothing was read in the clear; `R7` all the same |
/// | 3 | Both clear | A bundle that moves every label to `clear` loads, and the same call is still refused |
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn labels_bound_what_a_round_may_send_after_what_it_has_read() {
    use topak_contain::wasmtool::{WasmToolHost, WasmToolSpec, module_digest};
    let mut f = fixture("labels").await;
    let module = |name: &str, wat_src: &str| {
        let path = f.dir.join(format!("{name}.wasm"));
        std::fs::write(&path, wat::parse_str(wat_src).unwrap()).unwrap();
        let digest = module_digest(&path).unwrap();
        (path, digest)
    };
    let (secret, inputs) = (module("secret", SECRET_TOOL), module("inputs", INPUTS_TOOL));
    let mut specs = BTreeMap::new();
    let mut entries = serde_json::Map::new();
    // name, module, target, label, inputs as (name, destination, accepts)
    type In = (&'static str, bool, &'static [&'static str]);
    let tools: [(&str, &(PathBuf, Digest), &str, &[&str], &[In]); 6] = [
        ("web", &inputs, "web.example:443", &["untrusted"], &[("q", false, &[])]),
        ("vault", &secret, "vault.internal:1", &["restricted"], &[("q", false, &[])]),
        ("summarize", &inputs, "tools.internal:1", &[], &[("text", false, &["restricted", "untrusted"])]),
        ("archive", &inputs, "tools.internal:1", &[], &[("text", false, &["untrusted"])]),
        ("post", &inputs, "paste.example:443", &["untrusted"], &[("body", false, &["restricted", "untrusted"])]),
        ("send", &inputs, "mail.example:25", &["untrusted"], &[("to", true, &["untrusted"]), ("body", false, &[])]),
    ];
    let mut id = BTreeMap::new();
    for (name, (path, digest), target, label, ins) in tools {
        let key = tool_id(name, digest);
        specs.insert(key.clone(), WasmToolSpec { module: path.clone(), module_sha256: digest.clone() });
        f.params.run_tools.insert(key.clone());
        let declared: serde_json::Map<String, Value> = ins
            .iter()
            .map(|(i, destination, accepts)| {
                let d = json!({ "type": "string", "required": true, "note": "An input.",
                                "destination": destination, "accepts": accepts });
                (i.to_string(), d)
            })
            .collect();
        let mut e = json!({
            "name": name, "digest": digest, "domain": "run", "purpose": "A tool of the scripted cell.",
            "inputs": declared, "result": { "label": label, "releases": [] },
            "channel": { "kind": "tcp", "target": target },
        });
        if !ins.iter().any(|(_, destination, _)| *destination) {
            e["destinations"] = json!("none");
        }
        entries.insert(key.clone(), e);
        id.insert(name, (name.to_string(), digest.clone()));
    }
    f.wasm = Some(Arc::new(WasmToolHost::new(specs).unwrap()));
    // The issued rules list what is inside the deployment. Everything else is outward.
    f.rules.inside_targets = ["vault.internal:1", "tools.internal:1"].into_iter().map(String::from).collect();
    let revision = |untrusted: &str, restricted: &str| {
        json!({ "topak": { "labels": {
            "vocabulary": ["untrusted", "restricted"],
            "delivery": { "thinker": { "untrusted": untrusted, "restricted": restricted },
                          "observer": { "untrusted": "clear", "restricted": "clear" } },
            "root": { "label": [] },
        }, "tools": entries.clone() } })
    };
    let (mixed, handles, clear) = (Digest("1".repeat(64)), Digest("2".repeat(64)), Digest("3".repeat(64)));
    f.extra_bundles = vec![
        (mixed.0.clone(), revision("clear", "handle")),
        (handles.0.clone(), revision("handle", "handle")),
        // A bundle that moves every label to `clear` is well-formed, and loads.
        (clear.0.clone(), revision("clear", "clear")),
    ];
    let c = cluster(&f, true).await;
    let n1 = &c.nodes[0];
    let chain = n1.state.read().unwrap().chain.clone();
    let call = |tool: &str, inputs: Value| {
        let (name, digest) = id[tool].clone();
        Action::Actuate { tool: name, digest, inputs: inputs.as_object().unwrap().clone() }
    };
    let handle = |seq: u64| json!({ "handle": { "actuate": seq } });
    let ro1 = grant_on(n1, "ro1", 1, &mixed, RUN_OBS).await["token"].as_str().unwrap().to_string();
    // A round of r1 on `rev`, with its cell Observer live on the round's topic.
    let open = async |round: Round, rev: &Digest| {
        let token = grant_on(n1, "r1", round, rev, RUN).await["token"].as_str().unwrap().to_string();
        let topic = lift::topic_name(&chain, Domain::Run, "r1", 0, round);
        let r = act(n1, &ro1, Action::Report { record: heartbeat(&topic, 0) }).await;
        assert!(r.admitted, "{}", r.detail);
        (token, topic)
    };
    let read_to = async |topic: &str, mark: u64| {
        let r = act(n1, &ro1, Action::Report { record: heartbeat(topic, mark) }).await;
        assert!(r.admitted, "{}", r.detail);
    };
    let close = async |_token: &str| {
        let r = end_round(n1, &f, "r1").await;
        assert_eq!(r["ok"], true, "{r}");
    };
    let record = async |topic: &str, seq: u64| {
        let topics = memory(n1).topics.lock().await;
        topics[topic].iter().find(|r| r.kind == RecordKind::Actuate && r.seq == Some(seq)).cloned().expect("recorded")
    };
    let clear_set = |seat: &str| n1.state.read().unwrap().live_lease(seat).unwrap().labels.clear_set.clone();
    let names = |l: &[&str]| l.iter().map(|s| s.to_string()).collect::<BTreeSet<String>>();

    // ---- round 1: untrusted is delivered clear, restricted as a handle ----
    let (r1, topic) = open(1, &mixed).await;
    // One tool's result is delivered clear, with its label in the envelope.
    let r = act(n1, &r1, call("web", json!({ "q": "news" }))).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!((&r.detail["result"]["delivery"], &r.detail["result"]["label"]), (&json!("clear"), &json!(["untrusted"])));
    assert_eq!(r.detail["result"]["result"], json!({ "q": "news" }));
    assert_eq!(clear_set("r1"), names(&["untrusted"]), "what was read in the clear joins clearSet");
    // Another's is delivered as a handle. Its label covers the literal it was called with, which
    // may carry anything read in the clear (R10). The bytes do not reach the principal, and
    // neither does their digest.
    let r = act(n1, &r1, call("vault", json!({ "q": "the key" }))).await;
    assert!(r.admitted, "{}", r.detail);
    let got = &r.detail["result"];
    assert_eq!((&got["delivery"], &got["label"]), (&json!("handle"), &json!(["restricted", "untrusted"])));
    assert_eq!(got["handle"], json!({ "actuate": 2 }), "named by its place in the record");
    assert!(got.get("result").is_none() && got.get("result_digest").is_none(), "{got}");
    assert!(!r.detail.to_string().contains("secret"), "suppressed: {}", r.detail);
    assert_eq!(clear_set("r1"), names(&["untrusted"]), "a handle adds nothing to clearSet");
    // Suppressed to the Thinker is not suppressed to the Observer: the record holds every fact.
    let rec = record(&topic, 2).await;
    let env = &rec.payload["actuate"];
    assert_eq!(rec.payload["body"]["result"], "the vault's secret");
    assert_eq!((&env["delivery"], &env["resultLabel"]), (&json!("handle"), &json!(["restricted", "untrusted"])));
    assert_eq!((&env["clearSet"], &env["inputLabels"]), (&json!(["untrusted"]), &json!([])));
    read_to(&topic, 2).await;

    // The handle, passed to a tool that accepts its label: admitted. The tool host resolves it,
    // the tool receives the bytes, and the result covers its input, so it too is a handle.
    let r = act(n1, &r1, call("summarize", json!({ "text": handle(2) }))).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["result"]["delivery"], "handle");
    assert!(!r.detail.to_string().contains("secret"), "{}", r.detail);
    let rec = record(&topic, 3).await;
    assert_eq!(rec.payload["body"]["result"], json!({ "text": "the vault's secret" }), "the tool was given the bytes");
    assert_eq!(rec.payload["body"]["inputs"], json!({ "text": handle(2) }), "the record holds what the Thinker sent");
    assert_eq!(rec.payload["actuate"]["inputLabels"], json!(["restricted", "untrusted"]));
    read_to(&topic, 3).await;
    // Passed to a tool that does not accept its label: refused at admit, by the bundle tier.
    let r = act(n1, &r1, call("archive", json!({ "text": handle(2) }))).await;
    assert!(deny_reason(&r).contains("Bundle"), "{}", r.detail);
    let r = act(n1, &r1, call("vault", json!({ "q": handle(2) }))).await;
    assert!(deny_reason(&r).contains("Bundle"), "an input that takes no handle: {}", r.detail);
    // A handle that names nothing in this round resolves to nothing.
    let r = act(n1, &r1, call("summarize", json!({ "text": handle(9) }))).await;
    assert!(deny_reason(&r).contains("names nothing in this round"), "{}", r.detail);

    // F1, read then send: untrusted content was read in the clear, and the outward call carries
    // restricted content, by handle. The floor refuses it, whatever the bundle says.
    let r = act(n1, &r1, call("post", json!({ "body": handle(2) }))).await;
    assert!(deny_reason(&r).contains("R5-no-read-then-send"), "{}", r.detail);
    // F2, steered destination: after the same read, the destination of an outward call is typed.
    let r = act(n1, &r1, call("send", json!({ "to": "someone@elsewhere.example", "body": "hello" }))).await;
    assert!(deny_reason(&r).contains("R6-no-steered-destination"), "{}", r.detail);
    close(&r1).await;

    // ---- round 2: both names are delivered as handles ----
    let (r1, topic) = open(2, &handles).await;
    let r = act(n1, &r1, call("web", json!({ "q": "news" }))).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["result"]["delivery"], "handle");
    let r = act(n1, &r1, call("vault", json!({ "q": "the key" }))).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["result"]["label"], json!(["restricted"]), "nothing was read, so the literal carries nothing");
    assert!(clear_set("r1").is_empty());
    read_to(&topic, 2).await;
    // The call F1 refused in round 1 is admitted: the same item, the same outward tool, and a
    // principal that has read nothing untrusted. It routes what it cannot read.
    let r = act(n1, &r1, call("post", json!({ "body": handle(2) }))).await;
    assert!(r.admitted, "{}", r.detail);
    assert!(!r.detail.to_string().contains("secret"), "{}", r.detail);
    assert_eq!(record(&topic, 3).await.payload["body"]["result"], json!({ "body": "the vault's secret" }));
    read_to(&topic, 3).await;
    // A typed destination is no steering when nothing untrusted was read.
    let r = act(n1, &r1, call("send", json!({ "to": "ops@corp.example", "body": "hello" }))).await;
    assert!(r.admitted, "{}", r.detail);
    read_to(&topic, 4).await;
    // F3, replayed content: the destination is a handle to untrusted content. Refused whatever
    // `clearSet` holds, and here it holds nothing.
    let r = act(n1, &r1, call("send", json!({ "to": handle(1), "body": "hello" }))).await;
    assert!(deny_reason(&r).contains("R7-no-replayed-destination"), "{}", r.detail);
    close(&r1).await;

    // ---- round 3: the bundle that delivers everything clear ----
    let (r1, topic) = open(3, &clear).await;
    let r = act(n1, &r1, call("web", json!({ "q": "news" }))).await;
    assert!(r.admitted, "{}", r.detail);
    let r = act(n1, &r1, call("vault", json!({ "q": "the key" }))).await;
    assert!(r.admitted, "{}", r.detail);
    assert_eq!(r.detail["result"]["result"], "the vault's secret", "delivered clear under this table");
    assert_eq!(clear_set("r1"), names(&["restricted", "untrusted"]));
    read_to(&topic, 2).await;
    // The same call is still refused. Delivering more in the clear bought a narrower round: the
    // floor's forbids are monotone in `clearSet`, and no table reaches past them.
    let r = act(n1, &r1, call("post", json!({ "body": handle(2) }))).await;
    assert!(deny_reason(&r).contains("R5-no-read-then-send"), "{}", r.detail);
    let r = act(n1, &r1, call("post", json!({ "body": "typed out" }))).await;
    assert!(deny_reason(&r).contains("R5-no-read-then-send"), "a literal carries what was read: {}", r.detail);
    close(&r1).await;
}

// ---- the operator as a principal (ADR-0050) ---------------------------------------------------

/// ADR-0050 §10's reference behaviours, on the linked floor's control entries. Three operators
/// are seated in each domain, each on a sign-on assertion, by the BOOTSTRAP path: a first lease
/// from a completed tally is not built, and that path stands in for the quorum.
///
/// | Behaviour | Where |
/// |---|---|
/// | A successor grant carries the round's task and its label; the seating bounds the label | 1 |
/// | A `Regrant` refused for widening | 2 |
/// | Every control action is on the operator's topic | 3 |
/// | An operator stops in its own domain only | 4 |
/// | A lapsed operator: a revocation by key alone refused, with a fresh assertion admitted; its `Regrant` and its fence refused | 5 |
/// | An add refused with no peer | 6 |
/// | The unsigned path stops nothing, and a forged request is not ordered | 7 |
#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn an_operator_is_a_principal_and_its_requests_are_decided() {
    let f = fixture("operators").await;
    let c = cluster(&f, false).await;
    let n1 = &c.nodes[0];
    let chain = n1.state.read().unwrap().chain.clone();
    let floor = |r: &Value| r["floor"].to_string();
    let labels = |l: &[&str]| l.iter().map(|s| s.to_string()).collect::<BTreeSet<String>>();
    assert_eq!(n1.state.read().unwrap().live_operators(Domain::Run).len(), 3);

    // A seating, by the BOOTSTRAP path: r1's first lease, and the labels its tasks may carry.
    let r = n1
        .operate(OperatorOp::Grant {
            principal: "principal-r1".into(),
            seat: "r1".into(),
            persona: Digest::of(b"persona"),
            bundle: f.bundle_rev.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: RUN.iter().copied().collect(),
            ttl_ms: 60_000,
            round: 1,
            role: RoundRole::Author,
            task_label: Some(labels(&["untrusted"])),
            task_labels_allowed: Some(labels(&["untrusted"])),
            sign_on: None,
        })
        .await;
    assert_eq!(r["ok"], true, "{r}");

    // ---- 1. the successor grant, its task and its label ----
    let task = "Close valve v7 and report.";
    let successor = |round: Round, alphabet: &[ActionKind], label: Option<&[&str]>| ControlAction::Regrant {
        target: "r1".into(),
        round,
        alphabet: alphabet.iter().copied().collect(),
        ttl_ms: 60_000,
        task: Some(Digest::of(task.as_bytes())),
        task_label: label.map(labels),
        sign_on: None,
    };
    let with_task = async |op: &str, a: ControlAction| control_with(n1, &f, op, a, None, Some(task.to_string())).await;
    // A live round is not regranted over.
    let r = with_task("opr1", successor(2, RUN, Some(&["untrusted"]))).await;
    assert_eq!((&r["ok"], &r["denied"]), (&json!(false), &json!("floor")), "{r}");
    assert_eq!(end_round(n1, &f, "r1").await["ok"], true);
    // No label on the task (ADR-0047 §1), and a label the seating does not allow (§5).
    let r = with_task("opr1", successor(2, RUN, None)).await;
    assert!(floor(&r).contains("C8-task-label-in-bounds"), "{r}");
    let r = with_task("opr1", successor(2, RUN, Some(&["restricted"]))).await;
    assert!(floor(&r).contains("C8-task-label-in-bounds"), "{r}");
    // The bytes are the ones the signed digest names.
    let r = control_with(n1, &f, "opr1", successor(2, RUN, Some(&["untrusted"])), None, Some("another task".into())).await;
    assert!(r["error"].to_string().contains("not the ones the request's digest names"), "{r}");
    // Granted: the seating's binding, the next round, the task in the round's payload.
    let r = with_task("opr1", successor(2, &[ActionKind::Consult, ActionKind::Report], Some(&["untrusted"]))).await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!(r["floor"], json!(["C1-regrant-successor"]));
    assert_eq!((&r["lease"]["round"], &r["lease"]["principal"]), (&json!(2), &json!("principal-r1")));
    let t2 = lift::topic_name(&chain, Domain::Run, "r1", 0, 2);
    let opening = memory(n1).topics.lock().await[&t2][0].clone();
    assert_eq!(opening.kind, RecordKind::Open);
    assert_eq!(opening.payload["task"], json!({ "digest": Digest::of(task.as_bytes()), "label": ["untrusted"], "text": task }));
    let clear = n1.state.read().unwrap().live_lease("r1").unwrap().labels.clear_set.clone();
    assert_eq!(clear, labels(&["untrusted"]), "the task is delivered clear, and clearSet starts from its label");

    // ---- 2. a successor never widens: round 2 gave up `Actuate`, and round 3 may not take it back ----
    assert_eq!(end_round(n1, &f, "r1").await["ok"], true);
    let r = with_task("opr1", successor(3, RUN, Some(&["untrusted"]))).await;
    assert_eq!((&r["ok"], &r["denied"]), (&json!(false), &json!("floor")), "widening: {r}");
    // An operator neither regrants nor renews itself.
    let own = ControlAction::Renew { target: "opr1".into(), alphabet: BTreeSet::new(), ttl_ms: 1000, sign_on: None };
    assert!(floor(&control(n1, &f, "opr1", own).await).contains("C6-no-self"));
    // A peer renews it, on a sign-on assertion for this boundary.
    let renew = |sign_on| ControlAction::Renew { target: "opr1".into(), alphabet: BTreeSet::new(), ttl_ms: 3_600_000, sign_on };
    let r = control(n1, &f, "opr2", renew(None)).await;
    assert!(r.to_string().contains("fresh sign-on assertion"), "{r}");
    let r = control(n1, &f, "opr2", renew(Some(sign_on(n1, &f, "opr1")))).await;
    assert_eq!(r["ok"], true, "{r}");

    // ---- 3. every control action is on the operator's topic, where its peers read it ----
    {
        let topics = memory(n1).topics.lock().await;
        let t = lift::topic_name(&chain, Domain::Run, "opr1", 0, 1);
        let actions: Vec<String> = topics[&t]
            .iter()
            .filter(|r| r.kind == RecordKind::Control)
            .map(|r| r.payload["control"]["action"].as_str().unwrap().to_string())
            .collect();
        assert_eq!(actions, ["end_round", "regrant", "end_round"], "what was ordered, and nothing that was refused");
    }

    // ---- 4. an operator stops in its own domain ----
    let r = control(n1, &f, "op1", ControlAction::EndRound { target: "opr3".into() }).await;
    assert!(floor(&r).contains("C9-stop-in-own-domain"), "{r}");

    // ---- 5. a lapsed operator ----
    assert_eq!(control(n1, &f, "opr1", ControlAction::EndRound { target: "opr3".into() }).await["ok"], true);
    let _a1 = grant(n1, &f, "a1", 1, RoundRole::Author, AUTHOR, 60_000).await;
    let r1 = with_task("opr1", successor(3, &[ActionKind::Consult], Some(&["untrusted"]))).await;
    assert_eq!(r1["ok"], true, "{r1}");
    let revoke = || ControlAction::Revoke { target: RevocationTarget::Principal("principal-r1".into()), reason: "seen".into() };
    // By its key alone: a key nobody revoked is not a standing lever.
    let r = control(n1, &f, "opr3", revoke()).await;
    assert_eq!((&r["ok"], &r["denied"]), (&json!(false), &json!("floor")), "{r}");
    assert!(n1.state.read().unwrap().live_lease("r1").is_some());
    // An add needs a lease, and the fleet fence does too, whatever the provider says.
    let fresh = || Some(sign_on(n1, &f, "opr3"));
    let r = control_with(n1, &f, "opr3", successor(4, &[ActionKind::Consult], Some(&["untrusted"])), fresh(), Some(task.into())).await;
    assert!(floor(&r).contains("C5-add-needs-lease-and-peer"), "{r}");
    let r = control_with(n1, &f, "opr3", ControlAction::FenceEpoch { reason: "stop".into() }, fresh(), None).await;
    assert!(floor(&r).contains("C7-fence-needs-lease"), "{r}");
    // With a fresh assertion, in its own domain: admitted, and attributed by its signature.
    let r = control_with(n1, &f, "opr3", revoke(), fresh(), None).await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!(r["floor"], json!(["C4-deny"]));
    assert!(n1.state.read().unwrap().live_lease("r1").is_none(), "revoked");
    {
        // It has no open round: its deny is on the `after` companion of its last one.
        let topics = memory(n1).topics.lock().await;
        let after = lift::after_topic_name(&chain, Domain::Run, "opr3", 0, 1);
        assert!(topics[&after].iter().any(|r| r.kind == RecordKind::Control && r.payload["control"]["action"] == "revoke"));
    }

    // ---- 6. an add needs a live peer ----
    assert_eq!(control(n1, &f, "opr1", ControlAction::EndRound { target: "opr2".into() }).await["ok"], true);
    let r = control(n1, &f, "opr1", renew(Some(sign_on(n1, &f, "opr2")))).await;
    assert!(floor(&r).contains("C5-add-needs-lease-and-peer"), "{r}");
    // It can still stop, alone.
    assert_eq!(n1.state.read().unwrap().live_operators(Domain::Run).len(), 1);

    // ---- 7. the unsigned path, and a forgery ----
    let r = n1.operate(OperatorOp::FenceEpoch { reason: "from the socket".into(), attribution: "nobody".into() }).await;
    assert_eq!(r["ok"], false, "{r}");
    assert!(r.to_string().contains("an operator's signed request"), "{r}");
    let r = n1
        .operate(OperatorOp::Revoke {
            target: RevocationTarget::Principal("principal-a1".into()),
            reason: "from the socket".into(),
            attribution: "nobody".into(),
        })
        .await;
    assert_eq!(r["ok"], false, "{r}");
    assert_eq!(n1.state.read().unwrap().epoch, 0);
    assert!(n1.state.read().unwrap().live_lease("a1").is_some());
    // A request for op1's seat, signed with op2's key.
    let request = ControlRequest {
        operator: "op1".into(),
        epoch: 0,
        ctr: 1_000_000,
        action: ControlAction::FenceEpoch { reason: "forged".into() },
    };
    let sig = sign(&f.keys.ops["op2"], CONTROL_PURPOSE, &request.body(&chain));
    let r = n1.operate(OperatorOp::Control { request, sig, assertion: None, task: None }).await;
    assert!(r["error"].to_string().contains("not signed by the operator seat's key"), "{r}");
    // The real one: a live operator fences the fleet by its key alone.
    let r = control(n1, &f, "op1", ControlAction::FenceEpoch { reason: "e-stop".into() }).await;
    assert_eq!(r["ok"], true, "{r}");
    assert_eq!(r["floor"], json!(["C4-deny"]));
    let st = n1.state.read().unwrap();
    assert!(st.epoch == 1 && st.live_by_seat.is_empty(), "every lease is fenced, the operators' with them");
}
