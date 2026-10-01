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
}

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
        round_bound: 50,
        lease_margin_ms: 100,
        after_topic_limit: 3,
        run_round_bound: None,
    };

    let keys = Keys { anchors: (0..3).map(|_| key()).collect(), bg: (0..2).map(|_| key()).collect(), bundle: key() };
    let seat = |d: Domain, k: topak_core::SeatKind| SeatDecl { domain: d, kind: k, cell: None, key: pubhex(&key()) };
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
    };

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
    let sig = topak_core::authentic::sign(topak_bundle::BUNDLE_PURPOSE, &topak_bundle::bundle_body(&rev), &keys.bundle.to_bytes());
    std::fs::write(dir.join("bundles").join(format!("{rev}.sig")), serde_json::to_vec(&sig).unwrap()).unwrap();
    let l = LocalBundles::load_dir(&dir.join("bundles"), &rules.bundle_keys).await.unwrap();
    let bundle_rev = l.revisions().next().expect("the signed copy loads").clone();

    Fixture { dir, corpus_obj, run_obj, tool, run_tool, tools, params, rules, keys, bundle_rev }
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
            Box::new(BundleTier::new(None, LocalBundles::load_dir(&bundles, &f.rules.bundle_keys).await.unwrap()))
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
    let fixture = fixture.strip_prefix("topak-e2e-").unwrap_or(&fixture).rsplit_once('-').map(|(n, _pid)| n.to_string()).unwrap_or(fixture);
    if let Some(name) = topak_core::trace::name_from_env(&format!("e2e-{fixture}")) {
        nodes[0].state.write().unwrap().trace = Some(name);
    }
    Cluster { nodes, hub }
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
        })
        .await;
    assert_eq!(r["ok"], true, "grant {seat}: {r}");
    assert_eq!(r["contained"], false, "rung 0 is Mediated, always");
    r["token"].as_str().unwrap().to_string()
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
    let r = n1.operate(OperatorOp::GatesPassed { artifact: artifact.clone(), evidence: evidence.clone() }).await;
    assert_eq!(r["ok"], true, "{r}");
    let r = act(n1, &g1, vote(Verdict::Grant, &Digest::of(b"other evidence"))).await;
    assert!(deny_reason(&r).contains("EvidenceMismatch"), "{}", r.detail);

    // The author is recused. Since ADR-0037 §4 this holds at the grant: a1 is a thinker seat and
    // cannot be issued `Vote` at all, so the B7 envelope (still in the floor) is never reached
    // through the mechanism. The refusal is the grant's, not the admit's.
    let r = n1
        .operate(OperatorOp::Grant {
            principal: "principal-a1".into(),
            seat: "a1".into(),
            persona: Digest::of(b"persona"),
            bundle: f.bundle_rev.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: VOTER.iter().copied().collect(),
            ttl_ms: 60_000,
            round: 2,
            role: RoundRole::Voter,
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
    let r = n1
        .operate(OperatorOp::Revoke {
            target: RevocationTarget::Principal("principal-r1".into()),
            reason: "principal revoked".into(),
            attribution: "operator test".into(),
        })
        .await;
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
    let r = n1.operate(OperatorOp::FenceEpoch { reason: "e-stop".into(), attribution: "operator test".into() }).await;
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
        SeatDecl { domain: Domain::Build, kind: topak_core::SeatKind::Grant, cell: None, key: pubhex(&key()) },
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
    let r = isolated
        .operate(OperatorOp::FenceEpoch { reason: "from the minority".into(), attribution: "test".into() })
        .await;
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
    let r = n1.operate(OperatorOp::EndRound { token: r1.clone(), reason: EndReason::Operator }).await;
    assert_eq!(r["ok"], true, "{r}");
    let seal = n1.state.read().unwrap().seals["r1"].clone();
    assert_eq!(seal.topic, t1);
    let refused = n1
        .operate(OperatorOp::Grant {
            principal: "principal-r1".into(),
            seat: "r1".into(),
            persona: Digest::of(b"persona"),
            bundle: f.bundle_rev.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: RUN.iter().copied().collect(),
            ttl_ms: 60_000,
            round: 2,
            role: RoundRole::Author,
        })
        .await;
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
    let r = n1.operate(OperatorOp::EndRound { token: r1.clone(), reason: EndReason::Operator }).await;
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
    let refused = n1
        .operate(OperatorOp::Grant {
            principal: "principal-r1".into(),
            seat: "r1".into(),
            persona: Digest::of(b"persona"),
            bundle: f.bundle_rev.clone(),
            confinement: topak_core::lease::Confinement { digest: Digest::of(b"none"), rung: 0 },
            alphabet: RUN.iter().copied().collect(),
            ttl_ms: 60_000,
            round: 2,
            role: RoundRole::Author,
        })
        .await;
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
