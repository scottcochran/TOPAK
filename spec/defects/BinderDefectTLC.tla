---- MODULE BinderDefectTLC ----
EXTENDS Emergency_live
BadInv        == (\E t \in Tools : ENABLED EmAdmit(t)) => (\A t \in Tools : ENABLED EmAdmit(t))
BadEventually == (\E t \in Tools : <>(t \in em.envelope)) => (\A t \in Tools : <>(t \in em.envelope))
BadLeadsTo    == (\E t \in Tools : em.live ~> (t \in em.envelope)) => (\A t \in Tools : em.live ~> (t \in em.envelope))
AllTools      == \A t \in Tools : [](em.round > 0 => t \in em.envelope)
InvBig        == \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope
ConjBig       == em.round >= 0 /\ \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope
SmallE        == <>(em.round < 0 \/ \E t \in {"tx"} : t \in domainTools)
Has(v)        == em.round > 0 => \E x \in Tools : x = v /\ x \in em.envelope
AllHas        == \A v \in Tools : [](Has(v))
====
