<!-- Layer: assurance · Simulink Requirements links and Simulink Design Verifier proof objectives · TOPAK source: the binding table; ADR-0045 Annex A -->
<!-- Of the paper's categories, model-based design is the one with a real assurance layer: ISO 26262 traceability from requirement to model to test to generated code, with a verification status per requirement. What it carries as "assumptions" is Design Verifier's Proof Assumption blocks, scoped to one proof; there is no deployment-wide declaration from which a lost premise voids a requirement. -->

Requirement set `topak_lease.slreqx`, with links (Requirements Editor, "Links" column) and verification status:

| ID | Summary | Implemented by | Verified by | Status | Assumes (sldv.assume / Proof Assumption) |
|---|---|---|---|---|---|
| LEASE-4.1 | Renewal never adds authority | Stateflow `Lease/Renew` (05-model) | Design Verifier objective `PO_4_1_alphabet_subset`, `PO_4_1_ttl_le`; Simulink Test `renew_widening_refused` | **Proven** (DV); Passed (Test) | `live.live == true`; at most one live lease per principal (`sldv.assume(count_live(p) <= 1)`) |
| LEASE-4.2 | Fixed fields across renewal | `Lease/Renew` | `PO_4_2_round`, `PO_4_2_role`, `PO_4_2_bundle`, `PO_4_2_rung`, `PO_4_2_digest` | **Proven** | none |
| LEASE-4.3 | Never renewed at a lower rung; lapses if unattestable | `Lease/Renew`, `Contain/Appraise` | `PO_4_3_no_lower`; Test `renew_unattestable_lapses` | **Undecided** at this model: `Contain/Appraise` is a stub (rung 3 SIMULATED) | appraisal oracle is honest (T-0045-16, T-0045-17) |
| LEASE-4.4 | ttl ≤ T_persona | `Lease/Renew` | `PO_4_4_t_persona` | **Proven** | `T_persona` parameter from the floor values |
| LEASE-5.2 | Epoch fence ends every live lease | `Lease/Fence` | `PO_5_2_all_ended` | **Proven** | none |
| LEASE-5.3 | No action under a fenced epoch, before the floor | `Admit/CheckLive` | `PO_5_3_fenced_first`; Test `fenced_action_never_reaches_floor` | **Proven**; Passed | none |
| LEASE-5.1 | Targeted revocation stops one, bars later grants | `Lease/Revoke`, `Lease/Grant` | `PO_5_1_only_target`, `PO_5_1_no_regrant` | **Proven** | revocation set is replicated (T-0045-1) |

**What the status column is and is not.** *Proven* is Design Verifier's result over the Simulink
model at the configured bounds; it is the counterpart of a TLC row (T-0045-29), not of a TLAPS proof,
and it says nothing of the generated C unless a SIL back-to-back test (09-runtime) is also linked.
*Passed* is a Simulink Test result on the model. The ISO 26262 traceability report lists every
requirement with no *Verified by* link, which is ADR-0057 §8's "every clause with guarantees and no
discharging edge" by another name.

**Where the givens go.** Design Verifier's Proof Assumption blocks (`sldv.assume`) scope an
assumption to the proof that uses it; a Simulink Requirements requirement of custom type
`Assumption` can be linked with `Derives` so that a requirement whose assumption is removed shows
*Unverified*. That is the nearest the toolchain comes to "a lost premise voids a theorem", and it is
a manual link, not a computation.
