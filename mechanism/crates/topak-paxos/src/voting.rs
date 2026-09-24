//! The `Voting` abstraction: acceptors, ballots, quorums, no messages.
//!
//! Used as a refinement ghost. Every durable acceptor vote the message-level protocol makes is
//! recorded here, and the two invariants the real argument rests on are checked on each one.

use std::collections::{BTreeMap, BTreeSet};

use crate::{Ballot, Cmd, NodeId, Slot};

pub struct Voting<V> {
    members: usize,
    /// (slot, ballot) → the one value voted for at that ballot.
    value_at: BTreeMap<(Slot, Ballot), Cmd<V>>,
    /// (slot, ballot) → acceptors that voted.
    voters: BTreeMap<(Slot, Ballot), BTreeSet<NodeId>>,
    /// slot → the value chosen there, once any ballot reaches a majority.
    chosen: BTreeMap<Slot, Cmd<V>>,
}

impl<V: Clone + PartialEq + std::fmt::Debug> Voting<V> {
    pub fn new(members: usize) -> Self {
        Self { members, value_at: BTreeMap::new(), voters: BTreeMap::new(), chosen: BTreeMap::new() }
    }

    fn majority(&self) -> usize {
        self.members / 2 + 1
    }

    /// Record `acc` voting for `cmd` in `slot` at `ballot`. Errors name the violated invariant.
    pub fn vote(&mut self, acc: NodeId, slot: Slot, ballot: Ballot, cmd: &Cmd<V>) -> Result<(), String> {
        match self.value_at.get(&(slot, ballot)) {
            Some(v) if v != cmd => {
                return Err(format!("OneValuePerBallot: slot {slot} ballot {ballot:?} has {v:?} and {cmd:?}"));
            }
            Some(_) => {}
            None => {
                self.value_at.insert((slot, ballot), cmd.clone());
            }
        }
        let n = {
            let s = self.voters.entry((slot, ballot)).or_default();
            s.insert(acc);
            s.len()
        };
        if n >= self.majority() {
            match self.chosen.get(&slot) {
                Some(c) if c != cmd => {
                    return Err(format!("ChosenUnique: slot {slot} chose {c:?} and then {cmd:?}"));
                }
                Some(_) => {}
                None => {
                    self.chosen.insert(slot, cmd.clone());
                }
            }
        }
        Ok(())
    }

    pub fn chosen(&self, slot: Slot) -> Option<&Cmd<V>> {
        self.chosen.get(&slot)
    }
}
