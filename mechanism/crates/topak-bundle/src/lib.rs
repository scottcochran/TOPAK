//! The bundle tier (ADR-0030 §2): per-request Rego, consulted only after the floor permits,
//! and able only to refuse.
//!
//! **Primary: an OPA sidecar.** **Fallback: the same bundle, compiled to WASM, in-process.**
//!
//! The fallback is an *engine* fallback, never a *policy* fallback. The lease names the bundle
//! a principal is admitted against (ADR-0031 §1 `bundle`), and a decision counts only if it
//! came from exactly that bundle:
//!
//! | Sidecar says                                  | Result                                          |
//! |-----------------------------------------------|-------------------------------------------------|
//! | `true`, from the lease's bundle revision      | Allow (sidecar)                                 |
//! | anything else, from the lease's revision      | Refuse (sidecar). Authoritative: no fallback    |
//! | unreachable, error, timeout, non-2xx          | Local WASM iff it holds the lease's revision    |
//! | a different revision (e.g. mid-rollout)       | Local WASM iff it holds the lease's revision    |
//! | local holds no matching revision              | Refuse                                          |
//!
//! Without the digest match, a sidecar outage would silently lift any narrowing the operator
//! pushed after the local copy was built — ADR-0030 §9 finding 3, arriving by another route.
//! Every admit records which engine decided, so a fallback is attributable.

use std::collections::BTreeMap;
use std::io::Read;
use std::path::Path;
use std::sync::Arc;
use std::time::Duration;

use anyhow::{Context as _, bail};
use opa_wasm::wasmtime::{Config, Engine, Module, Store};
use opa_wasm::{DefaultContext, Policy, Runtime};
use serde_json::{Value, json};
use tokio::sync::Mutex;
use topak_core::Digest;
use topak_core::admit::BundleOutcome;
use topak_core::state::BundleEngine;

/// The bundle entrypoint, `data.topak.bundle.allow`.
pub const ENTRYPOINT: &str = "topak/bundle/allow";

// ---- sidecar ---------------------------------------------------------------------------------

pub struct Sidecar {
    base: String,
    http: reqwest::Client,
}

enum SidecarAnswer {
    /// The sidecar evaluated the lease's bundle; `true` only for an affirmative allow.
    Decided(bool),
    /// Reachable, but serving another revision.
    OtherRevision(String),
    Unreachable(String),
}

impl Sidecar {
    pub fn new(base: impl Into<String>, timeout: Duration) -> anyhow::Result<Self> {
        let http = reqwest::Client::builder().timeout(timeout).connect_timeout(timeout).build()?;
        Ok(Self { base: base.into().trim_end_matches('/').to_string(), http })
    }

    async fn ask(&self, want: &Digest, input: &Value) -> SidecarAnswer {
        let url = format!("{}/v1/data/{ENTRYPOINT}?provenance=true", self.base);
        let resp = match self.http.post(&url).json(&json!({ "input": input })).send().await {
            Ok(r) => r,
            Err(e) => return SidecarAnswer::Unreachable(e.to_string()),
        };
        if !resp.status().is_success() {
            return SidecarAnswer::Unreachable(format!("HTTP {}", resp.status()));
        }
        let body: Value = match resp.json().await {
            Ok(b) => b,
            Err(e) => return SidecarAnswer::Unreachable(format!("body: {e}")),
        };
        // Exactly one bundle, and it must be the lease's.
        let revisions: Vec<&str> = body["provenance"]["bundles"]
            .as_object()
            .map(|m| m.values().filter_map(|b| b["revision"].as_str()).collect())
            .unwrap_or_default();
        match revisions.as_slice() {
            [r] if *r == want.0 => SidecarAnswer::Decided(body["result"] == Value::Bool(true)),
            [r] => SidecarAnswer::OtherRevision((*r).to_string()),
            _ => SidecarAnswer::OtherRevision(format!("{} bundles loaded", revisions.len())),
        }
    }
}

// ---- local WASM ------------------------------------------------------------------------------

struct Compiled {
    store: Store<()>,
    policy: Policy<DefaultContext>,
}

/// Compiled bundles on local disk, keyed by revision.
pub struct LocalBundles {
    bundles: BTreeMap<Digest, Arc<Mutex<Compiled>>>,
}

/// The pieces of an OPA bundle tarball the fallback needs.
pub struct BundleFiles {
    pub revision: String,
    pub wasm: Vec<u8>,
    pub data: Value,
}

pub fn read_bundle_tarball(bytes: &[u8]) -> anyhow::Result<BundleFiles> {
    let mut archive = tar::Archive::new(flate2::read::GzDecoder::new(bytes));
    let (mut wasm, mut data, mut manifest) = (None, None, None);
    for entry in archive.entries()? {
        let mut entry = entry?;
        let path = entry.path()?.to_string_lossy().trim_start_matches('/').to_string();
        let mut buf = Vec::new();
        entry.read_to_end(&mut buf)?;
        match path.as_str() {
            "policy.wasm" => wasm = Some(buf),
            "data.json" => data = Some(serde_json::from_slice(&buf)?),
            ".manifest" => manifest = Some(serde_json::from_slice::<Value>(&buf)?),
            _ => {}
        }
    }
    let revision =
        manifest.as_ref().and_then(|m| m["revision"].as_str()).context("bundle has no .manifest revision")?.to_string();
    Ok(BundleFiles {
        revision,
        wasm: wasm.context("bundle has no policy.wasm")?,
        data: data.unwrap_or_else(|| json!({})),
    })
}

impl LocalBundles {
    pub fn empty() -> Self {
        Self { bundles: BTreeMap::new() }
    }

    /// Load every `<revision>.tar.gz` in `dir`. A file whose manifest revision differs from its
    /// name is refused rather than trusted under either name.
    ///
    /// PROVISIONAL (bundle signing): the revision is read from the manifest and not verified
    /// against a signature.
    pub async fn load_dir(dir: &Path) -> anyhow::Result<Self> {
        let mut me = Self::empty();
        if !dir.exists() {
            return Ok(me);
        }
        for entry in std::fs::read_dir(dir)? {
            let path = entry?.path();
            let Some(name) = path.file_name().and_then(|n| n.to_str()) else { continue };
            let Some(stem) = name.strip_suffix(".tar.gz") else { continue };
            let files = read_bundle_tarball(&std::fs::read(&path)?)?;
            if files.revision != stem {
                bail!("{name}: manifest revision {} does not match the file name", files.revision);
            }
            me.insert(files).await?;
        }
        Ok(me)
    }

    pub async fn insert(&mut self, files: BundleFiles) -> anyhow::Result<()> {
        let engine = Engine::new(&Config::new())?;
        let module = Module::new(&engine, &files.wasm)?;
        let mut store = Store::new(&engine, ());
        let runtime = Runtime::new(&mut store, &module).await?;
        if !runtime.entrypoints().contains(ENTRYPOINT) {
            bail!("bundle {} lacks entrypoint {ENTRYPOINT}", files.revision);
        }
        let policy = runtime.with_data(&mut store, &files.data).await?;
        self.bundles.insert(Digest(files.revision), Arc::new(Mutex::new(Compiled { store, policy })));
        Ok(())
    }

    pub fn revisions(&self) -> impl Iterator<Item = &Digest> {
        self.bundles.keys()
    }

    /// `Some(true)` only for an affirmative allow from the named revision. `None` if the
    /// revision is not held locally.
    async fn evaluate(&self, rev: &Digest, input: &Value) -> Option<Result<bool, String>> {
        let compiled = self.bundles.get(rev)?.clone();
        let mut c = compiled.lock().await;
        let Compiled { store, policy } = &mut *c;
        let out: anyhow::Result<Value> = policy.evaluate(&mut *store, ENTRYPOINT, input).await;
        Some(match out {
            // OPA WASM returns a result set: [{"result": <value>}].
            Ok(v) => Ok(v.as_array().is_some_and(|a| a.len() == 1 && a[0]["result"] == Value::Bool(true))),
            Err(e) => Err(e.to_string()),
        })
    }
}

// ---- the tier --------------------------------------------------------------------------------

pub struct BundleTier {
    sidecar: Option<Sidecar>,
    local: LocalBundles,
}

impl BundleTier {
    pub fn new(sidecar: Option<Sidecar>, local: LocalBundles) -> Self {
        Self { sidecar, local }
    }

    /// Ask the bundle whether to refuse. Called only after a floor permit.
    pub async fn decide(&self, lease_bundle: &Digest, input: &Value) -> BundleOutcome {
        let why_local = match &self.sidecar {
            Some(s) => match s.ask(lease_bundle, input).await {
                SidecarAnswer::Decided(true) => {
                    return BundleOutcome::Allow { engine: BundleEngine::Sidecar, bundle: lease_bundle.clone() };
                }
                SidecarAnswer::Decided(false) => {
                    return BundleOutcome::Refuse {
                        engine: Some(BundleEngine::Sidecar),
                        reason: "bundle did not allow".into(),
                    };
                }
                SidecarAnswer::OtherRevision(r) => format!("sidecar serves revision {r}"),
                SidecarAnswer::Unreachable(e) => format!("sidecar unreachable: {e}"),
            },
            None => "no sidecar configured".into(),
        };
        match self.local.evaluate(lease_bundle, input).await {
            Some(Ok(true)) => {
                tracing::warn!(bundle = %lease_bundle.short(), reason = %why_local, "bundle decided by local WASM fallback");
                BundleOutcome::Allow { engine: BundleEngine::LocalWasm, bundle: lease_bundle.clone() }
            }
            Some(Ok(false)) => {
                BundleOutcome::Refuse { engine: Some(BundleEngine::LocalWasm), reason: "bundle did not allow".into() }
            }
            Some(Err(e)) => BundleOutcome::Refuse {
                engine: Some(BundleEngine::LocalWasm),
                reason: format!("local bundle error: {e}"),
            },
            None => BundleOutcome::Refuse {
                engine: None,
                reason: format!("{why_local}; no local bundle matches the lease's bundle {}", lease_bundle.short()),
            },
        }
    }
}
