//! Replica-to-replica transport for Paxos messages.
//!
//! Best-effort by design: Paxos tolerates loss, duplication and reordering, so a send that
//! cannot be made promptly is dropped rather than queued without bound.
//!
//! PROVISIONAL (replica authentication): frames are unauthenticated JSON over plain TCP. Under
//! the crash-fault model the replicas are trusted; anything else on the network is not, and
//! mutual TLS between replicas is required before this leaves a lab.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::mpsc;
use topak_core::state::Entry;
use topak_paxos::{Msg, NodeId};

pub type Wire = (NodeId, Msg<Entry>);

pub trait PeerSend: Send + Sync {
    fn send(&self, to: NodeId, msg: Msg<Entry>);
}

// ---- TCP -------------------------------------------------------------------------------------

pub struct TcpNet {
    id: NodeId,
    outbound: HashMap<NodeId, mpsc::Sender<Msg<Entry>>>,
}

const MAX_FRAME: usize = 64 << 20;

impl TcpNet {
    pub async fn start(
        id: NodeId,
        peers: &BTreeMap<NodeId, String>,
        inbound: mpsc::Sender<Wire>,
    ) -> anyhow::Result<Arc<Self>> {
        let listener = TcpListener::bind(&peers[&id]).await?;
        tokio::spawn(async move {
            loop {
                let Ok((mut s, _)) = listener.accept().await else { continue };
                let inbound = inbound.clone();
                tokio::spawn(async move {
                    loop {
                        let Ok(n) = s.read_u32().await else { return };
                        if n as usize > MAX_FRAME {
                            return;
                        }
                        let mut buf = vec![0u8; n as usize];
                        if s.read_exact(&mut buf).await.is_err() {
                            return;
                        }
                        match serde_json::from_slice::<Wire>(&buf) {
                            Ok(w) => {
                                let _ = inbound.send(w).await;
                            }
                            Err(e) => tracing::warn!(error = %e, "bad replica frame"),
                        }
                    }
                });
            }
        });
        let mut outbound = HashMap::new();
        for (peer, addr) in peers {
            if *peer == id {
                continue;
            }
            let (tx, mut rx) = mpsc::channel::<Msg<Entry>>(4096);
            let addr = addr.clone();
            tokio::spawn(async move {
                let mut conn: Option<TcpStream> = None;
                while let Some(msg) = rx.recv().await {
                    if conn.is_none() {
                        conn = tokio::time::timeout(Duration::from_millis(200), TcpStream::connect(&addr))
                            .await
                            .ok()
                            .and_then(Result::ok);
                        if let Some(c) = &conn {
                            let _ = c.set_nodelay(true);
                        }
                    }
                    let Some(c) = conn.as_mut() else { continue };
                    let body = serde_json::to_vec(&(id, msg)).expect("serializable");
                    let ok = c.write_u32(body.len() as u32).await.is_ok() && c.write_all(&body).await.is_ok();
                    if !ok {
                        conn = None;
                    }
                }
            });
            outbound.insert(*peer, tx);
        }
        Ok(Arc::new(Self { id, outbound }))
    }
}

impl PeerSend for TcpNet {
    fn send(&self, to: NodeId, msg: Msg<Entry>) {
        if to == self.id {
            return;
        }
        if let Some(tx) = self.outbound.get(&to) {
            let _ = tx.try_send(msg);
        }
    }
}

// ---- in-process hub, for tests ---------------------------------------------------------------

#[derive(Default)]
pub struct Hub {
    routes: Mutex<HashMap<NodeId, mpsc::Sender<Wire>>>,
    /// Replicas cut off from everyone (partition testing).
    pub isolated: Mutex<BTreeSet<NodeId>>,
}

impl Hub {
    pub fn register(&self, id: NodeId, inbound: mpsc::Sender<Wire>) {
        self.routes.lock().unwrap().insert(id, inbound);
    }
}

pub struct ChannelNet {
    pub id: NodeId,
    pub hub: Arc<Hub>,
}

impl PeerSend for ChannelNet {
    fn send(&self, to: NodeId, msg: Msg<Entry>) {
        {
            let iso = self.hub.isolated.lock().unwrap();
            if iso.contains(&self.id) || iso.contains(&to) {
                return;
            }
        }
        if let Some(tx) = self.hub.routes.lock().unwrap().get(&to) {
            let _ = tx.try_send((self.id, msg));
        }
    }
}
