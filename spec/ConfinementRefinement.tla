------------------------ MODULE ConfinementRefinement ------------------------
(* The mechanism's confinement path read against Confinement_A1.tla: ADR-0045   *)
(* T-0045-28, stage one, widened to launch, appraise, grant and revoke          *)
(* (feature item 4; derived/topak-contain-wrapper-design-2026.10.02.md §7).      *)
(*                                                                              *)
(* Every recorded trace is replayed through Mechanism.tla (`TraceMatches`), so   *)
(* `st` is, step by step, the reference's own projected state. This module maps *)
(* that state onto Confinement_A1's variables and checks its invariants on it:  *)
(*                                                                              *)
(*   Confinement_A1                     here (per live lease f)                 *)
(*   lease[p].live                      f \in LiveFences(st)                    *)
(*   lease[p].rung = Declared           rung = the seat's declared rung         *)
(*   lease[p].nEpoch, lease[p].epoch    att.nEpoch, epoch                       *)
(*   contested, revoked                 st.contested, principal targets         *)
(*   Contained(p)                       f \in st.contained                      *)
(*                                                                              *)
(* `Declared` is per seat in the reference (PROVISIONAL declared-rung), so      *)
(* NoSilentDowngrade is read per seat. ContainedMeansConfined is not checkable  *)
(* here: it is about the image the host actually ran, which the mechanism never *)
(* sees. What is checked in its place is that `contained` names only live       *)
(* leases at rung >= 1 on an Attested appraisal of a registered profile: the    *)
(* premises the abstract module's Contained rests on.                          *)
EXTENDS Mechanism

LiveFences(s) == {s.liveBySeat[x] : x \in DOMAIN s.liveBySeat}

\* NoSilentDowngrade (ADR-0034 §3.4, ADR-0031 A1): no live lease below, or above, its seat's rung.
RNoSilentDowngrade ==
  \A f \in LiveFences(st) :
    st.leases[f].seat \in DOMAIN st.seats => st.leases[f].rung = st.seats[st.leases[f].seat].rung

\* ContestedStopped (ADR-0034 §3.7): a Contested principal is revoked and holds no live lease.
RContestedStopped ==
  \A p \in DOMAIN st.contested :
    /\ [kind |-> "principal", id |-> p] \in st.revoked
    /\ \A f \in LiveFences(st) : st.leases[f].principal # p

\* FreshAppraisal (ADR-0034 §3.6): no live lease rests on an appraisal from a fenced epoch.
RFreshAppraisal ==
  \A f \in LiveFences(st) : ~IsNone(st.leases[f].att) => st.leases[f].att.nEpoch = st.leases[f].epoch

\* Contained's premises (ADR-0034 §4): a live lease, rung >= 1, Attested, a registered profile.
RContainedAttested ==
  \A f \in st.contained :
    /\ f \in LiveFences(st)
    /\ st.leases[f].rung >= 1
    /\ ~IsNone(st.leases[f].att)
    /\ st.leases[f].att.verdict = "attested"
    /\ st.leases[f].conf \in DOMAIN st.profiles

ConfinementRefined == RNoSilentDowngrade /\ RContestedStopped /\ RFreshAppraisal /\ RContainedAttested
=============================================================================
