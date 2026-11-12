#!/bin/bash
# Which base does a CI run compare against, and which suites does a change touch?
#   usage: tools/ci-plan.sh EVENT [PR_BASE_SHA] [PUSH_BEFORE_SHA]
# Prints key=value lines (append them to $GITHUB_OUTPUT):
#   base=<sha>        pull_request: the PR's base; push: the commit before the push; otherwise, or when that commit is
#                     unknown (a new branch, a force push), HEAD's parent. tools/ratchet.py compares against it.
#   tlc= reference= lean= floor=   true when the change touches that suite's inputs, and always on
#                     workflow_dispatch and schedule. A suite is:
#     tlc        spec/, the TLC jar and its pin, the results tools          -> tools/check-results.sh
#     reference  mechanism/, policies/, floor/ (topak-floor links a floor)  -> cargo test in mechanism/
#     lean       mechanism/lean, spec/lean, floor/lean, tools/LEAN-PIN      -> lake build in each
#     floor      floor/                                                     -> floor/run-gates.py
#   A change to .github/workflows/results.yml or to this script touches every suite.
# Runs the same by hand: tools/ci-plan.sh pull_request "$(git merge-base origin/main HEAD)". ADR-0069 §10.2 (Proposed).
set -u
event=${1:?usage: tools/ci-plan.sh EVENT [PR_BASE_SHA] [PUSH_BEFORE_SHA]}
pr_base=${2:-}; before=${3:-}
known() { [ -n "$1" ] && ! [[ "$1" =~ ^0+$ ]] && git cat-file -e "$1^{commit}" 2>/dev/null; }
if [ "$event" = pull_request ] && known "$pr_base"; then base=$pr_base
elif [ "$event" = push ] && known "$before"; then base=$before
else base=$(git rev-parse HEAD~1 2>/dev/null || git rev-parse HEAD); fi
echo "base=$base"
case "$event" in
  workflow_dispatch|schedule) for s in tlc reference lean floor; do echo "$s=true"; done; exit 0 ;;
esac
changed=$(git diff --name-only "$base" HEAD)
touches() { grep -qE "$1" <<< "$changed" && echo true || echo false; }
all='^(\.github/workflows/results\.yml|tools/ci-plan\.sh)$'
echo "tlc=$(touches "$all|^spec/|^tools/(tla2tools\.jar|TLA-PIN|check-results\.sh|compare-results\.py)$")"
echo "reference=$(touches "$all|^(mechanism|policies|floor)/")"
echo "lean=$(touches "$all|^(mechanism|spec|floor)/lean/|^tools/LEAN-PIN$")"
echo "floor=$(touches "$all|^floor/")"
