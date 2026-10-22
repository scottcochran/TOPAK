---- MODULE CombineUnderBinder ----
EXTENDS Emergency_live_proof, TLAPS
LEMMA OneInst == ASSUME NEW t \in {"te"} PROVE SpecL => [](em.round > 0 => t \in em.envelope)
<1>1. t = "te"
    OBVIOUS
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. EnvelopeHasTe <=> (em.round > 0 => t \in em.envelope)
    BY <1>1 DEF EnvelopeHasTe
<1> QED
    BY <1>2, <1>3, PTL
LEMMA AllFromOne == \A t \in Tools : SpecL => [](em.round > 0 => t \in em.envelope)
BY OneInst
====
