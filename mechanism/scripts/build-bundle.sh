#!/usr/bin/env bash
# Build the bundle tier as an OPA WASM bundle whose revision is a content digest.
#
# The revision is the bundle's identity everywhere: the lease's `bundle` field, the sidecar's
# reported provenance, and the local fallback's file name. It is SHA-256 over the sorted
# (path, bytes) of every non-test .rego file and data.json, so equal sources give equal ids.
#
# A bundle is trusted by its signature (ADR-0044): with TOPAK_BUNDLE_SECRET set to a 32-byte hex
# Ed25519 secret, the revision is signed for the purpose `bundle` into <revision>.sig beside the
# tarball, and the mechanism loads the bundle only if that key is in the issued rules'
# `bundle_keys`. Without the secret the tarball is built unsigned and nothing will load it;
# scripts/dev-init.sh signs a copy under the dev bundle key into dev/bundles/.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
src="${1:-$here/../policies}"
out="${2:-$here/bundles}"
mkdir -p "$out"

rev="$(cd "$src" && find . -type f \( -name '*.rego' ! -name '*_test.rego' -o -name 'data.json' \) | LC_ALL=C sort |
  while read -r f; do printf '%s\0' "$f"; cat "$f"; printf '\0'; done | shasum -a 256 | cut -d' ' -f1)"

docker run --rm --platform linux/amd64 -v "$src:/policies:ro" -v "$out:/out" openpolicyagent/opa \
  build -t wasm -e topak/bundle/allow --revision "$rev" --ignore '*_test.rego' -o "/out/$rev.tar.gz" /policies >&2

if [ -n "${TOPAK_BUNDLE_SECRET:-}" ]; then
  "$here/target/debug/topak" sign --purpose bundle --secret "$TOPAK_BUNDLE_SECRET" <(printf '{"revision":"%s"}' "$rev") > "$out/$rev.sig"
fi
echo "$rev"
