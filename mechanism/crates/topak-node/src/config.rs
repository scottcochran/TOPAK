//! Node configuration. Relative paths resolve against the config file's directory.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use anyhow::Context as _;
use serde::{Deserialize, Serialize};
use topak_mcp::toolhost::ToolSpec;
use topak_paxos::NodeId;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct KafkaConfig {
    pub brokers: Vec<String>,
    #[serde(default = "one")]
    pub replication: i16,
}

fn one() -> i16 {
    1
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NodeConfig {
    pub id: NodeId,
    /// Every replica, including this one: id → `host:port` for replica traffic.
    pub peers: BTreeMap<NodeId, String>,
    pub data_dir: PathBuf,
    pub agent_socket: PathBuf,
    pub operator_socket: PathBuf,
    /// Genesis (or dev) rules. Checked against the rules floor at startup.
    pub rules: PathBuf,
    /// Mechanism parameters (ADR-0022 §3). Must be identical on every replica.
    pub params: PathBuf,
    /// Content-addressed corpus: one file per object, named by its SHA-256.
    pub corpus_dir: PathBuf,
    /// Compiled bundle tarballs, `<revision>.tar.gz`.
    pub bundles_dir: PathBuf,
    /// OPA sidecar base URL. Absent: the local WASM bundle is the only engine.
    #[serde(default)]
    pub opa_sidecar: Option<String>,
    #[serde(default = "sidecar_timeout")]
    pub opa_timeout_ms: u64,
    /// Kafka brokers. Absent: an in-memory transport (single-process demos only).
    #[serde(default)]
    pub kafka: Option<KafkaConfig>,
    /// Downstream tool hosts, keyed by allowlist id `name@digest`.
    #[serde(default)]
    pub tools: BTreeMap<String, ToolSpec>,
    #[serde(default = "hb")]
    pub heartbeat_ms: u64,
    #[serde(default = "et")]
    pub election_timeout_ms: u64,
    /// The launcher (ADR-0036 §6). Absent: this replica grants, and launches nothing.
    #[serde(default)]
    pub contain: Option<ContainConfig>,
}

/// Backends and verifier, by rung. A `sim-cvm` backend or a `sim` verifier is refused unless the
/// binary was built with the `sim` feature, and even then its key counts only if an anchor
/// issuance put it in the rules' `verifier_keys`.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ContainConfig {
    #[serde(default)]
    pub backends: BTreeMap<u8, BackendConfig>,
    /// The rung-3 verifier (T-0045-17).
    #[serde(default)]
    pub verifier: Option<VerifierConfig>,
    /// Retained evidence (F18). Default: `<data_dir>/evidence`.
    #[serde(default)]
    pub evidence_dir: Option<PathBuf>,
    #[serde(default = "hello")]
    pub hello_timeout_ms: u64,
}

fn hello() -> u64 {
    10_000
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum BackendConfig {
    Process {
        command: PathBuf,
        #[serde(default)]
        args: Vec<String>,
    },
    Docker {
        #[serde(default = "docker")]
        docker: PathBuf,
        image_ref: String,
        #[serde(default)]
        args: Vec<String>,
        #[serde(default)]
        mounts: BTreeMap<String, PathBuf>,
    },
    /// SIMULATED rung 3 (topak-contain `sim`).
    SimCvm {
        command: PathBuf,
        #[serde(default)]
        args: Vec<String>,
        model: PathBuf,
        /// Hex, 32 bytes: the simulated platform's endorsement secret.
        chip_secret: String,
        tcb: u64,
    },
    MeasuredBoot,
    Snp,
    Tdx,
}

fn docker() -> PathBuf {
    "docker".into()
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
pub enum VerifierConfig {
    /// A seam: always unreachable, so every rung-3 launch is Unattestable.
    Http { url: String },
    /// SIMULATED (topak-contain `sim`): hex secrets for the verifier, and the platform's
    /// endorsement key it trusts.
    Sim { secret: String, endorsement: String },
}

fn secret(hex_str: &str) -> anyhow::Result<[u8; 32]> {
    hex::decode(hex_str)?.try_into().map_err(|_| anyhow::anyhow!("a secret is 32 bytes"))
}

impl ContainConfig {
    pub fn build(&self, data_dir: &Path) -> anyhow::Result<crate::mechanism::Contain> {
        use std::sync::Arc;
        use topak_contain::appraise::{Appraiser, HttpVerifier, LauncherAssertion};
        use topak_contain::backend::{Backend, ProcessBackend};
        use topak_contain::{docker::DockerBackend, seams};
        let sim_refused = || anyhow::anyhow!("a simulated backend or verifier needs a build with the `sim` feature");
        let mut backends: BTreeMap<u8, Arc<dyn Backend>> = BTreeMap::new();
        for (rung, b) in &self.backends {
            let built: Arc<dyn Backend> = match b.clone() {
                BackendConfig::Process { command, args } => Arc::new(ProcessBackend { command, args }),
                BackendConfig::Docker { docker, image_ref, args, mounts } => {
                    Arc::new(DockerBackend { docker, image_ref, args, mount_sources: mounts })
                }
                BackendConfig::SimCvm { command, args, model, chip_secret, tcb } => {
                    let _ = (&command, &args, &model, &chip_secret, tcb);
                    #[cfg(feature = "sim")]
                    {
                        let p = topak_contain::sim::SimPlatform::new(secret(&chip_secret)?, tcb);
                        Arc::new(topak_contain::sim::SimCvmBackend::new(command, args, model, p))
                    }
                    #[cfg(not(feature = "sim"))]
                    return Err(sim_refused());
                }
                BackendConfig::MeasuredBoot => Arc::new(seams::MeasuredBootBackend),
                BackendConfig::Snp => Arc::new(seams::SnpBackend),
                BackendConfig::Tdx => Arc::new(seams::TdxBackend),
            };
            anyhow::ensure!(
                built.rung() == *rung,
                "a {} backend reaches rung {}, not {rung}",
                built.kind(),
                built.rung()
            );
            backends.insert(*rung, built);
        }
        let mut appraisers: BTreeMap<u8, Arc<dyn Appraiser>> = BTreeMap::from([(1, Arc::new(LauncherAssertion) as _)]);
        match &self.verifier {
            None => {}
            Some(VerifierConfig::Http { url }) => {
                appraisers.insert(3, Arc::new(HttpVerifier { url: url.clone() }));
            }
            Some(VerifierConfig::Sim { secret: s, endorsement }) => {
                let _ = (s, endorsement);
                #[cfg(feature = "sim")]
                appraisers.insert(3, Arc::new(topak_contain::sim::SimVerifier::new(secret(s)?, endorsement.clone())));
                #[cfg(not(feature = "sim"))]
                return Err(sim_refused());
            }
        }
        let _ = (sim_refused, secret);
        Ok(crate::mechanism::Contain {
            backends,
            appraisers,
            evidence_dir: self.evidence_dir.clone().unwrap_or_else(|| data_dir.join("evidence")),
            hello_timeout: std::time::Duration::from_millis(self.hello_timeout_ms),
        })
    }
}

fn sidecar_timeout() -> u64 {
    250
}
fn hb() -> u64 {
    50
}
fn et() -> u64 {
    400
}

impl NodeConfig {
    pub fn load(path: &Path) -> anyhow::Result<Self> {
        let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
        let mut c: NodeConfig = serde_json::from_str(&text)?;
        let base = path.parent().unwrap_or(Path::new("."));
        let fix = |p: &mut PathBuf| {
            if p.is_relative() {
                *p = base.join(&*p);
            }
        };
        fix(&mut c.data_dir);
        fix(&mut c.agent_socket);
        fix(&mut c.operator_socket);
        fix(&mut c.rules);
        fix(&mut c.params);
        fix(&mut c.corpus_dir);
        fix(&mut c.bundles_dir);
        for t in c.tools.values_mut() {
            fix(&mut t.command);
        }
        if let Some(ct) = c.contain.as_mut() {
            if let Some(d) = ct.evidence_dir.as_mut() {
                fix(d);
            }
            for b in ct.backends.values_mut() {
                match b {
                    BackendConfig::Process { command, .. } => fix(command),
                    BackendConfig::SimCvm { command, model, .. } => {
                        fix(command);
                        fix(model);
                    }
                    BackendConfig::Docker { mounts, .. } => mounts.values_mut().for_each(fix),
                    _ => {}
                }
            }
        }
        Ok(c)
    }
}
