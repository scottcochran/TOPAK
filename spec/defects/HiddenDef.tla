---- MODULE HiddenDef ----
EXTENDS Emergency_live_proof, TLAPS
LT(t) == SpecL => [](em.round > 0 => t \in em.envelope)
LEMMA InstTe == ASSUME NEW t \in {"te"} PROVE LT(t)
<1>1. t = "te"
    OBVIOUS
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. EnvelopeHasTe <=> (em.round > 0 => t \in em.envelope)
    BY <1>1 DEF EnvelopeHasTe
<1> QED
    BY <1>2, <1>3, PTL DEF LT
LEMMA Closure == \A t \in {"te"} : LT(t)
BY InstTe
LEMMA Literal == LT("te")
BY InstTe
LEMMA SuperBad == \A t \in {"te", "t2"} : LT(t)
BY InstTe
LEMMA OutsideBad == ASSUME NEW t \in Tools PROVE LT(t)
BY InstTe
====
