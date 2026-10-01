#!/bin/bash
# Fetch tla2tools.jar into tools/. The jar is TRACKED (ADR-0045 T-0045-29): every results file prints
# its digest, so replacing it with another build is a change the next manifest will show. Run this only
# to reinstall the pinned version; it no longer rewrites the wrappers, which are tracked beside it.
set -e
TLA_VERSION="v1.7.4"
TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
jar="$TOOLS_DIR/tla2tools.jar"
if [ -f "$jar" ]; then
  echo "tla2tools.jar is present (sha256 $(shasum -a 256 "$jar" | cut -c1-16)); refusing to overwrite the tracked jar."
  echo "Remove it first if you mean to replace it, and expect the digest in the next results file to change."
  exit 1
fi
echo "Downloading tla2tools.jar $TLA_VERSION..."
curl -L "https://github.com/tlaplus/tlaplus/releases/download/$TLA_VERSION/tla2tools.jar" -o "$jar"
echo "Installed $jar (sha256 $(shasum -a 256 "$jar" | cut -c1-16)). Compare with the digest the results files print."
