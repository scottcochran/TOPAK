--------------------------- MODULE Emergency_live ---------------------------
(* ADR-0039 A2 as an availability invariant. "A person seated by the           *)
(* break-glass roster's quorum for one round does not wait on an Observer."    *)
(* Emergency.tla shows this as a behaviour, its witness w3: some run admits an *)
(* emergency call with no live Observer. A witness says the call happens in    *)
(* one run. The claim is that once the seat is live, nothing the Observer does *)
(* can stop its calls, in any state. Like ConsultNeverCoupled (RunCoupling),   *)
(* LagNeverGates (Correlator) and DenyAlwaysAvailable (Operators), it is       *)
(* stated as an invariant over ENABLED:                                        *)
(*                                                                             *)
(*   EmergencyNeverCoupled          while the seat is live, a call of any tool *)
(*                                  in its envelope can be admitted, whatever  *)
(*                                  the Observer's state                       *)
(*   EmergencyCallsWithoutObserver  while the seat is live and the Observer is *)
(*                                  not, some emergency call can be admitted:  *)
(*                                  the envelope is never empty, since it      *)
(*                                  holds te (ADR-0052 R1) and, in this model, *)
(*                                  t1, which is in force from Init on and is  *)
(*                                  in every envelope (EnvelopeHasT1)          *)
(*                                                                             *)
(* Under its hypothesis EmergencyNeverCoupled holds in every state, reachable  *)
(* or not: EmAdmit's guard does not read the Observer. What shows that it      *)
(* states A2 is the pair of mutations below, which break it, with NextL being  *)
(* Emergency's Next under every other Mut. Neither property rests on te alone, *)
(* since t1 keeps the envelope non-empty without it; that te itself can be     *)
(* called is Emergency.tla's witness NeverEmergencyOnlyTool. Both are about    *)
(* the calls of a live seat, which is A2's scope, and not about the seating:   *)
(* an activation that waited for a live Observer would pass every check here.  *)
(*                                                                             *)
(* Emergency.tla is cited by digest and not edited; this module extends it.    *)
(* Its Next is Emergency's with the emergency call split into its two          *)
(* outcomes, the admit and the refusal, so that ENABLED can be asked of the    *)
(* admit. Under every Mut of Emergency.tla the two together are EmCall         *)
(* exactly, so NextL is Emergency's Next and the state graph is the same.      *)
(*                                                                             *)
(* Mut = "M_EMCOUPLE":  R3 extended to the emergency seat: its calls need a    *)
(*                      live Observer, as a Thinker's do. Every invariant of   *)
(*                      Emergency.tla holds. The witness w3 is no longer       *)
(*                      reached, so TLC's witness run catches this one too.    *)
(*                      Must break both properties.                            *)
(* Mut = "M_EMCOUPLE2": the same from the seat's second round on: a re-seated  *)
(*                      emergency seat waits for an Observer. Every invariant  *)
(*                      holds, and w3 is still reached, in round one. Must     *)
(*                      break both properties, which are the only check that   *)
(*                      catches it.                                            *)
EXTENDS Emergency

\* Under this module's two mutations, an emergency call is coupled.
EmCoupled == \/ Mut = "M_EMCOUPLE"
             \/ (Mut = "M_EMCOUPLE2" /\ em.round >= 2)

\* EmCall(t)'s two outcomes, open to the coupling: the admit ...
EmAdmit(t) ==
  /\ em.live
  /\ (t \in em.envelope \/ X1)
  /\ (obsLive \/ ~EmCoupled)
  /\ calls' = {[seat |-> "emergency", tool |-> t, allowlisted |-> t \in em.envelope,
                observed |-> obsLive]}
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, refused, records>>

\* ... and the refusal.
EmRefuse(t) ==
  /\ em.live
  /\ ~((t \in em.envelope \/ X1) /\ (obsLive \/ ~EmCoupled))
  /\ refused' = TRUE
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, calls, records>>

NextL ==
  \/ \E t \in Domain : Promote(t)
  \/ \E r \in Roster : Approve(r)
  \/ \E h \in Holders : Activate(h)
  \/ EndEm \/ Regrant \/ Renew \/ ObsToggle
  \/ \E t \in Tools : EmAdmit(t) \/ EmRefuse(t) \/ ThinkerCall(t)
  \/ \E x \in records : Erase(x)

SpecL == Init /\ [][NextL]_vars

\* --- the two properties -----------------------------------------------------

EmergencyNeverCoupled == \A t \in Tools : (em.live /\ t \in em.envelope) => ENABLED EmAdmit(t)

EmergencyCallsWithoutObserver == (em.live /\ ~obsLive) => \E t \in Tools : ENABLED EmAdmit(t)

\* --- a check of the header's reading: an invariant that must hold -------------

\* t1 is in every envelope the seat has had: Init puts it in force, no action takes a tool
\* out of force, and Activate's envelope is the tools in force with te.
EnvelopeHasT1 == em.round > 0 => "t1" \in em.envelope
=============================================================================
