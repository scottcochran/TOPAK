//! The lease: the composite credential (ADR-0031).

use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

use crate::types::*;

/// `[digest, rung]` — the confinement profile and how belief in it was established (ADR-0031 §3).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Confinement {
    pub digest: Digest,
    /// 0 none declared · 1 asserted by launcher · 2 measured boot · 3 confidential VM + verifier.
    /// Rungs 1–3 have no semantics yet (the attestation-rung record is unwritten).
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

/// PROVISIONAL (provenance criterion): ADR-0031 §3 makes confinement necessary but not
/// sufficient for `Contained`; the provenance independence criterion is unwritten. Until it
/// exists nothing is `Contained`, whatever the rung.
pub const PROVENANCE_CRITERION_DEFINED: bool = false;

impl Lease {
    /// `Contained(p)` as far as the lease can say. Rung 0 is `Mediated`, always (§3).
    pub fn is_contained(&self) -> bool {
        self.confinement.rung >= 1 && PROVENANCE_CRITERION_DEFINED
    }

    /// ADR-0031 §4: `new ⊑ self`. A renewal may narrow the alphabet, lower the rung or shorten
    /// the TTL. It may never add authority.
    ///
    /// PROVISIONAL (bundle order): §4 also allows "narrow the bundle", but whether one Rego
    /// bundle is narrower than another is undecidable here (ADR-0030 §1 is why no check is
    /// needed between tiers, and nothing orders bundles among themselves). Fail-closed: renewal
    /// keeps the bundle identical; a bundle change takes effect at the next grant, and an urgent
    /// one fences the epoch.
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
        if new.confinement.rung > self.confinement.rung {
            return Err("renewal raises the confinement rung".into());
        }
        if new.ttl_ms > self.ttl_ms {
            return Err("renewal lengthens the TTL".into());
        }
        Ok(())
    }
}
