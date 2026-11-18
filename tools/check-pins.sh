#!/bin/bash
# Do the pins agree? Compares tools/tla2tools.jar with tools/TLA-PIN, and tools/TLA-KIT-PIN and tools/TLAPS-PIN with
# it and with each other.
#   usage: tools/check-pins.sh      exit 1 if any check below fails; a line marked "reported" never fails
# 1. The tracked jar's sha256 is tools/TLA-PIN's.
# 2. tools/TLA-KIT-PIN names a release, an image by digest, a commit and the digests it states, each well formed
#    (ADR-0077 §1, Proposed). Its jar_sha256 is tools/TLA-PIN's jar: the image runs the jar this repository pins.
# 3. tools/TLAPS-PIN's binary_sha256_16 is the first 16 hex of its binary_sha256 (ADR-0077 §4).
# 4. tools/TLAPS-PIN's binary_sha256 against tools/TLA-KIT-PIN's tlapm_sha256: reported while the two pins name
#    different builds on purpose, and a failure once tools/TLAPS-PIN names the image (an `image` line; ADR-0077 §5).
# The prover and Lean pins are also checked where their binaries are cited, since neither binary is tracked:
# spec/proof-sync.sh checks that every proof results file names tools/TLAPS-PIN's prover, and tools/lean-sync.sh
# checks the Lean results files and every lean-toolchain against tools/LEAN-PIN. That the image's attestations
# verify is checked by .github/workflows/results.yml, which needs the network. Runs the same by hand and in CI
# (.github/workflows/checks.yml; ADR-0069 §10.2, Proposed).
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
status=0
field() { [ -f "$root/tools/$1" ] && grep -E "^$2 " "$root/tools/$1" | head -1 | cut -d' ' -f2-; }
ok()   { echo "  ok        $*"; }
bad()  { echo "  FAILED    $*"; status=1; }
note() { echo "  reported  $*"; }

echo "tools/TLA-PIN"
jar=$(grep -v '^#' "$root/tools/TLA-PIN" | awk 'NF {print $2; exit}')
got=$(shasum -a 256 "$root/tools/tla2tools.jar" | cut -d' ' -f1)
if [ "$jar" = "$got" ]; then ok "tools/tla2tools.jar is the pinned jar ($jar)"
else bad "tools/tla2tools.jar is $got, not the pinned $jar: NOT THE PINNED JAR"; fi

echo "tools/TLA-KIT-PIN"
if [ ! -f "$root/tools/TLA-KIT-PIN" ]; then
  bad "missing"
else
  form() {  # field, pattern, what it should be
    v=$(field TLA-KIT-PIN "$1")
    if [[ "$v" =~ $2 ]]; then ok "$1 $v"; else bad "$1 is '${v}', not $3"; fi
  }
  hex64='^[0-9a-f]{64}$'
  form release '^v[0-9]+\.[0-9]+\.[0-9]+$' "a release tag vMAJOR.MINOR.PATCH"
  form image '^ghcr\.io/scottcochran/tla-kit@sha256:[0-9a-f]{64}$' "the image by digest"
  form commit '^[0-9a-f]{40}$' "a full commit"
  form jar_sha256 "$hex64" "a sha256"
  form tlapm_sha256 "$hex64" "a sha256"
  form cvc5_sha256 "$hex64" "a sha256"
  form ethos_sha256 "$hex64" "a sha256"
  form pinned '^[0-9]{4}\.[0-9]{2}\.[0-9]{2}$' "a date"
  if [ "$(field TLA-KIT-PIN jar_sha256)" = "$jar" ]; then ok "jar_sha256 is tools/TLA-PIN's jar"
  else bad "jar_sha256 is not tools/TLA-PIN's jar ($jar): the image runs another jar"; fi
fi

echo "tools/TLAPS-PIN"
full=$(field TLAPS-PIN binary_sha256); short=$(field TLAPS-PIN binary_sha256_16)
if [[ "$full" =~ ^[0-9a-f]{64}$ ]] && [ "${full:0:16}" = "$short" ]; then ok "binary_sha256_16 is the first 16 hex of binary_sha256"
else bad "binary_sha256 '${full}' and binary_sha256_16 '${short}' do not agree"; fi
kit=$(field TLA-KIT-PIN tlapm_sha256)
if [ -n "$kit" ] && [ "$full" = "$kit" ]; then
  ok "binary_sha256 is the image's prover (tools/TLA-KIT-PIN tlapm_sha256)"
elif [ -n "$(field TLAPS-PIN image)" ]; then
  bad "tools/TLAPS-PIN names the image, and its binary_sha256 ${full:0:16}… is not the image's prover ${kit:0:16}…"
else
  note "binary_sha256 ${full:0:16}… (commit $(field TLAPS-PIN commit)) is not the image's prover ${kit:0:16}…: the pins name different builds until ADR-0077 §5"
fi

[ $status -eq 0 ] && echo "the pins agree" || echo "THE PINS DO NOT AGREE"
exit $status
