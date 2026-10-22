---- MODULE TemporalUnderBinder ----
EXTENDS Emergency_live, TLAPS
LEMMA BadEventually == (\E t \in Tools : <>(t \in em.envelope)) => (\A t \in Tools : <>(t \in em.envelope))
OBVIOUS
LEMMA BadLeadsTo == (\E t \in Tools : em.live ~> (t \in em.envelope)) => (\A t \in Tools : em.live ~> (t \in em.envelope))
OBVIOUS
====
