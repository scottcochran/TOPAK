//! Issued rules, the rules floor that bounds them (ADR-0026), and issuance validation
//! (ADR-0025).
//!
//! The rules floor stays mechanism-checked (ADR-0030 §7). Parametricity is load-bearing: every
//! value an entry bounds is read by the mechanism from the issued rules, never hard-coded, or the
//! entry would be vacuous (ADR-0026 §6).

use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::fmt;

use crate::authentic::{self, KeyHex, Signed};
use crate::types::*;

/// `quorum` is `"all"` or a grant-vote threshold *k* (ADR-0024 §2). `"any"` is withdrawn.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Quorum {
    All,
    Threshold(u32),
}

impl Serialize for Quorum {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        match self {
            Quorum::All => s.serialize_str("all"),
            Quorum::Threshold(k) => s.serialize_u32(*k),
        }
    }
}

impl<'de> Deserialize<'de> for Quorum {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        match Value::deserialize(d)? {
            Value::String(s) if s == "all" => Ok(Quorum::All),
            Value::Number(n) => n
                .as_u64()
                .and_then(|k| u32::try_from(k).ok())
                .map(Quorum::Threshold)
                .ok_or_else(|| serde::de::Error::custom("quorum threshold must be a u32")),
            other => Err(serde::de::Error::custom(format!(
                "quorum must be \"all\" or a threshold; got {other} (\"any\" is withdrawn)"
            ))),
        }
    }
}

/// A seat declared by the rules. PROVISIONAL (seat registry): no record says where seats and
/// their domains are declared; the rosters are issued (ADR-0025 §1a), so seats are issued too.
/// The kind is ADR-0037 §2: fixed at declaration, and the bound on what the seat may be issued.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SeatDecl {
    pub domain: Domain,
    pub kind: SeatKind,
    /// For an `observer` seat: the Thinker seat it watches, which puts it in that Thinker's cell
    /// (ADR-0038 §1). `None` on an observer seat is a correlator, which belongs to no cell and
    /// watches every cell in its domain. Meaningless on other kinds, and refused there.
    #[serde(default)]
    pub cell: Option<SeatId>,
    /// The key that identifies the seat's holder. R5 compares these against the anchor key set.
    pub key: KeyHex,
}

/// The break-glass roster and envelope, issued with the rules (ADR-0009, ADR-0013 §1).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BreakGlassRules {
    pub roster: BTreeSet<KeyHex>,
    /// Approvals needed. PROVISIONAL: no record fixes the break-glass quorum rule.
    pub quorum: u32,
    /// Tool ids (`name@digest`) inside the break-glass envelope.
    pub tools: BTreeSet<String>,
    /// Actions a break-glass grant may authorize. Read by the mechanism so R7 has a value to
    /// bound; the floor's X1 additionally confines break-glass to `Actuate`.
    pub actions: BTreeSet<String>,
}

/// The authority-defining set (ADR-0025): rosters and their parameters, the anchor's own keys.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Rules {
    pub rules_epoch: RulesEpoch,
    pub quorum: Quorum,
    pub min_grant: u32,
    pub seats: BTreeMap<SeatId, SeatDecl>,
    pub grant_roster: BTreeSet<SeatId>,
    pub veto_roster: BTreeSet<SeatId>,
    pub anchor_keys: BTreeSet<KeyHex>,
    #[serde(default)]
    pub break_glass: Option<BreakGlassRules>,
    /// Genesis rules issue no erasure roster, so erasure is disabled from epoch 0 (ADR-0028).
    #[serde(default)]
    pub erasure_roster: Option<BTreeSet<KeyHex>>,
}

impl Rules {
    pub fn seat_domain(&self, seat: &str) -> Option<Domain> {
        self.seats.get(seat).map(|s| s.domain)
    }

    pub fn seat_kind(&self, seat: &str) -> Option<SeatKind> {
        self.seats.get(seat).map(|s| s.kind)
    }

    /// The observer seats in a Thinker's cell (ADR-0038 §1): those declaring `cell = thinker`.
    pub fn cell_observers(&self, thinker: &str) -> Vec<SeatId> {
        self.seats
            .iter()
            .filter(|(_, d)| d.kind == SeatKind::Observer && d.cell.as_deref() == Some(thinker))
            .map(|(id, _)| id.clone())
            .collect()
    }

    /// Whether `observer` is in `W(thinker)` (ADR-0038 §2): its cell Observer, or a correlator
    /// in the same domain. The reference has no topic read ACL, so this is the declared reach.
    pub fn watches(&self, observer: &str, thinker: &str) -> bool {
        match (self.seats.get(observer), self.seats.get(thinker)) {
            (Some(o), Some(t)) if o.kind == SeatKind::Observer && t.kind == SeatKind::Thinker => match &o.cell {
                Some(c) => c == thinker,
                None => o.domain == t.domain,
            },
            _ => false,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Violation {
    pub entry: &'static str,
    pub detail: String,
}

impl fmt::Display for Violation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.entry, self.detail)
    }
}

fn v(entry: &'static str, detail: impl Into<String>) -> Violation {
    Violation { entry, detail: detail.into() }
}

/// R6: the floor-exception count bound (ADR-0013 §3). The exceptions live in the policy floor,
/// so this is checked against the floor text the mechanism loaded.
pub const EXCEPTION_BOUND: usize = 2;

/// Actions R7 forbids a break-glass grant to authorize.
pub const R7_FORBIDDEN: [&str; 3] = ["Issue", "Vote", "Promote"];

/// The genesis rules floor: R1, R2, R5, R6, R7, R9 (G2 §2). R3 and R4 are withdrawn (they are
/// mechanism constants: recusal in the `Vote` envelope, "a timeout is never a grant" in the
/// tally). R8 is reserved and not implemented.
pub fn check_rules_floor(r: &Rules, floor_exceptions: usize) -> Vec<Violation> {
    let mut out = Vec::new();

    // R1 — quorum = "all" over counted grant seats.
    if r.quorum != Quorum::All {
        out.push(v("R1", format!("quorum is {:?}, not \"all\"", r.quorum)));
    }
    // R2 — minGrant ≥ 2. Without it an empty roster promotes with zero votes (ADR-0026 §6).
    if r.min_grant < 2 {
        out.push(v("R2", format!("minGrant is {}, below 2", r.min_grant)));
    }
    // R5 — no key both in the anchor key set and on the promotion roster.
    for seat in r.grant_roster.iter().chain(&r.veto_roster) {
        if let Some(decl) = r.seats.get(seat)
            && r.anchor_keys.contains(&decl.key)
        {
            out.push(v("R5", format!("seat {seat}'s key is also an anchor key")));
        }
    }
    // R6 — floor-exception count ≤ 2.
    if floor_exceptions > EXCEPTION_BOUND {
        out.push(v("R6", format!("{floor_exceptions} floor exceptions exceed the bound {EXCEPTION_BOUND}")));
    }
    // R7 — no break-glass grant may authorize Issue, Vote, or promotion.
    if let Some(bg) = &r.break_glass {
        for a in R7_FORBIDDEN {
            if bg.actions.contains(a) {
                out.push(v("R7", format!("break-glass envelope authorizes {a}")));
            }
        }
    }
    // R9 — quorum = "all" ∨ quorum ≥ 2. Conditional: binds only once R1 is relaxed.
    if let Quorum::Threshold(k) = r.quorum
        && k < 2
    {
        out.push(v("R9", format!("threshold {k} is below 2 (single-signer is a separate degeneracy)")));
    }
    out
}

/// Well-formedness the mechanism needs to read the rules at all. These are not rules-floor
/// entries: they bound nothing the anchor intends, they reject rules the mechanism cannot use.
pub fn check_well_formed(r: &Rules) -> Vec<Violation> {
    let mut out = Vec::new();
    for seat in r.grant_roster.iter().chain(&r.veto_roster) {
        match r.seats.get(seat) {
            None => out.push(v("WF", format!("roster seat {seat} is not declared"))),
            Some(d) if d.domain != Domain::Build => {
                out.push(v("WF", format!("roster seat {seat} is not a Build seat")))
            }
            _ => {}
        }
    }
    // ADR-0038 §1: a cell names a declared thinker seat in the same domain; only observers have one.
    for (id, d) in &r.seats {
        match (&d.cell, d.kind) {
            (Some(_), k) if k != SeatKind::Observer => {
                out.push(v("WF", format!("seat {id} is a {k} and cannot have a cell")))
            }
            (Some(t), _) => match r.seats.get(t) {
                Some(td) if td.kind == SeatKind::Thinker && td.domain == d.domain => {}
                Some(_) => out.push(v("WF", format!("observer {id}'s cell {t} is not a thinker seat in its domain"))),
                None => out.push(v("WF", format!("observer {id}'s cell {t} is not declared"))),
            },
            (None, _) => {}
        }
    }
    if let Some(bg) = &r.break_glass
        && (bg.quorum == 0 || bg.quorum as usize > bg.roster.len())
    {
        out.push(v("WF", "break-glass quorum must be between 1 and the roster size"));
    }
    if r.anchor_keys.is_empty() {
        out.push(v("WF", "anchor key set is empty"));
    }
    out
}

/// An anchor issuance: new rules at the next rules epoch, signed (ADR-0025 `Issue`).
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Issuance {
    pub rules: Rules,
    pub signatures: Vec<Signed>,
}

pub const ISSUANCE_PURPOSE: &str = "issuance";

/// Validate an issuance against the rules in force: epoch increment, `Authentic`, the rules
/// floor. The mechanism rejects any issuance that violates the floor (ADR-0026).
///
/// PROVISIONAL (custody): `Authentic` is "every key in the current anchor key set signed",
/// which is archetype custody A-0025 (strict unanimity). Degenerate custody rungs are
/// declarations and would change only this function.
pub fn validate_issuance(current: &Rules, iss: &Issuance, floor_exceptions: usize) -> Result<(), Vec<Violation>> {
    let mut out = Vec::new();
    if iss.rules.rules_epoch != current.rules_epoch + 1 {
        out.push(v(
            "Issue",
            format!("rules epoch {} is not the successor of {}", iss.rules.rules_epoch, current.rules_epoch),
        ));
    }
    let body = serde_json::to_value(&iss.rules).expect("serializable");
    let signers = authentic::valid_signers(ISSUANCE_PURPOSE, &body, &iss.signatures, &current.anchor_keys);
    if signers != current.anchor_keys {
        out.push(v("Authentic", format!("{} of {} anchor keys signed", signers.len(), current.anchor_keys.len())));
    }
    out.extend(check_well_formed(&iss.rules));
    out.extend(check_rules_floor(&iss.rules, floor_exceptions));
    if out.is_empty() { Ok(()) } else { Err(out) }
}
