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
; Topak::Roster
(declare-datatype E3 (
  (E3 (E3_eid String))))
; {epoch, grantRoster, lease, rulesEpoch, verdict, vetoRoster, voteRulesEpoch}
(declare-datatype R4 (
  (R4 (R4_a0 (_ BitVec 64)) (R4_a1 E3) (R4_a2 R2) (R4_a3 (_ BitVec 64)) (R4_a4 String) (R4_a5 E3) (R4_a6 (_ BitVec 64)))))
; "context"
(declare-const t4 R4)
(define-fun t5 () R2 (R4_a2 t4))
(define-fun t6 () (Set String) (R2_a0 t5))
(define-fun t7 () Bool (set.member "Vote" t6))
(define-fun t8 () Bool (and t3 t7))
(define-fun t9 () (_ BitVec 64) (R4_a6 t4))
(define-fun t10 () (_ BitVec 64) (R4_a3 t4))
(define-fun t11 () Bool (= t9 t10))
(define-fun t12 () Bool (and t8 t11))
(define-fun t13 () E3 (R4_a1 t4))
; ancs[Topak::Seat, Topak::Roster]
(declare-fun f1 (E1) (Set E3))
(define-fun t14 () (Set E3) (f1 t0))
(define-fun t15 () Bool (set.member t13 t14))
(define-fun t16 () String (R0_a1 t1))
(define-fun t17 () Bool (= t16 "grant"))
(define-fun t18 () Bool (and t15 t17))
(define-fun t19 () E3 (R4_a5 t4))
(define-fun t20 () Bool (set.member t19 t14))
(define-fun t21 () Bool (= t16 "observer"))
(define-fun t22 () Bool (and t20 t21))
(define-fun t23 () Bool (or t18 t22))
(define-fun t24 () Bool (and t12 t23))
(define-fun t25 () String (R4_a4 t4))
(define-fun t26 () Bool (= t25 "grant"))
(define-fun t27 () Bool (not t15))
(define-fun t28 () Bool (and t26 t27))
; {author}
(declare-datatype R5 (
  (R5 (R5_a0 E1))))
; Topak::Artifact
(declare-datatype E6 (
  (E6 (E6_eid String))))
; "resource"
(declare-const t29 E6)
; attrs[Topak::Artifact]
(declare-fun f2 (E6) R5)
(define-fun t30 () R5 (f2 t29))
(define-fun t31 () E1 (R5_a0 t30))
(define-fun t32 () Bool (= t31 t0))
(define-fun t33 () Bool (or t28 t32))
(define-fun t34 () Bool (not t33))
(define-fun t35 () Bool (and t24 t34))
(assert true)
(assert t35)
(check-sat)
