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
; Topak::ToolSet
(declare-datatype E2 (
  (E2 (E2_eid String))))
; {quorum, tools}
(declare-datatype R3 (
  (R3 (R3_a0 Bool) (R3_a1 E2))))
; {alphabet, rulesEpoch}
(declare-datatype R4 (
  (R4 (R4_a0 (Set String)) (R4_a1 (_ BitVec 64)))))
; Topak::CorpusRoot
(declare-datatype E5 (
  (E5 (E5_eid String))))
; {breakGlass, epoch, lease, observerLive, round, runRoot, toolAllowlist}
(declare-datatype R6 (
  (R6 (R6_a0 R3) (R6_a1 (_ BitVec 64)) (R6_a2 R4) (R6_a3 Bool) (R6_a4 (_ BitVec 64)) (R6_a5 E5) (R6_a6 E2))))
; "context"
(declare-const t4 R6)
(define-fun t5 () R3 (R6_a0 t4))
(define-fun t6 () Bool (R3_a0 t5))
(define-fun t7 () Bool (and t3 t6))
(define-fun t8 () E2 (R3_a1 t5))
; Topak::Tool
(declare-datatype E7 (
  (E7 (E7_eid String))))
; "resource"
(declare-const t9 E7)
; ancs[Topak::Tool, Topak::ToolSet]
(declare-fun f1 (E7) (Set E2))
(define-fun t10 () (Set E2) (f1 t9))
(define-fun t11 () Bool (set.member t8 t10))
(define-fun t12 () Bool (and t7 t11))
(define-fun t13 () R4 (R6_a2 t4))
(define-fun t14 () (Set String) (R4_a0 t13))
(define-fun t15 () Bool (set.member "Actuate" t14))
(define-fun t16 () Bool (and t3 t15))
(define-fun t17 () E2 (R6_a6 t4))
(define-fun t18 () Bool (set.member t17 t10))
(define-fun t19 () Bool (and t16 t18))
(define-fun t20 () Bool (or t12 t19))
(define-fun t21 () String (R0_a1 t1))
(define-fun t22 () Bool (= t21 "thinker"))
(define-fun t23 () Bool (R6_a3 t4))
(define-fun t24 () Bool (not t23))
(define-fun t25 () Bool (and t22 t24))
(define-fun t26 () Bool (not t22))
(define-fun t27 () Bool (or t25 t26))
(define-fun t28 () Bool (not t27))
(define-fun t29 () Bool (and t20 t28))
(define-fun t30 () Bool (not t25))
(define-fun t31 () Bool (and t20 t30))
(define-fun t32 () Bool (= t29 t31))
(define-fun t33 () Bool (not t32))
(assert true)
(assert t33)
(check-sat)
