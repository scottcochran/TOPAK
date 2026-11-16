-------------------------------- MODULE Alone --------------------------------
(* A vehicle that stops hearing its plane: ADR-0062 (Proposed), §5 and §7, and *)
(* the invariants over ENABLED of its ratification condition (§11), with       *)
(* proposal §10 of derived/topak-federated-c2-design-proposal-2026.11.10b.md.  *)
(* One vehicle, one governor, one stack.                                       *)
(*                                                                             *)
(*   AlonePermitsNothing  a governor whose vehicle is alone permits nothing    *)
(*                        but the beacon, and the beacon within its count (§5) *)
(*   ExpiryGrantsNothing  after a lease ends no entry is permitted, and the    *)
(*                        only terminal act is hold or the seating's terminal  *)
(*                        behaviour, which the stack does not select (§7)      *)
(*   LocalNeverWaits      while a lease is live and its vehicle hears its      *)
(*                        plane, a `local` entry within its count can be       *)
(*                        permitted, whatever the plane's primary, any other   *)
(*                        vehicle or any Observer is doing (§11; ⟨21⟩)         *)
(*   TerminalNeverWaits   with a lease ended, the terminal behaviour is        *)
(*                        enabled whatever the stack does (proposal §10)       *)
(*                                                                             *)
(* LocalNeverWaits and TerminalNeverWaits are invariants over ENABLED, in the  *)
(* shape of Emergency_live.tla. Each holds in every state under its            *)
(* hypothesis, and what shows that it states the claim is the mutations that   *)
(* break it, which no other row sees.                                          *)
(*                                                                             *)
(* FINDING. Proposal §10 says of ExpiryGrantsNothing that after a lease ends   *)
(* "the only effects are hold and the seating's terminal behaviour". ADR-0062  *)
(* §5 keeps a beacon after the lease has ended, and ADR-0065 §2, with          *)
(* ADR-0015, counts a transmission as an effect. The two cannot both be read   *)
(* literally. This module states ExpiryGrantsNothing of entries and terminal   *)
(* acts, and bounds the beacon in AlonePermitsNothing, which is ADR-0062's own *)
(* reading: "It permits no actuation."                                         *)
(*                                                                             *)
(* What is abstracted. "Hears its plane" is the flag `hears`, and GoAlone is   *)
(* free: overdue is read off the governor's own clock, and PlaneClock.tla owns *)
(* that clock, with its residual. A stalled primary does stop the ticks, so    *)
(* it can make a vehicle alone, as ADR-0062 §2 says. It reaches the governor   *)
(* as GoAlone, and never as a wait on a permit, which is what LocalNeverWaits  *)
(* says. `alphabet` membership stands for everything static a permit reads:    *)
(* the envelope, the floor and the bundles: a refusal by those is a refusal    *)
(* and not a wait. A lease's count is the constant Count. One local entry l1   *)
(* and one ordered entry o1. An ordered entry waits for a round of the plane,  *)
(* which is the contrast LocalNeverWaits draws. EndLease stands for every      *)
(* ending in §7 but going alone and a fence: count and extent spent, `ttl`,    *)
(* and the plane's end or revocation. A relayed fence is applied while alone;  *)
(* what it fences on a chain is Federation.tla's. Hold while the lease stays   *)
(* live, when an extent ends (§4), is PlaneClock.tla's. Reports on peer        *)
(* topics are Peer.tla's. Reaching a safe state is physics, and is not here.   *)
(*                                                                             *)
(* Mut = "none":              ADR-0062 as drafted.                             *)
(* Mut = "M_ALONEACTS":       going alone does not end the lease, so the       *)
(*                            vehicle goes on permitting within its count.     *)
(*                            AlonePermitsNothing must fail. Proposal §10 has  *)
(*                            it permit one `local` entry; since a permit      *)
(*                            needs a live lease, the guard that stops it is   *)
(*                            the ending, and this removes that.               *)
(* Mut = "M_BEACONUNCOUNTED": the beacon's count is one higher than declared.  *)
(*                            AlonePermitsNothing must fail.                   *)
(* Mut = "M_STACKCHOOSES":    the stack selects the terminal act.              *)
(*                            ExpiryGrantsNothing must fail.                   *)
(* Mut = "M_ENTRYAFTEREND":   an entry is permitted under an ended lease.      *)
(*                            ExpiryGrantsNothing must fail, and so must       *)
(*                            AlonePermitsNothing, since going alone is one    *)
(*                            way a lease ends.                                *)
(* Mut = "M_WAITPRIMARY":     a `local` permit waits for the primary.          *)
(* Mut = "M_WAITPEER":        a `local` permit waits for another vehicle.      *)
(* Mut = "M_WAITOBSERVER":    a `local` permit waits for a live Observer,      *)
(*                            which is R3 kept mid-lease and ADR-0062 §8       *)
(*                            moves to the grant. Each of these three must     *)
(*                            break LocalNeverWaits and nothing else.          *)
(* Mut = "M_STACKGATED":      the terminal behaviour waits for the stack.      *)
(*                            TerminalNeverWaits must fail and nothing else.   *)
(*                                                                             *)
(* Deadlock is not checked: the environment's actions are always enabled.      *)
EXTENDS Naturals

CONSTANTS Mut, Count, MaxBeacon, MaxGrant, MaxFence, Seated

ASSUME SeatedBehaviour == Seated \in {"return", "land", "stop"}

LocalEntries   == {"l1"}
OrderedEntries == {"o1"}
Entries        == LocalEntries \cup OrderedEntries
Alphabets      == {{"l1"}, {"l1", "o1"}}
Behaviours     == {"hold", "return", "land", "stop"}

VARIABLES lstate, alphabet, used, beacons, hears, fence, grants,
          primary, peer, observer, stack,
          aloneActed, entryAfterEnd, wrongTerminal, recovered, seen

vars == <<lstate, alphabet, used, beacons, hears, fence, grants,
          primary, peer, observer, stack,
          aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>

Init ==
  /\ lstate = "none"
  /\ alphabet = {}
  /\ used = 0
  /\ beacons = 0
  /\ hears = TRUE
  /\ fence = 0
  /\ grants = 0
  /\ primary = "up"
  /\ peer = "up"
  /\ observer = "live"
  /\ stack = "ready"
  /\ aloneActed = FALSE
  /\ entryAfterEnd = FALSE
  /\ wrongTerminal = FALSE
  /\ recovered = "none"
  /\ seen = {}

\* The mechanism's guards, each open to one mutation.
PermitLive == lstate = "live" \/ (Mut = "M_ENTRYAFTEREND" /\ lstate = "ended")
LocalGate  == /\ (Mut # "M_WAITPRIMARY"  \/ primary = "up")
              /\ (Mut # "M_WAITPEER"     \/ peer = "up")
              /\ (Mut # "M_WAITOBSERVER" \/ observer = "live")
Gate(e)    == IF e \in LocalEntries THEN LocalGate ELSE primary = "up"
Ended(s)   == IF s = "live" THEN "ended" ELSE s
BeaconLimit == IF Mut = "M_BEACONUNCOUNTED" THEN MaxBeacon + 1 ELSE MaxBeacon
RecoverOK(b) == Mut = "M_STACKCHOOSES" \/ b \in {"hold", Seated}
RecoverGate  == Mut # "M_STACKGATED" \/ stack = "ready"
AfterGoAlone == IF Mut = "M_ALONEACTS" THEN lstate ELSE Ended(lstate)

\* The plane orders a lease: one round, charged to the budget, to a vehicle it hears. ⟨Q15⟩: a
\* vehicle that hears its plane again may be leased again.
Grant(a) ==
  /\ hears
  /\ lstate # "live"
  /\ primary = "up"
  /\ grants < MaxGrant
  /\ lstate' = "live"
  /\ alphabet' = a
  /\ used' = 0
  /\ beacons' = 0
  /\ grants' = grants + 1
  /\ seen' = seen \cup (IF "alone" \in seen THEN {"regrant"} ELSE {})
  /\ UNCHANGED <<hears, fence, primary, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered>>

\* The governor permits an entry, against its own count. Only the lease and the entry's own gate
\* are read: no round for a local entry.
Permit(e) ==
  /\ PermitLive
  /\ used < Count
  /\ e \in alphabet
  /\ Gate(e)
  /\ used' = used + 1
  /\ aloneActed' = (aloneActed \/ ~hears)
  /\ entryAfterEnd' = (entryAfterEnd \/ lstate # "live")
  /\ seen' = seen \cup {IF e \in LocalEntries THEN "local" ELSE "ordered"}
  /\ UNCHANGED <<lstate, alphabet, beacons, hears, fence, grants,
                 primary, peer, observer, stack, wrongTerminal, recovered>>

\* Count and extent spent, ttl, or the plane's end or revocation.
EndLease ==
  /\ lstate = "live"
  /\ lstate' = "ended"
  /\ UNCHANGED <<alphabet, used, beacons, hears, fence, grants,
                 primary, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>

\* The next tick is overdue by the governor's own clock: the vehicle is alone, and the lease ends where it stands.
GoAlone ==
  /\ hears
  /\ hears' = FALSE
  /\ lstate' = AfterGoAlone
  /\ seen' = seen \cup {"alone"}
  /\ UNCHANGED <<alphabet, used, beacons, fence, grants,
                 primary, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered>>

\* A tick heard again ends the state. It grants nothing.
HearAgain ==
  /\ ~hears
  /\ hears' = TRUE
  /\ UNCHANGED <<lstate, alphabet, used, beacons, fence, grants,
                 primary, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>

\* A relayed fence applies on receipt, heard or alone, and ends a live lease.
FenceRelay ==
  /\ fence < MaxFence
  /\ fence' = fence + 1
  /\ lstate' = Ended(lstate)
  /\ seen' = seen \cup (IF hears THEN {} ELSE {"fenceAlone"})
  /\ UNCHANGED <<alphabet, used, beacons, hears, grants,
                 primary, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered>>

\* A vehicle that is alone may send the beacon, counted per lease.
Beacon ==
  /\ ~hears
  /\ lstate # "none"
  /\ beacons < BeaconLimit
  /\ beacons' = beacons + 1
  /\ seen' = seen \cup {"beacon"}
  /\ UNCHANGED <<lstate, alphabet, used, hears, fence, grants,
                 primary, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered>>

\* The recovery function, in the governor's trust domain, carries out the seating's behaviour.
Recover(b) ==
  /\ lstate = "ended"
  /\ RecoverGate
  /\ RecoverOK(b)
  /\ recovered' = b
  /\ wrongTerminal' = (wrongTerminal \/ b \notin {"hold", Seated})
  /\ seen' = seen \cup {"recover"}
  /\ UNCHANGED <<lstate, alphabet, used, beacons, hears, fence, grants,
                 primary, peer, observer, stack,
                 aloneActed, entryAfterEnd>>

\* The rest of the world, which no governor guard reads except under a mutation.
MovePrimary ==
  /\ primary' = IF primary = "up" THEN "down" ELSE "up"
  /\ UNCHANGED <<lstate, alphabet, used, beacons, hears, fence, grants, peer, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>
MovePeer ==
  /\ peer' = IF peer = "up" THEN "down" ELSE "up"
  /\ UNCHANGED <<lstate, alphabet, used, beacons, hears, fence, grants, primary, observer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>
MoveObserver ==
  /\ observer' = IF observer = "live" THEN "stale" ELSE "live"
  /\ UNCHANGED <<lstate, alphabet, used, beacons, hears, fence, grants, primary, peer, stack,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>
MoveStack ==
  /\ stack' = IF stack = "ready" THEN "wedged" ELSE "ready"
  /\ UNCHANGED <<lstate, alphabet, used, beacons, hears, fence, grants, primary, peer, observer,
                 aloneActed, entryAfterEnd, wrongTerminal, recovered, seen>>

Next ==
  \/ \E a \in Alphabets : Grant(a)
  \/ \E e \in Entries : Permit(e)
  \/ EndLease \/ GoAlone \/ HearAgain \/ FenceRelay \/ Beacon
  \/ \E b \in Behaviours : Recover(b)
  \/ MovePrimary \/ MovePeer \/ MoveObserver \/ MoveStack

Spec == Init /\ [][Next]_vars

\* --- the four properties ------------------------------------------------------

BeaconWithin        == beacons <= MaxBeacon
AlonePermitsNothing == ~aloneActed /\ BeaconWithin
ExpiryGrantsNothing == ~entryAfterEnd /\ ~wrongTerminal

LocalNeverWaits ==
  (lstate = "live" /\ hears /\ used < Count /\ "l1" \in alphabet) => ENABLED Permit("l1")

TerminalNeverWaits == lstate = "ended" => ENABLED Recover(Seated)

Safe == AlonePermitsNothing /\ ExpiryGrantsNothing /\ LocalNeverWaits /\ TerminalNeverWaits

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverLocalPermitted   == "local" \notin seen
NeverOrderedPermitted == "ordered" \notin seen
NeverAlone            == "alone" \notin seen
NeverEndedByAlone     == ~(lstate = "ended" /\ ~hears)
NeverBeacon           == "beacon" \notin seen
NeverRecovered        == "recover" \notin seen
NeverFenceWhileAlone  == "fenceAlone" \notin seen
NeverLeasedAfterAlone == "regrant" \notin seen
\* A permit that waits: an ordered entry does wait on the primary, so LocalNeverWaits draws a distinction.
NeverOrderedWaits ==
  ~(lstate = "live" /\ hears /\ used < Count /\ "o1" \in alphabet /\ ~ENABLED Permit("o1"))
=============================================================================
