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
(define-fun t7 () Bool (set.member "Report" t6))
(define-fun t8 () Bool (and t3 t7))
; {epoch, owner, round, sealed}
(declare-datatype R7 (
  (R7 (R7_a0 (_ BitVec 64)) (R7_a1 E1) (R7_a2 (_ BitVec 64)) (R7_a3 Bool))))
; Topak::Topic
(declare-datatype E8 (
  (E8 (E8_eid String))))
; "resource"
(declare-const t9 E8)
; attrs[Topak::Topic]
(declare-fun f1 (E8) R7)
(define-fun t10 () R7 (f1 t9))
(define-fun t11 () E1 (R7_a1 t10))
(define-fun t12 () Bool (= t11 t0))
(define-fun t13 () Bool (and t8 t12))
(define-fun t14 () (_ BitVec 64) (R7_a0 t10))
(define-fun t15 () (_ BitVec 64) (R6_a1 t4))
(define-fun t16 () Bool (= t14 t15))
(define-fun t17 () Bool (and t13 t16))
(define-fun t18 () (_ BitVec 64) (R7_a2 t10))
(define-fun t19 () (_ BitVec 64) (R6_a4 t4))
(define-fun t20 () Bool (= t18 t19))
(define-fun t21 () Bool (and t17 t20))
(define-fun t22 () Bool (R7_a3 t10))
(define-fun t23 () Bool (not t22))
(define-fun t24 () Bool (and t21 t23))
(define-fun t25 () String (R0_a1 t1))
(define-fun t26 () Bool (= t25 "thinker"))
(define-fun t27 () Bool (R6_a3 t4))
(define-fun t28 () Bool (not t27))
(define-fun t29 () Bool (and t26 t28))
(define-fun t30 () Bool (not t29))
(define-fun t31 () Bool (and t24 t30))
(assert true)
(assert t31)
(check-sat)
