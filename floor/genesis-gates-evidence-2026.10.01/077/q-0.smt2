(set-option :produce-models true)
(set-logic ALL)
(declare-datatype Option (par (X) (
  (none)
  (some (val X)))))
; Topak::CorpusRoot
(declare-datatype E0 (
  (E0 (E0_eid String))))
; {alphabet, rulesEpoch}
(declare-datatype R1 (
  (R1 (R1_a0 (Set String)) (R1_a1 (_ BitVec 64)))))
; Topak::ToolSet
(declare-datatype E2 (
  (E2 (E2_eid String))))
; Topak::Workspace
(declare-datatype E3 (
  (E3 (E3_eid String))))
; {corpusRoot, epoch, inputsInWorkspace, lease, round, roundRole, toolAllowlist, workspace}
(declare-datatype R4 (
  (R4 (R4_a0 E0) (R4_a1 (_ BitVec 64)) (R4_a2 Bool) (R4_a3 R1) (R4_a4 (_ BitVec 64)) (R4_a5 String) (R4_a6 E2) (R4_a7 E3))))
; "context"
(declare-const t0 R4)
(define-fun t1 () (_ BitVec 64) (R4_a1 t0))
(define-fun t2 () Bool (bvsaddo t1 (_ bv1 64)))
(assert t2)
(check-sat)
