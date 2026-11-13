#!/bin/bash
# Is the tracked TLC jar the pinned one? Compares tools/tla2tools.jar with tools/TLA-PIN.
#   usage: tools/check-pins.sh      exit 1 if the jar's sha256 is not the pin's
# The other two pins are checked where their binaries are cited, since neither binary is tracked:
# spec/proof-sync.sh checks that every proof results file names tools/TLAPS-PIN's prover, and tools/lean-sync.sh
# checks the Lean results files and every lean-toolchain against tools/LEAN-PIN. Runs the same by hand and in CI
# (.github/workflows/checks.yml; ADR-0069 §10.2, Proposed).
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
want=$(grep -v '^#' "$root/tools/TLA-PIN" | awk 'NF {print $2; exit}')
got=$(shasum -a 256 "$root/tools/tla2tools.jar" | cut -d' ' -f1)
echo "tools/tla2tools.jar  pinned $want"
echo "                     found  $got"
if [ "$want" = "$got" ]; then echo "in step with tools/TLA-PIN"; else echo "NOT THE PINNED JAR"; exit 1; fi
