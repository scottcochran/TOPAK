#!/usr/bin/env bash
# Layer: deployment · Pact Broker: environments, recorded deployments and can-i-deploy · TOPAK source: ADR-0058 §4 (publish the inventory per deployment), ADR-0023 §7b (the gate reads the declaration)
# The broker is where contract testing keeps a deployment's standing: which provider version is in
# which environment, which consumer versions it verified, and whether a candidate may deploy. That is a
# two-grade inventory (verified / not) per environment, read by a gate. It knows nothing of premises.
set -euo pipefail
BROKER=${PACT_BROKER_BASE_URL:-http://localhost:9292}
PROVIDER="topak-node operator socket"
RELEASE_DIGEST=$(git rev-parse HEAD)   # the promoted release, by digest (ADR-0024 §1)

# The deployments, as environments.
pact-broker create-environment --name reference  --display-name "the reference (rung 0, dev rules)" --production=false -b "$BROKER" || true
pact-broker create-environment --name rung3-sim  --display-name "rung 3 SIMULATED (tests/contain.rs)" --production=false -b "$BROKER" || true

# The gate: may this release be deployed to the reference environment? Reads the matrix the
# verification runs (04-assurance/contract, 09-runtime/contract) published.
pact-broker can-i-deploy --pacticipant "$PROVIDER" --version "$RELEASE_DIGEST" --to-environment reference -b "$BROKER"

# Record the deployment; later can-i-deploy calls for consumers read this.
pact-broker record-deployment --pacticipant "$PROVIDER" --version "$RELEASE_DIGEST" --environment reference -b "$BROKER"

# Interactions given rung-3 provider states were published as *pending* for this provider version:
# that is the broker's word for "void here", and the only grade below verified it has.
