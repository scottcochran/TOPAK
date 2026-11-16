------------------------------- MODULE Release -------------------------------
(* An irreversible effect is a person's: ADR-0066 (Proposed), its              *)
(* ratification condition (§7), proposal §10 of                                *)
(* derived/topak-federated-c2-design-proposal-2026.11.10b.md, and ADR-0062 §6  *)
(* for what cannot be void. A person at a `release` seat composes and signs an *)
(* act; it is ordered at the commanded plane, relayed by the autonomous plane, *)
(* which can refuse one and cannot originate one, and fired by a governor's    *)
(* interlock, which checks the key, the commanded certificate, that the act    *)
(* names this vehicle, that it is unused, and that it is fresh.                *)
(*                                                                             *)
(* One commanded plane, one autonomous plane, two vehicles, one person, one    *)
(* agent, and one irreversible entry. Ticks are plain numbers in the log and   *)
(* are not a clock (PlaneClock.tla owns time); freshness is a comparison of    *)
(* tick numbers. `Ids` number the acts, and an act is written once.            *)
(*                                                                             *)
(*   SignedByPerson        every irreversible effect has a person's key on it  *)
(*   OrderedAtCommand      ... and was ordered at a commanded plane (§4)       *)
(*   UsedOnce              an act produces at most one effect, anywhere (§4)   *)
(*   NoOlderThanDeclared   an effect is no more than FreshT ticks past the     *)
(*                         tick its act names (§4)                             *)
(*   IrreversibleIsAPersons the conjunction of those four (§7)                 *)
(*   ConflictIsAFinding    a check failing at a seal or above subtracts, and   *)
(*                         voids nothing a governor permitted (ADR-0062 §6)    *)
(*   OrderedInContact      an act is admitted only in contact with the intent  *)
(*                         boundary (§4)                                       *)
(*   ReleaseNeverCoupled   while the seat is live and the plane is in contact, *)
(*                         a release can be admitted, whatever any agent or    *)
(*                         Observer is doing (§7, in the shape of              *)
(*                         Emergency_live.tla)                                 *)
(*                                                                             *)
(* The interlock is the only check this module relies on. An agent's signed   *)
(* act may be ordered at the commanded plane (AdmitAgent) and the autonomous  *)
(* plane may originate any act (LiteOriginate). The floor's refusals of those *)
(* (FD5, FD6 and FD9, ADR-0067) are a second check in series that is not       *)
(* assumed here, so every property that holds rests on the interlock alone.    *)
(* A person's key and a commanded plane's certificate are taken as             *)
(* unforgeable. The mechanism "cannot tell a person from a program holding the *)
(* person's key" (ToO §3.3), and nothing here can either.                      *)
(*                                                                             *)
(* THREE FINDINGS AGAINST ADR-0066.                                            *)
(* 1. §4's list of what the interlock checks omits that the act names this    *)
(*    vehicle, though the act names one. Without that check, one act fires    *)
(*    once on each vehicle, since `unused` is each governor's own record.     *)
(*    The check is modelled, and M_ANYVEHICLE removes it. UsedOnce must fail.  *)
(* 2. "With no link there is no irreversible effect" is true of the order and *)
(*    not of the effect. An act that crossed the link before it was cut is    *)
(*    still delivered and still fires inside FreshT, and a governor has no    *)
(*    way to know the link is cut (witness NeverFiredAfterCut, VIOLATED). What *)
(*    bounds it is freshness. OrderedInContact is what §4 can claim.          *)
(* 3. "An act an adversary withholds arrives aged" is measured in the plane's  *)
(*    ticks, and a captured plane can stop ticking. NoOlderThanDeclared is     *)
(*    therefore a statement about ticks and says nothing of duration. Duration *)
(*    is the watchdog's, ADR-0064 §5, and PlaneClock.tla's.                    *)
(*                                                                             *)
(* What is abstracted. An act's entry, inputs and envelope: the floor's        *)
(* business. The roster's quorum that activates the seat: Emergency.tla's      *)
(* shape, here one action. An act names the latest tick the commanded plane    *)
(* knows; naming an older one only ages it sooner. A void before the effect,   *)
(* which ADR-0062 §6 allows of an ordered entry, is not modelled: every check  *)
(* here fails after the effect. Whether the act was right is the person's      *)
(* judgment, §5, and nothing checks it.                                        *)
(*                                                                             *)
(* Mut = "none":             ADR-0066 as drafted.                              *)
(* Mut = "M_AGENTRELEASE":   the interlock does not check the person's key.    *)
(*                           SignedByPerson must fail.                         *)
(* Mut = "M_LITERELEASE":    the interlock accepts the autonomous plane's      *)
(*                           certificate. OrderedAtCommand must fail.          *)
(* Mut = "M_REPLAY":         the interlock does not check that the act is      *)
(*                           unused. UsedOnce must fail.                       *)
(* Mut = "M_ANYVEHICLE":     the interlock does not check the act's vehicle.   *)
(*                           UsedOnce must fail.                               *)
(* Mut = "M_LATEFIRST":      a first delivery after the ticks have run is      *)
(*                           accepted, as an interval from receipt would be.   *)
(*                           NoOlderThanDeclared must fail.                    *)
(* Mut = "M_VOID":           a failed check voids an effect that happened.     *)
(*                           ConflictIsAFinding must fail.                     *)
(* Mut = "M_NOCONTACT":      a release is admitted with no link.               *)
(*                           OrderedInContact must fail.                       *)
(* Mut = "M_OBSCOUPLE":      a release waits for a live Observer.              *)
(*                           ReleaseNeverCoupled must fail.                    *)
(* Mut = "M_AGENTPROPOSES":  a release waits for an agent's proposal, the      *)
(*                           design §3 rejects. ReleaseNeverCoupled must fail. *)
(*                                                                             *)
(* Deadlock is not checked: a release that is never used is safe.              *)
EXTENDS Naturals

CONSTANTS Mut, MaxActs, MaxTick, FreshT

Ids      == 1..MaxActs
Vehicles == {"v1", "v2"}
Signers  == {"person", "agent"}

NoAct == [signer |-> "none", plane |-> "none", tick |-> 0, vehicle |-> "none"]

VARIABLES relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
          used, firedIds, standing, findings,
          notPerson, notCommanded, replayed, stale, noContact, seen
vars == <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
          used, firedIds, standing, findings,
          notPerson, notCommanded, replayed, stale, noContact, seen>>

Act(s, pl, v) == [signer |-> s, plane |-> pl, tick |-> tick, vehicle |-> v]

Init ==
  /\ relLive = FALSE
  /\ contact = TRUE
  /\ tick = 0
  /\ obsLive = FALSE
  /\ agentBusy = FALSE
  /\ nextId = 1
  /\ acts = [i \in Ids |-> NoAct]
  /\ delivered = {}
  /\ relayRefused = {}
  /\ used = [v \in Vehicles |-> {}]
  /\ firedIds = {}
  /\ standing = {}
  /\ findings = {}
  /\ notPerson = FALSE
  /\ notCommanded = FALSE
  /\ replayed = FALSE
  /\ stale = FALSE
  /\ noContact = FALSE
  /\ seen = {}

\* The interlock's five checks, each open to one mutation.
KeyOK(id)         == Mut = "M_AGENTRELEASE" \/ acts[id].signer = "person"
CertOK(id)        == Mut = "M_LITERELEASE" \/ acts[id].plane = "cmd"
VehicleOK(v, id)  == Mut = "M_ANYVEHICLE" \/ acts[id].vehicle = v
UnusedOK(v, id)   == Mut = "M_REPLAY" \/ id \notin used[v]
FreshOK(id)       == Mut = "M_LATEFIRST" \/ tick <= acts[id].tick + FreshT

Interlock(v, id) == KeyOK(id) /\ CertOK(id) /\ VehicleOK(v, id) /\ UnusedOK(v, id) /\ FreshOK(id)

\* The guards on a release admit: open to the mutations that couple it.
LinkOK      == Mut = "M_NOCONTACT" \/ contact
Uncoupled   == (Mut # "M_OBSCOUPLE" \/ obsLive) /\ (Mut # "M_AGENTPROPOSES" \/ agentBusy)

\* The seat is activated and ended; the link, an Observer and an agent come and go.
Activate    == ~relLive /\ relLive' = TRUE
               /\ UNCHANGED <<contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                              used, firedIds, standing, findings,
                              notPerson, notCommanded, replayed, stale, noContact, seen>>
EndRelease  == relLive /\ relLive' = FALSE
               /\ UNCHANGED <<contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                              used, firedIds, standing, findings,
                              notPerson, notCommanded, replayed, stale, noContact, seen>>
LinkToggle  == contact' = ~contact
               /\ UNCHANGED <<relLive, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                              used, firedIds, standing, findings,
                              notPerson, notCommanded, replayed, stale, noContact, seen>>
ObsToggle   == obsLive' = ~obsLive
               /\ UNCHANGED <<relLive, contact, tick, agentBusy, nextId, acts, delivered, relayRefused,
                              used, firedIds, standing, findings,
                              notPerson, notCommanded, replayed, stale, noContact, seen>>
AgentToggle == agentBusy' = ~agentBusy
               /\ UNCHANGED <<relLive, contact, tick, obsLive, nextId, acts, delivered, relayRefused,
                              used, firedIds, standing, findings,
                              notPerson, notCommanded, replayed, stale, noContact, seen>>
Advance     == tick < MaxTick /\ tick' = tick + 1
               /\ UNCHANGED <<relLive, contact, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                              used, firedIds, standing, findings,
                              notPerson, notCommanded, replayed, stale, noContact, seen>>

\* A person at a live release seat signs an act, ordered at the commanded plane. No guard
\* reads an agent or an Observer but the two mutations; no bound but the module's own.
AdmitRelease ==
  /\ relLive
  /\ LinkOK
  /\ Uncoupled
  /\ nextId <= MaxActs
  /\ \E v \in Vehicles : acts' = [acts EXCEPT ![nextId] = Act("person", "cmd", v)]
  /\ nextId' = nextId + 1
  /\ noContact' = (noContact \/ ~contact)
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, delivered, relayRefused,
                 used, firedIds, standing, findings,
                 notPerson, notCommanded, replayed, stale, seen>>

\* An agent's signature on an act, ordered at the commanded plane. The floor would refuse
\* it (FD5 to FD9); this module does not assume so.
AdmitAgent ==
  /\ nextId <= MaxActs
  /\ \E v \in Vehicles : acts' = [acts EXCEPT ![nextId] = Act("agent", "cmd", v)]
  /\ nextId' = nextId + 1
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, delivered, relayRefused,
                 used, firedIds, standing, findings,
                 notPerson, notCommanded, replayed, stale, noContact, seen>>

\* A captured autonomous plane originates an act over any signature it holds. It needs no
\* relay, since it is the relay.
LiteOriginate(s) ==
  /\ nextId <= MaxActs
  /\ \E v \in Vehicles : acts' = [acts EXCEPT ![nextId] = Act(s, "lite", v)]
  /\ delivered' = delivered \cup {nextId}
  /\ nextId' = nextId + 1
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, relayRefused,
                 used, firedIds, standing, findings,
                 notPerson, notCommanded, replayed, stale, noContact, seen>>

\* The autonomous plane relays an act the commanded plane ordered, over the link ...
Relay(id) ==
  /\ acts[id] # NoAct
  /\ acts[id].plane = "cmd"
  /\ id \notin delivered
  /\ id \notin relayRefused
  /\ contact
  /\ delivered' = delivered \cup {id}
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, relayRefused,
                 used, firedIds, standing, findings,
                 notPerson, notCommanded, replayed, stale, noContact, seen>>

\* ... or refuses it.
RelayRefuse(id) ==
  /\ acts[id] # NoAct
  /\ acts[id].plane = "cmd"
  /\ id \notin delivered
  /\ id \notin relayRefused
  /\ relayRefused' = relayRefused \cup {id}
  /\ seen' = seen \cup {"relayRefuse"}
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered,
                 used, firedIds, standing, findings,
                 notPerson, notCommanded, replayed, stale, noContact>>

\* A governor fires a delivered act. Each flag is computed from what is true of the act,
\* and none from what the guard read.
Fire(v, id) ==
  /\ id \in delivered
  /\ Interlock(v, id)
  /\ notPerson'    = (notPerson \/ acts[id].signer # "person")
  /\ notCommanded' = (notCommanded \/ acts[id].plane # "cmd")
  /\ replayed'     = (replayed \/ id \in firedIds)
  /\ stale'        = (stale \/ tick > acts[id].tick + FreshT)
  /\ used'     = [used EXCEPT ![v] = used[v] \cup {id}]
  /\ firedIds' = firedIds \cup {id}
  /\ standing' = standing \cup {id}
  /\ seen' = seen \cup {"fired"} \cup (IF contact THEN {} ELSE {"afterCut"})
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                 findings, noContact>>

\* A governor refuses one, and says for which check.
RefuseAct(v, id) ==
  /\ id \in delivered
  /\ ~Interlock(v, id)
  /\ seen' = seen \cup (IF KeyOK(id) THEN {} ELSE {"refKey"})
                  \cup (IF CertOK(id) THEN {} ELSE {"refCert"})
                  \cup (IF VehicleOK(v, id) THEN {} ELSE {"refVehicle"})
                  \cup (IF UnusedOK(v, id) THEN {} ELSE {"refReplay"})
                  \cup (IF FreshOK(id) THEN {} ELSE {"refAged"})
  /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                 used, firedIds, standing, findings,
                 notPerson, notCommanded, replayed, stale, noContact>>

\* A check fails at a seal or above, against an effect that has happened: a finding, and
\* it ends the seat. Under M_VOID it also voids the effect.
CheckFails(id) ==
  /\ id \in firedIds
  /\ id \notin findings
  /\ findings' = findings \cup {id}
  /\ relLive' = FALSE
  /\ standing' = IF Mut = "M_VOID" THEN standing \ {id} ELSE standing
  /\ seen' = seen \cup {"finding"} \cup (IF relLive THEN {"subtract"} ELSE {})
  /\ UNCHANGED <<contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                 used, firedIds, notPerson, notCommanded, replayed, stale, noContact>>

Next ==
  \/ Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance
  \/ AdmitRelease \/ AdmitAgent
  \/ \E s \in Signers : LiteOriginate(s)
  \/ \E id \in Ids : Relay(id) \/ RelayRefuse(id) \/ CheckFails(id)
  \/ \E v \in Vehicles, id \in Ids : Fire(v, id) \/ RefuseAct(v, id)

Spec == Init /\ [][Next]_vars

\* --- the properties -----------------------------------------------------------

SignedByPerson      == ~notPerson
OrderedAtCommand    == ~notCommanded
UsedOnce            == ~replayed
NoOlderThanDeclared == ~stale

IrreversibleIsAPersons ==
  SignedByPerson /\ OrderedAtCommand /\ UsedOnce /\ NoOlderThanDeclared

ConflictIsAFinding == firedIds \subseteq standing
OrderedInContact   == ~noContact

Safe == IrreversibleIsAPersons /\ ConflictIsAFinding /\ OrderedInContact

\* --- the availability invariant, over ENABLED ---------------------------------

\* The module's bound on acts is in the hypothesis, as a bound and not as a claim.
ReleaseNeverCoupled == (relLive /\ contact /\ nextId <= MaxActs) => ENABLED AdmitRelease

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverFired         == "fired" \notin seen
NeverFiredAfterCut == "afterCut" \notin seen
NeverRefusedKey    == "refKey" \notin seen
NeverRefusedCert   == "refCert" \notin seen
NeverRefusedVehicle == "refVehicle" \notin seen
NeverRefusedReplay == "refReplay" \notin seen
NeverRefusedAged   == "refAged" \notin seen
NeverRelayRefused  == "relayRefuse" \notin seen
NeverFinding       == "finding" \notin seen
NeverSubtraction   == "subtract" \notin seen
=============================================================================
