#!/bin/bash
# Fetch the pinned TLA+ Proof System (TLAPS) release into tools/tlaps-<version>/ (not tracked: about
# 1.1 GB compressed, 1.9 GB on disk, Isabelle and Z3 included). The wrapper tools/tlapm runs it, and every
# proof results file prints the binary's sha256, so a different build is a change the results show.
# Prebuilt for macOS arm64 and Linux x86_64 only; see https://github.com/tlaplus/tlapm for other platforms.
set -e
TLAPS_VERSION="1.6.0-pre"
TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$TOOLS_DIR/tlaps-$TLAPS_VERSION"
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64) PLATFORM="arm64-darwin" ;;
  Linux-x86_64) PLATFORM="x86_64-linux-gnu" ;;
  *) echo "No prebuilt TLAPS $TLAPS_VERSION for $(uname -s) $(uname -m)"; exit 1 ;;
esac
if [ -x "$DEST/bin/tlapm" ]; then
  echo "tlapm is present at $DEST/bin/tlapm (sha256 $(shasum -a 256 "$DEST/bin/tlapm" | cut -c1-16)); remove the directory to reinstall."
  exit 0
fi
tarball="tlapm-$TLAPS_VERSION-$PLATFORM.tar.gz"
echo "Downloading $tarball..."
mkdir -p "$DEST"
curl -L --fail "https://github.com/tlaplus/tlapm/releases/download/$TLAPS_VERSION/$tarball" \
  | tar -xzf - -C "$DEST" --strip-components=1
[ -x "$DEST/bin/tlapm" ] || { echo "Install failed: $DEST/bin/tlapm is missing"; exit 1; }
echo "Installed $DEST/bin/tlapm (tlapm $("$DEST/bin/tlapm" --version), sha256 $(shasum -a 256 "$DEST/bin/tlapm" | cut -c1-16)). Compare with the digest the proof results files print."
