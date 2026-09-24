//! Sans-IO Multi-Paxos for the TOPAK control plane.
//!
//! Layered as the corpus's TLA+ practice prescribes (`derived/tlaplus-paxos-cheat-sheet`):
//!
//! - [`voting`] — acceptors, ballots and quorums with **no messages**. Here it is a ghost: the
//!   simulation feeds it every durable vote and checks the `Voting` invariants
//!   (`OneValuePerBallot`, at most one value chosen per slot) against the real replicas.
//! - [`replica`] — message-level Multi-Paxos. A replica is a pure state machine:
//!   `handle(Input) -> Vec<Output>`. Time arrives as an input; sockets and disks are the host's.
//!
//! **Fault model: crash-recovery, not Byzantine.** The replicas are the mechanism, inside the
//! trusted base; the Byzantine premise of ADR-0007 is about agents, which never speak Paxos.
//! Recovery is safe only if the host makes every `Persist*` output durable before it transmits
//! any `Send` that follows it in the same batch.

pub mod replica;
pub mod voting;

pub use replica::*;

use serde::{Deserialize, Serialize};

pub type NodeId = u32;
/// Log positions start at 1, so a fence of 0 can mean "none".
pub type Slot = u64;

/// Ballots are totally ordered by (round, node). `Ballot::default()` is below every real ballot.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct Ballot {
    pub round: u64,
    pub node: NodeId,
}

/// A slot's command. A new leader fills gaps it cannot recover with `Noop`.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Cmd<V> {
    Noop,
    Value(V),
}
