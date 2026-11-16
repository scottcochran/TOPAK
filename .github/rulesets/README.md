# Rulesets

The repository's branch and tag rules, as GitHub ruleset JSON. GitHub holds the copy in force. The files here are
the reviewable text, exported from the repository's rulesets on 2026.11.16 with the fields GitHub adds on its side
removed (`id`, `source`, `node_id`, `_links`, the timestamps). Each file imports through **Settings → Rules →
Rulesets → New ruleset → Import a ruleset**. `manifests/EXCLUDE` excludes `.github/`, so nothing here moves a
digest.

When a ruleset is changed on GitHub, export it again and replace its file here, so the two do not drift. Ruleset
03 below is the one exception: its file is ahead of GitHub until it is imported.

## What each one does

| File | Applies to | Rules | Enforcement | Bypass |
|---|---|---|---|---|
| `01-main-integrity.json` | the default branch | no deletion; no force push; signed commits; a pull request for every change, merged by merge commit only, with every review thread resolved | active | repository admins. Without it, the custodian could not merge their own pull requests while `02` requires an approval nobody else can give |
| `02-main-custodian-review.json` | the default branch | one approving review, from a code owner (`CODEOWNERS` names the custodian for everything), on the last push | active | repository admins, so the custodian can merge their own pull requests. Every other author needs the custodian's approval |
| `03-main-required-checks.json` | the default branch | the status checks `checks` and `frozen-files`, and the branch up to date with the base | **disabled** | nobody |
| `04-tags-immutable.json` | every tag | no update, no deletion | active | nobody. The manifests, records and the reviewer's guide cite `G*`, `ToO-rev*`, `REF-*` and `glossary-*` tags, and a cited tag must stay where it was |
| `05-tags-custodian-creates.json` | every tag | no creation | active | repository admins. Only the custodian cuts tags. It is kept apart from `04` so the bypass does not also permit deleting one |

Two rulesets on the same branch are both enforced. A bypass is recorded on the merged pull request.

The repository settings these rulesets assume are in place: squash and rebase merging are off (`01` allows merge
commits only, and a squash or rebase would give merged work a new hash that a manifest row or a pin cut on the
branch could not find), head branches are deleted on merge, and private vulnerability reporting, which
`SECURITY.md` promises, is on.

## The required checks (`03`)

`03` was first written for a workflow that `main` never adopted. That version named `check-refs`,
`verify-manifests`, `proof-sync`, `lean-sync`, `mechanism-tests` and `DCO`. No workflow on `main` reports those
contexts, so enabling it would have blocked every merge. ADR-0069's workflows (Proposed) replaced it. The file now
names the two checks that report on every pull request:

| Context | Workflow | What it runs |
|---|---|---|
| `checks` | `.github/workflows/checks.yml` | the TLC jar against its pin, `spec/proof-sync.sh`, `tools/verify-manifest.sh --all`, and four ratcheted checks (`tools/ratchet.py`): the corpus pins, `tools/lean-sync.sh`, `tools/check-refs.py`, and the record lint |
| `frozen-files` | `.github/workflows/frozen-files.yml` | `.github/scripts/frozen-files.py`, rules F1 to F9 in its header. In its own workflow so that it reruns when a label changes |

`results.yml` (TLC, the reference's tests, Lean, the floor's gates) is not required. It runs only when a pull
request touches `spec/`, `tools/`, `mechanism/`, `policies/` or `floor/`, and its jobs are conditional and one per
module (`tlc (Anchor)`, …). A required context that never reports leaves the pull request waiting forever. The
custodian reads its results at review.

`DCO` is not required either, because the DCO app (https://github.com/apps/dco) is not installed and its context
would never report. Add it back to `03` after installing the app.

**Before enabling `03`:** import this file over the disabled ruleset, and let both workflows run on one pull
request so GitHub has seen the two contexts.

`strict_required_status_checks_policy` is on, so a pull request must contain the current `main` before it merges.
That costs a merge of `main` into the branch when `main` has moved. In return, the green result was computed
against what will actually be merged.

## The `frozen-override` label

The custodian lifts the freeze for one pull request by adding the label `frozen-override`. It is for a change the
corpus itself authorizes, such as a layout move, or a revision in place that a record's amendment states. The check
then reports violations as warnings. The label counts only when a code owner added it, since anyone with triage
access can add a label. The label does not exist on the repository yet. Create it before it is first needed.

## What rulesets cannot express

- Which lane a change is in (conveniences and code; records and checkpoints; safety findings). That is for
  `CONTRIBUTING.md`, and for the custodian at review.
- That a pull request approval is not a ratification. Ratification is the custodian's batch under ADR-0029, and the
  C1 to C4 confirmations wait for a post-bootstrap quorum.
- Who drafted a commit. `.claude/settings.json` makes the assistant ask before every `git commit` and `git push`,
  and the signature requirement in `01` means every commit on `main` carries a key the custodian added.
