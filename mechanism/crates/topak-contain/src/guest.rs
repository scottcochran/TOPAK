//! The one channel between the launcher and a guest (ADR-0034 P1, ADR-0036 §2): line-delimited
//! JSON over a byte stream. At rung 1 the stream is the guest's stdio; vsock is a backend swap.
//!
//! The guest speaks first, once, with its identity. After that the guest asks and the host
//! answers, except for three things only the host starts: an attestation request, the lease the
//! guest is acting under, and shutdown. No token ever crosses this channel.

use std::time::Duration;

use serde::{Deserialize, Serialize};
use tokio::io::{AsyncBufReadExt, AsyncRead, AsyncWrite, AsyncWriteExt, BufReader};
use tokio::sync::mpsc;
use topak_core::authentic::KeyHex;
use topak_core::confine::SessionProof;
use topak_core::{Digest, Epoch, LogIndex};
use topak_mcp::proto::{AgentOp, AgentResponse};

/// The guest's first line (ADR-0036 §2.1). A guest that cannot verify its bundle exits without
/// writing it. `session_key` is the public half of the key pair the guest made at start, at
/// rungs 2 and 3 (ADR-0034 §3.1).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct GuestHello {
    /// The digest of the Persona bundle's `model.json`.
    pub persona: Digest,
    pub family: String,
    pub params: u64,
    pub root: String,
    #[serde(default)]
    pub session_key: Option<KeyHex>,
}

/// The guest's half of the evidence: what it asks its platform to bind into the report. The
/// platform's half, the measurement and its signature, is never the guest's to supply.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct GuestEvidence {
    pub report_data: Digest,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "msg", rename_all = "snake_case")]
pub enum GuestMsg {
    Hello(GuestHello),
    Evidence(GuestEvidence),
    /// One `AgentOp`, token-less. At rungs 2 and 3 it carries the guest's session proof.
    Op {
        op: AgentOp,
        #[serde(default)]
        proof: Option<SessionProof>,
    },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "msg", rename_all = "snake_case")]
pub enum HostMsg {
    /// Re-attest: bind this nonce (ADR-0034 §3.1, §3.6).
    Attest {
        nonce: Digest,
    },
    /// The lease the guest acts under, at grant and after every renewal. A guest at rung 2 or 3
    /// signs over it.
    Granted {
        fence: LogIndex,
        epoch: Epoch,
    },
    Response {
        response: AgentResponse,
    },
    Shutdown,
}

/// Both directions of the channel. Lines are read by a task of their own, so `recv` can be raced
/// against other work without losing a partial line.
pub struct GuestIo {
    lines: mpsc::Receiver<String>,
    w: Box<dyn AsyncWrite + Unpin + Send>,
}

impl GuestIo {
    pub fn new(r: impl AsyncRead + Unpin + Send + 'static, w: impl AsyncWrite + Unpin + Send + 'static) -> Self {
        let (tx, lines) = mpsc::channel(64);
        tokio::spawn(async move {
            let mut r = BufReader::new(r).lines();
            while let Ok(Some(line)) = r.next_line().await {
                if tx.send(line).await.is_err() {
                    break;
                }
            }
        });
        GuestIo { lines, w: Box::new(w) }
    }

    pub async fn send(&mut self, m: &HostMsg) -> std::io::Result<()> {
        let mut line = serde_json::to_vec(m).expect("serializable");
        line.push(b'\n');
        self.w.write_all(&line).await?;
        self.w.flush().await
    }

    /// The next message. `Ok(None)`: the guest closed its side. `Err`: a line that is not one.
    pub async fn recv(&mut self) -> Result<Option<GuestMsg>, String> {
        match self.lines.recv().await {
            None => Ok(None),
            Some(l) => serde_json::from_str(&l).map(Some).map_err(|e| format!("not a guest message: {e}")),
        }
    }

    async fn recv_within(&mut self, t: Duration, what: &str) -> Result<GuestMsg, String> {
        match tokio::time::timeout(t, self.recv()).await {
            Err(_) => Err(format!("no {what} within {} ms", t.as_millis())),
            Ok(Ok(None)) => Err(format!("the guest closed its channel before its {what}")),
            Ok(Ok(Some(m))) => Ok(m),
            Ok(Err(e)) => Err(e),
        }
    }

    pub async fn read_hello(&mut self, t: Duration) -> Result<GuestHello, String> {
        match self.recv_within(t, "identity line").await? {
            GuestMsg::Hello(h) => Ok(h),
            other => Err(format!("the first line is not the guest's identity: {other:?}")),
        }
    }

    /// Ask for evidence before the bridge runs: at launch, nothing else is in flight.
    pub async fn attest(&mut self, nonce: &Digest, t: Duration) -> Result<GuestEvidence, String> {
        self.send(&HostMsg::Attest { nonce: nonce.clone() }).await.map_err(|e| e.to_string())?;
        match self.recv_within(t, "evidence").await? {
            GuestMsg::Evidence(e) => Ok(e),
            other => Err(format!("expected evidence, got {other:?}")),
        }
    }
}
