---- MODULE CdotUnderBinder ----
EXTENDS Emergency_live, TLAPS
LEMMA BadCdot == (\E t \in Tools : EmAdmit(t) \cdot EmAdmit(t)) => (\A t \in Tools : EmAdmit(t) \cdot EmAdmit(t))
OBVIOUS
====
