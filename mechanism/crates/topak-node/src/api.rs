//! The two Unix sockets: agent (actions only) and operator (environment steps).
//! One JSON line in, one JSON line out, per connection.

use std::os::unix::fs::PermissionsExt;
use std::path::Path;
use std::sync::Arc;

use serde_json::json;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::UnixListener;
use topak_mcp::proto::{AgentRequest, AgentResponse};

use crate::mechanism::Mechanism;
use crate::ops::OperatorOp;

fn bind(path: &Path, mode: u32) -> anyhow::Result<UnixListener> {
    let _ = std::fs::remove_file(path);
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let l = UnixListener::bind(path)?;
    std::fs::set_permissions(path, std::fs::Permissions::from_mode(mode))?;
    Ok(l)
}

pub async fn serve_agents(path: &Path, mech: Arc<Mechanism>) -> anyhow::Result<()> {
    let l = bind(path, 0o660)?;
    loop {
        let (s, _) = l.accept().await?;
        let mech = mech.clone();
        tokio::spawn(async move {
            let (r, mut w) = s.into_split();
            let mut line = String::new();
            if BufReader::new(r).read_line(&mut line).await.is_err() {
                return;
            }
            let resp = match serde_json::from_str::<AgentRequest>(&line) {
                Ok(req) => mech.act(req).await,
                Err(e) => AgentResponse { admitted: false, detail: json!({ "error": e.to_string() }) },
            };
            let mut out = serde_json::to_vec(&resp).unwrap_or_default();
            out.push(b'\n');
            let _ = w.write_all(&out).await;
        });
    }
}

pub async fn serve_operator(path: &Path, mech: Arc<Mechanism>) -> anyhow::Result<()> {
    let l = bind(path, 0o600)?;
    loop {
        let (s, _) = l.accept().await?;
        let mech = mech.clone();
        tokio::spawn(async move {
            let (r, mut w) = s.into_split();
            let mut line = String::new();
            if BufReader::new(r).read_line(&mut line).await.is_err() {
                return;
            }
            let resp = match serde_json::from_str::<OperatorOp>(&line) {
                Ok(op) => mech.operate(op).await,
                Err(e) => json!({ "ok": false, "error": e.to_string() }),
            };
            let mut out = serde_json::to_vec(&resp).unwrap_or_default();
            out.push(b'\n');
            let _ = w.write_all(&out).await;
        });
    }
}
