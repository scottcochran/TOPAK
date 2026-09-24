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
        Ok(c)
    }
}
