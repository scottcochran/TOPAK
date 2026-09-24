//! The fallback rule, against the real compiled bundle in `mechanism/bundles/`.
//!
//! Build it first with `scripts/build-bundle.sh`. The sidecar is simulated by a tiny HTTP
//! server so each branch of the rule is reachable: authoritative sidecar deny (no fallback),
//! unreachable sidecar (fallback), revision mismatch (fallback), unknown revision (refuse).

use std::path::PathBuf;
use std::time::Duration;

use serde_json::{Value, json};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use topak_bundle::*;
use topak_core::Digest;
use topak_core::admit::BundleOutcome;
use topak_core::state::BundleEngine;

fn bundles_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../bundles")
}

async fn local() -> (LocalBundles, Digest) {
    let l = LocalBundles::load_dir(&bundles_dir()).await.expect("bundles load");
    let rev = l.revisions().next().expect("run scripts/build-bundle.sh first").clone();
    (l, rev)
}

fn invoke(inputs: Value) -> Value {
    json!({
        "action": "Invoke",
        "principal": { "seat": "a1", "domain": "build" },
        "resource": { "tool": "tlc", "digest": "d1" },
        "inputs": inputs,
    })
}

/// A one-shot-per-connection fake OPA that answers every query with `body`.
async fn fake_sidecar(body: Value) -> String {
    let l = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let addr = l.local_addr().unwrap();
    tokio::spawn(async move {
        loop {
            let Ok((mut s, _)) = l.accept().await else { return };
            let body = body.to_string();
            tokio::spawn(async move {
                let mut buf = vec![0u8; 65536];
                let _ = s.read(&mut buf).await;
                let resp = format!(
                    "HTTP/1.1 200 OK\r\ncontent-type: application/json\r\ncontent-length: {}\r\nconnection: close\r\n\r\n{}",
                    body.len(),
                    body
                );
                let _ = s.write_all(resp.as_bytes()).await;
            });
        }
    });
    format!("http://{addr}")
}

fn sidecar(url: &str) -> Sidecar {
    Sidecar::new(url, Duration::from_millis(300)).unwrap()
}

#[tokio::test]
async fn unreachable_sidecar_falls_back_to_the_matching_local_bundle() {
    let (l, rev) = local().await;
    let tier = BundleTier::new(Some(sidecar("http://127.0.0.1:1")), l);
    let ok = tier.decide(&rev, &invoke(json!({ "spec": "Lease.tla", "config": "Lease.cfg" }))).await;
    assert_eq!(ok, BundleOutcome::Allow { engine: BundleEngine::LocalWasm, bundle: rev.clone() });
    let bad = tier.decide(&rev, &invoke(json!({ "spec": "Lease.tla" }))).await;
    assert!(matches!(bad, BundleOutcome::Refuse { engine: Some(BundleEngine::LocalWasm), .. }), "{bad:?}");
}

#[tokio::test]
async fn no_local_bundle_for_the_lease_is_a_refusal() {
    let (l, _) = local().await;
    let tier = BundleTier::new(Some(sidecar("http://127.0.0.1:1")), l);
    let out = tier.decide(&Digest("some-other-bundle".into()), &invoke(json!({ "spec": "a", "config": "b" }))).await;
    assert!(matches!(out, BundleOutcome::Refuse { engine: None, .. }), "{out:?}");
}

#[tokio::test]
async fn a_reachable_sidecar_deny_is_authoritative() {
    let (l, rev) = local().await;
    let url =
        fake_sidecar(json!({ "result": false, "provenance": { "bundles": { "b": { "revision": rev.0 } } } })).await;
    let tier = BundleTier::new(Some(sidecar(&url)), l);
    // The local bundle would allow this; the sidecar's deny must stand.
    let out = tier.decide(&rev, &invoke(json!({ "spec": "Lease.tla", "config": "Lease.cfg" }))).await;
    assert!(matches!(out, BundleOutcome::Refuse { engine: Some(BundleEngine::Sidecar), .. }), "{out:?}");
}

#[tokio::test]
async fn a_sidecar_allow_counts_only_from_the_leases_revision() {
    let (l, rev) = local().await;
    let url =
        fake_sidecar(json!({ "result": true, "provenance": { "bundles": { "b": { "revision": "newer" } } } })).await;
    let tier = BundleTier::new(Some(sidecar(&url)), l);
    // Sidecar allows from another revision: ignored; the local lease-matching bundle decides.
    let out = tier.decide(&rev, &invoke(json!({ "spec": "Lease.tla" }))).await;
    assert!(matches!(out, BundleOutcome::Refuse { engine: Some(BundleEngine::LocalWasm), .. }), "{out:?}");
}

#[tokio::test]
async fn a_sidecar_allow_from_the_leases_revision_admits() {
    let (l, rev) = local().await;
    let url =
        fake_sidecar(json!({ "result": true, "provenance": { "bundles": { "b": { "revision": rev.0 } } } })).await;
    let tier = BundleTier::new(Some(sidecar(&url)), l);
    let out = tier.decide(&rev, &invoke(json!({}))).await;
    assert_eq!(out, BundleOutcome::Allow { engine: BundleEngine::Sidecar, bundle: rev });
}

#[tokio::test]
async fn undefined_is_not_allow() {
    let (l, rev) = local().await;
    let url = fake_sidecar(json!({ "provenance": { "bundles": { "b": { "revision": rev.0 } } } })).await;
    let tier = BundleTier::new(Some(sidecar(&url)), l);
    let out = tier.decide(&rev, &invoke(json!({ "spec": "a", "config": "b" }))).await;
    assert!(matches!(out, BundleOutcome::Refuse { .. }), "{out:?}");
}
