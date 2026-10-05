//! A TOPAK mechanism replica.
//!
//! ```text
//!  agent ──MCP/stdio──▶ topak mcp ──unix socket──▶ ┌──────────── node ────────────┐
//!                                                  │ session → ActionRequest       │
//!                                                  │ epoch fence, lease   (core)   │
//!                                                  │ lift → frozen input  (core)   │
//!                                                  │ floor: Cedar, linked (floor)  │
//!                                                  │ bundle: OPA sidecar | WASM    │
//!                                                  │ Admit ─▶ Paxos ─▶ commit      │
//!                                                  │ effect: read/draft/tool/emit  │
//!                                                  └──────────────┬────────────────┘
//!  operator ──unix socket──▶ grant/renew/revoke/issue/gates       └─▶ Kafka round topics
//! ```

pub mod api;
pub mod config;
pub mod driver;
pub mod mechanism;
pub mod net;
pub mod ops;
pub mod wal;

use std::sync::Arc;
use std::time::Duration;

use anyhow::Context as _;
use tokio::sync::mpsc;
use topak_bundle::{BundleTier, LocalBundles, Sidecar};
use topak_core::rules::Rules;
use topak_core::state::{Params, State};
use topak_floor::Floor;
use topak_mcp::toolhost::ToolHost;
use topak_transport::{Kafka, Memory, Transport};

use crate::config::NodeConfig;
use crate::mechanism::{Mechanism, Parts};

/// Genesis state from a rules file: refuses rules that violate the rules floor (the runtime
/// stand-in for the unwritten `GenesisSatisfiesFloor`).
pub fn genesis(rules_path: &std::path::Path, floor: &Floor) -> anyhow::Result<State> {
    let rules: Rules = serde_json::from_str(&std::fs::read_to_string(rules_path)?)
        .with_context(|| format!("parsing {}", rules_path.display()))?;
    State::genesis(rules, floor.exception_count()).map_err(|v| {
        anyhow::anyhow!(
            "rules violate the rules floor: {}",
            v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join("; ")
        )
    })
}

/// Start one replica: floor, rules, bundle tier, transport, Paxos, sockets.
pub async fn start_node(cfg: NodeConfig) -> anyhow::Result<Arc<Mechanism>> {
    let floor = Floor::load()?;
    tracing::info!(floor = %floor.floor_digest().short(), schema = %floor.schema_digest().short(), engine = topak_floor::ENGINE, "floor loaded (pinned)");
    let genesis = genesis(&cfg.rules, &floor)?;
    let params: Params = serde_json::from_str(&std::fs::read_to_string(&cfg.params)?)?;

    // ADR-0044: bundles load only under a signature that verifies under the rules' bundle keys.
    // ADR-0049 §6: and only with a well-formed allowlist. W7 to W9 read two lists the rules issue
    // (ADR-0025 A2, pending). They are read once, here, from the genesis rules: a later issuance
    // that changes them does not re-check a bundle already loaded.
    let issued = topak_bundle::Issued {
        inside_targets: genesis.rules.inside_targets.clone(),
        releasers: genesis.rules.releasers.clone(),
    };
    let local = LocalBundles::load_dir_issued(&cfg.bundles_dir, &genesis.rules.bundle_keys, &issued).await?;
    let revs: Vec<String> = local.revisions().map(|d| d.short().to_string()).collect();
    tracing::info!(?revs, keys = genesis.rules.bundle_keys.len(), sidecar = ?cfg.opa_sidecar, "bundle tier (verified revisions)");
    let sidecar = cfg
        .opa_sidecar
        .as_ref()
        .map(|u| Sidecar::new(u.clone(), Duration::from_millis(cfg.opa_timeout_ms)))
        .transpose()?;
    let bundle = BundleTier::new(sidecar, local);

    let transport = match &cfg.kafka {
        Some(k) => Transport::Kafka(Kafka::connect(k.brokers.clone(), k.replication).await?),
        None => {
            tracing::warn!("no Kafka configured: in-memory transport");
            Transport::Memory(Memory::default())
        }
    };

    let (prop_tx, prop_rx) = mpsc::channel(1024);
    let (in_tx, in_rx) = mpsc::channel(8192);
    let net = net::TcpNet::start(cfg.id, &cfg.peers, in_tx).await?;
    std::fs::create_dir_all(&cfg.data_dir)?;
    let (wal, durable) = wal::Wal::open(&cfg.data_dir.join("wal.jsonl"))?;
    let mut pcfg = topak_paxos::Config::new(cfg.id, cfg.peers.keys().copied().collect());
    pcfg.heartbeat_ms = cfg.heartbeat_ms;
    pcfg.election_timeout_ms = cfg.election_timeout_ms;
    let replica = topak_paxos::Replica::recover(pcfg, durable);

    let mech = Mechanism::new(Parts {
        id: cfg.id,
        params,
        genesis,
        floor,
        bundle: Box::new(bundle),
        transport,
        tools: ToolHost::new(cfg.tools.clone()),
        wasm_tools: if cfg.wasm_tools.is_empty() {
            None
        } else {
            Some(Arc::new(topak_contain::wasmtool::WasmToolHost::new(cfg.wasm_tools.clone())?))
        },
        corpus_dir: cfg.corpus_dir.clone(),
        data_dir: cfg.data_dir.clone(),
        proposals: prop_tx,
        contain: cfg.contain.as_ref().map(|c| c.build(&cfg.data_dir)).transpose()?,
    })?;
    tokio::spawn(driver::Driver { replica, wal: Some(wal), net, mech: mech.clone() }.run(in_rx, prop_rx));
    spawn_sweeper(mech.clone());
    {
        let (m, p) = (mech.clone(), cfg.agent_socket.clone());
        tokio::spawn(async move {
            if let Err(e) = api::serve_agents(&p, m).await {
                tracing::error!(error = %e, "agent socket");
            }
        });
    }
    {
        let (m, p) = (mech.clone(), cfg.operator_socket.clone());
        tokio::spawn(async move {
            if let Err(e) = api::serve_operator(&p, m).await {
                tracing::error!(error = %e, "operator socket");
            }
        });
    }
    Ok(mech)
}

pub fn spawn_sweeper(mech: Arc<Mechanism>) {
    tokio::spawn(async move {
        let mut t = tokio::time::interval(Duration::from_millis(250));
        loop {
            t.tick().await;
            mech.sweep_expired().await;
        }
    });
}
