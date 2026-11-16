------------------------------ MODULE Mesh_proof ------------------------------
(* TLAPS proof of the invariants of Mesh.tla (ADR-0055 §11). Mesh.tla is not   *)
(* edited.                                                                     *)
(*                                                                             *)
(*   THEOREM BudgetBoundAlways              [Mut # "M_OVERRUN",                *)
(*                                           Mut # "M_ORCHFREE"]               *)
(*   THEOREM CompletedOnlyBySinkAlways      [Mut # "M_BUDGETDONE"]             *)
(*   THEOREM RouteOnItsEventAlways          [Mut # "M_TRACKER"]                *)
(*   THEOREM NoActivationAfterFindingAlways [Mut # "M_SOURCEONLY"]             *)
(*   THEOREM LabelCoversTruthAlways         [Mut # "M_FORGETTAINT"]            *)
(*   THEOREM TaintedNeverOutwardAlways      [Mut # "M_FORGETTAINT"]            *)
(*   THEOREM ClearHopsAlternateAlways       [Mut # "M_NOLINEAGE"]              *)
(*   THEOREM SafeAlways                     [Mut = "none"]                     *)
(*                                                                             *)
(* Each hypothesis is the mutation the "breaks" rows of Mesh-rows.txt pair     *)
(* with the property, and no other. TLC checks these at the one budget the     *)
(* module fixes, and two remainder rows only under CapOnePast; a proof does    *)
(* not need that cut.                                                          *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant;  *)
(* before the promotion there are no activations and the workflow is running;  *)
(* and every activation is well formed (`ActsWF`): it was created at or before *)
(* the log's position, its causal history is among activations at or before    *)
(* it, its lineage is its node's seat, and, past the root, its trigger is an   *)
(* earlier activation that had ended, of the source of the edge that entered   *)
(* it.                                                                         *)
(*                                                                             *)
(* Everything about the sequence of activations is said once, in `ActsStep`.   *)
(* A step of the module does one of four things to it: it changes nothing an   *)
(* invariant reads (`Frame`: an activation's identity, its finding, and, once  *)
(* it has ended, its status and labels, are fixed); it appends one activation  *)
(* entered by an edge enabled in the state it was appended to (`AddStep`); it  *)
(* is the promotion; or it is a finding. Each property is then four cases.     *)
(*                                                                             *)
(* NoActivationAfterFinding rests on the finding's position being past every   *)
(* activation already created, and on the guard at creation. Taint needs the   *)
(* trigger's truth to be frozen once it has ended. ClearHopsAlternate needs    *)
(* the promoted seating to alternate, and a seat fixed by the promotion.       *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Mesh-results-*.txt). Check: tools/tlapm --cleanfp --strict.                *)
EXTENDS Mesh, SequenceTheorems, TLAPS

Whys    == {"lease", "ended", "closed", "finding", "history", "guard"}
ActRec  == [node : Nodes, trig : Nat, via : Edges \cup {"root"},
            status : {"ready", "running", "ended", "failed"}, st : Sts \cup {"none"},
            lbl : BOOLEAN, truth : BOOLEAN, lin : Lin, hist : SUBSET Nat,
            found : BOOLEAN, foundAt : Nat, at : Nat]
PendRec == [edge : Chosen, ev : Nat, round : Nat]
AppRec  == [edge : Chosen, ev : Nat, to : Nat, at : Nat]

TypeOK ==
  /\ promoted \in BOOLEAN
  /\ seat \in [Nodes -> Lin]
  /\ wf \in {"running", "completed", "failed"}
  /\ acts \in Seq(ActRec)
  /\ nCharged \in Nat
  /\ nAll \in Nat
  /\ exhausted \in BOOLEAN
  /\ orch \in [live : BOOLEAN, ev : Nat, id : Nat]
  /\ nRounds \in Nat
  /\ served \subseteq Nat
  /\ consumed \subseteq Nat
  /\ decFailed \subseteq Nat
  /\ pending \subseteq PendRec
  /\ applied \subseteq AppRec
  /\ voided \subseteq [edge : Edges, why : Whys]
  /\ idx \in Nat

BeforePromotion == ~promoted => acts = <<>> /\ wf = "running"

ActsWF ==
  \A j \in Ix(acts) :
    /\ acts[j].at <= idx
    /\ acts[j].hist \subseteq 1..j
    /\ acts[j].lin = seat[acts[j].node]
    /\ j > 1 => /\ acts[j].trig \in 1..(j - 1)
                /\ acts[j].via \in Edges
                /\ acts[j].node = Dst[acts[j].via]
                /\ acts[acts[j].trig].node = Src[acts[j].via]
                /\ acts[acts[j].trig].status = "ended"

Shape == TypeOK /\ BeforePromotion /\ ActsWF

\* The parts of Apply and End the proof needs by name; each is the module's own text.
ApplyTgt(r)  == IF Tracker THEN LatestOpen ELSE r.ev
ApplyLive(r) == orch.live /\ (Tracker \/ (orch.id = r.round /\ orch.ev = r.ev))
ApplyOk(r)   == ApplyLive(r) /\ wf = "running" /\ ApplyTgt(r) \in OpenEv /\ EnabledIn(acts, r.edge, ApplyTgt(r))
EndA1(i, s, t) == [acts EXCEPT ![i].status = "ended", ![i].st = s,
                               ![i].lbl = @ \/ t, ![i].truth = @ \/ t]

\* What a step keeps of an activation: c is what activation j has become.
FixedR(j, c) ==
  /\ c.node = acts[j].node
  /\ c.trig = acts[j].trig
  /\ c.via = acts[j].via
  /\ c.lin = acts[j].lin
  /\ c.hist = acts[j].hist
  /\ c.at = acts[j].at
  /\ c.found = acts[j].found
  /\ c.foundAt = acts[j].foundAt
  /\ acts[j].status = "ended" => /\ c.status = "ended"
                                 /\ c.lbl = acts[j].lbl
                                 /\ c.truth = acts[j].truth
  /\ (acts[j].truth => acts[j].lbl) => (c.truth => c.lbl)

Frame(b) == \A j \in 1..Len(acts) : FixedR(j, b[j])

\* One activation of node n is appended, entered by edge e out of activation t, which is enabled
\* in the sequence pre it is appended to.
AddStep(pre, n, t, e) ==
  /\ pre \in Seq(ActRec)
  /\ Len(pre) = Len(acts)
  /\ Frame(pre)
  /\ t \in 1..Len(acts)
  /\ e \in Edges
  /\ n = Dst[e]
  /\ EnabledIn(pre, e, t)
  /\ acts' = Append(pre, NewAct(pre, n, t, e, idx + 1))
  /\ idx' = idx + 1
  /\ UNCHANGED seat

\* The label and truth of activation t are read by the invariants below.
InvT == LabelCoversTruth /\ TaintedNeverOutward
InvH == ClearHopsAlternate /\ (promoted => Alternates(seat))
InvB == nAll = nCharged /\ nCharged <= N
-----------------------------------------------------------------------------
LEMMA EdgeFacts ==
  /\ Chosen \subseteq Edges
  /\ \A e \in Edges : Src[e] \in Nodes /\ Dst[e] \in Nodes
  /\ "e3" \in Edges /\ Dst["e3"] = "s" /\ Src["e3"] = "w"
  /\ "s" \in Nodes /\ Sink \in Nodes /\ Root \in Nodes
  /\ Root = "s"
  BY DEF Chosen, Edges, Src, Dst, Nodes, Sink, Root

LEMMA SeqFacts ==
  ASSUME NEW S, NEW s \in Seq(S)
  PROVE  /\ Len(s) \in Nat
         /\ DOMAIN s = 1..Len(s)
         /\ \A k \in 1..Len(s) : s[k] \in S
  BY LenProperties, ElementOfSeq

LEMMA OpenEvNat == OpenEv \subseteq Ix(acts)
  BY DEF OpenEv

LEMMA IxNat ==
  ASSUME acts \in Seq(ActRec)
  PROVE  Ix(acts) \subseteq Nat /\ \A k \in Ix(acts) : acts[k] \in ActRec
  BY SeqFacts DEF Ix

LEMMA NewActRec ==
  ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(pre), NEW e \in Edges, NEW p \in Nat,
         seat \in [Nodes -> Lin]
  PROVE  NewAct(pre, n, t, e, p) \in ActRec
<1>1. Len(pre) \in Nat /\ t \in Nat /\ pre[t] \in ActRec
  BY SeqFacts
<1>2. {Len(pre) + 1} \cup pre[t].hist \in SUBSET Nat
  BY <1>1 DEF ActRec
<1>3. (e \in Clear /\ Mut # "M_FORGETTAINT" /\ pre[t].lbl) \in BOOLEAN
      /\ (e \in Clear /\ pre[t].truth) \in BOOLEAN
  OBVIOUS
<1>4. seat[n] \in Lin /\ t \in Nat
  BY <1>1
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF NewAct, ActRec

LEMMA UpdFrame ==
  ASSUME acts \in Seq(ActRec), NEW i \in 1..Len(acts), NEW v \in ActRec, FixedR(i, v)
  PROVE  LET b == [acts EXCEPT ![i] = v]
         IN  /\ b \in Seq(ActRec)
             /\ Len(b) = Len(acts)
             /\ Frame(b)
<1> DEFINE b == [acts EXCEPT ![i] = v]
<1>1. /\ b \in Seq(ActRec)
      /\ Len(b) = Len(acts)
      /\ \A j \in 1..Len(acts) : b[j] = IF j = i THEN v ELSE acts[j]
  BY ExceptSeq
<1>2. \A j \in 1..Len(acts) : FixedR(j, b[j])
  <2> SUFFICES ASSUME NEW j \in 1..Len(acts) PROVE FixedR(j, b[j])
    OBVIOUS
  <2>1. CASE j = i
    BY <1>1, <2>1
  <2>2. CASE j # i
    BY <1>1, <2>2 DEF FixedR
  <2> QED
    BY <2>1, <2>2
<1> QED
  BY <1>1, <1>2 DEF Frame

LEMMA FrameRefl ==
  ASSUME acts \in Seq(ActRec)
  PROVE  Frame(acts)
  BY DEF Frame, FixedR

\* A status change on an activation that has not ended.
LEMMA StatusFrame ==
  ASSUME acts \in Seq(ActRec), NEW i \in 1..Len(acts), NEW v \in {"running", "failed"},
         acts[i].status \in {"ready", "running"}, acts' = [acts EXCEPT ![i].status = v]
  PROVE  /\ acts' \in Seq(ActRec)
         /\ Len(acts') = Len(acts)
         /\ Frame(acts')
<1>0. acts[i] \in ActRec
  BY SeqFacts
<1> DEFINE w == [acts[i] EXCEPT !.status = v]
<1>1. w \in ActRec
  BY <1>0 DEF ActRec
<1>2. FixedR(i, w)
  BY <1>0 DEF FixedR, ActRec
<1>3. acts' = [acts EXCEPT ![i] = w]
  OBVIOUS
<1>4. LET b == [acts EXCEPT ![i] = w]
      IN  /\ b \in Seq(ActRec)
          /\ Len(b) = Len(acts)
          /\ Frame(b)
  BY <1>1, <1>2, UpdFrame
<1> QED
  BY <1>3, <1>4 DEF Frame

\* What End does to the sequence before any new activation.
LEMMA EndFacts ==
  ASSUME acts \in Seq(ActRec), NEW i \in 1..Len(acts), NEW s \in Sts, NEW t \in BOOLEAN,
         acts[i].status = "running"
  PROVE  LET a1 == EndA1(i, s, t)
         IN  /\ a1 \in Seq(ActRec)
             /\ Len(a1) = Len(acts)
             /\ Frame(a1)
             /\ \A j \in 1..Len(acts) : j # i => a1[j] = acts[j]
<1>0. acts[i] \in ActRec
  BY SeqFacts
<1> DEFINE w == [acts[i] EXCEPT !.status = "ended", !.st = s, !.lbl = @ \/ t, !.truth = @ \/ t]
<1>1. w \in ActRec
  BY <1>0 DEF ActRec
<1>2. FixedR(i, w)
  BY <1>0 DEF FixedR, ActRec
<1>3. EndA1(i, s, t) = [acts EXCEPT ![i] = w]
  BY DEF EndA1
<1>4. LET b == [acts EXCEPT ![i] = w]
      IN  /\ b \in Seq(ActRec)
          /\ Len(b) = Len(acts)
          /\ Frame(b)
  BY <1>1, <1>2, UpdFrame
<1>5. \A j \in 1..Len(acts) : [acts EXCEPT ![i] = w][j] = IF j = i THEN w ELSE acts[j]
  BY <1>1, ExceptSeq
<1> QED
  BY <1>3, <1>4, <1>5 DEF Frame

\* What Finding does to the sequence.
LEMMA FindingFacts ==
  ASSUME TypeOK, NEW i \in Ix(acts), Finding(i)
  PROVE  /\ acts' \in Seq(ActRec)
         /\ Len(acts') = Len(acts)
         /\ ~acts[i].found
         /\ acts'[i].foundAt = idx + 1
         /\ acts'[i].found = TRUE
         /\ idx' = idx + 1
         /\ UNCHANGED seat
         /\ \A j \in Ix(acts) : j # i => acts'[j] = acts[j]
         /\ \A j \in Ix(acts) : /\ acts'[j].node = acts[j].node
                                /\ acts'[j].trig = acts[j].trig
                                /\ acts'[j].via = acts[j].via
                                /\ acts'[j].lin = acts[j].lin
                                /\ acts'[j].hist = acts[j].hist
                                /\ acts'[j].at = acts[j].at
                                /\ acts'[j].status = acts[j].status
                                /\ acts'[j].lbl = acts[j].lbl
                                /\ acts'[j].truth = acts[j].truth
<1>0. acts \in Seq(ActRec) /\ i \in 1..Len(acts) /\ idx \in Nat
  BY DEF TypeOK, Ix
<1>1. acts[i] \in ActRec
  BY <1>0, SeqFacts
<1> DEFINE w == [acts[i] EXCEPT !.found = TRUE, !.foundAt = idx + 1]
<1>2. w \in ActRec
  BY <1>0, <1>1 DEF ActRec
<1>3. acts' = [acts EXCEPT ![i] = w] /\ ~acts[i].found /\ idx' = idx + 1 /\ UNCHANGED seat
  BY DEF Finding
<1>4. /\ [acts EXCEPT ![i] = w] \in Seq(ActRec)
      /\ Len([acts EXCEPT ![i] = w]) = Len(acts)
      /\ \A j \in 1..Len(acts) : [acts EXCEPT ![i] = w][j] = IF j = i THEN w ELSE acts[j]
  BY <1>0, <1>2, ExceptSeq
<1>5. acts'[i] = w
  BY <1>0, <1>3, <1>4
<1>6. /\ acts'[i].foundAt = idx + 1
      /\ acts'[i].found = TRUE
  BY <1>1, <1>5 DEF ActRec
<1>7. \A j \in Ix(acts) : j # i => acts'[j] = acts[j]
  BY <1>3, <1>4 DEF Ix
<1>8. \A j \in Ix(acts) : /\ acts'[j].node = acts[j].node
                          /\ acts'[j].trig = acts[j].trig
                          /\ acts'[j].via = acts[j].via
                          /\ acts'[j].lin = acts[j].lin
                          /\ acts'[j].hist = acts[j].hist
                          /\ acts'[j].at = acts[j].at
                          /\ acts'[j].status = acts[j].status
                          /\ acts'[j].lbl = acts[j].lbl
                          /\ acts'[j].truth = acts[j].truth
  <2> SUFFICES ASSUME NEW j \in Ix(acts)
               PROVE  /\ acts'[j].node = acts[j].node
                      /\ acts'[j].trig = acts[j].trig
                      /\ acts'[j].via = acts[j].via
                      /\ acts'[j].lin = acts[j].lin
                      /\ acts'[j].hist = acts[j].hist
                      /\ acts'[j].at = acts[j].at
                      /\ acts'[j].status = acts[j].status
                      /\ acts'[j].lbl = acts[j].lbl
                      /\ acts'[j].truth = acts[j].truth
    OBVIOUS
  <2>1. CASE j = i
    BY <1>1, <1>5, <2>1 DEF ActRec
  <2>2. CASE j # i
    BY <1>7, <2>2
  <2> QED
    BY <2>1, <2>2
<1> QED
  BY <1>3, <1>4, <1>6, <1>7, <1>8

\* What an appended activation looks like.
LEMMA AddFacts ==
  ASSUME TypeOK, NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
         AddStep(pre, n, t, e)
  PROVE  LET nw == NewAct(pre, n, t, e, idx + 1)
         IN  /\ nw \in ActRec
             /\ acts' \in Seq(ActRec)
             /\ Len(acts') = Len(acts) + 1
             /\ \A k \in 1..Len(acts) : acts'[k] = pre[k]
             /\ acts'[Len(acts) + 1] = nw
<1> DEFINE nw == NewAct(pre, n, t, e, idx + 1)
<1>0. /\ Len(pre) = Len(acts) /\ acts \in Seq(ActRec) /\ seat \in [Nodes -> Lin] /\ idx + 1 \in Nat
      /\ acts' = Append(pre, nw)
  BY DEF AddStep, TypeOK
<1>1. nw \in ActRec
  BY <1>0, NewActRec
<1>2. /\ Append(pre, nw) \in Seq(ActRec)
      /\ Len(Append(pre, nw)) = Len(pre) + 1
      /\ \A k \in 1..Len(pre) : Append(pre, nw)[k] = pre[k]
      /\ Append(pre, nw)[Len(pre) + 1] = nw
  BY <1>1, AppendProperties
<1> QED
  BY <1>0, <1>1, <1>2

\* The root sequence of the promotion.
LEMMA RootSeq ==
  ASSUME NEW x \in ActRec
  PROVE  /\ <<x>> \in Seq(ActRec)
         /\ Len(<<x>>) = 1
         /\ <<x>>[1] = x
<1>1. /\ Append(<<>>, x) \in Seq(ActRec)
      /\ Len(Append(<<>>, x)) = 0 + 1
      /\ Append(<<>>, x)[0 + 1] = x
  <2>1. <<>> \in Seq(ActRec) /\ Len(<<>>) = 0
    BY EmptySeq
  <2> QED
    BY <2>1, AppendProperties
<1>2. <<x>> = Append(<<>>, x)
  <2>1. <<>> \in Seq(ActRec) /\ <<x>> \in [1..1 -> ActRec]
    BY EmptySeq
  <2>2. <<x>> \in Seq(ActRec)
    BY <2>1, SeqDef
  <2>3. Len(<<x>>) = 1
    BY <2>2, LenProperties
  <2>4. Len(Append(<<>>, x)) = 1 /\ Append(<<>>, x) \in Seq(ActRec) /\ Append(<<>>, x)[1] = x
    BY <1>1
  <2>5. \A k \in 1..Len(<<x>>) : <<x>>[k] = Append(<<>>, x)[k]
    BY <2>3, <2>4
  <2> QED
    BY <2>2, <2>3, <2>4, <2>5, SeqEqual
<1> QED
  BY <1>1, <1>2

\* Every step of the module, classified by what it does to the sequence of activations.
LEMMA ActsStep ==
  ASSUME TypeOK, [Next]_vars
  PROVE  \/ /\ acts' \in Seq(ActRec)
            /\ Len(acts') = Len(acts)
            /\ Frame(acts')
            /\ idx' >= idx
            /\ UNCHANGED seat
         \/ \E pre \in Seq(ActRec), n \in Nodes, t \in 1..Len(acts), e \in Edges : AddStep(pre, n, t, e)
         \/ \E st \in Seatings : Promote(st)
         \/ \E i \in Ix(acts) : Finding(i)
<1>0. acts \in Seq(ActRec) /\ idx \in Nat /\ seat \in [Nodes -> Lin]
  BY DEF TypeOK
<1>q. ASSUME UNCHANGED acts, idx' >= idx, UNCHANGED seat
      PROVE  /\ acts' \in Seq(ActRec)
             /\ Len(acts') = Len(acts)
             /\ Frame(acts')
             /\ idx' >= idx
             /\ UNCHANGED seat
  <2>1. Frame(acts)
    BY <1>0, FrameRefl
  <2>2. Frame(acts')
    BY <1>q, <2>1
  <2> QED
    BY <1>0, <1>q, <2>2
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>1, <1>q DEF vars
<1>2. ASSUME NEW st \in Seatings, Promote(st) PROVE \E st2 \in Seatings : Promote(st2)
  BY <1>2
<1>3. ASSUME NEW i \in Ix(acts), Grant(i)
      PROVE  /\ acts' \in Seq(ActRec)
             /\ Len(acts') = Len(acts)
             /\ Frame(acts')
             /\ idx' >= idx
             /\ UNCHANGED seat
  <2>1. i \in 1..Len(acts) /\ acts[i].status = "ready" /\ UNCHANGED <<seat, idx>>
    BY <1>3 DEF Grant, Ix
  <2>2. \/ acts' = [acts EXCEPT ![i].status = "running"]
        \/ acts' = [acts EXCEPT ![i].status = "failed"]
    BY <1>3 DEF Grant
  <2>3. /\ acts' \in Seq(ActRec)
        /\ Len(acts') = Len(acts)
        /\ Frame(acts')
    BY <1>0, <2>1, <2>2, StatusFrame
  <2> QED
    BY <1>0, <2>1, <2>3
<1>4. ASSUME NEW i \in Ix(acts), NEW s \in Sts, NEW t \in BOOLEAN, End(i, s, t)
      PROVE  \/ /\ acts' \in Seq(ActRec)
                /\ Len(acts') = Len(acts)
                /\ Frame(acts')
                /\ idx' >= idx
                /\ UNCHANGED seat
             \/ \E pre \in Seq(ActRec), n \in Nodes, tt \in 1..Len(acts), e \in Edges : AddStep(pre, n, tt, e)
  <2>0. /\ i \in 1..Len(acts)
        /\ acts[i].status = "running"
        /\ idx' = idx + 1
        /\ UNCHANGED seat
    BY <1>4 DEF End, Ix
  <2> DEFINE a1 == EndA1(i, s, t)
  <2>1. /\ a1 \in Seq(ActRec)
        /\ Len(a1) = Len(acts)
        /\ Frame(a1)
    BY <1>0, <2>0, EndFacts
  <2>2. acts' = IF acts[i].node = "w" /\ wf = "running" /\ EnabledIn(a1, "e3", i)
                  THEN Append(a1, NewAct(a1, "s", i, "e3", idx + 1))
                  ELSE a1
    BY <1>4 DEF End, EndA1
  <2>3. CASE acts[i].node = "w" /\ wf = "running" /\ EnabledIn(a1, "e3", i)
    <3>1. "s" \in Nodes /\ "e3" \in Edges /\ "s" = Dst["e3"]
      BY EdgeFacts
    <3>2. AddStep(a1, "s", i, "e3")
      BY <2>0, <2>1, <2>2, <2>3, <3>1 DEF AddStep
    <3> QED
      BY <2>0, <2>1, <3>1, <3>2
  <2>4. CASE ~(acts[i].node = "w" /\ wf = "running" /\ EnabledIn(a1, "e3", i))
    <3>1. acts' = a1
      BY <2>2, <2>4
    <3>2. Frame(acts')
      BY <2>1, <3>1 DEF Frame
    <3> QED
      BY <1>0, <2>0, <2>1, <3>1, <3>2
  <2> QED
    BY <2>3, <2>4
<1>5. ASSUME NEW i \in Ix(acts), Finding(i) PROVE \E i2 \in Ix(acts) : Finding(i2)
  BY <1>5
<1>6. ASSUME \/ \E i \in Ix(acts) : OrchGrant(i) \/ DecisionLapse(i)
             \/ \E e \in Chosen : Decide(e)
             \/ OrchLapse \/ Settle
      PROVE  UNCHANGED acts /\ UNCHANGED idx /\ UNCHANGED seat
  BY <1>6 DEF OrchGrant, DecisionLapse, Decide, OrchLapse, Settle
<1>7. ASSUME NEW r \in pending, Apply(r)
      PROVE  \/ /\ acts' \in Seq(ActRec)
                /\ Len(acts') = Len(acts)
                /\ Frame(acts')
                /\ idx' >= idx
                /\ UNCHANGED seat
             \/ \E pre \in Seq(ActRec), n \in Nodes, tt \in 1..Len(acts), e \in Edges : AddStep(pre, n, tt, e)
  <2>0. /\ idx' = idx + 1 /\ UNCHANGED seat
        /\ r \in PendRec /\ r.edge \in Edges
        /\ Dst[r.edge] \in Nodes
    BY <1>7, EdgeFacts DEF Apply, TypeOK, PendRec
  <2>1. CASE ApplyOk(r)
    <3> DEFINE tgt == ApplyTgt(r)
    <3>1. /\ tgt \in OpenEv
          /\ EnabledIn(acts, r.edge, tgt)
          /\ acts' = Append(acts, NewAct(acts, Dst[r.edge], tgt, r.edge, idx + 1))
      BY <1>7, <2>1 DEF Apply, ApplyOk, ApplyTgt, ApplyLive
    <3>2. tgt \in 1..Len(acts)
      BY <3>1, OpenEvNat DEF Ix
    <3>3. Frame(acts) /\ acts \in Seq(ActRec)
      BY <1>0, FrameRefl
    <3>4. AddStep(acts, Dst[r.edge], tgt, r.edge)
      BY <2>0, <3>1, <3>2, <3>3 DEF AddStep
    <3> QED
      BY <2>0, <3>2, <3>3, <3>4
  <2>2. CASE ~ApplyOk(r)
    <3>1. UNCHANGED acts
      BY <1>7, <2>2 DEF Apply, ApplyOk, ApplyTgt, ApplyLive
    <3>2. idx' >= idx
      BY <1>0, <2>0
    <3> QED
      BY <2>0, <3>1, <3>2, <1>q
  <2> QED
    BY <2>1, <2>2
<1> QED
  BY <1>0, <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>q DEF Next

LEMMA InitShape == Init => Shape
<1> SUFFICES ASSUME Init PROVE Shape OBVIOUS
<1>1. acts = <<>> /\ <<>> \in Seq(ActRec) /\ Len(<<>>) = 0
  BY EmptySeq DEF Init
<1>2. TypeOK
  BY <1>1 DEF Init, TypeOK, Lin
<1>3. BeforePromotion
  BY DEF Init, BeforePromotion
<1>4. ActsWF
  BY <1>1 DEF ActsWF, Ix
<1> QED
  BY <1>2, <1>3, <1>4 DEF Shape

LEMMA ActsSeqNext ==
  ASSUME TypeOK, [Next]_vars
  PROVE  acts' \in Seq(ActRec)
<1>0. seat \in [Nodes -> Lin]
  BY DEF TypeOK
<1>1. CASE /\ acts' \in Seq(ActRec)
           /\ Len(acts') = Len(acts)
           /\ Frame(acts')
           /\ idx' >= idx
           /\ UNCHANGED seat
  BY <1>1
<1>2. ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
             AddStep(pre, n, t, e)
      PROVE  acts' \in Seq(ActRec)
  BY <1>2, AddFacts
<1>3. ASSUME NEW st \in Seatings, Promote(st) PROVE acts' \in Seq(ActRec)
  <2> DEFINE x == [node |-> Root, trig |-> 0, via |-> "root", status |-> "ready", st |-> "none",
                   lbl |-> FALSE, truth |-> FALSE, lin |-> st[Root], hist |-> {1},
                   found |-> FALSE, foundAt |-> 0, at |-> 0]
  <2>1. x \in ActRec
    <3>1. st \in [Nodes -> Lin] /\ Root \in Nodes
      BY EdgeFacts DEF Seatings
    <3> QED
      BY <3>1 DEF ActRec, Root
  <2>2. acts' = <<x>>
    BY <1>3 DEF Promote
  <2>3. <<x>> \in Seq(ActRec)
    BY <2>1, RootSeq
  <2> QED
    BY <2>2, <2>3
<1>4. ASSUME NEW i \in Ix(acts), Finding(i) PROVE acts' \in Seq(ActRec)
  BY <1>4, FindingFacts
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, ActsStep

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>0. /\ acts' \in Seq(ActRec)
      /\ acts \in Seq(ActRec)
  BY ActsSeqNext DEF TypeOK
<1>ix. /\ Ix(acts) \subseteq Nat
       /\ OpenEv \subseteq Nat
  BY <1>0, IxNat, OpenEvNat
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>1 DEF TypeOK, vars, budV, orchV, decV
<1>2. ASSUME NEW st \in Seatings, Promote(st) PROVE TypeOK'
  BY <1>0, <1>2 DEF Promote, TypeOK, Seatings, budV, orchV, decV
<1>3. ASSUME NEW i \in Ix(acts), Grant(i) PROVE TypeOK'
  BY <1>0, <1>3 DEF Grant, TypeOK, orchV, decV
<1>4. ASSUME NEW i \in Ix(acts), Finding(i) PROVE TypeOK'
  BY <1>0, <1>4 DEF Finding, TypeOK, budV, orchV, decV
<1>5. ASSUME NEW i \in Ix(acts), OrchGrant(i) PROVE TypeOK'
  <2>1. i \in Nat
    BY <1>ix
  <2>2. CASE Mut = "M_ORCHFREE" \/ CanCharge
    <3>1. /\ orch' = [live |-> TRUE, ev |-> IF Tracker THEN 0 ELSE i, id |-> nRounds + 1]
          /\ nRounds' = nRounds + 1 /\ nAll' = nAll + 1
          /\ nCharged' = IF Mut = "M_ORCHFREE" THEN nCharged ELSE nCharged + 1
          /\ served' = served \cup {i}
          /\ UNCHANGED <<decFailed, exhausted>>
      BY <1>5, <2>2 DEF OrchGrant
    <3> QED
      BY <1>0, <1>5, <2>1, <3>1 DEF OrchGrant, TypeOK
  <2>3. CASE ~(Mut = "M_ORCHFREE" \/ CanCharge)
    <3>1. /\ decFailed' = decFailed \cup {i} /\ exhausted' = TRUE
          /\ UNCHANGED <<orch, nRounds, nAll, nCharged, served>>
      BY <1>5, <2>3 DEF OrchGrant
    <3> QED
      BY <1>0, <1>5, <2>1, <3>1 DEF OrchGrant, TypeOK
  <2> QED
    BY <2>2, <2>3
<1>6. ASSUME NEW i \in Ix(acts), DecisionLapse(i) PROVE TypeOK'
  <2>1. i \in Nat
    BY <1>ix
  <2> QED
    BY <1>0, <1>6, <2>1 DEF DecisionLapse, TypeOK, budV, orchV
<1>7. ASSUME NEW i \in Ix(acts), NEW s \in Sts, NEW t \in BOOLEAN, End(i, s, t) PROVE TypeOK'
  BY <1>0, <1>7 DEF End, TypeOK, budV, orchV, decV
<1>8. ASSUME NEW e \in Chosen, Decide(e) PROVE TypeOK'
  <2>1. DecideEv \in Nat /\ orch.id \in Nat
    BY <1>ix, <1>8 DEF Decide, TypeOK
  <2>2. [edge |-> e, ev |-> DecideEv, round |-> orch.id] \in PendRec
    BY <2>1 DEF PendRec
  <2> QED
    BY <1>0, <1>8, <2>2 DEF Decide, TypeOK, budV, orchV
<1>9. ASSUME NEW r \in pending, Apply(r) PROVE TypeOK'
  <2>0. r \in PendRec /\ r.edge \in Edges
    BY EdgeFacts DEF TypeOK, PendRec
  <2>1. CASE ApplyOk(r)
    <3> DEFINE tgt == ApplyTgt(r)
    <3>1. /\ tgt \in OpenEv
          /\ pending' = pending \ {r}
          /\ idx' = idx + 1
          /\ consumed' = consumed \cup {tgt}
          /\ applied' = applied \cup {[edge |-> r.edge, ev |-> r.ev, to |-> tgt, at |-> idx + 1]}
          /\ orch' = IF Tracker THEN orch ELSE [orch EXCEPT !.live = FALSE]
          /\ UNCHANGED voided
          /\ UNCHANGED <<promoted, seat, wf, budV, nRounds, served, decFailed>>
      BY <1>9, <2>1 DEF Apply, ApplyOk, ApplyTgt, ApplyLive
    <3>2. tgt \in Nat
      BY <1>ix, <3>1
    <3>3. [edge |-> r.edge, ev |-> r.ev, to |-> tgt, at |-> idx + 1] \in AppRec
      BY <2>0, <3>2 DEF TypeOK, PendRec, AppRec
    <3> QED
      BY <1>0, <3>1, <3>2, <3>3 DEF TypeOK, budV
  <2>2. CASE ~ApplyOk(r)
    <3>1. /\ pending' = pending \ {r}
          /\ idx' = idx + 1
          /\ UNCHANGED <<consumed, acts, applied, orch>>
          /\ UNCHANGED <<promoted, seat, wf, budV, nRounds, served, decFailed>>
          /\ \E w \in Whys : voided' = voided \cup {[edge |-> r.edge, why |-> w]}
      BY <1>9, <2>2 DEF Apply, ApplyOk, ApplyTgt, ApplyLive, Whys
    <3> QED
      BY <1>0, <2>0, <3>1 DEF TypeOK, budV
  <2> QED
    BY <2>1, <2>2
<1>10. CASE OrchLapse
  BY <1>0, <1>10 DEF OrchLapse, TypeOK, budV, decV
<1>11. CASE Settle
  BY <1>0, <1>11 DEF Settle, TypeOK, budV, orchV, decV
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. /\ TypeOK /\ TypeOK' /\ BeforePromotion /\ ActsWF
      /\ acts \in Seq(ActRec) /\ idx \in Nat
      /\ seat \in [Nodes -> Lin]
  BY NextTypeOK DEF Shape, TypeOK
<1>b. BeforePromotion'
  <2>1. CASE UNCHANGED vars
    BY <1>0, <2>1 DEF vars, BeforePromotion
  <2>2. ASSUME NEW st \in Seatings, Promote(st) PROVE BeforePromotion'
    BY <2>2 DEF Promote, BeforePromotion
  <2>3. CASE Settle
    BY <2>3 DEF Settle, BeforePromotion
  <2>4. ASSUME \/ \E i \in Ix(acts) : Grant(i) \/ Finding(i) \/ OrchGrant(i) \/ DecisionLapse(i)
               \/ \E i \in Ix(acts), s \in Sts, t \in BOOLEAN : End(i, s, t)
               \/ \E e \in Chosen : Decide(e)
               \/ OrchLapse
        PROVE  BeforePromotion'
    <3> SUFFICES ASSUME ~promoted' PROVE acts' = <<>> /\ wf' = "running"
      BY DEF BeforePromotion
    <3>0. ~promoted
      BY <2>4 DEF Grant, Finding, OrchGrant, DecisionLapse, End, Decide, OrchLapse
    <3>1. acts = <<>> /\ wf = "running"
      BY <1>0, <3>0 DEF BeforePromotion
    <3>2. Ix(acts) = {}
      BY <3>1, EmptySeq DEF Ix
    <3>3. OpenEv = {}
      BY <3>2, OpenEvNat
    <3>4. OrchLapse \/ \E e \in Chosen : Decide(e)
      BY <2>4, <3>2
    <3>5. CASE OrchLapse
      BY <3>1, <3>5 DEF OrchLapse
    <3>6. ASSUME NEW e \in Chosen, Decide(e) PROVE acts' = <<>> /\ wf' = "running"
      <4>1. DecideEv \in OpenEv
        BY <3>6 DEF Decide
      <4> QED
        BY <3>3, <4>1
    <3> QED
      BY <3>4, <3>5, <3>6
  <2>5. ASSUME NEW r \in pending, Apply(r) PROVE BeforePromotion'
    <3> SUFFICES ASSUME ~promoted' PROVE acts' = <<>> /\ wf' = "running"
      BY DEF BeforePromotion
    <3>1. ~promoted /\ UNCHANGED wf
      BY <2>5 DEF Apply
    <3>2. acts = <<>> /\ wf = "running"
      BY <1>0, <3>1 DEF BeforePromotion
    <3>3. Ix(acts) = {}
      BY <3>2, EmptySeq DEF Ix
    <3>4. ~ApplyOk(r)
      BY <3>3, OpenEvNat DEF ApplyOk
    <3>5. UNCHANGED acts
      BY <2>5, <3>4 DEF Apply, ApplyOk, ApplyTgt, ApplyLive
    <3> QED
      BY <3>1, <3>2, <3>5
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, <2>5 DEF Next
<1>a. ActsWF'
  <2>u. ASSUME acts' \in Seq(ActRec), Len(acts') = Len(acts), Frame(acts'), idx' >= idx, UNCHANGED seat
        PROVE  ActsWF'
    <3> SUFFICES ASSUME NEW j \in Ix(acts')
                 PROVE  /\ acts'[j].at <= idx'
                        /\ acts'[j].hist \subseteq 1..j
                        /\ acts'[j].lin = seat'[acts'[j].node]
                        /\ j > 1 => /\ acts'[j].trig \in 1..(j - 1)
                                    /\ acts'[j].via \in Edges
                                    /\ acts'[j].node = Dst[acts'[j].via]
                                    /\ acts'[acts'[j].trig].node = Src[acts'[j].via]
                                    /\ acts'[acts'[j].trig].status = "ended"
      BY DEF ActsWF
    <3>1. j \in 1..Len(acts)
      BY <2>u DEF Ix
    <3>2. FixedR(j, acts'[j])
      BY <2>u, <3>1 DEF Frame
    <3>3. /\ acts[j].at <= idx
          /\ acts[j].hist \subseteq 1..j
          /\ acts[j].lin = seat[acts[j].node]
          /\ j > 1 => /\ acts[j].trig \in 1..(j - 1)
                      /\ acts[j].via \in Edges
                      /\ acts[j].node = Dst[acts[j].via]
                      /\ acts[acts[j].trig].node = Src[acts[j].via]
                      /\ acts[acts[j].trig].status = "ended"
      BY <1>0, <3>1 DEF ActsWF, Ix
    <3>4. /\ Len(acts) \in Nat /\ j \in Nat
          /\ acts[j] \in ActRec
          /\ idx \in Nat /\ idx' \in Nat
      BY <1>0, <2>u, <3>1, SeqFacts DEF TypeOK
    <3>5. /\ acts'[j].at <= idx'
          /\ acts'[j].hist \subseteq 1..j
          /\ acts'[j].lin = seat'[acts'[j].node]
      BY <2>u, <3>2, <3>3, <3>4 DEF FixedR, ActRec
    <3>6. ASSUME j > 1
          PROVE  /\ acts'[j].trig \in 1..(j - 1)
                 /\ acts'[j].via \in Edges
                 /\ acts'[j].node = Dst[acts'[j].via]
                 /\ acts'[acts'[j].trig].node = Src[acts'[j].via]
                 /\ acts'[acts'[j].trig].status = "ended"
      <4>1. /\ acts[j].trig \in 1..(j - 1)
            /\ acts'[j].trig = acts[j].trig
            /\ acts'[j].via = acts[j].via
            /\ acts'[j].node = acts[j].node
        BY <3>2, <3>3, <3>6 DEF FixedR
      <4>2. acts[j].trig \in 1..Len(acts)
        BY <3>1, <3>4, <4>1
      <4>3. FixedR(acts[j].trig, acts'[acts[j].trig])
        BY <2>u, <4>2 DEF Frame
      <4>4. /\ acts'[acts[j].trig].node = acts[acts[j].trig].node
            /\ acts'[acts[j].trig].status = "ended"
        BY <3>3, <3>6, <4>3 DEF FixedR
      <4> QED
        BY <3>3, <3>6, <4>1, <4>4
    <3> QED
      BY <3>5, <3>6
  <2>n. ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
               AddStep(pre, n, t, e)
        PROVE  ActsWF'
    <3> DEFINE nw == NewAct(pre, n, t, e, idx + 1)
    <3>0. /\ nw \in ActRec
          /\ acts' \in Seq(ActRec)
          /\ Len(acts') = Len(acts) + 1
          /\ \A k \in 1..Len(acts) : acts'[k] = pre[k]
          /\ acts'[Len(acts) + 1] = nw
      BY <1>0, <2>n, AddFacts
    <3>1. /\ Len(pre) = Len(acts) /\ Frame(pre) /\ t \in 1..Len(acts) /\ n = Dst[e]
          /\ EnabledIn(pre, e, t)
          /\ idx' = idx + 1 /\ UNCHANGED seat
      BY <2>n DEF AddStep
    <3>2. Len(acts) \in Nat /\ t \in Nat
      BY <1>0, SeqFacts
    <3> SUFFICES ASSUME NEW j \in Ix(acts')
                 PROVE  /\ acts'[j].at <= idx'
                        /\ acts'[j].hist \subseteq 1..j
                        /\ acts'[j].lin = seat'[acts'[j].node]
                        /\ j > 1 => /\ acts'[j].trig \in 1..(j - 1)
                                    /\ acts'[j].via \in Edges
                                    /\ acts'[j].node = Dst[acts'[j].via]
                                    /\ acts'[acts'[j].trig].node = Src[acts'[j].via]
                                    /\ acts'[acts'[j].trig].status = "ended"
      BY DEF ActsWF
    <3>3. j \in 1..Len(acts) \/ j = Len(acts) + 1
      BY <3>0, <3>2 DEF Ix
    <3>4. CASE j = Len(acts) + 1
      <4>1. acts'[j] = nw
        BY <3>0, <3>4
      <4>2. /\ nw.node = n /\ nw.trig = t /\ nw.via = e /\ nw.lin = seat[n] /\ nw.at = idx + 1
            /\ nw.hist = {Len(pre) + 1} \cup pre[t].hist
        BY DEF NewAct
      <4>3. /\ FixedR(t, pre[t])
            /\ pre[t] \in ActRec
            /\ acts[t].hist \subseteq 1..t
            /\ acts[t].lin = seat[acts[t].node]
            /\ acts'[t] = pre[t]
        BY <1>0, <3>0, <3>1, SeqFacts DEF Frame, ActsWF, Ix
      <4>4. pre[t].hist \subseteq 1..t
        BY <4>3 DEF FixedR
      <4>5. nw.hist \subseteq 1..j
        BY <3>1, <3>2, <3>4, <4>2, <4>4
      <4>6. /\ pre[t].node = Src[e] /\ pre[t].status = "ended"
        BY <3>1 DEF EnabledIn
      <4> QED
        BY <1>0, <3>1, <3>2, <3>4, <4>1, <4>2, <4>3, <4>5, <4>6 DEF TypeOK
    <3>5. CASE j \in 1..Len(acts)
      <4>1. acts'[j] = pre[j] /\ FixedR(j, pre[j])
        BY <3>0, <3>1, <3>5 DEF Frame
      <4>2. /\ acts[j].at <= idx
            /\ acts[j].hist \subseteq 1..j
            /\ acts[j].lin = seat[acts[j].node]
            /\ j > 1 => /\ acts[j].trig \in 1..(j - 1)
                        /\ acts[j].via \in Edges
                        /\ acts[j].node = Dst[acts[j].via]
                        /\ acts[acts[j].trig].node = Src[acts[j].via]
                        /\ acts[acts[j].trig].status = "ended"
        BY <1>0, <3>5 DEF ActsWF, Ix
      <4>3. acts[j] \in ActRec /\ idx \in Nat /\ j \in Nat
        BY <1>0, <3>2, <3>5, SeqFacts
      <4>4. /\ acts'[j].at <= idx'
            /\ acts'[j].hist \subseteq 1..j
            /\ acts'[j].lin = seat'[acts'[j].node]
        BY <3>1, <4>1, <4>2, <4>3 DEF FixedR, ActRec
      <4>5. ASSUME j > 1
            PROVE  /\ acts'[j].trig \in 1..(j - 1)
                   /\ acts'[j].via \in Edges
                   /\ acts'[j].node = Dst[acts'[j].via]
                   /\ acts'[acts'[j].trig].node = Src[acts'[j].via]
                   /\ acts'[acts'[j].trig].status = "ended"
        <5>1. /\ acts[j].trig \in 1..(j - 1)
              /\ acts'[j].trig = acts[j].trig
              /\ acts'[j].via = acts[j].via
              /\ acts'[j].node = acts[j].node
          BY <4>1, <4>2, <4>5 DEF FixedR
        <5>2. acts[j].trig \in 1..Len(acts)
          BY <3>2, <3>5, <4>3, <5>1
        <5>3. FixedR(acts[j].trig, pre[acts[j].trig]) /\ acts'[acts[j].trig] = pre[acts[j].trig]
          BY <3>0, <3>1, <5>2 DEF Frame
        <5>4. /\ acts'[acts[j].trig].node = acts[acts[j].trig].node
              /\ acts'[acts[j].trig].status = "ended"
          BY <4>2, <4>5, <5>3 DEF FixedR
        <5> QED
          BY <4>2, <4>5, <5>1, <5>4
      <4> QED
        BY <4>4, <4>5
    <3> QED
      BY <3>3, <3>4, <3>5
  <2>p. ASSUME NEW st \in Seatings, Promote(st) PROVE ActsWF'
    <3> DEFINE x == [node |-> Root, trig |-> 0, via |-> "root", status |-> "ready", st |-> "none",
                     lbl |-> FALSE, truth |-> FALSE, lin |-> st[Root], hist |-> {1},
                     found |-> FALSE, foundAt |-> 0, at |-> 0]
    <3>1. x \in ActRec
      <4>1. st \in [Nodes -> Lin] /\ Root \in Nodes
        BY EdgeFacts DEF Seatings
      <4> QED
        BY <4>1 DEF ActRec, Root
    <3>2. acts' = <<x>> /\ seat' = st /\ UNCHANGED idx
      BY <2>p DEF Promote
    <3>3. Len(<<x>>) = 1 /\ <<x>>[1] = x
      BY <3>1, RootSeq
    <3>4. Ix(acts') = {1} /\ acts'[1] = x
      BY <3>2, <3>3 DEF Ix
    <3> SUFFICES ASSUME NEW j \in Ix(acts')
                 PROVE  /\ acts'[j].at <= idx'
                        /\ acts'[j].hist \subseteq 1..j
                        /\ acts'[j].lin = seat'[acts'[j].node]
                        /\ j > 1 => FALSE
      BY DEF ActsWF
    <3>5. j = 1 /\ idx \in Nat
      BY <1>0, <3>4
    <3> QED
      BY <3>2, <3>4, <3>5
  <2>f. ASSUME NEW i \in Ix(acts), Finding(i) PROVE ActsWF'
    <3>0. /\ acts' \in Seq(ActRec) /\ Len(acts') = Len(acts) /\ idx' = idx + 1 /\ UNCHANGED seat
          /\ \A j \in Ix(acts) : /\ acts'[j].node = acts[j].node
                                 /\ acts'[j].trig = acts[j].trig
                                 /\ acts'[j].via = acts[j].via
                                 /\ acts'[j].lin = acts[j].lin
                                 /\ acts'[j].hist = acts[j].hist
                                 /\ acts'[j].at = acts[j].at
                                 /\ acts'[j].status = acts[j].status
      BY <1>0, <2>f, FindingFacts
    <3> SUFFICES ASSUME NEW j \in Ix(acts')
                 PROVE  /\ acts'[j].at <= idx'
                        /\ acts'[j].hist \subseteq 1..j
                        /\ acts'[j].lin = seat'[acts'[j].node]
                        /\ j > 1 => /\ acts'[j].trig \in 1..(j - 1)
                                    /\ acts'[j].via \in Edges
                                    /\ acts'[j].node = Dst[acts'[j].via]
                                    /\ acts'[acts'[j].trig].node = Src[acts'[j].via]
                                    /\ acts'[acts'[j].trig].status = "ended"
      BY DEF ActsWF
    <3>1. j \in Ix(acts)
      BY <3>0 DEF Ix
    <3>2. /\ acts[j].at <= idx
          /\ acts[j].hist \subseteq 1..j
          /\ acts[j].lin = seat[acts[j].node]
          /\ j > 1 => /\ acts[j].trig \in 1..(j - 1)
                      /\ acts[j].via \in Edges
                      /\ acts[j].node = Dst[acts[j].via]
                      /\ acts[acts[j].trig].node = Src[acts[j].via]
                      /\ acts[acts[j].trig].status = "ended"
      BY <1>0, <3>1 DEF ActsWF
    <3>3. acts[j] \in ActRec /\ idx \in Nat /\ Len(acts) \in Nat /\ j \in Nat
      BY <1>0, <3>1, IxNat, SeqFacts
    <3>4. /\ acts'[j].at <= idx'
          /\ acts'[j].hist \subseteq 1..j
          /\ acts'[j].lin = seat'[acts'[j].node]
      BY <3>0, <3>1, <3>2, <3>3 DEF ActRec
    <3>5. ASSUME j > 1
          PROVE  /\ acts'[j].trig \in 1..(j - 1)
                 /\ acts'[j].via \in Edges
                 /\ acts'[j].node = Dst[acts'[j].via]
                 /\ acts'[acts'[j].trig].node = Src[acts'[j].via]
                 /\ acts'[acts'[j].trig].status = "ended"
      <4>1. /\ acts[j].trig \in 1..(j - 1)
            /\ acts'[j].trig = acts[j].trig
            /\ acts'[j].via = acts[j].via
            /\ acts'[j].node = acts[j].node
        BY <3>0, <3>1, <3>2, <3>5
      <4>2. acts[j].trig \in Ix(acts)
        BY <3>1, <3>3, <4>1 DEF Ix
      <4>3. /\ acts'[acts[j].trig].node = acts[acts[j].trig].node
            /\ acts'[acts[j].trig].status = acts[acts[j].trig].status
        BY <3>0, <4>2
      <4> QED
        BY <3>2, <3>5, <4>1, <4>3
    <3> QED
      BY <3>4, <3>5
  <2> QED
    BY <1>0, <2>u, <2>n, <2>p, <2>f, ActsStep
<1> QED
  BY <1>0, <1>b, <1>a DEF Shape
-----------------------------------------------------------------------------
\* --- The budget ---------------------------------------------------------------
LEMMA NextInvB ==
  ASSUME Mut # "M_OVERRUN", Mut # "M_ORCHFREE", TypeOK, InvB, [Next]_vars
  PROVE  InvB'
<1>0. nAll \in Nat /\ nCharged \in Nat /\ nAll = nCharged /\ nCharged <= N /\ N \in Nat
  BY DEF TypeOK, InvB, N
<1>c. CanCharge => nCharged < N
  BY DEF CanCharge
<1>1. ASSUME NEW i \in Ix(acts), Grant(i) PROVE InvB'
  <2>1. CASE CanCharge
    <3>1. nCharged' = nCharged + 1 /\ nAll' = nAll + 1
      BY <1>1, <2>1 DEF Grant
    <3> QED
      BY <1>0, <1>c, <2>1, <3>1 DEF InvB
  <2>2. CASE ~CanCharge
    <3>1. UNCHANGED <<nCharged, nAll>>
      BY <1>1, <2>2 DEF Grant
    <3> QED
      BY <1>0, <3>1 DEF InvB
  <2> QED
    BY <2>1, <2>2
<1>2. ASSUME NEW i \in Ix(acts), OrchGrant(i) PROVE InvB'
  <2>1. CASE CanCharge
    <3>1. nCharged' = nCharged + 1 /\ nAll' = nAll + 1
      BY <1>2, <2>1 DEF OrchGrant
    <3> QED
      BY <1>0, <1>c, <2>1, <3>1 DEF InvB
  <2>2. CASE ~CanCharge
    <3>1. UNCHANGED <<nCharged, nAll>>
      BY <1>2, <2>2 DEF OrchGrant
    <3> QED
      BY <1>0, <3>1 DEF InvB
  <2> QED
    BY <2>1, <2>2
<1>3. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E i \in Ix(acts) : Finding(i) \/ DecisionLapse(i)
             \/ \E i \in Ix(acts), s \in Sts, t \in BOOLEAN : End(i, s, t)
             \/ \E e \in Chosen : Decide(e)
             \/ \E r \in pending : Apply(r)
             \/ OrchLapse \/ Settle
             \/ UNCHANGED vars
      PROVE  UNCHANGED <<nCharged, nAll>>
  BY <1>3 DEF Promote, Finding, DecisionLapse, End, Decide, Apply, OrchLapse, Settle, vars, budV
<1>4. ASSUME UNCHANGED <<nCharged, nAll>> PROVE InvB'
  BY <1>0, <1>4 DEF InvB
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Next

THEOREM BudgetBoundAlways ==
  ASSUME Mut # "M_OVERRUN", Mut # "M_ORCHFREE"
  PROVE  Spec => []BudgetBound
<1>1. TypeOK /\ InvB /\ [Next]_vars => TypeOK' /\ InvB'
  BY NextTypeOK, NextInvB
<1>2. Init => TypeOK /\ InvB
  BY InitShape DEF Init, Shape, InvB, N
<1>3. InvB => BudgetBound
  BY DEF InvB, BudgetBound
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
\* --- Completion ---------------------------------------------------------------
LEMMA SinkEndedFrozen ==
  ASSUME Shape, [Next]_vars
  PROVE  SinkEnded => SinkEnded'
<1> SUFFICES ASSUME SinkEnded PROVE SinkEnded' OBVIOUS
<1>0. /\ TypeOK /\ acts \in Seq(ActRec) /\ BeforePromotion
      /\ Len(acts) \in Nat
  BY SeqFacts DEF Shape, TypeOK
<1>1. PICK i \in Ix(acts) : acts[i].node = Sink /\ acts[i].status = "ended"
  BY DEF SinkEnded
<1>2. ASSUME acts' \in Seq(ActRec), Len(acts') = Len(acts), Frame(acts')
      PROVE  SinkEnded'
  <2>1. i \in 1..Len(acts) /\ FixedR(i, acts'[i])
    BY <1>1, <1>2 DEF Ix, Frame
  <2>2. acts'[i].node = Sink /\ acts'[i].status = "ended"
    BY <1>1, <2>1 DEF FixedR
  <2>3. i \in Ix(acts')
    BY <1>2, <2>1 DEF Ix
  <2> QED
    BY <2>2, <2>3 DEF SinkEnded
<1>3. ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
             AddStep(pre, n, t, e)
      PROVE  SinkEnded'
  <2>1. /\ acts' \in Seq(ActRec)
        /\ Len(acts') = Len(acts) + 1
        /\ \A k \in 1..Len(acts) : acts'[k] = pre[k]
    BY <1>0, <1>3, AddFacts
  <2>2. i \in 1..Len(acts) /\ FixedR(i, pre[i])
    BY <1>1, <1>3 DEF Ix, AddStep, Frame
  <2>3. acts'[i].node = Sink /\ acts'[i].status = "ended"
    BY <1>1, <2>1, <2>2 DEF FixedR
  <2>4. i \in Ix(acts')
    BY <1>0, <2>1, <2>2 DEF Ix
  <2> QED
    BY <2>3, <2>4 DEF SinkEnded
<1>4. ASSUME NEW st \in Seatings, Promote(st) PROVE SinkEnded'
  <2>1. ~promoted
    BY <1>4 DEF Promote
  <2>2. Ix(acts) = {}
    BY <1>0, <2>1, EmptySeq DEF BeforePromotion, Ix
  <2> QED
    BY <1>1, <2>2
<1>5. ASSUME NEW m \in Ix(acts), Finding(m) PROVE SinkEnded'
  <2>1. /\ acts' \in Seq(ActRec) /\ Len(acts') = Len(acts)
        /\ acts'[i].node = acts[i].node /\ acts'[i].status = acts[i].status
    BY <1>0, <1>1, <1>5, FindingFacts
  <2>2. i \in Ix(acts')
    BY <1>1, <2>1 DEF Ix
  <2> QED
    BY <1>1, <2>1, <2>2 DEF SinkEnded
<1> QED
  BY <1>0, <1>2, <1>3, <1>4, <1>5, ActsStep

LEMMA NextCompletedOnlyBySink ==
  ASSUME Mut # "M_BUDGETDONE", Shape, CompletedOnlyBySink, [Next]_vars
  PROVE  CompletedOnlyBySink'
<1>0. /\ TypeOK /\ BeforePromotion /\ (SinkEnded => SinkEnded')
  BY SinkEndedFrozen DEF Shape
<1>1. CASE Settle
  <2>1. CASE SinkEnded /\ wf' = "completed"
    BY <1>0, <2>1 DEF CompletedOnlyBySink
  <2>2. CASE /\ ~SinkEnded /\ (exhausted \/ Quiescent)
             /\ wf' = IF Mut = "M_BUDGETDONE" /\ exhausted THEN "completed" ELSE "failed"
    BY <2>2 DEF CompletedOnlyBySink
  <2> QED
    BY <1>1, <2>1, <2>2 DEF Settle
<1>2. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E i \in Ix(acts) : Grant(i) \/ Finding(i) \/ OrchGrant(i) \/ DecisionLapse(i)
             \/ \E i \in Ix(acts), s \in Sts, t \in BOOLEAN : End(i, s, t)
             \/ \E e \in Chosen : Decide(e)
             \/ \E r \in pending : Apply(r)
             \/ OrchLapse \/ UNCHANGED vars
      PROVE  UNCHANGED wf
  BY <1>2 DEF Promote, Grant, Finding, OrchGrant, DecisionLapse, End, Decide, Apply, OrchLapse, vars
<1>3. ASSUME UNCHANGED wf PROVE CompletedOnlyBySink'
  BY <1>0, <1>3 DEF CompletedOnlyBySink
<1> QED
  BY <1>1, <1>2, <1>3 DEF Next

THEOREM CompletedOnlyBySinkAlways ==
  ASSUME Mut # "M_BUDGETDONE"
  PROVE  Spec => []CompletedOnlyBySink
<1>1. Shape /\ CompletedOnlyBySink /\ [Next]_vars => Shape' /\ CompletedOnlyBySink'
  BY NextShape, NextCompletedOnlyBySink
<1>2. Init => Shape /\ CompletedOnlyBySink
  BY InitShape DEF Init, CompletedOnlyBySink
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
\* --- A route consumes its own event -------------------------------------------
LEMMA NextRouteOnItsEvent ==
  ASSUME Mut # "M_TRACKER", RouteOnItsEvent, [Next]_vars
  PROVE  RouteOnItsEvent'
<1>t. ~Tracker
  BY DEF Tracker
<1>1. ASSUME NEW r \in pending, Apply(r) PROVE RouteOnItsEvent'
  <2>1. ApplyTgt(r) = r.ev
    BY <1>t DEF ApplyTgt
  <2>2. CASE ApplyOk(r)
    <3>1. applied' = applied \cup {[edge |-> r.edge, ev |-> r.ev, to |-> ApplyTgt(r), at |-> idx + 1]}
      BY <1>1, <2>2 DEF Apply, ApplyOk, ApplyTgt, ApplyLive
    <3> QED
      BY <2>1, <3>1 DEF RouteOnItsEvent
  <2>3. CASE ~ApplyOk(r)
    <3>1. UNCHANGED applied
      BY <1>1, <2>3 DEF Apply, ApplyOk, ApplyTgt, ApplyLive
    <3> QED
      BY <3>1 DEF RouteOnItsEvent
  <2> QED
    BY <2>2, <2>3
<1>2. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E i \in Ix(acts) : Grant(i) \/ Finding(i) \/ OrchGrant(i) \/ DecisionLapse(i)
             \/ \E i \in Ix(acts), s \in Sts, t \in BOOLEAN : End(i, s, t)
             \/ \E e \in Chosen : Decide(e)
             \/ OrchLapse \/ Settle \/ UNCHANGED vars
      PROVE  UNCHANGED applied
  BY <1>2 DEF Promote, Grant, Finding, OrchGrant, DecisionLapse, End, Decide, OrchLapse, Settle, vars, decV
<1>3. ASSUME UNCHANGED applied PROVE RouteOnItsEvent'
  BY <1>3 DEF RouteOnItsEvent
<1> QED
  BY <1>1, <1>2, <1>3 DEF Next

THEOREM RouteOnItsEventAlways ==
  ASSUME Mut # "M_TRACKER"
  PROVE  Spec => []RouteOnItsEvent
<1>1. RouteOnItsEvent /\ [Next]_vars => RouteOnItsEvent'
  BY NextRouteOnItsEvent
<1>2. Init => RouteOnItsEvent
  BY DEF Init, RouteOnItsEvent
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
\* --- No activation after a finding ---------------------------------------------
LEMMA NextNoActivationAfterFinding ==
  ASSUME Mut # "M_SOURCEONLY", Shape, NoActivationAfterFinding, [Next]_vars
  PROVE  NoActivationAfterFinding'
<1>0. /\ TypeOK /\ ActsWF
      /\ acts \in Seq(ActRec) /\ Len(acts) \in Nat /\ idx \in Nat
  BY SeqFacts DEF Shape, TypeOK
<1>w. ASSUME NEW j \in Ix(acts), j > 1, NEW b \in acts[acts[j].trig].hist
      PROVE  /\ acts[j].trig \in Ix(acts)
             /\ b \in Ix(acts)
             /\ acts[j].at \in Nat /\ acts[j].at <= idx
             /\ ~acts[b].found \/ acts[b].foundAt > acts[j].at
  <2>1. j \in 1..Len(acts) /\ acts[j].trig \in 1..(j - 1) /\ acts[j].at <= idx /\ acts[j] \in ActRec
    BY <1>0, <1>w, SeqFacts DEF ActsWF, Ix
  <2>2. acts[j].trig \in 1..Len(acts) /\ acts[j].trig \in Ix(acts)
    BY <1>0, <2>1 DEF Ix
  <2>3. acts[acts[j].trig].hist \subseteq 1..acts[j].trig
    BY <1>0, <2>2 DEF ActsWF, Ix
  <2>4. b \in Ix(acts)
    BY <1>0, <1>w, <2>1, <2>2, <2>3 DEF Ix
  <2>5. acts[j].at \in Nat
    BY <2>1 DEF ActRec
  <2>6. ~acts[b].found \/ acts[b].foundAt > acts[j].at
    BY <1>w DEF NoActivationAfterFinding
  <2> QED
    BY <2>1, <2>2, <2>4, <2>5, <2>6
<1>u. ASSUME acts' \in Seq(ActRec), Len(acts') = Len(acts), Frame(acts')
      PROVE  NoActivationAfterFinding'
  <2> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, NEW b \in acts'[acts'[j].trig].hist
               PROVE  ~acts'[b].found \/ acts'[b].foundAt > acts'[j].at
    BY DEF NoActivationAfterFinding
  <2>1. j \in 1..Len(acts) /\ j \in Ix(acts) /\ FixedR(j, acts'[j])
    BY <1>u DEF Ix, Frame
  <2>2. acts'[j].trig = acts[j].trig /\ acts'[j].at = acts[j].at
    BY <2>1 DEF FixedR
  <2>3. /\ acts[j].trig \in 1..(j - 1) /\ acts[j].trig \in 1..Len(acts)
    BY <1>0, <2>1 DEF ActsWF, Ix
  <2>4. FixedR(acts[j].trig, acts'[acts[j].trig])
    BY <1>u, <2>3 DEF Frame
  <2>5. acts'[acts[j].trig].hist = acts[acts[j].trig].hist
    BY <2>4 DEF FixedR
  <2>6. b \in acts[acts[j].trig].hist
    BY <2>2, <2>5
  <2>7. /\ b \in Ix(acts)
        /\ ~acts[b].found \/ acts[b].foundAt > acts[j].at
    BY <2>1, <2>6, <1>w
  <2>8. FixedR(b, acts'[b])
    BY <1>u, <2>7 DEF Frame, Ix
  <2> QED
    BY <2>2, <2>7, <2>8 DEF FixedR
<1>n. ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
             AddStep(pre, n, t, e)
      PROVE  NoActivationAfterFinding'
  <2> DEFINE nw == NewAct(pre, n, t, e, idx + 1)
  <2>0. /\ nw \in ActRec
        /\ acts' \in Seq(ActRec)
        /\ Len(acts') = Len(acts) + 1
        /\ \A k \in 1..Len(acts) : acts'[k] = pre[k]
        /\ acts'[Len(acts) + 1] = nw
    BY <1>0, <1>n, AddFacts
  <2>1. Len(pre) = Len(acts) /\ Frame(pre) /\ EnabledIn(pre, e, t)
    BY <1>n DEF AddStep
  <2>2. Unfound(pre, t)
    BY <2>1 DEF EnabledIn
  <2>3. \A c \in pre[t].hist : ~pre[c].found
    BY <2>2 DEF Unfound
  <2> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, NEW b \in acts'[acts'[j].trig].hist
               PROVE  ~acts'[b].found \/ acts'[b].foundAt > acts'[j].at
    BY DEF NoActivationAfterFinding
  <2>4. j \in 1..Len(acts) \/ j = Len(acts) + 1
    BY <1>0, <2>0 DEF Ix
  <2>5. CASE j = Len(acts) + 1
    <3>1. acts'[j] = nw /\ nw.trig = t
      BY <2>0, <2>5 DEF NewAct
    <3>2. /\ acts'[t] = pre[t]
          /\ FixedR(t, pre[t])
          /\ acts[t].hist \subseteq 1..t
      BY <1>0, <2>0, <2>1 DEF Frame, ActsWF, Ix
    <3>3. b \in pre[t].hist /\ pre[t].hist \subseteq 1..t
      BY <3>1, <3>2 DEF FixedR
    <3>4. b \in 1..Len(acts)
      BY <1>0, <3>3
    <3>5. ~pre[b].found /\ acts'[b] = pre[b]
      BY <2>0, <2>3, <3>3, <3>4
    <3> QED
      BY <3>5
  <2>6. CASE j \in 1..Len(acts)
    <3>1. acts'[j] = pre[j] /\ FixedR(j, pre[j]) /\ j \in Ix(acts)
      BY <2>0, <2>1, <2>6 DEF Frame, Ix
    <3>2. /\ acts'[j].trig = acts[j].trig /\ acts'[j].at = acts[j].at
      BY <3>1 DEF FixedR
    <3>3. acts[j].trig \in 1..Len(acts) /\ acts[j].trig \in 1..(j - 1)
      BY <1>0, <2>6, <3>1 DEF ActsWF, Ix
    <3>4. FixedR(acts[j].trig, pre[acts[j].trig]) /\ acts'[acts[j].trig] = pre[acts[j].trig]
      BY <2>0, <2>1, <3>3 DEF Frame
    <3>5. b \in acts[acts[j].trig].hist
      BY <3>2, <3>4 DEF FixedR
    <3>6. /\ b \in Ix(acts)
          /\ ~acts[b].found \/ acts[b].foundAt > acts[j].at
      BY <3>1, <3>5, <1>w, <2>6
    <3>7. acts'[b] = pre[b] /\ FixedR(b, pre[b])
      BY <2>0, <2>1, <3>6 DEF Frame, Ix
    <3> QED
      BY <3>2, <3>6, <3>7 DEF FixedR
  <2> QED
    BY <2>4, <2>5, <2>6
<1>p. ASSUME NEW st \in Seatings, Promote(st) PROVE NoActivationAfterFinding'
  <2> DEFINE x == [node |-> Root, trig |-> 0, via |-> "root", status |-> "ready", st |-> "none",
                   lbl |-> FALSE, truth |-> FALSE, lin |-> st[Root], hist |-> {1},
                   found |-> FALSE, foundAt |-> 0, at |-> 0]
  <2>1. x \in ActRec
    <3>1. st \in [Nodes -> Lin] /\ Root \in Nodes
      BY EdgeFacts DEF Seatings
    <3> QED
      BY <3>1 DEF ActRec, Root
  <2>2. acts' = <<x>>
    BY <1>p DEF Promote
  <2>3. Len(<<x>>) = 1
    BY <2>1, RootSeq
  <2>4. \A j \in Ix(acts') : ~(j > 1)
    BY <2>2, <2>3 DEF Ix
  <2> QED
    BY <2>4 DEF NoActivationAfterFinding
<1>f. ASSUME NEW i \in Ix(acts), Finding(i) PROVE NoActivationAfterFinding'
  <2>0. /\ acts' \in Seq(ActRec) /\ Len(acts') = Len(acts)
        /\ ~acts[i].found
        /\ acts'[i].foundAt = idx + 1
        /\ acts'[i].found = TRUE
        /\ \A k \in Ix(acts) : k # i => acts'[k] = acts[k]
        /\ \A k \in Ix(acts) : /\ acts'[k].trig = acts[k].trig
                               /\ acts'[k].hist = acts[k].hist
                               /\ acts'[k].at = acts[k].at
    BY <1>0, <1>f, FindingFacts
  <2> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, NEW b \in acts'[acts'[j].trig].hist
               PROVE  ~acts'[b].found \/ acts'[b].foundAt > acts'[j].at
    BY DEF NoActivationAfterFinding
  <2>1. j \in Ix(acts)
    BY <2>0 DEF Ix
  <2>2. acts'[j].trig = acts[j].trig /\ acts'[j].at = acts[j].at
    BY <2>0, <2>1
  <2>3. acts[j].trig \in 1..Len(acts) /\ acts[j].trig \in Ix(acts)
    <3>1. acts[j].trig \in 1..(j - 1)
      BY <1>0, <2>1 DEF ActsWF
    <3> QED
      BY <1>0, <2>1, <3>1 DEF Ix
  <2>4. acts'[acts[j].trig].hist = acts[acts[j].trig].hist
    BY <2>0, <2>3
  <2>5. b \in acts[acts[j].trig].hist
    BY <2>2, <2>4
  <2>6. /\ b \in Ix(acts)
        /\ acts[j].at \in Nat /\ acts[j].at <= idx
        /\ ~acts[b].found \/ acts[b].foundAt > acts[j].at
    BY <2>1, <2>5, <1>w
  <2>7. CASE b = i
    BY <1>0, <2>0, <2>2, <2>6, <2>7
  <2>8. CASE b # i
    <3>1. acts'[b] = acts[b]
      BY <2>0, <2>6, <2>8
    <3> QED
      BY <2>2, <2>6, <3>1
  <2> QED
    BY <2>7, <2>8
<1> QED
  BY <1>0, <1>u, <1>n, <1>p, <1>f, ActsStep

THEOREM NoActivationAfterFindingAlways ==
  ASSUME Mut # "M_SOURCEONLY"
  PROVE  Spec => []NoActivationAfterFinding
<1>1. Shape /\ NoActivationAfterFinding /\ [Next]_vars => Shape' /\ NoActivationAfterFinding'
  BY NextShape, NextNoActivationAfterFinding
<1>2. Init => Shape /\ NoActivationAfterFinding
  BY InitShape DEF Init, NoActivationAfterFinding, Ix
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
\* --- Taint --------------------------------------------------------------------
LEMMA NextInvT ==
  ASSUME Mut # "M_FORGETTAINT", Shape, InvT, [Next]_vars
  PROVE  InvT'
<1>0. /\ TypeOK /\ ActsWF /\ LabelCoversTruth /\ TaintedNeverOutward
      /\ acts \in Seq(ActRec) /\ Len(acts) \in Nat
  BY SeqFacts DEF Shape, TypeOK, InvT
<1>u. ASSUME acts' \in Seq(ActRec), Len(acts') = Len(acts), Frame(acts') PROVE InvT'
  <2>1. LabelCoversTruth'
    <3> SUFFICES ASSUME NEW j \in Ix(acts') PROVE acts'[j].truth => acts'[j].lbl
      BY DEF LabelCoversTruth
    <3>1. j \in 1..Len(acts) /\ FixedR(j, acts'[j])
      BY <1>u DEF Ix, Frame
    <3>2. acts[j].truth => acts[j].lbl
      BY <1>0, <3>1 DEF LabelCoversTruth, Ix
    <3> QED
      BY <3>1, <3>2 DEF FixedR
  <2>2. TaintedNeverOutward'
    <3> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, acts'[j].node \in Outward
                 PROVE  ~acts'[acts'[j].trig].truth
      BY DEF TaintedNeverOutward
    <3>1. j \in 1..Len(acts) /\ j \in Ix(acts) /\ FixedR(j, acts'[j])
      BY <1>u DEF Ix, Frame
    <3>2. acts'[j].trig = acts[j].trig /\ acts'[j].node = acts[j].node
      BY <3>1 DEF FixedR
    <3>3. /\ acts[j].trig \in 1..(j - 1)
          /\ acts[acts[j].trig].status = "ended"
          /\ ~acts[acts[j].trig].truth
      BY <1>0, <3>1, <3>2 DEF ActsWF, TaintedNeverOutward
    <3>4. acts[j].trig \in 1..Len(acts)
      BY <1>0, <3>1, <3>3
    <3>5. FixedR(acts[j].trig, acts'[acts[j].trig])
      BY <1>u, <3>4 DEF Frame
    <3>6. acts'[acts[j].trig].truth = acts[acts[j].trig].truth
      BY <3>3, <3>5 DEF FixedR
    <3> QED
      BY <3>2, <3>3, <3>6
  <2> QED
    BY <2>1, <2>2 DEF InvT
<1>n. ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
             AddStep(pre, n, t, e)
      PROVE  InvT'
  <2> DEFINE nw == NewAct(pre, n, t, e, idx + 1)
  <2>0. /\ nw \in ActRec
        /\ acts' \in Seq(ActRec)
        /\ Len(acts') = Len(acts) + 1
        /\ \A k \in 1..Len(acts) : acts'[k] = pre[k]
        /\ acts'[Len(acts) + 1] = nw
    BY <1>0, <1>n, AddFacts
  <2>1. /\ Len(pre) = Len(acts) /\ Frame(pre) /\ EnabledIn(pre, e, t) /\ n = Dst[e]
    BY <1>n DEF AddStep
  <2>2. /\ FixedR(t, pre[t])
        /\ pre[t].truth => pre[t].lbl
    <3>1. FixedR(t, pre[t])
      BY <2>1 DEF Frame
    <3>2. acts[t].truth => acts[t].lbl
      BY <1>0 DEF LabelCoversTruth, Ix
    <3> QED
      BY <3>1, <3>2 DEF FixedR
  <2>3. /\ nw.trig = t
        /\ nw.node = n
        /\ (nw.truth => nw.lbl)
    BY <2>2 DEF NewAct
  <2>4. LabelCoversTruth'
    <3> SUFFICES ASSUME NEW j \in Ix(acts') PROVE acts'[j].truth => acts'[j].lbl
      BY DEF LabelCoversTruth
    <3>1. j \in 1..Len(acts) \/ j = Len(acts) + 1
      BY <1>0, <2>0 DEF Ix
    <3>2. CASE j = Len(acts) + 1
      BY <2>0, <2>3, <3>2
    <3>3. CASE j \in 1..Len(acts)
      <4>1. acts'[j] = pre[j] /\ FixedR(j, pre[j])
        BY <2>0, <2>1, <3>3 DEF Frame
      <4>2. acts[j].truth => acts[j].lbl
        BY <1>0, <3>3 DEF LabelCoversTruth, Ix
      <4> QED
        BY <4>1, <4>2 DEF FixedR
    <3> QED
      BY <3>1, <3>2, <3>3
  <2>5. TaintedNeverOutward'
    <3> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, acts'[j].node \in Outward
                 PROVE  ~acts'[acts'[j].trig].truth
      BY DEF TaintedNeverOutward
    <3>1. j \in 1..Len(acts) \/ j = Len(acts) + 1
      BY <1>0, <2>0 DEF Ix
    <3>2. CASE j = Len(acts) + 1
      <4>1. acts'[j] = nw /\ acts'[t] = pre[t] /\ n \in Outward
        BY <2>0, <2>3, <3>2
      <4>2. ~(Dst[e] \in Outward /\ pre[t].lbl)
        BY <2>1 DEF EnabledIn, TaintOK
      <4>3. ~pre[t].truth
        BY <2>1, <2>2, <4>1, <4>2
      <4> QED
        BY <2>3, <4>1, <4>3
    <3>3. CASE j \in 1..Len(acts)
      <4>1. acts'[j] = pre[j] /\ FixedR(j, pre[j]) /\ j \in Ix(acts)
        BY <2>0, <2>1, <3>3 DEF Frame, Ix
      <4>2. acts'[j].trig = acts[j].trig /\ acts'[j].node = acts[j].node
        BY <4>1 DEF FixedR
      <4>3. /\ acts[j].trig \in 1..(j - 1)
            /\ acts[acts[j].trig].status = "ended"
            /\ ~acts[acts[j].trig].truth
        BY <1>0, <3>3, <4>1, <4>2 DEF ActsWF, TaintedNeverOutward
      <4>4. acts[j].trig \in 1..Len(acts)
        BY <1>0, <3>3, <4>3
      <4>5. FixedR(acts[j].trig, pre[acts[j].trig]) /\ acts'[acts[j].trig] = pre[acts[j].trig]
        BY <2>0, <2>1, <4>4 DEF Frame
      <4>6. acts'[acts[j].trig].truth = acts[acts[j].trig].truth
        BY <4>3, <4>5 DEF FixedR
      <4> QED
        BY <4>2, <4>3, <4>6
    <3> QED
      BY <3>1, <3>2, <3>3
  <2> QED
    BY <2>4, <2>5 DEF InvT
<1>p. ASSUME NEW st \in Seatings, Promote(st) PROVE InvT'
  <2> DEFINE x == [node |-> Root, trig |-> 0, via |-> "root", status |-> "ready", st |-> "none",
                   lbl |-> FALSE, truth |-> FALSE, lin |-> st[Root], hist |-> {1},
                   found |-> FALSE, foundAt |-> 0, at |-> 0]
  <2>1. x \in ActRec
    <3>1. st \in [Nodes -> Lin] /\ Root \in Nodes
      BY EdgeFacts DEF Seatings
    <3> QED
      BY <3>1 DEF ActRec, Root
  <2>2. acts' = <<x>>
    BY <1>p DEF Promote
  <2>3. Len(<<x>>) = 1 /\ <<x>>[1] = x
    BY <2>1, RootSeq
  <2>4. Ix(acts') = {1} /\ acts'[1] = x
    BY <2>2, <2>3 DEF Ix
  <2>5. LabelCoversTruth'
    BY <2>4 DEF LabelCoversTruth
  <2>6. TaintedNeverOutward'
    BY <2>4 DEF TaintedNeverOutward
  <2> QED
    BY <2>5, <2>6 DEF InvT
<1>f. ASSUME NEW i \in Ix(acts), Finding(i) PROVE InvT'
  <2>0. /\ acts' \in Seq(ActRec) /\ Len(acts') = Len(acts)
        /\ \A k \in Ix(acts) : /\ acts'[k].node = acts[k].node
                               /\ acts'[k].trig = acts[k].trig
                               /\ acts'[k].lbl = acts[k].lbl
                               /\ acts'[k].truth = acts[k].truth
    BY <1>0, <1>f, FindingFacts
  <2>1. Ix(acts') = Ix(acts)
    BY <2>0 DEF Ix
  <2>2. LabelCoversTruth'
    <3> SUFFICES ASSUME NEW j \in Ix(acts') PROVE acts'[j].truth => acts'[j].lbl
      BY DEF LabelCoversTruth
    <3> QED
      BY <1>0, <2>0, <2>1 DEF LabelCoversTruth
  <2>3. TaintedNeverOutward'
    <3> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, acts'[j].node \in Outward
                 PROVE  ~acts'[acts'[j].trig].truth
      BY DEF TaintedNeverOutward
    <3>1. /\ j \in Ix(acts)
          /\ acts'[j].trig = acts[j].trig /\ acts'[j].node = acts[j].node
      BY <2>0, <2>1
    <3>2. /\ acts[j].trig \in 1..(j - 1) /\ ~acts[acts[j].trig].truth
      BY <1>0, <3>1 DEF ActsWF, TaintedNeverOutward
    <3>3. acts[j].trig \in Ix(acts)
      BY <1>0, <3>1, <3>2 DEF Ix
    <3>4. acts'[acts[j].trig].truth = acts[acts[j].trig].truth
      BY <2>0, <3>3
    <3> QED
      BY <3>1, <3>2, <3>4
  <2> QED
    BY <2>2, <2>3 DEF InvT
<1> QED
  BY <1>0, <1>u, <1>n, <1>p, <1>f, ActsStep

LEMMA InitInvT == Init => Shape /\ InvT
<1> SUFFICES ASSUME Init PROVE Shape /\ InvT OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. Ix(acts) = {}
  <2>1. acts = <<>> /\ Len(<<>>) = 0
    BY EmptySeq DEF Init
  <2> QED
    BY <2>1 DEF Ix
<1> QED
  BY <1>1, <1>2 DEF InvT, LabelCoversTruth, TaintedNeverOutward

THEOREM LabelCoversTruthAlways ==
  ASSUME Mut # "M_FORGETTAINT"
  PROVE  Spec => []LabelCoversTruth
<1>1. Shape /\ InvT /\ [Next]_vars => Shape' /\ InvT'
  BY NextShape, NextInvT
<1>2. InvT => LabelCoversTruth
  BY DEF InvT
<1> QED
  BY InitInvT, <1>1, <1>2, PTL DEF Spec

THEOREM TaintedNeverOutwardAlways ==
  ASSUME Mut # "M_FORGETTAINT"
  PROVE  Spec => []TaintedNeverOutward
<1>1. Shape /\ InvT /\ [Next]_vars => Shape' /\ InvT'
  BY NextShape, NextInvT
<1>2. InvT => TaintedNeverOutward
  BY DEF InvT
<1> QED
  BY InitInvT, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
\* --- Lineages alternate ----------------------------------------------------------
LEMMA NextInvH ==
  ASSUME Mut # "M_NOLINEAGE", Shape, InvH, [Next]_vars
  PROVE  InvH'
<1>0. /\ TypeOK /\ ActsWF /\ BeforePromotion /\ ClearHopsAlternate
      /\ promoted => Alternates(seat)
      /\ acts \in Seq(ActRec) /\ Len(acts) \in Nat
      /\ seat \in [Nodes -> Lin]
  BY SeqFacts DEF Shape, TypeOK, InvH
<1>prom. ASSUME \/ \E i \in Ix(acts) : Grant(i) \/ Finding(i) \/ OrchGrant(i) \/ DecisionLapse(i)
                \/ \E i \in Ix(acts), s \in Sts, t \in BOOLEAN : End(i, s, t)
                \/ \E e \in Chosen : Decide(e)
                \/ \E r \in pending : Apply(r)
                \/ OrchLapse \/ Settle \/ UNCHANGED vars
         PROVE  UNCHANGED <<promoted, seat>>
  BY <1>prom DEF Grant, Finding, OrchGrant, DecisionLapse, End, Decide, Apply, OrchLapse, Settle, vars
<1>a. (promoted' => Alternates(seat)')
  <2>1. ASSUME NEW st \in Seatings, Promote(st) PROVE promoted' => Alternates(seat)'
    <3>1. Alternates(st) /\ seat' = st
      BY <2>1 DEF Promote
    <3> QED
      BY <3>1 DEF Alternates
  <2>2. ASSUME UNCHANGED <<promoted, seat>> PROVE promoted' => Alternates(seat)'
    BY <1>0, <2>2 DEF Alternates
  <2> QED
    BY <1>prom, <2>1, <2>2 DEF Next
<1>u. ASSUME acts' \in Seq(ActRec), Len(acts') = Len(acts), Frame(acts') PROVE ClearHopsAlternate'
  <2> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, acts'[j].via \in Clear
               PROVE  acts'[j].lin # acts'[acts'[j].trig].lin
    BY DEF ClearHopsAlternate
  <2>1. j \in 1..Len(acts) /\ j \in Ix(acts) /\ FixedR(j, acts'[j])
    BY <1>u DEF Ix, Frame
  <2>2. acts'[j].trig = acts[j].trig /\ acts'[j].via = acts[j].via /\ acts'[j].lin = acts[j].lin
    BY <2>1 DEF FixedR
  <2>3. acts[j].trig \in 1..Len(acts)
    <3>1. acts[j].trig \in 1..(j - 1)
      BY <1>0, <2>1 DEF ActsWF
    <3> QED
      BY <1>0, <2>1, <3>1
  <2>4. FixedR(acts[j].trig, acts'[acts[j].trig])
    BY <1>u, <2>3 DEF Frame
  <2>5. acts[j].lin # acts[acts[j].trig].lin
    BY <1>0, <2>1, <2>2 DEF ClearHopsAlternate
  <2> QED
    BY <2>2, <2>4, <2>5 DEF FixedR
<1>n. ASSUME NEW pre \in Seq(ActRec), NEW n \in Nodes, NEW t \in 1..Len(acts), NEW e \in Edges,
             AddStep(pre, n, t, e)
      PROVE  ClearHopsAlternate'
  <2> DEFINE nw == NewAct(pre, n, t, e, idx + 1)
  <2>0. /\ nw \in ActRec
        /\ acts' \in Seq(ActRec)
        /\ Len(acts') = Len(acts) + 1
        /\ \A k \in 1..Len(acts) : acts'[k] = pre[k]
        /\ acts'[Len(acts) + 1] = nw
    BY <1>0, <1>n, AddFacts
  <2>1. /\ Len(pre) = Len(acts) /\ Frame(pre) /\ EnabledIn(pre, e, t) /\ n = Dst[e]
    BY <1>n DEF AddStep
  <2>2. /\ promoted
    <3>1. acts # <<>>
      <4>1. Len(acts) >= 1
        BY <1>0
      <4>2. Len(<<>>) = 0
        BY EmptySeq
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1 DEF BeforePromotion
  <2>3. Alternates(seat)
    BY <1>0, <2>2
  <2> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, acts'[j].via \in Clear
               PROVE  acts'[j].lin # acts'[acts'[j].trig].lin
    BY DEF ClearHopsAlternate
  <2>4. j \in 1..Len(acts) \/ j = Len(acts) + 1
    BY <1>0, <2>0 DEF Ix
  <2>5. CASE j = Len(acts) + 1
    <3>1. acts'[j] = nw /\ nw.via = e /\ nw.trig = t /\ nw.lin = seat[n]
      BY <2>0, <2>5 DEF NewAct
    <3>2. e \in Clear
      BY <3>1
    <3>3. seat[Src[e]] # seat[Dst[e]]
      BY <2>3, <3>2 DEF Alternates
    <3>4. /\ acts'[t] = pre[t]
          /\ FixedR(t, pre[t])
          /\ acts[t].lin = seat[acts[t].node]
      BY <1>0, <2>0, <2>1 DEF Frame, ActsWF, Ix
    <3>5. pre[t].node = Src[e]
      BY <2>1 DEF EnabledIn
    <3>6. pre[t].lin = seat[Src[e]]
      <4>1. acts[t].node = Src[e] /\ pre[t].lin = acts[t].lin
        BY <3>4, <3>5 DEF FixedR
      <4> QED
        BY <3>4, <4>1
    <3> QED
      BY <2>1, <3>1, <3>3, <3>4, <3>6
  <2>6. CASE j \in 1..Len(acts)
    <3>1. acts'[j] = pre[j] /\ FixedR(j, pre[j]) /\ j \in Ix(acts)
      BY <2>0, <2>1, <2>6 DEF Frame, Ix
    <3>2. acts'[j].trig = acts[j].trig /\ acts'[j].via = acts[j].via /\ acts'[j].lin = acts[j].lin
      BY <3>1 DEF FixedR
    <3>3. acts[j].trig \in 1..Len(acts)
      <4>1. acts[j].trig \in 1..(j - 1)
        BY <1>0, <3>1 DEF ActsWF
      <4> QED
        BY <1>0, <2>6, <4>1
    <3>4. FixedR(acts[j].trig, pre[acts[j].trig]) /\ acts'[acts[j].trig] = pre[acts[j].trig]
      BY <2>0, <2>1, <3>3 DEF Frame
    <3>5. acts[j].lin # acts[acts[j].trig].lin
      BY <1>0, <3>1, <3>2 DEF ClearHopsAlternate
    <3> QED
      BY <3>2, <3>4, <3>5 DEF FixedR
  <2> QED
    BY <2>4, <2>5, <2>6
<1>p. ASSUME NEW st \in Seatings, Promote(st) PROVE ClearHopsAlternate'
  <2> DEFINE x == [node |-> Root, trig |-> 0, via |-> "root", status |-> "ready", st |-> "none",
                   lbl |-> FALSE, truth |-> FALSE, lin |-> st[Root], hist |-> {1},
                   found |-> FALSE, foundAt |-> 0, at |-> 0]
  <2>1. x \in ActRec
    <3>1. st \in [Nodes -> Lin] /\ Root \in Nodes
      BY EdgeFacts DEF Seatings
    <3> QED
      BY <3>1 DEF ActRec, Root
  <2>2. acts' = <<x>>
    BY <1>p DEF Promote
  <2>3. Len(<<x>>) = 1
    BY <2>1, RootSeq
  <2>4. \A j \in Ix(acts') : ~(j > 1)
    BY <2>2, <2>3 DEF Ix
  <2> QED
    BY <2>4 DEF ClearHopsAlternate
<1>f. ASSUME NEW i \in Ix(acts), Finding(i) PROVE ClearHopsAlternate'
  <2>0. /\ acts' \in Seq(ActRec) /\ Len(acts') = Len(acts)
        /\ \A k \in Ix(acts) : /\ acts'[k].trig = acts[k].trig
                               /\ acts'[k].via = acts[k].via
                               /\ acts'[k].lin = acts[k].lin
    BY <1>0, <1>f, FindingFacts
  <2> SUFFICES ASSUME NEW j \in Ix(acts'), j > 1, acts'[j].via \in Clear
               PROVE  acts'[j].lin # acts'[acts'[j].trig].lin
    BY DEF ClearHopsAlternate
  <2>1. j \in Ix(acts)
    BY <2>0 DEF Ix
  <2>2. acts'[j].trig = acts[j].trig /\ acts'[j].via = acts[j].via /\ acts'[j].lin = acts[j].lin
    BY <2>0, <2>1
  <2>3. acts[j].trig \in Ix(acts)
    <3>1. acts[j].trig \in 1..(j - 1)
      BY <1>0, <2>1 DEF ActsWF
    <3> QED
      BY <1>0, <2>1, <3>1 DEF Ix
  <2>4. acts'[acts[j].trig].lin = acts[acts[j].trig].lin
    BY <2>0, <2>3
  <2>5. acts[j].lin # acts[acts[j].trig].lin
    BY <1>0, <2>1, <2>2 DEF ClearHopsAlternate
  <2> QED
    BY <2>2, <2>4, <2>5
<1>c. ClearHopsAlternate'
  BY <1>0, <1>u, <1>n, <1>p, <1>f, ActsStep
<1> QED
  BY <1>a, <1>c DEF InvH

LEMMA InitInvH == Init => Shape /\ InvH
<1> SUFFICES ASSUME Init PROVE Shape /\ InvH OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. Ix(acts) = {}
  <2>1. acts = <<>> /\ Len(<<>>) = 0
    BY EmptySeq DEF Init
  <2> QED
    BY <2>1 DEF Ix
<1> QED
  BY <1>1, <1>2 DEF InvH, ClearHopsAlternate, Init

THEOREM ClearHopsAlternateAlways ==
  ASSUME Mut # "M_NOLINEAGE"
  PROVE  Spec => []ClearHopsAlternate
<1>1. Shape /\ InvH /\ [Next]_vars => Shape' /\ InvH'
  BY NextShape, NextInvH
<1>2. InvH => ClearHopsAlternate
  BY DEF InvH
<1> QED
  BY InitInvH, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []BudgetBound
  BY BudgetBoundAlways
<1>2. Spec => []CompletedOnlyBySink
  BY CompletedOnlyBySinkAlways
<1>3. Spec => []RouteOnItsEvent
  BY RouteOnItsEventAlways
<1>4. Spec => []NoActivationAfterFinding
  BY NoActivationAfterFindingAlways
<1>5. Spec => []LabelCoversTruth
  BY LabelCoversTruthAlways
<1>6. Spec => []TaintedNeverOutward
  BY TaintedNeverOutwardAlways
<1>7. Spec => []ClearHopsAlternate
  BY ClearHopsAlternateAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail: each lemma states, in the module's terms, the  *)
(* guard the mutation removes. The counterexamples are TLC's.                  *)

\* M_OVERRUN: a lease is charged with the budget already spent.
LEMMA MutOverrunChargesPastTheBudget ==
  ASSUME Mut = "M_OVERRUN", nCharged = N
  PROVE  CanCharge
  BY DEF CanCharge, N

\* M_ORCHFREE: an orchestrator round is not charged.
LEMMA MutOrchFreeChargesNothing ==
  ASSUME Mut = "M_ORCHFREE"
  PROVE  (IF Mut = "M_ORCHFREE" THEN nCharged ELSE nCharged + 1) = nCharged
  OBVIOUS

\* M_BUDGETDONE: running out of budget is recorded as a completion.
LEMMA MutBudgetDoneCompletes ==
  ASSUME Mut = "M_BUDGETDONE", exhausted
  PROVE  (IF Mut = "M_BUDGETDONE" /\ exhausted THEN "completed" ELSE "failed") = "completed"
  OBVIOUS

\* M_TRACKER: a route is decided for the latest open event, not its own.
LEMMA MutTrackerRoutesTheLatest ==
  ASSUME Mut = "M_TRACKER"
  PROVE  DecideEv = LatestOpen
  BY DEF DecideEv, Tracker

\* M_SOURCEONLY: only the activation's own finding is read, not its history's.
LEMMA MutSourceOnlyReadsOneActivation ==
  ASSUME Mut = "M_SOURCEONLY", NEW as, NEW i, ~as[i].found
  PROVE  Unfound(as, i)
  BY DEF Unfound

\* M_FORGETTAINT: the receiver of a clear edge is not labelled by its source.
LEMMA MutForgetTaintDropsTheLabel ==
  ASSUME Mut = "M_FORGETTAINT", NEW as, NEW n, NEW t, NEW e, NEW p
  PROVE  NewAct(as, n, t, e, p).lbl = FALSE
  BY DEF NewAct

\* M_NOLINEAGE: the gate passes a seating that does not alternate.
LEMMA MutNoLineagePassesTheGate ==
  ASSUME Mut = "M_NOLINEAGE", NEW st
  PROVE  Mut = "M_NOLINEAGE" \/ Alternates(st)
  OBVIOUS
=============================================================================
