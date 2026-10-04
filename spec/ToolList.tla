----------------------------- MODULE ToolList -----------------------------
(* The tool list: ADR-0048 (Proposed), its ratification condition (§8). At the *)
(* start of a round the Listener delivers the interface of every tool the      *)
(* lease may call, and the mechanism writes the same list to the round topic   *)
(* as the round's opening record, where the Observer reads it.                 *)
(*                                                                             *)
(* The mechanism sees a lease, a bundle revision and a topic. This module also *)
(* carries, as ghost state the mechanism never reads, what the Thinker was     *)
(* actually told (`told`), and for every call whether the tool it names was on *)
(* that list when the call was decided.                                        *)
(*                                                                             *)
(*   ToolListIsExact       under a live lease the Thinker was told the         *)
(*                         allowlist of the granted revision, narrowed by the  *)
(*                         lease: no more and no fewer                         *)
(*   ToldMatchesDecided    no admitted call names a tool the Thinker was not   *)
(*                         told of, and no call is refused for a tool it was   *)
(*                         told of                                             *)
(*   ListFixedForRound     under a live lease, what the Thinker was told is    *)
(*                         what it was told at the grant                       *)
(*   OpeningRecordFirst    no effect is recorded on a round's topic before its *)
(*                         opening record                                      *)
(*   OpenedListIsTold      the list in the opening record is the list the      *)
(*                         Thinker was told: the Observer reads what the       *)
(*                         Thinker was given                                   *)
(*                                                                             *)
(* Two bundle revisions with different allowlists, so that a promotion in the  *)
(* middle of a round changes which tools exist. A grant names the revision     *)
(* promoted at that moment (ADR-0031 §1) and any narrowing (§4). The Thinker   *)
(* is havoc: it calls any tool, told or not.                                   *)
(*                                                                             *)
(* Not modelled: the rendering and its size bound; purpose text, which nothing *)
(* checks (ADR-0048 §5); the other reasons a call may be refused (the floor's  *)
(* other entries, the bundle's input checks), so "refused" here means refused  *)
(* at the allowlist. One principal, any number of rounds.                      *)
(*                                                                             *)
(* Mut = "none":          ADR-0048 as revised at R4.                           *)
(* Mut = "M_RECOMPUTE":   a promotion re-delivers the list from the new        *)
(*                        revision to a live round. Must break                 *)
(*                        ToolListIsExact, ToldMatchesDecided,                 *)
(*                        ListFixedForRound and OpenedListIsTold.              *)
(* Mut = "M_WIDE":        the list ignores the lease's narrowing. Must break   *)
(*                        ToolListIsExact and ToldMatchesDecided.              *)
(* Mut = "M_DECIDELATEST": a call is decided against the latest revision and   *)
(*                        not the lease's. Must break ToldMatchesDecided and   *)
(*                        nothing else.                                        *)
(* Mut = "M_LATE":        the opening record is written when the mechanism     *)
(*                        gets to it, not at the grant. Must break             *)
(*                        OpeningRecordFirst and nothing else.                 *)
EXTENDS Naturals

CONSTANT Mut

Tools == {"t1", "t2", "t3"}
Revs  == {1, 2}
Allow == [r \in Revs |-> IF r = 1 THEN {"t1", "t2"} ELSE {"t2", "t3"}]

VARIABLES
  latest,          \* the bundle revision last promoted
  lease,           \* [live, rev, narrow]: the round's lease
  told,            \* the tools the Thinker was told of (ghost)
  toldAtGrant,     \* the same, as it was when the lease was granted (ghost)
  opened,          \* the round topic has its opening record
  openList,        \* the list that record holds
  actsBeforeOpen,  \* an effect was recorded on the topic before the opening record (ghost)
  admitted,        \* this round's admitted calls: [tool, wasTold]
  refused          \* this round's calls refused at the allowlist: [tool, wasTold]

vars == <<latest, lease, told, toldAtGrant, opened, openList, actsBeforeOpen, admitted, refused>>

Init ==
  /\ latest = 1
  /\ lease = [live |-> FALSE, rev |-> 1, narrow |-> {}]
  /\ told = {} /\ toldAtGrant = {}
  /\ opened = FALSE /\ openList = {}
  /\ actsBeforeOpen = FALSE
  /\ admitted = {} /\ refused = {}

\* The tool list for a lease: ADR-0048 §2.
List(rv, n) == IF Mut = "M_WIDE" THEN Allow[rv] ELSE Allow[rv] \cap n

\* A grant, for a new round: the revision in force, any narrowing. The list is delivered and
\* the opening record written.
Grant(n) ==
  /\ ~lease.live
  /\ lease' = [live |-> TRUE, rev |-> latest, narrow |-> n]
  /\ told' = List(latest, n) /\ toldAtGrant' = List(latest, n)
  /\ IF Mut = "M_LATE"
       THEN opened' = FALSE /\ openList' = {}
       ELSE opened' = TRUE /\ openList' = List(latest, n)
  /\ actsBeforeOpen' = FALSE
  /\ admitted' = {} /\ refused' = {}
  /\ UNCHANGED latest

\* M_LATE only: the opening record is written at some later moment.
WriteOpen ==
  /\ Mut = "M_LATE" /\ lease.live /\ ~opened
  /\ opened' = TRUE /\ openList' = told
  /\ UNCHANGED <<latest, lease, told, toldAtGrant, actsBeforeOpen, admitted, refused>>

\* A bundle is promoted. A live round keeps the revision its lease names (ADR-0031 R2).
Promote(r) ==
  /\ r # latest
  /\ latest' = r
  /\ told' = IF Mut = "M_RECOMPUTE" /\ lease.live THEN List(r, lease.narrow) ELSE told
  /\ UNCHANGED <<lease, toldAtGrant, opened, openList, actsBeforeOpen, admitted, refused>>

\* The revision a call is decided against.
DecideRev == IF Mut = "M_DECIDELATEST" THEN latest ELSE lease.rev

\* `Actuate` or `Invoke` of tool t. Admitted at the allowlist, and recorded on the topic, or refused.
Call(t) ==
  /\ lease.live
  /\ IF t \in Allow[DecideRev] \cap lease.narrow
       THEN /\ admitted' = admitted \cup {[tool |-> t, wasTold |-> t \in told]}
            /\ actsBeforeOpen' = (actsBeforeOpen \/ ~opened)
            /\ UNCHANGED refused
       ELSE /\ refused' = refused \cup {[tool |-> t, wasTold |-> t \in told]}
            /\ UNCHANGED <<admitted, actsBeforeOpen>>
  /\ UNCHANGED <<latest, lease, told, toldAtGrant, opened, openList>>

EndRound ==
  /\ lease.live
  /\ lease' = [lease EXCEPT !.live = FALSE]
  /\ UNCHANGED <<latest, told, toldAtGrant, opened, openList, actsBeforeOpen, admitted, refused>>

Next == \/ \E n \in SUBSET Tools : Grant(n)
        \/ \E r \in Revs : Promote(r)
        \/ \E t \in Tools : Call(t)
        \/ WriteOpen
        \/ EndRound

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

ToolListIsExact == lease.live => told = Allow[lease.rev] \cap lease.narrow

ToldMatchesDecided == /\ \A a \in admitted : a.wasTold
                      /\ \A x \in refused : ~x.wasTold

ListFixedForRound == lease.live => told = toldAtGrant

OpeningRecordFirst == ~actsBeforeOpen

OpenedListIsTold == opened => openList = told

Safe == /\ ToolListIsExact /\ ToldMatchesDecided /\ ListFixedForRound
        /\ OpeningRecordFirst /\ OpenedListIsTold

\* --- reachability witnesses: each must be VIOLATED ---------------------------

\* A bundle is promoted in the middle of a round: the case the properties are about.
NeverPromotedMidRound == ~(lease.live /\ latest # lease.rev)
\* A lease narrows its allowlist.
NeverNarrowed == lease.live => told = Allow[lease.rev]
\* A call is admitted, and one is refused.
NeverAdmitted == admitted = {}
NeverRefused == refused = {}
\* The next round is told the new revision's tools.
NeverNewList == ~(lease.live /\ lease.rev = 2 /\ "t3" \in told)
\* A tool that exists in the latest revision is refused under a lease on the old one: a
\* promotion does not reach a live round.
NeverRefusedNewTool == \A x \in refused : ~(x.tool \in Allow[latest])
=============================================================================
