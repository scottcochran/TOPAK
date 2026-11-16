------------------------------ MODULE Federation ------------------------------
(* A deployment that is a tree of planes: ADR-0059 (Proposed), its             *)
(* ratification condition (§9), and proposal §10 of                            *)
(* derived/topak-federated-c2-design-proposal-2026.11.10b.md. Each plane is    *)
(* seated by its parent under a charter it can only narrow, is a havoc issuer  *)
(* bounded by that charter, and is fenced by every plane above it.             *)
(*                                                                             *)
(* The tree is one chain of three planes, r -> a -> b, with r the root. A      *)
(* property here reads one path of the tree; a sibling would only be a second  *)
(* debit against the same `left`. `Captured` names the planes that sign        *)
(* anything their key can sign. The root's tally is honest: ADR-0025 bounds    *)
(* the anchor by the floor, which is another module's question.                *)
(*                                                                             *)
(*   CharterNarrows     a charter seated by an honest parent is the parent's   *)
(*                      or narrower, field by field (§1)                       *)
(*   LeaseWithinChain   every lease a verifier accepts is within every charter *)
(*                      on its chain (§4, §5)                                  *)
(*   HavocPlaneBounded  whatever the captured planes sign, no verifier permits *)
(*                      an entry the root's tally did not vote (§4)            *)
(*   BudgetConserved    leases issued under a charter and under every charter  *)
(*                      below it never exceed its budget, for a subtree with   *)
(*                      no captured plane (§1)                                 *)
(*   AnyPlaneFences     no verifier that has heard an epoch permits under a    *)
(*                      chain that carries an older epoch of that plane (§6)   *)
(*                                                                             *)
(* BUDGETCONSERVED IS STATED FOR AN HONEST SUBTREE, AND THAT IS A FINDING.     *)
(* §1 says the debit makes "the root's tally bounds the whole tree". The debit *)
(* bounds what is allocated. A captured plane can sign more leases than its    *)
(* budget, each to a different vehicle, and no single verifier sees more than  *)
(* its own, so nothing here can refuse them. What survives capture is the      *)
(* honest parent's account, which this module also carries (`Account`), and    *)
(* the per-governor bound of ADR-0063.                                         *)
(*                                                                             *)
(* What is abstracted. A charter has four of ADR-0059's fields: `seated`,      *)
(* `alphabet` (a set, narrowed by subset), `budget` (a number, narrowed by     *)
(* <= and debited) and `fence`. `labels`, `bundles`, `ttlMax`, `countMax` and  *)
(* `expiry` have the shape of the first two and are not repeated. A charter's  *)
(* `fence` is the epoch of its parent at the seating, which is the one value   *)
(* in `fences` that the plane above has actually signed: a captured plane can  *)
(* write any value for the planes above it, and the link above certifies the   *)
(* true one, so one value per link is what the check rests on. A commit        *)
(* certificate is taken as unforgeable (ADR-0059 §5, ADR-0061). A presented    *)
(* lease is any entry and any epoch, under any plane, honest or not: this is   *)
(* more than a signature allows of an honest plane, so a property that holds   *)
(* rests on the verifier's checks alone. `Verifiers` are honest: a governor,   *)
(* or a plane's admit path, which runs the same comparison (§6). A plane is    *)
(* not re-seated: a fenced charter stays fenced until a new promotion, which   *)
(* this module leaves out. Membership is Membership.tla's (ADR-0061).          *)
(*                                                                             *)
(* Mut = "none":          ADR-0059 as drafted.                                 *)
(* Mut = "M_WIDEN":       a seating by an honest parent may widen the          *)
(*                        alphabet. CharterNarrows must fail, and nothing else:*)
(*                        the verifier reads every charter on the chain.       *)
(* Mut = "M_LASTLINK":    a verifier checks only the granting plane's charter. *)
(*                        LeaseWithinChain and HavocPlaneBounded must fail.    *)
(* Mut = "M_TRUSTPLANE":  a verifier takes a captured plane's word for its own *)
(*                        chain and checks no charter. LeaseWithinChain and    *)
(*                        HavocPlaneBounded must fail.                         *)
(* Mut = "M_NODEBIT":     a child's budget is not debited from its parent's.   *)
(*                        BudgetConserved must fail.                           *)
(* Mut = "M_STALEEPOCH":  a check compares only the granting plane's epoch.    *)
(*                        AnyPlaneFences must fail.                            *)
(*                                                                             *)
(* Proposal §10 says each property has a mutation that breaks it and nothing   *)
(* else. M_LASTLINK and M_TRUSTPLANE each break two properties: under capture  *)
(* a lease outside the chain is, or can be, outside what the root voted.       *)
(*                                                                             *)
(* Deadlock is not checked: a chain that is seated and spent is safe.          *)
EXTENDS Naturals

CONSTANTS Mut, MaxEpoch, RootBudget, Captured, Verifiers

ASSUME CapturedNotRoot == Captured \subseteq {"a", "b"}

Planes       == {"r", "a", "b"}
Children     == {"a", "b"}
Parent       == [a |-> "r", b |-> "a"]
Child        == [r |-> "a", a |-> "b"]
Entries      == {"e1", "e2", "e3"}
RootAlphabet == {"e1", "e2"}

ChainOf(p) == IF p = "r" THEN {"r"} ELSE IF p = "a" THEN {"r", "a"} ELSE Planes
Below(p)   == IF p = "r" THEN Planes ELSE IF p = "a" THEN {"a", "b"} ELSE {"b"}

NoCharter   == [seated |-> FALSE, alphabet |-> {}, budget |-> 0, fence |-> 0]
RootCharter == [seated |-> TRUE, alphabet |-> RootAlphabet, budget |-> RootBudget, fence |-> 0]
Offered     == [seated : {TRUE}, alphabet : SUBSET Entries, budget : 0..RootBudget, fence : 0..MaxEpoch]

VARIABLES charter, left, issued, epoch, heard, outsideChain, outsideRoot, fenced, seen
vars == <<charter, left, issued, epoch, heard, outsideChain, outsideRoot, fenced, seen>>

Init ==
  /\ charter = [p \in Planes |-> IF p = "r" THEN RootCharter ELSE NoCharter]
  /\ left    = [p \in Planes |-> IF p = "r" THEN RootBudget ELSE 0]
  /\ issued  = [p \in Planes |-> 0]
  /\ epoch   = [p \in Planes |-> 0]
  /\ heard   = [v \in Verifiers |-> [q \in Planes |-> 0]]
  /\ outsideChain = FALSE
  /\ outsideRoot  = FALSE
  /\ fenced       = FALSE
  /\ seen         = {}

\* The mechanism's guards, each open to one mutation.
Narrows(c, par) == Mut = "M_WIDEN" \/ c.alphabet \subseteq par.alphabet
Debit(c)        == IF Mut = "M_NODEBIT" THEN 0 ELSE c.budget

WithinChain(p, e) == \A q \in ChainOf(p) : e \in charter[q].alphabet
ChainChecked(p, e) ==
  \/ Mut = "M_TRUSTPLANE" /\ p \in Captured
  \/ IF Mut = "M_LASTLINK" THEN e \in charter[p].alphabet ELSE WithinChain(p, e)

\* What a chain says of plane q's epoch: the lease's own value for the granting plane, and
\* for a plane above it the value q signed into the charter of the plane below it.
Carried(p, q, ep) == IF q = p THEN ep ELSE charter[Child[q]].fence
FenceTrue(v, p, ep) == \A q \in ChainOf(p) : Carried(p, q, ep) >= heard[v][q]
FenceOK(v, p, ep)   == IF Mut = "M_STALEEPOCH" THEN ep >= heard[v][p] ELSE FenceTrue(v, p, ep)

\* An honest parent seats a child: the charter is narrower, its budget is debited, and it
\* carries the parent's epoch.
SeatHonest(p, c) ==
  /\ Parent[p] \notin Captured
  /\ charter[Parent[p]].seated
  /\ ~charter[p].seated
  /\ Narrows(c, charter[Parent[p]])
  /\ c.budget <= left[Parent[p]]
  /\ c.fence = epoch[Parent[p]]
  /\ charter' = [charter EXCEPT ![p] = c]
  /\ left' = [left EXCEPT ![p] = c.budget, ![Parent[p]] = left[Parent[p]] - Debit(c)]
  /\ UNCHANGED <<issued, epoch, heard, outsideChain, outsideRoot, fenced, seen>>

\* A captured parent signs any charter its key can sign, and debits nothing.
SeatCaptured(p, c) ==
  /\ Parent[p] \in Captured
  /\ charter[Parent[p]].seated
  /\ ~charter[p].seated
  /\ charter' = [charter EXCEPT ![p] = c]
  /\ left' = [left EXCEPT ![p] = c.budget]
  /\ UNCHANGED <<issued, epoch, heard, outsideChain, outsideRoot, fenced, seen>>

\* An honest plane orders a lease and spends a unit of its budget.
Issue(p) ==
  /\ p \notin Captured
  /\ charter[p].seated
  /\ left[p] >= 1
  /\ left' = [left EXCEPT ![p] = left[p] - 1]
  /\ issued' = [issued EXCEPT ![p] = issued[p] + 1]
  /\ UNCHANGED <<charter, epoch, heard, outsideChain, outsideRoot, fenced, seen>>

\* A plane moves its epoch: a plane fence.
MoveEpoch(p) ==
  /\ epoch[p] < MaxEpoch
  /\ epoch' = [epoch EXCEPT ![p] = epoch[p] + 1]
  /\ UNCHANGED <<charter, left, issued, heard, outsideChain, outsideRoot, fenced, seen>>

\* A fence travels as far as the link does: a verifier hears a plane's latest epoch, or does not.
Hear(v, q) ==
  /\ heard[v][q] < epoch[q]
  /\ heard' = [heard EXCEPT ![v][q] = epoch[q]]
  /\ UNCHANGED <<charter, left, issued, epoch, outsideChain, outsideRoot, fenced, seen>>

\* A verifier accepts a presented lease: entry e under plane p, carrying epoch ep for p.
Permit(v, p, e, ep) ==
  /\ charter[p].seated
  /\ ChainChecked(p, e)
  /\ FenceOK(v, p, ep)
  /\ outsideChain' = (outsideChain \/ ~WithinChain(p, e))
  /\ outsideRoot'  = (outsideRoot \/ e \notin RootAlphabet)
  /\ fenced'       = (fenced \/ ~FenceTrue(v, p, ep))
  /\ seen' = seen \cup {"permit"} \cup (IF p = "b" THEN {"deep"} ELSE {})
                  \cup (IF heard[v]["r"] >= 1 THEN {"afterFence"} ELSE {})
  /\ UNCHANGED <<charter, left, issued, epoch, heard>>

\* A verifier refuses one.
Refuse(v, p, e, ep) ==
  /\ charter[p].seated
  /\ ~(ChainChecked(p, e) /\ FenceOK(v, p, ep))
  /\ seen' = seen \cup (IF ChainChecked(p, e) THEN {} ELSE {"refChain"})
                  \cup (IF FenceOK(v, p, ep) THEN {} ELSE {"refFence"})
  /\ UNCHANGED <<charter, left, issued, epoch, heard, outsideChain, outsideRoot, fenced>>

Next ==
  \/ \E p \in Children, c \in Offered : SeatHonest(p, c) \/ SeatCaptured(p, c)
  \/ \E p \in Planes : Issue(p) \/ MoveEpoch(p)
  \/ \E v \in Verifiers, q \in Planes : Hear(v, q)
  \/ \E v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch :
       Permit(v, p, e, ep) \/ Refuse(v, p, e, ep)

Spec == Init /\ [][Next]_vars

\* --- the five properties ------------------------------------------------------

CharterNarrows ==
  \A p \in Children :
    (charter[p].seated /\ Parent[p] \notin Captured) =>
      /\ charter[p].alphabet \subseteq charter[Parent[p]].alphabet
      /\ charter[p].budget <= charter[Parent[p]].budget

LeaseWithinChain  == ~outsideChain
HavocPlaneBounded == ~outsideRoot
AnyPlaneFences    == ~fenced

TreeIssued(p) ==
  IF p = "r" THEN issued["r"] + issued["a"] + issued["b"]
  ELSE IF p = "a" THEN issued["a"] + issued["b"]
  ELSE issued["b"]

BudgetConserved ==
  \A p \in Planes : (Below(p) \cap Captured = {}) => TreeIssued(p) <= charter[p].budget

Safe == CharterNarrows /\ LeaseWithinChain /\ HavocPlaneBounded /\ BudgetConserved /\ AnyPlaneFences

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverPermitted       == "permit" \notin seen
NeverDeepPermit      == "deep" \notin seen
NeverPermitAfterFence == "afterFence" \notin seen
NeverRefusedByChain  == "refChain" \notin seen
NeverRefusedByFence  == "refFence" \notin seen
NeverHavocWideCharter ==
  ~\E p \in Children :
     /\ charter[p].seated
     /\ Parent[p] \in Captured
     /\ ~(charter[p].alphabet \subseteq charter[Parent[p]].alphabet)
NeverChildDebited == ~(charter["a"].budget >= 1 /\ left["r"] + charter["a"].budget = RootBudget)
NeverBudgetSpent  == ~\E p \in Planes : p \notin Captured /\ issued[p] >= 1 /\ left[p] = 0
=============================================================================
