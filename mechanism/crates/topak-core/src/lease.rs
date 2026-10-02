//! The lease: the composite credential (ADR-0031).

use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

use crate::types::*;

/// `[digest, rung]` — the confinement profile and how belief in it was established (ADR-0031 §3).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Confinement {
    pub digest: Digest,
    /// 0 none declared · 1 asserted by launcher · 2 measured boot · 3 confidential VM + verifier.
    /// Rung semantics are ADR-0034 §2. A rung of 1 or more is granted only on an appraisal
    /// (`confine.rs`, `State::apply_grant`). Fixed across renewal (ADR-0031 A1).
    /// `Contained(p)` is `State::contained`, a lookup over the lease and the issued rules.
    pub rung: u8,
}

pub const MAX_RUNG: u8 = 3;

/// The lease schema of ADR-0031 §1. The field set is closed: a capability that is not one of
/// these fields is not carried by the lease, and adding one is a mechanism release.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Lease {
    pub principal: String,
    pub seat: SeatId,
    pub persona: Digest,
    pub epoch: Epoch,
    /// The Paxos log index at grant (ADR-0031 §2). Also the lease's identity.
    pub fence: LogIndex,
    pub rules_epoch: RulesEpoch,
    pub bundle: Digest,
    pub confinement: Confinement,
    pub alphabet: BTreeSet<ActionKind>,
    /// The round this lease is granted for (ADR-0031 §1, §2). Never reused per seat.
    pub round: Round,
    /// The principal's role in that round. The floor keys on it (ADR-0022 §7).
    pub role: RoundRole,
    /// Expiry as a duration on the local monotonic clock (ADR-0031 §7, ADR-0032).
    pub ttl_ms: u64,
}

impl Lease {
    /// ADR-0031 §4: `new ⊑ self`. A renewal may narrow the alphabet or shorten the TTL. It may
    /// never add authority.
    ///
    /// The confinement rung is fixed across renewal (ADR-0031 A1). Lowering it under a live lease
    /// is a silent downgrade (ADR-0034 §3.4): a renewal whose evidence no longer reaches the rung
    /// is refused, and the lease lapses.
    ///
    /// The bundle is fixed across renewal (ADR-0031 R2): nothing orders two bundles, so a new
    /// bundle reaches a principal only at its next grant. An urgent one ends the round, or fences
    /// the epoch fleet-wide.
    pub fn check_renewal(&self, new: &Lease) -> Result<(), String> {
        let same = |what: &str, ok: bool| if ok { Ok(()) } else { Err(format!("renewal changes {what}")) };
        same("principal", new.principal == self.principal)?;
        same("seat", new.seat == self.seat)?;
        same("persona", new.persona == self.persona)?;
        same("epoch", new.epoch == self.epoch)?;
        same("rulesEpoch", new.rules_epoch == self.rules_epoch)?;
        same("bundle", new.bundle == self.bundle)?;
        same("confinement digest", new.confinement.digest == self.confinement.digest)?;
        // Round and role are fixed for the lease's life: changing either is a grant (§4).
        same("round", new.round == self.round)?;
        same("role", new.role == self.role)?;
        if !new.alphabet.is_subset(&self.alphabet) {
            return Err("renewal widens the alphabet".into());
        }
        // A1: a change either way is refused. Raising adds authority; lowering is a silent
        // downgrade. `Lease_A1.tla` `M_LOWER` is the rule this replaces (`>` only).
        same("confinement rung", new.confinement.rung == self.confinement.rung)?;
        if new.ttl_ms > self.ttl_ms {
            return Err("renewal lengthens the TTL".into());
        }
        Ok(())
    }
}
