---- MODULE ConjBox ----
EXTENDS Emergency_live_proof, TLAPS
LEMMA SmallI == SpecL => [](em.round >= 0 /\ \A t \in {"te"} : em.round > 0 => t \in em.envelope)
<1>1. SpecL => []TypeOK
    BY TypeAlwaysL
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. TypeOK /\ EnvelopeHasTe => (em.round >= 0 /\ \A t \in {"te"} : em.round > 0 => t \in em.envelope)
    BY DEF TypeOK, EmType, EnvelopeHasTe
<1> QED
    BY <1>1, <1>2, <1>3, PTL
LEMMA BigI == SpecL => [](em.round >= 0 /\ \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope)
BY SmallI
LEMMA BigE == SpecL => <>(em.round < 0 \/ \E t \in {"tx", "t1"} : t \in domainTools)
<1>1. Init => (em.round < 0 \/ \E t \in {"tx", "t1"} : t \in domainTools)
    BY DEF Init
<1> QED
    BY <1>1, PTL DEF SpecL
LEMMA SmallE == SpecL => <>(em.round < 0 \/ \E t \in {"tx"} : t \in domainTools)
BY BigE
====
