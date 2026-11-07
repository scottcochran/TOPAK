<!-- Layer: implementation · Contract testing, provider side · TOPAK source: the operator socket in topak-node, against ../03-record/contract and ../06-interface/contract -->

In contract testing the implementation-layer artifact is the provider verification run: the
provider is started, every consumer's pact is replayed against it, and the result is published
by provider version (a release digest). The provider is never generated from the contract; the
edge is *tested*, and the inputs are exactly the interactions consumers wrote.

**Pact** (JS): `04-assurance/contract/renew.provider.verify.spec.js` is the run; its
`stateHandlers` set up each provider state against the real `State`. Publish with
`providerVersion: <release digest>` so the broker's matrix (10-deployment) knows which build passed.

**Specmatic**, from the OpenAPI, no code to write:

```bash
# Start the reference's operator HTTP shim, then:
specmatic test --testBaseURL http://localhost:18080 \
  --config ../06-interface/contract/specmatic/specmatic.yaml \
  --examples ../03-record/contract/specmatic/lease_examples,../06-interface/contract/specmatic/lease_examples
# Every path/response in lease.openapi.yaml is exercised with generated inputs plus the examples;
# a response that does not match the schema (an extra lease field, a 409 with an unlisted reason) fails.
```

What neither run checks: a widening renewal that no example names. Specmatic's generative tests
draw inputs from the schema, which gets close, but the "never" is the model's (05-model), not the contract's.
