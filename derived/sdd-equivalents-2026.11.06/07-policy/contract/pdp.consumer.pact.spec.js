// Layer: policy · Contract testing (Pact) · TOPAK source: floor B4 behind ../api/authzen.openapi.yaml
// The admit pipeline is the consumer; the floor evaluator the provider. Contract testing can pin
// the decision for named requests; it cannot say anything about requests nobody wrote down, which
// is exactly what the floor's gates and Lean theorems are for. Specmatic would do the same from the
// OpenAPI with the two examples above as its example files.
const { PactV3 } = require('@pact-foundation/pact');
const { FloorClient } = require('../src/floor-client');

const provider = new PactV3({ consumer: 'topak-core admit', provider: 'floor evaluator' });
const ctx = { lease: { alphabet: ['Read', 'Draft', 'Invoke', 'Emit', 'Submit'], rulesEpoch: 5 }, epoch: 3, round: 7, roundRole: 'author' };
const a1 = { type: 'Topak::Seat', id: 'a1', properties: { domain: 'build', kind: 'thinker' } };

describe('floor B4-emit-own-topic', () => {
  it('allows an emit to the seat\'s own unsealed topic at the current epoch and round', () => {
    provider.given('the genesis floor, schema S and the gen-tests entities at epoch 3, round 7')
      .uponReceiving('a1 emits to a1-r7')
      .withRequest({ method: 'POST', path: '/access/v1/evaluation', body: { subject: a1, action: { name: 'Emit' },
        resource: { type: 'Topak::Topic', id: 'a1-r7', properties: { owner: 'a1', epoch: 3, round: 7, sealed: false } }, context: ctx } })
      .willRespondWith({ status: 200, body: { decision: true, context: { reasons: ['B4-emit-own-topic'] } } });
    return provider.executeTest(async (m) => expect((await new FloorClient(m.url).evaluate(a1, 'Emit', 'a1-r7', ctx)).decision).toBe(true));
  });

  it('denies an emit to a sealed topic', () => {
    provider.given('the genesis floor, schema S and the gen-tests entities at epoch 3, round 7')
      .uponReceiving('a1 emits to a1-r7-sealed')
      .withRequest({ method: 'POST', path: '/access/v1/evaluation', body: { subject: a1, action: { name: 'Emit' },
        resource: { type: 'Topak::Topic', id: 'a1-r7-sealed', properties: { owner: 'a1', epoch: 3, round: 7, sealed: true } }, context: ctx } })
      .willRespondWith({ status: 200, body: { decision: false } });
    return provider.executeTest(async (m) => expect((await new FloorClient(m.url).evaluate(a1, 'Emit', 'a1-r7-sealed', ctx)).decision).toBe(false));
  });

  it('treats an evaluation error as a deny (ADR-0030 §1)', () => {
    provider.given('the genesis floor with a topic whose owner attribute is missing')
      .uponReceiving('a1 emits to a malformed topic')
      .withRequest({ method: 'POST', path: '/access/v1/evaluation', body: { subject: a1, action: { name: 'Emit' },
        resource: { type: 'Topak::Topic', id: 'a1-broken' }, context: ctx } })
      .willRespondWith({ status: 200, body: { decision: false, context: { error: 'attribute `owner` not found' } } });
    return provider.executeTest(async (m) => expect((await new FloorClient(m.url).evaluate(a1, 'Emit', 'a1-broken', ctx)).decision).toBe(false));
  });
});
