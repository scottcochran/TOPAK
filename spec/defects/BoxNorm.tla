---- MODULE BoxNorm ----
EXTENDS Emergency_live_proof, TLAPS
InvSmall == \A t \in {"te"} : em.round > 0 => t \in em.envelope
InvBig   == \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope
LEMMA InvSmallAlways == SpecL => []InvSmall
<1>1. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>2. EnvelopeHasTe <=> InvSmall
    BY DEF EnvelopeHasTe, InvSmall
<1> QED
    BY <1>1, <1>2, PTL
LEMMA InvBigAlways == SpecL => []InvBig
BY InvSmallAlways DEF InvSmall, InvBig
====
