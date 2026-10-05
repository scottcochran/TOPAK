----------------------------- MODULE Emergency -----------------------------
(* Break-glass as an emergency seating: ADR-0052 (Proposed), its ratification  *)
(* condition (§9). A quorum on the break-glass roster seats a named person on  *)
(* a seat of kind `emergency` for one round. The seat's calls are admitted by  *)
(* the ordinary allowlist permit over an envelope computed at activation, and  *)
(* the floor carries no exception for break-glass.                             *)
(*                                                                             *)
(* The mechanism sees keys, approvals and leases. This module also carries, as *)
(* ghost state the mechanism never reads, whether the holder of the seat is a  *)
(* person or an agent, and for every lease whether a quorum stood behind it.   *)
(*                                                                             *)
(*   EmergencyLeaseHasARosterQuorum  every emergency lease was granted on the  *)
(*                                   approvals of a quorum of the roster       *)
(*   EmergencyLeaseIsOneRound        no emergency lease was granted by anyone  *)
(*                                   but the roster, and none was renewed      *)
(*   NoAgentHoldsAnEmergencySeat     the holder of a live emergency lease is a *)
(*                                   person                                    *)
(*   CallsAreAllowlisted             no call, by either seat, is admitted for  *)
(*                                   a tool outside its seat's allowlist: no   *)
(*                                   admit is by an exception                  *)
(*   ThinkerStillCoupled             no Thinker's call is admitted without a   *)
(*                                   live Observer: R3 is unchanged            *)
(*   ActivationIsForensic            every round the emergency seat has had    *)
(*                                   has its activation record                 *)
(*                                                                             *)
(* The domain has two tools that are promoted over time, t1 and t2; one that   *)
(* is emergency-only, te, in the emergency seating's own bundle; and one that  *)
(* is in no bundle at all, tx. The envelope given at activation is the domain's *)
(* tools as they then stand, with te (ADR-0052 §2, R1). The agent's seat is a  *)
(* Thinker with an allowlist narrowed from the domain's.                       *)
(*                                                                             *)
(* The roster has three members and its quorum is two. One emergency seat, one *)
(* Thinker. How a lease ends (the round bound, its ttl, a revocation, a fence) *)
(* is one action, `EndEm`: the properties do not depend on which. Not          *)
(* modelled: the label forbids, the task and its label, the drill, which is an *)
(* activation like any other, and a person acting outside the mechanism.       *)
(*                                                                             *)
(* Mut = "none":        ADR-0052 as revised at R1.                             *)
(* Mut = "M_NOQUORUM":  an activation with fewer approvals than the quorum.    *)
(*                      Must break EmergencyLeaseHasARosterQuorum only.        *)
(* Mut = "M_REGRANT":   an operator grants the emergency seat its next round.  *)
(*                      Must break EmergencyLeaseHasARosterQuorum,             *)
(*                      EmergencyLeaseIsOneRound and ActivationIsForensic.     *)
(* Mut = "M_RENEW":     an operator renews a live emergency lease. Must break  *)
(*                      EmergencyLeaseIsOneRound only.                         *)
(* Mut = "M_AGENT":     an agent may be seated. Must break                     *)
(*                      NoAgentHoldsAnEmergencySeat only.                      *)
(* Mut = "M_X1":        X1 is left in the floor: under a quorum's approvals    *)
(*                      any seat may call any tool, as the reference has it    *)
(*                      (D-0052-1). Must break CallsAreAllowlisted only.       *)
(* Mut = "M_UNCOUPLE":  R3 is dropped for the Thinker. Must break              *)
(*                      ThinkerStillCoupled only.                              *)
(* Mut = "M_ERASE":     erasure may remove an activation record. Must break    *)
(*                      ActivationIsForensic only.                             *)
EXTENDS Naturals

CONSTANTS Mut, MaxRound

Roster   == {"r1", "r2", "r3"}
Persons  == {"h"}
Agents   == {"g"}
Holders  == Persons \cup Agents
Domain   == {"t1", "t2"}                 \* tools a promotion can put in force
Tools    == Domain \cup {"te", "tx"}     \* te: emergency-only; tx: in no bundle

\* A quorum of the roster: two distinct members.
Quorate(S) == \E a \in S, b \in S : a # b

NoEm == [live |-> FALSE, round |-> 0, holder |-> "none", envelope |-> {},
         quorate |-> FALSE, by |-> "none", renewed |-> FALSE]

VARIABLES
  domainTools,   \* the Run tools in force in the domain
  approvals,     \* roster members who have approved the next activation
  em,            \* the emergency seat's lease, with what was true when it was granted
  thinkerAllow,  \* the Thinker's allowlist, narrowed from the domain's
  obsLive,       \* the Thinker's cell Observer is live
  calls,         \* the last admitted call: {} or one record
  refused,       \* a call has been refused
  records        \* activation records, by round (forensic floor, F5)

vars == <<domainTools, approvals, em, thinkerAllow, obsLive, calls, refused, records>>

Init ==
  /\ domainTools = {"t1"}
  /\ approvals = {}
  /\ em = NoEm
  /\ thinkerAllow = {"t1"}
  /\ obsLive = TRUE
  /\ calls = {}
  /\ refused = FALSE
  /\ records = {}

\* A promotion puts a tool in force. It does not reach a live round's envelope.
Promote(t) ==
  /\ t \in Domain \ domainTools
  /\ domainTools' = domainTools \cup {t}
  /\ UNCHANGED <<approvals, em, thinkerAllow, obsLive, calls, refused, records>>

Approve(r) ==
  /\ r \in Roster \ approvals
  /\ approvals' = approvals \cup {r}
  /\ UNCHANGED <<domainTools, em, thinkerAllow, obsLive, calls, refused, records>>

\* The roster's quorum seats a named holder for one round, on the domain's envelope as it
\* stands, and the activation is recorded.
Activate(h) ==
  /\ ~em.live /\ em.round < MaxRound
  /\ (Quorate(approvals) \/ Mut = "M_NOQUORUM")
  /\ h \in (IF Mut = "M_AGENT" THEN Holders ELSE Persons)
  /\ em' = [live |-> TRUE, round |-> em.round + 1, holder |-> h,
            envelope |-> domainTools \cup {"te"},
            quorate |-> Quorate(approvals), by |-> "roster", renewed |-> FALSE]
  /\ records' = records \cup {[round |-> em.round + 1, holder |-> h, approvers |-> approvals]}
  /\ approvals' = {}
  /\ UNCHANGED <<domainTools, thinkerAllow, obsLive, calls, refused>>

\* The lease ends: the round bound, its ttl, a revocation or a fence.
EndEm ==
  /\ em.live
  /\ em' = [em EXCEPT !.live = FALSE]
  /\ UNCHANGED <<domainTools, approvals, thinkerAllow, obsLive, calls, refused, records>>

\* Mutations only: an operator continues the emergency seat.
Regrant ==
  /\ Mut = "M_REGRANT"
  /\ ~em.live /\ em.round > 0 /\ em.round < MaxRound
  /\ em' = [em EXCEPT !.live = TRUE, !.round = @ + 1, !.quorate = FALSE, !.by = "operator"]
  /\ UNCHANGED <<domainTools, approvals, thinkerAllow, obsLive, calls, refused, records>>
Renew ==
  /\ Mut = "M_RENEW"
  /\ em.live
  /\ em' = [em EXCEPT !.renewed = TRUE]
  /\ UNCHANGED <<domainTools, approvals, thinkerAllow, obsLive, calls, refused, records>>

\* X1, where it is left in the floor: a quorum's approvals admit any tool for any seat.
X1 == Mut = "M_X1" /\ Quorate(approvals)

\* A call by the emergency seat. No Observer is asked for: R3 is over Thinkers.
EmCall(t) ==
  /\ em.live
  /\ IF t \in em.envelope \/ X1
       THEN /\ calls' = {[seat |-> "emergency", tool |-> t, allowlisted |-> t \in em.envelope,
                          observed |-> obsLive]}
            /\ UNCHANGED refused
       ELSE /\ refused' = TRUE
            /\ UNCHANGED calls
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, records>>

\* A call by the Thinker: its allowlist, and a live Observer (R3).
ThinkerCall(t) ==
  /\ IF (t \in thinkerAllow \/ X1) /\ (obsLive \/ Mut = "M_UNCOUPLE")
       THEN /\ calls' = {[seat |-> "thinker", tool |-> t, allowlisted |-> t \in thinkerAllow,
                          observed |-> obsLive]}
            /\ UNCHANGED refused
       ELSE /\ refused' = TRUE
            /\ UNCHANGED calls
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, records>>

\* The environment: the Observer fails or returns.
ObsToggle == obsLive' = ~obsLive
             /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, calls, refused, records>>

\* Mutation only: erasure removes an activation record.
Erase(x) ==
  /\ Mut = "M_ERASE"
  /\ x \in records
  /\ records' = records \ {x}
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, calls, refused>>

Next ==
  \/ \E t \in Domain : Promote(t)
  \/ \E r \in Roster : Approve(r)
  \/ \E h \in Holders : Activate(h)
  \/ EndEm \/ Regrant \/ Renew \/ ObsToggle
  \/ \E t \in Tools : EmCall(t) \/ ThinkerCall(t)
  \/ \E x \in records : Erase(x)

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

EmergencyLeaseHasARosterQuorum == em.live => em.quorate

EmergencyLeaseIsOneRound == em.round > 0 => (em.by = "roster" /\ ~em.renewed)

NoAgentHoldsAnEmergencySeat == em.live => em.holder \in Persons

CallsAreAllowlisted == \A c \in calls : c.allowlisted

ThinkerStillCoupled == \A c \in calls : c.seat = "thinker" => c.observed

ActivationIsForensic == \A n \in 1..em.round : \E x \in records : x.round = n

Safe == /\ EmergencyLeaseHasARosterQuorum /\ EmergencyLeaseIsOneRound /\ NoAgentHoldsAnEmergencySeat
        /\ CallsAreAllowlisted /\ ThinkerStillCoupled /\ ActivationIsForensic

\* --- reachability witnesses: each must be VIOLATED ---------------------------

\* The seat is activated, and a second time for a second round.
NeverActivated   == ~em.live
NeverSecondRound == em.round < 2
\* The emergency seat calls with no live Observer: it does not wait on one.
NeverUnobservedEmergencyCall == \A c \in calls : c.seat = "emergency" => c.observed
\* It calls the emergency-only tool, and a tool promoted since the last activation.
NeverEmergencyOnlyTool == \A c \in calls : c.tool # "te"
NeverNewToolInEnvelope == ~(em.live /\ "t2" \in em.envelope)
\* A promotion during a live round does not reach its envelope.
NeverStaleEnvelope == ~(em.live /\ "t2" \in domainTools /\ "t2" \notin em.envelope)
\* A call outside the envelope is refused, tx among them.
NeverRefused == ~refused
\* The Thinker is refused what the emergency seat may do: nothing elevates the agent.
NeverThinkerCall == \A c \in calls : c.seat # "thinker"
=============================================================================
