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
    tool: String,
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
    let tools = BTreeMap::from([(
        tool.clone(),
        ToolSpec { command: bin, args: vec![], binary_sha256: bin_digest, mcp_tool: "wordcount".into() },
    )]);

    let params = Params {
        corpus: BTreeSet::from([corpus_obj.clone()]),
        build_tools: BTreeSet::from([tool.clone()]),
        run_tools: BTreeSet::new(),
        round_bound: 50,
        lease_margin_ms: 100,
        after_topic_limit: 3,
    };

    let keys = Keys { anchors: (0..3).map(|_| key()).collect(), bg: (0..2).map(|_| key()).collect() };
    let seat = |d: Domain| SeatDecl { domain: d, key: pubhex(&key()) };
    let rules = Rules {
        rules_epoch: 0,
        quorum: Quorum::All,
        min_grant: 2,
        seats: BTreeMap::from([
            ("a1".into(), seat(Domain::Build)),
            ("g1".into(), seat(Domain::Build)),
            ("g2".into(), seat(Domain::Build)),
            ("g3".into(), seat(Domain::Build)),
            ("o1".into(), seat(Domain::Build)),
            ("r1".into(), seat(Domain::Run)),
        ]),
        // a1 authors and also holds a grant seat, so recusal has something to refuse.
        grant_roster: ["a1", "g1", "g2", "g3"].into_iter().map(String::from).collect(),
        veto_roster: BTreeSet::from(["o1".to_string()]),
        anchor_keys: keys.anchors.iter().map(pubhex).collect(),
        break_glass: Some(BreakGlassRules {
            roster: keys.bg.iter().map(pubhex).collect(),
            quorum: 2,
            tools: BTreeSet::from([tool.clone()]),
            actions: BTreeSet::from(["RunInvoke".to_string()]),
        }),
        erasure_roster: None,
    };

    let bundles = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../bundles");
    let l = LocalBundles::load_dir(&bundles).await.unwrap();
    let bundle_rev = l.revisions().next().expect("run scripts/build-bundle.sh first").clone();

    Fixture { dir, corpus_obj, tool, tools, params, rules, keys, bundle_rev }
}

/// A bundle that allows everything, to exercise effects the real placeholder bundle refuses.
/// It cannot widen anything: composition bounds it by the floor.
struct AllowAll;
impl BundleDecider for AllowAll {
    fn decide<'a>(&'a self, b: &'a Digest, _i: &'a Value) -> BoxFuture<'a, BundleOutcome> {
        Box::pin(async move { BundleOutcome::Allow { engine: BundleEngine::Sidecar, bundle: b.clone() } })
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
            let bundles = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../bundles");
            Box::new(BundleTier::new(None, LocalBundles::load_dir(&bundles).await.unwrap()))
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
const RUN: &[ActionKind] = &[ActionKind::RunInvoke, ActionKind::RunEmit];

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

    // The author is recused: the Vote envelope refuses it (floor B7).
    let a1v = grant(n1, &f, "a1", 2, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(n1, &a1v, vote(Verdict::Grant, &evidence)).await;
    assert!(deny_reason(&r).contains("B7-author-recused"), "{}", r.detail);
    let voter_topic = topak_core::lift::topic_name(&chain, Domain::Build, "a1", 0, 2);
    let denied_vote = memory(n1).topics.lock().await[&voter_topic].clone();
    assert!(
        denied_vote.iter().any(|r| r.kind == RecordKind::Deny && r.payload["reason"].to_string().contains("B7")),
        "the refused vote is in the voter round's record: {denied_vote:?}"
    );

    // A veto seat cannot grant (floor B8).
    let o1 = grant(n1, &f, "o1", 1, RoundRole::Voter, VOTER, 60_000).await;
    let r = act(n1, &o1, vote(Verdict::Grant, &evidence)).await;
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
    assert_eq!(r.detail["result"]["promoted"], true, "every counted grant seat granted; veto silence is not a veto");

    // ---- a targeted revocation ends one principal's round, not the fleet's (ADR-0031 §5 R3) ----
    let r1 = grant(n1, &f, "r1", 1, RoundRole::Author, RUN, 60_000).await;
    // a1v, the recused author's voter lease, is still live: the bystander.
    let r = act(n1, &r1, Action::RunEmit { record: json!({ "valve": "open" }) }).await;
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
    let r = act(n1, &r1, Action::RunEmit { record: json!({ "valve": "close" }) }).await;
    assert!(
        deny_reason(&r).contains(r#"{"LeaseEnded":"revoked"}"#),
        "rejected by the mechanism, not policy: {}",
        r.detail
    );
    let r = act(n1, &a1v, Action::Emit { record: json!({ "unaffected": true }) }).await;
    assert!(r.admitted, "another principal's round survives a targeted revocation: {}", r.detail);
    // The revoked principal keeps trying. Each attempt is in its round's `after` topic, up to the
    // bound (3 in this fixture), then one overflow marker, then nothing (ADR-0003 A2).
    for i in 0..5 {
        let r = act(n1, &r1, Action::RunEmit { record: json!({ "retry": i }) }).await;
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
    let r = act(n1, &a1v, Action::Emit { record: json!({ "after": "fence" }) }).await;
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
    let run = Action::RunInvoke { tool: name.into(), digest: Digest(digest.into()), inputs: inputs.clone() };
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
    good.seats.insert("g4".into(), SeatDecl { domain: Domain::Build, key: pubhex(&key()) });
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
