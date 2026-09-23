----------------------------- MODULE BreakGlass -----------------------------
(* ADR-0029 §5 bootstrap module 5 of 5.                                        *)
(* Invariant: BreakGlassNeverChangesAuthority.                                 *)
(*                                                                             *)
(* ADR-0009 makes break-glass a modeled, quorum-witnessed path. ADR-0026 R7     *)
(* bounds it: no break-glass grant may authorize `Issue`, `Vote`, or promotion. *)
(* Break-glass therefore grants authority WITHIN the rules in force and can     *)
(* never alter the rules themselves - the qualifier ADR-0015 R2 relies on when  *)
(* it keeps the authority-change set at two.                                    *)
(*                                                                             *)
(* Two independent guards are modeled, because they fail independently:         *)
(*   the floor entry R7, which bounds what an issuance may put in bgScope; and  *)
(*   the mechanism, which must confine a break-glass action to bgScope.         *)
(*                                                                             *)
(* Mut = "none":    both guards in force.                                       *)
(* Mut = "M_SCOPE": mutation. The mechanism ignores bgScope and admits any      *)
(*                  action under break-glass. The invariant must fail.          *)
(* Dropping R7 from Active is the other mutation: the floor stops bounding      *)
(* bgScope, a havoc issuance names an authority action, and the mechanism -     *)
(* correctly confining to bgScope - admits it. The invariant must fail there    *)
(* too, which is what makes R7 non-vacuous (ADR-0026 §6, §7).                   *)
EXTENDS RulesFloorBase

CONSTANTS Mut, MaxEpoch

VARIABLES rules, epoch, bgDid
vars == <<rules, epoch, bgDid>>

Init == rules = Genesis /\ epoch = 0 /\ bgDid = {}

\* The anchor issues rules; the floor bounds every issuance (Anchor module).
Issue ==
  /\ epoch < MaxEpoch
  /\ \E r \in RuleSpace : Floor(r) /\ rules' = r
  /\ epoch' = epoch + 1
  /\ UNCHANGED bgDid

\* What the mechanism admits under a break-glass grant. ADR-0009's envelope is
\* the issued bgScope; R7 is what keeps authority actions out of it.
Admits(x) == IF Mut = "M_SCOPE" THEN x \in BGActs      \* envelope ignored
                                ELSE x \in rules.bgScope

BreakGlass ==
  /\ \E x \in BGActs : Admits(x) /\ bgDid' = bgDid \cup {x}
  /\ UNCHANGED <<rules, epoch>>

Next == Issue \/ BreakGlass
Spec == Init /\ [][Next]_vars

\* BreakGlassNeverChangesAuthority. Nothing done under break-glass is an
\* authority-changing action, under any issuance sequence the floor admits.
BreakGlassNeverChangesAuthority == bgDid \cap AuthActs = {}

\* Reachability witness: must be VIOLATED, or the invariant holds because
\* break-glass is never invoked at all.
NeverBreakGlass == bgDid = {}
=============================================================================
