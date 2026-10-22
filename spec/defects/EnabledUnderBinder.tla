---- MODULE EnabledUnderBinder ----
EXTENDS Emergency_live, TLAPS
LEMMA Bad == (\E t \in Tools : ENABLED EmAdmit(t)) => (\A t \in Tools : ENABLED EmAdmit(t))
OBVIOUS
====
