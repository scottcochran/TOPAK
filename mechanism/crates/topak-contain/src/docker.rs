//! Rung 1 in a container (ADR-0036 §4): `slm/serve/run.sh`'s flags, read from the profile's
//! `launch` part, so the launcher applies the constraints the profile declares and nothing else.
//!
//! On Docker Desktop the boundary is the platform's Linux VM; on a Linux host the container shares
//! the kernel and the profile should name `runsc` (ADR-0036, Consequences). Either way it is the
//! container runtime the rung-1 trusted base names (ADR-0045 T-0045-19).

use std::collections::BTreeMap;
use std::path::PathBuf;
use std::sync::Arc;

use anyhow::{Context as _, bail};
use serde::Deserialize;
use tokio::process::Command;
use topak_core::Digest;

use crate::BoxFuture;
use crate::backend::*;
use crate::guest::{GuestEvidence, GuestHello};

/// The profile's `launch` part for a container. Every field is applied; none is defaulted to
/// something looser than the profile says.
#[derive(Clone, Debug, Deserialize)]
pub struct DockerLaunch {
    pub kind: String,
    /// P1: `none`, and nothing else is accepted.
    pub network: String,
    /// P2: a read-only root.
    pub read_only: bool,
    #[serde(default)]
    pub cap_drop: Vec<String>,
    #[serde(default)]
    pub security_opt: Vec<String>,
    #[serde(default)]
    pub ipc: Option<String>,
    #[serde(default)]
    pub pids_limit: Option<u32>,
    #[serde(default)]
    pub user: Option<String>,
    #[serde(default)]
    pub tmpfs: Vec<String>,
    #[serde(default)]
    pub runtime: Option<String>,
    /// P2: what is mounted, read-only. Sources are the node's, by destination.
    #[serde(default)]
    pub mounts: Vec<MountDecl>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct MountDecl {
    pub dst: String,
    pub mode: String,
}

pub struct DockerBackend {
    pub docker: PathBuf,
    /// The image reference to run. Its content digest must be the profile's `image`.
    pub image_ref: String,
    pub args: Vec<String>,
    /// Where each declared mount comes from on this host.
    pub mount_sources: BTreeMap<String, PathBuf>,
}

impl DockerBackend {
    /// The `docker run` arguments for a profile. Refuses a profile whose `launch` part would open
    /// a network or mount anything writable: those are not this launcher's to apply.
    pub fn run_args(&self, launch: &DockerLaunch, name: &str) -> anyhow::Result<Vec<String>> {
        if launch.kind != "docker" {
            bail!("the profile's launch part is {}, not docker", launch.kind);
        }
        if launch.network != "none" {
            bail!("P1: a profile with a network device is not launched here");
        }
        let mut a: Vec<String> = ["run", "--rm", "-i", "--network", "none", "--log-driver", "none", "--name", name]
            .into_iter()
            .map(String::from)
            .collect();
        if launch.read_only {
            a.push("--read-only".into());
        }
        for c in &launch.cap_drop {
            a.extend(["--cap-drop".into(), c.clone()]);
        }
        for s in &launch.security_opt {
            a.extend(["--security-opt".into(), s.clone()]);
        }
        if let Some(i) = &launch.ipc {
            a.extend(["--ipc".into(), i.clone()]);
        }
        if let Some(n) = launch.pids_limit {
            a.extend(["--pids-limit".into(), n.to_string()]);
        }
        if let Some(u) = &launch.user {
            a.extend(["--user".into(), u.clone()]);
        }
        for t in &launch.tmpfs {
            a.extend(["--tmpfs".into(), t.clone()]);
        }
        if let Some(r) = &launch.runtime {
            a.extend(["--runtime".into(), r.clone()]);
        }
        for m in &launch.mounts {
            if m.mode != "ro" {
                bail!("P2: mount {} is {}; only read-only mounts are launched", m.dst, m.mode);
            }
            let src = self.mount_sources.get(&m.dst).with_context(|| format!("no source for mount {}", m.dst))?;
            a.extend(["--mount".into(), format!("type=bind,src={},dst={},readonly", src.display(), m.dst)]);
        }
        a.push(self.image_ref.clone());
        a.extend(self.args.iter().cloned());
        Ok(a)
    }

    /// The image's content digest, as the runtime reports it, without the `sha256:` prefix.
    pub async fn image_digest(&self) -> anyhow::Result<Digest> {
        let out = Command::new(&self.docker)
            .args(["image", "inspect", "--format", "{{.Id}}", &self.image_ref])
            .output()
            .await?;
        anyhow::ensure!(
            out.status.success(),
            "docker image inspect {}: {}",
            self.image_ref,
            String::from_utf8_lossy(&out.stderr)
        );
        let id = String::from_utf8_lossy(&out.stdout).trim().to_string();
        Ok(Digest(id.strip_prefix("sha256:").unwrap_or(&id).to_string()))
    }
}

pub struct DockerGuest {
    instance: Digest,
    image: Digest,
    name: String,
    docker: PathBuf,
    child: Arc<ChildSlot>,
}

impl Backend for DockerBackend {
    fn rung(&self) -> u8 {
        1
    }

    fn kind(&self) -> &'static str {
        "docker"
    }

    fn launch<'a>(&'a self, req: LaunchRequest<'a>) -> BoxFuture<'a, anyhow::Result<LaunchedGuest>> {
        Box::pin(async move {
            let launch: DockerLaunch =
                serde_json::from_value(req.profile.launch.clone()).context("the profile's launch part")?;
            let image = self.image_digest().await?;
            let instance = new_instance();
            let name = format!("topak-{}", instance.short());
            let args = self.run_args(&launch, &name)?;
            let (child, io) = spawn(&self.docker, &args, &instance, false)?;
            let handle = Arc::new(DockerGuest {
                instance,
                image,
                name,
                docker: self.docker.clone(),
                child: ChildSlot::new(child),
            });
            Ok(LaunchedGuest { handle, io })
        })
    }
}

impl GuestHandle for DockerGuest {
    fn instance(&self) -> &Digest {
        &self.instance
    }

    fn evidence(&self, _from_guest: &GuestEvidence, hello: &GuestHello) -> anyhow::Result<Evidence> {
        Ok(Evidence::LauncherAssertion { image: Some(self.image.clone()), persona: hello.persona.clone() })
    }

    fn destroy(&self) -> BoxFuture<'_, ()> {
        Box::pin(async move {
            let _ = Command::new(&self.docker).args(["kill", &self.name]).output().await;
            self.child.kill();
        })
    }
}
