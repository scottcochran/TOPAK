---------------------------- MODULE Correlator ----------------------------
(* The correlator's detection function: ADR-0051 (Proposed), its ratification  *)
(* condition (§10). A correlator computes fixed folds over facts and reports   *)
(* findings that carry their evidence. This module carries three of the five   *)
(* correlations: `carried-label`, `shared-ingress` and `marked-past`.          *)
(*                                                                             *)
(* The mechanism sees labels. This module also carries, as ghost state no      *)
(* correlator reads, which bytes are really an attacker's: `tainted` for what  *)
(* a Thinker's model has read this round, `storeTaint` for what a shared       *)
(* target holds. `lost` and `forgot` are ghost too: they say that taint came   *)
(* by a path whose facts the store has dropped.                                *)
(*                                                                             *)
(*   CarriedCoversSplitPath  a send made by a Thinker that had really read an  *)
(*                           attacker's bytes, by any chain of shared targets  *)
(*                           whose facts are still held, is found by every     *)
(*                           honest correlator whose mark has passed it        *)
(*   FindingHasEvidence      every finding's condition held when it was made   *)
(*   IngressReachIsShared    `shared-ingress` names only Thinkers that were    *)
(*                           delivered the item                                *)
(*   SilenceIsCounted        a correlator whose mark passed a send another     *)
(*                           correlator found, and which found nothing, has a  *)
(*                           miss                                              *)
(*   MissIsOnACorrelation    no correlator is charged a miss for a judgment    *)
(*   HonestNeverCharged      no honest correlator has a miss                   *)
(*   StoreWithinRecord       the store holds no row of an erased round         *)
(*   LagNeverGates           a Thinker no finding names can call a shared      *)
(*                           target whatever the correlators have folded       *)
(*                                                                             *)
(* The floor is ADR-0047's F2 with every input a literal: a send is refused    *)
(* once the round's own `clearSet` holds `untrusted`. So every send in `sends` *)
(* passed the floor, and what `carried-label` finds is what the floor could    *)
(* not see. A call to a shared target both writes what the caller holds and    *)
(* returns what the target holds, which is the coarse reading of ADR-0051 §2.  *)
(*                                                                             *)
(* The fold's value is carried in the state as the facts arrive (`writes`,     *)
(* `effU`, `misses`): it is a function of the facts, and every reader of the   *)
(* same facts computes the same. A correlator's lag is in when it reports      *)
(* (`marked`), never in what the fold's value is. `writes` and `delivered` are *)
(* the fold state of ADR-0051 §6, keyed by round.                              *)
(*                                                                             *)
(* Declared premises, not modelled: one label (`untrusted`), so F1 and F3 and  *)
(* handles are outside (Labels.tla has them); `probe-then-use` and             *)
(* `distance-drift`, which are thresholds on counts; the horizon, which drops  *)
(* rows as erasure does; the judgment tier, except that a cell Observer finds  *)
(* against an item; a finding blocks the Thinkers it names for good, where the *)
(* records clear it at the round's end. An honest correlator is one that never *)
(* marks past a send its fold fires on. A Thinker's context is empty at the    *)
(* start of a round. `sharedF` and `namedF` hold the last finding of their     *)
(* kind, not the history: every one made is the last in the state after it, so *)
(* an invariant over the last is an invariant over all.                        *)
(*                                                                             *)
(* Mut = "none":         ADR-0051 as revised at R2.                            *)
(* Mut = "M_ROUNDSCOPE": labels are not carried past a round: the floor alone. *)
(*                       Must break CarriedCoversSplitPath.                    *)
(* Mut = "M_ONEHOP":     a call carries the mechanism's `clearSet` and not the *)
(*                       effective one: ADR-0051 before R2. Must break         *)
(*                       CarriedCoversSplitPath, and only with two targets.    *)
(* Mut = "M_BARE":       a finding needs no condition. Must break              *)
(*                       FindingHasEvidence and HonestNeverCharged.            *)
(* Mut = "M_DOMAIN":     `shared-ingress` names the domain. Must break         *)
(*                       IngressReachIsShared.                                 *)
(* Mut = "M_SELF":       a correlator's misses are not counted. Must break     *)
(*                       SilenceIsCounted.                                     *)
(* Mut = "M_TIERLESS":   a judgment finding charges every correlator whose     *)
(*                       mark passed it: ADR-0051 before R2. Must break        *)
(*                       MissIsOnACorrelation and HonestNeverCharged.          *)
(* Mut = "M_KEEP":       erasing a round leaves its rows. Must break           *)
(*                       StoreWithinRecord.                                    *)
(* Mut = "M_COUPLE":     a call waits for a correlator that has caught up.     *)
(*                       Must break LagNeverGates.                             *)
EXTENDS Integers, FiniteSets

CONSTANTS Mut, Thinkers, Stores, Corrs, Honest, MaxRound, MaxSends, MMiss

Items == {"i"}

VARIABLES
  round,      \* each Thinker's current round
  clearU,     \* the round's own clearSet holds `untrusted` (the mechanism's)
  effU,       \* the effective clearSet holds it (the fold's)
  tainted,    \* the Thinker's model has really read an attacker's bytes this round (ghost)
  lost,       \* ... by a path whose facts the store has dropped (ghost)
  storeTaint, \* a shared target really holds an attacker's bytes (ghost)
  forgot,     \* ... written by a call whose row the store has dropped (ghost)
  writes,     \* fold state: the calls that carried the label to a target, keyed by round
  delivered,  \* fold state: which item was delivered to whom, keyed by round
  erased,     \* the rounds that have been erased
  sends,      \* the admitted outward calls, with what was true when each was admitted
  found,      \* the items a cell Observer has found against
  marked,     \* for each correlator, the sends its mark has passed
  carriedF,   \* `carried-label` findings
  sharedF,    \* the last `shared-ingress` finding: {} or one record
  named,      \* the Thinkers a `shared-ingress` finding has named
  namedF,     \* the last `marked-past` finding: {} or one record
  misses      \* the misses counted

vars == <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered, erased,
          sends, found, marked, carriedF, sharedF, named, namedF, misses>>

Init ==
  /\ round = [t \in Thinkers |-> 1]
  /\ clearU = [t \in Thinkers |-> FALSE]
  /\ effU = [t \in Thinkers |-> FALSE]
  /\ tainted = [t \in Thinkers |-> FALSE]
  /\ lost = [t \in Thinkers |-> FALSE]
  /\ storeTaint = [x \in Stores |-> FALSE]
  /\ forgot = [x \in Stores |-> FALSE]
  /\ writes = {}
  /\ delivered = {}
  /\ erased = {}
  /\ sends = {}
  /\ found = {}
  /\ marked = [c \in Corrs |-> {}]
  /\ carriedF = {}
  /\ sharedF = {}
  /\ named = {}
  /\ namedF = {}
  /\ misses = {}

\* carried(x): some call still in the fold state carried the label to x.
Carried(x) == \E w \in writes : w.store = x

\* Any-of: a finding that names a Thinker blocks it.
Blocked(t) == (\E f \in carriedF : f.cite.by = t) \/ t \in named

Has(c, s) == \E f \in carriedF : f.by = c /\ f.cite = s

\* The Thinkers an item is on record as delivered to.
Had(i) == {t \in Thinkers : \E d \in delivered : d.to = t /\ d.item = i}

\* --- the Thinkers --------------------------------------------------------------

\* An outward read: an item from outside, delivered clear. Its label is `untrusted`
\* (ADR-0047 F4); whether it really is an attacker's is `bad`.
Read(t, i, bad) ==
  /\ ~Blocked(t)
  /\ clearU' = [clearU EXCEPT ![t] = TRUE]
  /\ effU' = [effU EXCEPT ![t] = TRUE]
  /\ tainted' = [tainted EXCEPT ![t] = @ \/ bad]
  /\ delivered' = delivered \cup {[to |-> t, round |-> round[t], item |-> i]}
  /\ UNCHANGED <<round, lost, storeTaint, forgot, writes, erased, sends, found, marked,
                 carriedF, sharedF, named, namedF, misses>>

\* What a call carries. ADR-0051 §2 at R2: the effective clearSet.
Out(t) == IF Mut = "M_ONEHOP" THEN clearU[t] ELSE effU[t]

\* A call on an inside entry whose target is x. The floor does not refuse it. It writes
\* what the caller holds and returns what the target holds, clear, under the target's
\* declared label, which is clean.
Touch(t, x) ==
  /\ ~Blocked(t)
  /\ Mut = "M_COUPLE" => \E c \in Corrs : sends \subseteq marked[c]
  /\ writes' = IF Out(t) /\ Mut # "M_ROUNDSCOPE"
               THEN writes \cup {[store |-> x, by |-> t, round |-> round[t]]} ELSE writes
  /\ storeTaint' = [storeTaint EXCEPT ![x] = @ \/ tainted[t]]
  /\ forgot' = [forgot EXCEPT ![x] = @ \/ lost[t]]
  /\ tainted' = [tainted EXCEPT ![t] = @ \/ storeTaint[x]]
  /\ effU' = [effU EXCEPT ![t] = @ \/ Carried(x)]
  /\ lost' = [lost EXCEPT ![t] = @ \/ forgot[x]]
  /\ UNCHANGED <<round, clearU, delivered, erased, sends, found, marked, carriedF, sharedF,
                 named, namedF, misses>>

\* An outward call with a literal destination. The floor (F2) refuses it once the
\* round's own clearSet holds `untrusted`.
Send(t) ==
  /\ ~Blocked(t)
  /\ ~clearU[t]
  /\ Cardinality(sends) < MaxSends
  /\ sends' = sends \cup {[by |-> t, round |-> round[t], eff |-> effU[t],
                           tainted |-> tainted[t], lost |-> lost[t]]}
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered,
                 erased, found, marked, carriedF, sharedF, named, namedF, misses>>

\* The round ends and the next begins with an empty context. Shared targets keep
\* what they hold.
EndRound(t) ==
  /\ round[t] < MaxRound
  /\ round' = [round EXCEPT ![t] = @ + 1]
  /\ clearU' = [clearU EXCEPT ![t] = FALSE]
  /\ effU' = [effU EXCEPT ![t] = FALSE]
  /\ tainted' = [tainted EXCEPT ![t] = FALSE]
  /\ lost' = [lost EXCEPT ![t] = FALSE]
  /\ UNCHANGED <<storeTaint, forgot, writes, delivered, erased, sends, found, marked,
                 carriedF, sharedF, named, namedF, misses>>

\* --- erasure (ADR-0006; ADR-0051 §6) --------------------------------------------

\* An ended round is erased, and the store drops the rows keyed by it. The targets
\* its calls wrote to are not erased with it.
Erase(t, r) ==
  /\ r \in 1..(round[t] - 1)
  /\ [who |-> t, round |-> r] \notin erased
  /\ erased' = erased \cup {[who |-> t, round |-> r]}
  /\ IF Mut = "M_KEEP"
     THEN UNCHANGED <<writes, delivered, forgot>>
     ELSE /\ writes' = {w \in writes : ~(w.by = t /\ w.round = r)}
          /\ delivered' = {d \in delivered : ~(d.to = t /\ d.round = r)}
          /\ forgot' = [x \in Stores |->
                          forgot[x] \/ \E w \in writes : w.store = x /\ w.by = t /\ w.round = r]
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, sends, found, marked,
                 carriedF, sharedF, named, namedF, misses>>

\* --- the cell Observers ---------------------------------------------------------

\* A cell Observer finds against an item delivered to its Thinker. It is a judgment.
\* Before R2 it charged every correlator whose mark had passed the delivery, and a
\* correlator that reads facts only has always passed it.
ObsFind(t, i) ==
  /\ \E d \in delivered : d.to = t /\ d.item = i
  /\ found' = found \cup {i}
  /\ misses' = IF Mut = "M_TIERLESS"
               THEN misses \cup {[obs |-> c, tier |-> "judgment", cite |-> i] : c \in Corrs}
               ELSE misses
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered,
                 erased, sends, marked, carriedF, sharedF, named, namedF>>

\* --- the correlators ------------------------------------------------------------

\* `carried-label` fires on a send: the correlator reports it, citing the send, and
\* its mark passes. Every other correlator that had passed it in silence has a miss.
Report(c, s) ==
  /\ s \in sends /\ s \notin marked[c]
  /\ s.eff \/ Mut = "M_BARE"
  /\ carriedF' = carriedF \cup {[by |-> c, cite |-> s, cond |-> s.eff]}
  /\ marked' = [marked EXCEPT ![c] = @ \cup {s}]
  /\ misses' = IF Mut = "M_SELF" THEN misses
               ELSE misses \cup {[obs |-> c2, tier |-> "correlation", cite |-> s] :
                                   c2 \in {q \in Corrs \ {c} : s \in marked[q] /\ ~Has(q, s)}}
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered,
                 erased, sends, found, sharedF, named, namedF>>

\* The correlator's mark passes a send and it reports nothing. An honest one does
\* this only where the fold did not fire. If another correlator has found the send,
\* this is a miss.
Pass(c, s) ==
  /\ s \in sends /\ s \notin marked[c]
  /\ c \in Honest => ~s.eff
  /\ marked' = [marked EXCEPT ![c] = @ \cup {s}]
  /\ misses' = IF Mut # "M_SELF" /\ \E q \in Corrs \ {c} : Has(q, s)
               THEN misses \cup {[obs |-> c, tier |-> "correlation", cite |-> s]} ELSE misses
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered,
                 erased, sends, found, carriedF, sharedF, named, namedF>>

\* `shared-ingress`: an item one watcher found against, and everyone on record as
\* delivered it.
Propagate(c, i) ==
  /\ i \in found \/ Mut = "M_BARE"
  /\ LET names == IF Mut = "M_DOMAIN" THEN Thinkers ELSE Had(i)
     IN /\ sharedF' = {[by |-> c, item |-> i, names |-> names, had |-> Had(i), cond |-> i \in found]}
        /\ named' = named \cup names
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered,
                 erased, sends, found, marked, carriedF, namedF, misses>>

MissesOf(q) == {m \in misses : m.obs = q}

\* `marked-past`: a correlator names another whose misses have reached m_miss.
Name(c, q) ==
  /\ q \in Corrs \ {c}
  /\ Cardinality(MissesOf(q)) >= MMiss \/ Mut = "M_BARE"
  /\ namedF' = {[by |-> c, names |-> q, cond |-> Cardinality(MissesOf(q)) >= MMiss]}
  /\ UNCHANGED <<round, clearU, effU, tainted, lost, storeTaint, forgot, writes, delivered,
                 erased, sends, found, marked, carriedF, sharedF, named, misses>>

Next ==
  \/ \E t \in Thinkers, i \in Items, bad \in BOOLEAN : Read(t, i, bad)
  \/ \E t \in Thinkers, x \in Stores : Touch(t, x)
  \/ \E t \in Thinkers : Send(t) \/ EndRound(t)
  \/ \E t \in Thinkers, r \in 1..MaxRound : Erase(t, r)
  \/ \E t \in Thinkers, i \in Items : ObsFind(t, i)
  \/ \E c \in Corrs, s \in sends : Report(c, s) \/ Pass(c, s)
  \/ \E c \in Corrs, i \in Items : Propagate(c, i)
  \/ \E c \in Corrs, q \in Corrs : Name(c, q)

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

CarriedCoversSplitPath ==
  \A c \in Honest \cap Corrs : \A s \in sends :
    (s \in marked[c] /\ s.tainted /\ ~s.lost) => Has(c, s)

FindingHasEvidence ==
  /\ \A f \in carriedF : f.cond
  /\ \A f \in sharedF : f.cond
  /\ \A f \in namedF : f.cond

IngressReachIsShared == \A f \in sharedF : f.names \subseteq f.had

SilenceIsCounted ==
  \A c \in Corrs : \A s \in marked[c] :
    (~Has(c, s) /\ \E q \in Corrs \ {c} : Has(q, s))
      => [obs |-> c, tier |-> "correlation", cite |-> s] \in misses

MissIsOnACorrelation == \A m \in misses : m.tier = "correlation"

HonestNeverCharged == \A m \in misses : m.obs \notin Honest

StoreWithinRecord ==
  /\ \A w \in writes : [who |-> w.by, round |-> w.round] \notin erased
  /\ \A d \in delivered : [who |-> d.to, round |-> d.round] \notin erased

LagNeverGates == \A t \in Thinkers : \A x \in Stores : ~Blocked(t) => ENABLED Touch(t, x)

Safe == /\ CarriedCoversSplitPath /\ FindingHasEvidence /\ IngressReachIsShared
        /\ SilenceIsCounted /\ MissIsOnACorrelation /\ HonestNeverCharged
        /\ StoreWithinRecord /\ LagNeverGates

\* --- reachability witnesses: each must be VIOLATED unless the row says otherwise

\* The split path: a send the floor admitted, made on an attacker's bytes, is found.
NeverSplitFound == \A f \in carriedF : ~(f.cond /\ f.cite.tainted)
\* The fold is coarse: a send is found whose Thinker had read nothing of an attacker's.
NeverFoundClean == \A f \in carriedF : ~(f.cond /\ ~f.cite.tainted)
\* `shared-ingress` names a Thinker other than the one whose Observer found the item.
NeverSharedTwo == \A f \in sharedF : ~(f.cond /\ Cardinality(f.names) > 1)
\* A correlator's silence is counted.
NeverMiss == misses = {}
\* `marked-past` fires on evidence.
NeverNamed == \A f \in namedF : ~f.cond
\* Erasure opens a hole: a send made on an attacker's bytes that no fold can see,
\* because the rows that said the target was tainted went with an erased round.
NeverLostTaint == \A s \in sends : ~(s.tainted /\ s.lost /\ ~s.eff)
\* A round is erased while a row keyed by it is held.
NeverErasedARow == erased = {}
=============================================================================
