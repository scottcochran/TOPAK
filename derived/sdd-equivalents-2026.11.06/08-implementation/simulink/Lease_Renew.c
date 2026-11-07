/*
 * Layer: implementation · Embedded Coder output from the Lease model (05-model), or SCADE KCG from lease_contract.lus
 * TOPAK source: lease.rs::check_renewal
 *
 * In model-based design nobody writes this file. The generated C carries traceability tags
 * ('<S1>/Renew') back to the block that produced each statement, and the certified generator
 * (KCG for SCADE, qualified under DO-178C/ISO 26262) is what the edge leaves to a person: the
 * paper's "spec-as-source" case study. Edge type: *generated*. Back-to-back SIL testing (09-runtime)
 * is what checks the generator did its job on this model.
 *
 * File: Lease_Renew.c
 * Code generated for Simulink model 'Lease'.
 * Model version                  : 1.12
 * Simulink Coder version         : 24.2 (R2024b)
 * C/C++ source code generated on : Fri Nov  6 09:14:02 2026
 */
#include "Lease_Renew.h"

/* Output and update for function-call system: '<S1>/Renew' */
void Lease_Renew(const Lease_T *live, const RenewRequest_T *req, boolean_T *ok, Lease_T *next)
{
  int32_T i;
  boolean_T subset;

  /* '<S1>/Renew/alphabet_subset': every flag set in req is set in live */
  subset = true;
  for (i = 0; i < 9; i++) {
    subset = subset && (!req->alphabet[i] || live->alphabet[i]);
  }

  /* '<S1>/Renew/refines': §4.1, §4.2, §4.4 */
  *ok = live->live && subset
        && (req->rung == live->confinement.rung)
        && (req->ttl_ms <= live->ttl_ms)
        && (req->ttl_ms <= LEASE_T_PERSONA_MS);

  /* '<S1>/Renew/new_lease': fields other than alphabet, ttl and fence are the live lease's */
  if (*ok) {
    *next = *live;
    for (i = 0; i < 9; i++) {
      next->alphabet[i] = req->alphabet[i];
    }
    next->ttl_ms = req->ttl_ms;
    next->fence = req->log_index;
  }
}
/* [EOF] */
