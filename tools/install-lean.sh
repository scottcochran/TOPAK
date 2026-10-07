#!/bin/bash
# Install the pinned Lean toolchain (tools/LEAN-PIN) through elan, and compare its binaries with the pin. Not tracked:
# elan keeps toolchains under ~/.elan (about 2 GB). Lake fetches cedar-spec and batteries for floor/lean on its first
# build, at the commits floor/lean/lake-manifest.json names; tools/lean-sync.sh compares those with the pin too.
# Needs elan (https://github.com/leanprover/elan). Prebuilt toolchains exist for macOS arm64 and Linux x86_64.
set -e
TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"
pin_field() { grep -E "^$1 " "$TOOLS_DIR/LEAN-PIN" | head -1 | cut -d' ' -f2-; }
TC="$(pin_field toolchain)"
if elan toolchain list | grep -qx "$TC"; then echo "$TC is installed."; else elan toolchain install "$TC"; fi
dir="$HOME/.elan/toolchains/$(echo "$TC" | sed 's|/|--|; s|:|---|')"
ok=1
for f in "libleanshared lib/lean/libleanshared.dylib" "libleanshared lib/libleanshared.so" "lean bin/lean" "leanchecker bin/leanchecker" "lake bin/lake"; do
  key=${f%% *}; path=${f#* }
  [ -f "$dir/$path" ] || continue
  have=$(shasum -a 256 "$dir/$path" | cut -c1-16); want=$(pin_field "${key}_sha256_16")
  if [ "$have" = "$want" ]; then echo "  $path: $have matches the pin"; else echo "  $path: $have, pin $want: DOES NOT MATCH"; ok=0; fi
done
[ $ok -eq 1 ] && echo "Installed $TC; matches tools/LEAN-PIN (platform $(pin_field platform))." \
  || echo "Installed $TC; does NOT match tools/LEAN-PIN. A different platform or build is a change every results file made with it shows."
