# The compiled occupant on an empty image (ADR-0036 §4's subtraction for P3): one static binary,
# no shell, no interpreter, no package manager. The Persona bundle is not in the image; the
# launcher mounts its three files read-only at /model.
#
#   docker build --provenance=false -f Dockerfile -t topak-slm-occupant .      (from slm/occupant/)
#
# --provenance=false keeps the image Id, which the profile pins (P7), from changing with every build's
# attestation timestamp.
#
# The builder is pinned by its multi-arch index digest and the crates by Cargo.lock (--locked).
# On musl the binary links statically, which is what lets it run on `scratch`: an image with no
# dynamic loader cannot start anything else.
ARG RUST=rust:1.98-alpine@sha256:7cc1c22d77d9432f7fe012a70e6d3e555af54c2a6832700ed7d553f1769ae89f

FROM ${RUST} AS build
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --locked --release && cp target/release/occupant /occupant

FROM scratch
COPY --from=build /occupant /occupant
USER 10001:10001
ENTRYPOINT ["/occupant"]
