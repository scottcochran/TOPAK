---- MODULE HiddenBox ----
EXTENDS Emergency_live_proof, TLAPS
LB(S) == SpecL => [](\A t \in S : em.round > 0 => t \in em.envelope)
LEMMA Small == LB({"te"})
<1>1. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>2. EnvelopeHasTe <=> (\A t \in {"te"} : em.round > 0 => t \in em.envelope)
    BY DEF EnvelopeHasTe
<1> QED
    BY <1>1, <1>2, PTL DEF LB
LEMMA BigBad == LB({"te", "t2"})
BY Small DEF LB
LEMMA BigPTL == LB({"te", "t2"})
BY Small, PTL DEF LB
====
