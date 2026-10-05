//! ADR-0049 §6: a bundle whose allowlist fails any of W1 to W10 does not load.
//!
//! Each case is the real built bundle in `mechanism/bundles/` with its `data.json` changed in one
//! place, signed under a key the rules carry: the signature is good and the allowlist is not.
//! Build the bundle first with `scripts/build-bundle.sh`.

use std::collections::BTreeSet;
use std::io::Read as _;
use std::path::PathBuf;

use serde_json::{Value, json};
use topak_bundle::*;
use topak_core::authentic::{self, KeyHex};
use topak_core::{Digest, Domain};

const SECRET: [u8; 32] = [9; 32];

fn built() -> (Vec<u8>, String) {
    let p = std::fs::read_dir(PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../bundles"))
        .expect("run scripts/build-bundle.sh first")
        .filter_map(|e| e.ok().map(|e| e.path()))
        .find(|p| p.extension().is_some_and(|x| x == "gz"))
        .expect("run scripts/build-bundle.sh first");
    let rev = p.file_name().unwrap().to_string_lossy().trim_end_matches(".tar.gz").to_string();
    (std::fs::read(p).unwrap(), rev)
}

/// The built bundle with `change` applied to its data, signed, alone in a fresh directory.
fn bundle_with(change: impl FnOnce(&mut Value)) -> (PathBuf, BTreeSet<KeyHex>, Digest) {
    static N: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    let (bytes, rev) = built();
    let mut archive = tar::Archive::new(flate2::read::GzDecoder::new(bytes.as_slice()));
    let mut out = tar::Builder::new(flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::default()));
    let mut change = Some(change);
    for entry in archive.entries().unwrap() {
        let mut entry = entry.unwrap();
        let path = entry.path().unwrap().to_string_lossy().trim_start_matches('/').to_string();
        let mut buf = Vec::new();
        entry.read_to_end(&mut buf).unwrap();
        if path == "data.json" {
            let mut data: Value = serde_json::from_slice(&buf).unwrap();
            (change.take().expect("one data.json"))(&mut data);
            buf = serde_json::to_vec(&data).unwrap();
        }
        let mut h = tar::Header::new_gnu();
        h.set_size(buf.len() as u64);
        h.set_mode(0o644);
        h.set_cksum();
        out.append_data(&mut h, path, buf.as_slice()).unwrap();
    }
    assert!(change.is_none(), "the bundle carries data.json");
    let gz = out.into_inner().unwrap().finish().unwrap();
    let n = N.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
    let dir = std::env::temp_dir().join(format!("topak-allowlist-{}-{n}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join(format!("{rev}.tar.gz")), gz).unwrap();
    let sig = authentic::sign(BUNDLE_PURPOSE, &bundle_body(&rev), &SECRET);
    std::fs::write(dir.join(format!("{rev}.sig")), serde_json::to_vec(&sig).unwrap()).unwrap();
    (dir, BTreeSet::from([sig.key]), Digest(rev))
}

fn search(d: &mut Value) -> &mut Value {
    &mut d["topak"]["tools"]["search@d3"]
}

fn tlc(d: &mut Value) -> &mut Value {
    &mut d["topak"]["tools"]["tlc@d1"]
}

fn without(v: &mut Value, field: &str) {
    v.as_object_mut().unwrap().remove(field);
}

async fn refused(check: &str, change: impl FnOnce(&mut Value)) {
    let (dir, keys, _) = bundle_with(change);
    let err = LocalBundles::load_dir(&dir, &keys).await.err().unwrap_or_else(|| panic!("{check}: the bundle loaded"));
    let err = format!("{err:#}");
    assert!(err.contains("ADR-0049 §6") && err.contains(&format!("{check}: entry")), "{check}: {err}");
}

#[tokio::test]
async fn the_built_bundle_loads_and_its_entries_are_read() {
    let (dir, keys, rev) = bundle_with(|_| {});
    let l = LocalBundles::load_dir(&dir, &keys).await.expect("the reference's allowlist is well-formed");
    let search = l.entry(&rev, "search@d3").expect("the Run entry");
    assert_eq!(search.domain, Domain::Run);
    assert_eq!(search.channel.as_ref().map(|c| c.target.as_str()), Some("search.internal:443"));
    // §4: outward is derived. With no target issued as inside, a channel is outward.
    assert!(search.outward && search.label.contains("untrusted"));
    let tlc = l.entry(&rev, "tlc@d1").expect("the Build entry");
    assert_eq!((tlc.domain, tlc.channel.is_none(), tlc.outward), (Domain::Build, true, false));
    assert!(tlc.inputs["spec"].required && !tlc.inputs["workers"].required);
    assert!(l.entry(&rev, "search@d9").is_none() && l.entry(&Digest("other".into()), "search@d3").is_none());
}

#[tokio::test]
async fn w1_identity() {
    refused("W1", |d| {
        let e = search(d).take();
        without(&mut d["topak"]["tools"], "search@d3");
        d["topak"]["tools"]["search@d9"] = e;
    })
    .await;
    refused("W1", |d| without(tlc(d), "domain")).await;
    refused("W1", |d| tlc(d)["domain"] = json!("both")).await;
}

#[tokio::test]
async fn w2_inputs() {
    refused("W2", |d| search(d)["inputs"]["query"]["type"] = json!("object")).await;
    refused("W2", |d| without(&mut tlc(d)["inputs"]["workers"], "type")).await;
    refused("W2", |d| without(&mut tlc(d)["inputs"]["workers"], "required")).await;
}

#[tokio::test]
async fn w3_interface() {
    refused("W3", |d| tlc(d)["purpose"] = json!("")).await;
    refused("W3", |d| without(search(d), "purpose")).await;
    refused("W3", |d| without(&mut search(d)["inputs"]["limit"], "note")).await;
    refused("W3", |d| tlc(d)["purpose"] = json!("x".repeat(allowlist::PURPOSE_MAX + 1))).await;
    refused("W3", |d| tlc(d)["inputs"]["spec"]["note"] = json!("x".repeat(allowlist::NOTE_MAX + 1))).await;
}

#[tokio::test]
async fn w4_a_run_entry_declares_its_channel() {
    refused("W4", |d| without(search(d), "channel")).await;
    refused("W4", |d| search(d)["channel"] = json!({ "kind": "https" })).await;
    refused("W4", |d| search(d)["channel"] = json!({ "kind": "", "target": "search.internal:443" })).await;
    refused("W4", |d| search(d)["channel"] = json!("https://search.internal")).await;
}

#[tokio::test]
async fn w5_a_build_entry_declares_none() {
    refused("W5", |d| tlc(d)["channel"] = json!({ "kind": "https", "target": "elsewhere.example:443" })).await;
}

#[tokio::test]
async fn w6_labels_are_present_and_in_the_vocabulary() {
    refused("W6", |d| without(search(d), "result")).await;
    refused("W6", |d| search(d)["result"]["label"] = json!(["untrusted", "pii"])).await;
    refused("W6", |d| search(d)["inputs"]["query"]["accepts"] = json!(["pii"])).await;
    // The same name, once the bundle's vocabulary holds it, is no refusal.
    let (dir, keys, rev) = bundle_with(|d| {
        d["topak"]["labels"]["vocabulary"] = json!(["untrusted", "restricted", "pii"]);
        search(d)["result"]["label"] = json!(["untrusted", "pii"]);
    });
    let l = LocalBundles::load_dir(&dir, &keys).await.expect("loads");
    assert!(l.entry(&rev, "search@d3").unwrap().label.contains("pii"));
    // The two reserved names are in every vocabulary, declared or not (ADR-0047 §1).
    let (dir, keys, _) = bundle_with(|d| without(&mut d["topak"], "labels"));
    LocalBundles::load_dir(&dir, &keys).await.expect("loads");
}

#[tokio::test]
async fn w7_an_outward_result_is_untrusted() {
    refused("W7", |d| search(d)["result"]["label"] = json!([])).await;
    // Outward is derived from the issued rules and not from the bundle: with the target issued
    // as inside, the same entry loads.
    let (dir, keys, rev) = bundle_with(|d| {
        search(d)["result"]["label"] = json!([]);
        without(search(d), "destinations");
    });
    let issued = Issued { inside_targets: BTreeSet::from(["search.internal:443".to_string()]), ..Default::default() };
    let l = LocalBundles::load_dir_issued(&dir, &keys, &issued).await.expect("loads");
    assert!(!l.entry(&rev, "search@d3").unwrap().outward);
}

#[tokio::test]
async fn w8_a_reserved_name_is_released_only_by_an_entry_the_rules_name() {
    refused("W8", |d| search(d)["result"]["releases"] = json!(["untrusted"])).await;
    refused("W8", |d| search(d)["result"]["releases"] = json!(["restricted"])).await;
    let (dir, keys, rev) = bundle_with(|d| search(d)["result"]["releases"] = json!(["untrusted"]));
    let issued = Issued { releasers: BTreeSet::from(["search@d3".to_string()]), ..Default::default() };
    let l = LocalBundles::load_dir_issued(&dir, &keys, &issued).await.expect("loads");
    assert!(l.entry(&rev, "search@d3").unwrap().releases.contains("untrusted"));
}

#[tokio::test]
async fn w9_an_outward_entry_marks_a_destination_or_says_it_has_none() {
    refused("W9", |d| without(search(d), "destinations")).await;
    refused("W9", |d| search(d)["destinations"] = json!("some")).await;
    refused("W9", |d| search(d)["inputs"]["query"]["destination"] = json!(true)).await;
    // A marked input in place of "none" is the other way to answer.
    let (dir, keys, rev) = bundle_with(|d| {
        without(search(d), "destinations");
        search(d)["inputs"]["query"]["destination"] = json!(true);
    });
    let l = LocalBundles::load_dir(&dir, &keys).await.expect("loads");
    assert!(l.entry(&rev, "search@d3").unwrap().inputs["query"].destination);
}

/// W10 cannot be written in §8's form: `accepts` and `destination` sit inside the input they
/// describe. What stands in its place is that a field the record does not define is refused, so a
/// misspelt or misplaced one is not silently dropped; and that a Build entry carries no labels (§1).
#[tokio::test]
async fn w10_a_field_the_record_does_not_define_is_refused() {
    refused("§1", |d| search(d)["accepts"] = json!({ "missing": ["untrusted"] })).await;
    refused("§1", |d| search(d)["inputs"]["query"]["desination"] = json!(true)).await;
    refused("§1", |d| tlc(d)["inputs"]["spec"]["destination"] = json!(false)).await;
    refused("§1", |d| tlc(d)["result"] = json!({ "label": [] })).await;
}
