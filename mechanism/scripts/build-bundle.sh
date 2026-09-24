#!/usr/bin/env bash
# Build the bundle tier as an OPA WASM bundle whose revision is a content digest.
#
# The revision is the bundle's identity everywhere: the lease's `bundle` field, the sidecar's
# reported provenance, and the local fallback's file name. It is SHA-256 over the sorted
# (path, bytes) of every non-test .rego file and data.json, so equal sources give equal ids.
#
# PROVISIONAL (bundle signing): OPA bundle signatures are not produced or verified. ADR-0030
# §2 requires signed bundles; see GAPS-AND-ASSUMPTIONS.md.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
src="${1:-$here/../policies}"
out="${2:-$here/bundles}"
mkdir -p "$out"

rev="$(cd "$src" && find . -type f \( -name '*.rego' ! -name '*_test.rego' -o -name 'data.json' \) | LC_ALL=C sort |
  while read -r f; do printf '%s\0' "$f"; cat "$f"; printf '\0'; done | shasum -a 256 | cut -d' ' -f1)"

docker run --rm --platform linux/amd64 -v "$src:/policies:ro" -v "$out:/out" openpolicyagent/opa \
  build -t wasm -e topak/bundle/allow --revision "$rev" --ignore '*_test.rego' -o "/out/$rev.tar.gz" /policies >&2

echo "$rev"
