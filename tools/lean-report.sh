#!/bin/bash
# The build-and-check half of every Lean results file (ADR-0053). Given a Lean package directory and its
# root module: a clean build, whose `#print axioms` lines it prints joined and sorted so that the output regenerates
# byte for byte; then `leanchecker --fresh <root>`, which replays every constant the root reaches, Lean's own library
# and any dependency included, through the kernel in a fresh environment from the stored .olean files.
#   usage: tools/lean-report.sh <package dir> <root module>      exits non-zero if the build or the replay fails
# Why the replay: a declaration added with the kernel check switched off (`debug.skipKernelTC`) builds, and
# `#print axioms` reports a theorem resting on it as depending on no axioms at all. The replay refuses it. That
# control was run on 2026.10.05 and is described in spec/proof-method.md §5b. The replay is the same kernel in a
# separate process, not an independent checker (lean4lean would be one; ADR-0053, open obligations).
#   usage: tools/lean-report.sh <package dir> --prover        print only the results file's Prover line
set -u
pkg=${1:?usage: lean-report.sh <package dir> <root module>}
if [ "${2:-}" = "--prover" ]; then
  cd "$pkg" || exit 2
  pre=$(lean --print-prefix); d16() { shasum -a 256 "$1" | cut -c1-16; }
  lib="$pre/lib/lean/libleanshared.dylib"; [ -f "$lib" ] || lib="$pre/lib/lean/libleanshared.so"
  echo "Prover: $(lean --version) · kernel libleanshared (sha256 $(d16 "$lib")) · leanchecker (sha256 $(d16 "$pre/bin/leanchecker")) · $(lake --version | head -1) · toolchain $(cat lean-toolchain) · driver: results.sh, tools/lean-report.sh"
  exit 0
fi
root=${2:?usage: lean-report.sh <package dir> <root module>}
cd "$pkg" || exit 2
rm -rf .lake/build
build=$(lake build 2>&1); bstatus=$?
printf '%s\n' "$build" | python3 -c '
import re, sys
lines, out = sys.stdin.read().split("\n"), []
for l in lines:
    if l.startswith((" ", "\t")) and out:
        out[-1] += " " + l.strip()
    else:
        out.append(l)
keep = sorted(l for l in out if re.match(r"(info|warning|error): ", l))
last = [l for l in out if l.startswith(("Build completed", "error: build failed"))]
print("\n".join(keep + last[-1:]))'
if [ $bstatus -ne 0 ]; then echo "Replay: not run, the build failed"; exit $bstatus; fi
replay=$(lake env leanchecker --fresh "$root" 2>&1); rstatus=$?
if [ $rstatus -eq 0 ]; then
  echo "Replay: leanchecker --fresh $root: every constant $root reaches replayed through the kernel in a fresh environment, accepted"
else
  echo "Replay: leanchecker --fresh $root: REFUSED"; printf '%s\n' "$replay" | tail -5
fi
exit $rstatus
