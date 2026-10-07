/-!
# The subtracting interval, transcribed and proved

`mechanism/crates/topak-core/src/clock.rs` (ADR-0032 §2): the one arithmetic check the mechanism's clock
makes. Intervals whose failure subtracts authority, lease expiry and vote timeout, run on a local monotonic
clock read with an asymmetric margin, so that clock error expires early rather than late. `Lease_A1.tla`
abstracts time away; this file proves the claim the Rust comment makes, of the Rust arithmetic.

```rust
/// A subtracting interval: elapsed once `now >= start + len - margin`. The margin moves expiry
/// earlier, never later (ADR-0032 §2, "fails closed").
pub fn subtracting_interval_elapsed(start: MonoMillis, len: u64, margin: u64, now: MonoMillis) -> bool {
    now.saturating_add(margin) >= start.saturating_add(len)
}
```

`u64` values are naturals below `2^64`; `saturating_add` is `min (a + b) (2^64 - 1)`. The transcription's
fidelity to the Rust is read, as in `Admit.lean`.
-/

namespace Topak.Clock

/-- `u64::MAX` -/
def u64Max : Nat := 2 ^ 64 - 1

/-- `a.saturating_add(b)` on `u64`. -/
def satAdd (a b : Nat) : Nat := min (a + b) u64Max

/-- `subtracting_interval_elapsed(start, len, margin, now)`. -/
def elapsed (start len margin now : Nat) : Bool := decide (satAdd now margin ≥ satAdd start len)

/-- Where nothing saturates, the check is the comment's `now >= start + len - margin`, with the subtraction
moved to the other side so that it never goes below zero. -/
theorem elapsed_iff (start len margin now : Nat) (h1 : now + margin ≤ u64Max) (h2 : start + len ≤ u64Max) :
    elapsed start len margin now = true ↔ now + margin ≥ start + len := by
  unfold elapsed satAdd
  rw [Nat.min_eq_left h1, Nat.min_eq_left h2]
  simp

/-- The margin moves expiry earlier, never later: a larger margin elapses whenever a smaller one does. -/
theorem elapsed_mono_margin (start len m m' now : Nat) (h : m ≤ m') (he : elapsed start len m now = true) :
    elapsed start len m' now = true := by
  unfold elapsed satAdd at *
  simp at *
  omega

/-- In particular, with the margin the interval elapses no later than without it. -/
theorem elapsed_never_later (start len margin now : Nat) (he : elapsed start len 0 now = true) :
    elapsed start len margin now = true :=
  elapsed_mono_margin start len 0 margin now (Nat.zero_le _) he

/-- Elapsed stays elapsed: the clock is monotonic, and so is the check in `now`. -/
theorem elapsed_mono_now (start len margin now now' : Nat) (h : now ≤ now') (he : elapsed start len margin now = true) :
    elapsed start len margin now' = true := by
  unfold elapsed satAdd at *
  simp at *
  omega

/-- The margin never makes an interval elapse before it started: at `now < start` with `margin ≤ len`, and no
saturation, the interval has not elapsed. A margin larger than the length is a configuration fault, not a
clock one. -/
theorem not_elapsed_before_start (start len margin now : Nat) (hm : margin ≤ len) (hn : now < start)
    (h1 : now + margin ≤ u64Max) (h2 : start + len ≤ u64Max) :
    elapsed start len margin now = false := by
  unfold elapsed satAdd
  rw [Nat.min_eq_left h1, Nat.min_eq_left h2]
  simp
  omega

#print axioms elapsed_iff
#print axioms elapsed_mono_margin
#print axioms elapsed_never_later
#print axioms elapsed_mono_now
#print axioms not_elapsed_before_start

end Topak.Clock
