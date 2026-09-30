------------------------------ MODULE RunSeats ------------------------------
(* Properties for ADR-0043 §2 (Proposed), alphabets by seat kind in Run, and   *)
(* for ADR-0040 §2: no variant name is common to Build and Run.                *)
(*                                                                             *)
(*   OnlyThinkersActuate        0043 §2  no seat but a thinker's is admitted   *)
(*                                       an Actuate                            *)
(*   ObserversConsultAndReport  0043 §2  a Run observer seat is admitted       *)
(*                                       Consult and Report, and nothing else  *)
(*   NoNameCrossesDomains       0040 §2  a Run variant is admitted only under  *)
(*                                       a Run seat, and a Build variant only  *)
(*                                       under a Build seat                    *)
(*                                                                             *)
(* Seats.tla models ADR-0037 §4's Build column and the one-seat rule. It is    *)
(* frozen by digest and is not changed; the one-seat rule is its, and is not   *)
(* restated here. A seat has a kind and a domain, both fixed at declaration.   *)
(* A grant asks for every variant there is; the mechanism issues what the      *)
(* seat's kind and domain allow. Every admitted action records the kind and    *)
(* the domain of the seat it was admitted under.                               *)
(*                                                                             *)
(* Mut = "none":     the mechanism as ADR-0043 specifies it.                    *)
(* Mut = "M_KIND":   the grant path ignores the kind bound. OnlyThinkersActuate *)
(*                   and ObserversConsultAndReport must fail.                  *)
(* Mut = "M_DOMAIN": the grant path ignores the domain. NoNameCrossesDomains    *)
(*                   must fail, and ObserversConsultAndReport with it: a Run   *)
(*                   observer seat issued Read holds something else.           *)
(* Mut = "M_OBSEMIT": an observer seat is issued Report only, the provisional   *)
(*                   column of ADR-0037 §4. No property fails; the witness     *)
(*                   NeverObserverConsulted HOLDS, which shows what the        *)
(*                   provisional column could not do.                          *)
EXTENDS FiniteSets

CONSTANTS Mut

Seats     == {"rt", "ro", "bt", "bo"}
BuildActs == {"Read", "Draft", "Emit"}
RunActs   == {"Consult", "Actuate", "Report"}
Acts      == BuildActs \cup RunActs

KindOf   == [rt |-> "thinker", ro |-> "observer", bt |-> "thinker", bo |-> "observer"]
DomainOf == [rt |-> "run",     ro |-> "run",      bt |-> "build",   bo |-> "build"]

DomainActs(d) == IF d = "run" THEN RunActs ELSE BuildActs

\* ADR-0037 §4 for Build, ADR-0043 §2 for Run.
KindBound(k) ==
  CASE k = "thinker"  -> {"Read", "Draft", "Emit", "Consult", "Actuate", "Report"}
    [] k = "observer" -> IF Mut = "M_OBSEMIT" THEN {"Read", "Emit", "Report"}
                                              ELSE {"Read", "Emit", "Consult", "Report"}

NoLease == [live |-> FALSE, alphabet |-> {}]

VARIABLES lease, acted
vars == <<lease, acted>>

Init == /\ lease = [s \in Seats |-> NoLease]
        /\ acted = {}

Grant(s) ==
  /\ ~lease[s].live
  /\ LET byKind   == IF Mut = "M_KIND" THEN Acts ELSE KindBound(KindOf[s])
         byDomain == IF Mut = "M_DOMAIN" THEN Acts ELSE DomainActs(DomainOf[s])
     IN lease' = [lease EXCEPT ![s] = [live |-> TRUE, alphabet |-> byKind \cap byDomain]]
  /\ UNCHANGED acted

Act(s) ==
  /\ lease[s].live
  /\ \E a \in lease[s].alphabet :
       acted' = acted \cup {[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]}
  /\ UNCHANGED lease

EndRound(s) ==
  /\ lease[s].live
  /\ lease' = [lease EXCEPT ![s] = NoLease]
  /\ UNCHANGED acted

Next == \E s \in Seats : Act(s) \/ EndRound(s) \/ Grant(s)
Spec == Init /\ [][Next]_vars

\* --- the three properties ---------------------------------------------------

\* ADR-0043 §2. Actuate is Run's one variant that runs anything, and only a thinker holds it.
OnlyThinkersActuate == \A r \in acted : r.act = "Actuate" => r.kind = "thinker"

\* ADR-0043 §2. A Run observer seat reads pinned content and reports, and nothing else.
ObserversConsultAndReport ==
  \A r \in acted : (r.kind = "observer" /\ r.domain = "run") => r.act \in {"Consult", "Report"}

\* ADR-0040 §2. No name is shared, so a verb names its domain.
NoNameCrossesDomains == \A r \in acted : (r.act \in RunActs) <=> (r.domain = "run")

Safe == OnlyThinkersActuate /\ ObserversConsultAndReport /\ NoNameCrossesDomains

\* --- reachability witnesses: each must be VIOLATED under "none" ----------------
NeverActuated          == ~\E r \in acted : r.act = "Actuate"
NeverObserverReported  == ~\E r \in acted : r.act = "Report" /\ r.kind = "observer"
NeverObserverConsulted == ~\E r \in acted : r.act = "Consult" /\ r.kind = "observer"
=============================================================================
