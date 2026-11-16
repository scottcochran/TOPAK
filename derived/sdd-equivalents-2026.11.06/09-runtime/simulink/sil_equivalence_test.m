% Layer: runtime · Simulink Test back-to-back (model vs. generated code, SIL/PIL) · TOPAK source: trace replay through Mechanism.tla
% Model-based design's runtime check is the equivalence test: the same logged inputs are driven through
% the model (normal mode) and through the generated code (SIL or on-target PIL), and every output
% signal must match within tolerance. That is trace replay with the model as the oracle and the
% generated C as the subject, which is exactly the T-0045-28 edge the corpus checks by replay.
% Edge type: *replayed* (what it leaves: inputs no logged run exercised). Model coverage from the
% same run reports which decision columns of 07-policy's truth table were never reached.
import sltest.testmanager.*;

tf  = TestFile('topak_lease_runtime.mldatx');
ts  = tf.createTestSuite('Lease back-to-back');
tc  = ts.createTestCase('equivalence', 'renew_fence_revoke_recorded_runs');
tc.setProperty('Model', 'Lease');

% Inputs: the recorded runs (the e2e suite's traces, converted to timeseries by trace2sl.py).
tc.addInput('traces/e2e_expiry_an_expired_lease_is_ended_and_refused_3.mat');
tc.addInput('traces/e2e_build_build_round_promotion_and_fencing_4.mat');
tc.addInput('traces/mut_lease_renewal_is_monotone_and_m_renew_is_refused_0.mat');

% Simulation 1: the model.   Simulation 2: the generated code (08-implementation/simulink/Lease_Renew.c), SIL.
tc.setProperty('SimulationMode', 'Normal', 'SimulationIndex', 1);
tc.setProperty('SimulationMode', 'Software-in-the-Loop (SIL)', 'SimulationIndex', 2);

% Equivalence criteria: every output signal equal, no tolerance (decisions are booleans and integers).
ec = tc.addEquivalenceCriteria('Signal', '*', 'AbsTol', 0, 'RelTol', 0);

% Coverage on the model during run 1: decision and condition coverage of Floor/B4_emit_own_topic
% and Lease/Renew. An unreached objective is a path no trace exercised (what the replayed edge leaves).
cov = tc.getCoverageSettings(); cov.RecordCoverage = true; cov.MdlRefCoverage = true;
cov.MetricSettings = 'dc';

res = run(tc);
assert(res.Outcome == TestResultOutcomes.Passed, 'model and generated code diverge on a recorded run');
cvhtml('coverage/lease', res.CoverageResults);          % the "untraced paths" report
