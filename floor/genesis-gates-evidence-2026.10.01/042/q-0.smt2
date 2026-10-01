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
(define-fun t5 () (Set String) (set.insert "F1" "F2" "F3" "F4" "F5" "F6" (as set.empty (Set String))))
(define-fun t6 () Bool (set.member t4 t5))
(define-fun t7 () Bool (not t6))
(define-fun t8 () Bool (and t1 t7))
(define-fun t9 () Bool (not t8))
(assert true)
(assert t9)
(check-sat)
