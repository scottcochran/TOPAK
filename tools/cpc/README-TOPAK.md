# Cooperating Proof Calculus signature (vendored)

The Eunoia signature for cvc5's Cooperating Proof Calculus (CPC), copied unchanged from the cvc5 source
tree at tag `cvc5-1.4.0` (commit `b432cd77ebeb41091de42637ca8523f8437a1db1`), directory `proofs/eo/cpc/`.
License: cvc5's modified BSD, in `COPYING` beside this file.

It is the rule set the pinned proof checker (`ethos`, see `tools/install-ethos.sh`) checks gate proofs
against (ADR-0030 §5 as amended by A1): a proof the solver emits is accepted only if every step is an
instance of a rule defined here. The signature is therefore part of the checker's trust root
(ADR-0045 T-0045-14) and its tree digest is printed in every gate results header beside the checker's
binary digest. Changing a file here changes that digest.

The signature must match the solver that produced the proof: cvc5 1.4.0, the static build in
`tools/cvc5-macOS-arm64-static/` (not tracked; its digest is printed in the header).
