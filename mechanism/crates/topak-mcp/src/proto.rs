//! The line-delimited JSON protocol between the MCP front door and the node's agent socket.

use serde::{Deserialize, Serialize, de::DeserializeOwned};
use serde_json::Value;
use std::path::PathBuf;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::net::UnixStream;
use topak_core::action::Action;

/// The session credential is a bearer token the node minted at grant and handed to whoever
/// launched this session. PROVISIONAL (session binding): the token is local to the granting
/// replica and is not replicated; a restart invalidates it.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentRequest {
    pub token: String,
    #[serde(flatten)]
    pub op: AgentOp,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case")]
pub enum AgentOp {
    /// One action from the alphabet.
    Act { action: Action },
    /// `Submit` of the current workspace: the mechanism computes the digest (a syntactic fact).
    SubmitWorkspace,
    /// `Submit(⊥)`: end the authoring round without offering anything. A subtraction.
    Abstain,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AgentResponse {
    pub admitted: bool,
    pub detail: Value,
}

/// A client for a node's Unix socket: one JSON line out, one JSON line back.
#[derive(Clone, Debug)]
pub struct SocketClient {
    pub path: PathBuf,
}

impl SocketClient {
    pub fn new(path: impl Into<PathBuf>) -> Self {
        Self { path: path.into() }
    }

    pub async fn request<Q: Serialize, R: DeserializeOwned>(&self, q: &Q) -> anyhow::Result<R> {
        let stream = UnixStream::connect(&self.path).await?;
        let (r, mut w) = stream.into_split();
        let mut line = serde_json::to_vec(q)?;
        line.push(b'\n');
        w.write_all(&line).await?;
        w.shutdown().await?;
        let mut reader = BufReader::new(r);
        let mut buf = String::new();
        reader.read_line(&mut buf).await?;
        Ok(serde_json::from_str(&buf)?)
    }
}
