------------------------------ MODULE Counter ------------------------------
(* The setup check's fixture: the smallest module that has one of everything the scripts handle. setup_check.py
   runs its row list, its proof and its flip test in a temp directory; it is not a model of anything.

   A counter that may step while it is below Limit, and records in a flag any step taken at or above it.

   Property     Bounded       no step was taken at or above Limit          (the guard on Step)
   Mutation     M_NOLIMIT     removes that guard; must break Bounded
   Witness      NeverStepped  must be VIOLATED: a step is reachable at all
   Liveness     Reaches       under SpecLive the counter reaches Limit; under Spec (no fairness) it need not
   Deadlock     the state n = Limit is terminal under none, and it is the only one (AtLimit)

   Limit is unconstrained here beyond being a natural number; the row list sets it. *)
EXTENDS Naturals

CONSTANTS Mut, Limit
ASSUME LimitNat == Limit \in Nat

VARIABLES n, over
vars == <<n, over>>

TypeOK == n \in Nat /\ over \in BOOLEAN

Init == n = 0 /\ over = FALSE

Step == /\ Mut = "M_NOLIMIT" \/ n < Limit
        /\ n' = n + 1
        /\ over' = (over \/ n >= Limit)

Next == Step
Spec == Init /\ [][Next]_vars
SpecLive == Spec /\ WF_vars(Step)

Bounded == ~over
NeverStepped == n = 0
AtLimit == n = Limit
Reaches == <>AtLimit
NoBehaviour == <>FALSE
Small == n <= Limit + 1   \* a state constraint for the mutation's rows, whose count is otherwise unbounded
=============================================================================
