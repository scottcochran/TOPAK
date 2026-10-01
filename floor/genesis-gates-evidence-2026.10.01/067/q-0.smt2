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
(define-fun t3 () Bool (= t2 "build"))
; {alphabet, rulesEpoch}
(declare-datatype R2 (
  (R2 (R2_a0 (Set String)) (R2_a1 (_ BitVec 64)))))
; Topak::CorpusRoot
(declare-datatype E3 (
  (E3 (E3_eid String))))
; Topak::ToolSet
(declare-datatype E4 (
  (E4 (E4_eid String))))
; Topak::Workspace
(declare-datatype E5 (
  (E5 (E5_eid String))))
; {corpusRoot, epoch, inputsInWorkspace, lease, round, roundRole, toolAllowlist, workspace}
(declare-datatype R6 (
  (R6 (R6_a0 E3) (R6_a1 (_ BitVec 64)) (R6_a2 Bool) (R6_a3 R2) (R6_a4 (_ BitVec 64)) (R6_a5 String) (R6_a6 E4) (R6_a7 E5))))
; "context"
(declare-const t4 R6)
(define-fun t5 () R2 (R6_a3 t4))
(define-fun t6 () (Set String) (R2_a0 t5))
(define-fun t7 () Bool (set.member "Read" t6))
(define-fun t8 () Bool (and t3 t7))
(define-fun t9 () E3 (R6_a0 t4))
; Topak::CorpusObject
(declare-datatype E7 (
  (E7 (E7_eid String))))
; "resource"
(declare-const t10 E7)
; ancs[Topak::CorpusObject, Topak::CorpusRoot]
(declare-fun f1 (E7) (Set E3))
(define-fun t11 () (Set E3) (f1 t10))
(define-fun t12 () Bool (set.member t9 t11))
(define-fun t13 () Bool (and t8 t12))
(define-fun t14 () String (R6_a5 t4))
(define-fun t15 () Bool (= t14 "voter"))
(define-fun t16 () Bool (not t15))
(define-fun t17 () Bool (and t13 t16))
(define-fun t18 () Bool (not t17))
(define-fun t19 () Bool (or t18 t13))
(define-fun t20 () Bool (not t19))
(assert true)
(assert t20)
(check-sat)
