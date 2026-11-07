<!-- Layer: runtime · Contract testing · TOPAK source: trace recording (trace.rs) and the results file (Mechanism-trace-results-*.txt) -->

Contract-testing tools have two runtime artifacts, one on each side of the exchange.

**Specmatic records live traffic as examples** (`specmatic proxy`). This is the nearest thing in
the paper's toolset to `TOPAK_TRACE_DIR`: real exchanges captured and turned into replayable
cases. The difference is what is recorded: HTTP pairs, not the replicated state after each one.

```bash
specmatic proxy --target http://localhost:18080 ./recorded      # run the e2e suite through it
# ./recorded/lease.openapi.yaml is inferred or updated; ./recorded/lease_examples/*.json are the exchanges
specmatic test --config specmatic.yaml --examples ./recorded/lease_examples   # replay later, against the next build
```

**Pact publishes verification results by provider version**, which is the results file with a
broker instead of a dated text file:

```bash
pact-broker publish ./pacts --consumer-app-version "$(git rev-parse HEAD)" --branch main
# after 04-assurance/contract/renew.provider.verify.spec.js runs with publishVerificationResult: true:
pact-broker describe-version --pacticipant "topak-node operator socket" --version "$RELEASE_DIGEST"
#   → verified: 11 interactions, pending: 2 (rung-3 states not establishable), failed: 0
```

Both are *tested* edges over recorded inputs. Neither compares the recorded behaviour with a model;
each compares it with the last recording or with the written interactions.
