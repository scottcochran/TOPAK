---------------------------- MODULE Confinement ----------------------------
(* Properties for ADR-0034, attested confinement: the discharge of ADR-0022 §6. *)
(*                                                                             *)
(*   ContainedMeansConfined §4  an effect counted Contained was taken inside    *)
(*                              the archetype profile, not merely attested so   *)
(*   NoSilentDowngrade      §3  no grant below the deployment's declared rung   *)
(*   ContestedStopped       §3  a Contested principal is revoked, never granted *)
(*   FreshAppraisal         §3  no lease rests on an appraisal from a fenced    *)
(*                              epoch                                           *)
(*                                                                             *)
(* Renewal re-attests (§3.6) and keeps the rung (ADR-0031 A1, pending). An     *)
(* Attested re-appraisal renews at the declared rung; an Unattestable one lets *)
(* the lease lapse; a Contested one revokes. NoSilentDowngrade now covers the  *)
(* renewal path as well as the grant.                                          *)
(*                                                                             *)
(* Evidence is the launch measurement (`boot`), not the running image: rungs 2 *)
(* and 3 measure what was launched, and neither detects a running guest being  *)
(* altered (§2, §5). The first run, before renewal existed, read the running   *)
(* image; the two agree at every first appraisal the unmutated model reaches.  *)
(*                                                                             *)
(* The deployment declares one confinement rung, `Declared` (ADR-0031 §3). The *)
(* host launches guests and may misbehave wherever the declared rung does not  *)
(* trust it:                                                                   *)
(*   rung 1  launcher asserts the profile.  Host trusted at launch and after.   *)
(*   rung 2  measured boot, appraised by the mechanism. Host may launch a rogue *)
(*           image; the hypervisor is trusted not to alter a running guest.     *)
(*   rung 3  confidential VM, independent verifier. Host trusted for nothing;   *)
(*           the hardware turns an attempt to alter a running guest into the    *)
(*           guest's death (the audited-row assumption, §6).                    *)
(*                                                                             *)
(* Profiles. "arch" is the archetype profile (§1, §4: possessed Persona        *)
(* inference inside the guest, every tool a Wasm component). "med" is any      *)
(* promoted profile that is not: a native tool or an external Persona. Both    *)
(* are promoted Build artifacts. "rogue" is an image nobody promoted.          *)
(*                                                                             *)
(* Mut = "none":        the mechanism as ADR-0034 specifies it.                 *)
(* Mut = "M_HOST":      the host is untrusted where the rung trusts it. Must    *)
(*                      fail at rungs 1 and 2, and change nothing at rung 3.    *)
(* Mut = "M_HW":        at rung 3 the hardware does not protect a running guest.*)
(* Mut = "M_CONTESTED": a Contested verdict is treated as Attested.             *)
(* Mut = "M_UNBOUND":   the lease is not bound to the attested guest instance.  *)
(* Mut = "M_STALE":     an appraisal survives an epoch fence.                   *)
(* Mut = "M_DOWNGRADE": an unattestable principal is granted at rung 0.         *)
(* Mut = "M_PROFILE":   Contained ignores the profile.                          *)
(* Mut = "M_RENEWLOW":  an Unattestable renewal is renewed at rung 0 instead of *)
(*                      lapsing: the frozen ADR-0031 §4 rule, which let a       *)
(*                      renewal lower the rung.                                 *)
EXTENDS FiniteSets, Naturals

CONSTANTS Mut, Declared, MaxEpoch, MaxIdx, MaxGen

Principals == {"p1", "p2"}
Promoted   == {"arch", "med"}
Arch       == "arch"

NoGuest   == [img |-> "none", asked |-> "none", boot |-> "none", gen |-> 0]
NoPending == [v |-> "none", prof |-> "none", nEpoch |-> 0, gen |-> 0]
NoLease   == [live |-> FALSE, rung |-> 0, prof |-> "none", epoch |-> 0, nEpoch |-> 0, gen |-> 0]

VARIABLES guest, gens, pending, lease, epoch, idx, revoked, verifierUp,
          acted, contested, refused, tamperKilled, renewOut
vars == <<guest, gens, pending, lease, epoch, idx, revoked, verifierUp,
          acted, contested, refused, tamperKilled, renewOut>>

Init == /\ guest   = [p \in Principals |-> NoGuest]
        /\ gens    = [p \in Principals |-> 0]
        /\ pending = [p \in Principals |-> NoPending]
        /\ lease   = [p \in Principals |-> NoLease]
        /\ epoch = 0
        /\ idx = 0
        /\ revoked = {}
        /\ verifierUp = TRUE
        /\ acted = {}
        /\ contested = {}
        /\ refused = FALSE
        /\ tamperKilled = FALSE
        /\ renewOut = {}

\* --- the host ---------------------------------------------------------------

\* Rung 1 trusts the launcher; rungs 2 and 3 do not.
HostMayLaunchRogue == Declared >= 2 \/ Mut = "M_HOST"

\* The orchestrator is asked for a promoted profile and launches a guest. A new
\* guest is a new instance: `gen` is the key its session is bound to (§3).
\* `boot` is what was launched, and is what a measurement reports.
Launch(p) ==
  /\ guest[p].img = "none"
  /\ gens[p] < MaxGen
  /\ \E asked \in Promoted :
       \E img \in (IF HostMayLaunchRogue THEN {asked, "rogue"} ELSE {asked}) :
         guest' = [guest EXCEPT ![p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]]
  /\ gens' = [gens EXCEPT ![p] = @ + 1]
  /\ UNCHANGED <<pending, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>

\* The host kills a guest. The mechanism is not told: its lease stays live until
\* the round ends, but no session reaches it (Act checks the binding).
Kill(p) ==
  /\ guest[p].img # "none"
  /\ guest' = [guest EXCEPT ![p] = NoGuest]
  /\ UNCHANGED <<gens, pending, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>

\* The host tries to alter a running guest.
\*   rungs 1, 2: the host (rung 1) or hypervisor (rung 2) is trusted not to;
\*               M_HOST lets it, and it succeeds.
\*   rung 3:     the hardware's integrity protection turns the attempt into the
\*               guest's death; M_HW removes that protection.
Tamper(p) ==
  /\ guest[p].img \notin {"none", "rogue"}
  /\ \/ /\ Declared <= 2 /\ Mut = "M_HOST"
        /\ guest' = [guest EXCEPT ![p].img = "rogue"]
        /\ UNCHANGED tamperKilled
     \/ /\ Declared = 3 /\ Mut = "M_HW"
        /\ guest' = [guest EXCEPT ![p].img = "rogue"]
        /\ UNCHANGED tamperKilled
     \/ /\ Declared = 3 /\ Mut # "M_HW"
        /\ guest' = [guest EXCEPT ![p] = NoGuest]
        /\ tamperKilled' = TRUE
  /\ UNCHANGED <<gens, pending, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, renewOut>>

\* The independent verifier exists only at rung 3, and may be unreachable.
VerifierFlip ==
  /\ Declared = 3
  /\ verifierUp' = ~verifierUp
  /\ UNCHANGED <<guest, gens, pending, lease, epoch, idx, revoked, acted, contested, refused, tamperKilled, renewOut>>

\* --- the mechanism ----------------------------------------------------------

\* The evidence says which image was launched. At rung 1 the launcher asserts the
\* profile it was asked for; at rungs 2 and 3 the measurement is the launched
\* image. A running guest altered after launch still measures as launched.
Evidence(p) == IF Declared = 1 THEN guest[p].asked ELSE guest[p].boot

Verdict(p) ==
  IF Declared = 3 /\ ~verifierUp THEN "Unattestable"
  ELSE IF Evidence(p) = guest[p].asked THEN "Attested"
  ELSE "Contested"

\* ADR-0034 §3. Appraisal precedes the grant; its nonce is the epoch and log
\* position it was taken at, and it names the guest instance it measured.
\* A Contested verdict is evidence of discrepancy: the mechanism orders a
\* targeted revocation of the principal at once (ADR-0031 §5).
Appraise(p) ==
  /\ guest[p].img # "none"
  /\ ~lease[p].live
  /\ p \notin revoked
  /\ pending[p].v = "none"
  /\ LET v == Verdict(p) IN
     IF v = "Contested" /\ Mut # "M_CONTESTED"
     THEN /\ idx < MaxIdx
          /\ idx' = idx + 1
          /\ revoked' = revoked \cup {p}
          /\ contested' = contested \cup {p}
          /\ UNCHANGED <<pending, refused>>
     ELSE IF v = "Unattestable" /\ Mut # "M_DOWNGRADE"
     THEN /\ refused' = TRUE
          /\ UNCHANGED <<pending, idx, revoked, contested>>
     ELSE /\ pending' = [pending EXCEPT ![p] =
                          [v |-> IF v = "Contested" THEN "Attested" ELSE v,
                           prof |-> guest[p].asked, nEpoch |-> epoch, gen |-> guest[p].gen]]
          /\ contested' = IF v = "Contested" THEN contested \cup {p} ELSE contested
          /\ UNCHANGED <<idx, revoked, refused>>
  /\ UNCHANGED <<guest, gens, lease, epoch, verifierUp, acted, tamperKilled, renewOut>>

\* A pending appraisal may always be discarded.
Discard(p) ==
  /\ pending[p].v # "none"
  /\ pending' = [pending EXCEPT ![p] = NoPending]
  /\ UNCHANGED <<guest, gens, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>

FreshEpoch(p) == Mut = "M_STALE"   \/ pending[p].nEpoch = epoch
SameGuest(p)  == Mut = "M_UNBOUND" \/ pending[p].gen = guest[p].gen

\* The grant: consensus-ordered, at the declared rung, only on a fresh Attested
\* verdict about the guest now holding the session. Under M_DOWNGRADE an
\* Unattestable verdict is granted at rung 0 instead of refused.
Grant(p) ==
  /\ pending[p].v \in {"Attested", "Unattestable"}
  /\ ~lease[p].live
  /\ p \notin revoked
  /\ idx < MaxIdx
  /\ FreshEpoch(p)
  /\ SameGuest(p)
  /\ lease' = [lease EXCEPT ![p] =
                 [live |-> TRUE,
                  rung |-> IF pending[p].v = "Attested" THEN Declared ELSE 0,
                  prof |-> pending[p].prof, epoch |-> epoch,
                  nEpoch |-> pending[p].nEpoch, gen |-> pending[p].gen]]
  /\ pending' = [pending EXCEPT ![p] = NoPending]
  /\ idx' = idx + 1
  /\ UNCHANGED <<guest, gens, epoch, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>

\* ADR-0034 §4. Membership: a live lease at rung >= 1 on an Attested verdict,
\* for the archetype profile. M_PROFILE drops the profile conjunct.
Contained(p) ==
  /\ lease[p].live
  /\ lease[p].rung >= 1
  /\ (Mut = "M_PROFILE" \/ lease[p].prof = Arch)

\* An admitted effect. The session must be the attested guest's (M_UNBOUND
\* drops the check). The record keeps what was really running.
Act(p) ==
  /\ lease[p].live
  /\ lease[p].epoch = epoch
  /\ guest[p].img # "none"
  /\ (Mut = "M_UNBOUND" \/ lease[p].gen = guest[p].gen)
  /\ acted' = acted \cup {[principal |-> p, contained |-> Contained(p), img |-> guest[p].img]}
  /\ UNCHANGED <<guest, gens, pending, lease, epoch, idx, revoked, verifierUp, contested, refused, tamperKilled, renewOut>>

\* ADR-0034 §3.6 with ADR-0031 A1. A renewal comes from the bound guest and
\* re-attests with a fresh nonce. Attested: renewed at the same rung, which is
\* the declared rung. Unattestable: not renewed, and the lease lapses, a local
\* subtraction that is then ordered (ADR-0031 E1). Contested: a targeted
\* revocation, as at grant. Under M_RENEWLOW an Unattestable renewal is renewed
\* at rung 0 instead.
Renew(p) ==
  /\ lease[p].live
  /\ lease[p].epoch = epoch
  /\ guest[p].img # "none"
  /\ lease[p].gen = guest[p].gen
  /\ idx < MaxIdx
  /\ idx' = idx + 1
  /\ LET v == Verdict(p) IN
     CASE v = "Attested" ->
            /\ lease' = [lease EXCEPT ![p].nEpoch = epoch]
            /\ renewOut' = renewOut \cup {"renewed"}
            /\ UNCHANGED <<revoked, contested>>
       [] v = "Contested" ->
            /\ lease' = [lease EXCEPT ![p] = NoLease]
            /\ revoked' = revoked \cup {p}
            /\ contested' = contested \cup {p}
            /\ renewOut' = renewOut \cup {"contested"}
       [] v = "Unattestable" /\ Mut = "M_RENEWLOW" ->
            /\ lease' = [lease EXCEPT ![p].rung = 0, ![p].nEpoch = epoch]
            /\ renewOut' = renewOut \cup {"lowered"}
            /\ UNCHANGED <<revoked, contested>>
       [] OTHER ->
            /\ lease' = [lease EXCEPT ![p] = NoLease]
            /\ renewOut' = renewOut \cup {"lapsed"}
            /\ UNCHANGED <<revoked, contested>>
  /\ UNCHANGED <<guest, gens, pending, epoch, verifierUp, acted, refused, tamperKilled>>

\* The round ends, and the guest with it (§1 P6: the guest is round-coterminous).
EndRound(p) ==
  /\ lease[p].live
  /\ lease' = [lease EXCEPT ![p] = NoLease]
  /\ guest' = [guest EXCEPT ![p] = NoGuest]
  /\ UNCHANGED <<gens, pending, epoch, idx, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>

\* The fleet fence (ADR-0031 §5).
Fence ==
  /\ epoch < MaxEpoch
  /\ idx < MaxIdx
  /\ epoch' = epoch + 1
  /\ idx' = idx + 1
  /\ UNCHANGED <<guest, gens, pending, lease, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>

Next == \/ Fence \/ VerifierFlip
        \/ \E p \in Principals :
             Launch(p) \/ Kill(p) \/ Tamper(p) \/ Appraise(p) \/ Discard(p)
             \/ Grant(p) \/ Renew(p) \/ Act(p) \/ EndRound(p)
Spec == Init /\ [][Next]_vars

\* --- the four properties --------------------------------------------------

\* §4. The claim is true, not only attested: every effect counted Contained was
\* taken by a guest running the archetype profile.
ContainedMeansConfined == \A r \in acted : r.contained => r.img = Arch

\* §3. A principal whose evidence does not reach the declared rung is refused,
\* not granted lower, and not renewed lower (ADR-0031 A1). Vacuity stays declared
\* rather than silent.
NoSilentDowngrade == \A p \in Principals : lease[p].live => lease[p].rung = Declared

\* §3. A Contested principal is revoked and holds no lease.
ContestedStopped == \A p \in contested : p \in revoked /\ ~lease[p].live

\* §3. No live lease rests on an appraisal taken before the current fence.
FreshAppraisal == \A p \in Principals : lease[p].live => lease[p].nEpoch = lease[p].epoch

Safe == ContainedMeansConfined /\ NoSilentDowngrade /\ ContestedStopped /\ FreshAppraisal

\* --- reachability witnesses: each must be VIOLATED -------------------------

\* The ratification condition (§7): a Contained principal takes an admitted effect.
NeverContainedEffect == \A r \in acted : ~r.contained
\* Discrimination: a Mediated principal also acts, so Contained is not everyone.
NeverMediatedEffect  == \A r \in acted : r.contained
\* Rungs 2 and 3 detect a rogue launch. At rung 1 this must HOLD: rung 1 cannot
\* produce a Contested verdict.
NeverContested       == contested = {}
\* Rung 3 refuses when the verifier is unreachable (PC: no grant, not a lower one).
NeverRefused         == ~refused
\* Rung 3 turns tampering into a subtraction.
NeverTamperKilled    == ~tamperKilled
\* A renewal re-attests and keeps the lease.
NeverRenewed         == "renewed" \notin renewOut
\* Rung 3: an unreachable verifier at renewal lets the lease lapse, the case in
\* which the frozen ADR-0031 §4 rule would have renewed it lower.
NeverLapsed          == "lapsed" \notin renewOut
\* Re-attestation of the same instance measures the same launch, so a renewal
\* never turns Contested. Must HOLD at every rung: see ADR-0034 §7.
NeverRenewContested  == "contested" \notin renewOut
=============================================================================
