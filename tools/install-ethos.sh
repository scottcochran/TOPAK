#!/bin/bash
# Build the pinned proof checker: ethos at the commit cvc5 1.4.0's contrib/get-ethos-checker names.
# The binary lands in tools/ethos-<short>/bin/ethos (not tracked); every gate results file prints its
# sha256, so a different build is a change the results show (ADR-0030 §5 A1; ADR-0045 T-0045-14).
# Needs cmake >= 3.12, a C++17 compiler and GMP (brew install cmake gmp). Pass a cmake path as $1 if
# cmake is not on PATH.
set -e
ETHOS_COMMIT="8dc85c4db8d6cc612f02dc3bb627331732605eff"
SHORT="${ETHOS_COMMIT:0:7}"
TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$TOOLS_DIR/ethos-$SHORT"
CMAKE="${1:-cmake}"
if [ -x "$DEST/bin/ethos" ]; then
  echo "ethos is present at $DEST/bin/ethos (sha256 $(shasum -a 256 "$DEST/bin/ethos" | cut -c1-16)); remove the directory to rebuild."
  exit 0
fi
work="$(mktemp -d)"
echo "Fetching ethos $ETHOS_COMMIT..."
git clone -q https://github.com/cvc5/ethos.git "$work/ethos"
git -C "$work/ethos" checkout -q "$ETHOS_COMMIT"
echo "Building..."
mkdir -p "$work/ethos/build"
(cd "$work/ethos/build" && "$CMAKE" .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/homebrew >/dev/null && make -j8 >/dev/null)
mkdir -p "$DEST/bin"
cp "$work/ethos/build/src/ethos" "$DEST/bin/ethos"
echo "$ETHOS_COMMIT" > "$DEST/COMMIT"
rm -rf "$work"
echo "Installed $DEST/bin/ethos (commit $SHORT, sha256 $(shasum -a 256 "$DEST/bin/ethos" | cut -c1-16)). Compare with the digest the results files print."
