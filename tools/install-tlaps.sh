#!/bin/bash
# Fetch the pinned TLA+ Proof System (TLAPS) release into tools/tlaps-<version>/ (not tracked: about
# 1.1 GB compressed, 1.9 GB on disk, Isabelle and Z3 included). The wrapper tools/tlapm runs it, and every
# proof results file prints the binary's sha256, so a different build is a change the results show.
# Prebuilt for macOS arm64 and Linux x86_64 only; see https://github.com/tlaplus/tlapm for other platforms.
# tools/TLAPS-PIN names the build the results files cite. The release tag is a pre-release that gets rebuilt, so
# what this script fetches today may not be that build; the install is compared with the pin and says so.
set -e
TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
pin_field() { grep -E "^$1 " "$TOOLS_DIR/TLAPS-PIN" | head -1 | cut -d' ' -f2-; }
TLAPS_VERSION="$(pin_field version)"
DEST="$TOOLS_DIR/tlaps-$TLAPS_VERSION"
check_pin() {
  have="$(shasum -a 256 "$DEST/bin/tlapm" | cut -c1-16)"; want="$(pin_field binary_sha256_16)"
  if [ "$have" = "$want" ]; then
    echo "Matches tools/TLAPS-PIN (commit $(pin_field commit))."
  else
    echo "Does NOT match tools/TLAPS-PIN: pinned $want… (commit $(pin_field commit)), installed $have… (tlapm $("$DEST/bin/tlapm" --version))."
    echo "The tag was rebuilt since the results files were made. tools/tlapm refuses this binary unless TLAPM_UNPINNED=1;"
    echo "a results file made with it cites a different prover, and moving the pin is the record of that."
  fi
}
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64) PLATFORM="arm64-darwin" ;;
  Linux-x86_64) PLATFORM="x86_64-linux-gnu" ;;
  *) echo "No prebuilt TLAPS $TLAPS_VERSION for $(uname -s) $(uname -m)"; exit 1 ;;
esac
if [ -x "$DEST/bin/tlapm" ]; then
  echo "tlapm is present at $DEST/bin/tlapm (sha256 $(shasum -a 256 "$DEST/bin/tlapm" | cut -c1-16)); remove the directory to reinstall."
  check_pin
  exit 0
fi
tarball="tlapm-$TLAPS_VERSION-$PLATFORM.tar.gz"
echo "Downloading $tarball..."
mkdir -p "$DEST"
curl -L --fail "https://github.com/tlaplus/tlapm/releases/download/$TLAPS_VERSION/$tarball" \
  | tar -xzf - -C "$DEST" --strip-components=1
[ -x "$DEST/bin/tlapm" ] || { echo "Install failed: $DEST/bin/tlapm is missing"; exit 1; }
echo "Installed $DEST/bin/tlapm (tlapm $("$DEST/bin/tlapm" --version), sha256 $(shasum -a 256 "$DEST/bin/tlapm" | cut -c1-16))."
check_pin
