------------------------------ MODULE RulesFloorNV ------------------------------
(* Non-vacuity check for ADR-0026 rules-floor entries R1-R5, R7.              *)
(* One artifact, one havoc anchor issuance, promotion per ADR-0024.            *)
(* Mech = "param": mechanism reads quorum/recusal/minGrant/timeout from rules. *)
(* Mech = "as0024": mechanism exactly as ADR-0024 rev.3 PromotionEnabled.     *)
(* Mech = "rev4":   mechanism exactly as ADR-0024 rev.4 PromotionEnabled:     *)
(*                  reads quorum/minGrant/recuse; only recorded votes count.  *)
EXTENDS FiniteSets, Naturals

CONSTANTS h1, h2, h3, h4, Humans, Author, AnchorKeys, Active, Mech

AuthActs == {"Issue", "Vote", "Promote"}
BGActs   == {"Issue", "Op"}

RuleSpace == [grant : SUBSET Humans, quorum : {"all", "any"}, recuse : BOOLEAN,
              minGrant : 0..2, timeoutGrant : BOOLEAN, bgScope : SUBSET BGActs]

Entry(e, r) ==
  CASE e = "R1" -> r.quorum = "all"
    [] e = "R2" -> r.minGrant >= 2
    [] e = "R3" -> r.recuse = TRUE
    [] e = "R4" -> r.timeoutGrant = FALSE
    [] e = "R5" -> r.grant \cap AnchorKeys = {}
    [] e = "R7" -> r.bgScope \cap AuthActs = {}

AllEntries == {"R1", "R2", "R3", "R4", "R5", "R7"}
Floor(r) == \A e \in Active : Entry(e, r)

Genesis == [grant |-> Humans \ ({Author} \cup AnchorKeys), quorum |-> "all",
            recuse |-> TRUE, minGrant |-> 2, timeoutGrant |-> FALSE, bgScope |-> {"Op"}]

\* Satisfiability: the full floor admits genesis (floor is non-empty).
ASSUME \A e \in AllEntries : Entry(e, Genesis)
\* Independence: every entry excludes some rule set the other entries admit.
ASSUME \A e \in AllEntries :
         \E r \in RuleSpace : ~Entry(e, r) /\ \A f \in AllEntries \ {e} : Entry(f, r)

VARIABLES rules, issued, votes, timedOut, promoted, approvers, bgDid
vars == <<rules, issued, votes, timedOut, promoted, approvers, bgDid>>

Init == /\ rules = Genesis /\ issued = FALSE
        /\ votes = [h \in Humans |-> "none"] /\ timedOut = {}
        /\ promoted = FALSE /\ approvers = {} /\ bgDid = {}

Counted ==
  IF Mech = "as0024" THEN rules.grant \ {Author}
  ELSE IF rules.recuse THEN rules.grant \ {Author} ELSE rules.grant

Effective(h) ==
  IF votes[h] # "none" THEN votes[h]
  ELSE IF Mech = "param" /\ h \in timedOut /\ rules.timeoutGrant THEN "grant" ELSE "none"

Granting == {h \in Counted : Effective(h) = "grant"}

Recorded == {h \in Counted : votes[h] = "grant"}

PromotionEnabled ==
  IF Mech = "rev4"
  THEN /\ Cardinality(Counted) >= rules.minGrant
       /\ IF rules.quorum = "all" THEN Recorded = Counted ELSE Recorded # {}
  ELSE IF Mech = "as0024"
  THEN /\ Cardinality(Counted) >= 2
       /\ \A h \in Counted : votes[h] = "grant"
  ELSE /\ Cardinality(Counted) >= rules.minGrant
       /\ IF rules.quorum = "all" THEN Granting = Counted ELSE Granting # {}

\* Havoc anchor: any floor-conformant rule set, once; fences in-flight votes.
Issue == /\ ~issued /\ ~promoted
         /\ \E r \in RuleSpace : Floor(r) /\ rules' = r
         /\ issued' = TRUE /\ votes' = [h \in Humans |-> "none"] /\ timedOut' = {}
         /\ UNCHANGED <<promoted, approvers, bgDid>>

Vote(h) == /\ ~promoted /\ h \in rules.grant /\ votes[h] = "none" /\ h \notin timedOut
           /\ \E v \in {"grant", "deny"} : votes' = [votes EXCEPT ![h] = v]
           /\ UNCHANGED <<rules, issued, timedOut, promoted, approvers, bgDid>>

Timeout(h) == /\ ~promoted /\ h \in rules.grant /\ votes[h] = "none" /\ h \notin timedOut
              /\ timedOut' = timedOut \cup {h}
              /\ UNCHANGED <<rules, issued, votes, promoted, approvers, bgDid>>

Promote == /\ ~promoted /\ PromotionEnabled
           /\ promoted' = TRUE /\ approvers' = IF Mech = "rev4" THEN Recorded ELSE Granting
           /\ UNCHANGED <<rules, issued, votes, timedOut, bgDid>>

BreakGlass == /\ \E x \in rules.bgScope : bgDid' = bgDid \cup {x}
              /\ UNCHANGED <<rules, issued, votes, timedOut, promoted, approvers>>

Next == Issue \/ Promote \/ BreakGlass \/ \E h \in Humans : Vote(h) \/ Timeout(h)
Spec == Init /\ [][Next]_vars

\* Properties, one per entry.
P1_AllSeatsGranted  == promoted => \A h \in rules.grant \ {Author} : votes[h] = "grant"
P2_AtLeastTwo       == promoted => Cardinality(approvers) >= 2
P3_AuthorNotCounted == promoted => Author \notin approvers
P4_NoTimeoutGrant   == promoted => \A h \in approvers : votes[h] = "grant"
P5_AnchorNotApprover == promoted => approvers \cap AnchorKeys = {}
P7_BGNoAuthority    == bgDid \cap AuthActs = {}
Safe == P1_AllSeatsGranted /\ P2_AtLeastTwo /\ P3_AuthorNotCounted
        /\ P4_NoTimeoutGrant /\ P5_AnchorNotApprover /\ P7_BGNoAuthority
\* Reachability witness: must be VIOLATED, or every property above is vacuous.
NeverPromoted == ~promoted
=============================================================================
