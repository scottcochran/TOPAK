//! The launcher's steps against a real guest process and a fake mechanism: launch, identity,
//! evidence, appraisal, bridge. What the mechanism does with the result is `topak-node`'s
//! `tests/contain.rs` and `topak-core`'s `tests/confinement.rs`.

use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::Duration;

use serde_json::json;
use tokio::sync::mpsc;
use topak_contain::BoxFuture;
use topak_contain::appraise::*;
use topak_contain::backend::*;
use topak_contain::bridge::*;
use topak_contain::docker::*;
use topak_contain::guest::GuestHello;
use topak_contain::sim::*;
use topak_core::confine::*;
use topak_core::{Digest, LogIndex};
use topak_mcp::proto::{AgentOp, AgentResponse};

const T: Duration = Duration::from_secs(5);

fn guest_bin() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_topak-demo-guest"))
}

/// A Persona bundle: `model.json` naming `weights.bin` by digest. `corrupt` breaks the weights.
fn bundle(name: &str, corrupt: bool) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("topak-contain-{name}-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let weights = b"weights of an in-house model";
    std::fs::write(dir.join("weights.bin"), if corrupt { &b"other weights"[..] } else { &weights[..] }).unwrap();
    let model =
        json!({ "family": "demo", "params": 1000, "weights": "weights.bin", "weights_sha256": Digest::of(weights) });
    std::fs::write(dir.join("model.json"), serde_json::to_vec(&model).unwrap()).unwrap();
    dir.join("model.json")
}

fn profile(image: Option<Digest>, persona: Digest, measurement: Option<String>) -> Profile {
    let clauses =
        Clause::ALL.iter().map(|c| (*c, ClauseDecl { verdict: ClauseVerdict::Pass, why: "test".into() })).collect();
    Profile {
        image,
        launch: json!({ "kind": "host-process" }),
        channel: json!({ "kind": "stdio" }),
        persona: PersonaRef { model_json_sha256: Some(persona) },
        reference: ReferenceValues { launch_measurement: measurement, min_tcb: Some(5) },
        clauses,
        subtractions: Default::default(),
        domain: topak_core::Domain::Build,
    }
}

fn nonce() -> NonceInput {
    NonceInput { epoch: 0, index: 7, principal: "p".into(), round: 1 }
}

async fn launch_and_appraise(
    backend: &dyn Backend,
    appraiser: &dyn Appraiser,
    prof: &Profile,
) -> (Result<Statement, VerifierError>, GuestHello, LaunchedGuest) {
    let d = Digest::of(b"profile");
    let mut g = backend.launch(LaunchRequest { profile: prof, profile_digest: &d, seat: "a1" }).await.unwrap();
    let hello = g.io.read_hello(T).await.unwrap();
    let n = nonce();
    let ge = g.io.attest(&n.digest(), T).await.unwrap();
    let ev = g.handle.evidence(&ge, &hello).unwrap();
    let ctx = AppraiseCtx { nonce: &n, profile: prof, profile_digest: &d, hello: &hello };
    (appraiser.appraise(ctx, &ev).await, hello, g)
}

#[tokio::test]
async fn rung_1_attests_the_launched_image_and_persona_and_nothing_else() {
    let model = bundle("r1", false);
    let persona = Digest::of(&std::fs::read(&model).unwrap());
    let image = file_digest(&guest_bin()).unwrap();
    let b = ProcessBackend { command: guest_bin(), args: vec!["--model".into(), model.display().to_string()] };

    let (r, hello, g) = launch_and_appraise(&b, &LauncherAssertion, &profile(Some(image), persona.clone(), None)).await;
    let (st, sig) = r.unwrap();
    assert_eq!((st.verdict, st.rung, sig), (Appraised::Attested, 1, None));
    assert_eq!(hello.persona, persona);
    assert!(hello.session_key.is_none(), "rung 1 binds no session key: the bridge is the session");
    g.handle.destroy().await;

    // ADR-0036 §7, first refusal: the image is not the profile's. Unattestable, never Contested.
    let (r, _, g) =
        launch_and_appraise(&b, &LauncherAssertion, &profile(Some(Digest::of(b"other")), persona, None)).await;
    assert!(matches!(r, Err(VerifierError::Malformed(ref s)) if s.contains("image")), "{r:?}");
    g.handle.destroy().await;
}

#[tokio::test]
async fn a_guest_that_cannot_verify_its_bundle_writes_no_identity() {
    // ADR-0036 §7, second refusal.
    let model = bundle("corrupt", true);
    let b = ProcessBackend { command: guest_bin(), args: vec!["--model".into(), model.display().to_string()] };
    let p = profile(None, Digest::of(b"x"), None);
    let d = Digest::of(b"profile");
    let mut g = b.launch(LaunchRequest { profile: &p, profile_digest: &d, seat: "a1" }).await.unwrap();
    let e = g.io.read_hello(T).await.unwrap_err();
    assert!(e.contains("closed"), "{e}");
}

/// A mechanism that records what it was asked.
struct Recorder(Mutex<Vec<(LogIndex, String, bool)>>);

impl ActSink for Recorder {
    fn act_bound<'a>(
        &'a self,
        fence: LogIndex,
        op: AgentOp,
        proof: Option<SessionProof>,
    ) -> BoxFuture<'a, AgentResponse> {
        let kind = serde_json::to_value(&op).unwrap()["op"].as_str().unwrap().to_string();
        self.0.lock().unwrap().push((fence, kind, proof.is_some()));
        Box::pin(async { AgentResponse { admitted: true, detail: json!({}) } })
    }
}

#[tokio::test]
async fn the_bridge_carries_the_round_and_re_attests_between_actions() {
    let model = bundle("bridge", false);
    let platform = SimPlatform::new([3; 32], 6);
    let args = vec![
        "--model".into(),
        model.display().to_string(),
        "--rung".into(),
        "3".into(),
        "--read".into(),
        Digest::of(b"obj").0,
        "--script".into(),
        "read,draft,emit,submit".into(),
    ];
    let b = SimCvmBackend::new(guest_bin(), args, model.clone(), platform);
    let d = Digest::of(b"profile");
    let p = profile(Some(file_digest(&guest_bin()).unwrap()), Digest::of(b"x"), None);
    let mut g = b.launch(LaunchRequest { profile: &p, profile_digest: &d, seat: "a1" }).await.unwrap();
    let hello = g.io.read_hello(T).await.unwrap();
    assert!(hello.session_key.is_some());
    g.io.attest(&nonce().digest(), T).await.unwrap();

    let sink = Arc::new(Recorder(Mutex::new(vec![])));
    let (tx, rx) = mpsc::channel(4);
    tx.send(Ctl::Granted { fence: 9, epoch: 0 }).await.unwrap();
    let run = tokio::spawn(bridge(g.io, 9, sink.clone(), rx));
    // Re-attestation while the round runs: the evidence comes back through the bridge.
    let (etx, erx) = tokio::sync::oneshot::channel();
    tx.send(Ctl::Attest { nonce: Digest::of(b"renewal nonce"), reply: etx }).await.unwrap();
    let ev = tokio::time::timeout(T, erx).await.unwrap().unwrap();
    assert_eq!(ev.report_data, report_data(&Digest::of(b"renewal nonce"), hello.session_key.as_ref()));
    tx.send(Ctl::Granted { fence: 12, epoch: 0 }).await.unwrap();
    for _ in 0..50 {
        if sink.0.lock().unwrap().len() == 4 {
            break;
        }
        tokio::time::sleep(Duration::from_millis(20)).await;
    }
    tx.send(Ctl::Shutdown).await.unwrap();
    assert_eq!(tokio::time::timeout(T, run).await.unwrap().unwrap(), BridgeEnd::Shutdown);
    let seen = sink.0.lock().unwrap().clone();
    let kinds: Vec<&str> = seen.iter().map(|(_, k, _)| k.as_str()).collect();
    assert_eq!(kinds, ["act", "act", "act", "submit_workspace"]);
    assert!(seen.iter().all(|(_, _, signed)| *signed), "every action at rung 3 carries the guest's proof");
}

#[tokio::test]
async fn the_simulated_verifier_attests_contests_and_refuses() {
    let model = bundle("sim", false);
    let persona = Digest::of(&std::fs::read(&model).unwrap());
    let platform = SimPlatform::new([3; 32], 6);
    let args = vec!["--model".into(), model.display().to_string(), "--rung".into(), "3".into()];
    let b = SimCvmBackend::new(guest_bin(), args, model.clone(), platform.clone());
    let v = SimVerifier::new([4; 32], platform.endorsement_key());
    let good =
        profile(Some(file_digest(&guest_bin()).unwrap()), persona.clone(), Some(b.expected_measurement().unwrap()));

    let (r, hello, g) = launch_and_appraise(&b, &v, &good).await;
    let (st, sig) = r.unwrap();
    assert_eq!(st.verdict, Appraised::Attested);
    assert_eq!(st.session_key, hello.session_key, "the statement binds the guest's key");
    let sig = sig.unwrap();
    assert_eq!(sig.key, v.key());
    assert!(topak_core::authentic::verify(APPRAISAL_PURPOSE, &serde_json::to_value(&st).unwrap(), &sig));
    g.handle.destroy().await;

    // A rogue image: signed, measured, and not the profile's. Contested.
    b.rogue.store(true, std::sync::atomic::Ordering::SeqCst);
    let (r, _, g) = launch_and_appraise(&b, &v, &good).await;
    assert_eq!(r.unwrap().0.verdict, Appraised::Contested);
    g.handle.destroy().await;
    b.rogue.store(false, std::sync::atomic::Ordering::SeqCst);

    // PC/EC: an unreachable verifier, and a TCB the verifier no longer accepts. Unattestable.
    v.reachable.store(false, std::sync::atomic::Ordering::SeqCst);
    let (r, _, g) = launch_and_appraise(&b, &v, &good).await;
    assert_eq!(r.unwrap_err(), VerifierError::Unreachable);
    g.handle.destroy().await;
    v.reachable.store(true, std::sync::atomic::Ordering::SeqCst);
    v.min_tcb.store(7, std::sync::atomic::Ordering::SeqCst);
    let (r, _, g) = launch_and_appraise(&b, &v, &good).await;
    assert!(matches!(r, Err(VerifierError::EndorsementExpired(_))), "{r:?}");
    g.handle.destroy().await;
}

#[test]
fn the_docker_launch_part_is_applied_and_cannot_be_loosened() {
    let b = DockerBackend {
        docker: "docker".into(),
        image_ref: "topak-guest".into(),
        args: vec!["--model".into(), "/model/model.json".into()],
        mount_sources: [("/model/model.json".to_string(), PathBuf::from("/host/model.json"))].into(),
    };
    let launch = |v: serde_json::Value| serde_json::from_value::<DockerLaunch>(v).unwrap();
    let ok = launch(json!({
        "kind": "docker", "network": "none", "read_only": true, "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges"], "ipc": "none", "pids_limit": 64, "user": "10001:10001",
        "tmpfs": ["/tmp:rw,noexec,nosuid,nodev,size=16m"], "mounts": [{ "dst": "/model/model.json", "mode": "ro" }],
    }));
    let a = b.run_args(&ok, "topak-x").unwrap().join(" ");
    for want in [
        "--network none",
        "--read-only",
        "--cap-drop ALL",
        "--ipc none",
        "--pids-limit 64",
        "dst=/model/model.json,readonly",
    ] {
        assert!(a.contains(want), "{want} missing from {a}");
    }
    assert!(a.ends_with("topak-guest --model /model/model.json"));
    let net = launch(json!({ "kind": "docker", "network": "bridge", "read_only": true }));
    assert!(b.run_args(&net, "x").is_err(), "P1");
    let rw = launch(
        json!({ "kind": "docker", "network": "none", "read_only": true, "mounts": [{ "dst": "/model/model.json", "mode": "rw" }] }),
    );
    assert!(b.run_args(&rw, "x").is_err(), "P2");
}

/// ADR-0036 §4's guest in a real container, gated: `TOPAK_DOCKER_IMAGE=<an image with python3>`.
/// The profile's `launch` part is what the runtime applies; its `image` is the image's content
/// digest, so the launcher's assertion is about what ran.
#[tokio::test]
async fn a_container_guest_is_launched_appraised_and_bridged() {
    let Ok(image_ref) = std::env::var("TOPAK_DOCKER_IMAGE") else {
        eprintln!("skipped: set TOPAK_DOCKER_IMAGE to an image with python3");
        return;
    };
    let model = bundle("docker", false);
    let dir = model.parent().unwrap().to_path_buf();
    let guest = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("guest/demo_guest.py");
    let b = DockerBackend {
        docker: "docker".into(),
        image_ref,
        args: ["python3", "/guest/demo_guest.py", "--model", "/model/model.json", "--script", "draft"]
            .map(String::from)
            .to_vec(),
        mount_sources: [
            ("/guest/demo_guest.py".to_string(), guest),
            ("/model/model.json".to_string(), dir.join("model.json")),
            ("/model/weights.bin".to_string(), dir.join("weights.bin")),
        ]
        .into(),
    };
    let persona = Digest::of(&std::fs::read(&model).unwrap());
    let mut p = profile(Some(b.image_digest().await.unwrap()), persona.clone(), None);
    p.launch = json!({
        "kind": "docker", "network": "none", "read_only": true, "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges"], "ipc": "none", "pids_limit": 64, "user": "65534:65534",
        "tmpfs": ["/tmp:rw,noexec,nosuid,nodev,size=16m"],
        "mounts": [
            { "dst": "/guest/demo_guest.py", "mode": "ro" },
            { "dst": "/model/model.json", "mode": "ro" },
            { "dst": "/model/weights.bin", "mode": "ro" },
        ],
    });
    let (r, hello, g) = launch_and_appraise(&b, &LauncherAssertion, &p).await;
    assert_eq!(r.unwrap().0.verdict, Appraised::Attested);
    assert_eq!(hello.persona, persona, "the Persona inside the container is the profile's");

    let sink = Arc::new(Recorder(Mutex::new(vec![])));
    let (tx, rx) = mpsc::channel(4);
    tx.send(Ctl::Granted { fence: 5, epoch: 0 }).await.unwrap();
    let run = tokio::spawn(bridge(g.io, 5, sink.clone(), rx));
    for _ in 0..100 {
        if !sink.0.lock().unwrap().is_empty() {
            break;
        }
        tokio::time::sleep(Duration::from_millis(50)).await;
    }
    tx.send(Ctl::Shutdown).await.unwrap();
    assert_eq!(tokio::time::timeout(T, run).await.unwrap().unwrap(), BridgeEnd::Shutdown);
    assert_eq!(sink.0.lock().unwrap().clone(), vec![(5, "act".to_string(), false)], "one token-less action");
    g.handle.destroy().await;

    // The wrong image: a different digest in the profile. Unattestable.
    p.image = Some(Digest::of(b"another image"));
    let (r, _, g) = launch_and_appraise(&b, &LauncherAssertion, &p).await;
    assert!(r.is_err());
    g.handle.destroy().await;
}
