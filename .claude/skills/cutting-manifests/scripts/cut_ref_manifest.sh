#!/usr/bin/env bash
# cut_ref_manifest.sh NAME COMMIT [CUT-DATE]      write manifests/NAME over mechanism/ and policies/ at COMMIT
# cut_ref_manifest.sh --print COMMIT              print the entries and write nothing
#
# A reference manifest measures the tree at a commit, so this reads that commit and never the working tree: an
# uncommitted edit or an untracked file cannot enter it. It refuses to overwrite a manifest. It prints the index.tsv
# row, the manifest's digest as an ADR-0033 addendum cites it, and the entry delta from the newest reference manifest.
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
entries() {
  local commit="$1" tmp
  tmp="$(mktemp -d)"
  git -C "$repo" archive "$commit" mechanism policies | tar -x -C "$tmp"
  git -C "$repo" ls-tree -r --name-only "$commit" mechanism policies | LC_ALL=C sort | tr '\n' '\0' \
    | (cd "$tmp" && xargs -0 shasum -a 256)
  rm -rf "$tmp"
}
if [ "${1:-}" = "--print" ]; then
  entries "${2:?usage: cut_ref_manifest.sh --print COMMIT}"
  exit 0
fi
name="${1:?usage: cut_ref_manifest.sh NAME COMMIT [CUT-DATE]}"
commit="${2:?usage: cut_ref_manifest.sh NAME COMMIT [CUT-DATE]}"
cutdate="${3:-$(date +%Y.%m.%d)}"
case "$name" in SHA256SUMS-REF-*) ;; *) echo "cut_ref_manifest: a reference manifest is named SHA256SUMS-REF-<date>[suffix]" >&2; exit 2;; esac
out="$repo/manifests/$name"
if [ -e "$out" ]; then echo "cut_ref_manifest: $name exists; a manifest is never overwritten" >&2; exit 2; fi
git -C "$repo" rev-parse --verify -q "$commit^{commit}" >/dev/null || { echo "cut_ref_manifest: no commit $commit" >&2; exit 2; }
short="$(git -C "$repo" rev-parse --short=7 "$commit")"
entries "$commit" > "$out.tmp"
mv "$out.tmp" "$out"
n="$(grep -c . "$out")"
prev="$(awk -F'\t' '$2 == "reference" { n = $1 } END { print n }' "$repo/manifests/index.tsv")"
printf 'index.tsv row:\t%s\treference\t%s\t%s\t%s\t%s\t<why: the addendum, and what it measures>\n' "$name" "$cutdate" "$short" "$n" "$n"
printf 'digest (first 16 hex): %s\n' "$(shasum -a 256 "$out" | cut -c1-16)"
if [ -n "$prev" ] && [ -f "$repo/manifests/$prev" ]; then
  python3 - "$repo/manifests/$prev" "$out" "$prev" <<'PY'
import sys
def read(p):
    return {l.split(None, 1)[1].strip(): l.split()[0] for l in open(p) if l.strip()}
a, b = read(sys.argv[1]), read(sys.argv[2])
add = sorted(set(b) - set(a)); rem = sorted(set(a) - set(b)); chg = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
pol = sum(1 for k in chg + add + rem if k.startswith("policies/"))
print(f"delta from {sys.argv[3]} ({len(a)} entries): {len(add)} added, {len(rem)} removed, {len(chg)} changed, {pol} of those under policies/")
PY
fi
