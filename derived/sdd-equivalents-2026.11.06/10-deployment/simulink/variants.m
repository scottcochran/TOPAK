% Layer: deployment · Simulink variant controls and configuration sets · TOPAK source: ADR-0023 §6 (parameters moved), ADR-0058 §1 (keep/replace/add/omit)
% In model-based design a deployment is a variant configuration: variant subsystems are activated
% by control variables, and a configuration set names the target. An inactive variant is "omit";
% a variant subsystem with a different implementation is "replace". Design Verifier and Simulink
% Test results are stored per variant configuration, which is an inventory per deployment in all
% but name. What is missing is any statement that a deactivated variant voids a requirement: the
% Requirements report just shows it unverified in that configuration.

% --- The reference ----------------------------------------------------------------------------
cfg = Simulink.VariantConfigurationData;
cfg.addConfiguration('reference', 'The reference: rung 0, dev rules, SIMULATED appraisal');
cfg.addControlVariable('reference', 'CONFINEMENT_RUNG',   Simulink.VariantControl(0));        % D-0034-4: rung 0 for every seat
cfg.addControlVariable('reference', 'APPRAISAL_SOURCE',   Simulink.VariantControl('SIMULATED')); % T-0045-16/17 absent: Contain/Appraise is a stub
cfg.addControlVariable('reference', 'TRANSPORT',          Simulink.VariantControl('InMemory')); % kept: Kafka carries no ordering authority (ADR-0005)
cfg.addControlVariable('reference', 'FLOOR_STAGE',        Simulink.VariantControl('workflow')); % executed, Proposed
cfg.addControlVariable('reference', 'T_PERSONA_MS',       Simulink.VariantControl(3600000));   % placeholder (genesis-values.json)
cfg.addConstraint('one_live_lease', 'true');                                                    % §2 ⟨C1⟩: not a variant; always on

% --- A hypothetical rung-3 deployment ----------------------------------------------------------
cfg.addConfiguration('rung3', 'Confidential VM with an independent verifier');
cfg.addControlVariable('rung3', 'CONFINEMENT_RUNG', Simulink.VariantControl(3));
cfg.addControlVariable('rung3', 'APPRAISAL_SOURCE', Simulink.VariantControl('Verifier'));   % Contain/Appraise active: LEASE-4.3 becomes checkable
cfg.addControlVariable('rung3', 'TRANSPORT',        Simulink.VariantControl('Kafka'));
cfg.addControlVariable('rung3', 'FLOOR_STAGE',      Simulink.VariantControl('genesis'));

% Activate a configuration and re-run what 04-assurance/simulink links (Design Verifier objectives,
% Simulink Test). Results land in the requirement set's status column per configuration.
cfg.setDefaultConfigurationName('reference');
Simulink.VariantManager.activateModel('Lease', 'Configuration', 'reference');
sldvrun('Lease', sldvoptions('Mode', 'PropertyProving'));       % LEASE-4.1, 4.2, 4.4, 5.x: Proven; LEASE-4.3: Undecided (stub)
sltest.testmanager.run;                                          % the back-to-back run of 09-runtime
