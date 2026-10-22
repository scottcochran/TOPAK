---- MODULE NameCollision ----
EXTENDS TLAPS
VARIABLE x
D33  == x = x
E280 == x # x
LEMMA BoxD33 == []D33
<1>1. D33
    BY DEF D33
<1> QED
    BY <1>1, PTL
LEMMA NotBoxE280 == ~[]E280
<1>1. ~E280
    BY DEF E280
<1> QED
    BY <1>1, PTL
LEMMA FalseBySMT == FALSE
BY BoxD33, NotBoxE280
R63  == x = x
R699 == x # x
LEMMA In == R63
BY DEF R63
LEMMA Out == ~R699
BY DEF R699
LEMMA FalseByPTL == FALSE
BY In, Out, PTL
====
