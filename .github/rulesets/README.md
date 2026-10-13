# Rulesets

The repository's branch and tag rules, as GitHub ruleset JSON. Each file imports through **Settings → Rules →
Rulesets → New ruleset → Import a ruleset**. They are kept here so the rules are reviewable text; GitHub holds the
copy in force. `manifests/EXCLUDE` excludes `.github/`, so nothing here moves a digest.

Rulesets need a public repository or GitHub Pro (the API answers 403 until then), so import these **after** the
repository is made public.

## What each one does

| File | Applies to | Rules | Bypass |
|---|---|---|---|
| `01-main-integrity.json` | the default branch | no deletion; no force push; signed commits; a pull request for every change, merged by merge commit only, with every review thread resolved | nobody, the custodian included |
| `02-main-custodian-review.json` | the default branch | one approving review, from a code owner (`CODEOWNERS` names the custodian for everything), on the last push | repository admins, so the custodian can merge their own pull requests. Every other author needs the custodian's approval |
| `03-main-required-checks.json` | the default branch | the status checks named below, and the branch up to date with the base | nobody. **Imported disabled**: enable it after the workflow that produces the checks has run once, or every merge is blocked |
| `04-tags-immutable.json` | every tag | no update, no deletion | nobody. The manifests, records and the reviewer's guide cite `G*`, `ToO-rev*`, `REF-*` and `glossary-*` tags, and a cited tag must stay where it was |
| `05-tags-custodian-creates.json` | every tag | no creation | repository admins. Only the custodian cuts tags; it is kept apart from `04` so the bypass does not also permit deleting one |

Two rulesets on the same branch are both enforced; bypassing `02` leaves `01` and `03` in force. A bypass is
recorded on the merged pull request.

## After importing

1. **Check the bypass list** of `02` and `05`. GitHub's export leaves the bypass list out of the JSON, and the
   importer may do the same; if it is empty, add *Repository admin* with *Always allow*.
2. **Settings → General → Pull Requests**: untick *Allow squash merging* and *Allow rebase merging* (both are on
   today). `01` already limits merges on the default branch to merge commits; this makes the buttons match. A
   squash or rebase gives merged work a new hash, and a manifest row or an ADR-0033 pin cut on the branch would
   then cite a commit that is not on `main`. Tick *Automatically delete head branches*; a merge commit keeps every
   hash reachable, so deleting the branch loses nothing.
3. **Commit signing**: `01` refuses unsigned commits, including the custodian's. Set up SSH or GPG signing locally
   and add the key under Settings → SSH and GPG keys. Merge commits GitHub makes are signed by GitHub.
4. **Settings → Security**: enable *Private vulnerability reporting*, which `SECURITY.md` promises.

## The required checks

`03` names seven status-check contexts. The first six must be the **job names** in a workflow under
`.github/workflows/`; the seventh comes from the DCO app (https://github.com/apps/dco), which asks outside
contributors for a `Signed-off-by` line.

| Context | What it runs |
|---|---|
| `check-refs` | `tools/check-refs.py`, through the ratchet |
| `frozen-files` | `.github/scripts/frozen-files.py`, in its own workflow (`frozen-files.yml`) so it reruns when a label changes. Its rules F1 to F9 are in the script's header. The custodian's `frozen-override` label turns violations into warnings, and counts only when a code owner added it. It also refuses `.pdf`, `.zip` and files over 5 MB, which push rulesets would do natively but are not offered on user-owned public repositories |
| `verify-manifests` | `tools/verify-manifest.sh --all`, failing on any `EXPECTED` row, failing file, or unknown commit; needs `fetch-depth: 0` |
| `proof-sync` | `spec/proof-sync.sh`, through the ratchet |
| `lean-sync` | `tools/lean-sync.sh`, through the ratchet |
| `mechanism-tests` | checks that the tracked bundle's name is the digest of the current policies, then `opa test`, then `cargo test --workspace --release --locked`. No Docker: the tests use the tracked bundle |

**The ratchet** (`.github/scripts/ratchet.py`) is why `03` can be enabled while `main` carries debts.
`check-refs`, `proof-sync` and `lean-sync` all exit 1 on `main` today, for debts G11 lists: thirteen stale
citations, most inside frozen files; `Workflow.tla` and `Mesh.tla` without a proof or a reason (item 101); and
the three `mechanism/lean` series stale since the reference rebuild (A16, A17). The ratchet runs each checker on
the base and on the pull request, and fails only on a failure key the base did not have. Carried debts are shown
as notices.

**Enable `03` once both workflows have run on a pull request**, so GitHub has seen the seven contexts. The DCO app
must be installed first, or the `DCO` context never reports and every merge waits on it.

`strict_required_status_checks_policy` is on, so a pull request must contain the current `main` before it merges.
That costs a merge of `main` into the branch when `main` has moved, and buys a green result that was computed
against what will actually be merged. Set it to `false` in `03` if the extra merge commits are unwelcome.

## What rulesets cannot express

- Which lane a change is in (conveniences and code; records and checkpoints; safety findings). That is for
  `CONTRIBUTING.md`, and for the custodian at review.
- That a pull request approval is not a ratification. Ratification is the custodian's batch under ADR-0029, and the
  C1 to C4 confirmations wait for a post-bootstrap quorum.
- That the assistant never commits. `.claude/settings.json` denies it locally; the signature requirement in `01`
  is what makes that visible on the record.
