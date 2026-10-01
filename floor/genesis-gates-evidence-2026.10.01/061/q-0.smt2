(set-option :produce-models true)
(set-logic ALL)
(declare-datatype Option (par (X) (
  (none)
  (some (val X)))))
; {domain, kind}
(declare-datatype R0 (
  (R0 (R0_a0 String) (R0_a1 String))))
; Topak::Seat
(declare-datatype E1 (
  (E1 (E1_eid String))))
; "principal"
(declare-const t0 E1)
; attrs[Topak::Seat]
(declare-fun f0 (E1) R0)
(define-fun t1 () R0 (f0 t0))
(define-fun t2 () String (R0_a0 t1))
(define-fun t3 () Bool (= t2 "run"))
; {alphabet, rulesEpoch}
(declare-datatype R2 (
  (R2 (R2_a0 (Set String)) (R2_a1 (_ BitVec 64)))))
; Topak::ToolSet
(declare-datatype E3 (
  (E3 (E3_eid String))))
; {quorum, tools}
(declare-datatype R4 (
  (R4 (R4_a0 Bool) (R4_a1 E3))))
; Topak::CorpusRoot
(declare-datatype E5 (
  (E5 (E5_eid String))))
; {breakGlass, epoch, lease, observerLive, round, runRoot, toolAllowlist}
(declare-datatype R6 (
  (R6 (R6_a0 R4) (R6_a1 (_ BitVec 64)) (R6_a2 R2) (R6_a3 Bool) (R6_a4 (_ BitVec 64)) (R6_a5 E5) (R6_a6 E3))))
; "context"
(declare-const t4 R6)
(define-fun t5 () R2 (R6_a2 t4))
(define-fun t6 () (Set String) (R2_a0 t5))
(define-fun t7 () Bool (set.member "Consult" t6))
(define-fun t8 () Bool (and t3 t7))
(define-fun t9 () E5 (R6_a5 t4))
; Topak::CorpusObject
(declare-datatype E7 (
  (E7 (E7_eid String))))
; "resource"
(declare-const t10 E7)
; ancs[Topak::CorpusObject, Topak::CorpusRoot]
(declare-fun f1 (E7) (Set E5))
(define-fun t11 () (Set E5) (f1 t10))
(define-fun t12 () Bool (set.member t9 t11))
(define-fun t13 () Bool (and t8 t12))
(assert true)
(assert t13)
(check-sat)
