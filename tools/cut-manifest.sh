#!/usr/bin/env bash
# cut-manifest.sh NAME   — write manifests/NAME over the corpus artifacts, root-relative, LC_ALL=C sorted,
# excluding what manifests/EXCLUDE lists (the G5 §9 rule, stated once). Measures mechanism/, policies/ and slm/
# through their tree manifests, not file by file. Prints the row to append to manifests/index.tsv.
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"; name="$1"
cd "$repo"
git ls-files -co --exclude-standard | grep -vE -f manifests/EXCLUDE | LC_ALL=C sort | xargs shasum -a 256 > "manifests/$name"
n=$(grep -c . "manifests/$name")
printf 'index.tsv row:\t%s\tcheckpoint\t%s\t<commit>\t%s\t%s\n' "$name" "$(date +%Y.%m.%d)" "$n" "$n"
