//! The clock model (ADR-0032).
//!
//! Clocks buy liveness, never safety: the epoch fence carries safety without reading a clock
//! (§1). Intervals whose failure subtracts authority — lease expiry, vote timeout — run on a
//! local monotonic clock read with an asymmetric margin, so clock error expires early rather
//! than late (§2). No safety decision reads a clock supplied by a principal (§3): the only time
//! source here is the mechanism's own.

/// Milliseconds on the mechanism's local monotonic clock. Not wall time.
pub type MonoMillis = u64;

pub trait MonotonicClock: Send + Sync {
    fn now_ms(&self) -> MonoMillis;
}

/// `std::time::Instant`-backed clock.
pub struct SystemMonotonic {
    origin: std::time::Instant,
}

impl SystemMonotonic {
    pub fn new() -> Self {
        Self { origin: std::time::Instant::now() }
    }
}

impl Default for SystemMonotonic {
    fn default() -> Self {
        Self::new()
    }
}

impl MonotonicClock for SystemMonotonic {
    fn now_ms(&self) -> MonoMillis {
        self.origin.elapsed().as_millis() as MonoMillis
    }
}

/// A subtracting interval: elapsed once `now >= start + len - margin`. The margin moves expiry
/// earlier, never later (ADR-0032 §2, "fails closed").
pub fn subtracting_interval_elapsed(start: MonoMillis, len: u64, margin: u64, now: MonoMillis) -> bool {
    now.saturating_add(margin) >= start.saturating_add(len)
}
