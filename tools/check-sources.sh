#!/bin/bash
# Are the upstream builds the pins name still what upstream serves? Reports and never edits a pin.
#   usage: tools/check-sources.sh     exit 1 if an upstream has moved away from its pin, 2 if one cannot be reached
# Checked:
#   tlapm   the release tag tools/TLAPS-PIN names (`version`), against the pin's `commit`. The tag is a pre-release
#           that upstream rebuilds; when it moves, a fresh tools/install-tlaps.sh fetches another prover, and a proof
#           results file made with it cites another binary. Moving the pin is the review's record of that.
# Uses `gh api` when gh is installed (CI sets GH_TOKEN), and the public API with curl otherwise.
# Like f1-tla's tools/check-sources.py, this is the upstream half of intake (ADR-0069 §3 I-2, Proposed): a finding
# against a pin is input to a review, never an edit. CI runs it on demand only (.github/workflows/sources.yml).
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
pin() { grep -E "^$1 " "$root/tools/TLAPS-PIN" | head -1 | cut -d' ' -f2; }
api() {
  if command -v gh >/dev/null 2>&1; then gh api "$1" --jq "$2"
  else curl -fsS "https://api.github.com/$1" | python3 -c "import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1]))" "$3"; fi
}
status=0
tag=$(pin version); want=$(pin commit)
obj=$(api "repos/tlaplus/tlapm/git/ref/tags/$tag" '.object.sha + " " + .object.type' 'd["object"]["sha"]+" "+d["object"]["type"]') \
  || { echo "tlapm: cannot read tag $tag"; exit 2; }
sha=${obj% *}
if [ "${obj#* }" = tag ]; then
  sha=$(api "repos/tlaplus/tlapm/git/tags/$sha" '.object.sha' 'd["object"]["sha"]') || { echo "tlapm: cannot read tag object"; exit 2; }
fi
when=$(api "repos/tlaplus/tlapm/releases/tags/$tag" '.published_at' 'd["published_at"]' 2>/dev/null || echo unknown)
if [ "${sha:0:${#want}}" = "$want" ]; then
  echo "tlapm $tag: upstream commit ${sha:0:7}, published $when; matches tools/TLAPS-PIN ($want)"
else
  echo "tlapm $tag: upstream commit ${sha:0:7}, published $when; tools/TLAPS-PIN names $want: UPSTREAM HAS MOVED"
  echo "  A fresh tools/install-tlaps.sh would fetch a different prover. Keep the pinned binary, or re-prove and move the pin."
  status=1
fi
exit $status
