(set-option :produce-models true)
(set-logic ALL)
(declare-datatype Option (par (X) (
  (none)
  (some (val X)))))
; {erasureQuorum}
(declare-datatype R0 (
  (R0 (R0_a0 Bool))))
; "context"
(declare-const t0 R0)
(define-fun t1 () Bool (R0_a0 t0))
; {class}
(declare-datatype R1 (
  (R1 (R1_a0 String))))
; Topak::ArchiveRecord
(declare-datatype E2 (
  (E2 (E2_eid String))))
; "resource"
(declare-const t2 E2)
; attrs[Topak::ArchiveRecord]
(declare-fun f0 (E2) R1)
(define-fun t3 () R1 (f0 t2))
(define-fun t4 () String (R1_a0 t3))
(define-fun t5 () Bool (= t4 "F1"))
(define-fun t6 () (Set String) (set.insert "F1" "F2" "F3" "F4" "F5" "F6" (as set.empty (Set String))))
(define-fun t7 () Bool (set.member t4 t6))
(define-fun t8 () Bool (or t5 t7))
(define-fun t9 () Bool (not t8))
(define-fun t10 () Bool (and t1 t9))
(define-fun t11 () Bool (not t7))
(define-fun t12 () Bool (and t1 t11))
(define-fun t13 () Bool (= t10 t12))
(define-fun t14 () Bool (not t13))
(assert true)
(assert t14)
(check-sat)
