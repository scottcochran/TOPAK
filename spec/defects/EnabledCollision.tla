---- MODULE EnabledCollision ----
EXTENDS Emergency_live, TLAPS
LEMMA TwoNew == ASSUME NEW c32 \in Tools, NEW c905 \in Tools, ENABLED EmAdmit(c32) PROVE ENABLED EmAdmit(c905)
OBVIOUS
====
