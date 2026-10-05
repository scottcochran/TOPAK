//! TOPAK admit-path reference mechanism — the core.
//!
//! Everything in this crate is deterministic and performs no I/O. It holds the parts of the
//! verified object that are *mechanism code* rather than floor text:
//!
//! - the epoch fence and lease discipline (ADR-0022 §2, ADR-0031),
//! - confinement: the profile, the appraisal at grant, the session proof (ADR-0034, ADR-0036),
//! - the rules floor that bounds anchor issuances (ADR-0026),
//! - the promotion tally (ADR-0024),
//! - the syntactic lift that builds the one frozen input both policy tiers read (ADR-0030 §4),
//! - monotone composition of the floor and bundle decisions (ADR-0030 §1),
//! - the replicated state machine applied from the Paxos log (ADR-0015).
//!
//! Provisional choices are marked `PROVISIONAL:` and indexed in `GAPS-AND-ASSUMPTIONS.md`.

pub mod action;
pub mod admit;
pub mod authentic;
pub mod clock;
pub mod confine;
pub mod labels;
pub mod lease;
pub mod lift;
pub mod promotion;
pub mod rules;
pub mod state;
pub mod trace;
pub mod types;

pub use types::*;
pub mod observer;
pub use observer::{Heartbeat, ObserverValues, PersonaValues};
