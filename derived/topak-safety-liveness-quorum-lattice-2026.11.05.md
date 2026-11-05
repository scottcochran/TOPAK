> How can the following concepts be combined: PACELC; Safety, Always, Eventually, Liveness, Strong/Weak Fairness;
> Quorum, Unitary. Perhaps similar to the TOPAK premise lattice?

**Verdict:** they combine, and the corpus already holds most of the pieces. Each concept takes one of three places
in the premise lattice of `topak-rung-DAG-2026.09.27.md`: a **kind of theorem**, a **premise** under a theorem, or
a **parameter axis**. PACELC is not a fourth thing. It is a label computed from where the partition and latency
premises sit. "Unitary" is read here as a single-actor decision, *k* = 1; if a unitary (central) authority against a
federated one was meant, that is another axis, not a point on the quorum chain.

## Where each concept goes

| Concept | Role in the lattice | Where the corpus already has it |
|---|---|---|
| **Safety, Always (□P)** | A theorem kind: nothing bad ever happens | Every row of `spec/theorem-premise-binding.md` |
| **Liveness, Eventually (◇P, P ~> Q)** | A theorem kind: something good eventually happens | `spec/Coupling_live.tla`, `spec/Emergency_live.tla` (ToO §5.5) |
| **Weak and strong fairness** | Premise nodes under liveness theorems only. SF on an action implies WF on it, so as assumptions they order none < WF < SF | A12 and A18 (ToO §13). The liveness plan notes that coupling needs SF on `Admit`, or `Stale` restricted, because `Stale` makes `Admit` only intermittently enabled |
| **Quorum (*k*-of-*n*), unitary (*k* = 1)** | A parameter axis, per action class | Approver fault tolerance and anchor custody: A-0025 (n, 0), D-0024-1 (*k*-of-*n*), D-0024-2 (single signer) |
| **PACELC** | A label derived from where the partition premise and the latency premise sit | Stated in prose, never as a column: "Build favors consistency over latency" (ToO §5.2); "during a partition nothing commits" for effects (liveness plan); stale bundles monotone-safe under partition (ToO §3.1) |

## How they connect

**1. Quorum is one dial that trades safety against liveness.** The custody table's `(capture, loss)` pair (ToO §7.2)
is that pair already:

- **capture = *k***: how many Byzantine holders it takes to grant. The safety tolerance: `P9_NoSoloGrant` needs
  *k* ≥ 2, which R9 keeps once R1 is relaxed.
- **loss = *n* − *k***: how many unavailable holders still let a grant happen. The liveness tolerance: "Liveness
  equals the availability of every grant seat" at unanimity (ToO §7.1).

Unitary (*k* = 1) and unanimity (*k* = *n*) are the two ends of the chain. Points between them are only
Pareto-comparable. The 09.16 critical review's argument that (n−1, 1) may dominate (n, 0) is exactly this trade, and
it is the dominance rule ADR-0023 defers.

This grant threshold is not a consensus quorum. Consensus is crash-fault (T-0045-1, in BASE), and its intersection
conditions sit inside that row; the threshold here is an authorization count over people. The two should not share a
column.

**2. Quorum size depends on direction.** The corpus already applies the asymmetry:

- Authority-increasing acts (grant, promote, seat) are quorum-gated.
- Authority-decreasing acts are unitary: deny, e-stop, revocation, `deny=all`, and Observers combining by any-of
  with no Observer quorum (ToO §5.1; `Observers.tla`'s `M_QUORUM`).

Subtraction is monotone-safe, so no single actor can make it unsafe, and unitary keeps it as available as it can be.
The quorum axis is therefore a pair per action class: *k* for adding, *k* for removing.

**3. Fairness and timing premises belong under liveness theorems only.** ADR-0032 §1, "clocks buy liveness, never
safety", becomes a structural constraint on the DAG: **no safety theorem may have a fairness, timing or partition
premise among its ancestors.** Liveness theorems carry those premises:

- fairness on actions (WF or SF);
- consensus progress under partial synchrony (the liveness plan's Tier 2);
- seat availability at least *k*, from the quorum axis.

**4. PACELC falls out as a computed label.** Read a partition as falsifying the consensus-progress premise. Then,
per action class:

- **PC** if none of its safety theorems depends on that premise: under a partition only its liveness theorems go
  void, and it stalls safely.
- **PA** if it stays live under a partition. That is safe only for a monotone action, which is why the subtraction
  path is PA and still safe.
- **EL or EC** concerns a quantitative premise (`W + L + D < T_irrev`, `T_obs`, `K`). The liveness plan puts these in
  the measured-not-proved tier, so the latency side is a declared gap premise, not a theorem.

That gives roughly: Run effects PC/EC within a declared latency budget, Run subtraction PA/EL, Build PC/EC. Each label
would be read from the table rather than asserted.

## The combined structure

The same structure as the rung-DAG analysis: a **lattice of order ideals over one theorem and premise DAG**, with a
deployment a point in the product of these axes:

```
Q_add   : 1 (unitary) ≤ … ≤ n (unanimous)      per authority-increasing class
Q_sub   : usually fixed at 1 (any-of)            per subtracting class
Fair    : none ≤ WF(a) ≤ SF(a)                   per action, as an assumption
Net     : async ≤ partial synchrony ≤ synchronous
Timing  : unmeasured ≤ declared ≤ measured       W, L, D, T_obs, K
```

A deployment's inventory splits into two ideals:

- the **safety ideal**, which depends only on `Q_add` and the trusted-base rows;
- the **liveness ideal**, which also depends on `Fair`, `Net`, `Timing` and *n* − *k*.

As with Observer scoping in ADR-0023, the result is a lattice and not a chain: 3-of-5 under WF and 5-of-5 under SF
are incomparable. In the matrix form of `topak-rung-DAG-as-matrix-2026.10.03.md` this adds premise columns and one
row attribute, Kind; it does not need a tensor.

## What it would take

1. **Columns in the binding table:** Kind (□ or ~>), Fairness (—, WF(action) or SF(action)), Network (none or
   partial synchrony), Quorum (capture, loss). The liveness modules have no rows yet (ToO §7.9), so they would be the
   first to use them.
2. **A check in `spec/inventory.py`** that every safety row has Fairness — and Network none, so that ADR-0032 §1 is
   computed rather than stated.
3. **The PACELC label per action class**, computed from those columns.
4. **The mutation discipline kept for liveness:** one mutation per leads-to property that must break it, as
   `M_HBLIVE` breaks `GrantStallEnds` while passing every safety check and every witness. That case is the strongest
   argument for Kind as its own column.

## Caveats

- PACELC is an informal 2 × 2 classification, not an ordered axis. It fits as a derived label, not a dimension.
- The ordering none < WF < SF is an ordering of assumptions per action. Fairness on different actions is not
  comparable, so `Fair` is itself a product over actions, not a chain.
- Nothing here proves a liveness property. The proof routes and their open cases stay as ToO §5.5 and ADR-0046 A2
  state them.
