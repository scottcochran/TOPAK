//! The fallback rule, against the real compiled bundle in `mechanism/bundles/`.
//!
//! Build it first with `scripts/build-bundle.sh`. The sidecar is simulated by a tiny HTTP
//! server so each branch of the rule is reachable: authoritative sidecar deny (no fallback),
//! unreachable sidecar (fallback), revision mismatch (fallback), unknown revision (refuse).

use std::path::PathBuf;
use std::time::Duration;

use std::collections::BTreeSet;
use std::io::{Read as _, Write as _};

use serde_json::{Value, json};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use topak_bundle::*;
use topak_core::Digest;
use topak_core::admit::BundleOutcome;
use topak_core::authentic::{self, KeyHex};
use topak_core::state::BundleEngine;

fn bundles_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../bundles")
}

/// The tracked tarball, built by `scripts/build-bundle.sh`.
fn built_tarball() -> (PathBuf, String) {
    let p = std::fs::read_dir(bundles_dir())
        .expect("run scripts/build-bundle.sh first")
        .filter_map(|e| e.ok().map(|e| e.path()))
        .find(|p| p.extension().is_some_and(|x| x == "gz"))
        .expect("run scripts/build-bundle.sh first");
    let rev = p.file_name().unwrap().to_string_lossy().trim_end_matches(".tar.gz").to_string();
    (p, rev)
}

const SECRET: [u8; 32] = [7; 32];

/// A signed copy of the built bundle in a fresh directory (ADR-0044 §2): the key set the rules
/// would carry, and the revision.
fn signed_dir(name: &str, secret: &[u8; 32]) -> (PathBuf, BTreeSet<KeyHex>, Digest) {
    static N: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    let (tarball, rev) = built_tarball();
    // Tests run in parallel in one process: each call gets its own directory.
    let n = N.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
    let dir = std::env::temp_dir().join(format!("topak-bundle-{name}-{}-{n}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::copy(&tarball, dir.join(format!("{rev}.tar.gz"))).unwrap();
    let sig = authentic::sign(BUNDLE_PURPOSE, &bundle_body(&rev), secret);
    std::fs::write(dir.join(format!("{rev}.sig")), serde_json::to_vec(&sig).unwrap()).unwrap();
    (dir, BTreeSet::from([sig.key]), Digest(rev))
}

async fn local() -> (LocalBundles, Digest) {
    let (dir, keys, rev) = signed_dir("local", &SECRET);
    let l = LocalBundles::load_dir(&dir, &keys).await.expect("signed bundle loads");
    assert!(l.verified(&rev));
    (l, rev)
}

// ---- ADR-0044: a bundle is trusted by its signature, not its file name --------------------------

#[tokio::test]
async fn an_unsigned_bundle_does_not_load() {
    let (dir, keys, rev) = signed_dir("unsigned", &SECRET);
    std::fs::remove_file(dir.join(format!("{}.sig", rev.0))).unwrap();
    let err = LocalBundles::load_dir(&dir, &keys).await.err().expect("refused");
    assert!(err.to_string().contains("no signature file"), "{err}");
}

#[tokio::test]
async fn a_bundle_signed_under_a_key_the_rules_do_not_carry_does_not_load() {
    let (dir, _keys, _) = signed_dir("foreign", &[9; 32]);
    let other = authentic::sign(BUNDLE_PURPOSE, &json!({}), &SECRET).key;
    let err = LocalBundles::load_dir(&dir, &BTreeSet::from([other])).await.err().expect("refused");
    assert!(err.to_string().contains("do not carry"), "{err}");
    let empty = LocalBundles::load_dir(&dir, &BTreeSet::new()).await.err().expect("no keys, nothing loads");
    assert!(empty.to_string().contains("do not carry"), "{empty}");
}

/// The attack ADR-0044's Context names: a tarball renamed to another revision, its manifest
/// forged to match. The name check alone would pass; the signature over the forged revision
/// does not exist, and the one that does exist is over the real revision.
#[tokio::test]
async fn a_renamed_tarball_with_a_forged_manifest_is_refused() {
    let (dir, keys, rev) = signed_dir("forged", &SECRET);
    let forged = "f".repeat(64);
    // Rewrite the tarball with `.manifest` naming the forged revision.
    let bytes = std::fs::read(dir.join(format!("{}.tar.gz", rev.0))).unwrap();
    let mut archive = tar::Archive::new(flate2::read::GzDecoder::new(bytes.as_slice()));
    let mut out = tar::Builder::new(flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::default()));
    for entry in archive.entries().unwrap() {
        let mut entry = entry.unwrap();
        let path = entry.path().unwrap().to_string_lossy().trim_start_matches('/').to_string();
        let mut buf = Vec::new();
        entry.read_to_end(&mut buf).unwrap();
        if path == ".manifest" {
            let mut m: Value = serde_json::from_slice(&buf).unwrap();
            m["revision"] = json!(forged);
            buf = serde_json::to_vec(&m).unwrap();
        }
        let mut h = tar::Header::new_gnu();
        h.set_size(buf.len() as u64);
        h.set_mode(0o644);
        h.set_cksum();
        out.append_data(&mut h, path, buf.as_slice()).unwrap();
    }
    let gz = out.into_inner().unwrap().finish().unwrap();
    std::fs::remove_file(dir.join(format!("{}.tar.gz", rev.0))).unwrap();
    std::fs::write(dir.join(format!("{forged}.tar.gz")), gz).unwrap();
    // 1. With the real signature file renamed beside it: the signature is over the real revision.
    std::fs::rename(dir.join(format!("{}.sig", rev.0)), dir.join(format!("{forged}.sig"))).unwrap();
    let err = LocalBundles::load_dir(&dir, &keys).await.err().expect("refused");
    assert!(err.to_string().contains("does not verify"), "{err}");
    // 2. With no signature at all: refused for that.
    std::fs::remove_file(dir.join(format!("{forged}.sig"))).unwrap();
    let err = LocalBundles::load_dir(&dir, &keys).await.err().expect("refused");
    assert!(err.to_string().contains("no signature file"), "{err}");
    // 3. Only the holder of a bundle key can make the forgery load, and that is signing at
    //    promotion (§4), which is the authority and not the attack.
    let sig = authentic::sign(BUNDLE_PURPOSE, &bundle_body(&forged), &SECRET);
    let mut f = std::fs::File::create(dir.join(format!("{forged}.sig"))).unwrap();
    f.write_all(&serde_json::to_vec(&sig).unwrap()).unwrap();
    assert!(LocalBundles::load_dir(&dir, &keys).await.unwrap().verified(&Digest(forged)));
}

#[tokio::test]
async fn a_sidecar_allow_from_an_unverified_revision_is_refused() {
    let (l, _) = local().await;
    let other = Digest("other-revision".into());
    let url =
        fake_sidecar(json!({ "result": true, "provenance": { "bundles": { "b": { "revision": other.0 } } } })).await;
    let tier = BundleTier::new(Some(sidecar(&url)), l);
    assert!(!tier.verified(&other));
    let out = tier.decide(&other, &invoke(json!({}))).await;
    assert!(matches!(out, BundleOutcome::Refuse { engine: None, .. }), "ADR-0044 §3: {out:?}");
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
