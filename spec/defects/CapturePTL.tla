---- MODULE CapturePTL ----
EXTENDS Emergency_live_proof, TLAPS
Diag   == em.round > 0 => \E x \in Tools : x = x /\ x \in em.envelope
Has(v) == em.round > 0 => \E x \in Tools : x = v /\ x \in em.envelope
LH(v)  == SpecL => []Has(v)
LEMMA DiagAlways == SpecL => []Diag
<1>1. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>2. EnvelopeHasTe => Diag
    BY DEF EnvelopeHasTe, Diag, Tools
<1> QED
    BY <1>1, <1>2, PTL
LEMMA LHInst == ASSUME NEW x \in Tools PROVE LH(x)
BY DiagAlways, PTL DEF LH, Has, Diag
LEMMA LHAll == \A x \in Tools : LH(x)
BY LHInst
====
