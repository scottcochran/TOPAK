# The reference as a container image, for the compose cluster (compose.cluster.yml).
# Build context is the repository root, so the image carries policies/ and spec/*.tla, which
# scripts/dev-init.sh reads:
#
#   docker build -f mechanism/Dockerfile -t topak-node .
#
# DEV SCAFFOLDING. Nothing here is a release, a genesis bundle or a deployment under ADR-0023.
# The base images are pinned by digest (rust 1.100.0, Debian bookworm).
FROM rust:1-slim-bookworm@sha256:bb875b0f8ce726053e259034848c471840e96bfe591fd52556178ae9a05e6126 AS build
RUN apt-get update && apt-get install -y --no-install-recommends cmake make g++ pkg-config && rm -rf /var/lib/apt/lists/*
WORKDIR /topak/mechanism
COPY mechanism/ ./
# topak-floor links the floor in with include_str! (crates/topak-floor/src/lib.rs).
COPY floor/proposed/workflow-floor.cedar floor/proposed/workflow.cedarschema /topak/floor/proposed/
COPY floor/genesis-values.json /topak/floor/
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/topak/mechanism/target \
    cargo build --release --locked -p topak-node --bins \
 && mkdir -p /out && cp target/release/topak target/release/topak-demo-tool /out/

FROM debian:bookworm-slim@sha256:e67eeead736ff7bbe258ef088bff683635c561b1fcfefad0806c1df4ab49ce0e
# jq and perl's shasum for dev-init.sh, python3 for smoke.py.
RUN apt-get update && apt-get install -y --no-install-recommends jq perl python3 && rm -rf /var/lib/apt/lists/*
COPY --from=build /out/ /usr/local/bin/
WORKDIR /topak/mechanism
COPY mechanism/scripts/ scripts/
COPY mechanism/bundles/ bundles/
COPY policies/ /topak/policies/
COPY spec/*.tla /topak/spec/
ENV TOPAK_BIN_DIR=/usr/local/bin TOPAK_DEV=/topak/mechanism/dev
CMD ["topak", "--help"]
