--------------------------- MODULE RulesFloorNV_rev5 ---------------------------
(* Non-vacuity check for the ADR-0026 rules floor after the 2026.09.23          *)
(* revisions: R3 withdrawn, R9 added, quorum a threshold (S6-2, S6-3).          *)
(*                                                                              *)
(* Supersedes the rev4 column of ADR-0026 §6, which modeled ADR-0024 rev.4 and   *)
(* did not model the ADR-0022 Vote envelope at all.                             *)
(*                                                                              *)
(* Mech = "rev5":     the mechanism as ADR-0024 revision 5. quorum is "all" or  *)
(*                    a grant-vote threshold k. Author recusal is a mechanism   *)
(*                    constant, enforced twice: the author is not a counted     *)
(*                    seat (ADR-0024 §6) and the ADR-0022 Vote envelope refuses  *)
(*                    the author's vote.                                        *)
(* Mech = "norecuse": mutation for the withdrawn R3. Recusal is removed from    *)
(*                    both sites. P3 must fail, which is what makes withdrawing  *)
(*                    R3 safe rather than merely convenient.                    *)
EXTENDS FiniteSets, Naturals

CONSTANTS Active, Mech

\* Five humans, not the rev4 model's four. At four, R5 keeps the anchor
\* key-holder off the roster and recusal removes the author, leaving exactly two
\* counted seats - and a threshold of k >= 2 over two seats IS unanimity, so the
\* R1 mutation holds vacuously and proves nothing. Five is also the archetype
\* figure ADR-0026 §6 finding 5 derives (S6-10).
Humans     == {"h1", "h2", "h3", "h4", "h5"}
Author     == "h1"
AnchorKeys == {"h4"}

AuthActs == {"Issue", "Vote", "Promote"}
BGActs   == {"Issue", "Op"}

\* quorum is "all" (unanimity over counted seats) or a grant-vote threshold k.
\* The rev4 value "any" is withdrawn: it is k = 1 (S6-2).
\*
\* The records write this as one field holding either a string or a number.
\* TLC will not compare a string with a number, so the model tags it instead:
\* [mode |-> "all"] and [mode |-> "k", k |-> n]. The encoding is the model's,
\* not the record's; k is carried in both modes and ignored when mode = "all".
QVals == [mode : {"all", "k"}, k : 0..4]

RuleSpace == [grant : SUBSET Humans, quorum : QVals, minGrant : 0..2,
              bgScope : SUBSET BGActs]

Entry(e, r) ==
  CASE e = "R1" -> r.quorum.mode = "all"
    [] e = "R2" -> r.minGrant >= 2
    [] e = "R5" -> r.grant \cap AnchorKeys = {}
    [] e = "R7" -> r.bgScope \cap AuthActs = {}
    [] e = "R9" -> r.quorum.mode = "all" \/ r.quorum.k >= 2

AllEntries == {"R1", "R2", "R5", "R7", "R9"}
Floor(r) == \A e \in Active : Entry(e, r)

Genesis == [grant |-> Humans \ ({Author} \cup AnchorKeys),
            quorum |-> [mode |-> "all", k |-> 0],
            minGrant |-> 2, bgScope |-> {"Op"}]

\* Satisfiability: the full floor admits genesis.
ASSUME \A e \in AllEntries : Entry(e, Genesis)

\* Independence, for every entry but R9.
ASSUME \A e \in AllEntries \ {"R9"} :
         \E r \in RuleSpace : ~Entry(e, r) /\ \A f \in AllEntries \ {e} : Entry(f, r)

\* R9 is a CONDITIONAL entry and fails the independence test above by
\* construction: every rule set R9 excludes (quorum 0 or 1) is also excluded by
\* R1, which admits only "all". R9 binds a deployment that has already relaxed
\* R1 - that is, a promotion degeneracy - and its independence is therefore
\* stated relative to a floor without R1.
ASSUME \E r \in RuleSpace :
         /\ ~Entry("R9", r)
         /\ \A f \in AllEntries \ {"R1", "R9"} : Entry(f, r)

VARIABLES rules, issued, votes, promoted, approvers, seats, bgDid
vars == <<rules, issued, votes, promoted, approvers, seats, bgDid>>

Init == /\ rules = Genesis /\ issued = FALSE
        /\ votes = [h \in Humans |-> "none"]
        /\ promoted = FALSE /\ approvers = {} /\ seats = {} /\ bgDid = {}

\* ADR-0024 §6: the author holds no seat. A mechanism constant, not an issued
\* value - which is why ADR-0026 R3 was withdrawn (S6-3).
Counted == IF Mech = "norecuse" THEN rules.grant ELSE rules.grant \ {Author}

Recorded == {h \in Counted : votes[h] = "grant"}

\* ADR-0024 revision 5. Only recorded votes count; a timeout is never a grant.
PromotionEnabled ==
  /\ Cardinality(Counted) >= rules.minGrant
  /\ IF rules.quorum.mode = "all"
     THEN Recorded = Counted
     ELSE Cardinality(Recorded) >= rules.quorum.k

\* Havoc anchor: any floor-conformant rule set, once; fences in-flight votes.
Issue == /\ ~issued /\ ~promoted
         /\ \E r \in RuleSpace : Floor(r) /\ rules' = r
         /\ issued' = TRUE /\ votes' = [h \in Humans |-> "none"]
         /\ UNCHANGED <<promoted, approvers, seats, bgDid>>

\* The ADR-0022 Vote envelope, modeled for the first time: a seat at the current
\* rules epoch, and never the artifact's author.
Vote(h) == /\ ~promoted /\ h \in rules.grant /\ votes[h] = "none"
           /\ (Mech # "norecuse" => h # Author)
           /\ \E v \in {"grant", "deny"} : votes' = [votes EXCEPT ![h] = v]
           /\ UNCHANGED <<rules, issued, promoted, approvers, seats, bgDid>>

Promote == /\ ~promoted /\ PromotionEnabled
           /\ promoted' = TRUE /\ approvers' = Recorded /\ seats' = Counted
           /\ UNCHANGED <<rules, issued, votes, bgDid>>

BreakGlass == /\ \E x \in rules.bgScope : bgDid' = bgDid \cup {x}
              /\ UNCHANGED <<rules, issued, votes, promoted, approvers, seats>>

Next == Issue \/ Promote \/ BreakGlass \/ \E h \in Humans : Vote(h)
Spec == Init /\ [][Next]_vars

\* Properties, one per entry. R1 and R9 protect different things: R1 that every
\* counted seat granted, R9 that no single grant promotes once R1 is relaxed.
P1_Unanimity         == promoted => approvers = seats
P2_TwoSeatsCounted   == promoted => Cardinality(seats) >= 2
P3_AuthorNotCounted  == promoted => Author \notin approvers
P5_AnchorNotApprover == promoted => approvers \cap AnchorKeys = {}
P7_BGNoAuthority     == bgDid \cap AuthActs = {}
P9_NoSoloGrant       == promoted => Cardinality(approvers) >= 2

Safe == P1_Unanimity /\ P2_TwoSeatsCounted /\ P3_AuthorNotCounted
        /\ P5_AnchorNotApprover /\ P7_BGNoAuthority /\ P9_NoSoloGrant

\* Reachability witness: must be VIOLATED, or every property above is vacuous.
NeverPromoted == ~promoted
=============================================================================
