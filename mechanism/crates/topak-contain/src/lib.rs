//! The launcher in the node (ADR-0036 §6): launch, appraise, bridge, for one grant.
//!
//! ```text
//!  operator ── launch ──▶ node ──▶ Backend::launch ──▶ guest (one channel: GuestIo)
//!                           │        guest: hello (Persona digest, session key at rung ≥ 2)
//!                           │        node: nonce from the log ──▶ guest: report data
//!                           │        platform: evidence ──▶ Appraiser: statement | Unattestable
//!                           │        Attested ─▶ Grant{appraisal} · Contested ─▶ Contested · else nothing
//!                           └──────▶ bridge: guest ops ⇄ mechanism, under the granted fence
//! ```
//!
//! | Backend          | Rung | What it is                                                      |
//! |------------------|------|-----------------------------------------------------------------|
//! | `ProcessBackend` | 1    | A host process. Confines nothing; its profile says so           |
//! | `DockerBackend`  | 1    | ADR-0036 §4's container, flags from the profile's `launch` part  |
//! | `SimCvmBackend`  | 3    | SIMULATED, feature `sim`: a measured process and a test verifier |
//! | `seams`          | 2, 3 | Firecracker or Kata with a TPM quote; SEV-SNP; TDX. Not built   |
//!
//! And for Run (ADR-0034 A2, pending): `wasmtool`, the tool host's runtime, which hands a Run tool
//! one network capability, its declared target, and nothing else (P4 for Run: channel fidelity).
//!
//! What a replica believes is decided in `topak-core` at apply, not here: this crate produces
//! entries, and the state machine checks them.

pub mod appraise;
pub mod backend;
pub mod bridge;
pub mod docker;
pub mod guest;
pub mod seams;
#[cfg(feature = "sim")]
pub mod sim;
pub mod wasmtool;

use std::future::Future;
use std::pin::Pin;

use serde::{Deserialize, Serialize};
use topak_core::Digest;

pub type BoxFuture<'a, T> = Pin<Box<dyn Future<Output = T> + Send + 'a>>;

/// The simulated platform's report: always compiled, so that evidence a node retains can be read
/// back by a node built without the simulator.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SimReport {
    pub measurement: String,
    pub report_data: Digest,
    pub tcb: u64,
    pub platform: String,
}

/// Whether this build carries the simulator. A node built without it refuses a `sim` config.
pub const SIM_BUILT: bool = cfg!(feature = "sim");
