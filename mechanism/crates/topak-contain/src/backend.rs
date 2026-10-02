//! Backends: what starts a guest, and what the platform says about it.
//!
//! The pipeline is the same at every rung (ADR-0036 §2): launch, appraise, grant, bridge. A
//! backend owns the first step and the platform's half of the evidence. What the evidence is
//! worth is the appraiser's (`appraise.rs`) and, at apply, the mechanism's (`topak-core`).

use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::sync::{Arc, Mutex};

use serde::{Deserialize, Serialize};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::{Child, Command};
use topak_core::Digest;
use topak_core::authentic::Signed;
use topak_core::confine::Profile;

use crate::BoxFuture;
use crate::guest::{GuestEvidence, GuestHello, GuestIo};

pub struct LaunchRequest<'a> {
    pub profile: &'a Profile,
    pub profile_digest: &'a Digest,
    pub seat: &'a str,
}

pub struct LaunchedGuest {
    pub handle: Arc<dyn GuestHandle>,
    pub io: GuestIo,
}

/// What a platform reports. The digest of this value is the statement's `evidence`, and the value
/// is what the launching node retains (F18).
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Evidence {
    /// Rung 1 (ADR-0036 §2.2): the launcher says what it launched. Nobody else checks.
    LauncherAssertion {
        image: Option<Digest>,
        persona: Digest,
    },
    /// The simulator's confidential-VM report (`sim.rs`). Shape of rung 3, substance of a test.
    SimSnp {
        report: crate::SimReport,
        signature: Signed,
    },
    /// Seams. Real SEV-SNP and TDX reports (T-0045-16), and rung 2's TPM quote. None is appraised.
    Snp {
        report: String,
    },
    Tdx {
        quote: String,
    },
    TpmQuote {
        quote: String,
    },
}

impl Evidence {
    pub fn digest(&self) -> Digest {
        Digest::of_json(self)
    }
}

pub trait Backend: Send + Sync {
    /// The rung this backend's evidence can reach.
    fn rung(&self) -> u8;
    fn kind(&self) -> &'static str;
    fn launch<'a>(&'a self, req: LaunchRequest<'a>) -> BoxFuture<'a, anyhow::Result<LaunchedGuest>>;
}

pub trait GuestHandle: Send + Sync {
    /// The launched instance: `gen` of `Confinement.tla`. Never reused.
    fn instance(&self) -> &Digest;
    /// The platform's half of the evidence for this guest, binding what the guest supplied.
    fn evidence(&self, from_guest: &GuestEvidence, hello: &GuestHello) -> anyhow::Result<Evidence>;
    /// P6: the guest is destroyed. Idempotent.
    fn destroy(&self) -> BoxFuture<'_, ()>;
}

/// A fresh instance identity.
pub fn new_instance() -> Digest {
    Digest::of(&rand::random::<[u8; 16]>())
}

pub fn file_digest(path: &Path) -> anyhow::Result<Digest> {
    Ok(Digest::of(&std::fs::read(path)?))
}

/// Start `command` with stdin and stdout held by the launcher and stderr to its log, outward
/// only (ADR-0036 §2, finding 3). The child dies with its handle. `clear_env`: a process guest
/// starts with an empty environment; a runtime's CLI keeps the launcher's, and the runtime sets
/// the guest's.
pub(crate) fn spawn(
    command: &Path,
    args: &[String],
    instance: &Digest,
    clear_env: bool,
) -> anyhow::Result<(Child, GuestIo)> {
    let mut cmd = Command::new(command);
    cmd.args(args).stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped()).kill_on_drop(true);
    if clear_env {
        cmd.env_clear();
    }
    let mut child = cmd.spawn()?;
    let stdin = child.stdin.take().expect("piped");
    let stdout = child.stdout.take().expect("piped");
    let stderr = child.stderr.take().expect("piped");
    let short = instance.short().to_string();
    tokio::spawn(async move {
        let mut lines = BufReader::new(stderr).lines();
        while let Ok(Some(l)) = lines.next_line().await {
            tracing::info!(target: "guest", instance = %short, "{l}");
        }
    });
    Ok((child, GuestIo::new(stdout, stdin)))
}

/// A child process the handle owns and can kill.
pub(crate) struct ChildSlot(Mutex<Option<Child>>);

impl ChildSlot {
    pub(crate) fn new(c: Child) -> Arc<Self> {
        Arc::new(ChildSlot(Mutex::new(Some(c))))
    }

    pub(crate) fn kill(&self) {
        if let Some(mut c) = self.0.lock().unwrap().take() {
            let _ = c.start_kill();
        }
    }
}

/// Rung 1 on a host process: the guest is a process the launcher started, with its stdio as the
/// one channel. It confines nothing: its profile declares P1 and P2 `fail` (ADR-0036 R1), and the
/// rung says only that the launcher asserts what it launched.
pub struct ProcessBackend {
    pub command: PathBuf,
    pub args: Vec<String>,
}

pub struct ProcessGuest {
    instance: Digest,
    image: Digest,
    child: Arc<ChildSlot>,
}

impl Backend for ProcessBackend {
    fn rung(&self) -> u8 {
        1
    }

    fn kind(&self) -> &'static str {
        "process"
    }

    fn launch<'a>(&'a self, _req: LaunchRequest<'a>) -> BoxFuture<'a, anyhow::Result<LaunchedGuest>> {
        Box::pin(async move {
            // The image is what runs: the binary's bytes at launch.
            let image = file_digest(&self.command)?;
            let instance = new_instance();
            let (child, io) = spawn(&self.command, &self.args, &instance, true)?;
            let handle = Arc::new(ProcessGuest { instance, image, child: ChildSlot::new(child) });
            Ok(LaunchedGuest { handle, io })
        })
    }
}

impl GuestHandle for ProcessGuest {
    fn instance(&self) -> &Digest {
        &self.instance
    }

    fn evidence(&self, _from_guest: &GuestEvidence, hello: &GuestHello) -> anyhow::Result<Evidence> {
        Ok(Evidence::LauncherAssertion { image: Some(self.image.clone()), persona: hello.persona.clone() })
    }

    fn destroy(&self) -> BoxFuture<'_, ()> {
        self.child.kill();
        Box::pin(async {})
    }
}
