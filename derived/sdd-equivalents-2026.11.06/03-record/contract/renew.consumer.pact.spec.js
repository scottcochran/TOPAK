// Layer: record · Contract testing (Pact, consumer side) · TOPAK source: ADR-0031 §4
// The operator CLI is the consumer; the replica's operator socket is the provider. A Pact
// interaction is one guarantee as an exchange. Provider states ("given") name what the mechanism
// must hold before the exchange, which is where the record's givens go (see 04-assurance).
const { PactV3, MatchersV3: M } = require('@pact-foundation/pact');
const { OperatorClient } = require('../src/operator-client');

const provider = new PactV3({ consumer: 'topak-op', provider: 'topak-node operator socket' });
const LIVE = 'seat a1 holds a live lease at fence 1 with alphabet [Read, Emit], rung 0, ttl 1000 ms';

describe('ADR-0031 §4 renewal only narrows', () => {
  it('§4.1 refuses a renewal that widens the alphabet', () => {
    provider
      .given(LIVE)
      .uponReceiving('a renewal adding Draft to the alphabet')
      .withRequest({ method: 'POST', path: '/leases/1/renew',
        body: { seat: 'a1', alphabet: ['Read', 'Emit', 'Draft'], rung: 0, ttl_ms: 1000 } })
      .willRespondWith({ status: 409, body: { reason: 'renewal widens the alphabet' } });
    return provider.executeTest(async (mock) => {
      const r = await new OperatorClient(mock.url).renew(1, { seat: 'a1', alphabet: ['Read', 'Emit', 'Draft'], rung: 0, ttl_ms: 1000 });
      expect(r.status).toBe(409);
    });
  });

  it('§4.1 applies a narrowing renewal at a new fence', () => {
    provider
      .given(LIVE)
      .uponReceiving('a renewal narrowing to Read with a shorter ttl')
      .withRequest({ method: 'POST', path: '/leases/1/renew',
        body: { seat: 'a1', alphabet: ['Read'], rung: 0, ttl_ms: 500 } })
      .willRespondWith({ status: 201, body: M.like({
        fence: M.integer(20), alphabet: ['Read'], ttl_ms: 500, round: 7, role: 'author',
        confinement: { digest: M.string(), rung: 0 } }) });
    return provider.executeTest(async (mock) => {
      const r = await new OperatorClient(mock.url).renew(1, { seat: 'a1', alphabet: ['Read'], rung: 0, ttl_ms: 500 });
      expect(r.status).toBe(201);
      expect(r.body.fence).not.toBe(1);
    });
  });

  it('§4.2 refuses a renewal that changes the role', () => {
    provider
      .given(LIVE)
      .uponReceiving('a renewal changing the role to voter')
      .withRequest({ method: 'POST', path: '/leases/1/renew',
        body: { seat: 'a1', alphabet: ['Read'], rung: 0, ttl_ms: 1000, role: 'voter' } })
      .willRespondWith({ status: 409, body: { reason: 'renewal changes role' } });
    return provider.executeTest(async (mock) => {
      const r = await new OperatorClient(mock.url).renew(1, { seat: 'a1', alphabet: ['Read'], rung: 0, ttl_ms: 1000, role: 'voter' });
      expect(r.status).toBe(409);
    });
  });
});
