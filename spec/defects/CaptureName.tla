---- MODULE CaptureName ----
EXTENDS TLAPS
CONSTANT D
VARIABLE w
P(z) == \E k \in D : w = <<k, z>>
Q    == \E k \in D : w = <<k, k>>
LEMMA Capture == ASSUME NEW k \in D, []Q PROVE [](P(k))
BY DEF P, Q
====
