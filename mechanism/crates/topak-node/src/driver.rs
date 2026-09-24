//! Drives the sans-IO replica: feeds it inputs, and carries out its outputs in the order the
//! contract requires — persists fsynced before any send leaves, then sends, then deliveries.

use std::sync::Arc;
use std::sync::atomic::Ordering;
use std::time::Duration;

use tokio::sync::mpsc;
use topak_core::clock::MonotonicClock;
use topak_core::state::Entry;
use topak_paxos::{Input, Output, Replica};

use crate::mechanism::Mechanism;
use crate::net::{PeerSend, Wire};
use crate::wal::Wal;

pub struct Driver {
    pub replica: Replica<Entry>,
    pub wal: Option<Wal>,
    pub net: Arc<dyn PeerSend>,
    pub mech: Arc<Mechanism>,
}

impl Driver {
    pub async fn run(mut self, mut inbound: mpsc::Receiver<Wire>, mut proposals: mpsc::Receiver<Entry>) {
        let mut tick = tokio::time::interval(Duration::from_millis(10));
        tick.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);
        loop {
            let input = tokio::select! {
                Some(e) = proposals.recv() => Input::Propose(e),
                Some((from, msg)) = inbound.recv() => Input::Receive { from, msg },
                _ = tick.tick() => Input::Tick { now_ms: self.mech.clock.now_ms() },
            };
            let outs = self.replica.handle(input);
            self.mech.leader.store(self.replica.is_leader(), Ordering::Relaxed);
            self.process(outs).await;
        }
    }

    async fn process(&mut self, outs: Vec<Output<Entry>>) {
        let persists: Vec<&Output<Entry>> =
            outs.iter().filter(|o| matches!(o, Output::PersistPromise { .. } | Output::PersistAccept { .. })).collect();
        if let Some(wal) = &mut self.wal
            && let Err(e) = wal.append(&persists)
        {
            // Without durability this replica must not speak: drop the batch's sends.
            tracing::error!(error = %e, "WAL append failed; withholding sends");
            return;
        }
        for o in outs {
            match o {
                Output::Send { to, msg } => self.net.send(to, msg),
                Output::Deliver { slot, value } => self.mech.apply_committed(slot, value).await,
                _ => {}
            }
        }
    }
}
