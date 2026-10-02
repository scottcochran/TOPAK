//! The bridge (ADR-0036 §2.4): every `AgentOp` the guest writes goes to the mechanism under the
//! lease the guest was granted, and every response goes back. At rung 1 the bridge is the
//! session: no other process holds anything that names the lease. At rungs 2 and 3 the guest's
//! own signature does, and the bridge only carries it.

use std::sync::Arc;

use tokio::sync::{mpsc, oneshot};
use topak_core::confine::SessionProof;
use topak_core::{Epoch, LogIndex};
use topak_mcp::proto::{AgentOp, AgentResponse};

use crate::BoxFuture;
use crate::guest::{GuestEvidence, GuestIo, GuestMsg, HostMsg};

/// Where the bridge sends what the guest asks: the mechanism, bound to a lease by fence.
pub trait ActSink: Send + Sync {
    fn act_bound<'a>(
        &'a self,
        fence: LogIndex,
        op: AgentOp,
        proof: Option<SessionProof>,
    ) -> BoxFuture<'a, AgentResponse>;
}

/// What the launcher tells a running bridge.
pub enum Ctl {
    /// Re-attest at renewal: the guest's evidence for this nonce comes back on `reply`.
    Attest {
        nonce: topak_core::Digest,
        reply: oneshot::Sender<GuestEvidence>,
    },
    /// The lease moved to a new fence (renewal).
    Granted {
        fence: LogIndex,
        epoch: Epoch,
    },
    Shutdown,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum BridgeEnd {
    /// The guest closed its channel: the round ends (ADR-0036 §2.4).
    GuestClosed,
    /// The launcher ended it: the lease ended, or the guest is being destroyed.
    Shutdown,
    ProtocolError(String),
}

pub async fn bridge(
    mut io: GuestIo,
    mut fence: LogIndex,
    sink: Arc<dyn ActSink>,
    mut ctl: mpsc::Receiver<Ctl>,
) -> BridgeEnd {
    let mut pending: Option<oneshot::Sender<GuestEvidence>> = None;
    loop {
        tokio::select! {
            msg = io.recv() => match msg {
                Ok(None) => return BridgeEnd::GuestClosed,
                Err(e) => return BridgeEnd::ProtocolError(e),
                Ok(Some(GuestMsg::Op { op, proof })) => {
                    let response = sink.act_bound(fence, op, proof).await;
                    if io.send(&HostMsg::Response { response }).await.is_err() {
                        return BridgeEnd::GuestClosed;
                    }
                }
                Ok(Some(GuestMsg::Evidence(ev))) => match pending.take() {
                    Some(tx) => { let _ = tx.send(ev); }
                    None => return BridgeEnd::ProtocolError("evidence nobody asked for".into()),
                },
                Ok(Some(GuestMsg::Hello(_))) => return BridgeEnd::ProtocolError("a second identity line".into()),
            },
            c = ctl.recv() => match c {
                Some(Ctl::Attest { nonce, reply }) => {
                    pending = Some(reply);
                    if io.send(&HostMsg::Attest { nonce }).await.is_err() {
                        return BridgeEnd::GuestClosed;
                    }
                }
                Some(Ctl::Granted { fence: f, epoch }) => {
                    fence = f;
                    if io.send(&HostMsg::Granted { fence: f, epoch }).await.is_err() {
                        return BridgeEnd::GuestClosed;
                    }
                }
                Some(Ctl::Shutdown) | None => {
                    let _ = io.send(&HostMsg::Shutdown).await;
                    return BridgeEnd::Shutdown;
                }
            },
        }
    }
}
