//! Promotion is a quorum grant (ADR-0024). The tally follows the `PromotionEnabled` snippet in
//! ADR-0024 line for line.

use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

use crate::rules::{Quorum, Rules};
use crate::types::*;

/// A recorded vote. Only recorded votes count; a timeout is never a grant (mechanism constant,
/// formerly R4), so there is no timeout path into this structure at all.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct VoteRecord {
    pub verdict: Verdict,
    pub evidence: Digest,
    pub rules_epoch: RulesEpoch,
}

/// A submitted artifact and the votes cast on it. A promotion is a round keyed by artifact
/// digest (ADR-0024 §7).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Candidate {
    pub artifact: Digest,
    pub author: SeatId,
    pub votes: BTreeMap<SeatId, VoteRecord>,
    pub promoted_at: Option<LogIndex>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Tally {
    Promoted,
    Pending {
        granted: usize,
        counted: usize,
    },
    /// Every counted grant seat granted, but the author's round is not covered by a cell
    /// Observer (ADR-0039 §3; ADR-0024 A2.3, ratified 2026.09.29). A stall, never a denial: PC/EC.
    Stalled(String),
    Denied(String),
}

/// `PromotionEnabled(a)` from ADR-0024, given the gate evidence, with the author's round taken
/// as covered. The state machine uses [`tally_with_coverage`]; this form is for the tally rules
/// alone (tests, status).
pub fn tally(c: &Candidate, rules: &Rules, evidence: Option<&Digest>) -> Tally {
    tally_with_coverage(c, rules, evidence, true)
}

/// `PromotionEnabled(a)` with coverage (ADR-0024 A2.3). `covered` is the
/// mechanism's fact that the author's cell Observer reported a watermark at or beyond the seal
/// of the author's round topic (ADR-0039 §3). It is read here and not in the floor, because it
/// is mechanism state, as recusal's counted set is.
pub fn tally_with_coverage(c: &Candidate, rules: &Rules, evidence: Option<&Digest>, covered: bool) -> Tally {
    // Gates enable voting; they do not vote (§4). No evidence, nothing can count.
    let Some(evidence) = evidence else {
        return Tally::Pending { granted: 0, counted: 0 };
    };
    let current = |r: &VoteRecord, verdict: Verdict| {
        r.verdict == verdict && &r.evidence == evidence && r.rules_epoch == rules.rules_epoch
    };

    // G == r.grantSeats \ {Author(a)} — recusal as a mechanism constant (§6).
    let counted: BTreeSet<&SeatId> = rules.grant_roster.iter().filter(|s| **s != c.author).collect();
    if counted.len() < rules.min_grant as usize {
        return Tally::Denied(format!(
            "recusal leaves {} counted grant seats, below minGrant {}",
            counted.len(),
            rules.min_grant
        ));
    }

    // A veto-seat deny is a denial; veto-seat silence is not (§2).
    for s in &rules.veto_roster {
        if c.votes.get(s).is_some_and(|r| current(r, Verdict::Deny)) {
            return Tally::Denied(format!("veto seat {s} denied"));
        }
    }

    let granted = counted.iter().filter(|s| c.votes.get(**s).is_some_and(|r| current(r, Verdict::Grant))).count();

    let would_promote = match rules.quorum {
        Quorum::All => {
            // Any grant-seat deny is a denial under unanimity.
            if let Some(s) = counted.iter().find(|s| c.votes.get(**s).is_some_and(|r| current(r, Verdict::Deny))) {
                return Tally::Denied(format!("grant seat {s} denied under unanimity"));
            }
            granted == counted.len()
        }
        Quorum::Threshold(k) => granted >= k as usize,
    };
    if !would_promote {
        return Tally::Pending { granted, counted: counted.len() };
    }
    if !covered {
        return Tally::Stalled("the author's round is not covered by a cell Observer (ADR-0039 §3)".into());
    }
    Tally::Promoted
}
