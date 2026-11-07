// Layer: assurance · Contract testing (Pact, provider verification) · TOPAK source: the binding table's premise column; ADR-0045 Annex A
// Pact's *provider state* is the one place in the paper's tool set where a guarantee carries its
// givens: the consumer says "given <state>", and the provider must either set that state up or
// declare it cannot. A state handler that returns `{ declared: false }` is a premise the provider
// does not hold, and every interaction resting on it is reported as not verified, which is the
// Pact-shaped "void". Pact also has two grades, *verified* and *pending* (WIP pacts), which is
// ADR-0049 §4's *checked*/*claimed* and no more.
const { Verifier } = require('@pact-foundation/pact');
const { startNode, stopNode, node } = require('./harness');

const DECLARATION = require('../../10-deployment/contract/declaration.json');   // ADR-0045 §4 rows, as the provider holds them

describe('topak-node operator socket honours topak-op pacts', () => {
  beforeAll(startNode);
  afterAll(stopNode);

  it('verifies every interaction whose provider states the deployment can establish', () =>
    new Verifier({
      provider: 'topak-node operator socket',
      providerBaseUrl: node.url,
      pactUrls: ['../03-record/contract/pacts/topak-op-topak-node-operator-socket.json'],
      // Provider states are the givens. Each one names the rows it rests on.
      stateHandlers: {
        'seat a1 holds a live lease at fence 1 with alphabet [Read, Emit], rung 0, ttl 1000 ms': async () => {
          requires('T-0045-10');                               // rules issued, seats declared
          await node.apply(1, { op: 'grant', seat: 'a1', alphabet: ['Read', 'Emit'], rung: 0, ttl_ms: 1000 });
          return { declared: true, rows: ['T-0045-10'] };
        },
        'seat a1 holds a rung-3 attested lease': async () => {
          // T-0045-16 and T-0045-17 exist only SIMULATED at the reference: the state cannot be
          // established, and every interaction given it is void for this deployment.
          return requires('T-0045-16', 'T-0045-17');
        },
      },
      // "pending" pacts: interactions the provider is not yet required to pass. The nearest thing
      // to a grade below *verified*: the consumer's claim is published, the provider's word is not given.
      enablePending: true,
      includeWipPactsSince: '2026-11-01',
      publishVerificationResult: true,
      providerVersion: node.releaseDigest,                       // the promoted release, by digest (T-0045-28's identity)
    }).verifyProvider());
});

function requires(...rows) {
  const missing = rows.filter((r) => !DECLARATION.rows.some((d) => d.id === r && d.status !== 'excluded'));
  if (missing.length) throw new Error(`void: premise ${missing.join(', ')} not declared (ADR-0045 §3 rule 1)`);
  return { declared: true, rows };
}
