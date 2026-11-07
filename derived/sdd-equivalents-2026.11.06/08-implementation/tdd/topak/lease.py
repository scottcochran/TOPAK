"""Layer: implementation · TDD · TOPAK source: topak-core/src/lease.rs::check_renewal, as the tests in 03-record/tdd made it go green.

A Python port of `Lease::check_renewal`, written to the tests, with the Rust it ports in the
docstring. This is the paper's TDD: the test is the micro-specification, the code is what passed
it. The edge to lease.rs is *read* (one person compared them); the edge to Lease_A1.tla is *tested*.
"""
from dataclasses import dataclass, replace
from typing import FrozenSet, Literal


@dataclass(frozen=True)
class Confinement:
    digest: str
    rung: int        # 0..3; fixed across renewal (ADR-0031 A1)


@dataclass(frozen=True)
class Lease:
    """ADR-0031 §1: twelve fields, closed."""
    principal: str
    seat: str
    persona: str
    epoch: int
    fence: int
    rules_epoch: int
    bundle: str
    confinement: Confinement
    alphabet: FrozenSet[str]
    round: int
    role: Literal["author", "voter"]
    ttl_ms: int

    def replace(self, **kw) -> "Lease":
        return replace(self, **kw)

    def check_renewal(self, new: "Lease") -> None:
        """ADR-0031 §4: `new ⊑ self`. Raises RenewalRefused with the reason lease.rs gives.

        ```rust
        same("principal", new.principal == self.principal)?;  ... same("role", new.role == self.role)?;
        if !new.alphabet.is_subset(&self.alphabet) { return Err("renewal widens the alphabet".into()); }
        same("confinement rung", new.confinement.rung == self.confinement.rung)?;
        if new.ttl_ms > self.ttl_ms { return Err("renewal lengthens the TTL".into()); }
        ```
        """
        for what, ok in [
            ("principal", new.principal == self.principal),
            ("seat", new.seat == self.seat),
            ("persona", new.persona == self.persona),
            ("epoch", new.epoch == self.epoch),
            ("rulesEpoch", new.rules_epoch == self.rules_epoch),
            ("bundle", new.bundle == self.bundle),
            ("confinement digest", new.confinement.digest == self.confinement.digest),
            ("round", new.round == self.round),       # R1: a change of round or role is a grant
            ("role", new.role == self.role),
        ]:
            if not ok:
                raise RenewalRefused(f"renewal changes {what}")
        if not new.alphabet <= self.alphabet:
            raise RenewalRefused("renewal widens the alphabet")
        if new.confinement.rung != self.confinement.rung:   # A1: either direction is refused
            raise RenewalRefused("renewal changes confinement rung")
        if new.ttl_ms > self.ttl_ms:
            raise RenewalRefused("renewal lengthens the TTL")


class RenewalRefused(Exception):
    @property
    def reason(self) -> str:
        return self.args[0]
